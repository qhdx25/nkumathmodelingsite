<script setup>
import { computed, ref } from 'vue'
import { RouterLink } from 'vue-router'
import HeroBanner from '../components/HeroBanner.vue'
import NavStrip from '../components/NavStrip.vue'
import VerticalTicker from '../components/VerticalTicker.vue'
import { banners, entries, news, stats } from '../data/site'
import { notices } from '../data/notices'

const tab = ref('news')

const toRow = (item) => {
  // 数据里新闻多为“年月”精度，统一用“月 / 年”两块，避免有的显示日、有的显示年
  const iso = item.fullDate || item.date || ''
  const m = String(iso).match(/(\d{4})[-.](\d{1,2})/)
  const parts = m
    ? { big: String(Number(m[2])).padStart(2, '0'), small: m[1] }
    : { big: '·', small: '' }
  return {
    title: item.title,
    date: parts,
    href: item.url || null,
    to: item.slug ? `/notice/${item.slug}` : null,
  }
}

const rows = computed(() =>
  tab.value === 'news' ? news.map(toRow) : notices.slice(0, 6).map(toRow),
)

const topics = [
  { title: '2027 美赛报名', note: '报名入口、时间节点与校内组队安排', to: '/competition', image: '/img/hero/nku-02.jpg' },
  { title: '校队训练体系', note: '从入门到国赛的三阶训练路径', to: '/training', image: '/img/hero/nku-03.jpg' },
  { title: '协会十周年', note: '十年回顾与历届赛事成绩', to: '/committee', image: '/img/hero/nku-05.jpg' },
]

const gallery = banners.slice(0, 6)
</script>

<template>
  <main>
    <HeroBanner :items="banners" />
    <NavStrip />

    <section class="home-news">
      <div class="container">
        <div class="news-tabs">
          <button type="button" :class="{ 'is-active': tab === 'news' }" @click="tab = 'news'">最新动态</button>
          <button type="button" :class="{ 'is-active': tab === 'notice' }" @click="tab = 'notice'">通知公告</button>
          <RouterLink class="news-more" :to="tab === 'news' ? '/news' : '/notice'">更多 &gt;</RouterLink>
        </div>

        <div class="news-grid">
          <div class="news-list">
            <VerticalTicker :key="tab" :items="rows" :rows="4" :cell-height="56" :speed="9">
              <template #default="{ item }">
                <a v-if="item.href" class="nku-row" :href="item.href" target="_blank" rel="noreferrer">
                  <span class="nku-date">
                    <b>{{ item.date.big }}</b>
                    <em>{{ item.date.small }}</em>
                  </span>
                  <span class="nku-title">{{ item.title }}</span>
                </a>
                <RouterLink v-else class="nku-row" :to="item.to || '/notice'">
                  <span class="nku-date">
                    <b>{{ item.date.big }}</b>
                    <em>{{ item.date.small }}</em>
                  </span>
                  <span class="nku-title">{{ item.title }}</span>
                </RouterLink>
              </template>
            </VerticalTicker>
          </div>

          <aside class="news-topics">
            <h3 class="topic-head">系列专题</h3>
            <ul>
              <li v-for="item in topics" :key="item.title">
                <RouterLink :to="item.to">
                  <img :src="item.image" alt="" loading="lazy" />
                  <span class="topic-copy">
                    <strong>{{ item.title }}</strong>
                    <em>{{ item.note }}</em>
                  </span>
                </RouterLink>
              </li>
            </ul>
          </aside>
        </div>
      </div>
    </section>

    <section class="about-band">
      <div class="container about-inner">
        <div class="about-head">
          <p class="about-kicker">协会概况</p>
          <h2>用数学描述问题<br />用模型检验答案</h2>
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
        </div>
      </div>
    </section>

    <section class="gallery-band" id="gallery">
      <div class="container">
        <div class="section-head">
          <h2>影像数模</h2>
          <RouterLink class="head-link" to="/news">更多动态 →</RouterLink>
        </div>
        <ul class="gallery-grid">
          <li v-for="(item, i) in gallery" :key="item.id" :class="`g-${i + 1}`">
            <img :src="item.image" :alt="item.credit || '南开校园'" loading="lazy" />
            <span class="gallery-credit">{{ item.credit }}</span>
          </li>
        </ul>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <div class="section-head">
          <h2>你可能在找</h2>
        </div>
        <div class="entries">
          <RouterLink v-for="item in entries" :key="item.title" class="entry" :to="item.to">
            <h3>{{ item.title }}</h3>
            <p>{{ item.body }}</p>
            <span class="entry-more">{{ item.action }} →</span>
          </RouterLink>
        </div>
      </div>
    </section>
  </main>
</template>
