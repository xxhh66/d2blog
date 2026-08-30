"""认证与验证码相关逻辑。

负责向用户发送邮箱验证码，并限制重发频率，避免恶意刷验证码或重复发送。
"""
import asyncio
import random
from datetime import datetime, timedelta

from fastapi import HTTPException

from app.core.caches import verify_code_cache
from app.core.config import settings
from app.schemas.auth import RegisterParam, LoginParam, LoginResult
from app.utils import smtp_util, pwd_util,jwt_util
from app.models import User
EMAIL_LOCKS={}
VERIFY_CODE_LOCK = asyncio.Lock()

class AuthService:
    """认证服务，封装验证码发送等基础认证能力。"""

    async def send_verify_code(self, email: str):
        """发送邮箱验证码，并校验是否在冷却期内。"""
        if email not in EMAIL_LOCKS:
            async with VERIFY_CODE_LOCK:
                if email not in EMAIL_LOCKS:
                    EMAIL_LOCKS[email] = asyncio.Lock()

        async with EMAIL_LOCKS[email]:
            # 如果同一邮箱最近已发送验证码，则根据创建时间判断是否还在冷却中。
            verify_code_dict = verify_code_cache.get(email)
            if verify_code_dict:
                one_minutes = timedelta(minutes=1)
                if verify_code_dict.get("created_at") + one_minutes > datetime.now():
                    raise HTTPException(status_code=400, detail="验证码已发送，请稍后再试")

            # 生成 6 位随机数字验证码，并保存到缓存，便于后续校验逻辑复用。
            code = "".join(random.choices("0123456789", k=6))
            now = datetime.now()
            verify_code_cache.set(email, {"code": code, "created_at": now})

            try:
                # 发送邮件时，消息内容中说明验证码有效时间，便于用户及时填写。
                smtp_util.send_message(f"您的验证码是：{code},将在3分钟内过期", email, "验证码")
            except Exception:
                raise HTTPException(status_code=400, detail="系统繁忙，请稍后重试")

            return True

    # 注册
    async def register(self, param: RegisterParam):
        """
        用户注册逻辑。
        Args:
            param: 注册参数（包含 email, code, password 等）
        Returns:
            bool: 注册成功返回 True
        Raises:
            HTTPException 400: 验证码过期或错误
            HTTPException 400: 用户已存在
        Process:
            1. 验证验证码（从缓存中获取并比对）
            2. 检查用户是否已存在
            3. 加密密码
            4. 创建用户记录
            5. 返回成功
        """
        # 从缓存中获取该邮箱的验证码记录
        verify_code_dict = verify_code_cache.get(param.email)
        # 检查验证码是否存在
        if not verify_code_dict:
            raise HTTPException(status_code=400,detail='验证码过期')
        # 对比验证码是否正确
        if verify_code_dict["code"] != param.code:
            raise HTTPException(status_code=400,detail="验证码过期或不正确")
        # 检查用户是否已经存在
        user = await User.get_or_none(email=param.email,is_deleted=False)
        if user:
            raise HTTPException(status_code=400,detail="用户已存在")
        # 密码通过哈希加密
        hashed_password = pwd_util.get_password_hash(param.password)
        user_data = param.model_dump()
        user_data['password'] = hashed_password

        await User.create(**user_data)
        return True

    async def login(self,param:LoginParam)->LoginResult:
        # 1. 将用户查出
        user = await User.get_or_none(email=param.email,is_deleted=False)
        if not user:
            raise HTTPException(status_code=400,detail="用户不存在")
        # 2. 验证密码
        if not pwd_util.verify_password(param.password, user.password):
            raise HTTPException(status_code=400, detail="密码错误")
        # 3. 生成token
        user_data = {
            'sub':str(user.pk),
            'email':user.email
        }
        access_token = jwt_util.create_access_token(user_data)
        refresh_token = jwt_util.create_refresh_token(user_data)
        seconds = int(timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES).total_seconds())
        return LoginResult(access_token=access_token, refresh_token=refresh_token, expires_in=seconds)









