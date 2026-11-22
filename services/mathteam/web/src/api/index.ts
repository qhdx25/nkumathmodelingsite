/**
 * Axios 客户端封装。
 *
 * 为什么集中封装？
 * 1. 统一 baseURL：后端所有接口都在 /api/v1 下
 * 2. 统一注入 JWT：每个需要登录的请求都要带 Authorization 头
 * 3. 统一错误处理：后端失败响应是 {code, message, data}，抽出 message 直接提示用户
 *
 * 一个常见的 TypeScript 坑：响应拦截器 return response.data 后，运行时的确直接拿到数据，
 * 但类型系统仍认为返回的是 AxiosResponse<T>。这里用 ApiClient 接口重新声明返回值为 Promise<T>，
 * 让调用方的类型提示与运行时行为一致。
 */
import axios, {
  type AxiosError,
  type AxiosInstance,
  type AxiosRequestConfig,
  type InternalAxiosRequestConfig,
} from 'axios'
import ElMessage from 'element-plus/es/components/message/index.mjs'
import type {
  ApplicationOut,
  ApplicationWithApplicant,
  Capability,
  ChatPolicy,
  MessageOut,
  NotificationOut,
  Page,
  ProfileOut,
  ProfileUpdate,
  RecommendationItem,
  RecommendationOut,
  RecruitmentOut,
  ResumeOut,
  TeamCard,
  TeamDetail,
  TeamOut,
  TeamProfileOut,
  Token,
  UserOut,
} from '@/types'

const TOKEN_KEY = 'mathteam_token'

/** 拦截器改写后的真实返回类型 */
interface ApiClient extends Pick<AxiosInstance, 'interceptors'> {
  get<T>(url: string, config?: AxiosRequestConfig): Promise<T>
  post<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T>
  patch<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T>
  delete<T>(url: string, config?: AxiosRequestConfig): Promise<T>
}

const rawHttp = axios.create({
  // Vite 开发服务器把 /api 转发到 FastAPI；生产由 Nginx 同域转发
  baseURL: import.meta.env.VITE_API_BASE || '/api/v1',
  timeout: 15000,
})

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token)
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY)
}

// 请求拦截器：每次发请求前自动带上 Bearer Token
rawHttp.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = getToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器：成功时直接返回 data，失败时统一提示
rawHttp.interceptors.response.use(
  (response) => response.data,
  (error: AxiosError<{ message?: string; detail?: string }>) => {
    const status = error.response?.status
    const message =
      error.response?.data?.message ||
      error.response?.data?.detail ||
      (status === 401 ? '登录已过期，请重新登录' : '请求失败，请稍后重试')

    if (status === 401) {
      clearToken()
      // 避免在登录页本身弹出“登录已过期”
      if (!location.pathname.startsWith('/login')) {
        ElMessage.warning(message)
        setTimeout(() => location.href = '/login', 800)
      }
    } else {
      ElMessage.error(message)
    }
    return Promise.reject(error)
  },
)

// 对外暴露重新声明过返回类型的客户端
export const http = rawHttp as unknown as ApiClient

// ---------- 认证 ----------
export const authApi = {
  login: (username: string, password: string) =>
    // OAuth2PasswordRequestForm 要求表单格式，Axios 用 URLSearchParams 自动设置正确的 Content-Type
    http.post<Token>('/auth/login', new URLSearchParams({ username, password })),
  register: (data: {
    username: string
    email: string
    password: string
    real_name?: string
    school?: string
  }) => http.post<UserOut>('/auth/register', data),
  me: () => http.get<UserOut>('/auth/me'),
}

// ---------- 能力维度 ----------
export const capabilityApi = {
  list: (category?: string) =>
    http.get<Capability[]>('/capabilities', { params: category ? { category } : {} }),
  create: (data: Omit<Capability, 'id'>) => http.post<Capability>('/capabilities', data),
}

// ---------- 个人画像 ----------
export const profileApi = {
  mine: () => http.get<ProfileOut>('/profile/me'),
  update: (data: ProfileUpdate) => http.patch<ProfileOut>('/profile/me', data),
  user: (id: number) => http.get<ProfileOut>(`/profile/users/${id}`),
  uploadResume: (file: File) => {
    const form = new FormData()
    form.append('file', file)
    return http.post<ResumeOut>('/profile/me/resume', form, {
      timeout: 120000,
    })
  },
  deleteResume: () => http.delete<{ message: string }>('/profile/me/resume'),
  downloadResume: (userId: number) =>
    http.get<Blob>(`/profile/users/${userId}/resume`, {
      responseType: 'blob',
      timeout: 120000,
    }),
}

// ---------- 团队 ----------
export const teamApi = {
  mine: () => http.get<TeamOut[]>('/teams/mine'),
  create: (data: {
    name: string
    description?: string
    competition_track: string
    max_size: number
  }) => http.post<TeamOut>('/teams', data),
  detail: (id: number) => http.get<TeamDetail>(`/teams/${id}`),
  profile: (id: number) => http.get<TeamProfileOut>(`/teams/${id}/profile`),
  addMember: (teamId: number, userId: number) =>
    http.post<TeamDetail>(`/teams/${teamId}/members/${userId}`),
}

// ---------- 招募 ----------
export const recruitmentApi = {
  cards: (skip = 0, limit = 20, track?: string, skill?: string) =>
    http.get<Page<TeamCard>>('/recruitments/cards', {
      params: { skip, limit, ...(track ? { track } : {}), ...(skill ? { skill } : {}) },
    }),
  list: (skip = 0, limit = 20, track?: string, skill?: string) =>
    http.get<Page<RecruitmentOut>>('/recruitments', {
      params: { skip, limit, ...(track ? { track } : {}), ...(skill ? { skill } : {}) },
    }),
  detail: (id: number) => http.get<RecruitmentOut>(`/recruitments/${id}`),
  create: (teamId: number, data: unknown) =>
    http.post<RecruitmentOut>(`/recruitments/teams/${teamId}`, data),
  update: (id: number, data: unknown) =>
    http.patch<RecruitmentOut>(`/recruitments/${id}`, data),
  close: (id: number) => http.post<RecruitmentOut>(`/recruitments/${id}/close`),
}

// ---------- 申请 ----------
export const applicationApi = {
  apply: (recruitmentId: number, message?: string) =>
    http.post<ApplicationOut>(`/applications/recruitments/${recruitmentId}`, { message }),
  mine: () => http.get<ApplicationOut[]>('/applications/mine'),
  team: (teamId: number) =>
    http.get<ApplicationWithApplicant[]>(`/applications/teams/${teamId}`),
  review: (id: number, decision: 'accept' | 'reject', review_note?: string) =>
    http.post<ApplicationOut>(`/applications/${id}/review`, { decision, review_note }),
}

// ---------- 推荐 ----------
export const recommendationApi = {
  teams: (topK = 10) => http.get<RecommendationItem[]>('/recommendations/teams', { params: { top_k: topK } }),
  members: (teamId: number, topK = 10) =>
    http.get<RecommendationItem[]>('/recommendations/members', { params: { team_id: teamId, top_k: topK } }),
  history: () => http.get<RecommendationOut[]>('/recommendations/history'),
}

// ---------- 消息 ----------
export const messageApi = {
  history: (teamId: number, skip = 0, limit = 50) =>
    http.get<MessageOut[]>(`/messages/teams/${teamId}`, { params: { skip, limit } }),
  notifications: () => http.get<NotificationOut[]>('/messages/notifications'),
  policy: () => http.get<ChatPolicy>('/messages/chat-policy'),
  uploadAttachment: (teamId: number, file: File, content = '') => {
    const form = new FormData()
    form.append('file', file)
    if (content) form.append('content', content)
    return http.post<MessageOut>(
      `/messages/teams/${teamId}/attachments`,
      form,
      { timeout: 120000 },
    )
  },
  attachmentBlob: (messageId: number) =>
    http.get<Blob>(`/messages/attachments/${messageId}/download`, {
      responseType: 'blob',
      timeout: 120000,
    }),
}

// ---------- 后台 ----------
export const adminApi = {
  users: (skip = 0, limit = 20) => http.get<Page<UserOut>>('/admin/users', { params: { skip, limit } }),
  teams: () => http.get<{
    id: number
    name: string
    status: string
    max_size: number
    member_count: number
    competition_track: string
    creator_name: string
    school: string | null
    composite_score: number
    score_grade: string
  }[]>('/admin/teams'),
  recruitments: () =>
    http.get<{ id: number; title: string; status: string; team_id: number }[]>('/admin/recruitments'),
  stats: () => http.get<Record<string, number>>('/admin/stats'),
  setUserStatus: (id: number, status: 'active' | 'disabled') =>
    http.patch<UserOut>(`/admin/users/${id}/status`, undefined, { params: { status } }),
  removeRecruitment: (id: number) => http.delete(`/admin/recruitments/${id}`),
  setAssociationAdmin: (id: number, enable: boolean) =>
    http.patch<UserOut>(`/admin/users/${id}/association-admin`, undefined, {
      params: { enable },
    }),
  exportTable: () => http.get<Blob>('/admin/export', {
    responseType: 'blob',
    timeout: 120000,
  }),
}
