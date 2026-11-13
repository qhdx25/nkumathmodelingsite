<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'

const props = defineProps({
  items: { type: Array, required: true },
  rows: { type: Number, default: 4 },
  // 固定行高（不传则按首个单元格实测高度）
  cellHeight: { type: Number, default: 0 },
  interval: { type: Number, default: 3500 },
  // 右侧竖向指示点
  dots: { type: Boolean, default: false },
})

const rootRef = ref(null)
const index = ref(0)
const measured = ref(0)
const paused = ref(false)
const animate = ref(true)
let timer = null

const canScroll = computed(() => props.items.length > props.rows)
const cellH = computed(() => props.cellHeight || measured.value)
const visibleRows = computed(() => Math.min(props.rows, props.items.length))

// 末尾补 rows 个克隆项：滚到第 n 位时画面与第 0 位完全一致，可无感回跳
const loop = computed(() =>
  props.items.length > props.rows ? [...props.items, ...props.items.slice(0, props.rows)] : props.items,
)
const activeIndex = computed(() => index.value % props.items.length)

const rootStyle = computed(() =>
  cellH.value ? { height: `${cellH.value * visibleRows.value}px` } : null,
)
const cellStyle = computed(() => (cellH.value ? { height: `${cellH.value}px` } : null))
const trackStyle = computed(() => ({
  transform: `translateY(-${index.value * cellH.value}px)`,
  transition: animate.value ? 'transform 0.5s ease' : 'none',
}))

function measure() {
  if (props.cellHeight) return
  const first = rootRef.value?.querySelector('.ticker-cell')
  if (first) {
    const h = Math.round(first.getBoundingClientRect().height)
    if (h > 0) measured.value = h
  }
}

function step() {
  if (paused.value || !canScroll.value) return
  index.value += 1
}

function handleEnd() {
  if (index.value >= props.items.length) {
    animate.value = false
    index.value = 0
    requestAnimationFrame(() => requestAnimationFrame(() => { animate.value = true }))
  }
}

function goTo(i) {
  animate.value = true
  index.value = i
}

onMounted(() => {
  measure()
  window.addEventListener('resize', measure)
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    animate.value = false
    return
  }
  timer = setInterval(step, props.interval)
})

onBeforeUnmount(() => {
  if (timer) clearInterval(timer)
  window.removeEventListener('resize', measure)
})
</script>

<template>
  <div
    ref="rootRef"
    class="ticker"
    :class="{ 'has-dots': dots, 'is-static': !canScroll }"
    :style="rootStyle"
    @mouseenter="paused = true"
    @mouseleave="paused = false"
    @focusin="paused = true"
    @focusout="paused = false"
  >
    <div class="ticker-track" :style="trackStyle" @transitionend="handleEnd">
      <div v-for="(item, i) in loop" :key="i" class="ticker-cell" :style="cellStyle">
        <slot :item="item" :index="i"></slot>
      </div>
    </div>

    <div v-if="dots && canScroll" class="ticker-dots">
      <button
        v-for="(item, i) in items"
        :key="i"
        type="button"
        class="ticker-dot"
        :class="{ 'is-active': i === activeIndex }"
        :aria-label="`第 ${i + 1} 项`"
        @click="goTo(i)"
      ></button>
    </div>
  </div>
</template>
