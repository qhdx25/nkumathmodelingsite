/** 通用格式化工具 */

export function formatDate(value?: string | null): string {
  if (!value) return '—'
  // 后端返回 UTC ISO 字符串，toLocaleString 会按浏览器本地时区展示
  return new Date(value).toLocaleString('zh-CN', {
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit',
  })
}

export const categoryLabels: Record<string, string> = {
  foundation: '数学理论',
  implementation: '编程实现',
  analysis: '数据分析',
  modeling: '建模分析',
  writing: '论文写作',
  collaboration: '竞赛协作',
}

export const statusLabels: Record<string, string> = {
  forming: '组建中',
  recruiting: '招募中',
  active: '组队完成',
  archived: '已归档',
  open: '开放招募',
  closed: '已关闭',
  pending: '待处理',
  accepted: '已通过',
  rejected: '已拒绝',
}

export const awardLevelLabels: Record<string, string> = {
  international: '国际级奖项',
  national: '国家级奖项',
  provincial: '省级/赛区奖项',
  school: '校级奖项',
  participation: '参赛经历',
  other: '其他奖项',
}

export function label(key: string): string {
  return statusLabels[key] || categoryLabels[key] || awardLevelLabels[key] || key
}
