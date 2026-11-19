<script setup lang="ts">
import { nextTick, onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import { adminApi } from '@/api'
import type { UserOut } from '@/types'
import { formatDate } from '@/utils/format'

const stats = ref<Record<string, number>>({})
const users = ref<UserOut[]>([])
const teams = ref<{ id: number; name: string; status: string; max_size: number }[]>([])
const recruitments = ref<{ id: number; title: string; status: string; team_id: number }[]>([])
const chartEl = ref<HTMLElement | null>(null)
let chart: echarts.ECharts | null = null
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    const [s, u, t, r] = await Promise.all([
      adminApi.stats(), adminApi.users(0, 50), adminApi.teams(), adminApi.recruitments(),
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
  const labelsMap: Record<string, string> = {
    users: '用户', teams: '团队', capabilities: '能力维度',
    recruitments: '招募', applications: '申请', messages: '消息', admin_logs: '管理日志',
  }
  const entries = Object.entries(stats.value).filter(([k]) => labelsMap[k])
  chart.setOption({
    tooltip: { trigger: 'item' },
    legend: { bottom: 0 },
    series: [{
      type: 'pie', radius: ['40%', '68%'], center: ['50%', '45%'],
      data: entries.map(([k, v]) => ({ name: labelsMap[k], value: v })),
      label: { formatter: '{b}: {c}' },
    }],
  }, true)
}

async function toggleStatus(user: UserOut) {
  const next = user.status === 'active' ? 'disabled' : 'active'
  await adminApi.setUserStatus(user.id, next)
  ElMessage.success(`账号已${next === 'active' ? '启用' : '停用'}`)
  await load()
}

async function remove(id: number) {
  await ElMessageBox.confirm('确认下架这条招募信息？', '提示', { type: 'warning' })
  await adminApi.removeRecruitment(id)
  ElMessage.success('已删除')
  await load()
}

onMounted(load)
window.addEventListener('resize', () => chart?.resize())
</script>

<template>
  <div class="page" v-loading="loading">
    <h1 class="page-title">后台管理</h1>
    <p class="page-desc">用户、团队、招募管理与运营数据统计（学校管理员仅能管理本校用户）</p>

    <div class="grid grid-two">
      <el-card>
        <template #header>运营数据概览</template>
        <div class="stats">
          <div v-for="(value, key) in stats" :key="key" class="stat">
            <div class="stat-value">{{ value }}</div>
            <div class="muted">{{ key }}</div>
          </div>
        </div>
      </el-card>
      <el-card>
        <template #header>数据占比</template>
        <div ref="chartEl" class="chart-box" />
      </el-card>
    </div>

    <el-card class="mt-16">
      <template #header>用户管理</template>
      <el-table :data="users" size="small">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="email" label="邮箱" />
        <el-table-column prop="school" label="学校" />
        <el-table-column prop="role" label="角色" width="130" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'danger'" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="注册时间" width="170">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button link :type="row.status === 'active' ? 'danger' : 'success'" @click="toggleStatus(row)">
              {{ row.status === 'active' ? '停用' : '启用' }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <div class="grid grid-two mt-16">
      <el-card>
        <template #header>团队列表</template>
        <el-table :data="teams" size="small">
          <el-table-column prop="id" label="ID" width="70" />
          <el-table-column prop="name" label="团队名称" />
          <el-table-column prop="status" label="状态" width="110" />
          <el-table-column prop="max_size" label="容量" width="80" />
        </el-table>
      </el-card>
      <el-card>
        <template #header>招募管理</template>
        <el-table :data="recruitments" size="small">
          <el-table-column prop="id" label="ID" width="70" />
          <el-table-column prop="title" label="标题" />
          <el-table-column prop="status" label="状态" width="100" />
          <el-table-column label="操作" width="90">
            <template #default="{ row }">
              <el-button link type="danger" @click="remove(row.id)">下架</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>
  </div>
</template>

<style scoped>
.stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(110px, 1fr)); gap: 12px; }
.stat { text-align: center; padding: 14px 8px; background: #f8fafc; border-radius: 8px; }
.stat-value { font-size: 24px; font-weight: 700; color: #4f46e5; }
</style>
