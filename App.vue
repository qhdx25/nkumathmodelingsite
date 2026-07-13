<script setup>
import { RouterView } from 'vue-router'

import emblemUrl from './assets/nku-emblem.jpg'
import { footerLinks } from './site-data'

const navigation = [
  { label: '首页', href: '/' },
  { label: '南开概览', href: '/#overview' },
  { label: '数学底色', href: '/#mathematics' },
  { label: '协会框架', href: '/#association' },
  { label: '委员会', href: '/committee' },
  { label: '建模资料', href: '/materials' },
  { label: '资源中心', href: '/#resources' },
  { label: '校区信息', href: '/#campus' },
  { label: '联系我们', href: '#contact' },
]
</script>

<template>
  <div class="site-shell">
    <div class="page-grid" aria-hidden="true"></div>

    <RouterView />

    <footer id="contact" class="site-footer">
      <div class="container footer-grid">
        <div class="footer-links">
          <div class="footer-column">
            <strong>官方链接</strong>
            <a v-for="item in footerLinks" :key="item.label" :href="item.href" target="_blank" rel="noreferrer">
              {{ item.label }}
            </a>
          </div>

          <div class="footer-column">
            <strong>站点导航</strong>
            <a href="/">返回首页</a>
            <a href="/committee">委员会</a>
            <a href="/materials">建模资料</a>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>
