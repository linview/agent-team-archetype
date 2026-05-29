# 前端框架模式对比

TDFIR 方法论框架无关。本文件提供主流框架的模式映射，帮助跨项目复用。

## 核心概念映射

| 概念 | Vue 3 (Composition API) | React (Hooks) | Svelte | Angular |
|------|------------------------|---------------|--------|---------|
| 组件定义 | `<script setup lang="ts">` | `function Comp() {}` | `<script lang="ts">` | `@Component({})` |
| 响应式状态 | `ref()` / `reactive()` | `useState()` | `$:` / `let` | `signal()` / RxJS |
| 计算属性 | `computed()` | `useMemo()` | `$:` | `computed()` |
| 副作用 | `watch()` / `watchEffect()` | `useEffect()` | `$:` / `onMount()` | `ngOnInit` / RxJS |
| 生命周期 | `onMounted()` / `onUnmounted()` | `useEffect(() => {}, [])` | `onMount()` / `onDestroy()` | `ngOnInit` / `ngOnDestroy` |
| 模板引用 | `ref<HTMLDivElement>()` | `useRef<HTMLDivElement>()` | `bind:this` | `@ViewChild()` |
| 条件渲染 | `v-if` / `v-show` | `{cond && <Comp/>}` | `{#if cond}` | `*ngIf` |
| 列表渲染 | `v-for` | `.map()` | `{#each}` | `*ngFor` |
| 表单绑定 | `v-model` | `onChange` + `value` | `bind:value` | `[(ngModel)]` |
| 依赖注入 | `provide` / `inject` | Context API | `setContext` / `getContext` | DI + `@Injectable` |
| 全局状态 | Pinia | Zustand / Jotai / Redux | Svelte stores | NgRx / Signals |
| 路由 | Vue Router | React Router | SvelteKit | Angular Router |

## API 调用模式

### Vue 3

```typescript
const loading = ref(false)
const data = ref<Item[]>([])

async function fetchData() {
  loading.value = true
  try {
    const resp = await api.getItems({ page_size: 100 })
    if (resp.data.code === 0) {
      data.value = resp.data.data.items
    }
  } finally {
    loading.value = false
  }
}

onMounted(fetchData)
```

### React

```typescript
const [loading, setLoading] = useState(false)
const [data, setData] = useState<Item[]>([])

useEffect(() => {
  let cancelled = false
  setLoading(true)
  api.getItems({ page_size: 100 }).then(resp => {
    if (!cancelled && resp.data.code === 0) {
      setData(resp.data.data.items)
    }
  }).finally(() => setLoading(false))
  return () => { cancelled = true }
}, [])
```

### Svelte

```typescript
let loading = false
let data: Item[] = []

onMount(async () => {
  loading = true
  try {
    const resp = await api.getItems({ page_size: 100 })
    if (resp.data.code === 0) {
      data = resp.data.data.items
    }
  } finally {
    loading = false
  }
})
```

## ECharts 生命周期管理

所有框架共享同一原则：**条件渲染销毁 DOM 时，必须 dispose 旧实例再 re-init。**

### Vue 3 — 使用 composable

见 [scripts/vue_echarts_composable.ts](../scripts/vue_echarts_composable.ts)

### React — 使用 custom hook

```typescript
function useECharts(data: ChartData | null) {
  const containerRef = useRef<HTMLDivElement>(null)
  const chartRef = useRef<ECharts | null>(null)

  useEffect(() => {
    if (!containerRef.current || !data) return
    chartRef.current?.dispose()
    const chart = echarts.init(containerRef.current)
    chartRef.current = chart
    chart.setOption(buildOption(data))
    return () => { chart.dispose() }
  }, [data])

  useEffect(() => {
    const onResize = () => chartRef.current?.resize()
    window.addEventListener('resize', onResize)
    return () => window.removeEventListener('resize', onResize)
  }, [])

  return containerRef
}
```

### Svelte — 使用 action

```typescript
function echartsAction(node: HTMLDivElement, data: ChartData | null) {
  let chart: ECharts | null = null
  const onResize = () => chart?.resize()

  if (data) {
    chart = echarts.init(node)
    chart.setOption(buildOption(data))
    window.addEventListener('resize', onResize)
  }

  return {
    update(newData: ChartData | null) {
      chart?.dispose()
      if (newData) {
        chart = echarts.init(node)
        chart.setOption(buildOption(newData))
      }
    },
    destroy() {
      chart?.dispose()
      window.removeEventListener('resize', onResize)
    }
  }
}
```

## 远程搜索模式

下拉选择器 + 服务端搜索是常见 UED 模式，各框架实现：

### Vue 3 (Element Plus)

```html
<el-select
  v-model="selected"
  filterable
  remote
  :remote-method="searchItems"
  :loading="loading"
>
  <el-option v-for="item in options" :key="item.id" :label="item.label" :value="item.id" />
</el-select>
```

### React (Ant Design)

```tsx
<Select
  value={selected}
  showSearch
  onSearch={searchItems}
  loading={loading}
  filterOption={false}
>
  {options.map(item => <Option key={item.id} value={item.id}>{item.label}</Option>)}
</Select>
```

### Svelte (自定义)

```html
<select bind:value={selected} on:input={handleSearch}>
  {#each options as item}
    <option value={item.id}>{item.label}</option>
  {/each}
</select>
```
