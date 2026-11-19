import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import 'element-plus/dist/index.css'
import './styles.css'

import App from './App.vue'
import router from './router'

const app = createApp(App)

// Pinia：Vue 3 官方状态管理库，替代 Vuex
app.use(createPinia())
// 路由：页面导航与登录守卫
app.use(router)
// Element Plus 组件库；传 zhCn 让分页、日期选择器等显示中文
app.use(ElementPlus, { locale: zhCn })

app.mount('#app')
