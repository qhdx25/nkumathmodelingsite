<script setup>
// 全局景深数学背景（fixed 双画布，App.vue 挂一次，全站共用）
//  背景画布 z:-1：三层视差符号（远/中/近）+ 点阵 + 曲线，压在正文之下
//  前景画布 z:30：大符号只出现在左右两侧带内，越过正文边缘形成遮挡关系，
//                半出屏的超大符号加强景深；页头(z:40)仍在其上，保持干净
// 动效遵循 ai-design-skills：只动 transform 类绘制、离屏/隐藏即暂停、
// prefers-reduced-motion 只画一帧。
import { onBeforeUnmount, onMounted, ref } from 'vue'

const backC = ref(null)
const frontC = ref(null)

const GLYPHS = ['∑', '∫', '∂', '∇', 'π', 'λ', 'μ', 'θ', 'φ', 'ψ', 'Ψ', 'Ω', 'ε', 'δ', 'η', 'σ', '∞', '√', '±', '≈', '≅', 'ℝ', 'ℕ']

// 公式（Unicode 直接可渲染），和符号混排；偏长短不一
const FORMULAS = [
  'x² + y² = r²',
  'E = mc²',
  'a² + b² = c²',
  'eⁱπ + 1 = 0',
  'f′(x) = 0',
  'lim x → ∞',
  '∫ f(x) dx',
  '∑ λᵢ xᵢ',
  '∂u/∂t = κ∇²u',
  'x = (−b ± √Δ)/2a',
  'max cᵀx, Ax ≤ b',
  'min ‖Ax − b‖²',
  '∇·E = ρ/ε₀',
  'P(A|B) ∝ P(B|A)P(A)',
  'det(A) ≠ 0',
  'cov(X,Y) → 0',
]

// 远 → 近：字号越大越淡、越慢，滚动视差系数越小
// fRatio：该层里公式所占比例；公式按 0.55 倍字号渲染（字符串宽）
const LAYERS = [
  { n: 8, sMin: 150, sMax: 330, fMin: 320, fMax: 520, aMin: 0.024, aMax: 0.05, vy: 3.5, par: 0.02, sway: 26, fRatio: 3 },
  { n: 14, sMin: 46, sMax: 118, fMin: 200, fMax: 380, aMin: 0.05, aMax: 0.095, vy: 6.5, par: 0.055, sway: 18, fRatio: 4 },
  { n: 16, sMin: 22, sMax: 58, fMin: 130, fMax: 260, aMin: 0.1, aMax: 0.17, vy: 11, par: 0.1, sway: 12, fRatio: 3 },
]
const FRONT_N = 12

let bctx = null
let fctx = null
let w = 0
let h = 0
let back = []
let front = []
let raf = 0
let running = false
let reduced = false
const t0 = performance.now()

const rand = (a, b) => a + Math.random() * (b - a)
const mod = (v, m) => ((v % m) + m) % m
const shuffle = (arr) => {
  for (let i = arr.length - 1; i > 0; i--) {
    const j = (Math.random() * (i + 1)) | 0
    ;[arr[i], arr[j]] = [arr[j], arr[i]]
  }
  return arr
}

// 抖动网格布点：把视口切成 n 格，每格放一个元素再抖动，
// 保证符号/公式全屏均匀散开，不会聚成一坨；同层速度接近，散布长期保持
function spreadCells(n, w, h) {
  const cols = Math.max(2, Math.round(Math.sqrt((n * w) / h)))
  const rows = Math.max(1, Math.ceil(n / cols))
  const cells = []
  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) cells.push([c, r])
  }
  shuffle(cells)
  const cw = w / cols
  const chh = h / rows
  return cells.slice(0, n).map(([c, r]) => ({
    x: (c + rand(0.12, 0.88)) * cw,
    y: (r + rand(0.12, 0.88)) * chh,
  }))
}

function makeDot(l, pos, i) {
  const isFormula = i % l.fRatio === 0
  const text = isFormula
    ? FORMULAS[(Math.random() * FORMULAS.length) | 0]
    : GLYPHS[(Math.random() * GLYPHS.length) | 0]
  // 公式按目标宽度反算字号（Georgia 平均字宽约 0.5em），单符号直接随机字号
  const size = isFormula
    ? Math.max(16, rand(l.fMin, l.fMax) / (0.5 * text.length))
    : rand(l.sMin, l.sMax)
  return {
    x: pos.x,
    y: pos.y,
    s: size,
    text,
    isFormula,
    vy: l.vy * rand(0.85, 1.15),
    ph: Math.random() * Math.PI * 2,
    fq: rand(0.12, 0.4),
    a: rand(l.aMin, l.aMax),
    sway: l.sway * rand(0.6, 1.3) * (isFormula ? 0.5 : 1),
    par: l.par,
  }
}

function seed() {
  // 背景三层：每层用抖动网格保证全屏散开
  back = []
  for (const l of LAYERS) {
    const cells = spreadCells(l.n, w, h)
    back = back.concat(cells.map((pos, i) => makeDot(l, pos, i)))
  }
  // 前景：左右侧带，大符号 + 偶尔一条公式
  front = []
  const band = Math.max(90, w * 0.15)
  for (let i = 0; i < FRONT_N; i++) {
    const left = i % 2 === 0
    const x = left ? rand(-20, band) : w - rand(-20, band)
    front.push(
      makeDot(
        { sMin: 42, sMax: 150, aMin: 0.06, aMax: 0.13, vy: 8, par: 0.14, sway: 14, fRatio: 5 },
        { x, y: Math.random() * h },
        i,
      ),
    )
  }
  // 两个半出屏的超大符号：最前景的景深感
  front.push({
    ...makeDot({ sMin: 250, sMax: 330, aMin: 0.032, aMax: 0.045, vy: 2.5, par: 0.035, sway: 20, fRatio: 99 }, { x: -70, y: Math.random() * h }, 1),
    text: '∑',
    isFormula: false,
  })
  front.push({
    ...makeDot({ sMin: 230, sMax: 310, aMin: 0.032, aMax: 0.045, vy: 2.5, par: 0.035, sway: 20, fRatio: 99 }, { x: w + 70, y: Math.random() * h }, 2),
    text: 'ψ',
    isFormula: false,
  })
}

function setup() {
  const dpr = Math.min(window.devicePixelRatio || 1, 1.5)
  w = Math.max(1, window.innerWidth)
  h = Math.max(1, window.innerHeight)
  for (const cv of [backC.value, frontC.value]) {
    if (!cv) continue
    cv.width = Math.round(w * dpr)
    cv.height = Math.round(h * dpr)
    cv.style.width = `${w}px`
    cv.style.height = `${h}px`
    const c = cv.getContext('2d')
    c.setTransform(dpr, 0, 0, dpr, 0, 0)
    if (cv === backC.value) bctx = c
    else fctx = c
  }
  seed()
  draw(performance.now())
}

function drawGlyphs(ctx, list, sy, t) {
  const range = h + 200
  for (const d of list) {
    d.y -= d.vy / 60
    const yy = mod(d.y - sy * d.par, range) - 100
    const xx = d.x + Math.sin(t * d.fq * 2 + d.ph) * d.sway
    ctx.save()
    ctx.translate(xx, yy)
    ctx.rotate(Math.sin(t * 0.22 + d.ph) * (d.isFormula ? 0.05 : 0.13))
    ctx.font = `${d.s}px Georgia, 'Times New Roman', serif`
    ctx.fillStyle = `rgba(113, 10, 83, ${d.a})`
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'
    ctx.fillText(d.text, 0, 0)
    ctx.restore()
  }
}

function drawGrid() {
  bctx.fillStyle = 'rgba(113, 10, 83, 0.04)'
  const gap = 34
  for (let x = gap / 2; x < w; x += gap) {
    for (let y = gap / 2; y < h; y += gap) {
      bctx.fillRect(x, y, 1.4, 1.4)
    }
  }
}

// 正弦曲线 + 移动亮点（示波器感）
function drawSine(t) {
  const midY = h * 0.7
  const amp = h * 0.13
  bctx.strokeStyle = 'rgba(113, 10, 83, 0.09)'
  bctx.lineWidth = 1.2
  bctx.beginPath()
  for (let x = 0; x <= w; x += 7) {
    const y = midY + Math.sin(x / 110 + t * 0.6) * amp * Math.sin((x / w) * Math.PI)
    if (x === 0) bctx.moveTo(x, y)
    else bctx.lineTo(x, y)
  }
  bctx.stroke()
  const px = (t * 50) % (w + 60) - 30
  const py = midY + Math.sin(px / 110 + t * 0.6) * amp * Math.sin((px / w) * Math.PI)
  bctx.fillStyle = 'rgba(113, 10, 83, 0.3)'
  bctx.beginPath()
  bctx.arc(px, py, 2.6, 0, Math.PI * 2)
  bctx.fill()
}

// 大号五瓣玫瑰线，慢速旋转
function drawRose(t) {
  const cx = w * 0.87
  const cy = h * 0.3
  const R = Math.min(h * 0.26, 190)
  bctx.strokeStyle = 'rgba(113, 10, 83, 0.07)'
  bctx.lineWidth = 1
  bctx.beginPath()
  for (let i = 0; i <= 360; i += 2) {
    const th = (i * Math.PI) / 180
    const r = R * Math.cos(5 * th + t * 0.22)
    const x = cx + r * Math.cos(th)
    const y = cy + r * Math.sin(th)
    if (i === 0) bctx.moveTo(x, y)
    else bctx.lineTo(x, y)
  }
  bctx.stroke()
}

function draw(now) {
  const t = (now - t0) / 1000
  const sy = window.scrollY || 0
  if (bctx) {
    bctx.clearRect(0, 0, w, h)
    drawGrid()
    for (let i = 0; i < LAYERS.length; i++) {
      drawGlyphs(bctx, back.slice(i * LAYERS[i].n, (i + 1) * LAYERS[i].n), sy, t)
    }
    drawSine(t)
    drawRose(t)
  }
  if (fctx && w >= 760) {
    fctx.clearRect(0, 0, w, h)
    drawGlyphs(fctx, front, sy, t)
  }
}

function loop(now) {
  draw(now)
  if (running) raf = requestAnimationFrame(loop)
}

function play() {
  if (running || reduced || document.hidden) return
  running = true
  raf = requestAnimationFrame(loop)
}

function pause() {
  running = false
  cancelAnimationFrame(raf)
}

function onVis() {
  if (document.hidden) pause()
  else play()
}

onMounted(() => {
  reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  setup()
  window.addEventListener('resize', setup)
  document.addEventListener('visibilitychange', onVis)
  play()
})

onBeforeUnmount(() => {
  pause()
  window.removeEventListener('resize', setup)
  document.removeEventListener('visibilitychange', onVis)
})
</script>

<template>
  <canvas ref="backC" class="mathbg-back" aria-hidden="true"></canvas>
  <canvas ref="frontC" class="mathbg-front" aria-hidden="true"></canvas>
</template>
