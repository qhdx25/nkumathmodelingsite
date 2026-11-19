<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref } from 'vue'
import {
  Document,
  Picture,
  VideoCamera,
} from '@element-plus/icons-vue'
import ElMessage from 'element-plus/es/components/message/index.mjs'
import { messageApi, teamApi, getToken } from '@/api'
import type {
  ChatPolicy,
  MessageOut,
  TeamDetail,
  TeamOut,
} from '@/types'
import { useUserStore } from '@/stores/user'
import { formatDate, label } from '@/utils/format'

interface SystemNotice {
  id: string
  content: string
}

interface PresenceEvent {
  type: 'presence'
  online_user_ids: number[]
}

const store = useUserStore()
const teams = ref<TeamOut[]>([])
const team = ref<TeamDetail | null>(null)
const teamId = ref<number | null>(null)
const messages = ref<MessageOut[]>([])
const notices = ref<SystemNotice[]>([])
const onlineUserIds = ref<Set<number>>(new Set())
const input = ref('')
const socket = ref<WebSocket | null>(null)
const listEl = ref<HTMLElement | null>(null)
const connected = ref(false)
const unreadCount = ref(0)
const atBottom = ref(true)
const reconnectTimer = ref<number | null>(null)
const policy = ref<ChatPolicy | null>(null)
const fileInput = ref<HTMLInputElement | null>(null)
const pickerAccept = ref('')
const uploading = ref(false)
const attachmentUrls = ref<Record<number, string>>({})
const loadingAttachmentIds = ref<number[]>([])
let manuallyClosed = false

const onlineCount = computed(() => {
  if (!team.value) return 0
  return team.value.members.filter((member) =>
    onlineUserIds.value.has(member.user_id),
  ).length
})

async function loadTeams() {
  const [teamRows, chatPolicy] = await Promise.all([
    teamApi.mine(),
    messageApi.policy(),
  ])
  teams.value = teamRows
  policy.value = chatPolicy
  if (!teams.value.length) return
  teamId.value = teams.value[0].id
  await loadConversation()
}

async function loadConversation() {
  if (teamId.value === null) return
  revokeAttachmentUrls()
  const [detail, history] = await Promise.all([
    teamApi.detail(teamId.value),
    messageApi.history(teamId.value, 0, 200),
  ])
  team.value = detail
  messages.value = history
  for (const message of messages.value) {
    if (message.attachment?.kind === 'image' && !message.attachment.expired) {
      void loadAttachment(message)
    }
  }
  notices.value = []
  unreadCount.value = 0
  connect()
  await scrollToBottom()
}

function connect() {
  const token = getToken()
  if (teamId.value === null || !token) return
  clearReconnectTimer()
  socket.value?.close()
  manuallyClosed = false

  const protocol = location.protocol === 'https:' ? 'wss' : 'ws'
  const url = `${protocol}://${location.host}/ws/teams/${teamId.value}`
  // JWT 通过 WebSocket 子协议传递，避免出现在 URL 和代理访问日志中。
  const ws = new WebSocket(url, ['bearer', token])
  socket.value = ws

  ws.onopen = () => {
    connected.value = true
  }
  ws.onclose = () => {
    connected.value = false
    if (!manuallyClosed && teamId.value !== null) {
      reconnectTimer.value = window.setTimeout(connect, 2000)
    }
  }
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data)
    if (data.type === 'message') {
      if (messages.value.some((message) => message.id === data.id)) return
      const message: MessageOut = {
        id: data.id,
        team_id: teamId.value!,
        sender_id: data.sender_id,
        sender_name: data.sender_name,
        content: data.content,
        message_type: data.message_type || 'text',
        attachment: data.attachment || null,
        created_at: data.created_at,
      }
      messages.value.push(message)
      if (message.attachment?.kind === 'image' && !message.attachment.expired) {
        void loadAttachment(message)
      }
      if (data.sender_id !== store.user?.id && !atBottom.value) {
        unreadCount.value += 1
      }
      scrollToBottom()
    } else if (data.type === 'presence') {
      onlineUserIds.value = new Set(
        (data as PresenceEvent).online_user_ids || [],
      )
    } else if (data.type === 'system') {
      notices.value.push({
        id: `${Date.now()}-${Math.random()}`,
        content: data.content,
      })
      notices.value = notices.value.slice(-5)
    } else if (data.type === 'error') {
      ElMessage.warning(data.content)
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
  if (content.length > 1000) {
    ElMessage.warning('消息不能超过 1000 个字符')
    return
  }
  socket.value.send(JSON.stringify({ content }))
  input.value = ''
}

function onComposerKeydown(event: KeyboardEvent) {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    send()
  }
}

async function scrollToBottom() {
  await nextTick()
  if (listEl.value) {
    listEl.value.scrollTop = listEl.value.scrollHeight
    atBottom.value = true
    unreadCount.value = 0
  }
}

function onConversationScroll() {
  if (!listEl.value) return
  const gap =
    listEl.value.scrollHeight -
    listEl.value.scrollTop -
    listEl.value.clientHeight
  atBottom.value = gap < 80
  if (atBottom.value) unreadCount.value = 0
}

function switchTeam(id: number) {
  manuallyClosed = true
  socket.value?.close()
  teamId.value = id
  loadConversation()
}

function isOnline(userId: number): boolean {
  return onlineUserIds.value.has(userId)
}

function avatarText(name: string): string {
  return name.trim().slice(0, 1).toUpperCase() || '?'
}

function dayLabel(value: string): string {
  return new Date(value).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    weekday: 'short',
  })
}

function showDay(index: number): boolean {
  if (index === 0) return true
  return dayLabel(messages.value[index - 1].created_at) !==
    dayLabel(messages.value[index].created_at)
}

function clearReconnectTimer() {
  if (reconnectTimer.value !== null) {
    window.clearTimeout(reconnectTimer.value)
    reconnectTimer.value = null
  }
}

function pickFile(kind: 'image' | 'video' | 'file') {
  pickerAccept.value =
    kind === 'image' ? 'image/*' : kind === 'video' ? 'video/*' : ''
  nextTick(() => fileInput.value?.click())
}

async function onFileSelected(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  target.value = ''
  if (!file || teamId.value === null) return
  if (policy.value && file.size > policy.value.max_bytes) {
    ElMessage.warning(`文件不能超过 ${formatFileSize(policy.value.max_bytes)}`)
    return
  }

  uploading.value = true
  try {
    const message = await messageApi.uploadAttachment(
      teamId.value,
      file,
      input.value.trim(),
    )
    if (!messages.value.some((item) => item.id === message.id)) {
      messages.value.push(message)
    }
    input.value = ''
    if (message.attachment?.kind === 'image') {
      void loadAttachment(message)
    }
    await scrollToBottom()
  } catch {
    // Axios 拦截器统一提示，保留输入框内容便于重试。
  } finally {
    uploading.value = false
  }
}

async function loadAttachment(message: MessageOut): Promise<string | null> {
  const existing = attachmentUrls.value[message.id]
  if (existing) return existing
  if (!message.attachment || message.attachment.expired) return null
  if (loadingAttachmentIds.value.includes(message.id)) return null

  loadingAttachmentIds.value.push(message.id)
  try {
    const blob = await messageApi.attachmentBlob(message.id)
    const url = URL.createObjectURL(blob)
    attachmentUrls.value = { ...attachmentUrls.value, [message.id]: url }
    return url
  } catch {
    ElMessage.warning('附件加载失败，可能已超过保留期')
    return null
  } finally {
    loadingAttachmentIds.value = loadingAttachmentIds.value.filter(
      (id) => id !== message.id,
    )
  }
}

async function playVideo(message: MessageOut) {
  const url = await loadAttachment(message)
  if (!url) return
  await nextTick()
}

async function downloadAttachment(message: MessageOut) {
  const url = await loadAttachment(message)
  if (!url || !message.attachment) return
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = message.attachment.name
  anchor.click()
}

function isAttachmentLoading(messageId: number): boolean {
  return loadingAttachmentIds.value.includes(messageId)
}

function attachmentCaption(message: MessageOut): string {
  return /^\[(image|video|file)\]/.test(message.content)
    ? ''
    : message.content
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`
}

function revokeAttachmentUrls() {
  for (const url of Object.values(attachmentUrls.value)) {
    URL.revokeObjectURL(url)
  }
  attachmentUrls.value = {}
}

onMounted(loadTeams)
onUnmounted(() => {
  manuallyClosed = true
  clearReconnectTimer()
  socket.value?.close()
  socket.value = null
  revokeAttachmentUrls()
})
</script>

<template>
  <div class="page">
    <div class="page-heading">
      <div>
        <h1 class="page-title">团队会话</h1>
        <p class="page-desc">
          像即时通讯工具一样查看成员在线状态、历史消息并实时交流
        </p>
      </div>
      <el-tag :type="connected ? 'success' : 'info'">
        {{ connected ? '实时连接已建立' : '正在重连' }}
      </el-tag>
    </div>

    <el-card v-if="teamId" class="chat-card" :body-style="{ padding: '0' }">
      <div class="conversation-shell">
        <aside class="member-panel">
          <div class="team-summary">
            <div class="team-avatar">{{ avatarText(team?.name || '队') }}</div>
            <div>
              <strong>{{ team?.name }}</strong>
              <div class="muted">
                {{ label(team?.status || '') }} ·
                {{ team?.member_count || 0 }}/{{ team?.max_size || 0 }} 人
              </div>
            </div>
          </div>

          <el-select
            v-if="teams.length > 1"
            :model-value="teamId"
            placeholder="选择团队"
            class="team-select"
            @change="switchTeam"
          >
            <el-option
              v-for="item in teams"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>

          <div class="member-title">
            <span>团队成员</span>
            <span class="muted">{{ onlineCount }} 人在线</span>
          </div>
          <div
            v-for="member in team?.members || []"
            :key="member.user_id"
            class="member-item"
          >
            <el-avatar :size="34">{{ avatarText(member.username) }}</el-avatar>
            <div class="member-meta">
              <div class="member-name">
                {{ member.username }}
                <span v-if="member.user_id === store.user?.id" class="self-tag">我</span>
              </div>
              <div class="muted">
                {{ member.role === 'leader' ? '队长' : '队员' }}
              </div>
            </div>
            <span
              class="presence-dot"
              :class="{ online: isOnline(member.user_id) }"
              :title="isOnline(member.user_id) ? '在线' : '离线'"
            />
          </div>

          <div class="room-tip">
            <strong>会话说明</strong>
            <p>
              Enter 发送，Shift + Enter 换行。图片、视频和文件最多保留
              {{ policy?.retention_hours || 24 }} 小时。
            </p>
          </div>
        </aside>

        <section class="conversation-panel">
          <header class="conversation-header">
            <div>
              <strong>{{ team?.name }}</strong>
              <div class="muted">
                {{ onlineCount }} / {{ team?.member_count || 0 }} 人在线
              </div>
            </div>
            <el-tag size="small" effect="plain">
              {{ label(team?.status || '') }}
            </el-tag>
          </header>

          <div
            ref="listEl"
            class="message-list"
            @scroll="onConversationScroll"
          >
            <template v-for="(message, index) in messages" :key="message.id">
              <div v-if="showDay(index)" class="day-divider">
                {{ dayLabel(message.created_at) }}
              </div>
              <div
                class="message"
                :class="{ mine: message.sender_id === store.user?.id }"
              >
                <el-avatar
                  v-if="message.sender_id !== store.user?.id"
                  :size="34"
                  class="message-avatar"
                >
                  {{ avatarText(message.sender_name) }}
                </el-avatar>
                <div class="message-body">
                  <div class="meta">
                    <strong>{{ message.sender_name }}</strong>
                    <span>{{ formatDate(message.created_at) }}</span>
                  </div>
                  <div
                    v-if="message.message_type === 'resource' && message.attachment"
                    class="attachment-card"
                  >
                    <div class="attachment-heading">
                      <el-icon>
                        <Picture v-if="message.attachment.kind === 'image'" />
                        <VideoCamera v-else-if="message.attachment.kind === 'video'" />
                        <Document v-else />
                      </el-icon>
                      <div class="attachment-name">
                        <strong>{{ message.attachment.name }}</strong>
                        <span>
                          {{ formatFileSize(message.attachment.size) }} ·
                          {{ formatDate(message.attachment.expires_at) }} 过期
                        </span>
                      </div>
                    </div>

                    <div v-if="message.attachment.expired" class="attachment-expired">
                      附件已过期，服务器仅保留 {{ policy?.retention_hours || 24 }} 小时
                    </div>
                    <template v-else-if="message.attachment.kind === 'image'">
                      <img
                        v-if="attachmentUrls[message.id]"
                        :src="attachmentUrls[message.id]"
                        :alt="message.attachment.name"
                        class="message-image"
                        @click="downloadAttachment(message)"
                      />
                      <div
                        v-else
                        class="attachment-loading"
                        @click="loadAttachment(message)"
                      >
                        {{ isAttachmentLoading(message.id) ? '图片加载中…' : '点击加载图片' }}
                      </div>
                    </template>
                    <template v-else-if="message.attachment.kind === 'video'">
                      <video
                        v-if="attachmentUrls[message.id]"
                        :src="attachmentUrls[message.id]"
                        controls
                        preload="metadata"
                        class="message-video"
                      />
                      <el-button
                        v-else
                        size="small"
                        :loading="isAttachmentLoading(message.id)"
                        @click="playVideo(message)"
                      >
                        播放视频
                      </el-button>
                    </template>
                    <el-button
                      v-else
                      size="small"
                      :loading="isAttachmentLoading(message.id)"
                      @click="downloadAttachment(message)"
                    >
                      下载文件
                    </el-button>
                    <p v-if="attachmentCaption(message)" class="attachment-caption">
                      {{ attachmentCaption(message) }}
                    </p>
                  </div>
                  <div
                    v-else
                    class="bubble"
                  >
                    {{ message.content }}
                  </div>
                </div>
              </div>
            </template>

            <div
              v-for="notice in notices"
              :key="notice.id"
              class="system-notice"
            >
              {{ notice.content }}
            </div>
            <el-empty
              v-if="!messages.length && !notices.length"
              description="还没有消息，开始第一次团队讨论吧"
            />
          </div>

          <button
            v-if="unreadCount > 0"
            class="new-message-button"
            @click="scrollToBottom"
          >
            {{ unreadCount }} 条新消息，回到最新
          </button>

          <footer class="composer">
            <div class="attachment-toolbar">
              <span class="muted">临时附件</span>
              <el-button link type="primary" :disabled="uploading" @click="pickFile('image')">
                <el-icon><Picture /></el-icon> 图片
              </el-button>
              <el-button link type="primary" :disabled="uploading" @click="pickFile('video')">
                <el-icon><VideoCamera /></el-icon> 视频
              </el-button>
              <el-button link type="primary" :disabled="uploading" @click="pickFile('file')">
                <el-icon><Document /></el-icon> 文件
              </el-button>
              <span class="muted toolbar-hint">
                单个不超过 {{ formatFileSize(policy?.max_bytes || 0) }}，服务器仅保留
                {{ policy?.retention_hours || 24 }} 小时
              </span>
              <input
                ref="fileInput"
                type="file"
                class="hidden-file-input"
                :accept="pickerAccept"
                @change="onFileSelected"
              />
            </div>
            <el-input
              v-model="input"
              type="textarea"
              :autosize="{ minRows: 2, maxRows: 5 }"
              maxlength="1000"
              show-word-limit
              resize="none"
              placeholder="输入消息，Enter 发送，Shift + Enter 换行"
              @keydown="onComposerKeydown"
            />
            <div class="composer-footer">
              <span class="muted">
                {{ uploading ? '附件上传中…' : connected ? '在线同步中' : '连接恢复后可发送文字' }}
              </span>
              <el-button
                type="primary"
                :disabled="!connected || !input.trim()"
                @click="send"
              >
                发送
              </el-button>
            </div>
          </footer>
        </section>
      </div>
    </el-card>
    <el-empty v-else description="你还没有加入团队，无法进入团队会话" />
  </div>
</template>

<style scoped>
.page-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 20px;
}

.chat-card {
  overflow: hidden;
  border-radius: 14px;
}

.conversation-shell {
  display: grid;
  grid-template-columns: 230px minmax(0, 1fr);
  min-height: 680px;
}

.member-panel {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 20px 16px;
  background: #f8fafc;
  border-right: 1px solid #e5e7eb;
}

.team-summary {
  display: flex;
  align-items: center;
  gap: 11px;
  padding-bottom: 14px;
  border-bottom: 1px solid #e5e7eb;
}

.team-avatar {
  display: grid;
  flex: 0 0 40px;
  width: 40px;
  height: 40px;
  place-items: center;
  color: #fff;
  font-weight: 700;
  background: linear-gradient(135deg, #4f46e5, #7c3aed);
  border-radius: 12px;
}

.team-select {
  width: 100%;
}

.member-title {
  display: flex;
  justify-content: space-between;
  margin-top: 8px;
  color: #475569;
  font-size: 13px;
  font-weight: 600;
}

.member-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 8px;
  border-radius: 10px;
}

.member-item:hover {
  background: #eef2ff;
}

.member-meta {
  min-width: 0;
  flex: 1;
}

.member-name {
  overflow: hidden;
  font-size: 14px;
  font-weight: 600;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.self-tag {
  margin-left: 4px;
  color: #4f46e5;
  font-size: 11px;
}

.presence-dot {
  width: 9px;
  height: 9px;
  background: #cbd5e1;
  border-radius: 50%;
}

.presence-dot.online {
  background: #22c55e;
  box-shadow: 0 0 0 3px rgba(34, 197, 94, 0.14);
}

.room-tip {
  margin-top: auto;
  padding: 12px;
  color: #64748b;
  font-size: 12px;
  line-height: 1.65;
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
}

.room-tip strong {
  color: #334155;
}

.room-tip p {
  margin: 5px 0 0;
}

.conversation-panel {
  position: relative;
  display: flex;
  min-width: 0;
  flex-direction: column;
  background: #fff;
}

.conversation-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid #eef2f7;
}

.message-list {
  height: 500px;
  overflow-y: auto;
  padding: 18px 22px;
  background:
    linear-gradient(180deg, rgba(248, 250, 252, 0.8), transparent 90px),
    #fff;
}

.day-divider {
  width: fit-content;
  margin: 8px auto 18px;
  padding: 3px 10px;
  color: #94a3b8;
  font-size: 12px;
  background: #f8fafc;
  border-radius: 20px;
}

.message {
  display: flex;
  gap: 10px;
  margin: 13px 0;
  max-width: 78%;
}

.message.mine {
  margin-left: auto;
  flex-direction: row-reverse;
}

.message-avatar {
  flex: 0 0 34px;
  margin-top: 16px;
  color: #334155;
  background: #e2e8f0;
}

.message-body {
  min-width: 0;
}

.message.mine .message-body {
  text-align: right;
}

.meta {
  display: flex;
  gap: 8px;
  margin-bottom: 5px;
  color: #94a3b8;
  font-size: 12px;
}

.message.mine .meta {
  justify-content: flex-end;
}

.bubble {
  display: inline-block;
  padding: 10px 13px;
  color: #1f2937;
  line-height: 1.65;
  text-align: left;
  overflow-wrap: anywhere;
  white-space: pre-wrap;
  background: #f1f5f9;
  border-radius: 4px 12px 12px;
}

.message.mine .bubble {
  color: #fff;
  background: #4f46e5;
  border-radius: 12px 4px 12px 12px;
}

.system-notice {
  width: fit-content;
  margin: 8px auto;
  padding: 4px 10px;
  color: #94a3b8;
  font-size: 12px;
}

.new-message-button {
  position: absolute;
  right: 28px;
  bottom: 122px;
  padding: 6px 12px;
  color: #fff;
  font-size: 12px;
  background: #4f46e5;
  border: 0;
  border-radius: 16px;
  cursor: pointer;
  box-shadow: 0 6px 16px rgba(79, 70, 229, 0.25);
}

.composer {
  padding: 14px 18px 16px;
  background: #fff;
  border-top: 1px solid #eef2f7;
}

.attachment-toolbar {
  display: flex;
  align-items: center;
  gap: 5px;
  margin-bottom: 9px;
}

.toolbar-hint {
  margin-left: auto;
}

.hidden-file-input {
  display: none;
}

.composer-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 8px;
}

.attachment-card {
  min-width: 230px;
  max-width: 360px;
  padding: 11px;
  text-align: left;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
}

.attachment-heading {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  color: #4f46e5;
}

.attachment-name {
  display: flex;
  min-width: 0;
  flex-direction: column;
  color: #1f2937;
}

.attachment-name strong {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.attachment-name span,
.attachment-loading {
  color: #94a3b8;
  font-size: 12px;
}

.attachment-expired {
  margin-top: 10px;
  padding: 8px;
  color: #b45309;
  font-size: 12px;
  background: #fffbeb;
  border-radius: 8px;
}

.message-image,
.message-video {
  display: block;
  max-width: 100%;
  max-height: 280px;
  margin-top: 10px;
  border-radius: 8px;
}

.message-image {
  cursor: pointer;
}

.attachment-caption {
  margin: 8px 0 0;
  color: #475569;
  font-size: 13px;
  white-space: pre-wrap;
}

@media (max-width: 900px) {
  .conversation-shell {
    grid-template-columns: 1fr;
  }

  .member-panel {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    border-right: 0;
    border-bottom: 1px solid #e5e7eb;
  }

  .member-title,
  .room-tip {
    grid-column: 1 / -1;
  }

  .message-list {
    height: 430px;
  }

  .toolbar-hint {
    width: 100%;
    margin-left: 0;
  }
}
</style>
