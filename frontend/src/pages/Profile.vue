<template>
  <Layout>
    <div class="profile-container">
      <!-- 左侧/顶部 个人概览卡片 -->
      <div class="profile-sidebar">
        <div class="user-card">
          <div class="avatar-wrapper">
            <div class="avatar-circle">
              <span v-if="profileData.name">{{ profileData.name[0] }}</span>
              <span v-else>{{ profileData.username ? profileData.username[0] : 'U' }}</span>
            </div>
            <div class="role-badge" :class="profileData.role ? profileData.role.toLowerCase() : ''">
              {{ profileData.role === 'TEACHER' ? '教师' : '学生' }}
            </div>
          </div>
          <h2 class="user-name">{{ profileData.name || profileData.username }}</h2>
          <p class="user-id">{{ profileData.studentId || 'ID: ' + profileData.username }}</p>
          <div class="user-meta">
            <div class="meta-item">
              <span class="icon">🏢</span>
              <span>{{ profileData.department || '计算机学院' }}</span>
            </div>
            <div class="meta-item">
              <span class="icon">📧</span>
              <span>{{ profileData.email || '未设置邮箱' }}</span>
            </div>
          </div>
        </div>

        <div class="security-status">
          <h4>账号安全</h4>
          <div class="status-item">
            <span class="label">人脸数据</span>
            <span class="value" :class="{ 'status-ok': user.face_features, 'status-warn': !user.face_features }">
              {{ user.face_features ? '已录入' : '未录入' }}
            </span>
          </div>
          <div class="status-item">
            <span class="label">密码强度</span>
            <span class="value status-ok">安全</span>
          </div>
        </div>
      </div>

      <!-- 右侧 详细资料编辑 -->
      <div class="profile-main">
        <div class="content-card">
          <div class="card-header">
            <h3>基本资料</h3>
            <p>管理您的个人信息，确保教学/学习记录准确</p>
          </div>
          
          <div class="form-grid">
            <div class="form-group">
              <label>登录账号</label>
              <div class="input-wrapper readonly">
                <span class="icon">👤</span>
                <input :value="profileData.username" readonly />
              </div>
            </div>
            
            <div class="form-group">
              <label>真实姓名</label>
              <div class="input-wrapper">
                <span class="icon">📝</span>
                <input v-model="profileData.name" type="text" placeholder="请输入姓名" />
              </div>
            </div>

            <div class="form-group">
              <label>学号/工号</label>
              <div class="input-wrapper">
                <span class="icon">🆔</span>
                <input v-model="profileData.studentId" placeholder="请输入学号/工号" />
              </div>
            </div>

            <div class="form-group">
              <label>电子邮箱</label>
              <div class="input-wrapper">
                <span class="icon">✉️</span>
                <input v-model="profileData.email" type="email" placeholder="请输入邮箱" />
              </div>
            </div>

            <div class="form-group full-width">
              <label>所属院系</label>
              <div class="input-wrapper">
                <span class="icon">🏛️</span>
                <input v-model="profileData.department" placeholder="请输入所属院系" />
              </div>
            </div>
          </div>

          <div class="card-actions">
            <button @click="handleSave" class="btn-primary">保存基本资料</button>
          </div>
        </div>

        <div class="content-card face-card">
          <div class="card-header">
            <h3>人脸数据管理</h3>
            <p>用于课堂签到和身份验证，请确保光线充足</p>
          </div>
          
          <div class="face-content">
            <div class="face-preview">
              <div class="face-placeholder">
                <svg viewBox="0 0 24 24" width="48" height="48" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                  <circle cx="12" cy="7" r="4"></circle>
                </svg>
              </div>
              <div class="face-info">
                <span class="status-text">{{ user.face_features ? '人脸档案已就绪' : '尚未录入人脸' }}</span>
                <button @click="showFaceUpdate = !showFaceUpdate" class="btn-outline">
                  {{ showFaceUpdate ? '取消录入' : (user.face_features ? '重新录入' : '立即录入') }}
                </button>
              </div>
            </div>

            <transition name="fade">
              <div v-if="showFaceUpdate" class="face-capture-container">
                <FaceCapture :allowUpload="true" @capture="onFaceUpdate" />
              </div>
            </transition>
          </div>
        </div>

        <div class="content-card danger-zone">
          <div class="card-header">
            <h3>安全操作</h3>
          </div>
          <div class="danger-actions">
            <button @click="showPwdModal = true" class="btn-secondary">修改登录密码</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 修改密码弹窗 -->
    <transition name="fade">
      <div v-if="showPwdModal" class="modal-overlay" @click.self="showPwdModal = false">
        <div class="modal-content pwd-modal">
          <div class="modal-header">
            <div class="header-icon">🔐</div>
            <h3>修改登录密码</h3>
            <p>请定期更换密码以保护您的账号安全</p>
          </div>

          <div class="modal-body">
            <div class="form-group">
              <label>原密码</label>
              <div class="input-wrapper">
                <span class="icon">🔑</span>
                <input v-model="pwdForm.old_pwd" type="password" placeholder="请输入当前使用的密码" />
              </div>
            </div>
            
            <div class="form-group">
              <label>新密码</label>
              <div class="input-wrapper">
                <span class="icon">✨</span>
                <input v-model="pwdForm.new_pwd" type="password" placeholder="请输入 6 位以上新密码" />
              </div>
            </div>
            
            <div class="form-group">
              <label>确认新密码</label>
              <div class="input-wrapper">
                <span class="icon">✅</span>
                <input v-model="pwdForm.confirm_pwd" type="password" placeholder="请再次输入新密码" />
              </div>
            </div>
          </div>

          <div class="modal-actions">
            <button @click="showPwdModal = false" class="btn-cancel">取消</button>
            <button @click="handlePwdChange" class="btn-submit">确认修改密码</button>
          </div>
        </div>
      </div>
    </transition>
  </Layout>
</template>

<script setup>
import { ref, onMounted, reactive, watch } from 'vue'
import Layout from '../components/Layout.vue'
import FaceCapture from '../components/FaceCapture.vue'
import { useAuthStore } from '../store/auth'
import { getProfile, updateProfile, updateFace, changePassword } from '../api'

const { user, login, updateUser } = useAuthStore()
const profileData = ref({ 
  username: '',
  name: '',
  role: '',
  studentId: '',
  email: '',
  department: '',
  ...user.value 
})

// 监听 store 中的 user 变化，同步到本地表单
watch(user, (newVal) => {
  if (newVal) {
    profileData.value = { ...profileData.value, ...newVal }
  }
}, { immediate: true })
const showFaceUpdate = ref(false)
const showPwdModal = ref(false)

const pwdForm = reactive({
  old_pwd: '',
  new_pwd: '',
  confirm_pwd: ''
})

onMounted(async () => {
  try {
    const res = await getProfile()
    if (res.code === 200) {
      profileData.value = { ...profileData.value, ...res.data }
      // 同步到 store
      updateUser(res.data)
    }
  } catch (err) {
    console.error('获取个人资料失败:', err)
  }
})

const onFaceUpdate = async (blob) => {
  try {
    const reader = new FileReader()
    reader.readAsDataURL(blob)
    reader.onloadend = async () => {
      const base64data = reader.result
      const res = await updateFace(base64data)
      if (res.code === 200) {
        alert("人脸信息已更新")
        showFaceUpdate.value = false
        // 更新本地 store 状态，触发 UI 变化
        updateUser({ ...user.value, face_features: 'updated' })
      } else {
        alert(res.msg || "更新失败")
      }
    }
  } catch (err) {
    alert('更新人脸失败: ' + err.message)
  }
}

const handleSave = async () => {
  try {
    // 映射字段名以匹配后端 Pydantic 模型
    const payload = {
      name: profileData.value.name,
      email: profileData.value.email,
      student_id: profileData.value.studentId,
      department: profileData.value.department
    }
    const res = await updateProfile(payload)
    if (res.code === 200) {
      updateUser(profileData.value)
      alert("个人资料已保存")
    } else {
      alert(res.message || "保存失败")
    }
  } catch (err) {
    alert('保存失败: ' + err.message)
  }
}

const handlePwdChange = async () => {
  if (!pwdForm.old_pwd || !pwdForm.new_pwd) {
    alert("请填写完整信息")
    return
  }
  if (pwdForm.new_pwd !== pwdForm.confirm_pwd) {
    alert("两次输入的新密码不一致")
    return
  }

  try {
    const res = await changePassword(pwdForm.old_pwd, pwdForm.new_pwd)
    if (res.code === 200) {
      alert("密码修改成功")
      showPwdModal.value = false
      // 清空表单
      pwdForm.old_pwd = ''
      pwdForm.new_pwd = ''
      pwdForm.confirm_pwd = ''
    } else {
      alert(res.message || "修改失败")
    }
  } catch (err) {
    alert("修改失败: " + err.message)
  }
}
</script>

<style scoped>
.profile-container {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem;
}

/* 左侧侧边栏 */
.profile-sidebar {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.user-card {
  background: white;
  padding: 2rem;
  border-radius: 16px;
  text-align: center;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}

.avatar-wrapper {
  position: relative;
  width: 100px;
  height: 100px;
  margin: 0 auto 1.5rem;
}

.avatar-circle {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #42b983, #3aa876);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2.5rem;
  color: white;
  font-weight: bold;
  box-shadow: 0 4px 10px rgba(66, 185, 131, 0.3);
}

.role-badge {
  position: absolute;
  bottom: -5px;
  right: -5px;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: bold;
  color: white;
  border: 2px solid white;
}

.role-badge.teacher { background: #42b983; }
.role-badge.student { background: #3498db; }

.user-name {
  margin: 0 0 0.5rem 0;
  font-size: 1.5rem;
  color: #2c3e50;
}

.user-id {
  color: #95a5a6;
  font-size: 0.9rem;
  margin-bottom: 1.5rem;
}

.user-meta {
  border-top: 1px solid #eee;
  padding-top: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
  text-align: left;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  color: #666;
  font-size: 0.9rem;
}

.security-status {
  background: white;
  padding: 1.5rem;
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}

.security-status h4 {
  margin: 0 0 1rem 0;
  color: #2c3e50;
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.8rem;
  font-size: 0.9rem;
}

.status-item .label { color: #7f8c8d; }
.status-ok { color: #42b983; font-weight: bold; }
.status-warn { color: #e67e22; font-weight: bold; }

/* 右侧主内容 */
.profile-main {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.content-card {
  background: white;
  padding: 2rem;
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}

.card-header {
  margin-bottom: 2rem;
}

.card-header h3 {
  margin: 0 0 0.5rem 0;
  color: #2c3e50;
  font-size: 1.25rem;
}

.card-header p {
  margin: 0;
  color: #95a5a6;
  font-size: 0.9rem;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

.form-group.full-width {
  grid-column: span 2;
}

.form-group label {
  display: block;
  margin-bottom: 0.6rem;
  color: #2c3e50;
  font-weight: 500;
  font-size: 0.9rem;
}

.input-wrapper {
  display: flex;
  align-items: center;
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 10px;
  padding: 0 1rem;
  transition: all 0.3s;
}

.input-wrapper:focus-within {
  border-color: #42b983;
  background: white;
  box-shadow: 0 0 0 3px rgba(66, 185, 131, 0.1);
}

.input-wrapper.readonly {
  background: #f1f3f5;
  cursor: not-allowed;
}

.input-wrapper .icon {
  margin-right: 0.8rem;
  font-size: 1.1rem;
}

.input-wrapper input {
  flex: 1;
  border: none;
  background: transparent;
  padding: 0.8rem 0;
  font-size: 0.95rem;
  color: #2c3e50;
  outline: none;
}

.card-actions {
  margin-top: 2rem;
  display: flex;
  justify-content: flex-end;
}

.btn-primary {
  background: #42b983;
  color: white;
  border: none;
  padding: 0.8rem 2rem;
  border-radius: 10px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-primary:hover {
  background: #3aa876;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(66, 185, 131, 0.2);
}

/* 人脸管理卡片 */
.face-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.face-preview {
  display: flex;
  align-items: center;
  gap: 2rem;
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 12px;
}

.face-placeholder {
  width: 80px;
  height: 80px;
  background: #e9ecef;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #adb5bd;
}

.face-info {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}

.status-text {
  font-weight: 500;
  color: #2c3e50;
}

.btn-outline {
  background: white;
  border: 1px solid #dee2e6;
  padding: 0.6rem 1.2rem;
  border-radius: 8px;
  color: #495057;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-outline:hover {
  border-color: #42b983;
  color: #42b983;
}

.face-capture-container {
  border: 2px dashed #e9ecef;
  border-radius: 16px;
  padding: 1rem;
  background: #fff;
}

/* 危险区域 */
.danger-zone {
  border-left: 4px solid #ff4d4f;
}

.btn-secondary {
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  padding: 0.6rem 1.5rem;
  border-radius: 8px;
  color: #666;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary:hover {
  background: #fff1f0;
  border-color: #ff4d4f;
  color: #ff4d4f;
}

/* 弹窗样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.4);
  backdrop-filter: blur(6px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.pwd-modal {
  background: white;
  padding: 2.5rem;
  border-radius: 24px;
  width: 420px;
  box-shadow: 0 25px 50px -12px rgba(0,0,0,0.15);
  border: 1px solid rgba(255,255,255,0.3);
}

.modal-header {
  text-align: center;
  margin-bottom: 2rem;
}

.header-icon {
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

.modal-header h3 {
  margin: 0 0 0.5rem 0;
  color: #2c3e50;
  font-size: 1.5rem;
}

.modal-header p {
  margin: 0;
  color: #95a5a6;
  font-size: 0.9rem;
}

.modal-body {
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
}

.modal-actions {
  display: flex;
  gap: 1rem;
  margin-top: 2.5rem;
}

.modal-actions button {
  flex: 1;
  padding: 0.9rem;
  border-radius: 12px;
  font-weight: bold;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-cancel {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  color: #7f8c8d;
}

.btn-cancel:hover {
  background: #f1f3f5;
  color: #2c3e50;
}

.btn-submit {
  background: #42b983;
  border: none;
  color: white;
  box-shadow: 0 4px 12px rgba(66, 185, 131, 0.2);
}

.btn-submit:hover {
  background: #3aa876;
  transform: translateY(-1px);
  box-shadow: 0 6px 15px rgba(66, 185, 131, 0.3);
}

.btn-submit:active {
  transform: translateY(0);
}

/* 动画 */
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

@media (max-width: 900px) {
  .profile-container {
    grid-template-columns: 1fr;
  }
  .form-grid {
    grid-template-columns: 1fr;
  }
  .form-group.full-width {
    grid-column: span 1;
  }
}
</style>
