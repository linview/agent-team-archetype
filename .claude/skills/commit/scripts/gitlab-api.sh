#!/bin/bash
# gitlab-api.sh - Code Committer Skill GitLab API 封装
# Version: 1.0.0
# Description: 封装 GitLab API 操作，包括 MR 创建、标签获取等

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 引入错误码定义
# shellcheck source=scripts/error-codes.sh
source "${SCRIPT_DIR}/error-codes.sh"

# ============================================
# Credential 读取函数（自包含实现）
# ============================================

# 确保 .env.skill 在 .gitignore 中（自动添加）
ensure_env_skill_in_gitignore() {
    local proj_root="$1"
    local gitignore="$proj_root/.gitignore"

    # 如果 .gitignore 不存在，创建它
    if [ ! -f "$gitignore" ]; then
        echo "# Environment variables" > "$gitignore"
        echo ".env" >> "$gitignore"
        echo ".env.local" >> "$gitignore"
        echo ".env.skill           # Claude Code skill 专用配置文件" >> "$gitignore"
        echo "✅ 已创建 .gitignore 并添加 .env.skill" >&2
        return 0
    fi

    # 检查 .env.skill 是否已存在（允许后面有注释或空格）
    if grep -qE '^\s*\.env\.skill\b' "$gitignore" 2>/dev/null; then
        return 0  # 已存在，无需添加
    fi

    # 自动添加 .env.skill 到 .gitignore
    echo ".env.skill           # Claude Code skill 专用配置文件" >> "$gitignore"
    echo "✅ 已自动将 .env.skill 添加到 .gitignore" >&2
    return 0
}

# 检查 .env.skill 或 .env 文件是否在 .gitignore 中
is_env_in_gitignore() {
    local proj_root="$1"
    local env_file="${2:-.env.skill}"
    local gitignore="$proj_root/.gitignore"

    if [ ! -f "$gitignore" ]; then
        return 1
    fi

    # 精确匹配指定的文件（允许后面有注释），或匹配通配符 .env*
    if grep -qE "^${env_file}\\b|^\.env\*" "$gitignore" 2>/dev/null; then
        return 0
    fi

    return 1
}

# 从 .env 文件读取 credential（自动确保安全）
load_credential() {
    local key="$1"
    local proj_root="${2:-$(git rev-parse --show-toplevel 2>/dev/null)}"

    # 1. 环境变量
    local env_value
    env_value=$(printenv "$key" 2>/dev/null)
    if [ -n "$env_value" ]; then
        echo "$env_value"
        return 0
    fi

    # 2. .env.skill（自动确保 .gitignore 安全）
    if [ -n "$proj_root" ]; then
        local env_skill_file="$proj_root/.env.skill"
        if [ -f "$env_skill_file" ]; then
            # ⚠️ 自动确保安全：如果 .env.skill 不在 .gitignore，自动添加
            if ! is_env_in_gitignore "$proj_root" ".env.skill"; then
                ensure_env_skill_in_gitignore "$proj_root"
            fi

            local value
            value=$(grep -E "^${key}=" "$env_skill_file" 2>/dev/null | cut -d'=' -f2- | tr -d '[:space:]' | head -n1)
            if [ -n "$value" ]; then
                echo "$value"
                return 0
            fi
        fi

        # 3. .env（向后兼容）
        local env_file="$proj_root/.env"
        if [ -f "$env_file" ]; then
            if ! is_env_in_gitignore "$proj_root" ".env"; then
                echo "❌ 错误: .env 文件存在但未在 .gitignore 中，存在泄密风险！" >&2
                return 1
            fi

            local value
            value=$(grep -E "^${key}=" "$env_file" 2>/dev/null | cut -d'=' -f2- | tr -d '[:space:]' | head -n1)
            if [ -n "$value" ]; then
                echo "$value"
                return 0
            fi
        fi
    fi

    echo ""
    return 1
}

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
# GitLab 配置
# ============================================

# 从 git remote 推理 GitLab URL
# 输出: GitLab API 基础 URL（如 https://git.example.com）
gitlab_detect_url() {
    local remote_url
    remote_url=$(git remote get-url origin 2>/dev/null)

    if [ -z "$remote_url" ]; then
        return 1
    fi

    local gitlab_url

    # 解析不同格式的 remote URL
    if [[ "$remote_url" =~ ^git@([^:]+): ]]; then
        # SSH 格式: git@git.example.com:group/repo.git
        local host
        host=$(echo "$remote_url" | sed -E 's|.*@([^:]+):.*|\1|')
        gitlab_url="https://$host"
    elif [[ "$remote_url" =~ ^https:// ]]; then
        # HTTPS 格式: https://git.example.com/group/repo.git
        gitlab_url=$(echo "$remote_url" | sed -E 's|https://([^/]+).*|\1|')
    elif [[ "$remote_url" =~ ^http:// ]]; then
        # HTTP 格式: http://git.example.com/group/repo.git
        gitlab_url=$(echo "$remote_url" | sed -E 's|http://([^/]+).*|\1|')
    else
        return 1
    fi

    echo "$gitlab_url"
    return 0
}

# 获取 GitLab 项目路径
# 输出: 项目路径（如 group/repo）
gitlab_get_project_path() {
    local remote_url
    remote_url=$(git remote get-url origin 2>/dev/null)

    if [ -z "$remote_url" ]; then
        return 1
    fi

    local project_path

    # 去掉协议和域名，获取项目路径
    # SSH: git@git.example.com:group/repo.git -> group/repo
    # HTTPS: https://git.example.com/group/repo.git -> group/repo
    project_path=$(echo "$remote_url" | sed -E 's|.*:([^:]+/[^/]+).*|\1|' | sed 's|\.git$||')

    echo "$project_path"
    return 0
}

# 获取 GitLab PAT
gitlab_get_pat() {
    # 1. 从 .env.skill 或 .env 读取
    local pat
    pat=$(load_credential "GITLAB_PAT")
    if [ -n "$pat" ]; then
        echo "$pat"
        return 0
    fi

    # 2. 全局配置（向后兼容）
    local global_config="$HOME/.config/code-committer/config.yaml"
    if [ -f "$global_config" ]; then
        local config_pat
        config_pat=$(grep -oP 'pat:\s*\K[^[:space:]]+' "$global_config" 2>/dev/null | head -n1)
        if [ -n "$config_pat" ] && [ "$config_pat" != '""' ]; then
            echo "$config_pat"
            return 0
        fi
    fi

    # 3. 项目配置（向后兼容）
    local proj_root
    proj_root=$(git rev-parse --show-toplevel 2>/dev/null)
    if [ -n "$proj_root" ]; then
        local proj_config="$proj_root/.claude/code-committer.yaml"
        if [ -f "$proj_config" ]; then
            local config_pat
            config_pat=$(grep -oP 'pat:\s*\K[^[:space:]]+' "$proj_config" 2>/dev/null | head -n1)
            if [ -n "$config_pat" ] && [ "$config_pat" != '""' ]; then
                echo "$config_pat"
                return 0
            fi
        fi
    fi

    echo ""
    return 1
}

# 检查 PAT 配置
# 输出: 0 - 已配置, 203 - 未配置
gitlab_check_pat() {
    local pat
    pat=$(gitlab_get_pat)

    if [ -z "$pat" ]; then
        return 203
    fi

    return 0
}

# ============================================
# GitLab API 操作
# ============================================

# GitLab API 通用请求函数
# 参数: $1 - API 端点（如 /merge_requests）
#       $2 - HTTP 方法（GET, POST, PUT, DELETE）
#       $3 - 请求数据（可选，JSON 格式）
# 输出: API 响应（JSON 格式）
gitlab_api_request() {
    local endpoint="$1"
    local method="${2:-GET}"
    local data="${3:-}"

    local gitlab_url
    gitlab_url=$(gitlab_detect_url)

    if [ -z "$gitlab_url" ]; then
        exit_with_error 400 "无法推理 GitLab URL"
    fi

    local project_path
    project_path=$(gitlab_get_project_path)

    if [ -z "$project_path" ]; then
        exit_with_error 400 "无法获取项目路径"
    fi

    local pat
    pat=$(gitlab_get_pat)

    if [ -z "$pat" ]; then
        exit_with_error 203 "GitLab PAT 未配置"
    fi

    local url="$gitlab_url/api/v4/projects/$(echo "$project_path" | sed 's|/|%2F|g')$endpoint"

    # 构建 curl 命令
    local curl_opts=(-s -S -X "$method" \
        -H "PRIVATE-TOKEN: $pat" \
        -H "Content-Type: application/json")

    if [ -n "$data" ]; then
        curl_opts+=(-d "$data")
    fi

    # 发送请求
    curl "${curl_opts[@]}" "$url"
}

# 创建 MR
# 参数: $1 - 源分支
#       $2 - 目标分支
#       $3 - MR 标题
#       $4 - MR 描述（可选）
#       $5 - 标签（可选，逗号分隔）
# 输出: MR URL，失败时返回非零退出码
gitlab_create_mr() {
    local source_branch="$1"
    local target_branch="$2"
    local title="$3"
    local description="${4:-}"
    local labels="${5:-}"

    if [ -z "$source_branch" ] || [ -z "$target_branch" ] || [ -z "$title" ]; then
        exit_with_error 402 "创建 MR 缺少必要参数"
    fi

    info "正在创建 GitLab MR..."
    info "   源分支: $source_branch"
    info "   目标分支: $target_branch"
    info "   标题: $title"

    # 构建请求体
    local request_body
    request_body=$(cat << EOF
{
  "source_branch": "$source_branch",
  "target_branch": "$target_branch",
  "title": "$title",
  "remove_source_branch": false
}
EOF
)

    # 添加描述
    if [ -n "$description" ]; then
        # 转义换行符和引号
        local escaped_desc
        escaped_desc=$(echo "$description" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | tr '\n' '\\n')
        request_body=$(echo "$request_body" | sed 's/}$/,\n  "description": "'"${escaped_desc}"'"/')
    fi

    # 添加标签
    if [ -n "$labels" ]; then
        # 将逗号分隔的标签转换为数组
        local labels_array
        labels_array=$(echo "$labels" | sed 's/,/", "/g' | sed 's/\([^,]*\)/"\1"/g' | tr '\n' ',' | sed 's/,$//')
        request_body=$(echo "$request_body" | sed 's/}$/,\n  "labels": ['${labels_array}']}/')
    fi

    # 发送请求
    local response
    response=$(gitlab_api_request "/merge_requests" "POST" "$request_body")
    local exit_code=$?

    if [ $exit_code -ne 0 ]; then
        exit_with_error 402 "GitLab API 请求失败"
    fi

    # 检查响应中的错误
    if [[ "$response" =~ \"error\" ]] || [[ "$response" =~ \"message\":.*\"(already exists|已存在)\" ]]; then
        # MR 可能已存在
        if [[ "$response" =~ \"web_url\" ]]; then
            # 尝试提取已存在的 MR URL
            local mr_url
            mr_url=$(echo "$response" | grep -oP '"web_url":\s*"\K[^"]*' | head -n1)
            warning "MR 可能已存在"
            echo "$mr_url"
            return 0
        fi
        exit_with_error 402 "创建 MR 失败: $response"
    fi

    # 提取 MR 信息
    local mr_iid mr_url web_url
    mr_iid=$(echo "$response" | grep -oP '"iid":\s*\K[0-9]+' | head -n1)
    web_url=$(echo "$response" | grep -oP '"web_url":\s*"\K[^"]*' | head -n1)

    if [ -n "$mr_iid" ] && [ -n "$web_url" ]; then
        success "MR 创建成功: !$mr_iid"
        echo "$web_url"
        return 0
    else
        exit_with_error 402 "创建 MR 失败，无法解析响应"
    fi
}

# 获取 MR URL
# 参数: $1 - MR IID
#       $2 - 源分支（可选，用于精确匹配）
# 输出: MR Web URL
gitlab_get_mr_url() {
    local mr_iid="$1"
    local source_branch="${2:-}"

    local gitlab_url
    gitlab_url=$(gitlab_detect_url)

    if [ -z "$gitlab_url" ]; then
        return 1
    fi

    local project_path
    project_path=$(gitlab_get_project_path)

    if [ -z "$project_path" ]; then
        return 1
    fi

    # 构建查询参数
    local query_params=""
    if [ -n "$source_branch" ]; then
        query_params="?source_branch=$source_branch"
    fi

    local endpoint="/merge_requests${query_params}"

    local response
    response=$(gitlab_api_request "$endpoint" "GET")

    # 从响应中提取 MR URL
    local mr_url
    mr_url=$(echo "$response" | grep -oP '"web_url":\s*"\K[^"]*' | head -n1)

    if [ -n "$mr_url" ]; then
        echo "$mr_url"
        return 0
    fi

    return 1
}

# 获取项目标签列表
# 输出: 标签列表（逗号分隔）
gitlab_get_labels() {
    local response
    response=$(gitlab_api_request "/labels?per_page=100" "GET")

    # 提取标签名称
    local labels
    labels=$(echo "$response" | grep -oP '"name":\s*"\K[^"]*' | tr '\n' ',' | sed 's/,$//')

    echo "$labels"
}

# 根据变更内容匹配合适的标签
# 参数: $1 - 变更文件列表
gitlab_match_labels() {
    local changed_files="$1"

    local labels=()

    # 根据文件路径推断标签
    if echo "$changed_files" | grep -qE '\.(md|txt|rst)'; then
        labels+=("documentation")
    fi

    if echo "$changed_files" | grep -qE 'test_|_test\.|spec'; then
        labels+=("testing")
    fi

    if echo "$changed_files" | grep -qE '\.(json|yaml|yml|toml)'; then
        labels+=("configuration")
    fi

    # 输出逗号分隔的标签列表
    local IFS=','
    echo "${labels[*]}"
}

# 获取 MR 模板
# 参数: $1 - 模板类型（feature, bugfix, hotfix, refactoring, docs, ci-cd）
# 输出: 模板内容
mr_get_template() {
    local template_type="$1"
    local script_dir
    script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

    local template_file="$script_dir/../references/mr-templates/${template_type}.md"

    if [ -f "$template_file" ]; then
        cat "$template_file"
        return 0
    fi

    # 如果模板文件不存在，返回默认模板
    cat << 'EOF'
## 功能说明
（描述本次变更的目的）

## 变更内容
- 变更点 1
- 变更点 2

## 测试
- [ ] 单元测试通过
- [ ] SIT 测试通过
EOF
}

# ============================================
# 辅助函数
# ============================================

# 显示 GitLab 配置信息
show_gitlab_config() {
    local gitlab_url
    gitlab_url=$(gitlab_detect_url)

    local project_path
    project_path=$(gitlab_get_project_path)

    echo "📋 GitLab 配置信息:"
    echo "   GitLab URL: $gitlab_url"
    echo "   项目路径: $project_path"

    local has_pat
    if gitlab_check_pat; then
        echo "   PAT 状态: ✅ 已配置"
    else
        echo "   PAT 状态: ❌ 未配置"
    fi
    echo ""
}

# 如果直接执行此脚本，显示帮助信息
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    echo "gitlab-api.sh - Code Committer Skill GitLab API 封装"
    echo ""
    echo "用法:"
    echo "  source scripts/gitlab-api.sh"
    echo ""
    echo "函数:"
    echo "  gitlab_detect_url                          - 推理 GitLab URL"
    echo "  gitlab_get_project_path                     - 获取项目路径"
    echo "  gitlab_get_pat                              - 获取 GitLab PAT"
    echo "  gitlab_create_mr <source> <target> <title> - 创建 MR"
    echo "  gitlab_get_mr_url <mr_iid> <source_branch> - 获取 MR URL"
    echo "  gitlab_get_labels                           - 获取项目标签"
    echo "  gitlab_match_labels <files>                 - 匹配标签"
    echo "  mr_get_template <type>                       - 获取 MR 模板"
    echo ""
    echo "示例:"
    echo "  gitlab_create_mr feat/login master \"feat(auth): login\""
    echo "  gitlab_get_labels"
fi
