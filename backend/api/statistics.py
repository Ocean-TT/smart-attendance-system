from fastapi import APIRouter, Depends
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from database.db import get_db
from database.models import User, Classroom, PracticeRecord, AttendanceRecord, AttendanceSession, student_classroom, QuestionSubmission, ClassroomQuestion, QuestionBank, Question
from utils.response import success_response, error_response
from utils.auth import get_current_user

router = APIRouter(prefix="/stats", tags=["statistics"])

@router.get("/student/{student_id}")
async def get_student_stats(student_id: str, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    # 尝试查找该学生
    result = await db.execute(select(User).where(User.student_id == student_id))
    target_user = result.scalars().first()
    
    if not target_user:
        return error_response(msg="找不到该学生")

    # 1. 获取练习统计
    practice_stats = await db.execute(
        select(
            func.count(PracticeRecord.id),
            func.sum(PracticeRecord.total_questions),
            func.sum(PracticeRecord.correct_count),
            func.sum(PracticeRecord.score)
        ).where(PracticeRecord.student_id == target_user.id)
    )
    p_count, total_q, total_c, total_p_score = practice_stats.first()
    
    p_count = p_count or 0
    total_q = total_q or 0
    total_c = total_c or 0
    total_p_score = total_p_score or 0
    accuracy_val = f"{round((total_c / total_q) * 100)}%" if total_q > 0 else "0%"

    # 2. 获取出勤统计
    # 获取学生加入的所有班级 ID
    class_ids_result = await db.execute(
        select(student_classroom.c.classroom_id)
        .where(student_classroom.c.student_id == target_user.id)
    )
    class_ids = [r[0] for r in class_ids_result.all()]

    # 获取这些班级的所有签到会话总数
    required_count = 0
    if class_ids:
        required_count = await db.scalar(
            select(func.count(AttendanceSession.id))
            .where(AttendanceSession.classroom_id.in_(class_ids))
        ) or 0

    # 获取该学生已签到的次数
    attendance_count = await db.scalar(
        select(func.count(AttendanceRecord.id))
        .where(AttendanceRecord.student_id == target_user.id)
    ) or 0

    absent_count = max(0, required_count - attendance_count)
    attendance_rate = f"{round((attendance_count / required_count) * 100)}%" if required_count > 0 else "0%"

    # 计算实时总积分 (签到2分 + 提问得分 + 练习得分)
    # 1. 签到积分
    total_points = attendance_count * 2
    # 2. 练习积分
    total_points += total_p_score
    # 3. 课堂提问积分
    question_subs = await db.execute(
        select(QuestionSubmission, ClassroomQuestion.type)
        .join(ClassroomQuestion, QuestionSubmission.question_id == ClassroomQuestion.id)
        .where(QuestionSubmission.student_id == target_user.id)
    )
    for sub, q_type in question_subs.all():
        if sub.is_correct == 1:
            total_points += 5
        elif q_type == "MANUAL":
            total_points += 2
    
    # 同步更新到用户表，确保一致性
    if target_user.points != total_points:
        target_user.points = total_points
        await db.commit()

    # 3. 获取最近表现记录 (签到和提问)
    history = []
    
    # 获取最近 5 次签到
    attendance_history_result = await db.execute(
        select(AttendanceRecord, Classroom.name)
        .join(AttendanceSession, AttendanceRecord.session_id == AttendanceSession.id)
        .join(Classroom, AttendanceSession.classroom_id == Classroom.id)
        .where(AttendanceRecord.student_id == target_user.id)
        .order_by(AttendanceRecord.check_in_time.desc())
        .limit(5)
    )
    for rec, cls_name in attendance_history_result.all():
        history.append({
            "date": rec.check_in_time.strftime("%Y-%m-%d"),
            "event": f"课堂签到: {cls_name}",
            "points": 2,
            "status": "正常"
        })

    # 获取最近 5 次课堂提问提交
    question_history_result = await db.execute(
        select(QuestionSubmission, Classroom.name)
        .join(ClassroomQuestion, QuestionSubmission.question_id == ClassroomQuestion.id)
        .join(Classroom, ClassroomQuestion.classroom_id == Classroom.id)
        .where(QuestionSubmission.student_id == target_user.id)
        .order_by(QuestionSubmission.submit_time.desc())
        .limit(5)
    )
    for sub, cls_name in question_history_result.all():
        pts = 5 if sub.is_correct == 1 else (2 if sub.is_correct is None else 0)
        history.append({
            "date": sub.submit_time.strftime("%Y-%m-%d"),
            "event": f"课堂提问: {cls_name}",
            "points": pts,
            "status": "正确" if sub.is_correct == 1 else ("已提交" if sub.is_correct is None else "错误")
        })

    # 按时间排序
    history.sort(key=lambda x: x["date"], reverse=True)

    # 4. 获取本月出勤日历数据
    from datetime import datetime, timedelta
    now = datetime.now()
    first_day = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if now.month == 12:
        last_day = now.replace(year=now.year + 1, month=1, day=1) - timedelta(seconds=1)
    else:
        last_day = now.replace(month=now.month + 1, day=1) - timedelta(seconds=1)

    calendar_data = {}
    if class_ids:
        # 获取本月所有签到会话
        sessions_result = await db.execute(
            select(AttendanceSession, Classroom.name)
            .join(Classroom, AttendanceSession.classroom_id == Classroom.id)
            .where(AttendanceSession.classroom_id.in_(class_ids))
            .where(AttendanceSession.start_time >= first_day)
            .where(AttendanceSession.start_time <= last_day)
        )
        sessions = sessions_result.all()

        # 获取本月所有签到记录
        records_result = await db.execute(
            select(AttendanceRecord.session_id)
            .where(AttendanceRecord.student_id == target_user.id)
            .where(AttendanceRecord.check_in_time >= first_day)
            .where(AttendanceRecord.check_in_time <= last_day)
        )
        attended_session_ids = {r[0] for r in records_result.all()}

        now_date = now.date()
        for sess, cls_name in sessions:
            sess_date = sess.start_time.date()
            date_str = sess_date.strftime("%Y-%m-%d")
            
            if date_str not in calendar_data:
                # 初始状态：过去日期默认为绿色(全勤)，今天及未来默认为无色
                status = "green" if sess_date < now_date else ""
                calendar_data[date_str] = {"status": status, "courses": []}
            
            is_attended = sess.id in attended_session_ids
            calendar_data[date_str]["courses"].append({
                "name": cls_name,
                "attended": is_attended,
                "time": sess.start_time.strftime("%H:%M")
            })
            
            # 核心逻辑修改：只要课程开始时间已过且未签到，该天即标记为红色
            if sess.start_time < now and not is_attended:
                calendar_data[date_str]["status"] = "red"

    # 5. 构造返回数据
    data = {
        "attendanceRate": attendance_rate,
        "totalPoints": total_points,
        "practicedCount": total_q,
        "accuracy": accuracy_val,
        "attendanceCount": attendance_count,
        "requiredCount": required_count,
        "absentCount": absent_count,
        "history": history[:10],
        "calendarData": calendar_data
    }
        
    return success_response(data=data)

@router.get("/teacher/overview")
async def get_teacher_overview(class_id: Optional[int] = None, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    # 1. 获取该教师管理的所有班级
    result = await db.execute(select(Classroom).where(Classroom.teacher_id == user.id))
    classrooms = result.scalars().all()
    
    if not classrooms:
        return success_response(data={
            "avgAttendance": "0%",
            "completionRate": "0%",
            "activityIndex": 0,
            "classComparison": [],
            "rankings": [],
            "studentList": [],
            "classrooms": []
        })

    # 如果没有指定 class_id，默认选择第一个班级
    if class_id is None:
        class_id = classrooms[0].id

    # 2. 计算选中班级的统计数据
    selected_class = next((c for c in classrooms if c.id == class_id), classrooms[0])
    
    # 出勤率计算
    session_count = await db.scalar(
        select(func.count(AttendanceSession.id))
        .where(AttendanceSession.classroom_id == selected_class.id)
    ) or 0
    total_required = session_count * (selected_class.student_count or 0)
    total_actual = await db.scalar(
        select(func.count(AttendanceRecord.id))
        .join(AttendanceSession, AttendanceRecord.session_id == AttendanceSession.id)
        .where(AttendanceSession.classroom_id == selected_class.id)
    ) or 0
    attendance_rate = (total_actual / total_required * 100) if total_required > 0 else 0

    # 题库完成率计算
    bank_result = await db.execute(select(QuestionBank).where(QuestionBank.classroom_id == selected_class.id))
    bank = bank_result.scalars().first()
    completion_rate = 0
    q_count = 0
    if bank:
        q_count = await db.scalar(select(func.count(Question.id)).where(Question.bank_id == bank.id)) or 0
        if q_count > 0:
            # 获取该班级所有学生
            student_ids_res = await db.execute(
                select(student_classroom.c.student_id)
                .where(student_classroom.c.classroom_id == selected_class.id)
            )
            student_ids = [r[0] for r in student_ids_res.all()]
            
            if student_ids:
                # 计算每个学生的完成量
                done_counts_res = await db.execute(
                    select(PracticeRecord.student_id, func.sum(PracticeRecord.total_questions))
                    .where(PracticeRecord.student_id.in_(student_ids))
                    .where(PracticeRecord.bank_id == bank.id)
                    .group_by(PracticeRecord.student_id)
                )
                done_counts = {r[0]: r[1] for r in done_counts_res.all()}
                
                total_progress = 0
                for sid in student_ids:
                    s_done = done_counts.get(sid, 0)
                    total_progress += min(100, (s_done / q_count) * 100)
                completion_rate = total_progress / len(student_ids)

    # 学习活跃度指数计算 (出勤40% + 完成率40% + 积分表现20%)
    # 获取平均积分
    avg_points = await db.scalar(
        select(func.avg(User.points))
        .join(student_classroom, User.id == student_classroom.c.student_id)
        .where(student_classroom.c.classroom_id == selected_class.id)
    ) or 0
    normalized_points = min(100, (avg_points / 50) * 100) # 假设50分为满分基准
    activity_index = (attendance_rate * 0.4) + (completion_rate * 0.4) + (normalized_points * 0.2)

    # 3. 计算本周积分 (用于状态判定)
    from datetime import datetime, timedelta
    now = datetime.now()
    week_start = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
    
    # 获取该班级所有学生 ID
    student_ids_res = await db.execute(
        select(student_classroom.c.student_id)
        .where(student_classroom.c.classroom_id == selected_class.id)
    )
    student_ids = [r[0] for r in student_ids_res.all()]
    
    weekly_points_map = {sid: 0 for sid in student_ids}
    if student_ids:
        # 本周签到积分
        att_weekly = await db.execute(
            select(AttendanceRecord.student_id, func.count(AttendanceRecord.id))
            .where(AttendanceRecord.student_id.in_(student_ids))
            .where(AttendanceRecord.check_in_time >= week_start)
            .group_by(AttendanceRecord.student_id)
        )
        for sid, count in att_weekly.all():
            weekly_points_map[sid] += count * 2
            
        # 本周练习积分
        prac_weekly = await db.execute(
            select(PracticeRecord.student_id, func.sum(PracticeRecord.score))
            .where(PracticeRecord.student_id.in_(student_ids))
            .where(PracticeRecord.created_at >= week_start)
            .group_by(PracticeRecord.student_id)
        )
        for sid, score in prac_weekly.all():
            weekly_points_map[sid] += (score or 0)
            
        # 本周课堂提问积分
        ques_weekly = await db.execute(
            select(QuestionSubmission.student_id, QuestionSubmission.is_correct, ClassroomQuestion.type)
            .join(ClassroomQuestion, QuestionSubmission.question_id == ClassroomQuestion.id)
            .where(QuestionSubmission.student_id.in_(student_ids))
            .where(QuestionSubmission.submit_time >= week_start)
        )
        for sid, is_correct, q_type in ques_weekly.all():
            if is_correct == 1:
                weekly_points_map[sid] += 5
            elif q_type == "MANUAL":
                weekly_points_map[sid] += 2

    # 4. 获取学生列表
    students_query = (
        select(User, func.count(AttendanceRecord.id).label("att_count"))
        .join(student_classroom, User.id == student_classroom.c.student_id)
        .outerjoin(AttendanceRecord, User.id == AttendanceRecord.student_id)
        .where(student_classroom.c.classroom_id == selected_class.id)
        .group_by(User.id)
        .order_by(User.points.desc())
    )
    
    students_result = await db.execute(students_query)
    students_data = students_result.all()
    
    # 获取该班级的总签到会话数
    total_sessions = session_count

    student_list = []
    for s, att_count in students_data:
        att_rate_val = (att_count / total_sessions * 100) if total_sessions > 0 else 0
        
        # 单个学生的题库完成率
        s_completion = 0
        if bank and q_count > 0:
            s_done = await db.scalar(
                select(func.sum(PracticeRecord.total_questions))
                .where(PracticeRecord.student_id == s.id)
                .where(PracticeRecord.bank_id == bank.id)
            ) or 0
            s_completion = min(100, round((s_done / q_count) * 100))

        weekly_pts = weekly_points_map.get(s.id, 0)
        student_list.append({
            "id": s.id,
            "student_id": s.student_id,
            "name": s.name,
            "points": s.points or 0,
            "weeklyPoints": weekly_pts,
            "attendanceRate": f"{round(att_rate_val)}%",
            "completionRate": f"{round(s_completion)}%",
            "status": "优秀" if weekly_pts >= 10 else ("良好" if weekly_pts >= 4 else "待改进")
        })

    # 5. 最近课堂详情
    recent_sessions_query = (
        select(AttendanceSession, Classroom.name, Classroom.student_count)
        .join(Classroom, AttendanceSession.classroom_id == Classroom.id)
        .where(Classroom.teacher_id == user.id)
    )
    if class_id:
        recent_sessions_query = recent_sessions_query.where(Classroom.id == class_id)
    
    recent_sessions_query = recent_sessions_query.order_by(AttendanceSession.start_time.desc()).limit(6)
    recent_sessions_result = await db.execute(recent_sessions_query)
    recent_sessions_data = []
    
    for sess, cls_name, total_students in recent_sessions_result.all():
        attended_count = await db.scalar(
            select(func.count(AttendanceRecord.id))
            .where(AttendanceRecord.session_id == sess.id)
        ) or 0
        recent_sessions_data.append({
            "id": sess.id,
            "className": cls_name,
            "date": sess.start_time.strftime("%m-%d %H:%M"),
            "attendedCount": attended_count,
            "totalCount": total_students or 0,
            "rate": round((attended_count / (total_students or 1) * 100)) if total_students else 0
        })

    data = {
        "avgAttendance": f"{round(attendance_rate)}%",
        "completionRate": f"{round(completion_rate)}%",
        "activityIndex": round(activity_index),
        "recentSessions": recent_sessions_data,
        "rankings": student_list[:10],
        "studentList": student_list,
        "classrooms": [{"id": c.id, "name": c.name} for c in classrooms]
    }
    return success_response(data=data)

