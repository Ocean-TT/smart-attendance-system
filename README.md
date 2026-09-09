# 课堂考勤与点名提问系统

基于 FastAPI + Vue 3 + dlib 的课堂考勤系统，支持人脸签到、智能点名、考勤管理与数据统计。

## 功能

- **人脸考勤**：基于 dlib 实现人脸检测与特征提取，支持刷脸签到
- **智能点名**：加权随机算法，根据历史记录动态调整点名概率
- **考勤管理**：课程、学生、考勤记录的完整 CRUD
- **数据统计**：考勤率、到课分布等统计接口

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Python · FastAPI · dlib |
| 前端 | Vue 3 · Vite |
| 数据库 | SQLite / MySQL |

## 快速开始

### 后端

```bash
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python seed.py          # 初始化数据库
python main.py          # 启动服务，默认 http://127.0.0.1:8000
```

### 前端

```bash
cd frontend
npm install
npm run dev             # 默认 http://localhost:5173
```

## 项目结构

```
├── backend/            # FastAPI 后端
├── frontend/           # Vue 3 前端
├── database/           # 数据库脚本
└── docs/               # API 文档
```
