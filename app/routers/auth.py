"""认证相关路由。

对外暴露与邮箱验证码发送相关的接口，属于用户认证模块的入口。
"""

from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.params import Query
from pydantic import EmailStr

from app.core import deps
from app.schemas.common import ApiResult
from app.schemas.user import RegisterParam
from app.services.auth import AuthService

# 路由分组用于在 OpenAPI 文档中归类展示用户认证相关接口。
router = APIRouter(tags=["用户认证"])


@router.get("/get_verify_code")
async def get_verify_code(
    email: Annotated[EmailStr, Query()],
    auth_service: Annotated[AuthService, Depends(deps.get_auth_service)],
):
    """按邮箱发送验证码，并返回统一的 API 响应结构。"""
    return ApiResult.success(await auth_service.send_verify_code(email))

@router.post("/register", response_model=ApiResult[bool])
async def register(param: RegisterParam,
                          auth_service: Annotated[AuthService, Depends(deps.get_auth_service)]):
    return ApiResult.success(await auth_service.register(param))