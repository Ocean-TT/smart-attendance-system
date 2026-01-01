import asyncio
import json
from database.db import engine, Base, AsyncSessionLocal as SessionLocal
from database.models import User, QuestionBank, Question, Classroom

async def seed_data():
    async with engine.begin() as conn:
        # 重新创建表
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with SessionLocal() as db:
        # 1. 创建初始用户
        teacher = User(
            username="teacher",
            password="123",
            name="张老师",
            role="TEACHER",
            email="teacher@example.com"
        )
        student = User(
            username="student",
            password="123",
            name="李小明",
            role="STUDENT",
            student_id="2026001",
            email="student@example.com"
        )
        db.add_all([teacher, student])
        await db.commit()

        # 2. 创建初始班级
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

        # 2.5 将学生加入班级
        # 使用关联表
        from database.models import student_classroom
        await db.execute(student_classroom.insert().values(student_id=student.id, classroom_id=class1.id))
        await db.execute(student_classroom.insert().values(student_id=student.id, classroom_id=class2.id))
        await db.commit()

        # 3. 创建初始题库
        bank1 = QuestionBank(
            name="软件工程期末复习",
            description="包含选择题和判断题",
            creator_id=teacher.id
        )
        db.add(bank1)
        await db.commit()

        # 4. 创建初始题目
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

    print("Seed data created successfully!")

if __name__ == "__main__":
    asyncio.run(seed_data())
