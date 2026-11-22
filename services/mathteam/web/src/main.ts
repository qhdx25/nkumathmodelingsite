import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElAvatar from 'element-plus/es/components/avatar/index.mjs'
import ElBadge from 'element-plus/es/components/badge/index.mjs'
import ElButton from 'element-plus/es/components/button/index.mjs'
import ElCard from 'element-plus/es/components/card/index.mjs'
import ElConfigProvider from 'element-plus/es/components/config-provider/index.mjs'
import ElContainer, {
  ElAside,
  ElHeader,
  ElMain,
} from 'element-plus/es/components/container/index.mjs'
import ElDialog from 'element-plus/es/components/dialog/index.mjs'
import ElDrawer from 'element-plus/es/components/drawer/index.mjs'
import ElEmpty from 'element-plus/es/components/empty/index.mjs'
import ElForm, { ElFormItem } from 'element-plus/es/components/form/index.mjs'
import ElIcon from 'element-plus/es/components/icon/index.mjs'
import ElInput from 'element-plus/es/components/input/index.mjs'
import ElInputNumber from 'element-plus/es/components/input-number/index.mjs'
import ElLoading from 'element-plus/es/components/loading/index.mjs'
import ElMenu, { ElMenuItem } from 'element-plus/es/components/menu/index.mjs'
import ElPagination from 'element-plus/es/components/pagination/index.mjs'
import ElProgress from 'element-plus/es/components/progress/index.mjs'
import ElRadioGroup, {
  ElRadioButton,
} from 'element-plus/es/components/radio/index.mjs'
import ElRate from 'element-plus/es/components/rate/index.mjs'
import ElSelect, { ElOption } from 'element-plus/es/components/select/index.mjs'
import ElTable, { ElTableColumn } from 'element-plus/es/components/table/index.mjs'
import ElTabs, { ElTabPane } from 'element-plus/es/components/tabs/index.mjs'
import ElTag from 'element-plus/es/components/tag/index.mjs'
import ElTimeline, {
  ElTimelineItem,
} from 'element-plus/es/components/timeline/index.mjs'
import 'element-plus/dist/index.css'
import './styles.css'

import App from './App.vue'
import router from './router'

const app = createApp(App)

// Pinia：Vue 3 官方状态管理库，替代 Vuex
app.use(createPinia())
// 路由：页面导航与登录守卫
app.use(router)
// 只注册项目实际使用的组件，避免把 Element Plus 全量 JS 打进主包。
const elementComponents = [
  ElAside, ElAvatar, ElBadge, ElButton, ElCard, ElConfigProvider, ElContainer,
  ElDialog, ElDrawer, ElEmpty, ElForm, ElFormItem, ElHeader, ElIcon,
  ElInput, ElInputNumber, ElLoading, ElMain, ElMenu, ElMenuItem, ElOption,
  ElPagination, ElProgress, ElRadioButton, ElRadioGroup, ElRate, ElSelect,
  ElTabPane, ElTable, ElTableColumn, ElTabs, ElTag, ElTimeline,
  ElTimelineItem,
]
for (const component of elementComponents) {
  app.use(component)
}

app.mount('#app')
