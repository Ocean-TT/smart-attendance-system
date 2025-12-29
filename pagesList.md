# 页面列表与文件映射

| 页面功能 | 文件路径 | 访问路由 | 角色权限 |
| :--- | :--- | :--- | :--- |
| 1. 登录、注册 | [frontend/src/pages/Auth.vue](frontend/src/pages/Auth.vue) | `/auth` | 公开 |
| 2. 题库管理 | [frontend/src/pages/QuestionBank.vue](frontend/src/pages/QuestionBank.vue) | `/questions` | 教师 |
| 3. 首页/仪表盘 | [frontend/src/pages/Dashboard.vue](frontend/src/pages/Dashboard.vue) | `/` | 通用 |
| 4. 班级详情 | [frontend/src/pages/ClassDetails.vue](frontend/src/pages/ClassDetails.vue) | `/class/:id` | 通用 |
| 5. 课堂页面 | [frontend/src/pages/Classroom.vue](frontend/src/pages/Classroom.vue) | `/classroom/:id` | 通用 |
| 6. 统计分析页 | [frontend/src/pages/Statistics.vue](frontend/src/pages/Statistics.vue) | `/stats` | 通用 |
| 7. 用户资料页 | [frontend/src/pages/Profile.vue](frontend/src/pages/Profile.vue) | `/profile` | 通用 |

## 核心组件
- 布局组件: [frontend/src/components/Layout.vue](frontend/src/components/Layout.vue)
- 人脸采集: [frontend/src/components/FaceCapture.vue](frontend/src/components/FaceCapture.vue)
