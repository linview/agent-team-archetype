# 非交互式使用示例

## 示例 1: 自动生成 Commit

```bash
source scripts/code-committer.sh
code_committer_commit --auto-generate --non-interactive

# 输出:
# test: Update test_login.py
# ✅ Commit 创建成功
```

## 示例 2: 推送远端（自动创建分支）

```bash
source scripts/code-committer.sh
code_committer_push \
    --branch feature/login \
    --create-if-not-exists \
    --non-interactive

# 输出:
# ℹ️  推送到远端: origin/feature/login
# ℹ️  远端分支不存在，将创建新分支
# ✅ 推送成功: origin/feature/login
```

## 示例 3: 创建 MR（一次性提供所有参数）

```bash
source scripts/code-committer.sh
code_committer_mr_create \
    --source-branch feature/login \
    --target-branch master \
    --mr-title "feat(auth): implement JWT authentication" \
    --feishu-task 6723548458 \
    --non-interactive

# 输出:
# ℹ️  自动检测目标分支: master
# ℹ️  正在验证飞书工作项 #6723548458...
# ✅ 工作项验证通过: "用户登录功能开发"
# ℹ️  正在创建 GitLab MR...
# ℹ️    源分支: feature/login
# ℹ️    目标分支: master
# ℹ️    标题: feat(auth): implement JWT authentication
# ✅ MR 创建成功: !123
#    https://git.example.com/.../-/merge_requests/123
```

## 示例 4: 一键提交+推送+创建 MR

```bash
source scripts/code-committer.sh

# 暂存变更
git add .

# 执行组合操作
code_committer_push_and_mr \
    --auto-generate \
    --mr-title "feat(auth): implement login" \
    --feishu-task 6723548458 \
    --non-interactive

# 输出:
# ℹ️  步骤 1/2: 推送到远端
# ℹ️  推送到远端并设置上游: origin/feature/auth
# ✅ 推送成功: origin/feature/auth
# ℹ️  步骤 2/2: 创建 MR
# ℹ️  自动检测目标分支: master
# ℹ️  正在验证飞书工作项 #6723548458...
# ✅ 工作项验证通过: "用户登录功能开发"
# ℹ️  正在创建 GitLab MR...
# ✅ MR 创建成功: !124
#    https://git.example.com/.../-/merge_requests/124
```

## 示例 5: 错误处理（退出码）

```bash
# 检查退出码
source scripts/code-committer.sh
code_committer_mr_create ... --non-interactive
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "成功"
elif [ $EXIT_CODE -eq 203 ]; then
    echo "PAT 未配置，请设置 GITLAB_PAT 环境变量"
elif [ $EXIT_CODE -eq 500 ]; then
    echo "飞书工作项验证失败，请检查工作项 ID"
else
    echo "未知错误: $EXIT_CODE"
fi
```
