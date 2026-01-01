import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../store/auth'
import Auth from '../pages/Auth.vue'
import Dashboard from '../pages/Dashboard.vue'
import QuestionBank from '../pages/QuestionBank.vue'
import ClassDetails from '../pages/ClassDetails.vue'
import Classroom from '../pages/Classroom.vue'
import Statistics from '../pages/Statistics.vue'
import Profile from '../pages/Profile.vue'

const routes = [
  { path: '/auth', component: Auth, meta: { requiresGuest: true } },
  { path: '/', component: Dashboard, meta: { requiresAuth: true } },
  { path: '/questions', component: QuestionBank, meta: { requiresAuth: true } },
  { path: '/class/:id', component: ClassDetails, meta: { requiresAuth: true } },
  { path: '/classroom/:id?', component: Classroom, meta: { requiresAuth: true } },
  { path: '/stats', alias: '/statistics', component: Statistics, meta: { requiresAuth: true } },
  { path: '/profile', component: Profile, meta: { requiresAuth: true } },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const auth = useAuthStore()
  
  // 1. 处理需要登录的页面
  if (to.meta.requiresAuth && !auth.isAuthenticated()) {
    return next('/auth')
  }

  // 2. 处理已登录用户访问登录页
  if (to.meta.requiresGuest && auth.isAuthenticated()) {
    return next('/')
  }

  // 3. 处理角色权限
  if (to.meta.role && auth.getUserRole() !== to.meta.role) {
    alert('您没有权限访问此页面')
    return next('/')
  }

  next()
})

export default router
