#!/bin/bash
# Scrum Master 自动化工作流
# 当 docs/scrum/ 文件被修改时，自动审计元数据并渲染视图

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"

# 激活 Python 虚拟环境（如果存在）
if [ -f "$PROJECT_ROOT/.venv/bin/activate" ]; then
    source "$PROJECT_ROOT/.venv/bin/activate"
fi

# Step 1: 审计 Story/Epic 文件，生成 metadata.json
echo "[Scrum Master] 审计 docs/scrum/ 元数据..."
python3 "$SCRIPT_DIR/audit_metadata.py"

# Step 2: 从 metadata.json 渲染 KANBAN.md 和 DASHBOARD.md
echo "[Scrum Master] 渲染视图文件..."
python3 "$SCRIPT_DIR/render_views.py"

echo "[Scrum Master] ✅ 元数据审计和视图渲染完成"
echo "[Scrum Master] 📝 注意：metadata.json、KANBAN.md、DASHBOARD.md 需要单独提交"
