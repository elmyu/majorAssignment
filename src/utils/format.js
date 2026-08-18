// ==================== 通用工具 ====================
// 各组件重复出现的日期 / 金额格式化、ID 生成逻辑统一收口于此。

/** 生成带前缀的唯一 ID */
export function genId(prefix) {
  return `${prefix}_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`
}

/** 将 ISO 时间字符串格式化为 "YYYY-MM-DD HH:mm" */
export function fmtDate(iso) {
  const d = new Date(iso)
  const pad = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

/** 金额千分位格式化，保留两位小数 */
export function fmtPrice(p) {
  return Number(p || 0).toLocaleString('zh-CN', { minimumFractionDigits: 2 })
}

