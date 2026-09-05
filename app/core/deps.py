"""依赖注入辅助模块。

用于为路由函数提供服务实例，保持控制器层简洁，并且可复用依赖管理逻辑。
"""
from typing import Annotated

from fastapi import HTTPException
from fastapi.params import Header, Depends

from app.services.auth import AuthService
from app.models import User
from app.utils import jwt_util


def get_auth_service() -> AuthService:
    """创建并返回认证服务实例。

    在 FastAPI 的 Depends 中使用时，每次请求都可以获取一个新的服务对象，
    方便在路由层按需执行认证相关逻辑。
    """
    return AuthService()

# v1版本
# async def get_current_user(access_token: Annotated[str, Header()])->User:
#     try:
#         payload = jwt_util.verify_token(access_token,'access')
#         print(payload)
#         user_id = int(payload.get('sub'))
#     except Exception as e:
#         print(e)
#         raise HTTPException(status_code=400, detail="无效的token")
#     return await User.get(id=user_id)

# v2版本
async def get_current_user(authorization: Annotated[str, Header()])->User:
    if not authorization:
        raise HTTPException(status_code=401,detail="未提供认证信息")

    parts = authorization.split(" ")
    print(parts)
    if  len(parts) != 2:
        raise HTTPException(status_code=400,detail="认证格式错误，请使用 'Bearer <token>'")

    # 检查是否为 Bearer 类型
    if parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=401,
            detail="认证类型错误，请使用 'Bearer'"
        )

    try:
        payload = jwt_util.verify_token(parts[1],'access')
        print(payload)
        user_id = int(payload.get('sub'))
        return await User.get(id=user_id)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="无效的token")

def check_permission(prem:str):
    def _check_permission(user:Annotated[User,Depends(get_current_user)]):
        if prem!='test_blog':
            raise HTTPException(status_code=400,detail="无权限")
    return _check_permission

