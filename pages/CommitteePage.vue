<script setup>
import { committeeDepartments, committeeOverview } from '../site-data'
import emblemUrl from '../assets/nku-emblem.jpg'

const navigation = [
  { label: '首页', href: '/' },
  { label: '南开概览', href: '/#overview' },
  { label: '协会框架', href: '/#association' },
  { label: '校队培训', href: '/training' },
  { label: '建模资料', href: '/materials' },
]
</script>

<template>
  <main class="subpage-main">
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
    <section id="committee" class="section section-first">
      <div class="container">
        <div class="section-heading">
          <div>
            <p class="section-kicker">委员会</p>
            <h2>把委员会与各部门成员独立放在一个页面里</h2>
          </div>
          <p class="section-note">
            以下内容根据你提供的委员会架构图整理。首页不再直接展示这些细节，统一在这里集中查看会更清楚。
          </p>
        </div>

        <div class="committee-overview">
          <article v-for="group in committeeOverview" :key="group.title" class="committee-card">
            <p class="card-kicker">委员会层级</p>
            <h3>{{ group.title }}</h3>
            <div class="member-tags">
              <span v-for="member in group.members" :key="member" class="member-tag">{{ member }}</span>
            </div>
          </article>
        </div>

        <div class="committee-grid">
          <article
            v-for="department in committeeDepartments"
            :key="department.name"
            class="committee-department"
          >
            <div class="committee-header">
              <p class="card-kicker">部门架构</p>
              <h3>{{ department.name }}</h3>
            </div>

            <div class="committee-roles">
              <div v-for="role in department.roles" :key="`${department.name}-${role.title}`" class="committee-role">
                <strong>{{ role.title }}</strong>
                <div class="member-tags">
                  <span
                    v-for="member in role.members"
                    :key="`${department.name}-${role.title}-${member}`"
                    class="member-tag"
                  >
                    {{ member }}
                  </span>
                </div>
              </div>
            </div>
          </article>
        </div>

        <p class="committee-note">
          注：如果后面你们发现个别名字或职务需要微调，可以继续按这一页的结构直接替换，不需要再动首页布局。
        </p>
      </div>
    </section>
  </main>
</template>
