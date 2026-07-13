<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'

import emblemUrl from '../assets/nku-emblem.jpg'
import {
  associationCards,
  campusCards,
  mathTimeline,
  overviewStats,
  resourceColumns,
  slides,
} from '../site-data'

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
  <main>
    <section id="hero" class="hero-section">
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

    <section id="overview" class="section">
      <div class="container">
        <div class="section-heading">
          <div>
            <p class="section-kicker">南开概览</p>
            <h2>百年学府，薪火相传</h2>
          </div>
          <p class="section-note">
            南开大学作为百年名校，始终秉承"允公允能，日新月异"的校训精神，培养了一代代优秀人才。
          </p>
        </div>

        <div class="stats-grid">
          <article v-for="item in overviewStats" :key="item.label" class="stat-card">
            <p class="stat-label">{{ item.label }}</p>
            <h3>{{ item.value }}</h3>
            <p>{{ item.detail }}</p>
          </article>
        </div>
      </div>
    </section>

    <section id="mathematics" class="section">
      <div class="container math-grid">
        <article class="math-story">
          <p class="section-kicker">数学底色</p>
          <h2>数学强国，南开担当</h2>
          <p>
            南开大学数学学科历史悠久、实力雄厚。自1920年姜立夫先生创立数学系以来，历经百年发展，形成了独特的学术传统和卓越的科研实力。陈省身数学研究所的成立，更是为南开数学走向世界奠定了坚实基础。
          </p>
          <p>
            在这样的学术沃土上，数学建模协会蓬勃发展，致力于培养学生的创新思维和实践能力，为国家输送了大批优秀的数学建模人才。
          </p>
        </article>

        <div class="timeline-grid">
          <article v-for="item in mathTimeline" :key="item.title" class="timeline-card">
            <span class="timeline-year">{{ item.year }}</span>
            <h3>{{ item.title }}</h3>
            <p>{{ item.description }}</p>
          </article>
        </div>
      </div>
    </section>

    <section id="association" class="section">
      <div class="container">
        <div class="section-heading">
          <div>
            <p class="section-kicker">协会框架</p>
            <h2>组织架构，协同共进</h2>
          </div>
          <p class="section-note">
            协会下设多个部门，各部门分工明确、协同合作，共同推动协会各项工作的开展。
          </p>
        </div>

        <div class="portal-grid">
          <article v-for="card in associationCards" :key="card.title" class="portal-card">
            <p class="card-kicker">{{ card.kicker }}</p>
            <h3>{{ card.title }}</h3>
            <p>{{ card.description }}</p>
            <a :href="card.href">{{ card.action }}</a>
          </article>
        </div>
      </div>
    </section>

    <section id="resources" class="section">
      <div class="container">
        <div class="section-heading">
          <div>
            <p class="section-kicker">校队培训</p>
            <h2>系统训练，备战竞赛</h2>
          </div>
          <p class="section-note">
            从入门到精通，我们为你准备了全方位的培训资源和实战训练。
          </p>
        </div>

        <div class="resource-grid">
          <article v-for="column in resourceColumns" :key="column.title" class="resource-card">
            <h3>{{ column.title }}</h3>
            <ul class="resource-list">
              <li v-for="item in column.items" :key="item">{{ item }}</li>
            </ul>
          </article>
        </div>
      </div>
    </section>

    <section id="campus" class="section">
      <div class="container">
        <div class="section-heading">
          <div>
            <p class="section-kicker">校区信息</p>
            <h2>一校三区，共创辉煌</h2>
          </div>
          <p class="section-note">
            南开大学三个校区各具特色，共同构成了充满活力的校园文化。
          </p>
        </div>

        <div class="campus-grid">
          <article v-for="campus in campusCards" :key="campus.campus" class="campus-card">
            <p class="card-kicker">{{ campus.campus }}</p>
            <h3>{{ campus.address }}</h3>
            <p class="campus-postcode">邮编 {{ campus.postcode }}</p>
            <p>{{ campus.note }}</p>
          </article>
        </div>
      </div>
    </section>
  </main>
</template>
