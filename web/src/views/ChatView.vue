<script setup lang="ts">
import { nextTick, onMounted, onUnmounted, ref } from 'vue'
import ElMessage from 'element-plus/es/components/message/index.mjs'
import { messageApi, teamApi } from '@/api'
import { getToken } from '@/api'
import type { MessageOut, TeamOut } from '@/types'
import { useUserStore } from '@/stores/user'
import { formatDate } from '@/utils/format'

const store = useUserStore()
const teams = ref<TeamOut[]>([])
const teamId = ref<number | null>(null)
const messages = ref<MessageOut[]>([])
const input = ref('')
const socket = ref<WebSocket | null>(null)
const listEl = ref<HTMLElement | null>(null)
const connected = ref(false)

async function loadTeams() {
  teams.value = await teamApi.mine()
  if (teams.value.length) {
    teamId.value = teams.value[0].id
    await loadHistory()
    connect()
  }
}

async function loadHistory() {
  if (teamId.value === null) return
  messages.value = await messageApi.history(teamId.value, 0, 100)
  await scrollToBottom()
}

function connect() {
  const token = getToken()
  if (teamId.value === null || !token) return
  socket.value?.close()

  // WebSocket 无法通过 JS 设置自定义 Authorization 头，因此按后端设计用查询参数传 token
  const protocol = location.protocol === 'https:' ? 'wss' : 'ws'
  // 开发时 Vite 把 /ws 代理到 FastAPI；生产需把 host 换成后端域名
  const url = `${protocol}://${location.host}/ws/teams/${teamId.value}`
  // token 放入 WebSocket 子协议，不放进 URL，避免被代理访问日志记录。
  const ws = new WebSocket(url, ['bearer', token])
  socket.value = ws

  ws.onopen = () => { connected.value = true }
  ws.onclose = () => {
    connected.value = false
    if (teamId.value !== null) setTimeout(connect, 2000)  // 断线自动重连
  }
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data)
    if (data.type === 'message') {
      messages.value.push({
        id: data.id, team_id: teamId.value!, sender_id: data.sender_id,
        sender_name: data.sender_name, content: data.content,
        message_type: 'text', created_at: data.created_at,
      })
      scrollToBottom()
    } else if (data.type === 'system') {
      ElMessage.info(data.content)
    }
  }
}

function send() {
  const content = input.value.trim()
  if (!content) return
  if (!socket.value || socket.value.readyState !== WebSocket.OPEN) {
    ElMessage.warning('连接尚未就绪，请稍候')
    return
  }
  socket.value.send(JSON.stringify({ content }))
  input.value = ''
}

async function scrollToBottom() {
  await nextTick()
  if (listEl.value) listEl.value.scrollTop = listEl.value.scrollHeight
}

function switchTeam(id: number) {
  teamId.value = id
  loadHistory()
  connect()
}

onMounted(loadTeams)
onUnmounted(() => {
  // 组件卸载时主动关闭，避免重连定时器在后台持续运行
  socket.value?.close()
  socket.value = null
})
</script>

<template>
  <div class="page">
    <h1 class="page-title">团队交流</h1>
    <p class="page-desc">团队内部实时聊天，历史消息走 REST 接口、新消息通过 WebSocket 推送</p>

    <div class="toolbar">
      <el-select :model-value="teamId" placeholder="选择团队" style="width: 220px" @change="switchTeam">
        <el-option v-for="t in teams" :key="t.id" :label="t.name" :value="t.id" />
      </el-select>
      <el-tag :type="connected ? 'success' : 'info'">{{ connected ? '已连接' : '连接中/离线' }}</el-tag>
    </div>

    <el-card v-if="teamId" class="chat-card">
      <div ref="listEl" class="message-list">
        <div v-for="m in messages" :key="m.id" class="message" :class="{ mine: m.sender_id === store.user?.id }">
          <div class="meta">
            <strong>{{ m.sender_name }}</strong>
            <span class="muted">{{ formatDate(m.created_at) }}</span>
          </div>
          <div class="bubble">{{ m.content }}</div>
        </div>
        <el-empty v-if="!messages.length" description="还没有消息，开始聊天吧" />
      </div>
      <div class="composer">
        <el-input v-model="input" placeholder="输入消息，回车发送" @keyup.enter="send" />
        <el-button type="primary" @click="send">发送</el-button>
      </div>
    </el-card>
    <el-empty v-else description="你还没有加入团队，无法聊天" />
  </div>
</template>

<style scoped>
.chat-card { height: 620px; display: flex; flex-direction: column; }
.message-list { flex: 1; overflow-y: auto; padding: 8px 12px; }
.message { margin: 12px 0; max-width: 70%; }
.message.mine { margin-left: auto; text-align: right; }
.meta { font-size: 12px; color: #6b7280; margin-bottom: 4px; display: flex; gap: 10px; }
.message.mine .meta { justify-content: flex-end; }
.bubble {
  display: inline-block; padding: 9px 13px; border-radius: 10px;
  background: #f1f5f9; text-align: left; word-break: break-all;
}
.message.mine .bubble { background: #4f46e5; color: #fff; }
.composer { display: flex; gap: 10px; padding-top: 12px; border-top: 1px solid #e5e7eb; }
</style>
