# Commit Conventions

本文件是 **commit message 格式的单一权威源**（提交/推送/合并工程规范的归口处）。dev（本地提交）/ commit（推送·MR）/ refactor 等所有角色的提交行为均以本文件为准；项目层声明（如 CLAUDE.md「提交风格」）与本文件第一层语义一致。

## 第一层：项目规范（应然，优先遵循）

**格式**：

```
<type>(<scope>): <subject>

<body>          # 可选
<footer>        # 可选（任务 ID、BREAKING CHANGE 等）
```

**type 枚举**（与 MR Title 格式保持同一枚举集）：

`feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`

**规则**：

- **scope**：可选，标识影响范围（模块/目录/技能名，如 `skills`、`guide`、`examples`）
- **subject**：祈使语气、≤50 字符、结尾不加句号
- **body**：可选，解释 what/why（不展开 how 细节），每行 ≤72 字符
- **footer**：可选，关联任务（如 `Closes STORY-3-02`）、破坏性变更标记（`BREAKING CHANGE: ...`）

**示例**：

```
feat(skills): 新增 git add 禁用 -f 铁律

- commit skill 主落点：铁律章节（规则+处置+Why）
- dev/refactor 同步禁令，双栈落地

Closes ISSUE-20261120-001
```

## 第二层：auto-generate 工具默认（实然，仅作回退）

`commit.sh --auto-generate` 脚本的内置规则——**仅在未匹配到项目风格时作为回退**，产出后须按第一层校对修正：

1. **type 识别**（与第一层枚举兼容）：测试文件 `test:` / 文档 `docs:` / 配置 `chore(config):` / 源码 `feat:`
2. **摘要回退形态**：单文件 `Update <filename>`、多文件 `Update <count> files`——**此形态不符合第一层 subject 规范**（subject 应为动宾描述而非 `Update` 前缀），agent 审核时必须改写
3. **长度限制**：subject ≤50 字符，超长截断
4. **项目风格匹配**：脚本会加载项目最近 commits 与 CLAUDE.md 提交约定对齐风格——在 CC 风格项目（如本仓库）下通常直接产出第一层格式

## 裁决规则

两层数值或形态冲突时，**第一层项目规范优先**；第二层仅描述脚本实然默认，不构成规范授权。agent 手写、改写或审核 commit message 时一律按第一层执行。

> 历史动机注记：旧版规范曾表述「不强制 Conventional Commits（避免 semantic_release 版本爆炸）」——该担忧针对 CC 的 `feat`/`fix` 触发 semantic_release 自动 bump 的场景；本仓库版本由 pm 按 semver 手动定版（见 pm skill「发布版本规划」），无 semantic_release 自动化，担忧不成立，故统一为 CC 规范。

## 示例

```bash
# 自动生成（产出后按第一层校对，Update 形态须改写）
commit.sh --auto-generate

# 手动指定（直接按第一层格式）
commit.sh --message "feat(auth): implement JWT authentication"
```
