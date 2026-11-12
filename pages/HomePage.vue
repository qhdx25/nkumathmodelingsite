<script setup>
import { RouterLink } from 'vue-router'
import NewsFeed from '../components/NewsFeed.vue'
import { entries, intro, stats } from '../data/site'
</script>

<template>
  <main>
    <section class="hero">
      <div class="container hero-grid">
        <div class="hero-copy">
          <p class="kicker">南开大学数学建模协会 · 成立于 2016 年</p>
          <h1>
            用数学描述问题，<br />
            用模型检验答案。
          </h1>
          <p class="hero-lead">
            我们承办校内规模最大的数学建模赛事，服务全校 1200 余名参赛同学，
            组织培训、选拔与校际交流。一次建模，终身受益。
          </p>
          <div class="hero-actions">
            <RouterLink class="btn btn-solid" to="/competition">查看竞赛信息</RouterLink>
            <RouterLink class="btn btn-ghost" to="/materials">打开建模资料</RouterLink>
          </div>
        </div>

        <div class="hero-panel">
          <div class="stat-grid">
            <div v-for="item in stats" :key="item.label" class="stat-card">
              <p class="stat-value">{{ item.value }}</p>
              <p class="stat-label">{{ item.label }}</p>
              <p class="stat-note">{{ item.note }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="section">
      <div class="container intro-grid">
        <article v-for="item in intro" :key="item.title" class="intro-card">
          <p class="kicker">{{ item.kicker }}</p>
          <h3>{{ item.title }}</h3>
          <p>{{ item.body }}</p>
        </article>
      </div>
    </section>

    <NewsFeed />

    <section class="section section-entries">
      <div class="container">
        <div class="section-head">
          <div>
            <p class="kicker">快速入口</p>
            <h2>你可能在找</h2>
          </div>
        </div>

        <div class="entry-grid">
          <RouterLink v-for="item in entries" :key="item.title" class="entry-card" :to="item.to">
            <p class="card-kicker">{{ item.kicker }}</p>
            <h3>{{ item.title }}</h3>
            <p>{{ item.body }}</p>
            <span class="text-link">{{ item.action }} →</span>
          </RouterLink>
        </div>
      </div>
    </section>
  </main>
</template>
