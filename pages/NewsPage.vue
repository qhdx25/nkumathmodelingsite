<script setup>
import { computed } from 'vue'
import PageRail from '../components/PageRail.vue'
import { news, newsMore, newsSources } from '../data/site'

const sections = [
  { id: 'latest', label: '要闻' },
  { id: 'y2026', label: '2026' },
  { id: 'y2025', label: '2025' },
  { id: 'sources', label: '资料来源' },
]

const sorted = computed(() => news.slice().sort((a, b) => (a.ym < b.ym ? 1 : -1)))
const featured = computed(() => sorted.value.find((n) => n.featured) || sorted.value[0])
const rest = computed(() => sorted.value.filter((n) => n !== featured.value))
const y2026 = computed(() => rest.value.filter((n) => n.ym.startsWith('2026')))
const y2025 = computed(() => rest.value.filter((n) => n.ym.startsWith('2025')))
const total = computed(() => news.length)
const years = computed(() => new Set(news.map((n) => n.ym.slice(0, 4))).size)
</script>

<template>
  <main class="page comp-page news-page">
    <div class="comp-body">
      <PageRail :sections="sections" />

      <div class="comp-flow">
        <section class="page-head">
          <div class="container">
            <p class="eyebrow">News · 2025—2026</p>
            <h1>最新动态</h1>
            <p class="page-lead">
              协会与学院相关的报道、通知与获奖记录，按时间倒序排列。每条均来自南开新闻网、
              数学科学学院官网、「南开数院学工」公众号或本地媒体，可点原文核对。
              目前已收录 <strong>{{ total }}</strong> 条。
            </p>
            <div class="stat-strip">
              <div class="stat">
                <p class="stat-num">{{ total }}</p>
                <p class="stat-label">收录条目</p>
              </div>
              <div class="stat">
                <p class="stat-num">{{ years }}</p>
                <p class="stat-label">覆盖年份</p>
              </div>
              <div class="stat">
                <p class="stat-num">{{ newsSources.length }}</p>
                <p class="stat-label">信息来源</p>
              </div>
            </div>
          </div>
        </section>

        <section id="latest" class="section">
          <div class="container">
            <div class="section-head">
              <h2>要闻</h2>
              <span class="head-note">{{ featured.date }}</span>
            </div>

            <a class="lead-story" :href="featured.url" target="_blank" rel="noreferrer">
              <p class="lead-story-meta">
                <span class="lead-story-tag">{{ featured.tag }}</span>
                <time>{{ featured.date }}</time>
                <span class="lead-story-src">{{ featured.source }}</span>
              </p>
              <h3>{{ featured.title }}</h3>
              <p class="lead-story-sum">{{ featured.summary }}</p>
              <span class="lead-story-go">阅读原文 ↗</span>
            </a>
          </div>
        </section>

        <section id="y2026" class="section">
          <div class="container">
            <div class="section-head">
              <h2>2026 年</h2>
              <span class="head-note">{{ y2026.length }} 条</span>
            </div>
            <ul class="news-archive comp-archive">
              <li v-for="item in y2026" :key="item.title">
                <a :href="item.url" target="_blank" rel="noreferrer">
                  <time>{{ item.date }}</time>
                  <div>
                    <h3>{{ item.title }}</h3>
                    <p>{{ item.summary }}</p>
                    <span class="src">{{ item.source }} ↗</span>
                  </div>
                </a>
              </li>
            </ul>
          </div>
        </section>

        <section id="y2025" class="section">
          <div class="container">
            <div class="section-head">
              <h2>2025 年</h2>
              <span class="head-note">{{ y2025.length }} 条</span>
            </div>
            <ul class="news-archive comp-archive">
              <li v-for="item in y2025" :key="item.title">
                <a :href="item.url" target="_blank" rel="noreferrer">
                  <time>{{ item.date }}</time>
                  <div>
                    <h3>{{ item.title }}</h3>
                    <p>{{ item.summary }}</p>
                    <span class="src">{{ item.source }} ↗</span>
                  </div>
                </a>
              </li>
            </ul>
          </div>
        </section>

        <section id="sources" class="section">
          <div class="container">
            <div class="section-head">
              <h2>资料来源</h2>
              <span class="head-note">{{ newsMore.hint }}</span>
            </div>
            <ul class="source-list">
              <li v-for="s in newsSources" :key="s.label">
                <a :href="s.url" target="_blank" rel="noreferrer">
                  <strong>{{ s.label }}</strong>
                  <span>{{ s.note }}</span>
                  <em aria-hidden="true">↗</em>
                </a>
              </li>
            </ul>
            <p class="section-foot">
              条目为人工整理：日期取自原文发稿时间，摘要做了压缩；如发现与原文不符，指出条目即可更正。
            </p>
          </div>
        </section>
      </div>
    </div>
  </main>
</template>
