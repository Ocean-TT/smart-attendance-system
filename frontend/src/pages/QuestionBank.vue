<template>
  <Layout>
    <div class="question-bank-container">
      <!-- 根据角色渲染不同的子组件 -->
      <TeacherBank v-if="user?.role === 'TEACHER'" />
      <StudentBank v-else-if="user?.role === 'STUDENT'" />
      
      <!-- 加载状态 -->
      <div v-else class="loading">
        正在加载题库...
      </div>
    </div>
  </Layout>
</template>

<script setup>
import Layout from '../components/Layout.vue'
import TeacherBank from './question-bank/TeacherBank.vue'
import StudentBank from './question-bank/StudentBank.vue'
import { useAuthStore } from '../store/auth'

const { user } = useAuthStore()
</script>

<style scoped>
.question-bank-container {
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
