<script setup>
import { ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { stripNav } from '../data/site'

const route = useRoute()
const router = useRouter()
const keyword = ref('')

const isActive = (to) => {
  if (to.includes('#')) return false
  return to === '/' ? route.path === '/' : route.path.startsWith(to)
}

function submit() {
  const q = keyword.value.trim()
  if (!q) return
  router.push({ path: '/search', query: { q } })
}
</script>

<template>
  <div class="nav-strip">
    <div class="strip-shell">
      <div class="container strip-inner">
        <nav class="strip-links" aria-label="栏目导航">
          <RouterLink
            v-for="item in stripNav"
            :key="item.label"
            :to="item.to"
            :class="{ 'is-active': isActive(item.to) }"
          >{{ item.label }}</RouterLink>
        </nav>

        <form class="strip-search" role="search" @submit.prevent="submit">
          <input
            v-model="keyword"
            type="search"
            placeholder="搜索"
            aria-label="站内搜索"
          />
          <button type="submit" aria-label="搜索">
            <svg viewBox="0 0 24 24" width="17" height="17" aria-hidden="true">
              <circle cx="11" cy="11" r="6.4" fill="none" stroke="currentColor" stroke-width="1.7" />
              <path d="m16 16 4.2 4.2" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" />
            </svg>
          </button>
        </form>
      </div>
    </div>
  </div>
</template>
