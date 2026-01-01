<template>
  <div class="student-stats">
    <div class="stats-summary">
      <div class="summary-item">
        <span class="val">{{ stats.attendanceCount }}</span>
        <span class="lab">本学期出勤</span>
      </div>
      <div class="summary-item">
        <span class="val">{{ stats.totalPoints }}</span>
        <span class="lab">累计积分</span>
      </div>
      <div class="summary-item">
        <span class="val">{{ stats.accuracy }}</span>
        <span class="lab">练习正确率</span>
      </div>
    </div>

    <div class="detail-grid">
      <div class="card attendance-card">
        <h4>本月出勤日历</h4>
        <div class="calendar-container">
          <div class="calendar-weekdays">
            <span v-for="d in ['日', '一', '二', '三', '四', '五', '六']" :key="d">{{ d }}</span>
          </div>
          <div class="calendar-grid">
            <div v-for="empty in firstDayOffset" :key="'empty-'+empty" class="day-cell empty"></div>
            <div v-for="day in daysInMonth" :key="day" 
                 class="day-cell" 
                 :class="getDayStatus(day)"
                 @mouseenter="hoverDay = day"
                 @mouseleave="hoverDay = null">
              <span class="day-num">{{ day }}</span>
              
              <!-- 悬停卡片 -->
              <div v-if="hoverDay === day && getDayCourses(day).length > 0" class="day-tooltip">
                <div class="tooltip-header">{{ currentMonthStr }} {{ day }}日</div>
                <div v-for="(course, idx) in getDayCourses(day)" :key="idx" class="tooltip-item">
                  <span class="status-dot" :class="{ attended: course.attended }"></span>
                  <div class="course-info-mini">
                    <div class="c-name">{{ course.name }}</div>
                    <div class="c-meta">{{ course.time }} · {{ course.attended ? '已出勤' : '缺勤' }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="calendar-legend">
            <span><i class="dot green"></i> 全勤</span>
            <span><i class="dot red"></i> 缺勤</span>
            <span><i class="dot transparent"></i> 无课/待上</span>
          </div>
        </div>
      </div>

      <div class="card attendance-detail">
        <h4>出勤统计</h4>
        <div class="attendance-stats-list">
          <div class="stat-row">
            <span>应到次数</span>
            <span class="num">{{ stats.requiredCount }}</span>
          </div>
          <div class="stat-row">
            <span>实到次数</span>
            <span class="num green">{{ stats.attendanceCount }}</span>
          </div>
          <div class="stat-row">
            <span>缺勤次数</span>
            <span class="num red">{{ stats.absentCount }}</span>
          </div>
          <div class="attendance-rate-box">
            <div class="rate-circle">
              <span class="rate-val">{{ stats.attendanceRate }}</span>
              <span class="rate-lab">出勤率</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="history-table">
      <h4>最近表现记录</h4>
      <table>
        <thead>
          <tr>
            <th>日期</th>
            <th>课程</th>
            <th>互动得分</th>
            <th>状态</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(item, index) in stats.history" :key="index">
            <td>{{ item.date }}</td>
            <td>{{ item.event }}</td>
            <td>+{{ item.points }}</td>
            <td><span class="tag-success">正常</span></td>
          </tr>
          <tr v-if="!stats.history || stats.history.length === 0">
            <td colspan="4" style="text-align: center; color: #999;">暂无记录</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useAuthStore } from '../../store/auth'
import { getStudentStats } from '../../api'

const props = defineProps({
  studentId: {
    type: String,
    default: ''
  }
})

const { user } = useAuthStore()
const stats = ref({
  attendanceCount: 0,
  totalPoints: 0,
  accuracy: '0%',
  requiredCount: 0,
  absentCount: 0,
  attendanceRate: '0%',
  history: [],
  calendarData: {}
})

// 日历相关逻辑
const now = new Date()
const daysInMonth = new Date(now.getFullYear(), now.getMonth() + 1, 0).getDate()
const firstDayOffset = new Date(now.getFullYear(), now.getMonth(), 1).getDay()
const hoverDay = ref(null)
const currentMonthStr = `${now.getFullYear()}年${now.getMonth() + 1}月`

const getDayStatus = (day) => {
  const dateStr = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`
  const dayData = stats.value.calendarData?.[dateStr]
  return dayData ? dayData.status : ''
}

const getDayCourses = (day) => {
  const dateStr = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`
  return stats.value.calendarData?.[dateStr]?.courses || []
}

const fetchData = async () => {
  try {
    // 优先使用 props 传进来的 ID，否则使用当前登录用户的 ID
    const targetId = props.studentId || user.value?.studentId || '20230001'
    const res = await getStudentStats(targetId)
    const data = res.data || res
    
    stats.value = {
      ...stats.value,
      ...data
    }
  } catch (err) {
    console.error('获取学生统计失败:', err)
  }
}

onMounted(fetchData)

// 监听 ID 变化（用于老师切换查看不同学生）
watch(() => props.studentId, fetchData)
</script>

<style scoped>
.student-stats { display: flex; flex-direction: column; gap: 2rem; }
.stats-summary { display: flex; background: #34495e; color: white; padding: 1.5rem; border-radius: 16px; justify-content: space-around; }
.summary-item { text-align: center; }
.summary-item .val { display: block; font-size: 1.8rem; font-weight: bold; margin-bottom: 0.3rem; }
.summary-item .lab { font-size: 0.85rem; opacity: 0.8; }

.detail-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; }
.card { background: white; padding: 1.2rem; border-radius: 12px; box-shadow: 0 2px 12px rgba(0,0,0,0.05); }
.card h4 { margin-top: 0; margin-bottom: 1.2rem; }

/* 日历样式 */
.calendar-container {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-width: 400px;
  margin: 0 auto;
}

.calendar-weekdays {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  text-align: center;
  font-size: 0.75rem;
  color: #999;
  margin-bottom: 0.4rem;
}

.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 6px;
}

.day-cell {
  aspect-ratio: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  background: transparent;
  border: 1px solid #f0f0f0;
  font-size: 0.85rem;
  color: #999;
  position: relative;
  cursor: default;
  transition: all 0.2s;
}

.day-cell.empty {
  border: none;
  background: transparent;
}

.day-cell.blue {
  background: #e3f2fd;
  color: #1976d2;
  border-color: #bbdefb;
  font-weight: bold;
}

.day-cell.green {
  background: #e8f5e9;
  color: #2e7d32;
  border-color: #c8e6c9;
  font-weight: bold;
}

.day-cell.red {
  background: #ffebee;
  color: #c62828;
  border-color: #ffcdd2;
  font-weight: bold;
}

.day-cell:not(.empty):hover {
  transform: scale(1.05);
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  z-index: 10;
}

.day-num {
  z-index: 1;
}

/* 悬停提示卡片 */
.day-tooltip {
  position: absolute;
  bottom: 120%;
  left: 50%;
  transform: translateX(-50%);
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.15);
  padding: 1rem;
  width: 200px;
  z-index: 100;
  pointer-events: none;
}

.day-tooltip::after {
  content: '';
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  border: 8px solid transparent;
  border-top-color: white;
}

.tooltip-header {
  font-size: 0.8rem;
  color: #999;
  margin-bottom: 0.8rem;
  border-bottom: 1px solid #eee;
  padding-bottom: 0.4rem;
}

.tooltip-item {
  display: flex;
  align-items: flex-start;
  gap: 0.8rem;
  margin-bottom: 0.8rem;
}

.tooltip-item:last-child { margin-bottom: 0; }

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #ff5252;
  margin-top: 5px;
  flex-shrink: 0;
}

.status-dot.attended {
  background: #42b983;
}

.course-info-mini {
  flex: 1;
}

.c-name {
  font-size: 0.85rem;
  font-weight: bold;
  color: #2c3e50;
  line-height: 1.2;
}

.c-meta {
  font-size: 0.75rem;
  color: #666;
  margin-top: 2px;
}

.calendar-legend {
  display: flex;
  justify-content: center;
  gap: 1.2rem;
  margin-top: 1rem;
  font-size: 0.75rem;
  color: #666;
}

.calendar-legend .dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 2px;
  margin-right: 4px;
}

.calendar-legend .green { background: #e8f5e9; border: 1px solid #2e7d32; }
.calendar-legend .red { background: #ffebee; border: 1px solid #c62828; }
.calendar-legend .transparent { background: transparent; border: 1px solid #f0f0f0; }

.attendance-stats-list { display: flex; flex-direction: column; gap: 1rem; }
.stat-row { display: flex; justify-content: space-between; font-size: 0.9rem; color: #666; }
.stat-row .num { font-weight: bold; color: #333; }
.stat-row .num.green { color: #42b983; }
.stat-row .num.red { color: #e74c3c; }

.attendance-rate-box { margin-top: 1rem; display: flex; justify-content: center; }
.rate-circle { width: 100px; height: 100px; border: 6px solid #f0f2f5; border-top-color: #3498db; border-radius: 50%; display: flex; flex-direction: column; align-items: center; justify-content: center; }
.rate-val { font-size: 1.2rem; font-weight: bold; color: #3498db; }
.rate-lab { font-size: 0.7rem; color: #999; }

.history-table { background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 12px rgba(0,0,0,0.05); }
table { width: 100%; border-collapse: collapse; margin-top: 1rem; }
th { text-align: left; color: #999; font-size: 0.85rem; padding: 10px; border-bottom: 2px solid #f8f9fa; }
td { padding: 12px 10px; font-size: 0.9rem; border-bottom: 1px solid #f8f9fa; }
.tag-success { color: #42b983; background: #e8f5e9; padding: 2px 8px; border-radius: 4px; font-size: 0.8rem; }
</style>
