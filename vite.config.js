import { defineConfig } from 'vite'
import { viteSingleFile } from 'vite-plugin-singlefile'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig(({ mode }) => {
  const single = process.env.SINGLE_FILE === '1'
  return {
  plugins: [single && viteSingleFile(), vue()],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./', import.meta.url)),
      },
    },
    build: single
      ? {
          // 全部图片内联成 data URL，产出单个可双击打开的 HTML
          assetsInlineLimit: 100_000_000,
          cssCodeSplit: false,
        }
      : undefined,
  }
})
