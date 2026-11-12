<script setup>
import { RouterLink } from 'vue-router'
import { footerLinks, nav } from '../data/site'
</script>

<template>
  <footer class="site-footer">
    <div class="container footer-grid">
      <div class="footer-brand">
        <p class="footer-title">南开大学数学建模协会</p>
        <p class="footer-desc">
          成立于 2016 年，数学科学学院下属学生社团。<br />
          以赛促学，学以致用。
        </p>
      </div>

      <div class="footer-column">
        <strong>站点导航</strong>
        <RouterLink v-for="item in nav" :key="item.label" :to="item.to">{{ item.label }}</RouterLink>
      </div>

      <div class="footer-column">
        <strong>官方链接</strong>
        <a v-for="item in footerLinks" :key="item.label" :href="item.href" target="_blank" rel="noreferrer">
          {{ item.label }}
        </a>
      </div>
    </div>

    <div class="container footer-bottom">
      <span>© 2026 南开大学数学建模协会</span>
      <span class="demo-tag">Demo 预览版 · 部分数据为占位，待补充后上线</span>
    </div>
  </footer>
</template>
