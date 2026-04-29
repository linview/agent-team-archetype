---
id: "EPIC-6"
title: "服务层实现（K8s Informer + 业务逻辑）"
description: "实现服务层，包括 K8s Informer 集成、Pod 事件处理、{BUSINESS_SHORT}计算引擎"
status: "CANCELLED"
priority: "P2"
cancelled_date: "2026-04-02"
cancelled_reason: "架构版本冲突：Epic-6 基于 v3.3 设计（已过时），统一到 Epic-15 v4.0 设计"
layer: "SERVICE_LAYER"
owner: "user@example.com"
start_date: "2026-02-01"
target_date: "2026-02-01"
completed_date: "2026-02-01"
stories:
  - "STORY-6-01"
  - "STORY-6-02"
  - "STORY-6-03"
  - "STORY-6-04"
  - "STORY-6-05"
  - "STORY-6-06"
  - "STORY-6-07"
  - "STORY-6-08"
  - "STORY-6-09"
  - "STORY-6-10"
  - "STORY-6-11"
  - "STORY-6-12"
  - "STORY-6-13"
  - "STORY-6-14"
  - "STORY-6-15"
  - "STORY-6-16"
dependencies:
  - "EPIC-5"
tags:
  - "service-layer"
  - "kubernetes"
  - "informer"
  - "gpu-calculation"
version: "1.2"
created_at: "2026-01-31"
updated_at: "2026-04-02"
implementation_notes: |
  ⚠️ **Epic 已取消**（2026-04-02）：
  - Epic-6 基于 v3.3 设计（已归档至 `archive/service_layer_architecture_v3.3_20260402.md`）
  - Epic-15 基于 v4.0 设计（当前标准：职责分离 + TTL 策略 + SSOT 修复）
  - **未完成 Story 已取消**（STORY-6-16），统一到 Epic-15

  **已完成部分保留**（2026-02-01）：
  - ✅ STORY-6-01 ~ 6-14: 代码已完整实现（12 个核心文件，2318 行代码）
  - ✅ K8s Informer 集成：factory.go, pod_informer.go, pod_handler.go, event_queue.go, worker.go
  - ✅ Pod 事件处理：metadata.go, source_identifier.go, gpu_info.go
  - ✅ {BUSINESS_SHORT}计算：gpu_calculator.go, state_machine.go, event_processor.go, engine.go
  - ✅ 单元测试全部通过
  - ✅ 代码编译通过
  - 文件位置：internal/pkgs/k8s/informer/, internal/pkgs/k8s/extractor/, internal/pkgs/calculator/

  **未完成部分取消**：
  - ❌ STORY-6-16: TTL 自动清理实施（由 Epic-15 STORY-15-01/15-02/15-04 替代）
---

# Epic-6: 服务层实现（K8s Informer + 业务逻辑）

## 1. 概述

### 1.1 背景

服务层是业务逻辑的核心，负责监听 K8s Pod 事件、提取 GPU 元数据、计算 {BUSINESS_SHORT}。使用 K8s Informer 模式实现高效的事件监听，结合状态机实现 {BUSINESS_SHORT}的精确计算。

### 1.2 目标

- 集成 K8s Informer 监听 Pod 事件
- 实现 Pod 元数据提取器
- 实现 {BUSINESS_SHORT}计算引擎
- 实现状态机管理 DevPod 生命周期

### 1.3 范围

**包含**：
- K8s Informer 工厂
- Pod 事件处理器
- GPU 元数据提取
- {BUSINESS_SHORT}计算引擎
- DevPod 状态机

**不包含**：
- RESTful API 实现（应用层）

---

## 2. 需求分析

### 2.1 功能需求

| 需求 ID | 需求描述 | 优先级 |
|---------|---------|--------|
| FR-6-01 | K8s Informer 工厂初始化 | P0 |
| FR-6-02 | Pod 事件监听（Add/Update/Delete） | P0 |
| FR-6-03 | GPU 元数据提取 | P0 |
| FR-6-04 | {BUSINESS_SHORT}计算引擎 | P0 |
| FR-6-05 | DevPod 状态机 | P0 |
| FR-6-06 | 事件队列与异步处理 | P1 |

### 2.2 非功能需求

| 需求 ID | 需求描述 | 指标 |
|---------|---------|------|
| NFR-6-01 | 事件处理延迟 | < 1 秒 |
| NFR-6-02 | 并发处理能力 | 100+ events/s |
| NFR-6-03 | Informer 重连时间 | < 5 秒 |

### 2.3 技术约束

- **K8s 客户端**: client-go v0.33.0
- **Informer**: SharedInformerFactory
- **队列**: workqueue.RateLimitingQueue

---

## 3. 架构设计

### 3.1 架构图

```
┌─────────────────────────────────────────────────┐
│                  K8s API Server                 │
└──────────────────┬──────────────────────────────┘
                   │ Watch Events
                   ▼
┌─────────────────────────────────────────────────┐
│          SharedInformerFactory                  │
│  ┌───────────────────────────────────────────┐  │
│  │            Pod Informer                   │  │
│  └───────────────────────────────────────────┘  │
│                   │                              │
│                   ▼                              │
│  ┌───────────────────────────────────────────┐  │
│  │          Event Handler                    │  │
│  │  • OnAdd(Pod)                             │  │
│  │  • OnUpdate(Pod)                          │  │
│  │  • OnDelete(Pod)                          │  │
│  └───────────────────────────────────────────┘  │
│                   │                              │
│                   ▼                              │
│  ┌───────────────────────────────────────────┐  │
│  │       Metadata Extractor                  │  │
│  │  • Extract GPU Type                       │  │
│  │  • Extract GPU Count                      │  │
│  │  • Extract DevPod Metadata                │  │
│  └───────────────────────────────────────────┘  │
│                   │                              │
│                   ▼                              │
│  ┌───────────────────────────────────────────┐  │
│  │      GPU Usage Calculation Engine         │  │
│  │  • State Machine                          │  │
│  │  • GPU Hours Calculation                  │  │
│  │  • Quality Monitor                        │  │
│  └───────────────────────────────────────────┘  │
│                   │                              │
│                   ▼                              │
│  ┌───────────────────────────────────────────┐  │
│  │            Data Layer                     │  │
│  │  • Save to Database                       │  │
│  │  • Update Cache                           │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

### 3.2 目录结构

```
internal/pkgs/
├── k8s/
│   ├── informer/
│   │   ├── factory.go           # Informer 工厂
│   │   ├── pod_handler.go       # Pod 事件处理器
│   │   └── event_queue.go       # 事件队列
│   └── extractor/
│       ├── metadata.go          # 元数据提取器
│       └── gpu_info.go          # GPU 信息提取
├── calculator/
│   ├── engine.go                # 计算引擎
│   ├── state_machine.go         # 状态机
│   └── gpu_hours.go             # GPU 时长计算
└── service/
    ├── example-service_service.go       # DevPod 服务
    └── usage_service.go         # 用量服务
```

### 3.3 Pod 事件处理器

```go
package informer

import (
    "k8s.io/api/core/v1"
)

type PodEventHandler struct {
    queue       workqueue.RateLimitingInterface
    extractor   *extractor.MetadataExtractor
    calculator  *calculator.Engine
}

func (h *PodEventHandler) OnAdd(obj interface{}) {
    pod := obj.(*v1.Pod)
    // 检查是否为 DevPod
    if !h.isDevPod(pod) {
        return
    }
    // 提取元数据
    metadata := h.extractor.Extract(pod)
    // 加入队列
    h.queue.Add(metadata)
}

func (h *PodEventHandler) OnUpdate(oldObj, newObj interface{}) {
    oldPod := oldObj.(*v1.Pod)
    newPod := newObj.(*v1.Pod)
    // 检查状态变更
    if oldPod.Status.Phase != newPod.Status.Phase {
        metadata := h.extractor.Extract(newPod)
        h.queue.Add(metadata)
    }
}

func (h *PodEventHandler) OnDelete(obj interface{}) {
    pod := obj.(*v1.Pod)
    if !h.isDevPod(pod) {
        return
    }
    metadata := h.extractor.Extract(pod)
    metadata.Delete = true
    h.queue.Add(metadata)
}

func (h *PodEventHandler) isDevPod(pod *v1.Pod) bool {
    _, exists := pod.Labels["example-service.example.com/managed"]
    return exists
}
```

### 3.4 GPU 元数据提取器

```go
package extractor

import (
    "k8s.io/api/core/v1"
)

type MetadataExtractor struct{}

type PodMetadata struct {
    PodName      string
    Namespace    string
    GPUCount     int
    GPUType      string
    Phase        v1.PodPhase
    StartTime    *metav1.Time
    Delete       bool
}

func (e *MetadataExtractor) Extract(pod *v1.Pod) *PodMetadata {
    metadata := &PodMetadata{
        PodName:   pod.Name,
        Namespace: pod.Namespace,
        Phase:     pod.Status.Phase,
        StartTime: pod.Status.StartTime,
        Delete:    false,
    }

    // 提取 GPU 数量
    for _, container := range pod.Spec.Containers {
        if gpu, ok := container.Resources.Requests["nvidia.com/gpu"]; ok {
            metadata.GPUCount += int(gpu.Value())
        }
    }

    // 提取 GPU 类型
    if nodeSelector, ok := pod.Spec.NodeSelector["gpu-type"]; ok {
        metadata.GPUType = nodeSelector
    }

    return metadata
}
```

### 3.5 {BUSINESS_SHORT}计算引擎

```go
package calculator

import (
    "time"
)

type Engine struct {
    stateMachine *StateMachine
}

type GPUUsageRecord struct {
    DevPodID    int64
    StartTime   time.Time
    EndTime     *time.Time
    GPUCount    int
    GPUHours    float64
}

func (e *Engine) Calculate(record *GPUUsageRecord) error {
    // 状态机处理
    newState := e.stateMachine.Transition(record)

    switch newState {
    case Running:
        // 开始计算
        return e.startCalculation(record)
    case Stopped:
        // 结束计算
        return e.endCalculation(record)
    default:
        return nil
    }
}

func (e *Engine) startCalculation(record *GPUUsageRecord) error {
    // 插入用量记录
    record.StartTime = time.Now()
    return nil
}

func (e *Engine) endCalculation(record *GPUUsageRecord) error {
    // 计算 GPU 时长
    if record.EndTime != nil {
        duration := record.EndTime.Sub(record.StartTime)
        record.GPUHours = duration.Hours() * float64(record.GPUCount)
    }
    return nil
}
```

### 3.6 状态机

```go
package calculator

type DevPodState string

const (
    Pending   DevPodState = "PENDING"
    Running   DevPodState = "RUNNING"
    Stopped   DevPodState = "STOPPED"
    Released  DevPodState = "RELEASED"
)

type StateMachine struct{}

func (sm *StateMachine) Transition(record *GPUUsageRecord) DevPodState {
    // 状态转换逻辑
    // PENDING -> RUNNING -> STOPPED -> RELEASED
    return Running
}
```

---

## 4. 实施计划

### 4.1 Story 列表

| Story ID | Story 标题 | 故事点 | 预估工期 |
|----------|-----------|--------|---------|
| STORY-6-01 | K8s Informer 集成 | 5 | 1 天 |
| STORY-6-02 | Pod 事件处理 | 5 | 1 天 |
| STORY-6-03 | GPU 元数据提取 | 3 | 1 天 |
| STORY-6-04 | {BUSINESS_SHORT}计算引擎 | 8 | 1 天 |

### 4.2 依赖关系

```
EPIC-5（数据层）
    ↓
STORY-6-01（Informer）
    ↓
STORY-6-02（事件处理）
    ↓
STORY-6-03（元数据提取） ←→ STORY-6-04（计算引擎）
```

### 4.3 里程碑

| 里程碑 | 日期 | 交付物 |
|--------|------|--------|
| M6-1 | Day 1 | Informer 集成完成 |
| M6-2 | Day 2 | 事件处理完成 |
| M6-3 | Day 3 | 元数据提取完成 |
| M6-4 | Day 4 | 计算引擎完成，Epic-6 完成 |

---

## 5. 风险与依赖

### 5.1 技术风险

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|---------|
| Informer 断连 | 高 | 中 | 实现重连机制 |
| 事件堆积 | 高 | 中 | 使用工作队列限流 |
| 状态机死锁 | 中 | 低 | 状态超时自动恢复 |

### 5.2 资源依赖

| 依赖项 | 类型 | 状态 |
|--------|------|------|
| EPIC-5（数据层） | Epic | PLANNED |
| K8s 集群访问权限 | 资源 | 需申请 |

### 5.3 缓解措施

- 使用 SharedInformerFactory 减少资源消耗
- 实现事件重试机制
- 添加 Prometheus 监控指标

---

## 6. 验收标准

### 6.1 功能验收

- [ ] Informer 成功监听 Pod 事件
- [ ] 元数据提取正确
- [ ] {BUSINESS_SHORT}计算准确
- [ ] 状态机转换正确

### 6.2 性能验收

- [ ] 事件处理延迟 < 1 秒
- [ ] 并发处理 100+ events/s

### 6.3 质量验收

- [ ] 单元测试覆盖率 > 80%
- [ ] 集成测试通过

---

## 7. 附录

### 7.1 参考文档

- [client-go 官方文档](https://github.com/kubernetes/client-go)
- [K8s Informer 机制](https://kubernetes.io/docs/reference/using-api/api-concepts/)

### 7.2 设计文档链接

- [{BUSINESS_SHORT}计算引擎设计](../design/gpu_usage_design.md)
