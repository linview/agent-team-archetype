# Changelog

All notable changes to agent-team-archetype will be documented in this file.

## [2.1.0] - 2026-06-03

> 强化 `/pm` 为总入口角色，支持意图识别与动态路由；新增 `/ued` 前端交互设计角色；增强 `/qa` 测试分层定义并支持 E2E 测试；`/pm` 支持 FSM 管理 story 状态流转。

项目地址：https://git.example.com/user/agent-team-archetype

### 重大更新

#### /pm — 意图识别与动态路由

- 强化 `/pm` 作为团队总入口的角色，具备**意图识别**和**动态路由**能力
- 用户只需描述需求，`/pm` 自动分派给合适的角色执行
- 新增 FSM（有限状态机）管理 story 状态，提供清晰的进度定义和状态流转规则 (`references/story_status_fsm.md`)
- 重构 story 状态更新工作流，支持更精细的任务生命周期管理 (`references/story_status_update_workflow.md`)

#### /ued — 全新前端视觉交互角色

- 新增 `/ued` 角色，负责前端视觉交互设计方案的开发
- 内置完整的原型设计参考：聊天界面、仪表盘、数据可视化、表单、落地页、移动端等 6 种原型模板 (`examples/`)
- 提供框架选型指南 (`references/framework-guide.md`)、原型设计方法论 (`references/prototype-guide.md`)、视觉设计规范 (`references/visual-design-guide.md`)
- 包含交互流程 (`templates/interaction_flow.md`) 和线框图 (`templates/wireframe.md`) 模板
- 集成 ECharts 生命周期 (`references/echarts-lifecycle.md`)、编码模式 (`references/encoding-patterns.md`) 等工程化参考

#### /qa — 增强测试分层定义

- 重构 `/qa` 技能，精简主文档，采用渐进式披露
- 新增测试分层明确定义：UT / API / SIT / UAT / E2E，支持 **E2E 测试类型** (`references/testing_layer_definitions.md`)
- 新增测试幂等性指南 (`references/test_idempotency.md`)、UT 覆盖率指南 (`references/ut_coverage_guide.md`)
- 新增测试排障手册 (`references/troubleshooting.md`)

### 其他改进

- **/commit**: 优化 GitLab API 脚本和 MR 创建排障指南
- **/dev**: 更新 git-workflow 脚本
- **/sentinel**: 更新配置管理说明
- **模板**: 统一 pm 模板占位符格式（epic、story、kanban、sprint 等）
- **docs**: 移除 README.md 中过时的更新日志部分

---

## [2.0.0] - 2026-04-29

### 重大变更

- **去实现化重构**：转型为纯原型工程，移除所有业务逻辑实现，仅保留框架代码和接口定义
- **技能产品化**：所有 Skill（`/arch`、`/dev`、`/qa`、`/devops`、`/commit`）完成去项目化、产品化改造
- **Skill 重命名**：统一技能命名规范 — `architect` → `arch`、`developer` → `dev`、`scrum_master` → `pm`、`code-committer` → `commit`、`regular-checker` → `sentinel`
- **AI-Native 开发指南**：创建 Guide Book v0.1.0-alpha，新增 Agent Team 协作原理可视化（协作流程图、时序图）
- **spec-xchecker**：实验性规格校验工具，从 v3.0 迭代至 v4.0，符合 Claude Code 官方文档标准

### 架构

- 分层架构：Handler → Logic → DAO（接口化）→ Model
- 技术栈：Go 1.24+ / go-zero / GORM / PostgreSQL / Kubernetes
- 四层测试策略：UT / API / SIT / UAT
- 部署模板：Docker Compose（本地开发）+ Helm Charts（K8s 部署）

---

## [1.0.0] - 2026-02-04

### 初始版本

- Agent Team Archetype 框架 v1.0
- 初始 Skill 定义：`architect`、`developer`、`qa`、`devops`、`scrum_master`
- 基础项目结构：分层架构、部署模板、测试框架
