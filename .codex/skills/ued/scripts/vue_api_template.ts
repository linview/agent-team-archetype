/**
 * Vue 3 Composition API 调用模板
 *
 * 使用方式：复制到项目，替换 API 函数和类型
 */
import { ref, onMounted } from 'vue'
import type { Ref } from 'vue'

interface UseFetchOptions<T> {
  /** API 调用函数 */
  fetcher: () => Promise<{ data: { code: number; data: { items: T[] } } }>
  /** 是否在 mount 时自动调用 */
  immediate?: boolean
}

interface UseFetchReturn<T> {
  data: Ref<T[]>
  loading: Ref<boolean>
  error: Ref<string | null>
  refetch: () => Promise<void>
}

export function useFetch<T>(options: UseFetchOptions<T>): UseFetchReturn<T> {
  const data = ref<T[]>([]) as Ref<T[]>
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function refetch() {
    loading.value = true
    error.value = null
    try {
      const resp = await options.fetcher()
      if (resp.data.code === 0) {
        data.value = resp.data.data.items
      } else {
        error.value = `API error: code=${resp.data.code}`
      }
    } catch (e) {
      error.value = e instanceof Error ? e.message : String(e)
    } finally {
      loading.value = false
    }
  }

  if (options.immediate !== false) {
    onMounted(refetch)
  }

  return { data, loading, error, refetch }
}
