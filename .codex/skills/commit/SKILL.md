---
name: commit
description: "代码提交与 MR 创建技能 - 自动生成语义化 commit message、创建符合规范的 GitLab Merge Request、验证飞书工作项关联。当用户提到 Git 提交、commit、push、推送代码、创建 MR、创建 PR、合并请求、或需要提交代码、推送代码、创建 MR/PR 时，必须使用此技能。支持交互式（对话）和非交互式（参数）两种模式。"
version: "2.3.0"
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
- [ ] 变更列表与 `.gitignore` 对比无命中：`git diff --name-only origin/<target-branch>...HEAD | xargs -r git check-ignore --no-index --` 输出为空（有输出 = 有文件绕过 ignore 被强加，先移除并查明来源。⚠️ 只检查本次 MR 增量变更，**不追溯历史存量**——先于 `.gitignore` 规则提交的存量文件取舍由人类 owner 决断）
- [ ] 提交历史正确（`git log --oneline origin/<target-branch>..HEAD`）

**只有以上全部满足，才能创建 MR！**

**Why**: 避免重复提交、错误的 diff、不必要的冲突

**典型后果**:
- MR 包含已合并到目标分支的变更
- 需要强制 rebase 修复，增加工作量
- 影响代码审查效率和 CI/CD 流程

---

## 🚨 铁律：git add 禁用 -f（强制执行）

**⚠️ 暂存文件时禁止使用 `git add -f`（含 `--force`）！！！`-f` 会绕过 `.gitignore` 的约束！**

**规则**（强制执行）：

```bash
# ❌ 禁止：绕过 .gitignore
git add -f <file>
git add --force <file>

# ✅ 正确：尊重 .gitignore
git add <file>
git add .
git add -A
```

**文件被 ignore 加不进去时的正确处置**：
1. `git check-ignore -v <file>` 确认命中的是哪条 ignore 规则
2. 判断该文件是否真的应该入库：
   - 确需入库 → 修订 `.gitignore`（收紧规则范围）或移动文件到非忽略路径，再正常 `git add`
   - 不该入库（临时报告/密钥/构建产物）→ 放弃添加，遵守约束

**Why**: `-f` 绕过 `.gitignore` 会把密钥凭证、临时报告、构建产物等不该入库的文件强行提交进仓库，造成敏感信息泄露与仓库污染

**典型后果**:
- 密钥/凭证被提交入库，安全事故
- 大量临时文件污染 MR diff，干扰代码审查
- push 后需 rewrite history（filter-branch/BFG）才能清除，殃及全团队

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

# 飞书认证密钥（配置此项即视为飞书环境，MR 需关联工作项；
# 未配置且用户未提供 uid 时视为非飞书环境，跳过工作项验证）
FEISHU_AUTH_KEY=cli_xxxxxxxxxxxxxx

# GitLab 实例地址（可选，默认从环境变量读取）
GITLAB_URL=https://git.example.com

# 飞书项目 ID（可选，用于工作项验证）
FEISHU_PROJECT_ID=xxxxxxxxxxxxx
```

**部署前验证**:
1. 读取项目根目录 `.env.skill` 文件获取凭证信息
2. 验证 GitLab PAT 是否有效
3. 飞书环境（探测到 `FEISHU_AUTH_KEY`）时验证 auth_key 是否可用；非飞书环境跳过
4. 确认凭证有足够的权限（git write、feishu project read）

**注意**: `.env.skill` 已在 `.gitignore` 中，不应提交到 Git 仓库

---

## 核心功能

### 1. Commit 自动生成

基于代码变更自动生成语义化 commit message：

- 分析文件列表 + code diff + 工作上下文
- 输出 ≤1/2 屏幕的精简描述
- **遵循统一提交规范**（Conventional Commits，细则见 [references/commit-conventions.md](references/commit-conventions.md)——第一层项目规范优先，`Update <file>` 仅为 auto-generate 回退形态，须校对改写）
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

### 4. 飞书工作项验证（默认强制必填）

验证飞书项目工作项关联。行为由配置 `feishu.require_validation` 决定（**默认 `true` 强制必填**，等同旧版行为；`auto` 为环境条件必填，需显式开启）：

| 模式 | 行为 |
|------|------|
| `true`（默认） | **任何环境**必须提供飞书工作项 uid 并验证；无法提供有效 uid 时阻止创建 |
| `auto` | 环境条件必填——探测到飞书集成则必填并验证，探测不到则跳过（不阻塞 MR 创建） |
| `false` | 完全跳过验证与 front matter 注入 |

各模式下的验证动作：
- 检查 YAML front matter 格式
- 使用 lark-cli 验证工作项 ID 是否存在

**`auto` 模式的环境探测**——满足任一即视为飞书环境：
1. `.env.skill`（或 `.env`/环境变量）中配置了 `FEISHU_AUTH_KEY`
2. 用户明确提供了飞书工作项 uid（如 `--feishu-task` 参数）

**重要说明**：
- 飞书工作项 uid 是飞书项目管理系统中的唯一标识符
- **`true` 模式或飞书环境下**创建 MR 必须关联有效的飞书工作项 uid（数字格式，如 6934756567），不得使用占位符、默认值或跳过验证；用户无法提供有效 uid 时阻止创建并说明原因
- **`false` 模式或 `auto` 模式非飞书环境下**不要求 front matter，直接生成不含 `feishu.task` 的 description
- 验证失败行为：非交互模式直接报错退出（退出码 500）；交互模式提示补正，阻止创建

### 5. 内审规则检查

执行代码提交前的内审检查：

- 敏感信息检查（密钥、密码、IP 地址等）
- 测试覆盖检查（测试文件是否存在或变更）
- 文档更新检查

---

## Commit 规则

**📌 详细提交约定**：参见 [references/commit-conventions.md](references/commit-conventions.md)——**commit message 格式的单一权威源**（分层：第一层项目规范 Conventional Commits 优先 / 第二层 auto-generate 工具默认仅作回退）

**格式**：遵循 Conventional Commits（`<type>(<scope>): <subject>`），type/scope/subject/body/footer 规则见 references；auto-generate 生成后按第一层校对，`Update <file>` 回退形态须改写。

**自动生成**：基于代码变更自动生成语义化 message，加载项目最近 commits 匹配风格。

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

### MR Description 格式（四段落结构）

description 主体统一为四段落，与 `references/mr-templates/` 六类型模板骨架一致：

```yaml
---
feishu.task: 6723548458
---

## 功能列表

本 MR 交付的能力/修复点（意图层）：

- 新增 JWT 登录鉴权流程
- 修复 token 过期后的刷新竞态

## 变更列表

- `internal/logic/auth.go`: 新增 JWT 签发与校验逻辑
- `internal/handler/login.go`: 接入新鉴权中间件
- `tests/api/test_login.py`: 补充鉴权契约用例

## 验证结果

- `go test ./internal/...` 全部通过（42 cases）
- `pytest tests/api -q` 通过（8 passed）

## 补充说明

- 回滚方案：revert 本 MR 即可，无 schema 变更
```

**四段落规范**：
1. `## 功能列表`——意图层，条目化陈述本 MR 交付的能力/修复点
2. `## 变更列表`——文件级变更要点，条目化，可按目录分组
3. `## 验证结果`——证据层，条目化列出已执行的验证及结果
4. `## 补充说明`——风险/回滚/后续事项；**可选，无内容时省略整段**

**条目风格（强制）**：
- **一行一条、动宾结构、禁长篇段落**；每条 ≤1 行
- 段落叙述禁入前三段（功能列表/变更列表/验证结果）

**front matter 规则（按验证模式）**：
1. YAML front matter 位于描述开头；`require_validation: true`（默认）或飞书环境下必填（模式判定见「飞书工作项验证」节）
2. 字段名固定为 `feishu.task`，冒号后必须有空格
3. 工作项 ID 是数字格式（如 6723548458）
4. `false` 模式或 `auto` 模式非飞书环境省略整个 front matter 块

### MR 动态更新（活文档规则）

**description 是活文档，不是 create 时的一次性产物**。MR 创建后发生新 push/update 时，必须重新总结并更新：

1. **重新读取最新 file diff**：`git diff origin/<target-branch>...HEAD`（注意先 `git fetch origin <target-branch>` 同步远端）
2. **按四段落重新总结**：功能列表/变更列表/验证结果必须反映**合并请求的最终全部变更**，而非仅增量 commit
3. **更新 description**：通过 GitLab API `PUT /merge_requests/<iid>` 更新描述
4. **title 同步**：title 与最终 diff 意图不符时一并更新（格式仍为 Conventional Commits `type(scope): summary`）

**触发时机**：MR create 之后向源分支追加了任何新 commit（push、rebase、补丁修正）且 MR 仍处于 open 状态。

**禁止行为**：
- 禁止沿用 create 时的旧描述不管——追加 commit 后描述失真即违规
- 禁止只描述增量 commit 而遗漏既有变更

---

## 工作模式

**📌 详细使用示例**：
- 交互式模式：参见 [examples/interactive-usage.md](examples/interactive-usage.md)
- 非交互式模式：参见 [examples/non-interactive-usage.md](examples/non-interactive-usage.md)

### 交互式模式

交互式模式提供对话式流程，每个步骤都有默认值，用户可以确认或修改：

1. 确认目标分支（自动检测 master/main）
2. 检查 PAT 配置
3. **确定验证模式**（读 `require_validation` 配置，默认 `true`；`auto` 时探测 `FEISHU_AUTH_KEY` 或用户明确提供 uid）
4. **必填模式/飞书环境：输入并验证飞书工作项 uid**；`false` 模式/`auto` 非飞书环境：跳过此步
5. 生成/确认 MR Title
6. 确认创建 MR

**⚠️ 飞书工作项 uid 必填性由 `require_validation` 决定（默认强制必填）**
- `true`（默认）：任何环境必填——不得使用占位符、默认值或跳过；用户无法提供有效 uid 时阻止创建并说明原因；必须使用 lark-cli 或手动方式验证 uid 存在性
- `auto` 飞书环境（探测到 `FEISHU_AUTH_KEY` 或用户提供了 uid）：同上必填
- `auto` 非飞书环境 / `false`：跳过——不询问、不注入 front matter，直接进入下一步

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

# ⚠️ 注意：--feishu-task 参数必填性由 require_validation 决定（默认 true 强制必填）
# true（默认）：任何环境必须提供有效的工作项 uid
# auto：飞书环境（.env.skill 配置 FEISHU_AUTH_KEY）必须提供，非飞书环境可省略
# false：可省略，直接创建不带 front matter 的 MR
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
  # 工作项验证模式(默认 true 强制必填,等同旧版行为)
  # true: 任何环境必填并验证
  # auto: 环境条件必填——探测 FEISHU_AUTH_KEY/用户 uid,探测到则必填,探测不到则跳过
  # false: 完全跳过
  require_validation: "true"
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
5. **飞书任务 ID 验证**（条件必填）: 飞书环境下检查 YAML front matter 格式（`feishu.task: <uid>`）；非飞书环境跳过
6. **完整工作流程**: 同步目标分支 → PAT 验证 → 创建 MR → 查询信息 → 验证结果
7. **MR 动态更新**: MR create 后追加 commit 时，重新读取最新 file diff 并按四段落重新总结更新 title/description（见「MR 动态更新」节）

### 常见错误

**🚨 MR 包含重复的文件变更**（铁律违反）:
- **原因**: 创建 MR 前未同步目标分支，导致包含已合并的变更
- **解决**: `git fetch origin <target-branch>` && `git rebase origin/<target-branch>` --force-with-lease
- **预防**: 遵循铁律，创建 MR 前必须先同步并 rebase 目标分支

**🚨 MR description 与实际 diff 脱节**（活文档违规）:
- **原因**: MR create 后追加了 commit 但未更新 description
- **解决**: 重新读取最新 file diff（`git diff origin/<target-branch>...HEAD`），按四段落重新总结并通过 API 更新 description
- **预防**: 每次 push 后检查 MR 是否 open，open 则触发动态更新

**HTTP 401 Unauthorized**:
- 原因: PAT 无效或权限不足
- 解决: 验证 PAT 是否有 `api` 权限

**glab 命令无返回结果**:
- 原因: PAT 未配置或版本过旧
- 解决: 使用 `glab --web` 或切换到 curl API

**飞书任务 ID 验证失败**（仅飞书环境）:
- 原因: YAML 格式错误或 ID 不存在
- 解决: 检查 `feishu.task: <uid>` 格式，冒号后有空格
- 非飞书环境: 确认未误配 `FEISHU_AUTH_KEY`，或直接省略 `--feishu-task` 走跳过分支

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

- [commit 规范](references/commit-conventions.md)
- [飞书文档：GitLab MR - 飞书工作项关联功能使用指南](https://example.feishu.cn/wiki/DOCUMENT_ID)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [GitLab API Documentation: Merge Requests](https://docs.gitlab.com/ee/api/merge_requests.html)
- [GitLab API Documentation: Users](https://docs.gitlab.com/ee/api/users.html)

---

**版本**: v2.3.0
**维护者**: DevTools Team

**更新日志**:
- v2.3.0 (2026-11-21): ✨ 新增「git add 禁用 -f」铁律(强制执行:规则 bash 块+被 ignore 文件正确处置流程+Why/典型后果)+ MR 门禁 checklist 新增「变更列表×.gitignore 增量对比」项(`git check-ignore --no-index` 检出 tracked 文件绕过 ignore 被强加;只查本次 MR 增量不追溯历史存量,存量取舍归人类 owner)(MR !21);commit 规范统一归口(ISSUE-20261120-001)——commit-conventions.md 重写为**单一权威源**(第一层项目规范 CC 优先/第二层 auto-generate 工具默认仅回退+裁决规则),SKILL.md 两处「不强制 CC」矛盾表述修正(含 semantic_release 历史动机注记),fixture eval 回归全 PASS
- v2.2.1 (2026-08-22): 🐛 `require_validation` 默认值回归 `true`(MR !13 review 修正——新配置项默认值应等同引入前行为,`auto` 环境条件必填改为显式开启);SKILL.md 飞书验证节改三模式语义表
- v2.2.0 (2026-08-22): ✨ MR description 四段落结构(功能列表/变更列表/验证结果/补充说明,条目化禁长篇)+ MR 动态更新规则(create 后 push 必须按最新 file diff 重新总结)+ 飞书 front matter 环境条件必填(非飞书环境跳过)(STORY-5-02)
- v2.1.1 (2026-08-15): 🐛 hook 生成器嵌入绝对路径(修复安装后 `$SCRIPT_DIR/../../` 悬空解析);SKILL.md 设计文档死链改 skill 内 references
