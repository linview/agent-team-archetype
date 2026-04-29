#!/bin/bash
# ============================================================
# Regular Checker - 定期巡检执行脚本
# ============================================================
# 功能：执行 Resource Meter 服务的定期巡检
# 用法：./run_inspection.sh <LEVEL> <ENV>
# 示例：./run_inspection.sh standard prod
# ============================================================

set -e  # 遇到错误立即退出

# ============================================================
# 参数解析
# ============================================================

LEVEL=${1:-sanity}            # 巡检级别：smoke, sanity, full
ENV=${2:-dev}                   # 环境：dev, test, prod
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
REPORT_DIR="test_reports/inspection"
REPORT_FILE="${REPORT_DIR}/inspection_${LEVEL}_${ENV}_${TIMESTAMP}.md"

# ============================================================
# 创建报告目录
# ============================================================

mkdir -p "$REPORT_DIR"

# 归档旧报告（保留 7 天）
find "$REPORT_DIR" -name "inspection_*.md" -mtime +7 -delete 2>/dev/null || true

# ============================================================
# 打印巡检信息
# ============================================================

echo "=========================================="
echo "Resource Meter 定期巡检"
echo "=========================================="
echo "环境: $ENV"
echo "级别: $LEVEL"
echo "时间: $(date)"
echo ""

# 检查环境变量
if [[ -z "$RESOURCE_METER_API_URL" ]]; then
    echo "❌ 错误：环境变量 RESOURCE_METER_API_URL 未设置"
    echo ""
    echo "请先设置环境变量："
    echo "  export RESOURCE_METER_API_URL=\"http://localhost:8082/api/v1\""
    echo "  export DB_HOST=\"127.0.0.10\""
    echo "  export DB_PORT=\"32432\""
    echo "  export DB_NAME=\"event_db\""
    echo "  export DB_USER=\"postgres\""
    echo "  export DB_PASSWORD=\"post@1234.com\""
    exit 1
fi

echo "📍 API URL: $RESOURCE_METER_API_URL"
echo "📍 数据库: ${DB_HOST:-localhost}:${DB_PORT:-5433}/${DB_NAME:-event_db-dev}"

# 检查 KUBECONFIG 文件是否存在（用于降级判断）
# ⚠️ 支持通过 KUBECONFIG="DISABLED" 禁用 K8s 测试
if [[ -n "$KUBECONFIG" && "$KUBECONFIG" != "DISABLED" && -f "$KUBECONFIG" ]]; then
  echo "📍 KUBECONFIG: $KUBECONFIG (已配置)"
  KUBECONFIG_AVAILABLE="true"
else
  echo "📍 KUBECONFIG: 未配置 (将跳过需要 K8s 的测试)"
  KUBECONFIG_AVAILABLE="false"
fi
echo ""

# ============================================================
# 根据级别选择测试套件
# ============================================================

case $LEVEL in
  smoke)
    echo "🔍 执行冒烟测试（API Smoke Tests）..."
    TEST_SUITES="tests/api/api_smoke.py"
    MAX_TIME=30
    ;;
  sanity)
    echo "🔍 执行健全性测试（API + 核心 SIT/UAT 只读）..."
    # KUBECONFIG 降级：检查 KUBECONFIG 文件是否存在
    if [[ "$KUBECONFIG_AVAILABLE" == "true" ]]; then
      TEST_SUITES="tests/api/api_smoke.py tests/sit/test_data_quality_validation.py tests/sit/test_data_quality_for_story_15_18.py tests/sit/test_sit_15_19.py tests/uat/test_gpu_accuracy_mock.py tests/uat/test_story_15_18_e2e.py tests/uat/test_uat_15_19.py"
      echo "  ✓ KUBECONFIG 已配置，运行完整 SIT/UAT 测试"
    else
      TEST_SUITES="tests/api/api_smoke.py"
      echo "  ⚠️  KUBECONFIG 未配置，仅运行 API 测试（跳过需要 K8s 的 SIT/UAT 测试）"
    fi
    MAX_TIME=300
    ;;
  full)
    echo "🔍 执行完整测试（API + SIT + UAT）..."
    TEST_SUITES="tests/api/ tests/sit/ tests/uat/test_gpu_accuracy.py"
    MAX_TIME=600
    ;;
  *)
    echo "❌ 无效的巡检级别: $LEVEL"
    echo "支持的级别: smoke, sanity, full"
    exit 1
    ;;
esac

echo ""

# ============================================================
# 运行测试
# ============================================================

echo "=========================================="
echo "开始执行测试..."
echo "=========================================="
echo ""

# 记录开始时间
START_TIME=$(date +%s)

# JUnit XML 报告文件路径（用于生成 Markdown 报告）
JUNIT_XML="${REPORT_DIR}/junit_${LEVEL}_${ENV}_${TIMESTAMP}.xml"

# 根据级别设置 pytest 超时参数
PYTEST_TIMEOUT_ARGS=""
case $LEVEL in
  full)  PYTEST_TIMEOUT_ARGS="--timeout=600" ;;  # 10 分钟
  sanity) PYTEST_TIMEOUT_ARGS="--timeout=300" ;;  # 5 分钟
esac

# 运行 pytest（使用 JUnit XML 记录测试结果）
if uv run pytest $TEST_SUITES \
  -v \
  --tb=short \
  $PYTEST_TIMEOUT_ARGS \
  --junitxml="$JUNIT_XML"; then
    TEST_RESULT="✅ 通过"
    EXIT_CODE=0
else
    TEST_RESULT="❌ 失败"
    EXIT_CODE=1
fi

# 记录结束时间
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo ""
echo "=========================================="
echo "巡检完成"
echo "=========================================="
echo "结果: $TEST_RESULT"
echo "耗时: ${DURATION} 秒"
echo "报告: $REPORT_FILE"
echo ""

# ============================================================
# 生成 Markdown 详细报告（从 JUnit XML）
# ============================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ -f "$JUNIT_XML" ]]; then
    echo "📝 生成 Markdown 报告..."
    uv run python3 "$SCRIPT_DIR/generate_md_report.py" \
        "$JUNIT_XML" \
        "$REPORT_FILE" \
        "$ENV" \
        "$LEVEL" \
        "$RESOURCE_METER_API_URL" \
        "${DB_HOST:-localhost}:${DB_PORT:-5433}/${DB_NAME:-event_db-dev}" \
        "$DURATION"

    # 清理 JUnit XML 文件
    rm -f "$JUNIT_XML"

    # 复制报告到 test_reports/regression/ 目录（用于自动循环任务）
    echo "📋 开始复制报告到 regression 目录..."
    REGRESSION_REPORT_DIR="test_reports/regression"
    mkdir -p "$REGRESSION_REPORT_DIR"
    cp "$REPORT_FILE" "$REGRESSION_REPORT_DIR/"
    echo "✅ 报告已复制到 $REGRESSION_REPORT_DIR/"
else
    echo "⚠️  警告: JUnit XML 文件未找到，生成简化报告"
    cat > "$REPORT_FILE" <<EOF
# Resource Meter 定期巡检报告

**环境**: $ENV
**级别**: $LEVEL
**时间**: $(date '+%Y-%m-%d %H:%M:%S')
**结果**: $TEST_RESULT
**耗时**: ${DURATION} 秒

## 环境信息

- **API URL**: $RESOURCE_METER_API_URL
- **数据库**: ${DB_HOST:-localhost}:${DB_PORT:-5433}/${DB_NAME:-event_db-dev}

## ⚠️ 注意

测试执行失败，无法生成详细的测试结果报告。请检查日志获取更多信息。
EOF
fi

# ============================================================
# 输出报告摘要
# ============================================================

echo "=========================================="
echo "报告摘要"
echo "=========================================="
echo "Markdown 报告: $REPORT_FILE"
echo ""

# ============================================================
# 返回退出码
# ============================================================

exit $EXIT_CODE
