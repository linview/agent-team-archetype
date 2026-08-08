# 仓库工作指南

## 仓库定位

这是一个 AI-native **原型模板仓库**，不是可直接交付的生产服务。仓库的主要价值在于项目结构、分层示例、接口骨架、测试框架和设计文档，而不是可运行的业务实现。

仓库由两层组成：
- **主项目根目录**：方法论知识库 + agent skills（`.claude/`、`.codex/`）+ 通用文档（`GUIDE.md`、`docs/guides/`），不含任何业务实现。
- **`examples/backend/`**：一个**自包含、可独立编译的后端工程范例**（独立 Go module `example-service`），完整展示分层架构、DAO 接口、数据模型、配置/部署模板与测试框架。

默认判断：
- 除非用户明确要求，否则不要把这个仓库补全成具体业务系统。
- 优先保持“模板 / 原型”属性，不要无意引入项目私有实现。

## 项目结构与模块组织

主项目根目录只保留通用内容：
- `README.md` / `GUIDE.md` / `AGENTS.md` / `CLAUDE.md` / `CHANGELOG.md`：方法论与使用指南
- `.claude/`、`.codex/`：agent skills（架构、开发、测试、提交、PM 等角色定义）
- `docs/guides/`：AI-Native 开发方法论（`ai_native_development_guide_book.md`）
- `examples/backend/`：完整后端工程范例（见下）

`examples/backend/` 是完整的后端工程范例（独立 Go module）：
- `internal/`：核心 Go 骨架
  - `config/`：配置结构体定义
  - `dao/`：数据访问接口（`interfaces.go` 定义 `...DAOInterface` 抽象，范例中实现层省略）
  - `model/`：数据模型（Pod 资源、GPU 用量、CMDB 等业务实体）
  - `types/`：共享 API 类型
  - `handler/`、`logic/`、`middleware/`、`pkg/`、`svc/`：占位目录（`.gitkeep`），展示分层位置
- `etc/config/`：运行时配置框架（`*.yaml.template` + 范例配置）
- `deploy/`：部署模板（Docker Compose + Kubernetes Helm Charts）
- `tests/`：测试骨架（api / sit / uat / regression，pytest）
- `docs/`：业务设计文档与 scrum 管理文档
- `Makefile`、`pyproject.toml`、`.gitlab-ci.yml`、`go.mod`、`main.go`：构建、依赖与入口

需要注意的真实状态：
- 业务实现已整体搬迁至 `examples/backend/`，主项目根目录**不再包含**任何 Go 代码或业务逻辑。
- `examples/backend/internal/dao/interfaces.go` 仅定义接口；具体的 DAO 实现类型在本范例中省略（实际项目应在此提供实现并通过编译期断言 `var _ Iface = (*Impl)(nil)` 校验）。
- `examples/backend/internal/handler`、`svc`、`logic` 为占位目录，范例仅展示服务骨架与数据层。

## 构建、测试与开发命令

后端范例的所有工程命令都在 `examples/backend/` 下执行：
- `cd examples/backend && make fmt`：使用 `gofmt -s -w .` 格式化 Go 代码
- `cd examples/backend && make lint`：运行 `golangci-lint`
- `cd examples/backend && go build ./...`：编译整个范例（独立 module，无需 go.work）
- `cd examples/backend && go test ./internal/...`：执行 `internal/` 下的 Go 单元测试
- `cd examples/backend && python -m pytest tests/api -q`：运行 API 层 pytest 发现
- `cd examples/backend && python -m pytest tests/sit -v`：运行 SIT 测试；需要显式环境准备

请把 `make build`、`make run`、Docker 相关目标视为模板示例，除非范例已被具体化为真实项目。

## 编码风格与命名约定

遵循 Go 默认风格：
- 使用 tab 缩进
- 始终通过 `gofmt` 保持格式一致
- 导出标识符使用 `CamelCase`

接口命名保持清晰后缀，例如 `...DAOInterface`。Python 测试遵循 `test_*.py`、`Test*`、`test_*` 约定。

## 测试约定

Pytest 配置位于 `examples/backend/tests/pytest.ini`，fixture 分布在：
- `examples/backend/tests/api/`
- `examples/backend/tests/sit/`
- `examples/backend/tests/uat/`

范例目标测试分层是 UT、API、SIT、UAT，当前大部分内容为骨架。

注意事项：
- 不要随意运行 `tests/uat`
- 不要轻易修改与环境绑定的配置
- SIT/UAT fixture 可能连接真实 Kubernetes 和 PostgreSQL 环境
- 在未确认环境安全前，不要把 SIT/UAT 当作本地无害测试执行
- 测试用例通过 `@pytest.mark.trace` marker 承载追溯信息（定位符 `story`/`epic`/`endpoint` + 版本化源锚 `design="<doc>_vX.Y#<章节>"`），详见 `.claude/skills/qa/references/test_traceability.md`。`examples/backend/tests/` 已实例化：marker 注册（`pytest.ini`）、收集期校验（`conftest.py`）、规范示例（`_examples/`）。
- `@trace` 是 review 工具，非 MR 门禁：设计版本演进 / 章节重排 / story 退役时运行 `.claude/skills/qa/scripts/trace_drift.py` 做漂移检测（纯静态扫描，不开 pytest、不连 PG/K8s，环境安全）。

## 提交与 PR 规范

近期提交历史以 Conventional Commit 风格为主，例如：
- `fix(skills): ...`
- `feat(guide): ...`
- `docs(examples): ...`

提交信息应简洁、带作用域。PR 说明应明确：
- 这次改动是否仍然“模板安全”
- 影响了哪些目录或文件（主项目方法论 vs `examples/backend/` 范例）
- 做了哪些验证
- 是否仍存在未处理的占位符、外部依赖或环境风险

## 安全与配置提示

不要把 `examples/backend/etc/config/*.yaml` 视为默认可安全复用的本地配置；其中部分文件可能含环境特定值。不要在文档、提交说明或评审备注中复制敏感信息。

引用 `examples/backend/docs/design/` 下的设计文档前，先确认文件实际存在。

## 对代理的工作要求

- 当任务是“理解仓库”时，优先说明它是原型模板：主项目是方法论知识库，`examples/backend/` 是可编译的后端范例。
- 当任务是“修改仓库”时，先判断是在维护方法论/skills（主项目），还是在调整后端范例（`examples/backend/`）。
- 业务代码改动一律在 `examples/backend/` 内进行；主项目根目录不应新增业务实现。
- 如果用户没有明确要求具体化，优先做文档整理、模板泛化、说明补齐和结构澄清。
- 未经确认，不主动运行可能访问真实外部环境的测试或脚本。
- 编写 pytest 用例时，用 `@pytest.mark.trace` 标注追溯信息（定位符 + 版本化源锚 `design`），让用例集可被漂移检测器扫描；不把追溯信息散落在注释里。
