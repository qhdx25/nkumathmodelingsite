<script setup>
const steps = [
  { n: '01', title: 'Register as a member', body: 'Fill in your basic information and any modeling experience. Members can join every training session and internal contest.' },
  { n: '02', title: 'Pick a direction', body: 'Secretariat (planning / office / finance), Competition Department, Publicity Department and the Working Committee all recruit at the same time.' },
  { n: '03', title: 'Interview', body: 'Held within two weeks of the semester start. A short self-introduction plus one scenario question — no modeling test.' },
  { n: '04', title: 'Join the team', body: 'A one-semester probation follows, then confirmation. You can be a member and a committee member at the same time.' },
]

const roles = [
  { name: 'Secretariat · Planning', body: 'Contest planning, process design, cross-team coordination' },
  { name: 'Secretariat · Office', body: 'Meetings, archives, duty rota and supplies' },
  { name: 'Secretariat · Finance', body: 'Budget, reimbursement and public accounts' },
  { name: 'Competition Department', body: 'Hosting contests, registration review, results and points' },
  { name: 'Publicity Department', body: 'WeChat account, posters and photo records' },
  { name: 'Working Committee', body: 'Training, materials and special projects' },
]

const faq = [
  { q: 'Can I join with zero modeling experience?', a: 'Yes. The interview does not test modeling ability, and training starts from the basics.' },
  { q: 'Can first-year students apply?', a: 'Yes. The association is open to undergraduates, master’s and doctoral students across the university.' },
  { q: 'How much time does it take?', a: 'Work follows the contest calendar, with a busier month before each contest; about 2–4 hours a week otherwise.' },
  { q: 'When does recruitment open?', a: 'Every September, with a smaller spring round if positions remain open. Notices appear on the Chinese site.' },
]
</script>

<template>
  <main class="page">
    <section class="page-head">
      <div class="container">
        <h1>Join us</h1>
        <p class="page-lead">
          The association recruits every September, with two tracks — general members and committee
          members. No prior modeling experience is required.
        </p>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <div class="section-head">
          <h2>How to join</h2>
          <span class="head-note">2026 intake · opens in September</span>
        </div>
        <ol class="recruit-steps">
          <li v-for="s in steps" :key="s.n">
            <span class="recruit-n">{{ s.n }}</span>
            <h3>{{ s.title }}</h3>
            <p>{{ s.body }}</p>
          </li>
        </ol>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <div class="section-head">
          <h2>Open directions</h2>
          <span class="head-note">Six roles across four teams</span>
        </div>
        <ul class="recruit-roles">
          <li v-for="r in roles" :key="r.name">
            <h3>{{ r.name }}</h3>
            <p>{{ r.body }}</p>
          </li>
        </ul>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <div class="section-head">
          <h2>How to apply</h2>
        </div>
        <div class="recruit-apply">
          <p>
            Once the recruitment notice is published, submit the form linked in the school WeChat
            article. You are also welcome to find teammates on the Chinese team-up board and enter
            the campus contest first.
          </p>
          <p class="recruit-meta">
            Enquiries: Student Affairs Office, School of Mathematical Sciences · Association Secretariat
          </p>
        </div>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <div class="section-head">
          <h2>FAQ</h2>
        </div>
        <dl class="recruit-faq">
          <div v-for="item in faq" :key="item.q">
            <dt>{{ item.q }}</dt>
            <dd>{{ item.a }}</dd>
          </div>
        </dl>
      </div>
    </section>
  </main>
</template>
