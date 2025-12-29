<template>
  <Layout>
    <div class="classroom">
      <div class="main-area">
        <h3>课堂互动 (班级 ID: {{ route.params.id }})</h3>
        
        <div v-if="userRole === 'TEACHER'" class="teacher-controls">
          <button @click="startAttendance" class="btn-primary">发起考勤</button>
          <button @click="randomCall" class="btn-success">随机点名</button>
          <button class="btn-warning">课堂提问</button>
        </div>
        
        <div v-else class="student-area">
          <div v-if="sessionStatus === 'ATTENDANCE'" class="attendance-box">
            <h4>考勤进行中...</h4>
            <FaceCapture @capture="onSign" />
          </div>
          <p v-else>等待老师发起互动...</p>
        </div>

        <div v-if="selectedStudent" class="call-result">
          <h2>被点名学生: {{ selectedStudent }}</h2>
          <div v-if="userRole === 'TEACHER'" class="rating">
            <p>记录表现:</p>
            <button>优秀</button>
            <button>良好</button>
            <button>一般</button>
          </div>
        </div>
      </div>

      <aside class="status-sidebar">
        <h4>实时状态</h4>
        <ul>
          <li>已签到: 12 / 45</li>
          <li>当前状态: {{ sessionStatus }}</li>
        </ul>
      </aside>
    </div>
  </Layout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import Layout from '../components/Layout.vue'
import FaceCapture from '../components/FaceCapture.vue'

const route = useRoute()
const userRole = ref('TEACHER')
const sessionStatus = ref('IDLE')
const selectedStudent = ref(null)

const startAttendance = () => {
  sessionStatus.value = 'ATTENDANCE'
}

const randomCall = () => {
  const students = ['张三', '李四', '王五', '赵六']
  selectedStudent.value = students[Math.floor(Math.random() * students.length)]
  sessionStatus.value = 'QUESTIONING'
}

const onSign = (blob) => {
  alert("签到成功！")
}

onMounted(() => {
  const user = JSON.parse(localStorage.getItem('user') || '{}')
  userRole.value = user.role || 'STUDENT'
})
</script>

<style scoped>
.classroom { display: grid; grid-template-columns: 1fr 300px; gap: 20px; }
.main-area { background: white; padding: 20px; border-radius: 8px; min-height: 400px; }
.teacher-controls { display: flex; gap: 10px; margin-bottom: 20px; }
.btn-primary { background: #1890ff; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; }
.btn-success { background: #52c41a; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; }
.btn-warning { background: #faad14; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; }
.student-area { padding: 20px; border: 2px dashed #ddd; text-align: center; }
.call-result { margin-top: 40px; text-align: center; padding: 20px; background: #f6ffed; border: 1px solid #b7eb8f; }
.status-sidebar { background: white; padding: 20px; border-radius: 8px; }
ul { list-style: none; padding: 0; }
li { padding: 8px 0; border-bottom: 1px solid #eee; }
</style>
