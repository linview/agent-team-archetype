# 交互式使用示例

## 示例 1: 自动生成 Commit 并推送

```bash
# 1. 暂存变更
git add src/login.py tests/test_login.py

# 2. 使用 skill 自动生成 commit message
source scripts/code-committer.sh
code_committer_commit --auto-generate

# 输出示例:
# ✅ Commit 创建成功
#    test: Update test_login.py
```

## 示例 2: 创建关联飞书工作项的 MR（交互式）

```bash
# 使用 skill 创建 MR
source scripts/code-committer.sh
code_committer_mr_create

# 交互流程:
# ℹ️  目标分支是 origin/master，确认吗？[Y/n]
#    Y
# ℹ️  检测到 $GITLAB_PAT 已设置
# ℹ️  是否关联飞书工作项？[y/N]
#    y
# 请输入飞书工作项 ID:
#    6723548458
# ℹ️  正在验证飞书工作项 #6723548458...
# ✅ 工作项验证通过: "用户登录功能开发"
# 请输入 MR Title (Conventional Commits 格式):
#    feat(auth): implement JWT authentication
# ℹ️  准备创建 MR，确认？
#    Y
# ✅ MR 创建成功: !123
#    https://<git-host>/.../-/merge_requests/123
```

## 示例 3: 一键提交+推送+创建 MR

```bash
source scripts/code-committer.sh

# 暂存变更
git add .

# 一键执行
code_committer_push_and_mr --auto-generate \
    --mr-title "feat(auth): implement login" \
    --feishu-task 6723548458

# 输出示例:
# ℹ️  步骤 1/2: 推送到远端
# ✅ 推送成功: origin/feature/login
# ℹ️  步骤 2/2: 创建 MR
# ✅ MR 创建成功: !124
#    https://<git-host>/.../-/merge_requests/124
```
