<script setup>
import { computed, ref } from 'vue'
import HeroBanner from '../components/HeroBanner.vue'
import NavStrip from '../components/NavStrip.vue'
import VerticalTicker from '../components/VerticalTicker.vue'
import {
  enAbout,
  enBanners,
  enFeatured,
  enNews,
  enNotices,
  enSeries,
  enSideGroups,
  enStats,
  enStripNav,
} from '../data/en'

const tab = ref('news')
const sideTab = ref('events')

const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
const parse = (iso) => {
  const m = String(iso || '').match(/(\d{4})-(\d{2})-(\d{2})/)
  return m ? { y: m[1], m: Number(m[2]), d: m[3], short: MONTHS[Number(m[2]) - 1] } : null
}

const newsRows = computed(() =>
  enNews.map((item) => {
    const p = parse(item.date)
    return {
      title: item.title,
      day: p ? p.d : '·',
      month: p ? p.short : '',
      href: item.url || '#news',
    }
  }),
)

const noticeRows = computed(() =>
  enNotices.map((item) => {
    const p = parse(item.date)
    return { title: item.title, day: p ? p.d : '·', yearMonth: p ? `${p.y}-${String(p.m).padStart(2, '0')}` : item.date }
  }),
)

const sideList = computed(() => enSideGroups[sideTab.value] || [])
</script>

<template>
  <main>
    <HeroBanner :items="enBanners" />
    <NavStrip :items="enStripNav" placeholder="Search" hash-mode />

    <!-- Latest news / Notices -->
    <section id="news" class="home-news">
      <div class="container">
        <div class="news-tabs">
          <button type="button" :class="{ 'is-active': tab === 'news' }" @click="tab = 'news'">Latest News</button>
          <button type="button" :class="{ 'is-active': tab === 'notice' }" @click="tab = 'notice'">Notices</button>
          <a class="news-more" href="#news">More &gt;</a>
        </div>

        <div v-if="tab === 'news'" class="news-main">
          <div class="feature-pair">
            <a
              v-for="item in enFeatured"
              :key="item.title"
              class="feature-card"
              :href="item.url"
              target="_blank"
              rel="noreferrer"
            >
              <span class="feature-media"><img :src="item.image" alt="" /></span>
              <span class="feature-body">
                <span class="feature-title">{{ item.title }}</span>
                <span class="feature-foot">
                  <svg class="icon-clock" viewBox="0 0 24 24" width="13" height="13" aria-hidden="true">
                    <circle cx="12" cy="12" r="8.4" fill="none" stroke="currentColor" stroke-width="1.6" />
                    <path d="M12 7.6V12l3 1.8" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" />
                  </svg>
                  <time>{{ item.date }}</time>
                  <span class="feature-arrow">→</span>
                </span>
              </span>
            </a>
          </div>

          <div class="date-list">
            <VerticalTicker :items="newsRows" :rows="4" :cell-height="62" :speed="9">
              <template #default="{ item }">
                <a v-if="item.href" class="date-row" :href="item.href" target="_blank" rel="noreferrer">
                  <span class="date-box"><b>{{ item.day }}</b><em>{{ item.month }}</em></span>
                  <span class="date-title">{{ item.title }}</span>
                </a>
              </template>
            </VerticalTicker>
            <a class="date-more" href="#news">View all news →</a>
          </div>
        </div>

        <ul v-else class="notice-grid">
          <li v-for="item in noticeRows" :key="item.title">
            <a href="#news">
              <span class="notice-date">
                <b>{{ item.day }}</b>
                <em>{{ item.yearMonth }}</em>
              </span>
              <span class="notice-cell-title">{{ item.title }}</span>
            </a>
          </li>
        </ul>
      </div>
    </section>

    <!-- Series: purple band, centred heading -->
    <section id="series" class="series-band">
      <div class="container">
        <div class="series-head">
          <h2>Series</h2>
          <a class="head-more" href="#series">More &gt;</a>
        </div>
        <ul class="series-grid">
          <li v-for="item in enSeries" :key="item.title">
            <a href="#series">
              <span class="series-media">
                <img :src="item.image" :alt="item.title" />
                <span class="series-tag">{{ item.tag }}</span>
              </span>
              <span class="series-title">{{ item.title }}</span>
              <span class="series-note">{{ item.note }}</span>
            </a>
          </li>
        </ul>
      </div>
    </section>

    <!-- Figure + tabbed list -->
    <section id="events" class="side-band">
      <div class="container side-inner">
        <figure class="side-figure">
          <img src="/img/news/wx-league.jpg" alt="Five-University Modeling League defence" />
          <figcaption>First Tianjin Five-University Modeling League · Oct 2026</figcaption>
        </figure>

        <div class="side-panel">
          <div class="side-tabs">
            <button type="button" :class="{ 'is-active': sideTab === 'events' }" @click="sideTab = 'events'">Events</button>
            <button type="button" :class="{ 'is-active': sideTab === 'training' }" @click="sideTab = 'training'">Training</button>
            <button type="button" :class="{ 'is-active': sideTab === 'resources' }" @click="sideTab = 'resources'">Resources</button>
            <a class="side-more" href="#events">More &gt;</a>
          </div>
          <ul class="side-list">
            <li v-for="item in sideList" :key="item.label">
              <a href="#events">
                <span class="side-label">{{ item.label }}</span>
                <span class="side-meta">{{ item.meta }}</span>
              </a>
            </li>
          </ul>
        </div>
      </div>
    </section>

    <!-- About -->
    <section id="about" class="about-band">
      <div class="container about-inner">
        <div class="about-head">
          <p class="about-kicker">{{ enAbout.kicker }}</p>
          <h2 class="about-slogan">
            <span class="l1">{{ enAbout.heading.split('\n')[0] }}</span>
            <span class="l2">{{ enAbout.heading.split('\n')[1] }}</span>
          </h2>
        </div>
        <div class="about-body">
          <p>{{ enAbout.body }}</p>
          <div class="about-cards">
            <div v-for="item in enStats" :key="item.value" class="about-card">
              <p class="about-num">{{ item.value }}</p>
              <p class="about-label">{{ item.label }}</p>
              <p class="about-note">{{ item.note }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Gallery (empty for now) -->
    <section id="gallery" class="gallery-band">
      <div class="container">
        <div class="section-head">
          <h2>Gallery</h2>
          <span class="head-note">Photos being collected</span>
        </div>
        <div class="gallery-empty">
          <p>Photos of association activities will appear here</p>
          <p class="gallery-empty-hint">Recruitment, training, mock contests, league defence and award ceremonies — listed by date once collected</p>
        </div>
      </div>
    </section>
  </main>
</template>
