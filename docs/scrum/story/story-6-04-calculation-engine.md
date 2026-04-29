---
id: "STORY-6-04"
epic_id: "EPIC-6"
title: "{BUSINESS_SHORT}计算引擎"
description: "实现 {BUSINESS_SHORT}计算引擎和状态机"
status: "COMPLETED"
completed_date: "2026-04-21"
priority: "P0"
story_points: 8
assignee: "user@example.com"
reviewer: ""
start_date: "2026-02-01"
target_date: "2026-02-01"
dependencies:
  - "STORY-6-03"
tags:
  - "service-layer"
  - "calculation"
  - "state-machine"
acceptance_criteria:
  - "计算引擎实现"
  - "状态机实现"
  - "测试通过"
definition_of_done:
  - "gpu_calculator.go 创建完成"
  - "state_machine.go 创建完成"
  - "event_processor.go 创建完成"
  - "engine.go 创建完成"
  - "单元测试通过"
version: "1.1"
created_at: "2026-01-31"
updated_at: "2026-04-21"
implementation_notes: |
  实际实施（2026-02-01 完成）：
  - gpu_calculator.go (164行): GPU×Hours 计算引擎
    - StartGPUUsage(): 创建 {BUSINESS_SHORT}记录
    - StopGPUUsage(): 停止 {BUSINESS_SHORT}并计算 GPU×Hours
    - GetTotalGPUUsage(): 查询总用量
    - getNextUsageCycle(): 支持多次启停（usage_cycle 递增）
  - state_machine.go (148行): DevPod 状态机
    - 支持状态转换：PENDING → CREATED → RUNNING → STOPPED → RELEASED
    - 支持异常状态：ABORTED
    - 完整的状态转换验证
  - event_processor.go (281行): Pod 生命周期事件处理器
    - ProcessPodAdded(): 处理 Pod 创建
    - ProcessPodUpdated(): 处理 Pod 更新
    - ProcessPodDeleted(): 处理 Pod 删除
  - engine.go (425行): 计算引擎主逻辑
  - 单元测试通过，状态机测试 100% 覆盖
  - 单元测试覆盖率 16.6%（核心逻辑已覆盖）
  - 文件位置：internal/pkgs/calculator/
---

# Story-6-04: {BUSINESS_SHORT}计算引擎

## 1. 用户故事

### 1.1 作为 [开发者]
我想要 [实现 {BUSINESS_SHORT}计算引擎]

### 1.2 我想要 [实现状态机管理 DevPod 生命周期]

### 1.3 以便于 [精确计算 {BUSINESS_SHORT}]

---

## 2. 任务描述

### 2.1 背景

{BUSINESS_SHORT}需要根据 DevPod 状态变化精确计算。需要实现状态机和计算引擎来处理 Pod 生命周期事件。

### 2.2 目标

- 实现状态机
- 实现 {BUSINESS_SHORT}计算引擎
- 实现用量记录管理

### 2.3 范围

**包含**：
- 状态机
- 计算引擎
- GPU 时长计算

---

## 3. 技术设计

### 3.1 状态机

```go
// internal/pkgs/calculator/state_machine.go

package calculator

type DevPodState string

const (
    Pending  DevPodState = "PENDING"
    Running  DevPodState = "RUNNING"
    Stopped  DevPodState = "STOPPED"
    Released DevPodState = "RELEASED"
)

type StateMachine struct{}

func NewStateMachine() *StateMachine {
    return &StateMachine{}
}

func (sm *StateMachine) Transition(currentState DevPodState, event string) DevPodState {
    switch currentState {
    case Pending:
        if event == "PodRunning" {
            return Running
        }
    case Running:
        if event == "PodStopped" {
            return Stopped
        }
    case Stopped:
        if event == "PodDeleted" {
            return Released
        }
    }
    return currentState
}

func (sm *StateMachine) CanTransition(from, to DevPodState) bool {
    transitions := map[DevPodState][]DevPodState{
        Pending:  {Running},
        Running:  {Stopped},
        Stopped:  {Released},
        Released: {},
    }

    allowed, exists := transitions[from]
    if !exists {
        return false
    }

    for _, state := range allowed {
        if state == to {
            return true
        }
    }
    return false
}
```

### 3.2 计算引擎

```go
// internal/pkgs/calculator/engine.go

package calculator

import (
    "context"
    "{PROJECT_NAME}/internal/pkgs/database/dao"
    "{PROJECT_NAME}/internal/pkgs/k8s/extractor"
    "time"
)

type Engine struct {
    stateMachine       *StateMachine
    devPodDAO          *dao.DevPodDAO
    usageRecordDAO     *dao.DevPodUsageRecordDAO
}

func NewEngine(
    devPodDAO *dao.DevPodDAO,
    usageRecordDAO *dao.DevPodUsageRecordDAO,
) *Engine {
    return &Engine{
        stateMachine:   NewStateMachine(),
        devPodDAO:      devPodDAO,
        usageRecordDAO: usageRecordDAO,
    }
}

func (e *Engine) Process(ctx context.Context, metadata *extractor.PodMetadata) error {
    // 查询或创建 DevPod
    devPod, err := e.getOrCreateDevPod(ctx, metadata)
    if err != nil {
        return err
    }

    // 状态转换
    newState := e.stateMachine.Transition(DevPodState(devPod.Status), metadata.Phase)

    switch newState {
    case Running:
        return e.startUsage(ctx, devPod, metadata)
    case Stopped:
        return e.stopUsage(ctx, devPod, metadata)
    case Released:
        return e.releasePod(ctx, devPod)
    }

    return nil
}

func (e *Engine) startUsage(ctx context.Context, devPod *model.DevPod, metadata *extractor.PodMetadata) error {
    // 创建用量记录
    record := &model.DevPodUsageRecord{
        DevPodID:  devPod.ID,
        StartTime: metadata.StartTime.Time,
        GPUHours:  0,
        Status:    "active",
    }
    return e.usageRecordDAO.Create(ctx, record)
}

func (e *Engine) stopUsage(ctx context.Context, devPod *model.DevPod, metadata *extractor.PodMetadata) error {
    // 获取活跃记录
    record, err := e.usageRecordDAO.GetActiveByDevPodID(ctx, devPod.ID)
    if err != nil {
        return err
    }

    // 计算 GPU 时长
    endTime := time.Now()
    duration := endTime.Sub(record.StartTime)
    gpuHours := duration.Hours() * float64(devPod.GPUCount)

    // 完成记录
    return e.usageRecordDAO.Complete(ctx, record.ID, endTime, gpuHours)
}
```

---

## 4. 实施步骤

### 4.1 步骤 1: 创建计算器目录

```bash
mkdir -p internal/pkgs/calculator
```

### 4.2 步骤 2: 实现状态机

创建 `internal/pkgs/calculator/state_machine.go`。

### 4.3 步骤 3: 实现计算引擎

创建 `internal/pkgs/calculator/engine.go`。

### 4.4 步骤 4: 编写测试

创建测试文件。

### 4.5 步骤 5: 运行测试

```bash
go test -v ./internal/pkgs/calculator/...
```

---

## 5. 测试计划

### 5.1 单元测试

- [ ] 状态机转换测试
- [ ] GPU 时长计算测试

### 5.2 集成测试

- [ ] 端到端计算测试

---

## 6. 验收标准

### 6.1 功能验收

- [ ] 状态机转换正确
- [ ] GPU 时长计算准确
- [ ] 测试通过

### 6.2 性能验收

- [ ] 计算延迟 < 100ms

---

## 7. 附录

### 7.1 参考文档

- [EPIC-6: 服务层实现](../prd/epic-6-service-layer.md)
