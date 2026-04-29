---
name: commit
description: "代码提交与 MR 创建技能 - 自动生成语义化 commit message、创建符合规范的 GitLab Merge Request、验证飞书工作项关联。当用户提到 Git 提交、commit、push、推送代码、创建 MR、创建 PR、合并请求、或需要提交代码、推送代码、创建 MR/PR 时，必须使用此技能。支持交互式（对话）和非交互式（参数）两种模式。"
version: "2.1"
author: DevTools Team <devtools@example.com>
license: Proprietary
tags:
  - devops
  - git
  - gitlab
  - feishu
---

# Commit Skill

企业级 Git 提交和 MR 创建技能，支持自动生成语义化 commit message、创建符合规范的 MR、验证飞书工作项关联。

## 核心职责

1. **代码提交**：自动生成语义化 commit message，基于代码变更分析
2. **推送代码**：推送到远端仓库，支持自动创建远端分支
3. **MR 创建**：创建符合 Conventional Commits 规范的 GitLab MR
4. **工作项验证**：验证飞书项目工作项关联，确保可追溯性
5. **内审检查**：提交前检查敏感信息、测试覆盖、文档更新

---

## 🚨 铁律：MR 创建前必须同步目标分支（强制执行）

**⚠️ 创建 MR 之前，必须先同步目标分支的代码！！！没有 conflict 才能创建 MR！**

**标准工作流程**（强制执行）：

```bash
# Step 1: 同步目标分支（必须！）
git fetch origin <target-branch>

# Step 2: Rebase 到最新目标分支（必须！）
git rebase origin/<target-branch>

# Step 3: 检查是否有冲突
git status

# Step 4: 只有在没有冲突的情况下，才能：
#    - 推送代码
#    - 创建 MR
```

**检查清单**（强制执行）：
- [ ] 目标分支已同步（`git fetch origin <target-branch>`）
- [ ] 已 rebase 到最新目标分支（`git rebase origin/<target-branch>`）
- [ ] 无冲突（`git status` 显示 clean）
- [ ] 变更列表正确（`git diff --name-only origin/<target-branch>...HEAD`）
- [ ] 提交历史正确（`git log --oneline origin/<target-branch>..HEAD`）

**只有以上全部满足，才能创建 MR！**

**Why**: 避免重复提交、错误的 diff、不必要的冲突

**典型后果**:
- MR 包含已合并到目标分支的变更
- 需要强制 rebase 修复，增加工作量
- 影响代码审查效率和 CI/CD 流程

---

## ⚠️ 环境配置管理

**设计原则**:
- ✅ **SKILL.md**: 存储可移植的代码提交流程和最佳实践
- ✅ **.env.skill**: 存储项目特定凭证信息（GitLab PAT、飞书 auth_key 等）
- ❌ **禁止**: 将具体凭证值硬编码在 SKILL.md 中

**凭证信息配置**:

项目根目录的 `.env.skill` 文件会保留此技能需要的凭证信息：

```bash
# GitLab Personal Access Token
GITLAB_PAT=glpat-xxxxxxxxxxxxx

# 飞书认证密钥
FEISHU_AUTH_KEY=cli_xxxxxxxxxxxxxx

# Git Host 实例地址（可选，默认从 git remote 自动检测）
# 支持 GitLab、GitHub、Gitea 等平台
# GITLAB_URL=https://gitlab.example.com
# GITHUB_TOKEN=ghp_xxxxxxxxxxxxx

# 飞书项目 ID（可选，用于工作项验证）
FEISHU_PROJECT_ID=xxxxxxxxxxxxx
```

**部署前验证**:
1. 读取项目根目录 `.env.skill` 文件获取凭证信息
2. 验证 GitLab PAT 是否有效
3. 验证飞书 auth_key 是否可用
4. 确认凭证有足够的权限（git write、feishu project read）

**注意**: `.env.skill` 已在 `.gitignore` 中，不应提交到 Git 仓库

---

## 核心功能

### 1. Commit 自动生成

基于代码变更自动生成语义化 commit message：

- 分析文件列表 + code diff + 工作上下文
- 输出 ≤1/2 屏幕的精简描述
- **不强制 Conventional Commits 格式**（避免 semantic_release 版本爆炸）
- 支持动态上下文注入（加载项目最近 commits 匹配风格）

### 2. Push 远端

支持推送到远端仓库：

- 默认使用 `origin/<branch>` 命名
- 远端分支不存在时自动创建
- 自动检测默认目标分支（master/main）

### 3. MR 创建

创建符合规范的 GitLab MR：

- **MR Title**：遵循 Conventional Commits 格式 `type(scope): summary<30字符`
- **MR Description**：包含飞书工作项元数据（YAML front matter 格式）
- 支持交互式（可选对话）和非交互式（一次性参数）两种模式

### 4. 飞书工作项验证

验证飞书项目工作项关联：

- 检查 YAML front matter 格式
- 使用 lark-cli 验证工作项 ID 是否存在
- **⚠️ 强制要求：必须要求用户提供关联的"飞书工作项 uid"**
- 非交互模式：验证失败直接报错退出
- 交互模式：提示补正，阻止创建

**重要说明**：
- 飞书工作项 uid 是飞书项目管理系统中的唯一标识符
- 创建 MR 时必须关联有效的飞书工作项 uid（数字格式，如 6934756567）
- 不得使用占位符、默认值或跳过此验证步骤
- 如果用户无法提供有效的 uid，应阻止创建 MR 并说明原因

### 5. 内审规则检查

执行代码提交前的内审检查：

- 敏感信息检查（密钥、密码、IP 地址等）
- 测试覆盖检查（测试文件是否存在或变更）
- 文档更新检查

---

## Commit 规则

**📌 详细提交约定**：参见 [references/commit-conventions.md](references/commit-conventions.md)

**自由格式**：不强制 Conventional Commits，commit message 可以自由编写。

**自动生成**：基于代码变更自动生成语义化 message，参考项目最近的 commits 风格。

---

## MR 规范

**📌 MR 模板**：
- [Feature MR 模板](references/mr-templates/feature.md)
- [Bugfix MR 模板](references/mr-templates/bugfix.md)
- [Hotfix MR 模板](references/mr-templates/hotfix.md)
- [Refactoring MR 模板](references/mr-templates/refactoring.md)
- [Documentation MR 模板](references/mr-templates/docs.md)
- [CI/CD MR 模板](references/mr-templates/ci-cd.md)

### MR Title 格式

```
type(scope): summary
```

- **type**: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert
- **scope**: 影响范围（可选）
- **summary**: 简短描述（<30 字符）

### MR Description 格式

```yaml
---
feishu.task: 6723548458
---

## 功能说明
（功能描述）

## 变更内容
- 变更点 1
- 变更点 2

## 测试
- [ ] 单元测试通过
- [ ] SIT 测试通过
```

**重要规则**：
1. YAML front matter 必须在描述开头
2. 字段名固定为 `feishu.task`
3. 冒号后必须有空格
4. 工作项 ID 是数字格式（如 6723548458）

---

## 工作模式

**📌 详细使用示例**：
- 交互式模式：参见 [examples/interactive-usage.md](examples/interactive-usage.md)
- 非交互式模式：参见 [examples/non-interactive-usage.md](examples/non-interactive-usage.md)

### 交互式模式

交互式模式提供对话式流程，每个步骤都有默认值，用户可以确认或修改：

1. 确认目标分支（自动检测 master/main）
2. 检查 PAT 配置
3. **输入飞书工作项 uid（⚠️ 强制要求）**
4. **验证飞书工作项 uid 有效性**
5. 生成/确认 MR Title
6. 确认创建 MR

**⚠️ 重要：飞书工作项 uid 是必填项**
- 不得使用占位符、默认值或跳过此步骤
- 如果用户无法提供有效的 uid，应阻止创建 MR 并说明原因
- 必须使用 lark-cli 或手动方式验证 uid 存在性

### 非交互式模式

非交互式模式通过命令行参数一次性提供所有信息，适合自动化脚本：

```bash
# 自动生成 commit
git add <files>
commit.sh --auto-generate --non-interactive

# 推送代码
push.sh --branch feature/login --remote origin --create-if-not-exists --non-interactive

# 创建 MR
mr.sh create \
  --source-branch feat/login \
  --target-branch master \
  --mr-title "feat(auth): implement login" \
  --feishu-task 6723548458 \
  --non-interactive

# ⚠️ 注意：--feishu-task 参数是必填项
# 如果用户未提供，必须明确提示并提供有效的飞书工作项 uid
```

---

## 错误处理

### 退出码系统

使用 3 位数字退出码（000-999）：

- **0xx**: 成功/信息
- **2xx**: 依赖/配置错误
- **3xx**: Git 操作错误
- **4xx**: GitLab API 错误
- **5xx**: 飞书集成错误
- **6xx**: 内审检查错误
- **9xx**: 未知错误

### 交互式 vs 非交互式错误处理

| 场景 | 交互式 | 非交互式 |
|------|--------|----------|
| PAT 未配置 | 提示配置指导，等待输入 | 输出错误，退出码 203 |
| 工作项验证失败 | 提示补正，阻止创建 | 输出错误，退出码 500 |
| GitLab API 错误 | 显示错误，询问重试 | 输出错误，退出码 402 |
| 内审检查失败 | 警告，询问是否继续 | 输出警告，继续创建 |

---

## 配置

**📌 配置文件示例**：参见 [config/code-committer.yaml](config/code-committer.yaml)

### PAT 配置优先级

1. 环境变量 `GITLAB_PAT`
2. 配置文件 `~/.config/commit/config.yaml`
3. 项目配置 `.claude/commit.yaml`
4. 运行时交互输入（仅交互式模式）

### 配置文件示例

```yaml
gitlab:
  pat: ""  # 留空表示使用环境变量
  auto_detect_url: true

feishu:
  require_validation: true
  auth_identity: "user"

audit:
  check_sensitive_data: true
  check_test_coverage: false
  check_documentation: true

commit:
  max_length_lines: 12
  include_file_summary: true
  load_recent_commits: true
  check_claude_md: true
```

---

## 依赖要求

**📌 可用脚本**：
- `scripts/commit-generator.sh`：自动生成 commit message
- `scripts/feishu-validator.sh`：验证飞书工作项
- `scripts/audit-checker.sh`：执行审计检查
- `scripts/error-codes.sh`：错误码定义
- `scripts/gitlab-api.sh`：GitLab API 操作
- `scripts/remote-handler.sh`：远端仓库操作
- 其他辅助脚本位于 `scripts/` 目录

**系统依赖**：
- **git**: 版本控制（必需）
- **lark-cli**: 飞书 CLI（飞书功能必需）
  - 安装: `npm install -g lark-cli`
  - GitHub: https://github.com/larksuite/cli

---

## 使用示例

### 场景 1: 自动生成 commit 并推送

```bash
# 暂存变更
git add src/login.py tests/test_login.py

# 自动生成 commit message
commit.sh --auto-generate

# 推送到远端
push.sh --create-if-not-exists
```

### 场景 2: 创建关联飞书工作项的 MR

```bash
# 非交互式
mr.sh create \
  --source-branch feat/login \
  --target-branch master \
  --mr-title "feat(auth): implement JWT authentication" \
  --feishu-task 6723548458 \
  --non-interactive

# 交互式
mr.sh create
# (按提示输入)
```

### 场景 3: 一键提交+推送+创建 MR

```bash
push-and-mr.sh \
  --feishu-task 6723548458 \
  --non-interactive
```

---

## 内审检查

**📌 详细审计检查清单**：参见 [references/audit-checklist.md](references/audit-checklist.md)

### 敏感信息检查

检测以下模式并提供警告：

- `password.*=`
- `api[_-]?key.*=`
- `secret.*=`
- IP 地址格式

### 测试覆盖检查

检查变更中是否包含测试文件：

- 检查文件名是否包含 `test` 或 `spec`
- 不实际运行测试，仅检查文件是否存在或变更

### 文档更新检查

检查相关文档是否需要更新：

- README.md
- API 文档
- 变更日志

---

## 最佳实践

**📌 详细故障排除指南**: 参见 [references/mr-creation-troubleshooting.md](references/mr-creation-troubleshooting.md)

### MR 创建成功的关键技巧

**核心技巧**：
1. **⚠️ 同步目标分支**（铁律）：`git fetch origin <target-branch>` && `git rebase origin/<target-branch>`
2. **PAT 验证**: 先验证 PAT 权限，避免 401 错误
3. **HTTP 状态码捕获**: 使用 `curl -w` 捕获状态码，判断创建结果
4. **MR 信息查询**: 通过 API 查询 MR 的 iid 和 web_url
5. **飞书任务 ID 验证**: 检查 YAML front matter 格式（`feishu.task: <uid>`）
6. **完整工作流程**: 同步目标分支 → PAT 验证 → 创建 MR → 查询信息 → 验证结果

### 常见错误

**🚨 MR 包含重复的文件变更**（铁律违反）:
- **原因**: 创建 MR 前未同步目标分支，导致包含已合并的变更
- **解决**: `git fetch origin <target-branch>` && `git rebase origin/<target-branch>` --force-with-lease
- **预防**: 遵循铁律，创建 MR 前必须先同步并 rebase 目标分支

**HTTP 401 Unauthorized**:
- 原因: PAT 无效或权限不足
- 解决: 验证 PAT 是否有 `api` 权限

**glab 命令无返回结果**:
- 原因: PAT 未配置或版本过旧
- 解决: 使用 `glab --web` 或切换到 curl API

**飞书任务 ID 验证失败**:
- 原因: YAML 格式错误或 ID 不存在
- 解决: 检查 `feishu.task: <uid>` 格式，冒号后有空格

---

## 🤝 Agent Team 协作

Commit 工作需要与其他角色密切协作。本 SKILL 专注于代码提交和 MR 创建技术实践，相关职责请参考：

- **开发工作流** → [dev SKILL](../dev/SKILL.md)
  - 代码开发、测试规范
  - Commit message 格式要求
  - 参考：`docs/scrum/story/` 中的 Story 文档

- **测试验证** → [qa SKILL](../qa/SKILL.md)
  - 测试覆盖要求
  - 提交前测试验证
  - SIT/UAT 测试标准

- **项目管理** → [pm SKILL](../pm/SKILL.md)
  - 飞书工作项管理
  - Story/Epic 状态跟踪
  - 参考：飞书项目管理系统

- **DevOps 流程** → [devops SKILL](../devops/SKILL.md)
  - CI/CD Pipeline 集成
  - MR/Merge Request 审批流程
  - 部署环境配置

---

## 参考

- [设计文档](/docs/design/skills/commit-v1.0.0.md)
- [飞书文档：GitLab MR - 飞书工作项关联功能使用指南](https://feishu.example.com/wiki/StSfwrGDoibiIOklf8ccOFumnHd)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [GitLab API Documentation: Merge Requests](https://docs.gitlab.com/ee/api/merge_requests.html)
- [GitLab API Documentation: Users](https://docs.gitlab.com/ee/api/users.html)

---

**版本**: v2.1
**维护者**: DevTools Team
