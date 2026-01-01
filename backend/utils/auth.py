from fastapi import Header, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.db import get_db
from database.models import User
import base64
from urllib.parse import unquote

async def get_current_user(authorization: str = Header(None), db: AsyncSession = Depends(get_db)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未登录或 Token 无效")
    
    encoded_token = authorization.replace("Bearer ", "")
    try:
        # 尝试 Base64 解码并 URL 解码（处理中文用户名）
        token = unquote(base64.b64decode(encoded_token).decode('utf-8'))
    except Exception:
        # 如果解码失败，尝试直接使用原字符串（兼容旧 Token）
        token = encoded_token

    if token.startswith("jwt-token-for-"):
        username = token.replace("jwt-token-for-", "")
        result = await db.execute(select(User).where(User.username == username))
        user = result.scalars().first()
        if user:
            return user
            
    raise HTTPException(status_code=401, detail="Token 无效")
