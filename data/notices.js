// 信息公示数据：获奖公示 / 会议纪要
// reader 指向 public/pages/<slug>/ 下的页图（p01.webp 正文页、t01.webp 缩略图）
// file 指向 public/files/ 下的原 PDF，可为 null（仅站内翻页阅读 + 官方原文链接）

export const categories = [
  { id: 'all', label: '全部' },
  { id: 'award', label: '获奖公示' },
  { id: 'minutes', label: '会议纪要' },
  { id: 'files', label: '赛务文件' },
]

export const notices = [
  {
    slug: 'cumcm-2026-award-draft',
    category: 'award',
    title: '2026 高教社杯全国大学生数学建模竞赛获奖名单（初稿）',
    sub: '公示说明、异议受理程序与获奖名单全文，共 45 页',
    issuer: '全国大学生数学建模竞赛组委会',
    date: '2026-11-02',
    pages: 45,
    reader: '/pages/cumcm-2026-award-draft',
    file: null,
    sourceUrl: 'https://dxs.moe.gov.cn/zx/a/hd_sxjm_gsyw/261102/209746.shtml',
    sourceLabel: '中国大学生在线 · 原文',
    period: { from: '2026-11-08', to: '2026-11-14' },
    summary:
      '全国组委会与中国大学生在线合作发布本年度获奖名单初稿。名单在公示期内接受异议，公示期结束后 6 个月内仍可提出异议；对学校、队员、指导教师姓名的文字错误，须在公示期内报所属赛区组委会汇总。',
    points: [
      '公示期：2026 年 11 月 8 日 — 11 月 14 日，为期 7 天。',
      '异议须书面提出，由全国组委会或各赛区组委会受理；举报人信息予以保密。',
      '姓名文字错误请在 11 月 14 日前报所属赛区组委会，逾期按该名单印制奖状。',
      '每队最多一名「指导教师」，原则上不受理集体名称范围内的变更申请。',
    ],
    internal: false,
  },
  {
    slug: 'wuxiao-2026-award',
    category: 'award',
    title: '第一届天津市五校数学建模联赛获奖名单',
    sub: '32 支队伍参加答辩、18 支获奖：金奖 3 项、银奖 6 项、铜奖 9 项',
    issuer: '五校数学建模联赛组委会 · 南开大学数学科学学院',
    date: '2026-11-01',
    pages: 0,
    reader: null,
    file: null,
    sourceUrl: 'https://news.nankai.edu.cn/zhxw/system/2026/11/01/030075089.shtml',
    sourceLabel: '南开新闻网 · 答辩会报道',
    summary:
      '2026 年 10 月 25 日，第一届天津市五校数学建模联赛答辩会在南开大学数学科学学院举行。联赛由南开大学数学科学学院牵头，联合天津大学、天津理工大学、天津工业大学、天津师范大学共同举办，是 2026 年天津市五校数学文化节的系列活动之一。',
    points: [
      '五校共 32 支队伍参加答辩，经评审团综合评议评出金奖 3 项、银奖 6 项、铜奖 9 项。',
      '答辩分上、下午两个场次，队伍就问题背景、模型假设、求解思路、结果检验与应用价值作陈述。',
      '南开大学数学建模教练组组长胡刚作《蛋白质固有无序区域预测》主题报告。',
      '协会负责人江绮佳作年度工作汇报，介绍协会建设、人才培养与校际联动情况。',
    ],
    internal: false,
  },
  {
    slug: 'cumcm-2026-signup',
    category: 'files',
    title: '2026 年全国大学生数学建模竞赛（兼校赛）报名通知',
    sub: '三人一队、全员南开在籍本科生；4 月 8 日 9:00 — 4 月 22 日 16:00 报名',
    issuer: '南开大学教务部 · 数学科学学院',
    date: '2026-04-08',
    pages: 0,
    reader: null,
    file: null,
    sourceUrl: 'https://math.nankai.edu.cn/2026/0414/c34414a592893/page.htm',
    sourceLabel: '数学科学学院官网 · 原文',
    summary:
      '为备战 2026 年全国大学生数学建模竞赛及南开大学数学建模竞赛（兼选拔赛），学院启动报名工作并组建 2026 年南开大学建模飞书交流群，供同学们组队与沟通。',
    points: [
      '每队限报 3 人、不得少于 3 人，指定队长 1 人；3 名队员均须为南开大学在籍本科生。',
      '报名时间：2026 年 4 月 8 日 9:00 起至 4 月 22 日 16:00 止。',
      '已确定组队的，在 3 名队员入群后直接在飞书群云文档填写信息；未组队的可在群内寻找队员。',
      '附件为盖章版《南开大学数学建模竞赛报名通知》。',
    ],
    internal: false,
  },
  {
    slug: 'council-2-20260322',
    category: 'minutes',
    title: '二届理事会第二次会议纪要',
    sub: '补选常务理事、人事任免',
    issuer: '南开大学数学建模协会',
    date: '2026-03-22',
    pages: 3,
    reader: '/pages/council-2-20260322',
    file: '/files/council-2-20260322.pdf',
    summary:
      '2026 年 3 月 22 日上午于数学科学学院第一会议室召开，全体理事参会、部分干事代表列席。会议补选常务理事，并作出相关人事任免决定。',
    points: ['补选常务理事，分工为协助分管研究生工作的副主席处理研究生日常工作。', '审议并通过相关人事任免事项。'],
    internal: true,
  },
  {
    slug: 'minutes-2-20260317',
    category: 'minutes',
    title: '二届常务理事会第二次会议纪要',
    sub: '常务理事辞职与补选推荐',
    issuer: '南开大学数学建模协会',
    date: '2026-03-17',
    pages: 2,
    reader: '/pages/minutes-2-20260317',
    file: '/files/minutes-2-20260317.pdf',
    summary:
      '2026 年 3 月 17 日于线上召开，全体常务理事参会。会议同意常务理事辞职申请，任命研究生事务办公室主任，并推荐常务理事补选候选人。',
    points: [
      '同意常务理事辞去常务理事职务，同时免去其研究生事务办公室主任职务。',
      '任命新任研究生事务办公室主任，主持办公室工作。',
      '推荐该同学作为常务理事补选候选人，报理事会补选。',
    ],
    internal: true,
  },
  {
    slug: 'minutes-3-20260331',
    category: 'minutes',
    title: '二届常务理事会第三次会议纪要',
    sub: '副主席辞职与任命',
    issuer: '南开大学数学建模协会',
    date: '2026-03-31',
    pages: 2,
    reader: '/pages/minutes-3-20260331',
    file: '/files/minutes-3-20260331.pdf',
    summary:
      '2026 年 3 月 31 日于线上召开，全体常务理事参会。会议同意两位副主席辞去对应工作，并任命新的副主席分管宣传部。',
    points: ['同意两位副主席辞去所任工作。', '任命新任协会副主席，分工为分管宣传部。'],
    internal: true,
  },
  {
    slug: 'minutes-4-20260722',
    category: 'minutes',
    title: '二届常务理事会第四次会议纪要',
    sub: '三项工作条例审议通过、启动换届',
    issuer: '南开大学数学建模协会',
    date: '2026-07-22',
    pages: 2,
    reader: '/pages/minutes-4-20260722',
    file: '/files/minutes-4-20260722.pdf',
    summary:
      '2026 年 7 月 22 日于线上召开。会议审议通过《理事会工作条例》《组织工作条例》《换届工作条例》三项草案并决定报理事会通过，同时决定开展 2026—2027 比赛年换届工作。',
    points: [
      '通过《南开大学数学建模协会理事会工作条例（草案）》。',
      '通过《南开大学数学建模协会组织工作条例（草案）》。',
      '通过《南开大学数学建模协会换届工作条例（草案）》，并报理事会通过。',
      '决定开展换届工作，依条例成立换届工作委员会。',
    ],
    internal: true,
  },
  {
    slug: 'minutes-5-20260830',
    category: 'minutes',
    title: '二届常务理事会第五次会议纪要',
    sub: '新一届人事安排、年度表彰',
    issuer: '南开大学数学建模协会',
    date: '2026-08-30',
    pages: 4,
    reader: '/pages/minutes-5-20260830',
    file: '/files/minutes-5-20260830.pdf',
    summary:
      '2026 年 8 月 30 日于线上召开。会议听取换届工作委员会报告，形成 2026—2027 比赛年常务理事、主席团与部门负责人推荐决定；对上一比赛年表现优秀的负责人、理事和干事予以表彰；并讨论协会资金使用与补贴发放。',
    points: [
      '听取换届工作委员会资格审查报告与面试谈话记录总结。',
      '形成《关于推荐 2026—2027 比赛年常务理事、主席团和各部门负责人的决定》。',
      '表彰 2025—2026 比赛年优秀协会负责人、优秀理事与优秀干事。',
      '讨论协会资金使用与补贴发放事项。',
    ],
    internal: true,
  },
]

// 按日期倒序（含公示期状态计算）
export function listNotices(category = 'all') {
  const today = new Date()
  const rows = notices
    .filter((n) => category === 'all' || n.category === category)
    .slice()
    .sort((a, b) => (a.date < b.date ? 1 : -1))

  return rows.map((n) => ({ ...n, status: statusOf(n, today) }))
}

export function getNotice(slug) {
  const n = notices.find((item) => item.slug === slug)
  return n ? { ...n, status: statusOf(n, new Date()) } : null
}

function statusOf(n, today) {
  if (!n.period) return { text: '已发布', tone: 'done' }
  const from = new Date(n.period.from + 'T00:00:00')
  const to = new Date(n.period.to + 'T23:59:59')
  if (today < from) return { text: '即将公示', tone: 'soon' }
  if (today > to) return { text: '公示已结束', tone: 'done' }
  return { text: '公示中', tone: 'live' }
}
