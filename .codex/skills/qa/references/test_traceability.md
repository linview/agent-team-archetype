# 测试可追溯性与设计漂移检测（Test Traceability & Design Drift）

> qa skill 方法论参考。配套框架代码见 [`assets/`](../assets/)、检测器见 [`scripts/trace_drift.py`](../scripts/trace_drift.py)。
> 本期范围:marker + 漂移检测 + 文档;spec-xchecker 读 `@trace` 输出 RTM 矩阵留后续。

---

## 0. 为什么不是"给测试加属性"

测试与需求/设计是 **N:M 关系**(一个测试可验证多个 AC,一个 AC 可被多个测试覆盖)。把它建模成测试上的**属性**(`covered_by: [AC-1, AC-2]`)会陷入两个泥潭:

- **多源归属歧义**:一个 API 测试覆盖 5 个 story 的同一端点时,AC 归属混乱。
- **腐烂副本**:设计演进,属性里抄的 AC 文本与设计脱节,无人更新,变成"看起来追溯、实则过期"。

所以我们把追溯拆成**两个正交维度**,各管一件事:

| 维度 | 回答的问题 | 载体 | 时态 |
|---|---|---|---|
| **定位符**（空间维 · 查阅） | "这测试对应哪个可追溯实体?" | `story` / `epic` / `endpoint` | 当下 |
| **版本化源锚**（时间维 · 漂移检测） | "这测试是依据哪个版本的设计写的?" | `design="<doc>_vX.Y#<章节>"` | **历史快照** |

定位符解决"空间上找得到";源锚解决"时间上没烂掉"。后者是本方法论的**主价值**。

---

## 1. 核心论证:源锚是历史快照,不是当前目标

> 这一条化解了"design 锚会变成腐烂副本"的批评 —— 关键在于**时态不同**。

仓库里有两类对"设计"的引用:

- **`@trace(design=...)`（测试锚）= 历史快照**:"本用例**当初**针对 `service_layer_architecture_v4.2` 的《查询路由策略》章节编写"。一旦写入,**不再随设计变动而自动更新** —— 这正是它的价值。
- **`Story.design_docs`（pm 侧）= 当前目标**:"实现本 story 时**应**达到 `...v4.3`"。

两者**时态不同,不冲突**:
- pin 版本 == 当前版本 → 用例与设计同步 ✅
- pin 版本 < 当前版本 → **这就是漂移信号** ⚠️(设计演进了,用例没跟上)

如果测试锚"聪明地"跟着设计走(自动指向最新版),反而**抹掉了漂移信号** —— 你再也看不出哪些用例是按旧设计写的、需要复审。所以:**源锚故意是只读的历史指纹**。

> 设计演进规则见 [pm design_spec_evolution_rules.md](../../pm/references/design_spec_evolution_rules.md) L21(旧版进 `archive/`)、L508-509(Design Spec 是 SSOT,Epic/Story 非源头)。检测器据此判断"当前版本"。

---

## 2. marker schema

```python
import pytest

@pytest.mark.trace(
    story="STORY-6-02",                                     # 定位符 · 三选一
    ac="SIT",                                              # 层归属枚举(必填): API|SIT|E2E|UAT(UT 不用 @trace)
    design="service_layer_architecture_v4.2#查询路由策略",   # 版本化源锚(技术层必带)
    # epic="EPIC-6",                                        #   ← E2E/UAT 用此(epic 在 docs/scrum/prd/ 下即 PRD 源)
    # note="hotfix-2026-07-29 紧急修复"                      #   ← 退化口(无 story 场景)
)
def test_xxx():
    ...
```

**字段规则**:

| 字段 | 必填 | 约束 | 说明 |
|---|---|---|---|
| `ac` | ✅ | 枚举 `API\|SIT\|E2E\|UAT` | 层归属,对齐 pm `ac_testing_strategy.md` 的 `[LAYER]` AC 标签(UT 不用 @trace,追溯交 CT 层) |
| 定位符 | ✅(任选其一) | `story`/`epic`/`endpoint` **有且仅有一个** | "一测一主功能锚"(见 §5) |
| `design` | 技术层必带 | 格式 `<doc_stem>_vX.Y#<真实章节>` | 版本借真实文件名;`#` 后为真实标题(禁编造 `#3.2`) |
| `epic` | 用户层用此 | `EPIC-<seq>` | epic 文件即 PRD 载体,兼作 PRD 源锚 |
| `note` | 退化口 | 字符串 | hotfix/探索性/无-story(dev SKILL L18 三类场景),允许无定位符 |

**版本号格式**:文件名即版本来源,如 `service_layer_architecture_v4.2.md`、`api_design_v1.3.md`。`#` 后**必须是文档里真实存在的章节标题核心词**(检测器会校验是否存在)。

---

## 3. 层 ↔ 锚 映射(默认心智模型,非完备检查表)

> "粒度对等"问题的解法:**层 ↔ 锚对角映射**(非平铺)。每一层用它**粒度最匹配**的源,不强求都用 design 文档。

| 层 | 定位符（查阅） | 版本化源锚（漂移检测） | 为什么 |
|---|---|---|---|
| **UT** | 代码符号 | —(**UT 不走 `@trace`**) | UT 真实来源=代码符号(非设计文档);追溯交 spec-xchecker CT 层(symbol ↔ test_) |
| **API** | `endpoint` | `design="api_design_v1.3#<章节>"` | 端点契约最稳定;多 story 共享一端点是正常 |
| **SIT** | `story` + `ac=SIT` | `design="service_layer_architecture_v4.2#<章节>"` | SIT 验证服务层逻辑 → 锚服务层设计 |
| **E2E** | `epic` | PRD 锚(epic 自身) | 跨 story 旅程,天然多源,Epic 是可控粒度 |
| **UAT** | `epic` | PRD 锚(epic 自身) | 验收按 PRD/Epic 叙事(用户确认保持 PRD 粒度) |

### 非对角测试(不在默认映射里,单列规则)

下列测试**不强求**满足"定位符+design 锚"的默认形态,避免被误报为未追溯:

| 测试类型 | 主源 / 规则 |
|---|---|
| `regression` | `note="regress-<bug-id>"`,bug 记录(QA-XXX)为主源 |
| `bug_detection` | `note="bug-<id>"`,QA 问题报告为主源 |
| `perf` | 定位符可选;无 primary 也允许 |
| 部署/运维测试 | `note="deploy-..."`,允许无 primary |
| 无-story 重构 | `note="refactor-<scope>"`,dev SKILL L18 无-story 场景 |

> 检测器对 `note` 模式只校验格式不报漂移(无 design 锚时归为"ℹ️ 无 design 锚,正常")。

### 增强 @trace 时的语义对齐自检(防偏)

> 教训来源:v7.2 曾把 `"UT"` 放进 `VALID_AC`,使 UT 可被打 `@trace`——而 UT 的 SSOT 是代码符号,`design` 锚覆盖不到,语义错配。新增/修改 **ac 值、定位符、design 锚格式**时强制走一遍下列三问,把"原则"守在"约束"之前。

1. **SSOT 是什么?** 这个层/分支的*唯一真实来源*是代码符号、设计文档、还是 PRD/Epic?
2. **被哪个锚覆盖?** 这个 SSOT 能否被 `@trace` 现有锚(`story`/`epic`/`endpoint`/`design`)表达?
   - 能 → 进 `VALID_AC`,并在 `_AC_SSOT` 声明其锚。
   - **不能 → 不该进 `VALID_AC`**,另寻追溯通道(UT↔代码交 spec-xchecker **CT 层** symbol↔`test_`),并在 `_AC_EXCLUDED` 记录排除理由。
3. **换栈是否成立?** archetype 是跨项目模板,必须在**至少两种技术栈**下复核(如 Go 栈 UT 走 `go test` 调不了 pytest marker,Python 栈 UT 也是 pytest 却能被打 `@trace`——同一结论在两栈下表现不同,以"会暴露问题"的那栈为准)。

> 前两问已部分机械化(框架自测的 `VALID_AC ↔ SSOT` 元不变式,见 `assets/trace_framework.py`);第三问(跨栈反事实)仍需人判断——这是 archetype 特有的、最易被单一范例栈掩盖的盲区。

---

## 4. 漂移检测机制（核心交付）

**消费方**:/qa 定期**分层用例 review**(不是 MR 门禁)。
**触发**:设计文档版本演进 / 章节重排 / story 退役。
**动作**:看到漂移信号 → 做 design↔test **内容 review** → 决定用例 **UPDATE / RETIRE / ADD**。

### 四态

| 态 | 触发条件 | 建议动作 |
|---|---|---|
| ✅ **同步** | pin 版本 == 当前版本,且 `#章节` 仍在 | 无需动作 |
| ⚠️ **版本漂移** | pin 版本 < 当前版本(design 已演进) | 复核内容是否仍有效 → UPDATE / RETIRE |
| ⚠️ **章节漂移** | pin == 当前,但 `#章节` 在当前文档找不到(重排/改名/删除) | 重新对齐锚 → UPDATE |
| 🔴 **悬空** | doc 族消失,或 story 状态 = CANCELLED | RETIRE(用例随 story / 文档退役) |

### 运行检测器

```bash
python .codex/skills/qa/scripts/trace_drift.py \
  --test-dir examples/backend/tests \
  --design-dir examples/backend/docs/design \
  --scrum-dir examples/backend/docs/scrum
# → 报告输出 test_reports/trace_drift_report.md(遵循全局临时文件规范)
```

检测器**纯静态**:regex 扫 `@pytest.mark.trace(...)` → 抽 kwargs → 对比 design 目录当前版本与章节存在性 → 查 story 状态。**不开 pytest、不连 PG/K8s**,环境安全。有 actionable 漂移时 exit=1,便于接入 review 流程。

---

## 5. "一测一主功能锚"规则

> 回答 Q3(多源归属歧义)与 Q2(粒度对等)的核心约束。

**规则**:一个测试**只验证一个用户可观察行为**(功能维度唯一锚)。

- ✅ 约束的是**功能维度**:定位符 `story`/`epic`/`endpoint` **有且仅有一个**(框架 `validate_trace_items` 强制校验)。
- ❌ **不**约束 AC 层维度:一个测试可同时为 `[API]` + `[SIT]` 提供 AC 证据 —— 这是**复用**,不是 smell。

**为什么定位符必须单值**:多源(一个用例挂 5 个 story)会让 AC 归属指向模糊,产生歧义。N:M 关系由"**多个测试**各持一个定位符"来表达,而不是"一个测试挂多个定位符"。

**例外**:`note` 退化口(hotfix/探索性)允许无定位符 —— 这些场景本来就没有功能归属。

---

## 6. 能力边界(本期不做什么)

- **UT 追溯**:**UT 不使用 `@trace`**(粒度爆炸且语义错配——UT 真实来源是代码符号,非设计文档);UT↔代码的追溯交 spec-xchecker **CT 层**(symbol ↔ `test_`)。
- **Playwright E2E / Go UT**:不在 `@trace` 标注范围(非 pytest 标记生态)。文档覆盖,机械化留后续。
- **FSM 门禁不受影响**:pm 的 Story 状态门(IN_PROGRESS 需 [UT]、TESTING 需 [SIT] 等)**仍按 AC 签字率**判断,不按 `@trace` 覆盖率。`@trace` 是 review 工具,非门禁。
- **漏标检测不在本期范围**:检测器只处理**已标注**的用例;统计"哪些 AC 没 `@trace`"是 spec-xchecker RTM 矩阵的活(后续)。
- **校验默认 warning**:`validate_trace_items` 默认收集期 warning;`TRACE_STRICT=1` 升为收集 fail(本期不强制阻断)。

---

## 7. 生命周期:story CANCELLED → 悬空

pm Story 有 FSM 状态(含 CANCELLED)。当 story 被取消,挂在它上面的测试失去功能归属 → 检测器 grep `docs/scrum/story/` 的 `status:` → CANCELLED 时判为**悬空**,提示 RETIRE。

这闭环了用户的"新陈代谢"诉求:用例集随设计迭代与 story 生命周期**自动暴露**过期项,由 review 决定去留。

---

## 8. 落地指南(把框架代码复制进项目)

> qa skill = 方法论的规范源;`examples/backend` = 一次实例化(见 §9)。框架以 **copy-paste asset** 形态提供(skill 非 pip 包,跨目录 import 脆弱)。

### 三步落地

**① 注册 marker** —— 在项目 `pytest.ini` 的 `[pytest]` `markers =` 块加一行(取自 [`assets/pytest_trace_marker.ini.snippet`](../assets/pytest_trace_marker.ini.snippet)):

```ini
trace: 主追溯(定位符 story/epic/endpoint + 版本化源锚 design)。详见 qa/references/test_traceability.md
```

**② 放框架代码** —— 把 [`assets/trace_framework.py`](../assets/trace_framework.py) 复制到项目(如 `tests/trace_framework.py`)。

**③ 挂收集期校验** —— 在 `tests/conftest.py`:

```python
from trace_framework import validate_trace_items

def pytest_collection_modifyitems(config, items):
    validate_trace_items(config, items)
```

落地后:定位符互斥、`ac` 枚举、`design` 格式都在**收集期**被校验(默认 warning,`TRACE_STRICT=1` 升为 fail)。

### 参考:examples/backend 已是实例化范本

- `examples/backend/tests/pytest.ini` —— marker 注册行
- `examples/backend/tests/conftest.py` —— `validate_trace_items` 接入
- `examples/backend/tests/_examples/test_trace_example.py` —— 规范示例(不在 `testpaths`,零回归污染)

---

## 9. 与 spec-xchecker 的关系（后续工作）

本期 `@trace` 是**测试侧自描述**。后续 spec-xchecker 配套:

- `checker_scenario.py`(ST 层)读 `@trace` 的 `story`/`ac` → 替代当前的关键词子串启发式,精确判断"AC 是否有 SIT 覆盖"。
- 输出 **RTM(需求追溯矩阵)**:AC × 测试覆盖网格,join key 用 pytest nodeid(命名序列仅作幂等)。

这一步留作后续 story,本期不实现。
