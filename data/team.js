// 组队平台：论坛形态的骨架。功能由其他同学负责，这里只定版式与留白

export const boards = [
  { id: 'all', label: '全部' },
  { id: 'team', label: '找队友' },
  { id: 'join', label: '找队伍' },
  { id: 'talk', label: '经验交流' },
  { id: 'notice', label: '板块公告' },
]

// 真实帖子尚未接入，用结构示意占位（明确标注，避免被误当成真实数据）
export const samplePosts = [
  {
    board: '找队友',
    title: '示例帖：这里显示帖子标题，一行放不下会折行',
    author: '发帖人',
    meta: '帖子的发布时间 · 回复数 · 最后回复',
    replies: 0,
    placeholder: true,
  },
  {
    board: '找队伍',
    title: '示例帖：招募帖可以写明方向、需要的角色和联系方式',
    author: '发帖人',
    meta: '帖子的发布时间 · 回复数 · 最后回复',
    replies: 0,
    placeholder: true,
  },
  {
    board: '经验交流',
    title: '示例帖：经验帖、复盘、资料分享都放在这个板块',
    author: '发帖人',
    meta: '帖子的发布时间 · 回复数 · 最后回复',
    replies: 0,
    placeholder: true,
  },
]

export const planned = [
  '发帖 / 回帖：需要登录，建议复用学校统一身份或飞书扫码',
  '板块与标签：找队友、找队伍、经验交流、板块公告',
  '筛选：按赛事（国赛 / 美赛 / 校赛）与年级、专业标签过滤',
  '联系方式保护：不公开展示手机号，改用站内私信或表单',
]
