// 竞赛页数据：竞赛日历、赛事信息、成绩公示、积分公示
// 时间与链接均取自赛事官方页面，标注「参考」的为上一赛季日期，用于给出大致时间窗

export const calendar = {
  status: 'pending',
  title: '2026–2027 学年竞赛日历',
  note: '以校历风格图片呈现，标注全年赛事节点与校内选拔时间。',
  requirement: '建议尺寸 2400×1600（3:2），PNG 或 WebP，单张控制在 300KB 内。',
}

export const contests = [
  {
    id: 'mcm-icm-2027',
    name: '美国大学生数学建模竞赛',
    abbr: 'MCM/ICM 2027',
    level: '国际级',
    status: 'open',
    statusText: '报名中',
    registerBy: '2027-01-28 15:00 EST',
    window: '2027 年 1 月 29 日 06:00 — 2 月 2 日 09:00（北京时间）',
    extras: ['三人一队，同校在读', '全英文论文，96 小时', '$100 / 队', '结果 2027-05-08 公布'],
    officialUrl: 'https://www.contest.comap.com/undergraduate/contests/mcm/instructions.html',
    registerUrl: 'https://www.contest.comap.com/undergraduate/contests/mcm/register.php',
    siteName: 'COMAP 官网',
  },
  {
    id: 'cumcm-2027',
    name: '全国大学生数学建模竞赛',
    abbr: 'CUMCM 2027',
    level: '国家级',
    status: 'soon',
    statusText: '待官网发布',
    registerBy: '校内选拔参考往年 4 月',
    window: '参考：9 月上旬开赛，连续 74 小时',
    extras: ['三人一队，本科生', '赛区奖 + 全国奖两级评审', '须提交 AI 工具使用说明'],
    officialUrl: 'https://www.mcm.edu.cn',
    registerUrl: '',
    siteName: '全国大学生数学建模竞赛官网',
    note: '校内选拔由协会承办，报名通知将通过学院公众号发布。',
  },
  {
    id: 'mathorcup-2027',
    name: 'MathorCup 数学应用挑战赛',
    abbr: 'MathorCup 2027',
    level: '全国学会主办',
    status: 'soon',
    statusText: '待官网发布',
    registerBy: '参考：前一年 12 月底开放报名',
    window: '参考：4 月中旬开赛，为期 4 天',
    extras: ['教师 / 研究生 / 本科 / 专科分组', '5 道企业真题任选', '赛区赛 + 国赛两级评奖'],
    officialUrl: 'https://www.mathorcup.org',
    registerUrl: 'https://www.saikr.com',
    siteName: '官网 / 赛氪报名',
  },
  {
    id: 'szcup-2027',
    name: '深圳杯数学建模挑战赛',
    abbr: '深圳杯',
    level: '全国学会主办',
    status: 'soon',
    statusText: '待官网发布',
    registerBy: '上半年发布研究课题',
    window: '参考：约 6 月提交论文，暑期赴深圳现场答辩',
    extras: ['4 道开放性研究课题任选', '课题研究制，周期数周至数月', '决赛需现场答辩'],
    officialUrl: 'http://m2ct.org',
    registerUrl: '',
    siteName: '深圳杯官网',
  },
  {
    id: 'neepu-2027',
    name: '电工数学建模竞赛',
    abbr: '电工杯',
    level: '全国学会主办',
    status: 'soon',
    statusText: '待官网发布',
    registerBy: '参考：5 月开赛前一个月',
    window: '参考：5 月下旬，连续 72 小时',
    extras: ['A / B 两题任选', '免费参赛', 'AI 使用限制最严格'],
    officialUrl: 'https://shumo.neepu.edu.cn',
    registerUrl: '',
    siteName: '竞赛官网',
  },
  {
    id: 'tianjin-5u',
    name: '天津市五校数学建模联赛',
    abbr: '五校联赛 · 第二届',
    level: '区域联赛',
    status: 'soon',
    statusText: '待发布',
    registerBy: '首届于 2026 年 10 月完成答辩',
    window: '参考：秋季学期举办',
    extras: ['南开牵头，联合天大、天理工、天工大、天师大', '现场答辩制', '设金奖 / 银奖 / 铜奖'],
    officialUrl: '',
    registerUrl: '',
    siteName: '',
    note: '首届由南开大学数学科学学院牵头举办，第二届安排待定。',
  },
]

// 成绩公示：已结束赛事的汇总，具体名单为占位
export const results = [
  {
    event: '第一届天津市五校数学建模联赛',
    time: '2026 年 10 月',
    summary: '32 支队伍参赛，18 支获奖',
    detail: '金奖 3 项 · 银奖 6 项 · 铜奖 9 项',
    status: 'partial',
    statusText: '汇总已出，名单待补',
    note: '需补充：获奖队伍名单（校名 / 队名 / 队员 / 指导教师）',
  },
  {
    event: '2026 年全国大学生数学建模竞赛',
    time: '2026 年 9 月',
    summary: '—',
    detail: '—',
    status: 'pending',
    statusText: '待公示',
    note: '需补充：南开获奖队伍清单与赛区 / 全国奖等级',
  },
  {
    event: '2026 年南开大学数学建模竞赛（校赛）',
    time: '2026 年 8 月',
    summary: '—',
    detail: '—',
    status: 'pending',
    statusText: '待公示',
    note: '需补充：获奖名单与国赛入选队伍',
  },
]

export const points = {
  status: 'pending',
  title: '积分公示',
  note: '协会赛事积分按参赛与获奖情况累计，用于年度评优与校队选拔参考。',
  requirement: '由竞赛部整理，接入后以表格形式展示：姓名 / 学号后四位 / 赛事 / 积分 / 累计。',
}

export const dataNote =
  '本页赛事时间为各赛事官方公布的当前赛季信息；标注「参考」的为上一赛季日期，仅用于提示大致时间窗，正式报名请以官网通知为准。'

// 首页「赛事日历」用的时间节点：按日期升序，官方日期与参考日期分别标注
export const seasonNodes = [
  { date: '2026-09-10', name: '全国大学生数学建模竞赛（国赛）', tag: '参考：9 月上旬开赛', link: '/competition' },
  { date: '2026-09-20', name: '“华为杯”研究生数学建模竞赛', tag: '每年 9 月开赛', link: '/competition' },
  { date: '2026-12-25', name: 'MathorCup 报名开放', tag: '参考：前一年 12 月底', link: '/competition' },
  { date: '2027-01-28', name: '美国大学生数学建模竞赛 · 报名截止', tag: '官方：15:00 EST', link: '/competition' },
  { date: '2027-01-29', name: '美国大学生数学建模竞赛 · 开赛', tag: '官方：连续 96 小时', link: '/competition' },
  { date: '2027-05-08', name: '美国大学生数学建模竞赛 · 结果公布', tag: '官方', link: '/competition' },
]
