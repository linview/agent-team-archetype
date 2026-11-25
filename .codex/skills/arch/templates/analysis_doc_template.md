# Analysis 文档模板

**用途**: 在 `{project_docs}/analysis/` 创建分析文档（「设计变更三步流程」第①步载体——调研/实验/动议的过程思考区）

**使用说明**:
1. 复制此模板到 `{project_docs}/analysis/{体裁}_{topic}[_v{X.Y}].md`（体裁前缀在左：research / poc / rca / retro…）
2. **topic 是标识符不是摘要**：1-2 词为宜、上限 3 个下划线词；禁缩写；撞名用区分词/弱版本解决——超限的语义放进文档内标题
3. **状态与日期不进文件名**——状态升级只改下方 `status` 字段，文件名不动
4. `research` 状态正文完全自由（可从一句话开始）；升级到 `proposal` 时**必须补最小假设表**——pass 判据要可独立判定，不能从方案本身反推

---

## Analysis 文档模板

# {标题：topic 的自然语言展开}

**status**: research  # research → proposal → adopted（adopted 后冻结，演进开新文件）
**created**: {YYYY-MM-DD}
**adopted_by**: {project_docs}/design/{文档}#{锚点}  # 仅 adopted 状态回填

---

## 变更动机

[为什么改：触发源（dev 实现反馈 / sentinel 巡检 / spec-xchecker 漂移 / 新需求）+ 不改的风险（在未实证假设上做实现的返工代价）]

## 候选方案对比

| | 方案 A: {名称} | 方案 B: {名称} |
|--|---------------|---------------|
| 描述 | | |
| 优势 | | |
| 劣势/风险 | | |
| 推荐 | ✅ / — | |

[推荐理由与取舍说明]

## 假设表（POC 验证对象）——proposal 状态必含

| # | 关键假设 | 验证方法 | pass 判据 | fail 时的设计影响 |
|---|---------|---------|----------|------------------|
| H1 | | | | |
| H2 | | | | |
| H3 | | | | |

> **写法要点**（防 POC 论证退化为形式）：
> - pass 判据必须**可独立判定**——判据不能从方案本身反推（同义反复，STORY-1-01 gate review H3 教训）
> - fail 影响必须**预先写明**——POC fail 时直接对照本列决定回修范围，不做事后合理化
> - 每条假设**独立可验**——一条假设混两个论点时拆开

## POC 路径建议

[供 pm 评估参考，二选一或组合]：

- **重路径（独立 POC Story）**：假设复杂/多切片。切片设计：[最小端到端切片覆盖哪些 H；附加切片覆盖哪些 H]。
- **轻路径（快速实验）**：单点假设。实验设计：[做什么实验、看什么指标]。

> 执行位统一为 `{project_docs}/test_reports/poc/{topic}/`（不入库，试错自由）；侵入式验证才开 `.worktrees/poc-{topic}/`（不合并）。design update 时结论与关键证据迁入 `{project_docs}/analysis/poc_{topic}/`。

## adopted 回填（采纳时执行）

[被 design 采纳时：① design/ 下已重新解读另写正式方案（非 mv 搬运）；② 本文件 `status` 改 adopted；③ 回填 `adopted_by` 指向 design 文档锚点；④ 本文件冻结，后续演进开新文件]
