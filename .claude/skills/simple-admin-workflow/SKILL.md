---
name: simple-admin-workflow
description: Simple Admin 完整开发工作流指导技能,涵盖从 Ent Schema 定义到 RPC 服务、API 网关、前端页面的全链路开发。当用户进行以下操作时使用此技能:(1) 开发新功能、新增字段、修改数据模型,(2) 创建或修改微服务的任何环节(Ent/RPC/API/前端),(3) 进行 CRUD 开发、接口开发、页面开发,(4) 需要使用 m-goctls 工具生成代码,(5) 在 Simple Admin 项目中进行任何开发工作。此技能提供完整的工作流指导,包括命令使用、文件修改规则、常见问题排查等。
---

# Simple Admin 完整开发工作流

## 概述

本技能提供 Simple Admin 项目的**端到端开发工作流指导**,涵盖从数据模型定义到前端页面的完整链路。

**核心工作流**:
```
Ent Schema → Ent 代码 → RPC Proto & Logic → RPC 服务 → API 定义 & Logic → API 服务 → 前端页面
```

**主要功能**:
- ✅ 新功能完整开发流程(从 Schema 到前端)
- ✅ 现有功能修改流程(字段新增、接口修改)
- ✅ 部分环节开发(只开发 RPC/API/前端)
- ✅ Makefile 命令参考和最佳实践
- ✅ 常见问题诊断和解决方案

**关键原则**:
1. **根目录 Makefile 优先** - 在项目根目录使用 `make {service}-{command}` 简化命令
2. **配置驱动** - 所有参数从 `goctls.yaml` 和 `Makefile` 读取
3. **源文件修改规则** - 只修改 `ent/schema/`、`desc/*.proto`、`api/desc/*.api`

**命令简化**:
- ✅ 推荐: `make {service}-gen-ent` (在根目录)
- ❌ 避免: 直接使用 `m-goctls` 命令

## 工作流决策树

根据用户需求,选择合适的工作流路径:

### 1. 用户是否明确开发环节?

**如果用户说明只需要某个环节** (如"只需要 RPC"、"只修改前端"):
- 与用户二次确认需求
- 跳转到对应的部分工作流(见下方"部分环节开发")

**否则** (如"新增用户管理功能"、"给 User 增加 phone 字段"):
- 默认执行完整工作流,从 Ent Schema 一直到前端

### 2. 确认微服务

**操作**：使用 Read 工具读取 `goctls.yaml` 文件，从 `service.serviceList` 获取微服务列表。

**微服务列表**：
- `core` - 核心服务（通常包含用户、角色、菜单等基础功能）
- 其他服务从 `goctls.yaml` 的 `service.serviceList` 读取

询问用户要在哪个微服务中开发功能。

### 3. 确认功能需求

明确要开发的功能:
- 新增完整 CRUD 功能?
- 修改现有数据模型?
- 新增自定义接口?
- 只修改前端展示?

## 核心工作流

### 场景 A: 从零开发新功能(完整链路)

适用于新增完整的 CRUD 功能,如"用户管理"、"产品管理"等。

#### 第 1 步: 定义 Ent Schema

**位置**: `{serverDir}/{service}/ent/schema/{model}.go` 或 `{serverDir}/{service}/rpc/ent/schema/{model}.go`

（`{serverDir}` 从 `goctls.yaml` 的 `serverDirPrefix` 读取，默认为 `servers`）

**操作**:
1. 创建或编辑 Schema 文件
2. 定义字段、索引、约束、关系
3. 如需权限控制,添加 `@casbin:enabled` 注释

**示例**:
```go
// @casbin:enabled
type User struct {
    ent.Schema
}

func (User) Fields() []ent.Field {
    return []ent.Field{
        field.Uint64("id"),
        field.String("username").Unique().MaxLen(50),
        field.String("email").Unique().MaxLen(100),
        field.String("password").Sensitive(),
        field.Uint8("status").Default(1),
        field.Int64("created_at").Immutable(),
        field.Int64("updated_at"),
    }
}

func (User) Indexes() []ent.Index {
    return []ent.Index{
        index.Fields("username"),
        index.Fields("email"),
    }
}
```

**参考**: 详细的 Schema 编写指南见 [simple-admin-rpc](../simple-admin-rpc/SKILL.md) 技能

#### 第 2 步: 生成 Ent 代码

**命令** (在项目根目录):
```bash
make {service}-gen-ent
```

**生成内容**: `ent/*.go` - ORM 代码和迁移脚本

#### 第 3 步: 生成 RPC Proto 和 Logic

**命令** (在项目根目录):
```bash
make {service}-gen-rpc-ent-logic model=User group=user
```

**参数**:
- `model` - 模型名(首字母大写,如 User、Product)
- `group` - 分组名(小写,如 user、product)

**生成内容**:
- `desc/{group}/{model_lower}.proto` - gRPC 接口定义
- `internal/logic/{group}/*_logic.go` - CRUD 实现(5个文件)

**⚠️ 注意**: 此命令会覆盖已存在的 Logic 文件,如有自定义逻辑需备份

#### 第 4 步: 生成 RPC 服务代码

**命令** (在项目根目录):
```bash
make {service}-gen-rpc
```

**生成内容**:
- `{service}.proto` - 合并后的 Proto(从 desc/ 自动合并)
- `types/{service}/*.pb.go` - Protobuf 类型
- `internal/server/*.go` - gRPC 服务器

**⚠️ 重要规则**:
- ✅ 只修改 `desc/*.proto`
- ❌ 绝对不要修改根目录的 `{service}.proto`(自动生成)

#### 第 5 步: 生成 API 定义和 Logic

有两种方式:

**方式 A - 从 RPC 自动生成(推荐 CRUD)**:
```bash
make core-gen-api-from-rpc service={service_name} model=User
```

**方式 B - 手写 API 定义(自定义接口)**:
1. 在 `servers/core/api/desc/{service}/` 创建 `.api` 文件
2. 定义接口、请求/响应结构
3. 运行 `make gen-api` 生成代码
4. 手动实现 Logic(调用 RPC)

**⚠️ API 类型一致性规则(极其重要!)**:

在 `api/desc/` 目录下添加新的 API 文件时，必须遵守以下规则:

1. **必须 import base.api**: 在文件开头添加 `import "../base.api"`

2. **强制使用基础类型**: 以下场景必须使用 `base.api` 中的类型，不得自定义:
   - **分页请求** → 必须使用 `PageInfo` (包含 page, pageSize)
   - **列表响应** → 必须使用 `BaseListInfo` (包含 total, data)
   - **ID 请求** → 必须使用 `IDReq`(单个)、`IDsReq`(多个)、`IDPathReq`(路径参数)
   - **UUID 请求** → 必须使用 `UUIDReq`(单个)、`UUIDsReq`(多个)
   - **简单响应** → 必须使用 `BaseMsgResp` (只返回 code, msg)
   - **带数据响应** → 必须使用 `BaseDataInfo` (返回 code, msg, data)
   - **实体信息** → 必须继承 `BaseIDInfo`(uint64 ID) 或 `BaseUUIDInfo`(string UUID)
   - **存在性检查** → 必须使用 `ExistResp`

3. **保持类型一致性**: 避免重复定义相同功能的类型，确保整个项目的 API 类型统一

**示例**:
```api
syntax = "v1"

import "../base.api"

info(
    title: "user api"
    desc: "user management api"
    author: "Ryan SU"
    version: "v1.0"
)

type (
    // User info response
    UserInfo {
        BaseIDInfo           // 继承基础 ID 信息

        Username string `json:"username"`
        Email    string `json:"email"`
        Status   uint8  `json:"status"`
    }

    // User list response
    UserListResp {
        BaseListInfo         // 继承基础列表信息
    }

    // User list request
    UserListReq {
        PageInfo             // 继承分页参数

        Username string `json:"username,optional"`
    }
)

@server(
    group: user
    jwt: Auth
)

service Core {
    @handler getUserList
    post /user/list (UserListReq) returns (UserListResp)

    @handler getUserById
    post /user (IDReq) returns (BaseDataInfo)

    @handler deleteUser
    delete /user (IDsReq) returns (BaseMsgResp)
}
```

**参考**: 详细的 API 开发指南见 [simple-admin-api](../simple-admin-api/SKILL.md) 技能

#### 第 6 步: 更新 all.api 并生成 API 服务代码

**⚠️ 重要步骤**: 如果是新增的 API 文件,需要在 `all.api` 中添加 import

**操作步骤**:

1. **编辑 `api/desc/all.api`**,添加新 API 文件的 import:
   ```api
   import "./core/user.api"     # 如果是 core 服务
   import "./job/task.api"      # 如果是 job 服务
   import "./aiplorer/xxx.api"  # 如果是其他服务
   ```

2. **生成 API 代码**:
   ```bash
   make core-gen-api
   ```

**生成内容**:
- `api/internal/handler/**/*_handler.go` - HTTP 处理器
- `api/internal/types/types.go` - 请求/响应类型

#### 第 7 步: 生成前端页面

**命令**:
```bash
cd servers/core
m-goctls frontend vben5 \
  --api_file=./api/desc/{service}/user.api \
  --model_name=User \
  --model_chinese_name=用户 \
  --model_english_name=user \
  --folder_name=sys \
  --sub_folder=user \
  --prefix=sys-api \
  --output=../../web/apps/simple-admin-core
```

**核心参数**:
- `--api_file` - API 定义文件路径
- `--model_name` - 模型名(首字母大写)
- `--folder_name` - 主文件夹(sys/mcms/fms 等)
- `--prefix` - API 前缀(sys-api/mcms-api 等)
- `--output` - 输出目录(通常是 `../../web/apps/simple-admin-core`)

**生成内容**:
- `src/views/{folder}/{sub}/index.vue` - 列表页面
- `src/views/{folder}/{sub}/form.vue` - 表单组件
- `src/api/{folder}/{english_name}.ts` - API 调用
- `src/locales/*/views/{folder}/{english_name}.json` - 国际化

**参考**: 完整的前端生成命令参数见 [commands-reference.md](references/commands-reference.md)

#### 第 8 步: 测试验证

```bash
# 启动 所有 服务
make service-run

# 启动前端
cd web
pnpm dev:simple-admin-core

# 访问 http://localhost:5555 测试功能
```

### 场景 B: 修改现有功能

#### 子场景 B1: 新增/修改字段

**步骤**:
1. 修改 Ent Schema (`ent/schema/{model}.go`)
2. `make gen-ent` - 重新生成 Ent 代码
3. **选择性执行** `make gen-rpc-ent-logic model={Model} group={group}` (⚠️ 会覆盖 Logic)
4. `make gen-rpc` - 重新生成 RPC 服务代码
5. 更新 API 定义(如需暴露新字段)
6. `make gen-api` - 重新生成 API 代码
7. 手动更新前端页面(添加新字段到表单和列表)

**⚠️ 避免覆盖的方法**:
- 在 `goctls.yaml` 中设置 `entConfig.overwrite: false`
- 使用 Git 版本控制,随时可恢复
- 备份 Logic 文件后再重新生成

#### 子场景 B2: 新增自定义接口(非 CRUD)

**步骤**:
1. 在 `desc/{service}.proto` 中添加新的 RPC 方法
2. `make gen-rpc` - 生成 RPC 代码
3. 在 `internal/logic/` 下创建新的 Logic 文件,实现业务逻辑
4. 在 `api/desc/{service}/*.api` 中添加对应的 API 接口
5. `make gen-api` - 生成 API 代码
6. 在 `api/internal/logic/` 中实现 API Logic(调用 RPC)
7. 前端手动添加 API 调用和页面功能

#### 子场景 B3: 只修改前端

**步骤**:
1. 直接修改 `web/apps/simple-admin-core/src/views/` 下的 Vue 文件
2. 测试验证

### 场景 C: 部分环节开发

#### 子场景 C1: 只开发 RPC(不需要 API 和前端)

**适用场景**: 内部服务调用、后台任务、定时任务等

**步骤**:
1. 定义 Ent Schema
2. `make gen-ent`
3. `make gen-rpc-ent-logic model={Model} group={group}`
4. `make gen-rpc`
5. 测试 RPC 服务

**参考**: 详见 [simple-admin-rpc](../simple-admin-rpc/SKILL.md) 技能

#### 子场景 C2: 只开发 API(RPC 已存在)

**适用场景**: 需要为已有 RPC 服务提供 HTTP 接口

**步骤**:
1. 使用 `make gen-api-from-rpc` 或手写 API 定义
2. `make gen-api`
3. 实现 API Logic
4. 测试 API

**参考**: 详见 [simple-admin-api](../simple-admin-api/SKILL.md) 技能

#### 子场景 C3: 只开发前端(API 已存在)

**适用场景**: API 已完成,只需要添加或修改前端页面

**步骤**:
1. 使用 `m-goctls frontend vben5` 生成基础页面
2. 根据需求自定义页面
3. 测试前端功能

### 场景 D: 检查 API 文件规范

**适用场景**: 检查现有 API 文件是否符合类型一致性规范

**规范要求**: 参见"第 5 步"中的"API 类型一致性规则"

## 重要规则和最佳实践

### 文件修改规则(极其重要!)

**✅ 可以修改的文件**:
- `ent/schema/*.go` - Ent Schema 定义
- `desc/*.proto` - RPC Proto 源文件(微服务的 desc 目录)
- `api/desc/*.api` - API 定义源文件(desc 目录)
- `internal/logic/*.go` - 业务逻辑实现
- `web/` 下所有前端文件

**❌ 不能修改的文件(自动生成,会被覆盖)**:
- `ent/` 目录下除 `schema/` 外的所有文件
- 根目录的 `{service}.proto`(从 desc/ 合并)
- `types/` 目录下的 Protobuf 生成文件
- `internal/handler/` - HTTP 处理器
- `internal/server/` - gRPC 服务器

**⚠️ 需要维护的文件（AI 负责）**:
- `api/desc/all.api` - 新增 API 文件时需要添加 import 语句

### 根目录 Makefile 优先原则

**✅ 最推荐 - 在项目根目录使用**:
```bash
make {service}-gen-ent
make {service}-gen-rpc-ent-logic model=Task group=task
make {service}-gen-rpc
make core-gen-api
```

**❌ 避免 - 直接使用 m-goctls**:
```bash
# 不推荐 - 参数复杂易错
m-goctls rpc ent --schema=./ent/schema --style=go_zero ...
```

**根目录 Makefile 的优势**:
- 🚀 无需 cd 切换目录
- 🎯 命令更简洁直观
- 🔧 AI 和用户都可以使用

**查看所有可用命令**:
```bash
make help
```

### 配置驱动

所有参数从 `goctls.yaml` 和各微服务的 `Makefile` 中读取,避免手动指定:

```yaml
# goctls.yaml (项目根目录)
i18n: true
ent: true
style: "go_zero"

entConfig:
  searchKeyNum: 300
  overwrite: false  # 避免覆盖 Logic

frontend:
  folderName: "sys"
  apiPrefix: "sys-api"
  formType: "drawer"
```

### 权限控制

在 Ent Schema 上方添加 `@casbin:enabled` 注释即可启用权限控制:
```go
// @casbin:enabled
type User struct {
    ent.Schema
}
```

生成的 Logic 会自动包含权限检查,API 层通过 JWT + Casbin 中间件控制。

## 详细参考文档

本技能包含详细的参考文档,按需加载:

### [workflow-complete.md](references/workflow-complete.md)
**完整工作流详细步骤指南**

包含:
- 每个场景的详细步骤和代码示例
- Ent Schema 编写指南
- Proto 和 API 定义示例
- Logic 实现模式
- 完整示例演示

**何时阅读**: 需要详细的步骤说明或代码示例时

## 快速参考

### 常用命令速查 (根目录)

| 命令 | 作用 | 使用场景 |
|-----|------|---------|
| `make {service}-gen-ent` | 生成 Ent 代码 | 修改 Schema 后 |
| `make {service}-gen-rpc-ent-logic model=X group=x` | 生成 RPC CRUD | 新增模型 |
| `make {service}-gen-rpc` | 生成 RPC 代码 | 修改 Proto 后 |
| `make core-gen-api` | 生成 API 代码 | 修改 API 定义后 |
| `make core-gen-api-from-rpc service=x model=X` | 从 RPC 生成 API | 暴露 RPC 为 API |
| `m-goctls frontend vben5 ...` | 生成前端页面 | 新增 CRUD 页面 |
| `make help` | 查看所有命令 | 不确定命令时 |

### 目录结构速查

```
{serverDir}/{service}/    # serverDir 从 goctls.yaml 读取
├── Makefile              # ✅ 所有命令入口
├── ent/schema/          # ✅ 可修改: Schema 定义
├── desc/                # ✅ 可修改: Proto 源文件
├── internal/logic/      # ✅ 可修改: 业务逻辑
├── {service}.proto      # ❌ 不可修改: 自动合并
└── types/               # ❌ 不可修改: 自动生成
```

## 工作流程示例

**用户**: "我要开发一个产品管理功能,属于 core 服务"

**完整流程**:
```bash
# 1. 定义 Schema
# 使用 Edit 工具编辑 {serverDir}/core/rpc/ent/schema/product.go

# 2. 逐步生成代码
make core-gen-ent
make core-gen-rpc-ent-logic model=Product group=product
make core-gen-rpc

# 3. 生成 API
make core-gen-api-from-core-rpc model=Product

# 4. 更新 all.api (如果是新 API 文件)
# 使用 Edit 工具在 {serverDir}/core/api/desc/all.api 中添加:
# import "./core/product.api"

# 5. 重新生成 API
make core-gen-api

# 6. 生成前端
cd {serverDir}/core
m-goctls frontend vben5 \
  --api_file=./api/desc/core/product.api \
  --model_name=Product \
  --model_chinese_name=产品 \
  --folder_name=sys \
  --prefix=sys-api \
  --output=../../web/apps/simple-admin-core
```

**传统方式** (逐步执行):
```bash
# 1. 定义 Schema
# 编辑 {serverDir}/core/rpc/ent/schema/product.go

# 2. 生成代码
make core-gen-ent
make core-gen-rpc-ent-logic model=Product group=product
make core-gen-rpc
make core-gen-api-from-core-rpc model=Product
make core-gen-api

# 3. 生成前端和测试...
```

**注**: `{serverDir}` 从 `goctls.yaml` 的 `serverDirPrefix` 配置读取

## 注意事项

1. **优先使用根目录命令** - `make {service}-{command}` 比 cd 切换更方便
2. **理解什么文件可以修改** - 只修改源文件(schema/desc),不修改生成文件
3. **备份重要逻辑** - 重新生成前备份自定义的 Logic 代码
4. **使用版本控制** - Git 可以随时恢复被覆盖的文件
5. **查看 make help** - 不确定命令时,先查看帮助
6. **遇到问题先查文档** - 参考 troubleshooting.md 排查常见问题

## 获取帮助

```bash
# 查看 Makefile 所有命令
make {service}-help
# 查看 m-goctls 帮助
m-goctls --help
m-goctls frontend vben5 --help
```

**社区资源**:
- Simple Admin 文档: https://doc.ryansu.tech/
- GitHub: https://github.com/suyuan32/simple-admin-core
