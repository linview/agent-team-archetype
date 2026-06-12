#!/bin/bash
# remote-handler.sh - Code Committer Skill 远端分支处理
# Version: 1.0.0
# Description: 处理 Git 远端分支操作，包括推送、创建分支、检测默认分支

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
# Git 仓库检测
# ============================================

# 检查是否在 Git 仓库中
check_git_repo() {
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        exit_with_error 300 "当前目录不在 Git 仓库中"
    fi
}

# 获取当前分支名
get_current_branch() {
    git rev-parse --abbrev-ref HEAD 2>/dev/null || echo ""
}

# 获取远端 URL
get_remote_url() {
    git remote get-url origin 2>/dev/null || echo ""
}

# ============================================
# 远端分支操作
# ============================================

# 检查远端分支是否存在
# 参数: $1 - 远端名称（默认 origin）
#       $2 - 分支名
# 输出: 0 - 存在, 1 - 不存在
remote_check_exists() {
    local remote="${1:-origin}"
    local branch="$2"

    if [ -z "$branch" ]; then
        return 1
    fi

    # 使用 ls-remote 检查远端分支是否存在
    if git ls-remote --heads "$remote" "$branch" 2>/dev/null | grep -q .; then
        return 0
    else
        return 1
    fi
}

# 推送到远端
# 参数: $1 - 远端名称（默认 origin）
#       $2 - 分支名（默认当前分支）
#       $3 - 是否创建不存在的分支（true/false，默认 true）
# 输出: 退出码 0 - 成功, 303 - Push 失败, 305 - 分支创建失败
remote_push() {
    local remote="${1:-origin}"
    local branch="${2:-$(get_current_branch)}"
    local create_if_not_exists="${3:-true}"

    if [ -z "$branch" ]; then
        exit_with_error 304 "无法确定分支名"
    fi

    info "推送到远端: $remote/$branch"

    # 检查远端分支是否存在
    if ! remote_check_exists "$remote" "$branch"; then
        if [ "$create_if_not_exists" = "true" ]; then
            info "远端分支不存在，将创建新分支"
            # 设置上游分支，会自动创建远端分支
            git push -u "$remote" "$branch" || exit_with_error 303
        else
            exit_with_error 305 "远端分支 $remote/$branch 不存在"
        fi
    else
        # 远端分支存在，直接推送
        git push "$remote" "$branch" || exit_with_error 303
    fi

    success "推送成功: $remote/$branch"
    return 0
}

# 推送并设置上游（简化版本）
# 参数: $1 - 远端名称（默认 origin）
#       $2 - 分支名（默认当前分支）
remote_push_with_upstream() {
    local remote="${1:-origin}"
    local branch="${2:-$(get_current_branch)}"

    if [ -z "$branch" ]; then
        exit_with_error 304 "无法确定分支名"
    fi

    info "推送到远端并设置上游: $remote/$branch"

    # 使用 -u 参数设置上游
    git push -u "$remote" "$branch" || exit_with_error 303

    success "推送成功: $remote/$branch"
    return 0
}

# ============================================
# 默认分支检测
# ============================================

# 获取默认目标分支（自动检测 master/main）
# 输出: 分支名（master 或 main）
remote_get_default_target() {
    # 优先级: 远程 main > 远程 master > 本地 HEAD

    # 检查远端是否有 main 分支
    if git ls-remote --heads origin main 2>/dev/null | grep -q .; then
        echo "main"
        return 0
    fi

    # 检查远端是否有 master 分支
    if git ls-remote --heads origin master 2>/dev/null | grep -q .; then
        echo "master"
        return 0
    fi

    # 检查本地默认分支（symbolic ref）
    local default_ref
    default_ref=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null)
    if [ -n "$default_ref" ]; then
        echo "$default_ref" | sed 's@^refs/remotes/origin/@@'
        return 0
    fi

    # 默认返回 master
    echo "master"
    return 0
}

# 检查分支是否是主分支（master/main）
# 参数: $1 - 分支名
# 输出: 0 - 是主分支, 1 - 不是主分支
is_main_branch() {
    local branch="$1"
    local main_branch
    main_branch=$(remote_get_default_target)

    if [ "$branch" = "$main_branch" ] || [ "$branch" = "main" ] || [ "$branch" = "master" ]; then
        return 0
    fi

    return 1
}

# ============================================
# 分支信息获取
# ============================================

# 获取远端分支列表
# 参数: $1 - 远端名称（默认 origin）
remote_list_branches() {
    local remote="${1:-origin}"
    git ls-remote --heads "$remote" 2>/dev/null | sed 's/.*\t\///' | sort
}

# 获取本地分支列表
local_list_branches() {
    git for-each-ref --format='%(refname:short)' refs/heads/ 2>/dev/null | sort
}

# 获取跟踪分支信息
remote_get_tracking_branch() {
    local branch="${1:-$(get_current_branch)}"

    if [ -z "$branch" ]; then
        echo ""
        return 1
    fi

    # 获取当前分支的跟踪分支
    local tracking
    tracking=$(git config --get "branch.$branch.remote")

    if [ -n "$tracking" ]; then
        echo "$tracking/$(git config --get "branch.$branch.merge" | sed 's/refs\/heads\///')"
        return 0
    fi

    echo ""
    return 1
}

# ============================================
# 分支比较
# ============================================

# 检查本地分支是否领先/落后远端
# 参数: $1 - 分支名（默认当前分支）
#       $2 - 远端名称（默认 origin）
remote_compare_branch() {
    local branch="${1:-$(get_current_branch)}"
    local remote="${2:-origin}"

    if [ -z "$branch" ]; then
        return 1
    fi

    # 获取远程引用
    local remote_branch="refs/remotes/$remote/$branch"

    if ! git rev-parse --verify "$remote_branch" > /dev/null 2>&1; then
        info "远端分支 $remote/$branch 不存在"
        return 1
    fi

    # 比较提交
    local ahead behind
    ahead=$(git rev-list --count "$remote_branch"..HEAD 2>/dev/null || echo "0")
    behind=$(git rev-list --count HEAD.."$remote_branch" 2>/dev/null || echo "0")

    if [ "$ahead" -gt 0 ] && [ "$behind" -gt 0 ]; then
        warning "分支 $branch 相对于远端: 领先 $ahead 个提交，落后 $behind 个提交"
    elif [ "$ahead" -gt 0 ]; then
        info "分支 $branch 相对于远端: 领先 $ahead 个提交"
    elif [ "$behind" -gt 0 ]; then
        info "分支 $branch 相对于远端: 落后 $behind 个提交"
    else
        success "分支 $branch 与远端保持一致"
    fi

    return 0
}

# ============================================
# 辅助函数
# ============================================

# 显示分支状态摘要
show_branch_status() {
    local current_branch
    current_branch=$(get_current_branch)

    local tracking
    tracking=$(remote_get_tracking_branch "$current_branch")

    echo "📋 分支状态摘要:"
    echo "   当前分支: $current_branch"

    if [ -n "$tracking" ]; then
        echo "   跟踪分支: $tracking"
    else
        echo "   跟踪分支: 无"
    fi

    local default_target
    default_target=$(remote_get_default_target)
    echo "   默认目标: $default_target"
    echo ""
}

# 如果直接执行此脚本，显示帮助信息
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    echo "remote-handler.sh - Code Committer Skill 远端分支处理"
    echo ""
    echo "用法:"
    echo "  source scripts/remote-handler.sh"
    echo ""
    echo "函数:"
    echo "  remote_check_exists <remote> <branch>       - 检查远端分支是否存在"
    echo "  remote_push <remote> <branch> <create>     - 推送到远端"
    echo "  remote_get_default_target                  - 获取默认目标分支"
    echo "  is_main_branch <branch>                     - 检查是否是主分支"
    echo "  remote_list_branches <remote>               - 列出远端分支"
    echo "  remote_compare_branch <branch> <remote>     - 比较本地和远端分支"
    echo ""
    echo "示例:"
    echo "  remote_push origin feature/login"
    echo "  remote_push origin feature/login true"
    echo "  remote_get_default_target  # 输出: master 或 main"
fi
