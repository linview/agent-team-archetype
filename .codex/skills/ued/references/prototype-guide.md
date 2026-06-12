# HTML 原型指南

从文字描述或 ASCII 简图生成可浏览器预览的独立 HTML 原型，用于验证排版、交互流、动效。

---

## 核心原则

1. **单文件**：一个 `.html` 包含所有 CSS 和 JS，双击即可打开
2. **真实感**：用 mock 数据填充，不是 lorem ipsum 空壳
3. **可交互**：点击、切换、展开、筛选等基本操作都能运行
4. **有动效**：页面加载编排、hover 反馈、状态切换动画
5. **可抛弃**：原型验证完就丢，不作为生产代码基础

---

## HTML 结构模板

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>[页面名称] - Prototype</title>
  <style>
    /* === 主题变量 === */
    :root {
      --color-primary: #2563eb;
      --color-primary-light: #dbeafe;
      --color-accent: #f59e0b;
      --color-success: #10b981;
      --color-danger: #ef4444;
      --color-bg: #f8fafc;
      --color-surface: #ffffff;
      --color-text: #1e293b;
      --color-text-muted: #64748b;
      --color-border: #e2e8f0;
      --radius: 6px;
      --shadow: 0 1px 3px rgba(0,0,0,0.08);
      --transition: 0.2s ease;
    }

    /* === 基础重置 === */
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: 'PingFang SC', -apple-system, sans-serif;
      color: var(--color-text);
      background: var(--color-bg);
      line-height: 1.6;
    }

    /* === 布局 === */
    /* 见下方布局模式 */

    /* === 组件 === */
    /* 见下方组件模式 */

    /* === 动效 === */
    /* 见下方动效模式 */
  </style>
</head>
<body>
  <!-- 布局结构 -->
  <script>
    // 交互逻辑
  </script>
</body>
</html>
```

---

## 布局模式

### 侧栏 + 主内容区（企业后台标配）

```css
.layout {
  display: grid;
  grid-template-columns: 240px 1fr;
  grid-template-rows: 56px 1fr;
  height: 100vh;
}
.layout-header  { grid-column: 1 / -1; }
.layout-sidebar { grid-row: 2; }
.layout-main    { grid-row: 2; overflow-y: auto; padding: 24px; }
```

```html
<div class="layout">
  <header class="layout-header"><!-- 顶栏 --></header>
  <aside class="layout-sidebar"><!-- 侧栏导航 --></aside>
  <main class="layout-main"><!-- 内容区 --></main>
</div>
```

### 多列卡片网格

```css
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 16px;
}
```

### 左右分栏（详情页）

```css
.split-layout {
  display: grid;
  grid-template-columns: 1fr 360px;
  gap: 24px;
}
```

---

## 组件模式

### KPI 卡片

```html
<div class="kpi-card">
  <div class="kpi-label">CI/CD 流水线</div>
  <div class="kpi-value">128</div>
  <div class="kpi-trend trend-up">+12.5%</div>
  <div class="kpi-status healthy">健康</div>
</div>
```

```css
.kpi-card {
  background: var(--color-surface);
  border-radius: var(--radius);
  padding: 20px;
  box-shadow: var(--shadow);
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.kpi-value { font-size: 2rem; font-weight: 700; }
.kpi-trend { font-size: 0.875rem; font-weight: 600; }
.trend-up { color: var(--color-success); }
.trend-down { color: var(--color-danger); }
.kpi-status {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  width: fit-content;
}
.kpi-status.healthy { background: #dcfce7; color: #166534; }
.kpi-status.warning { background: #fef3c7; color: #92400e; }
.kpi-status.error   { background: #fee2e2; color: #991b1b; }
```

### 数据表格

```html
<div class="table-wrapper">
  <table>
    <thead>
      <tr>
        <th>ID</th><th>标题</th><th>状态</th><th>时间</th>
      </tr>
    </thead>
    <tbody id="table-body">
      <!-- JS 动态填充 -->
    </tbody>
  </table>
</div>
```

```css
.table-wrapper { overflow-x: auto; }
table {
  width: 100%;
  border-collapse: collapse;
  background: var(--color-surface);
  border-radius: var(--radius);
  overflow: hidden;
}
th, td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid var(--color-border);
}
th {
  background: var(--color-bg);
  font-weight: 600;
  font-size: 0.875rem;
  color: var(--color-text-muted);
}
tr:hover td { background: var(--color-primary-light); }
```

### 搜索栏 + 筛选器

```html
<div class="toolbar">
  <input type="text" class="search-input" placeholder="搜索...">
  <select class="filter-select">
    <option>全部状态</option>
    <option>进行中</option>
    <option>已完成</option>
  </select>
  <button class="btn btn-primary">搜索</button>
</div>
```

```css
.toolbar {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 16px;
}
.search-input, .filter-select {
  padding: 8px 12px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  font-size: 0.875rem;
}
.search-input:focus, .filter-select:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-light);
}
```

### 标签页切换

```html
<div class="tabs">
  <button class="tab active" data-tab="overview">概览</button>
  <button class="tab" data-tab="details">详情</button>
  <button class="tab" data-tab="history">历史</button>
</div>
<div class="tab-content active" id="tab-overview">概览内容</div>
<div class="tab-content" id="tab-details">详情内容</div>
<div class="tab-content" id="tab-history">历史内容</div>
```

```css
.tabs { display: flex; gap: 0; border-bottom: 2px solid var(--color-border); }
.tab {
  padding: 10px 20px;
  border: none;
  background: none;
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-text-muted);
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  transition: var(--transition);
}
.tab:hover { color: var(--color-text); }
.tab.active {
  color: var(--color-primary);
  border-bottom-color: var(--color-primary);
}
.tab-content { display: none; padding: 20px 0; }
.tab-content.active { display: block; }
```

```javascript
document.querySelectorAll('.tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    tab.classList.add('active');
    document.getElementById('tab-' + tab.dataset.tab).classList.add('active');
  });
});
```

### 展开/折叠面板

```html
<div class="accordion">
  <div class="accordion-item">
    <button class="accordion-header" onclick="this.parentElement.classList.toggle('open')">
      需求链路追踪 <span class="accordion-arrow">▼</span>
    </button>
    <div class="accordion-body">
      <!-- 折叠内容 -->
    </div>
  </div>
</div>
```

```css
.accordion-body {
  max-height: 0;
  overflow: hidden;
  transition: max-height 0.3s ease;
}
.accordion-item.open .accordion-body {
  max-height: 600px;
}
.accordion-arrow {
  transition: transform 0.3s ease;
  font-size: 0.75rem;
}
.accordion-item.open .accordion-arrow {
  transform: rotate(180deg);
}
```

### 模态框

```html
<div class="modal-overlay" id="modal">
  <div class="modal">
    <div class="modal-header">
      <h3>标题</h3>
      <button onclick="closeModal()" class="modal-close">&times;</button>
    </div>
    <div class="modal-body">内容</div>
    <div class="modal-footer">
      <button class="btn" onclick="closeModal()">取消</button>
      <button class="btn btn-primary">确认</button>
    </div>
  </div>
</div>
```

```css
.modal-overlay {
  display: none;
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.4);
  z-index: 1000;
  align-items: center;
  justify-content: center;
}
.modal-overlay.active { display: flex; }
.modal {
  background: var(--color-surface);
  border-radius: 8px;
  width: 90%;
  max-width: 520px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.15);
  animation: slideUp 0.25s ease;
}
@keyframes slideUp {
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}
```

### 侧栏导航

```html
<nav class="sidebar-nav">
  <a class="nav-item active">
    <span class="nav-icon">📊</span> 仪表盘
  </a>
  <a class="nav-item">
    <span class="nav-icon">📋</span> 需求
  </a>
  <a class="nav-item">
    <span class="nav-icon">🔀</span> 代码
  </a>
</nav>
```

```css
.sidebar-nav { padding: 12px; }
.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border-radius: var(--radius);
  color: var(--color-text-muted);
  text-decoration: none;
  font-size: 0.875rem;
  cursor: pointer;
  transition: var(--transition);
}
.nav-item:hover { background: var(--color-primary-light); color: var(--color-text); }
.nav-item.active {
  background: var(--color-primary-light);
  color: var(--color-primary);
  font-weight: 600;
}
.nav-icon { font-size: 1.1rem; }
```

---

## 动效模式

### 页面加载编排（错开出现）

```css
.stagger-item {
  opacity: 0;
  transform: translateY(12px);
  animation: fadeInUp 0.35s ease forwards;
}
.stagger-item:nth-child(1) { animation-delay: 0.0s; }
.stagger-item:nth-child(2) { animation-delay: 0.06s; }
.stagger-item:nth-child(3) { animation-delay: 0.12s; }
.stagger-item:nth-child(4) { animation-delay: 0.18s; }

@keyframes fadeInUp {
  to { opacity: 1; transform: translateY(0); }
}
```

### Hover 卡片抬升

```css
.card-hover {
  transition: transform var(--transition), box-shadow var(--transition);
}
.card-hover:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.1);
}
```

### 加载骨架屏

```css
.skeleton {
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 4px;
}
@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}
```

```html
<!-- 骨架屏用法 -->
<div class="skeleton" style="width:60%;height:20px;margin-bottom:8px"></div>
<div class="skeleton" style="width:40%;height:16px;margin-bottom:8px"></div>
<div class="skeleton" style="width:100%;height:60px"></div>
```

### 状态切换过渡

```css
.status-badge {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  transition: all 0.3s ease;
}
/* 切换 class 即可触发过渡动画 */
.status-badge.success { background: #dcfce7; color: #166534; }
.status-badge.warning { background: #fef3c7; color: #92400e; }
.status-badge.error   { background: #fee2e2; color: #991b1b; }
```

---

## Mock 数据策略

在 `<script>` 中定义 mock 数据，保持和真实 API 响应结构一致：

```javascript
const MOCK = {
  kpiCards: [
    { label: 'CI/CD 流水线', value: 128, trend: '+12.5%', status: 'healthy' },
    { label: '制品产物', value: 256, trend: '+5.2%', status: 'healthy' },
    { label: '集成测试', value: 48, trend: '-2.1%', status: 'warning' },
    { label: '数据健康', value: 96, trend: '+0.5%', status: 'healthy' },
  ],
  recentActivities: [
    { type: 'mr', title: 'feat: 添加用户认证模块', time: '10 分钟前', user: '张三' },
    { type: 'pipeline', title: '#128 构建成功', time: '25 分钟前', user: 'CI Bot' },
    { type: 'artifact', title: 'v2.3.1 发布', time: '1 小时前', user: '李四' },
  ],
  tableData: [
    { id: 'WI-001', title: '用户登录功能', status: 'success', time: '2026-05-28' },
    { id: 'WI-002', title: '数据导出优化', status: 'warning', time: '2026-05-27' },
    { id: 'WI-003', title: '权限管理重构', status: 'error', time: '2026-05-26' },
  ],
};
```

然后用 JS 渲染到 DOM：

```javascript
function renderTable(data) {
  const tbody = document.getElementById('table-body');
  tbody.innerHTML = data.map(row => `
    <tr>
      <td>${row.id}</td>
      <td>${row.title}</td>
      <td><span class="status-badge ${row.status}">${
        row.status === 'success' ? '通过' :
        row.status === 'warning' ? '警告' : '失败'
      }</span></td>
      <td>${row.time}</td>
    </tr>
  `).join('');
}
```

---

## 从 ASCII 简图到 HTML 的转换流程

当用户提供 ASCII 线框图时：

1. **识别布局区域**：从 `+--` 边界和 `|` 分隔符识别独立区块
2. **确定组件类型**：根据标签文字判断（"搜索" → 搜索栏、"列表" → 表格、"卡片" → KPI 卡片）
3. **选择布局模式**：根据区域排列（上下 → grid-template-rows，左右 → grid-template-columns）
4. **填充 Mock 数据**：根据字段名生成合理的模拟数据
5. **添加交互**：根据标注（"[点击展开]"、"切换 Tab"）添加 JS 交互
6. **添加动效**：页面加载编排 + hover 反馈

---

## 通用样式片段

### 按钮

```css
.btn {
  padding: 8px 16px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  background: var(--color-surface);
  cursor: pointer;
  font-size: 0.875rem;
  transition: var(--transition);
}
.btn:hover { background: var(--color-bg); }
.btn-primary {
  background: var(--color-primary);
  color: white;
  border-color: var(--color-primary);
}
.btn-primary:hover { opacity: 0.9; }
```

### 标签/徽章

```css
.badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
}
```

### 空状态

```html
<div class="empty-state">
  <div class="empty-icon">📭</div>
  <p>暂无数据</p>
</div>
```

```css
.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--color-text-muted);
}
.empty-icon { font-size: 3rem; margin-bottom: 12px; }
```

---

## 图标策略

原型中使用图标的三种方式（从简单到完整）：

1. **Emoji**（最快）：`📊 📋 🔀 📦 🧪 🔗` — 无需外部依赖
2. **Unicode 符号**：`← → ▼ × ☰ ⚡ ✓` — 常用交互图标
3. **CDN 图标库**（需要网络）：
```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/lucide-static@latest/font/lucide.min.css">
<!-- 使用：<i class="icon-search"></i> -->
```

---

## 从文字描述生成原型的提示词模式

当用户给出文字描述（而非 ASCII 简图）时，按以下结构解析：

| 用户描述 | 提取信息 | 映射组件 |
|---------|---------|---------|
| "顶部有 4 个 KPI 卡片" | 布局区域 + 组件类型 | card-grid + kpi-card |
| "下面是搜索 + 列表" | 搜索栏 + 数据表格 | toolbar + table |
| "点击展开详情" | 交互行为 | accordion |
| "左边侧栏" | 布局结构 | sidebar-nav |
| "切换 Tab" | 交互行为 | tabs |
| "弹出确认框" | 交互行为 | modal |
| "加载时有个动画" | 动效需求 | stagger-item / skeleton |
| "下拉选择" | 表单组件 | select |

---

## 在线参考检索

生成原型时可利用在线资源获取风格灵感和具体实现参考。检索到的内容只作为灵感，不直接复制代码。

### 推荐检索来源

| 来源 | 用途 | 搜索示例 |
|------|------|---------|
| **Tailwind CSS** (tailwindcss.com) | 布局模式、配色方案、间距系统 | `site:tailwindcss.com dashboard layout` |
| **shadcn/ui** (ui.shadcn.com) | 现代组件样式参考 | `site:ui.shadcn.com table component` |
| **CodePen** (codepen.io) | 可运行的 CSS/JS 片段 | `site:codepen.io CSS stagger animation` |
| **CSS Tricks** (css-tricks.com) | CSS 技巧和完整教程 | `site:css-tricks.com CSS grid layout` |
| **Dribbble** (dribbble.com) | 视觉风格灵感、配色 | `site:dribbble.com admin dashboard dark` |
| **Mobbin** (mobbin.com) | 移动端设计模式 | `site:mobbin.com chat interface` |
| **MDN** (developer.mozilla.org) | CSS 属性权威文档 | `site:developer.mozilla.org CSS custom properties` |

### 检索策略

| 场景 | 搜索关键词模式 | 示例 |
|------|---------------|------|
| 用户提到特定产品 | `[产品名] UI design` | `Linear app UI design` |
| 需要特定组件 | `[组件名] CSS pattern` | `data table CSS pattern responsive` |
| 需要动效灵感 | `CSS animation [效果名]` | `CSS stagger animation on scroll` |
| 不确定配色 | `color palette [风格]` | `color palette SaaS dashboard` |
| 框架组件参考 | `[框架名] [组件] example` | `Vue 3 select dropdown example` |
| CSS 布局问题 | `[布局类型] layout CSS` | `holy grail layout CSS grid` |

### 使用原则

1. **灵感而非复制**：检索到的代码需要根据当前项目的设计方向调整
2. **保持自包含**：不要引入检索来源的依赖（如 CDN 引用 Tailwind），只用其布局/配色思路
3. **优先 CSS**：从检索中学习 CSS 原生写法，而非依赖 JS 库
4. **验证兼容性**：检索到的 CSS 属性需要在目标浏览器中验证（参考 MDN）

### 不同风格的参考示例

`examples/` 目录提供了 6 种不同风格的原型示例，每种都有独特的视觉语言。在生成原型前浏览与目标风格最接近的示例，理解其构建方式：

- 企业后台 → `dashboard-prototype.html`（浅色、侧栏、数据密集）
- 营销落地页 → `landing-prototype.html`（暗色、渐变、大面积留白）
- 移动端 → `mobile-prototype.html`（iOS 风格、底部导航、触摸友好）
- 表单向导 → `form-prototype.html`（极简、多步骤、验证反馈）
- 数据大屏 → `dataviz-prototype.html`（深色、等宽字体、实时指标）
- 聊天界面 → `chat-prototype.html`（圆润气泡、侧栏列表、输入栏）

---

**版本**: v1.1
**创建日期**: 2026-05-29
**参考示例**: [examples/](../examples/) 目录
