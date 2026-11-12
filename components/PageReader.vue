<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'

const props = defineProps({
  // 页图目录，如 /pages/cumcm-2026-award-draft
  base: { type: String, required: true },
  pages: { type: Number, required: true },
  title: { type: String, default: '' },
})

const index = ref(1)
const ready = ref(false)
const stage = ref(null)
const strip = ref(null)

const pad = (n) => String(n).padStart(2, '0')
const pageSrc = (n) => `${props.base}/p${pad(n)}.webp`
const thumbSrc = (n) => `${props.base}/t${pad(n)}.webp`

const current = computed(() => pageSrc(index.value))
const atFirst = computed(() => index.value <= 1)
const atLast = computed(() => index.value >= props.pages)
const progress = computed(() => (index.value / props.pages) * 100)

function go(n) {
  const next = Math.min(Math.max(1, n), props.pages)
  if (next === index.value) return
  index.value = next
  ready.value = false
}

// 预取相邻页，翻页不等待
function prefetch(n) {
  if (n < 1 || n > props.pages) return
  const img = new Image()
  img.src = pageSrc(n)
}

watch(index, (n) => {
  prefetch(n + 1)
  prefetch(n - 1)
  // 缩略图条跟随当前页，避免 45 页时找不到高亮在哪
  const el = strip.value?.querySelector('.reader-thumb.is-active')
  el?.scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' })
})

function onKey(e) {
  if (e.key === 'ArrowLeft') {
    go(index.value - 1)
    e.preventDefault()
  } else if (e.key === 'ArrowRight') {
    go(index.value + 1)
    e.preventDefault()
  }
}

let stageEl = null

onMounted(() => {
  prefetch(2)
  stageEl = stage.value
  stageEl?.addEventListener('keydown', onKey)
})
onBeforeUnmount(() => {
  stageEl?.removeEventListener('keydown', onKey)
  stageEl = null
})
</script>

<template>
  <div class="reader">
    <div ref="stage" class="reader-stage" tabindex="0" aria-label="文档阅读区，可用左右方向键翻页">
      <button
        class="reader-arrow is-prev"
        type="button"
        aria-label="上一页"
        :disabled="atFirst"
        @click="go(index - 1)"
      >
        ‹
      </button>

      <figure class="reader-page">
        <img
          :key="current"
          :src="current"
          :alt="`${title} 第 ${index} 页`"
          :class="{ 'is-ready': ready }"
          @load="ready = true"
        />
      </figure>

      <button
        class="reader-arrow is-next"
        type="button"
        aria-label="下一页"
        :disabled="atLast"
        @click="go(index + 1)"
      >
        ›
      </button>

      <p class="reader-counter">
        <strong>{{ index }}</strong> / {{ pages }}
      </p>
    </div>

    <div class="reader-strip" ref="strip" role="group" aria-label="页缩略图">
      <button
        v-for="n in pages"
        :key="`t-${n}`"
        type="button"
        class="reader-thumb"
        :class="{ 'is-active': n === index }"
        :aria-label="`跳到第 ${n} 页`"
        :aria-current="n === index ? 'true' : undefined"
        @click="go(n)"
      >
        <img :src="thumbSrc(n)" alt="" loading="lazy" />
        <span>{{ n }}</span>
      </button>
    </div>

    <div class="reader-foot">
      <div class="reader-progress" aria-hidden="true"><i :style="{ width: progress + '%' }"></i></div>
      <div class="reader-nav">
        <button class="btn btn-ghost btn-sm" type="button" :disabled="atFirst" @click="go(index - 1)">
          上一页
        </button>
        <span class="reader-hint">可用 ← → 翻页</span>
        <button class="btn btn-ghost btn-sm" type="button" :disabled="atLast" @click="go(index + 1)">
          下一页
        </button>
      </div>
    </div>
  </div>
</template>
