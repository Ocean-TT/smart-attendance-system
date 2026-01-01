<template>
  <Layout>
    <div class="classroom-container">
      <!-- 根据角色渲染不同的子组件 -->
      <TeacherClassroom v-if="user?.role === 'TEACHER'" />
      <StudentClassroom v-else-if="user?.role === 'STUDENT'" />
      
      <!-- 加载状态或错误处理 -->
      <div v-else class="loading">
        正在进入课堂...
      </div>
    </div>
  </Layout>
</template>

<script setup>
import Layout from '../components/Layout.vue'
import TeacherClassroom from './classroom/TeacherClassroom.vue'
import StudentClassroom from './classroom/StudentClassroom.vue'
import { useAuthStore } from '../store/auth'

const { user } = useAuthStore()
</script>

<style scoped>
.classroom-container {
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
