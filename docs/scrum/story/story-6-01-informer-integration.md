---
id: "STORY-6-01"
epic_id: "EPIC-6"
title: "K8s Informer 集成"
description: "集成 K8s Informer，监听 Pod 事件"
status: "COMPLETED"
completed_date: "2026-04-21"
priority: "P0"
story_points: 5
assignee: "dev1@example.com"
reviewer: ""
start_date: "2026-02-01"
target_date: "2026-02-01"
dependencies:
  - "EPIC-5"
tags:
  - "service-layer"
  - "kubernetes"
  - "informer"
acceptance_criteria:
  - "Informer 工厂初始化"
  - "Pod 事件监听实现"
  - "测试通过"
definition_of_done:
  - "factory.go 创建完成"
  - "pod_informer.go 创建完成"
  - "pod_handler.go 创建完成"
  - "event_queue.go 创建完成"
  - "worker.go 创建完成"
  - "事件监听测试通过"
version: "1.1"
created_at: "2026-01-31"
updated_at: "2026-04-21"
implementation_notes: |
  实际实施（2026-02-01 完成）：
  - factory.go (109行): Informer 工厂，支持 Bearer Token + kubeconfig 双认证
  - pod_informer.go (72行): Pod Informer 封装
  - pod_handler.go (126行): Pod 事件处理器（OnAdd/OnUpdate/OnDelete）
  - event_queue.go (71行): 工作队列（RateLimitingQueue）
  - worker.go (108行): 事件处理 Worker
  - 单元测试通过，覆盖率 15.4%（需 K8s 集群的测试已跳过，符合预期）
  - 文件位置：internal/pkgs/k8s/informer/
---

# Story-6-01: K8s Informer 集成

## 1. 用户故事

### 1.1 作为 [开发者]
我想要 [集成 K8s Informer]

### 1.2 我想要 [监听 Pod 事件]

### 1.3 以便于 [实时处理 Pod 状态变更]

---

## 2. 任务描述

### 2.1 背景

服务需要监听 K8s Pod 事件，实时处理 DevPod 状态变更。使用 Informer 模式实现高效的事件监听。

### 2.2 目标

- 集成 K8s Informer
- 实现 Pod 事件监听
- 配置事件队列

### 2.3 范围

**包含**：
- Informer 工厂
- Pod Informer
- 事件队列

**不包含**：
- Pod 事件处理（STORY-6-02）

---

## 3. 技术设计

### 3.1 Informer 工厂

```go
// internal/pkgs/k8s/informer/factory.go

package informer

import (
    "context"
    "{PROJECT_NAME}/internal/config"
    "k8s.io/client-go/informers"
    "k8s.io/client-go/kubernetes"
    "k8s.io/client-go/rest"
    "k8s.io/client-go/tools/cache"
    "k8s.io/client-go/tools/clientcmd"
)

type Factory struct {
    informers.SharedInformerFactory
    client *kubernetes.Clientset
}

func NewFactory(ctx context.Context, cfg *config.Kubeconfig) (*Factory, error) {
    // 构建 K8s 配置
    var restConfig *rest.Config
    var err error

    if cfg.K8sBearerToken != "" {
        // 使用 Bearer Token
        restConfig = &rest.Config{
            Host:        cfg.K8sApiServerUrl,
            BearerToken: cfg.K8sBearerToken,
            TLSClientConfig: rest.TLSClientConfig{
                CAFile: cfg.K8sCaFilePath,
            },
        }
    } else {
        // 使用 kubeconfig 文件
        restConfig, err = clientcmd.BuildConfigFromFlags("", cfg.K8sCaFilePath)
        if err != nil {
            return nil, err
        }
    }

    // 创建 K8s 客户端
    client, err := kubernetes.NewForConfig(restConfig)
    if err != nil {
        return nil, err
    }

    // 创建 Informer 工厂
    factory := informers.NewSharedInformerFactoryWithOptions(
        client,
        0,
        informers.WithNamespace(cfg.DevPodNamespace),
    )

    return &Factory{
        SharedInformerFactory: factory,
        client:                client,
    }, nil
}

func (f *Factory) Start(ctx context.Context) {
    f.SharedInformerFactory.Start(ctx.Done())
    f.SharedInformerFactory.WaitForCacheSync(ctx.Done())
}
```

### 3.2 Pod Informer

```go
// internal/pkgs/k8s/informer/pod_informer.go

package informer

import (
    "context"
    "{PROJECT_NAME}/internal/pkgs/k8s/extractor"
    "k8s.io/api/core/v1"
    "k8s.io/client-go/informers"
    "k8s.io/client-go/tools/cache"
)

type PodInformer struct {
    informer cache.SharedIndexInformer
    handler *PodEventHandler
}

type PodEventHandler struct {
    queue     workqueue.RateLimitingInterface
    extractor *extractor.MetadataExtractor
}

func NewPodInformer(factory *Factory, handler *PodEventHandler) *PodInformer {
    informer := factory.Core().V1().Pods().Informer()

    informer.AddEventHandler(cache.ResourceEventHandlerFuncs{
        AddFunc:    handler.OnAdd,
        UpdateFunc: handler.OnUpdate,
        DeleteFunc: handler.OnDelete,
    })

    return &PodInformer{
        informer: informer,
        handler: handler,
    }
}

func (h *PodEventHandler) OnAdd(obj interface{}) {
    pod := obj.(*v1.Pod)
    if !h.isDevPod(pod) {
        return
    }
    metadata := h.extractor.Extract(pod)
    h.queue.Add(metadata)
}

func (h *PodEventHandler) OnUpdate(oldObj, newObj interface{}) {
    oldPod := oldObj.(*v1.Pod)
    newPod := newObj.(*v1.Pod)
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

---

## 4. 实施步骤

### 4.1 步骤 1: 创建 Informer 目录

```bash
mkdir -p internal/pkgs/k8s/informer
```

### 4.2 步骤 2: 实现 Informer 工厂

创建 `internal/pkgs/k8s/informer/factory.go`。

### 4.3 步骤 3: 实现 Pod Informer

创建 `internal/pkgs/k8s/informer/pod_informer.go`。

### 4.4 步骤 4: 集成到服务上下文

更新 `internal/svc/service_context.go`。

### 4.5 步骤 5: 编写测试

创建测试文件。

### 4.6 步骤 6: 运行测试

```bash
go test -v ./internal/pkgs/k8s/informer/...
```

---

## 5. 测试计划

### 5.1 单元测试

- [ ] Informer 初始化测试
- [ ] 事件处理测试

### 5.2 集成测试

- [ ] K8s 集群连接测试

---

## 6. 验收标准

### 6.1 功能验收

- [ ] Informer 正常启动
- [ ] Pod 事件可正常监听

### 6.2 性能验收

- [ ] 事件处理延迟 < 1 秒

---

## 7. 附录

### 7.1 参考文档

- [client-go 文档](https://github.com/kubernetes/client-go)
- [EPIC-6: 服务层实现](../prd/epic-6-service-layer.md)
