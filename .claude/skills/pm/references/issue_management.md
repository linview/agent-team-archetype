# Issue 管理规范

> Issue 用于跟踪开发过程中发现的、**独立于 Story 的** bug / 问题（如 Story 执行中发现的新 bug、线上小问题、体验缺陷）。与 Story（有计划的交付单元）区分：Story 是「要做的事」，Issue 是「发现的问题」。

## 文件命名规则

```
issue-YYYYMMDD-{short-kebab-description}.md
```

- `YYYYMMDD`：Issue 发现/创建日期
- `short-kebab-description`：简洁 kebab-case 描述（3-6 个词）
- 示例：`issue-20260604-cicd-date-range-filter-broken.md`

## ID 编号规则

```
ISSUE-YYYYMMDD-NNN
```

- `YYYYMMDD`：同文件名日期
- `NNN`：当日序号（001, 002, 003...）
- 创建前必须检查当日已有编号，避免冲突

冲突检测：

```bash
ls docs/scrum/issues/issue-$(date +%Y%m%d)*.md 2>/dev/null
```

## Issue 状态 FSM

### 状态定义

| 状态 | 含义 | 生命周期 |
|------|------|---------|
| **OPEN** | 新发现，待确认 | 临时 |
| **CONFIRMED** | 已确认是有效 Issue，待修复 | 临时 |
| **FIXING** | 正在修复中 | 临时 |
| **FIXED** | 代码已修复，待验证 | 临时 |
| **CLOSED** | 验证通过，已关闭 | **终态** |
| **WONTFIX** | 不修复（低优先级/非 bug/设计如此） | **终态** |
| **DUPLICATE** | 与已有 Issue 重复 | **终态** |

### 转换矩阵

| 从 | 到 | 条件 | 证据要求 |
|----|----|------|---------|
| — | OPEN | 新 Issue 创建 | 复现步骤或发现场景 |
| OPEN | CONFIRMED | 确认为有效 bug/问题 | 确认人记录 |
| OPEN | DUPLICATE | 确认与已有 Issue 重复 | `duplicate_of` 字段指向原 Issue |
| OPEN | WONTFIX | 确认不需要修复 | 关闭理由 |
| CONFIRMED | FIXING | 开始修复 | 关联 Story 或 commit |
| CONFIRMED | WONTFIX | 评估后决定不修复 | 关闭理由 |
| FIXING | FIXED | 代码修复完成 | commit SHA |
| FIXED | CLOSED | QA 验证通过 | 验证记录 |
| FIXED | OPEN | 验证不通过，需重新修复 | 复现说明 |

### 简化路径

适用于修复即验证的简单场景：

```
OPEN → FIXED → CLOSED
OPEN → WONTFIX
```

### 终态不可变性

与 Story FSM 一致：CLOSED、WONTFIX、DUPLICATE 为终态，不可回退。

## 必需 Frontmatter 字段

```yaml
---
id: "ISSUE-YYYYMMDD-NNN"
title: "简短描述"
severity: "P0 | P1 | P2 | P3"
status: "OPEN | CONFIRMED | FIXING | FIXED | CLOSED | WONTFIX | DUPLICATE"
created_at: "YYYY-MM-DD"
affected_component: "frontend | backend | database | ci | docs | skill"
---
```

可选字段（关闭时补充）：

```yaml
closed_at: "YYYY-MM-DD"
closed_by: "STORY-X-XX 或 commit SHA"
resolution: "fixed | wontfix | duplicate"
duplicate_of: "ISSUE-YYYYMMDD-NNN"  # 仅 DUPLICATE 状态
```

> `affected_component` 按实际项目分层填写。archetype 模板语境下典型取值：`backend`（业务实现层）、`skill`（agent skill 方法论）、`docs`（文档）、`ci`（流水线）、`database`（数据层）、`frontend`（如有前端）。

## 严重级别定义

| 级别 | 定义 | 响应要求 |
|------|------|---------|
| **P0** | 阻塞核心功能，用户无法使用 | 立即修复，当前 Sprint 内 |
| **P1** | 重要功能异常，有 workaround | 优先修复，当前或下一 Sprint |
| **P2** | 非核心功能异常或体验问题 | 计划修复，排入合适的 Sprint |
| **P3** | 微小问题或改进建议 | 可选修复，视资源情况 |

## 归档规则

### 三条归档路径

| 触发条件 | 操作 | 时机 |
|---------|------|------|
| 活跃 Issue 被其他 Story/bugfix 覆盖 | 标记 CLOSED + `git mv` 归档 | 确认覆盖时立即执行 |
| 终态 Issue 超过 30 天 | `git mv` 归档 | 每周项目审计时批量处理 |
| OPEN Issue 超过 15 天且确认仍存在 | 建议转为 Story 纳入开发计划 | 每周项目审计时检查 |

### 归档操作

```bash
# 归档单个 Issue
git mv docs/scrum/issues/issue-YYYYMMDD-*.md docs/scrum/issues/archive/

# 批量归档 30 天以上的终态 Issue（审计时执行）
find docs/scrum/issues/ -name "issue-*.md" -mtime +30 | while read f; do
  # 检查是否为终态
  if grep -q 'status: "CLOSED\|WONTFIX\|DUPLICATE"' "$f"; then
    git mv "$f" docs/scrum/issues/archive/
  fi
done
```

### 活跃目录保留原则

- 活跃状态（OPEN/CONFIRMED/FIXING/FIXED）Issue **永久保留**在 `issues/` 目录
- 终态 Issue 短期保留（≤30 天）作为最近记录
- 归档操作使用 `git mv` 保留历史
- **禁止删除** Issue 文件

## 15 天 OPEN 预警处理

每周项目审计时，检查是否有超过 15 天的 OPEN Issue：

```bash
# 查找超过 15 天的 OPEN Issue
find docs/scrum/issues/ -name "issue-*.md" -mtime +15 | while read f; do
  if grep -q 'status: "OPEN"' "$f"; then
    echo "⚠️ $(basename $f): OPEN 超过 15 天"
  fi
done
```

处理决策：

1. **确认仍存在** → 创建 Story 纳入开发计划，Issue 状态保持 OPEN
2. **已由其他工作修复** → 标记 CLOSED + 归档
3. **不再适用** → 标记 WONTFIX + 说明原因

## Issue 与 Story 的关系

| 场景 | 处理方式 |
|------|---------|
| Issue 需要正式修复 | 创建 Story，Issue `closed_by` 指向 Story |
| Issue 在当前 Story 中顺手修复 | Issue `closed_by` 指向 commit SHA |
| Issue 是 Story 执行中发现的新 bug | 记录 Issue，独立于当前 Story 跟踪 |
| P0/P1 Issue | 必须有对应 Story 或在当前 Story 中修复 |
| P2/P3 Issue | 可记录跟踪，不一定需要立即修复 |

## 模板

见 [Issue 模板](../templates/issue_template.md)
