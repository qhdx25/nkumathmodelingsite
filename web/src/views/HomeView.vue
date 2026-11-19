<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Search, Refresh } from '@element-plus/icons-vue'
import { applicationApi, recruitmentApi } from '@/api'
import type { TeamCard } from '@/types'
import { useUserStore } from '@/stores/user'
import { label } from '@/utils/format'

const router = useRouter()
const store = useUserStore()
const cards = ref<TeamCard[]>([])
const total = ref(0)
const loading = ref(false)
const track = ref('')
const skill = ref('')
const page = ref(1)   // 分页控件用 1 起始的页码
const skip = ref(0)   // 后端接口用 0 起始的偏移量
const limit = 12
const tracks = ['math_modeling', 'data_analysis', 'optimization', 'other']

async function loadCards() {
  loading.value = true
  try {
    // 首页卡片接口 /recruitments/cards 无需登录，公开可见
    const res = await recruitmentApi.cards(skip.value, limit, track.value || undefined, skill.value || undefined)
    cards.value = res.items
    total.value = res.total
  } finally {
    loading.value = false
  }
}

async function apply(card: TeamCard) {
  if (!store.isLoggedIn) {
    ElMessage.warning('请先登录再申请加入队伍')
    await router.push('/login')
    return
  }
  try {
    await applicationApi.apply(card.id, '我希望加入贵团队，共同完成竞赛任务。')
    ElMessage.success('申请已提交，可在「申请管理」查看进度')
  } catch {
    // 拦截器统一提示（例如重复申请 400）
  }
}

/** Element Plus 分页组件用 1 起始页码，后端接口用 0 起始偏移量 */
function onPageChange(p: number) {
  skip.value = (p - 1) * limit
  loadCards()
}

onMounted(loadCards)
</script>

<template>
  <div>
    <!-- 首屏横幅 -->
    <section class="hero">
      <div class="hero-inner">
        <h1>找到合适的队友，一起拿下数学建模竞赛</h1>
        <p>能力画像 · 智能匹配 · 队伍招募 · 协作交流，从发现队友到组队参赛的一站式平台</p>
        <div class="hero-actions">
          <el-button type="primary" size="large" @click="router.push('/register')">立即加入</el-button>
          <el-button size="large" @click="router.push(store.isLoggedIn ? '/recommendations' : '/login')">
            {{ store.isLoggedIn ? '查看智能推荐' : '体验智能推荐' }}
          </el-button>
        </div>
      </div>
    </section>

    <div class="page">
      <h2 class="page-title">正在招募的队伍</h2>
      <p class="page-desc">浏览队伍需求，筛选与你匹配的竞赛方向与技能</p>

      <div class="toolbar">
        <el-select v-model="track" placeholder="竞赛方向" clearable style="width: 180px" @change="loadCards">
          <el-option v-for="t in tracks" :key="t" :label="t" :value="t" />
        </el-select>
        <el-input
          v-model="skill"
          placeholder="所需技能，如 数据分析"
          clearable
          style="width: 240px"
          :prefix-icon="Search"
          @keyup.enter="loadCards"
          @clear="loadCards"
        />
        <el-button :icon="Search" @click="loadCards">搜索</el-button>
        <el-button :icon="Refresh" @click="track=''; skill=''; page=1; skip=0; loadCards()">重置</el-button>
        <span class="muted">共 {{ total }} 支队伍</span>
      </div>

      <div v-loading="loading" class="grid grid-cards">
        <el-card v-for="card in cards" :key="card.id" shadow="hover" class="team-card">
          <template #header>
            <div class="flex-between">
              <strong>{{ card.title }}</strong>
              <el-tag size="small" :type="card.team_status === 'recruiting' ? 'success' : 'info'">
                {{ label(card.team_status) }}
              </el-tag>
            </div>
          </template>
          <div class="card-body">
            <div class="row"><span class="muted">队伍</span><span>{{ card.team_name }}</span></div>
            <div class="row"><span class="muted">方向</span><span>{{ card.competition_track }}</span></div>
            <div class="row">
              <span class="muted">人数</span>
              <span>{{ card.current_members }} / {{ card.target_size }}</span>
            </div>
            <div class="skills">
              <el-tag v-for="s in card.required_skills" :key="s" size="small" type="warning" effect="plain">
                {{ s }}
              </el-tag>
              <span v-if="!card.required_skills.length" class="muted">不限技能</span>
            </div>
          </div>
          <template #footer>
            <div class="flex-between">
              <el-button link type="primary" @click="router.push(`/recruitments`)">查看详情</el-button>
              <el-button type="primary" size="small" @click="apply(card)">申请加入</el-button>
            </div>
          </template>
        </el-card>
      </div>

      <el-empty v-if="!loading && !cards.length" description="暂无符合条件的招募信息" />

      <div class="pagination">
        <el-pagination
          v-model:current-page="page"
          :page-size="limit"
          :total="total"
          layout="prev, pager, next"
          background
          @current-change="onPageChange"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
.hero {
  background: linear-gradient(120deg, #312e81 0%, #4f46e5 55%, #7c3aed 100%);
  color: #fff; padding: 64px 24px;
}
.hero-inner { max-width: 1100px; margin: 0 auto; }
.hero h1 { font-size: 38px; margin: 0 0 12px; font-weight: 800; }
.hero p { font-size: 16px; opacity: .9; margin: 0 0 28px; }
.hero-actions { display: flex; gap: 12px; }
.team-card { min-height: 230px; }
.card-body .row { display: flex; justify-content: space-between; padding: 5px 0; font-size: 14px; }
.skills { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 12px; }
.pagination { display: flex; justify-content: center; margin-top: 24px; }
</style>
