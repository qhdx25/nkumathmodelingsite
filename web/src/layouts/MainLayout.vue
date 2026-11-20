<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  Bell, DataAnalysis, Document, House, Message,
  Monitor, Search, Setting, SwitchButton, User, UserFilled,
} from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { messageApi } from '@/api'

const route = useRoute()
const router = useRouter()
const store = useUserStore()
const sidebarCollapsed = ref(false)
const notifications = ref<{ id: number; title: string; content: string | null }[]>([])
const drawerVisible = ref(false)

const activeMenu = computed(() => route.path)
const roleLabels: Record<string, string> = {
  student: '学生', leader: '队长',
  association_admin: '协会管理员',
  school_admin: '学校管理员', platform_admin: '平台管理员',
}
const roleLabel = computed(() => roleLabels[store.user?.role || ''] || '')

async function openNotifications() {
  drawerVisible.value = true
  if (store.isLoggedIn) {
    notifications.value = await messageApi.notifications()
  }
}

async function logout() {
  store.logout()
  await router.push('/login')
}
</script>

<template>
  <el-container class="layout">
    <el-aside :width="sidebarCollapsed ? '64px' : '210px'" class="aside">
      <div class="logo" @click="router.push('/')">
        <span v-if="!sidebarCollapsed">Math<span class="logo-accent">Team</span></span>
        <span v-else>M</span>
      </div>
      <el-menu
        :default-active="activeMenu"
        :collapse="sidebarCollapsed"
        :router="true"
        background-color="#111827"
        text-color="#cbd5e1"
        active-text-color="#ffffff"
        class="menu"
      >
        <el-menu-item index="/">
          <el-icon><House /></el-icon><template #title>首页发现</template>
        </el-menu-item>
        <el-menu-item index="/recruitments">
          <el-icon><Search /></el-icon><template #title>招募广场</template>
        </el-menu-item>
        <el-menu-item
          v-if="store.isLoggedIn && !store.isAssociationAdmin"
          index="/recommendations"
        >
          <el-icon><DataAnalysis /></el-icon><template #title>智能推荐</template>
        </el-menu-item>
        <el-menu-item v-if="store.isLoggedIn" index="/profile">
          <el-icon><User /></el-icon><template #title>个人中心</template>
        </el-menu-item>
        <el-menu-item
          v-if="store.isLoggedIn && !store.isAssociationAdmin"
          index="/teams"
        >
          <el-icon><UserFilled /></el-icon><template #title>我的团队</template>
        </el-menu-item>
        <el-menu-item
          v-if="store.isLoggedIn && !store.isAssociationAdmin"
          index="/applications"
        >
          <el-icon><Document /></el-icon><template #title>申请管理</template>
        </el-menu-item>
        <el-menu-item
          v-if="store.isLoggedIn && !store.isAssociationAdmin"
          index="/chat"
        >
          <el-icon><Message /></el-icon><template #title>团队交流</template>
        </el-menu-item>
        <el-menu-item v-if="store.isAdmin" index="/admin">
          <el-icon><Setting /></el-icon><template #title>后台管理</template>
        </el-menu-item>
      </el-menu>
      <div class="collapse-btn" @click="sidebarCollapsed = !sidebarCollapsed">
        <el-icon><Monitor /></el-icon>
        <span v-if="!sidebarCollapsed"> 收起侧栏</span>
      </div>
    </el-aside>

    <el-container>
      <el-header class="header">
        <div class="header-left">
          <span class="header-title">{{ route.meta.title || 'MathTeam' }}</span>
          <el-tag v-if="store.isLoggedIn" size="small" type="info" effect="dark">
            {{ roleLabel }}
          </el-tag>
        </div>
        <div class="header-right">
          <el-badge :value="notifications.length" :hidden="!notifications.length">
            <el-button :icon="Bell" circle @click="openNotifications" />
          </el-badge>
          <template v-if="store.isLoggedIn">
            <span class="username">{{ store.user?.real_name || store.user?.username }}</span>
            <el-button :icon="SwitchButton" @click="logout">退出</el-button>
          </template>
          <template v-else>
            <el-button @click="router.push('/login')">登录</el-button>
            <el-button type="primary" @click="router.push('/register')">注册</el-button>
          </template>
        </div>
      </el-header>

      <el-main class="main">
        <RouterView />
      </el-main>
    </el-container>

    <el-drawer v-model="drawerVisible" title="消息通知" size="360px">
      <el-empty v-if="!notifications.length" description="暂无通知" />
      <div v-for="n in notifications" :key="n.id" class="notice">
        <strong>{{ n.title }}</strong>
        <div class="muted">{{ n.content }}</div>
      </div>
    </el-drawer>
  </el-container>
</template>

<style scoped>
.layout { height: 100vh; }
.aside { background: #111827; transition: width .2s; overflow: hidden; }
.logo {
  height: 60px; line-height: 60px; text-align: center;
  color: #fff; font-size: 20px; font-weight: 800; cursor: pointer;
  border-bottom: 1px solid #1f2937;
}
.logo-accent { color: #818cf8; }
.menu { border-right: none; }
.collapse-btn {
  position: absolute; bottom: 12px; width: 100%; text-align: center;
  color: #94a3b8; font-size: 12px; cursor: pointer;
}
.header {
  background: #fff; border-bottom: 1px solid #e5e7eb;
  display: flex; align-items: center; justify-content: space-between;
  box-shadow: 0 1px 4px rgba(0,0,0,.04);
}
.header-left, .header-right { display: flex; align-items: center; gap: 12px; }
.header-title { font-weight: 600; font-size: 16px; }
.username { font-size: 14px; color: #374151; }
.main { padding: 0; overflow-y: auto; background: #f5f7fb; }
.notice { padding: 12px 0; border-bottom: 1px solid #eef2f7; }
</style>
