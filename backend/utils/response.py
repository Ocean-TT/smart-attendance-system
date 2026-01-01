from fastapi.responses import JSONResponse
from fastapi import status

def success_response(data=None, msg="success", code=200):
    """成功响应"""
    return JSONResponse(
        status_code=code,
        content={
            "code": code,
            "msg": msg,
            "data": data
        }
    )

def error_response(msg, code=400, data=None):
    """错误响应"""
    return JSONResponse(
        status_code=code,
        content={
            "code": code,
            "msg": msg,
            "data": data
        }
    )
