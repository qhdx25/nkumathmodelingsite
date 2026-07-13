<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { awardPapers, resourceColumns } from '../site-data'
import emblemUrl from '../assets/nku-emblem.jpg'
import slideCampus1 from '../assets/5e177bd9cee9a6227f02eed8016e1339.jpg'
import slideCampus2 from '../assets/8e9fb206-48cd-4a32-b020-83f8c64415f9.jpg'

const navigation = [
  { label: '首页', href: '/' },
  { label: '南开概览', href: '/#overview' },
  { label: '协会框架', href: '/#association' },
  { label: '校队培训', href: '/training' },
  { label: '建模资料', href: '/materials' },
]

const expandedPapers = ref({})

const toggleExpand = (index) => {
  expandedPapers.value[index] = !expandedPapers.value[index]
}

const isExpanded = (index) => {
  return expandedPapers.value[index]
}

const trainingSlides = [
  { image: slideCampus1, title: '校园春景', credit: '摄影：周嵩娜' },
  { image: slideCampus2, title: '主楼晚霞', credit: '摄影：郭子昂' },
]

const activeSlide = ref(0)
let slideTimer = null

const nextSlide = () => {
  activeSlide.value = (activeSlide.value + 1) % trainingSlides.length
}

const previousSlide = () => {
  activeSlide.value = (activeSlide.value - 1 + trainingSlides.length) % trainingSlides.length
}

const goToSlide = (index) => {
  activeSlide.value = index
}

const startAutoPlay = () => {
  slideTimer = setInterval(nextSlide, 5000)
}

const stopAutoPlay = () => {
  if (slideTimer) {
    clearInterval(slideTimer)
    slideTimer = null
  }
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
    <section class="hero-section hero-section-subpage">
      <div class="hero-carousel">
        <article
          v-for="(slide, index) in trainingSlides"
          :key="slide.title"
          class="hero-slide"
          :class="{ 'is-active': index === activeSlide }"
          :style="{ backgroundImage: `url(${slide.image})` }"
        >
          <div class="container hero-content"></div>
        </article>

        <header class="site-header site-header-subpage">
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
              v-for="(slide, index) in trainingSlides"
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

    <section id="training" class="section section-first">
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

    <section id="award-papers" class="section">
      <div class="container">
        <div class="section-heading">
          <div>
            <p class="section-kicker">获奖论文</p>
            <h2>历年国赛获奖论文合集</h2>
          </div>
          <p class="section-note">
            汇集2021-2024年全国大学生数学建模竞赛获奖论文，供同学们学习参考。
          </p>
        </div>

        <div v-for="yearGroup in awardPapers" :key="yearGroup.year" class="year-section">
          <div class="year-header">
            <span class="year-badge" :class="'year-' + yearGroup.year">{{ yearGroup.year }}</span>
            <h3>{{ yearGroup.title }}</h3>
            <p>{{ yearGroup.description }}</p>
          </div>

          <div class="paper-grid">
            <div v-for="(paper, index) in yearGroup.papers" :key="paper.problem" class="paper-item">
              <div v-if="paper.hasChildren" class="paper-card paper-card-expandable" @click="toggleExpand(yearGroup.year + '-' + index)">
                <span class="paper-problem" :class="paper.problem">{{ paper.problem }}</span>
                <h4>{{ paper.title }}</h4>
                <p class="paper-prize">{{ paper.prize }}</p>
                <p class="paper-team">{{ paper.team }}</p>
                <span class="paper-expand-icon">{{ isExpanded(yearGroup.year + '-' + index) ? '▼' : '▶' }}</span>
              </div>
              <a v-else class="paper-card" :href="paper.href" target="_blank" rel="noreferrer">
                <span class="paper-problem" :class="paper.problem.toLowerCase()">{{ paper.problem }}</span>
                <h4>{{ paper.title }}</h4>
                <p class="paper-prize">{{ paper.prize }}</p>
                <p class="paper-team">{{ paper.team }}</p>
              </a>
              <Transition name="expand">
                <div v-if="paper.hasChildren && isExpanded(yearGroup.year + '-' + index)" class="paper-children">
                  <div v-for="(child, childIndex) in paper.children" :key="child.problem" class="paper-item">
                    <div v-if="child.hasChildren" class="paper-card paper-card-expandable paper-card-child" @click="toggleExpand(yearGroup.year + '-' + index + '-' + childIndex)">
                      <span class="paper-problem" :class="child.problem.toLowerCase()">{{ child.problem }}</span>
                      <h4>{{ child.title }}</h4>
                      <p class="paper-prize">{{ child.prize }}</p>
                      <p class="paper-team">{{ child.team }}</p>
                      <span class="paper-expand-icon">{{ isExpanded(yearGroup.year + '-' + index + '-' + childIndex) ? '▼' : '▶' }}</span>
                    </div>
                    <a v-else class="paper-card paper-card-child" :href="child.href" target="_blank" rel="noreferrer">
                      <span class="paper-problem" :class="child.problem.toLowerCase()">{{ child.problem }}</span>
                      <h4>{{ child.title }}</h4>
                      <p class="paper-prize">{{ child.prize }}</p>
                      <p class="paper-team">{{ child.team }}</p>
                    </a>
                    <Transition name="expand">
                      <div v-if="child.hasChildren && isExpanded(yearGroup.year + '-' + index + '-' + childIndex)" class="paper-children paper-children-2">
                        <a v-for="grandchild in child.children" :key="grandchild.title" class="paper-card paper-card-grandchild" :href="grandchild.href" target="_blank" rel="noreferrer">
                          <span class="paper-problem paper-problem-pdf">{{ grandchild.team }}</span>
                          <h4>{{ grandchild.title }}</h4>
                          <p class="paper-prize">{{ grandchild.prize }}</p>
                        </a>
                      </div>
                    </Transition>
                  </div>
                </div>
              </Transition>
            </div>
          </div>
        </div>
      </div>
    </section>
  </main>
</template>
