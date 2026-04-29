---
name: "dev"
description: "开发工作流程指导 - 编码、测试、代码质量、MR/PR 创建和 CI/CD。用于开发任务、编码、功能实现、Bug 修复、单元测试、代码覆盖率、代码审查、CI/CD 流水线和 Git 操作。"
version: "5.1"
---

# Development Workflow

## Story-Driven Development（铁律）

**没有 Story，不写代码。**

Developer 三不做：
1. **不见 Story 不开工**：必须存在 `{project_docs}/scrum/story/story-*.md`，状态为 TODO/IN_PROGRESS
2. **不见 AC 不实现**：Story 必须有验收标准，否则退回 Scrum Master
3. **不被指派不接受**：不接受自我指派

例外（无需 Story）：用户直接指令、紧急生产修复、探索性调查

**说明**:
- `{project_docs}`: 项目文档目录（通常为 docs/）

---

## 核心职责

1. **代码风格**：遵循 KISS、DRY、SOLID 原则；接口与实现分离，逻辑与配置分离
2. **功能开发**：实现新功能、修复 Bug、优化性能
3. **单元测试**：编写和维护单元测试，确保**方法/分支覆盖率** ≥ `{coverage_threshold}`
4. **代码质量**：遵循代码规范，进行代码审查
5. **集成测试**：使用项目 SIT 测试框架验证功能
6. **文档维护**：反馈设计文档、API 文档、运维文档

**说明**:
- `{coverage_threshold}`: **方法/分支覆盖率**阈值（默认 70%）
- **覆盖率指标说明**：
  - **方法覆盖率**：确保每个方法都被调用
  - **分支覆盖率**：确保每个 if/switch 分支（true/false）都被执行
  - 选择原因：行覆盖率太简单，条件覆盖率太苛刻，方法/分支覆盖率是适度指标

---

## 代码风格

### 命名规范（⚠️ 重要）

**强制标准：蛇形命名方式 (snake_case)**

项目强制要求：所有代码文件、配置文件、脚本文件和目录必须使用蛇形命名方式（snake_case），即使用下划线 `_` 连接单词，禁止使用连字符 `-`。

#### 文件命名规则

| 类型 | ✅ 正确 | ❌ 错误 |
|------|---------|---------|
| **Go 源代码** | `{PROJECT_NAME}.go`, `config_dev.go`, `health_handler.go` | `{PROJECT_NAME}.go`, `config-dev.go`, `health-handler.go` |
| **配置文件** | `config_dev.yaml`, `database_config.yaml` | `config-dev.yaml`, `database-config.yaml` |
| **Shell 脚本** | `start_dev.sh`, `init_db.sh` | `start-dev.sh`, `init-db.sh` |
| **目录命名** | `example-service_informer`, `scripts_database` | `example-service-informer`, `scripts-database` |
| **API 定义** | `{PROJECT_NAME}.api`, `user_service.api` | `{PROJECT_NAME}.api`, `user-service.api` |
| **二进制文件** | `{PROJECT_NAME}_api`, `{PROJECT_NAME}_cli` | `{PROJECT_NAME}-api`, `{PROJECT_NAME}-cli` |

#### 例外情况

| 类型 | 允许格式 | 理由 |
|------|----------|------|
| **Go Modules** | `{PROJECT_NAME}` | Go 社区标准，所有 Go 官方和第三方模块都使用连字符 |
| **Go 包名** | 单个单词（`main`, `config`, `handler`） | Go 语言规范要求包名使用简短的单个小写单词 |
| **通用配置文件** | `Makefile`, `Dockerfile`, `.gitlab-ci.yml`, `docker-compose.yml`, `go.mod` | 开发工具的标准命名，修改会导致工具无法识别 |
| **文档文件** | `epic-1-scaffolding.md`, `story-1-01-design.md` | 文档文件使用连字符更便于阅读 |

#### 代码检查清单

在创建或重命名文件时，请按照以下清单检查：
- [ ] 文件名使用小写字母
- [ ] 多个单词使用下划线 `_` 连接
- [ ] 不使用连字符 `-`（除非属于例外情况）
- [ ] 不使用驼峰命名 `CamelCase` 或 `PascalCase`
- [ ] 不使用空格或特殊字符

#### 重命名操作指南

当发现不符合规范的文件时，按以下步骤重命名：

**1. 使用 git mv 重命名（保留历史）**
```bash
# 示例：重命名配置文件
git mv etc/config-dev.yaml etc/config_dev.yaml

# 示例：重命名 Go 源文件
git mv {PROJECT_NAME}.go {PROJECT_NAME}.go

# 示例：重命名目录
git mv sandbox/example-service-informer sandbox/example-service_informer
```

**2. 更新所有引用**
重命名文件后，必须更新所有引用该文件的地方：
- **Makefile**: 更新文件路径引用
- **配置文件**: 更新 include 引用
- **Go 代码**: 更新 import 路径
- **Shell 脚本**: 更新文件路径
- **文档**: 更新文件路径说明

**3. 验证编译和测试**
```bash
# 重新编译
make build

# 运行测试
make test
```

### 其他代码风格原则

- **KISS / DRY / SOLID**：追求简单、可维护、可扩展的实现
- **接口与实现分离**：保持模块职责单一、接口清晰，实现与调用解耦
- **模块化**：函数职责单一，避免冗长或重复代码
- **注释原则**：注释放在核心业务和复杂逻辑处，保持必要但不过度，注重代码自解释性
- **分层处理**：业务流程和外部依赖分层（如控制器、服务、存储分离）
- **格式统一**：使用项目配置的 lint / formatter 工具

---

## 容器化开发规范（⚠️ 关键）

**黄金规则**：每次更新代码后，启动服务前必须重新构建容器镜像

容器使用的是编译产物（二进制/字节码等），**不重新构建则代码更改不会生效**。

```bash
# ❌ 错误：只重启服务
docker compose restart {service_name}

# ✅ 正确：重新构建并启动
docker compose up -d --build {service_name}
```

**验证方法**：检查容器内编译产物的时间戳是否为最近时间。

---

## 测试规范

### 单元测试（UT）

#### 常见语言测试命令

| 语言 | `{test_cmd}` | `{coverage_cmd}`（方法/分支覆盖率） | Mock 工具 |
|------|--------------|-------------------------------------|-----------|
| **Go** | `go test ./...` | `go test -coverprofile=coverage.out` | mockery, testify |
| **Python** | `pytest` | `pytest --cov=. --cov-branch --cov-report=term-missing` | unittest.mock |
| **JavaScript** | `npm test` | `npm run test:coverage`（需配置分支覆盖率） | jest.mock, sinon |
| **Java** | `mvn test` | `mvn test jacoco:report`（需配置分支覆盖率） | Mockito |
| **TypeScript** | `npm test` | `npm run test:coverage -- --coverage` | jest.mock |
| **Rust** | `cargo test` | `cargo tarpaulin --out Html --branch` | mockito |

**说明**：
- Go 默认语句覆盖率，推荐使用 `-covermode=atomic` 提高准确性
- Python `--cov-branch` 启用分支覆盖率
- JavaScript/TypeScript Jest 默认语句覆盖率，需在 `jest.config.js` 配置 `coverageProvider: 'v8'` 启用分支覆盖率
- Java JaCoCo 需在 `pom.xml` 配置 `<instrMode>branch</instrMode>`
- Rust `tarpaulin --branch` 启用分支覆盖率

#### 执行步骤

```bash
# 1. 识别项目语言（查看 go.mod, package.json, pom.xml, Cargo.toml 等）
# 2. 从上表选择对应命令
# 3. 运行测试
{test_cmd}

# 生成覆盖率报告
{coverage_cmd}
```

**说明**:
- 如果项目有 Makefile 或 package.json 中定义的 test 脚本，**优先使用项目自定义命令**
- 覆盖率报告通常输出到 `coverage.out`、`.coverage`、`htmlcov/` 等目录

**覆盖率要求**：
- 核心组件：**方法/分支覆盖率** ≥ 80%
- 整体代码：**方法/分支覆盖率** ≥ `{coverage_threshold}`（默认 70%）

### 集成测试（SIT）

**黄金规则**：使用项目 SIT 测试框架，禁止自己编写测试脚本

#### 常见 SIT 框架

| 框架 | `{sit_run_cmd}` | 报告位置 |
|------|-----------------|----------|
| **自定义脚本** | `./tests/sit/run_sit_tests.sh --auto` | `test_reports/sit_report-*.md` |
| **pytest集成** | `pytest tests/integration/` | `test_reports/integration_report.html` |
| **Maven Verify** | `mvn verify` | `target/site/jacoco/index.html` |

```bash
# 使用项目 SIT 框架验证
{sit_run_cmd}
```

**说明**:
- 测试报告输出到 `test_reports/`

### Mock 测试策略

**核心原则：Spec → Scenario → Mock Data 三层对齐**

基于设计规范（Spec）定义测试场景（Scenario），构建对齐的 Mock 数据，确保单元测试准确体现设计意图。

**关键要求**：
- **Spec → Scenario 对齐**：每个 scenario 必须回溯到具体的 spec 条款
- **Scenario → Mock Data 对齐**：mock data 必须完全满足 scenario 的前置条件
- **可追溯性**：测试代码注释标注来源 spec 的章节号

**测试代码注释规范**（使用 AAA 模式）：
```go
// Spec: {design_doc} §{section}
// Scenario: {scenario_description}
func TestXXX(t *testing.T) {
    // Arrange: 基于 spec 构建场景
    // Act: 执行被测试的逻辑
    // Assert: 验证 spec 要求
}
```

**接口抽象原则**：
- 将具体类型改为接口，使用依赖注入传入 mock 对象
- 避免在业务逻辑中硬依赖具体实现

**说明**:
- `{design_doc}`: 设计文档名称
- `{section}`: 章节编号
- Mock 工具根据项目语言选择（见上表）

---

## 代码质量

### 常见语言代码质量工具

| 语言 | `{fmt_cmd}` | `{lint_cmd}` | `{build_cmd}` |
|------|-------------|--------------|---------------|
| **Go** | `gofmt -w .` 或 `go fmt ./...` | `golangci-lint run` 或 `make lint` | `go build ./...` |
| **Python** | `black .` | `flake8` 或 `pylint` | `python -m build` |
| **JavaScript** | `prettier --write .` | `eslint .` | `npm run build` |
| **Java** | `google-java-format -i .` | `checkstyle` | `mvn package` |
| **Rust** | `cargo fmt` | `cargo clippy` | `cargo build --release` |

### 提交前检查清单

- [ ] 代码已格式化（`{fmt_cmd}`）
- [ ] 通过静态分析（`{lint_cmd}`）
- [ ] 单元测试通过（`{test_cmd}`）
- [ ] **方法/分支覆盖率**达标（≥ `{coverage_threshold}`）
- [ ] SIT 测试验证通过（`{sit_run_cmd}`）
- [ ] 代码已审查（如果有 PR/MR）
- [ ] 文档已更新（如果需要）

**说明**:
- 从上表选择对应命令
- 如果项目有 Makefile 或 package.json 中定义了 fmt/lint 脚本，**优先使用项目自定义命令**

---

## 代码提交规范

**Commit Message 格式**：
```
<type>(<scope>): <subject>

<body>

<footer>
```

**类型**：`feat`, `fix`, `refactor`, `docs`, `test`, `chore`

---

## Git 推送规则（⚠️ 重要）

**默认行为**：
- ✅ **只做**：`git add` + `git commit`（提交到本地分支）
- ❌ **不做**：`git push`（不推送远程）

**`{main_branch}` 分支保护规则**：
- **方式 1**：Review 授权流程（修改代码 → commit → 等待 review → 用户手动 push）
- **方式 2**：MR/PR 流程（创建 feature 分支 → push → 创建 MR/PR → 合并）

**绝对禁止**：未经明确授权直接 `git push origin {main_branch}`

**YOLO 模式例外条件**（必须同时满足）：
1. 用户**明确授权**（明确说"YOLO模式"或"可以推送"）
2. 只能推送 **`{main_branch}` 之外的分支**（feature/*, dev, bugfix/* 等）
3. 推送前必须显示 commit 信息供审查
4. **永远不要自动推送 `{main_branch}`**（即使 YOLO 模式也不行）

**说明**:
- `{main_branch}`: 主分支名（通常为 master 或 main）

---

## Git Worktree 工作流

**核心概念**：主干开发模式，支持并行开发多个任务

> **💡 辅助脚本**：本 SKILL 附带了 Git Workflow 辅助脚本 `git-workflow.skill.sh`，简化 worktree 操作。
>
> **安装**（一次性）：
> ```bash
> # 添加到 ~/.bashrc 或 ~/.zshrc
> echo 'source $(git rev-parse --show-toplevel)/.claude/skills/dev/scripts/git-workflow.skill.sh' >> ~/.bashrc
> source ~/.bashrc
> ```
>
> **快速使用**：
> ```bash
> # 创建功能分支 worktree
> git-workflow.feature.start story-06-01 "pod handler"
>
> # 在 worktree 中同步上游 master/main
> git-workflow.feature.sync
>
> # 推送并创建 MR
> git-workflow.feature.submit
>
> # MR 合并后清理 worktree
> git-workflow.feature.finish story-06-01
>
> # 列出所有 worktree 及其状态
> git-workflow.worktree.list
> ```
>
> **优势**：1 条命令替代 6-8 步 Git 操作，自动检测项目配置，彩色输出提示

### 分支命名规范

- 功能分支：`feat/{task_id}-{summary}`
- Bug 修复：`fix/{bug_id}-{description}`
- 紧急修复：`hotfix/{short_description}`
- 重构：`refactor/{short_description}`

### 标准流程

```bash
# 1. 创建 worktree
cd {project_root}
git worktree add ../{worktree_dir}/{branch_name} -b {branch_name}

# 2. 在 worktree 中开发
cd ../{worktree_dir}/{branch_name}
# ... 开发代码 ...
git add .
git commit -m "<type>(<scope>): <subject>"

# 3. 推送到远程（非 {main_branch} 分支）
git push origin {branch_name}

# 4. 创建 MR/PR（根据项目使用的平台）

# 5. MR/PR 合并后，清理 worktree
cd {project_root}
git worktree remove ../{worktree_dir}/{branch_name}
git branch -d {branch_name}
```

**说明**:
- `{project_root}`: 项目根目录
- `{worktree_dir}`: worktree 存放目录（常见值：`../{project_name}-worktrees`, `../worktrees`）

### Worktree 管理

- 同时维护 2-3 个工作树，不超过 5 个
- 定期执行 `git worktree prune` 清理孤立 worktree

---

## 开发工作流

### Bug 修复流程

1. **问题定位**：阅读测试报告，查看代码，确定根因
2. **修复实现**：编写修复代码，添加单元测试
3. **单元测试**：运行 `{test_cmd}`
4. **SIT 验证**：运行 `{sit_run_cmd}`
5. **提交代码**：撰写清晰的 Commit Message
6. **生成报告**：如果修改影响核心功能，运行完整测试

### 新功能开发流程

1. **需求分析**：阅读 PRD 和 Story 文档
2. **设计实现**：参考设计文档，设计数据结构、接口、流程
3. **编码实现**：遵循代码规范，编写单元测试
4. **单元测试**：运行 `{test_cmd}`，确保覆盖率达标
5. **SIT 验证**：运行 `{sit_run_cmd}`
6. **文档更新**：更新设计文档、API 文档、CLAUDE.md
7. **代码审查**：提交 MR/PR，根据反馈修改
8. **合并发布**：合并到主分支，生成测试报告

---

## MR/PR 创建与 CI 调试

### 核心工作模式

```
MR/PR 创建 → Pipeline 监听 → 状态判断 → 成功/失败处理
                    ↓                      ↓
               持续监听               Yolo Mode 修复
                                       ↓
                                  重新推送 → 继续监听
                                           ↓
                                       闭环验证
```

### 阶段一：MR/PR 创建

#### 前置检查

- [ ] 功能完整性：所有 AC 已满足
- [ ] 代码质量：单元测试**方法/分支覆盖率**达标
- [ ] 测试验证：UT / SIT / UAT 全部通过
- [ ] 代码规范：符合项目编码规范
- [ ] 文档更新：设计文档、API 文档已更新
- [ ] Git 规范：Commit Message 包含任务 ID
- [ ] 分支状态：feature 分支提交已整理

#### MR/PR Description 模板（40-100 行）

```markdown
## 功能说明
[简述功能目标 + 核心改进点 3-5 条]

## 变更说明
### 新增文件 (N 个)
- `path/file` (X lines) - 简短说明

### 修改文件 (M 个)
- `path/file` - 修改说明

### 代码统计
- 新增: +X lines
- 删除: -Y lines
- 测试覆盖率: XX%

## 测试验证结果
| 场景 | 预期 | 实际 | 状态 |
|------|------|------|------|
| 场景1 | XXX | XXX | ✅ |

## 相关文档
- Story: `{project_docs}/scrum/story/story-*.md`
- Design: `{project_docs}/design/{layer}_design_v{version}.md`

## 验收标准
- [x] AC1
- [x] AC2
```

#### 创建步骤

**使用 CLI 工具（推荐）**：
```bash
# GitLab
glab mr create --title "<type>(<scope>): <subject>" \
  --target-branch {main_branch} --source-branch {branch_name}

# GitHub
gh pr create --title "<type>(<scope>): <subject>" \
  --base {main_branch} --head {branch_name}
```

**使用 REST API（备选）**：
- 使用项目对应平台的 REST API 创建 MR/PR
- 注意 Shell 变量作用域：变量设置和使用必须在同一命令行

### 阶段二：Pipeline 监控

**状态值**：`pending` → `running` → `success` / `failed` / `canceled` / `skipped`

**监控方式**：
- 使用平台 CLI（`glab`, `gh`）或 REST API 查询 Pipeline 状态
- 获取失败 Job 列表和日志
- 日志过大时保存到文件分析

**CI 失败类型与处理**：

| 失败类型 | 负责方 | 典型场景 |
|---------|--------|----------|
| 编译错误 | Dev | 语法错误、类型不匹配、依赖缺失 |
| 测试失败 | Dev/QA | 断言失败、集成测试失败 |
| 超时 | Dev | 死锁、网络延迟、性能问题 |
| Runner 异常 | Ops | Runner 不可用、资源不足 |

### 阶段三：Yolo Mode 快速修复

**触发条件**：Pipeline 失败

**5 步修复流程**：
1. **同步主分支**：`git fetch origin {main_branch}` + `git rebase origin/{main_branch}`
2. **本地修复**：根据 CI 日志定位并修复问题
3. **本地验证**：运行 `{test_cmd}`, `{fmt_cmd}`, `{build_cmd}` 全部通过
4. **提交并推送**：commit + push 到 feature 分支
5. **继续监听**：回到阶段二，直到 Pipeline 成功

**说明**:
- `{build_cmd}`: 构建命令（见上表）

---

## 常见错误

### ❌ 错误 1：自己编写集成测试脚本

```
❌ 自写测试脚本代替项目 SIT 框架
✅ 使用项目 SIT 测试框架（{sit_run_cmd}）
```

### ❌ 错误 2：提交前不运行测试

```
❌ 直接 git add . && git commit && git push
✅ {fmt_cmd} && {lint_cmd} && {test_cmd} && {sit_run_cmd} → 然后 commit
```

### ❌ 错误 3：容器开发不重新构建

```
❌ 修改代码后只重启容器（docker compose restart）
✅ 修改代码后重新构建（docker compose up -d --build）
```

---

## 关键资源

**项目文档**：
- `CLAUDE.md` - 项目概述、核心架构、开发规范
- `{project_docs}/design/` - 设计文档目录
- `{project_docs}/scrum/story/` - Story 文档目录

**SKILL 文档**：
- `.claude/skills/qa/SKILL.md` - QA 工作流程和测试规范
- `.claude/skills/pm/SKILL.md` - Scrum 工作流程
- `.claude/skills/arch/SKILL.md` - 架构设计规范

---

## 占位符推断规则（精简版）

Claude 执行时按优先级推断占位符：

1. **检查项目配置**（Makefile, package.json, go.mod, pom.xml, Cargo.toml）
2. **查看目录结构**（docs/, tests/, scripts/）
3. **从 Git 配置推断**（.git/config, git remote -v）
4. **使用常见值表格**（本 SKILL 提供的默认值）
5. **询问用户**（以上都失败时）

**高可推断性占位符**（> 85%）：
`{main_branch}`, `{project_root}`, `{project_docs}`, `{test_cmd}`, `{build_cmd}`, `{fmt_cmd}`, `{lint_cmd}`, `{vcs_platform}`

**中等可推断性**（60-80%）：
`{coverage_threshold}`（默认 70%）, `{worktree_dir}`, `{sit_run_cmd}`

---

**版本**: v5.1
**创建日期**: 2026-04-28
**作者**: Development Team
**状态**: 正式发布

**更新日志**:
- v5.1 (2026-04-29): 整合 naming-conventions 到代码风格章节
- v5.0 (2026-04-28): 重构为符合官方最佳实践
- v4.1 (2026-04-28): 添加渐进式揭示 + 明确覆盖率指标
- v4.0 (2026-04-28): 去项目化产品化改造
- v3.1 (2026-04-25): 新增 Story-Driven Development 铁律
- v3.0 (2026-02-12): 从 pm SKILL 迁移 MR 工作流
- v2.0 (2026-02-03): 初始版本

