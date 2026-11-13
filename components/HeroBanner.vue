<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'

const props = defineProps({
  items: { type: Array, required: true },
  interval: { type: Number, default: 5000 },
})

const index = ref(0)
const paused = ref(false)
let timer = null

const current = computed(() => props.items[index.value] || {})

function go(i) {
  index.value = (i + props.items.length) % props.items.length
  restart()
}

function tick() {
  if (!paused.value) index.value = (index.value + 1) % props.items.length
}

function restart() {
  if (timer) clearInterval(timer)
  timer = setInterval(tick, props.interval)
}

onMounted(() => {
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return
  restart()
})

onBeforeUnmount(() => {
  if (timer) clearInterval(timer)
})
</script>

<template>
  <section class="hero" @mouseenter="paused = true" @mouseleave="paused = false">
    <div class="hero-slides">
      <a
        v-for="(item, i) in items"
        :key="item.id"
        class="hero-slide"
        :class="{ 'is-active': i === index }"
        :style="{ backgroundImage: `url(${item.image})` }"
        :href="item.url || undefined"
        :target="item.url ? '_blank' : undefined"
        :rel="item.url ? 'noreferrer' : undefined"
        :aria-hidden="i !== index"
      ></a>
    </div>
    <div class="hero-shade"></div>

    <button class="hero-arrow is-prev" type="button" aria-label="上一张" @click="go(index - 1)">
      <svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true">
        <path d="M15 4 7 12l8 8" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" />
      </svg>
    </button>
    <button class="hero-arrow is-next" type="button" aria-label="下一张" @click="go(index + 1)">
      <svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true">
        <path d="m9 4 8 8-8 8" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" />
      </svg>
    </button>

    <p v-if="current.credit" class="hero-credit">{{ current.credit }}</p>

    <div class="hero-dots">
      <button
        v-for="(item, i) in items"
        :key="item.id"
        type="button"
        class="hero-dot"
        :class="{ 'is-active': i === index }"
        :aria-label="`第 ${i + 1} 张`"
        @click="go(i)"
      ></button>
    </div>

    <slot></slot>
  </section>
</template>
