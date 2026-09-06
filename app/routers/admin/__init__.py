from fastapi import APIRouter

from app.routers.admin import categories,tags

admin_router = APIRouter(prefix="/admin")
admin_router.include_router(categories.router)
admin_router.include_router(tags.router)