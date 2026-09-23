from typing import Annotated, List

from fastapi import APIRouter, Depends

from app.core import deps
from app.schemas.categories import CategoryStatResult
from app.schemas.common import ApiResult
from app.services.categories import CategoryService

router = APIRouter(prefix="/categories", tags=["分类接口"])

@router.get("/stat", response_model=ApiResult[List[CategoryStatResult]], description="分类统计接口")
async def stat_categories(category_service: Annotated[CategoryService, Depends(deps.get_category_service)]):
    return ApiResult.success(await category_service.stat_categories())