<template>
  <Layout>
    <div class="statistics-container">
      <!-- 根据角色渲染不同的子组件 -->
      <TeacherStats v-if="user?.role === 'TEACHER'" />
      <StudentStats v-else-if="user?.role === 'STUDENT'" />
      
      <!-- 加载状态 -->
      <div v-else class="loading">
        正在加载统计数据...
      </div>
    </div>
  </Layout>
</template>

<script setup>
import Layout from '../components/Layout.vue'
import TeacherStats from './statistics/TeacherStats.vue'
import StudentStats from './statistics/StudentStats.vue'
import { useAuthStore } from '../store/auth'

const { user } = useAuthStore()
</script>

<style scoped>
.statistics-container {
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