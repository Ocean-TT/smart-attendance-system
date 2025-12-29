import { createRouter, createWebHistory } from 'vue-router'
import Auth from '../pages/Auth.vue'
import Dashboard from '../pages/Dashboard.vue'
import QuestionBank from '../pages/QuestionBank.vue'
import ClassDetails from '../pages/ClassDetails.vue'
import Classroom from '../pages/Classroom.vue'
import Statistics from '../pages/Statistics.vue'
import Profile from '../pages/Profile.vue'

const routes = [
  { path: '/auth', component: Auth },
  { path: '/', component: Dashboard, meta: { requiresAuth: true } },
  { path: '/questions', component: QuestionBank, meta: { requiresAuth: true, role: 'TEACHER' } },
  { path: '/class/:id', component: ClassDetails, meta: { requiresAuth: true } },
  { path: '/classroom/:id', component: Classroom, meta: { requiresAuth: true } },
  { path: '/stats', component: Statistics, meta: { requiresAuth: true } },
  { path: '/profile', component: Profile, meta: { requiresAuth: true } },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
