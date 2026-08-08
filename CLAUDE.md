# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

这是一个 **AI-Native 原型模板仓库（archetype）**，展示 AI-native 项目的架构形制与方法论，**不是可交付的生产服务**。仓库为**双层结构**：

| 层 | 位置 | 内容 |
|----|------|------|
| **主项目根目录** | `/` | 方法论知识库 + agent skills + 通用文档，**不含任何业务实现** |
| **后端范例** | `examples/backend/` | 自包含、可独立编译的 Go 工程（独立 module `example-service`），完整展示分层架构 |

**默认判断**（重要）：
- 业务代码改动**一律在 `examples/backend/` 内**进行；主项目根目录不应新增业务实现。
- 除非用户明确要求，**不要把仓库补全成具体业务系统**，优先保持"模板/原型"属性。
- 工作前先判断任务落在**主项目**（方法论/skills 维护）还是**范例**（`examples/backend/` 调整）。

## Development Commands

⚠️ **所有 Go / Make 工程命令都在 `examples/backend/` 下执行**——主项目根目录已于 v2.3 净化，**无 `go.mod`、无 `Makefile`、无可运行 Go 服务**。

```bash
cd examples/backend

# 编译（独立 module，无需 go.work）
go build ./...

# Go 单元测试（仅 internal/）
make test                    # = go test -v --cover ./internal/...
go test ./internal/...       # 直接跑
go test -run TestFoo ./internal/dao/...   # 跑单个测试

# 格式化与 lint
make fmt                     # = gofmt -s -w .
make lint                    # = golangci-lint run ...

# Python 测试（tests/ 下，pytest）
python -m pytest tests/api -q
python -m pytest tests/sit -v          # ⚠️ 见下方安全警告
```

`make build` / `make run` / `make docker` 等目标**视为模板示例**——`run` 依赖 `etc/config/config.yaml`（仓库只提供 `.template`），未填充配置前不可直接执行。

## Architecture

### 仓库双层结构

- **主项目根**：方法论（`GUIDE.md`、`docs/guides/`）+ agent skills（`.claude/`、`.codex/`）+ 通用文档。根目录残留的 `etc/`、`tests/` 为配置/测试**框架骨架**，非业务实现。
- **`examples/backend/`**：独立 Go module（`module example-service`，Go 1.24 + go-zero v1.8.3）。

### 范例分层架构（examples/backend/internal/）

```
HTTP Request → Handler → Logic → DAO(接口) → Model
```

- **interface-based DAO**：`internal/dao/interfaces.go` 定义 `...DAOInterface` 抽象，**范例中实现层省略**（实际项目应提供实现并用 `var _ Iface = (*Impl)(nil)` 做编译期断言）。
- `handler/`、`logic/`、`middleware/`、`pkg/`、`svc/` 为**占位目录**（`.gitkeep`），仅展示分层位置。
- `model/`：业务实体（Pod 资源、GPU 用量、CMDB）。

**技术栈**：Go 1.24+ / go-zero / GORM / PostgreSQL / client-go（K8s）。

## Testing Strategy

四层测试金字塔，测试代码位于 `examples/backend/tests/`（pytest，配置 `tests/pytest.ini`）：

| 层 | 位置 | 性质 |
|----|------|------|
| UT | `internal/**/*_test.go` | Go 单元测试，函数级 |
| API | `tests/api/` | 契约测试 |
| SIT | `tests/sit/` | 集成测试 |
| UAT | `tests/uat/` | 验收测试 |

🚨 **安全警告（务必遵守）**：
- **SIT / UAT fixture 可能连接真实 Kubernetes 与 PostgreSQL 环境**——未确认环境安全前，**不要把它们当作本地无害测试执行**。
- **不要随意运行 `tests/uat`**。
- 不要轻易修改与环境绑定的配置（`etc/config/*.yaml`）。

范例当前大部分测试内容为骨架。

## Configuration

**运行时配置**（`examples/backend/etc/config/`，可变）：
- `config-local.yaml` / `config-test.yaml` / `config-prod.yaml`（部分为 `.template`）

**部署配置**（`examples/backend/deploy/`，不可变镜像）：
- `docker/docker-compose.yml`（本地）
- `k8s/helm/...values-test.yaml` / `values-prod.yaml`

⚠️ `etc/config/*.yaml` **不视为默认可安全复用的本地配置**，可能含环境特定值。

**加载优先级**：CLI `-f path` > 环境变量 `CONFIG_FILE` > 默认 `etc/config/config.yaml`。

## Agent Team Skills

`.claude/skills/` 下定义了多角色 agent skills，用 `/skill-name` 调用：

| Skill | 领域 |
|-------|------|
| `arch` | 架构设计 |
| `dev` | 开发实现 |
| `qa` | 测试验证（UT/SIT/UAT 策略） |
| `devops` | 部署运维 |
| `pm` | 项目管理（Story/Epic/Sprint 编排） |
| `commit` | 代码提交与 MR |
| `refactor` | 安全重构 |
| `sentinel` | 线上巡检 |
| `spec-xchecker` | Design↔Scrum↔Code↔Tests 四路对齐检查 |
| `ued` | 前端体验 |

`.codex/skills/` 是对应 Codex agent 的适配层。完整协作流程见 `GUIDE.md`。

## Key Documents

- `GUIDE.md` — AI-Native 开发完整指南（Agent Team 协作、研发流程）⭐ 核心
- `AGENTS.md` — 仓库工作指南（代理协作约束）
- `docs/guides/ai_native_development_guide_book.md` — 开发方法论专著
- `examples/backend/docs/design/` — 范例设计文档（服务层架构、数据层、API 设计）
- `examples/backend/internal/dao/interfaces.go` — DAO 接口抽象

> 引用 `examples/backend/docs/design/` 下设计文档前，**先确认文件实际存在**（部分为 `.template`）。

## When Working with This Codebase

- **业务代码**：只在 `examples/backend/` 内。主项目根目录不新增业务实现。
- **PR 说明**需明确：改动是否仍"模板安全"、影响主项目还是范例、做了哪些验证、是否仍有占位符/外部依赖/环境风险。
- **提交风格**：Conventional Commits（`fix(skills): ...`、`feat(guide): ...`、`docs(examples): ...`），带作用域。
- **未经确认**，不主动运行可能访问真实外部环境（K8s/PG）的测试或脚本。

## Version History

- **v2.3** (2026-07-17): examples/backend 范例搬迁落定，主项目彻底净化为 archetype（MR !3）
- **v2.2** (2026-06-16): 技能质量修复（spec-xchecker 运行时静默失效修复、pm DEFERRED 状态）
- **v2.1** (2026-06-12): 技能生态增强（Codex 适配、9 skills 产品化、UED/spec-xchecker/sentinel/refactor 新增、4 轮脱敏）
- **v2.0** (2026-04-28): 去实现化重构（移除业务逻辑实现，仅保留框架）
- **v1.0** (2026-02-04): 初始版本

> 完整变更见 `CHANGELOG.md`。
