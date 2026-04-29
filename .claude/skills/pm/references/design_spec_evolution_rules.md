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
docs/design/service_layer_architecture_v4.0.md 存在
  ↓
Epic-15（基于 v4.0）默认应用
Epic-6（基于 v3.3）的未完成 Story 默认取消
```

**应用场景**:
- 架构设计从 v3.3 升级到 v4.0
- 数据库设计从 v2.0 升级到 v3.0
- API 设计从 v1.5 升级到 v2.0

---

### 规则 2: 取消旧 Story，确保可追溯

**行为**: 旧版本未完成 Story → 取消并记录替换关系

**取消流程（Story 文件）**:

```markdown
---
id: "STORY-6-15"
status: "CANCELLED"
cancel_reason: "被 v4.0 架构替代"
replaced_by: "STORY-15-01, STORY-15-02"
cancel_date: "2026-04-03"
design_spec_version: "v3.3 → v4.0"
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
id: "EPIC-6"
status: "SUPERSEDED"
superseded_by: "EPIC-15"
superseded_reason: "Design Spec v3.3 → v4.0 演进"
superseded_date: "2026-04-03"
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
Epic-6（v3.3）下有 story-6-01 ~ story-6-14
  ↓
story-6-01 ~ story-6-10 已完成（COMPLETED）
  ↓
这些 Story 状态保持不变
  ↓
Epic-6 的完成度 = 10/14（71.4%）
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
ls docs/design/service_layer_architecture_v*.md

# 输出示例：
# docs/design/service_layer_architecture_v4.0.md（当前）
# docs/design/archive/service_layer_architecture_v3.3.md（过期）
```

**验证方法**:
```bash
# 检查版本日期
grep -E "version|更新日期" docs/design/service_layer_architecture_v*.md
```

---

#### Step 2: 应用新 Epic/Story

**操作清单**:

- ✅ 创建新 Epic（如 Epic-15，基于 v4.0）
- ✅ 创建新 Story（如 story-15-01/02）
- ✅ 标记旧 Story 为 CANCELLED（如 story-6-15）

**创建新 Epic**:
```bash
# 使用模板
cp .claude/skills/pm/templates/epic_template.md \
   docs/scrum/prd/epic-15-data-layer-optimization-v4.md

# 编辑 Epic 文件，填写详细内容
vim docs/scrum/prd/epic-15-data-layer-optimization-v4.md
```

**创建新 Story**:
```bash
# 使用模板
cp .claude/skills/pm/templates/story_template.md \
   docs/scrum/story/story-15-01-redundancy-analysis.md

# 编辑 Story 文件，填写详细内容
vim docs/scrum/story/story-15-01-redundancy-analysis.md
```

**标记旧 Story**:
```bash
# 编辑旧 Story 文件
vim docs/scrum/story/story-6-15-data-table-bloat.md

# 添加取消字段
# cancel_reason: "被 v4.0 架构替代"
# replaced_by: "STORY-15-01, STORY-15-02"
# cancel_date: "2026-04-03"
# design_spec_version: "v3.3 → v4.0"
```

---

#### Step 3: 更新 Epic 状态

**旧 Epic 文件**（epic-6）:
```yaml
---
id: "EPIC-6"
status: "SUPERSEDED"  # 原状态可能是 IN_PROGRESS
superseded_by: "EPIC-15"
superseded_reason: "Design Spec v3.3 → v4.0 演进"
superseded_date: "2026-04-03"
---
```

**新 Epic 文件**（epic-15）:
```yaml
---
id: "EPIC-15"
status: "TODO"
supersedes: "EPIC-6"
supersedes_reason: "基于 v4.0 架构重新设计"
created_date: "2026-04-03"
---
```

---

#### Step 4: 同步 DASHBOARD/KANBAN

**更新 DASHBOARD.md**:
```markdown
## Epic 进度总览

| Epic ID | Epic 标题 | 状态 | 完成度 | Story 进度 | 开始日期 | 目标日期 |
|--------|---------|------|--------|-----------|----------|----------|
| EPIC-6 | 数据层架构优化 v3.3 | **SUPERSEDED** | 71.4% | 10/14 | 2026-02-03 | - |
| EPIC-15 | 数据层架构优化 v4.0 | TODO | 0% | 0/17 | 2026-04-16 | 2026-05-06 |
```

**更新 KANBAN.md**:
```markdown
### 🔄 已取消 / 已替代

| Story | Epic | 标题 | 取消原因 | 替换为 |
|-------|------|------|---------|--------|
| STORY-6-15 | EPIC-6 | 数据表膨胀问题调研 | v3.3 → v4.0 演进 | STORY-15-01, STORY-15-02 |
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
用 story-6-15（v3.3）替换 story-15-01（v4.0）
```

**✅ 正确做法**:
```
默认应用新版本（v4.0）
story-6-15 标记为 CANCELLED
story-15-01 正常执行
```

**为什么错误？**
- 违背"默认应用新版本"原则
- 新版本包含最新的架构决策
- 旧版本已经被废弃

---

### 错误 2: 理解为"重复需求"

**❌ 错误理解**:
```
Epic-6 和 Epic-15 是重复的，需要去重
```

**✅ 正确理解**:
```
这是 Design Spec 演进（v3.3 → v4.0）
不是重复需求，而是架构升级
```

**为什么错误？**
- 混淆"演进"与"重复"
- 演进是技术迭代，重复是管理失误
- Epic-6 和 Epic-15 是不同版本的技术方案

---

### 错误 3: 修改已完成历史

**❌ 错误做法**:
```
修改已完成 story-6-01 ~ story-6-10 的状态
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

### 案例 1: 服务层架构 v3.3 → v4.0 演进

**背景**:
- `docs/design/service_layer_architecture_v3.3.md` 存在
- Epic-6 基于v3.3，包含 15 个 Story
- 其中 story-6-01 ~ story-6-10 已完成，story-6-11 ~ story-6-15 未完成

**演进事件**:
- `docs/design/service_layer_architecture_v4.0.md` 发布
- 新版本优化了数据层架构

**处理流程**:

1. **创建新 Epic**:
   - Epic-15: 数据层架构优化 v4.0
   - 17 个 Story（重新设计）

2. **取消旧 Story**:
   - story-6-15: 数据表膨胀问题调研 → CANCELLED
   - `replaced_by: "STORY-15-01, STORY-15-02"`

3. **保留已完成 Story**:
   - story-6-01 ~ story-6-10 状态不变（COMPLETED）

4. **更新 Epic 状态**:
   - Epic-6: IN_PROGRESS → SUPERSEDED
   - Epic-15: TODO（新创建）

5. **同步 DASHBOARD/KANBAN**:
   - Epic-6 完成度 = 10/15（66.7%）
   - Epic-15 完成度 = 0/17（0%）

**结果**:
- Epic-6 完成度固定在 66.7%（已完成工作保留）
- Epic-15 从 0% 开始（全新架构）
- 可追溯性完整（明确记录替换关系）

---

### 案例 2: 数据库 DDL v2.0 → v3.0 演进

**背景**:
- `docs/design/database_ddl_v2.0.md` 存在
- Epic-5 基于 v2.0，包含 8 个 Story
- 所有 Story 均已完成

**演进事件**:
- `docs/design/database_ddl_v3.0.md` 发布
- 新版本添加了 TrainJob 支持

**处理流程**:

1. **创建新 Epic**:
   - Epic-12: TrainJob 支持与 Kubeflow 集成
   - 10 个 Story（新功能）

2. **保留旧 Epic**:
   - Epic-5 状态不变（COMPLETED）
   - 所有 Story 保持 COMPLETED

3. **更新 Epic 状态**:
   - Epic-5: COMPLETED（不变）
   - Epic-12: TODO（新创建）

4. **同步 DASHBOARD/KANBAN**:
   - Epic-5 完成度 = 8/8（100%）
   - Epic-12 完成度 = 0/10（0%）

**结果**:
- Epic-5 完成度固定在 100%（历史工作保留）
- Epic-12 从 0% 开始（新功能开发）
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
- [ ] 升级（如 v3.3 → v4.0）
- [ ] 重构（如 v2.0 → v3.0）
- [ ] 新功能（如添加 TrainJob 支持）

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
   - v4.0 发布 → Epic-15 默认应用
   - v3.3 未完成 Story 默认取消

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
