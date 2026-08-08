# 示例工程文档中心

**更新时间**: 2026-04-25
**维护者**: Development Team

---

## 📚 文档分类

### 🎯 设计文档 (design/)

- **[service_layer_architecture_v4.2.md](design/service_layer_architecture_v4.2.md)** ⭐ - 服务层架构设计（**当前标准**）
  - K8s Informer 监听机制
  - Pod 生命周期处理流程
  - 状态机设计
  - **版本**: v4.2 (2026-04-25)

- **[service_layer_faq_v4.1.md](design/service_layer_faq_v4.1.md)** - 服务层 FAQ
  - 常见问题与最佳实践
  - **版本**: v4.1 (2026-04-25)

- **[api_design_v1.3.md](design/api_design_v1.3.md)** - API 设计规范
  - RESTful 接口设计
  - 请求/响应格式
  - 聚合查询能力
  - **版本**: v1.3

- **[data_layer_design_{sem_ver}.md.template](design/data_layer_design_{sem_ver}.md.template)** - 数据层设计模板
  - 用于新项目的数据层设计文档骨架

---

## 🎯 文档使用指南

### 场景 1: 学习架构设计

**推荐阅读顺序**:
1. [service_layer_architecture_v4.2.md](design/service_layer_architecture_v4.2.md) - 系统整体架构
2. [api_design_v1.3.md](design/api_design_v1.3.md) - API 设计与调用约定
3. [service_layer_faq_v4.1.md](design/service_layer_faq_v4.1.md) - 常见问题答疑

### 场景 2: 创建新项目

1. 复制本工程结构作为起点
2. 使用 [data_layer_design 模板](design/data_layer_design_{sem_ver}.md.template) 起草自己的数据层设计
3. 参考 service_layer 与 api_design 完善自身业务

---

## 📝 文档维护规范

### 版本控制

- 所有设计文档应标注版本号
- 重大更新时,旧版本移至 `archive/`(本工程未提供)
- 在文档顶部保留版本历史

### 文档命名

- 设计文档: `<name>_design_v<version>.md`
- 模板文档: `<name>_design_{sem_ver}.md.template`

### 文档组织

```
docs/
├── README.md                                       # 本文档
└── design/
    ├── README.md                                   # 设计文档目录说明
    ├── service_layer_architecture_v4.2.md          # 服务层架构
    ├── service_layer_faq_v4.1.md                   # 服务层 FAQ
    ├── api_design_v1.3.md                          # API 设计
    └── data_layer_design_{sem_ver}.md.template     # 数据层设计模板
```

---

**文档版本**: v1.0
**更新日期**: 2026-04-25
**维护者**: Development Team
