<script setup lang="ts">
import { onMounted, ref } from 'vue'
import ElMessage from 'element-plus/es/components/message/index.mjs'
import { applicationApi, profileApi, teamApi } from '@/api'
import type { ApplicationOut, ApplicationWithApplicant, TeamOut } from '@/types'
import { formatDate, label } from '@/utils/format'

const mine = ref<ApplicationOut[]>([])
const teamApps = ref<ApplicationWithApplicant[]>([])
const myTeams = ref<TeamOut[]>([])
const selectedTeam = ref<number | null>(null)
const loading = ref(false)
const tab = ref('mine')

async function load() {
  loading.value = true
  try {
    mine.value = await applicationApi.mine()
    myTeams.value = await teamApi.mine()
    if (myTeams.value.length && selectedTeam.value === null) {
      selectedTeam.value = myTeams.value[0].id
    }
    if (selectedTeam.value !== null) await loadTeamApps()
  } finally {
    loading.value = false
  }
}

async function loadTeamApps() {
  if (selectedTeam.value === null) return
  try {
    teamApps.value = await applicationApi.team(selectedTeam.value)
  } catch {
    teamApps.value = []  // 非队长会收到 403
  }
}

async function review(app: ApplicationWithApplicant, decision: 'accept' | 'reject') {
  await applicationApi.review(app.id, decision)
  ElMessage.success(decision === 'accept' ? '已通过申请' : '已拒绝申请')
  await loadTeamApps()
  await load()
}

function statusType(s: string): 'success' | 'danger' | 'warning' {
  if (s === 'accepted') return 'success'
  if (s === 'rejected') return 'danger'
  return 'warning'
}

async function downloadApplicantResume(app: ApplicationWithApplicant) {
  if (!app.resume) return
  const blob = await profileApi.downloadResume(app.applicant_id)
  const url = URL.createObjectURL(blob)
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = app.resume.name
  anchor.click()
  window.setTimeout(() => URL.revokeObjectURL(url), 1000)
}

onMounted(load)
</script>

<template>
  <div class="page" v-loading="loading">
    <h1 class="page-title">申请管理</h1>
    <p class="page-desc">查看自己提交的申请，或审批加入团队的申请</p>

    <el-tabs v-model="tab">
      <el-tab-pane label="我的申请" name="mine">
        <el-table :data="mine" style="width: 100%">
          <el-table-column prop="id" label="编号" width="80" />
          <el-table-column prop="recruitment_id" label="招募 ID" width="100" />
          <el-table-column prop="message" label="附言" />
          <el-table-column prop="status" label="状态" width="110">
            <template #default="{ row }">
              <el-tag :type="statusType(row.status)" size="small">{{ label(row.status) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="提交时间" width="170">
            <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
          </el-table-column>
        </el-table>
        <el-empty v-if="!mine.length" description="还没有提交过申请" />
      </el-tab-pane>

      <el-tab-pane label="团队申请审批" name="team">
        <div class="toolbar">
          <span class="muted">选择团队：</span>
          <el-select v-model="selectedTeam" placeholder="我的团队" style="width: 220px" @change="loadTeamApps">
            <el-option v-for="t in myTeams" :key="t.id" :label="t.name" :value="t.id" />
          </el-select>
        </div>
        <el-table :data="teamApps" style="width: 100%">
          <el-table-column prop="applicant_id" label="申请者 ID" width="100" />
          <el-table-column label="申请者">
            <template #default="{ row }">
              {{ row.applicant?.real_name || row.applicant?.username || '—' }}
              <div class="muted">
                {{ row.applicant?.student_number || '—' }} ·
                {{ row.applicant?.college || '未填写学院' }} ·
                {{ row.applicant?.school || '未填写学校' }}
              </div>
            </template>
          </el-table-column>
          <el-table-column label="简历" width="100">
            <template #default="{ row }">
              <el-button
                v-if="row.resume"
                link
                type="primary"
                @click="downloadApplicantResume(row)"
              >
                下载简历
              </el-button>
              <span v-else class="muted">未上传</span>
            </template>
          </el-table-column>
          <el-table-column label="技能">
            <template #default="{ row }">
              <el-tag v-for="s in row.skills" :key="s.name" size="small" class="tag">
                {{ s.name }} {{ s.level }}/5
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="message" label="附言" />
          <el-table-column prop="status" label="状态" width="110">
            <template #default="{ row }">
              <el-tag :type="statusType(row.status)" size="small">{{ label(row.status) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="160">
            <template #default="{ row }">
              <template v-if="row.status === 'pending'">
                <el-button link type="success" @click="review(row, 'accept')">通过</el-button>
                <el-button link type="danger" @click="review(row, 'reject')">拒绝</el-button>
              </template>
              <span v-else class="muted">已处理</span>
            </template>
          </el-table-column>
        </el-table>
        <el-empty v-if="!teamApps.length" description="暂无待处理申请" />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<style scoped>
.tag { margin: 2px; }
</style>
