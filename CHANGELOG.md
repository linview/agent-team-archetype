# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [v2.5] - 2026-07-30

### Summary

v2.5 是 QA 技能的可追溯性**收紧**版本。修复 v2.4 `@trace` 机制在 **Python 栈**下的一个误用风险:`VALID_AC` 原含 `"UT"`,在框架校验层放行 `ac="UT"`,会诱导 QA 给 UT 用例打 `@trace`——而 UT 的唯一真实来源是**代码符号**(被测函数本身),不是设计文档,`@trace` 的 `design` 版本源锚对 UT 语义错配(锚错来源)。本次将 UT 移出 `@trace` 范围:`VALID_AC` 仅保留 `API/SIT/E2E/UAT`,`ac="UT"` 触发专属引导 issue;文档「唯一真实来源」表、test_traceability.md §3 §6、GUIDE.md 由"可选"统一改"不适用 `@trace`"。**UT 测试层与 pm `[UT]` AC 门禁不受影响**(UT↔代码追溯仍由 spec-xchecker CT 层 symbol↔test_ 负责,不经 @trace)。

### Changed

- **qa skill:UT 移出 `@trace` 标注范围**(SKILL.md v7.2 → v7.3)
  - `assets/trace_framework.py`:`VALID_AC` 移除 `"UT"`(仅留 API/SIT/E2E/UAT);`_validate_kwargs` 对 `ac="UT"` 报专属引导 issue;`__main__` 自测加 `bad/ut-not-allowed`——同步 `.claude` / `.codex` / `examples/backend/tests` 三份
  - `scripts/trace_drift.py`:`VALID_AC` 同步移除 UT(`.claude` / `.codex`)
  - 文档措辞收紧:SKILL.md「唯一真实来源」表、`references/test_traceability.md`(§2 schema 注释、§3 层↔锚映射表、§6 能力边界)、GUIDE.md §4.5.1 映射表——UT 由"可选 design 锚"改"不适用 `@trace`";`.codex` 镜像同步
  - 边界:UT 仍是测试金字塔最底层、UT 覆盖率统计不动、pm `[UT]` AC 验收门不动(IN_PROGRESS 需 [UT] 全通过,按 AC 签字率)
- **防偏机制**(把 v7.2 偏差教训沉淀为约束):`assets/trace_framework.py` 新增 `VALID_AC ↔ SSOT` 元不变式(`_AC_SSOT`/`_AC_EXCLUDED` + `_assert_validac_ssot_alignment` 自测断言),未来改 ac 枚举不同步改 SSOT 映射即自测报警(反向验证:加 UT 回枚举必触发);`references/test_traceability.md` §3 新增「增强 @trace 时的语义对齐自检」三问(SSOT 是什么 / 被哪个锚覆盖 / 换栈是否成立)——机器约束 + 人工准则双保险,防止单一范例栈(Go)掩盖跨栈(Python)语义错配

### Stats

| 指标 | 数值 |
|------|------|
| qa skill 版本 | v7.2 → v7.3 |
| 改动性质 | 收紧(UT 移出 @trace 范围),非新增能力 |
| 影响范围 | UT 测试层与 pm `[UT]` AC 门禁不受影响 |
| 定位 | review 工具(非 MR 门禁),与 spec-xchecker 互补 |

## [v2.4] - 2026-07-29

### Summary

v2.4 是 QA 技能的可追溯性增强版本。围绕"测试与需求/设计是 N:M 关系"的建模，qa skill 新增 **`@pytest.mark.trace` marker**（定位符 + 版本化源锚两维度）与**设计漂移检测器**，让用例集随设计迭代**新陈代谢**：每个用例记录创建时对应的 design 版本（历史快照，不随设计自动更新），设计演进时由检测器自动暴露过期用例，由分层 review 决定 update / retire / add。配套方法论、可复制框架代码、静态检测器与 `examples/backend` 实例化一并落地。本特性是 Design↔Test 维度的 review 闭环，与 `/spec-xchecker` 的静态对齐检查互补；定位为 **review 工具而非 MR 门禁**，不影响 pm 的 Story 状态门禁（仍按 AC 签字率）。

### Added

- **qa skill：测试可追溯性 + 设计漂移检测**（SKILL.md v7.1 → v7.2）
  - 新增 `@pytest.mark.trace` marker，两维度追溯：**定位符**（`story`/`epic`/`endpoint` 三选一，"一测一主功能锚"）+ **版本化源锚**（`design="<doc>_vX.Y#<章节>"`，历史快照）
  - 新增方法论参考 `references/test_traceability.md`：关系非属性论证、源锚 = 历史快照（化解"腐烂副本"批评）、层↔锚对角映射、非对角测试规则、4 态检测、能力边界
  - 新增可复制框架代码 `assets/`：`trace_framework.py`（marker 工厂 + 收集期校验 hook）、`test_trace_example.py`（五种写法示例）、`pytest_trace_marker.ini.snippet`（marker 注册行）
  - 新增静态漂移检测器 `scripts/trace_drift.py`：regex 扫 `@trace` → 对比 design 当前版本与章节存在性 → 查 story 状态，输出 4 态报告（同步 / 版本漂移 / 章节漂移 / 悬空）；纯静态，不开 pytest、不连 PG/K8s，环境安全
  - SKILL.md 新增「分层用例 review」节；「设计文档是唯一真实来源」表扩为 5 行（UT/API/SIT/E2E/UAT，保持 UAT = PRD@Epic 粒度）
- **`examples/backend/` 范例实例化**：marker 注册（`tests/pytest.ini`）、收集期校验接入（`tests/conftest.py` → `validate_trace_items`）、框架代码（`tests/trace_framework.py`）、规范示例（`tests/_examples/test_trace_example.py`，不在 `testpaths`，零回归污染）
- **文档同步**：GUIDE.md 新增 Part 4.5「测试可追溯性与设计漂移检测」节、Part 4 FAQ 与 Part 6.2 呼应；AGENTS.md 测试约定与代理工作要求增补

### Changed

- **`.codex/skills/qa/`** 同步对齐 `.claude/skills/qa/`（保留 Codex 适配层）
- GUIDE.md 版本 v2.0 → v2.4，更新日期 2026-07-29
- **Guide Book v0.1.0-alpha → v0.2.0-alpha**（`docs/guides/ai_native_development_guide_book.md`）：对齐 archetype 双层结构（§15.1）、Agent Team 10 角色表（§7.2 / §11.1）、5 层测试金字塔增 E2E + SIT 交叉验证（§6）；建立「指南版本 ↔ 项目 CHANGELOG 同步关系」机制（对应规则表 + 同步触发规则 + 流程卡点），使指南可随项目版本持续迭代

### Stats

| 指标 | 数值 |
|------|------|
| qa skill 版本 | v7.1 → v7.2 |
| 新增能力 | `@trace` marker / 漂移检测器 / 方法论参考 / 可复制框架代码 |
| SKILL.md 改动 | +64 行（主文档新增 review 节与资源索引） |
| 范例实例化 | pytest.ini + conftest.py + trace_framework.py + _examples/ |
| 定位 | review 工具（非 MR 门禁），与 spec-xchecker 互补 |
| 破坏性变更 | 无（新增 marker 与脚本，不影响现有测试与门禁） |

---

## [v2.3] - 2026-07-17

### Summary

v2.3 是项目结构落定版本，延续 v2.0 的去实现化主线。将业务实现从主项目整体搬迁至 `examples/backend/`，形成独立可运行的 Go 范例 module（`example-service`）；主项目彻底净化为纯 archetype（原型模板），仅保留框架、接口定义与文档。确立"**模板（主项目）+ 范例（examples/backend）**"的双层结构，使主项目可直接作为新项目脚手架复制使用。

### Added

- **`examples/backend/` 独立范例 module**（`module example-service`，MR !3）
  - 完整可运行的 Go 业务范例：`main.go` / `go.mod` / `go.sum` / `Makefile` / `pyproject.toml`
  - 业务实现层：`internal/`（config / dao / handler / model / pkg / svc / types）
  - 配套资源：`etc/`（配置）/ `tests/`（API / SIT / UAT）/ `deploy/`（部署模板）/ `docs/`（业务文档与 scrum 工件）

### Changed

- **主项目彻底净化为 archetype 模板**
  - 业务实现（`internal/`）、配套资源、业务文档整体迁出至 `examples/backend`
  - 主项目回归 `CLAUDE.md` 定义的原型工程定位：仅保留目录结构、分层架构示例、DAO 接口定义、数据模型、测试骨架、设计文档与部署模板
- **业务文档与配置迁移至 `examples/backend/` 并完成脱敏**
- 确立"模板 + 范例"双层项目结构，主项目与范例实现物理隔离

### Removed

- 主项目根目录 `go.mod` — 业务 module 迁出，主项目不再作为可运行 Go 服务
- `scripts/`（`generalize.py` / `README.md`）— 业务脚本随实现迁出

### Stats

| 指标 | 数值 |
|------|------|
| 合并 MR | !3 `feat/relocate-to-examples-backend` → `master`（`ef49e82`） |
| 业务 commit | 4（骨架搭建 / 资源搬迁 / 文档搬迁 / 主项目净化） |
| 变更文件 | 59（+453 / -670） |
| 新增独立 module | `example-service` |
| 破坏性变更 | 无（原型工程，无生产 API） |

---

## [v2.2] - 2026-06-16

### Summary

v2.2 是技能质量修复与增强版本。spec-xchecker 修复了 AC 驱动策略引擎的运行时静默失效（恢复核心功能）并提升 AC 提取与 Design Spec 引用判定精度；pm 新增 DEFERRED 状态追踪与动态看板行数校验。全部变更经实测验证，无破坏性接口变更。

### Added

- **pm skill：DEFERRED（已延迟）状态全链路追踪**
  - audit 统计 / kanban 泳道 / render 分组 / dashboard 模板协同支持 DEFERRED
  - 待办（todo）计算同步扣除 deferred，避免延迟项被重复计入待办
  - 向后兼容旧 metadata（`.get` / `|default(0)`）

### Fixed

- **spec-xchecker：修复 AC 驱动策略引擎运行时静默失效**
  - 主入口对齐 v2.5 策略 API（`generate_strategy()` 返回 dict，`final_checks`）
  - 修复后实测 Story 6-04：0 检查项 → 11 检查项（3 通过 / 8 失败）
- **spec-xchecker：策略报告键名与置信度格式**
  - 报告键名 `checks` → `final_checks`；置信度 `:.1%` → `:.1f}%`（避免 88.0 被渲染成 8800.0%）
- **spec-xchecker：`_check_pattern_in_content` 兼容 str/dict**
  - 修复对 `List[str]` 类型 AC 调 `.get` 导致的 AttributeError
- **spec-xchecker：AC 章节正则精度**
  - 结束符 `^(##\s*)` → `^(?=##\s)`，修复 `### AC-x` 子标题被误判为章节结束、导致 AC 整段截断丢失
- **spec-xchecker：DS-01 / DS-03 假阴性修复**
  - 新增 `design_spec_content` 短路判定，修复 Story 仅以 frontmatter `design_docs` 引用时旧正文正则漏判
- **pm skill：动态看板行数校验**
  - 固定下限（KANBAN 100 行 / DASHBOARD 80 行）改为 `max(25, n*5)` / `max(20, n*3)`，修复小项目被旧阈值误判为退化而拒绝写入

### Stats

| 指标 | 数值 |
|------|------|
| 技能改动提交 | 3 批（spec-xchecker ×2 + pm ×1） |
| spec-xchecker 实测对比 | 0 检查 → 11 检查 |
| pm 端到端验证 | KANBAN 55 行 / DASHBOARD 44 行均通过校验 |
| 破坏性变更 | 无 |

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
