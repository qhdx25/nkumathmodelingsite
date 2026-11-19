import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      // 用 @ 代替冗长的相对路径，例如 import api from '@/api'
      // 使用 URL.pathname 避免引入 @types/node
      '@': new URL('./src', import.meta.url).pathname,
    },
  },
  server: {
    port: 5173,
    // 开发时把 /api 和 /ws 请求转发给 FastAPI（8000 端口），
    // 这样前端代码里只写相对路径，不存在跨域问题。
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://127.0.0.1:8000',
        ws: true,
        changeOrigin: true,
      },
    },
  },
})
