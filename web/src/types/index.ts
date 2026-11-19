/**
 * 与后端 Pydantic Schema 一一对应的 TypeScript 类型。
 * 前后端共享同一份“数据形状”的约定：
 *   - 后端用 Pydantic 校验入参、过滤出参
 *   - 前端用这些类型获得 IDE 自动补全与编译期检查
 */

// ---------- 用户与认证 ----------
export type UserRole = 'student' | 'leader' | 'school_admin' | 'platform_admin'
export type UserStatus = 'active' | 'disabled'

export interface UserOut {
  id: number
  username: string
  email: string
  real_name: string | null
  school: string | null
  role: UserRole
  status: UserStatus
  created_at: string
}

export interface Token {
  access_token: string
  token_type: string
}

// ---------- 能力维度 ----------
export type CapabilityCategory =
  | 'foundation'
  | 'implementation'
  | 'analysis'
  | 'modeling'
  | 'writing'
  | 'collaboration'

export interface Capability {
  id: number
  name: string
  category: CapabilityCategory
  weight: number
  description: string | null
}

// ---------- 个人画像 ----------
export interface SkillView {
  capability_id: number
  name: string
  category: string
  level: number
  weight: number
}

export interface ProjectExperience {
  title: string
  role: string
  description?: string | null
  start_date?: string | null
  end_date?: string | null
}

export interface Preference {
  preferred_roles: string[]
  avoid_roles: string[]
  preferred_track: string | null
  weekly_hours: number
}

export interface ProfileOut {
  user_id: number
  username: string
  real_name: string | null
  school: string | null
  skills: SkillView[]
  projects: ProjectExperience[]
  competitions: ProjectExperience[]
  preference: Preference
}

export interface ProfileUpdate {
  skills?: { capability_id: number; level: number }[]
  projects?: ProjectExperience[]
  competitions?: ProjectExperience[]
  preference?: Preference
}

// ---------- 团队 ----------
export type TeamStatus = 'forming' | 'recruiting' | 'active' | 'archived'

export interface TeamOut {
  id: number
  name: string
  description: string | null
  competition_track: string
  max_size: number
  status: TeamStatus
  created_by: number
  created_at: string
  member_count: number
}

export interface TeamMemberOut {
  user_id: number
  username: string
  role: 'leader' | 'member'
  joined_at: string
}

export interface TeamDetail extends TeamOut {
  members: TeamMemberOut[]
}

export interface TeamProfileOut {
  team_id: number
  team_name: string
  member_count: number
  coverage: Record<string, { members: number; avg_level: number }>
  gaps: string[]
  weak: string[]
}

// ---------- 招募 ----------
export interface RecruitmentOut {
  id: number
  team_id: number
  title: string
  competition_track: string
  target_size: number
  required_roles: string[]
  required_skills: string[]
  description: string | null
  status: 'open' | 'closed'
  created_at: string
  current_members: number
}

export interface TeamCard {
  id: number
  team_id: number
  title: string
  competition_track: string
  target_size: number
  required_skills: string[]
  current_members: number
  team_name: string
  team_status: string
}

export interface Page<T> {
  items: T[]
  total: number
  skip: number
  limit: number
}

// ---------- 申请 ----------
export type ApplicationStatus = 'pending' | 'accepted' | 'rejected'

export interface ApplicationOut {
  id: number
  recruitment_id: number
  team_id: number
  applicant_id: number
  status: ApplicationStatus
  message: string | null
  review_note: string | null
  created_at: string
  reviewed_at: string | null
}

export interface ApplicationWithApplicant extends ApplicationOut {
  applicant: { id: number; username: string; real_name: string | null; school: string | null } | null
  skills: { name: string; level: number }[]
}

// ---------- 推荐 ----------
export interface DimensionScore {
  score: number
  weight: number
  reason: string
}

export interface RecommendationItem {
  target_type: 'recruitment' | 'user'
  target_id: number
  title: string
  team_id: number | null
  score: number
  breakdown: Record<'skill_match' | 'complement' | 'experience' | 'role_fit' | 'time_fit' | 'preference_fit', DimensionScore>
  strengths: string[]
  gaps: string[]
}

export interface RecommendationOut {
  id: number
  user_id: number
  target_type: string
  target_id: number
  score: number
  breakdown: Record<string, unknown>
  strengths: string[]
  gaps: string[]
  algorithm_version: string
  created_at: string
}

// ---------- 消息与通知 ----------
export interface MessageOut {
  id: number
  team_id: number
  sender_id: number
  sender_name: string
  content: string
  message_type: 'text' | 'system' | 'resource'
  created_at: string
}

export interface NotificationOut {
  id: number
  user_id: number
  title: string
  content: string | null
  is_read: boolean
  created_at: string
}
