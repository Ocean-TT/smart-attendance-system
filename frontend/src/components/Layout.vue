<template>
  <div class="layout">
    <aside class="sidebar">
      <h3>课堂系统</h3>
      <nav>
        <router-link to="/">仪表盘</router-link>
        <router-link to="/questions">题库管理</router-link>
        <router-link to="/profile">个人资料</router-link>
        <router-link to="/stats">统计分析</router-link>
        <button @click="logout" class="logout-btn">退出登录</button>
      </nav>
    </aside>
    <main class="content">
      <header>
        <h2>欢迎使用系统</h2>
      </header>
      <slot></slot>
    </main>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()
const logout = () => {
  localStorage.removeItem('token')
  router.push('/auth')
}
</script>

<style scoped>
.layout { display: flex; min-height: 100vh; }
.sidebar { width: 240px; background: #2c3e50; color: white; padding: 20px; }
.sidebar nav { display: flex; flexDirection: column; gap: 10px; }
.sidebar a { color: white; text-decoration: none; display: block; padding: 5px 0; }
.content { flex: 1; padding: 20px; background: #f4f7f6; }
.logout-btn { margin-top: 20px; background: #e74c3c; color: white; border: none; padding: 8px; cursor: pointer; width: 100%; }
</style>
