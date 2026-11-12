// 建模资料：五个分类（历年真题 / 历年优秀论文 / LaTeX / Python / MATLAB）
// 原则：只写真实存在的链接；拿不到的内容用 placeholder 说明缺什么，不编造地址

export const feishu = {
  title: '飞书建模资料总入口',
  desc: '历年竞赛真题、优秀论文、常用模型和工具教程，按分类归档在飞书知识库内。',
  url: 'https://nankai.feishu.cn/wiki/CMSXwe42YiGJtpkxSYHcaO5inwb',
}

export const groups = [
  {
    id: 'problems',
    kicker: '真题',
    title: '历年真题',
    desc: '国赛、美赛、MathorCup、深圳杯、五校联赛的历年题目与数据附件。',
    items: [
      { label: '全国大学生数学建模竞赛（国赛）', note: '赛题、优秀论文与竞赛通知', href: 'https://www.mcm.edu.cn/' },
      { label: '美国大学生数学建模竞赛（美赛）', note: 'MCM / ICM 历年赛题', href: 'https://www.contest.comap.com/undergraduate/contests/' },
      { label: 'MathorCup 高校数学建模挑战赛', note: '报名页与赛题发布', href: 'https://www.mathorcup.org/' },
      { label: '“深圳杯”数学建模挑战赛', note: '组委会官方站', href: 'http://www.m2ct.org/' },
    ],
    placeholder: '本地整理的「按年份打包真题 + 数据附件」尚未迁入，先用飞书总入口或上面各官网查看。',
  },
  {
    id: 'papers',
    kicker: '论文',
    title: '历年优秀论文',
    desc: '2021—2025 年国赛获奖论文，按年份、题型分组，可展开到具体篇目。',
    items: [],
    placeholder: '',
    embed: 'papers',
  },
  {
    id: 'latex',
    kicker: '排版',
    title: 'LaTeX 资料',
    desc: '论文模板、公式与图表排版、编译环境配置。',
    items: [],
    placeholder:
      '待补充：国赛论文 LaTeX 模板（含封面与页边距设置）、常用宏包清单、Overleaf 项目示例、本地 TeXLive 安装指引。',
  },
  {
    id: 'python',
    kicker: '编程',
    title: 'Python 资料',
    desc: '环境配置、数据处理、常用建模库与绘图规范。',
    items: [],
    placeholder:
      '待补充：Anaconda / venv 环境配置、numpy-pandas 数据处理速查、scipy 优化与拟合、matplotlib 出图规范（中文字体、分辨率、配色）。',
  },
  {
    id: 'matlab',
    kicker: '编程',
    title: 'MATLAB 入门资料',
    desc: '零基础入门、常用工具箱与建模常用函数。',
    items: [],
    placeholder:
      '待补充：MATLAB 安装与校园授权说明、基础语法速成、优化工具箱（linprog / fmincon）、曲线拟合与插值、绘图与论文配图。',
  },
]

// 原站的培训四栏，收敛到校队培训页，这里保留一份以便资料页复用
export const guide = [
  { title: '入门导学', items: ['建模基本流程', '常见模型梳理', '工具链安装指引'] },
  { title: '写作模板', items: ['LaTeX 模板', '论文结构示意', '图表与附录建议'] },
]
