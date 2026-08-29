"""认证与验证码相关逻辑。

负责向用户发送邮箱验证码，并限制重发频率，避免恶意刷验证码或重复发送。
"""

import random
from datetime import datetime, timedelta

from fastapi import HTTPException

from app.core.caches import verify_code_cache
from app.schemas.user import RegisterParam
from app.utils import smtp_util, pwd_util
from app.models import User

class AuthService:
    """认证服务，封装验证码发送等基础认证能力。"""

    async def send_verify_code(self, email: str):
        """发送邮箱验证码，并校验是否在冷却期内。"""
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
        # 先获取验证码
        verify_code_dict = verify_code_cache.get(param.email)
        if not verify_code_dict:
            raise HTTPException(status_code=400,detail='验证码过期')
        if verify_code_dict["code"] != param.code:
            raise HTTPException(status_code=400,detail="验证码过期或不正确")

        user = await User.get_or_none(email=param.email,is_deleted=False)
        if user:
            raise HTTPException(status_code=400,detail="用户已存在")

        hashed_password = pwd_util.get_password_hash(param.password)
        user_data = param.model_dump()
        user_data['password'] = hashed_password

        await User.create(**user_data)
        return True