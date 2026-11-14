<script setup>
import { computed, ref } from 'vue'
import { RouterLink } from 'vue-router'
import HeroBanner from '../components/HeroBanner.vue'
import NavStrip from '../components/NavStrip.vue'
import VerticalTicker from '../components/VerticalTicker.vue'
import { banners, news, series, stats } from '../data/site'
import { notices } from '../data/notices'
import { contests, seasonNodes } from '../data/contests'
import { resources } from '../data/training'
import { groups } from '../data/materials'

// 倒计时条：取 seasonNodes 里下一个尚未过去的时间节点，自动更新
const NOW = Date.now()
const upcomingNode = seasonNodes
  .map((n) => ({ ...n, ts: new Date(`${n.date}T00:00:00+08:00`).getTime() }))
  .filter((n) => n.ts + 86400000 >= NOW)
  .sort((a, b) => a.ts - b.ts)[0]
const daysLeft = upcomingNode ? Math.max(0, Math.ceil((upcomingNode.ts - NOW) / 86400000)) : 0

// 距今天 14 天内的动态标成「进行中」，左侧加紫色竖条
const FRESH_DAYS = 14
const daysAgo = (iso) => {
  const t = new Date(`${String(iso).replace(/\./g, '-')}T00:00:00+08:00`).getTime()
  return Number.isNaN(t) ? null : Math.floor((NOW - t) / 86400000)
}

const tab = ref('news')
const sideTab = ref('contest')
const side2Tab = ref('committee')

// 两条重点动态：封面图取自公众号原文
const featured = [
  {
    title: '第一届天津市五校数学建模联赛答辩会议顺利举行',
    date: '2026/10/27',
    image: '/img/news/wx-league.jpg',
    url: 'https://mp.weixin.qq.com/s/QvMJ6zMx8FKFsZCF2uSpGg',
  },
  {
    title: '2026 年“华为杯”研究生数学建模竞赛报名通知',
    date: '2026/06/02',
    image: '/img/news/wx-huawei.jpg',
    url: 'https://mp.weixin.qq.com/s/PWx5VBaqAiTaTf3_MALPYw',
  },
]

const newsRows = computed(() =>
  news.map((item) => {
    const iso = item.fullDate || item.date || ''
    const m = String(iso).match(/(\d{4})[-.](\d{1,2})[-.](\d{1,2})/)
    const ymd = String(iso).match(/(\d{4})[-.](\d{1,2})/)
    const ago = daysAgo(item.fullDate || item.date || '')
    return {
      title: item.title,
      day: m ? m[3] : ymd ? ymd[2] : '·',
      month: m ? `${m[2]}月` : ymd ? `${ymd[1]}` : '',
      href: item.url || null,
      fresh: ago !== null && ago >= 0 && ago <= FRESH_DAYS,
    }
  }),
)

const noticeRows = computed(() =>
  notices.map((item) => {
    const m = String(item.date || '').match(/(\d{4})-(\d{2})-(\d{2})/)
    return {
      title: item.title,
      day: m ? m[3] : '·',
      yearMonth: m ? `${m[1]}-${m[2]}` : item.date,
      to: `/notice/${item.slug}`,
    }
  }),
)

// 赛事日历：按日期升序，大日期 + 小字赛事名
const calendarRows = computed(() =>
  [...seasonNodes]
    .sort((a, b) => a.date.localeCompare(b.date))
    .map((item) => {
      const m = item.date.match(/(\d{4})-(\d{2})-(\d{2})/)
      return {
        title: item.name,
        tag: item.tag,
        day: m[3],
        yearMonth: `${m[1]}-${m[2]}`,
        to: item.link,
      }
    }),
)

// 左侧大图 + 右侧三组列表（对标官网「媒体南开 / 校情通报 / 干部选任」那一块）
const fmtMeta = (raw) => {
  const text = String(raw || '')
  const m = text.match(/(\d{4})-(\d{2})-(\d{2})/)
  if (m) return `截止 ${m[1]}.${m[2]}.${m[3]}`
  return text
}
const sideGroups = {
  contest: contests.slice(0, 6).map((item) => ({
    label: item.name,
    meta: fmtMeta(item.registerBy || item.window || item.level),
  })),
  training: resources.map((item) => ({
    label: item.label,
    meta: item.status === 'ok' ? '可访问' : '待补充',
  })),
  material: groups.map((g) => ({
    label: g.title,
    meta: `${g.items.length} 项`,
  })),
}
const sideList = computed(() => sideGroups[sideTab.value] || [])
const sideLinks = { contest: '/competition', training: '/training', material: '/materials' }

// 第二组：组织架构 / 组队平台 / 影像数模
const side2Groups = {
  committee: [
    { label: '会员代表大会', meta: '最高权力机构' },
    { label: '理事会 · 常务理事会', meta: '决策机构' },
    { label: '秘书处（策划室 / 办公室 / 财务室）', meta: '执行' },
    { label: '竞赛部', meta: '赛事承办' },
    { label: '宣传部', meta: '内容与视觉' },
    { label: '工作委员会', meta: '专项工作' },
  ],
  team: [
    { label: '发布招募信息', meta: '缺队友时发这里' },
    { label: '寻找队友', meta: '按方向筛选' },
    { label: '往届组队记录', meta: '2024 起' },
    { label: '组队交流群', meta: '飞书群' },
  ],
  gallery: [
    { label: '招新现场', meta: '待补充' },
    { label: '培训与模拟赛', meta: '待补充' },
    { label: '五校联赛答辩', meta: '待补充' },
    { label: '颁奖与合影', meta: '待补充' },
  ],
}
const side2List = computed(() => side2Groups[side2Tab.value] || [])
const side2Links = { committee: '/committee', team: '/team', gallery: '/#gallery' }

// 系列专题：一次显示 3 张，可左右翻 + 圆点
const SERIES_VISIBLE = 3
const seriesIndex = ref(0)
const seriesPages = computed(() => Math.max(1, series.length - SERIES_VISIBLE + 1))
const seriesShown = computed(() => series.slice(seriesIndex.value, seriesIndex.value + SERIES_VISIBLE))
function seriesGo(step) {
  const max = seriesPages.value
  seriesIndex.value = (seriesIndex.value + step + max) % max
}
</script>

<template>
  <main class="home">
    <HeroBanner :items="banners" />
    <NavStrip />

    <div v-if="upcomingNode" class="countdown">
      <div class="container countdown-inner">
        <span class="countdown-dot" aria-hidden="true" />
        <p class="countdown-text">
          距 <strong>{{ upcomingNode.name }}</strong> 还有
          <b>{{ daysLeft }}</b> 天
        </p>
        <span class="countdown-tag">{{ upcomingNode.tag }}</span>
        <RouterLink class="countdown-more" :to="upcomingNode.link">查看赛事 →</RouterLink>
      </div>
    </div>

    <section class="home-news">
      <div class="container">
        <div class="news-tabs">
          <button type="button" :class="{ 'is-active': tab === 'news' }" @click="tab = 'news'">最新动态</button>
          <button type="button" :class="{ 'is-active': tab === 'notice' }" @click="tab = 'notice'">通知公告</button>
          <button type="button" :class="{ 'is-active': tab === 'calendar' }" @click="tab = 'calendar'">赛事日历</button>
          <RouterLink
            class="news-more"
            :to="tab === 'news' ? '/news' : tab === 'notice' ? '/notice' : '/competition'"
          >更多 &gt;</RouterLink>
        </div>

        <!-- 最新动态：左两张图文卡 + 右日期列表 -->
        <div v-if="tab === 'news'" class="news-main">
          <div class="feature-pair">
            <a
              v-for="item in featured"
              :key="item.url"
              class="feature-card"
              :href="item.url"
              target="_blank"
              rel="noreferrer"
            >
              <span class="feature-media"><img :src="item.image" alt="" /></span>
              <span class="feature-body">
                <span class="feature-title">{{ item.title }}</span>
                <span class="feature-foot">
                  <svg class="icon-clock" viewBox="0 0 24 24" width="13" height="13" aria-hidden="true">
                    <circle cx="12" cy="12" r="8.4" fill="none" stroke="currentColor" stroke-width="1.6" />
                    <path d="M12 7.6V12l3 1.8" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" />
                  </svg>
                  <time>{{ item.date }}</time>
                  <span class="feature-arrow">→</span>
                </span>
              </span>
            </a>
          </div>

          <div class="date-list">
            <VerticalTicker :items="newsRows" :rows="4" :cell-height="56" :speed="9">
              <template #default="{ item }">
                <a
                  v-if="item.href"
                  class="date-row"
                  :class="{ 'is-fresh': item.fresh }"
                  :href="item.href"
                  target="_blank"
                  rel="noreferrer"
                >
                  <span class="date-box"><b>{{ item.day }}</b><em>{{ item.month }}</em></span>
                  <span class="date-title">{{ item.title }}</span>
                </a>
              </template>
            </VerticalTicker>
            <div class="list-foot">
              <RouterLink class="date-more" to="/news">查看全部动态 →</RouterLink>
              <span class="data-stamp">数据截至 2026-11</span>
            </div>
          </div>
        </div>

        <!-- 通知公告：三列灰底格 -->
        <ul v-else-if="tab === 'notice'" class="notice-grid">
          <li v-for="item in noticeRows" :key="item.to">
            <RouterLink :to="item.to">
              <span class="notice-date">
                <b>{{ item.day }}</b>
                <em>{{ item.yearMonth }}</em>
              </span>
              <span class="notice-cell-title">{{ item.title }}</span>
            </RouterLink>
          </li>
        </ul>

        <!-- 赛事日历：按日期升序，大日期 + 小字赛事名 -->
        <ul v-else class="notice-grid">
          <li v-for="item in calendarRows" :key="item.title">
            <RouterLink :to="item.to">
              <span class="notice-date">
                <b>{{ item.day }}</b>
                <em>{{ item.yearMonth }}</em>
              </span>
              <span class="cal-text">
                <span class="notice-cell-title">{{ item.title }}</span>
                <span class="cal-tag">{{ item.tag }}</span>
              </span>
            </RouterLink>
          </li>
        </ul>
      </div>
    </section>

    <!-- 系列专题：整幅紫底带，居中标题 + 右侧更多 + 三张横排图卡（可翻页） -->
    <section class="series-band">
      <div class="container">
        <div class="series-head">
          <h2>系列专题</h2>
          <RouterLink class="head-more" to="/news">更多 &gt;</RouterLink>
        </div>

        <div class="series-wrap">
          <button type="button" class="series-arrow is-prev" aria-label="上一组" @click="seriesGo(-1)">
            <svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true">
              <path d="m14.5 5-7 7 7 7" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
          </button>

          <ul class="series-grid">
            <li v-for="item in seriesShown" :key="item.title">
              <RouterLink :to="item.to">
                <span class="series-media">
                  <img :src="item.image" :alt="item.title" />
                  <span class="series-tag">{{ item.tag }}</span>
                </span>
                <span class="series-title">{{ item.title }}</span>
                <span class="series-note">{{ item.note }}</span>
              </RouterLink>
            </li>
          </ul>

          <button type="button" class="series-arrow is-next" aria-label="下一组" @click="seriesGo(1)">
            <svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true">
              <path d="m9.5 5 7 7-7 7" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
          </button>
        </div>

        <div class="series-dots">
          <button
            v-for="n in seriesPages"
            :key="n"
            type="button"
            :class="{ 'is-active': seriesIndex === n - 1 }"
            :aria-label="`第 ${n} 组`"
            @click="seriesIndex = n - 1"
          />
        </div>
      </div>
    </section>

    <!-- 左图 + 右三组列表：赛事 / 培训 / 资料 -->
    <section class="side-band">
      <div class="container side-inner">
        <figure class="side-figure">
          <img src="/img/news/wx-league.jpg" alt="五校联赛答辩会现场" />
          <figcaption>第一届天津市五校数学建模联赛答辩会 · 2026.10</figcaption>
        </figure>

        <div class="side-panel">
          <div class="side-tabs">
            <button type="button" :class="{ 'is-active': sideTab === 'contest' }" @click="sideTab = 'contest'">赛事速递</button>
            <button type="button" :class="{ 'is-active': sideTab === 'training' }" @click="sideTab = 'training'">培训资源</button>
            <button type="button" :class="{ 'is-active': sideTab === 'material' }" @click="sideTab = 'material'">建模资料</button>
            <RouterLink class="side-more" :to="sideLinks[sideTab]">更多 &gt;</RouterLink>
          </div>
          <ul class="side-list">
            <li v-for="item in sideList" :key="item.label">
              <RouterLink :to="sideLinks[sideTab]">
                <span class="side-label">{{ item.label }}</span>
                <span class="side-meta">{{ item.meta }}</span>
              </RouterLink>
            </li>
          </ul>
          <p class="data-stamp">数据截至 2026-11</p>
        </div>
      </div>
    </section>

    <!-- 第二组：组织架构 / 组队平台 / 影像数模 -->
    <section class="side-band side-band-alt">
      <div class="container side-inner">
        <div class="side-panel">
          <div class="side-tabs">
            <button type="button" :class="{ 'is-active': side2Tab === 'committee' }" @click="side2Tab = 'committee'">组织架构</button>
            <button type="button" :class="{ 'is-active': side2Tab === 'team' }" @click="side2Tab = 'team'">组队平台</button>
            <button type="button" :class="{ 'is-active': side2Tab === 'gallery' }" @click="side2Tab = 'gallery'">影像数模</button>
            <RouterLink class="side-more" :to="side2Links[side2Tab]">更多 &gt;</RouterLink>
          </div>
          <ul class="side-list">
            <li v-for="item in side2List" :key="item.label">
              <RouterLink :to="side2Links[side2Tab]">
                <span class="side-label">{{ item.label }}</span>
                <span class="side-meta">{{ item.meta }}</span>
              </RouterLink>
            </li>
          </ul>
          <p class="data-stamp">数据截至 2026-11 · 名单以最新公示为准</p>
        </div>

        <figure class="side-figure">
          <img src="/img/hero/nku-06.jpg" alt="南开大学主楼" />
          <figcaption>南开大学主楼 · 晚霞</figcaption>
        </figure>
      </div>
    </section>

    <section class="about-band">
      <div class="container about-inner">
        <div class="about-head">
          <p class="about-kicker">协会概况</p>
          <h2 class="about-slogan">
            <span class="l1">用数学描述问题</span>
            <span class="l2">用模型检验答案</span>
          </h2>
        </div>
        <div class="about-body">
          <p>
            南开大学数学建模协会成立于 2016 年，是数学科学学院下属学生社团。
            我们承办校内规模最大的数学建模赛事，服务全校 1200 余名参赛同学，
            并组织培训、选拔与校际交流。
          </p>
          <div class="about-cards">
            <div v-for="item in stats" :key="item.value" class="about-card">
              <p class="about-num">{{ item.value }}</p>
              <p class="about-label">{{ item.label }}</p>
              <p class="about-note">{{ item.note }}</p>
            </div>
          </div>
          <p class="data-stamp">数据截至 2026-11 · 由协会秘书处维护</p>
        </div>
      </div>
    </section>

    <section class="gallery-band" id="gallery">
      <div class="container">
        <div class="section-head">
          <h2>影像数模</h2>
          <span class="head-note">协会活动照片整理中 · 更新至 2026-11</span>
        </div>
        <div class="gallery-empty">
          <p>这里将放协会自己的活动照片</p>
          <p class="gallery-empty-hint">招新、培训、模拟赛、五校联赛答辩、颁奖现场等，待照片汇总后按时间排列</p>
        </div>
      </div>
    </section>
  </main>
</template>
