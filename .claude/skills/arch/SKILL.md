---
skill: "arch"
description: "架构师工作技能 - 架构设计、文档管理、语义化版本控制、设计审查、设计变更论证（analysis 文档 research→proposal→adopted 状态演进）与 POC 论证。当用户提到架构、设计文档、版本管理、技术选型、系统设计、数据模型、API设计、文档审查、设计规范、架构决策、设计变更、设计动议、分析文档、调研报告、POC、架构图/流程图/时序图/E-R 图等图表展示（mermaid 渲染）、文档可读性/成稿自检/去黑话/TOC/元数据整理、或需要创建/更新设计文档时，必须使用此技能。确保所有设计文档遵循语义化版本规范、命名约定与成稿可读性纪律。"
version: "2.5"
---

# Architect 工作技能

## 核心职责

1. **架构设计**：设计系统架构、数据模型、服务层架构、应用层架构
2. **文档管理**：维护设计文档，遵循语义化版本管理规范
3. **技术决策**：制定技术选型、设计模式、最佳实践
4. **跨层协调**：协调系统层、数据层、服务层、应用层的设计一致性
5. **设计审查**：Review 设计文档，确保架构合理性和可实施性
6. **设计变更论证**：含未实证关键假设的设计变更，在 `{project_docs}/analysis/` 维护分析文档并演进至 proposal 状态，经 POC 论证后升版正式设计

---

## 📋 设计文档管理规范（铁律）

### ⚠️ 核心原则：语义化版本 + 层次分类 + 归档管理

**设计文档必须遵循以下规则**：

1. **按架构层次分类命名**：使用 `{layer}_design_{sem_ver}.md` 格式
2. **语义化版本号**：变更粒度直接体现在文件名版本部分
3. **归档管理**：旧版本归档到 `{project_docs}/design/archive/`
4. **禁止描述性命名**：不使用 plan、update、design 等临时文件名
5. **设计变更走 analysis 论证通道**：含未实证关键假设的设计变更，先在 `{project_docs}/analysis/{体裁}_{topic}[_v{X.Y}].md` 演进至 proposal 状态（见「设计变更三步流程」章节）

**说明**:
- `{layer}`: 架构层次（如 system, service, data_layer, api）
- `{sem_ver}`: 语义化版本号（如 v1.0, v2.3.1）
- `{project_docs}`: 项目文档目录（通常为 docs/）

---

### 📏 文档长度控制原则

**核心要求**：
- **主文档**（遵循 `{layer}_design_{sem_ver}.md` 命名）：建议保持在 1000-2000 行
- **子文档**（遵循 `{layer}/{topic}_guide_{sem_ver}.md` 命名）：建议 200-500 行
- **避免过度示例化**：减少代码示例和详细实现指南

**拆分策略**：
1. **主文档保留核心设计**：架构概述、职责分离、数据模型概览、查询策略
2. **子文档聚焦专题实现**：特定技术实现、配置详解、部署方案等
3. **跨文档引用**：主文档提供概述和引用，子文档提供详细实现

**文档结构示例**（使用占位符）：
```
{project_docs}/design/
├── {layer}_design_v{major}.{minor}.{patch}.md    # 主文档
├── {layer}/                                       # 子文档目录（可选）
│   ├── {topic}_guide_v{major}.{minor}.{patch}.md
│   └── {implementation}_v{major}.{minor}.{patch}.md
└── archive/                                       # 归档目录
    └── {layer}_design_v{major}.{minor}.{patch}_{date}.md
```

**说明**:
- `{project_docs}`: 项目文档目录（如 docs/）
- `{layer}`: 架构层次（如 service, data_layer, api）
- `{major}.{minor}.{patch}`: 版本号（如 4.1.2）
- `{topic}`: 专题名称（如 fk_constraint, data_sync）
- `{implementation}`: 实现名称（如 ttl_cleanup）
- `{date}`: 归档日期（YYYYMMDD，如 20260422）

**引用格式**（主文档 → 子文档）：
```markdown
### {章节编号} {专题名称}

> **详细设计文档**：[{专题名称} v{version}]({layer}/{topic}_guide_v{version}.md)

**核心原则**：
1. {原则 1}
2. {原则 2}
3. {原则 3}
```

**判断标准**（何时拆分子文档）：
| 场景 | 处理方式 | 行数建议 |
|------|---------|---------|
| 核心架构设计 | 保留在主文档 | 100-200 行 |
| 详细实现指南 | 拆分子文档 | 200-500 行 |
| 完整实施方案 | 拆分子文档 | 300-500 行 |
| 大型时序图/流程图 | 拆分子文档 | > 50 行 |

**禁止事项**：
- ❌ 主文档超过 2000 行（必须拆分）
- ❌ 子文档超过 500 行（进一步拆分或精简）
- ❌ 代码示例占比超过 30%（移到子文档或代码仓库）
- ❌ 过度示例化（保留关键示例，删除重复说明）

---

### 🔗 跨文档引用准确性原则

**引用路径规范**（使用相对路径）：
1. **主文档 → 子文档**：使用相对路径 `{layer}/`（同层目录）
2. **子文档 → 主文档**：使用相对路径 `../{layer}_design_v{version}.md`
3. **子文档 → 子文档**：使用相对路径 `./{filename}.md`
4. **所有文档 → Story/报告**：使用相对路径 `../../{dir}/{subdir}/`

**说明**:
- `{layer}`: 架构层次（如 service, data_layer）
- `{version}`: 版本号（如 v1.0, v2.1）
- `{dir}`: 目录名称（如 scrum, test_reports）
- `{subdir}`: 子目录名称（如 story, reports）

**引用格式**：
```markdown
# 主文档中的引用
> **详细设计文档**：[{专题名称} v{version}]({layer}/{topic}_guide_v{version}.md)

# 子文档中的引用
- **[主文档：{layer}_design_v{version}.md - {章节编号}节](../{layer}_design_v{version}.md#{section-id})**
- **[{story-id}]({project_docs}/scrum/story/{story-file}.md)**
```

**验证清单**：
- [ ] 所有引用路径使用相对路径（不使用绝对路径）
- [ ] 锚点链接（`#section-id`）准确有效
- [ ] 跨文档引用在不同目录层级下正常工作
- [ ] 子文档移动后更新主文档引用路径

---

## 文档命名规范

### 架构层次分类

| 架构层次 | 文档命名模式 | 占位符说明 |
|---------|-------------|-----------|
| **系统架构** | `system_architecture_{sem_ver}.md` | {sem_ver} = v{major}.{minor}.{patch} |
| **数据层/数据存储** | `data_layer_design_{sem_ver}.md` | {sem_ver} = v{major}.{minor}.{patch} |
| **服务层架构** | `service_layer_architecture_{sem_ver}.md` | {sem_ver} = v{major}.{minor}.{patch} |
| **API/应用层** | `api_design_{sem_ver}.md` | {sem_ver} = v{major}.{minor}.{patch} |
| **FAQ 文档** | `{name}_faq_{sem_ver}.md` | {name} = 主题名称，{sem_ver} = 版本号 |

### 语义化版本规则

**版本格式**：`v{MAJOR}.{MINOR}.{PATCH}`

| 版本类型 | 版本号示例 | 变更类型 | 判断标准 |
|---------|-----------|---------|---------|
| **MAJOR** | v2.0 → v3.0 | 重大功能新增、架构变更 | 新增完整章节、数据模型变更、接口重定义 |
| **MINOR** | v2.0 → v2.1 | 功能新增、向后兼容 | 新增小功能、配置项、优化项 |
| **PATCH** | v2.0 → v2.0.1 | Bug 修复、小改动 | 修正错误、补充说明、格式调整 |

### ❌ 禁止的命名方式

**以下命名方式严格禁止**：

1. ❌ 描述性语言命名的临时文件：
   - `{feature}_design_updates.md`
   - `plan_{date}.md`
   - `design_update_phase1.md`
   - 任何带有 `plan`、`update`、`design` 等前缀的文件名

2. ❌ 不带版本号的文档：
   - `{layer}_design.md`（缺少版本号）
   - `faq.md`（缺少版本号）

3. ❌ 使用日期作为版本号：
   - `{layer}_design_{date}.md`（如 20260204）

4. ❌ `design/` 下任何 proposal 命名的文件：
   - `{project_docs}/design/proposal.md`、`{topic}_proposal_v{sem_ver}.md` 等一律禁止
   - **proposal 不是文档类型，是 analysis 文档头部的状态**（见「设计变更三步流程」章节）——设计动议落 `{project_docs}/analysis/{体裁}_{topic}[_v{X.Y}].md`，状态在头部 metadata 流转

5. ❌ analysis 文件名含状态或日期：
   - `research_{topic}_proposal_v1.0.md`（状态 `proposal` 进了文件名——状态升级即改名断链）
   - `research_{topic}_20260907.md`（日期进文件名——版本信息由 git 承载，`created` 在头部 metadata）
   - **✅ 正确**：`research_{topic}.md`、`research_{topic}_v1.1.md`（弱版本仅在重大重写时使用）

**✅ 正确的命名方式**：

- ✅ `{layer}_design_v{major}.{minor}.{patch}.md`
- ✅ `{layer}_design_v{major}.{minor}.md`
- ✅ `{name}_faq_v{major}.{minor}.{patch}.md`
- ✅ `{体裁}_{topic}[_v{X.Y}].md`（`{project_docs}/analysis/` 下的分析文档，见「设计变更三步流程」）

---

## 文档归档规范

### 归档时机

**每次 MAJOR 或 MINOR 版本更新时**，必须归档旧版本：

```bash
# 归档旧版本（示例）
mv {project_docs}/design/{layer}_design_v{major}.{minor}.md \
   {project_docs}/design/archive/{layer}_design_v{major}.{minor}_$(date +%Y%m%d).md

# 说明:
# - {project_docs}: 项目文档目录（如 docs/）
# - {layer}: 架构层次（如 service_layer, data_layer）
# - {major}.{minor}: 版本号
```

### 归档文件命名

**格式**：`{filename}_v{version}_{date}.{ext}`

| 组成部分 | 说明 | 示例 |
|---------|------|------|
| `{filename}` | 原文件名（不含版本号） | `{layer}_design` |
| `{version}` | 语义化版本号 | `v2.0` |
| `{date}` | 归档日期（YYYYMMDD） | `20260204` |
| `{ext}` | 文件扩展名 | `.md` |

**完整示例**：
- `{layer}_design_v{version}_{date}.md`（如 `service_layer_architecture_v2.0_20260204.md`）

### 默认保留位置

**`{project_docs}/design/` 目录只保留最新版本**：

```bash
# 正确的目录结构（示例）
{project_docs}/design/
├── {layer1}_design_v{version}.md      # 最新版本
├── {layer2}_design_v{version}.md      # 最新版本
└── {layer3}_design_v{version}.md      # 最新版本

{project_docs}/design/archive/
├── {layer1}_design_v{version}_{date}.md   # 历史版本
├── {layer2}_design_v{version}_{date}.md   # 历史版本
└── {layer3}_design_v{version}_{date}.md   # 历史版本

{project_docs}/analysis/              # 通用过程思考区（调研/实验/动议，入版本控制、不受 design 版本管理约束）
├── research_{topic}[_v{X.Y}].md       # 技术调研（status: research → proposal → adopted）
├── rca_{topic}[_v{X.Y}].md            # 根因分析
├── retro_{topic}[_v{X.Y}].md          # 复盘
├── poc_{topic}/                       # POC 精选证据目录（实验在 test_reports/poc/{topic}/，采纳时迁入）
│   ├── README.md                      # 结论报告：假设表逐条 pass/fail + 证据索引
│   └── {evidence files}               # 关键证据（验证脚本/输出/数据）
```

**说明**：
- `archive/` 目录存放归档的历史版本（带日期戳）
- `analysis/` 是 design 之外的独立目录：design/ 只放定案的正式方案，analysis/ 承载到达定案之前的全部过程思考（体裁前缀式命名，状态在头部 metadata，不进文件名）

---

## 文档更新流程

> 本流程是「设计变更三步流程」第③步的执行细节。含未实证关键假设的变更，先走完 analysis（proposal 状态）→ POC（见下一章），再回到本流程升版。

### Step 1: 确定变更类型

**判断版本号增量**：

| 变更内容 | 版本类型 | 文件名变化 |
|---------|---------|-----------|
| 新增完整章节 | MAJOR | v2.0 → v3.0 |
| 数据模型变更（DDL 脚本） | MAJOR | v2.3 → v3.0 |
| 接口重定义 | MAJOR | v1.0 → v2.0 |
| 新增配置项 | MINOR | v2.0 → v2.1 |
| 新增小功能 | MINOR | v2.0 → v2.1 |
| 修正错误 | PATCH | v2.0 → v2.0.1 |
| 补充说明 | PATCH | v2.0 → v2.0.1 |

### Step 2: 归档旧版本（如需要）

**MAJOR 或 MINOR 版本更新时**：

```bash
# 进入项目目录
cd {project_root}

# 归档旧版本
mv {project_docs}/design/{layer}_design_v{old_version}.md \
   {project_docs}/design/archive/{layer}_design_v{old_version}_$(date +%Y%m%d).md

# 说明:
# - {project_root}: 项目根目录
# - {project_docs}: 项目文档目录（如 docs/）
# - {layer}: 架构层次（如 service, data_layer）
# - {old_version}: 旧版本号（如 v2.0）
```

**PATCH 版本更新时**：
- 不归档（直接覆盖文件）

### Step 3: 创建新版本

**方式 1：复制旧版本（推荐）**

```bash
# 复制旧版本作为基础
cp {project_docs}/design/archive/{layer}_design_v{version}_{date}.md \
   {project_docs}/design/{layer}_design_v{new_version}.md

# 编辑新版本，更新内容
vim {project_docs}/design/{layer}_design_v{new_version}.md
```

**方式 2：直接创建新版本**

```bash
# 直接创建新版本
vim {project_docs}/design/{layer}_design_v{new_version}.md
```

### Step 4: 更新文档元数据（frontmatter）

**在文档头部 frontmatter 中更新版本元数据**——版本记录单一权威化：本版说明写 `version_notes`，`version_history` 只留最近 3-5 条，完整沿革由 git 历史与 archive/ 承载，**正文不保留版本历史表**：

```yaml
---
title: "{文档标题}"
version: "v{new_version}"
status: "✅ 设计完成"
created: "YYYY-MM-DD"
version_notes:
  - "v{new_version} 新增功能/修正内容 1"
  - "v{new_version} 新增功能/修正内容 2"
version_history:
  - "v1.0 初始版本"
  - "v2.0 {变更说明}"
  - "v{new_version} {变更说明}"
---
```

**版本三处一致**：文件名 `v{new_version}` = frontmatter `version` = 正文 H1 标题尾注版本，不一致由成稿自检脚本拦截（见「成稿可读性纪律」）。

### Step 5: 更新相关文档

**如果更新涉及多个文档，保持版本号一致**：

| 主文档版本 | FAQ 文档版本 | 示例场景 |
|-----------|------------|---------|
| v3.0 | v3.0 | 主文档 MAJOR 更新，FAQ 同步更新 |
| v2.1 | v2.1 | 主文档 MINOR 更新，FAQ 同步更新 |
| v2.0.1 | 不变 | 主文档 PATCH 更新，FAQ 不变 |

---

## 设计变更三步流程（proposal → POC → design update）

开发迭代中的设计变更不是"一次性前置阶段"的例外，而是有章可循的常规循环。触发源：dev 实现反馈 / sentinel 巡检发现 / 新需求 / spec-xchecker 漂移检测。

### 触发分级（假设驱动）

| 判定 | 特征 | 路径 |
|------|------|------|
| **无未实证关键假设** | 文案修正、参数调整、既有模式微调——回退成本低 | 跳过三步，直接走上方「文档更新流程」5 步 |
| **含未实证关键假设** | 架构假设、技术选型、外部依赖行为——假设不成立则设计返工 | 走完整三步流程 |

### 三步流程

```
① Analysis 文档（主干分支）
   {project_docs}/analysis/{体裁}_{topic}[_v{X.Y}].md，头部 status 演进至 proposal
   = 变更动机 + 候选方案对比 + 假设表 H1..Hn（pass/fail 判据 + fail 设计影响，proposal 状态必含）
        ↓
   [pm 评估] 重路径（立独立 POC Story）/ 轻路径（快速实验，无 Story 无 worktree）
        ↓
② POC（实验过程不入库）
   执行位 = {project_docs}/test_reports/poc/{topic}/（gitignored，零误提交压力，试错自由）
   侵入式验证（需临时改主干既有代码）才开 .worktrees/poc-{topic}/——用完即弃不合并
        ↓
③ Design Update（回主干分支）
   全 pass → 升版 design（5 步流程）；结论报告 + 关键证据精选迁入 analysis/poc_{topic}/
            （入库后才可被 design 引用）；analysis 文档转 adopted（冻结，回填 adopted_by）
   有 fail → 回 ① 在 analysis 文档内修订（重大重写开新版本文件）重做切片
        ↓
   [pm 拆实现 Story] design 定稿才派实现 Story（pm 四不派第 4 条）
```

**main branch 语义**：指团队约定的主干分支（master / develop / main 或其他）。

### 三条铁律

1. **design doc 严禁引用 test_reports/**：`test_reports/` 在 .gitignore 中，轻路径实验的有效信息必须先迁入 `{project_docs}/analysis/`（入版本控制）才能被 design doc 引用
2. **POC 实验过程不进版本库**：实验落 `test_reports/poc/{topic}/`（gitignored，试错自由）；侵入式验证开 worktree，改动不合并 main。design update 时只有结论与关键证据精选迁入 `analysis/poc_{topic}/`——被 design 引用的是入库证据，不是实验过程
3. **禁止 mv 提案进 design/**：采纳时必须在 design/ 下**重新解读内容意图、另写正式方案文档**——analysis 是过程思考体裁，design 是定案规范体裁，直接搬运会让未经定稿纪律打磨的过程文稿混入正式设计

### 🔗 细则与模板（按需加载）

逐步操作细节（Step ①②③ 详解、重/轻路径对照表、`analysis/` 目录规范——命名/metadata 最小集/三级状态演进/双向闭环）、analysis 文档结构规范（含防同义反复的假设表写法要点）、design Status 扩展枚举（`⏳ 待 POC`），见 **[设计变更三步流程 SOP 细则](references/design_iteration_sop.md)**。analysis 文档模板见 [templates/analysis_doc_template.md](templates/analysis_doc_template.md)。

---


## 文档结构规范

### 必需章节

**每个设计文档必须包含以下章节**，头部按「frontmatter → TOC → 正文」**渐进式加载三段式**组织（各段以 `---` 分隔——agent 与读者先读元数据定版本真伪、再读 TOC 定全文范围，按需加载正文章节，节约上下文；结构与判例见 [文档可读性纪律指南](references/doc_readability_guide.md)）：

1. **YAML frontmatter 元数据**（渐进式加载①：文档首部 `---` 包裹的独立段——渲染器不显示、机器可解析，版本信息**唯一权威载体**）

   ```yaml
   ---
   title: "{文档标题}"
   version: "v{X.Y.Z}"
   status: "✅ 设计完成"        # ⏳ 待 POC | ✅ 设计完成 | 🚧 实施中 | ⚠️ 已废弃
   created: "YYYY-MM-DD"
   supersedes: "v{X.Y.Z-1}（已归档至 archive/，可选）"
   version_notes:              # 本版说明，≤10 行
     - "v{X.Y} 新增功能/修正内容 1"
     - "v{X.Y} 新增功能/修正内容 2"
   version_history:            # 最近 3-5 条，完整沿革由 git + archive/ 承载
     - "v1.0 初始版本"
     - "v2.0 {变更说明}"
   ---
   ```

   **❌ 禁止把版本元数据写成正文**：正文头部不得堆叠版本表/版本说明块——markdown 渲染直接显示元数据，正文要点被元数据考古层淹没，读者读完前 10% 还看不到正文。正文可选保留 ≤15 行「本版变更」摘要。
   **版本三处一致**：文件名 `v{X.Y.Z}` = frontmatter `version` = 正文 H1 尾注版本。

2. **目录（TOC）**（渐进式加载②：全文导航地图，置于内容区最前）

   主文档 > 100 行必须提供 TOC，置于正文头部（H1 之后、概述之前），其后以 `---` 水平线与正文分隔；子文档 > 150 行同理：

   ```markdown
   ## 目录

   - [1. 设计概述](#1-设计概述)
   - [2. 数据模型](#2-数据模型)
   ```

   成稿后**必须对章节锚点做自检**——编号单调不回退、无复用、层级与编号深度一致、TOC 锚点与实际标题匹配，由成稿自检脚本拦截（见「成稿可读性纪律」）。

3. **文档概述**（渐进式加载③：正文起点——TOC 之后不得再插入版本元数据/过程性内容块）
   ```markdown
   ## 📋 文档概述

   本文档描述了...
   ```

4. **核心内容章节**
   - 根据文档类型组织（架构设计、数据模型、API 设计等）

5. **变更日志（可选）**
   - 对于 PATCH 更新，可以添加变更日志

### 推荐章节结构（示例）

**说明**: 以下为通用示例，具体章节根据实际项目调整

**system_architecture_{sem_ver}.md**：
```markdown
1. 架构概述
2. 技术栈
3. 部署架构
4. 网络拓扑
5. 安全设计
6. 监控告警
```

**data_layer_design_{sem_ver}.md**：
```markdown
1. 设计概述
2. 数据模型
3. 表结构设计
4. 索引设计
5. 数据字典
6. 迁移脚本
```

**service_layer_architecture_{sem_ver}.md**（示例）：
```markdown
1. 架构概述
2. 监听机制（如 K8s Informer、消息队列）
3. 生命周期处理流程
4. 状态机设计
5. 业务逻辑计算
6. 资源实时计算
7. 事件日志输出
8. {新增章节}
```

**{name}_faq_{sem_ver}.md**：
```markdown
FAQ-1: {问题 1}
FAQ-2: {问题 2}
...
FAQ-N: {问题 N}
```

---

## 图表运用原则

设计文档中需要直观传递概念时用图——一段需要读者在脑中重建组件关系/执行顺序/流转路径的文字描述，就该换成图。先识别概念类型（结构？顺序？流转？关系？），再对照选型，而不是"先决定画图再想画什么"。

### 速查：概念类型 → 图类型（默认 mermaid 渲染）

| 概念类型 | 图类型 | mermaid 语法 |
|---------|--------|-------------|
| 系统结构/组件拓扑 | 架构图 | `flowchart TB/LR` |
| 交互顺序 | 时序图 | `sequenceDiagram` |
| 业务流程/决策流转 | 流程图 | `flowchart TD` |
| 状态流转 | 状态图 | `stateDiagram-v2` |
| 数据模型/实体关系 | E-R 图 | `erDiagram` |
| 类/接口关系 | 类图 | `classDiagram` |

选型是开放集：垂直领域有更贴切的表达（C4 模型、数据流图等）时，按「最能直观传递概念」选用，不限于上表。

### 渲染与回退

- 默认 ```mermaid``` 围栏渲染（GitHub/GitLab 原生支持），每图配图题并被正文引用
- 单图规模控制：节点 ≤ 15 / 时序消息 ≤ 20 / 行数 ≤ 50——超出拆子文档（联动「文档长度控制原则」中"大型时序图/流程图 > 50 行"规则）
- ASCII 图仅备用：纯文本环境（commit message/diff/terminal）或 mermaid 表达力不足时

### 职责边界（arch 不生成，转介）

| 图表类别 | 归属 |
|---------|------|
| UI/UX 视觉设计稿（线框图/高保真原型/交互原型/配色排版方案） | **转 /ued** |
| 项目管理类图表（甘特图/鱼骨图/燃尽图/燃起图） | **转 /pm** |

arch 只负责系统方案/宏观设计的概念图；涉及上述两类时明确告知用户「此图表由 /{skill} 负责实现」，不在 arch 文档中生成。

> 完整细则（选型方法与三个完整示例、mermaid 书写规范、ASCII 回退条件、边界辨析易混淆场景、审查清单）见 **[设计文档图表运用指南](references/diagram_guide.md)**。

---

## 成稿可读性纪律（含去黑话铁律）

设计文档是开发/测试/运维链条的源头输入：文档在源头含糊，偏差与漂移会沿 Story→Code→Tests 逐级放大（dev 按黑话命名模块、qa 按黑话命名用例、运维按歧义编号定位对象）。本纪律保证"人类读者（含三个月后的作者本人与 AI 代理）不靠猜就能读懂"。**结构机械项由自检脚本强制，语义项由 AI review 执行**（见本章末）。

### 去黑话铁律（最高优先级，用户明令）

1. **黑话/隐喻不得独自承载语义**：房规、承重墙、第一刀、落账、实弹……首现必附直白同位语（如「承重墙（不可变更的核心约束）」）；承载语义的正式表述用直白语，黑话只做气氛补充。
2. **代号唯一且在档**：同一代号全文只有一个含义；同族字母（R1/R2/…）禁止跨语义空间复用（反例：R1 同时指依赖证据等级、挖掘算法名、纠偏规则名——三义歧义沿 Story 放大成三处错误实现）。代号首次出现括注定义，或集中「代号词典」章节。
3. **压缩有上限（拒绝过度压缩）**：单句括号嵌套 ≤ 2 层；一句只承载一个论断；斜杠串 > 3 个概念改列表；表格单元格 > 200 字符的散文论述移回正文段落。
4. **加粗每段 ≤ 2 处**：通篇重读等于没有重点。

### 成稿自检（结构机械项，脚本强制）

文档定稿前运行自检脚本，**exit ≠ 0 不得定稿**：

```bash
python {skill_dir}/scripts/doc_structure_check.py {project_docs}/design/{layer}_design_v{version}.md
```

脚本拦截项：YAML frontmatter 必填字段（version/status/created）与版本三处一致、TOC 存在性（主文档 > 100 行）、标题编号纪律（顶层与同级单调不回退/无复用/无占位编号如 `5.x`/标题层级=编号深度）、相对链接目标存在、test_reports/ 引用拦截（三条铁律 #1 的机械 enforcement）、表格超长单元格提示（>400 字符行，人工判断）。

**执行方式分层**：skill 指引（保底）→ hook 自动触发（使用方在 Claude Code `hooks.PostToolUse` / Codex `hooks.json` 挂载同一脚本，写入 design 文档即自检——配置两栈不同构、脚本同一份，样例见纪律指南）→ CI 门禁（项目侧纳入流水线全量强制）。

**hook 挂载引导（建议不代写）**：当项目持续产出 design 文档（本会话已产出 ≥2 篇，或项目 `{project_docs}/design/` 下已有 ≥3 篇）且未挂载自检 hook 时，主动建议用户挂载——按当前运行栈给出对应配置样例（见纪律指南），**经用户明确同意后**才创建/修改 hook 配置（Codex 侧字段先查所用版本官方 hooks 文档），并提醒 hooks 变更经 review 后于下次会话生效。不自动改写配置文件，不静默挂载。

### 内容自洽性语义 review 五问（AI 判定型，非格式项）

以下问题无法机械判定，需要结合语义/上下文/因果理解，由 AI 或审查者在评审流程中逐问执行——不通过即打回修订：

1. **版本记录单一权威？** 全文是否存在互斥的版本声明（frontmatter/正文版本表/文末沿革各说各话）？
2. **编号一号一义？** 表号/图号/代号是否被复用于不同对象，交叉引用是否因此歧义？
3. **名实相符三面对账？** ER↔DDL↔枚举字典（或接口↔实现↔配置）三类载体是否同步——被正文引用的对象是否处处都有落点？
4. **引用现行？** 引用的外部文档版本是否现行（而非已归档旧版）？声称的章节/附录是否真实存在（防幽灵引用）？
5. **勘误无歧义？** 修正错误时是否明确"哪里错了、现在是什么"，读者能否区分旧值与新值？

> 完整反例与判例见 **[文档可读性纪律指南](references/doc_readability_guide.md)**。

---

## 设计文档与 Story 的关系

### 双向追踪

**设计文档 → Story**：
- 每个设计文档可以对应多个 Story
- Story 引用设计文档的章节号

**Story → 设计文档**：
- Story 的实现会更新设计文档
- 设计文档的版本号要体现 Story 的变更

### 示例（通用化）

```yaml
# Story 文档（示例格式）
story_id: "{story-id}"
title: "{story-title}"
dependencies:
  - "{parent-story-id}"
design_docs:
  - "{project_docs}/design/{layer}_design_v{version}.md#{chapter}"
  - "{project_docs}/design/{layer}_design_v{version}.md#{section}"

# 实施完成后
design_updates:
  - "{project_docs}/design/{layer}_design_v{new_version}.md"  # v{old} → v{new}
  - "{project_docs}/design/{name}_faq_v{new_version}.md"      # v{old} → v{new}
```

**说明**:
- `{story-id}`: Story 标识符（如 STORY-123）
- `{chapter}`: 章节名称（如 "历史记录存储优化"）
- `{section}`: 小节名称（如 "数据模型概述"）

---

## 常见错误

### ❌ 错误 1：使用描述性文件名

```bash
# ❌ 错误：创建临时规划文件
vim {project_docs}/design/plan_{date}.md
vim {project_docs}/design/{feature}_design_updates.md
vim {project_docs}/design/proposal.md          # proposal 不是文档类型——design/ 下任何 proposal 命名都禁止

# ✅ 正确：直接更新正式文档
vim {project_docs}/design/{layer}_design_v{version}.md

# ✅ 正确：设计动议落 analysis/（含未实证关键假设时）
vim {project_docs}/analysis/research_{topic}.md  # 头部 status: research → proposal（状态不进文件名）
```

### ❌ 错误 2：不归档旧版本

```bash
# ❌ 错误：保留多个版本在 design/ 目录
{project_docs}/design/
├── {layer}_design_v1.0.md
├── {layer}_design_v2.0.md
└── {layer}_design_v3.0.md

# ✅ 正确：只保留最新版本
{project_docs}/design/
└── {layer}_design_v3.0.md

{project_docs}/design/archive/
├── {layer}_design_v1.0_{date1}.md
└── {layer}_design_v2.0_{date2}.md
```

### ❌ 错误 3：版本号判断错误

```bash
# ❌ 错误：小改动使用 MAJOR 版本
修正错别字 → v2.0 → v3.0  # 过度升级

# ✅ 正确：小改动使用 PATCH 版本
修正错别字 → v2.0 → v2.0.1

# ❌ 错误：重大改动使用 PATCH 版本
新增完整章节 → v2.0 → v2.0.1  # 版本号不足

# ✅ 正确：重大改动使用 MAJOR 版本
新增完整章节 → v2.0 → v3.0
```

### ❌ 错误 4：版本号不一致

文档头部版本号与文件名不一致：

```bash
# ❌ 错误：版本号不一致
文件名: data_layer_design_v2.2.md
头部: **版本**: v2.1

# ✅ 正确：版本号一致
文件名: data_layer_design_v2.2.md
头部: **版本**: v2.2
```

### ❌ 错误 5：版本记录多处并存互斥

版本信息同时写进正文版本表、正文版本说明块、文末沿革——升版时只更新其中一处，其余变成过期声明，读者读到文末被告知"当前版本是三个大版本之前"：

```markdown
# ❌ 错误：多处版本记录互斥
头部版本表:        vX.Y（最新）
头部版本说明块:    × N 个
中部版本历史表:    止于数个大版本之前（缺中间全部版本）
文末沿革:          仍声明旧版"现行权威"

# ✅ 正确：frontmatter 单一权威，正文不留版本历史表
---
version: "vX.Y"
version_notes: [...]
version_history: [最近 3-5 条]
---
```

---

## 最佳实践

1. **文档即代码**：设计文档与代码同等重要，必须版本化管理
2. **语义化版本**：严格遵循语义化版本规则，变更粒度体现在版本号
3. **及时归档**：每次 MAJOR/MINOR 更新时，及时归档旧版本
4. **版本同步**：主文档和 FAQ 文档的版本号保持一致
5. **单一真实来源**：设计文档是架构的唯一真实来源，禁止分散信息

---

## 关键资源（通用化）

**设计文档示例**：
- `{project_docs}/design/system_architecture_v1.0.md`
- `{project_docs}/design/data_layer_design_v2.3.md`
- `{project_docs}/design/service_layer_architecture_v2.0.md`
- `{project_docs}/design/service_layer_faq_v2.1.md`

**SKILL 文档**：
- `.claude/skills/dev/SKILL.md` - 开发工作技能
- `.claude/skills/qa/SKILL.md` - QA 工作技能
- `.claude/skills/pm/SKILL.md` - Scrum 工作流程

**参考细则**（按需加载）：
- [设计变更三步流程 SOP 细则](references/design_iteration_sop.md) - Step ①②③ 逐步操作、analysis/ 目录规范（命名 + metadata + 三级状态）、Status 枚举
- [analysis 文档模板](templates/analysis_doc_template.md) - 分析文档占位符模板（research 自由态 / proposal 假设表）
- [设计文档图表运用指南](references/diagram_guide.md) - 图表选型（架构图/流程图/时序图/状态图/E-R 图/类图）、mermaid 书写规范、ASCII 回退、职责边界（/ued、/pm 转介）
- [文档可读性纪律指南](references/doc_readability_guide.md) - 渐进式加载结构、frontmatter 模板、去黑话铁律判例、压缩上限、语义 review 五问详解、hook 挂载样例
- [文档审查清单](references/review_checklist.md) - 设计文档更新前后 5 组过检清单（变更路径/版本更新/归档引用/文档结构/最终验证）

**成稿自检脚本**：
- `scripts/doc_structure_check.py` - 结构机械项拦截（frontmatter/TOC/编号纪律/链接/test_reports），exit ≠ 0 不得定稿

**Story 文档**：
- `{project_docs}/scrum/story/story-*.md` - Story 执行指南

---

## 文档审查清单

**设计文档更新前后逐项过检**——完整清单（5 组：设计变更路径/版本更新/归档和引用/文档结构/最终验证）见 **[文档审查清单](references/review_checklist.md)**，执行位要点：

- 设计变更先分级：无未实证关键假设 → 直接走「文档更新流程」5 步；含 → 走「设计变更三步流程」
- 升版动作链：版本增量判定 → 归档旧版（MAJOR/MINOR，带日期戳）→ 更新 frontmatter（版本三处一致）
- 成稿定稿闸：自检脚本 `doc_structure_check.py` exit 0 + 语义 review 五问逐问过 + 去黑话铁律（同位语/代号唯一/压缩上限/加粗 ≤2）

---

**版本**: v2.5
**创建日期**: 2026-02-04
**作者**: Development Team
**状态**: 正式发布
**更新日志**（完整沿革见 git log，逐版 Conventional Commits 可溯）:
- v2.5 (2026-11-24): 🎯 成稿可读性纪律——去黑话铁律 4 条 + 渐进式加载三段式（frontmatter→TOC→正文，`---` 分隔）+ `doc_structure_check.py` 自检脚本（skill 指引/hook/CI 三层执行，挂载引导 offer-and-ask）+ 语义 review 五问 + `references/doc_readability_guide.md`
- v2.4 (2026-11-05): 🎯 图表运用能力——按概念类型选型（mermaid 默认/ASCII 回退）+ 职责边界（/ued、/pm 转介）+ `references/diagram_guide.md`
- v2.3 (2026-11-02): 🎯 proposal 通道废除，降维为 analysis 三级状态（research→proposal→adopted）——v2.2 proposal 五件套建成 56 天零实例，实证治理过重不可操作（MR !17 review 迭代）
- v2.2 (2026-09-07): 🎯 新增设计变更三步流程（EPIC-7：analysis→POC→design update，假设驱动分级 + 三条铁律）+ `references/design_iteration_sop.md`
- v2.1 (2026-04-29): 整合 documentation-versioning——文档头部模板扩展、版本一致性检查、审查清单四分
- v2.0 (2026-04-28): 🎯 去项目化产品化改造——占位符泛化（{layer}/{version}/{project_docs}），文档大幅精简
- v1.0 (2026-02-04): 初始版本