from fastapi import APIRouter, HTTPException, status, UploadFile, File, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, delete, func, update
from database.db import get_db
from database.models import Classroom, User, student_classroom, QuestionBank, Announcement, AttendanceSession, AttendanceRecord, ClassroomJoinedStudent, ClassroomQuestion, QuestionSubmission, Question
from utils.response import success_response, error_response
from utils.auth import get_current_user
from utils.face import extract_face_encoding
import random
import numpy as np
import face_recognition
import json
from datetime import datetime

router = APIRouter(prefix="/classroom", tags=["classroom"])

class CheckinRequest(BaseModel):
    faceData: str

class RandomCallRequest(BaseModel):
    strategy: str  # JOINED, ATTENDANCE, ALL

class RateRequest(BaseModel):
    student_id: str
    score: int

class ClassroomCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    schedule: Optional[str] = ""

class ClassroomUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    schedule: Optional[str] = None

class AddStudentRequest(BaseModel):
    student_id: str

class AnnouncementCreate(BaseModel):
    content: str

class QuestionStartRequest(BaseModel):
    type: str  # BANK or MANUAL
    question_id: Optional[int] = None
    content: Optional[str] = None
    answer: Optional[str] = None

class QuestionSubmitRequest(BaseModel):
    answer: str

@router.get("/list")
async def get_classrooms(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    if user.role == "TEACHER":
        # 教师：返回其创建的班级
        result = await db.execute(select(Classroom).where(Classroom.teacher_id == user.id))
    else:
        # 学生：返回其加入的班级
        result = await db.execute(
            select(Classroom)
            .join(student_classroom, Classroom.id == student_classroom.c.classroom_id)
            .where(student_classroom.c.student_id == user.id)
        )
    
    classes = result.scalars().all()
    data = []
    for c in classes:
        data.append({
            "id": c.id,
            "name": c.name,
            "description": c.description,
            "schedule": c.schedule,
            "student_count": c.student_count
        })
    return success_response(data=data)

@router.post("/{class_id}/add-student")
async def add_student_to_class(class_id: int, request: AddStudentRequest, db: AsyncSession = Depends(get_db)):
    # 1. 查找学生
    result = await db.execute(select(User).where(User.student_id == request.student_id))
    student = result.scalars().first()
    if not student:
        return error_response(msg="找不到该学号的学生")
    
    # 2. 检查是否已在班级中
    check = await db.execute(
        select(student_classroom)
        .where(student_classroom.c.student_id == student.id)
        .where(student_classroom.c.classroom_id == class_id)
    )
    if check.first():
        return error_response(msg="该学生已在班级中")
    
    # 3. 添加关联
    await db.execute(
        insert(student_classroom).values(student_id=student.id, classroom_id=class_id)
    )
    
    # 4. 更新班级人数
    result = await db.execute(select(Classroom).where(Classroom.id == class_id))
    cls = result.scalars().first()
    if cls:
        cls.student_count = (cls.student_count or 0) + 1
        
    await db.commit()
    return success_response(msg="学生添加成功")

@router.get("/{class_id}")
async def get_classroom_details(class_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Classroom, User.name)
        .join(User, Classroom.teacher_id == User.id)
        .where(Classroom.id == class_id)
    )
    row = result.first()
    if not row:
        return error_response(msg="班级不存在")
    
    cls, teacher_name = row
    
    # 计算平均出勤率
    total_sessions = await db.scalar(
        select(func.count(AttendanceSession.id))
        .where(AttendanceSession.classroom_id == class_id)
    ) or 0
    
    total_students = await db.scalar(
        select(func.count(student_classroom.c.student_id))
        .where(student_classroom.c.classroom_id == class_id)
    ) or 0
    
    avg_attendance = "0%"
    if total_sessions > 0 and total_students > 0:
        total_records = await db.scalar(
            select(func.count(AttendanceRecord.id))
            .join(AttendanceSession, AttendanceRecord.session_id == AttendanceSession.id)
            .where(AttendanceSession.classroom_id == class_id)
        ) or 0
        rate = (total_records / (total_sessions * total_students)) * 100
        avg_attendance = f"{rate:.1f}%"

    data = {
        "id": cls.id,
        "name": cls.name,
        "teacher": teacher_name,
        "description": cls.description,
        "schedule": cls.schedule,
        "student_count": total_students,
        "avgAttendance": avg_attendance,
        "is_active": cls.is_active,
        "courseCode": f"CLS-{cls.id:03d}"
    }
    return success_response(data=data)

@router.put("/{class_id}")
async def update_classroom(class_id: int, request: ClassroomUpdate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    result = await db.execute(select(Classroom).where(Classroom.id == class_id))
    cls = result.scalars().first()
    if not cls:
        return error_response(msg="班级不存在")
    
    if cls.teacher_id != user.id:
        return error_response(msg="无权修改此班级")
    
    if request.name is not None:
        cls.name = request.name
    if request.description is not None:
        cls.description = request.description
    if request.schedule is not None:
        cls.schedule = request.schedule
        
    await db.commit()
    return success_response(msg="班级信息更新成功")

@router.get("/{class_id}/announcements")
async def get_announcements(class_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Announcement)
        .where(Announcement.classroom_id == class_id)
        .order_by(Announcement.id.desc())
    )
    announcements = result.scalars().all()
    data = [{"id": a.id, "content": a.content, "date": a.date} for a in announcements]
    return success_response(data=data)

@router.post("/{class_id}/announcements")
async def create_announcement(class_id: int, request: AnnouncementCreate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    # 检查权限
    result = await db.execute(select(Classroom).where(Classroom.id == class_id))
    cls = result.scalars().first()
    if not cls or cls.teacher_id != user.id:
        return error_response(msg="无权发布公告")
    
    new_ann = Announcement(
        classroom_id=class_id,
        content=request.content,
        date=datetime.now().strftime("%Y-%m-%d")
    )
    db.add(new_ann)
    await db.commit()
    await db.refresh(new_ann)
    return success_response(data={"id": new_ann.id, "content": new_ann.content, "date": new_ann.date}, msg="公告发布成功")

@router.delete("/announcements/{ann_id}")
async def delete_announcement(ann_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    result = await db.execute(select(Announcement).where(Announcement.id == ann_id))
    ann = result.scalars().first()
    if not ann:
        return error_response(msg="公告不存在")
    
    # 检查权限（只有该班级的老师可以删除）
    result = await db.execute(select(Classroom).where(Classroom.id == ann.classroom_id))
    cls = result.scalars().first()
    if not cls or cls.teacher_id != user.id:
        return error_response(msg="无权删除此公告")
    
    await db.delete(ann)
    await db.commit()
    return success_response(msg="公告已删除")

@router.delete("/{class_id}/students/{student_id}")
async def remove_student_from_class(class_id: int, student_id: str, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    # 1. 检查权限
    result = await db.execute(select(Classroom).where(Classroom.id == class_id))
    cls = result.scalars().first()
    if not cls or cls.teacher_id != user.id:
        return error_response(msg="无权操作此班级")
    
    # 2. 查找学生内部 ID
    result = await db.execute(select(User).where(User.student_id == student_id))
    student = result.scalars().first()
    if not student:
        return error_response(msg="学生不存在")
    
    # 3. 删除关联
    await db.execute(
        delete(student_classroom)
        .where(student_classroom.c.student_id == student.id)
        .where(student_classroom.c.classroom_id == class_id)
    )
    
    # 4. 更新班级人数
    cls.student_count = max(0, (cls.student_count or 1) - 1)
    
    await db.commit()
    return success_response(msg="学生已从班级移除")

@router.get("/{class_id}/students")
async def get_classroom_students(class_id: int, db: AsyncSession = Depends(get_db)):
    # 真实逻辑：从关联表中查询属于该班级的学生
    result = await db.execute(
        select(User)
        .join(student_classroom, User.id == student_classroom.c.student_id)
        .where(student_classroom.c.classroom_id == class_id)
    )
    students = result.scalars().all()
    
    # 如果班级里还没学生，返回空列表
    if not students:
        return success_response(data=[])

    # 获取该班级总签到次数
    total_sessions = await db.scalar(
        select(func.count(AttendanceSession.id))
        .where(AttendanceSession.classroom_id == class_id)
    ) or 0

    # 获取当前活跃会话
    active_session_result = await db.execute(
        select(AttendanceSession)
        .where(AttendanceSession.classroom_id == class_id)
        .where(AttendanceSession.status == "OPEN")
    )
    active_session = active_session_result.scalars().first()

    data = []
    for s in students:
        # 获取每个学生的总签到次数
        student_attendance = await db.scalar(
            select(func.count(AttendanceRecord.id))
            .join(AttendanceSession, AttendanceRecord.session_id == AttendanceSession.id)
            .where(AttendanceSession.classroom_id == class_id)
            .where(AttendanceRecord.student_id == s.id)
        ) or 0

        # 检查当前活跃会话是否已签到
        is_signed = False
        if active_session:
            record_check = await db.execute(
                select(AttendanceRecord)
                .where(AttendanceRecord.session_id == active_session.id)
                .where(AttendanceRecord.student_id == s.id)
            )
            is_signed = record_check.scalars().first() is not None

        data.append({
            "id": s.id,
            "student_id": s.student_id,
            "name": s.name,
            "attendanceCount": student_attendance,
            "totalSessions": total_sessions,
            "signed": is_signed,
            "rating": "-"
        })
    return success_response(data=data)

@router.post("/create")
async def create_classroom(request: ClassroomCreate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    # 1. 创建班级
    new_class = Classroom(
        name=request.name,
        description=request.description,
        schedule=request.schedule,
        teacher_id=user.id
    )
    db.add(new_class)
    await db.flush() # 获取 new_class.id
    
    # 2. 自动创建一个关联题库
    new_bank = QuestionBank(
        name=f"{request.name} - 题库",
        description=f"关联班级：{request.name}",
        creator_id=user.id,
        classroom_id=new_class.id
    )
    db.add(new_bank)
    
    await db.commit()
    await db.refresh(new_class)
    
    data = {
        "id": new_class.id,
        "name": new_class.name,
        "description": new_class.description,
        "schedule": new_class.schedule
    }
    return success_response(data=data, msg="班级及关联题库创建成功")

@router.post("/{class_id}/start")
async def start_class(class_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    result = await db.execute(select(Classroom).where(Classroom.id == class_id))
    cls = result.scalars().first()
    if not cls or cls.teacher_id != user.id:
        return error_response(msg="无权开始上课")
    
    cls.is_active = 1
    await db.commit()
    return success_response(msg="已开始上课")

@router.post("/{class_id}/stop")
async def stop_class(class_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    result = await db.execute(select(Classroom).where(Classroom.id == class_id))
    cls = result.scalars().first()
    if not cls or cls.teacher_id != user.id:
        return error_response(msg="无权结束上课")
    
    cls.is_active = 0
    # 结束上课时清空已进入课堂的学生
    await db.execute(delete(ClassroomJoinedStudent).where(ClassroomJoinedStudent.classroom_id == class_id))
    # 同时关闭可能存在的签到
    await db.execute(
        update(AttendanceSession)
        .where(AttendanceSession.classroom_id == class_id)
        .where(AttendanceSession.status == "OPEN")
        .values(status="CLOSED")
    )
    await db.commit()
    return success_response(msg="已结束上课")

@router.post("/{class_id}/join")
async def join_classroom(class_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    # 检查是否已经在里面了
    result = await db.execute(
        select(ClassroomJoinedStudent)
        .where(ClassroomJoinedStudent.classroom_id == class_id)
        .where(ClassroomJoinedStudent.student_id == user.id)
    )
    if result.scalars().first():
        return success_response(msg="已在教室内")
    
    joined = ClassroomJoinedStudent(classroom_id=class_id, student_id=user.id)
    db.add(joined)
    await db.commit()
    return success_response(msg="已进入教室")

@router.post("/{class_id}/leave")
async def leave_classroom(class_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    await db.execute(
        delete(ClassroomJoinedStudent)
        .where(ClassroomJoinedStudent.classroom_id == class_id)
        .where(ClassroomJoinedStudent.student_id == user.id)
    )
    await db.commit()
    return success_response(msg="已离开教室")

@router.get("/{class_id}/joined_students")
async def get_joined_students(class_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(User)
        .join(ClassroomJoinedStudent, User.id == ClassroomJoinedStudent.student_id)
        .where(ClassroomJoinedStudent.classroom_id == class_id)
    )
    students = result.scalars().all()
    data = [{"id": s.id, "name": s.name, "student_id": s.student_id} for s in students]
    return success_response(data=data)

@router.post("/{class_id}/attendance/start")
async def start_attendance(class_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    # 1. 检查权限
    result = await db.execute(select(Classroom).where(Classroom.id == class_id))
    cls = result.scalars().first()
    if not cls or cls.teacher_id != user.id:
        return error_response(msg="无权启动签到")
    
    # 2. 关闭该班级之前可能未关闭的签到
    await db.execute(
        update(AttendanceSession)
        .where(AttendanceSession.classroom_id == class_id)
        .where(AttendanceSession.status == "OPEN")
        .values(status="CLOSED")
    )
    
    # 3. 创建新签到
    new_session = AttendanceSession(classroom_id=class_id, status="OPEN")
    db.add(new_session)
    await db.commit()
    return success_response(msg="签到已开始")

@router.get("/{class_id}/attendance/status")
async def get_attendance_status(class_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    # 1. 检查是否有正在进行的点名
    cls_result = await db.execute(select(Classroom).where(Classroom.id == class_id))
    cls = cls_result.scalars().first()
    
    if cls and cls.active_call_student_id:
        # 如果当前用户就是被点名的学生
        if user.id == cls.active_call_student_id:
            return success_response(data={"status": "CALLED"})
    
    # 2. 获取当前活跃的签到
    result = await db.execute(
        select(AttendanceSession)
        .where(AttendanceSession.classroom_id == class_id)
        .where(AttendanceSession.status == "OPEN")
    )
    session = result.scalars().first()
    
    if not session:
        return success_response(data={"status": "IDLE", "count": 0, "total": 0})
    
    # 获取已签到人数
    count = await db.scalar(
        select(func.count(AttendanceRecord.id))
        .where(AttendanceRecord.session_id == session.id)
    ) or 0
    
    # 获取班级总人数
    total = await db.scalar(
        select(func.count(student_classroom.c.student_id))
        .where(student_classroom.c.classroom_id == class_id)
    ) or 0
    
    return success_response(data={
        "status": "ATTENDANCE",
        "count": count,
        "total": total,
        "session_id": session.id
    })

@router.post("/{class_id}/call/random")
async def random_call(class_id: int, request: RandomCallRequest, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    # 1. 检查权限
    cls_result = await db.execute(select(Classroom).where(Classroom.id == class_id))
    cls = cls_result.scalars().first()
    if not cls or cls.teacher_id != user.id:
        return error_response(msg="无权发起点名")
    
    # 2. 根据策略获取候选学生
    candidates = []
    if request.strategy == "JOINED":
        # 已进入课堂的学生
        result = await db.execute(
            select(User)
            .join(ClassroomJoinedStudent, User.id == ClassroomJoinedStudent.student_id)
            .where(ClassroomJoinedStudent.classroom_id == class_id)
        )
        candidates = result.scalars().all()
    elif request.strategy == "ALL":
        # 全体学生
        result = await db.execute(
            select(User)
            .join(student_classroom, User.id == student_classroom.c.student_id)
            .where(student_classroom.c.classroom_id == class_id)
        )
        candidates = result.scalars().all()
    elif request.strategy == "ATTENDANCE":
        # 策略：优先点名出勤率低的学生
        # 1. 获取该班级所有学生
        all_students_result = await db.execute(
            select(User)
            .join(student_classroom, User.id == student_classroom.c.student_id)
            .where(student_classroom.c.classroom_id == class_id)
        )
        all_students = all_students_result.scalars().all()
        
        if not all_students:
            return error_response(msg="班级内没有学生")

        # 2. 计算每个学生的出勤次数
        student_stats = []
        for s in all_students:
            count = await db.scalar(
                select(func.count(AttendanceRecord.id))
                .join(AttendanceSession, AttendanceRecord.session_id == AttendanceSession.id)
                .where(AttendanceSession.classroom_id == class_id)
                .where(AttendanceRecord.student_id == s.id)
            ) or 0
            student_stats.append((s, count))
        
        # 3. 找出出勤次数最少的学生（可能有多个）
        min_count = min(s[1] for s in student_stats)
        candidates = [s[0] for s in student_stats if s[1] == min_count]
    
    if not candidates:
        return error_response(msg="没有符合条件的学生")
    
    # 3. 随机选择一个
    lucky_student = random.choice(candidates)
    cls.active_call_student_id = lucky_student.id
    await db.commit()
    
    return success_response(data={
        "id": lucky_student.id,
        "name": lucky_student.name,
        "student_id": lucky_student.student_id
    }, msg="点名成功")

@router.post("/{class_id}/call/reset")
async def reset_call(class_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    cls_result = await db.execute(select(Classroom).where(Classroom.id == class_id))
    cls = cls_result.scalars().first()
    if cls:
        cls.active_call_student_id = None
        await db.commit()
    return success_response(msg="已重置点名状态")

@router.post("/{class_id}/attendance/checkin")
async def student_checkin(class_id: int, request: CheckinRequest, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    # 1. 获取当前活跃签到
    result = await db.execute(
        select(AttendanceSession)
        .where(AttendanceSession.classroom_id == class_id)
        .where(AttendanceSession.status == "OPEN")
    )
    session = result.scalars().first()
    if not session:
        return error_response(msg="当前没有正在进行的签到")
    
    # 2. 检查是否已签到
    result = await db.execute(
        select(AttendanceRecord)
        .where(AttendanceRecord.session_id == session.id)
        .where(AttendanceRecord.student_id == user.id)
    )
    if result.scalars().first():
        return error_response(msg="您已完成签到")
    
    # 3. 人脸识别验证
    if not user.face_features:
        return error_response(msg="您尚未录入人脸信息，请先在个人资料页录入")
    
    # 提取当前上传的人脸特征
    target_encoding = extract_face_encoding(request.faceData)
    if not target_encoding:
        return error_response(msg="未能识别到人脸，请重试")
    
    try:
        # 解析数据库中的特征
        stored_features = json.loads(user.face_features)
        user_encoding = np.array(stored_features)
        target_encoding = np.array(target_encoding)
        
        # 比对
        matches = face_recognition.compare_faces([user_encoding], target_encoding, tolerance=0.4)
        if not matches[0]:
            return error_response(msg="人脸比对失败，请确保是本人签到")
            
    except Exception as e:
        print(f"Checkin face comparison error: {e}")
        return error_response(msg="人脸识别服务异常")

    # 4. 记录签到
    record = AttendanceRecord(session_id=session.id, student_id=user.id)
    db.add(record)
    
    # 签到奖励积分
    user.points = (user.points or 0) + 2
    
    await db.commit()
    return success_response(msg="签到成功，积分+2")

@router.post("/{class_id}/attendance/stop")
async def stop_attendance(class_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    # 1. 检查权限
    result = await db.execute(select(Classroom).where(Classroom.id == class_id))
    cls = result.scalars().first()
    if not cls or cls.teacher_id != user.id:
        return error_response(msg="无权停止签到")
    
    # 2. 关闭签到
    await db.execute(
        update(AttendanceSession)
        .where(AttendanceSession.classroom_id == class_id)
        .where(AttendanceSession.status == "OPEN")
        .values(status="CLOSED")
    )
    await db.commit()
    return success_response(msg="签到已结束")

@router.post("/call/rate")
async def rate_student(request: RateRequest, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    if user.role != "TEACHER":
        return error_response(msg="只有教师可以评分")
    
    # 查找学生
    result = await db.execute(select(User).where(User.student_id == request.student_id))
    student = result.scalars().first()
    if not student:
        return error_response(msg="找不到该学生")
    
    # 更新积分
    student.points = (student.points or 0) + request.score
    await db.commit()
    
    return success_response(msg=f"已为 {student.name} 评分: {request.score}")

@router.post("/{class_id}/question/start")
async def start_question(class_id: int, request: QuestionStartRequest, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    # 1. 检查权限
    result = await db.execute(select(Classroom).where(Classroom.id == class_id))
    cls = result.scalars().first()
    if not cls or cls.teacher_id != user.id:
        return error_response(msg="无权发起提问")
    
    # 2. 关闭该班级之前可能未关闭的提问
    await db.execute(
        update(ClassroomQuestion)
        .where(ClassroomQuestion.classroom_id == class_id)
        .where(ClassroomQuestion.status == "OPEN")
        .values(status="CLOSED")
    )
    
    # 3. 创建新提问
    new_q = ClassroomQuestion(
        classroom_id=class_id,
        type=request.type,
        question_id=request.question_id,
        content=request.content,
        answer=request.answer,
        status="OPEN"
    )
    
    # 如果是从题库选择，获取题库中的答案
    if request.type == "BANK" and request.question_id:
        q_result = await db.execute(select(Question).where(Question.id == request.question_id))
        q_obj = q_result.scalars().first()
        if q_obj:
            new_q.answer = q_obj.answer
            new_q.content = q_obj.content

    db.add(new_q)
    await db.commit()
    return success_response(msg="提问已开始")

@router.get("/{class_id}/question/status")
async def get_question_status(class_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    # 获取当前活跃的提问
    result = await db.execute(
        select(ClassroomQuestion)
        .where(ClassroomQuestion.classroom_id == class_id)
        .where(ClassroomQuestion.status == "OPEN")
    )
    q = result.scalars().first()
    
    if not q:
        return success_response(data={"status": "IDLE"})
    
    # 获取已提交人数
    submissions_result = await db.execute(
        select(QuestionSubmission)
        .join(User, QuestionSubmission.student_id == User.id)
        .where(QuestionSubmission.question_id == q.id)
    )
    submissions = submissions_result.scalars().all()
    
    # 如果是教师，返回详细统计
    if user.role == "TEACHER":
        data = {
            "status": "QUESTIONING",
            "type": q.type,
            "content": q.content,
            "submitted_count": len(submissions),
            "submissions": []
        }
        
        if q.type == "BANK":
            correct_count = sum(1 for s in submissions if s.is_correct == 1)
            data["accuracy"] = round(correct_count / len(submissions) * 100, 1) if submissions else 0
            
            # 统计各选项分布 (假设是选择题)
            options_stats = {}
            for s in submissions:
                options_stats[s.answer] = options_stats.get(s.answer, 0) + 1
            data["options_stats"] = options_stats
        else:
            # 手动提问，返回学生名单
            for s in submissions:
                # 需要重新查询以获取学生姓名
                s_user_result = await db.execute(select(User).where(User.id == s.student_id))
                s_user = s_user_result.scalars().first()
                data["submissions"].append({
                    "student_name": s_user.name if s_user else "未知",
                    "answer": s.answer,
                    "submit_time": s.submit_time.strftime("%H:%M:%S")
                })
        
        return success_response(data=data)
    else:
        # 如果是学生，检查是否已提交
        my_submission = await db.execute(
            select(QuestionSubmission)
            .where(QuestionSubmission.question_id == q.id)
            .where(QuestionSubmission.student_id == user.id)
        )
        has_submitted = my_submission.scalars().first() is not None
        
        return success_response(data={
            "status": "QUESTIONING",
            "type": q.type,
            "content": q.content,
            "has_submitted": has_submitted,
            "question_id": q.id
        })

@router.post("/{class_id}/question/submit")
async def submit_question_answer(class_id: int, request: QuestionSubmitRequest, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    # 1. 获取当前活跃提问
    result = await db.execute(
        select(ClassroomQuestion)
        .where(ClassroomQuestion.classroom_id == class_id)
        .where(ClassroomQuestion.status == "OPEN")
    )
    q = result.scalars().first()
    if not q:
        return error_response(msg="当前没有正在进行的提问")
    
    # 2. 检查是否已提交
    check = await db.execute(
        select(QuestionSubmission)
        .where(QuestionSubmission.question_id == q.id)
        .where(QuestionSubmission.student_id == user.id)
    )
    if check.scalars().first():
        return error_response(msg="您已提交过答案")
    
    # 3. 记录提交
    is_correct = None
    if q.type == "BANK" and q.answer:
        is_correct = 1 if request.answer.strip().upper() == q.answer.strip().upper() else 0
    
    submission = QuestionSubmission(
        question_id=q.id,
        student_id=user.id,
        answer=request.answer,
        is_correct=is_correct
    )
    db.add(submission)

    # 提问奖励积分
    if is_correct == 1:
        user.points = (user.points or 0) + 5
    elif q.type == "MANUAL":
        user.points = (user.points or 0) + 2 # 手动提问只要回答就给2分

    await db.commit()
    return success_response(msg="提交成功")

@router.post("/{class_id}/question/stop")
async def stop_question(class_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    # 1. 检查权限
    result = await db.execute(select(Classroom).where(Classroom.id == class_id))
    cls = result.scalars().first()
    if not cls or cls.teacher_id != user.id:
        return error_response(msg="无权停止提问")
    
    # 2. 关闭提问
    await db.execute(
        update(ClassroomQuestion)
        .where(ClassroomQuestion.classroom_id == class_id)
        .where(ClassroomQuestion.status == "OPEN")
        .values(status="CLOSED")
    )
    await db.commit()
    return success_response(msg="提问已结束")

@router.delete("/{class_id}")
async def delete_classroom(class_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    # 1. 检查权限
    result = await db.execute(select(Classroom).where(Classroom.id == class_id))
    cls = result.scalars().first()
    if not cls:
        return error_response(msg="班级不存在")
    if cls.teacher_id != user.id:
        return error_response(msg="无权删除此班级")
    
    # 2. 删除相关数据 (级联删除在某些数据库配置中可能自动完成，但这里我们手动处理一些关键关联)
    # 删除学生关联
    await db.execute(delete(student_classroom).where(student_classroom.c.classroom_id == class_id))
    # 删除公告
    await db.execute(delete(Announcement).where(Announcement.classroom_id == class_id))
    # 删除签到会话和记录
    sessions_res = await db.execute(select(AttendanceSession.id).where(AttendanceSession.classroom_id == class_id))
    session_ids = [r[0] for r in sessions_res.all()]
    if session_ids:
        await db.execute(delete(AttendanceRecord).where(AttendanceRecord.session_id.in_(session_ids)))
        await db.execute(delete(AttendanceSession).where(AttendanceSession.id.in_(session_ids)))
    
    # 删除课堂提问和提交
    questions_res = await db.execute(select(ClassroomQuestion.id).where(ClassroomQuestion.classroom_id == class_id))
    question_ids = [r[0] for r in questions_res.all()]
    if question_ids:
        await db.execute(delete(QuestionSubmission).where(QuestionSubmission.question_id.in_(question_ids)))
        await db.execute(delete(ClassroomQuestion).where(ClassroomQuestion.id.in_(question_ids)))

    # 删除题库关联 (如果有)
    await db.execute(update(QuestionBank).where(QuestionBank.classroom_id == class_id).values(classroom_id=None))

    # 3. 删除班级本身
    await db.delete(cls)
    await db.commit()
    return success_response(msg="班级已成功删除")
