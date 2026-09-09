# 课堂考勤与点名提问系统

基于 FastAPI + Vue 3 的课堂互动系统，支持人脸考勤、智能点名、随堂测验与数据统计。

## 功能

- **人脸考勤**：dlib 人脸检测 + 128 维特征比对，刷脸签到
- **智能点名**：加权随机算法，根据历史记录调整抽取概率
- **随堂测验**：题库管理、课堂答题、自动判分
- **数据统计**：考勤率、答题正确率、学生积分
- **用户系统**：JWT 鉴权 + bcrypt 密码哈希，教师/学生两种角色

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Python · FastAPI · SQLAlchemy (async) · Pydantic |
| 鉴权 | JWT (python-jose) · bcrypt (passlib) |
| CV | face-recognition (dlib) · OpenCV |
| 前端 | Vue 3 · Vite |
| 数据库 | SQLite (aiosqlite) |

## 快速开始

### 后端

```bash
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt

# 复制环境变量并修改 SECRET_KEY
copy .env.example .env

# 初始化数据库（会清空旧数据）
python seed.py

# 启动
python main.py
# 默认 http://127.0.0.1:8000
```

测试账号：`teacher/123456`，`student/123456`

### 前端

```bash
cd frontend
npm install
npm run dev
# 默认 http://localhost:5173
```

## 项目结构

```
backend/
├── main.py              # FastAPI 入口
├── api/                 # 路由模块
│   ├── auth.py          # 登录/注册/人脸登录
│   ├── classroom.py     # 班级管理
│   ├── questions.py      # 题库与答题
│   ├── statistics.py     # 数据统计
│   ├── dashboard.py      # 首页概览
│   └── profile.py        # 个人中心
├── database/
│   ├── db.py            # 异步引擎与 session
│   └── models.py        # SQLAlchemy 模型
├── utils/
│   ├── auth.py          # JWT 依赖注入
│   ├── face.py          # 人脸特征提取
│   └── response.py      # 统一响应格式
└── seed.py              # 初始化测试数据
```
