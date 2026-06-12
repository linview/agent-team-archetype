# Story 状态有限状态机（FSM）

**版本**: v1.0
**创建日期**: 2026-06-01

## 目录

1. [状态定义](#状态定义)
2. [状态转换矩阵](#状态转换矩阵)
3. [转换条件详解](#转换条件详解)
4. [特殊规则](#特殊规则)
5. [状态冲突处理](#状态冲突处理)

---

## 状态定义

| 状态 | 含义 | 生命周期 | 使用场景 |
|------|------|---------|---------|
| **TODO** | 待开始 | 临时 | 初始状态 |
| **IN_PROGRESS** | 进行中 | 临时 | 开发中 |
| **IN_REVIEW** | 代码审查 | 临时 | PR/MR 审查中 |
| **TESTING** | 测试中 | 临时 | QA 验证中 |
| **COMPLETED** | 已完成 | 终态 | AC 100% 签字 + QA 通过 |
| **BLOCKED** | 外部阻塞 | 临时 | 依赖未满足，可恢复 |
| **DEFERRED** | 延迟 | 终态 | 降优先级，未来版本再做 |
| **CANCELLED** | 取消 | 终态 | 业务逻辑错误/被替代，不再实现 |

**临时状态**（TODO/IN_PROGRESS/IN_REVIEW/TESTING/BLOCKED）：可继续流转
**终态**（COMPLETED/DEFERRED/CANCELLED）：不可变更（除非明确解冻）

---

## 状态转换矩阵

| 从 \\ 到 | TODO | IN_PROGRESS | IN_REVIEW | TESTING | COMPLETED | BLOCKED | DEFERRED | CANCELLED |
|---------|------|-------------|-----------|---------|-----------|---------|----------|-----------|
| **TODO** | — | ✅ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ |
| **IN_PROGRESS** | ❌ | — | ✅ | ❌ | ❌ | ✅ | ✅ | ✅ |
| **IN_REVIEW** | ❌ | ✅ | — | ✅ | ❌ | ✅ | ✅ | ✅ |
| **TESTING** | ❌ | ✅ | ✅ | — | ✅ | ✅ | ✅ | ✅ |
| **BLOCKED** | ✅ | ✅ | ✅ | ✅ | ❌ | — | ✅ | ✅ |
| **COMPLETED** | ❌ | ❌ | ❌ | ❌ | — | ❌ | ❌ | ❌ |
| **DEFERRED** | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | — | ❌ |
| **CANCELLED** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | — |

**读取方式**：行 = 当前状态，列 = 目标状态。✅ = 允许转换，❌ = 禁止转换。

---

## 转换条件详解

### 正向流转（主路径）

#### TODO → IN_PROGRESS
- **触发**：开发者被指派并开始编码
- **前置条件**：至少 1 条 Task 已勾选（开发启动标志）
- **证据**：首个 commit 包含 Story ID
- **AC 签字率**：≥ 0%

#### IN_PROGRESS → IN_REVIEW
- **触发**：代码开发完成，提交 PR/MR
- **前置条件**：所有功能标准 AC 已勾选
- **证据**：MR 已创建，包含变更文件列表
- **AC 签字率**：≥ 80%，Task 签字率 ≥ 50%

#### IN_REVIEW → TESTING
- **触发**：代码审查通过，MR 合并
- **前置条件**：全部 AC 已勾选，测试标准 AC 已验证
- **证据**：MR 合并记录 + CI 通过
- **AC 签字率**：100%，Task 签字率 ≥ 80%

#### TESTING → COMPLETED
- **触发**：QA 验证通过
- **前置条件**：全部 AC + Task 已勾选，QA 验证通过
- **证据**：QA 测试报告 + 无 P0/P1 Bug
- **AC 签字率**：100%，Task 签字率：100%

### 回退流转（质量不达标时）

#### IN_REVIEW → IN_PROGRESS
- **触发**：代码审查不通过（reviewer 要求修改）
- **前置条件**：明确的审查意见
- **证据**：MR comment 记录

#### TESTING → IN_PROGRESS
- **触发**：QA 测试发现 P0/P1 Bug
- **前置条件**：Bug 报告已提交
- **证据**：QA Bug 报告 + 修复 commit

#### TESTING → IN_REVIEW
- **触发**：QA 测试发现代码质量问题（非 Bug 级别）
- **前置条件**：需要重新审查
- **证据**：QA 反馈记录

### 阻塞与恢复

#### 任意临时状态 → BLOCKED
- **触发**：外部依赖未满足（如 API 未就绪、设计文档缺失、上游 Story 未完成）
- **前置条件**：明确记录阻塞原因和阻塞源
- **证据**：Story body 中记录 `blocked_reason` 和 `blocked_by`（阻塞源 Story ID）
- **说明**：BLOCKED 不影响已完成的工作，仅暂停推进

#### BLOCKED → 恢复到原状态
- **触发**：阻塞条件解除
- **前置条件**：阻塞源 Story 已 COMPLETED 或阻塞原因已消除
- **恢复目标**：恢复到进入 BLOCKED **之前**的状态
  - TODO → BLOCKED → TODO
  - IN_PROGRESS → BLOCKED → IN_PROGRESS
  - IN_REVIEW → BLOCKED → IN_REVIEW
  - TESTING → BLOCKED → TESTING
- **证据**：阻塞源 Story 状态更新为 COMPLETED

### 终态转换

#### 任意临时状态 → DEFERRED
- **触发**：PO/PM 决策降优先级
- **前置条件**：
  - 明确记录延迟原因
  - 明确计划重新排期的版本/时间
  - 记录 `replaced_by`（如有替代 Story）
- **证据**：PO/PM 的书面决策（会议纪要、评论等）

#### 任意临时状态 → CANCELLED
- **触发**：业务逻辑错误、需求变更、被其他 Story 替代
- **前置条件**：
  - 明确记录取消原因
  - 记录 `cancel_reason`
  - 记录 `replaced_by`（如有替代 Story）
- **证据**：需求变更文档或替代 Story 已创建

#### DEFERRED → TODO
- **触发**：PO/PM 决策重新排期
- **前置条件**：延迟原因已不存在或优先级重新提升
- **证据**：Sprint 规划会议决议

---

## 特殊规则

### 终态不可变性

**COMPLETED 状态不可变更**：
- 一旦标记 COMPLETED，不得回退到任何状态
- 如发现质量问题，应创建新 Bug Story 追踪修复，而非修改原 Story
- **Why**：保护 Sprint 历史数据的完整性，避免已完成工作量被篡改

**DEFERRED 和 CANCELLED 可有限解冻**：
- DEFERRED 只能恢复到 TODO（需重新评估优先级）
- CANCELLED 不可恢复（如需重做，应创建新 Story）

### BLOCKED 状态的记忆性

进入 BLOCKED 时必须记录：
1. `blocked_reason`：为什么被阻塞
2. `blocked_by`：被哪个 Story/事件阻塞
3. `original_status`：进入 BLOCKED 前的状态（用于恢复）

恢复时自动回到 `original_status`，而非固定回到某个状态。

### AC 签字率门禁（铁律）

状态流转 = AC 签字率达标，不达标不流转：

| 目标状态 | AC 签字率 | Task 签字率 | 前置条件 |
|---------|----------|------------|---------|
| IN_PROGRESS | ≥ 0% | ≥ 0% | 至少 1 条 Task 已勾选 |
| IN_REVIEW | ≥ 80% | ≥ 50% | 所有功能标准 AC 已勾选 |
| TESTING | 100% | ≥ 80% | 全部 AC 已勾选，测试标准 AC 已验证 |
| COMPLETED | 100% | 100% | 全部 AC + Task 已勾选，QA 验证通过 |

---

## 状态冲突处理

### 场景 1：多个 Story 互相阻塞（循环依赖）

**识别**：Story A blocked_by Story B，Story B blocked_by Story A

**处理**：
1. 检测循环依赖（遍历 blocked_by 链）
2. 打破循环：将其中一个 Story 拆分为更小粒度，解除互相依赖
3. 记录拆分决策

### 场景 2：BLOCKED 恢复时原状态已不适用

**场景**：Story 在 IN_REVIEW 时被 BLOCKED，恢复时发现代码已过时需要重新开发

**处理**：
1. 恢复到 IN_PROGRESS（而非原 IN_REVIEW），因为需要重新开发
2. 在 Story body 中记录状态降级原因
3. 重新评估 AC 签字率

### 场景 3：DEFERRED Story 需要大幅修改

**场景**：DEFERRED Story 恢复到 TODO 后，发现 AC 已过时

**处理**：
1. 恢复到 TODO
2. 重新评估 AC，必要时更新
3. 如变更超过 50% 的 AC，应创建新 Story 替代，保留原 Story 为 CANCELLED

---

**版本历史**:

| 版本 | 日期 | 变更说明 |
|------|------|---------|
| v1.0 | 2026-06-01 | 初始版本：8 状态 FSM + 转换矩阵 + 跳转条件 + 特殊规则 |
