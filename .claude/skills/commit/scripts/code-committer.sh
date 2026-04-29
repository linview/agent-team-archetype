#!/bin/bash
# code-committer.sh - Code Committer Skill 主入口脚本
# Version: 1.0.0
# Description: Git 提交和 MR 创建的主入口，支持交互式和非交互式模式

set -e

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_ROOT="$(dirname "$SCRIPT_DIR")"

# 引入依赖脚本
# shellcheck source=scripts/error-codes.sh
source "${SCRIPT_DIR}/error-codes.sh"
# shellcheck source=scripts/check-dependencies.sh
source "${SCRIPT_DIR}/check-dependencies.sh"
# shellcheck source=scripts/remote-handler.sh
source "${SCRIPT_DIR}/remote-handler.sh"
# shellcheck source=scripts/gitlab-api.sh
source "${SCRIPT_DIR}/gitlab-api.sh"
# shellcheck source=scripts/feishu-validator.sh
source "${SCRIPT_DIR}/feishu-validator.sh"

# ============================================
# 颜色输出
# ============================================
info() {
    echo "\033[0;34mℹ️  $*\033[0m"
}

success() {
    echo "\033[0;32m✅ $*\033[0m"
}

warning() {
    echo "\033[0;33m⚠️  $*\033[0m"
}

error() {
    echo "\033[0;31m❌ $*\033[0m"
}

# ============================================
# MR Description 生成函数（⚠️ 铁律：强制分析完整 diff）
# ============================================

# ⚠️ 铁律：必须分析 source_branch → target_branch 的完整 diff
# 禁止直接使用最后一个 commit message 作为 MR 描述
#
# 参数: $1 - source_branch
#       $2 - target_branch
#       $3 - feishu_task_id (可选)
# 输出: 生成的 MR 描述
mr_generate_description() {
    local source_branch="$1"
    local target_branch="$2"
    local feishu_task="$3"

    echo "⚠️  铁律执行：分析完整分支 diff ($source_branch → $target_branch)..." >&2

    # 1. 获取完整 diff 统计
    local diff_stats
    diff_stats=$(git diff "${target_branch}...${source_branch}" --stat 2>/dev/null)

    if [ -z "$diff_stats" ]; then
        error "无法获取 diff 信息，请确认目标分支存在"
        return 1
    fi

    # 2. 获取变更文件列表
    local changed_files
    changed_files=$(git diff "${target_branch}...${source_branch}" --name-status 2>/dev/null)

    if [ -z "$changed_files" ]; then
        error "没有检测到变更"
        return 1
    fi

    # 3. 分析文件变更类型
    local has_dao=false
    local has_logic=false
    local has_model=false
    local has_test=false
    local has_skill=false
    local file_count=$(echo "$changed_files" | wc -l)
    local insertions=0
    local deletions=0

    while IFS= read -r line; do
        local status=$(echo "$line" | cut -c1)
        local file=$(echo "$line" | cut -c2-)

        case "$file" in
            internal/dao/*) has_dao=true ;;
            internal/logic/*) has_logic=true ;;
            internal/model/*) has_model=true ;;
            */*test.go) has_test=true ;;
            .claude/skills/*) has_skill=true ;;
        esac
    done <<< "$changed_files"

    # 从 diff 统计中提取插入/删除行数
    insertions=$(echo "$diff_stats" | grep -oP '\d+(?=\s+insertion)' | awk '{s+=$1} END {print s+0}')
    deletions=$(echo "$diff_stats" | grep -oP '\d+(?=\s+deletion)' | awk '{s+=$1} END {print s+0}')

    # 4. 获取分支的所有提交（用于理解分支意图）
    local commits
    commits=$(git log "${target_branch}..${source_branch}" --oneline 2>/dev/null)
    local commit_count=$(echo "$commits" | wc -l)

    # 5. 分析主要功能（从提交信息中提取）
    local primary_feature=""
    local story_id=""

    while IFS= read -r commit; do
        # 提取 Story ID（如 STORY-15-06）
        if echo "$commit" | grep -qP 'STORY-\d+-\d+'; then
            story_id=$(echo "$commit" | grep -oP 'STORY-\d+-\d+')
            break
        fi
        # 尝试从标题识别主要功能
        if echo "$commit" | grep -qP '(实现|implement|新增|add|创建|create)'; then
            primary_feature=$(echo "$commit" | sed -E 's/.*实现|新增|添加|创建|//g' | sed -E 's/\s+(数据层|DAO|API|服务|功能).*//')
            [ -n "$primary_feature" ] && break
        fi
    done <<< "$commits"

    # 如果没有找到主要功能，使用分支名推断
    if [ -z "$primary_feature" ]; then
        primary_feature=$(echo "$source_branch" | sed -E 's/feat.*epic.*story.*//')
    fi

    # 6. 生成 MR 描述
    local desc=""

    # YAML front matter（飞书工作项）
    if [ -n "$feishu_task" ]; then
        desc+="---
feishu.task: $feishu_task
---

"
    fi

    # 功能说明
    desc+="## 功能说明
"
    if [ -n "$story_id" ]; then
        desc+="实现 $story_id："
    fi
    desc+="$primary_feature

"

    # 核心变更
    desc+="## 核心变更
"

    # 按模块分组描述变更
    if [ "$has_dao" = true ]; then
        desc+="### 数据层（DAO）
"
        git diff "${target_branch}...${source_branch}" -- internal/dao/ --stat 2>/dev/null | sed 's/^/  - /' | head -5
        desc+="
"
    fi

    if [ "$has_model" = true ]; then
        desc+="### 模型层
"
        git diff "${target_branch}...${source_branch}" -- internal/model/ --stat 2>/dev/null | sed 's/^/  - /' | head -3
        desc+="
"
    fi

    if [ "$has_logic" = true ]; then
        desc+="### 业务逻辑层
"
        git diff "${target_branch}...${source_branch}" -- internal/logic/ --stat 2>/dev/null | sed 's/^/  - /' | head -5
        desc+="
"
    fi

    if [ "$has_test" = true ]; then
        desc+="### 测试
"
        local test_files
        test_files=$(echo "$changed_files" | grep "test.go" | wc -l)
        desc+="- 更新 $test_files 个测试文件
"
        desc+="
"
    fi

    if [ "$has_skill" = true ]; then
        desc+="### 基础设施
"
        git diff "${target_branch}...${source_branch}" -- .claude/skills/ --stat 2>/dev/null | sed 's/^/  - /' | head -3
        desc+="
"
    fi

    # 变更统计
    desc+="## 变更统计
"
    desc+="- 文件数: $file_count
"
    desc+="- 插入: +$insertions 行
"
    desc+="- 删除: -$deletions 行
"
    desc+="- 提交数: $commit_count commits
"

    # 测试状态
    desc+="

## 测试
"
    if [ "$has_test" = true ]; then
        desc+="- [x] 单元测试已更新"
    fi
    if [ "$has_dao" = true ] || [ "$has_logic" = true ]; then
        desc+="- [x] 代码实现完成"
    fi

    echo "$desc"
    echo "✅ MR 描述生成完成（基于完整 diff 分析）" >&2
}

# ============================================
# Commit 操作
# ============================================

# 创建 commit
# 参数: --message <msg> | --auto-generate
#       --files <files> (可选)
#       --non-interactive
code_committer_commit() {
    local message=""
    local auto_generate=false
    local files=""
    local non_interactive=false

    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            --message)
                message="$2"
                shift 2
                ;;
            --auto-generate)
                auto_generate=true
                shift
                ;;
            --files)
                files="$2"
                shift 2
                ;;
            --non-interactive)
                non_interactive=true
                shift
                ;;
            *)
                error "未知参数: $1"
                return 1
                ;;
        esac
    done

    # 检查是否有暂存的变更
    if ! git diff --cached --quiet; then
        # 有暂存的变更
        :
    else
        # 没有暂存的变更，检查是否有未暂存的变更
        if git diff --quiet; then
            error "没有检测到变更，请先使用 git add 暂存文件"
            return 301
        fi

        # 如果有未暂存的变更且不是非交互模式，询问是否暂存所有变更
        if [ "$non_interactive" = false ]; then
            echo "检测到未暂存的变更，是否暂存所有变更？[Y/n]"
            read -r answer
            if [[ "$answer" =~ ^[Yy]$ ]]; then
                git add -A
            else
                return 0
            fi
        fi
    fi

    # 确定提交消息
    local commit_message="$message"

    if [ "$auto_generate" = true ] && [ -z "$message" ]; then
        # 自动生成 commit message
        commit_message=$(commit_generate_message)
    elif [ -z "$message" ]; then
        # 非交互模式必须有 message
        if [ "$non_interactive" = true ]; then
            error "非交互模式需要提供 --message 或 --auto-generate"
            return 1
        fi

        # 交互模式，提示用户输入
        echo "请输入 commit message（留空取消）："
        read -r commit_message

        if [ -z "$commit_message" ]; then
            info "已取消提交"
            return 0
        fi
    fi

    # 执行提交
    info "正在创建 commit..."
    git commit -m "$commit_message" || exit_with_error 302

    success "Commit 创建成功"
}

# 基于 diff 生成 commit message
commit_generate_message() {
    # 获取变更的文件列表
    local changed_files
    changed_files=$(git diff --cached --name-only --diff-filter=ACM)

    # 分析变更类型
    local file_types=""
    local has_test=false
    local has_docs=false
    local has_config=false

    for file in $changed_files; do
        if [[ "$file" =~ test|spec ]]; then
            has_test=true
        elif [[ "$file" =~ \.(md|txt|rst) ]]; then
            has_docs=true
        elif [[ "$file" =~ \.(json|yaml|yml|toml|conf) ]]; then
            has_config=true
        fi
    done

    # 生成简短的 commit message
    local summary=""
    local file_count=$(echo "$changed_files" | wc -l)

    if [ $file_count -eq 1 ]; then
        local filename
        filename=$(basename "$changed_files")
        summary="Update $filename"
    else
        summary="Update $file_count files"
    fi

    # 添加类型标签
    if [ "$has_test" = true ]; then
        summary="test: $summary"
    elif [ "$has_docs" = true ]; then
        summary="docs: $summary"
    elif [ "$has_config" = true ]; then
        summary="chore(config): $summary"
    fi

    # 添加文件摘要
    if [ "${#summary}" -lt 50 ]; then
        echo "$summary"
    else
        echo "$summary" | cut -c1-50
    fi
}

# ============================================
# Push 操作
# ============================================

# 推送到远端
# 参数: --branch <branch> | --current
#       --remote <remote>
#       --create-if-not-exists
#       --non-interactive
code_committer_push() {
    local branch=""
    local remote="origin"
    local create_if_not_exists=false
    local non_interactive=false
    local use_current=false

    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            --branch)
                branch="$2"
                shift 2
                ;;
            --current)
                use_current=true
                shift
                ;;
            --remote)
                remote="$2"
                shift 2
                ;;
            --create-if-not-exists)
                create_if_not_exists=true
                shift
                ;;
            --non-interactive)
                non_interactive=true
                shift
                ;;
            *)
                error "未知参数: $1"
                return 1
                ;;
        esac
    done

    # 确定分支
    if [ "$use_current" = true ]; then
        branch=$(get_current_branch)
    elif [ -z "$branch" ]; then
        branch=$(get_current_branch)
    fi

    if [ -z "$branch" ]; then
        error "无法确定分支名"
        return 304
    fi

    # 确认推送操作（交互模式）
    if [ "$non_interactive" = false ]; then
        echo "准备推送到远端: $remote/$branch"
        echo "确认推送？[Y/n]"
        read -r answer
        if [[ ! "$answer" =~ ^[Yy]$ ]]; then
            info "已取消推送"
            return 0
        fi
    fi

    # 执行推送
    remote_push "$remote" "$branch" "$create_if_not_exists"
}

# ============================================
# MR 创建操作
# ============================================

# 创建 MR
# 参数: --source-branch <branch>
#       --target-branch <branch>
#       --mr-title <title>
#       --feishu-task <task_id>
#       --non-interactive
code_committer_mr_create() {
    local source_branch=""
    local target_branch=""
    local mr_title=""
    local feishu_task=""
    local non_interactive=false

    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            --source-branch)
                source_branch="$2"
                shift 2
                ;;
            --target-branch)
                target_branch="$2"
                shift 2
                ;;
            --mr-title)
                mr_title="$2"
                shift 2
                ;;
            --feishu-task)
                feishu_task="$2"
                shift 2
                ;;
            --non-interactive)
                non_interactive=true
                shift
                ;;
            *)
                error "未知参数: $1"
                return 1
                ;;
        esac
    done

    # 确定源分支
    if [ -z "$source_branch" ]; then
        source_branch=$(get_current_branch)
    fi

    if [ -z "$source_branch" ]; then
        error "无法确定源分支"
        return 304
    fi

    # 确定目标分支
    if [ -z "$target_branch" ]; then
        target_branch=$(remote_get_default_target)
        info "自动检测目标分支: $target_branch"
    fi

    # 检查 PAT 配置
    if ! gitlab_check_pat; then
        error "GitLab PAT 未配置"
        info "请设置 GITLAB_PAT 环境变量或在配置文件中设置 pat 字段"
        if [ "$non_interactive" = true ]; then
            return 203
        fi
    fi

    # 确定飞书工作项
    if [ -z "$feishu_task" ]; then
        if [ "$non_interactive" = true ]; then
            # 非交互模式，跳过飞书验证
            feishu_task=""
        else
            # 交互模式，询问是否关联飞书工作项
            echo "是否关联飞书工作项？[y/N]"
            read -r answer
            if [[ "$answer" =~ ^[Yy]$ ]]; then
                echo "请输入飞书工作项 ID:"
                read -r feishu_task

                # 验证飞书工作项
                if [ -n "$feishu_task" ]; then
                    feishu_validate_task "$feishu_task" || return 500
                fi
            else
                feishu_task=""
            fi
        fi
    else
        # 验证飞书工作项
        feishu_validate_task "$feishu_task" || return 500
    fi

    # 确定 MR Title
    if [ -z "$mr_title" ]; then
        if [ "$non_interactive" = true ]; then
            error "非交互模式需要提供 --mr-title"
            return 1
        fi

        # 交互模式，提示用户输入
        echo "请输入 MR Title (Conventional Commits 格式):"
        read -r mr_title

        if [ -z "$mr_title" ]; then
            info "已取消创建 MR"
            return 0
        fi
    fi

    # 生成 MR Description（⚠️ 铁律：必须分析完整 diff）
    local mr_description
    mr_description=$(mr_generate_description "$source_branch" "$target_branch" "$feishu_task")

    if [ -z "$mr_description" ]; then
        error "MR 描述生成失败"
        return 1
    fi

    # 交互模式，确认创建
    if [ "$non_interactive" = false ]; then
        echo ""
        echo "准备创建 MR:"
        echo "  源分支: $source_branch"
        echo "  目标分支: $target_branch"
        echo "  标题: $mr_title"
        if [ -n "$feishu_task" ]; then
            echo "  飞书工作项: #$feishu_task"
        fi
        echo ""
        echo "确认创建？[Y/n]"
        read -r answer
        if [[ ! "$answer" =~ ^[Yy]$ ]]; then
            info "已取消创建 MR"
            return 0
        fi
    fi

    # 创建 MR
    gitlab_create_mr "$source_branch" "$target_branch" "$mr_title" "$mr_description"
}

# 推送并创建 MR（组合操作）
# 参数: --source-branch <branch> | --current
#       --target-branch <branch>
#       --mr-title <title>
#       --feishu-task <task_id>
#       --non-interactive
code_committer_push_and_mr() {
    local source_branch=""
    local target_branch=""
    local mr_title=""
    local feishu_task=""
    local non_interactive=false

    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            --source-branch)
                source_branch="$2"
                shift 2
                ;;
            --target-branch)
                target_branch="$2"
                shift 2
                ;;
            --mr-title)
                mr_title="$2"
                shift 2
                ;;
            --feishu-task)
                feishu_task="$2"
                shift 2
                ;;
            --non-interactive)
                non_interactive=true
                shift
                ;;
            *)
                error "未知参数: $1"
                return 1
                ;;
        esac
    done

    # 确定源分支
    if [ -z "$source_branch" ]; then
        source_branch=$(get_current_branch)
    fi

    # 先推送
    info "步骤 1/2: 推送到远端"
    remote_push "origin" "$source_branch" "true"

    # 再创建 MR
    echo ""
    info "步骤 2/2: 创建 MR"
    code_committer_mr_create \
        --source-branch "$source_branch" \
        --target-branch "$target_branch" \
        --mr-title "$mr_title" \
        --feishu-task "$feishu_task" \
        --non-interactive
}

# ============================================
# 主函数
# ============================================

# 显示帮助信息
show_help() {
    cat << 'EOF'
code-committer.sh - Code Committer Skill 主入口

用法:
  ./code-committer.sh <command> [options]

命令:
  commit              创建 commit
  push                推送到远端
  mr-create           创建 MR
  push-and-mr         推送并创建 MR

Commit 选项:
  --message <msg>     指定 commit message
  --auto-generate     自动生成 commit message
  --files <files>     指定文件列表
  --non-interactive   非交互模式

Push 选项:
  --branch <branch>   指定分支
  --current           使用当前分支
  --remote <remote>   指定远端（默认 origin）
  --create-if-not-exists  远端分支不存在时创建

MR 选项:
  --source-branch <branch>  源分支（默认当前分支）
  --target-branch <branch>  目标分支（自动检测 master/main）
  --mr-title <title>      MR 标题
  --feishu-task <id>      飞书工作项 ID

示例:
  # 自动生成 commit message
  ./code-committer.sh commit --auto-generate

  # 推送到远端
  ./code-committer.sh push --create-if-not-exists

  # 创建关联飞书工作项的 MR
  ./code-committer.sh mr-create --mr-title "feat(auth): login" --feishu-task 6723548458

  # 一键提交+推送+创建 MR
  ./code-committer.sh push-and-mr --auto-generate --mr-title "feat(auth): login" --feishu-task 6723548458 --non-interactive

退出码:
  0   - 成功
  200 - git 未安装
  203 - GitLab PAT 未配置
  300 - 不在 Git 仓库中
  301 - 未检测到变更
  302 - Commit 失败
  303 - Push 失败
  304 - 分支不存在
  305 - 远端分支创建失败
  400 - GitLab URL 推理失败
  402 - MR 创建失败
  500 - 飞书工作项验证失败
EOF
}

# 主函数
main() {
    # 检查依赖
    check_required_only

    # 解析命令
    local command="$1"
    shift || true

    case "$command" in
        commit)
            code_committer_commit "$@"
            ;;
        push)
            code_committer_push "$@"
            ;;
        mr-create)
            code_committer_mr_create "$@"
            ;;
        push-and-mr)
            code_committer_push_and_mr "$@"
            ;;
        --help|-h)
            show_help
            ;;
        *)
            error "未知命令: $command"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# 如果直接执行此脚本
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
