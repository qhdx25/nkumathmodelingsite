<script setup lang="ts">
import { nextTick, onMounted, onUnmounted, ref } from 'vue'
import ElMessage from 'element-plus/es/components/message/index.mjs'
import ElMessageBox from 'element-plus/es/components/message-box/index.mjs'
import echarts from '@/utils/echarts'
import { adminApi, profileApi } from '@/api'
import type { ProfileOut, UserOut } from '@/types'
import { awardLevelLabels, label } from '@/utils/format'
import { useUserStore } from '@/stores/user'

interface AdminTeam {
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
}

const store = useUserStore()
const stats = ref<Record<string, number>>({})
const users = ref<UserOut[]>([])
const teams = ref<AdminTeam[]>([])
const recruitments = ref<{ id: number; title: string; status: string; team_id: number }[]>([])
const chartEl = ref<HTMLElement | null>(null)
const profileDialog = ref(false)
const selectedProfile = ref<ProfileOut | null>(null)
const loading = ref(false)
const exporting = ref(false)
let chart: ReturnType<typeof echarts.init> | null = null

const statsLabels: Record<string, string> = {
  users: '用户',
  teams: '团队',
  capabilities: '能力维度',
  recruitments: '招募',
  applications: '申请',
  messages: '消息',
  admin_logs: '管理日志',
}
const roleLabels: Record<string, string> = {
  student: '学生',
  leader: '队长',
}

async function load() {
  loading.value = true
  try {
    const [s, u, t, r] = await Promise.all([
      adminApi.stats(),
      adminApi.users(0, 100),
      adminApi.teams(),
      adminApi.recruitments(),
    ])
    stats.value = s
    users.value = u.items
    teams.value = t
    recruitments.value = r
    await nextTick()
    renderChart()
  } finally {
    loading.value = false
  }
}

function renderChart() {
  if (!chartEl.value) return
  if (!chart) chart = echarts.init(chartEl.value)
  const entries = Object.entries(stats.value).filter(([key]) => statsLabels[key])
  chart.setOption({
    animation: false,
    tooltip: { trigger: 'item' },
    legend: { bottom: 0 },
    series: [{
      type: 'pie',
      radius: ['40%', '68%'],
      center: ['50%', '45%'],
      data: entries.map(([key, value]) => ({
        name: statsLabels[key],
        value,
      })),
      label: { formatter: '{b}: {c}' },
    }],
  }, true)
  chart.resize()
}

async function openProfile(user: UserOut) {
  selectedProfile.value = await profileApi.user(user.id)
  profileDialog.value = true
}

async function downloadResume(profile: ProfileOut) {
  if (!profile.resume) return
  const blob = await profileApi.downloadResume(profile.user_id)
  const url = URL.createObjectURL(blob)
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = profile.resume.name
  anchor.click()
  window.setTimeout(() => URL.revokeObjectURL(url), 1000)
}

async function exportTable() {
  exporting.value = true
  try {
    const blob = await adminApi.exportTable()
    const url = URL.createObjectURL(blob)
    const anchor = document.createElement('a')
    const date = new Date().toISOString().slice(0, 10)
    anchor.href = url
    anchor.download = `MathTeam组队与能力信息_${date}.csv`
    anchor.click()
    window.setTimeout(() => URL.revokeObjectURL(url), 1000)
    ElMessage.success('表格已导出')
  } finally {
    exporting.value = false
  }
}

async function toggleStatus(user: UserOut) {
  const next = user.status === 'active' ? 'disabled' : 'active'
  await adminApi.setUserStatus(user.id, next)
  ElMessage.success(`账号已${next === 'active' ? '启用' : '停用'}`)
  await load()
}

async function toggleAdmin(user: UserOut) {
  const enable = !user.is_admin
  await ElMessageBox.confirm(
    enable
      ? `确认将 ${user.username} 设为管理员？`
      : `确认取消 ${user.username} 的管理员身份？`,
    '身份变更',
    { type: 'warning' },
  )
  await adminApi.setAdmin(user.id, enable)
  ElMessage.success('身份已更新')
  await load()
}

async function remove(id: number) {
  await ElMessageBox.confirm('确认下架这条招募信息？', '提示', {
    type: 'warning',
  })
  await adminApi.removeRecruitment(id)
  ElMessage.success('已删除')
  await load()
}

function resizeChart() {
  chart?.resize()
}

onMounted(() => {
  load()
  window.addEventListener('resize', resizeChart)
})
onUnmounted(() => {
  window.removeEventListener('resize', resizeChart)
  chart?.dispose()
  chart = null
})
</script>

<template>
  <div class="page" v-loading="loading">
    <div class="flex-between">
      <div>
        <h1 class="page-title">后台管理</h1>
        <p class="page-desc">
          用户、团队、招募管理与运营数据统计
        </p>
      </div>
      <el-button type="primary" :loading="exporting" @click="exportTable">
        一键导出表格
      </el-button>
    </div>

    <div class="grid grid-two">
      <el-card>
        <template #header>运营数据概览</template>
        <div class="stats">
          <div v-for="(value, key) in stats" :key="key" class="stat">
            <div class="stat-value">{{ value }}</div>
            <div class="muted">{{ statsLabels[key] || key }}</div>
          </div>
        </div>
      </el-card>
      <el-card>
        <template #header>数据占比</template>
        <div ref="chartEl" class="chart-box" />
      </el-card>
    </div>

    <el-card class="mt-16 admin-users-card">
      <template #header>
        <div class="section-head">
          <div>
            <div class="section-kicker">USER DIRECTORY</div>
            <div class="section-title">用户、能力与奖项</div>
            <div class="section-desc">点击“画像”查看用户能力、经历、奖项与简历</div>
          </div>
          <div class="section-count">{{ users.length }} 位用户</div>
        </div>
      </template>

      <div class="admin-table-wrap">
        <el-table
          :data="users"
          row-key="id"
          size="small"
          class="admin-users-table"
        >
          <el-table-column prop="id" label="ID" width="62" />
          <el-table-column label="用户" min-width="165">
            <template #default="{ row }">
              <div class="user-cell">
                <el-avatar :size="34" class="user-avatar">
                  {{ (row.real_name || row.username).slice(0, 1) }}
                </el-avatar>
                <div class="user-copy">
                  <strong>{{ row.real_name || '未填写姓名' }}</strong>
                  <span>@{{ row.username }}</span>
                </div>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="学号" width="118">
            <template #default="{ row }">
              <span :class="{ muted: !row.student_number }">
                {{ row.student_number || '未填写' }}
              </span>
            </template>
          </el-table-column>
          <el-table-column label="学院 / 学校" min-width="190">
            <template #default="{ row }">
              <div class="cell-stack">
                <strong>{{ row.college || '未填写学院' }}</strong>
                <span>{{ row.school || '未填写学校' }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="联系方式" min-width="190">
            <template #default="{ row }">
              <div class="cell-stack">
                <strong>{{ row.phone || '未填写电话' }}</strong>
                <span>{{ row.email }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="身份" width="122">
            <template #default="{ row }">
              <div class="role-tags">
                <el-tag size="small" type="info">
                  {{ roleLabels[row.role] || row.role }}
                </el-tag>
                <el-tag v-if="row.is_admin" size="small" type="warning">
                  管理员
                </el-tag>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="82">
            <template #default="{ row }">
              <el-tag :type="row.status === 'active' ? 'success' : 'danger'" size="small">
                {{ row.status === 'active' ? '正常' : '停用' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="226">
            <template #default="{ row }">
              <div class="row-actions">
                <el-button link type="primary" @click="openProfile(row)">
                  画像
                </el-button>
                <el-button
                  v-if="row.id !== store.user?.id"
                  link
                  :type="row.status === 'active' ? 'danger' : 'success'"
                  @click="toggleStatus(row)"
                >
                  {{ row.status === 'active' ? '停用' : '启用' }}
                </el-button>
                <el-button
                  v-if="row.id !== store.user?.id"
                  link
                  type="warning"
                  @click="toggleAdmin(row)"
                >
                  {{ row.is_admin ? '取消管理员' : '设为管理员' }}
                </el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>

    <div class="grid grid-two mt-16">
      <el-card>
        <template #header>当前组队情况与评分</template>
        <el-table :data="teams" size="small">
          <el-table-column prop="name" label="团队" min-width="140" />
          <el-table-column label="队长 / 学校" min-width="150">
            <template #default="{ row }">
              <div>{{ row.creator_name }}</div>
              <div class="muted">{{ row.school || '未填写' }}</div>
            </template>
          </el-table-column>
          <el-table-column label="人数" width="80">
            <template #default="{ row }">{{ row.member_count }}/{{ row.max_size }}</template>
          </el-table-column>
          <el-table-column label="状态" width="95">
            <template #default="{ row }">{{ label(row.status) }}</template>
          </el-table-column>
          <el-table-column label="综合评分" width="105">
            <template #default="{ row }">
              <strong class="score">{{ row.composite_score }}</strong>
              <span class="muted"> {{ row.score_grade }}</span>
            </template>
          </el-table-column>
        </el-table>
      </el-card>

      <el-card>
        <template #header>招募管理</template>
        <el-table :data="recruitments" size="small">
          <el-table-column prop="id" label="ID" width="60" />
          <el-table-column prop="title" label="标题" />
          <el-table-column label="状态" width="90">
            <template #default="{ row }">{{ label(row.status) }}</template>
          </el-table-column>
          <el-table-column label="操作" width="80">
            <template #default="{ row }">
              <el-button link type="danger" @click="remove(row.id)">下架</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>

    <el-dialog v-model="profileDialog" title="用户画像详情" width="820px">
      <template v-if="selectedProfile">
        <div class="profile-summary">
          <div>
            <h3>{{ selectedProfile.real_name || selectedProfile.username }}</h3>
            <p class="muted">
              {{ roleLabels[selectedProfile.role] }} ·
              {{ selectedProfile.is_admin ? '管理员 · ' : '' }}
              {{ selectedProfile.student_number || '未填写学号' }} ·
              {{ selectedProfile.college || '未填写学院' }}
            </p>
          </div>
          <el-button
            v-if="selectedProfile.resume"
            type="primary"
            plain
            @click="downloadResume(selectedProfile)"
          >
            下载简历
          </el-button>
          <span v-else class="muted">未上传简历</span>
        </div>

        <div class="profile-grid">
          <div><span>学校</span><strong>{{ selectedProfile.school || '—' }}</strong></div>
          <div><span>电话</span><strong>{{ selectedProfile.phone || '—' }}</strong></div>
          <div><span>邮箱</span><strong>{{ selectedProfile.email }}</strong></div>
          <div><span>QQ</span><strong>{{ selectedProfile.qq || '—' }}</strong></div>
          <div><span>微信</span><strong>{{ selectedProfile.wechat || '—' }}</strong></div>
          <div><span>GitHub</span><strong>{{ selectedProfile.github || '—' }}</strong></div>
        </div>

        <h4>能力图谱</h4>
        <div class="skill-list">
          <el-tag
            v-for="skill in selectedProfile.skills"
            :key="skill.capability_id"
            type="primary"
            effect="dark"
          >
            {{ skill.name }} · {{ skill.level }}/5
          </el-tag>
          <span v-if="!selectedProfile.skills.length" class="muted">暂无能力数据</span>
        </div>

        <div class="grid grid-two mt-16">
          <div>
            <h4>项目经历</h4>
            <el-timeline v-if="selectedProfile.projects.length">
              <el-timeline-item
                v-for="(item, index) in selectedProfile.projects"
                :key="index"
                :timestamp="item.start_date || ''"
              >
                <strong>{{ item.title }}</strong> · {{ item.role }}
                <div class="muted">{{ item.description }}</div>
              </el-timeline-item>
            </el-timeline>
            <span v-else class="muted">暂无项目经历</span>
          </div>
          <div>
            <h4>竞赛与奖项</h4>
            <el-timeline v-if="selectedProfile.competitions.length">
              <el-timeline-item
                v-for="(item, index) in selectedProfile.competitions"
                :key="index"
                :timestamp="item.start_date || ''"
              >
                <strong>{{ item.title }}</strong> · {{ item.role }}
                <el-tag
                  v-if="item.award_level"
                  size="small"
                  type="warning"
                  effect="plain"
                  class="award-tag"
                >
                  {{ awardLevelLabels[item.award_level] }}
                </el-tag>
                <div class="muted">{{ item.description }}</div>
              </el-timeline-item>
            </el-timeline>
            <span v-else class="muted">暂无奖项经历</span>
          </div>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(110px, 1fr));
  gap: 12px;
}
.admin-users-card :deep(.el-card__body) { padding: 0; }
.section-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
}
.section-kicker {
  margin-bottom: 3px;
  color: var(--mt-primary-light);
  font-size: 10px;
  font-weight: 700;
  letter-spacing: .16em;
}
.section-title {
  color: var(--mt-primary);
  font-size: 17px;
  font-weight: 700;
}
.section-desc {
  margin-top: 4px;
  color: var(--mt-muted);
  font-size: 12px;
  font-weight: 400;
}
.section-count {
  flex: none;
  padding: 6px 12px;
  color: var(--mt-primary);
  font-size: 12px;
  font-weight: 700;
  background: rgba(113, 10, 83, .06);
  border: 1px solid rgba(113, 10, 83, .1);
  border-radius: 999px;
}
.admin-table-wrap { overflow-x: auto; }
.admin-users-table { min-width: 1050px; }
.admin-users-table :deep(.el-table__cell) {
  padding: 10px 0;
  vertical-align: middle;
}
.admin-users-table :deep(th.el-table__cell) {
  height: 44px;
  color: var(--mt-primary);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: .04em;
}
.user-cell {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}
.user-avatar {
  flex: none;
  color: #fff;
  font-weight: 700;
  background: linear-gradient(135deg, var(--mt-primary), var(--mt-accent));
  box-shadow: 0 6px 14px rgba(113, 10, 83, .18);
}
.user-copy,
.cell-stack {
  display: flex;
  min-width: 0;
  flex-direction: column;
  gap: 2px;
}
.user-copy strong,
.cell-stack strong {
  overflow: hidden;
  color: var(--mt-text);
  font-size: 13px;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.user-copy span,
.cell-stack span {
  overflow: hidden;
  color: var(--mt-muted);
  font-size: 11px;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.row-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  white-space: nowrap;
}
.row-actions :deep(.el-button) {
  height: 28px;
  margin-left: 0;
  padding: 0 4px;
  font-size: 12px;
}
.stat {
  padding: 14px 8px;
  text-align: center;
  background: #f8fafc;
  border-radius: 8px;
}
.stat-value {
  color: #4f46e5;
  font-size: 24px;
  font-weight: 700;
}
.role-tags { display: flex; gap: 4px; flex-wrap: nowrap; }
.score { color: #4f46e5; font-size: 16px; }
.profile-summary {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  padding: 14px;
  background: linear-gradient(135deg, #eef2ff, #faf5ff);
  border-radius: 12px;
}
.profile-summary h3 { margin: 0; }
.profile-summary p { margin: 5px 0 0; }
.profile-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
  margin-top: 14px;
}
.profile-grid div {
  display: flex;
  flex-direction: column;
  gap: 3px;
  padding: 8px 10px;
  background: #f8fafc;
  border-radius: 8px;
}
.profile-grid span { color: #64748b; font-size: 12px; }
.skill-list { display: flex; flex-wrap: wrap; gap: 8px; }
.award-tag { margin-left: 8px; }
@media (max-width: 760px) {
  .section-head { align-items: flex-start; }
  .section-count { margin-top: 2px; }
}
</style>
