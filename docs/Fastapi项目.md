# Fastapi项目

## 1. Fastapi 项目结构

创建新的`Fastapi`项目时，项目的结构大概如下：



```bash
fastapi_project/                   # 项目根目录
│
├── app/                           # 主应用目录（核心代码）
│   ├── __init__.py                # 包标识
│   ├── main.py                    # 应用入口（FastAPI 实例）
│   │
│   ├── core/                      # 核心配置模块
│   │   ├── __init__.py
│   │   ├── config.py             # 配置管理（读取 .env）
│   │   └── deps.py               # 依赖注入（Depends）
│   │
│   ├── models/                    # ORM 数据模型（数据库表）
│   │   ├── __init__.py
│   │   └── user.py               # 用户模型
│   │
│   ├── schemas/                   # Pydantic 模型（请求/响应验证）
│   │   ├── __init__.py
│   │   └── user.py               # 用户请求/响应结构
│   │
│   ├── routers/                   # 路由层（API 端点）
│   │   ├── __init__.py
│   │   └── auth.py               # 认证路由（登录/注册）
│   │
│   ├── services/                  # 业务逻辑层
│   │   ├── __init__.py
│   │   └── auth_service.py       # 认证业务逻辑
│   │
│   └── utils/                     # 工具函数
│       ├── __init__.py
│       ├── smtp_util.py          # 邮件发送
│       └── pwd_util.py           # 密码加密
│
├── .env                           # 环境变量（敏感信息，不提交 Git）
├── .env.example                   # 环境变量示例（提交 Git）
├── requirements.txt               # 项目依赖
└── README.md                      # 项目说明
```

### 1.1. `app/core`



### 1.2 `app/models`

`app/models/` 是 FastAPI 项目中**与数据库交互的核心桥梁**，主要有 **3 大作用**：

🎯 三大核心作用

| 作用                 | 说明                                                   | 类比                   |
| :------------------- | :----------------------------------------------------- | :--------------------- |
| **① 定义表结构**     | 用 Python 类描述数据库表有哪些字段、类型、约束         | 建筑图纸（设计表结构） |
| **② ORM 数据库操作** | 提供 `create()`、`filter()`、`update()` 等方法操作数据 | 施工队（增删改查）     |
| **③ 迁移数据源**     | 供 Aerich 读取并生成数据库迁移文件                     | 设计蓝图（指导变更）   |

1️⃣ 定义表结构

```python

# app/models/user.py
from tortoise import Model, fields

class User(Model):
    """
    定义 users 表的结构
    
    这个类对应数据库中的一张表，每个属性对应一个字段
    """
    
    # ===== 字段定义 =====
    # 主键：自增整数
    id = fields.IntField(pk=True)
    
    # 字符串字段：最大长度 128，唯一索引
    email = fields.CharField(
        max_length=128, 
        unique=True,           # 唯一约束
        db_index=True,         # 创建索引
        null=False,            # 不允许为空
        description="邮箱"      # 字段注释
    )
    
    # 字符串字段：存储加密后的密码
    password = fields.CharField(
        max_length=128,
        null=False,
        description="密码哈希值"
    )
    
    # 布尔字段：默认未删除
    is_deleted = fields.BooleanField(
        default=False,
        description="软删除标记"
    )
    
    # 时间字段：创建时自动填充
    created_at = fields.DatetimeField(
        auto_now_add=True,     # 创建时自动设置
        description="创建时间"
    )
    
    # 时间字段：更新时自动填充
    updated_at = fields.DatetimeField(
        auto_now=True,         # 每次更新时自动设置
        description="更新时间"
    )
    
    class Meta:
        table = "users"                # 数据库表名
        table_description = "用户表"    # 表注释
```

**对应 SQL**：

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(128) UNIQUE NOT NULL,
    password VARCHAR(128) NOT NULL,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

COMMENT ON TABLE users IS '用户表';
COMMENT ON COLUMN users.email IS '邮箱';
```

2️⃣ ORM 数据库操作

```python
# app/services/user_service.py
from app.models.user import User

class UserService:
    
    # ===== 创建数据 =====
    async def create_user(self, email: str, password: str):
        """插入一条新用户记录"""
        #  对应 SQL: INSERT INTO users (email, password) VALUES (?, ?)
        user = await User.create(
            email=email,
            password=password
        )
        return user
    
    # ===== 查询单条 =====
    async def get_user_by_id(self, user_id: int):
        """根据 ID 查询用户"""
        #  对应 SQL: SELECT * FROM users WHERE id = ? 
        return await User.get_or_none(id=user_id)
    
    async def get_user_by_email(self, email: str):
        """根据邮箱查询用户"""
        #  对应 SQL: SELECT * FROM users WHERE email = ?
        return await User.get_or_none(email=email)
    
    # ===== 查询多条 =====
    async def get_active_users(self):
        """获取所有未删除的用户"""
        #  对应 SQL: SELECT * FROM users WHERE is_deleted = FALSE
        return await User.filter(is_deleted=False).all()
    
    async def get_users_by_created_range(self, start, end):
        """按时间范围查询用户"""
        #  对应 SQL: SELECT * FROM users WHERE created_at BETWEEN ? AND ?
        return await User.filter(
            created_at__gte=start,   # >= start
            created_at__lte=end,     # <= end
            is_deleted=False
        ).all()
    
    # ===== 更新数据 =====
    async def update_user_email(self, user_id: int, new_email: str):
        """更新用户邮箱"""
        #  对应 SQL: UPDATE users SET email = ?, updated_at = NOW() WHERE id = ?
        user = await User.get(id=user_id)
        user.email = new_email
        await user.save()  # 保存变更
        return user
    
    async def soft_delete_user(self, user_id: int):
        """软删除用户（标记删除）"""
        #  对应 SQL: UPDATE users SET is_deleted = TRUE WHERE id = ?
        user = await User.get(id=user_id)
        user.is_deleted = True
        await user.save()
        return user
    
    # ===== 删除数据 =====
    async def hard_delete_user(self, user_id: int):
        """硬删除用户（物理删除，谨慎使用）"""
        #  对应 SQL: DELETE FROM users WHERE id = ?
        user = await User.get(id=user_id)
        await user.delete()
        return True
    
    # ===== 聚合查询 =====
    async def count_active_users(self):
        """统计未删除的用户数"""
        #  对应 SQL: SELECT COUNT(*) FROM users WHERE is_deleted = FALSE
        return await User.filter(is_deleted=False).count()
    
    # ===== 排序和分页 =====
    async def get_users_paginated(self, page: int = 1, size: int = 10):
        """分页查询用户"""
        #  对应 SQL: SELECT * FROM users WHERE is_deleted = FALSE 
        #             ORDER BY created_at DESC LIMIT ? OFFSET ?
        return await User.filter(is_deleted=False)\
            .order_by("-created_at")\
            .offset((page - 1) * size)\
            .limit(size)\
            .all()
```

3️⃣ 关联关系（一对多/多对多）

```python
# app/models/user.py
from tortoise import Model, fields

class User(Model):
    id = fields.IntField(pk=True)
    email = fields.CharField(max_length=128)
    
    # ===== 一对多关联 =====
    # 一个用户有多篇文章
    posts = fields.ReverseRelation["Post"]  # 反向关联
    
# app/models/post.py
class Post(Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=200)
    content = fields.TextField()
    
    # 外键：关联到 User 表
    author = fields.ForeignKeyField(
        "models.User",           # 关联到 User 模型
        related_name="posts",    # 反向关联名
        on_delete=fields.CASCADE # 用户删除时，文章也删除
    )

# ===== 使用关联查询 =====
async def get_user_with_posts(user_id: int):
    """获取用户及其所有文章"""
    # 预加载关联数据（避免 N+1 查询）
    user = await User.get(id=user_id).prefetch_related("posts")
    return user

# 使用示例
user = await get_user_with_posts(1)
print(f"用户: {user.email}")
for post in user.posts:  # 直接访问关联数据
    print(f"文章: {post.title}")
```

4️⃣ 迁移数据源

```python
# app/core/config.py
TORTOISE_ORM = {
    "connections": {"default": "postgres://..."},
    "apps": {
        "models": {
            # 告诉 Tortoise 去哪里找模型定义
            "models": ["app.models", "aerich.models"],
            "default_connection": "default",
        }
    }
}
```

迁移流程：

```bash
# 1. 修改 models/user.py（添加 age 字段）
class User(Model):
    email = fields.CharField(max_length=128)
    age = fields.IntField(null=True)  # ← 新增字段

# 2. 生成迁移文件（aerich 读取 models/）
uv run aerich migrate
# 输出: Migration 20240101_1234 generated

# 3. 查看迁移文件（自动生成）
# migrations/versions/20240101_1234_add_age.py
# 内容: ALTER TABLE users ADD COLUMN age INTEGER;

# 4. 执行迁移
uv run aerich upgrade
# 数据库 users 表增加 age 字段 
```



| 作用           | 代码示例                                         | 对应 SQL                        |
| :------------- | :----------------------------------------------- | :------------------------------ |
| **定义表结构** | `email = fields.CharField(max_length=128)`       | `email VARCHAR(128)`            |
| **插入数据**   | `await User.create(email="test@test.com")`       | `INSERT INTO users ...`         |
| **查询数据**   | `await User.filter(email="test@test.com")`       | `SELECT * FROM users WHERE ...` |
| **更新数据**   | `user.email = "new@test.com"; await user.save()` | `UPDATE users SET ...`          |
| **删除数据**   | `await user.delete()`                            | `DELETE FROM users ...`         |
| **迁移源**     | `aerich migrate` 读取 models                     | 生成 `ALTER TABLE` 语句         |

```bash
步骤 1: 定义模型 app/models/user.py
配置 app/core/config.py	
   ↓
步骤 2: 初始化 uv run aerich init 
   ↓
步骤 3: 生成迁移文件 ← uv run aerich migrate
   ↓
步骤 4: 执行迁移 ← uv run aerich upgrade
   ↓
步骤 5: 数据库文件/表创建完成 
```



### 1.3`app/schemas`



### 1.4 `app/routers`



### 1.5 `app/services`

