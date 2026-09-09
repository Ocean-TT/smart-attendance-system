from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from api import dashboard, auth, classroom, questions, statistics, profile
from database.db import engine, Base

app = FastAPI(
    title="Smart Attendance API",
    description="课堂考勤与点名提问系统后端服务",
    version="1.0.0",
)

# 启动时自动建表，省得每次手动跑
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# 前端 Vue 跑在 5173，开发期先放开跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 按模块注册路由，统一加 /api 前缀
app.include_router(auth.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(classroom.router, prefix="/api")
app.include_router(questions.router, prefix="/api")
app.include_router(statistics.router, prefix="/api")
app.include_router(profile.router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Smart Attendance API"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
