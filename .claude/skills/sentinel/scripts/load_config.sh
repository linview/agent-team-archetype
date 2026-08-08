#!/bin/bash
# ============================================================
# Sentinel 配置加载辅助脚本
# ============================================================
# 功能：从 .env.skill 加载环境配置
# 用法：source .claude/skills/sentinel/scripts/load_config.sh
# ============================================================

# 项目根目录（从脚本目录上 3 级）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
ENV_FILE="${PROJECT_ROOT}/.env.skill"

# 加载环境配置（从 .env.skill）
load_env_config() {
    local env=$1

    # 检查 .env.skill 是否存在
    if [[ ! -f "$ENV_FILE" ]]; then
        echo "⚠️  警告：配置文件不存在: $ENV_FILE"
        echo ""
        echo "请先创建配置文件："
        echo "  cat > $ENV_FILE <<EOF"
        echo "# Sentinel 配置 - $env 环境"
        echo ""
        echo "# API 配置"
        echo "export ${env^^}_API_URL=\"http://example.com:8082/api/v1\""
        echo ""
        echo "# 数据库配置"
        echo "export ${env^^}_DB_HOST=\"localhost\""
        echo "export ${env^^}_DB_PORT=\"5432\""
        echo "export ${env^^}_DB_NAME=\"app_db\""
        echo "export ${env^^}_DB_USER=\"postgres\""
        echo "export ${env^^}_DB_PASSWORD=\"your-password\""
        echo ""
        echo "# Kubernetes 配置（可选）"
        echo "export ${env^^}_KUBECONFIG=\"/path/to/kubeconfig\""
        echo "EOF"
        echo ""
        return 1
    fi

    # 从 .env.skill 读取配置（source 模式）
    local prefix
    case "$env" in
        dev)   prefix="DEV" ;;
        test)  prefix="TEST" ;;
        prod)  prefix="PROD" ;;
        *)
            echo "❌ 错误：不支持的环境: $env"
            return 1
            ;;
    esac

    # 读取配置变量
    local api_url db_host db_port db_name db_user db_password kubeconfig

    # Source .env.skill 获取变量
    source "$ENV_FILE"

    # 读取环境特定配置
    api_url="${prefix}_API_URL"
    db_host="${prefix}_DB_HOST"
    db_port="${prefix}_DB_PORT"
    db_name="${prefix}_DB_NAME"
    db_user="${prefix}_DB_USER"
    db_password="${prefix}_DB_PASSWORD"
    kubeconfig="${prefix}_KUBECONFIG"

    # 使用间接引用获取值
    api_url="${!api_url}"
    db_host="${!db_host}"
    db_port="${!db_port}"
    db_name="${!db_name}"
    db_user="${!db_user}"
    db_password="${!db_password}"
    kubeconfig="${!kubeconfig}"

    # 导出环境变量
    export SERVICE_API_URL="$api_url"
    export DB_HOST="$db_host"
    export DB_PORT="${db_port:-5432}"
    export DB_NAME="$db_name"
    export DB_USER="$db_user"
    export DB_PASSWORD="$db_password"

    # KUBECONFIG 可选
    if [[ "$KUBECONFIG" != "DISABLED" ]] && [[ -z "$KUBECONFIG" ]] && [[ -n "$kubeconfig" ]]; then
        export KUBECONFIG="$kubeconfig"
    fi

    # 如果设置为 "DISABLED"，则清除环境变量
    if [[ "$KUBECONFIG" == "DISABLED" ]]; then
        unset KUBECONFIG
    fi

    # 验证必需的环境变量
    if [[ -z "$SERVICE_API_URL" ]] || [[ -z "$DB_HOST" ]] || [[ -z "$DB_PASSWORD" ]]; then
        echo "⚠️  警告：配置文件中缺少必需的配置项（${prefix}_API_URL, ${prefix}_DB_HOST, ${prefix}_DB_PASSWORD）"
        echo "请检查配置文件：$ENV_FILE"
        return 1
    fi

    echo "✅ 已从 .env.skill 加载环境配置: $env"
    return 0
}

# 导出函数
export -f load_env_config
