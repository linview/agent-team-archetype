#!/bin/bash
# .claude/skills/spec-xchecker/notify_pending_reports.sh
#
# SessionStart Hook 通知脚本：在 Claude session 启动时通知上次检查结果
#
# 用法:
#   bash notify_pending_reports.sh

set -euo pipefail

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"

# 获取 memory 目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/utils/get_memory_dir.sh"
MEMORY_DIR=$(get_memory_dir "${PROJECT_DIR}")
INDEX_FILE="${MEMORY_DIR}/spec-xchecker/reports_index.json"

# 检查索引文件是否存在
if [ ! -f "${INDEX_FILE}" ]; then
    exit 0
fi

# 检查 jq 是否可用
if ! command -v jq &> /dev/null; then
    echo "[spec-xchecker] 警告: jq 未安装，无法读取报告" >&2
    exit 0
fi

# 查找未通知且已完成的报告
PENDING_REPORTS=$(jq -r '
  .reports[] |
  select(.status == "completed" and .notified == false) |
  "\(.timestamp)|\(.report_path)|\(.commit)"
' "${INDEX_FILE}")

if [ -z "${PENDING_REPORTS}" ]; then
    exit 0
fi

# 通知用户
echo ""
echo "========================================="
echo "🔍 [spec-xchecker] 发现 $(echo "${PENDING_REPORTS}" | wc -l) 份待审查报告"
echo "========================================="
echo ""

# 收集需要标记为已通知的 timestamps
NOTIFIED_TIMESTAMPS=""

while IFS='|' read -r timestamp report_path commit; do
    if [ -f "${report_path}" ]; then
        # 读取报告摘要
        SUMMARY=$(jq -r '
          "模式: \(.mode | ascii_upcase)\n" +
          "总检查项: \(.summary.total_checks)\n" +
          "通过: \(.summary.passed) (\(.summary.passed * 100 / .summary.total_checks)%)\n" +
          "失败: \(.summary.failed) (P0: \(.summary.p0_issues), P1: \(.summary.p1_issues), P2: \(.summary.p2_issues))"
        ' "${report_path}")

        echo "✅ 审查完成 (Commit: ${commit:0:8})"
        echo "📊 ${SUMMARY}"
        echo "📄 完整报告: ${report_path}"
        echo ""

        # 收集 timestamp
        NOTIFIED_TIMESTAMPS="${NOTIFIED_TIMESTAMPS}${timestamp}"
    fi
done <<< "${PENDING_REPORTS}"

# 批量更新 notified 状态（使用 Python）
if [ -n "${NOTIFIED_TIMESTAMPS}" ]; then
    python3 -c "
import json
import sys

timestamps = '${NOTIFIED_TIMESTAMPS}'.split() if '${NOTIFIED_TIMESTAMPS}' else []
with open('${INDEX_FILE}', 'r') as f:
    data = json.load(f)

for report in data['reports']:
    if report['timestamp'] in timestamps:
        report['notified'] = True

with open('${INDEX_FILE}', 'w') as f:
    json.dump(data, f, indent=2)
" 2>/dev/null || echo "[spec-xchecker] 警告: 无法更新 notified 状态" >&2
fi

exit 0
