<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import ElMessage from 'element-plus/es/components/message/index.mjs'
import echarts from '@/utils/echarts'
import {
  recommendationApi, recruitmentApi, teamApi,
} from '@/api'
import type { RecommendationItem, TeamDetail, TeamProfileOut } from '@/types'
import { formatDate, label } from '@/utils/format'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const store = useUserStore()
const teamId = Number(route.params.id)
const team = ref<TeamDetail | null>(null)
const profile = ref<TeamProfileOut | null>(null)
const candidates = ref<RecommendationItem[]>([])
const chartEl = ref<HTMLElement | null>(null)
let chart: ReturnType<typeof echarts.init> | null = null
const isLeader = computed(
  () =>
    team.value?.members.some(
      (member) =>
        member.user_id === store.user?.id && member.role === 'leader',
    ) ?? false,
)
const isFull = computed(
  () => !!team.value && team.value.member_count >= team.value.max_size,
)

const publishVisible = ref(false)
const publishForm = ref({
  title: '', competition_track: 'math_modeling', target_size: 1,
  required_roles: [] as string[], required_skills_text: '', description: '',
})

async function load() {
  team.value = await teamApi.detail(teamId)
  profile.value = await teamApi.profile(teamId)
  await nextTick()
  renderChart()
  if (isLeader.value && !isFull.value) {
    candidates.value = await recommendationApi.members(teamId, 5)
  } else {
    candidates.value = []
  }
}

function renderChart() {
  if (!chartEl.value || !profile.value) return
  if (!chart) chart = echarts.init(chartEl.value)
  const names = Object.keys(profile.value.coverage)
  const values = Object.values(profile.value.coverage).map((c) => c.avg_level)
  chart.setOption({
    animation: false,
    tooltip: {},
    xAxis: { type: 'category', data: names, axisLabel: { interval: 0, rotate: 20 } },
    yAxis: { type: 'value', min: 0, max: 5 },
    series: [{
      type: 'bar', data: values, barWidth: '45%',
      itemStyle: { color: '#4f46e5', borderRadius: [4, 4, 0, 0] },
      markLine: { data: [{ yAxis: 3, name: '薄弱线' }], lineStyle: { color: '#f59e0b' } },
    }],
  }, true)
  chart.resize()
}

function openPublish() {
  if (!team.value) return
  publishForm.value.target_size = Math.min(
    team.value.max_size,
    team.value.member_count + 1,
  )
  publishVisible.value = true
}

async function addMember(userId: number) {
  team.value = await teamApi.addMember(teamId, userId)
  ElMessage.success('成员已加入')
  await load()
}

async function publish() {
  try {
    await recruitmentApi.create(teamId, {
      title: publishForm.value.title,
      competition_track: publishForm.value.competition_track,
      target_size: publishForm.value.target_size,
      required_roles: publishForm.value.required_roles,
      // 表单里用逗号输入，提交时转成后端需要的字符串数组
      required_skills: publishForm.value.required_skills_text
        .split(/[,，]/).map((s) => s.trim()).filter(Boolean),
      description: publishForm.value.description || undefined,
    })
    ElMessage.success('招募信息已发布')
    publishVisible.value = false
  } catch { /* 拦截器处理 */ }
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
  <div class="page" v-loading="!team">
    <el-button link @click="router.push('/teams')">← 返回我的团队</el-button>
    <div class="flex-between mt-8">
      <div>
        <h1 class="page-title">{{ team?.name }}</h1>
        <p class="page-desc">{{ team?.description }}</p>
      </div>
      <div>
        <el-tag type="info">{{ label(team?.status || '') }}</el-tag>
        <el-button
          v-if="isLeader && !isFull"
          type="primary"
          class="mt-8"
          @click="openPublish"
        >
          发布招募
        </el-button>
      </div>
    </div>

    <div class="grid grid-two">
      <el-card>
        <template #header>团队信息</template>
        <div class="row"><span>竞赛方向</span><span>{{ team?.competition_track }}</span></div>
        <div class="row"><span>成员数</span><span>{{ team?.member_count }} / {{ team?.max_size }}</span></div>
        <div class="row"><span>创建时间</span><span>{{ formatDate(team?.created_at) }}</span></div>
        <h4 class="mt-16">成员列表</h4>
        <el-table :data="team?.members || []" size="small">
          <el-table-column prop="username" label="用户名" />
          <el-table-column prop="role" label="角色" width="90">
            <template #default="{ row }">
              <el-tag :type="row.role === 'leader' ? 'warning' : 'info'" size="small">
                {{ row.role === 'leader' ? '队长' : '队员' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="加入时间">
            <template #default="{ row }">{{ formatDate(row.joined_at) }}</template>
          </el-table-column>
        </el-table>
      </el-card>

      <el-card>
        <template #header>团队能力分布</template>
        <div ref="chartEl" class="chart-box" />
        <div class="mt-8">
          <span class="muted">能力缺口：</span>
          <el-tag v-for="g in profile?.gaps || []" :key="g" type="danger" size="small" effect="plain" class="tag">
            {{ g }}
          </el-tag>
          <span class="muted ml-8">能力偏弱：</span>
          <el-tag v-for="g in profile?.weak || []" :key="`weak-${g}`" type="warning" size="small" effect="plain" class="tag">
            {{ g }}
          </el-tag>
          <span
            v-if="!profile?.gaps?.length && !profile?.weak?.length"
            class="muted"
          >
            暂无明显能力缺口
          </span>
        </div>
      </el-card>
    </div>

    <el-card v-if="isLeader" class="mt-16">
      <template #header>推荐候选人（按团队短板匹配）</template>
      <el-table :data="candidates" size="small">
        <el-table-column prop="title" label="候选人" />
        <el-table-column prop="score" label="匹配分" width="100">
          <template #default="{ row }">{{ (row.score * 100).toFixed(0) }}</template>
        </el-table-column>
        <el-table-column label="优势项">
          <template #default="{ row }">
            <el-tag v-for="s in row.strengths" :key="s" size="small" type="success" class="tag">{{ s }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button
              v-if="!isFull"
              link
              type="primary"
              @click="addMember(row.target_id)"
            >
              添加
            </el-button>
            <span v-else class="muted">已满员</span>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!candidates.length" description="暂无推荐（仅队长可见）" />
    </el-card>

    <el-dialog v-model="publishVisible" title="发布招募" width="560px">
      <el-form :model="publishForm" label-position="top">
        <el-form-item label="标题"><el-input v-model="publishForm.title" /></el-form-item>
        <el-form-item label="竞赛方向"><el-input v-model="publishForm.competition_track" /></el-form-item>
        <el-form-item label="目标团队总人数">
          <el-input-number
            v-model="publishForm.target_size"
            :min="(team?.member_count || 0) + 1"
            :max="team?.max_size || 3"
          />
        </el-form-item>
        <el-form-item label="所需角色"><el-select v-model="publishForm.required_roles" multiple style="width:100%">
          <el-option label="writer 论文" value="writer" />
          <el-option label="analyst 数据分析" value="analyst" />
          <el-option label="coder 编程" value="coder" />
          <el-option label="modeler 建模" value="modeler" />
        </el-select></el-form-item>
        <el-form-item label="所需技能（多个用逗号分隔）">
          <el-input v-model="publishForm.required_skills_text" placeholder="论文写作,数据分析" />
        </el-form-item>
        <el-form-item label="描述"><el-input v-model="publishForm.description" type="textarea" :rows="3" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="publishVisible = false">取消</el-button>
        <el-button type="primary" @click="publish">发布</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.row { display: flex; justify-content: space-between; padding: 7px 0; font-size: 14px; }
.tag { margin: 2px 4px 2px 0; }
.ml-8 { margin-left: 8px; }
</style>
