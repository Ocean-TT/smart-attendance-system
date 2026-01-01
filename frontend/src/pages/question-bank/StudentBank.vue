<template>
  <div class="student-bank">
    <!-- 题库选择视图 -->
    <div v-if="mode === 'SELECT_BANK'" class="bank-selection">
      <header class="bank-header">
        <div class="welcome">
          <h2>自助练习模式</h2>
          <p>请选择一个题库开始练习，巩固你的知识点。</p>
        </div>
        <div class="stats">
          <div class="stat-item">
            <span class="label">已练习</span>
            <span class="value">{{ practicedCount }}</span>
          </div>
          <div class="stat-item">
            <span class="label">正确率</span>
            <span class="value">{{ accuracy }}%</span>
          </div>
        </div>
      </header>

      <div class="bank-grid">
        <div v-for="bank in questionBanks" :key="bank.id" class="bank-card" @click="selectBank(bank)">
          <div class="bank-card-header">
            <div class="bank-icon-wrapper">
              <span class="bank-icon">📚</span>
            </div>
            <div class="bank-tag">{{ bank.courseCode }}</div>
          </div>
          
          <div class="bank-card-body">
            <h4>{{ bank.name }}</h4>
            <div class="bank-stats-mini">
              <span>共 {{ bank.questionCount }} 题</span>
              <span>•</span>
              <span>已完成 {{ bank.progress || 0 }}%</span>
            </div>
            <div class="progress-bar-container">
              <div class="progress-bar-fill" :style="{ width: (bank.progress || 0) + '%' }"></div>
            </div>
          </div>

          <div class="bank-card-footer">
            <span class="start-text">进入练习</span>
            <span class="arrow">→</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 配置阶段 -->
    <div v-else-if="mode === 'CONFIG'" class="config-view">
      <div class="config-header">
        <button class="btn-back" @click="mode = 'SELECT_BANK'">← 返回题库列表</button>
        <h3>练习设置 - {{ selectedBank?.name }}</h3>
      </div>
      
      <div class="config-layout">
        <!-- 左侧：设置面板 -->
        <div class="config-left">
          <div class="config-card">
            <div class="config-section">
              <label>搜索题目</label>
              <div class="search-box">
                <input v-model="searchQuery" type="text" placeholder="输入关键词搜索题目..." class="search-input">
              </div>
            </div>
            
            <div class="config-section">
              <label>题目数量</label>
              <div class="count-input-group">
                <input v-model.number="questionCount" type="number" min="1" :max="filteredQuestions.length" class="count-input">
                <span class="total-hint">/ 共 {{ filteredQuestions.length }} 题</span>
              </div>
              <div class="quick-counts">
                <button 
                  v-for="num in [5, 10, 20]" 
                  :key="num"
                  :class="['mini-tag', { active: questionCount === num }]"
                  @click="questionCount = num"
                >{{ num }} 题</button>
              </div>
            </div>

            <button class="btn-start" @click="startPractice" :disabled="filteredQuestions.length === 0">
              开始练习 ({{ Math.min(questionCount, filteredQuestions.length) }} 题)
            </button>
          </div>
        </div>

        <!-- 右侧：题目预览 -->
        <div class="config-right">
          <div class="preview-container">
            <div class="preview-header">
              <span>题目预览</span>
              <span class="preview-count">显示 {{ paginatedQuestions.length }} 题</span>
            </div>
            
            <div class="preview-list">
              <div v-for="q in paginatedQuestions" :key="q.id" class="preview-item">
                <div class="preview-meta">
                  <span :class="['type-tag-mini', q.type]">
                    {{ q.type === 'SINGLE' ? '单选' : (q.type === 'JUDGE' ? '判断' : '简答') }}
                  </span>
                </div>
                <p class="preview-content">{{ q.content }}</p>
              </div>
              
              <div v-if="filteredQuestions.length === 0" class="empty-preview">
                <div class="empty-icon">🔍</div>
                <p>未找到匹配的题目</p>
              </div>
            </div>

            <!-- 分页控制 -->
            <div v-if="totalPages > 1" class="pagination">
              <button :disabled="currentPage === 1" @click="currentPage--" class="page-btn">上一页</button>
              <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
              <button :disabled="currentPage === totalPages" @click="currentPage++" class="page-btn">下一页</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 练习阶段 -->
    <div v-else-if="mode === 'PRACTICE' && currentQuestion" class="question-display">
      <div class="question-meta">
        <span :class="['type-tag', currentQuestion.type]">
          {{ currentQuestion.type === 'SINGLE' ? '单选题' : (currentQuestion.type === 'JUDGE' ? '判断题' : '简答题') }}
        </span>
        <span class="q-index">题目 {{ currentIndex + 1 }} / {{ activeQuestions.length }}</span>
      </div>
      
      <h3 class="q-content">{{ currentQuestion.content }}</h3>

      <div v-if="currentQuestion.type === 'SINGLE'" class="options-list">
        <button 
          v-for="(opt, idx) in currentQuestion.options" 
          :key="idx"
          @click="selectOption(idx)"
          :class="['option-btn', { 
            selected: selectedOption === idx,
            correct: showResult && isCorrect(idx),
            wrong: showResult && selectedOption === idx && !isCorrect(idx)
          }]"
          :disabled="showResult"
        >
          <span class="opt-label">{{ String.fromCharCode(65 + idx) }}</span>
          <span class="opt-text">{{ opt }}</span>
        </button>
      </div>

      <div v-if="currentQuestion.type === 'JUDGE'" class="options-list binary">
        <button 
          @click="selectOption('正确')" 
          :class="['option-btn', { 
            selected: selectedOption === '正确', 
            correct: showResult && currentQuestion.answer === '正确',
            wrong: showResult && selectedOption === '正确' && currentQuestion.answer !== '正确'
          }]"
          :disabled="showResult"
        >正确</button>
        <button 
          @click="selectOption('错误')" 
          :class="['option-btn', { 
            selected: selectedOption === '错误', 
            correct: showResult && currentQuestion.answer === '错误',
            wrong: showResult && selectedOption === '错误' && currentQuestion.answer !== '错误'
          }]"
          :disabled="showResult"
        >错误</button>
      </div>

      <div v-if="currentQuestion.type === 'SHORT'" class="essay-input">
        <textarea v-model="essayAnswer" placeholder="请输入你的回答..." :disabled="showResult"></textarea>
      </div>

      <div class="action-footer">
        <button v-if="!showResult" @click="checkAnswer" class="btn-check" :disabled="selectedOption === null && !essayAnswer">检查答案</button>
        <div v-else class="result-feedback">
          <p v-if="isUserCorrect" class="msg success">✨ 回答正确！太棒了！</p>
          <p v-else class="msg error">❌ 回答错误。正确答案是：{{ currentQuestion.answer }}</p>
          <button @click="nextQuestion" class="btn-next">下一题 →</button>
        </div>
      </div>
    </div>

    <!-- 结果阶段 -->
    <div v-else-if="mode === 'RESULT'" class="result-view">
      <div class="result-card">
        <div class="result-icon">🏆</div>
        <h2>练习完成！</h2>
        <div class="score-grid">
          <div class="score-item">
            <span class="val">{{ score }}</span>
            <span class="lab">得分</span>
          </div>
          <div class="score-item">
            <span class="val">{{ activeQuestions.length }}</span>
            <span class="lab">总题数</span>
          </div>
          <div class="score-item">
            <span class="val">{{ Math.round((score/activeQuestions.length)*100) }}%</span>
            <span class="lab">正确率</span>
          </div>
        </div>
        <div class="result-actions">
          <button @click="mode = 'SELECT_BANK'" class="btn-finish">返回题库列表</button>
          <button @click="restart" class="btn-retry">再练一次</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getQuestionBanks, getQuestionsInBank, getStudentStats, submitPractice } from '../../api'
import { useAuthStore } from '../../store/auth'

const { user } = useAuthStore()
const mode = ref('SELECT_BANK') // SELECT_BANK, CONFIG, PRACTICE, RESULT
const selectedBank = ref(null)
const practicedCount = ref(0)
const accuracy = ref(0)

const questionBanks = ref([])

const fetchBanks = async () => {
  try {
    const res = await getQuestionBanks()
    questionBanks.value = res.data
    
    // 获取学生统计
    const studentId = user.value?.studentId || '20230001'
    const statsRes = await getStudentStats(studentId)
    const stats = statsRes.data || statsRes
    practicedCount.value = stats.practicedCount || 0
    accuracy.value = parseInt(stats.accuracy) || 0
  } catch (error) {
    console.error('获取数据失败:', error)
  }
}

onMounted(() => {
  fetchBanks()
})

const selectBank = async (bank) => {
  selectedBank.value = bank
  mode.value = 'CONFIG'
  searchQuery.value = ''
  currentPage.value = 1
  try {
    const res = await getQuestionsInBank(bank.id)
    questions.value = res.data
  } catch (error) {
    console.error('获取题目失败:', error)
  }
}

const questionCount = ref(10)
const searchQuery = ref('')
const currentPage = ref(1)
const pageSize = 5

const questions = ref([])

const filteredQuestions = computed(() => {
  if (!searchQuery.value) return questions.value
  const query = searchQuery.value.toLowerCase()
  return questions.value.filter(q => 
    q.content.toLowerCase().includes(query) || 
    (q.options && q.options.some(opt => opt.toLowerCase().includes(query)))
  )
})

const totalPages = computed(() => Math.ceil(filteredQuestions.value.length / pageSize))

const paginatedQuestions = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return filteredQuestions.value.slice(start, start + pageSize)
})

const activeQuestions = ref([])
const currentIndex = ref(0)
const selectedOption = ref(null)
const essayAnswer = ref('')
const showResult = ref(false)
const score = ref(0)

const currentQuestion = computed(() => activeQuestions.value[currentIndex.value])
const isUserCorrect = ref(false)

const startPractice = () => {
  // 根据配置筛选题目
  activeQuestions.value = filteredQuestions.value.slice(0, questionCount.value)
  if (activeQuestions.value.length === 0) return
  
  currentIndex.value = 0
  mode.value = 'PRACTICE'
  resetQuestionState()
}

const selectOption = (idx) => {
  if (showResult.value) return
  selectedOption.value = idx
}

const isCorrect = (idx) => {
  if (!currentQuestion.value) return false
  const ansMap = { 0: 'A', 1: 'B', 2: 'C', 3: 'D' }
  const answer = currentQuestion.value.answer
  // 支持字母答案 (A) 或 文本答案 (维护阶段)
  return answer === ansMap[idx] || answer === currentQuestion.value.options[idx]
}

const checkAnswer = () => {
  showResult.value = true
  if (currentQuestion.value.type === 'SINGLE' || currentQuestion.value.type === 'JUDGE') {
    isUserCorrect.value = isCorrect(selectedOption.value)
  } else {
    isUserCorrect.value = true // 简答题模拟正确
  }
  
  if (isUserCorrect.value) score.value++
}

const nextQuestion = async () => {
  if (currentIndex.value < activeQuestions.value.length - 1) {
    currentIndex.value++
    resetQuestionState()
  } else {
    mode.value = 'RESULT'
    // 提交练习结果
    try {
      await submitPractice({
        bank_id: selectedBank.value.id,
        total_questions: activeQuestions.value.length,
        correct_count: score.value,
        score: score.value // 这里简单以正确题数作为分数
      })
      // 刷新统计数据和题库列表
      fetchBanks()
    } catch (error) {
      console.error('提交练习失败:', error)
    }
  }
}

const resetQuestionState = () => {
  selectedOption.value = null
  essayAnswer.value = ''
  showResult.value = false
  isUserCorrect.value = false
}

const restart = () => {
  score.value = 0
  startPractice()
}
</script>

<style scoped>
.student-bank { display: flex; flex-direction: column; gap: 1.5rem; }

.bank-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  padding: 1.5rem 2rem;
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}

.welcome h2 { margin: 0 0 0.5rem 0; color: #2c3e50; }
.welcome p { margin: 0; color: #7f8c8d; font-size: 0.95rem; }

.stats { display: flex; gap: 2rem; }
.stat-item { text-align: center; }
.stat-item .label { display: block; font-size: 0.8rem; color: #999; margin-bottom: 4px; }
.stat-item .value { font-size: 1.5rem; font-weight: bold; color: #42b983; }

.bank-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
}

.bank-card {
  background: white;
  border-radius: 20px;
  padding: 1.5rem;
  box-shadow: 0 4px 15px rgba(0,0,0,0.05);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
  border: 1px solid #f0f0f0;
}

.bank-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 30px rgba(66, 185, 131, 0.15);
  border-color: #42b983;
}

.bank-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.bank-icon-wrapper {
  width: 48px;
  height: 48px;
  background: #f0f9eb;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
}

.bank-tag {
  font-size: 0.75rem;
  background: #f4f4f5;
  color: #909399;
  padding: 4px 8px;
  border-radius: 6px;
  font-weight: 500;
}

.bank-card-body h4 {
  margin: 0 0 0.5rem 0;
  font-size: 1.15rem;
  color: #2c3e50;
  font-weight: 600;
}

.bank-stats-mini {
  display: flex;
  gap: 8px;
  font-size: 0.85rem;
  color: #606266;
  margin-bottom: 1rem;
}

.progress-bar-container {
  height: 6px;
  background: #ebeef5;
  border-radius: 3px;
  overflow: hidden;
}

.progress-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #42b983, #3498db);
  border-radius: 3px;
  transition: width 0.5s ease;
}

.bank-card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: auto;
  padding-top: 1rem;
  border-top: 1px solid #f5f7fa;
}

.start-text {
  font-size: 0.9rem;
  color: #42b983;
  font-weight: 600;
}

.arrow {
  color: #42b983;
  transition: transform 0.3s;
}

.bank-card:hover .arrow {
  transform: translateX(5px);
}

.config-view {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.config-header { display: flex; align-items: center; gap: 1.5rem; }
.btn-back { background: #f0f2f5; border: none; padding: 0.5rem 1rem; border-radius: 8px; cursor: pointer; color: #606266; font-weight: 500; }

.config-layout {
  display: grid;
  grid-template-columns: 350px 1fr;
  gap: 2rem;
  align-items: start;
}

.config-left .config-card {
  background: white;
  padding: 2rem;
  border-radius: 20px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.05);
}

.config-section { margin-bottom: 2rem; }
.config-section label { display: block; margin-bottom: 1rem; font-weight: bold; color: #2c3e50; }

.search-input {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #dcdfe6;
  border-radius: 10px;
  font-size: 0.95rem;
  outline: none;
  transition: border-color 0.3s;
}
.search-input:focus { border-color: #42b983; }

.count-input-group {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 1rem;
}
.count-input {
  width: 80px;
  padding: 10px;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  text-align: center;
  font-size: 1rem;
}
.total-hint { color: #909399; font-size: 0.9rem; }

.quick-counts { display: flex; gap: 8px; }
.mini-tag {
  padding: 6px 12px;
  border: 1px solid #dcdfe6;
  background: #f8f9fa;
  border-radius: 6px;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s;
}
.mini-tag.active { background: #42b983; color: white; border-color: #42b983; }

.config-right .preview-container {
  background: white;
  border-radius: 20px;
  padding: 1.5rem;
  box-shadow: 0 4px 20px rgba(0,0,0,0.05);
  min-height: 500px;
  display: flex;
  flex-direction: column;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  padding-bottom: 1rem;
  border-bottom: 1px solid #f0f0f0;
  margin-bottom: 1rem;
  font-weight: 600;
  color: #2c3e50;
}
.preview-count { color: #909399; font-size: 0.9rem; font-weight: normal; }

.preview-list { flex: 1; display: flex; flex-direction: column; gap: 1rem; }
.preview-item {
  padding: 1.2rem;
  background: #f8f9fa;
  border-radius: 12px;
  border: 1px solid #f0f0f0;
}
.preview-meta { margin-bottom: 0.5rem; }
.type-tag-mini {
  font-size: 0.7rem;
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: bold;
  text-transform: uppercase;
}
.type-tag-mini.SINGLE { background: #e1f5fe; color: #0288d1; }
.type-tag-mini.JUDGE { background: #f3e5f5; color: #7b1fa2; }
.type-tag-mini.SHORT { background: #fff3e0; color: #f57c00; }

.preview-content {
  margin: 0;
  color: #34495e;
  line-height: 1.5;
  font-size: 0.95rem;
}

.empty-preview {
  text-align: center;
  padding: 4rem 0;
  color: #909399;
}
.empty-icon { font-size: 3rem; margin-bottom: 1rem; }

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1.5rem;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid #f0f0f0;
}
.page-btn {
  padding: 6px 16px;
  border: 1px solid #dcdfe6;
  background: white;
  border-radius: 6px;
  cursor: pointer;
}
.page-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.page-info { font-size: 0.9rem; color: #606266; }

.btn-start {
  width: 100%;
  padding: 1.2rem;
  background: #42b983;
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 1.2rem;
  font-weight: bold;
  cursor: pointer;
  transition: background 0.3s;
  margin-top: 1rem;
}
.btn-start:hover { background: #3aa876; }
.btn-start:disabled { background: #a8d8b9; cursor: not-allowed; }

.question-display {
  background: white;
  padding: 2.5rem;
  border-radius: 20px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.05);
}

.question-meta { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; }
.type-tag { padding: 4px 12px; border-radius: 6px; font-size: 0.8rem; color: white; font-weight: bold; }
.type-tag.单选 { background: #3498db; }
.type-tag.判断 { background: #f1c40f; }
.type-tag.简答 { background: #e67e22; }
.q-index { color: #999; font-size: 0.9rem; }

.q-content { font-size: 1.4rem; line-height: 1.6; color: #2c3e50; margin-bottom: 2rem; }

.options-list { display: flex; flex-direction: column; gap: 1rem; }
.option-btn {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.2rem;
  border: 2px solid #f0f2f5;
  background: #f8f9fa;
  border-radius: 12px;
  cursor: pointer;
  text-align: left;
  transition: all 0.2s;
}
.option-btn:hover:not(:disabled) { border-color: #42b983; background: #f0f9eb; }
.option-btn.selected { border-color: #42b983; background: #f0f9eb; }
.option-btn.correct { border-color: #42b983; background: #e8f5e9; color: #2d8a5e; }
.option-btn.wrong { border-color: #e74c3c; background: #fdf2f2; color: #c0392b; }

.opt-label { font-weight: bold; color: #3498db; font-size: 1.1rem; }
.opt-text { font-size: 1.05rem; }

.essay-input textarea { width: 100%; height: 150px; padding: 1rem; border: 2px solid #f0f2f5; border-radius: 12px; outline: none; font-size: 1rem; }

.action-footer { margin-top: 2.5rem; border-top: 1px solid #eee; padding-top: 2rem; }
.btn-check { width: 100%; padding: 1rem; background: #34495e; color: white; border: none; border-radius: 12px; font-size: 1.1rem; font-weight: bold; cursor: pointer; }
.btn-check:disabled { opacity: 0.5; cursor: not-allowed; }

.result-feedback { text-align: center; }
.msg { font-size: 1.2rem; font-weight: bold; margin-bottom: 1.5rem; }
.msg.success { color: #42b983; }
.msg.error { color: #e74c3c; }
.btn-next { padding: 1rem 3rem; background: #42b983; color: white; border: none; border-radius: 12px; font-size: 1.1rem; font-weight: bold; cursor: pointer; }

.result-view { text-align: center; }
.result-card { background: white; padding: 4rem 2rem; border-radius: 24px; box-shadow: 0 10px 30px rgba(0,0,0,0.05); }
.result-icon { font-size: 5rem; margin-bottom: 1rem; }
.score-grid { display: flex; justify-content: center; gap: 3rem; margin: 3rem 0; }
.score-item { display: flex; flex-direction: column; }
.score-item .val { font-size: 2.5rem; font-weight: bold; color: #2c3e50; }
.score-item .lab { font-size: 0.9rem; color: #999; }

.result-actions { display: flex; justify-content: center; gap: 1.5rem; }
.btn-finish { padding: 1rem 2rem; background: #f0f2f5; color: #606266; border: none; border-radius: 12px; font-weight: bold; cursor: pointer; }
.btn-retry { padding: 1rem 2rem; background: #42b983; color: white; border: none; border-radius: 12px; font-weight: bold; cursor: pointer; }
</style>
