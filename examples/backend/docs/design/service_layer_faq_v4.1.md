# Example Service 服务层 FAQ v4.1

**文档版本**: v4.1
**创建日期**: 2026-02-02
**最后更新**: 2026-04-25
**作者**: Development Team + Architect + Scrum Master
**状态**: 正式发布
**替代版本**: v4.0 (已归档至 `archive/service_layer_faq_v4.0_20260407.md`)

---

## 📋 版本历史

| 版本 | 日期 | 变更说明 | 作者 |
|------|------|---------|------|
| v1.0 | 2026-02-02 | 初始版本 | Development Team |
| v2.0 | 2026-02-03 | 更新 FAQ-2：活跃 Pod GPU 实时计算 | QA + Development Team |
| v3.0 | 2026-02-04 | 更新 FAQ-8：历史记录存储优化 | Development Team |
| v3.1 | 2026-02-06 | 新增 FAQ-9：{BUSINESS_SHORT}负数问题 | Development Team |
| v3.2 | 2026-02-09 | 新增 FAQ-10/11/12/13：Annotation 前缀统一 + 资源字段说明 | Development Team |
| v3.3 | 2026-03-13 | 新增 FAQ-14：服务启动前 Pod 无法统计 {BUSINESS_SHORT} | Development Team |
| v4.0 | 2026-04-02 | 新增 FAQ-15/16/17/18：数据层架构优化（dim_metric 表 + SSOT 修复 + TTL 策略） | Development Team |
| **v4.1** | **2026-04-07** | **新增 FAQ-19/20/21/22/23/24/25：SSOT 职责分离架构 + 查询路由策略 + 外键迁移** | **Architect + Scrum Master** |
| **v4.1.1** | **2026-04-25** | **新增 FAQ-26/27：表选择优化原则 + LEFT JOIN NULL 语义（基于STORY-15-15生产数据验证）** | **Architect + Developer** |

**v4.0 主要变更**：
- ✅ 新增 FAQ-15：为什么需要新增 `pod_resource_dim_metric` 表？
- ✅ 新增 FAQ-16：`pod_resource_dim_metric` 表如何同步数据？
- ✅ 新增 FAQ-17：`k8s_pod_uid` 是什么？为什么需要 UNIQUE 约束？
- ✅ 新增 FAQ-18：status 表和 dim_metric 表的 TTL 为什么不同？

**v4.1 主要变更**：
- ✅ 新增 FAQ-19：为什么有两个 SSOT 表（status + dim_metric）？
- ✅ 新增 FAQ-20：15分钟同步延迟是否影响业务？
- ✅ 新增 FAQ-21：如何选择查询 status 还是 dim_metric？
- ✅ 新增 FAQ-22：TTL 清理后如何查询历史数据？
- ✅ 新增 FAQ-23：gpu_usage 外键为什么要迁移到 dim_metric？
- ✅ 新增 FAQ-24：dim_metric 表与 status 表的数据关系如何保持？
- ✅ 新增 FAQ-25：如何验证 SSOT 数据一致性？

**v4.1.1 主要变更**：
- ✅ 新增 FAQ-26：聚合查询为什么使用 dim_metric 作为主表？
- ✅ 新增 FAQ-27：LEFT JOIN 场景下如何正确处理 NULL 值？

**v3.3 继承内容**：
- FAQ-14：服务启动前 Pod 无法统计 {BUSINESS_SHORT}问题

---

## 📋 文档概述

本文档收集了 Example Service 服务层的常见问题及解决方案，帮助开发者和运维人员快速定位和解决问题。

---

## FAQ-15: 为什么需要新增 `pod_resource_dim_metric` 表？（v4.0 新增）🆕

### 问题描述

当前 `pod_resource_status` 表已经可以查询 {BUSINESS_SHORT}，为什么还要新增 `pod_resource_dim_metric` 表？这不是重复吗？

### 核心问题

**存储利用率低**：
- status 表有 40+ 字段，每行 1255 bytes
- GPU 查询只使用 14 个核心字段（含镜像+节点维度），每行只需 ~480 bytes
- **存储利用率 = 14/40 = 35%**，造成存储浪费

**查询性能差**：
- 每次 GPU 查询都需要扫描整行数据（包括无用字段）
- 页面缓存效率低
- 索引大小占用高（261 MB）

### 解决方案

**职责分离**：
- `pod_resource_status`：负责状态流转（读写表，30天 TTL）
- `pod_resource_dim_metric`：负责 GPU 聚合查询（只读表，90天 TTL）

**效果对比**：
| 指标 | 当前 | 优化后 |
|------|------|--------|
| status 表大小 | 2063 MB | ~480 MB (-77%) |
| GPU 查询扫描 | 1255 bytes/行 | 480 bytes/行 (-62%) |
| 总存储（稳定后） | ~3500 MB | ~1400 MB (-60%) |

**参考文档**：`docs/design/service_layer_architecture_v4.0.md#11-数据层架构优化v40-新增`

---

## FAQ-16: `pod_resource_dim_metric` 表如何同步数据？（v4.0 新增）🆕

### 问题描述

`pod_resource_dim_metric` 是只读表，它的数据从哪里来？同步频率是多少？

### 同步机制

| 参数 | 值 | 说明 |
|------|-----|------|
| 同步方式 | 定时批量同步 | 平衡一致性与性能 |
| 同步频率 | **15 分钟** | 每 15 分钟从 status 表增量同步 |
| 同步范围 | 增量同步 | 只同步 `updated_at > 15分钟前` 的记录 |
| 幂等性保证 | ON CONFLICT DO UPDATE | 冲突时更新（而非跳过） |

### 同步器实现

**代码位置**：`internal/pkg/syncer/dim_metric_syncer.go`

**Cron 配置**：
```yaml
cron:
  enabled: true
  jobs:
    - name: "sync-dim-metric"
      schedule: "*/15 * * * *"  # 每15分钟
      job: "DimMetricSyncer.Sync"
```

### 数据延迟

**影响**：
- GPU 查询最多有 15 分钟数据延迟
- 对于历史查询（> 1 小时），15 分钟延迟可忽略
- 对于实时监控（< 15 分钟），建议直接查询 status 表

**参考文档**：`docs/design/service_layer_architecture_v4.0.md#113-数据同步机制

---

## FAQ-17: `k8s_pod_uid` 是什么？为什么需要 UNIQUE 约束？（v4.0 新增）🆕

### 什么是 SSOT？

**SSOT** = Single Source of Truth（唯一真实来源）

在 Example Service 架构中：
- **`k8s_pod_uid`** = SSOT（Kubernetes Pod 的唯一标识符）
- **`resource_id`** = 数据库内部主键（UUID，用于外键关联）

### 问题发现

**Research 分析**：`docs/research/deep_dive_resource_id_and_storage_20260402.md`

| 发现项 | 数据 | 影响 |
|--------|------|------|
| **k8s_pod_uid 缺少 UNIQUE 约束** | DDL 中没有约束 | 导致 42.27% 重复率 |
| **重复记录数** | 63.6万条 | 浪费 ~900 MB 存储 |
| **同一 Pod 有多个 resource_id** | 一个 k8s_pod_uid 对应多个 resource_id | 数据一致性问题 |

### 修复方案

**添加 UNIQUE 约束**：
```sql
ALTER TABLE pod_resource_status
ADD CONSTRAINT uniq_pod_resource_status_k8s_pod_uid 
UNIQUE (k8s_pod_uid);
```

**清理重复记录**：
```sql
WITH ranked AS (
    SELECT 
        resource_id,
        k8s_pod_uid,
        ROW_NUMBER() OVER (
            PARTITION BY k8s_pod_uid 
            ORDER BY created_at DESC, status DESC
        ) AS rn
    FROM pod_resource_status
)
DELETE FROM pod_resource_status
WHERE resource_id IN (
    SELECT resource_id FROM ranked WHERE rn > 1
);
```

### 为什么重要？

**数据一致性**：
- 确保 `k8s_pod_uid` → `resource_id` 是 1:1 映射
- 避免同一个 Pod 有多条 status 记录
- 保证 {BUSINESS_DESCRIPTION}的准确性

**存储优化**：
- 清理 63.6 万条重复记录
- 节省 ~900 MB 存储空间

**参考文档**：`docs/research/deep_dive_resource_id_and_storage_20260402.md`

---

## FAQ-18: status 表和 dim_metric 表的 TTL 为什么不同？（v4.0 新增）🆕

### TTL 对比

| 表名 | TTL 周期 | 理由 | 清理频率 |
|------|---------|------|----------|
| `pod_resource_status` | **30 天** | 状态表，与history表对齐，中期保留 | 每天凌晨 3 点 |
| `pod_resource_history` | **30 天** | 审计表，与status表对齐，节省存储 | 每天凌晨 2 点 |
| `pod_resource_dim_metric` | **90 天** | 维度表，长期保留，支持历史查询（覆盖99.99% GPU用量）| 每天凌晨 4 点 |
| `pod_resource_gpu_usage` | **90 天** | 事实表，长期保留，与dim_metric表对齐 | 每天凌晨 5 点 |

### 为什么 status 表和 history 表 TTL 对齐？

**职责对齐设计**：
- `status` 表：状态流转记录（30天 TTL）
- `history` 表：审计日志（30天 TTL）
- `dim_metric` 表：GPU 聚合查询维度（90天 TTL）
- `gpu_usage` 表：{BUSINESS_SHORT}事实数据（90天 TTL）

**分组保留策略**：
- **短期组**（30天）：status + history（运营数据，节省存储）
- **长期组**（90天）：dim_metric + gpu_usage（度量数据，支持历史查询）

**存储优化**：
- 30天 TTL 对齐：清理逻辑简单，维护成本低
- 90天 TTL 对齐：覆盖99.99% GPU用量，满足历史查询需求

### 为什么 dim_metric 表 TTL 更长？

**查询需求**：
- {BUSINESS_DESCRIPTION}通常需要查看历史趋势（30/60/90 天）
- `dim_metric` 表字段少，存储成本低（400 bytes/行）
- 长期保留支持历史分析和趋势预测

### 清理条件

**status 表（30天 TTL，安全清理）**：
```sql
DELETE FROM pod_resource_status
WHERE created_at < NOW() - INTERVAL '30 days'
  AND status = 'RELEASED'  -- 只清理已释放的
  AND NOT EXISTS (
      SELECT 1 FROM pod_resource_gpu_usage
      WHERE resource_id = pod_resource_status.resource_id
        AND usage_start_at >= NOW() - INTERVAL '30 days'
  );
```

**history 表（30天 TTL）**：
```sql
DELETE FROM pod_resource_history
WHERE created_at < NOW() - INTERVAL '30 days';
```

**dim_metric 表（90天 TTL）**：
```sql
DELETE FROM pod_resource_dim_metric
WHERE created_at < NOW() - INTERVAL '90 days';
```

**gpu_usage 表（90天 TTL）**：
```sql
DELETE FROM pod_resource_gpu_usage
WHERE created_at < NOW() - INTERVAL '90 days';
```

**参考文档**：
- `docs/research/ttl_data_consistency_research_20260402.md`
- `docs/design/service_layer_architecture_v4.0.md#115-ttl-策略设计v40-优化`

---

## FAQ-1: 为什么我的 Pod 没有被 Example Service 监听？（v3.2 更新）

### 症状
- Pod 创建后，数据库 `pod_resource_status` 表中没有记录
- Informer 日志显示 "Skipping unmanaged Pod"

### 排查步骤

1. **检查 Pod Annotations**（v3.2 优先方法）：
   ```bash
   kubectl get pod <pod-name> -o jsonpath='{.metadata.annotations}'
   ```
   
   **必需字段**：
   - `cmdb.example.com/resource-type`（v3.2 推荐）
   - `user_id`, `team_id`, `project_id`（CMDB 维度）

2. **检查 Pod Labels**（降级方法）：
   ```bash
   kubectl get pod <pod-name> -o jsonpath='{.metadata.labels}'
   ```

3. **检查 Pod Namespace**：
   - DevPod: `example-service`
   - ArgoWorkflow: `argo`, `dcs`
   - RayJob: 任意 namespace（需有 `ray.io/is-ray-node` label）

4. **检查 Informer 日志**：
   ```bash
   docker logs {PROJECT_NAME}-api | grep "<pod-name>"
   ```

### 常见原因

| 原因 | 解决方案 |
|------|----------|
| 缺少 `cmdb.example.com/resource-type` annotation | 添加 annotation 或 label |
| Namespace 不匹配 | 检查 Pod 所在 namespace |
| Informer 未启动 | 检查服务状态 |
| Pod 启动早于服务部署 | 无法回溯历史事件，等待下一个 Pod |

---

## FAQ-19: 为什么有两个 SSOT 表（status + dim_metric）？（v4.1 新增）🆕

### 问题描述

v4.1 架构为什么有两个表记录同一个 Pod 的信息？这是否违反 SSOT（Single Source of Truth）原则？

### 核心回答

**不违反 SSOT 原则**，而是采用**职责分离 + 时间分层**的 SSOT 设计。

**核心原则**：
> v4.1 架构采用**职责分离 + 时间分层**的 SSOT 设计
> - 同一个 Pod 的数据分布在两个表（status + dim_metric）
> - 通过 `resource_id` UUID 保持关联
> - 按时间范围分层（0-30天 vs 0-90天）
> - 按职责分离（状态流转 vs GPU 查询）

**两个表的职责对比**：

| 维度 | pod_resource_status | pod_resource_dim_metric |
|------|---------------------|-------------------------|
| **职责** | 状态流转 + 实时查询 | GPU 查询（长期） |
| **生命周期** | 0-30天 | 0-90天 |
| **特性** | 读写表，Informer 写入 | 只读表，15分钟同步 |
| **字段数** | 40+ 字段（宽表） | 10 字段（窄表） |
| **存储利用率** | 13% | 46% |
| **查询性能** | 扫描 40+ 字段 | 扫描 10 字段（60%↓） |

**对比 v3.x 单一 SSOT 架构**：
- ❌ v3.x: status 表职责混乱（状态流转 + GPU 查询）
- ✅ v4.1: 职责分离清晰（状态流转 vs GPU 查询）

### 相关文档

- **[服务层架构设计 v4.1](./service_layer_architecture_v4.1.md)** - 第 11.2.1 节 SSOT 定义
- **[STORY-15-19: {BUSINESS_SHORT}外键迁移](../scrum/story/story-15-19-{BUSINESS_DOMAIN}-fk-migration.md)** - 外键迁移实施方案

---

## FAQ-20: 15分钟同步延迟是否影响业务？（v4.1 新增）🆕

### 问题描述

dim_metric 表通过 15 分钟定时同步自 status 表，这个延迟是否会影响业务查询？

### 核心回答

**对大部分业务场景影响可接受**，但需要明确查询路由策略。

**影响评估**：

| 业务场景 | 影响 | 可接受性 | 缓解措施 |
|---------|------|----------|----------|
| **{BUSINESS_DESCRIPTION}**（0-90天） | 🟢 低 | ✅ 完全可接受 | 使用 dim_metric 表（长期 SSOT） |
| **Pod 实时状态查询**（0-30天） | 🔴 高 | ❌ 不可接受 | 使用 status 表（实时 SSOT） |
| **Pod 历史状态查询**（31-90天） | 🟢 低 | ✅ 完全可接受 | 使用 dim_metric 表 + LEFT JOIN status |
| **GPU 聚合查询**（用户/团队/项目） | 🟢 低 | ✅ 完全可接受 | 使用 dim_metric 表（减少 60% 扫描） |

**查询路由策略**：
```sql
-- 实时查询（0-30天）：使用 status 表
SELECT * FROM pod_resource_status
WHERE resource_id = ?
  AND created_at >= NOW() - INTERVAL '30 days';

-- 历史查询（31-90天）：使用 dim_metric 表
SELECT * FROM pod_resource_dim_metric
WHERE resource_id = ?
  AND created_at < NOW() - INTERVAL '30 days';
```

### 相关文档

- **[服务层架构设计 v4.1](./service_layer_architecture_v4.1.md)** - 第 11.6 节查询路由策略

---

## FAQ-21: 如何选择查询 status 还是 dim_metric？（v4.1 新增）🆕

### 问题描述

什么时候查询 status 表？什么时候查询 dim_metric 表？

### 核心回答

**按时间范围 + 查询目的**选择正确的 SSOT。

**决策树**：

```
查询需求
  ↓
  ├─ GPU 聚合查询（用户/团队/项目）
  │   ↓
  │   └─ 使用 dim_metric 表（0-90天）✅
  │       └─ LEFT JOIN gpu_usage 表
  │
  ├─ Pod 详情查询
  │   ↓
  │   ├─ 需要实时状态（0-30天）？
  │   │   └─ 使用 status 表 ✅
  │   │
  │   └─ 需要历史数据（31-90天）？
  │       └─ 使用 dim_metric 表 + LEFT JOIN status ✅
  │
  └─ 实时状态查询（Pod 当前状态）
      ↓
      └─ 使用 status 表（Informer 实时写入）✅
```

**示例查询**：

**场景 1：{BUSINESS_DESCRIPTION}（0-90天）**
```sql
SELECT
    d.user_id,
    d.team_id,
    COALESCE(SUM(u.gpu_hours), 0) AS total_gpu_hours
FROM pod_resource_dim_metric d      -- ✅ 长期 SSOT
LEFT JOIN pod_resource_gpu_usage u ON d.resource_id = u.resource_id
WHERE d.created_at >= NOW() - INTERVAL '90 days'
GROUP BY d.user_id, d.team_id;
```

**场景 2：Pod 实时状态（0-30天）**
```sql
SELECT * FROM pod_resource_status     -- ✅ 实时 SSOT
WHERE resource_id = ?
  AND created_at >= NOW() - INTERVAL '30 days';
```

**场景 3：Pod 历史状态（31-90天）**
```sql
SELECT
    d.resource_id,
    d.pod_name,
    d.status,
    s.user_name,   -- 允许为 NULL
    s.team_name    -- 允许为 NULL
FROM pod_resource_dim_metric d       -- ✅ 长期 SSOT
LEFT JOIN pod_resource_status s ON d.resource_id = s.resource_id
WHERE d.resource_id = ?;
```

### 相关文档

- **[服务层架构设计 v4.1](./service_layer_architecture_v4.1.md)** - 第 11.6 节查询路由策略

---

## FAQ-22: TTL 清理后如何查询历史数据？（v4.1 新增）🆕

### 问题描述

status 表在 30 天后被清理，如何查询 31-90 天的历史数据？

### 核心回答

**使用 dim_metric 表（长期 SSOT）**，并通过 `LEFT JOIN` 获取扩展信息。

**关键设计**：
- `dim_metric` 表保留 90 天（长期 SSOT）
- `status` 表保留 30 天（短期 SSOT）
- 通过 `resource_id` UUID 保持关联

**查询模式**：

**31-90天数据查询**：
```sql
SELECT
    d.resource_id,
    d.pod_name,
    d.status,
    d.user_id,
    d.team_id,
    d.gpu_count,
    -- 扩展信息（如果 status 仍存在）
    s.user_name,   -- 允许为 NULL（status 已被清理）
    s.team_name,   -- 允许为 NULL
    s.image_name   -- 允许为 NULL
FROM pod_resource_dim_metric d
LEFT JOIN pod_resource_status s ON d.resource_id = s.resource_id
WHERE d.resource_id = ?;
```

**注意**：
- ✅ 使用 `LEFT JOIN`（允许 `s` 为 NULL）
- ✅ dim_metric 表保留 90 天（覆盖 31-90 天）
- ✅ resource_id 关联保证数据一致性

### 相关文档

- **[服务层架构设计 v4.1](./service_layer_architecture_v4.1.md)** - 第 11.6 节查询路由策略
- **[STORY-15-19: {BUSINESS_SHORT}外键迁移](../scrum/story/story-15-19-{BUSINESS_DOMAIN}-fk-migration.md)** - 外键迁移实施方案

---

## FAQ-23: gpu_usage 外键为什么要迁移到 dim_metric？（v4.1 新增）🆕

### 问题描述

为什么 gpu_usage 的外键要从 status 表迁移到 dim_metric 表？

### 核心回答

**对齐 TTL 策略**，避免 status 清理时级联删除 gpu_usage。

**问题背景**：

| 表名 | TTL | 清理时机 |
|------|-----|---------|
| **pod_resource_status** | 30 天 | 每天凌晨 3 点 |
| **pod_resource_dim_metric** | 90 天 | 每天凌晨 4 点 |
| **pod_resource_gpu_usage** | 90 天 | - |

**如果 gpu_usage FK 指向 status（30天 TTL）**：
```
Day 30:  status 记录被删除
    ↓
    CASCADE 删除 gpu_usage
    ↓
Day 30:  gpu_usage 被删除（❌ 违反 90天 TTL 策略）
```

**如果 gpu_usage FK 指向 dim_metric（90天 TTL）**：
```
Day 30:  status 记录被删除
    ↓
    gpu_usage 不受影响（FK 指向 dim_metric）
    ↓
Day 90:  dim_metric 记录被删除
    ↓
    CASCADE 删除 gpu_usage
    ↓
Day 90:  gpu_usage 被删除（✅ 符合 90天 TTL 策略）
```

**实施详情**：
- ✅ STORY-15-03: 创建 dim_metric 表
- ✅ STORY-15-19: 迁移 gpu_usage 外键到 dim_metric
- ✅ STORY-15-04: TTL 清理（在外键迁移后执行）

### 相关文档

- **[服务层架构设计 v4.1](./service_layer_architecture_v4.1.md)** - 第 11.5 节 TTL 策略设计
- **[STORY-15-19: {BUSINESS_SHORT}外键迁移](../scrum/story/story-15-19-{BUSINESS_DOMAIN}-fk-migration.md)** - 完整实施方案

---

## FAQ-24: dim_metric 表与 status 表的数据关系如何保持？（v4.1 新增）🆕

### 问题描述

两个表如何保证数据一致性？15分钟同步是否会丢失数据？

### 核心回答

**通过 resource_id UUID + 15分钟定时同步**保证数据一致性。

**数据关联机制**：

```sql
-- status 表（写入）
CREATE TABLE pod_resource_status (
    resource_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    k8s_pod_uid VARCHAR(64) NOT NULL,
    ...
);

-- dim_metric 表（同步）
CREATE TABLE pod_resource_dim_metric (
    resource_id UUID PRIMARY KEY,  -- ✅ 与 status 表共享 UUID
    k8s_pod_uid VARCHAR(64) NOT NULL UNIQUE,
    ...
);

-- 同步逻辑（15分钟）
INSERT INTO pod_resource_dim_metric (resource_id, ...)
SELECT resource_id, ... FROM pod_resource_status
WHERE updated_at > NOW() - INTERVAL '15 minutes'
ON CONFLICT (resource_id) DO UPDATE SET ...;
```

**一致性保证**：

| 机制 | 说明 | 保证 |
|------|------|------|
| **resource_id 关联** | 两个表共享同一个 UUID | ✅ 跨表 JOIN 一致性 |
| **15分钟同步** | DimMetricSyncer 定时同步 | ✅ 最终一致性 |
| **ON CONFLICT DO UPDATE** | 幂等性保证 | ✅ 重复同步不会产生重复数据 |

**数据不丢失**：
- ✅ Informer 先写入 status 表（实时写入）
- ✅ DimMetricSyncer 每 15 分钟同步（增量同步）
- ✅ `ON CONFLICT DO UPDATE` 保证幂等性
- ✅ 最大同步延迟：15 分钟

### 相关文档

- **[服务层架构设计 v4.1](./service_layer_architecture_v4.1.md)** - 第 11.4 节数据同步机制

---

## FAQ-25: 如何验证 SSOT 数据一致性？（v4.1 新增）🆕

### 问题描述

如何验证 status 表与 dim_metric 表的数据一致性？

### 核心回答

**通过 resource_id 关联验证**，检查两个表的数据是否一致。

**验证 SQL**：

```sql
-- 验证 resource_id 关联完整性
SELECT
    COUNT(DISTINCT s.resource_id) AS status_count,
    COUNT(DISTINCT d.resource_id) AS dim_metric_count,
    COUNT(DISTINCT d.resource_id) - COUNT(DISTINCT s.resource_id) AS diff_count
FROM pod_resource_status s
FULL OUTER JOIN pod_resource_dim_metric d ON s.resource_id = d.resource_id;

-- 预期结果：
-- status_count = dim_metric_count（或者 diff_count 很小，在同步误差范围内）
```

**验证 {BUSINESS_SHORT}外键完整性**：
```sql
-- 验证所有 gpu_usage 记录都关联到有效的 dim_metric 记录
SELECT
    COUNT(*) AS total_gpu_usage,
    COUNT(DISTINCT u.resource_id) AS distinct_refs,
    COUNT(DISTINCT d.resource_id) AS valid_refs,
    COUNT(DISTINCT u.resource_id) - COUNT(DISTINCT d.resource_id) AS orphan_refs
FROM pod_resource_gpu_usage u
LEFT JOIN pod_resource_dim_metric d ON u.resource_id = d.resource_id;

-- 预期结果：
-- orphan_refs = 0（无 orphan 记录）
```

### 相关文档

- **[STORY-15-19: {BUSINESS_SHORT}外键迁移](../scrum/story/story-15-19-{BUSINESS_DOMAIN}-fk-migration.md)** - AC-5 数据一致性验证

---

## FAQ-26: 聚合查询为什么使用 dim_metric 作为主表？（v4.1.1 新增）🆕

### 问题描述

v4.2 架构中，GPU 聚合查询为什么使用 `dim_metric` 作为主表，而不是 `gpu_usage`？

### 核心回答

**基于生产数据验证的优化决策**：主表选择应基于**数据量 + 过滤谓词下推**两个关键因素。

**生产环境数据统计**（2026-04-25验证）：
```
pod_resource_dim_metric: 48 MB (60,313行)
pod_resource_gpu_usage:  5.8 MB (6,383行)
比例: 8.1:1
```

**查询语义差异**：
```sql
-- v4.1（FROM gpu_usage）: 只返回有GPU使用记录的Pod
SELECT ... FROM gpu_usage u INNER JOIN dim_metric s
WHERE u.usage_start_at >= NOW() - INTERVAL '30 days'
-- 返回: 6,383个Pod

-- v4.2（FROM dim_metric）: 返回所有Pod，包括无GPU使用的
SELECT ... FROM dim_metric s LEFT JOIN gpu_usage u
WHERE s.created_at >= NOW() - INTERVAL '30 days'
-- 返回: 60,313个Pod（差异9.4倍）
```

**关键原则**：
1. **主表选择依据**：
   - ✅ **数据量驱动**：大表（dim_metric 48MB）作为主表驱动查询
   - ✅ **过滤谓词下推**：`WHERE s.created_at` 在主表上，支持索引扫描
   - ✅ **覆盖度优先**：统计所有Pod（90%无GPU使用）而非只统计有使用记录的Pod

2. **JOIN 类型选择**：
   - ✅ **LEFT JOIN**：保留所有dim_metric记录，包括无gpu_usage的Pod
   - ❌ **INNER JOIN**：只返回有GPU使用记录的Pod（丢失90%的Pod）

3. **性能对比**（EXPLAIN ANALYZE验证）：
   ```
   v4.1（FROM gpu_usage）:  0.471 ms, Nested Loop, Buffers: 56
   v4.2（FROM dim_metric）: 0.573 ms, Merge Left Join, Buffers: 17+2
   ```
   虽然v4.1稍快20%，但**查询语义完全不同**（6K vs 60K行）。

### 设计原则

> **主表选择黄金法则**：
> 1. 大表驱动，小表关联（Star Schema优化）
> 2. 过滤条件在大表上，支持谓词下推
> 3. 查询覆盖度优先（统计所有对象，而非只有记录的）

### 相关文档

- **[STORY-15-15: Logic层 dim_metric 表查询支持](../scrum/story/story-15-15-logic-layer-query.md)** - v4.2查询路由优化
- **生产数据验证报告**: `test_reports/STORY-15-15-execution-plan.md`

---

## FAQ-27: LEFT JOIN 场景下如何正确处理 NULL 值？（v4.1.1 新增）🆕

### 问题描述

v4.2 架构使用 `dim_metric LEFT JOIN gpu_usage`，如何正确处理NULL值？是否应该区分"0"和"NULL"？

### 核心回答

**基于生产数据验证的语义决策**：在LEFT JOIN场景下，**NULL转0是正确的业务语义**。

**生产环境数据分布**（2026-04-25验证）：
```
有GPU使用记录的Pod: 5,840 (9.68%)
无GPU使用记录的Pod:  54,473 (90.32%)
总GPU使用量: 2,484.35小时
```

**COALESCE 语义验证**：
```sql
SELECT 
  COUNT(DISTINCT s.resource_id) AS total_pods,           -- 60,313
  COUNT(DISTINCT CASE WHEN u.usage_id IS NULL THEN s.resource_id END) AS pods_with_null_gpu_usage,  -- 54,473
  COUNT(DISTINCT CASE WHEN u.usage_id IS NOT NULL THEN s.resource_id END) AS pods_with_gpu_usage,  -- 5,840
  ROUND(SUM(u.gpu_hours), 2) AS total_gpu_hours_without_coalesce,  -- 2,484.35
  ROUND(COALESCE(SUM(u.gpu_hours), 0), 2) AS total_gpu_hours_with_coalesce  -- 2,484.35
FROM pod_resource_dim_metric s
LEFT JOIN pod_resource_gpu_usage u ON s.resource_id = u.resource_id;
```

**关键发现**：
- 90.32%的Pod没有GPU使用记录（业务上=0小时）
- 使用`COALESCE(SUM(u.gpu_hours), 0)`将NULL转为0
- **这是正确的业务语义**，不是"数据缺失"

### 数据语义原则

> **LEFT JOIN NULL处理黄金法则**：
> 1. **NULL = 业务上的0**：当LEFT JOIN右表无记录时，NULL表达"无此业务数据"
> 2. **COALESCE统一语义**：将NULL转为0，保证聚合结果一致性
> 3. **不需要区分0和NULL**：在这个场景下，NULL就是0（无GPU使用）

### 错误的过度设计

❌ **错误**：区分"0"和"NULL"为"无使用"vs"数据缺失"
```sql
CASE 
  WHEN u.usage_id IS NULL THEN 'DATA_MISSING'  -- ❌ 过度设计
  WHEN SUM(u.gpu_hours) = 0 THEN 'NO_USAGE' 
  ELSE 'HAS_USAGE'
END
```

✅ **正确**：统一使用COALESCE
```sql
COALESCE(SUM(u.gpu_hours), 0) AS total_gpu_hours  -- ✅ 简洁正确
```

### 相关文档

- **[STORY-15-15: Logic层 dim_metric 表查询支持](../scrum/story/story-15-15-logic-layer-query.md)** - AC-2 COALESCE处理
- **生产数据验证报告**: `test_reports/STORY-15-15-execution-plan.md`

---

**文档版本**: v4.1.1
**创建日期**: 2026-02-02
**最后更新**: 2026-04-25
**作者**: Development Team + Architect + Scrum Master
**状态**: 正式发布
