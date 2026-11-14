<script setup>
const contests = [
  {
    name: 'MCM/ICM 2027',
    full: 'Mathematical Contest in Modeling / Interdisciplinary Contest in Modeling',
    level: 'International',
    register: 'Closes 2027-01-28, 15:00 EST',
    window: '2027-01-29 06:00 — 2027-02-02 09:00 (Beijing time)',
    facts: ['3 students per team, same institution', 'English paper, 96 hours', 'USD 100 per team'],
  },
  {
    name: 'CUMCM 2027',
    full: 'China Undergraduate Mathematical Contest in Modeling',
    level: 'National',
    register: 'Campus selection around April',
    window: 'Early September, 74 hours',
    facts: ['3 undergraduates per team', 'Provincial and national awards', 'AI-use statement required'],
  },
  {
    name: 'MathorCup 2027',
    full: 'MathorCup Mathematical Application Challenge',
    level: 'National society',
    register: 'Opens late December (previous season)',
    window: 'Mid-April, 4 days',
    facts: ['Separate tracks for teachers, graduates, undergraduates', 'Five industry problems, choose one'],
  },
  {
    name: 'Shenzhen Cup',
    full: 'Shenzhen Cup Mathematical Modeling Challenge',
    level: 'National society',
    register: 'Research topics released in spring',
    window: 'Paper due around June, on-site defence in Shenzhen in summer',
    facts: ['Research-style problem', 'Shortlisted teams present in person'],
  },
  {
    name: 'Electrical Engineering Modeling Contest',
    full: 'National Electrical Engineering Mathematical Modeling Contest',
    level: 'National society',
    register: 'About one month before the contest (previous season: May)',
    window: 'Late May, 72 hours',
    facts: ['Hosted by the Chinese Society for Electrical Engineering', '3 students per team'],
  },
  {
    name: 'Tianjin Five-University League',
    full: 'Tianjin Five-University Mathematical Modeling League',
    level: 'Regional league',
    register: 'First edition completed its defence in October 2026',
    window: 'Held in the autumn semester, hosted in rotation',
    facts: ['Five universities in Tianjin', 'Nankai hosted the first edition'],
  },
]
</script>

<template>
  <main class="page">
    <section class="page-head">
      <div class="container">
        <h1>Competitions</h1>
        <p class="page-lead">
          Contest calendar, registration windows and campus selection for the 2026–2027 season.
          Dates marked “previous season” are indicative only — always check the official notice.
        </p>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <div class="section-head">
          <h2>Contests we cover</h2>
          <span class="head-note">Updated 2026-11</span>
        </div>

        <ul class="en-contests">
          <li v-for="item in contests" :key="item.name">
            <div class="en-contest-head">
              <h3>{{ item.name }}</h3>
              <span class="en-contest-level">{{ item.level }}</span>
            </div>
            <p class="en-contest-full">{{ item.full }}</p>
            <dl class="en-contest-meta">
              <div>
                <dt>Registration</dt>
                <dd>{{ item.register }}</dd>
              </div>
              <div>
                <dt>Contest window</dt>
                <dd>{{ item.window }}</dd>
              </div>
            </dl>
            <ul class="en-contest-facts">
              <li v-for="f in item.facts" :key="f">{{ f }}</li>
            </ul>
          </li>
        </ul>

        <p class="section-foot">
          Campus selection for CUMCM is organised by the association; notices are published on the
          Chinese site and the school WeChat account.
        </p>
      </div>
    </section>
  </main>
</template>
