<script setup lang="ts">
import { onMounted, ref } from 'vue'
import ElMessage from 'element-plus/es/components/message/index.mjs'
import { recommendationApi, teamApi } from '@/api'
import type {
  RecommendationItem,
  RecommendationOut,
  TeamDetail,
  TeamOut,
} from '@/types'
import { formatDate } from '@/utils/format'
import { useUserStore } from '@/stores/user'

const store = useUserStore()
const items = ref<RecommendationItem[]>([])
const history = ref<RecommendationOut[]>([])
const myTeams = ref<TeamOut[]>([])
const teamId = ref<number | null>(null)
const mode = ref('teams')
const loading = ref(false)

const dimensionNames: Record<string, string> = {
  skill_match: '技能匹配',
  complement: '能力互补',
  experience: '竞赛经历',
  role_fit: '角色契合',
  time_fit: '时间投入',
  preference_fit: '方向偏好',
}

async function load() {
  loading.value = true
  try {
    if (mode.value === 'teams') {
      items.value = await recommendationApi.teams(10)
    } else if (teamId.value !== null) {
      items.value = await recommendationApi.members(teamId.value, 10)
    } else {
      items.value = []
    }
    history.value = await recommendationApi.history()
  } catch {
    items.value = []
  } finally {
    loading.value = false
  }
}

function applyTarget(item: RecommendationItem) {
  // 推荐的是招募或用户；跳转对应页面由用户继续操作
  ElMessage.info(
    item.target_type === 'recruitment'
      ? '请到「招募广场」找到该招募并提交申请'
      : '请到「我的团队」通过队长添加成员功能邀请该用户',
  )
}

onMounted(async () => {
  const mine = await teamApi.mine()
  const details = await Promise.all(mine.map((team) => teamApi.detail(team.id)))
  myTeams.value = mine.filter((team) =>
    details.some(
      (detail: TeamDetail) =>
        detail.id === team.id &&
        detail.members.some(
          (member) =>
            member.user_id === store.user?.id &&
            member.role === 'leader',
        ),
    ),
  )
  if (myTeams.value.length) teamId.value = myTeams.value[0].id
  await load()
})
</script>

<template>
  <div class="page">
    <h1 class="page-title">智能推荐</h1>
    <p class="page-desc">基于技能匹配、能力互补、经历与时间等六个维度，给出可解释的推荐结果</p>

    <div class="toolbar">
      <el-radio-group v-model="mode" @change="load">
        <el-radio-button value="teams">为我推荐团队</el-radio-button>
        <el-radio-button value="members">为队伍推荐成员</el-radio-button>
      </el-radio-group>
      <template v-if="mode === 'members'">
        <el-select v-model="teamId" placeholder="选择我的团队" style="width: 220px" @change="load">
          <el-option v-for="t in myTeams" :key="t.id" :label="t.name" :value="t.id" />
        </el-select>
      </template>
    </div>

    <div v-loading="loading" class="grid grid-two">
      <el-card v-for="(item, i) in items" :key="`${item.target_type}-${item.target_id}-${i}`">
        <template #header>
          <div class="flex-between">
            <strong>#{{ i + 1 }} {{ item.title }}</strong>
            <el-progress
              type="dashboard" :percentage="Math.round(item.score * 100)"
              :width="64" :stroke-width="6"
            />
          </div>
        </template>
        <div class="dimensions">
          <div v-for="(detail, key) in item.breakdown" :key="key" class="dim">
            <div class="flex-between">
              <span>{{ dimensionNames[key] || key }}</span>
              <span class="muted">{{ (detail.score * 100).toFixed(0) }} × {{ detail.weight }}</span>
            </div>
            <el-progress :percentage="Math.round(detail.score * 100)" :show-text="false" :stroke-width="6" />
            <div class="muted reason">{{ detail.reason }}</div>
          </div>
        </div>
        <div class="mt-8">
          <el-tag v-for="s in item.strengths" :key="s" type="success" size="small" class="tag">优势：{{ s }}</el-tag>
          <el-tag v-for="g in item.gaps" :key="g" type="warning" size="small" effect="plain" class="tag">差距：{{ g }}</el-tag>
        </div>
        <template #footer>
          <el-button link type="primary" @click="applyTarget(item)">去处理</el-button>
        </template>
      </el-card>
    </div>
    <el-empty v-if="!loading && !items.length" description="暂无推荐结果" />

    <el-card class="mt-24">
      <template #header>推荐历史（含算法版本）</template>
      <el-table :data="history" size="small">
        <el-table-column prop="target_type" label="类型" width="110" />
        <el-table-column prop="target_id" label="目标 ID" width="100" />
        <el-table-column prop="score" label="得分" width="90">
          <template #default="{ row }">{{ (row.score * 100).toFixed(0) }}</template>
        </el-table-column>
        <el-table-column prop="algorithm_version" label="算法版本" width="140" />
        <el-table-column label="时间">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!history.length" description="暂无历史记录" />
    </el-card>
  </div>
</template>

<style scoped>
.dim { margin-bottom: 10px; font-size: 13px; }
.reason { font-size: 12px; margin-top: 2px; }
.tag { margin: 2px 4px 2px 0; }
</style>
