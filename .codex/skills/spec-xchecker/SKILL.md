---
name: spec-xchecker
description: "四路交叉验证工具 - 检查 Design Spec ↔ Scrum ↔ Code ↔ Tests 对齐一致性。当用户需要验证代码实现是否符合设计文档、Story AC 是否完整、测试覆盖率是否达标、Story 开发完成检查、MR 前验证、代码审查一致性验证时，必须使用此技能。适用于开发阶段的质量保证，防止设计文档与实现不一致的事故。⚠️ 实验性质技能，建议结合人工审查使用。"
version: "4.2.1"
status: "experimental"
---

# Spec-XChecker - 四路交叉验证工具

> **⚠️ 实验性质技能（Experimental）**
>
> 此技能仍在积极迭代优化中，可能存在误报和漏报。建议作为开发辅助工具，结合人工审查使用。

---

## 快速开始

### 基本用法

```bash
# 检查指定 Story（Medium Mode，推荐）
/spec-xchecker --story 15-23 --mode medium

# 自动模式（自动检测当前 Story）
/spec-xchecker --auto-mode --mode medium
```

### 三种检查模式

| 模式 | 执行时间 | 检查范围 | 适用场景 |
|------|----------|----------|----------|
| **Quick** | <1 秒 | DS 层（设计依据） | Hook 自动触发、简单修改 |
| **Medium** | 5-10 秒 | DS + SC 层 | Story 开发完成、MR 前检查 |
| **Deep** | 30-60 秒 | DS + SC + CT + ST 层 | 大型重构、关键 Story 验证 |

---

## 核心职责

Spec-XChecker 是一个自动化审查工具，用于检查项目文档与代码实现的一致性，防止设计文档与实现不一致的事故。

**四路交叉验证**：
1. **DS 层**：Design Spec ↔ Scrum 文档（验证详细设计是否有概要设计依据）
2. **SC 层**：Scrum AC ↔ 代码实现（验证代码是否实现详细设计）
3. **CT 层**：代码函数 ↔ 单元/API 测试（验证代码是否有测试覆盖）
4. **ST 层**：Scrum AC ↔ SIT/UAT 测试（验证测试是否覆盖详细设计）

**核心原则**：
- **设计域 = SSOT**（唯一真实来源）：概要设计（`docs/design/`）+ 详细设计（`docs/scrum/`）
- **检查顺序铁律**：DS → SC → CT → ST（逐层验证，确保每一步都有依据）
- **静态检查 ≠ 运行时保证**：工具只做静态语义分析，不保证运行时正确性

---

## 检查清单

**📌 完整的 22 项检查清单**：参见 [references/checklist.md](references/checklist.md)

**检查顺序铁律**：DS → SC → CT → ST（不可改变）

### DS 层：Design Spec ↔ Scrum（5 项）

- **DS-01**: Story 是否引用 Design Spec（P1）
- **DS-02**: AC 是否与 Design Spec 一致（P0）
- **DS-03**: Design Spec 引用是否正确（P2）
- **DS-04**: Epic 规划是否与 Design Spec 一致（P2）
- **DS-05**: 设计文档成稿严谨性——语义 review 五问（P1，AI/人工判定，不进脚本自动检查）

### SC 层：Scrum ↔ Code（6 项）

- **SC-01**: 每个 AC 是否有对应代码实现（P1）
- **SC-02**: 代码逻辑是否满足 AC 描述（P0）
- **SC-03**: 新增代码是否引用了正确的表/字段（P1）
- **SC-04**: 错误处理是否覆盖异常场景（P2）
- **SC-05**: 日志输出是否符合规范（P2）
- **SC-06**: Commit Message 是否包含 Story ID（P2）

### CT 层：Code ↔ Tests (UT/API)（5 项）

- **CT-01**: UT 函数是否有对应 test_ 函数（P0）
- **CT-02**: API 接口是否有对应测试（P0）
- **CT-03**: UT 测试覆盖率是否达标（P1）
- **CT-04**: API 测试覆盖率是否达标（P1）
- **CT-05**: Mock 使用是否合理（P2）

### ST 层：Scrum ↔ Tests (SIT/UAT)（6 项）

- **ST-01**: 每个 AC 是否有对应 SIT 用例（P0）
- **ST-02**: SIT 测试是否检查正确对象（P0）
- **ST-03**: SIT 测试是否覆盖异常路径（P1）
- **ST-04**: UAT 测试是否覆盖用户场景（P2）
- **ST-05**: 测试数据质量评分是否达标（P2）
- **ST-06**: SIT 覆盖率是否满足要求（P1）

**优先级说明**：
- **P0**：关键检查，必须通过
- **P1**：重要检查，建议通过
- **P2**：次要检查，可选通过

---

## 智能策略引擎（v3.0）

**📌 详细的 AC 类型映射和策略说明**：参见 [references/strategy_engine.md](references/strategy_engine.md)

### 核心特性

**AC 驱动的动态检查策略**：
- 基于 AC 内容的本地启发式规则（不依赖外部 LLM API）
- 自动识别 Story 类型（Database/Testing/Feature/Hotfix 等）
- 动态生成检查策略（哪些检查做，哪些跳过）

**三级智能策略引擎**：
1. **Level 1**：扩展 AC 类型映射表（10 种类型）
2. **Level 2**：负向规则引擎（positive_checks + negative_checks 机制）
3. **Level 3**：动态置信度计算（单一类型 95%，混合类型 80%，无法分类 60%）

**效果提升**：
- STORY-15-22 检查项减少 43%（21→12）
- 通过率提升 76%（33%→58%）

---

## 高级用法

**📌 详细使用指南**：参见 [references/usage_guide.md](references/usage_guide.md)

### 指定检查范围

```bash
# 只检查 Code + Tests 层
/spec-xchecker --story 15-23 --mode medium --scope code,test

# 只检查 Design + Scrum 层
/spec-xchecker --story 15-23 --mode quick --scope ds,sc
```

### 指定输出格式

```bash
# Markdown 报告（默认）
/spec-xchecker --story 15-23 --mode medium

# JSON 报告
/spec-xchecker --story 15-23 --mode medium --format json
```

---

## 与其他工具的区别

| 维度 | `/review` | `/spec-xchecker` |
|------|-----------|-----------------|
| **核心目标** | 代码质量（Code is good?） | 对齐一致性（Code matches Spec?） |
| **检查依据** | 通用编程规范、项目规范 | Design Spec、Story AC、测试用例 |
| **检查范围** | 代码逻辑、风格、性能、安全 | 代码与文档的一致性 |
| **典型场景** | 日常 Code Review | Story 开发、MR 前检查 |

**协作关系**：
- 代码质量检查 → `/review` SKILL
- 对齐一致性检查 → `/spec-xchecker` SKILL
- 大型重构检查 → `/spec-xchecker --mode deep`

---

## 工具能力边界

**Spec-XChecker 能做什么**（静态检查）：
1. **文档结构检查**：文件是否存在、引用是否正确
2. **文本语义分析**：AC 关键词提取、代码函数名匹配
3. **覆盖率统计**：测试函数数量、表引用检查
4. **模式匹配**：Commit Message 格式、日志关键字

**Spec-XChecker 不能做什么**（运行时保证）：
1. ❌ **动态行为验证**：代码在运行时是否正确
2. ❌ **集成问题**：多个模块协同工作是否正常
3. ❌ **性能问题**：代码执行效率、资源占用
4. ❌ **安全漏洞**：SQL 注入、XSS 等运行时安全问题

**工程实践建议**：
- ✅ Spec-XChecker 用于**开发阶段**（MR 前检查、Story 完成验证）
- ✅ 运行时保证依赖**SIT/UAT 测试**（集成测试、用户验收测试）
- ✅ 生产环境依赖**监控告警**（日志、Metrics、Tracing）

---

## 🤝 Agent Team 协作

Spec-XChecker 与其他角色密切协作：

- **架构设计** → [arch SKILL](../arch/SKILL.md)
  - Design Spec 版本管理
  - 文档归档规范
  - 参考：`docs/design/` 中的设计文档

- **开发工作流** → [dev SKILL](../dev/SKILL.md)
  - 代码实现验证
  - 单元测试覆盖
  - Commit Message 规范

- **测试验证** → [qa SKILL](../qa/SKILL.md)
  - SIT/UAT 测试覆盖
  - 测试数据质量
  - 参考：`test_reports/` 中的测试报告

- **项目管理** → [pm SKILL](../pm/SKILL.md)
  - Story AC 验证
  - Epic 规划一致性
  - 参考：`docs/scrum/story/` 中的 Story 文档

---

## 目录结构

```
.codex/skills/spec-xchecker/
├── SKILL.md                     # 本文件（主入口）
├── scripts/                     # 所有可执行代码（官方标准）
│   ├── spec-xchecker.py         # 主入口脚本
│   ├── report_generator.py      # 报告生成器
│   ├── strategy_generator.py    # 智能策略引擎（v2.5）
│   ├── trigger_check.sh         # Stop Hook 触发脚本
│   ├── notify_pending_reports.sh # SessionStart Hook 通知脚本
│   ├── lib/                     # Python 模块
│   │   ├── story_resolver.py    # Story ID + Design Spec 加载
│   │   ├── classify.py          # 文件分类
│   │   └── get_memory_dir.sh    # Memory 目录计算
│   └── checkers/                # 检查器模块
│       ├── checker_design.py    # DS 层检查
│       ├── checker_code.py      # SC 层检查
│       ├── checker_test.py      # CT 层检查
│       ├── checker_scenario.py  # ST 层检查
│       └── strategy_generator.py# 智能策略引擎
├── references/                  # 参考文档（官方标准，按需加载）
│   ├── usage_guide.md           # 详细使用指南
│   ├── checklist.md             # 完整的 22 项检查清单
│   ├── strategy_engine.md       # 智能策略引擎详细说明
│   └── troubleshooting.md       # 故障排查指南
├── tests/                       # 回归测试装置（仅 .claude 栈；DS 层反例 + 双栈镜像守护，v4.1.3）
└── assets/                     # 静态资源（官方标准）
    └── config/
        └── config.yaml          # 配置文件
```

**目录结构说明**（符合官方最佳实践）：
- ✅ **scripts/** - 所有可执行代码（Python 脚本、Shell 脚本、模块）
- ✅ **references/** - 参考文档（按需加载，支持渐进式披露）
- ✅ **assets/** - 静态资源文件（配置文件、模板等）
- ✅ **SKILL.md** - 主入口（<500 行，包含核心内容和导航）

---

## 常见问题

**Q: 如何选择检查模式？**
- Quick：Hook 自动触发、简单修改
- Medium：Story 开发完成、MR 前检查（推荐）
- Deep：大型重构、关键 Story 验证

**Q: 检查通过但实际有问题？**
- 使用 `--mode deep` 进行更深入的检查
- 检查报告详情，查看具体是哪一项检查失败

**Q: 找不到 Story 文档？**
- 检查 `docs/scrum/story/story-13-{story_id}-*.md` 是否存在
- 确认 Story ID 格式正确（例如：15-23）

**Q: 没有 Design Spec？**
- 在 Story 文档中添加 `Design Spec: ../design/xxx.md`，或 frontmatter 列表形式 `design_docs:`/`design_refs:`（v4.1.3 起双字段兼容）
- 创建对应的 Design Spec 文档

**Q: Story 用 design_refs 字段（frontmatter）引用设计文档，为什么以前报"未引用 Design Spec"？**
- v4.1.3 起格式 1 双字段兼容（`design_docs`/`design_refs`），旧版本请升级
- 值支持 `path.md`、`path.md#锚点`、`path.md（章节注释）` 三种形态，路径后缀注释自动剥离

**Q: COMPLETED 终态 Story 引用已归档的旧版 Design Spec，DS-01 报 FAIL？**
- 属预期形态（终态历史快照语义）：终态 Story 按项目裁定保留历史版本引用，design 文档语义化版本演进归档后引用悬空
- 不建议刷新终态引用，工具也不做自动 fallback 到 `archive/`（会掩盖真实引用漂移）

**Q: 遇到其他问题？**
- 参见 [references/troubleshooting.md](references/troubleshooting.md) 获取详细故障排查指南

---

## 详细参考

以下参考文档会在需要时按需加载：

- **[详细使用指南](references/usage_guide.md)** - 命令行参数、Hook 配置、报告位置
- **[完整检查清单](references/checklist.md)** - 22 项检查的详细说明
- **[智能策略引擎](references/strategy_engine.md)** - AC 类型映射、负向规则、置信度计算
- **[故障排查指南](references/troubleshooting.md)** - 常见问题和解决方案

---

**版本**: v4.2.1 | **最后更新**: 2026-11-24 | **维护者**: maintainer@example.com

**更新日志**:
- v4.2.1 (2026-11-24): 🐛 **DS 层 fail-open 盲区修复——降级语义分离（SKIP/WARN）**
  - `checkers/checker_design.py` 三处「未命中即 PASS」降级路径修复（ISSUE-20261124-003）：DS-02 需求章节提取失败不再 `passed=True` 假绿，改返回 `passed=False + status='SKIP'`（未覆盖≠通过，不计入失败统计）；DS-03 版本正则扩展（原只认中文键「版本：vX.Y」→ 中文/英文键 + v 前缀可选 + YAML 引号形态），仍未识别时 WARN 显性化「版本校验未覆盖」；DS-04 无 Epic 引用/无法对账时 WARN 显性化「DS-04 未覆盖」（passed 保留 True，非 Epic 拆分属合法场景）
  - `CheckResult` 新增 `status` 字段（None/'SKIP'/'WARN'）；主流程 summary 新增 skipped/warned 统计，SKIP 不计入 failed/P0 issues（exit code 语义不变）；`report_generator.py` 报告新增「⏭️ 未覆盖项」「⚠️ 降级提示项」独立段落——覆盖率说明而非绿勾/红叉
  - 测试新增 `tests/test_ds_fail_open.py`（14 用例 × 双栈：正反例 + 降级改造不吞真实失败守护）；evals 激活 e11 反事实用例（`grade_programmatic.py --e11`，ds05_fixture 真实素材直调，抓到带引号 frontmatter 第四形态盲点）
- v4.2 (2026-11-24): 🎯 **DS 层新增 DS-05 设计文档成稿严谨性——语义 review 五问**
  - DS 层 4 项 → 5 项，清单总数 21 → 22：DS-05「版本记录单一权威 / 编号一号一义 / 名实三面对账 / 引用现行 / 勘误无歧义」，P1
  - **AI/人工判定项，不进脚本自动检查**：需要结合语义/上下文/因果理解（语义 review 不作为强制格式标准）；结构机械项（frontmatter 必填字段/TOC/编号纪律/链接存在性/test_reports 引用）不在 DS 层判定范围——DS-05 只负责语义层判定，机械格式项由设计文档产出侧的成稿纪律把关
  - 定位：设计文档在源头含糊，偏差沿 Story→Code→Tests 逐级放大；DS 层是四路验证第一道闸，把严谨性审查前移到设计文档本身
  - `checklist.md` DS 段补 DS-05 判定要点；`checkers/checker_design.py` 不变（DS-05 非机械项）
- v4.1.3 (2026-11-02): 🐛 **DS 层双修复**
  - `story_resolver.py` 格式 1：字段名兼容 `design_refs`（部分项目 Story 模板使用该字段，旧代码只认 `design_docs`，DS-01/02/03 对此类 Story 整类误报"未引用"）；值尾兼容 `path.md（全角括号章节注释）`——统一截取首个 `.md` 前纯路径，`#锚点` 与 `（注释）` 两种尾部均剥离
  - `checker_design.py` DS-04：新增最强证据快速通道——Design Spec 显式指派本 Story（正文含 `STORY-x-xx` 反向追踪字样）时直接通过；一份 guide 跨 Epic 承载多个 Story 时 Epic 编号无交集属常态，不再误报"Epic 引用不一致"
  - 顺手修复：.codex 栈 `trigger_check.sh`/`notify_pending_reports.sh` `PROJECT_DIR` 值尾多余 `}` 笔误（memory 目录计算走偏）
  - 新增 `tests/` 回归装置（DS 层反例清单 + 双栈镜像一致性守护，仅 .claude 栈）
  - 已知边界（预期形态，非缺陷不修）：终态（COMPLETED）Story 按项目裁定保留历史版本引用，design 文档语义化版本演进归档后引用悬空，DS-01 对此类 Story 报 FAIL 属终态历史快照语义
- v4.1.2 (2026-09-04): 🐛 `story_resolver.py` B5 修复——`design_docs` 值形如 `path.md#锚点` 时锚点段夹在 `.md` 与右引号之间，旧正则要求引号紧跟 `.md` 导致整类失配（DS-01/02/03 全误报）。版本序列补录条目（v4.1.3 已包含并扩展其语义）
- v4.1.1 (2026-08-15): 🐛 hook 脚本 `source utils/` 悬空路径修复为 `scripts/lib/`;.codex 栈 hook 恢复 Codex 自指环境变量(单层回退,清除栈绑定污染残留)
- v4.1 (2026-07-03): 🐛 **B2/B3/B4 工具缺陷修复**（patch，对比验证驱动）
  - **B2** `strategy_generator.py`：`go_code` 模式收紧（移除裸"实现"/"新增函数"/"创建 API"，改用 `.go`/`internal/pkg`/`go build`），Python 项目不再误判 go_code
  - **B3** `spec-xchecker.py`：`mode` 层裁剪（quick=DS / medium=DS+SC / deep=全集）+ UNKNOWN fallback 到全集 + 汇总统计改用裁剪后 `strategy_checks`（修 mode 不裁剪 + UNKNOWN 时 total=0）
  - **B4** `story_resolver.py`：`load_design_spec` 格式2 markdown 链接识别扩展（`link_path` 含 `design/` 也识别），DS-01 不再误报"未引用"
  - 对比验证：EPIC-5 全 5 Story before/after 全绿，quick=4/medium=10/deep=21，DS-01 由"未引用"→通过
  - 残留 R1（中文无空格正则）/R3（COMPLETED Story AC 提取）/R2（JSON stdout 污染）未治本，靠 UNKNOWN fallback 兜底，待另立 Story
- v4.0 (2026-04-29): 🎯 **官方标准重构**：完全符合 Claude Code 官方文档
  - **目录结构规范化**：调整为官方标准目录
    - ✅ `scripts/` - 所有可执行代码（包括 lib/ 和 checkers/ 子目录）
    - ✅ `references/` - 参考文档（按需加载，支持渐进式披露）
    - ✅ `assets/` - 静态资源（配置文件）
    - ❌ 移除非标准的 `lib/` 和 `checkers/` 顶级目录
  - **导入路径更新**：所有 Python 导入路径更新为 `scripts.lib.*` 和 `scripts.checkers.*`
  - **SKILL.md 目录结构章节**：更新为新的官方标准结构
  - **参考来源**：[Extend Claude with skills - Claude Code Docs](https://code.claude.com/docs/en/skills)
- v3.0 (2026-04-29): 🎯 **重大重构**：符合 Claude Code Skill 最佳实践
  - 更新 frontmatter（skill → name）
  - 优化 description，更"pushy"的触发描述
  - 精简主 SKILL.md（483 行 → ~300 行，减少 38%）
  - 提取详细内容到 references/ 目录
  - 添加 Agent Team 协作章节
  - 添加清晰的导航指引
- v2.5 (2026-04-25): 智能策略引擎（三级智能、负向规则、动态置信度）
- v2.4 (2026-04-20): AC 驱动的动态检查策略（POC）
- v2.3 (2026-04-15): 三域一致性模型、检查顺序铁律
