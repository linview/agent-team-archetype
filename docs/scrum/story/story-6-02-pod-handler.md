---
id: "STORY-6-02"
epic_id: "EPIC-6"
title: "Pod 事件处理"
description: "实现 Pod 事件处理器，处理 Add/Update/Delete 事件"
status: "COMPLETED"
completed_date: "2026-04-21"
priority: "P0"
story_points: 5
assignee: "dev1@example.com"
reviewer: ""
start_date: "2026-02-01"
target_date: "2026-02-01"
dependencies:
  - "STORY-6-01"
tags:
  - "service-layer"
  - "event-handler"
acceptance_criteria:
  - "Pod 事件处理器实现"
  - "事件队列处理实现"
  - "测试通过"
definition_of_done:
  - "metadata.go 创建完成"
  - "source_identifier.go 创建完成"
  - "gpu_info.go 创建完成"
  - "pod_handler.go 创建完成"
  - "event_queue.go 创建完成"
  - "事件处理测试通过"
version: "1.1"
created_at: "2026-01-31"
updated_at: "2026-04-21"
implementation_notes: |
  实际实施（2026-02-01 完成）：
  - metadata.go (205行): Pod 元数据提取器，提取 GPU/用户/团队/项目信息
  - source_identifier.go (120行): Pod 来源识别（DevPod vs ArgoWorkflow vs RayJob）
  - gpu_info.go (89行): GPU 信息提取
  - event_processor.go (281行): 事件处理器，处理 Pod 生命周期事件
  - 单元测试通过，extractor 覆盖率 41.7%
  - 文件位置：internal/pkgs/k8s/extractor/, internal/pkgs/calculator/event_processor.go
---

# Story-6-02: Pod 事件处理

## 1. 用户故事

### 1.1 作为 [开发者]
我想要 [实现 Pod 事件处理器]

### 1.2 我想要 [异步处理 Pod 事件]

### 1.3 以便于 [提高事件处理效率]

---

## 2. 任务描述

### 2.1 背景

Pod 事件需要异步处理，使用工作队列实现事件去重和限流。

### 2.2 目标

- 实现事件处理器
- 实现事件队列
- 实现事件处理逻辑

### 2.3 范围

**包含**：
- Pod 事件处理器
- 工作队列
- 事件处理逻辑

---

## 3. 技术设计

### 3.1 事件队列

```go
// internal/pkgs/k8s/informer/event_queue.go

package informer

import (
    "context"
    "github.com/go-logr/logr"
    "k8s.io/client-go/util/workqueue"
)

type Event struct {
    PodName   string
    Namespace string
    Delete    bool
}

type EventQueue struct {
    queue workqueue.RateLimitingInterface
    log   logr.Logger
}

func NewEventQueue(log logr.Logger) *EventQueue {
    return &EventQueue{
        queue: workqueue.NewNamedRateLimitingQueue(
            workqueue.DefaultControllerRateLimiter(),
            "pod-events",
        ),
        log: log,
    }
}

func (q *EventQueue) Add(event *Event) {
    q.queue.Add(event)
}

func (q *EventQueue) Get(ctx context.Context) (*Event, bool) {
    item, shutdown := q.queue.Get()
    if shutdown {
        return nil, false
    }
    event := item.(*Event)
    return event, true
}

func (q *EventQueue) Done(event *Event) {
    q.queue.Done(event)
}

func (q *EventQueue) Shutdown() {
    q.queue.ShutDown()
}
```

### 3.2 事件处理器

```go
// internal/pkgs/k8s/informer/pod_handler.go

package informer

import (
    "context"
    "{PROJECT_NAME}/internal/pkgs/k8s/extractor"
    "{PROJECT_NAME}/internal/pkgs/calculator"
    "k8s.io/api/core/v1"
    "k8s.io/client-go/util/workqueue"
)

type PodHandler struct {
    queue      workqueue.RateLimitingInterface
    extractor  *extractor.MetadataExtractor
    calculator *calculator.Engine
    log        logr.Logger
}

func NewPodHandler(
    queue workqueue.RateLimitingInterface,
    extractor *extractor.MetadataExtractor,
    calculator *calculator.Engine,
    log logr.Logger,
) *PodHandler {
    return &PodHandler{
        queue:      queue,
        extractor:  extractor,
        calculator: calculator,
        log:        log,
    }
}

func (h *PodHandler) Run(ctx context.Context, workers int) {
    for i := 0; i < workers; i++ {
        go h.runWorker(ctx, i)
    }
}

func (h *PodHandler) runWorker(ctx context.Context, workerID int) {
    for h.processNextItem(ctx) {
    }
}

func (h *PodHandler) processNextItem(ctx context.Context) bool {
    item, shutdown := h.queue.Get()
    if shutdown {
        return false
    }
    defer h.queue.Done(item)

    event := item.(*extractor.PodMetadata)
    if err := h.processEvent(ctx, event); err != nil {
        h.log.Error(err, "Error processing event", "pod", event.PodName)
        h.queue.AddRateLimited(item)
    } else {
        h.queue.Forget(item)
    }

    return true
}

func (h *PodHandler) processEvent(ctx context.Context, metadata *extractor.PodMetadata) error {
    h.log.Info("Processing Pod event", "pod", metadata.PodName, "phase", metadata.Phase)

    // 调用计算引擎处理
    return h calculator.Process(ctx, metadata)
}
```

---

## 4. 实施步骤

### 4.1 步骤 1: 创建事件队列

创建 `internal/pkgs/k8s/informer/event_queue.go`。

### 4.2 步骤 2: 实现 Pod 事件处理器

创建 `internal/pkgs/k8s/informer/pod_handler.go`。

### 4.3 步骤 4: 集成到 Informer

更新 `internal/pkgs/k8s/informer/pod_informer.go`。

### 4.5 步骤 5: 编写测试

创建测试文件。

### 4.6 步骤 6: 运行测试

```bash
go test -v ./internal/pkgs/k8s/informer/...
```

---

## 5. 测试计划

### 5.1 单元测试

- [ ] 事件队列测试
- [ ] 事件处理器测试

### 5.2 集成测试

- [ ] 端到端事件处理测试

---

## 6. 验收标准

### 6.1 功能验收

- [ ] Pod 事件可正常处理
- [ ] 事件去重正常
- [ ] 限流正常

### 6.2 性能验收

- [ ] 并发处理 100+ events/s

---

## 7. 附录

### 7.1 参考文档

- [EPIC-6: 服务层实现](../prd/epic-6-service-layer.md)
