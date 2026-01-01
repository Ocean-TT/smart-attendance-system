<template>
  <div class="teacher-dashboard">
    <header class="dashboard-header">
      <div class="header-left">
        <h2>教师控制台</h2>
        <p>欢迎回来，老师！这是您的教学概览。</p>
      </div>
      <div class="header-right">
        <Clock />
      </div>
    </header>

    <div class="stats-grid">
      <div class="stat-card">
        <h3>我的班级</h3>
        <div class="value">{{ dashboardData.classCount || 0 }}</div>
        <p>本学期授课班级</p>
      </div>
      <div class="stat-card">
        <h3>学生总数</h3>
        <div class="value">{{ dashboardData.studentCount || 0 }}</div>
        <p>覆盖学生人数</p>
      </div>
      <div class="stat-card next-course">
        <h3>下节课程</h3>
        <div v-if="dashboardData.nextCourse" class="next-course-info">
          <div class="course-name">{{ dashboardData.nextCourse.name }}</div>
          <div class="course-time">{{ dashboardData.nextCourse.schedule }}</div>
        </div>
        <div v-else class="value">暂无课程</div>
        <p>{{ dashboardData.nextCourse ? '即将开始' : '本周暂无排课' }}</p>
      </div>
      <div class="stat-card">
        <h3>题库题目</h3>
        <div class="value">{{ dashboardData.practiceCount || 0 }}</div>
        <p>已录入题目数量</p>
      </div>
    </div>

    <section class="managed-classes">
      <div class="section-header">
        <h3>我管理的班级</h3>
        <div class="header-actions">
          <button class="btn-create" @click="showCreateModal = true">+ 创建新班级</button>
          <button class="btn-delete-toggle" :class="{ active: isDeleteMode }" @click="isDeleteMode = !isDeleteMode">
            {{ isDeleteMode ? '完成' : '删除班级' }}
          </button>
        </div>
      </div>
      
      <div class="class-grid" :class="{ 'delete-mode-active': isDeleteMode }">
        <div v-for="cls in classes" :key="cls.id" class="class-card-item">
          <button v-if="isDeleteMode" class="btn-delete-card" @click="handleDeleteClass(cls.id, cls.name)" title="删除班级">
            <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="3 6 5 6 21 6"></polyline>
              <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
              <line x1="10" y1="11" x2="10" y2="17"></line>
              <line x1="14" y1="11" x2="14" y2="17"></line>
            </svg>
          </button>
          <div class="class-info">
            <h4>{{ cls.name }}</h4>
            <p class="description">{{ cls.description }}</p>
            <div class="class-stats">
              <span>👥 {{ cls.student_count || 0 }} 学生</span>
              <span>📅 {{ cls.schedule || '未设置时间' }}</span>
            </div>
          </div>
          <div class="class-actions">
            <router-link :to="'/class/' + cls.id" class="btn-link">班级详情</router-link>
            <router-link :to="'/classroom/' + cls.id" class="btn-enter">进入课堂</router-link>
          </div>
        </div>
      </div>
    </section>

    <!-- 创建班级弹窗 -->
    <div v-if="showCreateModal" class="modal-overlay">
      <div class="modal-content">
        <h3>创建新班级</h3>
        <form @submit.prevent="submitCreateClass">
          <div class="form-group">
            <label>班级名称</label>
            <input v-model="newClass.name" placeholder="例如：计算机网络 2025春季班" required />
          </div>
          <div class="form-group">
            <label>班级描述</label>
            <textarea v-model="newClass.description" placeholder="本课程讲解TCP/IP协议栈..." rows="2"></textarea>
          </div>
          <div class="form-group">
            <label>上课时间 (可添加多个)</label>
            <div v-for="(sched, index) in newClass.schedules" :key="index" class="schedule-row">
              <select v-model="sched.day" class="day-select">
                <option v-for="d in ['周一', '周二', '周三', '周四', '周五', '周六', '周日']" :key="d" :value="d">{{ d }}</option>
              </select>
              <input v-model="sched.time" placeholder="08:00-10:00" class="time-input" />
              <button type="button" @click="removeSchedule(index)" class="btn-remove" v-if="newClass.schedules.length > 1">×</button>
            </div>
            <button type="button" @click="addSchedule" class="btn-add-sched">+ 添加时间段</button>
          </div>
          <div class="modal-actions">
            <button type="button" class="btn-cancel" @click="showCreateModal = false">取消</button>
            <button type="submit" class="btn-submit">确认创建</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import Clock from '../../components/Clock.vue'
import { getDashboardOverview, getClassrooms, createClassroom, deleteClassroom } from '../../api'
import { useAuthStore } from '../../store/auth'

const auth = useAuthStore()
const showCreateModal = ref(false)
const isDeleteMode = ref(false)
const newClass = ref({
  name: '',
  description: '',
  schedules: [{ day: '周一', time: '08:00-10:00' }]
})

const addSchedule = () => {
  newClass.value.schedules.push({ day: '周一', time: '08:00-10:00' })
}

const removeSchedule = (index) => {
  newClass.value.schedules.splice(index, 1)
}

const dashboardData = ref({
  studentCount: 0,
  classCount: 0,
  questionBankCount: 0,
  practiceCount: 0,
  nextCourse: null,
  accuracy: 0
})

const classes = ref([])

onMounted(async () => {
  try {
    const [dashRes, classRes] = await Promise.all([
      getDashboardOverview(auth.user.value?.username),
      getClassrooms(auth.user.value?.username)
    ])
    dashboardData.value = dashRes.data || dashRes
    classes.value = classRes.data || classRes
  } catch (err) {
    console.error('获取仪表盘数据失败:', err)
  }
})

const submitCreateClass = async () => {
  try {
    // 将 schedules 转换为字符串
    const scheduleStr = newClass.value.schedules
      .map(s => `${s.day} ${s.time}`)
      .join(', ')
    
    const payload = {
      name: newClass.value.name,
      description: newClass.value.description,
      schedule: scheduleStr
    }
    
    const res = await createClassroom(payload)
    if (res.code === 200) {
      classes.value.unshift(res.data)
      showCreateModal.value = false
      newClass.value = { name: '', description: '', schedules: [{ day: '周一', time: '08:00-10:00' }] }
      alert('班级创建成功！')
      // 刷新概览数据
      const dashRes = await getDashboardOverview(auth.user.value?.username)
      dashboardData.value = dashRes.data || dashRes
    }
  } catch (err) {
    alert('创建失败: ' + err.message)
  }
}

const handleDeleteClass = async (id, name) => {
  if (!confirm(`确定要删除班级 "${name}" 吗？此操作将删除该班级的所有签到记录、公告和互动数据，且不可恢复！`)) {
    return
  }

  try {
    const res = await deleteClassroom(id)
    if (res.code === 200) {
      // 刷新列表
      const classRes = await getClassrooms(auth.user.value?.username)
      classes.value = classRes.data || classRes
      
      // 更新仪表盘统计
      const dashRes = await getDashboardOverview(auth.user.value?.username)
      dashboardData.value = dashRes.data || dashRes
      
      alert('班级已成功删除')
    } else {
      alert(res.msg || '删除失败')
    }
  } catch (err) {
    console.error('删除班级失败:', err)
    alert('删除班级失败，请重试')
  }
}
</script>

<style scoped>
.teacher-dashboard {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.dashboard-header h2 {
  margin: 0 0 0.5rem 0;
  color: #2c3e50;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
}

.stat-card {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.05);
  text-align: center;
}

.stat-card h3 {
  margin: 0;
  font-size: 1rem;
  color: #7f8c8d;
}

.stat-card .value {
  font-size: 2.5rem;
  font-weight: bold;
  color: #42b983;
  margin: 0.5rem 0;
}

.stat-card p {
  margin: 0;
  font-size: 0.85rem;
  color: #95a5a6;
}

.managed-classes {
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 16px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.btn-create {
  background: #42b983;
  color: white;
  border: none;
  padding: 0.6rem 1.2rem;
  border-radius: 8px;
  cursor: pointer;
  font-weight: bold;
  transition: background 0.3s;
}

.btn-create:hover {
  background: #3aa876;
}

.btn-delete-toggle {
  padding: 0.6rem 1.2rem;
  background: #f0f2f5;
  color: #666;
  border: 1px solid #ddd;
  border-radius: 8px;
  cursor: pointer;
  font-weight: bold;
  transition: all 0.3s;
}

.btn-delete-toggle:hover {
  background: #e4e7ed;
}

.btn-delete-toggle.active {
  background: #ff4d4f;
  color: white;
  border-color: #ff4d4f;
  box-shadow: 0 0 8px rgba(255, 77, 79, 0.4);
}

.class-grid.delete-mode-active .class-card-item {
  animation: shake 0.3s infinite ease-in-out;
  border: 1px dashed #ff4d4f;
}

@keyframes shake {
  0% { transform: rotate(0.5deg); }
  50% { transform: rotate(-0.5deg); }
  100% { transform: rotate(0.5deg); }
}

.class-card-item {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  position: relative;
  transition: all 0.3s;
}

.btn-delete-card {
  position: absolute;
  top: -12px;
  right: -12px;
  width: 28px;
  height: 28px;
  background: #ff4d4f;
  color: white;
  border: 2px solid white;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 6px rgba(0,0,0,0.15);
  z-index: 10;
  transition: all 0.2s;
}

.btn-delete-card:hover {
  background: #cf1322;
  transform: scale(1.2);
}

.class-info h4 {
  margin: 0 0 0.5rem 0;
  color: #2c3e50;
}

.description {
  font-size: 0.85rem;
  color: #7f8c8d;
  margin-bottom: 1rem;
}

.class-stats {
  display: flex;
  gap: 1rem;
  font-size: 0.8rem;
  color: #95a5a6;
}

.class-actions {
  margin-top: 1.5rem;
  display: flex;
  gap: 1rem;
}

.btn-link, .btn-enter {
  flex: 1;
  text-align: center;
  padding: 0.5rem;
  border-radius: 6px;
  text-decoration: none;
  font-size: 0.9rem;
  transition: all 0.3s;
}

.btn-link {
  background: #f0f2f5;
  color: #606266;
}

.btn-enter {
  background: #42b983;
  color: white;
}

.btn-enter:hover {
  background: #3aa876;
}

/* 弹窗样式 */
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
  border-radius: 12px;
  width: 100%;
  max-width: 450px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.1);
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: bold;
  color: #2c3e50;
}

.form-group input, .form-group textarea {
  width: 100%;
  padding: 0.8rem;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  outline: none;
}

.form-group input:focus, .form-group textarea:focus {
  border-color: #42b983;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 2rem;
}

.btn-cancel {
  background: #f5f7fa;
  border: 1px solid #dcdfe6;
  padding: 0.6rem 1.2rem;
  border-radius: 6px;
  cursor: pointer;
}

.btn-submit {
  background: #42b983;
  color: white;
  border: none;
  padding: 0.6rem 1.2rem;
  border-radius: 6px;
  cursor: pointer;
  font-weight: bold;
}
</style>


<style scoped>
.teacher-dashboard {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.dashboard-header h2 {
  margin: 0 0 0.5rem 0;
  color: #2c3e50;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
}

.stat-card {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.05);
  text-align: center;
}

.stat-card.next-course {
  border-left: 4px solid #42b983;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.next-course-info {
  margin: 0.5rem 0;
}

.course-name {
  font-size: 1.2rem;
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 0.3rem;
}

.course-time {
  font-size: 1rem;
  color: #42b983;
  font-weight: 600;
}

.stat-card h3 {
  margin: 0;
  font-size: 1rem;
  color: #666;
}

.stat-card .value {
  font-size: 2.5rem;
  font-weight: bold;
  color: #42b983;
  margin: 1rem 0;
}

.stat-card p {
  margin: 0;
  font-size: 0.85rem;
  color: #999;
}

.schedule-row {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.day-select {
  width: 80px;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.time-input {
  flex: 1;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.btn-remove {
  background: #ff4d4f;
  color: white;
  border: none;
  border-radius: 4px;
  width: 30px;
  cursor: pointer;
}

.btn-add-sched {
  background: none;
  border: 1px dashed #42b983;
  color: #42b983;
  padding: 0.5rem;
  width: 100%;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 0.5rem;
}

.btn-add-sched:hover {
  background: #f0f9eb;
}

.managed-classes {
  margin-top: 1rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.btn-create {
  padding: 0.6rem 1.2rem;
  background: #42b983;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: bold;
}

.class-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.class-card-item {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.05);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  position: relative;
  transition: transform 0.3s;
}

.btn-delete-card {
  position: absolute;
  top: -10px;
  right: -10px;
  width: 24px;
  height: 24px;
  background: #ff4d4f;
  color: white;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.2);
  z-index: 10;
}

.btn-delete-card:hover {
  background: #ff7875;
  transform: scale(1.1);
}

.class-card-item:hover {
  transform: translateY(-5px);
}

.class-info h4 {
  margin: 0 0 0.5rem 0;
  font-size: 1.2rem;
  color: #2c3e50;
}

.semester {
  font-size: 0.85rem;
  color: #999;
  margin-bottom: 1rem;
}

.class-stats {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  font-size: 0.9rem;
  color: #666;
}

.class-actions {
  margin-top: 1.5rem;
  display: flex;
  gap: 1rem;
}

.btn-link {
  flex: 1;
  text-align: center;
  padding: 0.6rem;
  background: #f0f2f5;
  color: #666;
  text-decoration: none;
  border-radius: 6px;
  font-size: 0.9rem;
}

.btn-enter {
  flex: 1;
  text-align: center;
  padding: 0.6rem;
  background: #42b983;
  color: white;
  text-decoration: none;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: bold;
}

.activity-list {
  margin-top: 1rem;
}

.activity-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 0;
  border-bottom: 1px solid #eee;
}

.activity-item:last-child {
  border-bottom: none;
}

.activity-info h4 {
  margin: 0 0 0.25rem 0;
}

.activity-info span {
  font-size: 0.85rem;
  color: #666;
}

.btn-secondary {
  padding: 0.5rem 1rem;
  background: #f0f2f5;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.3s;
}

.btn-secondary:hover {
  background: #e4e7ed;
}
</style>
