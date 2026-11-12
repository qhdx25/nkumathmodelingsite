<script setup>
import { RouterLink } from 'vue-router'
import { nav } from '../data/site'
</script>

<template>
  <div class="topbar">
    <div class="container">
      <span class="topbar-en">Nankai University Mathematical Modeling Association</span>
      <span class="topbar-right">关注「南开数院学工」公众号获取最新通知</span>
    </div>
  </div>

  <header class="site-header">
    <div class="container header-inner">
      <RouterLink to="/" class="brand">
        <span class="brand-mark" aria-hidden="true">
          <svg viewBox="0 0 44 44" width="44" height="44">
            <circle cx="22" cy="22" r="21" fill="#6510ad" />
            <circle cx="22" cy="22" r="17" fill="none" stroke="#c8a710" stroke-width="1" opacity="0.75" />
            <text
              x="22"
              y="28"
              text-anchor="middle"
              font-family="Arial, Helvetica, sans-serif"
              font-size="13"
              font-weight="700"
              letter-spacing="0.5"
              fill="#ffffff"
            >
              NKU
            </text>
          </svg>
        </span>
        <span class="brand-copy">
          <strong>南开大学数学建模协会</strong>
          <em>Nankai University Mathematical Modeling Association</em>
        </span>
      </RouterLink>

      <nav class="main-nav" aria-label="主导航">
        <RouterLink v-for="item in nav" :key="item.label" :to="item.to">{{ item.label }}</RouterLink>
      </nav>
    </div>
  </header>
</template>
