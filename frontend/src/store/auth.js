import { reactive, readonly, computed } from 'vue'

// 从 localStorage 初始化状态
const storedUser = JSON.parse(localStorage.getItem('user') || 'null')
const storedToken = localStorage.getItem('token') || null

const state = reactive({
  user: storedUser,
  token: storedToken,
  loading: false
})

const login = (userData, token) => {
  state.user = userData
  state.token = token
  localStorage.setItem('user', JSON.stringify(userData))
  localStorage.setItem('token', token)
}

const logout = () => {
  state.user = null
  state.token = null
  localStorage.removeItem('user')
  localStorage.removeItem('token')
}

const updateUser = (userData) => {
  state.user = { ...state.user, ...userData }
  localStorage.setItem('user', JSON.stringify(state.user))
}

const isAuthenticated = () => !!state.token
const getUserRole = () => state.user?.role || null

export const useAuthStore = () => {
  return {
    user: computed(() => state.user),
    token: computed(() => state.token),
    state: readonly(state),
    login,
    logout,
    updateUser,
    isAuthenticated,
    getUserRole
  }
}
