import asyncio
from database.db import engine
from database.models import User
from sqlalchemy import select

async def check():
    async with engine.connect() as conn:
        result = await conn.execute(select(User.username, User.student_id, User.password))
        print("Users in DB:", result.all())

if __name__ == "__main__":
    asyncio.run(check())
