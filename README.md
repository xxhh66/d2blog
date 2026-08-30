# d2blog

> FastAPI实现博客后端。

## 1. 开发环境搭建

### 1.1 初始化项目

**（1）初始化**

```bash
# 新版本初始化不会生成main.py函数,
uv init -p 3.12
# --no-package可以生成main.py
uv init -p 3.12 --no-package
```

+ 安装`uv`

```bash
# windows平台下
powershell -ExecutionPolicy Bypass -c "irm https://astral.sh/uv/install.ps1 | iex"

# 版本查询
uv --version

```

> uv 是由 Astral 公司开发的一款用 Rust 编写的 Python 包管理器和环境管理器，主要目标是提供比现有工具快 10-100 倍的性能，同时保持简单直观的用户体验。
>
> uv 可以替代 pip、virtualenv、pip-tools、pyenv 等工具，提供依赖管理、虚拟环境创建、Python 版本管理等一站式服务。
>
> uv add 管理项目依赖：项目下 `.venv\Lib\site‑packages`，也就是本项目虚拟环境内部。

+ `uv`与`uvicorn`区别

**没有父子关系，互不依赖**：uvicorn 是 Python 库；uv 是独立 Rust 写的工具。

```bash
# uv使用
uv init -p 3.12
uv add fastapi uvicorn[standard]
# 启动服务
uv run uvicorn main:app --reload


# uvicorn使用
uvicorn main:app --reload
```



| 工具    | 类型            | 作用                                         |
| ------- | --------------- | -------------------------------------------- |
| uv      | 独立工具 (Rust) | 管理 Python 版本、虚拟环境、安装包、运行命令 |
| uvicorn | Python 库       | Web 服务器，运行 FastAPI 接口程序            |

**（2）工程项目中添加包**

```bash
uv add fastapi uvicorn
```

**（3）创建文件结构**

```bash
# 创建app文件夹及对应子文件夹
├─app
│  ├─cache
│  ├─core
│  │  └─__pycache__
│  ├─models
│  │  └─__pycache__
│  ├─routers
│  ├─schemas
│  ├─services
│  ├─tasks
│  ├─utils
│  └─main.cpp
```

**（4）添加`d2blog/app/main.py`**

```python
from fastapi import FastAPI

myapp = FastAPI()

@myapp.get("/")
async def root():
    return {"hello": "world"}
```

**（5）添加`d2blog/start.py`**

```python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:myapp", host="0.0.0.0", port=8000,reload=True)
```

```bash
 # 启动测试
 uv run python .\start.py 
```

> 启动测试， `uv run python .\start.py `,浏览器打开http://127.0.0.1:8000/ 、http://127.0.0.1:8000/docs

**（6）添加ORM数据库迁移工具**

```bash
# 项目添加库
uv add aerich[toml]   

uv add "tortoise-orm[asyncpg]"  
```

添加修改代码`d2blog/app/core/config.py`

```
TORTOISE_ORM = {
    "connections": {"default": "postgres://postgres:123456@10.10.10.7:5432/fastapi"},
    "apps": {
        "models": {
            "models": ["app.models", "aerich.models"],
            "default_connection": "default",
        },
    },
}
```

修改 `d2blog/app/main.py`

```python
from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from app.core import config
myapp = FastAPI()

register_tortoise(myapp,config=config.TORTOISE_ORM,generate_schemas=False)

@myapp.get("/")
async def root():
    return {"hello": "world"}
```

```bash
# 初始化aerich
uv run aerich init -t app.core.config.TORTOISE_ORM
# 运行代码
 uv run python .\start.py         
```

### 1.2 静态配置`.env`

**（1）创建`d2blog/.env`文件**

```bash
DATABASE_URL=postgres://postgres:123456@10.10.10.7:5432/fastapi
```

**（2）修改`d2blog/app/core/config.py`文件**

```python
from pydantic_settings import BaseSettings,SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str=""

    model_config = SettingsConfigDict(env_file=".env",env_file_encoding="utf-8")

settings = Settings()
# V3
TORTOISE_ORM = {
    "connections": {"default": settings.DATABASE_URL},
    "apps": {
        "models": {
            "models": ["app.models", "aerich.models"],
            "default_connection": "default",
        },
    },
}
```

项目添加`pydantic_settings`

```bash
uv add pydantic_settings
```

**（3）创建数据库`d2blog/app/core/config.py`文件**

+ [postgres安装包链接](https://www.enterprisedb.com/downloads/postgres-postgresql-downloads)

```bash
postgres://postgres:123456@127.0.0.1:5432/postgres
  ①        ②       ③       ④       ⑤       ⑥

① 协议     ② 用户名  ③ 密码    ④ 主机    ⑤ 端口   ⑥ 数据库名
```

![image-20260829103732868](assets/image-20260829103732868.png)

+ 可视化工具：`DBeaver`、`Navicat Premium`

![image-20260829095539418](assets/image-20260829095539418.png)

### 1.3 注册

使用`email`注册功能。

```bash
# 缓存包
uv add cachetools
```

+ 增加`app/schemas/common.py`下缓存功能

```python
"""缓存模块。

该模块集中管理应用中使用到的内存缓存，包括通用缓存包装器和验证码缓存。
缓存使用 cachetools.TTLCache，可在固定生命周期内存储临时数据，并自动过期。
"""

from cachetools import TTLCache
from typing import Generic, TypeVar

T = TypeVar("T")

class CommonCache(Generic[T]):
    """对 TTLCache 的简单包装，提供统一的 get/set/delete 接口。

    适用于需要按键值存储的临时数据，例如验证码、会话状态或分布式任务状态。
    """

    def __init__(self, maxsize: int, ttl: int):
        # TTLCache 会在指定时间内自动清理过期项，避免无限增长。
        self.cache = TTLCache(maxsize=maxsize, ttl=ttl)

    def get(self, key: str) -> T | None:
        # 读取缓存时返回键对应的值，如不存在则返回 None。
        return self.cache.get(key)

    def set(self, key: str, value: T):
        # 保存数据时使用字符串键，便于按业务字段查询。
        self.cache[key] = value

    def delete(self, key: str) -> bool:
        # 删除缓存项并返回是否实际删除成功。
        return self.cache.pop(key, None)


# 验证码缓存：最多保存 100 个验证码记录，3 分钟自动过期。
verify_code_cache = CommonCache(maxsize=100, ttl=60 * 3)
```

`cachetools`包下的`TTLCache` = **带过期时间的内存字典缓存**，全部数据存在内存，进程重启缓存全部丢失。

①`maxsize`：缓存最大 key 数量，超过后自动淘汰 LRU（最近最少使用）条目

②`ttl`：每条数据存活时间，**单位秒**，到期自动失效

+ 增加`app/utils/smtp_util.py`邮件发生`smtp`验证

> 163邮箱开启smtp时，密码只显示一次！！！

```python
"""邮件发送工具。

封装 SMTP 发送逻辑，简化验证码、通知类消息的发送流程。
send_message() 被调用
    │
    ├─ 参数: body, to, subject
    │
    ├─ 步骤1: 构建邮件
    │   ├─ MIMEText(body, "plain", "utf-8")
    │   ├─ msg["From"] = SMTP_USER
    │   ├─ msg["To"] = to
    │   └─ msg["Subject"] = subject
    │
    ├─ 步骤2: 连接服务器
    │   └─ SMTP_SSL(SMTP_SERVER, SMTP_PORT)
    │
    ├─ 步骤3: 登录认证
    │   └─ server.login(SMTP_USER, SMTP_PASS)
    │
    ├─ 步骤4: 发送邮件
    │   └─ server.sendmail(SMTP_USER, to, msg.as_string())
    │
    ├─ 步骤5: 断开连接
    │   └─ server.quit()
    │
    └─ 返回 (成功或抛出异常)
"""

"""
邮件发送工具。

封装 SMTP 发送逻辑，简化验证码、通知类消息的发送流程。
"""

import smtplib
from email.mime.text import MIMEText

from app.core.config import settings


def send_message(body: str, to: str, subject: str):
    """发送文本邮件。

    Args:
        body: 邮件正文内容（支持中文）
        to: 收件人邮箱地址（支持单个收件人，多个需用逗号分隔）
        subject: 邮件主题
    
    Returns:
        None: 发送成功则无返回，失败则抛出异常
    
    Raises:
        SMTPAuthenticationError: 认证失败（用户名/密码错误）
        SMTPRecipientsRefused: 收件人被拒绝
        SMTPServerDisconnected: 服务器连接断开
        Exception: 其他SMTP相关异常
    """
    
    # ========== 第一步：构建邮件内容 ==========
    # MIMEText 用于构造纯文本格式的邮件
    # 参数说明：
    #   - body: 邮件正文内容
    #   - "plain": 邮件格式为纯文本（text/plain），非HTML
    #   - "utf-8": 字符编码，支持中文等非ASCII字符
    msg = MIMEText(body, "plain", "utf-8")
    
    # 设置邮件头信息（类似信封上的地址）
    msg["From"] = settings.SMTP_USER        # 发件人地址（配置中获取）
    msg["To"] = to                          # 收件人地址（函数参数传入）
    msg["Subject"] = subject                # 邮件主题（函数参数传入）
    
    # ========== 第二步：连接 SMTP 服务器 ==========
    # SMTP_SSL: 使用 SSL 加密连接（端口通常是 465）
    # 参数说明：
    #   - settings.SMTP_SERVER: SMTP 服务器地址（如 smtp.qq.com）
    #   - settings.SMTP_PORT: SMTP 服务器端口（SSL 一般为 465）
    # 
    # 注意：如果使用 TLS（端口 587），则使用 smtplib.SMTP() + server.starttls()
    server = smtplib.SMTP_SSL(settings.SMTP_SERVER, settings.SMTP_PORT)
    
    # ========== 第三步：登录 SMTP 服务器 ==========
    # 使用邮箱账号和密码（或授权码）进行身份验证
    # 参数说明：
    #   - settings.SMTP_USER: 邮箱账号（如 your_email@qq.com）
    #   - settings.SMTP_PASS: 密码或授权码（注意：QQ邮箱需使用授权码）
    server.login(settings.SMTP_USER, settings.SMTP_PASS)
    
    # ========== 第四步：发送邮件 ==========
    # sendmail 参数说明：
    #   - 第一个参数: 发件人地址（必须与登录账号一致）
    #   - 第二个参数: 收件人地址（可以是字符串或列表）
    #   - 第三个参数: 邮件内容（转为字符串格式）
    server.sendmail(settings.SMTP_USER, to, msg.as_string())
    
    # ========== 第五步：断开连接 ==========
    # 优雅地关闭与 SMTP 服务器的连接，释放资源
    server.quit()
```

+ 增加认证逻辑`app/services/auth.py`

  > 负责向用户发送验证码，并限制发送次数；

  ```python
  """认证与验证码相关逻辑。
  
  负责向用户发送邮箱验证码，并限制重发频率，避免恶意刷验证码或重复发送。
  """
  
  import random
  from datetime import datetime, timedelta
  
  from fastapi import HTTPException
  
  from app.core.caches import verify_code_cache
  from app.utils import smtp_util
  
  
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
  ```

　

+ 增加路由`app/services/auth.py`|`app/core/deps.py`

> APIRouter创建各模块子路由。

[Fastapi依赖项](https://fastapi.tiangolo.com/zh/tutorial/dependencies/)

```python
"""认证相关路由。

对外暴露与邮箱验证码发送相关的接口，属于用户认证模块的入口。
"""

from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.params import Query
from pydantic import EmailStr

from app.core import deps
from app.schemas.common import ApiResult
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
```

注入项`app/core/deps.py`

```python
"""依赖注入辅助模块。

用于为路由函数提供服务实例，保持控制器层简洁，并且可复用依赖管理逻辑。
"""

from app.services.auth import AuthService


def get_auth_service() -> AuthService:
    """创建并返回认证服务实例。

    在 FastAPI 的 Depends 中使用时，每次请求都可以获取一个新的服务对象，
    方便在路由层按需执行认证相关逻辑。
    """
    return AuthService()
```

+ 数据库模型`app/models/user.py`

创建一个用户表，

```
uv run aerich migrate
uv run aerich upgrade
```

定义表的结构，包括字段类型、约束、索引、表配置等信息，使用`tortoise`映射到`PostgreSQL`数据库,实现数据库迁移。

```python
from tortoise import Model,fields


class User(Model):
    email= fields.CharField(max_length=128, null=False,db_index=True,description="邮箱")
    password  =fields.CharField(max_length=128,null=False,db_index=True,description="密码")

    is_deleted = fields.BooleanField(default=False,null=False,description="是否删除")
    created_at = fields.DatetimeField(auto_now_add=True,null=False,db_index=True,descriptions="创建时间")
    updated_at = fields.DatetimeField(auto_now_add=True,null=False,descriptions="更新时间")

    class Meta:
        table = 't_user'
        table_description = '用户表'
```

并在`app/models/__init__.py`添加，

```python
from .user import User
```

+ 请求响应模型`app/schemas/auth.py`



```python
from pydantic import BaseModel, EmailStr, Field


class RegisterParam(BaseModel):
    email: EmailStr=Field(...,description="邮箱",max_length=128)
    password:str = Field(...,description="密码",max_length=20,min_length=6)
    code:str = Field(...,d
```

+ 创建路由`app/routers/auth.py`

```python
@router.post("/register", response_model=ApiResult[bool])
async def register(param: RegisterParam,
                          auth_service: Annotated[AuthService, Depends(deps.get_auth_service)]):
    return ApiResult.success(await auth_service.register(param))
```

+ 注册逻辑`app/services/auth.py`

```python
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
```



### 1.4 jwt

`JWT` （`JSON Web Token`） 是目前最流行的跨域认证解决方案，是一种基于 `Token` 的认证授权机制。 从` JWT` 的全称可以看出，`JWT` 本身也是 `Token`，一种规范化之后的 `JSON` 结构的 `Token`。

JWT 自身包含了身份验证所需要的所有信息，因此，我们的服务器不需要存储 Session 信息。这显然增加了系统的可用性和伸缩性，大大减轻了服务端的压力。

可以看出，**JWT 更符合设计 RESTful API 时的「Stateless（无状态）」原则** 。

`JWT` 本质上就是一组字串，通过（`.`）切分成三个为 Base64 编码的部分：

- **Header（头部）** : 描述 JWT 的元数据，定义了生成签名的算法以及 `Token` 的类型。Header 被 Base64Url 编码后成为 JWT 的第一部分。
- **Payload（载荷）** : 用来存放实际需要传递的数据，包含声明（Claims），如`sub`（subject，主题）、`jti`（JWT ID）。Payload 被 Base64Url 编码后成为 JWT 的第二部分。
- **Signature（签名）**：服务器通过 Payload、Header 和一个密钥(Secret)使用 Header 里面指定的签名算法（默认是 HMAC SHA256）生成。生成的签名会成为 JWT 的第三部分。

![JWT 组成](assets/jwt-composition.png)

**Header** 通常由两部分组成：

- `typ`（Type）：令牌类型，也就是 JWT。
- `alg`（Algorithm）：签名算法，比如 HS256。

示例：



```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

JSON 形式的 Header 被转换成 Base64 编码，成为 JWT 的第一部分。

**Payload** 也是 JSON 格式数据，其中包含了 Claims(声明，包含 JWT 的相关信息)。

Claims 分为三种类型：

- **Registered Claims（注册声明）**：预定义的一些声明，建议使用，但不是强制性的。
- **Public Claims（公有声明）**：JWT 签发方可以自定义的声明，但是为了避免冲突，应该在 [IANA JSON Web Token Registry](https://www.iana.org/assignments/jwt/jwt.xhtml) 中定义它们。
- **Private Claims（私有声明）**：JWT 签发方因为项目需要而自定义的声明，更符合实际项目场景使用。

下面是一些常见的注册声明：

- `iss`（issuer）：JWT 签发方。
- `iat`（issued at time）：JWT 签发时间。
- `sub`（subject）：JWT 主题。
- `aud`（audience）：JWT 接收方。
- `exp`（expiration time）：JWT 的过期时间。
- `nbf`（not before time）：JWT 生效时间，早于该定义的时间的 JWT 不能被接受处理。
- `jti`（JWT ID）：JWT 唯一标识。

示例：

```json
{
  "uid": "ff1212f5-d8d1-4496-bf41-d2dda73de19a",
  "sub": "1234567890",
  "name": "John Doe",
  "exp": 15323232,
  "iat": 1516239022,
  "scope": ["admin", "user"]
}
```

Payload 部分默认是不加密的，**一定不要将隐私信息存放在 Payload 当中！！！**JSON 形式的 Payload 被转换成 Base64 编码，成为 JWT 的第二部分。

**Signature** 部分是对前两部分的签名，作用是防止 JWT（主要是 payload） 被篡改。

这个签名的生成需要用到：

- Header + Payload。
- 存放在服务端的密钥(一定不要泄露出去)。
- 签名算法。

签名的计算公式如下：



```plain
HMACSHA256(
  base64UrlEncode(header) + "." +
  base64UrlEncode(payload),
  secret)
```

算出签名以后，把 Header、Payload、Signature 三个部分拼成一个字符串，每个部分之间用"点"（`.`）分隔，这个字符串就是 JWT 

![image-20260830145838791](assets/image-20260830145838791.png)

### 1.5 登陆

+ 服务修改

① 增加`pydantic`请求数据`app/schemas/auth.py`

```python
class LoginParam(BaseModel):
    email:EmailStr = Field(...,description="邮箱",max_length=128)
    password:str = Field(...,description="密码",max_length=20,min_length=6)

class LoginResult(BaseModel):
    access_token:str = Field(...,description="访问令牌")
    expires_in:int = Field(...,description="令牌有效期")
    refresh_token:str = Field(...,description="刷新令牌")
```

②新增`jwt`   `app/utils/jwt_util.py`

```python
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
    if not payload:
        raise HTTPException(status_code=401, detail="无效的token")
    if payload.get("typ") != token_type:
        raise HTTPException(status_code=401, detail="无效的token")
    return payload

```

③新增服务`app/services/auth.py`

```python
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
```

+ 路由修改 `app/routers/auth.py`

```python
@router.post("/login")
async def login(param:LoginParam,
                auth_service:Annotated[AuthService,Depends(deps.get_auth_service)]):
    return ApiResult.success(await auth_service.login(param))
```



### 1.6 认证



### 1.7 refresh_token



### 1.8 异常处理



### 1.9 博客相关模型定义



### 1.10 实现分类管理接口



### 1.11 标签管理接口



### 1.12 文章创建接口



### 1.13 文章创建与删除接口

## 3. 参考

1. [Fastapi依赖项](https://fastapi.tiangolo.com/zh/tutorial/dependencies/)
1. [Tortoise ORM 1.1.7文档](https://tortoise.github.io/getting_started.html)
3. [UV官方文档](https://docs.astral.sh/uv/getting-started/installation/#__tabbed_2_2)
3. [uv菜鸟教程](https://www.runoob.com/python3/uv-tutorial.html)
3. [JWT 基础概念详解](https://javaguide.cn/system-design/security/jwt-intro.html#%E4%BB%80%E4%B9%88%E6%98%AF-jwt)