from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from api import dashboard, auth, classroom, questions, statistics, profile
from database.db import engine, Base
import asyncio

app = FastAPI(title="CourseDesign API")

# 启动时创建数据库表
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由，统一添加 /api 前缀
app.include_router(auth.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(classroom.router, prefix="/api")
app.include_router(questions.router, prefix="/api")
app.include_router(statistics.router, prefix="/api")
app.include_router(profile.router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Welcome to CourseDesign API"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
