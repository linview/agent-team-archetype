---
id: "EPIC-1"
title: "项目脚手架搭建（Go-Zero + 多环境配置）"
description: "创建 Go-Zero 项目脚手架，配置多环境文件结构，建立基础构建系统"
status: "COMPLETED"
priority: "P0"
layer: "INFRA"
owner: "dev1@example.com"
start_date: "2026-01-31"
target_date: "2026-02-04"
stories:
  - "STORY-1-01"
  - "STORY-1-02"
  - "STORY-1-03"
dependencies: []
tags:
  - "scaffolding"
  - "go-zero"
  - "multi-env"
version: "1.0"
created_at: "2026-01-31"
updated_at: "2026-01-31"
completed_date: "2026-01-31"
implementation_summary: |
  Epic-1 项目脚手架搭建已完成：
  - goctl 项目脚手架生成完成
  - 多环境配置文件实现完成（config.yaml, config_dev.yaml, config_prod.yaml）
  - Makefile 构建系统实现完成（10+ 目标）
  - GitLab CI/CD Pipeline 配置完成
  - 项目结构符合 go-zero 最佳实践
---

# Epic-1: 项目脚手架搭建

## 1. 概述

### 1.1 背景

{BUSINESS_DESCRIPTION}服务是一个全新的 Go-Zero 微服务项目，需要从零搭建完整的工程化基础设施。参考 example-service 项目的成功经验，本服务需要建立标准的项目脚手架，包括代码生成、配置管理、构建系统等基础能力。

### 1.2 目标

- 使用 goctl 工具生成 Go-Zero 项目脚手架
- 建立多环境配置管理机制（开发/生产环境分离）
- 配置 Makefile 构建系统
- 配置 GitLab CI/CD Pipeline

### 1.3 范围

**包含**：
- Go-Zero 项目脚手架生成
- API 定义文件（.api）
- 配置结构体生成
- 多环境配置文件
- Makefile 构建脚本
- .gitlab-ci.yml CI/CD 配置

**不包含**：
- 具体业务逻辑实现
- 数据库 Schema 设计
- K8s 部署配置

---

## 2. 需求分析

### 2.1 功能需求

| 需求 ID | 需求描述 | 优先级 |
|---------|---------|--------|
| FR-1-01 | 使用 goctl 生成 Go-Zero 项目结构 | P0 |
| FR-1-02 | 定义 RESTful API 接口 | P0 |
| FR-1-03 | 生成配置结构体代码 | P0 |
| FR-1-04 | 创建多环境配置文件（dev/prod） | P0 |
| FR-1-05 | 编写 Makefile 构建脚本 | P0 |
| FR-1-06 | 配置 GitLab CI/CD Pipeline | P0 |

### 2.2 非功能需求

| 需求 ID | 需求描述 | 指标 |
|---------|---------|------|
| NFR-1-01 | 兼容 example-service 项目构建规范 | 100% 兼容 |
| NFR-1-02 | 本地构建时间 < 30 秒 | < 30s |
| NFR-1-03 | 环境配置切换无需修改代码 | 环境变量控制 |

### 2.3 技术约束

- **框架**: Go-Zero v1.8.3
- **Go 版本**: 1.24.2
- **构建工具**: make, goctl
- **配置格式**: YAML
- **CI/CD**: GitLab CI

---

## 3. 架构设计

### 3.1 目录结构

```
{PROJECT_NAME}/
├── cmd/                            # 入口文件
│   └── api/
│       └── {PROJECT_NAME}.go      # API 服务入口
├── internal/                       # 内部代码
│   ├── config/                     # 配置结构体
│   │   └── config.go               # goctl 生成
│   ├── handler/                    # HTTP 处理器
│   ├── logic/                      # 业务逻辑
│   ├── svc/                        # 服务上下文
│   │   └── service_context.go      # 服务上下文初始化
│   ├── types/                      # 类型定义
│   └── middleware/                 # 中间件
├── etc/                            # 配置文件
│   ├── config.yaml                 # 基础配置模板
│   ├── config-dev.yaml             # 开发环境配置
│   └── config-prod.yaml            # 生产环境配置
├── desc/                           # API 定义
│   └── {PROJECT_NAME}.api         # API 定义文件
├── Dockerfile                      # Dockerfile
├── Makefile                        # 构建脚本
├── .gitlab-ci.yml                  # CI/CD Pipeline
├── go.mod                          # Go 模块
└── README.md                       # 项目说明
```

### 3.2 多环境配置策略

**配置文件分层**：

```yaml
# config.yaml（基础配置，由 goctl 生成）
Name: GpuUsageStats.api
Host: 0.0.0.0
Port: 8082
Timeout: 200000

# config-dev.yaml（开发环境覆盖）
DatabaseConf:
  Host: localhost
  Port: 5432

# config-prod.yaml（生产环境覆盖）
DatabaseConf:
  Host: api.example.internal
  Port: 31532
```

**环境变量控制**：

```bash
# 本地开发
export CONFIG_FILE=config-dev.yaml

# 生产环境
export CONFIG_FILE=config-prod.yaml
```

### 3.3 技术选型

| 组件 | 技术选型 | 版本 | 说明 |
|------|---------|------|------|
| 框架 | go-zero | v1.8.3 | 微服务框架 |
| API 工具 | goctl | latest | 代码生成工具 |
| 构建 | make | - | 构建自动化 |
| CI/CD | GitLab CI | - | 持续集成 |

---

## 4. 实施计划

### 4.1 Story 列表

| Story ID | Story 标题 | 故事点 | 预估工期 |
|----------|-----------|--------|---------|
| STORY-1-01 | 使用 goctl 创建项目脚手架 | 3 | 1 天 |
| STORY-1-02 | 多环境配置文件结构 | 2 | 0.5 天 |
| STORY-1-03 | Makefile 和 .gitlab-ci.yml | 5 | 1.5 天 |

### 4.2 依赖关系

```
STORY-1-01（脚手架）
    ↓
STORY-1-02（配置） ←→ STORY-1-03（构建系统）
```

### 4.3 里程碑

| 里程碑 | 日期 | 交付物 |
|--------|------|--------|
| M1-1 | Day 1 | 项目脚手架完成 |
| M1-2 | Day 2 | 配置系统完成 |
| M1-3 | Day 3 | 构建系统完成，Epic-1 完成 |

---

## 5. 风险与依赖

### 5.1 技术风险

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|---------|
| goctl 版本兼容性问题 | 高 | 低 | 使用与 example-service 相同版本 |
| 配置文件结构设计不合理 | 中 | 中 | 参考 example-service 项目配置 |

### 5.2 资源依赖

| 依赖项 | 类型 | 状态 |
|--------|------|------|
| example-service 项目 Makefile | 参考 | 已完成 |
| example-service 项目 .gitlab-ci.yml | 参考 | 已完成 |

### 5.3 缓解措施

- 提前验证 goctl 版本兼容性
- 配置文件设计与 example-service 保持一致
- Makefile 目标与 example-service 保持一致

---

## 6. 验收标准

### 6.1 功能验收

- [ ] `make gen-api` 生成代码成功
- [ ] `make build-linux` 编译成功
- [ ] `make docker` 构建镜像成功
- [ ] 服务启动成功，健康检查通过

### 6.2 性能验收

- [ ] 本地构建时间 < 30 秒
- [ ] Docker 镜像构建 < 2 分钟

### 6.3 质量验收

- [ ] 代码符合 Go-Zero 规范
- [ ] 配置文件格式正确
- [ ] Makefile 与 example-service 项目风格一致

---

## 7. 附录

### 7.1 参考文档

- [Go-Zero 官方文档](https://go-zero.dev/)
- [sample_service 项目](https://git.example.com/example-org/sample_service)
- [CLAUDE.md](../CLAUDE.md)

### 7.2 设计文档链接

- [{BUSINESS_DESCRIPTION}服务设计文档](../design/gpu_usage_design.md)
