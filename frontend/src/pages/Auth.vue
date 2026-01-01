<template>
  <div class="auth-container">
    <div class="auth-card">
      <h2>{{ isLogin ? '登录' : '注册' }}</h2>
      <form @submit.prevent="handleSubmit">
        <!-- 角色选择 -->
        <div class="role-selector">
          <label :class="{ active: role === 'STUDENT' }">
            <input type="radio" v-model="role" value="STUDENT" /> 学生
          </label>
          <label :class="{ active: role === 'TEACHER' }">
            <input type="radio" v-model="role" value="TEACHER" /> 教师
          </label>
        </div>

        <input v-model="formData.username" :placeholder="isLogin ? (role === 'STUDENT' ? '用户名 / 学号 / 邮箱' : '用户名 / 邮箱') : '用户名'" :required="!isFaceLogin" />
        <input v-model="formData.password" type="password" placeholder="密码" :required="!isFaceLogin" v-if="!isFaceLogin" />
        
        <div v-if="isLogin" class="face-login-toggle">
          <button type="button" @click="isFaceLogin = !isFaceLogin" class="link-btn">
            {{ isFaceLogin ? '使用密码登录' : '使用人脸登录' }}
          </button>
        </div>

        <div v-if="isFaceLogin" class="face-capture-box">
          <FaceCapture :key="faceCaptureKey" @capture="onFaceCapture" />
          <p class="hint">请正对摄像头</p>
        </div>

        <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>

        <template v-if="!isLogin">
          <input v-model="formData.name" placeholder="真实姓名" required />
          <input v-model="formData.email" type="email" placeholder="电子邮箱" />
          <input v-model="formData.studentId" :placeholder="role === 'STUDENT' ? '学号' : '工号'" required />
          
          <div class="face-block">
            <div class="face-label">
              人脸录入 
              <span v-if="faceData" class="face-status-tag">✅ 已录入</span>
            </div>
            <FaceCapture :key="faceCaptureKey" :allowUpload="true" @capture="onFaceCapture" />
          </div>
        </template>
        
        <button type="submit" :disabled="loading">{{ loading ? '处理中...' : (isLogin ? '登录' : '注册') }}</button>
      </form>
      <p @click="toggleMode" class="toggle-link">
        {{ isLogin ? '没有账号？去注册' : '已有账号？去登录' }}
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../store/auth'
import FaceCapture from '../components/FaceCapture.vue'
import { loginApi, registerApi, faceLoginApi } from '../api'

const isLogin = ref(true)
const isFaceLogin = ref(false)
const role = ref('STUDENT')
const formData = ref({ username: '', password: '', studentId: '', name: '', email: '' })
const faceData = ref(null)
const faceCaptureKey = ref(0)
const router = useRouter()
const auth = useAuthStore()
const errorMessage = ref('')
const loading = ref(false)

const onFaceCapture = (blob) => {
  const reader = new FileReader()
  reader.readAsDataURL(blob)
  reader.onloadend = () => {
    const base64data = reader.result
    faceData.value = base64data
    if (isFaceLogin.value && isLogin.value) {
      handleFaceLogin(base64data)
    }
  }
}

const resetAuthForm = () => {
  formData.value = { username: '', password: '', studentId: '', name: '', email: '' }
  faceData.value = null
  faceCaptureKey.value++
  errorMessage.value = ''
}

const toggleMode = () => {
  isLogin.value = !isLogin.value
  isFaceLogin.value = false
  resetAuthForm()
}

const handleFaceLogin = async (base64) => {
  loading.value = true
  errorMessage.value = ''
  try {
    const res = await faceLoginApi(base64)
    if (res.code === 200) {
      auth.login(res.data.user, res.data.token)
      router.push('/')
    } else {
      errorMessage.value = res.msg || '人脸识别失败'
    }
  } catch (err) {
    errorMessage.value = '人脸登录服务异常'
  } finally {
    loading.value = false
  }
}

const handleSubmit = async () => {
  if (isFaceLogin.value) return

  errorMessage.value = ''
  loading.value = true
  
  try {
    if (isLogin.value) {
      const res = await loginApi(formData.value.username, formData.value.password)
      if (res.code === 200) {
        auth.login(res.data.user, res.data.token)
        router.push('/')
      } else {
        errorMessage.value = res.msg || '登录失败'
      }
    } else {
      const res = await registerApi({
        ...formData.value,
        role: role.value,
        faceData: faceData.value
      })
      if (res.code === 200) {
        alert('注册成功，请登录')
        isLogin.value = true
        resetAuthForm()
      } else {
        errorMessage.value = res.msg || '注册失败'
      }
    }
  } catch (err) {
    errorMessage.value = '网络请求失败'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-container { display: flex; justify-content: center; align-items: center; height: 100vh; background: #f5f7fa; }
.auth-card { background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); width: 400px; }
.role-selector { display: flex; gap: 1rem; margin-bottom: 1.5rem; }
.role-selector label { flex: 1; text-align: center; padding: 0.5rem; border: 1px solid #ddd; border-radius: 6px; cursor: pointer; }
.role-selector label.active { background: #409eff; color: white; border-color: #409eff; }
.role-selector input { display: none; }
form input { width: 100%; padding: 0.8rem; margin-bottom: 1rem; border: 1px solid #ddd; border-radius: 6px; box-sizing: border-box; }
button { width: 100%; padding: 0.8rem; background: #409eff; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 1rem; }
button:disabled { background: #a0cfff; }
.error-message { color: #f56c6c; font-size: 0.9rem; margin-bottom: 1rem; }
.toggle-link { text-align: center; margin-top: 1rem; color: #409eff; cursor: pointer; }
.face-login-toggle { text-align: right; margin-bottom: 1rem; }
.link-btn { background: none; color: #409eff; border: none; padding: 0; width: auto; font-size: 0.9rem; cursor: pointer; }
.face-capture-box { margin-bottom: 1.5rem; text-align: center; }
.hint { font-size: 0.8rem; color: #909399; margin-top: 0.5rem; }
.face-status-tag { background: #f0f9eb; color: #67c23a; padding: 2px 6px; border-radius: 4px; font-size: 0.8rem; }
.auth-card { background: white; padding: 36px; border-radius: 10px; box-shadow: 0 6px 18px rgba(20,30,40,0.06); width: 100%; max-width: 420px; }
form { display: flex; flex-direction: column; gap: 14px; }

.role-selector {
  display: flex;
  gap: 10px;
  margin-bottom: 5px;
}
.role-selector label {
  flex: 1;
  padding: 10px;
  border: 1px solid #e6e9ee;
  border-radius: 6px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 14px;
  color: #666;
}
.role-selector label.active {
  border-color: #1e90ff;
  background: #f0f7ff;
  color: #1e90ff;
  font-weight: bold;
}
.role-selector input {
  display: none;
}

input, select { padding: 10px; border-radius: 6px; border: 1px solid #e6e9ee; outline: none; font-size:14px; }
input:focus, select:focus { box-shadow: 0 0 0 3px rgba(30,144,255,0.08); border-color:#1e90ff; }
.error-message { color: #e74c3c; font-size: 13px; margin-top: -5px; }
button { padding: 12px; background: #1e90ff; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight:600; }
.toggle-link { text-align: center; margin-top: 12px; cursor: pointer; color: #1e90ff; }
.student-face-block { display: flex; flex-direction: column; gap: 8px; }
.face-block { border-radius: 8px; padding: 10px; background: #fbfdff; box-shadow: inset 0 1px 0 rgba(255,255,255,0.6); }
.face-label { font-size:13px; color:#333; margin-bottom:8px; font-weight:500; display: flex; justify-content: space-between; align-items: center; }
.face-status-tag { font-size: 11px; color: #42b983; background: #e8f5e9; padding: 2px 6px; border-radius: 4px; }
</style>