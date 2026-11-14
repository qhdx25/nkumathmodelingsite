<script setup>
import { RouterLink } from 'vue-router'
import VerticalTicker from './VerticalTicker.vue'
import { news } from '../data/site'
import { listNotices } from '../data/notices'

const notices = listNotices().slice(0, 6)
const catLabel = { award: '成绩', minutes: '纪要' }
</script>

<template>
  <section class="section" id="news">
    <div class="container dual">
      <div>
        <div class="section-head">
          <h2>最新动态</h2>
          <RouterLink class="head-link" to="/news">更多动态 →</RouterLink>
        </div>

        <VerticalTicker :items="news" :rows="4" :cell-height="46" :speed="12">
          <template #default="{ item }">
            <a class="news-cell" :href="item.url" target="_blank" rel="noreferrer">
              <span class="cell-title">{{ item.title }}</span>
              <time class="cell-date">{{ item.date }}</time>
            </a>
          </template>
        </VerticalTicker>
      </div>

      <div>
        <div class="section-head">
          <h2>通知公告</h2>
          <RouterLink class="head-link" to="/notice">全部公示 →</RouterLink>
        </div>

        <VerticalTicker :items="notices" :rows="4" :cell-height="46" :speed="12">
          <template #default="{ item }">
            <RouterLink class="notice-cell" :to="`/notice/${item.slug}`">
              <span class="cell-tag">{{ catLabel[item.category] }}</span>
              <span class="cell-title">{{ item.title }}</span>
              <time class="cell-date">{{ item.date }}</time>
            </RouterLink>
          </template>
        </VerticalTicker>
      </div>
    </div>
  </section>
</template>
