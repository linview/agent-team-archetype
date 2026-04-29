# Agent Team Archetype - AI-Native Project 原型工程

> ⚠️ **重要提示**：这是一个**原型工程（Prototype Project）**，用于展示 **AI-native Project 的架构形制**，**不是**用于实际运行的生产项目。

---

## 🎯 项目定位

**核心定位**: 这是一个**原型工程（Prototype Project）**，用于展示 **AI-native Project 的架构形制**。

**项目目标**:
- ✅ 展示 AI-native 项目的架构模式和最佳实践
- ✅ 提供可复用的项目结构和框架代码
- ✅ 作为其他项目的参考模板
- ❌ **不是**用于实际运行的生产项目
- ❌ **不包含**具体的业务逻辑实现

**核心价值**: 展示 **AI-native Project 的架构形制**，而非提供可直接运行的代码。

---

## 📂 项目结构

```
agent-team-archetype/
├── internal/                    # Go 核心代码目录
│   ├── config/                  # 配置结构定义
│   ├── dao/                     # 数据访问层接口定义
│   ├── handler/                 # HTTP 处理器（空目录，占位符）
│   ├── logic/                   # 业务逻辑层（空目录，占位符）
│   ├── model/                   # 数据模型定义
│   │   ├── aggregation.go       # 聚合模型
│   │   ├── cmdb.go              # CMDB 数据模型
│   │   └── pod_resource.go      # Pod 资源模型
│   ├── middleware/              # 中间件（空目录，占位符）
│   ├── pkg/                     # 工具包（空目录，占位符）
│   ├── svc/                     # 服务层（空目录，占位符）
│   └── types/                   # 通用类型定义
│
├── tests/                       # 测试目录
│   ├── conftest.py              # 主测试框架
│   ├── api/                     # API 契约测试
│   ├── sit/                     # 系统集成测试
│   ├── uat/                     # 用户验收测试
│   └── regression/              # 回归测试
│
├── docs/                        # 文档目录
│   ├── design/                  # 设计文档
│   ├── guides/                  # 使用指南
│   └── scrum/                   # 项目管理文档
│
├── deploy/                      # 部署配置
│   ├── docker/                  # Docker Compose（本地开发）
│   └── k8s/                     # Kubernetes Helm Charts
│
├── etc/                         # 运行时配置
│   └── config/                  # 配置文件框架
│
├── scripts/                     # 脚本工具
├── .claude/                     # Claude Code 配置
│   └── skills/                  # Agent Team 技能定义
│
├── main.go                      # 应用入口
├── Makefile                     # 构建工具
├── go.mod                       # Go 依赖管理
├── pyproject.toml               # Python 测试依赖
├── README.md                    # 本文件
├── GUIDE.md                     # AI-Native 开发指南
└── CLAUDE.md                    # Claude Code 使用指南
```

**代码量统计**（去实现化后）：
- Go 框架文件：5 个（接口定义、数据模型、类型定义）
- Python 测试框架：4 个（conftest.py）
- 设计文档：20+ 个（架构设计、API 设计、FAQ）

---

## 🚀 快速开始

### 1. 查看项目结构

```bash
# 查看目录结构
tree -L 2 -I 'node_modules|.git'

# 查看 Go 框架代码
ls -la internal/

# 查看测试框架
ls -la tests/
```

### 2. 学习架构设计

**查看设计文档**：
- `docs/design/service_layer_architecture_v4.2.md` - 服务层架构
- `docs/design/cmdb_design_v4.0.md` - 数据层设计
- `docs/design/api_design_v1.3.md` - API 设计

**理解接口定义**：
- `internal/dao/interfaces.go` - DAO 接口抽象
- `internal/model/cmdb.go` - CMDB 数据模型
- `internal/types/types.go` - 通用类型定义

**学习测试框架**：
- `tests/conftest.py` - 主测试框架
- `tests/sit/conftest.py` - SIT 测试框架

### 3. 创建新项目

```bash
# 步骤 1: 复制原型工程
cp -r agent-team-archetype my-new-project
cd my-new-project

# 步骤 2: 实现接口定义
# 根据 internal/dao/interfaces.go 定义实现具体 DAO
# 示例：实现 PodResourceStatusDAOInterface
type podResourceStatusDAO struct {
    db *gorm.DB
}

func (d *podResourceStatusDAO) Create(ctx context.Context, pod *model.PodResourceStatus) error {
    return d.db.WithContext(ctx).Create(pod).Error
}

# 步骤 3: 填充配置值
# 根据 etc/config/config.yaml 框架填充实际配置
database:
  host: localhost
  port: 5432
  user: postgres
  password: mypassword
  database: mydb

# 步骤 4: 添加业务逻辑
# 根据设计文档添加具体的业务逻辑实现
```

---

## 🛠️ 技术栈

### 后端框架
- **语言**: Go 1.24+
- **Web 框架**: go-zero
- **ORM**: GORM
- **数据库**: PostgreSQL
- **K8s 集成**: client-go

### 测试框架
- **单元测试**: Go testing
- **集成测试**: Pytest
- **SIT 测试**: Pytest + K8s
- **UAT 测试**: Pytest

### DevOps
- **容器化**: Docker
- **编排**: Kubernetes
- **CI/CD**: GitLab CI
- **Helm**: Helm Charts

### AI-Native 开发
- **Claude Code**: AI 编程助手
- **Agent Team**: 多角色协作开发（/arch, /dev, /qa, /devops 等）
- **Semantic Versioning**: 设计文档版本管理

---

## 📖 文档导航

### 新手入门
1. **本文件** (README.md) - 项目概况和结构
2. **[GUIDE.md](GUIDE.md)** - AI-Native 开发完整指南 ⭐
3. **[CLAUDE.md](CLAUDE.md)** - Claude Code 使用指南

### AI-Native 开发
1. **[GUIDE.md](GUIDE.md)** - AI-Native 开发理念、Agent Team 协作、完整开发流程
2. **[.claude/skills/](.claude/skills/)** - Agent Team 技能定义
   - `/arch` - 架构师技能
   - `/dev` - 开发者技能
   - `/qa` - QA 技能
   - `/devops` - DevOps 技能
   - `/commit` - 代码提交技能

### 架构理解
1. `docs/design/service_layer_architecture_v4.2.md` - 服务层架构
2. `docs/design/cmdb_design_v4.0.md` - 数据层设计
3. `docs/design/api_design_v1.3.md` - API 设计

### 开发指南
1. `docs/guides/` - 各种使用指南
2. `docs/scrum/` - 项目管理文档

---

## 🎓 原型工程 vs 实际项目

| 维度 | 原型工程 | 实际项目 |
|------|---------|---------|
| **代码量** | 5 个 Go 文件（框架代码） | 100+ 个 Go 文件（实现代码） |
| **测试用例** | 4 个测试框架 | 100+ 个测试用例 |
| **配置文件** | 配置框架（占位符） | 实际配置值 |
| **业务逻辑** | 无（只有接口定义） | 完整实现 |
| **可运行性** | ❌ 不可运行 | ✅ 可运行 |
| **用途** | 参考模板、架构展示 | 生产使用 |

---

## 🤝 贡献指南

### 如何使用原型工程

1. **学习架构**: 查看设计文档和接口定义，理解架构模式
2. **创建项目**: 复制原型工程作为新项目的基础
3. **实现接口**: 根据接口定义实现具体的 DAO、Handler、Logic
4. **填充配置**: 根据配置框架填充实际配置值
5. **添加测试**: 根据测试框架编写具体的测试用例

### 代码规范

- 遵循 `GUIDE.md` 中的 AI-Native 开发流程
- 参考 `.claude/skills/dev/SKILL.md` 开发指南
- 参考 `.claude/skills/qa/SKILL.md` 测试规范

---

## 🔗 相关资源

- **项目文档**: `docs/`
- **SKILL 文档**: `.claude/skills/`
- **AI-Native 开发指南**: [GUIDE.md](GUIDE.md)
- **Claude Code 指南**: [CLAUDE.md](CLAUDE.md)
- **问题反馈**: 通过项目 Issue 反馈

---

---

**状态**: 原型工程（展示架构形制）
