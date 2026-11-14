<script setup>
import { computed } from 'vue'
import { RouterLink, useRoute } from 'vue-router'

const route = useRoute()
const title = computed(() => route.meta?.titleEn || 'Page')
const zhPath = computed(() => route.meta?.zhPath || '/')
</script>

<template>
  <main class="page">
    <section class="page-head">
      <div class="container">
        <h1>{{ title }}</h1>
        <p class="page-lead">This section is being prepared.</p>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <div class="coming">
          <p class="coming-title">Coming soon</p>
          <p class="coming-body">
            The English version of this section is under construction. The full content is
            currently available in the Chinese site.
          </p>
          <div class="coming-actions">
            <RouterLink class="btn btn-solid" to="/en">Back to English home</RouterLink>
            <RouterLink class="btn" :to="zhPath">View in Chinese</RouterLink>
          </div>
        </div>
      </div>
    </section>
  </main>
</template>
