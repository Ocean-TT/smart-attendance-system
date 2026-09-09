import asyncio
import json
from passlib.context import CryptContext

from database.db import engine, Base, AsyncSessionLocal as SessionLocal
from database.models import User, QuestionBank, Question, Classroom

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def seed_data():
    async with engine.begin() as conn:
        # 重置数据库，开发期方便
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with SessionLocal() as db:
        # 建两个测试用户
        teacher = User(
            username="teacher",
            password=pwd_context.hash("123456"),
            name="张老师",
            role="TEACHER",
            email="teacher@example.com"
        )
        student = User(
            username="student",
            password=pwd_context.hash("123456"),
            name="李小明",
            role="STUDENT",
            student_id="2026001",
            email="student@example.com"
        )
        db.add_all([teacher, student])
        await db.commit()

        # 建两个示例班级
        class1 = Classroom(
            name="软件工程 1 班",
            teacher_id=teacher.id,
            description="软件工程专业核心课程",
            schedule="周一 8:00-10:00",
            student_count=45
        )
        class2 = Classroom(
            name="人工智能导论",
            teacher_id=teacher.id,
            description="AI 基础知识",
            schedule="周三 14:00-16:00",
            student_count=38
        )
        db.add_all([class1, class2])
        await db.commit()

        # 把学生加进班级（多对多中间表）
        from database.models import student_classroom
        await db.execute(student_classroom.insert().values(student_id=student.id, classroom_id=class1.id))
        await db.execute(student_classroom.insert().values(student_id=student.id, classroom_id=class2.id))
        await db.commit()

        # 建个题库和两道题
        bank1 = QuestionBank(
            name="软件工程期末复习",
            description="包含选择题和判断题",
            creator_id=teacher.id
        )
        db.add(bank1)
        await db.commit()

        q1 = Question(
            bank_id=bank1.id,
            type="SINGLE",
            content="软件生命周期中，哪个阶段最耗费资源？",
            options=json.dumps(["需求分析", "设计阶段", "编码阶段", "维护阶段"]),
            answer="维护阶段"
        )
        q2 = Question(
            bank_id=bank1.id,
            type="JUDGE",
            content="瀑布模型适用于需求不明确的项目。",
            options=json.dumps(["正确", "错误"]),
            answer="错误"
        )
        db.add_all([q1, q2])
        await db.commit()

    print("Seed data created!  测试账号: teacher/123456, student/123456")

if __name__ == "__main__":
    asyncio.run(seed_data())
