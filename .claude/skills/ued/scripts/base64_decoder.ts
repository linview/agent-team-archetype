/**
 * UTF-8 Base64 解码工具
 *
 * 问题：atob() 返回 Latin-1 字符串，中文等多字节 UTF-8 会乱码
 * 解法：atob() → Uint8Array → TextDecoder
 */

/** 解码 Base64 编码的 UTF-8 字符串 */
export function decodeBase64UTF8(base64: string): string {
  const bytes = Uint8Array.from(atob(base64), c => c.charCodeAt(0))
  return new TextDecoder().decode(bytes)
}

/** 解码 Base64 编码的 JSON 对象 */
export function decodeBase64JSON<T = Record<string, unknown>>(base64: string): T {
  return JSON.parse(decodeBase64UTF8(base64))
}

/** 从 Base64 JSON 中提取指定字段 */
export function extractFromBase64JSON(
  base64: string,
  field: string,
  fallback: string = '—'
): string {
  try {
    const json = decodeBase64JSON(base64)
    const value = json[field]
    return typeof value === 'string' ? value : fallback
  } catch {
    return fallback
  }
}
