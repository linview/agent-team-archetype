# ECharts 生命周期管理

## 核心问题：条件渲染 + ECharts 实例

当图表容器被条件渲染（`v-if` / `{cond && <div/>}` / `{#if}`）控制时，容器 DOM 会在条件为 false 时被销毁。但 ECharts 实例仍持有对已销毁 DOM 的引用——这就是"僵尸实例"。

**症状**：首次渲染正常，条件变为 false 再变回 true 后，图表不显示，且无报错。

**根因**：`setOption()` 成功执行，但写入了一个绑定到已销毁 DOM 的实例，渲染无效果。

## 解决方案

**每次渲染前 dispose 旧实例，始终重新 init：**

```
function renderChart(container, data):
  if !container or !data: return
  try { oldChart?.dispose() }    // 清理僵尸
  chart = echarts.init(container) // 始终重新绑定
  chart.setOption(buildOption(data))
```

## 完整 Vue 3 composable

见 [scripts/vue_echarts_composable.ts](../scripts/vue_echarts_composable.ts)

## 其他注意事项

### resize 监听

窗口 resize 时图表需要自适应：

```typescript
onMounted(() => window.addEventListener('resize', () => chart?.resize()))
onUnmounted(() => {
  chart?.dispose()
  window.removeEventListener('resize', () => chart?.resize())
})
```

### 深色主题

ECharts 默认使用浅色主题。如果项目有深色模式：

```typescript
const chart = echarts.init(container, 'dark')  // 使用内置 dark 主题
// 或自定义主题
const chart = echarts.init(container, customTheme)
```

### 大数据量优化

当数据点超过 1000 时，考虑：

1. **开启 large 模式**：`series: [{ type: 'scatter', large: true }]`
2. **数据采样**：前端降采样后再渲染
3. **虚拟滚动**：只渲染可视区域的数据点

### 内存泄漏

确保 `onUnmounted` / `useEffect cleanup` / `destroy` 中调用 `dispose()`，否则 ECharts 实例会泄漏。
