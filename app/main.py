"""FastAPI 应用入口。

该文件负责创建应用实例、注册数据库和路由，并暴露最基础的健康检查接口。
"""

from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise

from app.core import config
from app.routers import auth,routers_deps

# 创建应用实例，后续所有路由和中间件都挂载在此对象上。
myapp = FastAPI()

# 初始化 Tortoise ORM，并绑定到当前 FastAPI 应用。
register_tortoise(myapp, config=config.TORTOISE_ORM, generate_schemas=False)

# 引入认证相关路由，统一加上 /api 前缀。
myapp.include_router(auth.router, prefix="/api")
myapp.include_router(routers_deps.router, prefix="/router_deps")


@myapp.get("/")
async def root():
    """提供最简单的健康检查接口，供开发阶段快速验证服务状态。"""
    return {"hello": "world"}