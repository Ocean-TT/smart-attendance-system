import os
import base64
import json
from datetime import datetime, timedelta

import numpy as np
import face_recognition
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from passlib.context import CryptContext
from jose import jwt

from database.db import get_db
from database.models import User
from utils.response import success_response, error_response
from utils.face import extract_face_encoding

router = APIRouter(prefix="/auth", tags=["auth"])

# 密码哈希和JWT配置
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    password: str
    name: str
    role: str
    studentId: Optional[str] = None
    email: Optional[str] = None
    faceData: Optional[str] = None

class FaceLoginRequest(BaseModel):
    faceData: str


def create_access_token(data: dict):
    """生成 JWT token"""
    to_encode = data.copy()
    to_encode["exp"] = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


@router.post("/face-login")
async def face_login(request: FaceLoginRequest, db: AsyncSession = Depends(get_db)):
    """人脸登录：提取特征后和库里所有已注册人脸做比对"""
    encoding = extract_face_encoding(request.faceData)
    if not encoding:
        return error_response(msg="未检测到人脸或图像质量过低")
    
    # 取出所有录过人脸的用户
    result = await db.execute(select(User).where(User.face_features != None))
    users = result.scalars().all()
    
    target_encoding = np.array(encoding)
    
    for user in users:
        try:
            features = json.loads(user.face_features)
            if not isinstance(features, list):
                continue
            
            user_encoding = np.array(features)
            if user_encoding.shape != target_encoding.shape:
                continue

            # tolerance 0.4 是经验值，越小越严格
            matches = face_recognition.compare_faces([user_encoding], target_encoding, tolerance=0.4)
            if matches[0]:
                token = create_access_token({"sub": user.username, "role": user.role})
                return success_response(
                    data={
                        "token": token,
                        "user": {
                            "username": user.username,
                            "name": user.name,
                            "role": user.role,
                            "studentId": user.student_id
                        }
                    },
                    msg="人脸识别成功"
                )
        except Exception as e:
            print(f"人脸比对出错 {user.username}: {e}")
            continue
            
    return error_response(msg="人脸匹配失败，请使用密码登录", code=401)


@router.post("/login")
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    """账号密码登录，支持用户名/学号/邮箱三种方式"""
    result = await db.execute(
        select(User).where(
            or_(
                User.username == request.username,
                User.student_id == request.username,
                User.email == request.username
            )
        )
    )
    user = result.scalars().first()
    
    if not user or not pwd_context.verify(request.password, user.password):
        return error_response(msg="用户名或密码错误", code=401)
    
    token = create_access_token({"sub": user.username, "role": user.role})
    return success_response(
        data={
            "token": token,
            "user": {
                "username": user.username,
                "name": user.name,
                "role": user.role,
                "studentId": user.student_id
            }
        },
        msg="登录成功"
    )


@router.post("/register")
async def register(request: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """注册新用户，密码存哈希不存明文"""
    # 检查用户名是否已存在
    result = await db.execute(select(User).where(User.username == request.username))
    if result.scalars().first():
        return error_response(msg="用户名已存在")
    
    if request.email:
        result = await db.execute(select(User).where(User.email == request.email))
        if result.scalars().first():
            return error_response(msg="该邮箱已被注册")

    face_features_json = None
    if request.faceData:
        encoding = extract_face_encoding(request.faceData)
        if encoding:
            face_features_json = json.dumps(encoding)
    
    new_user = User(
        username=request.username,
        password=pwd_context.hash(request.password),  # bcrypt 哈希
        name=request.name,
        role=request.role,
        student_id=request.studentId,
        email=request.email,
        face_features=face_features_json
    )
    db.add(new_user)
    await db.commit()
    
    return success_response(msg="注册成功")
