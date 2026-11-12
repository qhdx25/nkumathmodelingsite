<script setup>
import { RouterLink } from 'vue-router'
import { news, newsMore } from '../data/site'
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
          <a class="head-link" :href="newsMore.url" target="_blank" rel="noreferrer">
            {{ newsMore.label }} →
          </a>
        </div>

        <ul class="list">
          <li v-for="item in news" :key="item.title">
            <a :href="item.url" target="_blank" rel="noreferrer" :title="item.source">
              <span class="list-title">{{ item.title }}</span>
              <time>{{ item.date }}</time>
            </a>
          </li>
        </ul>

        <p class="section-foot">{{ newsMore.hint }}，新推送同步转载至此。</p>
      </div>

      <div>
        <div class="section-head">
          <h2>通知公告</h2>
          <RouterLink class="head-link" to="/notice">全部公示 →</RouterLink>
        </div>

        <ul class="list">
          <li v-for="n in notices" :key="n.slug">
            <RouterLink :to="`/notice/${n.slug}`">
              <span class="list-tag">{{ catLabel[n.category] }}</span>
              <span class="list-title">{{ n.title }}</span>
              <time>{{ n.date }}</time>
            </RouterLink>
          </li>
        </ul>

        <p class="section-foot">成绩名单、会议纪要与公示文件，均可站内逐页阅读。</p>
      </div>
    </div>
  </section>
</template>
