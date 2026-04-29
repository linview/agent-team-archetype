# Story: 活跃 Pod {BUSINESS_SHORT}实时计算

---
id: "STORY-6-05"
epic_id: "EPIC-6"
title: "活跃 Pod {BUSINESS_SHORT}实时计算"
description: "实现活跃 Pod（usage_end_at 为 NULL）的 {BUSINESS_SHORT}实时查询功能，支持在 API 层返回动态计算的 GPU×Hours 数据"
status: "COMPLETED"
completed_date: "2026-04-21"
priority: "P1"
story_points: 5
assignee: "TBD"
reviewer: "TBD"
start_date: "TBD"
target_date: "TBD"
dependencies:
  - "STORY-6-04"  # 依赖 {BUSINESS_SHORT}计算引擎
tags:
  - "service-layer"
  - "gpu-calculation"
  - "api"
  - "database"
acceptance_criteria:
  - "DAO 层实现 GetGPUUsageWithCalculation() 方法"
  - "SQL 查询支持使用 NOW() 临时计算活跃 Pod 用量"
  - "API 响应包含 calculated_at 时间戳字段"
  - "前端可依据 usage_end_at 判断 Pod 是否活跃"
  - "单元测试覆盖率 > 80%"
  - "SIT 测试通过"
definition_of_done:
  - "代码已提交并通过 Review"
  - "单元测试覆盖率 > 80%"
  - "API 文档已更新"
  - "SIT 测试通过"
  - "性能测试通过（API 响应时间 < 500ms）"
version: "1.0"
created_at: "2026-02-02"
updated_at: "2026-04-21"
---

## 📋 用户故事（User Story）

### 作为
算法工程师、项目管理员、运维人员

### 我想要
查询活跃 Pod（正在运行的 Pod）的实时 {BUSINESS_SHORT}

### 以便于
- 实时监控 GPU 算力消耗
- 及时发现异常资源占用
- 进行成本核算和预算管理

### 验收标准
- [ ] API 查询活跃 Pod 时返回实时 {BUSINESS_SHORT}
- [ ] API 响应包含 `calculated_at` 时间戳
- [ ] `usage_end_at` 为 NULL 时表示 Pod 仍在运行
- [ ] 查询性能满足 P95 < 500ms

---

## 🎯 业务价值

### 当前痛点
1. **无法查询活跃 Pod 用量**：`pod_resource_gpu_usage` 表中，活跃 Pod 的 `usage_end_at` 字段为 NULL，导致无法计算 GPU×Hours
2. **无法实时监控**：管理者无法实时了解当前正在运行的 Pod 的算力消耗情况
3. **成本核算滞后**：只能在 Pod 结束后才能知道最终用量，无法进行实时成本控制

### 解决方案价值
1. **实时监控能力**：提供活跃 Pod 的实时 {BUSINESS_SHORT}查询
2. **动态计算**：使用 `NOW()` 临时计算，无需等待 Pod 结束
3. **前端友好**：通过 `usage_end_at` 判断活跃状态，通过 `calculated_at` 知道计算时间

---

## 📐 设计方案

### 设计文档参考
**详细设计方案**：[服务层架构设计 v1.0 - 第 7 节](../../design/service_layer_architecture_v1.0.md#7-活跃-pod-gpu-用量计算方案)

**相关章节**：
- 第 7.2 节：API 响应格式
- 第 7.3 节：数据库查询逻辑
- 第 7.4 节：实现位置

### API 响应格式

**统一返回**：所有记录在一个列表中，通过 `usage_end_at` 是否为 NULL 判断活跃状态

```json
{
  "resource_id": "res-001",
  "pod_name": "example-service-chenhuazhong",
  "gpu_count": 4,
  "usage_cycle": 1,
  "usage_start_at": "2026-02-02T10:00:00Z",
  "usage_end_at": null,
  "calculated_at": "2026-02-02T15:30:00Z",
  "gpu_hours": 18.0
}
```

**字段说明**：
- `usage_end_at` 为 `null` → 活跃 Pod
- `usage_end_at` 有值 → 已结束 Pod
- `calculated_at` → 查询计算时间戳
- `gpu_hours` → 实时估算值（活跃 Pod）或最终值（已结束 Pod）

### 数据库查询逻辑

**SQL 查询**（`internal/dao/pod_resource_gpu_usage_dao.go`）：
```sql
-- 活跃 Pod 用量查询（统一处理）
SELECT
    resource_id,
    usage_cycle,
    gpu_count,
    usage_start_at,
    usage_end_at,
    -- 如果 usage_end_at 为 NULL，使用 NOW() 计算
    CASE
        WHEN usage_end_at IS NULL THEN
            gpu_count * EXTRACT(EPOCH FROM (NOW() - usage_start_at)) / 3600.0
        ELSE
            gpu_hours
    END AS gpu_hours_calculated,
    -- 计算时间戳
    NOW() AS calculated_at
FROM pod_resource_gpu_usage
WHERE resource_id = ?
ORDER BY usage_cycle;
```

---

## 🔧 技术实现

### 1. DAO 层实现

**文件**：`internal/dao/pod_resource_gpu_usage_dao.go`

**新增方法**：
```go
// GetGPUUsageWithCalculation 查询 Pod 的 {BUSINESS_SHORT}记录（包含活跃 Pod 的实时计算）
// 返回值中，usage_end_at 为 NULL 的记录表示活跃 Pod，gpu_hours 为实时估算值
func (d *PodResourceGPUUsageDAO) GetGPUUsageWithCalculation(
    ctx context.Context,
    resourceID string,
) ([]*model.PodResourceGPUUsageWithCalculation, error) {
    query := `
        SELECT
            resource_id,
            usage_cycle,
            gpu_count,
            gpu_product,
            usage_start_at,
            usage_end_at,
            -- 如果 usage_end_at 为 NULL，使用 NOW() 计算
            CASE
                WHEN usage_end_at IS NULL THEN
                    gpu_count * EXTRACT(EPOCH FROM (NOW() - usage_start_at)) / 3600.0
                ELSE
                    gpu_hours
            END AS gpu_hours_calculated,
            -- 计算时间戳
            NOW() AS calculated_at
        FROM pod_resource_gpu_usage
        WHERE resource_id = $1
        ORDER BY usage_cycle
    `

    rows, err := d.db.Query(ctx, query, resourceID)
    if err != nil {
        return nil, fmt.Errorf("failed to query gpu usage: %w", err)
    }
    defer rows.Close()

    var records []*model.PodResourceGPUUsageWithCalculation
    for rows.Next() {
        var record model.PodResourceGPUUsageWithCalculation
        if err := rows.Scan(
            &record.ResourceID,
            &record.UsageCycle,
            &record.GPUCount,
            &record.GPUProduct,
            &record.UsageStartAt,
            &record.UsageEndAt,
            &record.GPUCalculatedHours,
            &record.CalculatedAt,
        ); err != nil {
            return nil, fmt.Errorf("failed to scan row: %w", err)
        }
        records = append(records, &record)
    }

    return records, nil
}
```

**数据模型**（`internal/model/pod_resource.go`）：
```go
// PodResourceGPUUsageWithCalculation 包含计算的 {BUSINESS_SHORT}
type PodResourceGPUUsageWithCalculation struct {
    ResourceID         string     `db:"resource_id"`
    UsageCycle         int        `db:"usage_cycle"`
    GPUCount           int        `db:"gpu_count"`
    GPUProduct         string     `db:"gpu_product"`
    UsageStartAt       time.Time  `db:"usage_start_at"`
    UsageEndAt         *time.Time `db:"usage_end_at"`
    GPUCalculatedHours float64    `db:"gpu_hours_calculated"` // 计算后的用量
    CalculatedAt       time.Time  `db:"calculated_at"`         // 计算时间戳
}
```

### 2. Logic 层实现

**文件**：`internal/logic/usage_query_logic.go`（如果不存在则创建）

```go
// QueryGPUUsage 查询 Pod 的 {BUSINESS_SHORT}（包含活跃 Pod 的实时计算）
func (l *UsageQueryLogic) QueryGPUUsage(req *types.UsageQueryReq) (*types.UsageQueryResp, error) {
    // 调用 DAO 层查询
    records, err := l.svcCtx.GpuUsageDAO.GetGPUUsageWithCalculation(l.ctx, req.ResourceID)
    if err != nil {
        return nil, err
    }

    // 转换为 API 响应
    var usageItems []*types.GPUUsageItem
    for _, record := range records {
        item := &types.GPUUsageItem{
            ResourceID:   record.ResourceID,
            UsageCycle:   record.UsageCycle,
            GPUCount:     record.GPUCount,
            GPUProduct:   record.GPUProduct,
            UsageStartAt: record.UsageStartAt,
            UsageEndAt:   record.UsageEndAt,
            CalculatedAt: record.CalculatedAt,
            GPUHours:     record.GPUCalculatedHours,
            IsActive:     record.UsageEndAt == nil, // 判断是否活跃
        }
        usageItems = append(usageItems, item)
    }

    return &types.UsageQueryResp{
        ResourceID: req.ResourceID,
        UsageItems: usageItems,
        TotalHours: calculateTotalHours(usageItems),
    }, nil
}
```

### 3. API 类型定义

**文件**：`internal/types/types.go`

```go
// GPUUsageItem {BUSINESS_SHORT}记录（包含活跃 Pod 的实时计算）
type GPUUsageItem struct {
    ResourceID   string     `json:"resource_id"`
    UsageCycle   int        `json:"usage_cycle"`
    GPUCount     int        `json:"gpu_count"`
    GPUProduct   string     `json:"gpu_product"`
    UsageStartAt time.Time  `json:"usage_start_at"`
    UsageEndAt   *time.Time `json:"usage_end_at"`
    CalculatedAt time.Time  `json:"calculated_at"`
    GPUHours     float64    `json:"gpu_hours"`
    IsActive     bool       `json:"is_active"`
}

// UsageQueryResp {BUSINESS_SHORT}查询响应
type UsageQueryResp struct {
    ResourceID string        `json:"resource_id"`
    UsageItems []*GPUUsageItem `json:"usage_items"`
    TotalHours float64       `json:"total_hours"`
}
```

---

## 📝 实施步骤

### Step 1: 数据模型扩展
- [ ] 在 `internal/model/pod_resource.go` 中添加 `PodResourceGPUUsageWithCalculation` 结构
- [ ] 定义字段：`GPUCalculatedHours`, `CalculatedAt`, `IsActive`

### Step 2: DAO 层实现
- [ ] 在 `internal/dao/pod_resource_gpu_usage_dao.go` 中实现 `GetGPUUsageWithCalculation()` 方法
- [ ] 编写 SQL 查询逻辑（使用 CASE WHEN NOW()）
- [ ] 添加单元测试

### Step 3: Logic 层实现
- [ ] 在 `internal/logic/` 中创建或修改查询逻辑
- [ ] 调用 DAO 层方法
- [ ] 转换为 API 响应格式

### Step 4: API 类型定义
- [ ] 在 `internal/types/types.go` 中添加 `GPUUsageItem` 结构
- [ ] 在 `internal/types/types.go` 中添加 `UsageQueryResp` 结构
- [ ] 使用 goctl 重新生成 API 代码（如果需要）

### Step 5: 单元测试
- [ ] DAO 层单元测试（Mock 数据库）
- [ ] Logic 层单元测试（Mock DAO）
- [ ] 测试覆盖率 > 80%

### Step 6: 集成测试
- [ ] 创建测试 Pod 并让其处于 RUNNING 状态
- [ ] 调用 API 查询 {BUSINESS_SHORT}
- [ ] 验证 `usage_end_at` 为 NULL
- [ ] 验证 `calculated_at` 时间戳存在
- [ ] 验证 `gpu_hours` 为实时计算值

### Step 7: 文档更新
- [ ] 更新 API 文档（`docs/api/usage_api.md`）
- [ ] 更新 FAQ 文档（`docs/design/service_layer_faq.md`）
- [ ] 更新 CLAUDE.md（如有必要）

---

## ✅ 测试方案

### 单元测试

**测试文件**：`internal/dao/pod_resource_gpu_usage_dao_test.go`

```go
func TestGetGPUUsageWithCalculation(t *testing.T) {
    // 测试场景 1: 活跃 Pod（usage_end_at = NULL）
    // 测试场景 2: 已结束 Pod（usage_end_at 有值）
    // 测试场景 3: 混合场景（既有活跃也有已结束）
}
```

### SIT 集成测试

**测试文件**：`tests/sit/test_active_pod_gpu_usage.sh`

```bash
#!/bin/bash
# SIT 测试：活跃 Pod {BUSINESS_SHORT}查询

# 1. 创建测试 Pod
create-devpod test-active-001 4 example-service 600

# 2. 等待 Pod 进入 RUNNING 状态
sleep 10

# 3. 查询 {BUSINESS_SHORT} API
curl -X GET "http://localhost:8082/api/v1/usage?resource_id=test-active-001"

# 4. 验证响应
# - usage_end_at 为 null
# - calculated_at 字段存在
# - gpu_hours > 0

# 5. 清理
delete test-active-001 example-service
```

---

## 🎯 验收标准

### 功能验收
- [ ] API 查询活跃 Pod 时返回实时 {BUSINESS_SHORT}
- [ ] API 响应包含 `calculated_at` 时间戳字段
- [ ] `usage_end_at` 为 NULL 时表示 Pod 仍在运行
- [ ] `is_active` 字段正确标识 Pod 活跃状态

### 性能验收
- [ ] API 响应时间 < 500ms (P95)
- [ ] 支持并发查询 100+ QPS
- [ ] 数据库查询优化（使用索引）

### 质量验收
- [ ] 单元测试覆盖率 > 80%
- [ ] 代码通过 golangci-lint 检查
- [ ] 代码通过 Review
- [ ] SIT 测试通过

### 文档验收
- [ ] API 文档已更新
- [ ] FAQ 文档已更新（FAQ-2）
- [ ] 代码注释完整

---

## 📊 工作量估算

| 任务 | 预估时间 | 说明 |
|------|---------|------|
| 数据模型扩展 | 0.5 天 | 添加结构体定义 |
| DAO 层实现 | 1 天 | SQL 查询 + 单元测试 |
| Logic 层实现 | 0.5 天 | 业务逻辑转换 |
| API 类型定义 | 0.5 天 | 类型定义 + goctl 生成 |
| 集成测试 | 0.5 天 | SIT 测试脚本 |
| 文档更新 | 0.5 天 | API 文档 + FAQ |
| 缓冲时间 | 0.5 天 | 代码 Review、Bug 修复 |
| **总计** | **4 天** | **约 2-3 个工作日** |

**故事点（Story Points）**：5

---

## 🚨 风险与依赖

### 技术风险
1. **SQL 查询性能**：使用 `NOW()` 可能影响查询性能
   - **缓解措施**：添加索引（resource_id, usage_start_at），性能测试
2. **时区问题**：`NOW()` 使用数据库服务器时间，可能与业务时区不一致
   - **缓解措施**：统一使用 UTC 时区，在 API 层转换

### 依赖关系
- **依赖 Story**：STORY-6-04（{BUSINESS_SHORT}计算引擎）
- **前置条件**：
  - `pod_resource_gpu_usage` 表已存在
  - `gpu_hours` 字段的 Trigger 已实现
  - DAO 层基础方法已实现

### 阻塞因素
- 数据库 Schema 未确定
- STORY-6-04 未完成

---

## 📚 参考文档

### 设计文档
- [服务层架构设计 v1.0 - 第 7 节](../../design/service_layer_architecture_v1.0.md#7-活跃-pod-gpu-用量计算方案)
- [服务层 FAQ - FAQ-2](../../design/service_layer_faq.md#faq-2-活跃-pod-的-gpu-用量如何查询)
- [GPU 统计设计 v1.0（归档）](../../design/archive/gpu_usage_statistics_design_v1.0.md)

### 相关代码
- `internal/dao/pod_resource_gpu_usage_dao.go` - {BUSINESS_SHORT} DAO
- `internal/model/pod_resource.go` - 数据模型
- `internal/pkgs/calculator/gpu_calculator.go` - GPU 计算器

### 数据库文档
- `docs/design/schema/gpu_usage_database_schema_v1.0.sql` - 数据库 Schema

---

## 📝 变更历史

| 版本 | 日期 | 变更内容 | 作者 |
|------|------|---------|------|
| 1.0 | 2026-02-02 | 初始版本 | Development Team |

---

**最后更新**: 2026-02-02
**维护者**: user@example.com
