<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref } from 'vue'
import ElMessage from 'element-plus/es/components/message/index.mjs'
import echarts from '@/utils/echarts'
import { capabilityApi, profileApi } from '@/api'
import type { Capability, ProfileOut, ProfileUpdate } from '@/types'
import { awardLevelLabels, categoryLabels } from '@/utils/format'

const profile = ref<ProfileOut | null>(null)
const capabilities = ref<Capability[]>([])
const chartEl = ref<HTMLElement | null>(null)
let chart: ReturnType<typeof echarts.init> | null = null

// 编辑弹窗的表单数据
const dialogVisible = ref(false)
const draft = ref<ProfileUpdate>({})
const saving = ref(false)
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
    dialogVisible.value = false
    ElMessage.success('画像已更新')
    await nextTick()
    renderChart()
  } finally {
    saving.value = false
  }
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
        <h1 class="page-title">我的能力画像</h1>
        <p class="page-desc">结构化展示六大能力维度，为智能组队提供数据基础</p>
      </div>
      <el-button type="primary" @click="openEdit">编辑画像</el-button>
    </div>

    <div v-loading="!profile" class="grid grid-two">
      <el-card>
        <template #header>能力雷达图</template>
        <div ref="chartEl" class="chart-box" />
        <el-empty v-if="!profile?.skills?.length" description="还没有技能数据，点击编辑画像添加" />
      </el-card>

      <el-card>
        <template #header>基本信息与偏好</template>
        <div class="row"><span class="muted">用户名</span><span>{{ profile?.username }}</span></div>
        <div class="row"><span class="muted">姓名</span><span>{{ profile?.real_name || '—' }}</span></div>
        <div class="row"><span class="muted">学校</span><span>{{ profile?.school || '—' }}</span></div>
        <div class="row"><span class="muted">每周可投入</span><span>{{ profile?.preference?.weekly_hours ?? '—' }} 小时</span></div>
        <div class="row"><span class="muted">倾向方向</span><span>{{ profile?.preference?.preferred_track || '—' }}</span></div>
        <div class="skill-list">
          <el-tag v-for="s in profile?.skills || []" :key="s.capability_id" effect="dark" type="primary">
            {{ s.name }} · {{ s.level }}/5
          </el-tag>
        </div>
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
    <el-dialog v-model="dialogVisible" title="编辑能力画像" width="720px">
      <el-form label-position="top">
        <div class="flex-between">
          <h4>技能熟练度（1=了解，5=精通）</h4>
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
.skill-list { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 16px; }
.form-row { display: flex; align-items: center; gap: 10px; margin: 8px 0; flex-wrap: wrap; }
.section-label { font-weight: 600; margin-top: 12px; }
.award-tag { margin-left: 8px; }
</style>
