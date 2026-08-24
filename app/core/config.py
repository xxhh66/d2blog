# TORTOISE_ORM = {
#     "connections": {"default": "mysql://root:123456@127.0.0.1:3306/test"},
#     "apps": {
#         "models": {
#             "models": ["tests.models", "aerich.models"],
#             "default_connection": "default",
#         },
#     },
# }

TORTOISE_ORM = {
    "connections": {"default": "postgres://postgres:123456@10.10.10.7:5432/fastapi"},
    "apps": {
        "models": {
            "models": ["app.models", "aerich.models"],
            "default_connection": "default",
        },
    },
}