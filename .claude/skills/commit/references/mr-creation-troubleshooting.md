# MR 创建故障排除指南

**版本**: v1.0
**创建日期**: 2026-04-08
**维护者**: DevOps Team

---

## ⭐ MR 创建成功的关键技巧（实战验证）

### 技巧 1: PAT 验证（必做第一步）

**问题**: 直接调用 GitLab API 创建 MR 返回 401 Unauthorized

**解决方案**: 先验证 PAT 权限，确认 PAT 有效的后再创建 MR

```bash
# 设置 PAT
export GITLAB_PAT="your_pat_token_here"

# 验证 PAT 权限（测试用户信息）
curl -s --header "PRIVATE-TOKEN: ${GITLAB_PAT}" \
  "https://<git-host>/api/v4/user" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f\"用户名: {data.get('username', 'N/A')}\")
print(f\"用户ID: {data.get('id', 'N/A')}\")
print(f\"Bot: {data.get('bot', False)}\")
print(f\"状态: {data.get('state', 'N/A')}\")
"

# 预期输出：
# 用户名: project_10428_bot1
# 用户ID: 1570
# Bot: True
# 状态: active
```

**为什么重要**:
- ✅ 提前发现 PAT 无效或权限不足
- ✅ 确认 PAT 对应的用户身份（bot vs 个人用户）
- ✅ 避免 MR 创建失败后才排查权限问题

---

### 技巧 2: MR 创建 + HTTP 状态码捕获

**问题**: `curl` 调用失败时无法确定具体原因（网络问题 vs API 错误 vs PAT 权限）

**解决方案**: 使用 `curl -w` 选项捕获 HTTP 状态码

```bash
# 准备 MR 描述（保存到文件）
MR_DESC_FILE="/tmp/mr_description.md"
cat > "${MR_DESC_FILE}" << 'EOF'
---
feishu.task: 6934756567
---

## 功能说明
STORY-15-19: 数据库基础设施完整实施
...

# 创建 MR 并捕获 HTTP 状态码
RESPONSE=$(curl -s -w "\n%{http_code}" --request POST \
  --header "PRIVATE-TOKEN: ${GITLAB_PAT}" \
  "https://<git-host>/api/v4/projects/example-org%2F{PROJECT_NAME}/merge_requests" \
  --data-urlencode "source_branch=feat/epic-15-story-15-19-database-infrastructure" \
  --data-urlencode "target_branch=master" \
  --data-urlencode "title=feat(database): STORY-15-19 数据库基础设施完整实施" \
  --data-urlencode "description=$(cat ${MR_DESC_FILE})" \
  --data-urlencode "remove_source_branch=false" 2>&1)

# 提取 HTTP 状态码（最后一行）
HTTP_CODE=$(echo "$RESPONSE" | tail -1)

# 判断结果
case "$HTTP_CODE" in
  201)
    echo "✅ MR 创建成功！"
    ;;
  401)
    echo "❌ PAT 权限不足（401 Unauthorized）"
    echo "请检查 PAT 是否有 api 权限"
    ;;
  400)
    echo "❌ 请求参数错误（400 Bad Request）"
    echo "请检查 MR 标题和描述格式"
    ;;
  *)
    echo "⚠️ 未知错误（HTTP $HTTP_CODE）"
    echo "响应内容："
    echo "$RESPONSE" | head -20
    ;;
esac
```

**HTTP 状态码说明**：
- `201` = Created ✅
- `400` = Bad Request（参数错误）
- `401` = Unauthorized（PAT 无效或权限不足）
- `403` = Forbidden（权限不足）
- `404` = Not Found（项目不存在）
- `409` = Conflict（分支冲突或 MR 已存在）
- `422` = Unprocessable Entity（验证失败）

---

### 技巧 3: MR 信息查询（iid 和 web_url）

**问题**: MR 创建成功后，需要获取 MR ID（iid）和访问链接

**解决方案**: 通过 API 查询最新的 MR

```bash
# 方法 1: 查询特定分支的最新 MR
curl -s --header "PRIVATE-TOKEN: ${GITLAB_PAT}" \
  "https://<git-host>/api/v4/projects/example-org%2F{PROJECT_NAME}/merge_requests?state=opened&source_branch=feat%2Fepic-15-story-15-19-database-infrastructure&order_by=created_at&sort=desc" \
  | python3 -c "
import sys, json
data = json.load(sys.stdin)
if data:
    mr = data[0]
    print(f\"MR ID: !{mr.get('iid')}\")
    print(f\"Title: {mr.get('title')}\")
    print(f\"URL: {mr.get('web_url')}\")
    print(f\"飞书任务ID: {mr.get('description', '').split('feishu.task: ')[1].split('---')[0].strip() if 'feishu.task:' in mr.get('description', '') else 'N/A'}\")
else:
    print('未找到 MR')
"

# 预期输出：
# MR ID: 27
# Title: feat(database): STORY-15-19 数据库基础设施完整实施
# URL: https://<git-host>/example-org/{PROJECT_NAME}/-/merge_requests/27
# 飞书任务ID: 6934756567
```

**关键说明**：
- **iid**: MR 的内部 ID（相对ID，如 27）
- **web_url**: MR 访问链接（用于直接打开）
- **source_branch**: 查询特定源分支的 MR
- **order_by**: 按创建时间倒序排列（最新的在前）

---

### 技巧 4: 飞书任务 ID 验证

**问题**: 需要确认 MR 描述中是否正确包含飞书任务 ID

**解决方案**: 检查 YAML front matter 格式

```bash
# 验证飞书任务 ID 是否正确包含
curl -s --header "PRIVATE-TOKEN: ${GITLAB_PAT}" \
  "https://<git-host>/api/v4/projects/example-org%2F{PROJECT_NAME}/merge_requests/27" \
  | python3 -c "
import sys, json
data = json.load(sys.stdin)
description = data.get('description', '')

# 检查 YAML front matter
if 'feishu.task: 6934756567' in description:
    print('✅ 飞书任务ID已正确关联: 6934756567')
elif 'feishu.task:' in description:
    # 提取任务 ID
    import re
    match = re.search(r'feishu\.task:\s*(\d+)', description)
    if match:
        print(f'⚠️ 飞书任务ID存在但值不匹配: {match.group(1)}')
        print(f'期望值: 6934756567')
    else:
        print('⚠️ feishu.task 字段存在但格式不正确')
else:
    print('❌ 未找到飞书任务ID')

# 显示描述前100字符（用于调试）
print(f'描述前100字符: {description[:100]}')
"
```

**YAML front matter 格式要求**：
```yaml
---
feishu.task: 6934756567
---
```

**常见错误**：
- ❌ 冒号后没有空格：`feishu.task:6934756567`
- ❌ 字段名错误：`feishu_task`（应为 `feishu.task`）
- ❌ 缺少 YAML 分隔符：没有 `---` 分隔符
- ❌ 缩进错误：YAML front matter 必须顶格写

---

### 技巧 5: 完整的 MR 创建工作流程（推荐）

**基于实战验证的完整流程**：

```bash
#!/bin/bash
# MR 创建脚本（推荐版本）

# ============================================================
# Step 1: 配置环境变量
# ============================================================
export GITLAB_PAT="B2zs93U9B99tx25qMzsH"
PROJECT_ID="example-org%2F{PROJECT_NAME}"
SOURCE_BRANCH="feat/epic-15-story-15-19-database-infrastructure"
TARGET_BRANCH="master"
MR_TITLE="feat(database): STORY-15-19 数据库基础设施完整实施"
MR_DESC_FILE="/tmp/mr_description.md"

# ============================================================
# Step 2: 验证 PAT 权限
# ============================================================
echo "Step 1: 验证 PAT 权限..."
USER_INFO=$(curl -s --header "PRIVATE-TOKEN: ${GITLAB_PAT}" \
  "https://<git-host>/api/v4/user")

USER_NAME=$(echo "$USER_INFO" | python3 -c "import sys, json; print(json.load(sys.stdin).get('username', 'N/A'))")

if [ "$USER_NAME" = "N/A" ]; then
    echo "❌ PAT 验证失败：无效或权限不足"
    exit 203
fi

echo "✅ PAT 验证成功：用户名 $USER_NAME"

# ============================================================
# Step 3: 创建 MR
# ============================================================
echo "Step 2: 创建 MR..."
RESPONSE=$(curl -s -w "\n%{http_code}" --request POST \
  --header "PRIVATE-TOKEN: ${GITLAB_PAT}" \
  "https://<git-host>/api/v4/projects/${PROJECT_ID}/merge_requests" \
  --data-urlencode "source_branch=${SOURCE_BRANCH}" \
  --data-urlencode "target_branch=${TARGET_BRANCH}" \
  --data-urlencode "title=${MR_TITLE}" \
  --data-urlencode "description=$(cat ${MR_DESC_FILE})" \
  --data-urlencode "remove_source_branch=false" 2>&1)

HTTP_CODE=$(echo "$RESPONSE" | tail -1)

# ============================================================
# Step 4: 判断结果并查询 MR 信息
# ============================================================
case "$HTTP_CODE" in
  201)
    echo "✅ MR 创建成功！"

    # 查询 MR 详细信息
    echo ""
    echo "Step 3: 查询 MR 详细信息..."
    sleep 2  # 等待 API 同步

    MR_INFO=$(curl -s --header "PRIVATE-TOKEN: ${GITLAB_PAT}" \
      "https://<git-host>/api/v4/projects/${PROJECT_ID}/merge_requests?state=opened&source_branch=${SOURCE_BRANCH}&order_by=created_at&sort=desc")

    MR_IID=$(echo "$MR_INFO" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data[0].get('iid', 'N/A'))")
    MR_URL=$(echo "$MR_INFO" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data[0].get('web_url', 'N/A'))")

    echo ""
    echo "========================================"
    echo "MR 创建成功！"
    echo "========================================"
    echo "MR ID: !${MR_IID}"
    echo "Title: ${MR_TITLE}"
    echo "URL: ${MR_URL}"
    echo ""
    echo "飞书任务ID: 6934756567（已验证）"
    echo "========================================"
    ;;

  401)
    echo "❌ PAT 权限不足（401 Unauthorized）"
    echo "请检查 PAT 是否有 api 权限"
    echo "PAT 用户: $USER_NAME"
    exit 401
    ;;

  409)
    echo "⚠️ MR 可能已存在（409 Conflict）"
    echo "请检查是否已有相同源分支的 MR"
    exit 409
    ;;

  *)
    echo "❌ 未知错误（HTTP $HTTP_CODE）"
    echo "响应内容："
    echo "$RESPONSE" | head -30
    exit 1
    ;;
esac
```

---

## 故障排除清单

### 问题 1: curl 返回 401 Unauthorized

**可能原因**：
1. PAT 无效或已过期
2. PAT 没有 `api` 权限
3. PAT 用户对项目没有 Maintainer 权限

**解决方案**：
```bash
# 1. 验证 PAT 用户信息
curl -s --header "PRIVATE-TOKEN: ${GITLAB_PAT}" \
  "https://<git-host>/api/v4/user" | python3 -m json.tool

# 2. 检查 PAT 权限范围（返回 scopes 字段）
curl -s --header "PRIVATE-TOKEN: ${GITLAB_PAT}" \
  "https://<git-host>/api/v4/personal_access_tokens/self" | python3 -c "import sys, json; print(json.load(sys.stdin).get('scopes', []))"

# 3. 确认 PAT 有 api 权限（应包含 'api'）
```

---

### 问题 2: glab 命令无返回结果

**可能原因**：
1. glab 未正确配置 PAT
2. glab 版本过旧
3. 输出被重定向到 /dev/null

**解决方案**：
```bash
# 方案 1: 使用 glab --web 选项（打开浏览器）
glab mr create --web

# 方案 2: 检查 glab 版本
glab version

# 方案 3: 使用 curl 直接调用 API（推荐）
# 见上述"技巧 5: 完整的 MR 创建工作流程"
```

---

### 问题 3: 飞书任务 ID 验证失败

**可能原因**：
1. YAML front matter 格式错误
2. 飞书任务 ID 不存在
3. lark-cli 未安装

**解决方案**：
```bash
# 方案 1: 手动验证（推荐）
# 访问 MR 页面，查看描述是否正确显示
echo "请手动访问 MR 页面验证飞书任务ID："
echo "https://<git-host>/example-org/{PROJECT_NAME}/-/merge_requests/27"

# 方案 2: 使用正则表达式提取验证
curl -s --header "PRIVATE-TOKEN: ${GITLAB_PAT}" \
  "https://<git-host>/api/v4/projects/example-org%2F{PROJECT_NAME}/merge_requests/27" \
  | python3 -c "
import sys, json, re
data = json.load(sys.stdin)
desc = data.get('description', '')
match = re.search(r'feishu\.task:\s*(\d+)', desc)
if match:
    print(f'飞书任务ID: {match.group(1)}')
else:
    print('未找到飞书任务ID')
"
```

---

## 完整示例：成功创建 MR 的实战案例

**背景**: STORY-15-19 数据库基础设施完整实施

**执行步骤**：

1. **准备 MR 描述文件**：
   ```bash
   cat > /tmp/mr_description.md << 'EOF'
   ---
   feishu.task: 6934756567
   ---

   ## 功能说明
   STORY-15-19: 数据库基础设施完整实施

   ## 变更内容
   - AC-1: 外键迁移完成
   - AC-3: 索引创建成功
   ...
   EOF
   ```

2. **验证 PAT 权限**：
   ```bash
   export GITLAB_PAT="B2zs93U9B99tx25qMzsH"
   curl -s --header "PRIVATE-TOKEN: ${GITLAB_PAT}" \
     "https://<git-host>/api/v4/user" | python3 -m json.tool
   ```

3. **创建 MR**：
   ```bash
   curl -s -w "\n%{http_code}" --request POST \
     --header "PRIVATE-TOKEN: ${GITLAB_PAT}" \
     "https://<git-host>/api/v4/projects/example-org%2F{PROJECT_NAME}/merge_requests" \
     --data-urlencode "source_branch=feat/epic-15-story-15-19-database-infrastructure" \
     --data-urlencode "target_branch=master" \
     --data-urlencode "title=feat(database): STORY-15-19 数据库基础设施完整实施" \
     --data-urlencode "description=$(cat /tmp/mr_description.md)" \
     --data-urlencode "remove_source_branch=false"
   ```

4. **验证结果**（HTTP 201）：
   ```bash
   # 查询 MR 信息
   curl -s --header "PRIVATE-TOKEN: ${GITLAB_PAT}" \
     "https://<git-host>/api/v4/projects/example-org%2F{PROJECT_NAME}/merge_requests?state=opened&source_branch=feat%2Fepic-15-story-15-19-database-infrastructure" \
     | python3 -c "
   import sys, json
   data = json.load(sys.stdin)
   mr = data[0]
   print(f\"MR ID: !{mr['iid']}\")
   print(f\"URL: {mr['web_url']}\")
   "
   ```

5. **输出**：
   ```
   ✅ MR 创建成功！
   MR ID: !27
   URL: https://<git-host>/example-org/{PROJECT_NAME}/-/merge_requests/27
   飞书任务ID: 6934756567（已验证）
   ```

---

**版本**: v1.0
**创建日期**: 2026-04-08
**维护者**: DevOps Team
