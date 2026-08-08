# internal 目录说明

## 目录用途

**internal** 是 Go 项目的核心代码目录，包含所有内部包和模块。

**原型工程说明**：此目录只保留框架代码（接口定义、数据模型），不包含具体实现。

---

## 📂 目录结构

```
internal/
├── config/           # 配置管理
│   └── config.go    # 配置结构定义
├── dao/              # 数据访问层
│   └── interfaces.go # DAO 接口定义
├── handler/          # HTTP 处理器（空目录）
├── logic/            # 业务逻辑层（空目录）
├── model/            # 数据模型
│   ├── aggregation.go # 聚合模型
│   ├── cmdb.go        # CMDB 数据模型
│   └── pod_resource.go # Pod 资源模型
├── middleware/       # 中间件（空目录）
├── pkg/              # 工具包（空目录）
├── svc/              # 服务层（空目录）
└── types/            # 通用类型定义
    └── types.go      # 通用类型
```

---

## 🎯 各目录说明

### config/

**用途**: 配置管理模块

**职责**:
- 定义配置结构体
- 加载和解析配置文件
- 提供配置访问接口

**原型工程**: 只保留配置结构定义，不包含加载逻辑

---

### dao/

**用途**: 数据访问层（Data Access Object）

**职责**:
- 定义数据库访问接口
- 提供数据操作的抽象
- 实现具体的数据访问逻辑

**原型工程**: 只保留接口定义（`interfaces.go`），不包含具体实现

**设计原则**:
- 使用接口抽象，隔离数据层实现
- 依赖注入，便于测试和替换
- 统一错误处理和事务管理

---

### handler/

**用途**: HTTP 请求处理器

**职责**:
- 处理 HTTP 请求和响应
- 参数验证和解析
- 调用业务逻辑层

**原型工程**: 空目录（只有 `.gitkeep` 占位符）

---

### logic/

**用途**: 业务逻辑层

**职责**:
- 实现核心业务逻辑
- 数据处理和计算
- 跨层协调

**原型工程**: 空目录（只有 `.gitkeep` 占位符）

---

### model/

**用途**: 数据模型定义

**职责**:
- 定义数据库表结构映射
- 定义数据验证规则
- 提供数据访问方法

**原型工程**: 保留数据模型定义（3 个文件），展示数据结构设计

**文件说明**:
- `aggregation.go`: 聚合数据模型
- `cmdb.go`: CMDB 数据模型（User, Team, Project）
- `pod_resource.go`: Pod 资源模型（PodResourceStatus, PodResourceGPUUsage）

---

### middleware/

**用途**: 中间件模块

**职责**:
- 请求拦截和处理
- 权限验证
- 日志记录
- 错误恢复

**原型工程**: 空目录（只有 `.gitkeep` 占位符）

---

### pkg/

**用途**: 工具包和辅助模块

**职责**:
- 提供通用工具函数
- 第三方库封装
- 算法实现

**原型工程**: 空目录（只有 `.gitkeep` 占位符）

---

### svc/

**用途**: 服务层模块

**职责**:
- 服务上下文管理
- 依赖注入容器
- 服务生命周期管理

**原型工程**: 空目录（只有 `.gitkeep` 占位符）

---

### types/

**用途**: 通用类型定义

**职责**:
- 定义通用数据结构
- 定义请求/响应类型
- 定义常量和枚举

**原型工程**: 保留通用类型定义（`types.go`）

---

## 🎯 设计原则

### 1. 接口抽象

**DAO 层使用接口抽象**，便于测试和替换实现：
```go
type PodResourceStatusDAOInterface interface {
    Create(ctx context.Context, pod *model.PodResourceStatus) error
    GetByK8sUID(ctx context.Context, k8sUID string) (*model.PodResourceStatus, error)
    Update(ctx context.Context, pod *model.PodResourceStatus) error
    List(ctx context.Context, filter *PodFilter) ([]*model.PodResourceStatus, error)
}
```

### 2. 依赖注入

**通过依赖注入**，降低耦合度：
```go
type PodHandler struct {
    podDAO dao.PodResourceStatusDAOInterface
    gpuCalculator *calculator.GPUUsageCalculator
}

func NewPodHandler(podDAO dao.PodResourceStatusDAOInterface) *PodHandler {
    return &PodHandler{podDAO: podDAO}
}
```

### 3. 分层架构

**清晰的分层结构**，职责分离：
```
Handler (HTTP) → Logic (业务) → DAO (数据) → Model (模型)
```

---

## 📝 使用指南

### 添加新的 DAO 实现

1. **实现接口**：
```go
type podResourceStatusDAO struct {
    db *gorm.DB
}

func (d *podResourceStatusDAO) Create(ctx context.Context, pod *model.PodResourceStatus) error {
    return d.db.WithContext(ctx).Create(pod).Error
}
```

2. **注册到容器**：
```go
func NewPodResourceStatusDAO(db *gorm.DB) dao.PodResourceStatusDAOInterface {
    return &podResourceStatusDAO{db: db}
}
```

### 添加新的数据模型

1. **定义模型结构**：
```go
type NewModel struct {
    ID        uint      `gorm:"primaryKey"`
    Name      string    `gorm:"not null"`
    CreatedAt time.Time `gorm:"autoCreateTime"`
    UpdatedAt time.Time `gorm:"autoUpdateTime"`
}
```

2. **添加表名约定**：
```go
func (NewModel) TableName() string {
    return "new_models"
}
```

---

## ⚠️ 注意事项

### 原型工程限制

- ❌ 不包含具体的业务逻辑实现
- ❌ 不包含数据访问层实现
- ❌ 不包含 HTTP 处理器实现
- ✅ 只保留接口定义和数据模型
- ✅ 展示分层架构设计原则
- ✅ 展示依赖注入和接口抽象

### 适配到新项目

1. 根据 `internal/dao/interfaces.go` 实现具体 DAO
2. 根据 `internal/model/*.go` 定义数据模型
3. 在 `internal/handler/`, `internal/logic/` 等目录添加业务逻辑
4. 遵循分层架构原则，保持职责分离

---

## 🔗 相关资源

- **设计文档**: `docs/design/service_layer_architecture_v4.2.md`
- **数据层设计**: `docs/design/cmdb_design_v4.0.md`
- **Go 项目规范**: https://github.com/golang/go/wiki/CodeReviewComments

---

**版本**: v1.0  
**更新日期**: 2026-04-28  
**维护者**: Development Team
