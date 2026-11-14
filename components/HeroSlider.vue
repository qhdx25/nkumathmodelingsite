<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'

const props = defineProps({
  items: { type: Array, required: true },
})

const index = ref(0)
const paused = ref(false)
let timer = null

const total = computed(() => props.items.length)

function go(i) {
  index.value = (i + total.value) % total.value
}
function next() {
  go(index.value + 1)
}
function prev() {
  go(index.value - 1)
}

function stop() {
  if (timer) {
    clearInterval(timer)
    timer = null
  }
}

function start() {
  stop()
  if (total.value <= 1) return
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return
  timer = setInterval(() => {
    if (!paused.value) next()
  }, 5000)
}

onMounted(start)
onBeforeUnmount(stop)
</script>

<template>
  <section class="banner" aria-label="重点活动轮播">
    <div class="container">
      <div
        class="banner-inner"
        @mouseenter="paused = true"
        @mouseleave="paused = false"
        @focusin="paused = true"
        @focusout="paused = false"
      >
        <div class="banner-viewport">
          <div class="banner-track" :style="{ transform: `translateX(-${index * 100}%)` }">
            <a
              v-for="(item, i) in items"
              :key="item.id"
              class="banner-slide"
              :href="item.url"
              target="_blank"
              rel="noreferrer"
            >
              <div class="banner-media">
                <img v-if="item.image" :src="item.image" :alt="item.title" />
                <div v-else class="banner-ph">
                  <span class="banner-ph-badge">图位 {{ i + 1 }} / {{ items.length }}</span>
                  <strong>此处放活动图片</strong>
                  <span class="banner-ph-note">建议 1600 × 480（10:3），WebP，单张 ≤ 200 KB</span>
                  <span class="banner-ph-note">整块可点击 → {{ item.linkLabel }}</span>
                </div>
              </div>

              <div class="banner-caption">
                <span class="banner-tag">{{ item.tag }}</span>
                <span class="banner-title">{{ item.title }}</span>
                <span class="banner-arrow" aria-hidden="true">›</span>
              </div>
            </a>
          </div>
        </div>

        <template v-if="total > 1">
          <button class="banner-nav is-prev" type="button" aria-label="上一张" @click="prev">‹</button>
          <button class="banner-nav is-next" type="button" aria-label="下一张" @click="next">›</button>

          <div class="banner-dots" role="group" aria-label="图片切换">
            <button
              v-for="(item, i) in items"
              :key="`dot-${item.id}`"
              type="button"
              class="banner-dot"
              :class="{ 'is-active': i === index }"
              :aria-label="`第 ${i + 1} 张`"
              :aria-current="i === index ? 'true' : undefined"
              @click="go(i)"
            ></button>
          </div>
        </template>
      </div>
    </div>
  </section>
</template>
