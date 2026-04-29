#!/bin/bash
# feishu-validator.sh - Code Committer Skill 飞书工作项验证
# Version: 1.0.0
# Description: 验证飞书项目工作项，检查 YAML front matter 格式

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 引入错误码定义
# shellcheck source=scripts/error-codes.sh
source "${SCRIPT_DIR}/error-codes.sh"

# 颜色输出
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
# 飞书工作项验证函数
# ============================================

# 检查 YAML front matter 格式
# 参数: $1 - MR description 文本
# 输出: 0 - 格式正确, 53 - 格式错误 (503 映射到 53)
feishu_check_frontmatter() {
    local description="$1"

    # 检查是否以 --- 开头
    if [[ ! "$description" =~ ^--- ]]; then
        return 0  # 没有 front matter 也是有效的（不关联飞书工作项）
    fi

    # 提取 front matter 部分
    local frontmatter
    frontmatter=$(echo "$description" | sed -n '/^---/,/^---$/p')

    # 检查是否有闭合的 ---
    if [[ ! "$frontmatter" =~ ^---$ ]]; then
        # 检查 frontmatter 是否正确闭合
        local line_count=$(echo "$frontmatter" | wc -l)
        if [ "$line_count" -lt 2 ]; then
            return 53  # 格式错误：没有闭合的 --- (503 -> 53)
        fi
    fi

    # 检查是否包含 feishu.task 字段
    if [[ ! "$frontmatter" =~ feishu\.task: ]]; then
        return 0  # 有 front matter 但没有 feishu.task 也是有效的
    fi

    # 检查 feishu.task 格式
    # 格式: feishu.task: <数字ID>
    if [[ ! "$frontmatter" =~ feishu\.task:[[:space:]]*[0-9]+ ]]; then
        return 53  # 格式错误：feishu.task 后面应该是数字 (503 -> 53)
    fi

    return 0
}

# 提取飞书工作项 ID
# 参数: $1 - MR description 文本
# 输出: 飞书工作项 ID（数字），如果没有则输出空字符串
feishu_extract_task_id() {
    local description="$1"

    # 检查是否包含 feishu.task
    if [[ ! "$description" =~ feishu\.task: ]]; then
        echo ""
        return 0
    fi

    # 提取任务 ID
    local task_id
    task_id=$(echo "$description" | grep -oP 'feishu\.task:\s*\K[0-9]+')

    echo "$task_id"
}

# 生成 YAML front matter
# 参数: $1 - 飞书工作项 ID
# 输出: YAML front matter 字符串
feishu_generate_frontmatter() {
    local task_id="$1"

    if [ -z "$task_id" ]; then
        echo ""
        return 0
    fi

    cat << EOF
---
feishu.task: $task_id
---
EOF
}

# 验证飞书工作项是否存在
# 参数: $1 - 飞书工作项 ID
# 输出: 0 - 存在, 50 - 验证失败, 51 - 不存在, 52 - 无权限
feishu_validate_task() {
    local task_id="$1"

    if [ -z "$task_id" ]; then
        warning "飞书工作项 ID 为空"
        return 0  # 空 ID 不是错误，只是不关联飞书工作项
    fi

    # 检查 lark-cli 是否可用
    if ! command -v lark-cli &> /dev/null; then
        warning "lark-cli 未安装，跳过飞书工作项验证"
        return 0
    fi

    info "正在验证飞书工作项 #$task_id..."

    # 尝试获取任务信息
    # 注意：这里使用 lark-cli task 相关命令
    # 具体命令可能需要根据实际的 lark-cli 版本调整

    # 这里是一个示例实现，实际使用时需要根据 lark-cli 的实际 API 调整
    local result
    result=$(lark-cli task +get --task-id "$task_id" --as user 2>&1)
    local exit_code=$?

    if [ $exit_code -eq 0 ]; then
        # 检查结果中是否包含错误信息
        if [[ "$result" =~ "not found" ]] || [[ "$result" =~ "不存在" ]]; then
            error "飞书工作项 #$task_id 不存在"
            return 51  # 501 -> 51
        fi

        if [[ "$result" =~ "permission" ]] || [[ "$result" =~ "无权限" ]]; then
            error "无权限访问飞书工作项 #$task_id"
            return 52  # 502 -> 52
        fi

        success "飞书工作项 #$task_id 验证通过"

        # 尝试提取任务标题
        local task_title
        task_title=$(echo "$result" | grep -oP '"summary":\s*"\K[^"]*' || echo "")

        if [ -n "$task_title" ]; then
            info "   工作项标题: $task_title"
        fi

        return 0
    else
        # 命令执行失败，可能是因为任务不存在或其他原因
        error "飞书工作项 #$task_id 验证失败"
        return 50  # 500 -> 50
    fi
}

# 格式化 MR description（添加或更新飞书元数据）
# 参数: $1 - 原始 MR description
#       $2 - 飞书工作项 ID（可选）
# 输出: 格式化后的 MR description
feishu_format_description() {
    local description="$1"
    local task_id="$2"

    # 如果没有提供任务 ID，直接返回原描述
    if [ -z "$task_id" ]; then
        echo "$description"
        return 0
    fi

    # 检查是否已有 front matter
    if [[ "$description" =~ ^--- ]]; then
        # 已有 front matter，检查是否需要更新 feishu.task
        if [[ "$description" =~ feishu\.task: ]]; then
            # 已有 feishu.task，更新它
            echo "$description" | sed "s/feishu\.task:.*/feishu.task: $task_id/"
        else
            # 没有 feishu.task，在 --- 后添加
            local new_frontmatter
            new_frontmatter=$(echo "$description" | sed "0,/^---$/{
                s/^---$/---\\nfeishu.task: $task_id/
            }")
            echo "$new_frontmatter"
        fi
    else
        # 没有 front matter，添加新的
        local frontmatter
        frontmatter=$(feishu_generate_frontmatter "$task_id")
        echo -e "$frontmatter\n$description"
    fi
}

# ============================================
# 辅助函数
# ============================================

# 显示验证状态摘要
show_validation_summary() {
    local has_feishu=$1
    local task_id=$2
    local is_valid=$3

    echo ""
    echo "📋 飞书工作项验证摘要:"
    if [ "$has_feishu" = "true" ]; then
        echo "   关联工作项: #$task_id"
        if [ "$is_valid" = "true" ]; then
            echo "   验证状态: ✅ 通过"
        else
            echo "   验证状态: ❌ 失败"
        fi
    else
        echo "   关联工作项: 无"
    fi
    echo ""
}

# 如果直接执行此脚本，显示帮助信息
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    echo "feishu-validator.sh - Code Committer Skill 飞书工作项验证"
    echo ""
    echo "用法:"
    echo "  source scripts/feishu-validator.sh"
    echo ""
    echo "函数:"
    echo "  feishu_check_frontmatter <description>     - 检查 YAML front matter 格式"
    echo "  feishu_extract_task_id <description>       - 提取飞书工作项 ID"
    echo "  feishu_generate_frontmatter <task_id>      - 生成 YAML front matter"
    echo "  feishu_validate_task <task_id>             - 验证飞书工作项是否存在"
    echo "  feishu_format_description <desc> <task_id> - 格式化 MR description"
    echo ""
    echo "示例:"
    echo "  feishu_validate_task 6723548458"
    echo "  feishu_format_description \"Implement feature\" 6723548458"
fi
