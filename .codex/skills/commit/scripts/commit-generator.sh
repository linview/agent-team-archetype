#!/bin/bash
# commit-generator.sh - Code Committer Skill Commit Message 生成
# Version: 1.0.0
# Description: 基于 diff 自动生成语义化 commit message

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 引入错误码定义
# shellcheck source=scripts/error-codes.sh
source "${SCRIPT_DIR}/error-codes.sh"

# ============================================
# Commit Message 生成函数
# ============================================

# 基于 diff 生成 commit message
# 输出: 生成的 commit message
commit_generate_message() {
    # 获取暂存的变更文件
    local changed_files
    changed_files=$(git diff --cached --name-only --diff-filter=ACM)

    if [ -z "$changed_files" ]; then
        # 没有暂存的变更，检查未暂存的变更
        changed_files=$(git diff --name-only --diff-filter=ACM)
    fi

    if [ -z "$changed_files" ]; then
        echo "No changes"
        return 1
    fi

    # 分析变更类型
    local commit_type=""
    local scope=""
    local summary=""

    # 统计文件类型
    local file_count=$(echo "$changed_files" | wc -l)
    local has_test=false
    local has_docs=false
    local has_config=false
    local has_source=false

    for file in $changed_files; do
        if [[ "$file" =~ test|spec ]]; then
            has_test=true
        elif [[ "$file" =~ \.(md|txt|rst|doc) ]]; then
            has_docs=true
        elif [[ "$file" =~ \.(json|yaml|yml|toml|conf|cfg) ]]; then
            has_config=true
        elif [[ "$file" =~ \.(py|js|ts|java|go|rs|c|h|cpp|cc|sh) ]]; then
            has_source=true
        fi
    done

    # 确定类型
    if [ "$has_test" = true ]; then
        commit_type="test"
    elif [ "$has_docs" = true ] && [ "$has_source" = false ]; then
        commit_type="docs"
    elif [ "$has_config" = true ] && [ "$has_source" = false ]; then
        commit_type="chore"
    elif [ "$has_config" = true ]; then
        commit_type="chore(config)"
    elif [ "$has_source" = true ]; then
        commit_type="feat"
    else
        commit_type="chore"
    fi

    # 确定范围（如果有明显的前端/后端区分）
    if echo "$changed_files" | grep -qE "(src/|components/|pages/)"; then
        if echo "$changed_files" | grep -qE "(frontend|ui|client|web)"; then
            scope="frontend"
        elif echo "$changed_files" | grep -qE "(backend|api|server|service)"; then
            scope="backend"
        fi
    fi

    # 生成摘要
    if [ $file_count -eq 1 ]; then
        local filename
        filename=$(basename "$changed_files")
        summary="Update $filename"
    else
        summary="Update $file_count files"
    fi

    # 组装 commit message
    local message=""
    if [ -n "$scope" ]; then
        message="$commit_type($scope): $summary"
    else
        message="$commit_type: $summary"
    fi

    echo "$message"
}

# 加载项目最近的 commits 匹配风格
commit_load_project_style() {
    local count="${1:-10}"

    info "分析项目最近 $count 条 commits 的风格..."

    local recent_commits
    recent_commits=$(git log -"$count" --pretty=format:"%s" 2>/dev/null || echo "")

    if [ -z "$recent_commits" ]; then
        warning "无法获取项目 commit 历史"
        return 1
    fi

    # 分析 commit 风格
    local uses_conventional=false
    local uses_scope=false

    while IFS= read -r commit_msg; do
        if [[ "$commit_msg" =~ ^[a-z]+(\[?[a-z]+\]?)?: ]]; then
            uses_conventional=true
        fi
        if [[ "$commit_msg" =~ ^[a-z]+\([a-z]+\): ]]; then
            uses_scope=true
        fi
    done <<< "$recent_commits"

    echo "项目 commit 风格分析:"
    if [ "$uses_conventional" = true ]; then
        echo "  - 使用 Conventional Commits 格式"
    fi
    if [ "$uses_scope" = true ]; then
        echo "  - 使用 scope"
    fi
}

# 检查 CLAUDE.md 中的项目提交约定
commit_check_claude_md() {
    local proj_root
    proj_root=$(git rev-parse --show-toplevel 2>/dev/null)

    if [ -z "$proj_root" ]; then
        return 1
    fi

    local claude_md="$proj_root/CLAUDE.md"

    if [ ! -f "$claude_md" ]; then
        return 1
    fi

    # 检查是否有提交相关的约定
    if grep -q -i "commit" "$claude_md" 2>/dev/null; then
        info "发现项目 CLAUDE.md 中有提交约定"
        # 提取相关段落
        grep -A 10 -i "commit" "$claude_md" | head -n 20
        return 0
    fi

    return 1
}

# 如果直接执行此脚本，显示帮助信息
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    echo "commit-generator.sh - Code Committer Skill Commit Message 生成"
    echo ""
    echo "用法:"
    echo "  source scripts/commit-generator.sh"
    echo ""
    echo "函数:"
    echo "  commit_generate_message           - 生成 commit message"
    echo "  commit_load_project_style [count] - 加载项目风格"
    echo "  commit_check_claude_md             - 检查 CLAUDE.md 约定"
    echo ""
    echo "示例:"
    echo "  commit_generate_message"
    echo "  commit_load_project_style 20"
fi
