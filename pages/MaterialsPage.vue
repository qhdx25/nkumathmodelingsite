<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { materialCards, slides } from '../site-data'
import emblemUrl from '../assets/nku-emblem.jpg'

const navigation = [
  { label: '首页', href: '/' },
  { label: '南开概览', href: '/#overview' },
  { label: '协会框架', href: '/#association' },
  { label: '校队培训', href: '/training' },
  { label: '建模资料', href: '/materials' },
]

const activeSlide = ref(0)
let slideTimer = null

function stopAutoPlay() {
  if (slideTimer) {
    clearInterval(slideTimer)
    slideTimer = null
  }
}

function startAutoPlay() {
  stopAutoPlay()
  slideTimer = setInterval(() => {
    activeSlide.value = (activeSlide.value + 1) % slides.length
  }, 5000)
}

function goToSlide(index) {
  activeSlide.value = index
  startAutoPlay()
}

function nextSlide() {
  activeSlide.value = (activeSlide.value + 1) % slides.length
  startAutoPlay()
}

function previousSlide() {
  activeSlide.value = (activeSlide.value - 1 + slides.length) % slides.length
  startAutoPlay()
}

onMounted(() => {
  startAutoPlay()
})

onBeforeUnmount(() => {
  stopAutoPlay()
})
</script>

<template>
  <main class="subpage-main">
    <section class="hero-section">
      <div class="hero-carousel">
        <article
          v-for="(slide, index) in slides"
          :key="slide.title"
          class="hero-slide"
          :class="{ 'is-active': index === activeSlide }"
          :style="{ backgroundImage: `url(${slide.image})` }"
        >
          <div class="container hero-content"></div>
        </article>

        <header class="site-header">
          <div class="container header-inner">
            <a class="brand" href="/">
              <img :src="emblemUrl" alt="南开大学校标" class="brand-emblem" />
              <div class="brand-copy">
                <strong>南开大学数学建模协会</strong>
                <p>Nankai University Mathematical Modeling Association</p>
              </div>
            </a>

            <nav class="main-nav" aria-label="主导航">
              <a v-for="item in navigation" :key="item.label" :href="item.href">{{ item.label }}</a>
            </nav>
          </div>
        </header>

        <div class="container hero-controls">
          <button class="carousel-arrow" type="button" aria-label="上一张" @click="previousSlide">‹</button>

          <div class="carousel-dots" role="tablist" aria-label="轮播切换">
            <button
              v-for="(slide, index) in slides"
              :key="slide.credit"
              class="carousel-dot"
              :class="{ 'is-active': index === activeSlide }"
              type="button"
              :aria-label="`切换到第 ${index + 1} 张`"
              @click="goToSlide(index)"
            >
              <span class="carousel-dot-core" aria-hidden="true"></span>
            </button>
          </div>

          <button class="carousel-arrow" type="button" aria-label="下一张" @click="nextSlide">›</button>
        </div>
      </div>
    </section>
    <section id="materials" class="section">
      <div class="container">
        <div class="section-heading">
          <div>
            <p class="section-kicker">建模资料</p>
            <h2>资料共享，共同进步</h2>
          </div>
          <p class="section-note">
            汇集历年竞赛真题、优秀论文、常用模型和工具教程，助力你的建模之路。
          </p>
        </div>

        <div class="material-grid material-grid-single">
          <a
            v-for="item in materialCards"
            :key="item.title"
            class="material-card"
            :href="item.href"
            target="_blank"
            rel="noreferrer"
          >
            <p class="card-kicker">{{ item.meta }}</p>
            <h3>{{ item.title }}</h3>
            <p>{{ item.description }}</p>
            <span>打开资料库</span>
          </a>
        </div>
      </div>
    </section>
  </main>
</template>
