from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# 用 aiosqlite 做异步驱动，配合 FastAPI 的 async 路由
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./database.db")

engine = create_async_engine(DATABASE_URL, echo=False)

# 每次请求拿一个 session，用完自动关
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()

# FastAPI 依赖注入：每个接口拿一个数据库会话
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
