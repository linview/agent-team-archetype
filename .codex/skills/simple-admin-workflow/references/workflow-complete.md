# Simple Admin 完整开发工作流

## 工作流总览

```
Ent Schema 定义
    ↓ make gen-ent
Ent ORM 代码
    ↓ make gen-rpc-ent-logic model=XXX group=xxx
RPC Proto + Logic
    ↓ make gen-rpc
RPC 服务代码
    ↓ make gen-api-from-rpc (可选) 或手写 API
API 定义 + Logic
    ↓ make gen-api
API 服务代码
    ↓ m-goctls frontend vben5
Vue 前端页面
```

## 场景 1：从零开发新功能（完整工作流）

### 前置准备

1. **确认微服务**：
   - 使用 Read 工具读取 `goctls.yaml` 文件
   - 从 `service.serviceList` 获取可用的微服务列表
   - 询问用户要在哪个微服务中开发（core 或 serviceList 中的服务）

2. **确认功能需求**：明确要开发的功能和数据模型

### 步骤 1：定义 Ent Schema

**位置**：`servers/{service}/ent/schema/{model}.go` 或 `servers/{service}/rpc/ent/schema/{model}.go`

**操作**：
1. 如果是新模型，创建 Schema 文件
2. 定义字段、索引、关系等
3. 如果需要权限控制，添加 `@casbin:enabled` 注释

**示例**：
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

**注意事项**：
- ✅ 可以修改：`ent/schema/*.go`
- ❌ 不能修改：`ent/` 目录下其他文件（自动生成）

### 步骤 2：生成 Ent 代码

**命令**（在项目根目录）：
```bash
make {service}-gen-ent
```

**生成内容**：
- `ent/*.go` - ORM 代码
- `ent/migrate/*.go` - 数据库迁移代码

### 步骤 3：生成 RPC Proto 和 Logic

**命令**（在项目根目录）：
```bash
make {service}-gen-rpc-ent-logic model=User group=user
```

**参数说明**：
- `model` - 模型名称（首字母大写，如 User）
- `group` - 分组名称（小写，如 user）

**生成内容**：
- `desc/user.proto` - gRPC 接口定义（源文件）
- `internal/logic/user/*_logic.go` - CRUD 实现
  - `create_user_logic.go`
  - `update_user_logic.go`
  - `delete_user_logic.go`
  - `get_user_by_id_logic.go`
  - `get_user_list_logic.go`

**注意事项**：
- ✅ 可以修改：`desc/*.proto`（Proto 源文件）
- ❌ 不能修改：根目录的 `{service}.proto`（自动合并生成）

### 步骤 4：生成 RPC 服务代码

**命令**（在项目根目录）：
```bash
make {service}-gen-rpc
```

**生成内容**：
- `{service}.proto` - 合并后的 Proto 文件（从 desc/ 自动合并）
- `types/{service}/*.pb.go` - Protobuf 类型
- `internal/server/*.go` - gRPC 服务器
- `internal/svc/service_context.go` - 服务上下文

### 步骤 5：生成 API 定义和 Logic

有两种方式：

#### 方式 A：从 RPC 自动生成（推荐 CRUD）

**命令**（在项目根目录）：
```bash
make core-gen-api-from-rpc service={service_name} model=User
```

**生成内容**：
- `api/desc/{service}/*.api` - API 定义
- `api/internal/logic/{service}/*_logic.go` - API Logic（调用 RPC）
- `api/internal/handler/{service}/*_handler.go` - HTTP 处理器

#### 方式 B：手写 API 定义（自定义接口）

1. 在 `servers/core/api/desc/{service}/` 目录下创建 `.api` 文件
2. 定义 API 接口、请求/响应结构
3. 运行 `make core-gen-api` 生成代码
4. 手动实现 Logic（调用 RPC）

**注意事项**：
- ✅ 可以修改：`api/desc/*.api`（API 源文件）
- ⚠️ 需要维护：`api/desc/all.api`（导入文件，新增 API 时需要添加 import）
- ✅ 可以修改：`api/internal/logic/*.go`（业务逻辑）
- ❌ 不能修改：`api/internal/handler/*.go`（HTTP 处理器，重新生成会覆盖）

### 步骤 6：更新 all.api 并生成 API 服务代码

**⚠️ 重要**：如果是新增的 API 文件，需要在 `all.api` 中添加 import

**步骤 6.1：编辑 all.api 添加 import**：

使用 Edit 工具在 `api/desc/all.api` 中添加新的 import 语句：

```api
# all.api 文件示例
import "base.api"
import "./core/role.api"
import "./core/user.api"        # 已有的
import "./core/product.api"     # 新增的 - 添加这一行
import "./job/task.api"
# ... 其他 import
```

**import 路径规则**：
- `./core/*.api` - Core 服务的 API
- `./job/*.api` - Job 服务的 API
- `./aiplorer/*.api` - Aiplorer 服务的 API
- `./connector/*.api` - Connector 服务的 API
- `./mcasbin/*.api` - Mcasbin 服务的 API

**步骤 6.2：生成 API 代码**：
```bash
make core-gen-api
```

**生成内容**：
- `api/internal/handler/` - HTTP 处理器
- `api/internal/types/types.go` - 类型定义

### 步骤 7：生成前端页面

**命令**（在项目根目录）：
```bash
cd {serverDir}/core
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

（`{serverDir}` 从 `goctls.yaml` 的 `serverDirPrefix` 读取，默认为 `servers`）

**参数说明**：
- `--api_file` - API 定义文件路径
- `--model_name` - 模型名称（首字母大写）
- `--model_chinese_name` - 模型中文名称（用于页面标题）
- `--model_english_name` - 模型英文名称（小写，用于文件命名）
- `--folder_name` - 主文件夹（sys/mcms/fms 等）
- `--sub_folder` - 子文件夹（可选）
- `--prefix` - API 前缀（sys-api/mcms-api 等）
- `--output` - 输出目录（通常是 `../../web/apps/simple-admin-core`）
- `--form_type` - 表单类型（modal/drawer，默认 modal）
- `--overwrite` - 是否覆盖已存在文件

**生成内容**：
- `src/views/{folder_name}/{sub_folder}/index.vue` - 列表页面
- `src/views/{folder_name}/{sub_folder}/form.vue` - 表单组件
- `src/api/{folder_name}/{model_english_name}.ts` - API 调用
- `src/router/routes/modules/{folder_name}.ts` - 路由配置（如果不存在）
- `src/locales/*/views/{folder_name}/{model_english_name}.json` - 国际化

**注意事项**：
- ✅ 前端所有生成的文件都可以修改
- ⚠️ 使用 `--overwrite` 会覆盖已有文件，谨慎使用

### 步骤 8：配置路由和菜单

**自动生成**：
- 如果使用 `m-goctls frontend vben5` 且路由文件不存在，会自动生成
- 菜单需要在后端的权限管理中配置

**手动配置**（如果需要）：
1. 编辑 `src/router/routes/modules/{folder_name}.ts`
2. 添加路由配置
3. 在后端权限管理中添加菜单项

### 步骤 9：测试和验证

1. **启动所有服务**（在项目根目录）：
   ```bash
   make service-run
   ```

2. **启动前端**：
   ```bash
   cd web
   pnpm dev:simple-admin-core
   ```


## 场景 2：修改现有功能（部分工作流）

### 子场景 2.1：新增/修改字段

**步骤**：
1. 修改 Ent Schema（`ent/schema/{model}.go`）
2. `make gen-ent` - 重新生成 Ent 代码
3. `make gen-rpc-ent-logic model={Model} group={group}` - 重新生成 RPC（⚠️ 会覆盖 Logic）
4. `make gen-rpc` - 重新生成 RPC 服务代码
5. 更新 API 定义（如果需要暴露新字段）
6. `make gen-api` - 重新生成 API 代码
7. 更新前端页面（手动添加新字段到表单和列表）

**注意事项**：
- ⚠️ `make gen-rpc-ent-logic` 会覆盖 Logic 文件，如果有自定义逻辑，需要备份
- ✅ 可以设置 `goctls.yaml` 中 `entConfig.overwrite: false` 来避免覆盖

### 子场景 2.2：新增自定义接口（不是 CRUD）

**步骤**：
1. 在 `desc/{service}.proto` 中添加新的 RPC 方法
2. `make {service}-gen-rpc` - 生成 RPC 代码
3. 在 `internal/logic/` 下创建新的 Logic 文件，实现业务逻辑
4. 在 `api/desc/{service}/*.api` 中添加对应的 API 接口
5. `make core-gen-api` - 生成 API 代码
6. 在 `api/internal/logic/` 中实现 API Logic（调用 RPC）
7. 前端手动添加 API 调用和页面功能

### 子场景 2.3：只修改前端

**步骤**：
1. 直接修改 `web/apps/simple-admin-core/src/views/` 下的 Vue 文件
2. 测试验证

## 场景 3：只开发某个环节

### 子场景 3.1：只开发 RPC（不需要 API 和前端）

**步骤**：
1. 定义 Ent Schema
2. `make {service}-gen-ent`
3. `make {service}-gen-rpc-ent-logic model={Model} group={group}`
4. `make {service}-gen-rpc`
5. 测试 RPC 服务

**应用场景**：
- 内部服务调用
- 后台任务
- 定时任务服务

### 子场景 3.2：只开发 API（RPC 已存在）

**步骤**：
1. 使用 `make core-gen-api-from-rpc` 或手写 API 定义
2. `make core-gen-api`
3. 实现 API Logic
4. 测试 API

### 子场景 3.3：只开发前端（API 已存在）

**步骤**：
1. 使用 `m-goctls frontend vben5` 生成基础页面
2. 根据需求自定义页面
3. 测试前端功能

## 重要规则和最佳实践

### 文件修改规则

**✅ 可以修改的文件**：
- `ent/schema/*.go` - Ent Schema 定义
- `desc/*.proto` - RPC Proto 源文件（微服务目录下的 desc 目录）
- `api/desc/*.api` - API 定义源文件（desc 目录）
- `internal/logic/*.go` - 业务逻辑实现
- `web/` 下所有前端文件

**⚠️ 需要维护的文件（AI 负责）**：
- `api/desc/all.api` - API 导入文件，新增 API 文件时需要添加 import 语句

**❌ 不能修改的文件（自动生成，会被覆盖）**：
- `ent/` 目录下除 `schema/` 外的所有文件
- 根目录的 `{service}.proto`（从 desc/ 合并）
- `types/` 目录下的 Protobuf 生成文件
- `internal/handler/` - HTTP 处理器
- `internal/server/` - gRPC 服务器


### 配置驱动

所有参数从 `goctls.yaml` 和各微服务的 `Makefile` 中读取，避免手动指定。

### 权限控制

- 在 Ent Schema 上方添加 `@casbin:enabled` 注释
- 生成的 Logic 会自动包含权限检查
- API 层通过 JWT + Casbin 中间件控制

### 国际化支持

- 项目启用了 i18n（`goctls.yaml` 中 `i18n: true`）
- 前端生成会自动创建多语言文件
- 错误信息使用 `l.svcCtx.Trans.Trans(l.ctx, "key")` 翻译

## 常见问题排查

### Proto 修改后没有生效

**原因**：修改了根目录的 `.proto` 文件，而不是 `desc/` 目录下的源文件

**解决**：
1. 只修改 `desc/*.proto`
2. 运行 `make gen-rpc` 重新合并

### Logic 被覆盖了

**原因**：运行 `make gen-rpc-ent-logic` 会覆盖 Logic 文件

**解决**：
- 方案 1：在 `goctls.yaml` 中设置 `entConfig.overwrite: false`
- 方案 2：手动备份 Logic 文件
- 方案 3：使用版本控制（Git）恢复

### API 生成失败

**原因**：`.api` 文件语法错误或路径问题

**解决**：
1. 检查 `.api` 文件语法
2. 确保在正确的目录下运行命令
3. 查看错误信息定位问题

### 前端生成的页面样式不对

**原因**：API 定义和字段类型不匹配

**解决**：
1. 检查 API 定义中的字段类型
2. 重新生成前端页面
3. 手动调整组件

## 完整示例：开发用户管理功能

见下方完整示例演示整个工作流。

### 1. 确认需求
- 功能：用户管理
- 微服务：core
- 字段：id, username, email, password, status, created_at, updated_at

### 2. 定义 Ent Schema
```bash
# 编辑 {serverDir}/core/rpc/ent/schema/user.go
# ({serverDir} 从 goctls.yaml 的 serverDirPrefix 读取)
```

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

### 3. 生成代码
```bash
# 在项目根目录执行

# 生成 Ent 代码
make core-gen-ent

# 生成 RPC Proto 和 Logic
make core-gen-rpc-ent-logic model=User group=user

# 生成 RPC 服务代码
make core-gen-rpc

# 生成 API（假设 core 服务有 API）
make core-gen-api-from-core-rpc model=User

# 生成 API 代码
make core-gen-api
```

### 4. 生成前端
```bash
cd {serverDir}/core
m-goctls frontend vben5 \
  --api_file=./api/desc/core/user.api \
  --model_name=User \
  --model_chinese_name=用户 \
  --model_english_name=user \
  --folder_name=sys \
  --sub_folder=user \
  --prefix=sys-api \
  --output=../../web/apps/simple-admin-core
```

（`{serverDir}` 从 `goctls.yaml` 的 `serverDirPrefix` 读取）

### 5. 测试
```bash
# 启动所有服务（在项目根目录）
make service-run

# 启动前端
cd web
pnpm dev:simple-admin-core
```

### 6. 访问页面
打开浏览器访问 `http://localhost:5555`（或配置的端口），测试用户管理功能。
