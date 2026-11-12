<script setup>
import { computed } from 'vue'
import { news, newsMore } from '../data/site'

const featured = computed(() => news.find((item) => item.featured) || news[0])
const rest = computed(() => news.filter((item) => item !== featured.value).slice(0, 4))
</script>

<template>
  <section class="news-section" id="news">
    <div class="container">
      <div class="section-head">
        <div>
          <p class="kicker">最新动态</p>
          <h2>协会与学院要闻</h2>
        </div>
        <a class="head-link" :href="newsMore.url" target="_blank" rel="noreferrer">
          {{ newsMore.label }} →
        </a>
      </div>

      <div class="news-grid">
        <article class="news-featured">
          <div class="news-visual" aria-hidden="true">
            <svg viewBox="0 0 320 200" preserveAspectRatio="none">
              <g stroke="#710a53" stroke-width="0.5" opacity="0.12">
                <path v-for="i in 8" :key="'h' + i" :d="`M0 ${i * 25} H320`" />
                <path v-for="i in 12" :key="'v' + i" :d="`M${i * 27} 0 V200`" />
              </g>
              <path
                d="M12 168 C60 150 84 108 118 104 C150 100 168 130 200 112 C232 94 258 52 308 34"
                fill="none"
                stroke="#710a53"
                stroke-width="1.6"
                stroke-linecap="round"
                opacity="0.7"
              />
              <g fill="#cfa972">
                <circle cx="118" cy="104" r="3.5" />
                <circle cx="200" cy="112" r="3.5" />
                <circle cx="308" cy="34" r="3.5" />
              </g>
            </svg>
          </div>

          <div class="news-featured-body">
            <p class="news-meta">
              <span>{{ featured.date }}</span>
              <span class="dot">·</span>
              <span>{{ featured.source }}</span>
            </p>
            <h3>{{ featured.title }}</h3>
            <p class="news-summary">{{ featured.summary }}</p>
            <a class="text-link" :href="featured.url" target="_blank" rel="noreferrer">阅读原文 →</a>
          </div>
        </article>

        <ul class="news-list">
          <li v-for="item in rest" :key="item.title">
            <a :href="item.url" target="_blank" rel="noreferrer">
              <time>{{ item.date }}</time>
              <span class="news-list-title">{{ item.title }}</span>
              <span class="news-source">{{ item.source }}</span>
            </a>
          </li>
        </ul>
      </div>

      <p class="news-hint">
        {{ newsMore.hint }}
      </p>
    </div>
  </section>
</template>
