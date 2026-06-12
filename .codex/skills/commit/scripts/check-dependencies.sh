#!/bin/bash
# check-dependencies.sh - Code Committer Skill 依赖检查
# Version: 1.0.0
# Description: 检查所需的依赖是否已安装

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
# 依赖检查函数
# ============================================

# 检查 git
check_git() {
    if ! command -v git &> /dev/null; then
        error "git 未安装"
        exit_with_error 200
    fi

    # 检查 git 版本
    local git_version=$(git --version 2>/dev/null)
    success "git 已安装: $git_version"
    return 0
}

# 检查 lark-cli
check_lark_cli() {
    if ! command -v lark-cli &> /dev/null; then
        warning "lark-cli 未安装，飞书功能将不可用"
        info "安装方法: npm install -g lark-cli"
        info "GitHub: https://github.com/larksuite/cli"
        return 201
    fi

    # 检查 lark-cli 版本
    local lark_version=$(lark-cli --version 2>/dev/null)
    success "lark-cli 已安装: $lark_version"
    return 0
}

# 检查 curl（用于 GitLab API）
check_curl() {
    if ! command -v curl &> /dev/null; then
        warning "curl 未安装，GitLab API 功能可能受影响"
        info "安装方法: apt-get install curl 或 yum install curl"
        return 1
    fi

    success "curl 已安装"
    return 0
}

# 检查 jq（用于 JSON 处理）
check_jq() {
    if ! command -v jq &> /dev/null; then
        warning "jq 未安装，JSON 解析功能可能受限"
        info "安装方法: apt-get install jq 或 yum install jq"
        return 1
    fi

    success "jq 已安装"
    return 0
}

# 检查 glab（可选）
check_glab() {
    if ! command -v glab &> /dev/null; then
        info "glab 未安装（可选）"
        info "如需使用 glab CLI，请访问: https://gitlab.com/gitlab-org/cli"
        return 1
    fi

    local glab_version=$(glab --version 2>/dev/null | head -n1)
    success "glab 已安装: $glab_version"
    return 0
}

# ============================================
# 主检查函数
# ============================================

# 执行所有检查
check_all() {
    local has_warning=false

    echo "🔍 检查 Code Committer Skill 依赖..."
    echo ""

    # 必需依赖
    check_git

    # 可选依赖
    check_lark_cli
    local lark_status=$?

    check_curl
    check_jq
    check_glab

    echo ""
    echo "📋 依赖检查摘要:"
    echo "   ✅ git: 已安装"
    if [ $lark_status -eq 0 ]; then
        echo "   ✅ lark-cli: 已安装"
    else
        echo "   ⚠️  lark-cli: 未安装（飞书功能不可用）"
        has_warning=true
    fi

    if [ "$has_warning" = true ]; then
        echo ""
        warning "部分可选依赖未安装，某些功能可能不可用"
        return 0
    fi

    success "所有依赖检查通过"
    return 0
}

# 快速检查（仅检查必需依赖）
check_required_only() {
    check_git
    # lark-cli 虽然是飞书功能必需，但不是所有功能都需要
    # 所以不在这里强制检查
    return 0
}

# ============================================
# 命令行接口
# ============================================

# 显示帮助信息
show_help() {
    cat << EOF
check-dependencies.sh - Code Committer Skill 依赖检查

用法:
  ./check-dependencies.sh [选项]

选项:
  --all, -a           检查所有依赖（包括可选）
  --required, -r      仅检查必需依赖
  --help, -h          显示此帮助信息

示例:
  ./check-dependencies.sh --all
  ./check-dependencies.sh -a

退出码:
  0   - 所有检查通过（或有可选依赖未安装）
  200 - git 未安装
  201 - lark-cli 未安装（仅 --all 时）
EOF
}

# 主函数
main() {
    local check_mode="required"

    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            --all|-a)
                check_mode="all"
                shift
                ;;
            --required|-r)
                check_mode="required"
                shift
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            *)
                error "未知选项: $1"
                show_help
                exit 1
                ;;
        esac
    done

    # 执行检查
    if [ "$check_mode" = "all" ]; then
        check_all
    else
        check_required_only
    fi
}

# 如果直接执行此脚本
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
