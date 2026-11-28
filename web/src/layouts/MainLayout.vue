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
        background-color="transparent"
        text-color="#e8dce5"
        active-text-color="#ffffff"
        class="menu"
      >
        <el-menu-item index="/">
          <el-icon><House /></el-icon><template #title>首页发现</template>
        </el-menu-item>
        <el-menu-item index="/recruitments">
          <el-icon><Search /></el-icon><template #title>招募广场</template>
        </el-menu-item>
        <el-menu-item v-if="store.isLoggedIn" index="/recommendations">
          <el-icon><DataAnalysis /></el-icon><template #title>智能推荐</template>
        </el-menu-item>
        <el-menu-item v-if="store.isLoggedIn" index="/profile">
          <el-icon><User /></el-icon><template #title>个人中心</template>
        </el-menu-item>
        <el-menu-item v-if="store.isLoggedIn" index="/teams">
          <el-icon><UserFilled /></el-icon><template #title>我的团队</template>
        </el-menu-item>
        <el-menu-item v-if="store.isLoggedIn" index="/applications">
          <el-icon><Document /></el-icon><template #title>申请管理</template>
        </el-menu-item>
        <el-menu-item v-if="store.isLoggedIn" index="/chat">
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
          <el-tag v-if="store.isAdmin" size="small" type="warning" effect="dark">
            管理员
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
.layout { background: transparent; }
.aside {
  position: relative; overflow: hidden;
  background:
    radial-gradient(circle at 20% 0%, rgba(195, 106, 169, .25), transparent 34%),
    linear-gradient(180deg, rgba(66, 8, 49, .97), rgba(35, 7, 28, .98));
  border-right: 1px solid rgba(255, 255, 255, .08);
  backdrop-filter: blur(20px);
  transition: width .24s ease;
}
.aside::before {
  content: ''; position: absolute; inset: 0; pointer-events: none;
  background-image:
    linear-gradient(rgba(255, 255, 255, .035) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, .035) 1px, transparent 1px);
  background-size: 34px 34px;
}
.logo {
  height: 60px; line-height: 60px; text-align: center;
  color: #fff; font-size: 20px; font-weight: 800; cursor: pointer;
  position: relative; z-index: 1; letter-spacing: .04em;
  border-bottom: 1px solid rgba(255, 255, 255, .09);
}
.logo-accent { color: #e6a7d4; }
.menu { position: relative; z-index: 1; border-right: none; padding: 8px; }
.menu .el-menu-item {
  height: 46px; margin: 4px 0; border-radius: 12px;
  transition: background .2s ease, transform .2s ease;
}
.menu .el-menu-item:hover { background: rgba(255, 255, 255, .08) !important; }
.menu .el-menu-item.is-active {
  background: linear-gradient(90deg, rgba(141, 58, 116, .86), rgba(195, 106, 169, .28)) !important;
  box-shadow: inset 3px 0 #f0b9e1, 0 8px 20px rgba(0, 0, 0, .16);
}
.collapse-btn {
  position: absolute; bottom: 12px; width: 100%; text-align: center;
  color: #c8b8c3; font-size: 12px; cursor: pointer; z-index: 1;
}
.header {
  background: rgba(255, 255, 255, .64);
  border-bottom: 1px solid rgba(113, 10, 83, .12);
  backdrop-filter: blur(18px) saturate(130%);
  display: flex; align-items: center; justify-content: space-between;
  box-shadow: 0 8px 30px rgba(66, 17, 53, .06);
}
.header-left, .header-right { display: flex; align-items: center; gap: 12px; }
.header-title { font-weight: 700; font-size: 16px; color: var(--mt-primary); }
.username { font-size: 14px; color: #5f4d5b; }
.main { padding: 0; overflow-y: auto; background: transparent; }
.notice { padding: 12px 0; border-bottom: 1px solid #eef2f7; }
</style>
