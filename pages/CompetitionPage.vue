<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { RouterLink } from 'vue-router'
import { imgUrl } from '../assets/resolver'
import ContestCard from '../components/ContestCard.vue'
import PlaceholderBlock from '../components/PlaceholderBlock.vue'
import { calendar, contests, dataNote, points, results } from '../data/contests'

const openCount = contests.filter((item) => item.status === 'open').length

// 奖项分布：拆成「名称 + 数目」两列，排成账目式小清单；
// 金银铜只让数字带一点色，不做胶囊、不做圆点
function awardChips(detail) {
  if (!detail || detail === '—') return null
  const parts = detail.split('·').map((s) => s.trim()).filter(Boolean)
  if (!parts.some((p) => /金|银|铜/.test(p))) return null
  return parts.map((text) => {
    const m = text.match(/^(\D+?)\s*(\d[\d\s]*\D*)$/)
    return {
      name: m ? m[1].trim() : text,
      num: m ? m[2].trim() : '',
      cls: text.includes('金') ? 'gold' : text.includes('银') ? 'silver' : text.includes('铜') ? 'bronze' : 'plain',
    }
  })
}

// 纵向 cover-flow 堆叠：所有卡片物理叠在同一层，激活卡居中在顶，
// 相邻卡片上下露出一截压在下面，滚轮/箭头/圆点切换
const carouselEl = ref(null)
const activeIdx = ref(0)

function cellClass(i) {
  const off = i - activeIdx.value
  const abs = Math.abs(off)
  const side = off < 0 ? '-up' : '-down'
  if (off === 0) return 'pos-center'
  if (abs === 1) return 'pos' + side
  if (abs === 2) return 'pos-far' + side
  if (abs === 3) return 'pos-out' + side
  return 'pos-hide' + side
}

function go(i) {
  activeIdx.value = Math.max(0, Math.min(contests.length - 1, i))
}

// 牌堆重心补偿：第 1 张上面没有"上层卡"、最后一张下面没有"下层卡"，
// 若始终居中，首尾会一侧空一大截。按上下可用层数把整堆平移一点，让视觉重心居中。
const UP_EXT = [0, 103, 151] // 上层卡相对激活卡顶部的探出量（px）
const DOWN_EXT = [316, 461, 483] // 下层卡相对激活卡顶部的底部延伸量（px）
const stackShift = computed(() => {
  const up = Math.min(2, activeIdx.value)
  const down = Math.min(2, contests.length - 1 - activeIdx.value)
  const centerTop = 172
  const mid = centerTop + (DOWN_EXT[down] - UP_EXT[up]) / 2
  return Math.round(Math.max(-80, Math.min(46, 340 - mid)))
})

let wheelLock = 0
function onWheel(e) {
  const now = Date.now()
  if (now - wheelLock < 380 || Math.abs(e.deltaY) < 6) return
  wheelLock = now
  go(activeIdx.value + (e.deltaY > 0 ? 1 : -1))
}

function onCarouselKey(e) {
  if (e.key === 'ArrowUp') {
    e.preventDefault()
    go(activeIdx.value - 1)
  } else if (e.key === 'ArrowDown') {
    e.preventDefault()
    go(activeIdx.value + 1)
  }
}

// 触屏左右滑动切换（竖滑仍交给页面滚动，不拦截）
let touchX = 0
let touchY = 0
function onTouchStart(e) {
  const t = e.touches[0]
  if (!t) return
  touchX = t.clientX
  touchY = t.clientY
}
function onTouchEnd(e) {
  const t = e.changedTouches[0]
  if (!t) return
  const dx = t.clientX - touchX
  const dy = t.clientY - touchY
  if (Math.abs(dx) < 42 || Math.abs(dx) < Math.abs(dy) * 1.2) return
  go(activeIdx.value + (dx < 0 ? 1 : -1))
}

// 左侧页内导航：锚点滚动 + 滚动高亮
const sections = [
  { id: 'calendar', label: '竞赛日历' },
  { id: 'contests', label: '竞赛发布' },
  { id: 'results', label: '成绩公示' },
  { id: 'points', label: '积分公示' },
]
const activeSection = ref('calendar')

// 页头总高（信息条 + 主导航）；锚点滚动与吸顶偏移都以此为准
const HEAD_OFFSET = 152

function jumpTo(id) {
  const el = document.getElementById(id)
  if (!el) return
  window.scrollTo({ top: el.getBoundingClientRect().top + window.scrollY - HEAD_OFFSET, behavior: 'smooth' })
}

// 紫栏左缘的滑动书脊：跟随当前项上下移动（一条白色竖条，像书脊上的书签）
const spineEl = ref(null)
function syncSpine() {
  const bar = spineEl.value
  const on = document.querySelector('.comp-page .csn-link.is-on')
  if (!bar || !on) return
  bar.style.transform = `translateY(${on.offsetTop}px)`
  bar.style.height = `${on.offsetHeight}px`
  bar.classList.add('is-ok')
}
watch(activeSection, () => nextTick(syncSpine))

let spyPending = false
function onPageScroll() {
  if (spyPending) return
  spyPending = true
  requestAnimationFrame(() => {
    spyPending = false
    let current = sections[0].id
    for (const s of sections) {
      const el = document.getElementById(s.id)
      if (el && el.getBoundingClientRect().top <= 170) current = s.id
    }
    activeSection.value = current
    updateProgress()
  })
}

// 紫栏右侧滚动进度：读取 comp-body 的滚动比例写入 CSS 变量
function updateProgress() {
  const nav = document.querySelector('.comp-page .comp-side-nav')
  const body = document.querySelector('.comp-page .comp-body')
  if (!nav || !body) return
  const rect = body.getBoundingClientRect()
  const total = rect.height - window.innerHeight
  const p = total > 0 ? Math.min(1, Math.max(0, -rect.top / total)) : 0
  nav.style.setProperty('--sp', p.toFixed(4))
}

const reduceMotion = () => window.matchMedia('(prefers-reduced-motion: reduce)').matches

// 数字滚动：统计条进入时从 0 计数到目标值
function countUp() {
  document.querySelectorAll('.comp-page .stat-num').forEach((el, i) => {
    const target = Number(el.getAttribute('data-count') || 0)
    if (!target) { el.textContent = '0'; return }
    if (reduceMotion()) { el.textContent = String(target); return }
    const dur = 900
    window.setTimeout(() => {
      const t0 = performance.now()
      const tick = (t) => {
        const p = Math.min(1, (t - t0) / dur)
        const eased = 1 - Math.pow(1 - p, 3)
        el.textContent = String(Math.round(target * eased))
        if (p < 1) requestAnimationFrame(tick)
      }
      requestAnimationFrame(tick)
    }, 240 + i * 130)
  })
}

// 区块入场：进入视口淡入上移（一次性）
let revealIO = null
function setupReveal() {
  const els = [...document.querySelectorAll('.comp-page .page-head, .comp-page .section')]
  els.forEach((el) => el.classList.add('will-reveal'))
  revealIO = new IntersectionObserver((entries) => {
    entries.forEach((en) => {
      if (!en.isIntersecting) return
      en.target.classList.add('is-in')
      revealIO.unobserve(en.target)
    })
  }, { threshold: 0.05, rootMargin: '0px 0px -6% 0px' })
  els.forEach((el) => revealIO.observe(el))
}

// 表格行聚光：鼠标位置写入行内 CSS 变量
function onTableMove(e) {
  const tr = e.target instanceof Element ? e.target.closest('tr') : null
  if (!tr) return
  const r = tr.getBoundingClientRect()
  tr.style.setProperty('--mx', `${Math.round(e.clientX - r.left)}px`)
  tr.style.setProperty('--my', `${Math.round(e.clientY - r.top)}px`)
}

onMounted(async () => {
  window.addEventListener('scroll', onPageScroll, { passive: true })
  window.addEventListener('resize', onResize)
  await nextTick()
  onPageScroll()
  syncSpine()
  countUp()
  setupReveal()
  const wrap = document.querySelector('.comp-page .table-wrap')
  if (wrap) wrap.addEventListener('mousemove', onTableMove, { passive: true })
})
function onResize() {
  syncSpine()
  updateProgress()
}
onBeforeUnmount(() => {
  window.removeEventListener('scroll', onPageScroll)
  window.removeEventListener('resize', onResize)
  if (revealIO) revealIO.disconnect()
  const wrap = document.querySelector('.comp-page .table-wrap')
  if (wrap) wrap.removeEventListener('mousemove', onTableMove)
})
</script>

<template>
  <main class="page comp-page">
    <!-- 双栏：左侧页内导航（sticky）+ 右侧正文流 -->
    <div class="comp-body">
      <nav class="comp-side-nav" aria-label="本页导航">
        <div class="csn-inner">
          <span ref="spineEl" class="csn-spine" aria-hidden="true"></span>
          <RouterLink to="/" class="csn-brand">
            <span class="csn-brand-cn">南开大学<br />数学建模协会</span>
            <span class="csn-brand-en">Nankai MCM Association</span>
          </RouterLink>
          <p class="csn-title">本页</p>
          <ul class="csn-list">
            <li v-for="s in sections" :key="s.id">
              <button
                type="button"
                class="csn-link"
                :class="{ 'is-on': activeSection === s.id }"
                :aria-current="activeSection === s.id ? 'true' : undefined"
                @click="jumpTo(s.id)"
              >
                <span class="csn-txt">{{ s.label }}</span>
                <span class="csn-arrow" aria-hidden="true">→</span>
              </button>
            </li>
          </ul>
          <img class="csn-emblem" :src="imgUrl('/img/nku-mark.png')" alt="" aria-hidden="true" />
        </div>
        <span class="csn-progress" aria-hidden="true"></span>
      </nav>

      <div class="comp-flow">
        <section class="page-head">
          <div class="container">
            <p class="eyebrow">Competition · 2026—2027</p>
            <h1>竞赛信息与成绩公示</h1>
            <p class="page-lead">
              全年赛事节点、报名入口、校内选拔安排，以及成绩与积分公示一览。
              当前有 <strong>{{ openCount }}</strong> 项赛事处于报名期。
            </p>
            <div class="stat-strip">
              <div class="stat">
                <span class="stat-num" :data-count="contests.length">{{ contests.length }}</span>
                <span class="stat-label">全年赛事</span>
              </div>
              <div class="stat">
                <span class="stat-num" :data-count="openCount">{{ openCount }}</span>
                <span class="stat-label">报名中</span>
              </div>
              <div class="stat">
                <span class="stat-num" :data-count="results.length">{{ results.length }}</span>
                <span class="stat-label">成绩条目</span>
              </div>
            </div>
          </div>
        </section>

        <section class="section" id="calendar">
      <div class="container">
        <div class="section-head">
          <h2>竞赛日历</h2>
          <span class="head-note">图片制作中</span>
        </div>

        <div class="calendar-slot">
          <PlaceholderBlock
            :title="calendar.title"
            :desc="calendar.note"
            :requirement="calendar.requirement"
            ratio="3 / 2"
          />
        </div>

        <p class="section-foot">
          图片放入 <code>assets/calendar.png</code> 后替换本区块即可，不需要改其他代码。
        </p>
      </div>
    </section>

    <section class="section" id="contests">
      <div class="container">
        <div class="section-head">
          <h2>竞赛信息发布</h2>
          <span class="head-note">更新于 2026.11</span>
        </div>

        <div
          class="contest-carousel"
          ref="carouselEl"
          tabindex="0"
          :style="{ '--stack-shift': stackShift + 'px' }"
          aria-label="赛事列表，上下滚动或用方向键切换"
          @wheel.prevent="onWheel"
          @keydown="onCarouselKey"
          @touchstart.passive="onTouchStart"
          @touchend.passive="onTouchEnd"
        >
          <div class="carousel-inner" :style="{ transform: `translateY(${stackShift}px)` }">
            <div
              v-for="(item, i) in contests"
              :key="item.id"
              class="car-cell"
              :class="cellClass(i)"
            >
              <ContestCard :contest="item" />
            </div>
          </div>
          <div class="carousel-nav">
            <button
              type="button"
              class="car-btn"
              aria-label="上一个赛事"
              :disabled="activeIdx === 0"
              @click="go(activeIdx - 1)"
            >
              ↑
            </button>
            <div class="car-dots" role="group" aria-label="赛事切换圆点">
              <button
                v-for="(c, i) in contests"
                :key="c.id"
                type="button"
                class="car-dot"
                :class="{ 'is-on': i === activeIdx }"
                :aria-label="`查看 ${c.name}`"
                :aria-current="i === activeIdx ? 'true' : undefined"
                @click="go(i)"
              />
            </div>
            <button
              type="button"
              class="car-btn"
              aria-label="下一个赛事"
              :disabled="activeIdx === contests.length - 1"
              @click="go(activeIdx + 1)"
            >
              ↓
            </button>
          </div>
        </div>

        <p class="section-foot">{{ dataNote }}</p>
      </div>
    </section>

    <section class="section" id="results">
      <div class="container">
        <div class="section-head">
          <h2>成绩公示</h2>
          <span class="head-note">名单整理中</span>
        </div>

        <div class="table-wrap">
          <table class="data-table">
            <thead>
              <tr>
                <th>赛事</th>
                <th>时间</th>
                <th>结果概览</th>
                <th>奖项分布</th>
                <th>状态</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in results" :key="item.event">
                <td class="cell-strong">
                  {{ item.event }}
                  <span class="cell-note">{{ item.note }}</span>
                </td>
                <td data-label="时间">{{ item.time }}</td>
                <td data-label="结果">{{ item.summary }}</td>
                <td data-label="奖项">
                  <span v-if="awardChips(item.detail)" class="award-spec">
                    <span
                      v-for="(chip, i) in awardChips(item.detail)"
                      :key="i"
                      class="aw"
                      :class="chip.cls"
                    >
                      <span class="aw-name">{{ chip.name }}</span>
                      <span class="aw-num">{{ chip.num }}</span>
                    </span>
                  </span>
                  <span v-else class="cell-muted">{{ item.detail }}</span>
                </td>
                <td data-label="状态">
                  <span class="status-pill" :class="item.status === 'partial' ? 'status-partial' : 'status-pending'">
                    {{ item.statusText }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>

          <RouterLink class="notice-callout" to="/notice/cumcm-2026-award-draft">
            <span class="nc-tag">公示中</span>
            <span class="nc-main">
              <strong>2026 高教社杯国赛获奖名单（初稿）</strong>
              <span>45 页 · 公示期 2026-11-08 — 11-14 · 可站内逐页阅读或跳官方原文</span>
            </span>
            <span class="nc-go" aria-hidden="true">›</span>
          </RouterLink>
        </div>

        <div class="result-placeholder">
          <PlaceholderBlock
            title="获奖名单明细"
            desc="按赛事分组的完整名单：队伍编号、队名、队员、指导教师、奖项等级。"
            requirement="提供 Excel 或飞书表格链接即可，我来接成表格并支持按赛事筛选。"
            ratio="auto"
            compact
          />
        </div>
      </div>
    </section>

    <section class="section" id="points">
      <div class="container">
        <div class="section-head">
          <h2>积分公示</h2>
          <span class="head-note">整理中</span>
        </div>

        <p class="points-note">{{ points.note }}</p>

        <PlaceholderBlock
          :title="points.title"
          :desc="points.requirement"
          requirement="支持按姓名 / 赛事 / 学期筛选，建议保留历史累计列。"
          ratio="auto"
          compact
        />
      </div>
    </section>

    <section class="section">
      <div class="container">
        <div class="strip">
          <div>
            <h2>要补充或更正信息？</h2>
            <p>竞赛通知、获奖名单、积分明细都可以交给协会竞赛部更新。</p>
          </div>
          <RouterLink class="btn" to="/committee">联系委员会</RouterLink>
        </div>
      </div>
    </section>
      </div>
    </div>
  </main>
</template>
