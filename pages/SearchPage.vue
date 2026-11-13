<script setup>
import { computed } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { news } from '../data/site'
import { notices } from '../data/notices'

const route = useRoute()
const keyword = computed(() => String(route.query.q || '').trim())

const pool = [
  ...news.map((item) => ({
    kind: '动态',
    title: item.title,
    date: item.fullDate || item.date,
    desc: item.summary || '',
    href: item.url || null,
    to: null,
  })),
  ...notices.map((item) => ({
    kind: '公示',
    title: item.title,
    date: item.date,
    desc: item.summary || item.sub || '',
    href: null,
    to: `/notice/${item.slug}`,
  })),
]

const hits = computed(() => {
  const q = keyword.value.toLowerCase()
  if (!q) return []
  return pool.filter((item) => `${item.title} ${item.desc}`.toLowerCase().includes(q))
})

const tags = ['建模', '美赛', '获奖', '纪要', '培训']
</script>

<template>
  <main class="page">
    <section class="page-head">
      <div class="container">
        <h1>站内搜索</h1>
        <p v-if="keyword" class="page-lead">“{{ keyword }}” 共找到 {{ hits.length }} 条结果</p>
        <p v-else class="page-lead">请输入关键词后回车，可检索协会动态与信息公示内容。</p>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <ul v-if="hits.length" class="news-archive search-list">
          <li v-for="item in hits" :key="item.title + item.date">
            <RouterLink v-if="item.to" :to="item.to">
              <time>{{ item.date }}</time>
              <div>
                <h3><span class="search-kind">{{ item.kind }}</span>{{ item.title }}</h3>
                <p>{{ item.desc }}</p>
              </div>
            </RouterLink>
            <a v-else :href="item.href" target="_blank" rel="noreferrer">
              <time>{{ item.date }}</time>
              <div>
                <h3><span class="search-kind">{{ item.kind }}</span>{{ item.title }}</h3>
                <p>{{ item.desc }}</p>
              </div>
            </a>
          </li>
        </ul>

        <p v-else-if="keyword" class="section-foot">
          没有匹配的内容。可以换个说法，或去
          <RouterLink to="/news">最新动态</RouterLink>
          与
          <RouterLink to="/notice">信息公示</RouterLink>
          里翻一翻。
        </p>
        <div v-else class="search-hint">
          <p>试试这些关键词：</p>
          <div class="search-tags">
            <RouterLink v-for="tag in tags" :key="tag" :to="{ path: '/search', query: { q: tag } }">{{ tag }}</RouterLink>
          </div>
        </div>
      </div>
    </section>
  </main>
</template>
