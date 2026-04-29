---
id: "STORY-1-01"
epic_id: "EPIC-1"
title: "使用 goctl 创建项目脚手架"
description: "使用 goctl 工具生成 Go-Zero 项目脚手架，包括 API 定义和基础代码结构"
status: "COMPLETED"
completed_date: "2026-04-21"
priority: "P0"
story_points: 3
assignee: "user@example.com"
reviewer: "user@example.com"
start_date: "2026-01-31"
target_date: "2026-01-31"
dependencies: []
tags:
  - "scaffolding"
  - "goctl"
  - "go-zero"
acceptance_criteria:
  - "goctl 生成项目结构完整"
  - "API 定义文件创建"
  - "配置结构体代码生成"
  - "服务可正常启动"
definition_of_done:
  - "项目脚手架生成成功"
  - "API 定义文件编写完成"
  - "配置结构体生成"
  - "本地启动测试通过"
version: "1.1"
created_at: "2026-01-31"
updated_at: "2026-04-21"
---

# Story-1-01: 使用 goctl 创建项目脚手架

## 1. 用户故事

### 1.1 作为 [开发者]
我想要 [使用 goctl 工具生成 Go-Zero 项目脚手架]

### 1.2 我想要 [定义 RESTful API 接口]

### 1.3 以便于 [快速启动项目开发]

---

## 2. 任务描述

### 2.1 背景

{BUSINESS_DESCRIPTION}服务是一个全新的 Go-Zero 微服务项目。使用 goctl 工具可以快速生成标准的项目结构，包括 Handler、Logic、Types 等代码。

### 2.2 目标

- 使用 goctl 生成 Go-Zero 项目结构
- 定义 RESTful API 接口
- 生成配置结构体代码
- 验证服务可正常启动

### 2.3 范围

**包含**：
- 创建项目目录结构
- 编写 API 定义文件
- 生成 Handler/Logic/Types 代码
- 配置结构体生成

**不包含**：
- 具体业务逻辑实现
- 数据库连接配置

---

## 3. 技术设计

### 3.1 项目目录结构

```
{PROJECT_NAME}/
├── cmd/
│   └── api/
│       └── {PROJECT_NAME}.go      # API 服务入口
├── internal/
│   ├── config/
│   │   └── config.go               # 配置结构体
│   ├── handler/                    # HTTP 处理器
│   │   ├── routes.go               # 路由注册
│   │   └── usagequeryhandler.go    # 用量查询处理器
│   ├── logic/                      # 业务逻辑
│   │   └── usagequerylogic.go      # 用量查询逻辑
│   ├── svc/                        # 服务上下文
│   │   └── service_context.go      # 服务上下文初始化
│   ├── types/                      # 类型定义
│   │   └── types.go                # API 请求/响应类型
│   └── middleware/                 # 中间件
├── etc/
│   └── {PROJECT_NAME}.yaml        # 配置文件
├── desc/
│   └── {PROJECT_NAME}.api         # API 定义文件
├── {PROJECT_NAME}.go              # 主入口
├── go.mod
├── go.sum
└── README.md
```

### 3.2 API 定义文件

```api
// desc/{PROJECT_NAME}.api

syntax = "v1"

info(
    title: "{BUSINESS_DESCRIPTION}服务"
    desc: "{BUSINESS_DESCRIPTION}与查询 API"
    author: "user@example.com"
    version: "v1.0"
)

import "base.api"

type (
    // 健康检查响应
    HealthCheckResponse {
        Status  string `json:"status"`
        Version string `json:"version"`
    }
)

@server(
    prefix: /api/v1
    group:   health
)
service {PROJECT_NAME} {
    @doc "健康检查"
    @handler healthz
    get /healthz returns (HealthCheckResponse)
}
```

### 3.3 配置结构体

```go
// internal/config/config.go

package config

import "github.com/zeromicro/go-zero/zrpc"

type Config struct {
    Rest      RestConf            `json:",optional"`
    RedisConf RedisConf           `json:",optional"`
    DatabaseConf DatabaseConf     `json:",optional"`
}

type RestConf struct {
    Host    string `json:",default=0.0.0.0"`
    Port    int    `json:",default=8082"`
    Timeout int    `json:",default=200000"`
}

type RedisConf struct {
    Host string
    Pass string
    DB   int `json:",default=0"`
}

type DatabaseConf struct {
    Type     string `json:",default=postgres"`
    Host     string
    Port     int
    DBName   string
    Username string
    Password string
}
```

### 3.4 伪代码/代码框架

```bash
# 1. 初始化 Go 模块
go mod init {PROJECT_NAME}

# 2. 生成 API 服务
goctl api go \
  --api ./desc/{PROJECT_NAME}.api \
  --dir ./ \
  --style=go_zero

# 3. 生成配置结构体
goctl config convert --etc etc/{PROJECT_NAME}.yaml --go internal/config/config.go
```

---

## 4. 实施步骤

### 4.1 步骤 1: 创建项目目录

```bash
mkdir -p {PROJECT_NAME}/{cmd/api,internal/{config,handler,logic,svc,types,middleware},etc,desc}
cd {PROJECT_NAME}
```

### 4.2 步骤 2: 编写 API 定义文件

创建 `desc/{PROJECT_NAME}.api`，定义基础接口：
- 健康检查接口
- 用量查询接口（预留）

### 4.3 步骤 3: 生成项目代码

使用 goctl 生成项目代码：
```bash
goctl api go --api ./desc/{PROJECT_NAME}.api --dir ./ --style=go_zero
```

### 4.4 步骤 4: 生成配置结构体

```bash
goctl config convert --etc etc/{PROJECT_NAME}.yaml --go internal/config/config.go
```

### 4.5 步骤 5: 初始化 Go 模块

```bash
go mod init {PROJECT_NAME}
go mod tidy
```

### 4.6 步骤 6: 验证服务启动

```bash
go run {PROJECT_NAME}.go -f etc/{PROJECT_NAME}.yaml
```

测试健康检查接口：
```bash
curl http://localhost:8082/api/v1/health/healthz
```

---

## 5. 测试计划

### 5.1 单元测试

- [x] 配置加载测试
- [x] 健康检查接口测试

### 5.2 集成测试

- [x] 服务启动测试
- [x] API 调用测试

### 5.3 手动测试

- [x] 验证项目结构完整性
- [x] 验证配置文件正确性

---

## 6. 验收标准

### 6.1 功能验收

- [x] 项目目录结构符合 Go-Zero 规范
- [x] API 定义文件创建成功 (`desc/{PROJECT_NAME}.api`)
- [x] 配置结构体生成成功 (`internal/config/config.go`)
- [x] 服务可正常启动 (`{PROJECT_NAME}.go`)
- [x] 健康检查接口可正常访问 (`/api/v1/health/healthz`)

### 6.2 性能验收

- [x] 服务启动时间 < 5 秒
- [x] 健康检查响应时间 < 100ms

### 6.3 质量验收

- [x] 代码符合 Go-Zero 规范
- [x] go.mod 依赖完整
- [x] README.md 包含项目说明

---

## 7. 完成定义（DoD）

### 7.1 代码要求

- [x] 代码已提交到 Git 仓库
- [x] 代码符合 Go-Zero 规范
- [x] 没有 TODO 或 FIXME

### 7.2 测试要求

- [x] 健康检查接口测试通过
- [x] 服务启动测试通过

### 7.3 文档要求

- [x] API 定义文件已创建
- [x] README.md 包含项目说明和启动方法

### 7.4 部署要求

- [x] 本地环境可正常运行
- [x] 健康检查接口可访问

---

## 10. 实施总结

### 完成情况

✅ **已完成** - 2026-01-31

**实施内容**:
1. 使用 goctl 生成 Go-Zero 项目脚手架
2. 创建 API 定义文件 `desc/{PROJECT_NAME}.api`
3. 生成配置结构体 `internal/config/config.go`
4. 实现健康检查接口 `/api/v1/health/healthz`
5. 服务可正常启动并响应请求

**测试结果**:
- ✅ 项目目录结构符合 Go-Zero 规范
- ✅ 服务启动成功，监听端口 8082
- ✅ 健康检查接口响应正常
- ✅ 配置加载功能正常

**实现文件**:
- `{PROJECT_NAME}.go` - 主入口文件
- `desc/{PROJECT_NAME}.api` - API 定义文件
- `internal/config/config.go` - 配置结构体
- `internal/handler/routes.go` - 路由注册
- `internal/handler/healthzhandler.go` - 健康检查处理器
- `internal/logic/healthzlogic.go` - 健康检查逻辑
- `internal/svc/service_context.go` - 服务上下文
- `internal/types/types.go` - 类型定义

---

## 8. 风险与依赖

### 8.1 技术风险

| 风险 | 缓解措施 |
|------|---------|
| goctl 版本不兼容 | 使用与 example-service 相同版本 |
| API 定义语法错误 | 参考 Go-Zero 官方文档 |

### 8.2 依赖任务

无

### 8.3 缓解措施

- 提前安装 goctl 工具
- 参考 example-service 项目结构
- 查看 Go-Zero 官方文档

---

## 9. 附录

### 9.1 参考文档

- [Go-Zero 官方文档](https://go-zero.dev/)
- [example-service 项目](https://git.example.com/example-org/example-service)

### 9.2 设计文档链接

- [EPIC-1: 项目脚手架搭建](../prd/epic-1-scaffolding.md)
