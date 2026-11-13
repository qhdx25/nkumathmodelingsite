<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'

const props = defineProps({
  items: { type: Array, required: true },
  rows: { type: Number, default: 4 },
  // 固定行高（不传则按首个单元格实测高度）
  cellHeight: { type: Number, default: 0 },
  // 平滑滚动速度 px/s
  speed: { type: Number, default: 16 },
  // 右侧滑动条
  scrollbar: { type: Boolean, default: true },
})

const rootRef = ref(null)
const measured = ref(0)
const offset = ref(0)
const hovered = ref(false)
const dragging = ref(false)
const reduced = ref(false)

const cellH = computed(() => props.cellHeight || measured.value)
const canScroll = computed(() => props.items.length > props.rows && cellH.value > 0)
const visibleRows = computed(() => Math.min(props.rows, props.items.length))
// 两倍内容：offset 在 [0, items*cellH) 内循环，画面永远接得上
const loop = computed(() => (canScroll.value ? [...props.items, ...props.items] : props.items))
const wrapAt = computed(() => props.items.length * cellH.value)

const rootStyle = computed(() =>
  cellH.value ? { height: `${cellH.value * visibleRows.value}px` } : null,
)
const cellStyle = computed(() => (cellH.value ? { height: `${cellH.value}px` } : null))
const trackStyle = computed(() => ({ transform: `translate3d(0, ${-offset.value}px, 0)` }))

/* ---------- 滑动条 ---------- */
const barH = computed(() => cellH.value * visibleRows.value)
const thumbH = computed(() => {
  if (!canScroll.value) return 0
  return Math.max(30, Math.round(barH.value * (visibleRows.value / props.items.length)))
})
const thumbTop = computed(() => {
  const span = barH.value - thumbH.value
  if (!wrapAt.value || span <= 0) return 0
  return (offset.value / wrapAt.value) * span
})
const thumbStyle = computed(() => ({ height: `${thumbH.value}px`, transform: `translateY(${thumbTop.value}px)` }))

/* ---------- 平滑滚动 ---------- */
let raf = 0
let last = 0
function frame(t) {
  const dt = last ? Math.min(t - last, 64) : 0
  last = t
  if (canScroll.value && !hovered.value && !dragging.value && !reduced.value) {
    offset.value = (offset.value + (props.speed * dt) / 1000) % wrapAt.value
  }
  raf = requestAnimationFrame(frame)
}

function measure() {
  if (props.cellHeight) return
  const first = rootRef.value?.querySelector('.ticker-cell')
  if (first) {
    const h = Math.round(first.getBoundingClientRect().height)
    if (h > 0) measured.value = h
  }
}

/* ---------- 拖动 ---------- */
function clampOffset(v) {
  if (!wrapAt.value) return 0
  return ((v % wrapAt.value) + wrapAt.value) % wrapAt.value
}

function startDrag(e) {
  if (!canScroll.value) return
  e.preventDefault()
  const bar = e.currentTarget
  const rect = bar.getBoundingClientRect()
  const span = rect.height - thumbH.value
  // 点在轨道上：先跳到该位置，再跟手拖
  if (e.target !== bar.querySelector('.ticker-thumb') && span > 0) {
    const y = e.clientY - rect.top - thumbH.value / 2
    offset.value = clampOffset((Math.min(Math.max(y, 0), span) / span) * wrapAt.value)
  }
  const startY = e.clientY
  const startOffset = offset.value
  dragging.value = true

  const move = (ev) => {
    if (span <= 0) return
    offset.value = clampOffset(startOffset + ((ev.clientY - startY) / span) * wrapAt.value)
  }
  const up = () => {
    dragging.value = false
    window.removeEventListener('pointermove', move)
    window.removeEventListener('pointerup', up)
    window.removeEventListener('pointercancel', up)
  }
  window.addEventListener('pointermove', move)
  window.addEventListener('pointerup', up)
  window.addEventListener('pointercancel', up)
}

onMounted(() => {
  measure()
  window.addEventListener('resize', measure)
  reduced.value = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  raf = requestAnimationFrame(frame)
})

onBeforeUnmount(() => {
  cancelAnimationFrame(raf)
  window.removeEventListener('resize', measure)
})
</script>

<template>
  <div
    ref="rootRef"
    class="ticker"
    :class="{ 'is-hover': hovered, 'is-dragging': dragging }"
    :style="rootStyle"
    @mouseenter="hovered = true"
    @mouseleave="hovered = false"
    @focusin="hovered = true"
    @focusout="hovered = false"
  >
    <div class="ticker-window">
      <div class="ticker-track" :style="trackStyle">
        <div v-for="(item, i) in loop" :key="i" class="ticker-cell" :style="cellStyle">
          <slot :item="item" :index="i"></slot>
        </div>
      </div>
    </div>

    <div v-if="scrollbar && canScroll" class="ticker-scroll" @pointerdown="startDrag">
      <span class="ticker-thumb" :style="thumbStyle"></span>
    </div>
  </div>
</template>
