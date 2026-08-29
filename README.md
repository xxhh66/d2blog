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



### 1.4 jwt



### 1.5 登陆



### 1.6 认证



### 1.7 refresh_token



### 1.8 异常处理



### 1.9 博客相关模型定义



### 1.10 实现分类管理接口



### 1.11 标签管理接口



### 1.12 文章创建接口



### 1.13 文章创建与删除接口





### 1. 参考

1. [Fastapi依赖项](https://fastapi.tiangolo.com/zh/tutorial/dependencies/)
1. [Tortoise ORM 1.1.7文档](https://tortoise.github.io/getting_started.html)
3. [UV官方文档](https://docs.astral.sh/uv/getting-started/installation/#__tabbed_2_2)
3. [uv菜鸟教程](https://www.runoob.com/python3/uv-tutorial.html)