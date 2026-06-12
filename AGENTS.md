# 仓库工作指南

## 仓库定位

这是一个 AI-native **原型模板仓库**，不是可直接交付的生产服务。仓库的主要价值在于项目结构、分层示例、接口骨架、测试框架和设计文档，而不是可运行的业务实现。

默认判断：
- 除非用户明确要求，否则不要把这个仓库补全成具体业务系统。
- 优先保持“模板 / 原型”属性，不要无意引入项目私有实现。

## 项目结构与模块组织

核心 Go 骨架位于 `internal/`：
- `config/`：配置结构体定义
- `dao/`：数据访问接口
- `model/`：数据模型
- `types/`：共享 API 类型

`handler/`、`logic/`、`middleware/`、`pkg/`、`svc/` 目前主要是占位目录。文档位于 `docs/`，部署与运行模板位于 `deploy/` 和 `etc/config/`，测试骨架位于 `tests/`。

需要注意的真实状态：
- 仓库中仍残留 `resource-meter` 历史内容
- 仍存在 `{PROJECT_NAME}` 等模板占位符
- `main.go` 中存在非法 import path，因此当前并非可直接构建状态
- `Makefile` 中部分目标仍引用旧项目名或缺失文件

## 构建、测试与开发命令

- `make fmt`：使用 `gofmt -s -w .` 格式化 Go 代码
- `make lint`：运行 `golangci-lint`
- `go test ./...`：执行全量 Go 测试；在当前仓库中通常会因为模板占位符未清理而失败
- `go test ./internal/...`：仅验证 `internal/` 下框架代码
- `python -m pytest tests/api -q`：运行 API 层 pytest 发现
- `python -m pytest tests/sit -v`：运行 SIT 测试；需要显式环境准备

请把 `make build`、`make run`、Docker 相关目标视为模板示例，除非仓库已经先被具体化并修复占位符问题。

## 编码风格与命名约定

遵循 Go 默认风格：
- 使用 tab 缩进
- 始终通过 `gofmt` 保持格式一致
- 导出标识符使用 `CamelCase`

接口命名保持清晰后缀，例如 `...DAOInterface`。Python 测试遵循 `test_*.py`、`Test*`、`test_*` 约定。若任务不是“将模板具体化”，则保留占位符导向的命名方式。

## 测试约定

Pytest 配置位于 `tests/pytest.ini`，fixture 分布在：
- `tests/api/`
- `tests/sit/`
- `tests/uat/`

仓库目标测试分层是 UT、API、SIT、UAT，但当前大部分内容仍是骨架。

注意事项：
- 不要随意运行 `tests/uat`
- 不要轻易修改与环境绑定的配置
- SIT/UAT fixture 可能连接真实 Kubernetes 和 PostgreSQL 环境
- 在未确认环境安全前，不要把 SIT/UAT 当作本地无害测试执行

## 提交与 PR 规范

近期提交历史以 Conventional Commit 风格为主，例如：
- `fix(skills): ...`
- `feat(guide): ...`
- `docs: ...`

提交信息应简洁、带作用域。PR 说明应明确：
- 这次改动是否仍然“模板安全”
- 影响了哪些目录或文件
- 做了哪些验证
- 是否仍存在未处理的占位符、外部依赖或环境风险

## 安全与配置提示

不要把 `etc/config/*.yaml` 视为默认可安全复用的本地配置；其中部分文件可能含环境特定值。不要在文档、提交说明或评审备注中复制敏感信息。

引用 `docs/design/` 下的设计文档前，先确认文件实际存在；部分索引文档仍可能指向历史路径或旧版本文件。

## 对代理的工作要求

- 当任务是“理解仓库”时，优先说明它是原型模板、当前不可直接运行，以及哪些内容是历史残留
- 当任务是“修改仓库”时，先判断是在维护模板，还是在把它具体化为真实项目
- 如果用户没有明确要求具体化，优先做文档整理、模板泛化、说明补齐和结构澄清
- 未经确认，不主动运行可能访问真实外部环境的测试或脚本
