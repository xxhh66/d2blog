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