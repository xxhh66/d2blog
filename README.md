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

增加`app/schemas/common.py`下缓存功能

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
verify_code_cache = TTLCache(maxsize=100, ttl=60 * 3)
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

1. [Tortoise ORM 1.1.7文档](https://tortoise.github.io/getting_started.html)
2. [UV官方文档](https://docs.astral.sh/uv/getting-started/installation/#__tabbed_2_2)

3. [uv菜鸟教程](https://www.runoob.com/python3/uv-tutorial.html)