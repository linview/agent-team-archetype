# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [Unreleased]

待发布变更占位。

---

## [v2.12.0] - 2026-11-25

### Summary

Agent Skills 体系整体升级（`.claude/skills/` 与 `.codex/skills/` 双栈内容保持一致；153 个文件，+8634 / −5966）。本批变更三条主线：arch 的设计文档治理能力、sentinel 的引擎化重构、pm / qa / commit 的流程细则化。另：仓库采用 MIT 许可证，两份指南文档同步对齐本版能力。

### Added

- **License**：添加 MIT `LICENSE`，README 补充许可声明
- **arch（升级至 v2.5）— 设计文档治理**
  - 设计变更三步流程：analysis → POC → design update，假设驱动分级 + 三条铁律；细则与模板见 `references/design_iteration_sop.md`、`templates/analysis_doc_template.md`
  - 成稿可读性纪律：去黑话铁律、frontmatter→TOC→正文渐进式加载、语义 review 五问，见 `references/doc_readability_guide.md`
  - 图表运用指南：按概念类型选型（mermaid 默认 / ASCII 回退）、/ued 与 /pm 转介边界，见 `references/diagram_guide.md`
  - `scripts/doc_structure_check.py`：成稿结构自检脚本（frontmatter / TOC / 编号纪律 / 相对链接 / test_reports 引用拦截），支持 skill 指引 → hook → CI 三层执行
  - `references/review_checklist.md`：设计文档更新前后 5 组过检清单
- **sentinel — 引擎化重构**
  - 新增 `scripts/sentinel_engine/`（19 个模块）：schema / resolver / runner / assertion / register / reporter / cli
  - 新增探针 7 类 `probes/`（api_query、api_smoke、db_query、http_probe、log_grep、metrics_scrape、schedule_liveness）与数据源工具 2 类 `tools/`（pg_fetcher、mysql_fetcher）
  - 新增向导式接入：`references/wizard_onboarding.template.md` + `templates/wizard_templates/` 三套声明模板（backend_api / data_etl / data_db）
- **pm**
  - 新增 `references/issue_management.md`：Issue 管理规范（独立于 Story 的 bug / 问题跟踪，与 Story「要做的事」明确区分）
  - 新增 `references/release_versioning.md`：发布版本规划细则（semver 2.0.0 + Keep a Changelog 通用能力）
  - 新增 `templates/issue_template.md`
- **qa**
  - 新增 `references/test_taxonomy.md`（v2.0）：测试分类学执行准则（判型 → 归属 → 标注，按 oracle 区分测试类型）
- **commit**
  - 新增 `scripts/feishu-validator.sh`：飞书项目工作项验证（检查 YAML front matter）
  - MR 模板六类（feature / bugfix / hotfix / docs / ci-cd / refactoring）统一更新

### Changed

- arch / commit / dev / pm / qa / spec-xchecker / refactor / ued 各 SKILL.md 与配套脚本按上述新能力扩展；commit 侧 `code-committer.sh`、`gitlab-api.sh`、`audit-checker.sh`、`code-committer.yaml`、`commit-conventions.md` 更新
- `GUIDE.md` 升级至 v2.6、`docs/guides/ai_native_development_guide_book.md` 升级至 v0.3.0：对齐本版 skill 能力（设计变更三步流程、sentinel 引擎化、测试分类学），补充方法论文图
- sentinel SKILL.md 重写为向导式接入 + 声明驱动的用法说明
- spec-xchecker：checker 设计与报告生成脚本更新（`checker_design.py`、`report_generator.py`、`lib/`），修订内存目录路径示例注释
- dev：`git-workflow.skill.sh` 与 SKILL.md 工作流细化
- `.codex/skills/` 全量对齐 `.claude/skills/` 当前内容（移除 simple-admin-workflow 后双栈均为 10 个 skill）

### Removed

- sentinel 旧脚本方案：`inspect`、`run_inspection.sh`、`load_config.sh`、`generate_md_report.py`、`inspection_config.yaml.template`（由 sentinel_engine 声明驱动引擎替代）
- `.codex/skills/simple-admin-workflow/`（`SKILL.md`、`references/workflow-complete.md`）

### Stats

| 指标 | 数值 |
|------|------|
| 变更规模 | 153 files，+8634 / −5966 |
| Skill 数量 | 双栈各 10（Codex 栈移除 simple-admin-workflow） |
| sentinel 新引擎 | sentinel_engine（19 模块：探针 7 类 + 数据源工具 2 类） |
| arch skill 版本 | v2.5（新增 references 4 篇 + 自检脚本 + analysis 模板） |
| 指南文档 | GUIDE.md v2.6 + guide book v0.3.0 |

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
