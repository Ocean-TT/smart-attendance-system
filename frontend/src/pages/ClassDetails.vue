<template>
  <Layout>
    <div class="class-details">
      <div class="header">
        <h3>班级详情 (ID: {{ route.params.id }})</h3>
        <div class="actions">
          <button @click="showImport = true" class="import-btn">导入学生 (CSV)</button>
          <button class="add-btn">添加学生</button>
        </div>
      </div>

      <div v-if="showImport" class="import-form">
        <h4>导入学生名单</h4>
        <form @submit.prevent="handleImport">
          <input type="file" accept=".csv" />
          <div class="form-actions">
            <button type="submit">上传并解析</button>
            <button type="button" @click="showImport = false">取消</button>
          </div>
        </form>
      </div>

      <div class="student-list">
        <h4>学生花名册</h4>
        <table>
          <thead>
            <tr>
              <th>学号</th>
              <th>姓名</th>
              <th>出勤率</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="s in students" :key="s.id">
              <td>{{ s.id }}</td>
              <td>{{ s.name }}</td>
              <td>{{ s.attendance }}</td>
              <td>
                <button class="del-btn">移除</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </Layout>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import Layout from '../components/Layout.vue'

const route = useRoute()
const students = ref([
  { id: '2021001', name: '张三', attendance: '95%' },
  { id: '2021002', name: '李四', attendance: '88%' },
])

const showImport = ref(false)
const handleImport = () => {
  alert("CSV 导入功能待实现")
  showImport.value = false
}
</script>

<style scoped>
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.import-btn { padding: 8px 16px; background: #1890ff; color: white; border: none; border-radius: 4px; margin-right: 10px; cursor: pointer; }
.add-btn { padding: 8px 16px; background: #52c41a; color: white; border: none; border-radius: 4px; cursor: pointer; }
.import-form { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; border: 1px solid #ddd; }
.student-list { background: white; padding: 20px; border-radius: 8px; }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 12px; text-align: left; border-bottom: 1px solid #f0f0f0; }
.del-btn { color: #ff4d4f; border: none; background: none; cursor: pointer; }
</style>
