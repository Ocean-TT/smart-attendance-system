<template>
  <div class="teacher-classroom">
    <!-- 未上课状态遮罩 -->
    <div v-if="!isClassActive" class="start-class-overlay">
      <div class="overlay-content">
        <div class="icon-box">🏫</div>
        <h3>准备好开始上课了吗？</h3>
        <p>点击下方按钮，学生将在仪表盘收到上课提示</p>
        <button @click="handleStartClass" class="btn-start-large" :disabled="loading">
          {{ loading ? '正在开启...' : '开始上课' }}
        </button>
      </div>
    </div>

    <div class="main-content">
      <header class="classroom-header">
        <div class="header-left">
          <button @click="router.back()" class="btn-back">← 退出教室</button>
          <h2>{{ classroomInfo.name }}</h2>
        </div>
        <button @click="handleStopClass" class="btn-stop-class">结束上课</button>
      </header>

      <section class="control-panel">
        <h3>课堂控制台</h3>
        <div class="button-group">
          <button @click="handleStartAttendance" :disabled="status === 'ATTENDANCE'" class="btn attendance">
            <span class="icon">📋</span> 发起人脸签到
          </button>
          <button @click="handleRandomCall" class="btn random-call">
            <span class="icon">🎲</span> 随机点名
          </button>
          <button @click="openQuestionModal" class="btn quiz">
            <span class="icon">❓</span> 课堂提问
          </button>
        </div>
      </section>

      <!-- 课堂提问面板 -->
      <section v-if="showQuestionModal" class="question-panel-section">
        <div class="panel-header">
          <h4>❓ 课堂提问</h4>
          <button @click="closeQuestionModal" class="btn-close">×</button>
        </div>

        <div v-if="!activeQuestion" class="question-setup">
          <div class="setup-tabs">
            <button @click="questionSource = 'BANK'" :class="{ active: questionSource === 'BANK' }">从题库选择</button>
            <button @click="questionSource = 'MANUAL'" :class="{ active: questionSource === 'MANUAL' }">手动输入</button>
          </div>

          <div v-if="questionSource === 'BANK'" class="bank-selector">
            <select v-model="selectedBankId" @change="fetchQuestionsInBank" class="bank-select">
              <option value="">请选择题库</option>
              <option v-for="bank in questionBanks" :key="bank.id" :value="bank.id">{{ bank.name }}</option>
            </select>
            
            <div v-if="selectedBankId" class="bank-controls">
              <div class="search-box-mini">
                <span class="search-icon">🔍</span>
                <input v-model="questionSearchQuery" placeholder="搜索题目内容..." @input="currentPage = 1" />
              </div>
            </div>

            <div v-if="selectedBankId" class="question-list-mini">
              <div v-for="q in paginatedQuestions" :key="q.id" 
                   class="q-item-mini" 
                   :class="{ selected: selectedQuestionId === q.id }"
                   @click="selectedQuestionId = q.id">
                <div class="q-type-tag" :class="q.type.toLowerCase()">{{ q.type === 'SINGLE' ? '单选' : q.type === 'JUDGE' ? '判断' : '多选' }}</div>
                <div class="q-content-text">{{ q.content }}</div>
              </div>
              <div v-if="filteredQuestions.length === 0" class="empty-hint">未找到匹配题目</div>
            </div>

            <!-- 分页控制 -->
            <div v-if="selectedBankId && totalPages > 1" class="mini-pagination">
              <button @click="currentPage--" :disabled="currentPage === 1">上一页</button>
              <span>{{ currentPage }} / {{ totalPages }}</span>
              <button @click="currentPage++" :disabled="currentPage === totalPages">下一页</button>
            </div>
          </div>

          <div v-else class="manual-input">
            <textarea v-model="manualQuestionContent" placeholder="请输入提问内容..." class="manual-textarea"></textarea>
          </div>

          <button @click="handleStartQuestion" class="btn-primary btn-start-q" :disabled="!canStartQuestion">
            开始提问
          </button>
        </div>

        <div v-else class="question-active-stats">
          <div class="q-content-preview">
            <strong>当前提问：</strong>
            <p>{{ activeQuestion.content }}</p>
          </div>

          <div class="stats-grid">
            <div class="stat-card">
              <div class="value">{{ activeQuestion.submitted_count }}</div>
              <div class="label">已提交人数</div>
            </div>
            <div v-if="activeQuestion.type === 'BANK'" class="stat-card">
              <div class="value">{{ activeQuestion.accuracy }}%</div>
              <div class="label">正确率</div>
            </div>
          </div>

          <!-- 题库题目显示选项分布 -->
          <div v-if="activeQuestion.type === 'BANK' && activeQuestion.options_stats" class="options-chart">
            <div v-for="(count, opt) in activeQuestion.options_stats" :key="opt" class="chart-row">
              <span class="opt-label">{{ opt }}</span>
              <div class="bar-bg">
                <div class="bar-fill" :style="{ width: (activeQuestion.submitted_count > 0 ? (count / activeQuestion.submitted_count * 100) : 0) + '%' }"></div>
              </div>
              <span class="opt-count">{{ count }}人</span>
            </div>
          </div>

          <!-- 手动提问显示提交名单 -->
          <div v-else class="submission-list">
            <h5>提交名单</h5>
            <div class="list-container">
              <div v-for="s in activeQuestion.submissions" :key="s.student_name" class="submission-item">
                <span class="s-name">{{ s.student_name }}</span>
                <span class="s-time">{{ s.submit_time }}</span>
                <span class="s-answer" v-if="s.answer">：{{ s.answer }}</span>
              </div>
              <div v-if="activeQuestion.submissions.length === 0" class="empty-hint">暂无学生提交</div>
            </div>
          </div>

          <button @click="handleStopQuestion" class="btn-stop-q">结束提问</button>
        </div>
      </section>

      <!-- 随机点名面板 -->
      <section v-if="showCallModal" class="call-panel-section">
        <div class="panel-header">
          <h4>🎲 随机点名</h4>
          <button @click="closeCallModal" class="btn-close">×</button>
        </div>
        
        <div v-if="!calledStudent" class="call-setup-inline">
          <p class="setup-hint">请选择点名策略：</p>
          <div class="strategy-grid">
            <button @click="callStrategy = 'JOINED'" :class="{ active: callStrategy === 'JOINED' }">
              <div class="icon">📍</div>
              <span>已进入课堂学生</span>
            </button>
            <button @click="callStrategy = 'ALL'" :class="{ active: callStrategy === 'ALL' }">
              <div class="icon">👥</div>
              <span>全体学生</span>
            </button>
            <button @click="callStrategy = 'ATTENDANCE'" :class="{ active: callStrategy === 'ATTENDANCE' }">
              <div class="icon">📉</div>
              <span>按出勤率点名</span>
            </button>
          </div>
          <button @click="performRandomCall" class="btn-primary btn-call-now" :disabled="loading">
            {{ loading ? '正在抽取...' : '开始点名' }}
          </button>
        </div>

        <div v-else class="call-result-inline">
          <div class="lucky-info">
            <div class="lucky-avatar">👤</div>
            <div class="lucky-text">
              <h2 class="lucky-name">{{ calledStudent.name }}</h2>
              <p class="lucky-id">学号：{{ calledStudent.student_id }}</p>
            </div>
          </div>
          
          <div class="rating-section-inline">
            <div class="rating-label">课堂表现评分：</div>
            <div class="stars">
              <button v-for="i in 5" :key="i" @click="rating = i" :class="{ active: rating >= i }">⭐</button>
            </div>
            <div class="action-buttons">
              <button @click="closeCallModal" class="btn-cancel">跳过</button>
              <button @click="submitCallRating" class="btn-submit" :disabled="!rating">提交评分</button>
            </div>
          </div>
        </div>
      </section>

      <section v-if="status === 'ATTENDANCE'" class="active-session">
        <div class="session-header">
          <h4>人脸签到进行中</h4>
          <button @click="handleStopSession" class="btn-stop">结束签到</button>
        </div>
        <div class="attendance-stats">
          <div class="stat-item">
            <span class="label">已签到</span>
            <span class="value">{{ attendanceCount }} / {{ classroomInfo.student_count || 0 }}</span>
          </div>
          <div class="progress-bar">
            <div class="progress" :style="{ width: (attendanceCount / (classroomInfo.student_count || 1) * 100) + '%' }"></div>
          </div>
        </div>
      </section>

      <section v-if="status === 'QUIZ'" class="quiz-monitor">
        <div class="session-header">
          <h4>课堂提问：软件工程缺陷...</h4>
          <button @click="handleStopSession" class="btn-stop">结束提问</button>
        </div>
        <div class="quiz-stats">
          <div class="stat-box">
            <span class="val">{{ quizSubmissions }}</span>
            <span class="lab">已提交</span>
          </div>
          <div class="stat-box">
            <span class="val">{{ correctRate }}%</span>
            <span class="lab">正确率</span>
          </div>
        </div>
        <div class="answer-dist">
          <div v-for="(count, opt) in answerDist" :key="opt" class="dist-row">
            <span class="opt-label">{{ opt }}</span>
            <div class="bar-wrap">
              <div class="bar" :style="{ width: (count / (classroomInfo.student_count || 1) * 100) + '%' }"></div>
            </div>
            <span class="count">{{ count }}人</span>
          </div>
        </div>
      </section>
    </div>

    <aside class="classroom-sidebar">
      <h4>已进入课堂学生 ({{ students.length }})</h4>
      <div class="student-list">
        <div v-for="s in students" :key="s.id" class="student-item">
          <span class="status-dot online"></span>
          {{ s.name }}
          <span v-if="s.signed" class="signed-tag">已签到</span>
        </div>
      </div>
    </aside>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { 
  startAttendance, 
  getAttendanceStatus, 
  stopSession, 
  randomCall, 
  resetCall,
  rateStudent,
  getClassroomStudents,
  getClassroomDetails,
  startClass,
  stopClass,
  getJoinedStudents,
  getQuestionBanks,
  getQuestionsInBank,
  startClassroomQuestion,
  getClassroomQuestionStatus,
  stopClassroomQuestion
} from '../../api'

const route = useRoute()
const router = useRouter()
const status = ref('IDLE')
const attendanceCount = ref(0)
const students = ref([])
const classroomInfo = ref({ name: '加载中...' })
const isClassActive = ref(false)
const loading = ref(false)

// 随机点名相关
const showCallModal = ref(false)
const callStrategy = ref('JOINED')
const calledStudent = ref(null)
const rating = ref(0)

// 课堂提问相关
const showQuestionModal = ref(false)
const questionSource = ref('BANK') // BANK or MANUAL
const questionBanks = ref([])
const selectedBankId = ref('')
const questionsInBank = ref([])
const selectedQuestionId = ref('')
const manualQuestionContent = ref('')
const activeQuestion = ref(null)

// 搜索与分页
const questionSearchQuery = ref('')
const currentPage = ref(1)
const pageSize = ref(5)

const filteredQuestions = computed(() => {
  if (!questionSearchQuery.value) return questionsInBank.value
  return questionsInBank.value.filter(q => 
    q.content.toLowerCase().includes(questionSearchQuery.value.toLowerCase())
  )
})

const totalPages = computed(() => Math.ceil(filteredQuestions.value.length / pageSize.value))

const paginatedQuestions = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredQuestions.value.slice(start, end)
})

let activePolling = null
let questionPollTimer = null

const fetchClassroomInfo = async () => {
  try {
    const res = await getClassroomDetails(route.params.id)
    if (res.code === 200) {
      classroomInfo.value = res.data
      isClassActive.value = res.data.is_active === 1
    }
  } catch (err) {
    console.error('获取班级信息失败:', err)
  }
}

const fetchJoinedStudents = async () => {
  try {
    const [activeRes, studentRes] = await Promise.all([
      getJoinedStudents(route.params.id),
      getClassroomStudents(route.params.id)
    ])
    
    if (activeRes.code === 200 && studentRes.code === 200) {
      const activeIds = activeRes.data.map(s => s.id)
      // 只显示已进入课堂的学生，并保留他们的签到状态等信息
      students.value = studentRes.data.filter(s => activeIds.includes(s.id))
    }
  } catch (err) {
    console.error('获取进入课堂学生失败:', err)
  }
}

onMounted(async () => {
  await fetchClassroomInfo()
  if (isClassActive.value) {
    fetchJoinedStudents()
    activePolling = setInterval(fetchJoinedStudents, 5000)
  }
})

onUnmounted(() => {
  if (activePolling) clearInterval(activePolling)
})

const handleStartClass = async () => {
  loading.value = true
  try {
    const res = await startClass(route.params.id)
    if (res.code === 200) {
      isClassActive.value = true
      fetchJoinedStudents()
      activePolling = setInterval(fetchJoinedStudents, 5000)
    }
  } catch (err) {
    alert('开始上课失败')
  } finally {
    loading.value = false
  }
}

const handleStopClass = async () => {
  if (!confirm('确定要结束本次课程吗？')) return
  try {
    const res = await stopClass(route.params.id)
    if (res.code === 200) {
      isClassActive.value = false
      if (activePolling) clearInterval(activePolling)
      router.back()
    }
  } catch (err) {
    alert('结束上课失败')
  }
}

// 提问相关
const quizSubmissions = ref(0)
const correctRate = ref(0)
const answerDist = ref({ 'A': 0, 'B': 0, 'C': 0, 'D': 0 })

const handleStartAttendance = async () => {
  const classId = route.params.id
  try {
    await startAttendance(classId)
    status.value = 'ATTENDANCE'
    pollAttendanceStatus()
  } catch (err) {
    alert('签到启动失败: ' + err.message)
  }
}

const pollAttendanceStatus = async () => {
  const classId = route.params.id
  const interval = setInterval(async () => {
    if (status.value !== 'ATTENDANCE') {
      clearInterval(interval)
      return
    }
    try {
      const data = await getAttendanceStatus(classId)
      const result = data.data || data
      attendanceCount.value = result.count || 0
      
      // 刷新学生列表以显示谁已签到，同时保持进入课堂过滤
      await fetchJoinedStudents()
    } catch (err) {
      console.error('获取签到状态失败:', err)
    }
  }, 3000)
}

const handleRandomCall = () => {
  showCallModal.value = true
  calledStudent.value = null
  rating.value = 0
}

const performRandomCall = async () => {
  loading.value = true
  try {
    const res = await randomCall(route.params.id, callStrategy.value)
    if (res.code === 200) {
      calledStudent.value = res.data
    } else {
      alert(res.msg || '点名失败')
    }
  } catch (err) {
    alert('随机点名失败: ' + err.message)
  } finally {
    loading.value = false
  }
}

const closeCallModal = async () => {
  showCallModal.value = false
  try {
    await resetCall(route.params.id)
  } catch (err) {
    console.error('重置点名状态失败:', err)
  }
}

const submitCallRating = async () => {
  if (!rating.value) return
  try {
    const res = await rateStudent(calledStudent.value.student_id, rating.value)
    if (res.code === 200) {
      alert('评分成功')
      closeCallModal()
    }
  } catch (err) {
    alert('评分失败')
  }
}

// 课堂提问逻辑
const canStartQuestion = computed(() => {
  if (questionSource.value === 'BANK') {
    return !!selectedQuestionId.value
  }
  return !!manualQuestionContent.value.trim()
})

const openQuestionModal = async () => {
  showQuestionModal.value = true
  if (questionBanks.value.length === 0) {
    try {
      const res = await getQuestionBanks()
      if (res.code === 200) {
        questionBanks.value = res.data
      }
    } catch (err) {
      console.error('获取题库失败:', err)
    }
  }
}

const fetchQuestionsInBank = async () => {
  if (!selectedBankId.value) return
  try {
    const res = await getQuestionsInBank(selectedBankId.value)
    if (res.code === 200) {
      questionsInBank.value = res.data
      questionSearchQuery.value = ''
      currentPage.value = 1
    }
  } catch (err) {
    console.error('获取题目失败:', err)
  }
}

const handleStartQuestion = async () => {
  const classId = route.params.id
  const data = {
    type: questionSource.value,
    question_id: questionSource.value === 'BANK' ? selectedQuestionId.value : null,
    content: questionSource.value === 'MANUAL' ? manualQuestionContent.value : null
  }
  
  try {
    const res = await startClassroomQuestion(classId, data)
    if (res.code === 200) {
      startQuestionPolling()
    }
  } catch (err) {
    alert('发起提问失败: ' + err.message)
  }
}

const startQuestionPolling = () => {
  const classId = route.params.id
  const poll = async () => {
    try {
      const res = await getClassroomQuestionStatus(classId)
      if (res.code === 200 && res.data.status === 'QUESTIONING') {
        activeQuestion.value = res.data
      } else {
        activeQuestion.value = null
        stopQuestionPolling()
      }
    } catch (err) {
      console.error('轮询提问状态失败:', err)
    }
  }
  poll()
  questionPollTimer = setInterval(poll, 3000)
}

const stopQuestionPolling = () => {
  if (questionPollTimer) {
    clearInterval(questionPollTimer)
    questionPollTimer = null
  }
}

const handleStopQuestion = async () => {
  const classId = route.params.id
  try {
    await stopClassroomQuestion(classId)
    activeQuestion.value = null
    stopQuestionPolling()
  } catch (err) {
    alert('停止提问失败: ' + err.message)
  }
}

const closeQuestionModal = () => {
  showQuestionModal.value = false
  if (!activeQuestion.value) {
    stopQuestionPolling()
  }
}

const handleStopSession = async () => {
  const classId = route.params.id
  try {
    await stopSession(classId)
    status.value = 'IDLE'
    calledStudent.value = null
    await fetchJoinedStudents()
  } catch (err) {
    alert('结束失败: ' + err.message)
  }
}
</script>

<style scoped>
.teacher-classroom {
  display: grid;
  grid-template-columns: 1fr 260px;
  gap: 2rem;
  height: calc(100vh - 100px);
  position: relative;
}

.start-class-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.95);
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  backdrop-filter: blur(5px);
}

.overlay-content {
  background: white;
  padding: 3rem;
  border-radius: 20px;
  box-shadow: 0 10px 40px rgba(0,0,0,0.1);
}

.icon-box {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.btn-start-large {
  background: #42b983;
  color: white;
  border: none;
  padding: 1rem 3rem;
  font-size: 1.2rem;
  font-weight: bold;
  border-radius: 50px;
  cursor: pointer;
  margin-top: 2rem;
  transition: transform 0.2s, background 0.2s;
}

.btn-start-large:hover {
  background: #3aa876;
  transform: scale(1.05);
}

.classroom-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #eee;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.btn-back {
  background: none;
  border: none;
  color: #666;
  cursor: pointer;
}

.btn-stop-class {
  background: #ff4d4f;
  color: white;
  border: none;
  padding: 0.5rem 1.2rem;
  border-radius: 6px;
  cursor: pointer;
}

.control-panel {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.05);
  margin-bottom: 2rem;
}

.button-group {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  margin-top: 1rem;
}

.btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 1.5rem;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: transform 0.2s, background 0.3s;
  font-weight: bold;
  color: white;
}

.btn:hover { transform: translateY(-2px); }
.btn:disabled { opacity: 0.6; cursor: not-allowed; }

.attendance { background: #42b983; }
.random-call { background: #3498db; }
.quiz { background: #f39c12; }

.active-session {
  background: #e8f5e9;
  padding: 1.5rem;
  border-radius: 12px;
  border: 1px solid #c8e6c9;
}

.session-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.btn-stop {
  padding: 0.5rem 1rem;
  background: #e74c3c;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.progress-bar {
  height: 10px;
  background: #ddd;
  border-radius: 5px;
  margin-top: 0.5rem;
  overflow: hidden;
}

.progress {
  height: 100%;
  background: #42b983;
  transition: width 0.5s;
}

.call-result {
  margin-top: 2rem;
  display: flex;
  justify-content: center;
}

.student-card {
  background: white;
  padding: 2rem;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
  text-align: center;
  width: 100%;
  max-width: 400px;
}

.avatar { font-size: 4rem; margin-bottom: 1rem; }

.rating-actions {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid #eee;
}

.stars {
  margin: 1rem 0;
  display: flex;
  justify-content: center;
  gap: 0.5rem;
}

.stars button {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  filter: grayscale(1);
}

.stars button.active { filter: grayscale(0); }

.btn-confirm {
  width: 100%;
  padding: 0.8rem;
  background: #34495e;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
}

/* 随机点名面板样式 (内联) */
.call-panel-section {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.08);
  margin-bottom: 2rem;
  overflow: hidden;
  animation: slideDown 0.3s ease-out;
}

@keyframes slideDown {
  from { transform: translateY(-20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.panel-header {
  padding: 1rem 1.5rem;
  background: #f8f9fa;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.panel-header h4 { margin: 0; color: #2c3e50; }

.call-setup-inline {
  padding: 1.5rem;
}

.call-result-inline {
  padding: 2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.lucky-info {
  display: flex;
  align-items: center;
  gap: 2rem;
  margin-bottom: 1.5rem;
}

.lucky-avatar {
  font-size: 3.5rem;
}

.lucky-text {
  text-align: left;
}

.lucky-name {
  font-size: 1.8rem;
  margin: 0;
  color: #2c3e50;
}

.lucky-id {
  color: #7f8c8d;
  margin: 0.2rem 0 0;
}

.rating-section-inline {
  width: 100%;
  max-width: 400px;
  padding-top: 1.5rem;
  border-top: 1px solid #eee;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.rating-label {
  font-weight: bold;
  color: #666;
  margin-bottom: 0.5rem;
}

.stars {
  margin: 1rem 0;
  display: flex;
  justify-content: center;
  gap: 0.5rem;
}

.stars button {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  filter: grayscale(1);
}

.stars button.active { filter: grayscale(0); }

.action-buttons {
  display: flex;
  gap: 1rem;
  width: 100%;
  margin-top: 1rem;
}

.action-buttons button {
  flex: 1;
  padding: 0.7rem;
  border-radius: 8px;
  font-weight: bold;
  cursor: pointer;
}

.btn-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #999;
  cursor: pointer;
}

.setup-hint {
  color: #666;
  margin-bottom: 1.5rem;
}

.strategy-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  margin-bottom: 2rem;
}

.strategy-grid button {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.8rem;
  padding: 1.5rem 1rem;
  background: white;
  border: 2px solid #f0f0f0;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.strategy-grid button .icon { font-size: 1.8rem; }
.strategy-grid button span { font-size: 0.9rem; color: #333; }

.strategy-grid button:hover {
  border-color: #3498db;
  background: #f7fbfe;
}

.strategy-grid button.active {
  border-color: #3498db;
  background: #ebf5ff;
  box-shadow: 0 4px 12px rgba(52, 152, 219, 0.15);
}

.btn-call-now {
  width: 100%;
  padding: 1rem;
  font-size: 1.1rem;
  font-weight: bold;
  border-radius: 12px;
  background: #3498db;
  color: white;
  border: none;
}

.btn-cancel {
  background: #f8f9fa;
  border: 1px solid #ddd;
  color: #666;
}

.btn-submit {
  background: #3498db;
  border: none;
  color: white;
}

.btn-submit:disabled {
  background: #bdc3c7;
  cursor: not-allowed;
}

/* 课堂提问面板样式 */
.question-panel-section {
  background: white;
  border-radius: 16px;
  box-shadow: 0 8px 30px rgba(0,0,0,0.1);
  margin-bottom: 2rem;
  overflow: hidden;
  border: 1px solid #eee;
}

.question-setup {
  padding: 2rem;
}

.setup-tabs {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.setup-tabs button {
  flex: 1;
  padding: 0.8rem;
  border: 1px solid #ddd;
  background: #f8f9fa;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.setup-tabs button.active {
  background: #3498db;
  color: white;
  border-color: #3498db;
}

.bank-select {
  width: 100%;
  padding: 0.8rem;
  border-radius: 8px;
  border: 1px solid #ddd;
  margin-bottom: 1rem;
}

.bank-controls {
  margin-bottom: 1rem;
}

.search-box-mini {
  display: flex;
  align-items: center;
  background: #f5f7fa;
  border-radius: 8px;
  padding: 0.5rem 1rem;
  border: 1px solid #e4e7ed;
}

.search-box-mini input {
  border: none;
  background: transparent;
  margin-left: 0.5rem;
  width: 100%;
  outline: none;
  font-size: 0.9rem;
}

.question-list-mini {
  max-height: 250px;
  overflow-y: auto;
  border: 1px solid #eee;
  border-radius: 8px;
  margin-bottom: 1rem;
}

.q-item-mini {
  padding: 0.8rem;
  border-bottom: 1px solid #f5f5f5;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background 0.2s;
  display: flex;
  align-items: flex-start;
  gap: 0.8rem;
}

.q-type-tag {
  font-size: 0.7rem;
  padding: 2px 6px;
  border-radius: 4px;
  white-space: nowrap;
  color: white;
}

.q-type-tag.single { background: #42b983; }
.q-type-tag.judge { background: #e6a23c; }
.q-type-tag.multiple { background: #3498db; }

.q-content-text {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.mini-pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
  font-size: 0.85rem;
}

.mini-pagination button {
  padding: 4px 12px;
  border: 1px solid #ddd;
  background: white;
  border-radius: 4px;
  cursor: pointer;
}

.mini-pagination button:disabled {
  background: #f5f5f5;
  cursor: not-allowed;
  color: #ccc;
}

.q-item-mini:hover {
  background: #f0f7ff;
}

.q-item-mini.selected {
  background: #e3f2fd;
  border-left: 4px solid #3498db;
}

.manual-textarea {
  width: 100%;
  height: 120px;
  padding: 1rem;
  border-radius: 8px;
  border: 1px solid #ddd;
  margin-bottom: 1.5rem;
  resize: none;
}

.btn-start-q {
  width: 100%;
  padding: 1rem;
  font-size: 1.1rem;
  font-weight: bold;
}

.question-active-stats {
  padding: 2rem;
}

.q-content-preview {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  border-left: 4px solid #3498db;
}

.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: #f0f7ff;
  padding: 1.5rem;
  border-radius: 12px;
  text-align: center;
}

.stat-card .value {
  font-size: 2rem;
  font-weight: bold;
  color: #3498db;
}

.stat-card .label {
  color: #666;
  font-size: 0.9rem;
  margin-top: 0.5rem;
}

.options-chart {
  margin-bottom: 2rem;
}

.chart-row {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.bar-bg {
  flex: 1;
  height: 12px;
  background: #eee;
  border-radius: 6px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  background: #3498db;
  transition: width 0.5s ease;
}

.submission-list {
  margin-bottom: 2rem;
}

.list-container {
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 0.5rem;
}

.submission-item {
  padding: 0.6rem;
  border-bottom: 1px solid #f5f5f5;
  font-size: 0.9rem;
}

.s-name { font-weight: bold; }
.s-time { color: #999; margin-left: 0.5rem; }
.s-answer { color: #3498db; }

.btn-stop-q {
  width: 100%;
  padding: 0.8rem;
  background: #e74c3c;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: bold;
  cursor: pointer;
}

.empty-hint {
  padding: 2rem;
  text-align: center;
  color: #999;
  font-size: 0.9rem;
}

.classroom-sidebar {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.05);
}

.student-list {
  margin-top: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}

.student-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #ccc;
}

.status-dot.online { background: #42b983; }

.signed-tag {
  margin-left: auto;
  font-size: 0.7rem;
  background: #e8f5e9;
  color: #42b983;
  padding: 2px 6px;
  border-radius: 4px;
}

.more { text-align: center; color: #999; font-size: 0.8rem; margin-top: 1rem; }
</style>
