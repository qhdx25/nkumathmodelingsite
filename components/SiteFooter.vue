<script setup>
import { RouterLink } from 'vue-router'
import { campuses, footerLinks, nav, subNav } from '../data/site'
import { enFooter, enHeader } from '../data/en'

const props = defineProps({
  lang: { type: String, default: 'zh' },
})
const isEn = () => props.lang === 'en'

const enCampuses = [
  { name: 'Balitai Campus', address: '94 Weijin Road, Nankai District, Tianjin', postcode: '300071' },
  { name: 'Jinnan Campus', address: '38 Tongyan Road, Haihe Education Park, Tianjin', postcode: '300350' },
  { name: 'TEDA Campus', address: '23 Hongda Street, TEDA, Tianjin', postcode: '300457' },
]
</script>

<template>
  <footer class="site-footer">
    <div class="container footer-grid">
      <div class="footer-brand">
        <p class="footer-title">{{ isEn() ? enFooter.title : '南开大学数学建模协会' }}</p>
        <p v-if="isEn()" class="footer-desc">
          Student society of the School of Mathematical Sciences, founded in 2016.<br />
          Learning through contests, applying what we learn.
        </p>
        <p v-else class="footer-desc">
          成立于 2016 年，数学科学学院下属学生社团。<br />
          以赛促学，学以致用。
        </p>
      </div>

      <div class="footer-column">
        <strong>{{ isEn() ? enFooter.navTitle : '站点导航' }}</strong>
        <template v-if="isEn()">
          <RouterLink v-for="item in enHeader.nav" :key="item.label" :to="item.to">{{ item.label }}</RouterLink>
        </template>
        <template v-else>
          <RouterLink v-for="item in nav" :key="item.label" :to="item.to">{{ item.label }}</RouterLink>
        </template>
      </div>

      <div class="footer-column">
        <strong>{{ isEn() ? enFooter.moreTitle : '更多' }}</strong>
        <template v-if="isEn()">
          <RouterLink v-for="item in enHeader.topLinks" :key="item.label" :to="item.to">{{ item.label }}</RouterLink>
        </template>
        <template v-else>
          <RouterLink v-for="item in subNav" :key="item.label" :to="item.to">{{ item.label }}</RouterLink>
        </template>
        <a v-for="item in footerLinks" :key="item.label" :href="item.href" target="_blank" rel="noreferrer">
          {{ item.label }}
        </a>
      </div>

      <div class="footer-column footer-address">
        <strong>{{ isEn() ? enFooter.addressTitle : '校区地址' }}</strong>
        <p v-for="c in isEn() ? enCampuses : campuses" :key="c.name">
          <span class="addr-name">{{ c.name }}</span>
          <span class="addr-detail">{{ c.address }}{{ isEn() ? ' ' : '（' }}{{ c.postcode }}{{ isEn() ? '' : '）' }}</span>
        </p>
      </div>
    </div>

    <div class="container footer-bottom">
      <span class="footer-copy">{{ isEn() ? enFooter.copy : '© 2026 南开大学数学建模协会' }}</span>
      <span class="footer-motto">允公允能，日新月异</span>
      <span class="footer-demo">{{ isEn() ? enFooter.demo : 'Demo 预览版 · 部分数据为占位，待补充后上线' }}</span>
    </div>
  </footer>
</template>
