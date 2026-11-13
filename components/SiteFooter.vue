<script setup>
import { RouterLink } from 'vue-router'
import { campuses, footerLinks, nav, subNav } from '../data/site'
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
        <strong>更多</strong>
        <RouterLink v-for="item in subNav" :key="item.label" :to="item.to">{{ item.label }}</RouterLink>
        <a v-for="item in footerLinks" :key="item.label" :href="item.href" target="_blank" rel="noreferrer">
          {{ item.label }}
        </a>
      </div>

      <div class="footer-column footer-address">
        <strong>校区地址</strong>
        <p v-for="c in campuses" :key="c.name">
          <span class="addr-name">{{ c.name }}</span>
          <span class="addr-detail">{{ c.address }}（{{ c.postcode }}）</span>
        </p>
      </div>
    </div>

    <div class="container footer-bottom">
      <span class="footer-copy">© 2026 南开大学数学建模协会</span>
      <span class="footer-motto">允公允能，日新月异</span>
      <span class="footer-demo">Demo 预览版 · 部分数据为占位，待补充后上线</span>
    </div>
  </footer>
</template>
