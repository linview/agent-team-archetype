---
id: "EPIC-3"
title: "数据库迁移与初始化脚本"
description: "编写数据库迁移脚本，支持开发和生产环境的数据库 Schema 管理"
status: "COMPLETED"
priority: "P0"
layer: "INFRA"
owner: "user@example.com"
start_date: "2026-02-07"
target_date: "2026-02-08"
stories:
  - "STORY-3-01"
  - "STORY-3-02"
  - "STORY-3-03"  # ✅ 新增：引入 golang-migrate 自动化迁移工具
dependencies:
  - "EPIC-1"
  - "EPIC-2"
tags:
  - "database"
  - "migration"
  - "postgresql"
  - "sql"
  - "golang-migrate"  # ✅ 新增标签
version: "1.1"  # ✅ 版本号更新
created_at: "2026-01-31"
updated_at: "2026-02-04"  # ✅ 更新日期
completed_date: "2026-01-31"
implementation_summary: |
  Sprint 1 数据层基础开发已完成：
  - 7 个核心表创建成功（4 CMDB + 3 Pod 资源）
  - 数据库种子数据初始化成功（216 GPU 小时）
  - Docker Compose 环境验证通过
  - 采用 v2.3 通用化设计（支持多 Pod 类型）

  **v1.1 更新（2026-02-04）**：
  - ✅ 新增 STORY-3-03：引入 golang-migrate 数据库迁移工具
  - 目标：替代手工 SQL 迁移脚本，实现自动化版本管理
  - 预期收益：减少人为错误、版本追踪清晰、统一团队流程
---

# Epic-3: 数据库迁移与初始化脚本

## 1. 概述

### 1.1 背景

数据库 Schema 需要版本化管理，支持开发和生产环境的数据库结构演进。通过迁移脚本实现数据库的初始化、升级和回滚，确保不同环境的数据库结构一致性。

### 1.2 目标

- 设计数据库 Schema（CMDB + DevPod 相关表）
- 编写版本化迁移脚本
- 实现迁移执行工具
- 准备种子数据

### 1.3 范围

**包含**：
- CMDB 表结构设计（gpu_type, gpu_node）
- DevPod 表结构设计（example-service, example-service_usage_record）
- 迁移脚本（001, 002, ...）
- 迁移执行脚本（migrate.sh）
- 种子数据脚本

**不包含**：
- 具体业务逻辑实现
- API 接口实现

---

## 2. 需求分析

### 2.1 功能需求

| 需求 ID | 需求描述 | 优先级 |
|---------|---------|--------|
| FR-3-01 | 设计 CMDB 表结构 | P0 |
| FR-3-02 | 设计 DevPod 表结构 | P0 |
| FR-3-03 | 编写迁移 SQL 脚本 | P0 |
| FR-3-04 | 实现迁移执行脚本 | P0 |
| FR-3-05 | 准备种子数据 | P1 |

### 2.2 非功能需求

| 需求 ID | 需求描述 | 指标 |
|---------|---------|------|
| NFR-3-01 | 迁移脚本幂等性 | 可重复执行 |
| NFR-3-02 | 回滚支持 | 支持版本回滚 |
| NFR-3-03 | 跨环境兼容 | dev/prod 通用 |

### 2.3 技术约束

- **数据库**: PostgreSQL 14
- **迁移工具**: 自研 Shell 脚本
- **SQL 方言**: PostgreSQL

---

## 3. 架构设计

### 3.1 数据库 Schema 设计

#### CMDB 表

```sql
-- GPU 类型表
CREATE TABLE gpu_type (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    model VARCHAR(100),
    memory_gb INTEGER,
    compute_capability VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- GPU 节点表
CREATE TABLE gpu_node (
    id SERIAL PRIMARY KEY,
    hostname VARCHAR(100) NOT NULL UNIQUE,
    ip_address VARCHAR(50) NOT NULL,
    gpu_count INTEGER NOT NULL,
    gpu_type_id INTEGER REFERENCES gpu_type(id),
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### DevPod 表

```sql
-- DevPod 表
CREATE TABLE example-service (
    id SERIAL PRIMARY KEY,
    pod_name VARCHAR(100) NOT NULL UNIQUE,
    namespace VARCHAR(50) NOT NULL,
    worker_type VARCHAR(20) NOT NULL,
    gpu_count INTEGER NOT NULL,
    gpu_type_id INTEGER REFERENCES gpu_type(id),
    user_id INTEGER NOT NULL,
    status VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- DevPod 用量记录表
CREATE TABLE example-service_usage_record (
    id SERIAL PRIMARY KEY,
    example-service_id INTEGER REFERENCES example-service(id),
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    gpu_hours DECIMAL(10, 2),
    status VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3.2 迁移脚本目录结构

```
scripts/database/
├── migrate/
│   ├── 001_create_cmdb_tables.sql
│   ├── 002_create_example-service_tables.sql
│   └── 003_create_indexes.sql
├── seed/
│   └── 001_insert_default_data.sql
├── migrate.sh
└── init-local-db.sh
```

### 3.3 迁移执行脚本

```bash
#!/bin/bash
# migrate.sh

CONFIG_FILE=${1:-etc/config-dev.yaml}

# 从配置文件读取数据库连接
DB_HOST=$(grep "Host:" $CONFIG_FILE | awk '{print $2}')
DB_PORT=$(grep "Port:" $CONFIG_FILE | awk '{print $2}')
DB_NAME=$(grep "DBName:" $CONFIG_FILE | awk '{print $2}')
DB_USER=$(grep "Username:" $CONFIG_FILE | awk '{print $2}')

# 执行迁移脚本
for script in scripts/database/migrate/*.sql; do
    echo "Executing $script..."
    psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f $script
done
```

---

## 4. 实施计划

### 4.1 Story 列表

| Story ID | Story 标题 | 故事点 | 预估工期 |
|----------|-----------|--------|---------|
| STORY-3-01 | 迁移脚本编写 | 5 | 1 天 |
| STORY-3-02 | 种子数据准备 | 3 | 1 天 |

### 4.2 依赖关系

```
EPIC-2（Docker Compose）
    ↓
STORY-3-01（迁移脚本）
    ↓
STORY-3-02（种子数据）
```

### 4.3 里程碑

| 里程碑 | 日期 | 交付物 |
|--------|------|--------|
| M3-1 | Day 1 | 数据库 Schema 设计完成 |
| M3-2 | Day 1 | 迁移脚本完成 |
| M3-3 | Day 2 | 种子数据完成，Epic-3 完成 |

---

## 5. 风险与依赖

### 5.1 技术风险

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|---------|
| Schema 设计变更 | 高 | 中 | 预留扩展字段 |
| 迁移脚本顺序错误 | 高 | 低 | 编号管理 + 事务保护 |

### 5.2 资源依赖

| 依赖项 | 类型 | 状态 |
|--------|------|------|
| EPIC-1（脚手架） | Epic | PLANNED |
| EPIC-2（Docker Compose） | Epic | PLANNED |

### 5.3 缓解措施

- 迁移脚本使用事务保护
- 本地测试通过后再应用到生产
- 设计文档评审通过后再实施

---

## 6. 验收标准

### 6.1 功能验收

- [ ] 迁移脚本在本地环境执行成功
- [ ] 数据库 Schema 符合设计文档
- [ ] 种子数据插入成功
- [ ] 迁移脚本可重复执行

### 6.2 性能验收

- [ ] 迁移执行时间 < 10 秒

### 6.3 质量验收

- [ ] SQL 语法正确
- [ ] 索引设计合理
- [ ] 外键约束正确

---

## 7. 附录

### 7.1 参考文档

- [PostgreSQL 官方文档](https://www.postgresql.org/docs/)
- [数据库设计文档](../design/cmdb_design_v2.1.md)

### 7.2 设计文档链接

- [{BUSINESS_DESCRIPTION}服务设计文档](../design/gpu_usage_design.md)
