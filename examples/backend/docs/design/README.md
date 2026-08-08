# 设计文档目录

**目录版本**: v1.0
**更新日期**: 2026-04-25
**维护者**: Development Team

---

## 📋 设计文档索引

### 当前版本(Current Versions)

| 文档名称 | 版本 | 更新日期 | 状态 | 描述 |
|---------|------|---------|------|------|
| [服务层架构设计](service_layer_architecture_v4.2.md) | v4.2 | 2026-04-25 | ✅ 有效 | K8s Informer + Pod 生命周期管理 |
| [服务层 FAQ](service_layer_faq_v4.1.md) | v4.1 | 2026-04-25 | ✅ 有效 | 服务层常见问题与最佳实践 |
| [API 设计](api_design_v1.3.md) | v1.3 | 2026-03-23 | ✅ 有效 | RESTful API 设计规范 |
| [数据层设计模板](data_layer_design_{sem_ver}.md.template) | - | - | 📋 模板 | 新项目数据层设计骨架 |

---

## 📂 文档组织结构

```
docs/design/
├── README.md                                       # 本文档
├── service_layer_architecture_v4.2.md              # 服务层架构(当前)
├── service_layer_faq_v4.1.md                       # 服务层 FAQ(当前)
├── api_design_v1.3.md                              # API 设计(当前)
└── data_layer_design_{sem_ver}.md.template         # 数据层设计模板
```

---

## 🏗️ 架构层次分类

### 服务层架构

**文档**: `service_layer_architecture_v{sem_ver}.md`

**内容**:
- K8s Informer 监听机制
- Pod 生命周期处理流程
- 状态机设计
- 资源计算逻辑

**FAQ 文档**: `service_layer_faq_v{sem_ver}.md`

### API/应用层

**文档**: `api_design_v{sem_ver}.md`

**内容**:
- API 接口设计
- 请求/响应格式
- 鉴权与审计

### 数据层

**模板**: `data_layer_design_{sem_ver}.md.template`

**用途**: 作为新项目数据层设计的起点,需要根据实际业务填充。

---

## 📋 文档命名规范

### 语义化版本规则

**版本格式**: `v{MAJOR}.{MINOR}.{PATCH}`

| 版本类型 | 版本号示例 | 变更类型 | 判断标准 |
|---------|-----------|---------|---------|
| **MAJOR** | v2.0 → v3.0 | 重大功能新增、架构变更 | 新增完整章节、表结构变更、接口重定义 |
| **MINOR** | v2.0 → v2.1 | 功能新增、向后兼容 | 新增小功能、配置项、优化项 |
| **PATCH** | v2.0 → v2.0.1 | Bug 修复、小改动 | 修正错误、补充说明、格式调整 |

### 文件命名规范

| 架构层次 | 文档命名模式 | 示例 |
|---------|-------------|------|
| **服务层架构** | `service_layer_architecture_{sem_ver}.md` | `service_layer_architecture_v4.2.md` |
| **服务层 FAQ** | `service_layer_faq_{sem_ver}.md` | `service_layer_faq_v4.1.md` |
| **API/应用层** | `api_design_{sem_ver}.md` | `api_design_v1.3.md` |
| **数据层模板** | `data_layer_design_{sem_ver}.md.template` | (按需生成) |

**❌ 禁止的命名方式**:
- ❌ 描述性语言命名的临时文件: `plan_20260204.md`、`design_updates.md`
- ❌ 不带版本号的文档: `service_layer_architecture.md`
- ❌ 使用日期作为版本号: `service_layer_architecture_20260204.md`

---

## 📝 文档更新流程

### Step 1: 确定变更类型

判断版本号增量(MAJOR/MINOR/PATCH)

### Step 2: 创建新版本

```bash
# 复制旧版本作为基础
cp docs/design/api_design_v1.3.md docs/design/api_design_v1.4.md

# 编辑新版本
$EDITOR docs/design/api_design_v1.4.md
```

### Step 3: 更新版本历史表

在每个文档的开头更新版本历史表:

```markdown
## 📋 版本历史

| 版本 | 日期 | 变更说明 | 作者 |
|------|------|---------|------|
| v1.3 | 2026-03-23 | 初始版本 | Development Team |
| v1.4 | YYYY-MM-DD | 待定 | 待定 |
```

### Step 4: 更新本文档

在新版本就绪后,更新本文档顶部的索引表。

---

## 🔍 文档审查清单

**设计文档更新前检查**:

- [ ] 确定版本号增量(MAJOR/MINOR/PATCH)
- [ ] 创建新版本文件
- [ ] 更新版本历史表
- [ ] 更新文档概述(如有必要)
- [ ] 更新相关文档(FAQ、其他层次文档)
- [ ] 验证文档结构完整(必需章节齐全)
- [ ] 验证内部链接有效
- [ ] 提交版本控制

---

**文档目录版本**: v1.0
**更新日期**: 2026-04-25
**维护者**: Development Team
