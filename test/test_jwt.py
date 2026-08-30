import base64
from datetime import datetime, timedelta
from typing import Any
from uuid import uuid4
import jwt

def create_token(body:dict[str,Any]):
    return jwt.encode(body, str(uuid4()), algorithm="HS256")


if __name__ =="__main__":
    now =datetime.now()

    body = {
        "iss": "bogeblog",
        "sub": "1",
        "aud": "android",
        "exp": now + timedelta(days=1),
        "nbf": now,
        "iat": now,
        "jti": str(uuid4()),
    }

    print(create_token(body))
    header, payload, signature = create_token(body).split( ".")

    print(base64.urlsafe_b64decode(header))
    payload = payload + "="
    print(len(payload))