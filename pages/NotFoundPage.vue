<script setup>
import { RouterLink } from 'vue-router'
</script>

<template>
  <main class="page">
    <section class="page-head">
      <div class="container">
        <p class="kicker">404</p>
        <h1>这个页面不存在</h1>
        <p class="page-lead">链接可能已经更新，或者地址输错了。</p>
        <div class="intro-actions">
          <RouterLink class="btn btn-solid" to="/">回到首页</RouterLink>
          <RouterLink class="btn btn-ghost" to="/competition">查看竞赛信息</RouterLink>
        </div>
      </div>
    </section>
  </main>
</template>
