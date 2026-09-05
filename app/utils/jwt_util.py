import base64
from datetime import datetime, UTC, timedelta
from typing import Any
from uuid import uuid4

import jwt
from fastapi import HTTPException

from app.core.config import Settings, settings


def create_token(body:dict[str,Any]):
    return jwt.encode(body, str(uuid4()), algorithm="HS256")

def create_access_token(body: dict[str, Any]) -> str:
    payload = body.copy()

    now = datetime.now(UTC)

    payload.update({
        "iss": settings.JWT_ISS,
        "aud": settings.JWT_AUD,
        "exp": now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        "nbf": now,
        "iat": now,
        "jti": str(uuid4()),
        "typ": "access"
    })

    return jwt.encode(payload, settings.SECURITY_KEY, algorithm="HS256")

def create_refresh_token(body: dict[str, Any]) -> str:
    payload = body.copy()

    now = datetime.now(UTC)

    payload.update({
        "iss": settings.JWT_ISS,
        "aud": settings.JWT_AUD,
        "exp": now + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES),
        "nbf": now,
        "iat": now,
        "jti": str(uuid4()),
        "typ": "refresh"
    })

    return jwt.encode(payload, settings.SECURITY_KEY, algorithm="HS256")

def verify_token(token: str, token_type: str = 'access') -> dict[str, Any]:
    payload = jwt.decode(token, settings.SECURITY_KEY, algorithms=["HS256"], audience=settings.JWT_AUD, issuer=settings.JWT_ISS)
    # 验证token是否过期
    if not payload:
        raise HTTPException(status_code=401, detail="无效的token")
    # 验证token类型
    if payload.get("typ") != token_type:
        raise HTTPException(status_code=401, detail="无效的token")
    return payload


# if __name__ =="__main__":
#     print(str(uuid4()))

    # now =datetime.now()
    #
    # body = {
    #     "iss": "bogeblog",
    #     "sub": "1",
    #     "aud": "android",
    #     "exp": now + timedelta(days=1),
    #     "nbf": now,
    #     "iat": now,
    #     "jti": str(uuid4()),
    # }
    #
    # print(create_token(body))
    # header, payload, signature = create_token(body).split( ".")
    #
    # print(base64.urlsafe_b64decode(header))
    # payload = payload + "="
    # print(len(payload))