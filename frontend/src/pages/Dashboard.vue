<template>
  <Layout>
    <div class="dashboard">
      <div class="header">
        <h3>{{ userRole === 'TEACHER' ? '我管理的班级' : '我参加的课程' }}</h3>
        <button v-if="userRole === 'TEACHER'" @click="showCreate = true" class="create-btn">创建新班级</button>
      </div>

      <div v-if="showCreate" class="create-form">
        <h4>创建班级</h4>
        <form @submit.prevent="handleCreateClass">
          <input v-model="newClass.name" placeholder="班级名称" required />
          <input v-model="newClass.semester" placeholder="学期" required />
          <button type="submit">提交</button>
          <button type="button" @click="showCreate = false">取消</button>
        </form>
      </div>

      <div class="class-grid">
        <div v-for="cls in classes" :key="cls.id" class="class-card">
          <h4>{{ cls.name }}</h4>
          <p>学期: {{ cls.semester }}</p>
          <p>学生人数: {{ cls.studentCount }}</p>
          <div class="actions">
            <router-link :to="'/class/' + cls.id">查看详情</router-link>
            <router-link v-if="userRole === 'TEACHER'" :to="'/classroom/' + cls.id" class="enter-btn">进入课堂</router-link>
          </div>
        </div>
      </div>
    </div>
  </Layout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import Layout from '../components/Layout.vue'

const userRole = ref('TEACHER')
const classes = ref([
  { id: 1, name: '计算机网络', semester: '2023秋季', studentCount: 45 },
  { id: 2, name: '操作系统', semester: '2023秋季', studentCount: 38 },
])

const showCreate = ref(false)
const newClass = ref({ name: '', semester: '' })

const handleCreateClass = () => {
  classes.value.push({ ...newClass.value, id: Date.now(), studentCount: 0 })
  showCreate.value = false
  newClass.value = { name: '', semester: '' }
}

onMounted(() => {
  const user = JSON.parse(localStorage.getItem('user') || '{}')
  userRole.value = user.role || 'STUDENT'
})
</script>

<style scoped>
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.create-btn { padding: 8px 16px; background: #52c41a; color: white; border: none; border-radius: 4px; cursor: pointer; }
.create-form { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; border: 1px solid #ddd; }
.create-form form { display: flex; gap: 10px; }
.class-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; }
.class-card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
.actions { margin-top: 16px; display: flex; gap: 10px; }
.enter-btn { color: #52c41a; }
</style>
