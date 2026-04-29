# Resource Meter 服务层架构设计 v4.2

**文档版本**: v4.2
**创建日期**: 2026-02-03
**最后更新**: 2026-04-25
**作者**: Development Team + Architect + Architect + Architect + Architect + Architect + Architect
**状态**: 正式发布
**替代版本**: v4.1 (已归档至 `archive/service_layer_architecture_v4.1_20260425.md`)

---

## 📋 版本历史

| 版本 | 日期 | 变更说明 | 作者 |
|------|------|---------|------|
| v1.0 | 2026-02-02 | 初始版本，完整服务层架构设计 | Development Team |
| v2.0 | 2026-02-03 | **重大更新**：明确活跃 Pod GPU 实时计算实现规范（从"建议"改为"强制要求"） | QA + Development Team |
| v3.0 | 2026-02-04 | **新增第 8 章**：历史记录存储优化（字段精简 + 事件压缩） | Development Team |
| v3.1 | 2026-02-06 | **新增第 9 章**：时区管理设计（统一 UTC+8，消除负数 {BUSINESS_SHORT}） | Development Team |
| v3.2 | 2026-02-09 | **新增第 10 章**：元数据提取规范（Annotation 前缀统一 + 服务层过滤逻辑重写） | Development Team |
| v3.3 | 2026-03-10 | **新增第 4.4 章**：TrainJob 支持（Kubeflow → JobSet → Pod 架构） | Development Team |
| **v4.0** | **2026-04-02** | **新增第 11 章**：数据层架构优化（职责分离 + TTL 策略 + SSOT 修复） | Development Team |
| **v4.1** | **2026-04-07** | **完善数据校准方案：终态状态机优先级 + Phase 0-4 完整实施方案** | Architect |
| **v4.2** | **2026-04-25** | **🎯 查询路由优化 + ABORTED条件性同步** | Architect |

**v4.0 主要变更**：
- ✅ **新增第 11 章**：数据层架构优化
  - ✅ 新增 `pod_resource_dim_metric` 维度表（GPU 聚合查询专用）
  - ✅ `pod_resource_status` 职责重新定义为状态流转记录表（30天 TTL）
  - ✅ 数据同步机制设计（15分钟定时同步）
  - ✅ TTL 策略优化（status: 30d, dim_metric: 90d, history: 15d）
- ✅ **SSOT 问题修复**：添加 `k8s_pod_uid UNIQUE` 约束
- ✅ **存储优化**：预期节省 ~69% 存储空间（3500 MB → 1100 MB）

**v4.1 主要变更**：
- ✅ **完善 11.7 节**：从简单 SQL 方案升级为完整的数据校准方案
  - ✅ 新增：终态状态机优先级排序（RELEASED > ABORTED > STOPPED > RUNNING > CREATED > PENDING）
  - ✅ 新增：多级排序规则（updated_at DESC + 状态优先级 + resource_id DESC）
  - ✅ 新增：完整实施方案（Phase 0-4）
  - ✅ 新增：{BUSINESS_SHORT}数据保护策略（重新分配 usage_cycle）
  - ✅ 新增：AC 验证准则（5 个验收标准）
  - ✅ 新增：回滚方案
- ✅ **解决并发写入问题**：Informer 2 个 Worker 并发写入导致 `updated_at` 相同（0.000000 秒差异）
- ✅ **向后兼容**：不破坏现有设计，只是补充细节

**v4.1.1 主要变更**：
- ✅ **对齐 Research 文档**：`docs/design/research/story-15-10-dimmetric-syncer-design-analysis.md`
  - ✅ 修正同步查询条件：`created_at OR updated_at >= 15min`（捕获新增和更新记录）
  - ✅ 修正技术选型：`time.Ticker`（标准库，零依赖）替代 `cron.Every`
  - ✅ 明确状态过滤策略：只同步有效状态（RUNNING, STOPPED, RELEASED）

**v4.2 主要变更**：
- ✅ **新增 11.4.1 节**：ABORTED 状态的条件性同步机制（关键修复）
  - ✅ 新增前置过滤条件：只同步有 {BUSINESS_SHORT}的 ABORTED 状态
  - ✅ 修复数据丢失问题：确保 ABORTED Pod 的 {BUSINESS_SHORT}不丢失
  - ✅ 设计原则：dim_metric 表中 ABORTED 状态必须满足 gpu_usage 表有记录
- ✅ **更新 11.6 节**：查询路由策略优化
  - ✅ 从"按时间范围选择 SSOT"改为"统一使用 dim_metric 表"
  - ✅ 查询逻辑简化：单一路径，易于维护
  - ✅ 数据质量提升：dim_metric 表经过过滤，数据更干净
  - ✅ 性能优化：窄表查询（18字段 vs 40+字段）
  - ⚠️ 15分钟延迟：对 {PROJECT_NAME} SLA 可接受
- ✅ **向后兼容**：不破坏现有设计，只优化查询和同步逻辑
  - ✅ 修正代码位置：`internal/svc/dimmetric_syncer.go`
  - ✅ 修正 Upsert 约束：`ON CONFLICT (k8s_pod_uid)` 替代 `ON CONFLICT (resource_id)`

**v3.3 继承内容**：
- TrainJob 支持（Kubeflow → JobSet → Pod 架构）
- PodSourceType 枚举扩展：新增 `PodSourceTrainJob`
- CMDB Annotations 规范：9 个必需字段定义
- v3.2 继承：Annotation 前缀统一 + 服务层过滤逻辑重写
- v3.1 继承：时区管理设计（统一 UTC+8）
- v3.0 继承：历史记录存储优化
- v2.0 继承：活跃 Pod GPU 实时计算（强制规范）

---

## 📋 文档概述

本文档详细描述了 Resource Meter 项目的服务层架构设计，包括：
- 服务层定位和职责
- K8s Informer 集成机制
- Pod 元数据提取规范（v3.2 新增）
- Pod 来源识别（v3.2 重写，v3.3 扩展 TrainJob）
- Pod 生命周期处理流程
- 状态机设计和 {BUSINESS_SHORT}计算
- 活跃 Pod GPU 实时计算（v2.0 核心更新）
- 历史记录存储优化（v3.0 新增）
- 时区管理设计（v3.1 新增）
- TrainJob 支持（v3.3 新增）
- **数据层架构优化（v4.0 新增）** 🆕
- K8s Event 日志输出设计

**📘 相关文档**：
- **[跨集群部署架构设计 v3.3](service_layer_cross_cluster_deployment_v3.3.md)** - 部署集群与目标监控集群的 RBAC、Token 生成、消费原理
- **[服务层 FAQ v4.1](service_layer_faq_v4.1.md)** - 常见问题及解决方案 🆕
- **[CMDB 设计 v3.0](cmdb_design_v3.0.md)** - Pod 资源管理 + CMDB 完整设计
- **[Research: SSOT 问题分析](../research/deep_dive_resource_id_and_storage_20260402.md)** - resource_id 与 SSOT 问题分析 🆕
- **[Research: TTL 策略调研](../research/ttl_data_consistency_research_20260402.md)** - TTL 策略与数据一致性调研 🆕

---

## 1. 架构概述

### 1.1 三层架构

```
┌─────────────────────────────────────────────────┐
│         Application Layer (API)                 │
│  RESTful API, Request Routing, Response         │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│          Service Layer                          │
│  • K8s Informer (Event Watch)                   │
│  • Event Processor (State Machine)              │
│  • GPU Usage Calculator                         │
│  • Pod Metadata Extractor                       │
│  • DimMetric Syncer (v4.0 新增) 🆕               │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│           Data Layer                            │
│  • pod_resource_status (状态表, 30d TTL)       │
│  • pod_resource_dim_metric (维度表, 90d TTL) 🆕  │
│  • pod_resource_gpu_usage (事实表, 不清理)     │
│  • pod_resource_history (审计表, 15d TTL)       │
│  • cmdb_users, cmdb_teams, cmdb_projects        │
└─────────────────────────────────────────────────┘
```

### 1.2 服务层职责

| 职责 | 说明 | 实现位置 |
|------|------|---------|
| **K8s 事件监听** | 监听所有 namespace 的 Pod 事件 | `internal/pkgs/k8s/informer/factory.go` |
| **Pod 过滤** | 过滤出需要管理的 Pod（DevPod, ArgoWorkflow, RayJob, TrainJob） | `internal/pkgs/k8s/extractor/source_identifier.go` (v3.2 重写, v3.3 扩展) |
| **元数据提取** | 从 Pod 对象提取 GPU 信息、业务信息 | `internal/pkgs/k8s/extractor/metadata.go` |
| **状态管理** | 维护 Pod 生命周期状态（6 个状态） | `internal/pkgs/calculator/state_machine.go` |
| **{BUSINESS_SHORT}计算** | 计算 GPU×Hours，支持多次启停 | `internal/pkgs/calculator/gpu_calculator.go` |
| **活跃 Pod 实时计算** | ✅ v2.0 强制要求：查询时使用 `NOW()` 实时计算 | `internal/dao/pod_resource_gpu_usage_dao.go` |
| **数据同步** | 🆕 v4.0 新增：status → dim_metric 数据同步（15分钟） | `internal/pkg/syncer/dim_metric_syncer.go` |
| **数据持久化** | 将状态和用量数据写入数据库 | `internal/dao/*` |

---

## 2. K8s Informer 监听机制

### 2.1 监听范围

**Namespace 覆盖**：
- **监听所有 namespace**（无 namespace 过滤器）
- 通过 `IsManagedByResourceMeter()` 函数在事件处理层过滤

**代码位置**：`internal/pkgs/k8s/informer/factory.go:73-78`
```go
factory := informers.NewSharedInformerFactoryWithOptions(
    client,
    0, // resync period: 0 means no periodic resync
    // No namespace filter - watch all namespaces
)
```

### 2.2 Pod 过滤条件（v3.2 重写）

**v3.2 架构变更**：从 annotation 显式声明优先，保留降级逻辑

#### 优先级降级机制

| 优先级 | 识别方式 | 条件 | 说明 |
|--------|---------|------|------|
| **P0** | Annotation 显式声明 | `cmdb.example.com/resource-type` | 新方案，推荐 |
| **P1** | 旧 Annotation 降级 | `example-service/resource-type` | ENHANCEMENT-001 调研发现 |
| **P2** | Label 推断 | `app.kubernetes.io/name`, `workflows.argoproj.io/workflow` | 兼容旧 Pod |
| **P3** | OwnerReference 推断 | StatefulSet, Workflow, RayJob | 最后兜底 |

**代码位置**：`internal/pkgs/k8s/extractor/source_identifier.go`

---

## 11. 数据层架构优化（v4.0 新增）🆕

### 11.1 设计背景

**问题发现**（基于 research 文档）：

1. **存储利用率低**：status 表有 40+ 字段，但 GPU 查询只使用 10 个核心字段
2. **数据重复问题**：42.27% 重复率（63.6万条），k8s_pod_uid 缺少 UNIQUE 约束
3. **职责混乱**：status 表既要支持状态流转（高频更新），又要支持聚合查询（高频查询）

**详细分析**：
- **Research: SSOT 问题分析**：`docs/research/deep_dive_resource_id_and_storage_20260402.md`
- **Research: TTL 策略调研**：`docs/research/ttl_data_consistency_research_20260402.md`

### 11.2 职责分离设计

#### 核心思想

```
┌─────────────────────────────────────────────────────────────┐
│                    数据层职责划分                                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  pod_resource_status（状态表）                                │
│  ├─ 职责：Pod 状态流转记录                                       │
│  ├─ 生命周期：30天（与history表对齐）                    │
│  ├─ 特性：读写表，随 K8s Pod 状态跳变而更新                 │
│  └─ 关键操作：Informer 写入、状态机更新                           │
│                                                             │
│  pod_resource_dim_metric（维度表）🆕                           │
│  ├─ 职责：{BUSINESS_SHORT}聚合查询的维度数据                               │
│  ├─ 生命周期：90天                                            │
│  ├─ 特性：只读表，数据同步自 status 表                         │
│  └─ 关键操作：定时同步（15分钟）、TTL 清理                         │
│                                                             │
│  pod_resource_gpu_usage（事实表）                              │
│  ├─ 职责：{BUSINESS_SHORT}事实数据                                         │
│  ├─ 生命周期：不清理                                           │
│  └─ 关键操作：GPU×Hours 计算、写入                               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 11.2.1 SSOT 定义（职责分离架构）🆕

**核心原则**：
> v4.1 架构采用**职责分离 + 时间分层**的 SSOT 设计
> - 同一个 Pod 的数据分布在两个表（status + dim_metric）
> - 通过 `resource_id` UUID 保持关联
> - 按时间范围分层（0-30天 vs 0-90天）
> - 按职责分离（状态流转 vs GPU 查询）

**SSOT 分层定义**：

| 时间范围 | SSOT 表 | 职责 | TTL | 特性 |
|---------|---------|------|-----|------|
| **0-30天** | `pod_resource_status` | 状态流转 + 实时查询 | 30天 | 读写表，Informer 写入 |
| **0-90天** | `pod_resource_dim_metric` | GPU 查询（长期） | 90天 | 只读表，15分钟同步 |

**与 v3.x 架构的对比**：

| 维度 | v3.x（单一 SSOT） | v4.1（职责分离 SSOT） |
|------|------------------|---------------------|
| **SSOT 定义** | status 表（单一） | status + dim_metric（分层） |
| **职责分离** | ❌ 混乱（状态+查询） | ✅ 清晰（状态 vs 查询） |
| **存储利用率** | 🟡 13%（40+ 字段） | ✅ 46%（10 字段） |
| **查询性能** | 🟡 扫描 40+ 字段 | ✅ 扫描 10 字段（60%↓） |
| **TTL 策略** | 🟡 不统一 | ✅ 对齐（30d vs 90d） |
| **数据一致性** | ✅ 完全一致 | 🟡 最终一致（15分钟延迟） |

**一致性保证机制**：

| 机制 | 说明 | 保证 |
|------|------|------|
| **resource_id 关联** | 两个表共享同一个 UUID | ✅ 跨表 JOIN 一致性 |
| **15分钟同步** | DimMetricSyncer 定时同步 | ✅ 最终一致性 |
| **查询路由策略** | 按时间范围选择 SSOT | ✅ 避免数据缺失 |
| **UNIQUE 约束** | k8s_pod_uid 防止重复 | ✅ 数据唯一性 |

**查询模式**：
```sql
-- GPU 聚合查询（0-90天）：使用 dim_metric 表（长期 SSOT）
SELECT
    d.user_id,
    d.team_id,
    COALESCE(SUM(u.gpu_hours), 0) AS total_gpu_hours
FROM pod_resource_dim_metric d      -- ✅ 长期 SSOT
LEFT JOIN pod_resource_gpu_usage u ON d.resource_id = u.resource_id
WHERE d.created_at >= NOW() - INTERVAL '90 days'
GROUP BY d.user_id, d.team_id;

-- Pod 详情查询（0-30天）：使用 status 表（实时 SSOT）
SELECT * FROM pod_resource_status s
WHERE s.resource_id = ?
  AND s.created_at >= NOW() - INTERVAL '30 days';

-- Pod 详情查询（31-90天）：使用 dim_metric 表 + LEFT JOIN status
SELECT
    d.resource_id,
    d.pod_name,
    d.status,
    s.user_name,   -- 允许为 NULL
    s.team_name    -- 允许为 NULL
FROM pod_resource_dim_metric d
LEFT JOIN pod_resource_status s ON d.resource_id = s.resource_id
WHERE d.resource_id = ?;
```

**潜在风险与缓解**：

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 数据同步延迟（15分钟） | 🟡 中 | 查询路由策略（按时间范围） |
| TTL 清理导致数据缺失 | 🔴 高 | 使用 LEFT JOIN（允许 s 为 NULL） |
| 并发写入时序差异 | 🟢 低 | UNIQUE 约束 + 终态状态机优先级 |

### 11.3 表结构设计

> **📖 详细表结构设计**：参见 **[cmdb_tables_v4.2.md](../cmdb/cmdb_tables_v4.2.md)** - 数据层表结构设计（权威来源）

本节仅列出核心表结构的概要，详细的字段定义、索引、约束请参考 `cmdb_tables_v4.1.md`。

#### pod_resource_status（状态表，30天 TTL）

**职责**：Pod 状态流转记录（读写表）

**保留完整字段**（约 40 个字段）：
```sql
CREATE TABLE pod_resource_status (
    -- 主键和标识
    resource_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    k8s_pod_uid VARCHAR(64) NOT NULL,  -- ✅ v4.0: 添加 UNIQUE 约束
    pod_name VARCHAR(128) NOT NULL,
    pod_namespace VARCHAR(64) NOT NULL DEFAULT 'example-service',
    pod_resource_type VARCHAR(32) NOT NULL DEFAULT 'EXAMPLE_SERVICE',
    
    -- K8s Owner 信息
    k8s_owner_kind VARCHAR(64),
    k8s_owner_name VARCHAR(128),
    k8s_pod_name VARCHAR(128),
    
    -- CMDB 信息
    user_id VARCHAR(64),
    user_name VARCHAR(128),
    user_email VARCHAR(255),
    team_id VARCHAR(64),
    team_name VARCHAR(128),
    project_id VARCHAR(64),
    project_name VARCHAR(128),
    
    -- 资源请求
    cpu_request VARCHAR(16),
    memory_request VARCHAR(16),
    gpu_count INTEGER DEFAULT 0,
    gpu_product VARCHAR(64),
    rdma_enabled BOOLEAN DEFAULT false,
    
    -- 状态字段
    status VARCHAR(32) NOT NULL DEFAULT 'PENDING',
    k8s_pod_phase VARCHAR(32),
    k8s_pod_reason VARCHAR(128),
    k8s_pod_message TEXT,
    
    -- 时间戳
    requested_at TIMESTAMP,
    approved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    pod_started_at TIMESTAMP,
    first_active_at TIMESTAMP,
    last_active_at TIMESTAMP,
    stopped_at TIMESTAMP,
    released_at TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 部署信息
    image_name VARCHAR(255),
    image_tag VARCHAR(128),
    ssh_node_port INTEGER,
    ssh_host_ip VARCHAR(64),
    workspace_pvc_name VARCHAR(128),
    
    -- 元数据
    business_attributes JSONB DEFAULT '{}',
    metadata_version VARCHAR(32),
    data_source VARCHAR(32) DEFAULT 'INFORMER',
    
    CONSTRAINT chk_pod_resource_type CHECK (pod_resource_type IN ('EXAMPLE_SERVICE', 'ARGO_WORKFLOW', 'RAY_JOB', 'TRAIN_JOB', 'UNKNOWN')),
    CONSTRAINT uniq_pod_resource_status_k8s_pod_uid UNIQUE (k8s_pod_uid)  -- ✅ v4.0: SSOT 修复
);
```

**索引**：
```sql
CREATE INDEX idx_status_user ON pod_resource_status(user_id);
CREATE INDEX idx_status_team ON pod_resource_status(team_id);
CREATE INDEX idx_status_project ON pod_resource_status(project_id);
CREATE INDEX idx_status_type ON pod_resource_status(pod_resource_type);
CREATE INDEX idx_status_k8s_pod_uid ON pod_resource_status(k8s_pod_uid);
CREATE INDEX idx_status_status_created ON pod_resource_status(status, created_at);
```

#### pod_resource_dim_metric（维度表，90天 TTL）🆕

**职责**：GPU 聚合查询专用维度表（只读表）

> **📖 详细表结构**：参见 **[cmdb_tables_v4.1.md - dim_metric 表](../cmdb/cmdb_tables_v4.1.md)** - 完整的 DDL、索引、约束定义

**字段概要**（22 个字段，v4.2.1 更新）：

| 字段分类 | 字段数 | 说明 |
|---------|-------|------|
| 主键和关联 | 2 | resource_id, k8s_pod_uid |
| Pod 基础信息 | 3 | pod_name, pod_namespace, pod_resource_type |
| CMDB 核心维度 | 3 | user_id, team_id, project_id |
| **CMDB 名称字段** | **4** | **user_name, user_email, team_name, project_name** 🆕 v4.2.1 |
| GPU 相关 | 2 | gpu_count, gpu_product |
| 节点维度 | 2 | ssh_host_ip, k8s_node_name |
| 状态字段 | 5 | status, created_at, released_at, pod_started_at, stopped_at |
| 同步元数据 | 1 | synced_at |

**v4.2.1 关键变更**（2026-04-26）：
- ✅ **新增字段**：user_name, user_email, team_name, project_name（聚合查询返回完整维度信息）
- ✅ **字段数量**：18 个 → 22 个（+22% 存储）
- ✅ **修复问题**：聚合查询 SQL 错误（`ERROR: column s.team_name does not exist`）
- ✅ **设计原则**：完整性原则 - 保留聚合查询所需的 ID 和名称字段

**存储对比**（v4.2.1 方案，22 个字段）：
| 表 | 字段数 | 每行大小 | 150万行总大小 | 存储利用率 |
|-----|-------|----------|-------------|-----------|
| status | 40+ | 1255 bytes | 1882 MB | 13% ❌ |
| dim_metric | 22 | ~730 bytes | ~1100 MB | 28% ✅ |

### 11.4 数据同步机制

#### 同步策略

| 参数 | 值 | 理由 |
|------|-----|------|
| 同步方式 | 定时批量 | 平衡一致性与性能 |
| 同步频率 | **15 分钟** | 用户确认 |
| 同步范围 | 增量同步（created_at >= 15分钟前 OR updated_at >= 15分钟前） | 捕获新增和更新记录 |
| 清理策略 | ON CONFLICT (k8s_pod_uid) DO UPDATE | 幂等性保证，以 k8s_pod_uid 为 SSOT 标识 |
| 状态过滤 | IN ('RUNNING', 'STOPPED', 'RELEASED') | 仅同步有效状态（终态和活跃态） |

#### 数据同步流向

```
┌───────────┐
│  K8s API  │
└─────┬─────┘
      │ Watch Pod Events
      ▼
┌───────────┐
│  Informer  │──────────────────────┐
└─────┬─────┘                      │
      │ Write Pod State           │
      ▼                            │
┌─────────────────┐               │
│ pod_resource_status│◄───────┘ (重复数据处理)
│   (30d TTL)     │               │
└─────────┬───────┘               │
          │ Sync (15min, time.Ticker)
           ▼                        │
     ┌─────────────────┐            │
    │DimMetricSyncer  │            │
    │(应用层 3 步转换)  │            │
     └─────────┬───────┘            │
               │ 1. 查询 status 增量 │
               │ 2. Go 代码转换      │
               │ 3. DAO.SyncBatch   │
               │    (分批 100 条)    │
               ▼                    │
            ┌─────────────────┐         │
            │pod_resource_     │         │
            │dim_metric        │         │
            │   (90d TTL)       │         │
            └─────────┬─────────┘         │
                      │                   │
                      ▼                   │
                 ┌─────────────┐              │
                 │ GPU Query    │◄──────────────┘
                 │ (DAO Layer)  │
                 └─────────────┘
```

#### 同步器实现

**代码位置**：`internal/svc/dimmetric_syncer.go`

**设计决策**（Gap Analysis 审查结论）：
- 调度方案：`time.Ticker`（标准库，零依赖）
- 重试方案：自实现指数退避（3 次，避免依赖膨胀）
- 同步架构：应用层 3 步（查询 → 转换 → Upsert），复用 DAO 层
- 状态过滤：只同步有效状态（RUNNING, STOPPED, RELEASED）
- 首次同步：dim_metric 为空时全量同步 15 天内数据
- 分批策略：每批 100 条，多次调用 DAO.SyncBatch

```go
type DimMetricSyncer struct {
    statusDAO    dao.PodResourceStatusDAOInterface
    dimMetricDAO dao.PodResourceDimMetricDAOInterface
    log          logr.Logger
    syncInterval time.Duration // 15 minutes
}

func NewDimMetricSyncer(
    statusDAO dao.PodResourceStatusDAOInterface,
    dimMetricDAO dao.PodResourceDimMetricDAOInterface,
    log logr.Logger,
) *DimMetricSyncer {
    return &DimMetricSyncer{
        statusDAO:    statusDAO,
        dimMetricDAO: dimMetricDAO,
        log:          log,
        syncInterval: 15 * time.Minute,
    }
}

// Start 启动同步器（后台协程，支持 graceful shutdown）
func (s *DimMetricSyncer) Start(ctx context.Context) error {
    s.log.Info("Starting DimMetricSyncer", "syncInterval", s.syncInterval)

    // 首次启动：检测是否需要全量同步
    if s.needFullSync(ctx) {
        s.log.Info("Detected empty dim_metric table, starting full sync (15 days)")
        if err := s.fullSync(ctx); err != nil {
            s.log.Error(err, "Full sync failed, will retry on next cycle")
        }
    }

    // 启动定时同步（time.Ticker，零依赖）
    ticker := time.NewTicker(s.syncInterval)
    go func() {
        for {
            select {
            case <-ticker.C:
                s.syncWithRetry(ctx)
            case <-ctx.Done():
                ticker.Stop()
                s.log.Info("DimMetricSyncer stopped (context cancelled)")
                return
            }
        }
    }()

    s.log.Info("DimMetricSyncer started successfully")
    return nil
}

// SyncOnce 执行一次增量同步（查询 status → 转换 → 分批 Upsert）
func (s *DimMetricSyncer) SyncOnce(ctx context.Context) error {
    // Step 1: 查询增量记录（无上界限制，无状态过滤）
    //   条件: created_at >= NOW()-15min OR updated_at >= NOW()-15min
    statusRecords, err := s.queryChangedRecords(ctx)
    if err != nil {
        return fmt.Errorf("query changed records: %w", err)
    }

    if len(statusRecords) == 0 {
        return nil
    }

    // Step 2: 转换 status → dim_metric（18 字段映射）
    dimMetrics := s.convertToDimMetrics(statusRecords)

    // Step 3: 分批 Upsert（每批 100 条）
    return s.batchUpsert(ctx, dimMetrics)
}

// queryChangedRecords 查询增量记录
func (s *DimMetricSyncer) queryChangedRecords(ctx context.Context) ([]*model.PodResourceStatus, error) {
    since := time.Now().Add(-s.syncInterval)
    filter := &dao.PodFilter{
        UpdatedAfter: &since,  // 新增字段：created_at >= $N OR updated_at >= $N
    }
    return s.statusDAO.List(ctx, filter)
}
```

**集成到 ServiceContext**：
```go
// internal/svc/service_context.go
func (svc *ServiceContext) Start(ctx context.Context) error {
    // ... Informer + Worker 启动 ...

    // 启动 DimMetricSyncer
    syncer := NewDimMetricSyncer(svc.StatusDAO, svc.DimMetricDAO, svc.Logger)
    if err := syncer.Start(ctx); err != nil {
        return fmt.Errorf("start DimMetricSyncer: %w", err)
    }
    svc.DimMetricSyncer = syncer
    return nil
}
```

#### 技术选型说明

**定时调度: 标准库 time.Ticker**

不引入 gocron，使用 Go 标准库 `time.Ticker` 实现 15 分钟定时调度。

**选择理由**：
- 零新增依赖，减少维护成本
- 代码量约 30 行，简洁清晰
- 足够满足固定间隔调度需求
- 符合"标准库优先"的设计原则

**实现示例**：
```go
ticker := time.NewTicker(s.syncInterval)
go func() {
    for {
        select {
        case <-ticker.C:
            s.syncWithRetry(ctx)
        case <-ctx.Done():
            ticker.Stop()
            return
        }
    }
}()
```

**重试机制: 自实现指数退避**

不引入 retry-go，自实现简单重试机制。

**选择理由**：
- 需求简单（3次重试、指数退避）
- 避免依赖膨胀
- 代码量约 20 行，易于维护

**状态过滤: 仅同步有效状态**

增量同步查询包含状态过滤条件：`status IN ('RUNNING', 'STOPPED', 'RELEASED')`

**设计理由**：
- **RUNNING**: 活跃 Pod，需要持续同步
- **STOPPED**: 已停止 Pod，可能再次启动，需要保留
- **RELEASED**: 已释放 Pod，终态，需要归档到 dim_metric
- **排除 PENDING/CREATED**: 中间态，不稳定，等待状态稳定后再同步

**数据完整性保障**：
- 查询条件包含 `created_at OR updated_at`，确保不丢失新创建的 Pod
- 15 分钟查询窗口天然重叠，容忍短暂延迟
- ON CONFLICT DO UPDATE 保证幂等性，重复执行安全

#### 状态过滤策略（v4.2 更新）🆕

**核心原则**：
> **dim_metric 表中 ABORTED 状态的必要条件**：
> - 该 Pod 在 gpu_usage 表中有记录
> - 如果 ABORTED Pod 无 {BUSINESS_SHORT}，则不同步

**设计理由**：
- ✅ **数据完整性**：确保有 {BUSINESS_SHORT}的 ABORTED Pod 不丢失
- ✅ **数据质量**：过滤掉无 {BUSINESS_SHORT}的噪声数据
- ✅ **避免误判**：防止短期 Pod（<15分钟）的数据丢失

**实现方式**：
```sql
-- 前置过滤条件：只同步有 {BUSINESS_SHORT}的 ABORTED 状态
SELECT ... FROM pod_resource_status s
WHERE (
    s.created_at >= NOW() - INTERVAL '15 minutes'
    OR s.updated_at >= NOW() - INTERVAL '15 minutes'
)
AND (
    s.status IN ('RUNNING', 'STOPPED', 'RELEASED')
    OR (
        s.status = 'ABORTED' 
        AND EXISTS (
            SELECT 1 FROM pod_resource_gpu_usage u 
            WHERE u.resource_id = s.resource_id
        )
    )
)
```

**关键场景**：

| 场景 | Pod 状态转换 | 是否同步 | 理由 |
|------|------------|---------|------|
| 场景 1 | PENDING → CREATED → RUNNING → RELEASED | ✅ 同步（RUNNING） | 正常生命周期 |
| 场景 2 | PENDING → CREATED → RUNNING → ABORTED | ✅ 同步（ABORTED） | **有 {BUSINESS_SHORT}** |
| 场景 3 | PENDING → CREATED → ABORTED | ❌ 不同步 | 无 {BUSINESS_SHORT} |
| 场景 4 | PENDING → CREATED → RUNNING（<15min）→ ABORTED | ✅ 同步（ABORTED） | **有 {BUSINESS_SHORT}** |

**数据完整性保证**：
- ✅ **场景 2**：ABORTED 前已进入 RUNNING → 已同步 → 状态更新为 ABORTED
- ✅ **场景 4**：短期 Pod（<15分钟）→ 同步器执行时已是 ABORTED → 条件性同步
- ✅ **场景 3**：从未进入 RUNNING → 无 {BUSINESS_SHORT} → 不同步（符合预期）

---

### 11.5 TTL 策略设计

#### TTL 对比（v4.0 优化策略）

| 表名 | 原 TTL | **新 TTL** | 清理频率 | 理由 |
|------|-------|----------|----------|----------|
| **pod_resource_status** | 无 | **30 天** | 每天凌晨3点 | 状态表，中期保留，与history表对齐 ✅ |
| **pod_resource_history** | 60天 | **30 天** | 每天凌晨2点 | 审计表，与status表对齐，节省存储 ✅ |
| **pod_resource_dim_metric** | - | **90 天** | 每天凌晨4点 | 维度表，长期保留，支持历史查询（覆盖99.99% GPU用量）|
| **pod_resource_gpu_usage** | 不清理 | **90 天** | 每天凌晨5点 | 事实表，长期保留，与dim_metric表对齐 ✅ |

**⚠️ 关键设计变更（2026-04-07）**：
- gpu_usage 表的外键从 `status.resource_id` 迁移到 `dim_metric.resource_id`
- 理由：对齐 TTL 策略（都是 90 天），避免 status 清理时级联删除 gpu_usage
- 详见 STORY-15-19: {BUSINESS_SHORT}外键迁移

#### TTL 对比（v4.0 优化策略）

| 表名 | 原 TTL | **新 TTL** | 清理频率 | 理由 |
|------|-------|----------|----------|------|
| **pod_resource_status** | 无 | **30 天** | 每天凌晨3点 | 状态表，中期保留，与history表对齐 ✅ |
| **pod_resource_history** | 60天 | **30 天** | 每天凌晨2点 | 审计表，与status表对齐，节省存储 ✅ |
| **pod_resource_dim_metric** | - | **90 天** | 每天凌晨4点 | 维度表，长期保留，支持历史查询（覆盖99.99% GPU用量）|
| **pod_resource_gpu_usage** | 不清理 | **90 天** | 每天凌晨5点 | 事实表，长期保留，与dim_metric表对齐 ✅ |

#### 清理条件（v4.1 优化版：STORY-15-19 后）

**status 表（30天 TTL）**：
```sql
-- 简化清理逻辑（不再需要保护 gpu_usage）
DELETE FROM pod_resource_status
WHERE created_at < NOW() - INTERVAL '30 days'
  AND status = 'RELEASED';
  -- ✅ FK 已迁移到 dim_metric（STORY-15-19），无需保护 gpu_usage
```

**dim_metric 表（90天 TTL）**：
```sql
-- 清理 90 天前的 dim_metric 记录
-- ⚠️ 会 CASCADE 删除关联的 gpu_usage 记录
DELETE FROM pod_resource_dim_metric
WHERE created_at < NOW() - INTERVAL '90 days';
  -- ✅ gpu_usage FK 指向 dim_metric（90天 TTL 对齐）
```

**gpu_usage 表（90天 TTL）**：
```sql
-- 不需要单独清理（通过 dim_metric CASCADE 删除）
-- ✅ gpu_usage FK → dim_metric (ON DELETE CASCADE)
```

### 11.6 查询路由策略（v4.2 优化）🆕

#### 核心原则（v4.2 更新）

**统一使用 `dim_metric` 表**：
- ✅ 所有 {BUSINESS_SHORT}查询统一使用 `dim_metric` 表（0-90天）
- ✅ 不再区分时间范围（0-30天 vs 31-90天）
- ✅ 查询逻辑简化：单一路径，易于维护

**设计变更理由**：
- ✅ **查询逻辑简化**：从时间范围路由改为单一路由，降低复杂度
- ✅ **数据质量提升**：dim_metric 表经过 15 分钟同步和数据过滤，数据更干净
- ✅ **性能优化**：窄表查询（18字段 vs 40+字段），预期性能提升 >50%
- ⚠️ **15分钟延迟**：对 {PROJECT_NAME} SLA 可接受（历史数据查询为主）

#### dim_metric 表结构（v4.2.1 更新）🆕

**⚠️ 重要设计变更**（2026-04-26）：

为支持聚合查询返回完整的维度信息（ID + 名称），v4.2.1 在 `dim_metric` 表中添加了名称字段。

> **详细表结构**：参见 [cmdb_tables_v4.2.md - dim_metric 表](../cmdb/cmdb_tables_v4.2.md)

**v4.2.1 变更概要**：

| 维度 | v4.1（18 字段） | **v4.2.1（22 字段）** | 变更 |
|------|----------------|---------------------|------|
| **CMDB 字段** | 只有 ID（user_id, team_id, project_id） | **ID + 名称**（user_name, team_name, project_name, user_email） | +4 字段 |
| **字段总数** | 18 个字段 | **22 个字段** | +4 字段 |
| **存储成本** | ~900 MB | ~1100 MB（+22%） | 可接受 |
| **查询性能** | 高（窄表） | **高**（仍然是窄表，22 字段 vs 40+ 字段） | 保持 |
| **聚合查询** | ❌ 需要 LEFT JOIN status 表 | ✅ 单表查询（包含名称字段） | **简化** |

**更新原因**：
- ❌ **v4.2 设计缺陷**：代码尝试查询 `s.team_name`, `s.project_name`，但表中没有这些字段
- ❌ **结果**：所有聚合查询返回 500 错误（STORY-15-15 测试发现）
- ✅ **v4.2.1 修复**：添加名称字段，支持完整的聚合查询（ID + 名称）

**与 v4.1 的对比**：

| 维度 | v4.1（按时间范围） | **v4.2（统一 dim_metric）** |
|------|------------------|---------------------------|
| **查询逻辑** | 复杂（时间范围判断） | **简单（单一路径）** |
| **数据源** | 混合（status + dim_metric） | **统一（dim_metric）** |
| **实时性** | 高（0-30天实时） | **中（15分钟延迟）** |
| **数据质量** | 中（status 有噪声） | **高（dim_metric 过滤噪声）** |
| **性能** | 中（部分宽表查询） | **高（窄表查询）** |
| **代码复杂度** | 高（双路径） | **低（单路径）** |

#### GPU 聚合查询（统一使用 dim_metric 表，v4.2.1 更新）🆕

**适用场景**：用户、团队、项目的 {BUSINESS_DESCRIPTION}（0-90天）

**v4.2.1 SQL（包含名称字段）**：

```sql
-- v4.2.1 架构：统一使用 dim_metric 表（包含名称字段）
SELECT
    s.user_id,
    MAX(s.user_name) AS user_name,      -- 🆕 v4.2.1: 用户名称
    MAX(s.user_email) AS user_email,    -- 🆕 v4.2.1: 用户邮箱
    s.team_id,
    MAX(s.team_name) AS team_name,      -- 🆕 v4.2.1: 团队名称
    COUNT(DISTINCT s.resource_id) AS pod_count,
    COALESCE(SUM(u.gpu_hours), 0) AS total_gpu_hours
FROM pod_resource_dim_metric s      -- ✅ 统一使用 dim_metric 表（包含名称字段）
LEFT JOIN pod_resource_gpu_usage u   -- 事实表（90天 {BUSINESS_SHORT}）
  ON s.resource_id = u.resource_id   -- ✅ FK 指向 dim_metric（STORY-15-19）
WHERE s.created_at >= NOW() - INTERVAL '90 days'
  AND s.status IN ('RUNNING', 'STOPPED', 'RELEASED', 'ABORTED')  -- ✅ v4.2: 包含 ABORTED
GROUP BY s.user_id, s.team_id;
```

**v4.2.1 聚合查询（按团队维度）**：

```sql
-- 按团队维度聚合（包含团队名称）
SELECT
    s.team_id,
    MAX(s.team_name) AS team_name,      -- 🆕 v4.2.1: 团队名称
    COUNT(DISTINCT s.resource_id) AS pod_count,
    COALESCE(SUM(u.gpu_hours), 0) AS total_gpu_hours
FROM pod_resource_dim_metric s
LEFT JOIN pod_resource_gpu_usage u
  ON s.resource_id = u.resource_id
  AND u.usage_start_at >= NOW() - INTERVAL '90 days'
  AND u.usage_start_at < NOW()
WHERE s.created_at >= NOW() - INTERVAL '90 days'
  AND s.status IN ('RUNNING', 'STOPPED', 'RELEASED', 'ABORTED')
GROUP BY s.team_id;
```

**v4.2.1 聚合查询（按项目维度）**：

```sql
-- 按项目维度聚合（包含项目名称）
SELECT
    s.project_id,
    MAX(s.project_name) AS project_name,  -- 🆕 v4.2.1: 项目名称
    COUNT(DISTINCT s.resource_id) AS pod_count,
    COALESCE(SUM(u.gpu_hours), 0) AS total_gpu_hours
FROM pod_resource_dim_metric s
LEFT JOIN pod_resource_gpu_usage u
  ON s.resource_id = u.resource_id
  AND u.usage_start_at >= NOW() - INTERVAL '90 days'
  AND u.usage_start_at < NOW()
WHERE s.created_at >= NOW() - INTERVAL '90 days'
  AND s.status IN ('RUNNING 'STOPPED', 'RELEASED', 'ABORTED')
GROUP BY s.project_id;
```

**优点**：
- ✅ 减少 45% 数据扫描量（22字段 vs 40+字段）
- ✅ 覆盖 90 天历史数据
- ✅ 避免查询已被删除的 `status` 记录
- ✅ **查询逻辑简化**：单一路径，无需时间范围判断
- ✅ **聚合查询完整**：包含 ID + 名称，无需 LEFT JOIN status 表（🆕 v4.2.1 修复）
- ✅ **数据质量提升**：dim_metric 表经过过滤（15分钟同步 + 状态过滤）

**⚠️ 注意事项**：
- ⚠️ **15分钟延迟**：新创建的 Pod 可能需要等待 15 分钟后才能查询到
- ⚠️ **ABORTED 状态**：只有有 {BUSINESS_SHORT}的 ABORTED Pod 才会被同步（详见 11.4.1 节）

#### Pod 详情查询（统一使用 dim_metric 表）

**适用场景**：查询单个 Pod 的详细信息

```sql
-- v4.2 架构：统一使用 dim_metric 表
SELECT
    d.resource_id,
    d.pod_name,
    d.status,
    d.user_id,
    d.team_id,
    d.gpu_count,
    d.gpu_product,
    d.k8s_node_name,
    d.created_at,
    d.released_at
FROM pod_resource_dim_metric d
WHERE d.resource_id = ?
  AND d.created_at >= NOW() - INTERVAL '90 days';
```

**优点**：
- ✅ 统一查询逻辑（无需时间范围判断）
- ✅ 窄表查询（18字段 vs 40+字段）
- ✅ 覆盖 90 天历史数据

**⚠️ 注意事项**：
- ⚠️ 如果需要实时查询（0-15分钟），建议等待 15 分钟同步周期完成
- ⚠️ 如果需要查询 >90天的数据，需要单独查询 status 表（如果仍存在）
    status,
    user_id,
    team_id,
    gpu_count,
    'status' AS source_table
FROM pod_resource_status
WHERE resource_id = ?
  AND created_at >= NOW() - INTERVAL '30 days'

UNION ALL

SELECT
    resource_id,
    pod_name,
    status,
    user_id,
    team_id,
    gpu_count,
    'dim_metric' AS source_table
FROM pod_resource_dim_metric
WHERE resource_id = ?
  AND created_at < NOW() - INTERVAL '30 days';
```

#### 查询路由决策树（v4.2 简化版）

```
查询需求
  ↓
  ├─ GPU 聚合查询（用户/团队/项目）
  │   ↓
  │   └─ 使用 dim_metric 表（0-90天）✅ 统一查询源
  │       └─ LEFT JOIN gpu_usage 表
  │
  ├─ Pod 详情查询
  │   ↓
  │   ├─ 数据时间范围？
  │   │   ├─ 0-30天 → 使用 status 表（实时 SSOT）
  │   │   └─ 31-90天 → 使用 dim_metric 表 + LEFT JOIN status
  │   │
  │   └─ 需要完整信息？
  │       ├─ 是 → UNION ALL 合并两个表
  │       └─ 否 → 按时间范围选择
  │
  └─ 实时状态查询（Pod 当前状态）
      ↓
      └─ 使用 status 表（Informer 实时写入）
```

### 11.7 查询模式（兼容 v4.0 设计）

#### GPU 聚合查询（使用 dim_metric 表）

```sql
-- v4.0 架构：{BUSINESS_SHORT}聚合查询（使用 dim_metric 表）
SELECT 
    s.user_id,
    s.team_id,
    COUNT(DISTINCT s.resource_id) AS pod_count,
    COALESCE(SUM(u.gpu_hours), 0) AS total_gpu_hours
FROM pod_resource_dim_metric s      -- 维度表（90天 CMDB 数据）
LEFT JOIN pod_resource_gpu_usage u   -- 事实表（无限期 {BUSINESS_SHORT}）
  ON s.resource_id = u.resource_id
WHERE s.created_at >= NOW() - INTERVAL '90 days'
  AND s.status IN ('RUNNING', 'STOPPED', 'RELEASED')
GROUP BY s.user_id, s.team_id;
```

#### Pod 详情查询（JOIN status 表）

```sql
-- 需要完整信息时，JOIN status 表
SELECT 
    c.resource_id,
    c.pod_name,
    c.gpu_count,
    c.status,
    -- 扩展信息（按需获取）
    e.user_name,
    e.team_name,
    e.image_name,
    e.ssh_node_port
FROM pod_resource_dim_metric c
LEFT JOIN pod_resource_status e ON c.resource_id = e.resource_id
WHERE c.resource_id = ?;
```

### 11.9 数据校准方案（v4.1 完善版）🆕

#### 问题背景

**根本原因**：
- Informer 的 2 个 Worker 并发处理同一个 Pod 的事件
- 缺少 `k8s_pod_uid UNIQUE` 约束，数据库层面无法防止重复插入
- **并发写入导致 `updated_at` 时间戳完全相同（0.000000 秒差异）**

**数据现状**（生产环境 2026-04-07）：
- 总记录数：1,270,962
- 唯一 Pod 数：957,384
- 重复记录数：313,578（**24.67%**）
- 被 gpu_usage 引用：311,476（**50.53%**）

#### 核心设计原则

**1. 终态状态机优先级（解决并发写入问题）**

基于 `internal/pkg/calculator/state_machine.go` 的状态转换规则：

| 状态优先级 | 状态 | 说明 | 终态 | 优先级原因 |
|-----------|------|------|------|-----------|
| **1** | **RELEASED** | Pod 正常释放，走完生命周期 | ✅ | 最"正常"的终态 |
| **2** | **ABORTED** | Pod 异常终止 | ✅ | 异常终态，但仍是终态 |
| 3 | STOPPED | Pod 停止（可能再次启动） | ❌ | 中间态 |
| 4 | RUNNING | Pod 正在运行（活跃状态） | ❌ | 中间态 |
| 5 | CREATED | Pod 已创建 | ❌ | 中间态 |
| 6 | PENDING | Pod 等待调度 | ❌ | 中间态 |

**设计意图**：
- ✅ 优先保留**终态**（RELEASED > ABORTED）
- ✅ 如果都是终态，优先保留 RELEASED（更"正常"的终态）
- ✅ **解决并发写入问题**：当 `updated_at` 相同时，按**状态优先级**选择（保证可解释性）
- ✅ 如果状态和时间都相同，按 **resource_id DESC** 选择（保证排序稳定性）

**2. 多级排序规则（关键创新）**

```sql
ORDER BY 
    updated_at DESC,           -- 优先级1：最后更新的
    CASE status                -- 优先级2：状态优先级（终态优先，解决并发写入问题）
        WHEN 'RELEASED' THEN 1
        WHEN 'ABORTED' THEN 2
        WHEN 'STOPPED' THEN 3
        WHEN 'RUNNING' THEN 4
        WHEN 'CREATED' THEN 5
        WHEN 'PENDING' THEN 6
        ELSE 99
    END ASC,
    resource_id DESC           -- 优先级3：保证排序稳定性
```

**为什么这样设计？**

1. **`updated_at DESC`**：
   - 保留最后更新的记录（通常是终态）
   - 适用于大部分正常情况（状态转换有序）

2. **状态优先级（关键创新）**：
   - **解决并发写入问题**：当两个 Worker 同时写入，`updated_at` 相同时
   - 终态（RELEASED/ABORTED）优先于中间态（RUNNING/STOPPED）
   - RELEASED 优先于 ABORTED（更"正常"的终态）
   - 保证排序结果**可解释**（不是随机的）

3. **`resource_id DESC`**：
   - 保证排序结果**稳定**（即使 `updated_at` 和 `status` 都相同）
   - UUID 的字典序作为最终决胜条件

**3. {BUSINESS_SHORT}数据保护（不丢失数据）**

**关键原则**：
- ✅ **不丢失 {BUSINESS_SHORT}数据**
- ✅ **重新分配 `usage_cycle`**（按 `usage_start_at` 时序）
- ✅ **更新 `resource_id` 外键**（关联到归一后的 status 记录）

#### 完整实施方案（Phase 0-4）

**执行时间估算**：75-140 分钟（约 1.25-2.33 小时）
**执行窗口**：建议在凌晨 2:00 - 6:00（低峰期）

**Phase 0: 数据备份（5-10 分钟）** 🟢
**Phase 1: Dry-Run 评估（5-10 分钟）** 🟢
**Phase 2: 更新 gpu_usage 外键（30-60 分钟）** 🔴
**Phase 3: 删除冗余 status 记录（20-40 分钟）** 🟡
**Phase 4: 添加 UNIQUE 约束（5 分钟）** 🟢

#### AC 验证准则（5 个）

**AC-1: 数据完整性**（{BUSINESS_SHORT}不丢失）
**AC-2: 唯一性约束**（无重复记录）
**AC-3: 状态分布合理**（终态优先）
**AC-4: {BUSINESS_SHORT}外键一致性**（无 orphan 记录）
**AC-5: usage_cycle 连续性**（时序正确）

#### 相关文档

- **[STORY-15-18: 数据校准完整实施方案](../scrum/story/story-15-18-data-reconciliation-complete-solution.md)**
- **[Research: SSOT 问题分析](../research/deep_dive_resource_id_and_storage_20260402.md)**
- **状态机代码**: `internal/pkg/calculator/state_machine.go`

### 11.10 预期效果

| 指标 | 当前 | 优化后 | 改善 |
|------|------|--------|------|
| status 表大小 | 2063 MB | ~400 MB | **-80%** |
| dim_metric 表大小 | 0 | ~300 MB | 新增 |
| GPU 查询扫描 | 1255 bytes/行 | 400 bytes/行 | **-68%** |
| 总存储（稳定后） | ~3500 MB | ~1100 MB | **-69%** |
| 重复记录率 | 42.27% | 0% | **-100%** |

---

### 11.11 TTL 清理实现方案（v4.1 完整版）🆕

#### 设计目标

实现应用层自动 TTL 清理功能，**不依赖运维手动执行**，确保数据表大小稳定在合理范围。

**核心原则**：
- ✅ **自动化**：服务自动执行清理，无需运维干预
- ✅ **安全可靠**：分批删除，保护活跃数据，记录清理日志
- ✅ **可配置**：支持开关控制、时区配置、cron 表达式调整
- ✅ **可观测**：日志记录、Prometheus 监控（延后实施）、清理统计

#### 技术选型

##### 方案对比

| 方案 | 优点 | 缺点 | 选择 |
|------|------|------|------|
| **robfig/cron** | 功能完整、社区成熟、支持秒级 | 依赖外部库 | ✅ **推荐** |
| **time.Ticker** | 标准库、无依赖 | 不支持复杂 cron 表达式 | ❌ |
| **外挂 Cron Job** | 解耦、重启不影响 | 部署复杂、需要运维配置 | ❌ 违背自动化原则 |

**✅ 最终选择**: `github.com/robfig/cron/v3`

**理由**：
1. 支持标准 cron 表达式（如 `0 3 * * *` 表示每天凌晨 3 点）
2. 支持时区配置（Asia/Shanghai UTC+8）
3. 社区成熟稳定（10k+ stars，广泛使用）
4. 易于集成到 go-zero ServiceContext

#### 调度器架构

##### 模块位置

```
internal/pkg/scheduler/
├── scheduler.go          # 调度器核心逻辑
├── tasks.go              # 清理任务实现
├── scheduler_test.go     # 单元测试
└── README.md             # 模块说明
```

##### 核心接口设计

**Scheduler 结构体**：
```go
// internal/pkg/scheduler/scheduler.go

package scheduler

import (
    "github.com/robfig/cron/v3"
    "github.com/zeromicro/go-zero/core/logx"
)

type Scheduler struct {
    cron           *cron.Cron
    config         *config.CronConf
    cleanupService *CleanupService
    logger         logx.Logger
}

// NewScheduler 创建调度器实例
func NewScheduler(conf *config.CronConf, cleanupSvc *CleanupService) *Scheduler {
    location, _ := time.LoadLocation(conf.Timezone)
    c := cron.New(cron.WithLocation(location))

    return &Scheduler{
        cron:           c,
        config:         conf,
        cleanupService: cleanupSvc,
        logger:         logx.WithContext(context.Background()),
    }
}

// Start 启动调度器
func (s *Scheduler) Start() error {
    if !s.config.Enabled {
        s.logger.Info("Scheduler is disabled")
        return nil
    }

    // 添加清理任务
    if _, err := s.cron.AddFunc(s.config.CleanupHistory, s.cleanupService.CleanupHistory); err != nil {
        return fmt.Errorf("failed to add cleanup history job: %w", err)
    }

    if _, err := s.cron.AddFunc(s.config.CleanupStatus, s.cleanupService.CleanupStatus); err != nil {
        return fmt.Errorf("failed to add cleanup status job: %w", err)
    }

    if _, err := s.cron.AddFunc(s.config.CleanupDimMetric, s.cleanupService.CleanupDimMetric); err != nil {
        return fmt.Errorf("failed to add cleanup dim_metric job: %w", err)
    }

    s.cron.Start()
    s.logger.Info("Scheduler started successfully")

    return nil
}

// Stop 停止调度器
func (s *Scheduler) Stop() {
    s.logger.Info("Stopping scheduler...")
    ctx := s.cron.Stop()
    <-ctx.Done()
    s.logger.Info("Scheduler stopped")
}
```

**CleanupService 结构体**（简化版）：
```go
// internal/pkg/scheduler/tasks.go

type CleanupService struct {
    dbEngine *sql.DB
    logger   logx.Logger
}

// CleanupHistory 清理 history 表（30 天 TTL）
func (s *CleanupService) CleanupHistory() {
    s.logger.Info("Starting cleanup history task")

    ctx, cancel := context.WithTimeout(context.Background(), 30*time.Minute)
    defer cancel()

    batchSize := 1000
    totalDeleted := 0

    for {
        result, err := s.dbEngine.ExecContext(ctx, `
            DELETE FROM pod_resource_history
            WHERE created_at < NOW() - INTERVAL '30 days'
            LIMIT $1
        `, batchSize)

        if err != nil {
            s.logger.Error("Failed to cleanup history", "error", err)
            return
        }

        rowsAffected, _ := result.RowsAffected()
        totalDeleted += int(rowsAffected)

        if rowsAffected < int64(batchSize) {
            break
        }

        time.Sleep(1 * time.Second)
    }

    s.logger.Info("Cleanup history task completed", "totalDeleted", totalDeleted)
}

// CleanupStatus 清理 status 表（30 天 TTL）
func (s *CleanupService) CleanupStatus() {
    s.logger.Info("Starting cleanup status task")

    ctx, cancel := context.WithTimeout(context.Background(), 30*time.Minute)
    defer cancel()

    batchSize := 1000
    totalDeleted := 0

    for {
        // 删除条件：created_at < 30天前 AND status = 'RELEASED'
        // ✅ v4.1 优化：无需保护 gpu_usage（FK 已迁移到 dim_metric）
        result, err := s.dbEngine.ExecContext(ctx, `
            DELETE FROM pod_resource_status
            WHERE created_at < NOW() - INTERVAL '30 days'
              AND status = 'RELEASED'
            LIMIT $1
        `, batchSize)

        if err != nil {
            s.logger.Error("Failed to cleanup status", "error", err)
            return
        }

        rowsAffected, _ := result.RowsAffected()
        totalDeleted += int(rowsAffected)

        if rowsAffected < int64(batchSize) {
            break
        }

        time.Sleep(1 * time.Second)
    }

    s.logger.Info("Cleanup status task completed", "totalDeleted", totalDeleted)
}

// CleanupDimMetric 清理 dim_metric 表（90 天 TTL）
// ⚠️ 会 CASCADE 删除关联的 gpu_usage 记录
func (s *CleanupService) CleanupDimMetric() {
    s.logger.Info("Starting cleanup dim_metric task")

    ctx, cancel := context.WithTimeout(context.Background(), 30*time.Minute)
    defer cancel()

    batchSize := 1000
    totalDeleted := 0

    for {
        result, err := s.dbEngine.ExecContext(ctx, `
            DELETE FROM pod_resource_dim_metric
            WHERE created_at < NOW() - INTERVAL '90 days'
            LIMIT $1
        `, batchSize)

        if err != nil {
            s.logger.Error("Failed to cleanup dim_metric", "error", err)
            return
        }

        rowsAffected, _ := result.RowsAffected()
        totalDeleted += int(rowsAffected)

        if rowsAffected < int64(batchSize) {
            break
        }

        time.Sleep(1 * time.Second)
    }

    s.logger.Info("Cleanup dim_metric task completed", "totalDeleted", totalDeleted)
}
```

#### 配置管理

##### Config 结构扩展

```go
// internal/config/config.go

type Config struct {
    // ... 其他配置

    CronConf CronConf
}

type CronConf struct {
    Enabled           bool   `json:",default=true"`
    Timezone          string `json:",default=Asia/Shanghai"`
    CleanupHistory    string `json:",default=0 2 * * *"`    // 每天 2 点
    CleanupStatus     string `json:",default=0 3 * * *"`    // 每天 3 点
    CleanupDimMetric  string `json:",default=0 4 * * *"`    // 每天 4 点
}
```

##### 配置文件示例

```yaml
# etc/{PROJECT_NAME}-api.yaml

CronConf:
  Enabled: true
  Timezone: 'Asia/Shanghai'
  CleanupHistory: '0 2 * * *'
  CleanupStatus: '0 3 * * *'
  CleanupDimMetric: '0 4 * * *'
```

#### ServiceContext 集成

```go
// internal/svc/service_context.go

type ServiceContext struct {
    // ... 其他字段
    Scheduler *scheduler.Scheduler
}

func NewServiceContext(c config.Config) *ServiceContext {
    // ... 其他初始化

    cleanupSvc := scheduler.NewCleanupService(svc.DBEngine())
    svc.Scheduler = scheduler.NewScheduler(&c.CronConf, cleanupSvc)

    return svc
}

func (s *ServiceContext) Start() error {
    // ... 其他启动逻辑

    if err := s.Scheduler.Start(); err != nil {
        return fmt.Errorf("failed to start scheduler: %w", err)
    }

    return nil
}

func (s *ServiceContext) Close() error {
    s.Scheduler.Stop()
    return nil
}
```

#### 错误处理和日志

##### 错误处理策略

1. **任务级别隔离**：每个清理任务独立运行，一个失败不影响其他任务
2. **超时保护**：每个任务设置 30 分钟超时，避免长时间占用数据库
3. **分批删除**：每次删除 1000 条，避免大事务阻塞
4. **短暂休眠**：批次间休眠 1 秒，避免持续占用数据库连接

##### 日志记录规范

```go
// 任务开始
s.logger.Info("Starting cleanup history task")

// 批次删除
s.logger.Info("Cleanup history batch",
    "deleted", rowsAffected,
    "totalDeleted", totalDeleted,
)

// 任务完成
s.logger.Info("Cleanup history task completed",
    "totalDeleted", totalDeleted,
)

// 任务失败
s.logger.Error("Failed to cleanup history",
    "error", err,
    "totalDeletedBeforeError", totalDeleted,
)
```

#### 监控和告警（🟡 延后实施）

##### Prometheus 监控指标（延后）

```go
// internal/pkg/scheduler/metrics.go（延后实施）

var (
    cleanupTasksTotal = promauto.NewCounterVec(prometheus.CounterOpts{
        Name: "{PROJECT_NAME}_cleanup_tasks_total",
        Help: "Total number of cleanup tasks executed",
    }, []string{"table", "status"})

    cleanupRowsDeleted = promauto.NewCounterVec(prometheus.CounterOpts{
        Name: "{PROJECT_NAME}_cleanup_rows_deleted_total",
        Help: "Total number of rows deleted by cleanup tasks",
    }, []string{"table"})

    cleanupTaskDuration = promauto.NewHistogramVec(prometheus.HistogramOpts{
        Name:    "{PROJECT_NAME}_cleanup_task_duration_seconds",
        Help:    "Duration of cleanup tasks in seconds",
        Buckets: prometheus.DefBuckets,
    }, []string{"table"})
)
```

#### 测试策略

##### 单元测试

**测试覆盖率目标**: ≥80%

**核心测试用例**：
```go
func TestScheduler_Start(t *testing.T)
func TestScheduler_Stop(t *testing.T)
func TestCleanupService_CleanupHistory(t *testing.T)
func TestCleanupService_CleanupStatus(t *testing.T)
func TestCleanupService_CleanupDimMetric(t *testing.T)
```

##### SIT 集成测试

**测试文件**: `tests/sit/test_ttl_cleanup.py`

**核心测试用例**：
```python
def test_cleanup_history_30_days()
def test_cleanup_status_only_released()
def test_cleanup_dim_metric_cascade_gpu_usage()
def test_cleanup_respects_data_retention()
```

##### 手动验证

1. **配置验证**：确认 `CronConf.Enabled=true`
2. **启动服务**：`make run`
3. **查看日志**：`docker logs {PROJECT_NAME}-api | grep "Cleanup history"`
4. **数据库验证**：
   ```sql
   -- 查询清理前记录数
   SELECT COUNT(*) FROM pod_resource_history
   WHERE created_at < NOW() - INTERVAL '30 days';

   -- 等待调度器执行

   -- 查询清理后记录数（应该为 0）
   SELECT COUNT(*) FROM pod_resource_history
   WHERE created_at < NOW() - INTERVAL '30 days';
   ```

#### 预期效果

| 指标 | 清理前 | 清理后（稳定） | 改善 |
|------|--------|---------------|------|
| **status 表大小** | 2063 MB | ~400 MB | **-80%** |
| **history 表大小** | 1200 MB | ~200 MB | **-83%** |
| **dim_metric 表大小** | 0 | ~300 MB | 新增 |
| **gpu_usage 表大小** | 无限增长 | ~800 MB | **稳定** |
| **总存储（稳定后）** | ~3500 MB | ~1700 MB | **-51%** |
| **清理自动化** | 手动运维 | 自动清理 | **100%** |

**关键收益**：
1. ✅ **自动化**：无需运维手动执行 SQL
2. ✅ **稳定存储**：数据表大小稳定在 ~1.7 GB
3. ✅ **节省成本**：年存储成本从无限增长 → 稳定在 ~1.7 GB
4. ✅ **可观测**：日志记录（Prometheus 监控延后）

#### 实施优先级

**优先级**: 🔴 **P0（最高优先级）**

**理由**：
1. **防止数据库无限增长**：TTL 清理是数据管理的基础功能
2. **依赖其他 Story**：STORY-15-19（FK 迁移）已完成，可以立即实施
3. **降低存储成本**：立即节省 ~51% 存储空间
4. **无其他依赖**：可以独立实施，不阻塞其他 Story

**⚠️ 监控延后**: Prometheus 监控指标延后实施（降低优先级），优先实现核心清理逻辑。

#### 相关文档

- **Story 文档**: `docs/scrum/story/story-15-22-ttl-cleanup-implementation.md`
- **实施计划**: `test_reports/ttl_cleanup_implementation_plan.md`
- **配置示例**: `etc/{PROJECT_NAME}-api.yaml`

---

## 📚️ 附录

### 相关文档

- **Research: SSOT 问题分析**: `docs/research/deep_dive_resource_id_and_storage_20260402.md`
- **Research: TTL 策略调研**: `docs/research/ttl_data_consistency_research_20260402.md`

### 术语表

| 术语 | 全称 | 说明 |
|------|------|------|
| **SSOT** | Single Source of Truth | 唯一真实来源 |
| **TTL** | Time To Live | 数据生存时间 |
| **DDL** | Data Definition Language | 数据定义语言 |
| **UNIQUE 约束** | - | 保证字段值唯一性的数据库约束 |
| **ON CONFLICT DO UPDATE** | - | PostgreSQL 幂等性语法（冲突时更新） |

---

**版本**: v4.2
**创建日期**: 2026-02-03
**最后更新**: 2026-04-11

---

## 🆕 DDL 更新日志（2026-04-07）

### 更新1: gpu_usage表添加UNIQUE约束 ✅

**问题**: DDL文件缺少 `pod_resource_gpu_usage` 表的UNIQUE约束定义

**影响**:
- 数据库结构与DDL文档不一致
- 新环境部署时缺少UNIQUE约束
- 可能导致重复的 `(resource_id, usage_cycle)` 组合

**解决方案**:

1. **更新DDL文件** (`db/ddl/002_pod_resource_tables.sql`):
   ```sql
   -- 添加UNIQUE约束（确保同一个Pod的usage_cycle不重复）
   CREATE UNIQUE INDEX IF NOT EXISTS uniq_pod_resource_gpu_usage_resource_id_cycle
       ON pod_resource_gpu_usage(resource_id, usage_cycle);
   ```

2. **执行DDL补丁** (`db/ddl/006_fix_gpu_usage_unique_constraint.sql`):
   - ✅ 生产环境已执行（2026-04-07 YOLO MODE）
   - ✅ UNIQUE约束已创建并验证

**验证结果**:
```sql
SELECT indexname FROM pg_indexes
WHERE tablename = 'pod_resource_gpu_usage'
  AND indexname = 'uniq_pod_resource_gpu_usage_resource_id_cycle';

-- 结果: uniq_pod_resource_gpu_usage_resource_id_cycle ✅
```

**相关文档**:
- DDL补丁: `db/ddl/006_fix_gpu_usage_unique_constraint.sql`
- Story文档: `docs/scrum/story/story-15-18-data-reconciliation-complete-solution.md`
- DevOps验证: `test_reports/devops_story_15_18_verification.md`

---

### 后续优化计划

#### 索引优化提案（待Architect审批）

**问题**: `idx_pod_resource_gpu_usage_resource_id` 索引可能冗余（34 MB）

**分析**:
- UNIQUE索引 `(resource_id, usage_cycle)` 可以覆盖 `resource_id` 单列查询
- PostgreSQL复合索引的前导列优化

**预期效果**:
- 释放空间：34 MB
- 写入性能：+2~5%

**风险**: 🟡 中等（需要充分验证）

**提案文件**: `db/ddl/archive/007_optimize_gpu_usage_indexes_proposal.sql`

**状态**: PENDING ARCHITECT REVIEW

---
**作者**: Development Team + Architect + Architect + Architect + Architect + Architect
**状态**: 正式发布
