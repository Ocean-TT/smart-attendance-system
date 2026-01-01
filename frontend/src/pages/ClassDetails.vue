<template>
  <Layout>
    <div class="class-details-container">
      <header class="details-header">
        <div class="title-section">
          <button @click="router.back()" class="btn-back">← 返回</button>
          <h2>{{ classInfo.name }} <span class="tag">{{ classInfo.semester }}</span></h2>
        </div>
        <div class="header-actions">
          <router-link :to="'/classroom/' + route.params.id" class="btn-enter-now">立即进入课堂</router-link>
        </div>
      </header>

      <div class="details-grid">
        <!-- 左侧：基本信息与统计 -->
        <div class="left-column">
          <section class="info-card">
            <div class="section-header">
              <h3>班级概况</h3>
            </div>
            <div class="info-grid">
              <div class="info-item">
                <span class="label">学生总数</span>
                <span class="value">{{ students.length }} 人</span>
              </div>
              <div class="info-item">
                <span class="label">平均出勤率</span>
                <span class="value highlight">{{ classInfo.avgAttendance || '0%' }}</span>
              </div>
              <div class="info-item full-width">
                <span class="label">上课时间</span>
                <div class="schedule-manager">
                  <template v-if="isTeacher">
                    <div v-for="(sched, index) in schedules" :key="index" class="schedule-row">
                      <select v-model="sched.day" @change="handleUpdateSchedule" class="select-day">
                        <option v-for="d in ['周一', '周二', '周三', '周四', '周五', '周六', '周日']" :key="d" :value="d">{{ d }}</option>
                      </select>
                      <div class="time-inputs">
                        <input type="time" v-model="sched.start" @change="handleUpdateSchedule" class="input-time" />
                        <span class="separator">-</span>
                        <input type="time" v-model="sched.end" @change="handleUpdateSchedule" class="input-time" />
                      </div>
                      <button v-if="schedules.length > 1" @click="removeSchedule(index)" class="btn-remove-sched" title="移除时段">×</button>
                    </div>
                    <button @click="addSchedule" class="btn-add-sched-inline">+ 添加上课时段</button>
                  </template>
                  <div v-else class="schedule-display">
                    <span v-for="(s, i) in schedules" :key="i" class="schedule-tag">{{ s.day }} {{ s.start }}-{{ s.end }}</span>
                  </div>
                </div>
              </div>
              <div class="info-item">
                <span class="label">课程代码</span>
                <span class="value">{{ classInfo.courseCode || 'N/A' }}</span>
              </div>
            </div>
          </section>

          <section class="student-list-section">
            <div class="section-header">
              <h3>学生花名册</h3>
              <div v-if="isTeacher" class="list-actions">
                <button @click="showImport = true" class="btn-secondary">批量导入</button>
                <button @click="showAddStudent = true" class="btn-primary">添加学生</button>
              </div>
            </div>

            <div v-if="showImport" class="import-box">
              <p>请选择 CSV 文件导入学生名单</p>
              <input type="file" accept=".csv" />
              <div class="box-actions">
                <button @click="handleImport" class="btn-confirm">开始上传</button>
                <button @click="showImport = false" class="btn-cancel">取消</button>
              </div>
            </div>

            <div v-if="showAddStudent" class="import-box">
              <p>请输入学生学号</p>
              <input v-model="newStudentId" type="text" placeholder="例如: 2023001" class="input-text" />
              <div class="box-actions">
                <button @click="handleAddStudent" class="btn-confirm">确认添加</button>
                <button @click="showAddStudent = false" class="btn-cancel">取消</button>
              </div>
            </div>

            <table class="student-table">
              <thead>
                <tr>
                  <th>学号</th>
                  <th>姓名</th>
                  <th>出勤次数</th>
                  <th>表现评分</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="s in paginatedStudents" :key="s.id">
                  <td>{{ s.student_id || s.id }}</td>
                  <td>{{ s.name }}</td>
                  <td>{{ s.attendanceCount || 0 }} / {{ s.totalSessions || 0 }}</td>
                  <td>
                    <span class="rating-tag">{{ s.rating || '-' }}</span>
                  </td>
                  <td>
                    <button @click="handleViewStudentRecords(s.student_id || s.id)" class="btn-text">查看记录</button>
                    <button v-if="isTeacher" @click="handleRemoveStudent(s.student_id || s.id)" class="btn-text delete">移除</button>
                  </td>
                </tr>
              </tbody>
            </table>

            <!-- 学生列表分页 -->
            <div v-if="students.length > studentPageSize" class="pagination">
              <button :disabled="studentPage === 1" @click="studentPage--" class="btn-page">上一页</button>
              <span class="page-info">{{ studentPage }} / {{ Math.ceil(students.length / studentPageSize) }}</span>
              <button :disabled="studentPage >= Math.ceil(students.length / studentPageSize)" @click="studentPage++" class="btn-page">下一页</button>
            </div>
          </section>
        </div>

        <!-- 右侧：最近公告与动态 -->
        <aside class="right-column">
          <section class="announcement-card">
            <h3>班级公告</h3>
            <div class="announcement-list">
              <div v-if="announcements.length === 0" class="empty-state">暂无公告</div>
              <div v-for="ann in paginatedAnnouncements" :key="ann.id" class="announcement-item">
                <div class="ann-header">
                  <span class="date">{{ ann.date }}</span>
                  <button v-if="isTeacher" @click="handleDeleteAnnouncement(ann.id)" class="btn-delete-ann" title="删除公告">×</button>
                </div>
                <p class="content">{{ ann.content }}</p>
              </div>
            </div>

            <!-- 公告分页 -->
            <div v-if="announcements.length > annPageSize" class="pagination mini">
              <button :disabled="annPage === 1" @click="annPage--" class="btn-page">上一页</button>
              <span class="page-info">{{ annPage }} / {{ Math.ceil(announcements.length / annPageSize) }}</span>
              <button :disabled="annPage >= Math.ceil(announcements.length / annPageSize)" @click="annPage++" class="btn-page">下一页</button>
            </div>

            <button v-if="isTeacher" @click="showAddAnnouncement = true" class="btn-outline">发布新公告</button>
          </section>

          <section class="recent-records">
            <h3>最近课堂记录</h3>
            <div class="record-list">
              <div v-if="records.length === 0" class="empty-state">暂无课堂记录</div>
              <div v-for="record in records" :key="record.id" class="record-item">
                <div class="record-info">
                  <span class="date">{{ record.date }}</span>
                  <span class="type">{{ record.type }}</span>
                </div>
                <span class="stat">出勤: {{ record.attendance }}</span>
              </div>
            </div>
          </section>
        </aside>
      </div>

      <!-- 发布公告弹窗 -->
      <div v-if="showAddAnnouncement" class="modal-overlay">
        <div class="modal-content">
          <h3>发布新公告</h3>
          <div class="form-group">
            <label>公告内容</label>
            <textarea v-model="newAnnouncement" placeholder="请输入公告内容..." class="input-textarea"></textarea>
          </div>
          <div class="modal-actions">
            <button @click="handlePublishAnnouncement" class="btn-confirm">立即发布</button>
            <button @click="showAddAnnouncement = false" class="btn-cancel">取消</button>
          </div>
        </div>
      </div>
    </div>
  </Layout>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Layout from '../components/Layout.vue'
import { useAuthStore } from '../store/auth'
import { 
  getClassroomDetails, 
  getClassroomStudents, 
  addStudentToClass, 
  updateClassroom, 
  getAnnouncements, 
  createAnnouncement,
  deleteAnnouncement,
  removeStudentFromClass
} from '../api'

const route = useRoute()
const router = useRouter()
const { user } = useAuthStore()
const isTeacher = computed(() => user.value?.role === 'TEACHER')

const showImport = ref(false)
const showAddStudent = ref(false)
const showAddAnnouncement = ref(false)
const newStudentId = ref('')
const newAnnouncement = ref('')

const scheduleDay = ref('周一')
const scheduleStart = ref('08:00')
const scheduleEnd = ref('10:00')

const schedules = ref([{ day: '周一', start: '08:00', end: '10:00' }])

const addSchedule = () => {
  schedules.value.push({ day: '周一', start: '08:00', end: '10:00' })
}

const removeSchedule = (index) => {
  schedules.value.splice(index, 1)
  handleUpdateSchedule()
}

const classInfo = ref({
  name: '加载中...',
  semester: '2025春季',
  schedule: ''
})

const students = ref([])
const announcements = ref([])
const records = ref([])

// 分页逻辑
const studentPage = ref(1)
const studentPageSize = 10
const paginatedStudents = computed(() => {
  const start = (studentPage.value - 1) * studentPageSize
  return students.value.slice(start, start + studentPageSize)
})

const annPage = ref(1)
const annPageSize = 5
const paginatedAnnouncements = computed(() => {
  const start = (annPage.value - 1) * annPageSize
  return announcements.value.slice(start, start + annPageSize)
})

const fetchStudents = async () => {
  const classId = route.params.id
  try {
    const studentRes = await getClassroomStudents(classId)
    if (studentRes.code === 200) {
      students.value = studentRes.data
    }
  } catch (err) {
    console.error('获取学生列表失败:', err)
  }
}

const fetchAnnouncements = async () => {
  const classId = route.params.id
  try {
    const res = await getAnnouncements(classId)
    if (res.code === 200) {
      announcements.value = res.data
    }
  } catch (err) {
    console.error('获取公告失败:', err)
  }
}

onMounted(async () => {
  const classId = route.params.id
  try {
    const detailRes = await getClassroomDetails(classId)
    
    if (detailRes.code === 200) {
      classInfo.value = { ...classInfo.value, ...detailRes.data }
      // 解析上课时间
      if (classInfo.value.schedule) {
        const parts = classInfo.value.schedule.replace('，', ',').split(',')
        const parsedSchedules = []
        parts.forEach(p => {
          const s = p.trim()
          const subParts = s.split(' ')
          if (subParts.length >= 2) {
            const day = subParts[0]
            const times = subParts[1].split('-')
            if (times.length >= 2) {
              parsedSchedules.push({ day, start: times[0], end: times[1] })
            }
          }
        })
        if (parsedSchedules.length > 0) {
          schedules.value = parsedSchedules
        }
      }
    }
    
    await Promise.all([
      fetchStudents(),
      fetchAnnouncements()
    ])
  } catch (err) {
    console.error('获取班级详情失败:', err)
  }
})

const handleUpdateSchedule = async () => {
  const newSchedule = schedules.value
    .map(s => `${s.day} ${s.start}-${s.end}`)
    .join(', ')
    
  try {
    const res = await updateClassroom(route.params.id, {
      name: classInfo.value.name,
      schedule: newSchedule
    })
    if (res.code === 200) {
      classInfo.value.schedule = newSchedule
    }
  } catch (err) {
    console.error('更新失败', err)
  }
}

const handlePublishAnnouncement = async () => {
  if (!newAnnouncement.value) return
  try {
    const res = await createAnnouncement(route.params.id, newAnnouncement.value)
    if (res.code === 200) {
      announcements.value.unshift(res.data)
      newAnnouncement.value = ''
      showAddAnnouncement.value = false
      alert('发布成功')
    }
  } catch (err) {
    alert('发布失败: ' + err.message)
  }
}

const handleDeleteAnnouncement = async (annId) => {
  if (!confirm('确定要删除这条公告吗？')) return
  try {
    const res = await deleteAnnouncement(annId)
    if (res.code === 200) {
      announcements.value = announcements.value.filter(a => a.id !== annId)
    }
  } catch (err) {
    alert('删除失败: ' + err.message)
  }
}

const handleImport = () => {
  alert('模拟导入成功！')
  showImport.value = false
}

const handleAddStudent = async () => {
  if (!newStudentId.value) {
    alert('请输入学号')
    return
  }
  
  try {
    const res = await addStudentToClass(route.params.id, newStudentId.value)
    if (res.code === 200) {
      alert('添加成功')
      showAddStudent.value = false
      newStudentId.value = ''
      await fetchStudents()
    } else {
      alert(res.message || '添加失败')
    }
  } catch (err) {
    alert(err.message || '添加失败')
  }
}

const handleRemoveStudent = async (studentId) => {
  if (!confirm(`确定要将学生(学号:${studentId})从本班级移除吗？`)) return
  try {
    const res = await removeStudentFromClass(route.params.id, studentId)
    if (res.code === 200) {
      alert('移除成功')
      await fetchStudents()
    }
  } catch (err) {
    alert('移除失败: ' + err.message)
  }
}

const handleViewStudentRecords = (studentId) => {
  // 跳转到统计分析页面，并带上学生 ID 参数
  router.push({
    path: '/stats',
    query: { studentId: studentId, classId: route.params.id }
  })
}
</script>

<style scoped>
.class-details-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.details-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  padding: 1.5rem 2rem;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.05);
}

.title-section {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.btn-back {
  background: none;
  border: none;
  color: #666;
  cursor: pointer;
  font-size: 1rem;
}

.tag {
  font-size: 0.9rem;
  background: #e8f5e9;
  color: #42b983;
  padding: 2px 8px;
  border-radius: 4px;
  margin-left: 0.5rem;
}

.btn-enter-now {
  background: #42b983;
  color: white;
  text-decoration: none;
  padding: 0.8rem 1.5rem;
  border-radius: 8px;
  font-weight: bold;
  transition: background 0.3s;
}

.btn-edit-small {
  background: #f0f2f5;
  border: none;
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 0.8rem;
  color: #666;
  cursor: pointer;
}

.btn-edit-small:hover {
  background: #e4e7ed;
}

.input-textarea {
  width: 100%;
  height: 120px;
  padding: 0.8rem;
  border: 1px solid #ddd;
  border-radius: 8px;
  resize: vertical;
  outline: none;
}

.empty-state {
  padding: 2rem;
  text-align: center;
  color: #999;
  font-size: 0.9rem;
  background: #f9f9f9;
  border-radius: 8px;
  margin: 1rem 0;
}

.details-grid {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 1.5rem;
}

.left-column, .right-column {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

section {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.05);
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
  margin-top: 1rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.info-item .label { color: #999; font-size: 0.9rem; }
.info-item .value { font-weight: bold; color: #2c3e50; }
.info-item .highlight { color: #42b983; font-size: 1.2rem; }

.info-item.full-width {
  grid-column: span 2;
}

.schedule-manager {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 8px;
  border: 1px solid #edf2f7;
}

.schedule-row {
  display: flex;
  align-items: center;
  gap: 0.8rem;
}

.select-day {
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  background: white;
  font-size: 0.9rem;
}

.time-inputs {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: white;
  padding: 2px 8px;
  border: 1px solid #ddd;
  border-radius: 6px;
}

.input-time {
  border: none;
  padding: 0.4rem;
  font-size: 0.9rem;
  outline: none;
}

.separator { color: #cbd5e0; }

.btn-remove-sched {
  background: #fff5f5;
  color: #e53e3e;
  border: 1px solid #feb2b2;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 1.2rem;
  transition: all 0.2s;
}

.btn-remove-sched:hover {
  background: #e53e3e;
  color: white;
}

.btn-add-sched-inline {
  background: white;
  border: 1px dashed #42b983;
  color: #42b983;
  padding: 0.6rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-add-sched-inline:hover {
  background: #f0f9eb;
  border-style: solid;
}

.schedule-display {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.schedule-tag {
  background: #e6fffa;
  color: #2c7a7b;
  border: 1px solid #b2f5ea;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.list-actions { display: flex; gap: 0.5rem; }

.btn-primary { background: #42b983; color: white; border: none; padding: 0.5rem 1rem; border-radius: 6px; cursor: pointer; }
.btn-secondary { background: #f0f2f5; color: #666; border: none; padding: 0.5rem 1rem; border-radius: 6px; cursor: pointer; }

.student-table {
  width: 100%;
  border-collapse: collapse;
}

.student-table th {
  text-align: left;
  padding: 1rem;
  border-bottom: 2px solid #f0f2f5;
  color: #666;
  font-size: 0.9rem;
}

.student-table td {
  padding: 1rem;
  border-bottom: 1px solid #f0f2f5;
  font-size: 0.9rem;
}

.rating-tag {
  background: #fff7e6;
  color: #faad14;
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: bold;
}

.btn-text {
  background: none;
  border: none;
  color: #3498db;
  cursor: pointer;
  margin-right: 10px;
}

.btn-text.delete { color: #e74c3c; }

.announcement-list, .record-list {
  margin: 1rem 0;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.announcement-item, .record-item {
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
}

.announcement-item .content { margin: 0 0 0.5rem 0; font-size: 0.9rem; }
.announcement-item .date, .record-info .date { font-size: 0.8rem; color: #999; }

.ann-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.btn-delete-ann {
  background: none;
  border: none;
  color: #ccc;
  font-size: 1.2rem;
  cursor: pointer;
  line-height: 1;
  padding: 0 4px;
  transition: color 0.2s;
}

.btn-delete-ann:hover {
  color: #ff4d4f;
}

.record-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.record-info { display: flex; flex-direction: column; }
.record-info .type { font-size: 0.9rem; font-weight: bold; }
.record-item .stat { font-size: 0.85rem; color: #42b983; }

.btn-outline {
  width: 100%;
  padding: 0.6rem;
  background: none;
  border: 1px dashed #ddd;
  border-radius: 6px;
  color: #999;
  cursor: pointer;
}

.import-box {
  background: #f0f7ff;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1rem;
  border: 1px solid #bae7ff;
}

.box-actions {
  margin-top: 10px;
  display: flex;
  gap: 10px;
}

.btn-confirm { background: #1890ff; color: white; border: none; padding: 5px 15px; border-radius: 4px; cursor: pointer; }
.btn-cancel { background: #ccc; color: white; border: none; padding: 5px 15px; border-radius: 4px; cursor: pointer; }

.input-text {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  margin-bottom: 10px;
}

/* 分页样式 */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid #f0f2f5;
}

.pagination.mini {
  margin-top: 0.5rem;
  margin-bottom: 1rem;
  padding-top: 0.5rem;
  font-size: 0.85rem;
}

.btn-page {
  padding: 4px 12px;
  border: 1px solid #ddd;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  color: #666;
}

.btn-page:disabled {
  background: #f5f5f5;
  color: #ccc;
  cursor: not-allowed;
}

.btn-page:not(:disabled):hover {
  border-color: #42b983;
  color: #42b983;
}

.page-info {
  color: #999;
  font-weight: 500;
}

.select-inline {
  padding: 4px 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.9rem;
  color: #333;
  background: #f9f9f9;
  cursor: pointer;
}

.schedule-picker {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.select-day {
  padding: 4px 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.9rem;
  background: #f9f9f9;
}

.input-time {
  padding: 3px 6px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.9rem;
  font-family: inherit;
}

.separator {
  color: #999;
}

.select-inline:focus, .select-day:focus, .input-time:focus {
  outline: none;
  border-color: #42b983;
}

/* 弹窗样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  width: 400px;
  max-width: 90%;
  box-shadow: 0 4px 20px rgba(0,0,0,0.15);
}

.modal-content h3 {
  margin-top: 0;
  margin-bottom: 1.5rem;
  color: #2c3e50;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #666;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 2rem;
}

.btn-confirm {
  background: #42b983;
  color: white;
  border: none;
  padding: 0.6rem 1.5rem;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
}

.btn-cancel {
  background: #f0f2f5;
  color: #666;
  border: none;
  padding: 0.6rem 1.5rem;
  border-radius: 6px;
  cursor: pointer;
}

.btn-confirm:hover { background: #369b6d; }
.btn-cancel:hover { background: #e4e7ed; }
</style>
