<template>
  <div class="layout">
    <aside class="sidebar">
      <div class="brand">
        <div class="logo-icon">
          <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M22 10v6M2 10l10-5 10 5-10 5z"></path>
            <path d="M6 12v5c3 3 9 3 12 0v-5"></path>
          </svg>
        </div>
        <h2 class="brand-name">智慧课堂</h2>
      </div>
      
      <nav class="nav-menu">
        <router-link to="/" class="nav-item">
          <div class="icon">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <rect x="3" y="3" width="7" height="7"></rect>
              <rect x="14" y="3" width="7" height="7"></rect>
              <rect x="14" y="14" width="7" height="7"></rect>
              <rect x="3" y="14" width="7" height="7"></rect>
            </svg>
          </div>
          <span class="label">仪表盘</span>
        </router-link>
        
        <router-link to="/questions" class="nav-item">
          <div class="icon">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
              <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
            </svg>
          </div>
          <span class="label">{{ user?.role === 'TEACHER' ? '题库管理' : '练习题库' }}</span>
        </router-link>
        
        <router-link to="/stats" class="nav-item">
          <div class="icon">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="18" y1="20" x2="18" y2="10"></line>
              <line x1="12" y1="20" x2="12" y2="4"></line>
              <line x1="6" y1="20" x2="6" y2="14"></line>
            </svg>
          </div>
          <span class="label">统计分析</span>
        </router-link>
      </nav>

      <div class="sidebar-footer">
        <router-link to="/profile" class="user-profile" v-if="user">
          <div class="avatar">{{ user.name ? user.name[0] : (user.username ? user.username[0].toUpperCase() : 'U') }}</div>
          <div class="info">
            <div class="name">{{ user.name || user.username }}</div>
            <div class="role">{{ user.role === 'TEACHER' ? '教师' : '学生' }}</div>
          </div>
        </router-link>
        <button @click="handleLogout" class="logout-btn">
          <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
            <polyline points="16 17 21 12 16 7"></polyline>
            <line x1="21" y1="12" x2="9" y2="12"></line>
          </svg>
          <span>退出登录</span>
        </button>
      </div>
    </aside>
    <main class="content">
      <header class="main-header">
        <div class="header-content">
          <h2 class="page-title">{{ pageTitle }}</h2>
          <div class="header-actions">
            <!-- 可以放一些全局操作，如通知等 -->
          </div>
        </div>
      </header>
      <div class="page-body">
        <slot></slot>
      </div>
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../store/auth'

const router = useRouter()
const route = useRoute()
const { user, logout } = useAuthStore()

const pageTitle = computed(() => {
  const titles = {
    '/': '仪表盘概览',
    '/questions': '题库管理',
    '/profile': '个人资料',
    '/stats': '数据统计',
    '/classroom': '智慧课堂'
  }
  // 处理动态路由如 /class/:id 或 /classroom/:id
  if (route.path.startsWith('/class/')) return '班级详情'
  if (route.path.startsWith('/classroom/')) return '智慧课堂'
  
  return titles[route.path] || '欢迎使用系统'
})

const handleLogout = () => {
  logout()
  router.push('/auth')
}
</script>

<style scoped>
.layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
  background: #f0f2f5;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

/* 侧边栏样式 */
.sidebar {
  width: 260px;
  background: #001529;
  color: rgba(255, 255, 255, 0.65);
  display: flex;
  flex-direction: column;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.15);
  z-index: 10;
  transition: all 0.3s;
}

.brand {
  height: 64px;
  display: flex;
  align-items: center;
  padding: 0 24px;
  gap: 12px;
  background: #002140;
}

.logo-icon {
  color: #1890ff;
  display: flex;
  align-items: center;
}

.nav-menu {
  flex: 1;
  padding: 16px 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
  overflow-y: auto;
}

/* 自定义滚动条样式，使其更美观 */
.nav-menu::-webkit-scrollbar {
  width: 4px;
}

.nav-menu::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
}

.nav-menu::-webkit-scrollbar-track {
  background: transparent;
}

.nav-item {
  display: flex;
  align-items: center;
  padding: 12px 24px;
  color: rgba(255, 255, 255, 0.65);
  text-decoration: none;
  transition: all 0.3s;
  gap: 12px;
}

.nav-item:hover {
  color: white;
  background: rgba(255, 255, 255, 0.05);
}

.nav-item.router-link-active {
  color: white;
  background: #1890ff;
}

.nav-item .icon {
  display: flex;
  align-items: center;
}

.nav-item .label {
  font-size: 14px;
  font-weight: 500;
}

/* 侧边栏底部 */
.sidebar-footer {
  padding: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  background: #001529;
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  padding: 8px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  cursor: pointer;
  text-decoration: none;
  transition: all 0.3s;
  border: 1px solid transparent;
}

.user-profile:hover {
  background: rgba(255, 255, 255, 0.1);
}

.user-profile.router-link-active {
  background: rgba(24, 144, 255, 0.15);
  border-color: rgba(24, 144, 255, 0.5);
}

.avatar {
  width: 36px;
  height: 36px;
  background: #1890ff;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 16px;
}

.user-profile .info {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.user-profile .name {
  color: white;
  font-size: 14px;
  font-weight: 500;
  white-space: nowrap;
  text-overflow: ellipsis;
  overflow: hidden;
}

.user-profile .role {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.45);
}

.logout-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: rgba(255, 255, 255, 0.65);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 14px;
}

.logout-btn:hover {
  color: #ff4d4f;
  border-color: #ff4d4f;
  background: rgba(255, 77, 79, 0.1);
}

/* 主内容区域 */
.content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.main-header {
  height: 64px;
  background: white;
  padding: 0 24px;
  display: flex;
  align-items: center;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  z-index: 9;
}

.header-content {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #000000d9;
}

.page-body {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .sidebar {
    width: 80px;
  }
  .brand-name, .nav-item .label, .user-profile .info, .logout-btn span {
    display: none;
  }
  .brand, .nav-item, .logout-btn {
    justify-content: center;
    padding: 12px;
  }
  .user-profile {
    padding: 4px;
    justify-content: center;
  }
}
</style>
