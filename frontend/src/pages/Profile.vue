<template>
  <Layout>
    <div class="profile">
      <h3>个人资料管理</h3>
      <div class="info-list">
        <div class="info-item">
          <label>用户名: </label>
          <span>{{ username }}</span>
        </div>
        <div class="info-item">
          <label>身份: </label>
          <span>{{ userRole === 'TEACHER' ? '教师' : '学生' }}</span>
        </div>
        
        <hr />
        
        <h4>人脸数据管理</h4>
        <div class="face-management">
          <div class="face-avatar">[人脸档案]</div>
          <button @click="showFaceUpdate = !showFaceUpdate">更新人脸信息</button>
        </div>

        <div v-if="showFaceUpdate" class="face-update-box">
          <FaceCapture @capture="onFaceUpdate" />
        </div>

        <div class="actions">
          <button class="pwd-btn">修改密码</button>
        </div>
      </div>
    </div>
  </Layout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import Layout from '../components/Layout.vue'
import FaceCapture from '../components/FaceCapture.vue'

const username = ref('')
const userRole = ref('STUDENT')
const showFaceUpdate = ref(false)

const onFaceUpdate = (blob) => {
  alert("人脸信息已更新")
  showFaceUpdate.value = false
}

onMounted(() => {
  const user = JSON.parse(localStorage.getItem('user') || '{}')
  username.value = user.username || '未知'
  userRole.value = user.role || 'STUDENT'
})
</script>

<style scoped>
.profile { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }
.info-list { margin-top: 20px; display: flex; flex-direction: column; gap: 15px; }
.info-item label { font-weight: bold; }
hr { border: 0; border-top: 1px solid #eee; margin: 10px 0; }
.face-management { display: flex; align-items: center; gap: 20px; }
.face-avatar { width: 100px; height: 100px; background: #eee; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #999; }
.face-update-box { margin-top: 10px; padding: 15px; border: 1px dashed #ddd; }
.actions { margin-top: 20px; }
.pwd-btn { padding: 10px 20px; background: #1890ff; color: white; border: none; border-radius: 4px; cursor: pointer; }
</style>
