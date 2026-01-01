from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.db import get_db
from database.models import User
from utils.response import success_response, error_response
from utils.face import extract_face_encoding
import base64
import numpy as np
import face_recognition
import json

router = APIRouter(prefix="/auth", tags=["auth"])

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

@router.post("/face-login")
async def face_login(request: FaceLoginRequest, db: AsyncSession = Depends(get_db)):
    encoding = extract_face_encoding(request.faceData)
    if not encoding:
        return error_response(msg="未检测到人脸或图像质量过低")
    
    # 获取所有有脸部特征的用户
    result = await db.execute(select(User).where(User.face_features != None))
    users = result.scalars().all()
    
    target_encoding = np.array(encoding)
    
    for user in users:
        try:
            # 尝试解析存储的特征
            features = json.loads(user.face_features)
            if not isinstance(features, list):
                continue
            
            user_encoding = np.array(features)
            
            # 确保维度匹配 (face_recognition 默认是 128 维)
            if user_encoding.shape != target_encoding.shape:
                continue

            # 比对人脸
            matches = face_recognition.compare_faces([user_encoding], target_encoding, tolerance=0.4)
            if matches[0]:
                token = f"jwt-token-for-{user.username}"
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
            print(f"Error processing face features for user {user.username}: {e}")
            continue
            
    return error_response(msg="人脸匹配失败，请使用密码登录", code=401)

@router.post("/login")
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    # 支持用户名、学号、邮箱登录
    from sqlalchemy import or_
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
    
    if not user or user.password != request.password:
        return error_response(msg="用户名或密码错误", code=401)
    
    token = f"jwt-token-for-{user.username}"
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
    # 检查用户是否已存在
    result = await db.execute(select(User).where(User.username == request.username))
    if result.scalars().first():
        return error_response(msg="用户名已存在")
    
    # 检查邮箱是否已存在
    if request.email:
        result = await db.execute(select(User).where(User.email == request.email))
        if result.scalars().first():
            return error_response(msg="该邮箱已被注册")

    face_features_json = None
    if request.faceData:
        encoding = extract_face_encoding(request.faceData)
        if encoding:
            face_features_json = json.dumps(encoding)
    
    # 创建新用户
    new_user = User(
        username=request.username,
        password=request.password,
        name=request.name,
        role=request.role,
        student_id=request.studentId,
        email=request.email,
        face_features=face_features_json
    )
    db.add(new_user)
    await db.commit()
    
    return success_response(msg="注册成功")

