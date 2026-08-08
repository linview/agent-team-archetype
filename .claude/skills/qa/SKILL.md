---
skill: "qa"
description: "QA 工作技能 — 测试分层架构、UT/API/SIT/E2E/UAT 测试、交叉验证策略、测试数据管理、测试报告管理。当用户提到测试、QA、质量保证、回归测试、单元测试、集成测试、验收测试、测试覆盖率、pytest、go test、E2E、Playwright、monkey test、fuzz test、RPC 测试、测试用例设计、TDD、测试框架、测试策略审查、问题排查、测试环境、测试数据、SIT 交叉验证、或需要设计/执行/增强测试策略时，必须使用此技能。确保所有测试活动遵循分层架构和业务正确性验证原则。"
version: "7.1"
---

# QA 工作技能

## 📋 文档概述

本文档描述 QA 工作的核心技能和流程，重点包括：
1. **测试分层架构**：UT → API → SIT → E2E → UAT 五层测试金字塔
2. **SIT 交叉验证策略**：数据层（DB）+ 服务层（API）交叉断言，定位服务层 bug
3. **测试设计原则**：验证业务数据逻辑正确性，而非仅验证"数据存在"

**章节优先级**：测试分层架构 → SIT 交叉验证 → TDD 验收标准 → 测试用例设计

---

## 核心职责

1. **UT 回归测试**：收集单元测试结果，统计测试覆盖率
2. **API 接口测试**：验证接口契约 + 业务数据正确性（**主动索取测试数据**）
3. **SIT 系统集成测试**：**数据层 + 后端服务层**联调验证，定位服务层 bug
4. **E2E 端到端测试**：**数据层 + 后端 + 前端**三层联调验证（Playwright）
5. **UAT 用户验收测试**：用户可感知功能场景验证，追求**全面准确**
6. **测试报告管理**：生成测试报告，反馈给团队

---

## 🏗️ 测试分层架构（⭐ 核心高价值）

### 测试金字塔模型

```
                /\
               /  \
              / UAT \  ← 发布门禁（最少）
             /------\
            /  E2E   \  ← 端到端用户场景（较少）
           /----------\
          /    SIT     \  ← ⭐ 数据层/服务层交叉验证（适中）
         /--------------\
        /     API         \  ← 接口契约 + 业务正确性（较多）
       /------------------\
      /       UT            \  ← 函数/方法逻辑（最多）
     /----------------------\
```

### 测试层级定义摘要

| 层级 | 核心目标 | 定位能力 | 用例数 |
|------|---------|---------|--------|
| **UT** | 函数/方法逻辑正确性（Mock 是合理手段） | 定位具体函数错误 | 最多 |
| **API** | 接口契约 + 业务数据正确性（需主动索取测试数据） | 定位接口层问题 | 较多 |
| **SIT** | **数据层 + 后端服务层**联调验证 | **定位服务层逻辑 bug** | 适中 |
| **E2E** | **数据层 + 后端 + 前端**三层联调验证（Playwright） | 验证三层贯通 | 较少 |
| **UAT** | 用户可感知功能场景（全面准确，非仅有数据） | 确认功能/数据精准可用 | 最少 |

> **完整定义**：每个测试层级的详细定义、目标、测试范围、工具和模式，见 [testing_layer_definitions.md](references/testing_layer_definitions.md)

### 各层级核心规则

**规则 1：目录对应关系**
- ✅ API 测试 → `tests/api/`
- ✅ SIT 测试 → `tests/sit/`
- ✅ E2E 测试 → `frontend/tests/e2e/`（前端项目内）

**规则 2：回归测试必须完整执行**
```bash
# ✅ 正确
pytest tests/api/ -v
# ❌ 错误
pytest tests/api/test_single.py -v
```

**规则 3：禁止使用 --maxfail 提前终止**

### 各层级不可替代性

```
UT 无法替代 SIT：Mock 无法发现集成问题
SIT 无法替代 E2E：测试环境无法模拟真实用户场景
E2E 无法替代 UAT：自动化无法替代人的业务判断

每一层都有独特价值，缺少任何一层都会留下盲区。
```

---

## ⭐ SIT 交叉验证策略（核心洞察）

### 核心原则

**SIT 的价值不是验证"数据存在"，而是验证"数据层和服务层的一致性"。**

如果数据层（DB 直接查询）可获得正确结果，但通过 API 在服务层无法获得，那就说明**服务层逻辑有 bug**。

### Bug 定位逻辑

```
数据层有数据 + API 返回空     → 🔴 服务层逻辑 bug
数据层无数据 + API 返回空     → ✅ 数据问题，非代码 bug
数据层有数据 + API 返回数据   → ✅ 正确
数据层无数据 + API 返回数据   → 🔴 数据映射 bug（幻觉数据）
```

### 交叉验证标准模式

```python
def test_cross_validation_db_vs_api(pg_conn):
    """SIT 交叉验证标准模式"""

    # Step 1: 数据层 — 直接查 DB 获取预期
    with pg_conn.cursor() as cur:
        cur.execute("SELECT ... FROM table WHERE condition")
        db_result = cur.fetchone()

    assert db_result is not None, "数据层：无预期数据，无法交叉验证"

    # Step 2: 服务层 — 调 API 获取实际
    resp = requests.get(f"{API_BASE}/endpoint", params={...})
    api_result = resp.json()["data"]

    # Step 3: 交叉断言 — DB 预期 vs API 实际
    assert len(api_result) > 0, (
        f"服务层 bug：DB 有 {db_result} 条记录，"
        "但 API 返回空数据 → 服务层逻辑有 bug"
    )
```

### SIT 测试的三种类型

| 类型 | 目的 | 示例 |
|------|------|------|
| **数据质量验证** | 验证 DB 数据格式、完整性 | commit_hash 是 SHA-1，artifact commit_hash 是 MD5 |
| **业务规则验证** | 验证数据符合业务规则 | app 制品有 commit-artifact 关联 |
| **⭐ 交叉验证** | DB 预期 vs API 实际 → 定位服务层 bug | DB 有数据但 API 返回空 → 服务层 bug |

### 为什么只有 SIT 能定位服务层 bug

| 测试层级 | 能否定位服务层 bug | 原因 |
|---------|------------------|------|
| UT | ❌ | Mock 隔离了数据库 |
| API | ⚠️ | 能发现"有问题"，无法定位层级 |
| **SIT** | ✅ | **DB 预期 vs API 实际 = 定位服务层** |
| E2E | ❌ | 只验证用户行为 |

> **完整案例**：source_map 类型过滤和源码追溯的 SIT 交叉验证实战，见 [testing_layer_definitions.md](references/testing_layer_definitions.md#实战案例sit-交叉验证)

---

## TDD 验收标准（⭐ 核心高价值）

### 🟢 绿灯（通过 — 可发布）
- ✅ 所有 SIT 测试通过
- ✅ 所有 E2E 核心测试通过
- ✅ 无 P0/P1 级 Bug

### 🟡 黄灯（有条件通过）
- ⚠️ SIT 测试通过率 70-89%
- ⚠️ 存在 P1 级 Bug（不影响核心功能）

### 🔴 红灯（不通过 — 禁止发布）
- ❌ SIT 测试失败（无法连接基础服务）
- ❌ 存在 P0 级 Bug

---

## 📋 测试用例设计原则（⭐ 高价值）

### ⚠️ 核心原则：验证业务数据逻辑正确性，而非仅验证"数据存在"

**错误标准**（不够）：
```python
# ❌ 只验证数据存在
assert len(body["data"]) > 0
assert resp.status_code == 200
```

**正确标准**（业务正确性）：
```python
# ✅ 验证业务数据逻辑
node_types = collect_all_node_types(body["data"])
assert "system" in node_types, "依赖树必须包含 system 节点"
assert "commit" in node_types, "app 制品依赖树必须追溯至 commit"
assert all(name.strip() for name in commit_names), "commit 名称不应为空"
```

### 设计文档是测试用例的唯一真实来源

| 层 | 唯一来源 | 反标载体（`@trace`） |
|---|---|---|
| UT | 代码符号 | **不适用 `@trace`**(UT 真实来源=代码符号;追溯交 spec-xchecker CT 层 symbol↔test_) |
| API | API 元数据文件 | `endpoint` + `design="api_design_vX.Y#<章节>"` |
| SIT | 设计文档 | `story` + `design="service_layer_architecture_vX.Y#<章节>"` |
| E2E | 用户旅程 / Epic | `epic`(Epic 即 PRD 源锚) |
| UAT | **PRD 文档 / Epic** | `epic`(保持 PRD@Epic 粒度) |

> 反标不止是"写下来",而是要让测试集随设计演进**新陈代谢**:见下方「分层用例 review」节与 [test_traceability.md](references/test_traceability.md)。

### 边界值与等价类划分

- 每个等价类至少一个测试用例
- 测试最小值、最大值、边界外值
- 测试空值、特殊字符、超长输入

---

## ⚡ pytest xfail/xpassed 实践策略

### 何时使用 xfail

- 测试先行：先写测试标记 xfail，再实现功能
- 依赖阻塞：等待外部依赖修复
- 环境限制：当前环境无法支持

### xpassed 处理流程

1. 识别 xpassed 测试：`pytest -v | grep XPASS`
2. 验证功能正确性
3. 移除 xfail 标记
4. 更新测试基线

### 统计规则

通过率计算：`pass_rate = (passed + xpassed) / total_tests`

---

## 🔧 测试环境规范（⚠️ 关键）

### 黄金规则

每次更新代码后，启动服务前必须重新构建容器镜像。

```bash
# ✅ 重新构建并启动
cd {deploy_path} && {compose_command} up -d --build

# ❌ 只重启不会应用新代码
{compose_command} restart {service_name}
```

### 环境一致性铁律

**Where you code = Where you test**
- 在 worktree 中开发 → 在 worktree 中测试
- 严禁跨环境测试（主仓库测试 worktree 代码 = 虚假通过）

> **详细规范**：容器环境验证、跨环境测试陷阱、检查清单，见 [troubleshooting.md](references/troubleshooting.md)

---

## 🔄 重构测试标准化流程（铁律）

### 核心原则：基线对比法

1. **重构前**：验证环境 + 建立测试基线
2. **执行重构**：使用 `git mv` 保留历史
3. **重构后**：重新构建环境 + 回归测试
4. **诊断**：基线 vs 重构后，通过率差异 ≤5%

```bash
# 基线
pytest tests/ -v --html=test_reports/baseline.html

# 重构后
pytest tests/ -v --html=test_reports/refactor.html

# 对比：差异 ≤5% → 重构安全
```

> **详细流程**：四阶段流程 + 问题诊断决策树，见 [troubleshooting.md](references/troubleshooting.md#重构测试标准化流程铁律)

---

## 📊 UT 覆盖率统计

### 核心原则

分层统计，聚焦核心逻辑：

| 层级 | 覆盖率目标 | 是否计入总体 |
|------|-----------|------------|
| **Logic 层** | ≥80% | ✅ 计入 |
| **Package 层** | ≥60% | ✅ 计入 |
| **数据访问层** | 20-30% | ❌ 单独统计 |

数据访问层的真实性验证交给 SIT 集成测试（真实数据库）。

> **详细指南**：统计方法、行业对标、报告模板，见 [ut_coverage_guide.md](references/ut_coverage_guide.md)

---

## 🧹 测试幂等性

### 核心原则

测试可以重复执行任意次数，每次结果相同。

### 保障机制

| 保护机制 | 作用范围 | 实现方式 |
|---------|---------|----------|
| 全局清理 | 测试会话级别 | `scope="session"` fixture |
| 独立命名 | 测试用例级别 | `test-{layer}-{id}-{desc}` |
| 自动清理 | 测试用例级别 | fixture yield 前后执行清理 |

> **详细策略**：四阶段幂等性策略、数据准备原则、检查清单，见 [test_idempotency.md](references/test_idempotency.md)

---

## 🐛 问题排查方法论（铁律）

### 核心原则：代码优先

1. 阅读代码，理解逻辑
2. 检查配置，是否符合代码预期
3. 修改配置，一次到位（不要试错）

> **详细方法论**：环境一致性、容器化开发规范、重构测试流程，见 [troubleshooting.md](references/troubleshooting.md)

---

## 测试报告管理

### 命名规范

- 报告文件：`{type}_report-{desc}-{timestamp}.html`
- 日志文件：`{type}_test_result-{desc}-{timestamp}.log`
- 类型：sit/uat/api

### 归档规则

`test_reports/` 下只保留当前测试报告，每次新一轮测试前归档往期：

```bash
mkdir -p test_reports/archive
mv test_reports/*report*.html test_reports/archive/
```

### 问题报告模板

```markdown
## 问题 ID: QA-{TYPE}-XXX

**严重级别**: 🔴 P0 / 🟡 P1 / 🟢 P2
**测试场景**: {test_scenario}
**实际结果**: {actual_result}
**预期结果**: {expected_result}
**根因分析**: {root_cause}
**修复位置**: {file_path}:{line_number}
```

---

## 🔄 分层用例 review（设计↔测试漂移检测）⭐

> 用例集要随设计迭代**新陈代谢**:测试用 `@trace` marker 记录"创建时对应的 design 版本";设计演进时,**漂移检测器**自动暴露过期用例,由 review 决定 update/retire/add。

### `@trace` marker（两维度）

```python
@pytest.mark.trace(
    story="STORY-6-02", ac="SIT",
    design="service_layer_architecture_v4.2#查询路由策略"  # 版本化源锚 = 历史快照
)
```

- **定位符**（空间·查阅）:`story`/`epic`/`endpoint` 三选一 —— "**一测一主功能锚**"(约束功能维度,不约束 AC 层维度)。
- **版本化源锚**（时间·漂移）:`design="<doc>_vX.Y#<真实章节>"`,是**历史快照**(不随设计自动更新)—— pin 版本与当前版本之差即漂移信号。

### 漂移检测（定期分层 review 的固定步骤）

```bash
python .claude/skills/qa/scripts/trace_drift.py
# → test_reports/trace_drift_report.md(纯静态,不开 pytest、不连 PG/K8s)
```

| 态 | 触发 | review 动作 |
|---|---|---|
| ✅ 同步 | pin == 当前 且章节仍在 | 无需动作 |
| ⚠️ 版本漂移 | pin < 当前(design 已演进) | 复核内容 → UPDATE / RETIRE |
| ⚠️ 章节漂移 | 章节 重排/改名/删除 | 重对齐锚 → UPDATE |
| 🔴 悬空 | doc 族消失 或 story CANCELLED | RETIRE |

> 框架代码(marker 工厂 + 收集期校验 hook)见 [assets/](assets/);完整方法论(时态论证、层↔锚对角映射、非对角测试规则、能力边界)见 [test_traceability.md](references/test_traceability.md)。

---

## 测试流程（通用模板）

### Phase 1: UT 回归
```bash
cd backend && go test ./... -v
```

### Phase 2: SIT 交叉验证
```bash
pytest tests/sit/ -v -m sit
```

### Phase 3: API 接口测试
```bash
pytest tests/api/ -v
```

### Phase 4: E2E 端到端测试
```bash
cd frontend && npx playwright test
```

### Phase 5: 覆盖率统计
```bash
cd backend && go test -coverprofile=coverage.out ./...
```

---

## 最佳实践

1. **每次修改代码后**：运行快速验证（单个测试用例）
2. **每次修复 bug 后**：运行完整 SIT 测试
3. **准备发布前**：运行完整 UT + API + SIT + E2E 测试
4. **测试标准**：验证业务数据逻辑正确性，不仅验证数据存在
5. **SIT 交叉验证**：每次写 SIT 测试时，先问"数据层预期是什么？服务层实际是什么？"
6. **报告管理**：每次测试前自动归档往期报告

---

## 附加资源

### Reference 文档（按需加载）

- **[testing_layer_definitions.md](references/testing_layer_definitions.md)** — ⭐ UT/API/SIT/E2E/UAT 标准定义、SIT 交叉验证实战案例
- **[test_traceability.md](references/test_traceability.md)** — ⭐ 测试可追溯性与设计漂移检测(两维度模型、层↔锚对角映射、4 态检测、能力边界)
- **[test_idempotency.md](references/test_idempotency.md)** — 测试幂等性四阶段策略、数据准备原则
- **[ut_coverage_guide.md](references/ut_coverage_guide.md)** — UT 覆盖率分层统计、行业对标、报告模板
- **[troubleshooting.md](references/troubleshooting.md)** — 问题排查方法论、环境一致性、重构测试流程

### 可复用框架代码（`assets/` + `scripts/`）

- **[assets/trace_framework.py](assets/trace_framework.py)** — `@trace` marker 工厂 + `pytest_collection_modifyitems` 校验 hook(复制进项目即用)
- **[assets/test_trace_example.py](assets/test_trace_example.py)** — 规范标注示例(SIT/API/UAT/E2E/hotfix 五种写法)
- **[assets/pytest_trace_marker.ini.snippet](assets/pytest_trace_marker.ini.snippet)** — `trace:` marker 注册行(贴进 pytest.ini)
- **[scripts/trace_drift.py](scripts/trace_drift.py)** — 设计↔测试漂移检测器(静态扫描,4 态报告)

### 关键资源

**测试框架文档**：
- pytest: https://docs.pytest.org/
- go test: https://golang.org/pkg/testing/
- Playwright: https://playwright.dev/

**测试策略参考**：
- Google 测试标准：https://testing.googleblog.com/
- Martin Fowler: https://martinfowler.com/

**协作 SKILL**：
- `.claude/skills/dev/SKILL.md` — 开发工作流（测试命令、覆盖率工具）
- `.claude/skills/pm/SKILL.md` — Story 管理与 AC 测试分层策略
- `.claude/skills/arch/SKILL.md` — 架构设计规范

---

**版本**: v7.3
**更新日期**: 2026-07-30

**更新日志**：
- v7.3 (2026-07-30): 🔧 **收紧 UT 不进入 `@trace` 范围**(消除 Python 栈下 UT 误标风险)
  - `VALID_AC` 移除 `"UT"`(仅保留 API/SIT/E2E/UAT);`_validate_kwargs` 对 `ac="UT"` 报专属引导 issue
  - 原则:UT 唯一真实来源是代码符号(非设计文档),`@trace` 的 design 源锚语义错配;UT↔代码追溯交 spec-xchecker CT 层
  - 文档「唯一真实来源」表 / test_traceability.md §3 §6 / GUIDE.md:UT 由"可选"改"不适用 `@trace`"
  - 不影响 UT 测试层与 pm `[UT]` AC 门禁(仍按 AC 签字率,不经 @trace)
  - 防偏(同批):`trace_framework.py` 加 `VALID_AC↔SSOT` 元不变式(`_AC_SSOT`/`_AC_EXCLUDED` + `_assert_validac_ssot_alignment`),改 ac 枚举不同步改 SSOT 映射即自测报警;`test_traceability.md` §3 加「语义对齐自检三问」(SSOT/锚覆盖/跨栈)——把 v7.2 偏差教训焊成机器约束 + 人工准则双保险
- v7.2 (2026-07-29): 🎯 **测试可追溯性 + 设计漂移检测**:用例集随设计迭代新陈代谢
  - 新增 `@trace` marker(两维度:定位符 story/epic/endpoint + 版本化源锚 design)——"一测一主功能锚"
  - 新增 `references/test_traceability.md`(方法论:关系非属性、源锚=历史快照、层↔锚对角映射、4 态检测、能力边界)
  - 新增 `assets/{trace_framework.py, test_trace_example.py, pytest_trace_marker.ini.snippet}`(可复制框架代码)
  - 新增 `scripts/trace_drift.py`(静态漂移检测器,4 态报告,纯静态环境安全)
  - SKILL.md 新增「分层用例 review」节;「唯一真实来源」表扩为 5 行(保持 UAT=PRD)
- v7.1 (2026-06-01): 用户反馈修正五层测试定义
  - E2E 重定义为"数据层 + 后端 + 前端"三层联调验证（触发源在前端）
  - API 增加测试数据管理策略（QA 主动索取测试数据）和多协议支持声明
  - UAT 强化验收标准（全面准确，非仅有数据）
  - Description 增加 monkey test、fuzz test、RPC 测试、测试策略审查等关键词
- v7.0 (2026-06-01): 🎯 **重大更新**：分层测试策略增强
  - 新增 SIT 交叉验证策略作为核心高价值概念（数据层 + 服务层交叉断言）
  - 创建 `references/testing_layer_definitions.md` — UT/API/SIT/E2E/UAT 标准定义
  - 创建 `references/test_idempotency.md` — 测试幂等性详细策略
  - 创建 `references/ut_coverage_guide.md` — UT 覆盖率统计指南
  - 创建 `references/troubleshooting.md` — 问题排查 + 环境一致性 + 重构测试
  - 精简 SKILL.md 从 975 行 → ~450 行（减少 54%），详细内容迁移至 references/
  - 测试标准从"验证数据存在"升级为"验证业务数据逻辑正确性"
- v6.0 (2026-04-28): 产品化改造
