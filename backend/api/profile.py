from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from passlib.context import CryptContext
from database.db import get_db
from database.models import User
from utils.auth import get_current_user
from utils.response import success_response, error_response
from utils.face import extract_face_encoding
import json

router = APIRouter(prefix="/user", tags=["profile"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    student_id: Optional[str] = None
    department: Optional[str] = None

class PasswordChange(BaseModel):
    old_pwd: str
    new_pwd: str

@router.get("/profile")
async def get_profile(user: User = Depends(get_current_user)):
    return success_response(data={
        "username": user.username,
        "name": user.name,
        "role": user.role,
        "email": user.email,
        "studentId": user.student_id,
        "department": user.department or "计算机学院"
    })

@router.put("/profile")
async def update_profile(profile: ProfileUpdate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    if profile.name is not None: 
        user.name = profile.name
    if profile.email is not None: 
        user.email = profile.email
    if profile.student_id is not None:
        user.student_id = profile.student_id
    if profile.department is not None:
        user.department = profile.department
    
    db.add(user)
    await db.commit()
    return success_response(msg="资料已更新")

@router.post("/password/change")
async def change_password(request: PasswordChange, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    # 校验旧密码（bcrypt）
    if not pwd_context.verify(request.old_pwd, user.password):
        return error_response(msg="原密码错误")
    
    user.password = pwd_context.hash(request.new_pwd)
    db.add(user)
    await db.commit()
    return success_response(msg="密码修改成功")

@router.post("/face/update")
async def update_face(data: dict, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    face_data = data.get("face_data")
    if not face_data:
        return error_response(msg="未提供人脸数据")
    
    encoding = extract_face_encoding(face_data)
    if not encoding:
        return error_response(msg="未检测到人脸，请重试")
        
    user.face_features = json.dumps(encoding)
    await db.commit()
    return success_response(msg="人脸数据已更新")
