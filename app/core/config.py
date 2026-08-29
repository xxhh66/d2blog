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
# V2：历史配置示例，保留方便对比和回滚。
# TORTOISE_ORM = {
#     "connections": {"default": "postgres://postgres:123456@10.10.10.7:5432/fastapi"},
#     "apps": {
#         "models": {
#             "models": ["app.models", "aerich.models"],
#             "default_connection": "default",
#         },
#     },
# }

# V1：最早版本示例，用于记录原始配置思路。
# TORTOISE_ORM = {
#     "connections": {"default": "mysql://root:123456@127.0.0.1:3306/test"},
#     "apps": {
#         "models": {
#             "models": ["tests.models", "aerich.models"],
#             "default_connection": "default",
#         },
#     },
# }