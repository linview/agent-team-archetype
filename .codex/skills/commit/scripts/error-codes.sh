#!/bin/bash
# error-codes.sh - Code Committer Skill 退出码定义
# Version: 1.0.0
# Description: 定义所有退出码及其描述，提供错误查询和退出函数
#
# 注意: Shell 退出码限制在 0-255 范围内
# 设计文档中的 3 位错误码用于文档分类，实际使用映射到 0-99
#
# 映射关系:
#   0-9   : 成功/信息 (0xx)
#   20-29 : 依赖/配置错误 (2xx)
#   30-39 : Git 操作错误 (3xx)
#   40-49 : GitLab API 错误 (4xx)
#   50-59 : 飞书集成错误 (5xx)
#   60-69 : 内审检查错误 (6xx)
#   99    : 未知错误 (9xx)

# ============================================
# 辅助函数
# ============================================

# 获取错误描述（支持 3 位错误码或实际退出码）
get_error_desc() {
    local code=$1
    case "$code" in
        # 成功/信息 (0xx -> 0-9)
        0|000) echo "成功" ;;
        1|001) echo "操作完成，但有警告" ;;

        # 依赖/配置错误 (2xx -> 20-29)
        20|200) echo "git 未安装" ;;
        21|201) echo "lark-cli 未安装，飞书功能不可用" ;;
        22|202) echo "配置文件不存在" ;;
        23|203) echo "GitLab PAT 未配置" ;;
        24|204) echo "配置格式错误" ;;

        # Git 操作错误 (3xx -> 30-39)
        30|300) echo "不在 Git 仓库中" ;;
        31|301) echo "未检测到变更" ;;
        32|302) echo "Commit 失败" ;;
        33|303) echo "Push 失败" ;;
        34|304) echo "分支不存在" ;;
        35|305) echo "远端分支创建失败" ;;

        # GitLab API 错误 (4xx -> 40-49)
        40|400) echo "GitLab URL 推理失败" ;;
        41|401) echo "GitLab API 认证失败" ;;
        42|402) echo "MR 创建失败" ;;
        43|403) echo "获取 MR 信息失败" ;;
        44|404) echo "标签获取失败" ;;

        # 飞书集成错误 (5xx -> 50-59)
        50|500) echo "飞书工作项验证失败" ;;
        51|501) echo "飞书工作项不存在" ;;
        52|502) echo "飞书工作项无权限访问" ;;
        53|503) echo "YAML front matter 格式错误" ;;

        # 内审检查错误 (6xx -> 60-69)
        60|600) echo "检测到敏感信息" ;;
        61|601) echo "测试覆盖不足" ;;
        62|602) echo "文档未更新" ;;

        # 未知错误 (9xx -> 99)
        99|999) echo "未知错误" ;;
        *)   echo "未定义的错误代码: $code" ;;
    esac
}

# 获取错误建议（支持 3 位错误码或实际退出码）
get_error_suggestion() {
    local code=$1
    case "$code" in
        20|200) echo "请安装 git: apt-get install git 或 yum install git" ;;
        21|201) echo "安装方法: npm install -g lark-cli" ;;
        23|203) echo "请设置 GITLAB_PAT 环境变量或在配置文件中设置 pat 字段" ;;
        24|204) echo "请检查配置文件 YAML 格式是否正确" ;;
        30|300) echo "请在 Git 仓库中执行此操作" ;;
        31|301) echo "请使用 git add 暂存文件后再提交" ;;
        33|303) echo "请检查网络连接和分支权限" ;;
        34|304) echo "请使用 git branch 查看可用分支" ;;
        35|305) echo "请检查远端仓库权限" ;;
        40|400) echo "请检查 git remote 配置" ;;
        41|401) echo "请检查 GITLAB_PAT 是否正确" ;;
        42|402) echo "请检查 MR 参数和权限" ;;
        50|500) echo "请检查工作项 ID 是否正确" ;;
        51|501) echo "请确认工作项 ID 是否有效" ;;
        52|502) echo "请检查 lark-cli 权限配置" ;;
        53|503) echo "格式: ---\\nfeishu.task: 6723548458\\n---" ;;
        60|600) echo "请检查代码中是否包含密钥、密码等敏感信息" ;;
        61|601) echo "建议添加对应的测试文件" ;;
        62|602) echo "请更新相关文档" ;;
        *)   echo "" ;;
    esac
}

# 将 3 位错误码转换为实际退出码
to_exit_code() {
    local code=$1
    case "$code" in
        000) echo 0 ;;
        001) echo 1 ;;
        200) echo 20 ;;
        201) echo 21 ;;
        202) echo 22 ;;
        203) echo 23 ;;
        204) echo 24 ;;
        300) echo 30 ;;
        301) echo 31 ;;
        302) echo 32 ;;
        303) echo 33 ;;
        304) echo 34 ;;
        305) echo 35 ;;
        400) echo 40 ;;
        401) echo 41 ;;
        402) echo 42 ;;
        403) echo 43 ;;
        404) echo 44 ;;
        500) echo 50 ;;
        501) echo 51 ;;
        502) echo 52 ;;
        503) echo 53 ;;
        600) echo 60 ;;
        601) echo 61 ;;
        602) echo 62 ;;
        999) echo 99 ;;
        *)   echo "$code" ;;  # 已经是 0-99 范围，直接返回
    esac
}

# 退出并输出错误信息
exit_with_error() {
    local code=$1
    local detail=${2:-""}

    # 转换为实际退出码
    local exit_code=$(to_exit_code "$code")

    echo "❌ 错误代码: $code" >&2
    echo "   错误描述: $(get_error_desc $code)" >&2

    local suggestion=$(get_error_suggestion $code)
    if [ -n "$suggestion" ]; then
        echo "   建议: $suggestion" >&2
    fi

    if [ -n "$detail" ]; then
        echo "   详细信息: $detail" >&2
    fi

    exit "$exit_code"
}

# 成功退出
exit_success() {
    local message=${1:-"操作成功"}
    echo "✅ $message"
    exit 0
}

# 带警告的成功退出
exit_with_warning() {
    local message=$1
    echo "⚠️  $message" >&2
    exit 1
}

# 打印错误信息但不退出（用于交互模式）
print_error() {
    local code=$1
    local detail=${2:-""}

    echo "❌ 错误代码: $code" >&2
    echo "   错误描述: $(get_error_desc $code)" >&2

    local suggestion=$(get_error_suggestion $code)
    if [ -n "$suggestion" ]; then
        echo "   建议: $suggestion" >&2
    fi

    if [ -n "$detail" ]; then
        echo "   详细信息: $detail" >&2
    fi
}

# 如果直接执行此脚本，显示帮助信息
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    echo "error-codes.sh - Code Committer Skill 退出码定义"
    echo ""
    echo "用法:"
    echo "  source scripts/error-codes.sh  # 在其他脚本中引用"
    echo ""
    echo "退出码分类（文档使用 3 位码，实际使用 2 位码）:"
    echo "  0/000  - 成功"
    echo "  1/001  - 带警告成功"
    echo "  20-29  - 依赖/配置错误 (2xx)"
    echo "  30-39  - Git 操作错误 (3xx)"
    echo "  40-49  - GitLab API 错误 (4xx)"
    echo "  50-59  - 飞书集成错误 (5xx)"
    echo "  60-69  - 内审检查错误 (6xx)"
    echo "  99/999 - 未知错误"
    echo ""
    echo "示例:"
    echo "  exit_with_error 203 \"未找到 GITLAB_PAT 环境变量\"  # 文档使用 3 位码"
    echo "  to_exit_code 503   # 输出: 53                      # 转换为实际退出码"
fi
