# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [Unreleased]

待发布变更占位。

---

## [v0.3.0] - 2026-08-08

### Summary

首个打 tag 的版本。确立仓库为**原型模板（archetype）形制**：主项目根目录承载方法论与 agent skills,业务实现范例集中在 `examples/backend/`(独立 Go module `example-service`)。

### Added

- **`examples/backend/` 完整 Go 工程范例**（独立 module `example-service`）
  - 业务骨架:`main.go` / `go.mod` / `go.sum` / `Makefile` / `pyproject.toml`
  - 分层目录:`internal/`(config / dao / handler / logic / middleware / model / pkg / svc / types)
  - 配置框架:`etc/config/`(`*.yaml.template` + 范例配置)
  - 部署模板:`deploy/`(Docker Compose 模板 + Kubernetes Helm Charts 占位)
  - 测试骨架:`tests/`(api / sit / uat / regression,pytest)
  - 设计文档:`docs/design/`(服务层架构、服务层 FAQ、API 设计、数据层设计模板)
- **Agent Skills 体系**(11 个,`.claude/skills/` + `.codex/skills/`)
  - `arch`(架构设计)、`dev`(开发实现)、`qa`(测试验证)、`devops`(部署运维)、`pm`(项目管理)、`commit`(代码提交)、`refactor`(安全重构)、`sentinel`(线上巡检)、`spec-xchecker`(四路对齐检查)、`ued`(前端体验)
  - `.codex/skills/` 为 Codex agent 的对应适配层
- **方法论文档**
  - `GUIDE.md`:AI-Native 开发完整指南(Agent Team 协作原理、研发流程)
  - `docs/guides/ai_native_development_guide_book.md`:开发方法论专著
  - `AGENTS.md`、`CLAUDE.md`、`README.md`、`CHANGELOG.md`:仓库使用与协作指南

### Changed

- **根目录聚焦为 archetype 模板**:仅保留方法论文档、agent skills、指南,不含任何业务实现
- **业务实现下沉至 `examples/backend/`**:目录结构、分层架构、DAO 接口定义、数据模型、配置/部署模板、测试框架均在该子目录内自包含

### Removed

- 主项目根目录的 Go 业务实现(`internal/`、`main.go`、`go.mod`、`go.sum`、`Makefile`)
- 主项目根目录的部署配置(`deploy/`、`etc/`、`scripts/`)
- 主项目根目录的测试套件(`tests/`、`pyproject.toml`、`pytest.ini`)
- 主项目根目录的 CI 配置(`.gitlab-ci.yml`)
- 主项目根目录的项目管理类记录

### Stats

| 指标 | 数值 |
|------|------|
| 仓库结构 | 双层(主项目方法论 + `examples/backend/` 范例) |
| Skill 数量 | 11 |
| 范例 module | `example-service`(Go 1.24 + go-zero v1.8.3) |
| 技术栈 | Go / go-zero / GORM / PostgreSQL / client-go(K8s) |
| 测试分层 | UT / API / SIT / UAT |

---

## Pre-release history (2026-04-29 ~ 2026-08-08)

v0.3.0 之前的提交序列(本仓库初始化与演进,详见 `git log`):

| 日期 | Commit 主题 |
|------|------------|
| 2026-08-08 | `chore(skills): 更新多个 skill 的脚本与模板` |
| 2026-06-12 | `docs: 新增多工程并行开发用户场景,升级至 v0.2.0-alpha` |
| 2026-06-12 | `docs refinement & codex skill support` |
| 2026-06-04 | `docs: 添加 CHANGELOG.md 记录 v2.1.0 版本更新` |
| 2026-06-03 | `skill: update agent team` |
| 2026-05-30 | `chore(skills): 更新 pm/ued 模板占位符格式` |
| 2026-04-29 | `docs: 移除 README.md 更新日志部分` |
| 2026-04-29 | `initial: agent-team-archetype v2.0` |
