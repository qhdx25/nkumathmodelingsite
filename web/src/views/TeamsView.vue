<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { teamApi } from '@/api'
import type { TeamOut } from '@/types'
import { formatDate, label } from '@/utils/format'

const router = useRouter()
const teams = ref<TeamOut[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const form = reactive({ name: '', description: '', competition_track: 'math_modeling', max_size: 3 })

async function load() {
  loading.value = true
  try {
    teams.value = await teamApi.mine()
  } finally {
    loading.value = false
  }
}

async function create() {
  try {
    await teamApi.create({
      name: form.name,
      description: form.description || undefined,
      competition_track: form.competition_track,
      max_size: form.max_size,
    })
    ElMessage.success('团队创建成功，你已成为队长')
    dialogVisible.value = false
    await load()
  } catch {
    // 拦截器统一提示
  }
}

onMounted(load)
</script>

<template>
  <div class="page">
    <div class="flex-between">
      <div>
        <h1 class="page-title">我的团队</h1>
        <p class="page-desc">创建团队、查看能力画像、管理成员</p>
      </div>
      <el-button type="primary" @click="dialogVisible = true">+ 创建团队</el-button>
    </div>

    <div v-loading="loading" class="grid grid-cards">
      <el-card v-for="t in teams" :key="t.id" shadow="hover">
        <template #header>
          <div class="flex-between">
            <strong>{{ t.name }}</strong>
            <el-tag size="small" :type="t.status === 'recruiting' ? 'success' : 'info'">
              {{ label(t.status) }}
            </el-tag>
          </div>
        </template>
        <p class="muted desc">{{ t.description || '暂无队伍简介' }}</p>
        <div class="row"><span>竞赛方向</span><span>{{ t.competition_track }}</span></div>
        <div class="row"><span>成员</span><span>{{ t.member_count }} / {{ t.max_size }}</span></div>
        <div class="row"><span>创建时间</span><span>{{ formatDate(t.created_at) }}</span></div>
        <template #footer>
          <el-button type="primary" link @click="router.push(`/teams/${t.id}`)">查看详情与画像</el-button>
        </template>
      </el-card>
    </div>
    <el-empty v-if="!loading && !teams.length" description="你还没有加入任何团队，先创建一个吧" />

    <el-dialog v-model="dialogVisible" title="创建团队" width="520px">
      <el-form :model="form" label-position="top">
        <el-form-item label="团队名称"><el-input v-model="form.name" placeholder="例如：数模先锋队" /></el-form-item>
        <el-form-item label="竞赛方向">
          <el-select v-model="form.competition_track" style="width: 100%">
            <el-option label="数学建模" value="math_modeling" />
            <el-option label="数据分析" value="data_analysis" />
            <el-option label="优化问题" value="optimization" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="队伍规模"><el-input-number v-model="form.max_size" :min="2" :max="6" /></el-form-item>
        <el-form-item label="简介"><el-input v-model="form.description" type="textarea" :rows="3" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="create">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.row { display: flex; justify-content: space-between; font-size: 14px; padding: 6px 0; }
.desc { min-height: 42px; }
</style>
