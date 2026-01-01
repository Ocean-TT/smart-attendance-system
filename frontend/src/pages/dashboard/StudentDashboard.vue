<template>
  <div class="student-dashboard">
    <header class="dashboard-header">
      <div class="header-left">
        <h2>学生工作台</h2>
        <p>你好，同学！今天也要加油学习哦。</p>
      </div>
      <Clock />
    </header>

    <!-- 正在上课提醒 -->
    <div v-if="activeClasses.length > 0" class="active-class-alert">
      <div class="alert-content">
        <span class="pulse-dot"></span>
        <div class="alert-text">
          <strong>正在上课：</strong>
          <span>{{ activeClasses[0].name }}</span>
        </div>
        <button class="btn-join-now" @click="enterClassroom(activeClasses[0].id)">立即进入</button>
      </div>
    </div>

    <div class="stats-grid">
      <div class="stat-card">
        <h3>出勤率</h3>
        <div class="value">{{ dashboardData?.accuracy || 0 }}%</div>
        <p>本学期表现优异</p>
      </div>
      <div class="stat-card">
        <h3>已修课程</h3>
        <div class="value">{{ dashboardData?.classCount || 0 }}</div>
        <p>当前正在学习</p>
      </div>
      <div class="stat-card">
        <h3>待完成练习</h3>
        <div class="value">{{ dashboardData?.practiceCount || 0 }}</div>
        <p>来自题库的挑战</p>
      </div>
      <div class="stat-card">
        <h3>我的积分</h3>
        <div class="value">{{ dashboardData?.totalPoints || 0 }}</div>
        <p>课堂表现奖励</p>
      </div>
    </div>

    <div class="dashboard-content">
      <section class="upcoming-classes">
        <h3>我的课程</h3>
        <div class="class-list">
          <div v-for="cls in classes" :key="cls.id" class="class-item active">
            <div class="time-tags">
              <span v-for="(s, i) in (cls.schedule || '').split(',')" :key="i" class="time-tag">
                {{ s.trim() }}
              </span>
            </div>
            <div class="info">
              <h4>{{ cls.name }}</h4>
              <p>{{ cls.description }}</p>
            </div>
            <button class="btn-primary" @click="enterClassroom(cls.id)">进入课堂</button>
          </div>
          <div v-if="classes.length === 0" class="no-data">暂无课程</div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import Clock from '../../components/Clock.vue'
import { getDashboardOverview, getClassrooms } from '../../api'
import { useAuthStore } from '../../store/auth'

const router = useRouter()
const auth = useAuthStore()
const dashboardData = ref(null)
const classes = ref([])
const activeClasses = ref([])
const errorMessage = ref('')

onMounted(async () => {
  try {
    const [dashRes, classRes] = await Promise.all([
      getDashboardOverview(auth.user.value?.username),
      getClassrooms(auth.user.value?.username)
    ])
    dashboardData.value = dashRes.data || dashRes
    classes.value = classRes.data || classRes
    
    // 提取正在上课的班级
    if (dashboardData.value?.activeClasses) {
      activeClasses.value = dashboardData.value.activeClasses
    }
    
    errorMessage.value = ''
  } catch (err) {
    errorMessage.value = err.message
    console.error('仪表盘数据加载失败:', err)
  }
})

const enterClassroom = (id) => {
  router.push('/classroom/' + id)
}
</script>

<style scoped>
.student-dashboard {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.dashboard-header h2 {
  margin: 0 0 0.5rem 0;
  color: #2c3e50;
}

.active-class-alert {
  background: #e8f5e9;
  border: 1px solid #42b983;
  border-radius: 12px;
  padding: 1rem 1.5rem;
  margin-bottom: 1rem;
}

.alert-content {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.pulse-dot {
  width: 12px;
  height: 12px;
  background-color: #42b983;
  border-radius: 50%;
  box-shadow: 0 0 0 rgba(66, 185, 131, 0.4);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { box-shadow: 0 0 0 0 rgba(66, 185, 131, 0.4); }
  70% { box-shadow: 0 0 0 10px rgba(66, 185, 131, 0); }
  100% { box-shadow: 0 0 0 0 rgba(66, 185, 131, 0); }
}

.alert-text {
  flex: 1;
  color: #2e7d32;
}

.btn-join-now {
  background: #42b983;
  color: white;
  border: none;
  padding: 0.5rem 1.5rem;
  border-radius: 20px;
  font-weight: bold;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-join-now:hover {
  background: #3aa876;
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
  color: #666;
}

.stat-card .value {
  font-size: 2.5rem;
  font-weight: bold;
  color: #3498db;
  margin: 1rem 0;
}

.stat-card p {
  margin: 0;
  font-size: 0.85rem;
  color: #999;
}

.upcoming-classes {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.05);
}

.class-list {
  margin-top: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.class-item {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  padding: 1rem;
  border-radius: 8px;
  background: #f8f9fa;
}

.class-item.active {
  border-left: 4px solid #3498db;
  background: #ebf5fb;
}

.time-tags {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 120px;
}

.time-tag {
  font-size: 0.8rem;
  font-weight: bold;
  color: #2c3e50;
  background: rgba(52, 152, 219, 0.1);
  padding: 2px 8px;
  border-radius: 4px;
  white-space: nowrap;
}

.info h4 {
  margin: 0 0 0.25rem 0;
}

.info p {
  margin: 0;
  font-size: 0.85rem;
  color: #666;
}

.btn-primary {
  margin-left: auto;
  padding: 0.5rem 1rem;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.status {
  margin-left: auto;
  font-size: 0.85rem;
  color: #999;
}
</style>
