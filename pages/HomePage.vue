<script setup>
import { RouterLink } from 'vue-router'
import HeroSlider from '../components/HeroSlider.vue'
import NewsFeed from '../components/NewsFeed.vue'
import VerticalTicker from '../components/VerticalTicker.vue'
import { banners, entries, intro, stats } from '../data/site'
</script>

<template>
  <main>
    <HeroSlider :items="banners" />

    <section class="section">
      <div class="container intro">
        <div>
          <h1>
            用数学描述问题，<br />
            <em>用模型检验答案。</em>
          </h1>
          <p>
            南开大学数学建模协会成立于 2016 年，是数学科学学院下属学生社团。
            我们承办校内规模最大的数学建模赛事，服务全校 1200 余名参赛同学，
            并组织培训、选拔与校际交流。
          </p>
          <div class="intro-actions">
            <RouterLink class="btn btn-solid" to="/competition">查看竞赛信息</RouterLink>
            <RouterLink class="btn btn-ghost" to="/materials">打开建模资料</RouterLink>
          </div>
        </div>

        <VerticalTicker :items="stats" :rows="2" :cell-height="84" :speed="14">
          <template #default="{ item }">
            <div class="stat">
              <p class="stat-v">{{ item.value }}</p>
              <div class="stat-txt">
                <p class="stat-l">{{ item.label }}</p>
                <p class="stat-n">{{ item.note }}</p>
              </div>
            </div>
          </template>
        </VerticalTicker>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <div class="section-head">
          <h2>协会概况</h2>
          <RouterLink class="head-link" to="/committee">组织架构 →</RouterLink>
        </div>

        <div class="facts">
          <div v-for="item in intro" :key="item.title">
            <p class="kicker">{{ item.kicker }}</p>
            <h3>{{ item.title }}</h3>
            <p>{{ item.body }}</p>
          </div>
        </div>
      </div>
    </section>

    <NewsFeed />

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
