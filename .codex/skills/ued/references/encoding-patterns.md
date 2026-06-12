# 编码与序列化常见问题

前端处理非 ASCII 数据时的常见陷阱和解法。

## Base64 UTF-8 解码

### 问题

`atob()` 将 Base64 解码为 Latin-1 二进制字符串（每个 char 占 1 字节）。但 UTF-8 中文是多字节编码（每字 3 字节），`atob()` 会把 UTF-8 字节序列拆散，产生乱码。

### 解法

先用 `atob()` 得到原始字节，再用 `TextDecoder` 正确解码 UTF-8：

```typescript
// 正确方式
function decodeBase64UTF8(base64: string): string {
  const bytes = Uint8Array.from(atob(base64), c => c.charCodeAt(0))
  return new TextDecoder().decode(bytes)
}

// 错误方式 — 中文会乱码
function wrongDecode(base64: string): string {
  return atob(base64) // Latin-1，非 UTF-8
}
```

### 完整示例：解码飞书任务 meta_data

```typescript
function decodeWorkItemTitle(metaData: string): string {
  try {
    const bytes = Uint8Array.from(atob(metaData), c => c.charCodeAt(0))
    const json = JSON.parse(new TextDecoder().decode(bytes))
    const desc = (json.description || '').replace(/\n/g, ' ').trim()
    return desc ? desc.slice(0, 40) : '—'
  } catch {
    return '—'
  }
}
```

## JSON 嵌套处理

后端返回的 JSON 可能有嵌套结构，前端需要展平或提取：

```typescript
// 后端返回
interface APIResponse<T> {
  code: number
  message: string
  data: {
    items: T[]
    pagination: { total: number; page_size: number; page_num: number }
  }
  warnings?: string[]
}

// 安全提取
function extractItems<T>(resp: APIResponse<T>): T[] {
  return resp.data?.items ?? []
}
```

## 时间格式处理

后端返回的时间字符串格式不统一时的处理：

```typescript
// ISO 8601 → 相对时间
function formatRelativeTime(isoStr: string): string {
  const date = new Date(isoStr)
  const diff = Date.now() - date.getTime()
  const minutes = Math.floor(diff / 60000)
  if (minutes < 60) return `${minutes} 分钟前`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours} 小时前`
  const days = Math.floor(hours / 24)
  return `${days} 天前`
}
```

## null vs 空数组

后端 Go 的 `nil slice` 序列化为 JSON `null`，而非 `[]`。前端需要防御：

```typescript
// 防御性处理
const items = response.data?.items ?? []
// 或者后端确保：if slice == nil { slice = []T{} }
```
