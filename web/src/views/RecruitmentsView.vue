<script setup lang="ts">
import { onMounted, ref } from 'vue'
import ElMessage from 'element-plus/es/components/message/index.mjs'
import { Search } from '@element-plus/icons-vue'
import { applicationApi, recruitmentApi, teamApi } from '@/api'
import type { RecruitmentOut, TeamDetail } from '@/types'
import { useUserStore } from '@/stores/user'
import { formatDate, label } from '@/utils/format'

const store = useUserStore()
const items = ref<RecruitmentOut[]>([])
const total = ref(0)
const page = ref(1)
const skip = ref(0)
const limit = 10
const track = ref('')
const skill = ref('')
const loading = ref(false)
const leaderTeamIds = ref<Set<number>>(new Set())

async function load() {
  loading.value = true
  try {
    const res = await recruitmentApi.list(skip.value, limit, track.value || undefined, skill.value || undefined)
    items.value = res.items
    total.value = res.total
  } finally {
    loading.value = false }
}

/** 查我带的队伍，用于显示“编辑/关闭”按钮（后端仍会做真正的权限校验） */
async function loadLeaderTeams() {
  if (!store.isLoggedIn || !store.canParticipate) return
  const mine = await teamApi.mine()
  const details = await Promise.all(mine.map((t) => teamApi.detail(t.id)))
  leaderTeamIds.value = new Set(
    details
      .filter((t: TeamDetail) => t.members.some(
        (m) => m.user_id === store.user?.id && m.role === 'leader',
      ))
      .map((t: TeamDetail) => t.id),
  )
}

async function apply(r: RecruitmentOut) {
  if (!store.isLoggedIn) {
    ElMessage.warning('请先登录')
    return
  }
  try {
    await applicationApi.apply(r.id, '希望加入团队，共同完成竞赛。')
    ElMessage.success('申请已提交')
  } catch { /* 拦截器处理 */ }
}

async function close(r: RecruitmentOut) {
  await recruitmentApi.close(r.id)
  ElMessage.success('招募已关闭')
  await load()
}

function onPageChange(p: number) {
  skip.value = (p - 1) * limit
  load()
}

onMounted(async () => {
  await load()
  await loadLeaderTeams()
})
</script>

<template>
  <div class="page">
    <h1 class="page-title">招募广场</h1>
    <p class="page-desc">浏览全部招募信息，按方向与技能筛选并申请加入</p>

    <div class="toolbar">
      <el-input v-model="track" placeholder="竞赛方向" clearable style="width: 180px" :prefix-icon="Search" @clear="load" />
      <el-input v-model="skill" placeholder="所需技能" clearable style="width: 200px" @clear="load" />
      <el-button type="primary" @click="page=1; skip=0; load()">搜索</el-button>
    </div>

    <div v-loading="loading">
      <el-card v-for="r in items" :key="r.id" class="rec-card">
        <div class="flex-between">
          <div>
            <h3 class="rec-title">{{ r.title }}</h3>
            <div class="muted">
              {{ label(r.status) }} · {{ r.competition_track }} · 队伍 {{ r.team_id }} ·
              发布于 {{ formatDate(r.created_at) }}
            </div>
          </div>
          <div>
            <el-tag type="info">{{ r.current_members }} / {{ r.target_size }} 人</el-tag>
          </div>
        </div>
        <p class="desc">{{ r.description }}</p>
        <div class="tags">
          <el-tag v-for="s in r.required_skills" :key="s" size="small" type="warning" effect="plain">
            技能：{{ s }}
          </el-tag>
          <el-tag v-for="role in r.required_roles" :key="role" size="small" effect="plain">
            角色：{{ role }}
          </el-tag>
        </div>
        <div class="actions">
          <el-button
            v-if="r.status === 'open'"
            type="primary"
            @click="apply(r)"
          >
            申请加入
          </el-button>
          <el-button v-if="r.status === 'open' && leaderTeamIds.has(r.team_id)" type="danger" plain @click="close(r)">
            关闭招募
          </el-button>
        </div>
      </el-card>
    </div>

    <el-empty v-if="!loading && !items.length" description="暂无招募信息" />
    <div class="pagination">
      <el-pagination
        v-model:current-page="page" :page-size="limit" :total="total"
        layout="prev, pager, next" background
        @current-change="onPageChange"
      />
    </div>
  </div>
</template>

<style scoped>
.rec-card { margin-bottom: 14px; }
.rec-title { margin: 0 0 6px; font-size: 17px; }
.desc { color: #4b5563; font-size: 14px; margin: 12px 0; }
.tags { display: flex; gap: 6px; flex-wrap: wrap; }
.actions { margin-top: 14px; }
.pagination { display: flex; justify-content: center; margin-top: 20px; }
</style>
