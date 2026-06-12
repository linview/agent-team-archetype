# 视觉设计指南

从 `/frontend-design` skill 提取的可操作视觉设计指导，适配工程化前端开发工作流。

---

## 设计思维四问

进入组件设计前快速自检，避免"打开编辑器直接写"的无方向感：

| 问题 | 目的 | 示例 |
|------|------|------|
| 这个界面给谁用？ | 确定基调 | 运维看板 → 功能主义；营销页 → 精炼奢华；内部工具 → 高效紧凑 |
| 一句话描述视觉风格 | 锁定方向 | "工业仪表盘" / "杂志排版" / "工具面板" / "卡片流" |
| 技术约束是什么？ | 缩小选择 | SSR 限制字体加载 / 移动端优先 / 暗色模式 / 无障碍 |
| 用户会记住什么？ | 差异化点 | 一个加载动画、一种独特排版、一个醒目的交互反馈 |

**原则**：不追求"最漂亮"，追求"最合适"。管理后台不需要炫酷动效，营销页不需要高密度数据表。

---

## 字体选择

### 选择策略

字体对界面的辨识度影响最大，但也是最容易被忽略的一环。

**选择原则**：
1. **display + body 搭配**：标题用一个有辨识度的 display font，正文用一个易读的 body font
2. **最多 2-3 种字体**：超过 3 种字体 = 视觉噪音
3. **考虑加载性能**：中文字体体积大，优先用系统字体栈 + 英文自定义字体

### 避免

| 字体 | 为什么避免 | 替代 |
|------|----------|------|
| Inter | 过于通用，AI 生成标配 | DM Sans、Outfit、Plus Jakarta Sans |
| Roboto | Android 默认，辨识度低 | Nunito、Manrope、Source Sans 3 |
| Arial | 系统回退字体，无设计感 | 任何有风格的 sans-serif |
| system-ui | 等于没选 | 明确指定具体字体 |

### 中英文混排字体栈

```css
/* 推荐：英文自定义 + 中文系统字体 */
font-family: 'Plus Jakarta Sans', -apple-system, 'PingFang SC',
  'Microsoft YaHei', sans-serif;

/* 标题：有辨识度的 display font */
font-family: 'Space Grotesk', 'Noto Sans SC', sans-serif;
```

### 字体加载优化

```css
/* font-display: swap 避免布局偏移 */
@font-face {
  font-family: 'Plus Jakarta Sans';
  src: url('/fonts/PlusJakartaSans.woff2') format('woff2');
  font-display: swap;
  unicode-range: U+0020-007E; /* 只加载 ASCII */
}
```

---

## 色彩系统

### CSS 变量统一管理

色彩值分散在代码中 = 维护噩梦。所有色彩通过 CSS 变量定义：

```css
:root {
  --color-primary: #2563eb;
  --color-primary-light: #3b82f6;
  --color-accent: #f59e0b;
  --color-bg: #ffffff;
  --color-surface: #f8fafc;
  --color-text: #1e293b;
  --color-text-muted: #64748b;
  --color-border: #e2e8f0;
}
```

### 色彩策略

| 策略 | 说明 | 适用场景 |
|------|------|---------|
| 主色 + 强调色 | 一个主色占据 60%，一个强调色占据 10% | 大多数企业应用 |
| 单色系 | 一个色相的不同明暗 | 数据密集型仪表盘 |
| 中性 + 一点色彩 | 灰色为主，一个颜色做 CTAs | 工具类应用 |

### 对比度

- 正文文本与背景对比度 ≥ 4.5:1（WCAG AA）
- 大标题对比度 ≥ 3:1
- 检查工具：Chrome DevTools → 元素面板 → Contrast ratio

### 反模式

| 反模式 | 为什么不好 | 替代 |
|--------|----------|------|
| 紫色渐变 + 白底 | AI 生成标配，千篇一律 | 选一个有意义的颜色方案 |
| 彩虹色按钮 | 视觉混乱 | 一个强调色就够了 |
| 纯灰度无色彩 | 乏味、无引导 | 加一个强调色用于 CTAs |
| 硬编码 `#xxx` | 不可维护 | CSS 变量 |

---

## 动效与交互

### 动效分层

不是所有元素都需要动效。按影响力分层：

| 层级 | 何时使用 | 实现方式 |
|------|---------|---------|
| **反馈** | 按钮 hover、表单验证、状态切换 | CSS transition（0.15-0.3s） |
| **引导** | 页面加载、数据刷新、新内容出现 | CSS animation + animation-delay |
| **氛围** | 背景、装饰元素、品牌传达 | CSS animation（循环）或 JS（复杂路径） |

### 优先 CSS-only

```css
/* 高质量 hover 效果 */
.card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

/* 页面加载编排 — 错开出现 */
.item {
  opacity: 0;
  animation: fadeInUp 0.4s ease forwards;
}
.item:nth-child(1) { animation-delay: 0s; }
.item:nth-child(2) { animation-delay: 0.08s; }
.item:nth-child(3) { animation-delay: 0.16s; }

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: translateY(0); }
}
```

### 何时引入 JS 动画库

- 复杂路径动画（SVG 路径绘制）
- 物理弹性效果（弹簧动画）
- 滚动驱动动画（scroll-linked）
- Vue: `@vueuse/motion`; React: `framer-motion`; 通用: `gsap`

### 反模式

| 反模式 | 为什么不好 |
|--------|----------|
| 所有元素都在动 | 视觉疲劳、分散注意力 |
| 动效 > 0.5s（非品牌动画） | 用户感觉"卡" |
| 纯装饰性粒子效果 | 增加认知负担，不传递信息 |
| 移动端大量 JS 动画 | 性能差、耗电 |

---

## 空间构图

### 布局策略

| 基调 | 布局特征 | 适用场景 |
|------|---------|---------|
| 功能主义 | 密集网格、最小间距、数据优先 | 后台管理、监控面板 |
| 精炼 | 大面积留白、少量高质量内容 | 营销页、Landing |
| 杂志感 | 不对称、图文混排、分栏 | 博客、内容站 |
| 工具型 | 固定侧栏 + 弹性内容区 | IDE、编辑器、工作台 |

### 间距系统

用 4px 或 8px 基准的间距系统：

```css
:root {
  --space-1: 4px;   /* 元素内间距 */
  --space-2: 8px;   /* 紧密元素间距 */
  --space-3: 16px;  /* 标准间距 */
  --space-4: 24px;  /* 区块间距 */
  --space-5: 32px;  /* 大区块间距 */
  --space-6: 48px;  /* 页面级间距 */
  --space-8: 64px;  /* 重大分隔 */
}
```

### 打破单调的技巧

1. **不对称布局**：左右分栏不用 50/50，试 60/40 或 70/30
2. **重叠元素**：卡片微重叠、图片溢出容器
3. **Z 轴层次**：阴影 + z-index 创造深度感
4. **对角线/斜切**：section 分隔用斜线而非水平线
5. **强调单一焦点**：一个页面/区块只有一个最重要的元素

---

## 反模式清单（避免 AI 生成感）

| 反模式 | 表现 | 修正 |
|--------|------|------|
| **千篇一律的配色** | 紫白渐变 + rounded-xl 按钮 | 根据项目语境选择色彩方案 |
| **字体无辨识度** | Inter/Roboto 全家桶 | 至少标题用有风格的字体 |
| **过度圆润** | 所有元素 `rounded-2xl` + `shadow-lg` | 按功能区分：按钮圆润、卡片微圆、数据表方角 |
| **均匀分布** | 所有卡片等宽等高等间距 | 用间距层级和大小变化创造节奏感 |
| **微交互泛滥** | 每个元素都有 hover 效果 | 只在关键交互点做微交互 |
| **缺乏语境** | "好看"但不匹配业务 | 先回答设计思维四问再动手 |
| **无色彩变量** | 代码中散布 `#3B82F6` | CSS 变量统一管理 |

---

## 框架适配

### Vue 3 + Element Plus

```css
/* 覆盖 Element Plus 的 CSS 变量 */
:root {
  --el-color-primary: var(--color-primary);
  --el-border-radius-base: 4px;
}
```

### React + Ant Design

```css
/* 使用 Ant Design token */
:where(.css-1xxxxxx).ant-btn-primary {
  background: var(--color-primary);
}
```

### Tailwind CSS

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: 'var(--color-primary)',
        accent: 'var(--color-accent)',
      },
      fontFamily: {
        display: ['Space Grotesk', 'sans-serif'],
        body: ['Plus Jakarta Sans', 'sans-serif'],
      },
    },
  },
}
```

---

**版本**: v1.0
**来源**: `/frontend-design` skill SOTA 内容，工程化改造
**创建日期**: 2026-05-29
