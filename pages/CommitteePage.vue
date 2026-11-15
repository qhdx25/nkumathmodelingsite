<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { history } from '../data/site'
import { listNotices } from '../data/notices'
import { rosterYears, rosters } from '../data/roster'

const minutes = listNotices('minutes')

const lv = [
  { title: '会员代表大会', desc: '协会最高议事机构，选举产生理事会。' },
  { title: '理事会', desc: '协会日常决策机构，向会员代表大会负责。' },
  { title: '常务理事会', desc: '理事会闭会期间的执行机构，统筹重大事项。' },
]

// 花名册学年切换
const year = ref(rosterYears[0])
const roster = computed(() => rosters[year.value])

function memberCount(dept) {
  return dept.rows.reduce((sum, row) => sum + row.names.length, 0)
}

// 主要负责人：行式列表 + 点击姓名弹出详情卡片
const leaderRows = computed(() => roster.value.leadership)
const activeLeader = ref(null)

function openLeader(p) {
  activeLeader.value = p
}
function closeLeader() {
  activeLeader.value = null
}
function onEsc(e) {
  if (e.key === 'Escape') closeLeader()
}
onMounted(() => window.addEventListener('keydown', onEsc))
onBeforeUnmount(() => window.removeEventListener('keydown', onEsc))
</script>

<template>
  <main class="page">
    <section class="page-head">
      <div class="container">
        <h1>组织架构与部门职责</h1>
        <p class="page-lead">
          协会在理事会领导下开展工作，下设秘书处与各职能部门、工作委员会办公室，
          并组建南开大学数学建模代表队（校代表队）。
        </p>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <div class="section-head">
          <h2>三级议事与执行</h2>
        </div>

        <ol class="level-list">
          <li v-for="(item, index) in lv" :key="item.title" class="level-item">
            <span class="level-index">{{ String(index + 1).padStart(2, '0') }}</span>
            <div>
              <h3>{{ item.title }}</h3>
              <p>{{ item.desc }}</p>
            </div>
          </li>
        </ol>
      </div>
    </section>

    <section class="section" id="roster">
      <div class="container">
        <div class="section-head">
          <h2>协会负责人与分工</h2>
          <div class="board-tabs" role="group" aria-label="学年切换">
            <button
              v-for="y in rosterYears"
              :key="y"
              type="button"
              class="chip"
              :class="{ 'is-active': year === y }"
              :aria-pressed="year === y"
              @click="year = y"
            >
              {{ rosters[y].label }}
            </button>
          </div>
        </div>

        <p class="council-line">
          <strong>常务理事会</strong>{{ roster.council.join('、') }}
        </p>
        <p v-if="roster.councilNote" class="council-note">{{ roster.councilNote }}</p>
        <p v-if="roster.councilFull" class="council-line">
          <strong>理事会（{{ roster.councilFull.length }} 人）</strong>{{ roster.councilFull.join('、') }}
        </p>

        <ul class="leader-rows">
          <li v-for="p in leaderRows" :key="p.name + p.role">
            <button
              type="button"
              class="leader-name-btn"
              :aria-label="`查看 ${p.name} 的详细信息`"
              @click="openLeader(p)"
            >
              {{ p.name }}
            </button>
            <span class="leader-role-cell">{{ p.role }}</span>
            <span class="leader-duty-cell">{{ p.duty }}</span>
          </li>
        </ul>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <div class="section-head">
          <h2>部门设置与成员名单</h2>
          <span class="head-note">{{ roster.label }} · 共 {{ roster.departments.length }} 个部门</span>
        </div>

        <div class="org-grid">
          <article v-for="dept in roster.departments" :key="dept.name" class="org-block">
            <h3>{{ dept.name }}<span class="org-count">{{ memberCount(dept) }} 人</span></h3>
            <dl class="org-rows">
              <div
                v-for="row in dept.rows"
                :key="row.role"
                class="org-row"
                :class="{ 'is-head': row.role.includes('副主席') || row.role.includes('负责人') }"
              >
                <dt>{{ row.role }}</dt>
                <dd v-if="row.names.length">{{ row.names.join('、') }}</dd>
                <dd v-else class="org-empty">{{ row.empty || '待补' }}</dd>
              </div>
            </dl>
          </article>
        </div>

        <p class="section-foot">
          名单转录自《南开大学数学建模协会（校代表队）理事干事花名册》，按学年更新；
          空缺职务以协会后续通知为准。
        </p>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <div class="org-grid">
          <article class="org-block">
            <h3>{{ roster.league.title }}<span class="org-count">团务</span></h3>
            <dl class="org-rows">
              <div
                v-for="row in roster.league.rows"
                :key="row.role"
                class="org-row"
                :class="{ 'is-head': row.role.includes('书记') }"
              >
                <dt>{{ row.role }}</dt>
                <dd v-if="row.names.length">{{ row.names.join('、') }}</dd>
                <dd v-else class="org-empty">{{ row.empty || '待补' }}</dd>
              </div>
            </dl>
          </article>

          <article class="org-block">
            <h3>{{ roster.team.title }}<span class="org-count">{{ memberCount(roster.team) }} 人</span></h3>
            <dl class="org-rows">
              <div
                v-for="row in roster.team.rows"
                :key="row.role"
                class="org-row"
                :class="{ 'is-head': row.role.includes('队长') }"
              >
                <dt>{{ row.role }}</dt>
                <dd v-if="row.names.length">{{ row.names.join('、') }}</dd>
                <dd v-else class="org-empty">{{ row.empty || '待补' }}</dd>
              </div>
            </dl>
          </article>
        </div>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <div class="section-head">
          <h2>历次会议记录</h2>
          <RouterLink class="head-link" to="/notice">全部公示文件 →</RouterLink>
        </div>

        <ul class="minutes-list">
          <li v-for="n in minutes" :key="n.slug">
            <RouterLink :to="`/notice/${n.slug}`">
              <time>{{ n.date }}</time>
              <span class="ml-title">{{ n.title }}</span>
              <span class="ml-sub">{{ n.sub }}</span>
              <span class="ml-go" aria-hidden="true">›</span>
            </RouterLink>
          </li>
        </ul>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <div class="section-head">
          <h2>南开数学与协会</h2>
          <span class="head-note">学科沿革</span>
        </div>

        <ol class="timeline">
          <li v-for="h in history" :key="h.year">
            <span class="tl-year">{{ h.year }}</span>
            <div>
              <h3>{{ h.title }}</h3>
              <p>{{ h.desc }}</p>
            </div>
          </li>
        </ol>
      </div>
    </section>
  </main>

  <!-- 负责人详情弹窗 -->
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="activeLeader" class="modal-overlay" @click.self="closeLeader">
        <div class="leader-modal" role="dialog" aria-modal="true" :aria-label="activeLeader.name">
          <button type="button" class="modal-close" aria-label="关闭" @click="closeLeader">×</button>
          <span class="lm-name">{{ activeLeader.name }}</span>
          <span class="lm-role">{{ activeLeader.role }}</span>
          <p class="lm-duty">{{ activeLeader.duty }}</p>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>
