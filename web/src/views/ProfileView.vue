<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref } from 'vue'
import ElMessage from 'element-plus/es/components/message/index.mjs'
import ElMessageBox from 'element-plus/es/components/message-box/index.mjs'
import echarts from '@/utils/echarts'
import { capabilityApi, profileApi } from '@/api'
import type { Capability, ProfileOut, ProfileUpdate } from '@/types'
import { awardLevelLabels, categoryLabels } from '@/utils/format'
import { useUserStore } from '@/stores/user'

const store = useUserStore()
const profile = ref<ProfileOut | null>(null)
const capabilities = ref<Capability[]>([])
const chartEl = ref<HTMLElement | null>(null)
let chart: ReturnType<typeof echarts.init> | null = null

// 编辑弹窗的表单数据
const dialogVisible = ref(false)
const draft = ref<ProfileUpdate>({})
const saving = ref(false)
const uploadingResume = ref(false)
const resumeInput = ref<HTMLInputElement | null>(null)
const skillLimit = 6

// 模板里避免对可能为 null 的字段使用非空断言，统一用可写 computed 代理
const preferredTrack = computed({
  get: () => draft.value.preference?.preferred_track ?? '',
  set: (value: string) => {
    if (!draft.value.preference) {
      draft.value.preference = { preferred_roles: [], avoid_roles: [], preferred_track: null, weekly_hours: 10 }
    }
    draft.value.preference.preferred_track = value
  },
})
const weeklyHours = computed({
  get: () => draft.value.preference?.weekly_hours ?? 10,
  set: (value: number) => {
    if (!draft.value.preference) {
      draft.value.preference = { preferred_roles: [], avoid_roles: [], preferred_track: null, weekly_hours: 10 }
    }
    draft.value.preference.weekly_hours = value
  },
})

async function load() {
  profile.value = await profileApi.mine()
  capabilities.value = await capabilityApi.list()
  await nextTick()
  renderChart()
}

/** 把技能数据画成雷达图：每个维度一根轴，熟练度 1~5 映射到 0~100 */
function renderChart() {
  if (!chartEl.value || !profile.value?.skills?.length) return
  if (!chart) chart = echarts.init(chartEl.value)
  const skills = profile.value.skills
  chart.setOption({
    tooltip: {},
    radar: {
      indicator: skills.map((s) => ({ name: categoryLabels[s.category] || s.name, max: 5 })),
      radius: '65%',
      splitArea: { areaStyle: { color: ['#f8fafc', '#eef2ff'] } },
    },
    series: [{
      type: 'radar',
      data: [{
        value: skills.map((s) => s.level),
        name: '当前能力',
        areaStyle: { color: 'rgba(79,70,229,.25)' },
        lineStyle: { color: '#4f46e5', width: 2 },
        itemStyle: { color: '#4f46e5' },
      }],
    }],
  }, true)
}

function openEdit() {
  const p = profile.value
  if (!p) return
  draft.value = {
    real_name: p.real_name,
    school: p.school,
    student_number: p.student_number,
    college: p.college,
    phone: p.phone,
    email: p.email,
    qq: p.qq,
    wechat: p.wechat,
    github: p.github,
    skills: p.skills.map((s) => ({ capability_id: s.capability_id, level: s.level })),
    projects: p.projects.map((x) => ({ ...x })),
    competitions: p.competitions.map((x) => ({ ...x })),
    preference: { ...p.preference },
  }
  dialogVisible.value = true
}

async function save() {
  try {
    const skills = draft.value.skills || []
    if (skills.length > skillLimit) {
      ElMessage.warning(`个人能力最多添加 ${skillLimit} 条`)
      return
    }
    if (new Set(skills.map((skill) => skill.capability_id)).size !== skills.length) {
      ElMessage.warning('同一能力维度不能重复添加')
      return
    }
    saving.value = true
    profile.value = await profileApi.update(draft.value)
    await store.fetchMe()
    dialogVisible.value = false
    ElMessage.success('个人信息已更新')
    await nextTick()
    renderChart()
  } finally {
    saving.value = false
  }
}

function chooseResume() {
  resumeInput.value?.click()
}

async function onResumeSelected(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  target.value = ''
  if (!file) return
  if (file.size > 10 * 1024 * 1024) {
    ElMessage.warning('简历不能超过 10 MB')
    return
  }
  uploadingResume.value = true
  try {
    if (profile.value) {
      profile.value.resume = await profileApi.uploadResume(file)
    }
    ElMessage.success('简历已上传，仅授权人员可见')
  } finally {
    uploadingResume.value = false
  }
}

async function downloadMyResume() {
  if (!profile.value?.resume) return
  const blob = await profileApi.downloadResume(profile.value.user_id)
  const url = URL.createObjectURL(blob)
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = profile.value.resume.name
  anchor.click()
  window.setTimeout(() => URL.revokeObjectURL(url), 1000)
}

async function deleteMyResume() {
  await ElMessageBox.confirm(
    '删除后管理员和申请团队队长将无法再查看当前简历，确认删除？',
    '删除简历',
    { type: 'warning' },
  )
  await profileApi.deleteResume()
  if (profile.value) profile.value.resume = null
  ElMessage.success('简历已删除')
}

function formatFileSize(bytes: number): string {
  return `${(bytes / 1024 / 1024).toFixed(2)} MB`
}

function addSkill() {
  if (!draft.value.skills) draft.value.skills = []
  if (draft.value.skills.length >= skillLimit) {
    ElMessage.warning(`个人能力最多添加 ${skillLimit} 条`)
    return
  }
  const used = new Set(draft.value.skills.map((skill) => skill.capability_id))
  const available = capabilities.value.find((capability) => !used.has(capability.id))
  if (!available) {
    ElMessage.warning('六个能力维度已全部添加')
    return
  }
  draft.value.skills.push({ capability_id: available.id, level: 3 })
}

function isCapabilityUsed(capabilityId: number, currentIndex: number): boolean {
  return (draft.value.skills || []).some(
    (skill, index) =>
      index !== currentIndex && skill.capability_id === capabilityId,
  )
}

function addExperience(key: 'projects' | 'competitions') {
  if (!draft.value[key]) draft.value[key] = []
  draft.value[key]?.push({ title: '', role: '' })
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
  <div class="page">
    <div class="flex-between">
      <div>
        <h1 class="page-title">个人中心</h1>
        <p class="page-desc">
          维护基本信息、私有简历和能力画像，为智能组队提供可信资料
        </p>
      </div>
      <el-button type="primary" @click="openEdit">编辑个人信息</el-button>
    </div>

    <div v-loading="!profile" class="grid grid-two">
      <el-card>
        <template #header>能力雷达图</template>
        <div ref="chartEl" class="chart-box" />
        <el-empty v-if="!profile?.skills?.length" description="还没有技能数据，点击编辑画像添加" />
      </el-card>

      <el-card>
        <template #header>基本信息</template>
        <div class="basic-grid">
          <div class="basic-field"><span>用户名</span><strong>{{ profile?.username }}</strong></div>
          <div class="basic-field"><span>姓名</span><strong>{{ profile?.real_name || '—' }}</strong></div>
          <div class="basic-field"><span>学号</span><strong>{{ profile?.student_number || '—' }}</strong></div>
          <div class="basic-field"><span>学院</span><strong>{{ profile?.college || '—' }}</strong></div>
          <div class="basic-field"><span>学校</span><strong>{{ profile?.school || '—' }}</strong></div>
          <div class="basic-field"><span>电话</span><strong>{{ profile?.phone || '—' }}</strong></div>
          <div class="basic-field"><span>邮箱</span><strong>{{ profile?.email || '—' }}</strong></div>
          <div class="basic-field"><span>QQ</span><strong>{{ profile?.qq || '—' }}</strong></div>
          <div class="basic-field"><span>微信</span><strong>{{ profile?.wechat || '—' }}</strong></div>
          <div class="basic-field"><span>GitHub</span><strong>{{ profile?.github || '—' }}</strong></div>
        </div>
        <div class="mt-16">
          <div class="row"><span class="muted">每周可投入</span><span>{{ profile?.preference?.weekly_hours ?? '—' }} 小时</span></div>
          <div class="row"><span class="muted">倾向方向</span><span>{{ profile?.preference?.preferred_track || '—' }}</span></div>
        </div>
        <div class="skill-list">
          <el-tag v-for="s in profile?.skills || []" :key="s.capability_id" effect="dark" type="primary">
            {{ s.name }} · {{ s.level }}/5
          </el-tag>
        </div>
      </el-card>

      <el-card>
        <template #header>
          <div class="flex-between">
            <span>私有简历</span>
            <el-tag v-if="profile?.resume" type="success" size="small">已上传</el-tag>
          </div>
        </template>
        <template v-if="profile?.resume">
          <div class="resume-file">
            <div>
              <strong>{{ profile.resume.name }}</strong>
              <p class="muted">
                {{ formatFileSize(profile.resume.size) }} ·
                {{ profile.resume.uploaded_at || '刚上传' }}
              </p>
            </div>
            <div class="resume-actions">
              <el-button link type="primary" @click="downloadMyResume">下载</el-button>
              <el-button link type="danger" @click="deleteMyResume">删除</el-button>
            </div>
          </div>
        </template>
        <p class="muted resume-privacy">
          简历仅本人、管理员，以及你已申请团队的队长可以查看。
          支持 PDF、DOC、DOCX，最大 10 MB。
        </p>
        <el-button
          type="primary"
          plain
          :loading="uploadingResume"
          @click="chooseResume"
        >
          {{ profile?.resume ? '替换简历' : '上传简历' }}
        </el-button>
        <input
          ref="resumeInput"
          type="file"
          accept=".pdf,.doc,.docx"
          class="hidden-file-input"
          @change="onResumeSelected"
        />
      </el-card>

      <el-card>
        <template #header>项目经历</template>
        <el-timeline v-if="profile?.projects?.length">
          <el-timeline-item v-for="(p, i) in profile.projects" :key="i" :timestamp="p.start_date || ''">
            <strong>{{ p.title }}</strong> · {{ p.role }}
            <div class="muted">{{ p.description }}</div>
          </el-timeline-item>
        </el-timeline>
        <el-empty v-else description="暂无项目经历" />
      </el-card>

      <el-card>
        <template #header>竞赛经历</template>
        <el-timeline v-if="profile?.competitions?.length">
          <el-timeline-item v-for="(p, i) in profile.competitions" :key="i" :timestamp="p.start_date || ''">
            <strong>{{ p.title }}</strong> · {{ p.role }}
            <el-tag
              v-if="p.award_level"
              size="small"
              type="warning"
              effect="plain"
              class="award-tag"
            >
              {{ awardLevelLabels[p.award_level] }}
            </el-tag>
            <div class="muted">{{ p.description }}</div>
          </el-timeline-item>
        </el-timeline>
        <el-empty v-else description="暂无竞赛经历" />
      </el-card>
    </div>

    <!-- 编辑弹窗：演示 PATCH 部分更新与嵌套表单 -->
    <el-dialog v-model="dialogVisible" title="编辑个人信息" width="820px">
      <el-form label-position="top">
        <h4>基本信息</h4>
        <div class="dialog-grid">
          <el-form-item label="姓名"><el-input v-model="draft.real_name" /></el-form-item>
          <el-form-item label="学号"><el-input v-model="draft.student_number" /></el-form-item>
          <el-form-item label="学院"><el-input v-model="draft.college" /></el-form-item>
          <el-form-item label="学校"><el-input v-model="draft.school" /></el-form-item>
          <el-form-item label="电话"><el-input v-model="draft.phone" /></el-form-item>
          <el-form-item label="邮箱"><el-input v-model="draft.email" /></el-form-item>
          <el-form-item label="QQ（可选）"><el-input v-model="draft.qq" /></el-form-item>
          <el-form-item label="微信（可选）"><el-input v-model="draft.wechat" /></el-form-item>
          <el-form-item label="GitHub（可选）">
            <el-input v-model="draft.github" placeholder="GitHub 用户名或主页" />
          </el-form-item>
        </div>

        <h4 class="mt-16">能力画像</h4>
        <div class="flex-between">
          <span>技能熟练度（1=了解，5=精通）</span>
          <span class="muted">
            {{ draft.skills?.length || 0 }} / {{ skillLimit }}
          </span>
        </div>
        <div v-for="(s, i) in draft.skills || []" :key="i" class="form-row">
          <el-select v-model="s.capability_id" placeholder="能力维度" style="width: 200px">
            <el-option
              v-for="c in capabilities"
              :key="c.id"
              :label="c.name"
              :value="c.id"
              :disabled="isCapabilityUsed(c.id, i)"
            />
          </el-select>
          <el-rate v-model="s.level" :max="5" />
          <el-button link type="danger" @click="draft.skills?.splice(i, 1)">删除</el-button>
        </div>
        <el-button
          link
          type="primary"
          :disabled="(draft.skills?.length || 0) >= skillLimit"
          @click="addSkill"
        >
          + 添加技能
        </el-button>

        <h4 class="mt-16">偏好设置</h4>
        <div class="form-row">
          <el-input v-model="preferredTrack" placeholder="倾向竞赛方向" style="width: 260px" />
          <span class="muted">每周投入</span>
          <el-input-number v-model="weeklyHours" :min="0" :max="80" />
        </div>

        <h4 class="mt-16">项目 / 竞赛经历</h4>
        <template v-for="key in (['projects', 'competitions'] as const)" :key="key">
          <div class="section-label">{{ key === 'projects' ? '项目经历' : '竞赛经历' }}</div>
          <div v-for="(item, i) in draft[key] || []" :key="i" class="form-row">
            <el-input v-model="item.title" placeholder="名称" style="width: 180px" />
            <el-input v-model="item.role" placeholder="担任角色" style="width: 150px" />
            <el-select
              v-if="key === 'competitions'"
              v-model="item.award_level"
              clearable
              placeholder="奖项等级"
              style="width: 140px"
            >
              <el-option
                v-for="(text, value) in awardLevelLabels"
                :key="value"
                :label="text"
                :value="value"
              />
            </el-select>
            <el-input v-model="item.description" placeholder="说明" style="flex: 1" />
            <el-button link type="danger" @click="draft[key]?.splice(i, 1)">删除</el-button>
          </div>
          <el-button link type="primary" @click="addExperience(key)">+ 添加一条</el-button>
        </template>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.row { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #f1f5f9; font-size: 14px; }
.basic-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }
.basic-field { display: flex; flex-direction: column; gap: 3px; padding: 9px 10px; background: #f8fafc; border-radius: 8px; }
.basic-field span { color: #64748b; font-size: 12px; }
.basic-field strong { overflow: hidden; font-size: 14px; text-overflow: ellipsis; }
.dialog-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 0 14px; }
.skill-list { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 16px; }
.form-row { display: flex; align-items: center; gap: 10px; margin: 8px 0; flex-wrap: wrap; }
.section-label { font-weight: 600; margin-top: 12px; }
.award-tag { margin-left: 8px; }
.resume-file { display: flex; justify-content: space-between; gap: 16px; padding: 12px; background: #f8fafc; border-radius: 10px; }
.resume-file p { margin: 4px 0 0; }
.resume-actions { display: flex; white-space: nowrap; }
.resume-privacy { line-height: 1.7; }
.hidden-file-input { display: none; }
@media (max-width: 760px) {
  .basic-grid, .dialog-grid { grid-template-columns: 1fr; }
}
</style>
