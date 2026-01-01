<template>
  <div class="teacher-bank">
    <!-- 题库列表视图 -->
    <div v-if="!selectedBank" class="bank-list-view">
      <header class="bank-header">
        <div class="header-info">
          <h2>题库管理</h2>
          <p>管理各班级关联的题库资源</p>
        </div>
      </header>
      
      <div class="bank-grid">
        <div v-for="bank in questionBanks" :key="bank.id" class="bank-card" @click="selectBank(bank)">
          <div class="bank-icon">📚</div>
          <div class="bank-info">
            <h4>{{ bank.name }}</h4>
            <p>{{ bank.questionCount }} 道题目</p>
            <span class="bank-tag">{{ bank.courseCode }}</span>
          </div>
          <div class="bank-arrow">→</div>
        </div>
      </div>
    </div>

    <!-- 题目管理视图 -->
    <div v-else class="question-manage-view">
      <header class="bank-header">
        <div class="header-left">
          <button class="btn-back" @click="selectedBank = null">← 返回题库列表</button>
          <h3>{{ selectedBank.name }} - 题目管理</h3>
        </div>
        <div class="search-bar">
          <input v-model="searchQuery" placeholder="搜索题目内容或标签..." class="input-search" />
          <select v-model="filterType" class="select-filter">
            <option value="ALL">所有类型</option>
            <option value="SINGLE">单选</option>
            <option value="MULTIPLE">多选</option>
            <option value="JUDGE">判断</option>
            <option value="SHORT">简答</option>
          </select>
        </div>
        <button @click="showAddModal = true" class="btn-add">+ 新建题目</button>
      </header>

      <div class="question-list">
        <div v-for="q in filteredQuestions" :key="q.id" class="question-card">
          <div class="card-header">
            <span :class="['type-tag', q.type]">{{ formatType(q.type) }}</span>
            <div class="tags">
              <span v-for="tag in q.tags" :key="tag" class="tag">#{{ tag }}</span>
            </div>
            <div class="actions">
              <button @click="editQuestion(q)" class="btn-icon">✏️</button>
              <button @click="deleteQuestion(q.id)" class="btn-icon delete">🗑️</button>
            </div>
          </div>
          <div class="card-body">
            <p class="content">{{ q.content }}</p>
            <div v-if="q.options" class="options">
              <div v-for="(opt, idx) in q.options" :key="idx" class="option">
                <span class="label">{{ String.fromCharCode(65 + idx) }}.</span> {{ opt }}
              </div>
            </div>
            <div class="answer-box">
              <strong>正确答案：</strong> <span class="answer-text">{{ q.answer }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 模拟弹窗 -->
    <div v-if="showAddModal" class="modal-overlay">
      <div class="modal-content">
        <h3>{{ editingId ? '编辑题目' : '新增题目' }}</h3>
        <form @submit.prevent="saveQuestion">
          <div class="form-group">
            <label>题目类型</label>
            <select v-model="form.type" required>
              <option value="SINGLE">单选</option>
              <option value="MULTIPLE">多选</option>
              <option value="JUDGE">判断</option>
              <option value="SHORT">简答</option>
            </select>
          </div>
          <div class="form-group">
            <label>题目内容</label>
            <textarea v-model="form.content" placeholder="请输入题干..." required></textarea>
          </div>
          <div v-if="['SINGLE', 'MULTIPLE'].includes(form.type)" class="form-group">
            <label>选项 (每行一个)</label>
            <textarea v-model="form.optionsText" placeholder="选项A&#10;选项B..."></textarea>
          </div>
          <div class="form-group">
            <label>正确答案</label>
            <input v-model="form.answer" placeholder="请输入答案" required />
          </div>
          <div class="form-group">
            <label>标签 (逗号分隔)</label>
            <input v-model="form.tagsText" placeholder="例如：网络, 基础" />
          </div>
          <div class="modal-actions">
            <button type="button" @click="closeModal" class="btn-cancel">取消</button>
            <button type="submit" class="btn-save">保存</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getQuestionBanks, getQuestionsInBank, createQuestion, updateQuestion, deleteQuestion as deleteQuestionApi } from '../../api'

const searchQuery = ref('')
const filterType = ref('ALL')
const showAddModal = ref(false)
const editingId = ref(null)
const selectedBank = ref(null)
const loading = ref(false)

const formatType = (type) => {
  const map = {
    'SINGLE': '单选',
    'MULTIPLE': '多选',
    'JUDGE': '判断',
    'SHORT': '简答'
  }
  return map[type] || type
}

const questionBanks = ref([])
const questions = ref([])

onMounted(async () => {
  await fetchBanks()
})

const fetchBanks = async () => {
  try {
    const response = await getQuestionBanks()
    questionBanks.value = response.data || response
  } catch (err) {
    console.error('获取题库失败:', err)
  }
}

const selectBank = async (bank) => {
  selectedBank.value = bank
  loading.value = true
  try {
    const response = await getQuestionsInBank(bank.id)
    questions.value = response.data || response
  } catch (err) {
    console.error('获取题目失败:', err)
  } finally {
    loading.value = false
  }
}

const form = ref({
  type: 'SINGLE',
  content: '',
  optionsText: '',
  answer: '',
  tagsText: ''
})

const filteredQuestions = computed(() => {
  return questions.value.filter(q => {
    const matchesSearch = q.content.toLowerCase().includes(searchQuery.value.toLowerCase()) || 
                         (q.tags && q.tags.some(t => t.toLowerCase().includes(searchQuery.value.toLowerCase())))
    const matchesType = filterType.value === 'ALL' || q.type === filterType.value
    return matchesSearch && matchesType
  })
})

const editQuestion = (q) => {
  editingId.value = q.id
  form.value = {
    type: q.type,
    content: q.content,
    optionsText: q.options ? q.options.join('\n') : '',
    answer: q.answer,
    tagsText: q.tags ? q.tags.join(', ') : ''
  }
  showAddModal.value = true
}

const deleteQuestion = async (id) => {
  if (confirm('确定要删除这道题吗？')) {
    try {
      await deleteQuestionApi(id)
      questions.value = questions.value.filter(q => q.id !== id)
    } catch (err) {
      alert('删除失败: ' + err.message)
    }
  }
}

const saveQuestion = async () => {
  const questionData = {
    type: form.value.type,
    content: form.value.content,
    answer: form.value.answer,
    tags: form.value.tagsText.split(',').map(t => t.trim()).filter(t => t),
    options: ['SINGLE', 'MULTIPLE'].includes(form.value.type) ? form.value.optionsText.split('\n').filter(o => o.trim()) : null
  }

  try {
    if (editingId.value) {
      await updateQuestion(editingId.value, questionData)
      const idx = questions.value.findIndex(q => q.id === editingId.value)
      if (idx !== -1) {
        questions.value[idx] = { ...questions.value[idx], ...questionData }
      }
      alert('更新成功')
    } else {
      const response = await createQuestion(selectedBank.value.id, questionData)
      const newQ = response.data || response
      questions.value.unshift(newQ)
    }
    closeModal()
  } catch (err) {
    alert('保存失败: ' + err.message)
  }
}

const closeModal = () => {
  showAddModal.value = false
  editingId.value = null
  form.value = { type: 'SINGLE', content: '', optionsText: '', answer: '', tagsText: '' }
}
</script>

<style scoped>
.teacher-bank { display: flex; flex-direction: column; gap: 1.5rem; }

.bank-list-view {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.bank-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.bank-card {
  background: white;
  padding: 1.5rem;
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
  display: flex;
  align-items: center;
  gap: 1.2rem;
  cursor: pointer;
  transition: all 0.3s;
  border: 2px solid transparent;
}

.bank-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.1);
  border-color: #42b983;
}

.bank-icon { font-size: 3rem; }
.bank-info h4 { margin: 0 0 0.4rem 0; font-size: 1.2rem; color: #2c3e50; }
.bank-info p { margin: 0; color: #909399; font-size: 0.9rem; }
.bank-tag { display: inline-block; margin-top: 0.6rem; font-size: 0.75rem; background: #f0f9eb; color: #67c23a; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
.bank-arrow { margin-left: auto; color: #c0c4cc; font-size: 1.2rem; }

.bank-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.05);
}

.header-left { display: flex; align-items: center; gap: 1rem; }
.btn-back { background: #f0f2f5; border: none; padding: 0.5rem 1rem; border-radius: 6px; cursor: pointer; color: #606266; font-weight: 500; }
.btn-back:hover { background: #e4e7ed; }

.search-bar { display: flex; gap: 10px; flex: 1; max-width: 500px; margin: 0 1.5rem; }
.input-search { flex: 1; padding: 0.6rem 1rem; border: 1px solid #ddd; border-radius: 8px; outline: none; }
.select-filter { padding: 0.6rem; border: 1px solid #ddd; border-radius: 8px; outline: none; }

.btn-add {
  padding: 0.6rem 1.5rem;
  background: #42b983;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: bold;
}

.question-list { display: flex; flex-direction: column; gap: 1rem; }

.question-card {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  border-left: 4px solid #eee;
  transition: border-color 0.3s;
}

.question-card:hover { border-color: #42b983; }

.card-header { display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem; }

.type-tag {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: bold;
  color: white;
}
.type-tag.单选 { background: #3498db; }
.type-tag.多选 { background: #9b59b6; }
.type-tag.判断 { background: #f1c40f; }
.type-tag.简答 { background: #e67e22; }

.tags { display: flex; gap: 5px; flex: 1; }
.tag { font-size: 0.8rem; color: #999; }

.actions { display: flex; gap: 5px; }
.btn-icon { background: none; border: none; cursor: pointer; font-size: 1.1rem; padding: 4px; border-radius: 4px; }
.btn-icon:hover { background: #f0f2f5; }
.btn-icon.delete:hover { background: #fff1f0; }

.content { font-size: 1.1rem; color: #2c3e50; margin-bottom: 1rem; font-weight: 500; }

.options { display: grid; grid-template-columns: 1fr 1fr; gap: 0.8rem; margin-bottom: 1rem; background: #f8f9fa; padding: 1rem; border-radius: 8px; }
.option { font-size: 0.95rem; color: #666; }
.option .label { font-weight: bold; color: #3498db; margin-right: 5px; }

.answer-box { font-size: 0.9rem; color: #666; padding-top: 1rem; border-top: 1px solid #eee; }
.answer-text { color: #42b983; font-weight: bold; }

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 2rem;
  border-radius: 16px;
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.form-group { margin-bottom: 1.2rem; display: flex; flex-direction: column; gap: 0.5rem; }
.form-group label { font-weight: bold; color: #666; font-size: 0.9rem; }
.form-group input, .form-group select, .form-group textarea {
  padding: 0.8rem;
  border: 1px solid #ddd;
  border-radius: 8px;
  outline: none;
}
.form-group textarea { height: 100px; resize: vertical; }

.modal-actions { display: flex; gap: 1rem; margin-top: 2rem; }
.btn-cancel { flex: 1; padding: 0.8rem; background: #f0f2f5; border: none; border-radius: 8px; cursor: pointer; }
.btn-save { flex: 1; padding: 0.8rem; background: #42b983; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; }
</style>
