#  装饰器

| 装饰器            | 来源        | 用途           |
| :---------------- | :---------- | :------------- |
| `@classmethod`    | 内置        | 定义类方法     |
| `@staticmethod`   | 内置        | 定义静态方法   |
| `@property`       | 内置        | 将方法转为属性 |
| `@dataclass`      | dataclasses | 生成数据类     |
| `@abstractmethod` | abc         | 定义抽象方法   |
| `@wraps`          | functools   | 保留元数据     |
| `@lru_cache`      | functools   | 缓存结果       |
| `@cache`          | functools   | 永久缓存       |
| `@app.get()`      | FastAPI     | 路由装饰器     |
| `@validator`      | Pydantic    | 字段验证       |
| `@pytest.fixture` | pytest      | 测试夹具       |
| `@login_required` | Django      | 登录验证       |

## 1.常用装饰器分类

### 1.1 类相关装饰器

#### 1.1.1 `@classmethod` - 类方法



```python
class User:
    name = "User"
    
    @classmethod
    def get_name(cls):
        """第一个参数是 cls（类本身）"""
        return cls.name

# 使用
print(User.get_name())  # "User" - 无需实例
```



#### 1.1.2. `@staticmethod` - 静态方法



```python
class MathUtils:
    @staticmethod
    def add(a, b):
        """没有 self 或 cls 参数"""
        return a + b

# 使用
print(MathUtils.add(3, 5))  # 8 - 无需实例
```



#### 1.1.3. `@property` - 属性方法



```python
class Person:
    def __init__(self, first_name, last_name):
        self.first_name = first_name
        self.last_name = last_name
    
    @property
    def full_name(self):
        """像访问属性一样调用方法"""
        return f"{self.first_name} {self.last_name}"

# 使用
person = Person("John", "Doe")
print(person.full_name)  # "John Doe" - 无需括号
```



#### 1.1.4. `@dataclass` - 数据类（ 3.7+）



```python
from dataclasses import dataclass

@dataclass
class Point:
    x: int
    y: int
    
    def distance_from_origin(self):
        return (self.x ** 2 + self.y ** 2) ** 0.5

# 使用
point = Point(3, 4)
print(point.x)  # 3 - 自动生成 __init__ 等方法
```



#### 1.1.5. `@abstractmethod` - 抽象方法



```python
from abc import ABC, abstractmethod

class Animal(ABC):
    @abstractmethod
    def sound(self):
        """子类必须实现这个方法"""
        pass

class Dog(Animal):
    def sound(self):
        return "Woof!"

# Dog() 可以正常使用
# Animal() 会报错（抽象类不能实例化）
```

### 1.2.函数相关装饰器

#### 1.2.1. `@functools.wraps` - 保留元数据



```python
from functools import wraps

def my_decorator(func):
    @wraps(func)  # 保留原函数的名称和文档
    def wrapper(*args, **kwargs):
        """Wrapper 文档"""
        print("装饰器执行")
        return func(*args, **kwargs)
    return wrapper

@my_decorator
def say_hello():
    """Hello 文档"""
    print("Hello!")

print(say_hello.__name__)   # "say_hello"（没有 @wraps 会变成 "wrapper"）
print(say_hello.__doc__)    # "Hello 文档"
```



#### 1.2.2. `@lru_cache` - 缓存结果



```python
from functools import lru_cache

@lru_cache(maxsize=128)
def fibonacci(n):
    """计算斐波那契数列（结果会被缓存）"""
    if n < 2:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# 第一次计算慢，之后瞬间返回
print(fibonacci(30))  # 计算并缓存
print(fibonacci(30))  # 直接从缓存返回
```



#### 1.2.3. `@cache` - 简单缓存（ 3.9+）



```python
from functools import cache

@cache
def expensive_function(x):
    """结果永久缓存"""
    return x * x
```



#### 1.2.4. `@asyncio.coroutine` - 协程（旧版）



```python
import asyncio

@asyncio.coroutine
def old_coroutine():
    yield from asyncio.sleep(1)
    return "Done"

# 现代  使用 async def
async def modern_coroutine():
    await asyncio.sleep(1)
    return "Done"
```



------

### 1.3.FastAPI 相关装饰器

#### 1.3.1. 路由装饰器



```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")          # GET 请求
@app.post("/items")    # POST 请求
@app.put("/items/{id}") # PUT 请求
@app.delete("/items/{id}") # DELETE 请求
@app.patch("/items/{id}")  # PATCH 请求
async def handle():
    return {"message": "ok"}
```



#### 1.3.2. 生命周期装饰器



```python
@app.on_event("startup")
async def startup():
    """应用启动时执行"""
    print("服务器启动")

@app.on_event("shutdown")
async def shutdown():
    """应用关闭时执行"""
    print("服务器关闭")
```



#### 1.3.3. 中间件装饰器



```python
@app.middleware("http")
async def add_custom_header(request, call_next):
    response = await call_next(request)
    response.headers["X-Custom"] = "Value"
    return response
```



------

### 1.4 Pydantic 验证装饰器

#### 1.4.1. `@validator` - 字段验证



```python
from pydantic import BaseModel, validator

class User(BaseModel):
    email: str
    password: str
    
    @validator('email')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('邮箱格式不正确')
        return v.lower()  # 转换为小写
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('密码至少8位')
        return v
```



#### 1.4.2. `@root_validator` - 全局验证



```python
from pydantic import BaseModel, root_validator

class Registration(BaseModel):
    password: str
    confirm_password: str
    
    @root_validator
    def validate_passwords_match(cls, values):
        if values.get('password') != values.get('confirm_password'):
            raise ValueError('两次密码不一致')
        return values
```



#### 1.4.3. `@field_validator` - Pydantic v2



```python
from pydantic import BaseModel, field_validator

class User(BaseModel):
    age: int
    
    @field_validator('age')
    def validate_age(cls, v):
        if v < 0 or v > 150:
            raise ValueError('年龄必须在 0-150 之间')
        return v
```



------

### 1.5.测试框架装饰器

#### 1.5.1. `@pytest.fixture` - 测试夹具



```python
import pytest

@pytest.fixture
def db_session():
    """为测试提供数据库连接"""
    db = create_database()
    yield db
    db.close()

def test_user(db_session):
    user = db_session.get_user(1)
    assert user.name == "Alice"
```



#### 1.5.2. `@pytest.mark.parametrize` - 参数化测试



```python
import pytest

@pytest.mark.parametrize("input,expected", [
    (1, 2),
    (2, 4),
    (3, 6),
])
def test_multiply_by_two(input, expected):
    assert input * 2 == expected
```



#### 1.5.3. `@pytest.mark.asyncio` - 异步测试



```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result == "expected"
```



------

### 1.6. Django 装饰器



```python
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page

@login_required
def profile(request):
    """需要登录才能访问"""
    return render(request, 'profile.html')

@cache_page(60 * 15)  # 缓存 15 分钟
def news_list(request):
    """缓存页面"""
    return render(request, 'news.html')
```



------

## 2.自定义装饰器

### 2.1. 无参数装饰器



```python
def timer(func):
    """计算函数执行时间"""
    from functools import wraps
    import time
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} 执行时间: {end - start:.2f}秒")
        return result
    return wrapper

@timer
def slow_function():
    time.sleep(1)
    return "Done"
```



### 2.2. 带参数装饰器



```python
def repeat(times):
    """重复执行函数 n 次"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            results = []
            for _ in range(times):
                results.append(func(*args, **kwargs))
            return results
        return wrapper
    return decorator

@repeat(3)
def say_hello():
    return "Hello!"

print(say_hello())  # ["Hello!", "Hello!", "Hello!"]
```



### 2.3. 类装饰器



```python
class CountCalls:
    """计数函数调用次数"""
    def __init__(self, func):
        self.func = func
        self.count = 0
    
    def __call__(self, *args, **kwargs):
        self.count += 1
        print(f"调用次数: {self.count}")
        return self.func(*args, **kwargs)

@CountCalls
def say_hello():
    print("Hello!")

say_hello()  # 调用次数: 1
say_hello()  # 调用次数: 2
```



### 2.4. 带状态的装饰器



```python
def retry(max_attempts=3):
    """失败时重试"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    print(f"第 {attempt + 1} 次尝试失败")
            raise last_exception
        return wrapper
    return decorator

@retry(max_attempts=5)
def unstable_function():
    import random
    if random.random() > 0.5:
        raise ValueError("随机失败")
    return "成功"
```

