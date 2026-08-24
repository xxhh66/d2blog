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