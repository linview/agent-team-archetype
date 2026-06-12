/**
 * Vue 3 ECharts composable
 *
 * 解决核心问题：条件渲染（v-if）销毁 DOM 后，
 * ECharts 实例变为僵尸，必须 dispose + re-init。
 */
import { ref, onMounted, onUnmounted, watch, type Ref } from 'vue'
import * as echarts from 'echarts'
import type { EChartsOption } from 'echarts'

interface UseEChartsOptions<T> {
  /** 图表容器 ref */
  container: Ref<HTMLDivElement | undefined>
  /** 响应式数据源 */
  data: Ref<T | null>
  /** 根据数据构建 ECharts option */
  buildOption: (data: T) => EChartsOption
}

export function useECharts<T>({ container, data, buildOption }: UseEChartsOptions<T>) {
  let chart: echarts.ECharts | null = null

  function render() {
    if (!container.value || !data.value) return
    // 关键：先 dispose 僵尸实例（v-if 会回收 DOM）
    try { chart?.dispose() } catch { /* ignore */ }
    chart = echarts.init(container.value)
    chart.setOption(buildOption(data.value))
  }

  function handleResize() {
    chart?.resize()
  }

  // 数据变化时重新渲染
  watch(data, render)

  // 窗口 resize 自适应
  onMounted(() => window.addEventListener('resize', handleResize))
  onUnmounted(() => {
    chart?.dispose()
    chart = null
    window.removeEventListener('resize', handleResize)
  })

  return { render, chart }
}
