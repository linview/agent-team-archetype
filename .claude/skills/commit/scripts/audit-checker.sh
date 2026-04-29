#!/bin/bash
# audit-checker.sh - Code Committer Skill 内审规则检查
# Version: 1.0.0
# Description: 检查敏感信息、测试覆盖、文档更新等

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 引入错误码定义
# shellcheck source=scripts/error-codes.sh
source "${SCRIPT_DIR}/error-codes.sh"

# ============================================
# 内审规则检查函数
# ============================================

# 检查敏感信息
# 参数: $1 - 检查模式（cached/working, 默认 cached）
# 输出: 0 - 无敏感信息, 600 - 检测到敏感信息
audit_check_sensitive() {
    local mode="${1:-cached}"
    local git_args=()

    if [ "$mode" = "cached" ]; then
        git_args=(--cached)
    elif [ "$mode" = "working" ]; then
        git_args=()
    fi

    # 获取变更的文件
    local changed_files
    changed_files=$(git diff "${git_args[@]}" --name-only --diff-filter=ACM)

    if [ -z "$changed_files" ]; then
        return 0
    fi

    local sensitive_found=false
    local sensitive_patterns=(
        "password.*=.*['\"]"
        "passwd.*=.*['\"]"
        "api[_-]?key.*=.*['\"]"
        "apikey.*=.*['\"]"
        "secret.*=.*['\"]"
        "token.*=.*['\"]"
        "\\b[a-f0-9]{32,}\\b"  # 可能是 32+ 位十六进制字符串（token/hash）
        "\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}"  # IP 地址
    )

    # 检查暂存区内容
    local diff_content
    diff_content=$(git diff "${git_args[@]}")

    for pattern in "${sensitive_patterns[@]}"; do
        if echo "$diff_content" | grep -iE "$pattern" > /dev/null; then
            sensitive_found=true
            local match_lines
            match_lines=$(echo "$diff_content" | grep -iE "$pattern" | head -n 3)
            error "检测到潜在敏感信息 (模式: $pattern)"
            echo "$match_lines"
            break
        fi
    done

    if [ "$sensitive_found" = true ]; then
        return 600
    fi

    return 0
}

# 检查测试覆盖
# 参数: $1 - 检查模式（cached/working, 默认 cached）
# 输出: 0 - 有测试文件, 601 - 缺少测试文件
audit_check_test_coverage() {
    local mode="${1:-cached}"
    local git_args=()

    if [ "$mode" = "cached" ]; then
        git_args=(--cached)
    elif [ "$mode" = "working" ]; then
        git_args=()
    fi

    # 获取变更的文件
    local changed_files
    changed_files=$(git diff "${git_args[@]}" --name-only --diff-filter=ACM)

    if [ -z "$changed_files" ]; then
        return 0
    fi

    local has_test=false
    local has_source=false

    for file in $changed_files; do
        if [[ "$file" =~ test|spec ]]; then
            has_test=true
        elif [[ "$file" =~ \.(py|js|ts|java|go|rs|c|h|cpp|cc|sh) ]]; then
            has_source=true
        fi
    done

    # 如果有源代码变更但没有测试文件变更，发出警告
    if [ "$has_source" = true ] && [ "$has_test" = false ]; then
        warning "未检测到测试文件变更"
        info "建议添加对应的测试文件"
        return 601
    fi

    return 0
}

# 检查文档更新
# 参数: $1 - 检查模式（cached/working, 默认 cached）
# 输出: 0 - 文档已更新或无需更新, 602 - 文档未更新
audit_check_documentation() {
    local mode="${1:-cached}"
    local git_args=()

    if [ "$mode" = "cached" ]; then
        git_args=(--cached)
    elif [ "$mode" = "working" ]; then
        git_args=()
    fi

    # 获取变更的文件
    local changed_files
    changed_files=$(git diff "${git_args[@]}" --name-only --diff-filter=ACM)

    if [ -z "$changed_files" ]; then
        return 0
    fi

    # 检查是否有源代码变更
    local has_source=false
    local has_docs=false

    for file in $changed_files; do
        if [[ "$file" =~ \.(py|js|ts|java|go|rs|c|h|cpp|cc|sh) ]]; then
            has_source=true
        elif [[ "$file" =~ (README|CHANGELOG|docs/) ]]; then
            has_docs=true
        fi
    done

    # 如果有源代码变更但没有文档更新，发出警告
    if [ "$has_source" = true ] && [ "$has_docs" = false ]; then
        local proj_root
        proj_root=$(git rev-parse --show-toplevel 2>/dev/null)

        # 检查项目中是否有 README
        if [ -n "$proj_root" ] && [ -f "$proj_root/README.md" ]; then
            warning "源代码有变更，但 README.md 未更新"
            info "建议检查是否需要更新文档"
            return 602
        fi
    fi

    return 0
}

# 执行所有检查
# 参数: $1 - 检查模式（cached/working, 默认 cached）
# 输出: 0 - 所有检查通过, 非零 - 有检查失败
audit_check_all() {
    local mode="${1:-cached}"
    local exit_code=0

    echo "🔍 执行内审检查..."
    echo ""

    # 敏感信息检查
    info "检查敏感信息..."
    if audit_check_sensitive "$mode"; then
        success "   敏感信息检查通过"
    else
        error "   敏感信息检查失败"
        exit_code=600
    fi

    # 测试覆盖检查
    info "检查测试覆盖..."
    if audit_check_test_coverage "$mode"; then
        success "   测试覆盖检查通过"
    else
        warning "   测试覆盖检查发出警告"
        # 测试覆盖警告不设置退出码
    fi

    # 文档更新检查
    info "检查文档更新..."
    if audit_check_documentation "$mode"; then
        success "   文档更新检查通过"
    else
        warning "   文档更新检查发出警告"
        # 文档更新警告不设置退出码
    fi

    echo ""
    if [ $exit_code -eq 0 ]; then
        success "所有内审检查通过"
    else
        error "部分内审检查失败"
    fi

    return "$exit_code"
}

# Pre-commit hook 执行
audit_run_pre_commit() {
    echo "🔍 执行 pre-commit 内审检查..."

    # 执行所有检查（检查暂存区）
    audit_check_all "cached"
    local result=$?

    if [ $result -eq 0 ]; then
        return 0
    fi

    # 如果有检查失败，询问是否继续
    echo ""
    echo "是否继续提交？[y/N]"
    read -r answer
    if [[ "$answer" =~ ^[Yy]$ ]]; then
        info "继续提交"
        return 0
    else
        info "已取消提交"
        return 1
    fi
}

# 安装 git hooks
# 参数: $1 --force 强制覆盖已存在的 hooks
audit_install_hooks() {
    local force_install=false

    if [ "$1" = "--force" ]; then
        force_install=true
    fi

    local proj_root
    proj_root=$(git rev-parse --show-toplevel 2>/dev/null)

    if [ -z "$proj_root" ]; then
        exit_with_error 300 "不在 Git 仓库中"
    fi

    local hooks_dir="$proj_root/.git/hooks"
    local skill_script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

    # 检查 hooks 目录是否存在
    if [ ! -d "$hooks_dir" ]; then
        error "Git hooks 目录不存在: $hooks_dir"
        return 1
    fi

    # 创建 pre-commit hook
    local pre_commit_hook="$hooks_dir/pre-commit"

    if [ -f "$pre_commit_hook" ] && [ "$force_install" = false ]; then
        warning "pre-commit hook 已存在"
        info "使用 --force 覆盖已存在的 hook"
        return 1
    fi

    info "安装 pre-commit hook..."

    cat > "$pre_commit_hook" << 'EOF'
#!/bin/bash
# Pre-commit hook for Code Committer Skill
# 自动执行内审检查

echo "🔍 执行 pre-commit 内审检查..."

# 调用 audit-checker.sh
SCRIPT_DIR="$(dirname "$0")"
"$SCRIPT_DIR/../../scripts/audit-checker.sh" audit-run-pre-commit

# 检查退出码
if [ $? -ne 0 ]; then
    echo ""
    echo "⚠️  Pre-commit check failed, commit aborted."
    echo "   Use --no-verify to skip this check."
    exit 1
fi
EOF

    chmod +x "$pre_commit_hook"

    success "pre-commit hook 安装成功"
    info "   Hook 位置: $pre_commit_hook"
    echo ""
    info "提示: 使用 'git commit --no-verify' 跳过 pre-commit 检查"

    return 0
}

# ============================================
# 辅助函数
# ============================================

# 显示检查配置
show_audit_config() {
    echo "📋 内审检查配置:"
    echo "   敏感信息检查: 启用"
    echo "   测试覆盖检查: 启用"
    echo "   文档更新检查: 启用"
    echo ""
}

# 如果直接执行此脚本，显示帮助信息
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    echo "audit-checker.sh - Code Committer Skill 内审规则检查"
    echo ""
    echo "用法:"
    echo "  ./audit-checker.sh <command> [options]"
    echo ""
    echo "命令:"
    echo "  check-sensitive      检查敏感信息"
    echo "  check-test-coverage 检查测试覆盖"
    echo "  check-documentation   检查文档更新"
    echo "  check-all             执行所有检查"
    echo "  audit-run-pre-commit  Pre-commit hook 执行"
    echo "  install-hooks         安装 git hooks"
    echo ""
    echo "选项:"
    echo "  --mode <mode>        检查模式 (cached/working)"
    echo "  --force              强制覆盖已存在的 hook"
    echo ""
    echo "示例:"
    echo "  ./audit-checker.sh check-all --mode cached"
    echo "  ./audit-checker.sh install-hooks --force"
fi
