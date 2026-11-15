<script setup>
// 书本式左栏（书脊）：品牌 → 本页小节 → 校徽，跟随滚动高亮 + 进度条
// 与竞赛页同一套视觉，放在 .comp-page 里即可复用样式
import { nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { RouterLink } from 'vue-router'
import { imgUrl } from '../assets/resolver'

const props = defineProps({
  sections: { type: Array, required: true },
})

const HEAD_OFFSET = 152
const active = ref(props.sections[0]?.id ?? '')
const navEl = ref(null)
const spineEl = ref(null)

function jumpTo(id) {
  const el = document.getElementById(id)
  if (!el) return
  window.scrollTo({ top: el.getBoundingClientRect().top + window.scrollY - HEAD_OFFSET, behavior: 'smooth' })
}

function syncSpine() {
  const bar = spineEl.value
  const on = navEl.value?.querySelector('.csn-link.is-on')
  if (!bar || !on) return
  bar.style.transform = `translateY(${on.offsetTop}px)`
  bar.style.height = `${on.offsetHeight}px`
  bar.classList.add('is-ok')
}
watch(active, () => nextTick(syncSpine))

let pending = false
function onScroll() {
  if (pending) return
  pending = true
  requestAnimationFrame(() => {
    pending = false
    let current = props.sections[0]?.id
    for (const s of props.sections) {
      const el = document.getElementById(s.id)
      if (el && el.getBoundingClientRect().top <= 170) current = s.id
    }
    active.value = current
    updateProgress()
  })
}

function updateProgress() {
  const nav = navEl.value
  const body = nav?.closest('.comp-body')
  if (!nav || !body) return
  const rect = body.getBoundingClientRect()
  const total = rect.height - window.innerHeight
  const p = total > 0 ? Math.min(1, Math.max(0, -rect.top / total)) : 0
  nav.style.setProperty('--sp', p.toFixed(4))
}

onMounted(() => {
  syncSpine()
  onScroll()
  window.addEventListener('scroll', onScroll, { passive: true })
  window.addEventListener('resize', onScroll)
})
onBeforeUnmount(() => {
  window.removeEventListener('scroll', onScroll)
  window.removeEventListener('resize', onScroll)
})
</script>

<template>
  <nav ref="navEl" class="comp-side-nav" aria-label="本页导航">
    <div class="csn-inner">
      <span ref="spineEl" class="csn-spine" aria-hidden="true"></span>
      <RouterLink to="/" class="csn-brand">
        <span class="csn-brand-cn">南开大学<br />数学建模协会</span>
        <span class="csn-brand-en">Nankai MCM Association</span>
      </RouterLink>
      <p class="csn-title">本页</p>
      <ul class="csn-list">
        <li v-for="s in sections" :key="s.id">
          <button
            type="button"
            class="csn-link"
            :class="{ 'is-on': active === s.id }"
            :aria-current="active === s.id ? 'true' : undefined"
            @click="jumpTo(s.id)"
          >
            <span class="csn-txt">{{ s.label }}</span>
            <span class="csn-arrow" aria-hidden="true">→</span>
          </button>
        </li>
      </ul>
      <img class="csn-emblem" :src="imgUrl('/img/nku-mark.png')" alt="" aria-hidden="true" />
    </div>
    <span class="csn-progress" aria-hidden="true"></span>
  </nav>
</template>
