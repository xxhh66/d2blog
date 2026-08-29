from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

# 获取项目根目录（bogo_blog）
BASE_DIR = Path(__file__).parent.parent.parent

class Settings(BaseSettings):
    DATABASE_URL: str = ""

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",   # 写绝对路径！
        env_file_encoding="utf-8"
    )

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
# V2
# TORTOISE_ORM = {
#     "connections": {"default": "postgres://postgres:123456@10.10.10.7:5432/fastapi"},
#     "apps": {
#         "models": {
#             "models": ["app.models", "aerich.models"],
#             "default_connection": "default",
#         },
#     },
# }

# V1
# TORTOISE_ORM = {
#     "connections": {"default": "mysql://root:123456@127.0.0.1:3306/test"},
#     "apps": {
#         "models": {
#             "models": ["tests.models", "aerich.models"],
#             "default_connection": "default",
#         },
#     },
# }