from sqlalchemy import Column, Integer, String, ForeignKey, Text, Float, DateTime, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from .db import Base

# 学生与班级的关联表
student_classroom = Table(
    "student_classroom",
    Base.metadata,
    Column("student_id", Integer, ForeignKey("users.id")),
    Column("classroom_id", Integer, ForeignKey("classrooms.id"))
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)  # 实际项目中应存储哈希值
    name = Column(String)
    role = Column(String)  # STUDENT 或 TEACHER
    student_id = Column(String, nullable=True)
    department = Column(String, nullable=True)
    email = Column(String, nullable=True)
    face_features = Column(Text, nullable=True)  # 存储人脸特征向量的 JSON 字符串
    points = Column(Integer, default=0)  # 积分/表现分

    # 关系
    classrooms = relationship("Classroom", secondary=student_classroom, back_populates="students")

class QuestionBank(Base):
    __tablename__ = "question_banks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(Text)
    creator_id = Column(Integer, ForeignKey("users.id"))
    classroom_id = Column(Integer, ForeignKey("classrooms.id"), nullable=True)
    
    questions = relationship("Question", back_populates="bank")
    classroom = relationship("Classroom", back_populates="question_bank")

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    bank_id = Column(Integer, ForeignKey("question_banks.id"))
    content = Column(Text)
    type = Column(String)  # SINGLE, MULTIPLE, JUDGE
    options = Column(Text)  # JSON 字符串存储选项
    answer = Column(String)
    
    bank = relationship("QuestionBank", back_populates="questions")

class Classroom(Base):
    __tablename__ = "classrooms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    teacher_id = Column(Integer, ForeignKey("users.id"))
    description = Column(Text)
    schedule = Column(String)
    student_count = Column(Integer, default=0)
    is_active = Column(Integer, default=0)  # 0: 未上课, 1: 正在上课
    active_call_student_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # 关系
    students = relationship("User", secondary=student_classroom, back_populates="classrooms")
    question_bank = relationship("QuestionBank", back_populates="classroom", uselist=False)
    announcements = relationship("Announcement", back_populates="classroom")

class Announcement(Base):
    __tablename__ = "announcements"

    id = Column(Integer, primary_key=True, index=True)
    classroom_id = Column(Integer, ForeignKey("classrooms.id"))
    content = Column(Text)
    date = Column(String)  # 存储日期字符串

    classroom = relationship("Classroom", back_populates="announcements")

class AttendanceSession(Base):
    __tablename__ = "attendance_sessions"

    id = Column(Integer, primary_key=True, index=True)
    classroom_id = Column(Integer, ForeignKey("classrooms.id"))
    start_time = Column(DateTime, default=datetime.now)
    status = Column(String, default="OPEN")  # OPEN, CLOSED

    records = relationship("AttendanceRecord", back_populates="session")

class AttendanceRecord(Base):
    __tablename__ = "attendance_records"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("attendance_sessions.id"))
    student_id = Column(Integer, ForeignKey("users.id"))
    check_in_time = Column(DateTime, default=datetime.now)

    session = relationship("AttendanceSession", back_populates="records")

class ClassroomQuestion(Base):
    __tablename__ = "classroom_questions"

    id = Column(Integer, primary_key=True, index=True)
    classroom_id = Column(Integer, ForeignKey("classrooms.id"))
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=True)
    content = Column(Text, nullable=True)
    type = Column(String)  # BANK or MANUAL
    answer = Column(String, nullable=True)
    status = Column(String, default="OPEN")  # OPEN, CLOSED
    start_time = Column(DateTime, default=datetime.now)

    submissions = relationship("QuestionSubmission", back_populates="question")

class QuestionSubmission(Base):
    __tablename__ = "question_submissions"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("classroom_questions.id"))
    student_id = Column(Integer, ForeignKey("users.id"))
    answer = Column(Text)
    is_correct = Column(Integer, nullable=True)
    submit_time = Column(DateTime, default=datetime.now)

    question = relationship("ClassroomQuestion", back_populates="submissions")
    student = relationship("User")

class ClassroomJoinedStudent(Base):
    __tablename__ = "classroom_joined_students"

    id = Column(Integer, primary_key=True, index=True)
    classroom_id = Column(Integer, ForeignKey("classrooms.id"))
    student_id = Column(Integer, ForeignKey("users.id"))
    join_time = Column(DateTime, default=datetime.now)

class PracticeRecord(Base):
    __tablename__ = "practice_records"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"))
    bank_id = Column(Integer, ForeignKey("question_banks.id"))
    total_questions = Column(Integer)
    correct_count = Column(Integer)
    score = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)
