<script setup>
import { RouterLink } from 'vue-router'
import { nav } from '../data/site'
</script>

<template>
  <header class="site-header">
    <div class="container header-inner">
      <RouterLink to="/" class="brand">
        <span class="brand-mark" aria-hidden="true">
          <svg viewBox="0 0 44 44" width="44" height="44">
            <circle cx="22" cy="22" r="21" fill="#7b2358" />
            <circle cx="22" cy="22" r="17" fill="none" stroke="#c8a160" stroke-width="0.8" opacity="0.65" />
            <text
              x="22"
              y="28"
              text-anchor="middle"
              font-family="Georgia, serif"
              font-size="14"
              letter-spacing="0.5"
              fill="#f6f1f3"
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
