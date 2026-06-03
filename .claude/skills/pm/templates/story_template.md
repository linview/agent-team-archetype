# Story 模板

**用途**: 创建新的 Story 文档

**使用说明**:
1. 复制此模板到 `docs/scrum/story/story-{epic序号}-{story序号:02d}-{简短描述}.md`
2. 替换模板中的占位符（如 `{序号}`、`{Story ID}`）
3. 填写 Story 的详细内容

---

## Story 模板

---
id: "STORY-{epic序号}-{story序号:02d}"
epic_id: "EPIC-{epic序号}"
title: "Story 标题"
description: "Story 简要描述"
status: "TODO"
priority: "P1"
story_points: 3
assignee: "developer@{company_domain}"
start_date: "2026-XX-XX"
target_date: "2026-XX-XX"
completed_date: ""
verified_by: ""
verification_date: ""
verification_evidence: []
dependencies: []
tags: []
version: "1.0"
created_at: "2026-XX-XX"
updated_at: "2026-XX-XX"
---

# STORY-{epic序号}-{story序号:02d}: Story 标题

## 用户故事

作为 [角色]，我想要 [功能]，以便 [价值]。

## 任务描述

[详细描述任务内容]

## 验收标准

### 功能标准
- [ ] 标准 1
- [ ] 标准 2
- [ ] 标准 3

### 测试标准（按实现阶段）

> **必填**：每个 Story 必须根据功能类型补充对应的测试 AC。
> 根据功能类型查矩阵确定必须的测试层级：[AC 测试分层策略](../references/ac_testing_strategy.md)
>
> | 功能类型 | [UT] | [API] | [SIT] | [E2E] | [UAT] |
> |---------|------|-------|-------|-------|-------|
> | 基础设施 | 必须 | - | 可选 | - | - |
> | 服务层 | 必须 | - | 可选 | - | - |
> | API 端点 | 必须 | 必须 | 必须 | - | - |
> | 前端页面 | 可选 | - | 必须 | 必须 | 必须 |

- [ ] **[UT]** （必填：Service/Logic 层覆盖率 >= 75%，通过率 100%）
<!-- 根据功能类型取消注释以下标签：
- [ ] **[API]** Handler 测试覆盖正常/异常/边界路径
- [ ] **[SIT]** 集成环境下跨模块交互验证
- [ ] **[E2E]** 前后端联调验证
- [ ] **[UAT]** 用户场景验收
-->

## 实施计划

### Phase 1: [阶段名称]

**任务**：
- [ ] 任务 1
- [ ] 任务 2

**预期产出**：
- 产出物 1
- 产出物 2

### Phase 2: [阶段名称]

**任务**：
- [ ] 任务 1
- [ ] 任务 2

**预期产出**：
- 产出物 1
- 产出物 2

## 依赖关系

- 依赖 Story：STORY-X-XX
- 被依赖 Story：STORY-Y-YY

## 风险与缓解

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|----------|
| 风险描述 | 高/中/低 | 高/中/低 | 缓解方案 |

## 参考资料

- [设计文档](../../design/xxx.md)
- [相关 Epic](../prd/epic-xxx.md)
- [相关 Story](./story-x-xx.md)

---

**创建日期**: 2026-XX-XX
**维护者**: developer@{company_domain}
**相关 Epic**: EPIC-{序号}
