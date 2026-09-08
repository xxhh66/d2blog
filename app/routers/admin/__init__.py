from fastapi import APIRouter

from app.routers.admin import categories,tags,articles

admin_router = APIRouter(prefix="/admin")
admin_router.include_router(categories.router)
admin_router.include_router(tags.router)
admin_router.include_router(articles.router)