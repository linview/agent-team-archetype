# 设计变更三步流程 SOP 细则

**用途**: 「设计变更三步流程」（analysis → POC → design update）的完整操作细则

**相关章节**: SKILL.md「设计变更三步流程」（触发判定与铁律摘要）

**使用说明**: 本文档提供三步流程的逐步操作细节、`{project_docs}/analysis/` 目录规范（命名/metadata/三级状态）、analysis 文档结构规范、design Status 枚举。何时走三步流程的判定（假设驱动分级）与三条铁律的核心约束在 SKILL.md 主文件——先读主文件判定路径，需要执行具体步骤时再加载本文。

---

## 概述

开发迭代中的设计变更不是"一次性前置阶段"的例外，而是有章可循的常规循环。触发源：dev 实现反馈 / sentinel 巡检发现 / 新需求 / spec-xchecker 漂移检测。

### 触发分级（假设驱动）

**先判定变更是否含未实证的关键假设**，流程成本按风险自适应：

| 判定 | 特征 | 路径 |
|------|------|------|
| **无未实证关键假设** | 文案修正、参数调整、既有模式的局部微调——失败影响可控，回退成本低 | 跳过三步，直接走 SKILL.md「文档更新流程」5 步升版 |
| **含未实证关键假设** | 架构假设（如执行模型闭环）、技术选型（如某库能否满足语义）、外部依赖行为（如 API 配额/延迟）——假设不成立则设计返工 | 走完整三步流程 |

**为什么假设驱动而非版本增量驱动**：一个 PATCH 级改动也可能踩在未实证的外部依赖行为上；反之一个 MAJOR 重组可能全部基于已实证模式。风险来自假设的实证状态，不是变更的体积。

### 三步流程总览

```
① Analysis 文档（主干分支）
   arch 在 {project_docs}/analysis/{体裁}_{topic}[_v{X.Y}].md 中论证：
   头部 status 演进至 proposal，正文补齐 = 变更动机 + 候选方案对比
   + 假设表 H1..Hn（每条含 pass/fail 判据 + fail 时的设计影响）
        ↓
   [pm 评估] 假设复杂需完整 spike → 立独立 POC Story（重路径）
             快速实验可覆盖 → 无 Story 无 worktree（轻路径）
        ↓
② POC（实验过程不入库）
   执行位 = {project_docs}/test_reports/poc/{topic}/（gitignored，零误提交压力，试错自由）
   侵入式验证（需临时改主干既有代码）才开 .worktrees/poc-{topic}/
         —— 用完即弃，改动不合并 main
   产出 = 假设验证结论表（H1..Hn 各 pass/fail + 证据）
        ↓
③ Design Update（回主干分支）
   全 pass → arch 在 design/ 下重新解读另写正式方案（走「文档更新流程」5 步升版）；
             结论报告 + 关键证据精选迁入 {project_docs}/analysis/poc_{topic}/（入库）；
             analysis 文档转 adopted（冻结）并回填 adopted_by
   有 fail → 回 ① 在 analysis 文档内修订（重大重写开新版本文件）→ 重做 POC 切片
        ↓
   [pm 拆实现 Story] design 状态已定稿才可派实现 Story（pm 四不派）
```

**main branch 语义**：指团队约定的主干分支（master / develop / main 或其他），下同。

---

## `{project_docs}/analysis/` 目录规范

`analysis/` 是 **design 之外的通用过程思考区**：调研、实验、动议、复盘等到达定案之前的全部过程思考都落这里。入版本控制，但**不受 design 版本管理约束**（无 semver 强制、无归档生命周期）。`design/` 只放定案的正式方案——两个目录的分界就是「定案与否」。

### 命名（体裁前缀式）

```
{体裁}_{topic}[_v{X.Y}].md
```

| 组成 | 规则 |
|------|------|
| `{体裁}` | **封闭集，位于最左**：`research`（调研）/ `poc`（实验论证）/ `rca`（根因分析）/ `retro`（复盘）…前缀在左保证解析可靠、按体裁聚类 |
| `{topic}` | 标识符，见下方防膨胀纪律 |
| `[_v{X.Y}]` | 弱版本，**可选**：仅重大重写或 POC fail 回修时使用（如 `research_{topic}_v1.1.md`）；常规演进不升版本 |
| 分隔符 | 下划线，对齐 design/ 树惯例 |

**状态与日期不进文件名**：状态升级（research → proposal → adopted）只改头部 metadata——文件名含状态意味着每次升级都要改名断链；日期由 git 历史承载，`created` 在头部 metadata。

**topic 防膨胀纪律**（topic 是标识符不是摘要）：

- 1-2 个下划线词为宜，**上限 3 个**——超限说明语义该进文档内标题，不是文件名
- **禁缩写**——可 grep 到的完整词优先（`credential` 而非 `cred`）
- 撞名时用**区分词或弱版本**解决，不堆修饰词
- 域语境不进 topic（由体裁前缀/正文/引用方承载）：`research_skill_evaluation.md` 而非 `research_skill_evaluation_domain_analysis.md`

```
✅ research_evaluation_evidence_retention_v1.0.md   # 恰 3 词，合法
✅ poc_sentinel/                                     # 1 词
❌ research_为什么我们需要在评测管线里留存过程数据.md   # 摘要不是标识符
❌ research_evidence_retention.md                    # 缩写，grep 不到完整语义
```

### 头部 metadata 最小集（3 字段封顶）

```markdown
**status**: research | proposal | adopted
**created**: YYYY-MM-DD
**adopted_by**: {design 文档相对路径}#{锚点}    # 仅 adopted 状态必填
```

不增设其他字段（owner/version 等）——过程文档轻治理，git 已承载作者与时间；字段越多，填写成本越高，通道越不可操作。

### 三级状态演进

| status | 语义 | 进入条件 | 正文要求 |
|--------|------|---------|---------|
| `research` | 过程思考中 | 入库即默认 | **完全自由**——笔记、摸底实测、方案草稿，任何组织形式 |
| `proposal` | 设计动议——内容可能成为正式定案 | 论证收敛、准备触发 POC | **必须补最小假设表**（H1..Hn + 可独立判定的 pass 判据 + fail 影响） |
| `adopted` | 已被正式 design 采纳 | design/ 下已另写正式方案并反标本文 | **冻结**——不再修改；后续演进开新文件（新 topic 或 `_v{X.Y}`） |

**为什么 proposal 是状态不是文档类型**：调研到动议是同一份思考的成熟度演进，不是两种文档——拆成两个通道意味着 mv/改名/双份维护。状态在头部流转，文件不动。

**入库即 research**：不设 `notes`/`draft` 之类更低的状态级——进了 git 就是最起码的 research，git 准入本身已是门槛。

### 双向闭环（adopted 的锚定）

- **analysis → design**：转 adopted 时回填 `adopted_by`，指向采纳它的 design 文档锚点
- **design → analysis**：design 新版在版本说明中反标出处（"经 analysis/{topic} 论证（POC 证据：poc_{topic}/）"）

两条锚点让「定案方案 ↔ 过程论证」可互相追溯，且 design 读者能找到完整论证链。

### POC 证据包：`poc_{topic}/`（采纳时精选迁入）

实验过程在 `{project_docs}/test_reports/poc/{topic}/`（gitignored，不入库）；design update 时结论与关键证据迁入：

```
{project_docs}/analysis/poc_{topic}/
├── README.md          # 结论报告：假设表逐条 pass/fail + 证据索引 + 设计影响
└── {evidence files}   # 关键证据（可跑的验证脚本/输出/数据）
```

**迁入规则**：结论报告独立成文（README.md），不依赖 `test_reports/` 或 worktree 分支存在即可完整理解论证链；迁入量以「复现论证所需」为准（可复现验证包可整体入库，先例 `poc_sentinel`；一次性实验只迁 README）。

---

## Step ①: Analysis 文档（主干分支）

analysis 文档在主干分支产出与迭代（它是入版本控制的过程资产，不是 worktree 里的实验品）：

- **位置与命名**：`{project_docs}/analysis/{体裁}_{topic}[_v{X.Y}].md`（见上方目录规范）
- **状态流转**：`research`（自由记录）→ `proposal`（论证收敛，**补最小假设表**——此后才触发 POC）→ `adopted`（被 design 采纳后冻结）
- **状态流转只改头部 metadata**：文件名不动、不 mv、不复制——升级零改名成本
- **重大重写**：POC fail 后若结论推翻原论证主线，开 `_v{X.Y}` 新文件（弱版本），旧版保留可追溯；局部修订则原地改
- **文档结构**：见下方「analysis 文档结构规范」

## Step ②: POC（按重/轻路径）

**执行位：`{project_docs}/test_reports/poc/{topic}/`**（gitignored）——实验过程不入库，零误提交压力，试错自由。仅侵入式验证（必须临时改动主干既有模块才能论证，主干工作区做有污染与漏删风险）才开 worktree `.worktrees/poc-{topic}/` 隔离，用完即弃、改动不合并 main。

重/轻路径只剩**管理强度**差异，执行位相同：

| | 重路径（独立 POC Story） | 轻路径（快速实验） |
|--|------------------------|-------------------|
| **适用** | 假设复杂/多切片/需 gate review | 单点假设、一次实验可覆盖 |
| **管理** | pm 立 POC Story（tags: poc/spike/gate，先例 STORY-1-01） | 无 Story，analysis 文档记录实验设计 |

**POC 切片原则**（源自 sentinel design §14 实践）：最小端到端切片覆盖最多假设；不追求生产级；验证的是"架构假设成立"而非"功能完整"。

**产出** = 假设验证结论表（H1..Hn 各 pass/fail + 证据）——design update 时精选迁入（见 Step ③）。

## Step ③: Design Update（回主干分支）

1. **POC 证据精选迁入**：结论报告 + 关键证据从 `test_reports/poc/{topic}/` 迁入 `{project_docs}/analysis/poc_{topic}/`——入库后才是可被 design 引用的正式证据。迁入量以「复现论证所需」为准：可复现性要求高的验证包可整体入库（先例 `poc_sentinel`），一次性实验只迁 README。
2. **design 升版（重新解读另写）**：在 design/ 下**重新解读 analysis 内容意图，另写正式方案文档**（按 SKILL.md「文档更新流程」5 步执行：定版本增量 → 归档旧版 → 创建新版 → 更新版本历史 → 同步关联文档）——**禁止把 proposal 状态文件 mv 进 design/**；新版元数据 Status 从 `⏳ 待 POC`（若有）转为定稿状态；版本说明反标出处（"经 analysis/{topic} 论证（POC 证据：poc_{topic}/）"）
3. **analysis 文档转 adopted**：头部 `status: adopted` + 回填 `adopted_by`（指向 design 文档锚点），此后冻结
4. **pm 衔接**：design 定稿后 pm 才拆实现 Story（四不派第 4 条）；建议随后重跑 spec-xchecker 四路对齐（design 升版后 Scrum/Code/Tests 可能漂移）

---

## 三条铁律（全文）

1. **design doc 严禁引用 test_reports/**：`test_reports/` 在 .gitignore 中，不随仓库分发，引用它等于引用会消失的证据。轻路径实验结果中的有效信息必须先迁移到 `{project_docs}/analysis/`（入版本控制）才能被 design doc 引用。
2. **POC 实验过程不进版本库**：实验落 `test_reports/poc/{topic}/`（gitignored，试错自由）；侵入式验证开 worktree，改动不合并 main。design update 时只有结论与关键证据精选迁入 `analysis/poc_{topic}/`——被 design 引用的是入库证据，不是实验过程。
3. **禁止 mv 提案进 design/**：采纳时必须在 design/ 下重新解读内容意图、另写正式方案文档。analysis 是过程思考的体裁（自由组织、状态标记），design 是定案规范的体裁（版本管理、结构化章节）——直接搬运会让未经定稿纪律打磨的过程文稿混入正式设计，两个体裁的治理强度差异正是本 SOP 的核心设计。

---

## analysis 文档结构规范

头部 metadata（最小集 3 字段）+ 正文按 status 分级要求：

```markdown
# {标题（自然语言，topic 的展开）}

**status**: research | proposal | adopted
**created**: YYYY-MM-DD
**adopted_by**: {design 文档}#{锚点}        # 仅 adopted 必填

## 变更动机
[为什么改：触发源（dev 反馈/巡检/漂移检测/新需求）+ 不改的风险]

## 候选方案对比
| | 方案 A | 方案 B |
|--|--------|--------|
| 描述 | | |
| 优势 | | |
| 劣势/风险 | | |
| 推荐 | ✅/— | |

## 假设表（POC 验证对象）——proposal 状态必含
| # | 关键假设 | 验证方法 | pass 判据 | fail 时的设计影响 |
|---|---------|---------|----------|------------------|
| H1 | | | | |
| H2 | | | | |

## POC 路径建议
[重路径（独立 POC Story，切片设计）/ 轻路径（快速实验设计）——供 pm 评估参考]
```

**research 状态正文完全自由**——上述章节只是 proposal 状态的完备形态参考：调研笔记可以从一句话开始，摸底实测可以直接贴数据，方案草稿可以只有对比没有结论。升级到 proposal 时才要求补齐（最小假设表为硬性下限）。

**假设表写法要点**（防 POC 论证退化为形式）：
- pass 判据必须**可独立判定**——判据不能从方案本身反推（否则论证是同义反复，STORY-1-01 gate review 的 H3 教训）
- fail 影响必须**预先写明**——POC fail 时直接对照本列决定回修范围，不做事后合理化
- 每条假设**独立可验**——一条假设混两个论点时拆开

可配合模板使用：`templates/analysis_doc_template.md`（占位符版本的同构模板）。

---

## design 元数据 Status 扩展枚举

设计文档元数据 Status 在原有基础上扩展：

| Status | 含义 | 后续动作 |
|--------|------|---------|
| ⏳ 待 POC | 设计含未实证假设，等待/正在进行 POC 论证 | POC 全 pass → 定稿；有 fail → 修订重验 |
| ✅ 设计完成 | 定稿（含经 POC 论证的定稿） | 交 pm 拆 Story |
| 🚧 实施中 | 实施阶段 | dev 实现，漂移反馈回 analysis 文档（proposal 状态） |
| ⚠️ 已废弃 | 被新版本替代 | 归档 |

---

## 实践原型与先例

- **POC gate 原型**：sentinel design v1.2 §14（假设表 H1-H6 格式、spike 切片设计、产出去向）
- **POC Story 先例**：STORY-1-01 POC spike（gate review 对抗性反事实核验、二次 review 签字机制、H3 同义反复教训）
- **analysis 文档先例**：`docs/analysis/research_evaluation_evidence_retention_v1.0.md`（research 类调研报告入库）
- **POC 证据目录先例**：`docs/analysis/poc_sentinel/`（README 结论报告 + 可跑验证包结构）
