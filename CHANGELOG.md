# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [v2.1] - 2026-06-12

### Summary

v2.1 是 v2.0（去实现化重构）之后的**技能生态增强版本**，核心变更包括：Codex Agent 多引擎 Skill 适配、全部 9 个 Skill 的产品化规范化重构、文档体系大幅增强、以及全面的隐私脱敏处理。

### Added

- **Codex Agent Skill 适配层**（`.codex/skills/`，103 文件）
  - 支持多版本 AI Agent（Claude Code + Codex）并行 Skill 适配
  - 删除冗余 `CODEX.md`，功能已由 `.codex/skills/` 完整替代

- **新增 UED 技能**（`.claude/skills/ued/`）
  - 前端体验设计、组件开发、交互优化、原型生成
  - 包含 6 个 HTML 原型示例（chat/dashboard/dataviz/form/landing/mobile）

- **新增 spec-xchecker 技能**（`.claude/skills/spec-xchecker/`）
  - Design ↔ Scrum ↔ Code ↔ Tests 四路交叉验证工具
  - 实验性质技能，支持对齐一致性检查

- **新增 sentinel 技能**（`.claude/skills/sentinel/`）
  - 线上服务哨兵：健康检查、定期巡检、RCA、数据质量验证
  - 含自动化巡检脚本和配置模板

- **新增 refactor 技能**（`.claude/skills/refactor/`）
  - 安全重构：逻辑不变前提下的代码结构优化、命名改进
  - 包含代码坏味道识别和重构技法参考

- **AI-Native Development Guide Book v0.1.0-alpha**
  - 独立的 AI-Native 开发指南文档

- **GUIDE.md 协作原理可视化章节**
  - Agent Team 协作流程图、时序图、完整研发流程

- **GUIDE.md & Guide Book FAQ 内容**
  - GUIDE.md 插入 6 个 Part FAQ（20 条）
  - Guide Book 插入 5 个 Part FAQ（16 条）
  - 充实常见陷阱（4→6 条）

- **k8s 部署目录占位**（`deploy/`）

### Changed

- **PM skill v14.1-exp**
  - 扩展 Agent Team 至 9 人，新增领域描述和触发场景
  - 新增多意图编排能力（动态路由、上下文传递）
  - 增强 Story 状态 FSM 定义（8 状态完整转换矩阵）
  - 重命名 scrum_master → pm，统一命名

- **commit skill v2.2**
  - 重命名 code-committer → commit
  - 添加所有文件引用，充分利用技能资源
  - 极致压缩版本章节

- **dev skill v5.1**
  - 整合 naming-conventions 到代码风格章节

- **devops skill v2.0**
  - 优化渐进式披露精准度

- **arch skill v2.1**
  - 整合 documentation-versioning 内容

- **spec-xchecker v4.0**
  - 完全符合 Claude Code 官方文档标准
  - 规范化目录结构和渐进式披露

- **GUIDE.md 重构为操作手册**
  - 重构协作流程图和时序图的流程顺序
  - 修复 Mermaid 图表渲染问题
  - 统一 agent 命名规范

### Fixed

- **全面隐私脱敏处理**（4 轮迭代）
  - 第 1 轮：移除组织特化信息（邮箱/域名/IP/密码/namespace）
  - 第 2 轮：.claude/skills/ 下的隐私信息
  - 第 3 轮：人名/邮箱/内部域名
  - 第 4 轮：产品名/组织名/K8s 标签/IP/本地路径（深度脱敏）

- 清除 pm2 残留引用
- 删除废弃 scrum_master skill
- 修正 Guide Book 中 claude-code 为 claude
- 移除协作流程图中离散的 QA 节点

### Removed

- `CODEX.md` — 功能已由 `.codex/skills/` 替代
- 废弃的 scrum_master skill — 已重命名为 pm
- 项目特定和设计文档类型的 SKILL 文件

### Stats

| 指标 | 数值 |
|------|------|
| 提交数量 | 45 |
| 时间跨度 | 2026-04-29 ~ 2026-06-12 |
| 新增 Skill | ued / spec-xchecker / sentinel / refactor |
| Skill 重构 | pm / commit / dev / devops / arch |
| 脱敏迭代 | 4 轮 |

---

## [v2.0] - 2026-04-28

### Changed

- **去实现化重构**：移除所有业务逻辑实现，仅保留框架代码
- 保留内容：目录结构、分层架构示例、DAO 接口定义、数据模型、测试骨架、设计文档、Docker/Helm 模板

---

## [v1.0] - 2026-02-04

### Added

- 初始版本：AI-native 项目原型工程 / 架构模板
- 分层架构：Handler → Logic → DAO → Model
- 技术栈：Go 1.24+ / go-zero / GORM / PostgreSQL / Kubernetes
- 四层测试策略：UT / API / SIT / UAT
- DevOps：Docker / Kubernetes / Helm Charts / GitLab CI
