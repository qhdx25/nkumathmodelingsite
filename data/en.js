// English version content for /en. Kept separate from data/site.js so the
// Chinese site stays untouched; add new keys here when more pages are translated.

export const enHeader = {
  note: 'School of Mathematical Sciences · Student Society',
  brand: 'Nankai Mathematical Modeling Association',
  brandSub: '南开大学数学建模协会',
  alt: 'Nankai University emblem',
  nav: [
    { label: 'Home', to: '/en' },
    { label: 'News', to: '/en/news' },
    { label: 'Competitions', to: '/en/competition' },
    { label: 'Training', to: '/en/training' },
    { label: 'Resources', to: '/en/materials' },
    { label: 'Committee', to: '/en/committee' },
  ],
  topLinks: [
    { label: 'Join us', to: '/en/recruit' },
    { label: 'Contact', to: '/committee' },
    { label: 'Downloads', to: '/materials' },
    { label: '中文', to: '/' },
  ],
}

export const enStripNav = [
  { label: 'News', to: '#news' },
  { label: 'Notices', to: '#news' },
  { label: 'Competitions', to: '#events' },
  { label: 'Training', to: '#events' },
  { label: 'Resources', to: '#events' },
  { label: 'Series', to: '#series' },
  { label: 'Gallery', to: '#gallery' },
]

export const enBanners = [
  { id: 'nku-01', image: '/img/hero/nku-01.jpg', credit: 'Photo: Zong Qiqi', url: '' },
  { id: 'nku-02', image: '/img/hero/nku-02.jpg', credit: 'Photo: Zhou Songxian', url: '' },
  { id: 'nku-03', image: '/img/hero/nku-03.jpg', credit: 'Photo: Guo Ziang', url: '' },
  { id: 'nku-04', image: '/img/hero/nku-04.jpg', credit: 'Photo: Zong Qiqi', url: '' },
  { id: 'nku-05', image: '/img/hero/nku-05.jpg', credit: 'Photo: Guo Ziang', url: '' },
  { id: 'nku-06', image: '/img/hero/nku-06.jpg', credit: 'Main Building at dusk', url: '' },
]

export const enFeatured = [
  {
    title: 'First Tianjin Five-University Modeling League defence held at Nankai',
    date: '2026/10/27',
    image: '/img/news/wx-league.jpg',
    url: 'https://mp.weixin.qq.com/s/QvMJ6zMx8FKFsZCF2uSpGg',
  },
  {
    title: '2026 “Huawei Cup” Graduate Modeling Contest: registration open',
    date: '2026/06/02',
    image: '/img/news/wx-huawei.jpg',
    url: 'https://mp.weixin.qq.com/s/PWx5VBaqAiTaTf3_MALPYw',
  },
]

export const enNews = [
  {
    date: '2026-11-01',
    title: 'First Tianjin Five-University Modeling League defence held at Nankai',
    url: 'https://news.nankai.edu.cn/zhxw/system/2026/11/01/030075089.shtml',
  },
  { date: '2026-09-12', title: '2026 recruitment for the association is now open' },
  {
    date: '2026-05-07',
    title: 'Tenth anniversary symposium of the association held',
    url: 'https://news.nankai.edu.cn/dcxy/system/2026/05/07/030071789.shtml',
  },
  { date: '2026-04-15', title: '2026 CUMCM (and campus contest) registration notice' },
  { date: '2026-04-02', title: 'Spring supplementary selection of the Nankai modeling team' },
]

export const enNotices = [
  { date: '2026-10-28', title: 'Results of the first Five-University Modeling League' },
  { date: '2026-10-20', title: 'Announcement of the 2026 team list' },
  { date: '2026-09-18', title: 'Training schedule for the autumn semester' },
  { date: '2026-09-05', title: 'Notice on venue booking for the campus contest' },
  { date: '2026-06-10', title: 'Integral ranking of the 2026 campus contest' },
  { date: '2026-06-02', title: 'Graduate contest registration and eligibility' },
]

export const enSeries = [
  {
    tag: 'Series',
    title: 'Tianjin Five-University Modeling League',
    note: 'Hosted in rotation · Nankai hosted the first',
    image: '/img/news/wx-league.jpg',
  },
  {
    tag: 'Series',
    title: '“Huawei Cup” Graduate Modeling Contest',
    note: 'For graduate students · starts every September',
    image: '/img/news/wx-huawei.jpg',
  },
  {
    tag: 'Series',
    title: 'China Undergraduate Mathematical Contest in Modeling',
    note: 'Also the campus contest and team selection',
    image: '/img/hero/nku-02.jpg',
  },
]

export const enSideGroups = {
  events: [
    { label: 'Tianjin Five-University Modeling League', meta: 'registration closed' },
    { label: '“Huawei Cup” Graduate Contest', meta: 'closes 2027.01.28' },
    { label: 'China Undergraduate Contest (CUMCM)', meta: 'every September' },
    { label: 'Mathematical Contest in Modeling (MCM/ICM)', meta: 'every February' },
    { label: 'Campus contest and team selection', meta: 'every April' },
    { label: 'Nankai modeling team supplementary trial', meta: 'every April' },
  ],
  training: [
    { label: 'Training system overview', meta: '4 stages' },
    { label: 'Lecture notes and recordings', meta: 'updated' },
    { label: 'Team selection rules', meta: 'published' },
    { label: 'Coach group office hours', meta: 'weekly' },
  ],
  resources: [
    { label: 'Past contest problems', meta: '2016–2026' },
    { label: 'Selected outstanding papers', meta: '36 papers' },
    { label: 'LaTeX template and style files', meta: 'ready' },
    { label: 'Python / MATLAB toolboxes', meta: 'ready' },
  ],
}

export const enStats = [
  { value: '2016', label: 'Founded', note: 'tenth anniversary in 2026' },
  { value: '1200+', label: 'Students reached', note: 'all majors, UG to PhD' },
  { value: '~300', label: 'Teams per year', note: 'largest modeling contest on campus' },
  { value: '10 yrs', label: 'Running', note: 'learning through contests' },
]

export const enAbout = {
  kicker: 'About',
  heading: 'Describe with mathematics\nverify with models',
  body:
    'Founded in 2016, the Nankai University Mathematical Modeling Association is a student society under the School of Mathematical Sciences. We host the largest modeling contest on campus, serve more than 1,200 participants from across the university, and organise training, selection and inter-university exchanges.',
}

export const enFooter = {
  title: 'Nankai Mathematical Modeling Association',
  desc: 'Student society of the School of Mathematical Sciences, founded in 2016.\nLearning through contests, applying what we learn.',
  navTitle: 'Sitemap',
  moreTitle: 'More',
  addressTitle: 'Campuses',
  copy: '© 2026 Nankai University Mathematical Modeling Association',
  motto: '允公允能，日新月异',
  demo: 'Demo site · content to be reviewed',
}
