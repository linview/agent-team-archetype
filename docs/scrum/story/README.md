# Story 目录说明

**目录用途**: 用户故事（User Story）和开发任务文档

**文档类型**: Story（具体执行步骤）

**项目**: {BUSINESS_DESCRIPTION}服务（{PROJECT_NAME}）

**组织方式**: 平铺式组织，按 Epic 序号前缀分类

---

## 当前状态总览

### Epic 进度概览

| Epic ID | Epic 名称 | 状态 | Stories | 已完成 | 进行中 | 未开始 | 完成度 |
|---------|-----------|------|---------|--------|--------|--------|--------|
| EPIC-0 | Bug 修复与生产问题 | IN_PROGRESS | 1 | 0 | 1 | 0 | 0% |
| EPIC-1 | 项目脚手架搭建 | IN_PROGRESS | 3 | 1 | 2 | 0 | 33% |
| EPIC-2 | Docker Compose 开发环境 | COMPLETED | 2 | 2 | 0 | 0 | 100% |
| EPIC-3 | 数据库迁移 | PLANNED | 2 | 0 | 0 | 2 | 0% |
| EPIC-4 | Dockerfile 与 ArgoCD 部署 | IN_PROGRESS | 2 | 1 | 0 | 1 | 50% |
| EPIC-5 | 数据层实现 | PLANNED | 3 | 0 | 0 | 3 | 0% |
| EPIC-6 | 服务层实现 | PLANNED | 5 | 0 | 0 | 5 | 0% |
| EPIC-7 | 应用层实现 | PLANNED | 3 | 0 | 0 | 3 | 0% |
| EPIC-8 | 测试与部署 | IN_PROGRESS | 8 | 0 | 0 | 8 | 0% |

**总计**: 24 Stories，**5 个已完成**，**3 个进行中**，**整体完成度约 21%**

### Story 详细状态

| Story ID | Story 标题 | 状态 | 完成日期 | 备注 |
|----------|-----------|------|----------|------|
| STORY-0-01 | P0 Bug Fix: PostgreSQL 序列不同步导致主键冲突 | 🔄 IN_PROGRESS | - | **紧急修复**，序列已同步，待代码修复 |
| STORY-1-01 | 使用 goctl 创建项目脚手架 | ✅ COMPLETED | 2026-01-31 | 项目结构完整 |
| STORY-1-02 | 多环境配置文件结构 | 🔄 IN_PROGRESS | - | 环境变量替换未实现 |
| STORY-1-03 | Makefile 和 .gitlab-ci.yml | 🔄 IN_PROGRESS | - | ArgoCD 触发待 EPIC-4 |
| STORY-2-01 | PostgreSQL + Redis 服务 | ✅ COMPLETED | 2026-01-31 | Docker Compose 配置完成 |
| STORY-2-02 | API 服务集成 | ✅ COMPLETED | 2026-01-31 | 一键启动完成 |
| STORY-3-01 | 数据库迁移脚本 | ⏳ TODO | - | **Sprint 1 优先级 P0** |
| STORY-3-02 | 种子数据初始化 | ⏳ TODO | - | **Sprint 1 优先级 P0** |
| STORY-4-01 | 生产环境 Dockerfile | ✅ COMPLETED | 2026-01-31 | Dockerfile 已创建 |
| STORY-4-02 | ArgoCD 和 K8s 部署 | ⏳ TODO | - | **Sprint 3 优先级 P1** |
| STORY-5-01 ~ 5-03 | 数据层实现 | ⏳ TODO | - | **Sprint 1 优先级 P0** |
| STORY-6-01 ~ 6-05 | 服务层实现 | ⏳ TODO | - | **Sprint 2 优先级 P0** |
| STORY-7-01 ~ 7-03 | 应用层实现 | ⏳ TODO | - | **Sprint 3 优先级 P1** |
| STORY-8-01 ~ 8-06 | 测试框架与 CI/CD | ⏳ TODO | - | **Sprint 4 优先级 P1** |
| STORY-8-07 | 测试框架快速改进 | ⏳ TODO | - | **基于 Review 报告 - 阶段1 (P1)** |
| STORY-8-08 | 测试基础设施建设 | ⏳ TODO | - | **基于 Review 报告 - 阶段2 (P1)** |

---

## 文档元数据规范

每个 Story 文档必须包含以下 YAML front matter 元数据：

```yaml
---
id: "STORY-X-YY"                 # Story ID: X=Epic序号, YY=Story序号
epic_id: "EPIC-X"               # 所属 Epic ID
title: "Story 标题"              # Story 名称
description: "Story 描述"        # 简要描述
status: "TODO"                   # 状态: TODO, IN_PROGRESS, IN_REVIEW, COMPLETED, BLOCKED
priority: "P1"                   # 优先级: P0, P1, P2, P3
story_points: 5                  # 故事点（估算工作量）
assignee: "负责人"               # 负责人
reviewer: "评审人"               # 评审人
start_date: "2026-01-31"         # 开始日期
target_date: "2026-02-05"        # 目标完成日期
dependencies:                    # 依赖的其他 Story
  - "STORY-X-00"
tags:                            # 标签
  - "database"
  - "postgresql"
acceptance_criteria:             # 验收标准
  - "标准 1"
  - "标准 2"
definition_of_done:              # 完成定义
  - "代码已提交并通过 Review"
  - "单元测试覆盖率 > 80%"
  - "文档已更新"
version: "1.0"                   # 文档版本
created_at: "2026-01-31"         # 创建日期
updated_at: "2026-01-31"         # 更新日期
---
```

---

## Story 文件组织结构

```
story/
├── README.md                           # 本文件
│
│── EPIC-0: Bug 修复与生产问题
├── story-0-01-sequence-sync-bug.md     # P0 Bug Fix: PostgreSQL 序列不同步
│
│── EPIC-1: 项目脚手架搭建
├── story-1-01-scaffolding.md          # 使用 goctl 创建项目脚手架
├── story-1-02-multi-env-config.md     # 多环境配置管理
├── story-1-03-makefile-ci.md          # Makefile 和 CI/CD 配置
│
│── EPIC-2: Docker Compose 开发环境
├── story-2-01-docker-compose-db.md    # PostgreSQL 容器配置
├── story-2-02-docker-compose-api.md   # API 服务容器配置
│
│── EPIC-3: 数据库迁移
├── story-3-01-migrate-scripts.md      # 数据库迁移脚本
├── story-3-02-seed-data.md            # 种子数据初始化
│
│── EPIC-4: Dockerfile 与 ArgoCD 部署
├── story-4-01-dockerfile-prod.md      # 生产环境 Dockerfile
├── story-4-02-argocd-k8s.md           # ArgoCD 和 K8s 部署配置
│
│── EPIC-5: 数据层实现
├── story-5-01-cmdb-dao.md             # CMDB 数据访问实现
├── story-5-02-devpod-dao.md           # DevPod 数据访问实现
├── story-5-03-connection-pool.md      # 数据库连接池配置
│
│── EPIC-6: 服务层实现
├── story-6-01-informer-integration.md # K8s Informer 集成
├── story-6-02-pod-handler.md          # Pod 事件处理器
├── story-6-03-metadata-extractor.md   # Pod 元数据提取器
├── story-6-04-calculation-engine.md   # {BUSINESS_SHORT}计算引擎
├── story-6-05-active-pod-{BUSINESS_DOMAIN}.md # 活跃 Pod {BUSINESS_SHORT}实时计算
│
│── EPIC-7: 应用层实现
├── story-7-01-api-design.md           # API 设计与代码生成
├── story-7-02-usage-api.md            # {BUSINESS_SHORT}查询 API 实现
├── story-7-03-auth-doc.md             # API 认证和文档
│
│── EPIC-8: 测试与部署
├── story-8-01-integration-tests.md     # 集成测试
├── story-8-02-prod-deployment.md        # 生产环境部署
├── story-8-03-monitoring-alerting.md   # 监控和告警
├── story-8-04-sit-pytest.md            # SIT 测试框架
├── story-8-05-expand-test-coverage.md  # 提升测试覆盖率
├── story-8-06-log-rotation.md          # K8s Event 日志轮转配置
├── story-8-07-testing-framework-quick-wins.md  # 测试框架快速改进 ✨ 新增
└── story-8-08-testing-infrastructure.md        # 测试基础设施建设 ✨ 新增
```

---

## Story 状态说明

| 状态 | 说明 | 可转换至 |
|------|------|---------|
| `TODO` | 待开始 | IN_PROGRESS, BLOCKED |
| `IN_PROGRESS` | 开发中 | IN_REVIEW, BLOCKED |
| `IN_REVIEW` | 评审中 | COMPLETED, IN_PROGRESS（需修改） |
| `COMPLETED` | 已完成 | - |
| `BLOCKED` | 已阻塞 | IN_PROGRESS（阻塞解除后） |

---

## Story 与 Epic 关联规则

1. **多对一关系**：多个 Story 属于一个 Epic
2. **命名约定**：
   - Story ID: `STORY-{Epic序号}-{Story序号:02d}`
   - Epic-1 的 Story: `STORY-1-01`, `STORY-1-02`, `STORY-1-03`
   - Epic-5 的 Story: `STORY-5-01`, `STORY-5-02`, `STORY-5-03`
3. **双向追踪**：
   - Story 通过 `epic_id` 字段指向所属的 Epic
   - Epic 通过 `stories` 字段列出关联的 Story

---

## 故事点（Story Points）估算

| 故事点 | 预估工时 | 复杂度 | 示例 |
|--------|---------|--------|------|
| 1 | 0.5 天 | 简单 | 修改配置文件 |
| 2 | 1 天 | 低 | 简单的 CRUD 接口 |
| 3 | 1.5 天 | 中 | 中等复杂度功能 |
| 5 | 2-3 天 | 中高 | 涉及多个模块的功能 |
| 8 | 4-5 天 | 高 | 复杂业务逻辑 |
| 13 | 1 周 | 很高 | 需要架构设计的功能 |

---

## 优先级定义

| 优先级 | 说明 | 示例 |
|--------|------|------|
| `P0` | 阻塞性任务，必须立即处理 | 数据库 Schema 创建 |
| `P1` | 高优先级，当前迭代必须完成 | K8s Informer 集成 |
| `P2` | 中优先级，可延后到下个迭代 | 报表导出功能 |
| `P3` | 低优先级，有空再处理 | 文档完善 |

---

## 验收标准示例

### 功能验收
- [ ] 创建 DevPod 时正确插入数据库
- [ ] Pod 状态变更时触发 {BUSINESS_SHORT}计算
- [ ] 查询 API 返回正确的 {BUSINESS_SHORT}数据

### 性能验收
- [ ] API 响应时间 < 500ms (P95)
- [ ] 支持并发查询 100+ QPS

### 质量验收
- [ ] 单元测试覆盖率 > 80%
- [ ] 代码通过 golangci-lint 检查
- [ ] 代码通过 Review

---

## 完成定义（Definition of Done）

每个 Story 完成时必须满足：

### 代码要求
- [ ] 代码已提交到主分支或功能分支
- [ ] 代码通过 Code Review（至少 1 人 Review）
- [ ] 代码符合项目编码规范
- [ ] 没有 TODO 或 FIXME（除非记录到 Issue）

### 测试要求
- [ ] 单元测试覆盖率 > 80%
- [ ] 所有测试用例通过
- [ ] 关键路径有集成测试

### 文档要求
- [ ] API 文档已更新（如有接口变更）
- [ ] 数据库 Schema 已更新（如有表结构变更）
- [ ] README 或相关文档已更新

### 部署要求
- [ ] 可在本地环境正常运行
- [ ] 可在测试环境部署成功
- [ ] 回归测试通过

---

## 命名规范

**文件命名**: `story-{epic序号}-{story序号:02d}-{简短描述}.md`

**示例**:
- `story-1-01-scaffolding.md`
- `story-5-01-cmdb-dao.md`
- `story-6-04-calculation-engine.md`

**ID 规则**: `STORY-{Epic序号}-{Story序号:02d}`

**示例**:
- Epic-1 下的 Story: `STORY-1-01`, `STORY-1-02`, `STORY-1-03`
- Epic-6 下的 Story: `STORY-6-01`, `STORY-6-02`, `STORY-6-03`, `STORY-6-04`

---

## 维护指南

### 创建新 Story

1. 确定所属的 Epic（查看 `../prd/` 目录下的 Epic 文档）
2. 使用标准命名创建 Story 文件
3. 填写元数据（`id`, `epic_id`, `status` 等）
4. 编写 Story 内容（用户故事、任务描述、技术设计、实施步骤、验收标准）
5. 在对应的 Epic 文档的 `stories` 字段中添加此 Story ID

### 更新 Story 状态

1. 更新 `status` 字段
2. 更新 `updated_at` 字段
3. 评估是否需要更新关联的 Epic 状态

### Story 状态流转规则

```
TODO → IN_PROGRESS → IN_REVIEW → COMPLETED
  ↓         ↓            ↓
BLOCKED ←───────────────┘
```

- **TODO → IN_PROGRESS**: 开始开发
- **IN_PROGRESS → IN_REVIEW**: 提交 Review
- **IN_REVIEW → COMPLETED**: Review 通过
- **IN_REVIEW → IN_PROGRESS**: Review 未通过，需修改
- **任何状态 → BLOCKED**: 遇到阻塞
- **BLOCKED → TODO**: 阻塞解除，重新规划

---

## 工程化执行建议

### 1. Story 执行顺序原则

**按依赖关系执行**：
- 优先执行 `dependencies` 为空的 Story
- 确保依赖 Story 先完成
- 使用拓扑排序确定执行顺序

**按优先级执行**：
- P0 > P1 > P2 > P3
- 同优先级下，按依赖关系排序

**并行执行**：
- 无依赖关系的 Story 可并行开发
- 每个 Epic 内部可并行（如 EPIC-5 的 3 个 Story 可并行）

### 2. 迭代规划

**推荐迭代周期**: 2 周

**迭代 1**（第 1-2 周）:
- EPIC-1: 项目脚手架搭建（STORY-1-01, STORY-1-02, STORY-1-03）
- EPIC-2: Docker Compose 开发环境（STORY-2-01, STORY-2-02）

**迭代 2**（第 3-4 周）:
- EPIC-3: 数据库迁移（STORY-3-01, STORY-3-02）
- EPIC-5: 数据层实现（STORY-5-01, STORY-5-02, STORY-5-03）

**迭代 3**（第 5-6 周）:
- EPIC-6: 服务层实现（STORY-6-01, STORY-6-02, STORY-6-03, STORY-6-04）

**迭代 4**（第 7-8 周）:
- EPIC-7: 应用层实现（STORY-7-01, STORY-7-02, STORY-7-03）
- EPIC-4: Dockerfile 与 ArgoCD 部署（STORY-4-01, STORY-4-02）

**迭代 5**（第 9-10 周）:
- EPIC-8: 测试与部署
- 性能优化和 Bug 修复

### 3. 风险管理

**高风险 Story**（需要特别关注）：
- STORY-3-01: 数据库迁移脚本（数据丢失风险）
- STORY-6-01: K8s Informer 集成（集成复杂度高）
- STORY-6-04: {BUSINESS_SHORT}计算引擎（业务逻辑复杂）

**缓解措施**：
- 提前进行技术预研（POC）
- 编写详细的测试用例
- 建立 Feature Branch 进行隔离开发
- 准备回滚方案

### 4. 质量保证

**每个 Story 必须包含**：
- 单元测试（覆盖率 > 80%）
- 集成测试（关键路径）
- 代码 Review（至少 1 人）
- 文档更新（API 文档、数据库 Schema 文档）

**CI/CD 检查点**：
- 代码格式检查（gofmt）
- 静态代码分析（golangci-lint）
- 单元测试执行（go test）
- 构建成功验证（make build）

---

**最后更新**: 2026-02-06
**维护者**: dev1@example.com
