# Epic 模板

**用途**: 创建新的 Epic PRD 文档

**使用说明**:
1. 复制此模板到 `docs/scrum/prd/epic-{序号}-{名称}.md`
2. 替换模板中的占位符（如 `{序号}`、`{名称}`）
3. 填写 Epic 的详细内容

---

## Epic 模板

---
id: "EPIC-{序号}"
title: "Epic 标题"
description: "Epic 简短描述（1-2 句话）"
status: "TODO"  # TODO/IN_PROGRESS/COMPLETED/BLOCKED/CANCELLED
priority: "P1"  # P0/P1/P2/P3
layer: "INFRA"  # 架构层次分类: INFRA/DATA_LAYER/SERVICE_LAYER/APP_LAYER/CROSS_LAYER
owner: "owner@example.com"
start_date: "2026-XX-XX"
target_date: "2026-XX-XX"
completed_date: ""  # 可选，仅在 status=COMPLETED 时填写
stories:
  - "STORY-{序号}-01"
  - "STORY-{序号}-02"
  - "STORY-{序号}-03"
  # ... 添加所有 Story ID
dependencies:
  - "EPIC-{序号}"  # 依赖的其他 Epic ID（可选）
tags: []
version: "1.0"
created_at: "2026-XX-XX"
updated_at: "2026-XX-XX"
---

# EPIC-{序号}: Epic 标题

## 概述

**Epic 目标**: [描述 Epic 的核心目标]

**业务价值**: [描述 Epic 对业务的价值]

**范围**: [描述 Epic 的范围和边界]

## 背景

**问题陈述**: [描述当前存在的问题或痛点]

**机会**: [描述为什么现在要解决这个问题的机会]

## 用户故事

列出 Epic 中的主要用户故事。

## Story 列表

- [ ] STORY-{序号}-01: [Story 标题]
- [ ] STORY-{序号}-02: [Story 标题]
- [ ] STORY-{序号}-03: [Story 标题]
- ...

## 验收标准

- [ ] 所有 Story 已完成
- [ ] 所有验收标准已满足
- [ ] 所有测试已通过
- [ ] 文档已更新

## 风险与依赖

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|----------|
| 风险描述 | 高/中/低 | 高/中/低 | 缓解方案 |

## 参考资料

- [设计文档](../../design/xxx.md)
- [相关 Epic](./epic-xxx.md)

---

**创建日期**: 2026-XX-XX
**维护者**: owner@example.com
**相关 Epic**: [关联 Epic ID]
