// 静态资源解析器：让 dev / 常规构建 / 单文件预览构建都能取到图片
// - 单文件构建：import.meta.glob 把 assets 下的图全部内联成 data URL
// - dev / 常规构建：glob 返回对应的资源 URL
// 调用方继续传站点内部路径（如 '/img/hero/nku-01.jpg'、'/pages/<slug>/p01.webp'），
// 查不到时原样返回（保持 public/ 兜底行为）。
const imgUrls = import.meta.glob('./img/**/*.{jpg,jpeg,png,webp,svg}', {
  eager: true,
  query: '?url',
  import: 'default',
})
const pageUrls = import.meta.glob('./pages/**/*.{webp,png,jpg}', {
  eager: true,
  query: '?url',
  import: 'default',
})

const map = {}
for (const [file, url] of Object.entries(imgUrls)) map[file.replace('./', '/')] = url
for (const [file, url] of Object.entries(pageUrls)) map[file.replace('./', '/')] = url

export function assetUrl(path) {
  if (!path) return path
  return map[path] ?? path
}

export const imgUrl = assetUrl
