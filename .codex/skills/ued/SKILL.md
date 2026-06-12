---
name: "ued"
description: "前端 UED 开发工作流——数据先行、分步实施、迭代精化。当你需要设计或修改前端页面、组件、交互流程时使用此 skill，包括新页面开发、现有页面重构、可视化图表、Bug 调试、交互优化。即使用户只是说'改一下首页'或'这个图显示不对'，也应参考此工作流。覆盖 Vue / React / Svelte 等主流前端框架。"
---

# 前端 UED 开发工作流

前端开发的实用步骤指南：先理解需求，再读懂数据，然后搭骨架、写代码、反复打磨。

## 核心原则

1. **数据先行**：写任何前端代码前，先读懂后端数据结构和 API 返回值
2. **容器验证**：每次代码变更后必须重建 Docker 容器（或刷新 dev server），浏览器验证实际效果
3. **迭代精化**：打磨阶段允许多轮，每轮只解决一类问题
4. **后端联动**：前端需求驱动的 API 变更，后端先行、设计文档同步
5. **变更分级**：按规模决定是否产出设计文档——小改不动文档，中改追加章节，大改升级版本

## 工作步骤概览

| 步骤 | 做什么 | 输入 | 输出 |
|------|--------|------|------|
| **1. 理解需求** | 明确要做什么 | 用户描述 / Bug 报告 | 任务定义 + 影响范围 |
| **2. 读懂数据** | 搞清数据从哪来、长什么样 | 后端代码 + DB schema + API spec | 数据流图 + 字段映射 |
| **3. 设计组件** | 规划组件结构和交互 | 步骤 1 + 步骤 2 的理解 | 组件树 + 线框图 + 交互流 |
| **4. 编码实现** | 按设计写代码 | 步骤 3 的设计 + 项目代码规范 | 实现代码 |
| **5. 迭代打磨** | 修复 Bug、优化体验 | 步骤 4 的实现 + 用户反馈 | 优化后的代码 |

### 设计产出的持久化规则

| 变更规模 | 设计产出 | 存储方式 |
|---------|---------|---------|
| **小**（Bug 修复、微调） | 不产出 | commit message 即证据 |
| **中**（新组件、页面重构） | 线框图 + 交互流 | 设计文档新章节 或 Story 附件 |
| **大**（新功能、架构变更） | 完整组件树 + 线框 + 状态管理 + 交互流 | 升级设计文档版本，旧版归档 |

线框图使用 Mermaid 或 ASCII，不依赖 Figma 等外部工具。框架选择见 [references/framework-guide.md](references/framework-guide.md)。

---

## 步骤 1：理解需求

明确用户要什么，不要急于写代码。

### 关键问题

| 问题 | 目的 | 怎么确认 |
|------|------|---------|
| 哪个页面/组件？ | 定位影响范围 | 问用户或看路由配置 |
| 用户操作流程是什么？ | 理解交互路径 | 让用户描述"我点这里然后看那里" |
| 后端 API 能支撑吗？ | 判断是否需要后端变更 | 读 handler/service 代码 |
| 设计文档怎么说？ | 找到 spec 依据 | 读项目设计文档 |

### 产出

- 一句话描述任务目标
- 列出可能涉及的文件（前端组件、API client、后端 handler/service/repo）
- 标记是否需要后端变更

---

## 步骤 2：读懂数据

在写任何 UI 代码之前，先彻底搞清楚数据从哪来、长什么样。

### 做什么

1. **读后端链路**：repository → service → handler，理解数据流转
2. **读数据模型**：struct/class 字段、序列化 tag、数据库列的对应关系
3. **查测试数据**：连接数据库确认实际有多少数据可用
4. **理解数据变换**：是否有 Base64 编码、JSON 嵌套、时间格式转换
5. **确认 API 响应结构**：统一响应格式中的 data、pagination、warnings 等字段

### 常见数据陷阱

| 陷阱 | 症状 | 解法 |
|------|------|------|
| 编码层问题（Base64/UTF-8） | 非英文字符乱码 | 见 [references/encoding-patterns.md](references/encoding-patterns.md) |
| `null` vs 空数组 | JSON 序列化为 `null` 而非 `[]` | 后端确保空切片初始化 |
| 字段名不一致 | 序列化 tag 与数据库列名不同 | 仔细读 struct 的 JSON/DB tag |
| 分页参数缺失 | 查询返回 0 条 | 检查默认分页参数 |

### 产出

- 数据流图：DB → Repo → Service → Handler → API Response → Frontend
- 关键字段映射表
- 已知的数据转换需求

---

## 步骤 3：设计组件

设计组件结构和布局，先骨架后血肉。

### 做什么

1. **确定组件层级**：页面 → 区块 → 组件 → 子组件
2. **选择可视化库**：ECharts / D3 / Chart.js / Recharts（按需选择）
3. **定义状态管理**：组件内 ref/reactive vs 全局 store vs URL 状态
4. **规划 API 调用时机**：mount 时 / 路由变化时 / 用户触发
5. **确定视觉设计方向**（见下方）

### 视觉设计方向

在确定组件层级和状态管理后，快速回答四个问题锁定视觉方向：

| 问题 | 目的 | 示例 |
|------|------|------|
| 这个界面给谁用？ | 确定基调 | 运维看板 → 功能主义 / 营销页 → 精炼 |
| 一句话描述视觉风格 | 锁定方向 | "工业仪表盘" / "杂志排版" / "工具面板" |
| 技术约束是什么？ | 缩小选择 | SSR / 移动端 / 暗色模式 / 无障碍 |
| 用户会记住什么？ | 差异化点 | 一个动画、一种排版、一个颜色 |

> 详细的字体选择、色彩系统、动效模式和构图技巧见 [references/visual-design-guide.md](references/visual-design-guide.md)。

### 布局设计原则

- **信息层次分明**：L1 概览 → L2 趋势/活动 → L3 详情/追踪
- **操作入口前置**：用户最常用的操作放在最显眼位置
- **渐进式揭示**：默认只展示关键信息，点击展开详情

### 线框图模板

见 [templates/wireframe.md](templates/wireframe.md)。

### HTML 原型（可选但推荐）

当设计涉及复杂布局、交互流或动效时，生成独立 HTML 文件用于浏览器预览——比 ASCII 线框图直观 10 倍，比框架代码快 10 倍。

**输入**：组件树 + 线框图 + 交互流（可以是文字描述或 ASCII 简图）
**输出**：单个 `.html` 文件（内联 CSS + JS），浏览器直接打开

**何时生成原型**：
- 中/大规模变更（新页面、布局重构、多步交互流）
- 需要与设计师/PM/后端对齐视觉方向时
- 动效/交互比较复杂，纯文字难以描述时

**原型要求**：

| 要求 | 为什么 | 怎么做 |
|------|--------|--------|
| 自包含 | 无需构建工具，浏览器直接打开 | 所有 CSS/JS 内联，CDN 仅限图标库 |
| Mock 数据 | 空页面看不出排版效果 | 硬编码 3-5 条示例数据 |
| 可交互 | 验证点击/切换/展开流程 | Vanilla JS 实现基本交互 |
| 有动效 | 验证动画节奏和时机 | CSS transition + animation |
| 主题变量 | 一眼看到色彩系统效果 | CSS custom properties |
| **风格匹配** | 原型必须反映步骤 3 选定的视觉方向 | 每次从零组合，不复制固定模板 |

**关键**：原型的视觉风格必须匹配"视觉设计方向"四问的结论——选了"工业仪表盘"就不应该出现圆润气泡，选了"活泼卡片流"就不应该用暗色大屏。从 `references/prototype-guide.md` 的模式库中按需组合，而非复制固定模板。

**在线参考**：生成原型时可利用在线资源获取风格灵感——搜索实际产品 UI、特定 CSS 模式、动效参考。推荐的检索来源见 [references/prototype-guide.md](references/prototype-guide.md) 的"在线参考检索"章节。

> 构建块和模式库见 [references/prototype-guide.md](references/prototype-guide.md)。不同风格的参考示例见 [examples/](examples/) 目录。

### 产出

- 组件树（ASCII 或 Mermaid）
- 状态变量清单
- API 调用计划（什么时候调、参数是什么）
- **HTML 原型**（可选，中/大规模变更时推荐）

---

## 步骤 4：编码实现

按设计写代码，遵循项目已有模式。框架特定的实现模式见 [references/](references/) 目录。

### 通用实现规范

**API 调用模式**（伪代码，各框架适配见 references）：
```
state: { loading: false, data: [], error: null }
action fetchData():
  loading = true
  try:
    response = api.getItems(params)
    if response.ok: data = response.items
  finally:
    loading = false
```

**图表生命周期**（通用原则）：
```
renderChart():
  if no container or no data: return
  dispose old chart instance  // 条件渲染会回收 DOM，必须清理旧实例
  chart = init(container)
  chart.setOption(config)

onUnmounted():
  chart?.dispose()
  remove resize listener
```

> 为什么每次都要 dispose？因为条件渲染（`v-if` / `{condition && <Comp/>}` / `{#if}`）会销毁 DOM 节点，图表实例绑定在已销毁的 DOM 上会变成僵尸实例，后续 `setOption()` 写入无底洞。

### Docker 验证

代码修改后必须重建容器（容器内是编译产物，不重建则代码不生效）：

```bash
docker compose up -d --build <frontend-service>
```

或使用 dev server（Vite / webpack dev server）时，检查 HMR 是否生效。

---

## 步骤 5：迭代打磨

实现后的打磨阶段，允许多轮迭代，每轮聚焦一类问题。

### 打磨检查清单

#### 第一轮：功能正确性

- [ ] API 调用参数正确（分页、搜索、过滤）
- [ ] 加载态、空态、错误态都有处理
- [ ] 数据类型转换正确（编码、时间、数字格式）
- [ ] 分页逻辑正确

#### 第二轮：交互体验

- [ ] 用户操作流程顺畅
- [ ] 表单/选择器的默认值合理
- [ ] 列表过长时有滚动或分页
- [ ] 图表交互正常（tooltip、点击、缩放）

#### 第三轮：视觉打磨

- [ ] 字体有辨识度（非默认 Inter/Roboto/Arial）
- [ ] 色彩系统用 CSS 变量统一管理，非硬编码色值
- [ ] 动效服务于交互反馈，不是装饰
- [ ] 空间构图有意为之（间距层级分明，非均匀分布）
- [ ] 整体风格一致，无拼凑感
- [ ] 间距、对齐、圆角一致
- [ ] 文字不溢出、不被截断
- [ ] 空状态有友好提示

### Bug 调试模式

当用户报告"操作后不显示/不刷新"类 Bug，按优先级排查：

1. **Network 面板**：API 是否被调用？返回码？响应体？
2. **Console 面板**：是否有运行时错误？
3. **组件状态**：reactive/ref 数据是否已更新？
4. **DOM 结构**：条件渲染是否导致 DOM 被销毁？

**高频 Bug 模式**：

| 症状 | 可能原因 | 排查方向 |
|------|---------|---------|
| 首次有效，二次无效 | 实例未重新创建 | 图表/DOM 生命周期 |
| 非英文乱码 | 编码层问题 | Base64 解码、TextDecoder |
| 选项不全 | API 分页限制 | 增大 page_size 或远程搜索 |
| 选择后无反应 | 状态未同步 | v-model / onChange 绑定 |

---

## 跨步骤协作

### 后端 API 变更流程

当前端需求驱动后端 API 变更时：

1. **后端先行**：repo → service → handler 逐层实现
2. **单测同步**：更新 mock 接口和测试用例
3. **设计文档升级**：对应设计文档 MINOR 版本升级，旧版归档到 `archive/`
4. **Scrum 同步**：更新/创建 Story，同步 Epic AC，刷新 DASHBOARD/KANBAN

### 与设计文档的集成

- 小变更：不更新设计文档，commit message 记录
- 中变更（新组件/交互）：在设计文档中追加章节
- 大变更（架构/新功能）：设计文档 MINOR 版本升级 + 归档旧版

---

## References 目录

框架特定实现模式和可复用代码：

| 文件 | 内容 | 何时使用 |
|------|------|---------|
| [references/framework-guide.md](references/framework-guide.md) | Vue 3 / React / Svelte / Angular 模式对比 | 选择技术方案或跨项目复用 |
| [references/encoding-patterns.md](references/encoding-patterns.md) | Base64 UTF-8 解码、JSON 嵌套处理 | 遇到编码/序列化问题 |
| [references/echarts-lifecycle.md](references/echarts-lifecycle.md) | ECharts 生命周期管理详细指南 | 使用 ECharts 可视化 |
| [references/visual-design-guide.md](references/visual-design-guide.md) | 字体选择、色彩系统、动效模式、空间构图 | 需要视觉设计指导时 |

## Scripts 目录

可复用代码模板：

| 文件 | 用途 |
|------|------|
| [scripts/vue_api_template.ts](scripts/vue_api_template.ts) | Vue 3 Composition API 调用模板 |
| [scripts/vue_echarts_composable.ts](scripts/vue_echarts_composable.ts) | Vue 3 ECharts composable |
| [scripts/base64_decoder.ts](scripts/base64_decoder.ts) | UTF-8 Base64 解码工具函数 |

## Templates 目录

设计产出模板：

| 文件 | 用途 |
|------|------|
| [templates/wireframe.md](templates/wireframe.md) | ASCII 线框图模板 |
| [templates/interaction_flow.md](templates/interaction_flow.md) | 交互流程文档模板 |

## Examples 目录

原型输出参考示例（不复制，仅参考构建方式和交互模式）：

| 文件 | 视觉风格 | 适用场景 |
|------|---------|---------|
| [examples/dashboard-prototype.html](examples/dashboard-prototype.html) | 浅色企业后台 | 管理面板、监控看板 |
| [examples/landing-prototype.html](examples/landing-prototype.html) | 暗色渐变营销页 | 落地页、产品介绍 |
| [examples/mobile-prototype.html](examples/mobile-prototype.html) | iOS 风格移动端 | App 界面、H5 页面 |
| [examples/form-prototype.html](examples/form-prototype.html) | 极简表单 | 注册、设置、多步向导 |
| [examples/dataviz-prototype.html](examples/dataviz-prototype.html) | 深色数据大屏 | 可视化大屏、实时监控 |
| [examples/chat-prototype.html](examples/chat-prototype.html) | 圆润气泡风格 | 聊天、消息、工单对话 |

---

**版本**: v5.1
**创建日期**: 2026-05-29
**作者**: Dev Team
