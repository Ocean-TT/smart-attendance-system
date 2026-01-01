<template>
  <div class="student-classroom">
    <div class="main-content">
      <!-- 暂未上课状态 -->
      <div v-if="classroomInfo.is_active === 0" class="not-started-state">
        <div class="status-card">
          <div class="pulse-icon inactive">💤</div>
          <h3>老师暂未开启课堂</h3>
          <p>当前课程尚未开始，请稍后再试或查看下方公告</p>
          <div class="schedule-hint" v-if="classroomInfo.schedule">
            <span>📅 上课时间：{{ classroomInfo.schedule }}</span>
          </div>
        </div>
      </div>

      <!-- 默认状态 (已上课但无互动) -->
      <div v-else-if="status === 'IDLE'" class="idle-state">
        <div class="status-card">
          <div class="pulse-icon">📡</div>
          <h3>正在等待老师发起互动...</h3>
          <p>请保持页面开启，不要离开课堂</p>
        </div>
      </div>

      <!-- 签到状态 -->
      <div v-if="status === 'ATTENDANCE'" class="attendance-state">
        <div class="action-card attendance-card">
          <div class="card-header">
            <div class="icon-box">📸</div>
            <h3>课堂签到</h3>
            <p>请选择识别方式完成出勤确认</p>
          </div>
          
          <div class="capture-wrapper">
            <FaceCapture :allowUpload="true" @capture="handleSign" />
          </div>

          <div class="attendance-footer">
            <p class="hint-text">提示：请确保光线充足，正对摄像头或上传清晰正面照</p>
          </div>

          <div v-if="isSigned" class="success-overlay">
            <div class="success-content">
              <div class="success-icon">
                <div class="circle"></div>
                <span class="check">✓</span>
              </div>
              <h4>签到成功！</h4>
              <p>系统已记录您的出勤状态</p>
              <button @click="status = 'IDLE'" class="btn-confirm">确定</button>
            </div>
          </div>
        </div>
      </div>

      <!-- 被点名状态 -->
      <div v-if="status === 'CALLED'" class="called-state">
        <div class="alert-card called-card">
          <div class="called-header">
            <div class="wave-icon">📢</div>
            <h3>你被老师点名了！</h3>
          </div>
          <div class="called-body">
            <div class="avatar-placeholder">👤</div>
            <h2>请准备回答问题</h2>
          </div>
          <div class="called-footer">
            <button @click="status = 'IDLE'" class="btn-ready-large">我准备好了</button>
          </div>
        </div>
      </div>

      <!-- 课堂提问状态 -->
      <div v-if="status === 'QUESTIONING'" class="quiz-state">
        <div class="action-card quiz-card">
          <div class="quiz-header">
            <span class="tag-quiz">课堂提问</span>
          </div>
          <div class="quiz-body">
            <p class="q-content">{{ activeQuestion.content }}</p>
            
            <div v-if="!activeQuestion.has_submitted">
              <!-- 题库题目 (假设是选择题) -->
              <div v-if="activeQuestion.type === 'BANK'" class="options-grid">
                <button 
                  v-for="opt in ['A', 'B', 'C', 'D']" 
                  :key="opt"
                  @click="handleQuestionSubmit(opt)"
                  class="opt-btn"
                >
                  {{ opt }}
                </button>
              </div>
              <!-- 手动提问 -->
              <div v-else class="manual-answer">
                <textarea v-model="studentAnswer" placeholder="请输入你的回答..." class="answer-textarea"></textarea>
                <button @click="handleQuestionSubmit(studentAnswer)" class="btn-submit-q" :disabled="!studentAnswer.trim()">
                  提交回答
                </button>
              </div>
            </div>
            
            <div v-else class="submitted-state">
              <div class="success-icon-mini">✓</div>
              <h4>回答已提交</h4>
              <p>请等待老师结束提问</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <aside class="info-sidebar">
      <div class="course-info">
        <h4>当前课程</h4>
        <p class="course-name">{{ classroomInfo.name || '未加入班级' }}</p>
        <p class="teacher">授课教师：{{ classroomInfo.teacher || '暂无' }}</p>
      </div>
      <div class="my-status">
        <h4>我的状态</h4>
        <div class="status-row">
          <span>签到状态</span>
          <span :class="['tag', isSigned ? 'success' : 'warning']">
            {{ isSigned ? '已签到' : '未签到' }}
          </span>
        </div>
        <div class="status-row">
          <span>课堂积分</span>
          <span class="points">+{{ myPoints }}</span>
        </div>
      </div>

      <div class="classroom-announcements">
        <h4>课堂公告</h4>
        <div class="ann-list">
          <div v-if="announcements.length === 0" class="empty-ann">暂无公告</div>
          <div v-for="ann in announcements" :key="ann.id" class="ann-item">
            <p class="ann-content">{{ ann.content }}</p>
            <span class="ann-date">{{ ann.date }}</span>
          </div>
        </div>
      </div>
    </aside>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import FaceCapture from '../../components/FaceCapture.vue'
import { 
  getClassroomDetails, 
  getAttendanceStatus, 
  studentCheckin, 
  getClassroomStudents, 
  getStudentStats,
  joinClassroom,
  leaveClassroom,
  getAnnouncements,
  getClassroomQuestionStatus,
  submitClassroomAnswer
} from '../../api'
import { useAuthStore } from '../../store/auth'

const route = useRoute()
const auth = useAuthStore()
const classId = route.params.id

const status = ref('IDLE')
const isSigned = ref(false)
const lastSessionId = ref(null)
const classroomInfo = ref({ name: '加载中...', teacher: '加载中...', is_active: 0 })
const myPoints = ref(0)
const announcements = ref([])

// 提问相关
const activeQuestion = ref(null)
const studentAnswer = ref('')

let timer = null

const fetchStatus = async () => {
  try {
    const res = await getAttendanceStatus(classId)
    const data = res.data || res
    
    // 1. 先获取当前学生在当前班级的状态（同步签到标记）
    const studentRes = await getClassroomStudents(classId)
    if (studentRes.code === 200) {
      const me = studentRes.data.find(s => s.student_id === auth.user.value?.studentId)
      if (me) {
        isSigned.value = me.signed
      }
    }

    // 2. 获取提问状态
    const qRes = await getClassroomQuestionStatus(classId)
    const qData = qRes.data

    // 3. 处理课堂状态切换逻辑 (优先级: CALLED > ATTENDANCE > QUESTIONING > IDLE)
    if (data && data.status === 'CALLED') {
      status.value = 'CALLED'
    } else if (data && data.status === 'ATTENDANCE') {
      // 如果是新的签到会话
      if (data.session_id !== lastSessionId.value) {
        lastSessionId.value = data.session_id
        // 只有未签到时才自动弹出签到界面
        if (!isSigned.value) {
          status.value = 'ATTENDANCE'
        }
      } else {
        // 同一个会话：如果已经签到且用户已经点击了“确定”（status 变回了 IDLE），则不再弹窗
        if (isSigned.value && status.value === 'IDLE') {
          // 保持 IDLE，不干扰用户
        } else if (!isSigned.value) {
          // 没签到则保持在签到界面
          status.value = 'ATTENDANCE'
        }
      }
    } else if (qData && qData.status === 'QUESTIONING') {
      status.value = 'QUESTIONING'
      activeQuestion.value = qData
    } else {
      status.value = 'IDLE'
      if (data && data.status === 'IDLE') {
        lastSessionId.value = null
      }
    }
    
    // 4. 顺便获取一下积分
    const statsRes = await getStudentStats(auth.user.value?.studentId || '20230001')
    myPoints.value = statsRes.data?.totalPoints || 0
  } catch (error) {
    console.error('获取课堂状态失败:', error)
  }
}

const handleQuestionSubmit = async (answer) => {
  if (!answer) return
  try {
    const res = await submitClassroomAnswer(classId, answer)
    if (res.code === 200) {
      activeQuestion.value.has_submitted = true
      studentAnswer.value = ''
    }
  } catch (err) {
    alert('提交失败: ' + err.message)
  }
}

const fetchClassInfo = async () => {
  try {
    const res = await getClassroomDetails(classId)
    classroomInfo.value = res.data
    
    // 获取公告
    const annRes = await getAnnouncements(classId)
    if (annRes.code === 200) {
      announcements.value = annRes.data
    }
  } catch (error) {
    console.error('获取班级信息失败:', error)
  }
}

onMounted(async () => {
  fetchClassInfo()
  fetchStatus()
  timer = setInterval(fetchStatus, 3000)
  
  // 加入课堂会话
  try {
    await joinClassroom(classId)
  } catch (err) {
    console.error('加入课堂失败:', err)
  }
})

onUnmounted(async () => {
  if (timer) clearInterval(timer)
  
  // 离开课堂会话
  try {
    await leaveClassroom(classId)
  } catch (err) {
    console.error('离开课堂失败:', err)
  }
})

const handleSign = async (blob) => {
  const reader = new FileReader()
  reader.readAsDataURL(blob)
  reader.onloadend = async () => {
    const base64data = reader.result
    try {
      const res = await studentCheckin(classId, base64data)
      if (res.code === 200) {
        isSigned.value = true
      } else {
        alert(res.msg || '签到失败')
      }
    } catch (err) {
      alert('签到失败: ' + err.message)
    }
  }
}

const submitAnswer = (idx) => {
  selectedAnswer.value = idx
  hasSubmitted.value = true
}

const startQuizDemo = () => {
  status.value = 'QUIZ'
  selectedAnswer.value = null
  hasSubmitted.value = false
  quizTimer.value = 30
}
</script>

<style scoped>
.student-classroom {
  display: grid;
  grid-template-columns: 1fr 260px;
  gap: 2rem;
  position: relative;
}

.main-content {
  min-height: 500px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.status-card, .action-card, .alert-card {
  background: white;
  padding: 3rem;
  border-radius: 24px;
  box-shadow: 0 20px 50px rgba(0,0,0,0.05);
  text-align: center;
  width: 100%;
  max-width: 520px;
  position: relative;
  overflow: hidden;
}

.attendance-card {
  padding: 0;
}

.card-header {
  padding: 2.5rem 2rem 1.5rem;
  background: linear-gradient(135deg, #f6f9fc 0%, #ffffff 100%);
  border-bottom: 1px solid #f0f2f5;
}

.icon-box {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.attendance-card h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.5rem;
}

.attendance-card p {
  color: #7f8c8d;
  margin-top: 0.5rem;
}

.capture-wrapper {
  padding: 2rem;
  background: white;
}

.attendance-footer {
  padding: 1.5rem;
  background: #fafbfc;
  border-top: 1px solid #f0f2f5;
}

.hint-text {
  font-size: 0.85rem;
  color: #95a5a6;
  margin: 0;
}

.success-overlay {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(255,255,255,0.98);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.success-icon {
  position: relative;
  width: 80px;
  height: 80px;
  margin: 0 auto 1.5rem;
}

.success-icon .circle {
  width: 100%;
  height: 100%;
  background: #42b983;
  border-radius: 50%;
  animation: scaleUp 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.success-icon .check {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: white;
  font-size: 2.5rem;
  font-weight: bold;
}

@keyframes scaleUp {
  from { transform: scale(0); }
  to { transform: scale(1); }
}

.btn-confirm {
  margin-top: 2rem;
  padding: 0.8rem 3rem;
  background: #42b983;
  color: white;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s;
  box-shadow: 0 4px 12px rgba(66, 185, 131, 0.2);
}

.btn-confirm:hover {
  background: #3aa876;
  transform: translateY(-2px);
  box-shadow: 0 6px 15px rgba(66, 185, 131, 0.3);
}

/* 被点名样式 */
.called-card {
  padding: 0;
  border: none;
  background: white;
  max-width: 450px;
}

.called-header {
  padding: 2rem;
  background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
  color: white;
}

.wave-icon {
  font-size: 3rem;
  margin-bottom: 0.5rem;
  animation: wave 1s infinite;
}

@keyframes wave {
  0%, 100% { transform: rotate(0); }
  50% { transform: rotate(15deg); }
}

.called-body {
  padding: 2.5rem 2rem;
}

.avatar-placeholder {
  font-size: 4rem;
  margin-bottom: 1rem;
  color: #eee;
}

.called-body h2 {
  margin: 0;
  color: #e74c3c;
  font-size: 1.8rem;
}

.called-body p {
  color: #7f8c8d;
  margin-top: 1rem;
}

.called-footer {
  padding: 1.5rem;
  background: #fffafa;
  border-top: 1px solid #ffebeb;
}

.btn-ready-large {
  width: 100%;
  padding: 1rem;
  background: #e74c3c;
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 1.1rem;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-ready-large:hover {
  background: #c0392b;
  transform: scale(1.02);
}

.pulse-icon {
  font-size: 4rem;
  margin-bottom: 1.5rem;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.1); opacity: 0.7; }
  100% { transform: scale(1); opacity: 1; }
}

.btn-back, .btn-ready {
  margin-top: 1.5rem;
  padding: 0.8rem 2rem;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: bold;
}

.alert-card {
  border: 2px solid #e74c3c;
  background: #fff5f5;
}

.alert-header {
  color: #e74c3c;
  font-weight: bold;
  font-size: 1.2rem;
  margin-bottom: 1rem;
}

/* 提问样式 */
.quiz-card {
  max-width: 600px;
}
.quiz-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 1.5rem;
}
.tag-quiz {
  background: #e1f5fe;
  color: #0288d1;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.9rem;
}
.timer {
  color: #e74c3c;
  font-weight: bold;
}
.options-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-top: 2rem;
}
.opt-btn {
  padding: 1rem;
  border: 1px solid #ddd;
  border-radius: 8px;
  background: white;
  cursor: pointer;
  transition: all 0.2s;
  text-align: left;
}
.opt-btn:hover:not(:disabled) {
  border-color: #3498db;
  background: #f7fbfe;
}
.q-content {
  font-size: 1.2rem;
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 2rem;
  line-height: 1.5;
}

.answer-textarea {
  width: 100%;
  height: 120px;
  padding: 1rem;
  border-radius: 8px;
  border: 1px solid #ddd;
  margin-bottom: 1rem;
  resize: none;
}

.btn-submit-q {
  width: 100%;
  padding: 1rem;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: bold;
  cursor: pointer;
}

.submitted-state {
  text-align: center;
  padding: 2rem;
}

.success-icon-mini {
  width: 40px;
  height: 40px;
  background: #42b983;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  margin: 0 auto 1rem;
}

.info-sidebar {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.pulse-icon.inactive {
  animation: none;
  background: #f0f2f5;
  color: #909399;
}

.schedule-hint {
  margin-top: 1.5rem;
  padding: 0.8rem;
  background: #fdf6ec;
  color: #e6a23c;
  border-radius: 8px;
  font-size: 0.9rem;
}

.classroom-announcements {
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid #eee;
}

.classroom-announcements h4 {
  margin: 0 0 1rem 0;
  color: #2c3e50;
  font-size: 1rem;
}

.ann-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  max-height: 300px;
  overflow-y: auto;
}

.ann-item {
  padding: 0.8rem;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 3px solid #42b983;
}

.ann-content {
  margin: 0 0 0.4rem 0;
  font-size: 0.85rem;
  color: #606266;
  line-height: 1.4;
}

.ann-date {
  font-size: 0.75rem;
  color: #909399;
}

.empty-ann {
  text-align: center;
  color: #999;
  font-size: 0.85rem;
  padding: 1rem 0;
}

.course-info, .my-status {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.05);
}

.course-name { font-weight: bold; color: #2c3e50; margin: 0.5rem 0; }
.teacher { font-size: 0.9rem; color: #666; }

.status-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 1rem;
  font-size: 0.9rem;
}

.tag {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.8rem;
}

.tag.success { background: #e8f5e9; color: #42b983; }
.tag.warning { background: #fff3e0; color: #f39c12; }

.points { color: #f1c40f; font-weight: bold; }

.demo-controls {
  position: absolute;
  bottom: -60px;
  left: 0;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 0.8rem;
  color: #999;
}

.demo-controls button {
  padding: 4px 8px;
  font-size: 0.7rem;
  cursor: pointer;
}
</style>
