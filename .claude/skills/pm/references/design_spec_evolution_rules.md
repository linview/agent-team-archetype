# Design Spec 演进规则细则

**用途**: Design Spec 版本演进的详细操作流程和案例参考

**相关章节**: SKILL.md "Design Spec 演进规则"（核心原则）

**使用说明**: 本文档提供详细的演进流程、示例和案例，核心规则请参考 SKILL.md 主文件。

---

## 核心原则

### 三大原则

1. **🎯 Design Spec 是唯一真实来源**
   - 所有开发/测试活动来源于 `docs/design/`
   - Epic/Story 是实现 Design Spec 的手段，非源头

2. **📈 Design Spec 持续演进**
   - `docs/design/` 下为**当前版本**
   - 过期版本移至 `docs/design/archive/`

3. **🔄 Scrum 是过程管理**
   - Epic/Story 管理开发流程
   - 非需求和设计的源头

---

## 演进规则（4 条核心）

### 规则 1: 默认应用新版本

**行为**: 新 Design Spec 版本 → 新 Epic/Story 方案默认生效

**示例**:
```
docs/design/{layer}_design_v{new_version}.md 存在
  ↓
Epic-{N}（基于 v{new_version}）默认应用
Epic-{M}（基于 v{old_version}）的未完成 Story 默认取消
```

**应用场景**:
- 架构设计从 v{old} 升级到 v{new}
- 数据库设计从 v{old} 升级到 v{new}
- API 设计从 v{old} 升级到 v{new}

---

### 规则 2: 取消旧 Story，确保可追溯

**行为**: 旧版本未完成 Story → 取消并记录替换关系

**取消流程（Story 文件）**:

```markdown
---
id: "STORY-{N}-{MM}"
status: "CANCELLED"
cancel_reason: "被 v{new_version} 架构替代"
replaced_by: "STORY-{N2}-{MM1}, STORY-{N2}-{MM2}"
cancel_date: "{cancel_date}"
design_spec_version: "v{old} → v{new}"
---
```

**可追溯性要求**（必须字段）:
- ✅ `cancel_reason`: 说明取消原因（"被 vX.X 替代"）
- ✅ `replaced_by`: 记录替换关系（新 Story ID）
- ✅ `cancel_date`: 记录取消日期
- ✅ `design_spec_version`: 记录版本演进

**Epic 文件取消流程**:

```markdown
---
id: "EPIC-{N}"
status: "SUPERSEDED"
superseded_by: "EPIC-{M}"
superseded_reason: "Design Spec v{old} → v{new} 演进"
superseded_date: "{date}"
---
```

---

### 规则 3: 已完成工作保留

**行为**: 已完成 Story 状态不可篡改

**保留规则**:
- ✅ **已完成**的旧版本 Story 状态不变（COMPLETED/IN_REVIEW/TESTING）
- ✅ 旧 Epic 的完成度由旧版本 Story 汇总
- ❌ 禁止修改已完成的历史状态

**示例**:
```
Epic-{N}（v{old}）下有 story-{N}-01 ~ story-{N}-{MM}
  ↓
story-{N}-01 ~ story-{N}-{KK} 已完成（COMPLETED）
  ↓
这些 Story 状态保持不变
  ↓
Epic-{N} 的完成度 = {KK}/{MM}（{percentage}%）
```

**为什么保留？**
1. 尊重历史工作成果
2. 保持项目进度可追溯
3. 避免"虚假完成"（已完成被取消）

---

### 规则 4: 版本升级处理流程

#### Step 1: 确认 Design Spec 版本

```bash
# 查询当前版本
ls {project_docs}/design/{layer}_design_v*.md

# 输出示例：
# {project_docs}/design/{layer}_design_v{new}.md（当前）
# {project_docs}/design/archive/{layer}_design_v{old}_YYYYMMDD.md（过期）
```

**验证方法**:
```bash
# 检查版本日期
grep -E "version|更新日期" {project_docs}/design/{layer}_design_v*.md
```

---

#### Step 2: 应用新 Epic/Story

**操作清单**:

- ✅ 创建新 Epic（如 Epic-{M}，基于 v{new}）
- ✅ 创建新 Story（如 story-{M}-01/02）
- ✅ 标记旧 Story 为 CANCELLED（如 story-{N}-{KK}）

**创建新 Epic**:
```bash
# 使用模板
cp .claude/skills/pm/templates/epic_template.md \
   {project_docs}/scrum/prd/epic-{M}-{description}.md

# 编辑 Epic 文件，填写详细内容
vim {project_docs}/scrum/prd/epic-{M}-{description}.md
```

**创建新 Story**:
```bash
# 使用模板
cp .claude/skills/pm/templates/story_template.md \
   {project_docs}/scrum/story/story-{M}-01-{description}.md

# 编辑 Story 文件，填写详细内容
vim {project_docs}/scrum/story/story-{M}-01-{description}.md
```

**标记旧 Story**:
```bash
# 编辑旧 Story 文件
vim {project_docs}/scrum/story/story-{N}-{KK}-{description}.md

# 添加取消字段
# cancel_reason: "被 v4.0 架构替代"
# replaced_by: "STORY-{M}-{MM1}, STORY-{M}-{MM2}"
# cancel_date: "{cancel_date}"
# design_spec_version: "v{old} → v{new}"
```

---

#### Step 3: 更新 Epic 状态

**旧 Epic 文件**（epic-{N}）:
```yaml
---
id: "EPIC-{N}"
status: "SUPERSEDED"  # 原状态可能是 IN_PROGRESS
superseded_by: "EPIC-{M}"
superseded_reason: "Design Spec v{old} → v{new} 演进"
superseded_date: "{date}"
---
```

**新 Epic 文件**（epic-{M}）:
```yaml
---
id: "EPIC-{M}"
status: "TODO"
supersedes: "EPIC-{N}"
supersedes_reason: "基于 v{new} 架构重新设计"
created_date: "{date}"
---
```

---

#### Step 4: 同步 DASHBOARD/KANBAN

**更新 DASHBOARD.md**:
```markdown
## Epic 进度总览

| Epic ID | Epic 标题 | 状态 | 完成度 | Story 进度 | 开始日期 | 目标日期 |
|--------|---------|------|--------|-----------|----------|----------|
| EPIC-{N} | {旧 Epic 标题} v{old} | **SUPERSEDED** | {X}% | {A}/{B} | {start_date} | - |
| EPIC-{M} | {新 Epic 标题} v{new} | TODO | 0% | 0/{C} | {start_date} | {target_date} |
```

**更新 KANBAN.md**:
```markdown
### 🔄 已取消 / 已替代

| Story | Epic | 标题 | 取消原因 | 替换为 |
|-------|------|------|---------|--------|
| STORY-{N}-{KK} | EPIC-{N} | {Story 标题} | v{old} → v{new} 演进 | STORY-{M}-{MM1}, STORY-{M}-{MM2} |
```

**同步命令**（手动或自动）:
```bash
# 检查源文件状态
grep -r "^status:" docs/scrum/prd/epic-*.md docs/scrum/story/*.md

# 更新 DASHBOARD.md 和 KANBAN.md（手动编辑或运行同步脚本）
```

---

## 常见错误（⚠️ 禁止）

### 错误 1: 用旧版本替换新版本

**❌ 错误做法**:
```
用 story-{N}-{KK}（v{old}）替换 story-{M}-{MM}（v{new}）
```

**✅ 正确做法**:
```
默认应用新版本（v{new}）
story-{N}-{KK} 标记为 CANCELLED
story-{M}-{MM} 正常执行
```

**为什么错误？**
- 违背"默认应用新版本"原则
- 新版本包含最新的架构决策
- 旧版本已经被废弃

---

### 错误 2: 理解为"重复需求"

**❌ 错误理解**:
```
Epic-{N} 和 Epic-{M} 是重复的，需要去重
```

**✅ 正确理解**:
```
这是 Design Spec 演进（v{old} → v{new}）
不是重复需求，而是架构升级
```

**为什么错误？**
- 混淆"演进"与"重复"
- 演进是技术迭代，重复是管理失误
- Epic-{N} 和 Epic-{M} 是不同版本的技术方案

---

### 错误 3: 修改已完成历史

**❌ 错误做法**:
```
修改已完成 story-{N}-01 ~ story-{N}-{KK} 的状态
```

**✅ 正确做法**:
```
保留已完成状态，只取消未完成 Story
```

**为什么错误？**
- 违背"已完成工作保留"原则
- 破坏项目历史记录
- 造成"虚假完成"（已完成被取消）

---

## 实际案例

### 案例 1: 服务层架构 v{old} → v{new} 演进

**背景**:
- `{project_docs}/design/{layer}_design_v{old}.md` 存在
- Epic-{N} 基于 v{old}，包含 {total} 个 Story
- 其中前 {completed} 个已完成，后 {remaining} 个未完成

**演进事件**:
- `{project_docs}/design/{layer}_design_v{new}.md` 发布
- 新版本优化了架构

**处理流程**:

1. **创建新 Epic**:
   - Epic-{M}: {新 Epic 描述} v{new}
   - {new_total} 个 Story（重新设计）

2. **取消旧 Story**:
   - story-{N}-{KK}: {描述} → CANCELLED
   - `replaced_by: "STORY-{M}-{MM1}, STORY-{M}-{MM2}"`

3. **保留已完成 Story**:
   - story-{N}-01 ~ story-{N}-{completed} 状态不变（COMPLETED）

4. **更新 Epic 状态**:
   - Epic-{N}: IN_PROGRESS → SUPERSEDED
   - Epic-{M}: TODO（新创建）

5. **同步 DASHBOARD/KANBAN**:
   - Epic-{N} 完成度 = {completed}/{total}（{percentage}%）
   - Epic-{M} 完成度 = 0/{new_total}（0%）

**结果**:
- Epic-{N} 完成度固定在 {percentage}%（已完成工作保留）
- Epic-{M} 从 0% 开始（全新架构）
- 可追溯性完整（明确记录替换关系）

---

### 案例 2: 数据库 DDL v{old} → v{new} 演进

**背景**:
- `{project_docs}/design/database_ddl_v{old}.md` 存在
- Epic-{N} 基于 v{old}，包含 {total} 个 Story
- 所有 Story 均已完成

**演进事件**:
- `{project_docs}/design/database_ddl_v{new}.md` 发布
- 新版本添加了新功能支持

**处理流程**:

1. **创建新 Epic**:
   - Epic-{M}: {新功能描述}
   - {new_total} 个 Story（新功能）

2. **保留旧 Epic**:
   - Epic-{N} 状态不变（COMPLETED）
   - 所有 Story 保持 COMPLETED

3. **更新 Epic 状态**:
   - Epic-{N}: COMPLETED（不变）
   - Epic-{M}: TODO（新创建）

4. **同步 DASHBOARD/KANBAN**:
   - Epic-{N} 完成度 = {total}/{total}（100%）
   - Epic-{M} 完成度 = 0/{new_total}（0%）

**结果**:
- Epic-{N} 完成度固定在 100%（历史工作保留）
- Epic-{M} 从 0% 开始（新功能开发）
- 两个 Epic 并存（不是重复，而是演进）

---

## 验证清单（创建新 Epic 前必须执行）

### Step 1: 检查 Design Spec 版本

```bash
# 列出所有 Design Spec 文件
find docs/design/ -name "*架构*.md" -o -name "*architecture*.md"

# 检查版本号
grep -E "版本|version" docs/design/*.md
```

**检查项**:
- [ ] 确认当前最新版本
- [ ] 确认过期版本位置（archive/）
- [ ] 确认版本发布日期

---

### Step 2: 确认演进（而非重复创建）

**问题 1**: 是否为新版本演进？
- [ ] 是（继续执行）
- [ ] 否（检查是否为重复创建）

**问题 2**: 新版本与旧版本的关系？
- [ ] 升级（如 v{old} → v{new}）
- [ ] 重构（如 v{old} → v{new}）
- [ ] 新功能（如添加 {feature} 支持）

**问题 3**: 是否需要取消旧 Story？
- [ ] 是（未完成 Story 标记 CANCELLED）
- [ ] 否（已完成 Story 保留状态）

---

### Step 3: 应用演进规则

**规则 1**: 默认应用新版本
- [ ] 创建新 Epic
- [ ] 创建新 Story

**规则 2**: 取消旧 Story
- [ ] 标记未完成 Story 为 CANCELLED
- [ ] 记录替换关系（replaced_by）

**规则 3**: 保留已完成 Story
- [ ] 验证已完成 Story 状态不变
- [ ] 验证 Epic 完成度正确

**规则 4**: 更新 Epic 状态
- [ ] 旧 Epic 标记为 SUPERSEDED
- [ ] 新 Epic 标记为 TODO

---

### Step 4: 确保可追溯性

**Story 文件字段**:
- [ ] `cancel_reason`: 说明取消原因
- [ ] `replaced_by`: 记录替换关系
- [ ] `cancel_date`: 记录取消日期
- [ ] `design_spec_version`: 记录版本演进

**Epic 文件字段**:
- [ ] `superseded_by`: 记录新 Epic ID
- [ ] `superseded_reason`: 说明演进原因
- [ ] `superseded_date`: 记录演进日期

**DASHBOARD/KANBAN 更新**:
- [ ] Epic 状态更新为 SUPERSEDED
- [ ] Story 状态更新为 CANCELLED
- [ ] 添加演进说明

---

## 命令参考

### 查询 Design Spec 版本

```bash
# 列出所有 Design Spec 文件
find docs/design/ -name "*.md" | sort

# 查看版本号
grep -E "版本|version|Version" docs/design/*.md

# 查看更新日期
grep -E "更新日期|updated|last update" docs/design/*.md
```

---

### 验证 Epic 状态一致性

```bash
# 检查所有 Epic 状态
grep -r "^status:" docs/scrum/prd/epic-*.md

# 检查 SUPERSEDED Epic 的替换关系
grep -A 5 "^status: \"SUPERSEDED\"" docs/scrum/prd/epic-*.md
```

---

### 验证 Story 状态一致性

```bash
# 检查所有 Story 状态
grep -r "^status:" docs/scrum/story/*.md | sort

# 检查 CANCELLED Story 的取消原因
grep -B 2 "^status: \"CANCELLED\"" docs/scrum/story/*.md | grep -E "cancel_reason|replaced_by"
```

---

### 同步 DASHBOARD/KANBAN

```bash
# 扫描源文件，生成统计
grep -r "^status:" docs/scrum/prd/epic-*.md docs/scrum/story/*.md | \
  sort | uniq -c | sort -rn

# 手动更新 DASHBOARD.md 和 KANBAN.md
vim docs/scrum/DASHBOARD.md
vim docs/scrum/KANBAN.md
```

---

## 总结

### 核心要点

1. **Design Spec 是唯一真实来源**
   - Epic/Story 是实现手段，非源头
   - 所有设计来源于 `docs/design/`

2. **新版本默认应用**
   - v{new} 发布 → Epic-{M} 默认应用
   - v{old} 未完成 Story 默认取消

3. **已完成工作保留**
   - 已完成 Story 状态不变
   - Epic 完成度固定在取消时刻

4. **可追溯性强制**
   - 记录取消原因、替换关系、演进日期
   - DASHBOARD/KANBAN 同步更新

### 快速检查清单

- [ ] 检查 Design Spec 版本
- [ ] 确认演进（非重复）
- [ ] 创建新 Epic/Story
- [ ] 取消旧 Story
- [ ] 更新 Epic 状态
- [ ] 同步 DASHBOARD/KANBAN

---

**相关文档**:
- SKILL.md 主文件: "Design Spec 演进规则"章节（4 条核心原则）
- `templates/epic_template.md`: Epic 文档模板
- `templates/story_template.md`: Story 文档模板

**维护者**: Scrum Master
**版本**: 1.0
**最后更新**: 2026-04-03
