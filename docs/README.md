# EXAMPLE-ORG example-service 文档中心

**更新时间**: 2026-01-31
**维护者**: EXAMPLE-ORG 团队

---

## 📚 文档分类

### 🎯 设计文档 (design/)

**最新版本**:

- **[cmdb_design_v2.1.md](design/cmdb_design_v2.1.md)** ⭐ - CMDB 完整设计（**当前标准**）
  - example-service 生命周期管理
  - {BUSINESS_DESCRIPTION}（支持多次启停）
  - 符合 event_db 策略
  - **版本**: v2.1 (2026-01-29)
  - **替代**: v2.0 (已归档)

- **[gpu_usage_statistics_design_v1.0.md](design/gpu_usage_statistics_design_v1.0.md)** - GPU 统计 MVP 设计
  - **定位**: 快速上线方案
  - **技术路线**: Informer + Redis
  - **目标**: MVP 功能验证
  - **版本**: v1.0 (2026-01-31)
  - **关联**: 与 cmdb_design_v2.1 功能重叠，但采用不同技术方案

- **[pod_source_identification_guide.md](design/pod_source_identification_guide.md)** - Pod 来源识别技术方案
  - Dev Pod vs ArgoWorkflow 识别
  - Label/Annotation/OwnerReference 方案
  - **版本**: v1.0 (2026-01-31)

**归档版本** (见 `archive/`):
- ~~`cmdb_design_v2.0.md`~~ (已归档，包含错误判断)

---

### 📊 分析文档 (analysis/)

- **[event_db_analysis.md](analysis/event_db_analysis.md)** - event_db 完整业务分析
  - 表分类统计
  - 事实表 vs 维度表
  - 业务流程分析

- **[event_db_er_diagram.md](analysis/event_db_er_diagram.md)** - ER 图总结

- **[event_db_trigger_functions.md](analysis/event_db_trigger_functions.md)** - Trigger 设计模式
  - event_db 现有 Trigger 分析
  - 简单 3-5 行代码原则

- **[gpu_usage_risks_and_mitigation.md](analysis/gpu_usage_risks_and_mitigation.md)** - GPU 统计风险分析

- **[cmdb_feasibility_and_improvement_proposal.md](analysis/cmdb_feasibility_and_improvement_proposal.md)** - CMDB 构建改进方案
  - 当前资源业务属性评估
  - argo-workflow vs example-service 可追溯性分析

---

### 🧪 测试计划 (test_plan/)

- **[production_regression_test_implementation_report.md](test_plan/production_regression_test_implementation_report.md)** - 生产环境回归测试实施报告
  - 测试层次设计（快速冒烟、核心回归、完整回归）
  - 只读操作原则
  - 生产环境验证结果

---

### 📖 集成指南 (guides/)

- **[example-service_integration.md](guides/example-service_integration.md)** - example-service 集成指南

- **[k8s_cluster_integration_guide.md](guides/k8s_cluster_integration_guide.md)** - K8s 集成指南

---

### 🔬 调研报告 (research/)

- **[namespace_metadata_analysis.md](research/namespace_metadata_analysis.md)** - 业务属性分析
  - argo-workflow vs example-service 元数据对比
  - Label vs Annotation 使用场景

- **[prod_gpu_cluster_analysis.md](research/prod_gpu_cluster_analysis.md)** - 生产集群资源分析
  - argo-workflow namespace 分析
  - example-service namespace 分析
  - GPU 资源使用情况

---

### 📦 归档文档 (archive/)

- **[cmdb_design_v2.0.md](archive/cmdb_design_v2.0.md)** - v2.0 设计（已过期）
  - ⚠️ **包含错误判断**: example-service 与 tasks 表关联
  - ✅ 已在 v2.1 中纠正
  - 保留原因: 版本对比和错误案例分析

- **[example-service_cmdb_solution_summary.md](archive/example-service_cmdb_solution_summary.md)** - 方案总结

- **[event_db_cmdb_design_detailed.md](archive/event_db_cmdb_design_detailed.md)** - 早期详细设计

---

## 🎯 文档使用指南

### 场景 1: CMDB 数据库设计

**推荐阅读顺序**:
1. [event_db_analysis.md](analysis/event_db_analysis.md) - 了解 event_db 现状
2. [event_db_trigger_functions.md](analysis/event_db_trigger_functions.md) - 了解 Trigger 设计模式
3. [cmdb_design_v2.1.md](design/cmdb_design_v2.1.md) - 完整设计方案（**当前标准**）
4. [archive/cmdb_design_v2.0.md](archive/cmdb_design_v2.0.md) - 对比 v2.0 的错误判断

### 场景 2: {BUSINESS_DESCRIPTION}实施

**推荐阅读顺序**:
1. [cmdb_feasibility_and_improvement_proposal.md](analysis/cmdb_feasibility_and_improvement_proposal.md) - 评估当前现状
2. [gpu_usage_risks_and_mitigation.md](analysis/gpu_usage_risks_and_mitigation.md) - 风险分析
3. [gpu_usage_statistics_design_v1.0.md](design/gpu_usage_statistics_design_v1.0.md) - MVP 方案（快速上线）
4. [cmdb_design_v2.1.md](design/cmdb_design_v2.1.md) - 完整方案（长期维护）

### 场景 3: K8s Informer 集成

**推荐阅读顺序**:
1. [namespace_metadata_analysis.md](research/namespace_metadata_analysis.md) - 了解业务属性现状
2. [prod_gpu_cluster_analysis.md](research/prod_gpu_cluster_analysis.md) - 了解生产集群
3. [pod_source_identification_guide.md](design/pod_source_identification_guide.md) - Pod 识别方案
4. [k8s_cluster_integration_guide.md](guides/k8s_cluster_integration_guide.md) - K8s 集成指南

---

## ⚠️ 重要概念澄清

### example-service 的准确定义

**✅ 正确定义** (v2.1 + 实际调研):
- **系统**: 独立的开发环境管理系统
- **服务**: `example-service` API (`git@<git-host>:example-org/example-service.git`)
- **镜像**: `docker.example.com/example-org/example-service`
- **K8s 资源**: StatefulSet (namespace: `example-service`)
- **功能**: 提供可挂载 NFS/GPU 的 SSH 开发容器

**❌ 错误定义** (v2.0，已纠正):
- ~~与 tasks 表相关~~
- ~~`tasks.task_type = 'MANUALLY_CREATED_RAY'`~~

**澄清**: `MANUALLY_CREATED_RAY` 是 **DCS 服务的 Ray 集群**，与 example-service 无关

### CMDB 数据库选择

**✅ 正确选择**:
- **主数据库**: event_db (PostgreSQL @ 127.0.0.1:32432)
- **用途**: 存储 CMDB 维度表、example-service 生命周期、{BUSINESS_DESCRIPTION}
- **理由**: 集中管理，符合现有架构

**❓ 待明确**:
- GPU 统计 MVP 是否使用 example-service 数据库？
- 建议统一使用 event_db

---

## 🔄 版本历史

### CMDB 设计演进

| 版本 | 日期 | 状态 | 主要变化 |
|------|------|------|---------|
| v1.0 | - | archive | 早期设计 ([`event_db_cmdb_design_detailed.md`](archive/event_db_cmdb_design_detailed.md)) |
| v2.0 | 2026-01-29 | ⚠️ archive | 包含错误判断（example-service 与 tasks 关联） |
| v2.1 | 2026-01-29 | ✅ **当前标准** | 纠正错误，符合 event_db 策略 |

### GPU 统计设计

| 版本 | 日期 | 状态 | 定位 |
|------|------|------|------|
| v1.0 | 2026-01-31 | ✅ MVP | 快速上线方案（Informer + Redis） |
| v2.0 | 规划中 | 📋 未来 | GPU 实际使用率（DCGM + Prometheus） |

---

## 📝 文档维护规范

### 版本控制

- 所有设计文档应标注版本号
- 重大更新时，旧版本移至 `archive/`
- 在文档顶部保留版本历史

### 文档命名

- 设计文档: `<name>_design_v<version>.md`
- 分析文档: `<topic>_analysis.md`
- 指南文档: `<topic>_guide.md`
- 调研报告: `<topic>_report.md`

### 归档原则

- **保留** 过期版本到 `archive/`
- **不删除** 任何历史文档
- **更新** README.md 反映当前版本

---

## 🔗 快速链接

- [event_db Trigger 模式参考](analysis/event_db_trigger_functions.md)
- [K8s Label vs Annotation 使用场景](research/namespace_metadata_analysis.md#label-vs-annotation)
- [Pod 来源识别代码示例](design/pod_source_identification_guide.md#综合识别方案推荐)
