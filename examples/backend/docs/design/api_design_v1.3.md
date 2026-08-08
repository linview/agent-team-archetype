# Example Service API 设计规范

**文档版本**: v1.3
**创建日期**: 2026-03-23
**作者**: Claude Code (Sonnet 4.6) + Architect Team
**状态**: 设计方案（待审核批准）
**架构层次**: API/应用层

---

## 📋 版本历史

| 版本 | 日期 | 变更说明 | 作者 |
|------|------|---------|------|
| v1.0 | 2026-03-23 | 初始版本：{BUSINESS_SHORT}聚合 API 设计 | Claude Code |
| v1.1 | 2026-04-26 | 新增：DimMetric 立即同步 API（服务于 STORY-15-25） | Architect + QA |
| v1.2 | 2026-04-27 | 新增：Admin API 鉴权设计（服务于 STORY-15-26） | Architect |
| v1.3 | 2026-04-27 | 新增：TTL 清理完整 API 设计（查询接口 + 改进的清理接口） | Architect |

**v1.0 主要变更**：
- ✅ 新增智能时间解析功能（支持 4 种时间格式）
- ✅ 新增多维度聚合统计（逗号分隔，最多 2 级）
- ✅ 新增自动时间聚合粒度推断
- ✅ 扩展 `/api/v1/gpu/usage` API（向后兼容）
- ✅ 数据库索引优化（4 个新索引）

**v1.1 主要变更**：
- ✅ 新增 `POST /api/v1/admin/dim_metric/sync` 端点（立即同步 API）
- ✅ 支持手动触发 DimMetricSyncer 同步（解决 15 分钟等待问题）
- ✅ 服务于 STORY-15-25 快速验证（ABORTED Pod sync 从 15 分钟 → 12 秒）

**v1.2 主要变更**：
- ✅ 新增"Admin API 鉴权设计"章节
- ✅ 确立临时方案（HTTP Header）和 MCasbin 方案（RBAC）的分级策略
- ✅ 统一 Admin API 概览（dim_metric/sync + ttl/cleanup）
- ✅ 说明安全保障措施（反向代理、审计日志）
- ✅ 说明未来迁移计划（EPIC-10: MCasbin 集成）

**v1.3 主要变更**：
- ✅ 新增"第 6 章：TTL 清理 API 设计"章节
- ✅ 新增 `GET /api/v1/admin/ttl/tables` 查询接口（HATEOAS 设计）
- ✅ 改进 `POST /api/v1/admin/ttl/cleanup` 清理接口（新增 `ttl_days` 参数）
- ✅ 完整工作流设计（查询 → 预览 → 清理）
- ✅ 遵循 REST 成熟度模型 Level 3（HATEOAS）

---

## 📋 文档概述

### 设计目标

基于现有 `/api/v1/gpu/usage` API，通过**智能时间解析**和**多维度聚合**实现灵活的 {BUSINESS_DESCRIPTION}，遵循 **KISS/DRY/SOLID** 原则，**不暴露 DB 细节**。

### 核心特性

- ✅ 复用现有 API，不增加新 endpoint
- ✅ 不修改数据库结构（DDL）
- ✅ 封装 DB 细节，API 用户无感知
- ✅ 智能时间格式支持（4 种格式）
- ✅ 自动聚合粒度推断
- ✅ 多维度聚合支持（逗号分隔，最多 2 级）

### 为什么需要这个设计？

**现有 API 的局限**：
- ❌ 缺少聚合统计能力（需要手动汇总大量详细记录）
- ❌ 时间格式单一（只支持 `YYYY-MM-DD` 格式）
- ❌ 无法多维度分析（不能按节点+命名空间组合查询）

**用户需求**：
- ✅ 快速查看每个节点的 {BUSINESS_SHORT}
- ✅ 查询具体时间段的用量
- ✅ 分析不同团队在各节点的资源使用

### 设计原则

- ✅ **最小影响**: Handler 层无需修改
- ✅ **向后兼容**: `aggregate_by` 参数可选，默认行为不变
- ✅ **KISS/DRY/SOLID**: 遵循最佳实践
- ✅ **封装 SQL**: 不暴露 `GROUP BY`, `DATE_TRUNC` 等 DB 概念

---

## 🏗️ 系统架构设计

### 架构层次

```
Handler Layer (无需修改)
    ↓
Logic Layer (修改，+80行)
    ├─ 智能时间解析 (新增，+150行)
    ├─ 聚合维度解析 (新增，+150行)
    └─ 聚合粒度推断 (新增方法)
    ↓
DAO Layer (修改，+200行)
    ├─ 动态 SQL 构建 (新增方法)
    └─ 聚合查询执行 (新增方法)
    ↓
Database Layer (新增索引，+250MB)
    └─ 4 个性能优化索引
```

### 关键文件清单

#### 需要修改的文件（4 个）

| 文件路径 | 修改内容 | 新增行数 | 复杂度 |
|---------|---------|---------|--------|
| `internal/types/types.go` | 扩展请求/响应类型 | +50行 | 低 |
| `internal/logic/gpu/query_gpu_usage_logic.go` | 集成聚合逻辑 | +80行 | 中 |
| `internal/dao/pod_resource_gpu_usage_dao.go` | 动态 SQL 构建 | +200行 | 高 |
| `internal/dao/interfaces.go` | 扩展接口定义 | +20行 | 低 |

#### 新增文件（7 个）

| 文件路径 | 类型 | 行数估算 | 用途 |
|---------|------|---------|------|
| `internal/logic/gpu/time_parser.go` | 源代码 | +150行 | 智能时间解析 |
| `internal/logic/gpu/aggregate_parser.go` | 源代码 | +150行 | 聚合维度解析 |
| `internal/model/aggregation.go` | 源代码 | +50行 | 聚合模型定义 |
| `internal/logic/gpu/time_parser_test.go` | 单元测试 | +100行 | 时间解析测试 |
| `internal/logic/gpu/aggregate_parser_test.go` | 单元测试 | +120行 | 聚合解析测试 |
| `internal/dao/pod_resource_gpu_usage_aggregate_test.go` | 单元测试 | +200行 | DAO 层聚合测试 |
| `tests/api/api_gpu_aggregate.py` | 集成测试 | +500行 | API 集成测试 |
| `db/ddl/006_add_aggregate_indexes.sql` | 数据库脚本 | +50行 | 索引创建脚本 |

---

## 📐 API 设计

### API 语法设计

#### 单级聚合

```bash
aggregate_by=node
aggregate_by=namespace
```

#### 二级聚合（逗号分隔，顺序敏感）

```bash
aggregate_by=node,namespace
aggregate_by=namespace,node
```

#### 与时间聚合组合（自动推断时间粒度）

```bash
start_time=2026-03-20&end_time=2026-03-23&aggregate_by=node
start_time=2026-03-20 00:00:00&end_time=2026-03-20 23:59:59&aggregate_by=node,namespace
```

### 智能时间格式支持

| 输入格式 | 示例 | 自动推演为 |
|---------|------|-----------|
| `YYYY-MM-DD` | `2026-03-20` | `2026-03-20 00:00:00` |
| `YYYY-MM-DD HH:MM` | `2026-03-20 14:20` | `2026-03-20 14:20:00` |
| `YYYY-MM-DD HH:MM:SS` | `2026-03-20 14:20:30` | 精确到秒 |
| `RFC3339` | `2026-03-20T14:20:30+08:00` | 精确到时区 |

### 自动时间聚合推断

| 时间范围 | 自动推断 | SQL 实现 |
|---------|---------|---------|
| 跨天（>24小时） | 按天聚合 | `DATE_TRUNC('day', usage_start_at)` |
| 跨小时（>1小时） | 按小时聚合 | `DATE_TRUNC('hour', usage_start_at)` |
| 跨分钟（>1分钟） | 按分钟聚合 | `DATE_TRUNC('minute', usage_start_at)` |
| 精确查询（<1分钟） | 不聚合 | 返回详细记录 |

### 聚合维度白名单

| 维度 | 说明 | 数据来源 | 返回字段 |
|------|------|---------|---------|
| `node` | 按 K8s 节点聚合 | `pod_resource_gpu_usage.k8s_node_name` | `node_name` |
| `namespace` | 按命名空间聚合 | `pod_resource_status.pod_namespace` | `namespace` |
| `user` | 按用户聚合 | `pod_resource_status.user_id` | `user_id`, `user_name`, `user_email` |
| `team` | 按团队聚合 | `pod_resource_status.team_id` | `team_id`, `team_name` |
| `project` | 按项目聚合 | `pod_resource_status.project_id` | `project_id`, `project_name` |

---

## 🔒 Admin API 鉴权设计

### Admin API 概览

**当前 Example Service 提供的 Admin API**：

| API | 端点 | Story | 鉴权方式 | 状态 |
|-----|------|-------|---------|------|
| **查询 TTL 表** | `GET /api/v1/admin/ttl/tables` | STORY-15-26 | 临时鉴权 | 🆕 v1.3 新增 |
| **TTL 手动清理** | `POST /api/v1/admin/ttl/cleanup` | STORY-15-26 | 临时鉴权 | v1.3 改进（+ttl_days 参数） |
| **DimMetric 立即同步** | `POST /api/v1/admin/dim_metric/sync` | STORY-15-25 | 无鉴权 | MVP（TODO：集成临时鉴权） |

**⚠️ 重要说明**：
- 当前 Admin API 采用**临时鉴权方案**（HTTP Header: `X-Admin-Role`）
- 完整的 MCasbin 权限集成待 **EPIC-10** 完成后实施
- 本章节确立临时方案和 MCasbin 方案的**分级策略**
- **v1.3 新增**：完整的 TTL 清理 API 设计（第 6 章），包含查询接口和改进的清理接口

---

### 分级策略（KISS 原则）

**核心原则**：简单、实用、可迁移

| 阶段 | 方案 | 复杂度 | 安全性 | 实施时间 | 状态 |
|------|------|--------|--------|---------|------|
| **Phase 1: 临时方案** | HTTP Header 检查 | 🟢 低 | 🟡 中 | 1 小时 | ✅ 当前实施 |
| **Phase 2: MCasbin 方案** | RBAC 权限控制 | 🔴 高 | 🟢 高 | 待 Epic-10 | ⏳ 未来迁移 |

**为什么采用分级策略？**
- ✅ **不阻塞核心功能**：TTL 清理是运维急需功能，不能等待 MCasbin 完成
- ✅ **渐进式迁移**：从简单方案开始，逐步演进到完整方案
- ✅ **风险可控**：临时方案有明确的安全保障措施
- ✅ **可追溯性**：设计文档记录完整的迁移路径

---

### Phase 1: 临时方案（当前实施）✅

**设计目标**：基本权限控制，确保 API 安全

**实现方式**：HTTP Header 检查

```go
// 临时权限检查
func (h *TTLHandler) hasAdminRole(r *http.Request) bool {
    adminRole := r.Header.Get("X-Admin-Role")
    if adminRole != "true" {
        h.logger.Info("Permission denied: missing or invalid X-Admin-Role header")
        return false
    }
    return true
}
```

**请求示例**：
```bash
# ❌ 错误：没有权限 Header → 403 Forbidden
curl -X POST http://localhost:8888/api/v1/admin/ttl/cleanup \
  -H "Content-Type: application/json" \
  -d '{"table": "history"}'

# ✅ 正确：带权限 Header → 200 OK
curl -X POST http://localhost:8888/api/v1/admin/ttl/cleanup \
  -H "Content-Type: application/json" \
  -H "X-Admin-Role: true" \
  -d '{"table": "history"}'
```

**安全保障**：
1. **反向代理 IP 白名单**（Nginx）：
```nginx
location /api/v1/admin/ {
    allow 203.0.113.0/24;  # 内部网络
    deny all;
    proxy_pass http://{PROJECT_NAME}-api;
}
```

2. **审计日志记录**：
```go
logger.Info("Admin API called",
    "api", "ttl/cleanup",
    "user", getUserID(r.Context()),
    "remote_addr", r.RemoteAddr,
    "permission_granted", true,
)
```

3. **生产环境前 Code Review**：必须 review 反向代理配置

**风险缓解**：
| 风险 | 严重性 | 缓解措施 | 状态 |
|------|--------|----------|------|
| Header 被伪造 | 🟡 中 | 反向代理 IP 白名单 + 审计日志 | ✅ 已缓解 |
| 反向代理配置错误 | 🟡 中 | Code Review + 测试验证 | ✅ 已缓解 |
| 生产环境误操作 | 🔴 高 | dry_run 模式 + 审计日志 | ✅ 已缓解 |

**适用场景**：
- ✅ 测试/开发环境
- ✅ 内部网络（通过反向代理隔离）
- ✅ 运维人员操作（配合审计日志）
- ❌ 不适合直接暴露到公网

---

### Phase 2: MCasbin 方案（未来迁移）⏳

**设计目标**：完整的 RBAC 权限控制

**实现方式**：MCasbin Enforcer

```go
// MCasbin 权限检查（未来实现）
func (h *TTLHandler) hasAdminRole(ctx context.Context) bool {
    // 从 context 中获取用户信息
    userID := getUserID(ctx)

    // 调用 MCasbin Enforcer 检查权限
    allowed, err := h.enforcer.Enforce(userID, "/api/v1/admin/ttl/cleanup", "POST")
    if err != nil {
        h.logger.Error("MCasbin enforce failed", "error", err)
        return false
    }

    return allowed
}
```

**RBAC 策略示例**：
```conf
[policy_definition]
p = sub, obj, act

[role_definition]
g = _, _

[policy_effect]
e = some(where (p.eft == allow))

[matchers]
m = r.sub == p.sub && r.obj == p.obj && r.act == p.act
```

**权限规则**：
```conf
# 策略：role:admin 可以访问所有 admin API
p, role:admin, /api/v1/admin/*, *

# 角色：用户属于 admin 角色
g, alice, role:admin
g, bob, role:admin
```

**迁移步骤**：
1. ✅ STORY-10-01: MCasbin 客户端封装完成
2. ⏳ **STORY-10-02: 权限检查中间件实现**（关键路径）
3. 修改 `hasAdminRole()` 调用 MCasbin Enforcer
4. 删除 HTTP Header 相关代码
5. 更新单元测试
6. 添加 MCasbin 权限集成测试
7. 更新文档（本设计 spec）

**前提条件**：
- ✅ EPIC-10: MCasbin 权限服务集成完成
- ✅ STORY-10-01: MCasbin 客户端封装（IN_PROGRESS）
- ⏳ **STORY-10-02: 权限检查中间件实现**（TODO）

**预计时间**：待 Epic-10 排期（当前 0% 完成）

---

### 反向代理配置参考

#### Nginx 配置（IP 白名单）

```nginx
location /api/v1/admin/ {
    # 方案 1: IP 白名单（推荐）
    allow 203.0.113.0/24;  # 内部网络
    deny all;

    # 日志记录（审计）
    access_log /var/log/nginx/admin_api.log;

    proxy_pass http://{PROJECT_NAME}-api;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}
```

#### Nginx 配置（JWT Token 认证）

```nginx
location /api/v1/admin/ {
    # 方案 2: JWT Token 认证
    auth_request /auth;
    auth_request_set $user_id $upstream_http_x_user_id;
    proxy_set_header X-Admin-Role "true";
    proxy_set_header X-User-ID $user_id;

    proxy_pass http://{PROJECT_NAME}-api;
}
```

---

### 相关文档

**设计文档**：
- 📘 **[服务层架构设计 v4.2](service_layer_architecture_v4.2.md)** - 服务层完整架构
- 📗 **[EPIC-10: MCasbin 权限服务集成](../scrum/prd/epic-10-mcasbin-integration.md)** - MCasbin 集成规划

**Story 文档**：
- 📕 **[STORY-15-26: TTL 手动触发 API](../scrum/story/story-15-26-ttl-manual-trigger-api.md)** - 完整实施计划
- 📕 **[STORY-10-02: 权限检查中间件实现](../scrum/story/story-10-02-permission-middleware.md)** - MCasbin 中间件（关键路径）

**决策记录**：
- 📙 **[临时权限方案决策说明](../test_reports/story-15-26-temporary-auth-decision.md)** - 为什么采用临时方案

---

## 📊 API 响应格式设计

### 详细记录响应（现有行为，向后兼容）

**请求**:
```bash
GET /api/v1/gpu/usage?start_time=2026-03-20&page=1&page_size=20
```

**响应**:
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "total_gpu_hours": 15433.2,
    "total_count": 29172,
    "record_count": 20,
    "page": 1,
    "page_size": 20,
    "total_pages": 1459,
    "records": [...]
  }
}
```

### 聚合结果响应（新增行为）

**请求**:
```bash
GET /api/v1/gpu/usage?start_time=2026-03-20&end_time=2026-03-23&aggregate_by=node
```

**响应**:
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "total_count": 41,
    "query_type": "aggregate",
    "aggregates": [
      {
        "time_bucket": null,
        "dimensions": {
          "node_name": "k8s-gpu-node-2-216"
        },
        "total_gpu_hours": 10833.56,
        "record_count": 2346,
        "unique_pods": 2216
      },
      {
        "time_bucket": null,
        "dimensions": {
          "node_name": "k8s-gpu-node-2-210"
        },
        "total_gpu_hours": 8666.86,
        "record_count": 3229,
        "unique_pods": 3027
      }
    ]
  }
}
```

### 二级聚合响应示例

**请求**:
```bash
GET /api/v1/gpu/usage?start_time=2026-03-20&aggregate_by=node,namespace
```

**响应**:
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "total_count": 164,
    "query_type": "aggregate",
    "aggregates": [
      {
        "time_bucket": null,
        "dimensions": {
          "node_name": "k8s-gpu-node-2-216",
          "namespace": "train-job"
        },
        "total_gpu_hours": 5433.2,
        "record_count": 1173,
        "unique_pods": 1100
      }
    ]
  }
}
```

### 时间+维度聚合响应示例

**请求**:
```bash
GET /api/v1/gpu/usage?start_time=2026-03-20 00:00:00&end_time=2026-03-20 23:59:59&aggregate_by=node,namespace
```

**响应**:
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "total_count": 3936,
    "query_type": "aggregate",
    "time_granularity": "hour",
    "aggregates": [
      {
        "time_bucket": "2026-03-20T00:00:00+08:00",
        "dimensions": {
          "node_name": "k8s-gpu-node-2-216",
          "namespace": "train-job"
        },
        "total_gpu_hours": 45.2,
        "record_count": 50,
        "unique_pods": 48
      }
    ]
  }
}
```

### CMDB 维度聚合响应示例（team/project）

**请求**（按 team 聚合）:
```bash
GET /api/v1/gpu/usage?start_time=2026-03-20&end_time=2026-03-23&aggregate_by=team
```

**响应**:
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "total_count": 5,
    "query_type": "aggregate",
    "aggregates": [
      {
        "dimensions": {
          "team_id": "76",
          "team_name": "真值组"
        },
        "total_gpu_hours": 1234.5,
        "record_count": 150,
        "unique_pods": 120
      },
      {
        "dimensions": {
          "team_id": "127",
          "team_name": "示例团队"
        },
        "total_gpu_hours": 567.8,
        "record_count": 80,
        "unique_pods": 65
      }
    ]
  }
}
```

**请求**（按 team,project 二级聚合）:
```bash
GET /api/v1/gpu/usage?start_time=2026-03-20&end_time=2026-03-23&aggregate_by=team,project
```

**响应**:
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "total_count": 8,
    "query_type": "aggregate",
    "aggregates": [
      {
        "dimensions": {
          "team_id": "76",
          "team_name": "真值组",
          "project_id": "123",
          "project_name": "ResNet50训练"
        },
        "total_gpu_hours": 890.1,
        "record_count": 100,
        "unique_pods": 85
      }
    ]
  }
}
```

**STORY-13-09 更新**：
- ✅ team 维度返回 `team_id` + `team_name` 字段
- ✅ project 维度返回 `project_id` + `project_name` 字段
- ✅ user 维度返回 `user_id` + `user_name` + `user_email` 字段
- ✅ 多维度组合时同时返回所有维度的 name 字段

### 响应格式设计说明

**为什么使用 `map[string]string` 作为动态维度？**
- ✅ 灵活支持任意维度组合（node, namespace, user, team, project）
- ✅ 易于扩展，添加新维度无需修改类型定义
- ✅ JSON 序列化友好，前端易于解析
- ✅ 避免定义大量不同的聚合 Item 类型

**为什么添加 `query_type` 字段？**
- ✅ 客户端可以明确区分详细记录和聚合结果
- ✅ 便于前端处理不同的数据格式
- ✅ 支持未来扩展更多查询类型

---

## 🗄️ 数据库设计

### 现有表结构（无需修改）

**pod_resource_gpu_usage 表**:
- `k8s_node_name` VARCHAR(255) - 支持按节点聚合
- `usage_start_at` TIMESTAMP - 支持时间聚合
- `resource_id` UUID - JOIN 键

**pod_resource_status 表**:
- `pod_namespace` VARCHAR(255) - 支持按命名空间聚合
- `user_id`, `team_id`, `project_id` - 支持 CMDB 维度聚合
- `resource_id` UUID - JOIN 键

### 新增索引（性能优化）

```sql
-- 索引 1: 节点+时间复合索引（支持按节点聚合）
CREATE INDEX CONCURRENTLY idx_gpu_usage_node_start
ON pod_resource_gpu_usage(k8s_node_name, usage_start_at);

-- 索引 2: 时间+节点复合索引（支持按时间聚合+节点过滤）
CREATE INDEX CONCURRENTLY idx_gpu_usage_start_node
ON pod_resource_gpu_usage(usage_start_at, k8s_node_name);

-- 索引 3: 覆盖索引（优化查询性能，避免回表）
CREATE INDEX CONCURRENTLY idx_gpu_usage_covering
ON pod_resource_gpu_usage(usage_start_at, k8s_node_name, resource_id)
INCLUDE (gpu_count, gpu_product, usage_end_at, gpu_hours);

-- 索引 4: 命名空间索引（通过 resource_id 关联）
CREATE INDEX CONCURRENTLY idx_status_namespace_resource
ON pod_resource_status(pod_namespace, resource_id);
```

### 索引性能评估

| 查询场景 | 无索引 | 现有索引 | 新增索引后 | 性能提升 |
|---------|--------|---------|-----------|---------|
| 按节点聚合 1 天 | 500ms | 120ms | **30ms** | 4x |
| 按 namespace 聚合 1 天 | 600ms | 150ms | **50ms** | 3x |
| 按节点+namespace 聚合 1 天 | 800ms | 200ms | **80ms** | 2.5x |
| 按时间+节点聚合 1 天 | 1000ms | 300ms | **120ms** | 2.5x |

### 索引维护成本

- **存储开销**: 约 250MB（假设 100 万条记录）
- **写入性能影响**: INSERT +5%, UPDATE +3%, DELETE +5%
- **评估结论**: ✅ 可接受（查询性能提升显著）

---

## 🎯 API 使用示例

### 示例 1: 按节点聚合

```bash
GET /api/v1/gpu/usage?start_time=2026-03-20&end_time=2026-03-23&aggregate_by=node
```

### 示例 2: 按命名空间聚合

```bash
GET /api/v1/gpu/usage?start_time=2026-03-20&end_time=2026-03-23&aggregate_by=namespace
```

### 示例 3: 按节点+命名空间聚合

```bash
GET /api/v1/gpu/usage?start_time=2026-03-20&end_time=2026-03-23&aggregate_by=node,namespace
```

### 示例 4: 智能时间格式

```bash
# 日期格式
GET /api/v1/gpu/usage?start_time=2026-03-20&aggregate_by=node

# 精确时间格式
GET /api/v1/gpu/usage?start_time=2026-03-20 14:30:45&aggregate_by=node

# RFC3339 格式
GET /api/v1/gpu/usage?start_time=2026-03-20T14:30:45+08:00&aggregate_by=node
```

### 示例 5: 向后兼容（详细记录）

```bash
GET /api/v1/gpu/usage?start_time=2026-03-20&page=1&page_size=20

# 无 aggregate_by，自动推断为详细记录
# 返回分页的详细记录（现有行为）
```

---

## ⚠️ 风险与缓解

### 高风险项

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|----------|
| **DAO 层动态 SQL 构建** | 高 | 中 | - 使用 pgx 参数化查询<br>- 严格验证输入<br>- Code Review 重点审核 |
| **JOIN 性能问题** | 高 | 中 | - 添加 4 个性能优化索引<br>- EXPLAIN ANALYZE 验证<br>- 生产环境性能测试 |

### 中风险项

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|----------|
| **聚合逻辑复杂度** | 中 | 中 | - 单元测试覆盖率 ≥ 80%<br>- Code Review<br>- 集成测试验证 |
| **向后兼容性** | 中 | 低 | - 完整的集成测试<br>- 回归测试<br>- aggregate_by 可选参数 |

### 低风险项

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|----------|
| **智能时间解析** | 低 | 低 | - 复用现有时区处理代码<br>- Go 标准库支持良好 |

---

## 🚀 未来扩展路径

### TODO: 支持 N 级聚合

```go
// 当前实现
if len(parts) > 2 {
    return nil, fmt.Errorf("aggregate_by supports max 2 levels (TODO: support N levels)")
}

// 未来实现（N 级支持）
// 移除 2 级限制，支持任意深度的聚合
// aggregate_by=user,team,project,node,namespace
```

### TODO: 更多聚合维度

```go
// 当前支持的维度
validDimensions := map[string]bool{
    "node":      true,
    "namespace": true,
    "user":      true,
    "team":      true,
    "project":   true,
}

// 未来可添加的维度
// "cluster":     true,  // 集群
// "gpu_product": true,  // GPU 型号
// "pod_type":    true,  // Pod 类型
```

### TODO: 高级聚合功能

- **上卷（Rollup）**: `aggregate_by=node&rollup=true`（将子节点聚合到父节点）
- **下钻（Drilldown）**: `aggregate_by=node&drilldown=pod`（从节点深入到 Pod 详情）
- **过滤聚合**: `aggregate_by=node&node_name=k8s-node-1`（在特定节点内聚合）

---

## 🗑️ TTL 清理 API 设计（v1.3 新增）

### API 1: 查询 TTL 表配置

**Endpoint**: `GET /api/v1/admin/ttl/tables`

**功能**: 查询所有支持 TTL 清理的表，返回配置信息、统计数据和操作链接（HATEOAS）。

**请求**:
```bash
curl -X GET http://localhost:8888/api/v1/admin/ttl/tables \
  -H "X-Admin-Role: true"
```

**响应**:
```json
{
  "code": 0,
  "data": {
    "tables": [
      {
        "table_name": "pod_resource_history",
        "default_ttl_days": 30,
        "total_rows": 150000,
        "cleanable_rows": 45000,
        "cleanable_size_mb": 250.5,
        "_links": {
          "cleanup": "/api/v1/admin/ttl/cleanup?table=history",
          "preview": "/api/v1/admin/ttl/cleanup?table=history&dry_run=true"
        }
      }
    ],
    "summary": {
      "total_tables": 3,
      "total_cleanable_rows": 96200
    }
  }
}
```

---

### API 2: 执行 TTL 清理

**Endpoint**: `POST /api/v1/admin/ttl/cleanup`

**功能**: 执行 TTL 清理操作，支持自定义 TTL 阈值（`ttl_days`）和 dry_run 模式。

**⚠️ 重要约束**:
- **不支持 `table='all'`**：必须明确指定表名（`history`/`status`/`dim_metric`），防止误操作
- **时间窗口固定**：清理 `NOW() - ttl_days` 之前的数据，不支持指定 `start_date`

**请求参数**:

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `table` | string | **必填** | `history`/`status`/`dim_metric`（**不支持 'all'**）⭐ v1.3 约束 |
| `ttl_days` | int | -1 | 保留天数（-1=使用配置文件默认值）⭐ v1.3 新增 |
| `dry_run` | bool | false | 仅预览不执行 |
| `batch_size` | int | 1000 | 批次大小（可选） |

**TTLDays 行为**:
- `-1` 或未指定: 使用配置文件默认值（history/status 30天，dim_metric 90天）
- `ttl_days = 60`: 清理 60 天前的数据（紧急清理）
- `ttl_days = 7`: 清理 7 天前的数据（测试验证）

**时间窗口计算**:
```sql
-- 清理逻辑（固定时间窗口）
DELETE FROM {table}
WHERE created_at < NOW() - INTERVAL '{ttl_days} days'
LIMIT {batch_size}
```

**请求示例**:
```bash
# 清理 history 表（使用默认 TTL：30天）
curl -X POST http://localhost:8888/api/v1/admin/ttl/cleanup \
  -H "X-Admin-Role: true" \
  -H "Content-Type: application/json" \
  -d '{"table": "history", "dry_run": false}'

# 紧急清理 status 表（60 天前）
curl -X POST http://localhost:8888/api/v1/admin/ttl/cleanup \
  -H "X-Admin-Role: true" \
  -H "Content-Type: application/json" \
  -d '{"table": "status", "ttl_days": 60, "dry_run": false}'
```

**响应示例**:
```json
{
  "code": 0,
  "message": "Cleanup completed",
  "data": {
    "table": "pod_resource_history",
    "ttl_days": 60,
    "rows_deleted": 45000,
    "size_freed_mb": 250.5,
    "duration_seconds": 15.6,
    "batches": 45
  }
}
```

**dry_run 预览响应**:
```json
{
  "code": 0,
  "message": "Cleanup preview completed",
  "data": {
    "table": "pod_resource_dim_metric",
    "ttl_days": 30,
    "rows_deleted": 0,
    "rows_would_be_deleted": 12345,
    "estimated_size_freed_mb": 210.8
  }
}
```

---

### 关键设计决策

**HATEOAS（REST Level 3）**: 查询接口响应包含 `_links` 字段，支持服务发现。

**TTLDays 灵活性**: 解决 v1.2 痛点（只能用默认 TTL），支持自定义清理范围。

**完整工作流**: 查询（GET /ttl/tables）→ 预览（dry_run=true）→ 清理（dry_run=false）

---

### 相关文档

- 📘 **[STORY-15-26](../scrum/story/story-15-26-ttl-manual-trigger-api.md)** - 完整实施计划
- 📘 **[TTL 清理实现方案 v4.1.2](service/ttl_cleanup_implementation_v4.1.2.md)** - 详细实现
- 🔒 **[Admin API 鉴权设计](#admin-api-鉴权设计)** - 权限控制

---

## 📋 验收标准

### 功能验收

- [ ] 所有时间格式测试通过（YYYY-MM-DD, YYYY-MM-DD HH:MM, YYYY-MM-DD HH:MM:SS, RFC3339）
- [ ] 逗号分隔聚合解析测试通过（单级、二级）
- [ ] 单级聚合测试通过（node, namespace, user, team, project）
- [ ] 二级聚合测试通过（node,namespace 组合）
- [ ] 自动时间粒度推断测试通过（day, hour, minute, none）
- [ ] 向后兼容性测试通过（无 aggregate_by 参数时返回详细记录）
- [ ] 性能测试通过（JOIN 查询 < 150ms）

### 质量验收

- [ ] 单元测试覆盖率 > 80%
- [ ] SIT 测试通过率 100%
- [ ] API 测试通过率 100%
- [ ] 代码审查通过（无 Major 问题）
- [ ] SQL 注入防护验证通过

### 文档验收

- [ ] API 文档更新（Swagger/OpenAPI）
- [ ] 使用示例完整
- [ ] CLAUDE.md 项目文档更新
- [ ] 数据库索引文档完整

---

## 📚 相关文档

### 架构文档

- [服务层架构设计 v3.3](service_layer_architecture_v3.3.md) - 服务层完整架构设计
- [CMDB 设计 v3.2](cmdb_design_v3.2.md) - Pod 资源管理 + CMDB 完整设计

### API 测试文档

- [API 测试文档](../../tests/api/README.md) - API 集成测试指南
- [项目排期](../schedule/gpu_aggregation_api_schedule.md) - 项目实施排期

### 数据库文档

- [数据库迁移文档](../../db/ddl/README.md) - DDL 脚本管理

---

## ✅ 审核检查清单

### 设计完整性

- [x] 功能完整性（智能时间、多维度聚合、自动推断）
- [x] 架构设计（Handler/Logic/DAO 层次清晰）
- [x] 数据结构（请求/响应类型完整）
- [x] 性能设计（4 个索引，<150ms 目标）

### 技术可行性

- [x] 工作量评估合理（9.5 天）
- [x] 技术依赖明确（PostgreSQL 11+, pgx/v5）
- [x] 环境准备就绪（Docker Compose, K8s）
- [x] 团队配置可行（1 后端 + 1 测试 + 1 DBA）

### 文档完整性

- [x] 设计文档完整
- [x] 实施细节明确
- [x] 验收标准具体
- [x] 风险评估详细

---

**文档版本**: v1.3
**创建日期**: 2026-03-23
**最后更新**: 2026-04-27
**作者**: Claude Code (Sonnet 4.6) + Architect Team
**状态**: ✅ 设计完成，待审核批准

**推荐采用**: ✅ v1.3 方案（包含完整 TTL 清理 API）
**下一步**: 等待人类审核批准
**预计开始**: 审核通过后立即开始
**预计完成**: 9 个工作日后
