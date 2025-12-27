<template>
  <Layout>
    <div class="question-bank">
      <div class="header">
        <h3>题库管理</h3>
        <button @click="showAdd = true" class="add-btn">新建题目</button>
      </div>

      <div v-if="showAdd" class="add-form">
        <h4>添加题目</h4>
        <form @submit.prevent="handleAdd">
          <select v-model="newQ.type">
            <option value="单选">单选</option>
            <option value="多选">多选</option>
            <option value="判断">判断</option>
            <option value="简答">简答</option>
          </select>
          <textarea v-model="newQ.content" placeholder="题干" required></textarea>
          <input v-model="newQ.answer" placeholder="正确答案" required />
          <input v-model="newQ.tags" placeholder="标签 (逗号分隔)" />
          <div class="form-actions">
            <button type="submit">保存</button>
            <button type="button" @click="showAdd = false">取消</button>
          </div>
        </form>
      </div>

      <table class="q-table">
        <thead>
          <tr>
            <th>类型</th>
            <th>题干</th>
            <th>标签</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="q in questions" :key="q.id">
            <td>{{ q.type }}</td>
            <td>{{ q.content }}</td>
            <td>
              <span v-for="t in q.tags" :key="t" class="tag">{{ t }}</span>
            </td>
            <td>
              <button class="edit-btn">编辑</button>
              <button class="del-btn">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </Layout>
</template>

<script setup>
import { ref } from 'vue'
import Layout from '../components/Layout.vue'

const questions = ref([
  { id: 1, type: '单选', content: '什么是TCP的三次握手？', tags: ['网络', '基础'], answer: '...' },
  { id: 2, type: '判断', content: 'HTTP是无状态协议。', tags: ['网络'], answer: '对' },
])

const showAdd = ref(false)
const newQ = ref({ type: '单选', content: '', tags: '', answer: '' })

const handleAdd = () => {
  questions.value.push({ ...newQ.value, id: Date.now(), tags: newQ.value.tags.split(',') })
  showAdd.value = false
  newQ.value = { type: '单选', content: '', tags: '', answer: '' }
}
</script>

<style scoped>
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.add-btn { padding: 8px 16px; background: #1890ff; color: white; border: none; border-radius: 4px; cursor: pointer; }
.add-form { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; border: 1px solid #ddd; }
.add-form form { display: flex; flex-direction: column; gap: 10px; }
.q-table { width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; }
.q-table th, .q-table td { padding: 12px; text-align: left; border-bottom: 1px solid #f0f0f0; }
.tag { background: #e6f7ff; color: #1890ff; padding: 2px 8px; border-radius: 4px; margin-right: 4px; font-size: 12px; }
.edit-btn { color: #1890ff; border: none; background: none; cursor: pointer; }
.del-btn { color: #ff4d4f; border: none; background: none; cursor: pointer; margin-left: 10px; }
</style>
