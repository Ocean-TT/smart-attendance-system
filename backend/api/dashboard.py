from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from database.db import get_db
from database.models import User, Classroom, QuestionBank, Question, student_classroom
from utils.response import success_response
from utils.auth import get_current_user
from typing import Optional
from datetime import datetime, timedelta

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

def get_next_course_info(classrooms):
    now = datetime.now()
    current_weekday = now.weekday()  # 0-6 (Mon-Sun)
    current_time = now.strftime("%H:%M")
    
    weekday_map = {"周一": 0, "周二": 1, "周三": 2, "周四": 3, "周五": 4, "周六": 5, "周日": 6}
    
    upcoming = []
    for cls in classrooms:
        if not cls.schedule:
            continue
        
        # 支持逗号分隔的多节课逻辑
        schedules = [s.strip() for s in cls.schedule.replace('，', ',').split(',')]
        for s in schedules:
            try:
                parts = s.split(' ')
                if len(parts) < 2: continue
                day_str = parts[0]
                time_range = parts[1]
                start_time = time_range.split('-')[0]
                
                target_weekday = weekday_map.get(day_str)
                if target_weekday is None: continue
                
                days_diff = (target_weekday - current_weekday) % 7
                # 如果是今天但上课时间已过，则看下周的这一天
                if days_diff == 0 and start_time < current_time:
                    days_diff = 7
                
                upcoming.append({
                    "name": cls.name,
                    "schedule": s,
                    "days_diff": days_diff,
                    "start_time": start_time
                })
            except:
                continue
    
    if not upcoming:
        return None
    
    upcoming.sort(key=lambda x: (x['days_diff'], x['start_time']))
    return upcoming[0]

@router.get("/overview")
async def dashboard_overview(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    if user.role == "TEACHER":
        # 教师：统计自己创建的班级和学生总数
        class_result = await db.execute(select(Classroom).where(Classroom.teacher_id == user.id))
        all_classes = class_result.scalars().all()
        
        class_count = len(all_classes)
        student_count = sum(c.student_count for c in all_classes)
        
        # 统计题库题目总数
        practice_count = await db.scalar(
            select(func.count(Question.id))
            .join(QuestionBank, Question.bank_id == QuestionBank.id)
            .where(QuestionBank.creator_id == user.id)
        ) or 0

        # 计算下节课程
        next_course = get_next_course_info(all_classes)

        data = {
            "classCount": class_count,
            "studentCount": student_count,
            "accuracy": 0,
            "practiceCount": practice_count,
            "nextCourse": next_course
        }
    else:
        # 学生：查询关联表中的班级数量
        class_count = await db.scalar(
            select(func.count(student_classroom.c.classroom_id))
            .where(student_classroom.c.student_id == user.id)
        )
        
        # 查询正在上课的班级
        active_classes_result = await db.execute(
            select(Classroom)
            .join(student_classroom, Classroom.id == student_classroom.c.classroom_id)
            .where(student_classroom.c.student_id == user.id)
            .where(Classroom.is_active == 1)
        )
        active_classes = active_classes_result.scalars().all()
        
        data = {
            "classCount": class_count,
            "accuracy": 0,
            "practiceCount": 0,
            "totalPoints": user.points or 0,
            "activeClasses": [{"id": c.id, "name": c.name} for c in active_classes]
        }
    return success_response(data=data)
