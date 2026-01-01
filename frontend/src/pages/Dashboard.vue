<template>
  <Layout>
    <div class="dashboard-container">
      <!-- 根据角色渲染不同的子组件 -->
      <TeacherDashboard v-if="user?.role === 'TEACHER'" />
      <StudentDashboard v-else-if="user?.role === 'STUDENT'" />
      
      <!-- 加载状态或错误处理 -->
      <div v-else class="loading">
        正在加载用户信息...
      </div>
    </div>
  </Layout>
</template>

<script setup>
import Layout from '../components/Layout.vue'
import TeacherDashboard from './dashboard/TeacherDashboard.vue'
import StudentDashboard from './dashboard/StudentDashboard.vue'
import { useAuthStore } from '../store/auth'

const { user } = useAuthStore()
</script>

<style scoped>
.dashboard-container {
  padding: 1rem;
}

.loading {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
  color: #666;
}
</style>
