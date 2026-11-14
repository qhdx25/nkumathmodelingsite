<script setup>
import { news, newsMore } from '../data/site'
</script>

<template>
  <main class="page">
    <section class="page-head">
      <div class="container">
        <h1>最新动态</h1>
        <p class="page-lead">
          协会与学院相关报道，按时间倒序排列。原文发布在南开新闻网、数学科学学院公众号或赛事官网。
        </p>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <ul class="news-archive">
          <li v-for="item in news" :key="item.title">
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

        <p class="section-foot">
          {{ newsMore.hint }}，新推送同步转载至此。需要补充条目，把「日期 / 标题 / 链接 / 摘要」给我即可。
        </p>
      </div>
    </section>
  </main>
</template>
