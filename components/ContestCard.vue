<script setup>
// 竞赛页：纵向切屏相框内的赛事卡（回退奶油白卡版式）
// 左图 + 封面压字标题；信息区深色文字；CTA=报名入口（浅紫）+ 了解更多（白）
import { onMounted, ref } from 'vue'
import { imgUrl } from '../assets/resolver'

const props = defineProps({
  contest: { type: Object, required: true },
})

// 赛事配图映射：优先真实竞赛现场照（五校联赛答辩），其余沿用校园实景
const IMAGES = {
  'mcm-icm-2027': { src: imgUrl('/img/hero/nku-03.jpg'), pos: 'center 55%' },
  'cumcm-2027': { src: imgUrl('/img/hero/nku-01.jpg'), pos: 'center 45%' },
  'mathorcup-2027': { src: imgUrl('/img/hero/nku-05.jpg'), pos: 'center 50%' },
  'szcup-2027': { src: imgUrl('/img/hero/nku-06.jpg'), pos: 'center 62%' },
  'neepu-2027': { src: imgUrl('/img/hero/nku-02.jpg'), pos: 'center 50%' },
  'tianjin-5u': { src: imgUrl('/img/news/wx-league.jpg'), pos: 'center 40%' },
}
const image = IMAGES[props.contest.id] || null
const imgBroken = ref(false)

function open() {
  if (props.contest.officialUrl) window.open(props.contest.officialUrl, '_blank', 'noreferrer')
}

// 进入视口时淡入
const root = ref(null)
const visible = ref(false)
onMounted(() => {
  if (!('IntersectionObserver' in window)) {
    visible.value = true
    return
  }
  const io = new IntersectionObserver(
    (entries) => {
      if (entries.some((e) => e.isIntersecting)) {
        visible.value = true
        io.disconnect()
      }
    },
    { threshold: 0.05 },
  )
  if (root.value) io.observe(root.value)
})
</script>

<template>
  <article
    ref="root"
    class="contest-card"
    :class="{ 'is-link': contest.officialUrl, 'is-visible': visible }"
    :role="contest.officialUrl ? 'link' : undefined"
    :tabindex="contest.officialUrl ? 0 : undefined"
    @click="open"
    @keydown.enter="open"
  >
    <figure class="contest-image">
      <img
        v-if="image && !imgBroken"
        :src="image.src"
        :alt="contest.name"
        :style="image.pos ? { objectPosition: image.pos } : undefined"
        loading="lazy"
        @error="imgBroken = true"
      />
      <div v-else class="contest-img-fallback" aria-hidden="true">
        <span>{{ contest.abbr }}</span>
      </div>
      <figcaption class="contest-cover">
        <p class="cover-eyebrow">
          <span class="contest-abbr">{{ contest.abbr }}</span>
          <span class="contest-level">{{ contest.level }}</span>
        </p>
        <span class="cover-title">{{ contest.name }}</span>
      </figcaption>
    </figure>

    <div class="contest-body">
      <p class="contest-state" :class="`state-${contest.status}`">
        <i class="state-dot" aria-hidden="true"></i>{{ contest.statusText }}
      </p>

      <p v-if="contest.note" class="contest-note">{{ contest.note }}</p>

      <div class="contest-meta">
        <div>
          <span>报名截止</span>
          <span>{{ contest.registerBy }}</span>
        </div>
        <div>
          <span>比赛时间</span>
          <span>{{ contest.window }}</span>
        </div>
        <div>
          <span>说明</span>
          <span>{{ contest.extras.join(' · ') }}</span>
        </div>
      </div>

      <div class="contest-actions">
        <a
          v-if="contest.registerUrl"
          class="btn btn-sm btn-solid"
          :href="contest.registerUrl"
          target="_blank"
          rel="noreferrer"
          @click.stop
        >
          报名入口
        </a>
        <a
          v-if="contest.officialUrl"
          class="btn btn-sm btn-more"
          :href="contest.officialUrl"
          target="_blank"
          rel="noreferrer"
          @click.stop
        >
          了解更多 <span aria-hidden="true">→</span>
        </a>
        <span v-if="!contest.registerUrl && !contest.officialUrl" class="contest-wait">报名通道待发布</span>
        <span v-if="contest.siteName" class="contest-site">{{ contest.siteName }}</span>
      </div>
    </div>
  </article>
</template>
