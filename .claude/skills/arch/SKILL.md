---
skill: "arch"
description: "架构师工作技能 - 架构设计、文档管理、语义化版本控制、设计审查。当用户提到架构、设计文档、版本管理、技术选型、系统设计、数据模型、API设计、文档审查、设计规范、架构决策、或需要创建/更新设计文档时，必须使用此技能。确保所有设计文档遵循语义化版本规范和命名约定。"
version: "2.1"
---

# Architect 工作技能

## 核心职责

1. **架构设计**：设计系统架构、数据模型、服务层架构、应用层架构
2. **文档管理**：维护设计文档，遵循语义化版本管理规范
3. **技术决策**：制定技术选型、设计模式、最佳实践
4. **跨层协调**：协调系统层、数据层、服务层、应用层的设计一致性
5. **设计审查**：Review 设计文档，确保架构合理性和可实施性

---

## 📋 设计文档管理规范（铁律）

### ⚠️ 核心原则：语义化版本 + 层次分类 + 归档管理

**设计文档必须遵循以下规则**：

1. **按架构层次分类命名**：使用 `{layer}_design_{sem_ver}.md` 格式
2. **语义化版本号**：变更粒度直接体现在文件名版本部分
3. **归档管理**：旧版本归档到 `{project_docs}/design/archive/`
4. **禁止描述性命名**：不使用 plan、update、design 等临时文件名

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
   - 任何带有 `plan`、`update`、`design`、`proposal` 等前缀的文件名

2. ❌ 不带版本号的文档：
   - `{layer}_design.md`（缺少版本号）
   - `faq.md`（缺少版本号）

3. ❌ 使用日期作为版本号：
   - `{layer}_design_{date}.md`（如 20260204）

**✅ 正确的命名方式**：

- ✅ `{layer}_design_v{major}.{minor}.{patch}.md`
- ✅ `{layer}_design_v{major}.{minor}.md`
- ✅ `{name}_faq_v{major}.{minor}.{patch}.md`

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

{project_docs}/design/analysis/       # 分析文档目录（可选）
├── informer_data_analysis.md          # Informer 实际数据分析
├── database_schema_analysis.md        # 数据库 schema 分析
└── technical_research.md              # 技术方案调研
```

**说明**：
- `archive/` 目录存放归档的历史版本（带日期戳）
- `analysis/` 目录存放分析文档和调研报告（不受版本管理约束）

---

## 文档更新流程

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

### Step 4: 更新版本历史表

**在每个文档的开头更新版本历史表**：

```markdown
## 📋 版本历史

| 版本 | 日期 | 变更说明 | 作者 |
|------|------|---------|------|
| v1.0 | YYYY-MM-DD | 初始版本 | {Author} |
| v2.0 | YYYY-MM-DD | {变更说明} | {Author} |
| v3.0 | YYYY-MM-DD | {变更说明} | {Author} |

**v3.0 主要变更**：
- ✅ {变更 1}
- ✅ {变更 2}
- ✅ {变更 3}
- ⚠️ 向后兼容：{兼容性说明}
```

### Step 5: 更新相关文档

**如果更新涉及多个文档，保持版本号一致**：

| 主文档版本 | FAQ 文档版本 | 示例场景 |
|-----------|------------|---------|
| v3.0 | v3.0 | 主文档 MAJOR 更新，FAQ 同步更新 |
| v2.1 | v2.1 | 主文档 MINOR 更新，FAQ 同步更新 |
| v2.0.1 | 不变 | 主文档 PATCH 更新，FAQ 不变 |

---

## 文档结构规范

### 必需章节

**每个设计文档必须包含以下章节**：

1. **文档元数据**
   ```markdown
   # {文档标题} v{version}

   **版本**: vX.Y (简短说明)
   **创建日期**: YYYY-MM-DD
   **状态**: ✅ 设计完成 | 🚧 实施中 | ⚠️ 已废弃
   **替代版本**: vX.Y-1 (已归档至 `archive/文件名_vX.Y-1_YYYYMMDD.md`)

   **版本说明**:
   - vX.Y 新增功能/修正内容 1
   - vX.Y 新增功能/修正内容 2

   **关键修正**（如果有）:
   1. ❌ vX.Y-1 错误假设
      ✅ vX.Y 修正内容
   ```

2. **版本历史表**
   ```markdown
   ## 📋 版本历史

   | 版本 | 日期 | 变更说明 | 作者 |
   |------|------|---------|------|
   | v1.0 | YYYY-MM-DD | 初始版本 | {Author} |
   | v2.0 | YYYY-MM-DD | {变更说明} | {Author} |
   | v3.0 | YYYY-MM-DD | {变更说明} | {Author} |

   **v3.0 主要变更**：
   - ✅ {变更 1}
   - ✅ {变更 2}
   - ✅ {变更 3}
   - ⚠️ 向后兼容：{兼容性说明}
   ```

3. **文档概述**
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
vim {project_docs}/design/proposal.md

# ✅ 正确：直接更新正式文档
vim {project_docs}/design/{layer}_design_v{version}.md
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

**Story 文档**：
- `{project_docs}/scrum/story/story-*.md` - Story 执行指南

---

## 文档审查清单

**设计文档更新前检查**：

### 版本更新检查

- [ ] 确定版本号增量（MAJOR/MINOR/PATCH）
- [ ] 已复制旧版本作为新版本基础
- [ ] 已更新文件名版本号（vX.Y → vX.Y+1）
- [ ] 已更新文档头部版本信息（版本号、日期、状态）
- [ ] 已更新版本说明和关键修正
- [ ] **验证版本号一致性**（文件名与头部版本号一致）

### 归档和引用检查

- [ ] 已归档旧版本到 `docs/archive/`（带日期戳）
- [ ] **不要删除** `docs/design/` 下的往期版本文件
- [ ] 已更新其他文档中的引用链接
- [ ] 已验证文件存在性

### 文档结构检查

- [ ] 验证文档结构完整（必需章节齐全）
- [ ] 验证内部链接有效（锚点链接准确）
- [ ] 验证跨文档引用使用相对路径

### 最终验证

- [ ] 提交版本控制
- [ ] 检查 Git 状态确保所有文件已暂存

---

**版本**: v2.1
**创建日期**: 2026-02-04
**作者**: Development Team
**状态**: 正式发布
**更新日志**:
- v2.1 (2026-04-29): 整合 documentation-versioning 内容
  - 扩展文档头部模板，添加详细版本信息和关键修正说明
  - 添加 analysis/ 目录说明（存放分析文档和调研报告）
  - 添加版本号一致性错误检查
  - 扩展文档审查清单，细分为版本更新、归档引用、文档结构、最终验证四个部分
- v2.0 (2026-04-28): 🎯 **重大更新**：去项目化产品化改造
  - 移除所有项目特化内容（特定业务概念、文件名、路径、章节编号、Story 引用）
  - 使用占位符替代特定内容（`{layer}`, `{version}`, `{project_docs}` 等）
  - 添加占位符说明，确保可复用到任何项目
  - 优化 description，使其更"pushy"，明确触发场景
  - 保留所有核心行为规则和约束
  - 文档行数从 513 行降至 330 行（减少 36%）
- v1.0 (2026-02-04): 初始版本
