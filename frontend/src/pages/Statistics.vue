<template>
  <Layout>
    <div class="statistics">
      <h3>数据统计与分析</h3>
      <div class="chart-grid">
        <div class="chart-card">
          <h4>出勤率统计</h4>
          <div class="placeholder">[图表占位: 出勤趋势图]</div>
        </div>
        <div class="chart-card">
          <h4>课堂活跃度</h4>
          <div class="placeholder">[图表占位: 提问/回答分布]</div>
        </div>
      </div>

      <div class="record-table">
        <h4>{{ userRole === 'TEACHER' ? '学生表现排行' : '我的详细记录' }}</h4>
        <table>
          <thead>
            <tr>
              <th>日期</th>
              <th>课程</th>
              <th>状态</th>
              <th>表现得分</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>2023-10-24</td>
              <td>计算机网络</td>
              <td>已到</td>
              <td>+5</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </Layout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import Layout from '../components/Layout.vue'

const userRole = ref('TEACHER')

onMounted(() => {
  const user = JSON.parse(localStorage.getItem('user') || '{}')
  userRole.value = user.role || 'STUDENT'
})
</script>

<style scoped>
.chart-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-top: 20px; }
.chart-card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
.placeholder { height: 200px; background: #f9f9f9; display: flex; alignItems: center; justifyContent: center; color: #999; }
.record-table { background: white; padding: 20px; border-radius: 8px; margin-top: 20px; }
table { width: 100%; border-collapse: collapse; margin-top: 10px; }
th, td { padding: 10px; text-align: left; border-bottom: 1px solid #eee; }
</style>
