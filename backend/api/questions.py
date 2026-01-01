from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from database.db import get_db
from database.models import QuestionBank, Question, User, Classroom, student_classroom, PracticeRecord
from utils.response import success_response, error_response
from utils.auth import get_current_user
import json

router = APIRouter(prefix="/questions", tags=["questions"])

class QuestionSchema(BaseModel):
    bank_id: Optional[int] = None
    type: str
    content: str
    options: Optional[List[str]] = None
    answer: str

class PracticeSubmit(BaseModel):
    bank_id: int
    total_questions: int
    correct_count: int
    score: int

@router.get("/banks")
async def get_banks(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    if user.role == "TEACHER":
        # 1. 检查该教师的所有班级，确保每个班级都有一个关联题库
        class_result = await db.execute(select(Classroom).where(Classroom.teacher_id == user.id))
        teacher_classes = class_result.scalars().all()
        
        for cls in teacher_classes:
            # 检查是否已有该班级的题库
            bank_check = await db.execute(select(QuestionBank).where(QuestionBank.classroom_id == cls.id))
            if not bank_check.scalars().first():
                # 自动补全缺失的题库
                new_bank = QuestionBank(
                    name=f"{cls.name} - 题库",
                    description=f"关联班级：{cls.name}",
                    creator_id=user.id,
                    classroom_id=cls.id
                )
                db.add(new_bank)
        
        await db.commit()

        # 2. 返回该教师创建的所有题库
        result = await db.execute(select(QuestionBank).where(QuestionBank.creator_id == user.id))
    else:
        # 学生：看到自己所在班级的老师创建的题库
        result = await db.execute(
            select(QuestionBank)
            .join(User, QuestionBank.creator_id == User.id)
            .join(Classroom, User.id == Classroom.teacher_id)
            .join(student_classroom, Classroom.id == student_classroom.c.classroom_id)
            .where(student_classroom.c.student_id == user.id)
            .distinct()
        )
    
    banks = result.scalars().all()
    data = []
    for b in banks:
        q_count_res = await db.execute(select(func.count(Question.id)).where(Question.bank_id == b.id))
        q_count = q_count_res.scalar() or 0
        
        progress = 0
        if user.role == "STUDENT":
            # 计算该学生在该题库的进度
            done_count = await db.scalar(
                select(func.sum(PracticeRecord.total_questions))
                .where(PracticeRecord.student_id == user.id)
                .where(PracticeRecord.bank_id == b.id)
            ) or 0
            if q_count > 0:
                progress = min(100, round((done_count / q_count) * 100))

        data.append({
            "id": b.id,
            "name": b.name,
            "questionCount": q_count,
            "description": b.description,
            "courseCode": f"CLASS-{b.classroom_id}" if b.classroom_id else "GENERAL",
            "progress": progress
        })
    return success_response(data=data)

@router.get("/banks/{bank_id}/questions")
async def get_questions(bank_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Question).where(Question.bank_id == bank_id))
    questions = result.scalars().all()
    data = []
    for q in questions:
        data.append({
            "id": q.id,
            "type": q.type,
            "content": q.content,
            "options": json.loads(q.options) if q.options else [],
            "answer": q.answer
        })
    return success_response(data=data)

@router.post("/")
async def create_question(question: QuestionSchema, db: AsyncSession = Depends(get_db)):
    new_q = Question(
        bank_id=question.bank_id,
        type=question.type,
        content=question.content,
        options=json.dumps(question.options) if question.options else "[]",
        answer=question.answer
    )
    db.add(new_q)
    await db.commit()
    await db.refresh(new_q)
    
    # 返回完整对象，方便前端更新列表
    return success_response(data={
        "id": new_q.id,
        "type": new_q.type,
        "content": new_q.content,
        "options": question.options or [],
        "answer": new_q.answer
    }, msg="创建题目成功")

@router.put("/{question_id}")
async def update_question(question_id: int, question: QuestionSchema, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Question).where(Question.id == question_id))
    q = result.scalars().first()
    if not q:
        return error_response(msg="题目不存在")
    
    q.type = question.type
    q.content = question.content
    q.options = json.dumps(question.options) if question.options else "[]"
    q.answer = question.answer
    
    await db.commit()
    return success_response(msg="更新题目成功")

@router.delete("/{question_id}")
async def delete_question(question_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Question).where(Question.id == question_id))
    q = result.scalars().first()
    if q:
        await db.delete(q)
        await db.commit()
    return success_response(msg=f"题目 {question_id} 已删除")

@router.post("/practice/submit")
async def submit_practice(submit: PracticeSubmit, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    new_record = PracticeRecord(
        student_id=user.id,
        bank_id=submit.bank_id,
        total_questions=submit.total_questions,
        correct_count=submit.correct_count,
        score=submit.score
    )
    db.add(new_record)
    
    # 更新用户总积分
    user.points = (user.points or 0) + submit.score
    
    await db.commit()
    return success_response(msg=f"练习结果已保存，积分 +{submit.score}")
