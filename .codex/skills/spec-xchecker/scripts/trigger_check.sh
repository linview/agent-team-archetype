#!/bin/bash
# .codex/skills/spec-xchecker/trigger_check.sh
#
# Stop Hook 触发脚本：在 Codex session 结束时启动 spec-xchecker
#
# 用法:
#   HOOK_TYPE=stop_hook bash trigger_check.sh
#
# 环境变量:
#   HOOK_TYPE    - hook 类型（stop_hook 或 session_start_hook）
#   CODEX_PROJECT_DIR - 项目根目录

set -euo pipefail

PROJECT_DIR="${CODEX_PROJECT_DIR:-${CLAUDE_PROJECT_DIR:-$(pwd)}}"

# 获取 memory 目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/lib/get_memory_dir.sh"
MEMORY_DIR=$(get_memory_dir "${PROJECT_DIR}")

# spec-xchecker 专用目录
XCHECKER_DIR="${MEMORY_DIR}/spec-xchecker"
mkdir -p "${XCHECKER_DIR}"

# 状态文件
INDEX_FILE="${XCHECKER_DIR}/reports_index.json"
LAST_CHECK_TIME="${XCHECKER_DIR}/last_check_time.txt"
LAST_CHECKED_COMMIT="${XCHECKER_DIR}/last_checked_commit.txt"
DEBOUNCE_WINDOW=300  # 5分钟防抖

# 初始化索引文件
if [ ! -f "${INDEX_FILE}" ]; then
    echo '{"reports":[]}' > "${INDEX_FILE}"
fi

# 获取当前最新 commit
LATEST_COMMIT=$(git -C "${PROJECT_DIR}" rev-parse HEAD 2>/dev/null || echo "unknown")
CURRENT_TIME=$(date +%s)

# 防抖检查
if [ -f "${LAST_CHECK_TIME}" ]; then
    LAST_TIME=$(cat "${LAST_CHECK_TIME}")
    ELAPSED=$((CURRENT_TIME - LAST_TIME))

    if [ ${ELAPSED} -lt ${DEBOUNCE_WINDOW} ]; then
        LAST_COMMIT=$(cat "${LAST_CHECKED_COMMIT}" 2>/dev/null || echo "")
        if [ "${LAST_COMMIT}" = "${LATEST_COMMIT}" ]; then
            exit 0
        fi
    fi
fi

# 记录本次检查
echo "${CURRENT_TIME}" > "${LAST_CHECK_TIME}"
echo "${LATEST_COMMIT}" > "${LAST_CHECKED_COMMIT}"

# 创建输出目录
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_DIR="/tmp/xchecker/${TIMESTAMP}"
mkdir -p "${OUTPUT_DIR}"

# 写入初始状态文件
cat > "${OUTPUT_DIR}/state.json" <<EOF
{
  "status": "pending",
  "timestamp": "${TIMESTAMP}",
  "trigger_time": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "trigger_type": "${HOOK_TYPE:-stop_hook}",
  "commit": "${LATEST_COMMIT}",
  "memory_dir": "${MEMORY_DIR}"
}
EOF

# 更新索引文件（追加新记录）
REPORT_ENTRY=$(cat <<EOF
{
  "timestamp": "${TIMESTAMP}",
  "commit": "${LATEST_COMMIT}",
  "report_path": "${OUTPUT_DIR}/report.json",
  "trigger_time": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "trigger_type": "${HOOK_TYPE:-stop_hook}",
  "status": "pending",
  "notified": false
}
EOF
)

# 使用 jq 追加到索引文件
if command -v jq &> /dev/null; then
    jq --argjson new_entry "${REPORT_ENTRY}" '.reports += [$new_entry]' "${INDEX_FILE}" > "${INDEX_FILE}.tmp"
    mv "${INDEX_FILE}.tmp" "${INDEX_FILE}"
else
    echo "[spec-xchecker] 警告: jq 未安装，索引文件未更新" >&2
fi

# 后台执行本地检查脚本（120秒超时）
timeout 120s nohup python3 "${SCRIPT_DIR}/spec-xchecker.py" \
  --auto-mode \
  --format json \
  --output "${OUTPUT_DIR}/report.json" \
  > "${OUTPUT_DIR}/codex_session.log" 2>&1 &

CC_PID=$!
echo "{\"cc_pid\": ${CC_PID}}" >> "${OUTPUT_DIR}/state.json"

# 立即退出（允许 session 正常结束）
exit 0
