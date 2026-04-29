# DASHBOARD 模板

**用途**: 创建项目进度全景视图

**使用说明**:
1. 复制此模板到 `docs/scrum/DASHBOARD.md`
2. 替换模板中的占位符
3. 填写项目的 Epic 和 Story 进度数据

---

## DASHBOARD 模板

# 项目进度全景视图

**最后更新**: [YYYY-MM-DD]
**项目周期**: [起始日期] 至今（约 X 周）
**当前 Sprint**: [Sprint 名称和周期]

---

## ⚠️ 数据源说明 (Data Source)

**🚨 重要**: 本文档是**衍生视图**，所有数据均来自以下**唯一真实源**：

- **Epic 数据源**: `docs/scrum/prd/epic-*.md`
- **Story 数据源**: `docs/scrum/story/story-*.md`

**更新规则**:
1. ✅ 修改 Story/Epic 状态时，**必须先更新源文件**
2. ✅ 然后运行同步命令更新本文档
3. ❌ **禁止直接修改本文档的状态数据**

---

## 📊 Epic 进度总览

| Epic ID | Epic 标题 | 状态 | 完成度 | Story 进度 | 开始日期 | 目标日期 |
|--------|---------|------|--------|-----------|----------|----------|
| EPIC-1 | [Epic 标题] | [状态] | [X%] | [Y/Z] | [日期] | [日期] |
| EPIC-2 | [Epic 标题] | [状态] | [X%] | [Y/Z] | [日期] | [日期] |
| ... | ... | ... | ... | ... | ... | ... |

**状态说明**:
- `TODO`: 未开始
- `IN_PROGRESS`: 进行中
- `COMPLETED`: 已完成
- `CANCELLED`: 已取消
- `SUPERSEDED`: 已被替代

---

## 📈 Story 状态统计

| 状态 | 数量 | 占比 |
|------|------|------|
| TODO | [数量] | [X%] |
| IN_PROGRESS | [数量] | [X%] |
| IN_REVIEW | [数量] | [X%] |
| TESTING | [数量] | [X%] |
| COMPLETED | [数量] | [X%] |
| BLOCKED | [数量] | [X%] |
| CANCELLED | [数量] | [X% |
| **总计** | [数量] | 100% |

---

## 🎯 Sprint 进度

### 当前 Sprint: [Sprint 名称]

**Sprint 周期**: [起始日期] - [结束日期]
**Sprint 状态**: [状态]
**负责人**: [负责人@example.com]

**Sprint 目标**:
- [ ] [目标 1]
- [ ] [目标 2]
- [ ] [目标 3]

**Story 分配**:
- [ ] STORY-X-XX: [Story 标题] - [负责人]
- [ ] STORY-Y-YY: [Story 标题] - [负责人]
- [ ] STORY-Z-ZZ: [Story 标题] - [负责人]

**进度统计**:
- 总 Story 数: [数量]
- 已完成: [数量] ([X%])
| 状态 | 数量 | 占比 |
|------|------|------|
| TODO | [数量] | [X%] |
| IN_PROGRESS | [数量] | [X%] |
| COMPLETED | [数量] | [X%] |

---

## 🔧 风险与阻塞

| Epic/Story | 风险类型 | 严重性 | 状态 | 缓解措施 |
|-----------|----------|--------|------|----------|
| EPIC-X | [风险描述] | 高/中/低 | [状态] | [缓解方案] |
| STORY-Y-YY | [风险描述] | 高/中/低 | [状态] | [缓解方案] |

---

## 📅 近期计划（未来 2 周）

**[日期 - 日期]: [Sprint 名称]**
- Epic-XX: [Epic 标题]
- 重点 Story: STORY-X-XX, STORY-Y-YY

**[日期 - 日期]: [Sprint 名称]**
- Epic-XX: [Epic 标题]
- 重点 Story: STORY-Z-ZZ, STORY-WWW

---

**更新频率**: 每日更新或 Story 状态变更时更新
**维护者**: Scrum Master
**相关文件**: `docs/scrum/KANBAN.md`
