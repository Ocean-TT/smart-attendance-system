<template>
  <div class="auth-container">
    <div class="auth-card">
      <h2>{{ isLogin ? '登录' : '注册' }}</h2>
      <form @submit.prevent="handleSubmit">
        <input v-model="formData.username" placeholder="用户名" required />
        <input v-model="formData.password" type="password" placeholder="密码" required />
        
        <template v-if="!isLogin">
          <select v-model="role">
            <option value="STUDENT">学生</option>
            <option value="TEACHER">教师</option>
          </select>
          <div v-if="role === 'STUDENT'">
            <input v-model="formData.studentId" placeholder="学号" required />
            <label>人脸录入:</label>
            <FaceCapture @capture="onFaceCapture" />
          </div>
        </template>
        
        <button type="submit">{{ isLogin ? '登录' : '注册' }}</button>
      </form>
      <p @click="isLogin = !isLogin" class="toggle-link">
        {{ isLogin ? '没有账号？去注册' : '已有账号？去登录' }}
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import FaceCapture from '../components/FaceCapture.vue'

const isLogin = ref(true)
const role = ref('STUDENT')
const formData = ref({ username: '', password: '', studentId: '' })
const faceBlob = ref(null)
const router = useRouter()

const onFaceCapture = (blob) => {
  faceBlob.value = blob
}

const handleSubmit = () => {
  // Mock 登录逻辑
  localStorage.setItem('token', 'mock-token')
  localStorage.setItem('user', JSON.stringify({ username: formData.value.username, role: role.value }))
  router.push('/')
}
</script>

<style scoped>
.auth-container { display: flex; justify-content: center; align-items: center; height: 100vh; background: #f0f2f5; }
.auth-card { background: white; padding: 40px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); width: 100%; max-width: 400px; }
form { display: flex; flexDirection: column; gap: 16px; }
input, select { padding: 10px; border-radius: 4px; border: 1px solid #ddd; }
button { padding: 12px; background: #1890ff; color: white; border: none; border-radius: 4px; cursor: pointer; }
.toggle-link { text-align: center; margin-top: 16px; cursor: pointer; color: #1890ff; }
</style>
