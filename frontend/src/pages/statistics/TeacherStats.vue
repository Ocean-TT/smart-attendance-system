<template>
  <div class="teacher-stats">
    <!-- 学生详情视图 -->
    <div v-if="selectedStudentId" class="student-detail-view">
      <div class="detail-header">
        <button @click="clearStudentFilter" class="btn-back">← 返回概览</button>
        <h3>学生详情: {{ selectedStudentId }}</h3>
      </div>
      <StudentStats :student-id="selectedStudentId" />
    </div>

    <!-- 教师概览视图 -->
    <div v-else class="overview-content">
      <div class="filter-bar">
        <div class="class-selector">
          <label>选择班级：</label>
          <select v-model="selectedClassId" @change="fetchOverview">
            <option v-for="c in stats.classrooms" :key="c.id" :value="c.id">{{ c.name }}</option>
          </select>
        </div>
        <div class="search-box">
          <input v-model="searchQuery" type="text" placeholder="搜索学生姓名或学号..." />
        </div>
      </div>

      <div class="overview-grid">
        <div class="stat-card">
          <div class="card-icon blue">👥</div>
          <div class="card-info">
            <span class="label">平均出勤率</span>
            <span class="value">{{ stats.avgAttendance }}</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="card-icon green">📚</div>
          <div class="card-info">
            <span class="label">题库完成率</span>
            <span class="value">{{ stats.completionRate }}</span>
          </div>
        </div>
        <div class="stat-card has-tooltip">
          <div class="card-icon orange">⚡</div>
          <div class="card-info">
            <span class="label">学习活跃度</span>
            <span class="value">{{ stats.activityIndex }}</span>
          </div>
          <div class="tooltip">
            <p><strong>活跃度计算公式：</strong></p>
            <p>(出勤率 × 40%) + (题库完成率 × 40%) + (积分表现分 × 20%)</p>
            <p><small>* 积分表现分以50分为满分基准进行归一化</small></p>
          </div>
        </div>
      </div>

      <div class="charts-row">
        <div class="chart-box">
          <h4>最近课堂出勤详情</h4>
          <div class="session-list">
            <div v-for="sess in stats.recentSessions" :key="sess.id" class="session-item">
              <div class="sess-info">
                <span class="sess-name">{{ sess.className }}</span>
                <span class="sess-date">{{ sess.date }}</span>
              </div>
              <div class="sess-progress">
                <div class="progress-bar">
                  <div class="progress-fill" :style="{ width: sess.rate + '%' }"></div>
                </div>
                <span class="sess-count">{{ sess.attendedCount }}/{{ sess.totalCount }}</span>
              </div>
            </div>
            <div v-if="!stats.recentSessions?.length" class="no-data-mini">暂无课堂记录</div>
          </div>
        </div>
        <div class="chart-box has-tooltip">
          <h4>学生表现分布</h4>
          <div class="pie-chart-container">
            <div class="pie-chart-mock" :style="pieGradient"></div>
            <div class="pie-legend">
              <div class="legend-item">
                <span class="dot s1"></span>
                <span class="label">优秀</span>
                <span class="count">{{ distribution.excellent }}人</span>
                <span class="percent">{{ getPercent(distribution.excellent) }}%</span>
              </div>
              <div class="legend-item">
                <span class="dot s2"></span>
                <span class="label">良好</span>
                <span class="count">{{ distribution.good }}人</span>
                <span class="percent">{{ getPercent(distribution.good) }}%</span>
              </div>
              <div class="legend-item">
                <span class="dot s3"></span>
                <span class="label">待改进</span>
                <span class="count">{{ distribution.needsImprovement }}人</span>
                <span class="percent">{{ getPercent(distribution.needsImprovement) }}%</span>
              </div>
            </div>
          </div>
          <div class="tooltip">
            <p><strong>学生状态判定标准 (每周刷新)：</strong></p>
            <p>• <strong>优秀：</strong> 本周累计积分 ≥ 10分</p>
            <p>• <strong>良好：</strong> 本周累计积分 4 - 9分</p>
            <p>• <strong>待改进：</strong> 本周累计积分 < 4分</p>
            <p><small>* 积分包含本周签到、课堂提问及练习得分</small></p>
          </div>
        </div>
      </div>

      <div class="student-list-section">
        <div class="section-header">
          <h4>学生详细数据</h4>
          <span class="count">共 {{ filteredStudents.length }} 名学生</span>
        </div>
        <div class="table-container">
          <table>
            <thead>
              <tr>
                <th>学号</th>
                <th>姓名</th>
                <th>出勤率</th>
                <th>题库完成率</th>
                <th>本周积分</th>
                <th>累计总分</th>
                <th>状态</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="s in filteredStudents" :key="s.id">
                <td>{{ s.student_id }}</td>
                <td>{{ s.name }}</td>
                <td>
                  <div class="progress-mini">
                    <div class="progress-inner" :style="{ width: s.attendanceRate, background: getRateColor(s.attendanceRate) }"></div>
                    <span>{{ s.attendanceRate }}</span>
                  </div>
                </td>
                <td>
                  <div class="progress-mini">
                    <div class="progress-inner" :style="{ width: s.completionRate, background: '#42b983' }"></div>
                    <span>{{ s.completionRate }}</span>
                  </div>
                </td>
                <td class="points-cell" style="color: #42b983;">{{ s.weeklyPoints }}</td>
                <td class="points-cell">{{ s.points }}</td>
                <td>
                  <span class="status-tag" :class="s.status === '优秀' ? 'tag-green' : (s.status === '良好' ? 'tag-blue' : 'tag-red')">
                    {{ s.status }}
                  </span>
                </td>
                <td>
                  <button @click="viewStudentDetail(s.student_id)" class="btn-text">查看详情</button>
                </td>
              </tr>
              <tr v-if="filteredStudents.length === 0">
                <td colspan="8" class="empty-cell">未找到匹配的学生</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getTeacherOverview } from '../../api'
import StudentStats from './StudentStats.vue'

const route = useRoute()
const router = useRouter()

const selectedStudentId = computed(() => route.query.studentId)
const selectedClassId = ref(null)
const searchQuery = ref('')

const stats = ref({
  avgAttendance: '0%',
  completionRate: '0%',
  activityIndex: 0,
  recentSessions: [],
  studentList: [],
  classrooms: []
})

const fetchOverview = async () => {
  try {
    const res = await getTeacherOverview(selectedClassId.value)
    if (res.code === 200) {
      stats.value = res.data
      // 如果当前没有选中班级且有班级列表，默认选中第一个
      if (selectedClassId.value === null && res.data.classrooms && res.data.classrooms.length > 0) {
        selectedClassId.value = res.data.classrooms[0].id
      }
    }
  } catch (err) {
    console.error('获取概览数据失败:', err)
  }
}

const filteredStudents = computed(() => {
  if (!searchQuery.value) return stats.value.studentList || []
  const q = searchQuery.value.toLowerCase()
  return (stats.value.studentList || []).filter(s => 
    s.name.toLowerCase().includes(q) || s.student_id.includes(q)
  )
})

const distribution = computed(() => {
  const list = stats.value.studentList || []
  const excellent = list.filter(s => s.status === '优秀').length
  const good = list.filter(s => s.status === '良好').length
  const needsImprovement = list.filter(s => s.status === '待改进').length
  return { excellent, good, needsImprovement }
})

const pieGradient = computed(() => {
  const total = (stats.value.studentList || []).length || 1
  const p1 = (distribution.value.excellent / total) * 100
  const p2 = (distribution.value.good / total) * 100 + p1
  return {
    background: `conic-gradient(#42b983 0% ${p1}%, #3498db ${p1}% ${p2}%, #f1c40f ${p2}% 100%)`
  }
})

const getRateColor = (rateStr) => {
  const rate = parseInt(rateStr)
  if (rate >= 90) return '#42b983'
  if (rate >= 70) return '#3498db'
  return '#e74c3c'
}

const getPercent = (count) => {
  const total = (stats.value.studentList || []).length
  if (total === 0) return 0
  return Math.round((count / total) * 100)
}

const viewStudentDetail = (studentId) => {
  router.push({ path: '/stats', query: { studentId } })
}

const clearStudentFilter = () => {
  router.push({ path: '/stats' })
}

onMounted(fetchOverview)
</script>

<style scoped>
.teacher-stats { display: flex; flex-direction: column; gap: 1.5rem; padding: 1rem; }
.overview-content { display: flex; flex-direction: column; gap: 1.5rem; }

.detail-header {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  margin-bottom: 1rem;
}

.btn-back {
  background: #f0f2f5;
  border: none;
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
  color: #666;
}

.btn-back:hover {
  background: #e4e7ed;
}

.filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  padding: 1rem 1.5rem;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.class-selector select {
  padding: 6px 12px;
  border-radius: 6px;
  border: 1px solid #ddd;
  outline: none;
  min-width: 150px;
}

.search-box input {
  padding: 6px 12px;
  border-radius: 20px;
  border: 1px solid #ddd;
  width: 250px;
  outline: none;
}

.overview-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem; }
.stat-card { background: white; padding: 1.5rem; border-radius: 12px; display: flex; align-items: center; gap: 1.2rem; box-shadow: 0 2px 12px rgba(0,0,0,0.05); position: relative; }

.has-tooltip { cursor: help; }
.tooltip {
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  background: #2c3e50;
  color: white;
  padding: 12px;
  border-radius: 8px;
  font-size: 0.8rem;
  width: 280px;
  z-index: 100;
  opacity: 0;
  visibility: hidden;
  transition: all 0.3s;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  margin-top: 10px;
}

.tooltip::after {
  content: '';
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  border: 6px solid transparent;
  border-bottom-color: #2c3e50;
}

.has-tooltip:hover .tooltip {
  opacity: 1;
  visibility: visible;
  transform: translateX(-50%) translateY(0);
}

.tooltip p { margin: 4px 0; line-height: 1.4; }
.tooltip strong { color: #ffa940; }

.card-icon { font-size: 1.8rem; width: 54px; height: 54px; display: flex; align-items: center; justify-content: center; border-radius: 12px; }
.card-icon.blue { background: #eef6ff; color: #3498db; }
.card-icon.green { background: #f0f9eb; color: #67c23a; }
.card-icon.orange { background: #fff7e6; color: #ffa940; }

.card-info .label { font-size: 0.85rem; color: #999; margin-bottom: 4px; display: block; }
.card-info .value { font-size: 1.6rem; font-weight: bold; color: #2c3e50; }

.charts-row { display: grid; grid-template-columns: 1.5fr 1fr; gap: 1.5rem; }
.chart-box { background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 12px rgba(0,0,0,0.05); position: relative; }
.chart-box h4 { margin-top: 0; margin-bottom: 1.5rem; color: #2c3e50; font-size: 1.1rem; }

.session-list { display: flex; flex-direction: column; gap: 12px; height: 200px; overflow-y: auto; padding-right: 5px; }
.session-item { display: flex; flex-direction: column; gap: 6px; padding-bottom: 8px; border-bottom: 1px solid #f5f7fa; }
.sess-info { display: flex; justify-content: space-between; align-items: center; }
.sess-name { font-size: 0.9rem; font-weight: 500; color: #2c3e50; }
.sess-date { font-size: 0.75rem; color: #999; }
.sess-progress { display: flex; align-items: center; gap: 10px; }
.progress-bar { flex: 1; height: 8px; background: #f0f2f5; border-radius: 4px; overflow: hidden; }
.progress-fill { height: 100%; background: linear-gradient(90deg, #3498db, #5dade2); border-radius: 4px; }
.sess-count { font-size: 0.8rem; color: #666; min-width: 45px; text-align: right; }

.pie-chart-mock { width: 140px; height: 140px; border-radius: 50%; box-shadow: inset 0 0 0 30px white; flex-shrink: 0; }
.pie-chart-container { display: flex; align-items: center; gap: 20px; justify-content: center; height: 180px; }
.pie-legend { display: flex; flex-direction: column; gap: 0.8rem; font-size: 0.85rem; color: #666; flex: 1; }
.legend-item { display: flex; align-items: center; gap: 8px; }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; }
.dot.s1 { background: #42b983; }
.dot.s2 { background: #3498db; }
.dot.s3 { background: #f1c40f; }
.legend-item .label { min-width: 45px; color: #2c3e50; }
.legend-item .count { color: #999; min-width: 35px; }
.legend-item .percent { font-weight: bold; color: #2c3e50; margin-left: auto; }

.student-list-section { background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 12px rgba(0,0,0,0.05); }
.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; }
.section-header h4 { margin: 0; font-size: 1.1rem; }
.section-header .count { font-size: 0.85rem; color: #999; }

.table-container { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; }
th { text-align: left; padding: 12px; font-size: 0.85rem; color: #999; border-bottom: 1px solid #f0f0f0; font-weight: 500; }
td { padding: 14px 12px; font-size: 0.9rem; border-bottom: 1px solid #f5f7fa; color: #444; }

.progress-mini { display: flex; align-items: center; gap: 10px; width: 120px; }
.progress-inner { height: 6px; border-radius: 3px; }
.progress-mini span { font-size: 0.8rem; color: #666; min-width: 35px; }

.points-cell { font-weight: bold; color: #2c3e50; }

.status-tag { padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; }
.tag-green { background: #e8f5e9; color: #2e7d32; }
.tag-blue { background: #e3f2fd; color: #1976d2; }
.tag-red { background: #fff7e6; color: #d48806; }

.btn-text { background: none; border: none; color: #3498db; cursor: pointer; font-size: 0.85rem; padding: 0; }
.btn-text:hover { text-decoration: underline; }
.empty-cell { text-align: center; color: #999; padding: 3rem !important; }
.no-data-mini { color: #999; font-size: 0.8rem; padding: 2rem; }
</style>
