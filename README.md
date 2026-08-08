# Agent Team Archetype - AI-Native Project 原型工程

> ⚠️ **重要提示**：这是一个**原型工程（Prototype Project）**，用于展示 **AI-native Project 的架构形制**，**不是**用于实际运行的生产项目。

---

## 🎯 项目定位

**核心定位**: 这是一个**原型工程（Prototype Project）**，用于展示 **AI-native Project 的架构形制**。

仓库由两层组成：
- **主项目根目录**：方法论知识库 + agent skills，不含任何业务实现。
- **`examples/backend/`**：一个**自包含、可独立编译的后端工程范例**（独立 Go module），完整展示分层架构、DAO 接口、数据模型、配置/部署模板与测试框架。

**项目目标**:
- ✅ 展示 AI-native 项目的架构模式和最佳实践
- ✅ 提供可复用的项目结构和框架代码（见 `examples/backend/`）
- ✅ 作为其他项目的参考模板
- ❌ **不是**用于实际运行的生产项目
- ❌ 主项目根目录**不包含**具体的业务逻辑实现

**核心价值**: 展示 **AI-native Project 的架构形制**，而非提供可直接运行的代码。

---

## 📂 项目结构

```
agent-team-archetype/
├── README.md                    # 本文件（项目概况）
├── GUIDE.md                     # AI-Native 开发完整指南 ⭐
├── AGENTS.md                    # 仓库工作指南（代理协作）
├── CLAUDE.md                    # Claude Code 使用指南
├── CHANGELOG.md                 # 更新日志
├── .gitignore
│
├── .claude/skills/              # Claude Code agent skills
├── .codex/skills/               # Codex agent skills
├── docs/
│   └── guides/                  # AI-Native 开发方法论（guide_book）
│
└── examples/
    └── backend/                 # ⭐ 完整后端工程范例（独立 Go module）
        ├── go.mod               # module example-service
        ├── main.go              # 应用入口（最小可运行骨架）
        ├── Makefile             # 构建工具
        ├── pyproject.toml       # Python 测试依赖
        ├── .gitlab-ci.yml       # 业务 CI
        ├── internal/            # Go 核心代码
        │   ├── config/          # 配置结构定义
        │   ├── dao/             # 数据访问层接口（interfaces.go）
        │   ├── model/           # 数据模型（Pod/GPU/CMDB 业务实体）
        │   ├── types/           # 通用类型定义
        │   ├── handler/         # HTTP 处理器（占位）
        │   ├── logic/           # 业务逻辑（占位）
        │   ├── middleware/      # 中间件（占位）
        │   ├── pkg/             # 工具包（占位）
        │   └── svc/             # 服务层（占位）
        ├── etc/config/          # 运行时配置（*.yaml.template + 范例）
        ├── deploy/              # 部署模板（Docker + K8s Helm）
        ├── tests/               # 测试骨架（api/sit/uat）
        └── docs/                # 业务设计 + scrum 管理文档
```

---

## 🚀 快速开始

### 1. 学习方法论（主项目）

```bash
# 阅读 AI-Native 开发完整指南
cat GUIDE.md

# 阅读开发方法论专著
cat docs/guides/ai_native_development_guide_book.md

# 查看 agent skills
ls .claude/skills/
```

### 2. 查看后端工程范例

```bash
cd examples/backend

# 查看目录结构
tree -L 2 -I 'node_modules|.git'

# 查看 Go 框架代码
ls -la internal/

# 编译范例（独立 module，无需 go.work）
go build ./...
```

### 3. 学习架构设计

**查看设计文档**（位于范例内）：
- `examples/backend/docs/design/service_layer_architecture_v4.2.md` - 服务层架构
- `examples/backend/docs/design/data_layer_design_*.md.template` - 数据层设计模板
- `examples/backend/docs/design/api_design_v1.3.md` - API 设计

**理解接口定义**：
- `examples/backend/internal/dao/interfaces.go` - DAO 接口抽象
- `examples/backend/internal/model/` - 数据模型
- `examples/backend/internal/types/types.go` - 通用类型定义

### 4. 基于范例创建新项目

```bash
# 步骤 1: 复制范例作为新项目基础
cp -r examples/backend my-new-project
cd my-new-project

# 步骤 2: 重命名 Go module
# 编辑 go.mod: module example-service → module my-new-project
# 全仓替换 import "example-service/..." → "my-new-project/..."

# 步骤 3: 实现 DAO 接口
# 根据 internal/dao/interfaces.go 提供具体实现

# 步骤 4: 装配 handler 与 ServiceContext
# 在 main.go 中注册业务 handler

# 步骤 5: 填充配置值
# 根据 etc/config/*.yaml.template 填充实际配置
```

---

## 🛠️ 技术栈（examples/backend）

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
3. **[AGENTS.md](AGENTS.md)** - 仓库工作指南
4. **[CLAUDE.md](CLAUDE.md)** - Claude Code 使用指南

### AI-Native 开发
1. **[GUIDE.md](GUIDE.md)** - AI-Native 开发理念、Agent Team 协作、完整开发流程
2. **[docs/guides/ai_native_development_guide_book.md](docs/guides/ai_native_development_guide_book.md)** - 开发方法论专著
3. **[.claude/skills/](.claude/skills/)** - Agent Team 技能定义
   - `/arch` - 架构师技能
   - `/dev` - 开发者技能
   - `/qa` - QA 技能
   - `/devops` - DevOps 技能
   - `/pm` - 项目管理技能
   - `/commit` - 代码提交技能

### 架构理解（范例内）
1. `examples/backend/docs/design/service_layer_architecture_v4.2.md` - 服务层架构
2. `examples/backend/docs/design/api_design_v1.3.md` - API 设计
3. `examples/backend/internal/dao/interfaces.go` - DAO 接口抽象

---

## 🎓 原型工程 vs 实际项目

| 维度 | 原型工程（本仓库） | 实际项目 |
|------|---------|---------|
| **主项目根** | 方法论 + agent skills（无业务代码） | — |
| **范例代码** | `examples/backend/`（接口骨架 + 占位） | 完整实现 |
| **可运行性** | 范例可编译；主项目非可执行 | ✅ 可运行 |
| **业务逻辑** | 接口定义为主，实现层省略 | 完整实现 |
| **用途** | 参考模板、架构展示、方法论 | 生产使用 |

---

## 🤝 贡献指南

### 如何使用原型工程

1. **学习方法论**: 阅读 `GUIDE.md` 与 `docs/guides/`，理解 AI-Native 开发理念
2. **理解架构**: 查看 `examples/backend/internal/` 的接口定义与数据模型
3. **创建项目**: 复制 `examples/backend/` 作为新项目的基础
4. **实现接口**: 根据 `internal/dao/interfaces.go` 实现具体的 DAO、Handler、Logic
5. **填充配置**: 根据配置模板填充实际配置值
6. **添加测试**: 根据测试框架编写具体的测试用例

### 代码规范

- 遵循 `GUIDE.md` 中的 AI-Native 开发流程
- 参考 `.claude/skills/dev/SKILL.md` 开发指南
- 参考 `.claude/skills/qa/SKILL.md` 测试规范

---

## 🔗 相关资源

- **方法论**: `GUIDE.md` + `docs/guides/`
- **后端范例**: `examples/backend/`
- **SKILL 文档**: `.claude/skills/`
- **Claude Code 指南**: [CLAUDE.md](CLAUDE.md)
- **问题反馈**: 通过项目 Issue 反馈

---

## 📝 更新日志

### v2.1 (2026-07) - 工程范例化

**重大变更**：
- ✅ 后端工程代码整体搬迁至 `examples/backend/`，作为完整后端架构范例
- ✅ 主项目根目录纯净化：仅保留方法论、agent skills、通用文档
- ✅ 业务文档（design/scrum）随范例搬迁；`docs/guides/`（方法论）保留主项目
- ✅ 范例脱敏为 `example-service`（保留 GPU/Pod/CMDB 业务领域示范）

**主项目根目录现状**：
- 通用文档：README / GUIDE / AGENTS / CLAUDE / CHANGELOG
- agent skills：`.claude/`、`.codex/`
- 方法论：`docs/guides/`
- 范例：`examples/backend/`（独立 Go module）

### v2.0 (2026-04-28) - 去实现化改造

**重大变更**：
- ✅ 移除所有业务逻辑实现（保留接口定义）
- ✅ 移除所有测试用例（保留测试框架）
- ✅ 精简配置文件（保留配置框架）
- ✅ 更新文档说明（明确原型工程定位）

### v1.0 (2026-02-04) - 初始版本

---

**版本**: v2.1
**创建日期**: 2026-02-04
**最后更新**: 2026-07-02
**状态**: 原型工程（主项目方法论 + examples/backend 范例）
