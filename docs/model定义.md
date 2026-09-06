# 模型定义

1. **数据模型（`Pydantic Model`）** - 用于请求/响应验证
2. **数据库模型（`ORM Model`）** - 用于数据库操作

| 对比             | `Pydantic` 模型     | `ORM` 模型                    |
| :--------------- | :------------------ | :---------------------------- |
| **用途**         | `API` 请求/响应验证 | 数据库表映射                  |
| **位置**         | `schemas/` 目录     | `models/` 目录                |
| **基类**         | `BaseModel`         | `Model` (Tortoise/SQLAlchemy) |
| **功能**         | 数据验证、序列化    | CRUD 操作、关联查询           |
| **是否存数据库** | 不存储              | 存储到数据库                  |
| **包含敏感字段** | 不包含（如密码）    | 包含所有字段                  |



## 1. ORM



**ORM（Object-Relational Mapping，对象关系映射）** 是一种编程技术，让你可以用**面向对象的方式**操作数据库，而不需要写 SQL 语句。

```text
数据库表 (Table)     ↔    Python 类 (Class)
表中的记录 (Row)     ↔    类的实例 (Object)
表的字段 (Column)    ↔    类的属性 (Attribute)

SQL: SELECT * FROM users WHERE id = 1;
ORM: User.get(id=1)
```

**一句话**：`ORM` 让你用 Python 代码操作数据库，而不是写 `SQL`。

### 1.1 基础模型定义

```python
# app/models/user.py
from tortoise import Model, fields
from tortoise.models import Model

class User(Model):
    """
    用户表 ORM 模型
    
    这个类对应数据库中的 users 表
    每个属性对应表中的一个字段
    """
    
    # ===== 字段定义 =====
    
    # 主键：自增整数
    id = fields.IntField(pk=True)
    
    # 字符串字段：最大长度 50，唯一，不允许为空
    username = fields.CharField(
        max_length=50,
        unique=True,
        null=False,
        db_index=True,
        description="用户名"
    )
    
    # 字符串字段：最大长度 128，唯一
    email = fields.CharField(
        max_length=128,
        unique=True,
        null=False,
        db_index=True,
        description="邮箱"
    )
    
    # 字符串字段：存储哈希密码
    password_hash = fields.CharField(
        max_length=128,
        null=False,
        description="密码哈希"
    )
    
    # 可选字段：允许为空
    avatar = fields.CharField(
        max_length=255,
        null=True,
        default=None,
        description="头像URL"
    )
    
    # 整数字段：带范围约束
    age = fields.IntField(
        null=True,
        min_value=0,
        max_value=150,
        description="年龄"
    )
    
    # 布尔字段：默认值
    is_active = fields.BooleanField(
        default=True,
        null=False,
        description="是否激活"
    )
    
    is_deleted = fields.BooleanField(
        default=False,
        null=False,
        description="软删除标记"
    )
    
    # 枚举字段（使用 choices）
    role = fields.CharField(
        max_length=20,
        default="user",
        choices={
            "user": "普通用户",
            "moderator": "版主",
            "admin": "管理员"
        },
        description="用户角色"
    )
    
    # 时间字段：自动填充
    created_at = fields.DatetimeField(
        auto_now_add=True,  # 创建时自动设置当前时间
        description="创建时间"
    )
    
    updated_at = fields.DatetimeField(
        auto_now=True,  # 更新时自动设置当前时间
        description="更新时间"
    )
    
    last_login = fields.DatetimeField(
        null=True,
        description="最后登录时间"
    )
    
    # ===== 元数据配置 =====
    class Meta:
        table = "users"                      # 数据库表名
        table_description = "用户表"          # 表注释
        ordering = ["-created_at"]           # 默认排序
        indexes = [                          # 复合索引
            ("email", "is_active"),
        ]
    
    # ===== 模型方法 =====
    
    def __str__(self):
        """字符串表示"""
        return f"<User {self.username}>"
    
    def __repr__(self):
        """调试用表示"""
        return f"User(id={self.id}, username={self.username})"
    
    # ===== 实例方法 =====
    
    async def soft_delete(self):
        """软删除（标记删除）"""
        self.is_deleted = True
        await self.save()
    
    async def activate(self):
        """激活用户"""
        self.is_active = True
        await self.save()
    
    async def deactivate(self):
        """禁用用户"""
        self.is_active = False
        await self.save()
    
    async def update_last_login(self):
        """更新最后登录时间"""
        self.last_login = datetime.now()
        await self.save()
    
    def is_admin(self) -> bool:
        """检查是否为管理员"""
        return self.role == "admin"
    
    # ===== 类方法 =====
    
    @classmethod
    async def get_by_email(cls, email: str):
        """通过邮箱获取用户"""
        return await cls.get_or_none(email=email, is_deleted=False)
    
    @classmethod
    async def get_by_username(cls, username: str):
        """通过用户名获取用户"""
        return await cls.get_or_none(username=username, is_deleted=False)
    
    @classmethod
    async def get_active_users(cls):
        """获取所有活跃用户"""
        return await cls.filter(is_active=True, is_deleted=False).all()
    
    @classmethod
    async def get_admins(cls):
        """获取所有管理员"""
        return await cls.filter(role="admin", is_deleted=False).all()
    
    @classmethod
    async def search(cls, keyword: str):
        """搜索用户"""
        return await cls.filter(
            Q(username__icontains=keyword) | 
            Q(email__icontains=keyword),
            is_deleted=False
        ).all()
```



![image-20260905173903894](assets/image-20260905173903894.png)

## 2. Tortoise

参考: [Tortoise文档](https://tortoise.org.cn/index.html)

+ 步骤

```bash
安装依赖->配置链接->定义模型->初始化数据库->数据库迁移->CRUD操作->关闭链接
```

+ 安装

```bash
# 安装 Tortoise ORM 核心库
uv add tortoise-orm

# 安装数据库驱动（根据使用的数据库选择）
# PostgreSQL
uv add asyncpg

# MySQL
uv add aiomysql

# SQLite（内置支持，无需额外安装）
```



### 2. 1 安装

```bash
pip install "tortoise-orm[accel]"
```

### 2.2  `ORM`初始化程序

+ 方法1： 基础配置：`db_url` + `modules`



```python
from tortoise import Tortoise

async def init():
    await Tortoise.init(
        db_url='sqlite://db.sqlite3',           # 数据库连接URL
        modules={'models': ['app.models']}      # 模型所在模块
    )
    # 生成数据库表结构（仅限开发环境）
    await Tortoise.generate_schemas()

```

**`db_url`**: 指定数据库连接，例如 `sqlite://db.sqlite3` 或 `postgres://user:pass@localhost:5432/mydb`。

**`modules`**: 一个字典，用于告诉 Tortoise 从哪个 Python 模块导入模型，格式为 `{'app_name': ['模块路径']}`。

+ 方法2：`config` 字典

当需要连接多个数据库、配置路由或进行更复杂的设置时，推荐使用这种方式。

如果你在 `app.models` 模块（或你指定的任何加载模型的位置）中定义了 `__models__` 变量，`generate_schemas()` 将使用该列表，而不是自动发现模型。

初始化应用程序的另一种方法是使用带有 `config` 参数的 `Tortoise.init()` 方法。

```python
from tortoise import Tortoise

CONFIG = {
    "connections": {  # 定义数据库连接
        "default": {
            "engine": "tortoise.backends.sqlite",
            "credentials": {"file_path": "default.sqlite3"}
        },
        "another_db": {
            "engine": "tortoise.backends.postgresql",
            "credentials": {
                "host": "localhost",
                "port": "5432",
                "user": "postgres",
                "password": "123456",
                "database": "test_db"
            }
        }
    },
    "apps": {  # 定义应用及其模型
        "models": {
            "models": ["app.models", "aerich.models"],
            "default_connection": "default"
        }
    }
}

async def init():
    await Tortoise.init(config=CONFIG)
    await Tortoise.generate_schemas()
```

在 `FastAPI` 项目中，可以利用 `register_tortoise` 工具，在应用启动和关闭时自动处理连接的初始化与清理。

```python
from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise

app = FastAPI()

register_tortoise(
    app,
    db_url="sqlite://db.sqlite3",
    modules={"models": ["app.models"]},
    generate_schemas=True,  # 建议开发时开启
    add_exception_handlers=True,
)
```

**清理连接**: 在应用关闭时，必须调用 `Tortoise.close_connections()` 来正确关闭所有数据库连接，防止应用无法正常退出

示例：

```python
"""应用配置中心。

统一读取环境变量和 ORM 配置，保证数据库、邮件等敏感参数可以集中管理。
"""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# 获取项目根目录，确保 .env 文件能够被正确定位。
BASE_DIR = Path(__file__).parent.parent.parent


class Settings(BaseSettings):
    """从 .env 文件加载配置项。

    BaseSettings 会自动读取环境变量，并在未显式配置时使用默认值。
    """

    DATABASE_URL: str = ""

    SMTP_SERVER: str = ""
    SMTP_PORT: int = 465
    SMTP_USER: str = ""
    SMTP_PASS: str = ""

    SECURITY_KEY:str = ''
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    JWT_ISS:str = 'bogeblog'
    JWT_AUD:str = 'web'

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",  # 使用项目根目录下的 .env 文件。
        env_file_encoding="utf-8",
    )


# 初始化配置实例，供业务代码直接使用 settings.DATABASE_URL 等字段。
settings = Settings()

# V3：当前使用的 Tortoise ORM 配置，连接指定的 PostgreSQL 数据库。
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

#### 2.2.1 `db_url + modules` 方式初始化初始化

```python
# ============================================================
# 方式一：使用 db_url + modules 初始化
# ============================================================

async def test_init_with_db_url():
    """
    测试方式一：db_url + modules
    
    这是 Tortoise ORM 最简单、最直接的初始化方式。
    通过数据库连接 URL 和模块路径两个参数即可完成配置。
    
    特点：
    - 最简洁的方式
    - 适合单数据库场景
    - 适合快速开始
    """
    print("\n" + "=" * 60)
    print("测试方式一：db_url + modules")
    print("=" * 60)
    
    try:
        # 1. 初始化
        print("步骤1: 初始化 Tortoise")
        # await Tortoise.init() 是 Tortoise ORM 的核心初始化方法
        # 
        # 参数说明：
        #   - db_url: 数据库连接字符串
        #     - SQLite:  "sqlite://db.sqlite3"
        #     - PostgreSQL: "postgres://user:pass@localhost:5432/dbname"
        #     - MySQL: "mysql://user:pass@localhost:3306/dbname"
        #   
        #   - modules: 模型所在模块的配置
        #     - 格式: {"应用名": ["模块路径1", "模块路径2"]}
        #     - "models" 是应用名（可以自定义）
        #     - ["app.models"] 指向包含模型的 Python 包
        # 
        # 执行过程：
        #   1. 解析数据库连接 URL
        #   2. 创建数据库连接池
        #   3. 加载指定模块中的模型
        #   4. 建立模型与数据库表的映射关系       
        await Tortoise.init(
            db_url=SQLITE_DB_URL,
            modules={"models": ["app.models"]}
        )
        print("初始化成功")
        
        # 2. 生成表结构
        print("步骤2: 生成表结构")
        await Tortoise.generate_schemas()
        print("表结构生成成功")
        
        # 3. 测试连接
        print("步骤3: 测试数据库操作")
        # 创建测试数据
        user = await User.create(
            username="test_user_1",
            email="test1@example.com",
            password_hash="hashed_password_1"
        )
        print(f"创建用户成功: {user.username} (ID: {user.id})")
        
        # 查询测试
        found = await User.get_by_email("test1@example.com")
        print(f"查询用户成功: {found.username} (邮箱: {found.email})")
        
        # 4. 清理数据
        await User.filter().delete()
        print("清理测试数据成功")
        
        return True
        
    except Exception as e:
        print(f"测试失败: {e}")
        return False
        
    finally:
        # 5. 关闭连接
        await Tortoise.close_connections()
        print("数据库连接已关闭")
        print("-" * 60)
```

#### 2.2.2 使用 config 字典初始化

```bash
# 新项目需要初始化
uv init
# 需要安装aerich
uv add aerich

pip install aerich
```



+ 配置

```python
# ===== 配置3: Tortoise ORM 配置字典 =====
TORTOISE_ORM_CONFIG = {
    # 连接配置
    "connections": {
        "default": {
            # 数据库引擎
            #   - tortoise.backends.sqlite    → SQLite
            #   - tortoise.backends.asyncpg   → PostgreSQL
            #   - tortoise.backends.mysql     → MySQL
            "engine": "tortoise.backends.sqlite",
            # 连接凭证
            "credentials": {
                "file_path": "test_db.sqlite3",
                # ===== SQLite 配置 =====
                # SQLite 只需要指定文件路径
                "file_path": "test_db.sqlite3",
                # 可选参数：
                #   - ":memory:"  → 使用内存数据库（用于测试）
                #   - "db.sqlite3" → 使用文件数据库
                
                # ===== PostgreSQL 配置（示例） =====
                # "host": "localhost",        # 数据库主机地址
                # "port": 5432,               # 数据库端口
                # "user": "postgres",         # 数据库用户名
                # "password": "123456",       # 数据库密码
                # "database": "myblog",       # 数据库名称
                # "schema": "public",         # 使用的 schema（可选）
                # "pool_min_size": 1,         # 连接池最小连接数
                # "pool_max_size": 10,        # 连接池最大连接数
                # "pool_max_queries": 50000,  # 连接最大查询次数
                # "pool_timeout": 30,         # 获取连接超时时间（秒）
                
                # ===== MySQL 配置（示例） =====
                # "host": "localhost",
                # "port": 3306,
                # "user": "root",
                # "password": "123456",
                # "database": "myblog",
                # "charset": "utf8mb4",       # 字符集
                # "pool_recycle": 3600,       # 连接回收时间（秒）                
            }
        }
    },
    # 应用模型配置
    "apps": {
        "models": {
            "models": [
                "app.models",        # 业务模型
                "aerich.models",     # 迁移管理模型（必须）
            ],
            "default_connection": "default",
        }
    },
    "use_tz": False,
    "timezone": "Asia/Shanghai",
}
```

+ 实现

```python
# ============================================================
# 方式二：使用 config 字典初始化
# ============================================================

async def test_init_with_config():
    """
    测试方式二：config 字典
    
    特点：
    - 更灵活
    - 适合多数据库场景
    - 支持更精细的配置
    """
    print("\n" + "=" * 60)
    print("📌 测试方式二：config 字典")
    print("=" * 60)
    
    try:
        # 1. 初始化
        print("▶ 步骤1: 使用 config 字典初始化")
        await Tortoise.init(config=TORTOISE_ORM_CONFIG)
        print("✅ 初始化成功")
        
        # 2. 生成表结构
        print("▶ 步骤2: 生成表结构")
        await Tortoise.generate_schemas()
        print("✅ 表结构生成成功")
        
        # 3. 测试操作
        print("▶ 步骤3: 测试数据库操作")
        user = await User.create(
            username="test_user_2",
            email="test2@example.com",
            password_hash="hashed_password_2"
        )
        print(f"✅ 创建用户成功: {user.username}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False
        
    finally:
        await Tortoise.close_connections()
        print("🔒 数据库连接已关闭")
        print("-" * 60)

```

#### 2.2.3 使用 `FastAPI register_tortoise`

```python
# ============================================================
# 方式三：使用 FastAPI register_tortoise
# ============================================================

async def test_init_with_fastapi_register():
    """
    测试方式三：FastAPI register_tortoise
    这是 FastAPI 官方推荐的 Tortoise ORM 集成方式，
    通过 register_tortoise 工具函数自动管理数据库连接的生命周期。
    特点：
    - 自动管理生命周期
    - 自动处理异常
    - 推荐用于 FastAPI 项目
    """
    print("\n" + "=" * 60)
    print("📌 测试方式三：FastAPI register_tortoise")
    print("=" * 60)
    
    try:
        from fastapi import FastAPI
        from tortoise.contrib.fastapi import register_tortoise
        
        # 1. 创建 FastAPI 应用
        app = FastAPI()
        print("✅ FastAPI 应用创建成功")
        
        # 2. 注册 Tortoise
        print("▶ 步骤2: 使用 register_tortoise 注册")
        # 参数说明：
        #   - app: FastAPI 应用实例（必须）
        #   - db_url: 数据库连接字符串（与 config 二选一）
        #   - config: Tortoise ORM 配置字典（与 db_url 二选一）
        #   - modules: 模型模块路径（当使用 db_url 时必须）
        #   - generate_schemas: 是否自动创建表（开发环境用）
        #   - add_exception_handlers: 是否添加异常处理器
        #   - app_name: 应用名称（默认 "models"）        
        register_tortoise(
            app,
            # db_url=SQLITE_DB_URL,
            config=TORTOISE_ORM_CONFIG,   # Tortoise ORM 配置
            modules={"models": ["app.models"]},
            generate_schemas=True,
            add_exception_handlers=True,
        )
        print("✅ register_tortoise 注册成功")
        
        # 3. 测试：模拟请求上下文
        print("▶ 步骤3: 测试数据库操作")
        
        # 创建用户
        user = await User.create(
            username="test_user_3",
            email="test3@example.com",
            password_hash="hashed_password_3"
        )
        print(f"✅ 创建用户成功: {user.username}")
        
        # 查询验证
        count = await User.filter().count()
        print(f"✅ 当前用户总数: {count}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False
        
    finally:
        await Tortoise.close_connections()
        print("🔒 数据库连接已关闭")
        print("-" * 60)


```

![image-20260906112008509](assets/image-20260906112008509.png)

## 3.` Aerich`

`Aerich `和`Tortoise-ORM `是**分工明确、协同工作**的**官方搭档**。

- **Tortoise-ORM**：是核心的 **ORM (对象关系映射) 库**。它的主要职责是在 Python 代码和数据库之间搭起桥梁，让你通过操作 Python 对象（模型）来读写数据库，而不用直接编写 SQL 语句。
- **Aerich**：则是专门为 Tortoise-ORM 设计的**数据库版本管理与迁移工具**。它的主要职责是跟踪你模型（Model）的变化，并把这些变化同步到真实的数据库表结构上。



1. **定义与配置**：首先，你在代码中定义好 Tortoise-ORM 的**模型（Model）**（例如用户表、文章表）和数据库连接配置。
2. **初始化 Aerich**：在项目初始化时，使用 `aerich init` 命令来初始化迁移环境，并在 Tortoise-ORM 的配置中加上 `aerich.models`。这相当于告诉 Aerich：“嘿，请关注这些模型的变化”。
3. **生成迁移**：当你修改了模型（比如给 `User` 模型加了 `age` 字段），运行 `aerich migrate` 命令。Aerich 就会自动分析你的模型和当前数据库的差异，并生成一个**迁移文件**（一个记录了这次变更的 Python 脚本）。
4. **应用迁移**：最后，运行 `aerich upgrade` 命令，Aerich 就会执行迁移文件中的指令，把改动正式应用到你的数据库里，让数据库表结构和你的模型保持一致。

[Aerich ](https://github.com/tortoise/aerich/blob/dev/README.md)

[Aerich Migration](https://tortoise.github.io/migration.html)