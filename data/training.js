// 校队培训：培训资料链接 + 代表队培训通知
// 本页由其他同学负责建设，这里只搭骨架、留位置，内容未到位的写清楚缺什么

export const owner = {
  note: '本页面由校队培训负责人建设，当前为结构占位版。',
  contact: '资料与通知的维护入口确定后在此处补上。',
}

// 培训资料链接：已确定的只有飞书总入口，其余按缺项列出
export const resources = [
  {
    label: '飞书 · 培训资料总入口',
    desc: '讲义、示例代码、往届讲评回放集中在飞书知识库。',
    href: 'https://nankai.feishu.cn/wiki/CMSXwe42YiGJtpkxSYHcaO5inwb',
    status: 'ok',
  },
  { label: '培训讲义（PDF / PPT）', desc: '按专题整理，供课后复习。', status: 'pending' },
  { label: '讲评与回放录像', desc: '模拟赛讲评、往届培训录像。', status: 'pending' },
  { label: '校队选拔与训练安排表', desc: '本学期训练课表、时间地点、主讲人。', status: 'pending' },
]

// 培训内容体系：沿用原站的四栏划分
export const tracks = [
  {
    title: '入门导学',
    desc: '第一次接触建模从这里开始',
    items: ['建模基本流程', '常见模型梳理', '工具链安装指引'],
  },
  {
    title: '竞赛训练',
    desc: '以赛代练，按真题推进',
    items: ['历年赛题归档', '模拟赛资料', '复盘与讲评记录'],
  },
  {
    title: '写作模板',
    desc: '把结果写成能得分的论文',
    items: ['LaTeX 模板', '论文结构示意', '图表与附录建议'],
  },
  {
    title: '经验沉淀',
    desc: '老队员踩过的坑',
    items: ['组队建议', '时间管理方法', '展示答辩与复盘心得'],
  },
]

// 代表队培训通知：一条都还没有，等负责人提供
export const notices = []
