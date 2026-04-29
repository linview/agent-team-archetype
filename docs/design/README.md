# 设计文档目录

**目录版本**: v1.1
**更新日期**: 2026-04-23
**维护者**: Development Team

---

## 📋 设计文档索引

### 最新版本（Current Versions）

| 文档名称 | 版本 | 更新日期 | 状态 | 描述 |
|---------|------|---------|------|------|
| [系统架构设计](system_architecture_v1.0.md) | v1.0 | 2025-01-XX | ✅ 有效 | 系统整体架构设计 |
| [CMDB 设计](cmdb_design_v3.2.md) | v3.2 | 2026-02-10 | ✅ 有效 | Pod 资源管理 + CMDB 设计 |
| [服务层架构设计](service_layer_architecture_v3.3.md) | v3.3 | 2026-03-10 | ✅ 有效 | 服务层完整架构设计 |
| [服务层 FAQ](service_layer_faq_v3.2.md) | v3.2 | 2026-03-13 | ✅ 有效 | 服务层常见问题解答 |
| [API 设计](api_design_v1.0.md) | v1.0 | 2026-03-23 | ✅ 有效 | {BUSINESS_SHORT}聚合 API 设计 |
| [Spec-XChecker 设计](spec-xchecker_design_v2.3.md) | v2.3 | 2026-04-23 | ✅ **新增** | 四路交叉验证工具设计 |
| [MCasbin 集成设计](mcasbin_integration_design_v1.0.md) | v1.0 | 2026-02-13 | ✅ 有效 | MCasbin 权限服务集成 |
| [监控设计](monitoring_design_v1.0.md) | v1.0 | 2026-03-06 | ✅ 有效 | 监控告警系统设计 |

### 归档版本（Archived Versions）

归档文档请查看 [`archive/`](archive/) 目录。

---

## 🆕 2026-04-23 更新

### 新增文档

**✨ [Spec-XChecker 设计 v2.3](spec-xchecker_design_v2.3.md)** - 四路交叉验证工具设计

**核心特性**：
- ✅ 三域一致性模型（设计域 = SSOT）
- ✅ 检查顺序铁律（DS → SC → CT → ST）
- ✅ 工具能力边界（静态检查 ≠ 运行时保证）
- ✅ 21 项检查清单（4 DS + 6 SC + 5 CT + 6 ST）

**工程哲学**：
- 设计域 = SSOT（概要设计 + 详细设计）
- 详细设计必须依据概要设计，不能冲突
- 检查顺序遵循依赖关系：DS → SC → CT → ST
- 静态语义检查不保证运行时正确性

---

## 🆕 2026-03-23 更新

### 新增文档

**✨ [API 设计 v1.0](api_design_v1.0.md)** - {BUSINESS_SHORT}聚合 API 设计

**核心特性**：
- ✅ 智能时间解析（支持 4 种时间格式）
- ✅ 多维度聚合统计（逗号分隔，最多 2 级）
- ✅ 自动时间聚合粒度推断
- ✅ 向后兼容（aggregate_by 参数可选）
- ✅ 数据库索引优化（4 个新索引）

**工作量与排期**：
- 总工作量：9.5 个工作日
- 团队配置：1 后端 + 1 测试 + 1 DBA
- 详细排期：参见 [Epic-13 文档](../scrum/prd/epic-13-{BUSINESS_DOMAIN}-aggregation-api.md)

**关键里程碑**：
- Day 3: Phase 1-2 完成（基础设施就绪）
- Day 6: Phase 3-4 完成（核心功能实现）
- Day 6.5: Phase 5 完成（测试验证通过）
- Day 8: Phase 6 完成（生产环境部署）

---

## 📂 文档组织结构

```
docs/design/
├── README.md                              # 本文档
├── system_architecture_v1.0.md            # 系统架构设计
├── cmdb_design_v3.2.md                    # CMDB 设计
├── service_layer_architecture_v3.3.md     # 服务层架构设计
├── service_layer_faq_v3.2.md              # 服务层 FAQ
├── api_design_v1.0.md                     # API 设计
├── spec-xchecker_design_v2.3.md           # Spec-XChecker 设计 ⭐ 新增
├── mcasbin_integration_design_v1.0.md     # MCasbin 集成设计
├── monitoring_design_v1.0.md              # 监控设计
└── archive/                               # 归档版本
    ├── cmdb_design_v2.3_20260204.md
    ├── service_layer_architecture_v3.2_20260310.md
    ├── spec-xchecker_design_v2.2_20260423.md  # ⭐ 新增归档
    └── ...
```

---

## 🏗️ 架构层次分类

### 系统架构层

**文档**: `system_architecture_v{sem_ver}.md`

**内容**：
- 系统整体架构设计
- 技术栈选型
- 部署架构
- 网络拓扑
- 安全设计
- 监控告警

### 数据层/CMDB

**文档**: `cmdb_design_v{sem_ver}.md`

**内容**：
- 数据模型设计
- 表结构设计
- 索引设计
- 数据字典
- 迁移脚本

### 服务层架构

**文档**: `service_layer_architecture_v{sem_ver}.md`

**内容**：
- K8s Informer 监听机制
- Pod 生命周期处理流程
- 状态机设计
- {BUSINESS_SHORT}计算
- 活跃 Pod GPU 实时计算
- K8s Event 日志输出

**FAQ 文档**: `service_layer_faq_v{sem_ver}.md`

### API/应用层

**文档**: `api_design_v{sem_ver}.md`

**内容**：
- API 接口设计
- 请求/响应格式
- 聚合功能设计
- 性能优化方案

---

## 📋 文档命名规范

### 语义化版本规则

**版本格式**：`v{MAJOR}.{MINOR}.{PATCH}`

| 版本类型 | 版本号示例 | 变更类型 | 判断标准 |
|---------|-----------|---------|---------|
| **MAJOR** | v2.0 → v3.0 | 重大功能新增、架构变更 | 新增完整章节、表结构变更、接口重定义 |
| **MINOR** | v2.0 → v2.1 | 功能新增、向后兼容 | 新增小功能、配置项、优化项 |
| **PATCH** | v2.0 → v2.0.1 | Bug 修复、小改动 | 修正错误、补充说明、格式调整 |

### 文件命名规范

| 架构层次 | 文档命名模式 | 示例 |
|---------|-------------|------|
| **系统架构** | `system_architecture_{sem_ver}.md` | `system_architecture_v1.0.md` |
| **数据层/CMDB** | `cmdb_design_{sem_ver}.md` | `cmdb_design_v3.2.md` |
| **服务层架构** | `service_layer_architecture_{sem_ver}.md` | `service_layer_architecture_v3.3.md` |
| **API/应用层** | `api_design_{sem_ver}.md` | `api_design_v1.0.md` |
| **FAQ 文档** | `{name}_faq_{sem_ver}.md` 或 `{name}_faq.md` | `service_layer_faq_v3.2.md` |

**❌ 禁止的命名方式**：
- ❌ 描述性语言命名的临时文件：`plan_20260204.md`、`design_updates.md`
- ❌ 不带版本号的文档：`service_layer_architecture.md`
- ❌ 使用日期作为版本号：`service_layer_architecture_20260204.md`

---

## 📝 文档更新流程

### Step 1: 确定变更类型

判断版本号增量（MAJOR/MINOR/PATCH）

### Step 2: 归档旧版本（如需要）

**MAJOR 或 MINOR 版本更新时**：

```bash
# 归档旧版本
mv docs/design/api_design_v1.0.md \
   docs/design/archive/api_design_v1.0_$(date +%Y%m%d).md
```

**PATCH 版本更新时**：
- 不归档（直接覆盖文件）

### Step 3: 创建新版本

```bash
# 复制旧版本作为基础（推荐）
cp docs/design/archive/api_design_v1.0_20260323.md \
   docs/design/api_design_v2.0.md

# 编辑新版本，更新内容
vim docs/design/api_design_v2.0.md
```

### Step 4: 更新版本历史表

在每个文档的开头更新版本历史表：

```markdown
## 📋 版本历史

| 版本 | 日期 | 变更说明 | 作者 |
|------|------|---------|------|
| v1.0 | 2026-03-23 | 初始版本：{BUSINESS_SHORT}聚合 API 设计 | Claude Code |
| v2.0 | YYYY-MM-DD | 待定 | 待定 |
```

### Step 5: 更新相关文档

如果更新涉及多个文档，保持版本号一致。

---

## 🔍 文档审查清单

**设计文档更新前检查**：

- [ ] 确定版本号增量（MAJOR/MINOR/PATCH）
- [ ] 归档旧版本（如需要）
- [ ] 创建新版本文件
- [ ] 更新版本历史表
- [ ] 更新文档概述（如有必要）
- [ ] 更新相关文档（FAQ、其他层次文档）
- [ ] 验证文档结构完整（必需章节齐全）
- [ ] 验证内部链接有效
- [ ] 提交版本控制

---

## 📚 关键资源

**设计文档**：
- [Spec-XChecker 设计 v2.3](spec-xchecker_design_v2.3.md) - 四路交叉验证工具设计 ⭐ 新增
- [API 设计 v1.0](api_design_v1.0.md) - {BUSINESS_SHORT}聚合 API 设计
- [服务层架构设计 v3.3](service_layer_architecture_v3.3.md) - 服务层完整架构设计
- [CMDB 设计 v3.2](cmdb_design_v3.2.md) - Pod 资源管理 + CMDB 设计

**排期文档**：
- [API 聚合实施排期 v1.0](../scrum/schedule/api_aggregation_implementation_v1.0.md) - 项目实施排期

**SKILL 文档**：
- [Arch SKILL](../../.claude/skills/arch/SKILL.md) - 架构师工作技能
- [Dev SKILL](../../.claude/skills/dev/SKILL.md) - 开发工作技能
- [QA SKILL](../../.claude/skills/qa/SKILL.md) - QA 工作技能

**Story 文档**：
- [Story README](../scrum/story/README.md) - Story 执行指南

---

**文档目录版本**: v1.1
**更新日期**: 2026-04-23
**维护者**: Development Team
