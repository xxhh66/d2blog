from typing import Annotated,List
from fastapi import APIRouter,Depends
from app.core import deps
from app.models import User
from app.schemas.categories import CategoryCreateParam,CategoryUpdateParam,CategoryPageParam,CategoryPageItemResult
from app.schemas.common import ApiResult, IdParam
from app.services.admin.categories import CategoryAdminService

router = APIRouter(prefix="/categories", tags=["后端-分类管理接口"])

@router.post("/create")
async def create(param: CategoryCreateParam,
                 user: Annotated[User, Depends(deps.get_current_user)],
                 category_service: Annotated[CategoryAdminService, Depends(deps.get_category_admin_service)]):
    print(f"Received param: {param.name}")
    return ApiResult.success(await category_service.create(param, user))

@router.post("/update")
async def update(param: CategoryUpdateParam,
                 user: Annotated[User, Depends(deps.get_current_user)],
                 category_service: Annotated[CategoryAdminService, Depends(deps.get_category_admin_service)]):
    return ApiResult.success(await category_service.update(param, user))

@router.post("/delete")
async def delete(param: IdParam,
                 user: Annotated[User, Depends(deps.get_current_user)],
                 category_service: Annotated[CategoryAdminService, Depends(deps.get_category_admin_service)]):
    return ApiResult.success(await category_service.delete(param, user))

@router.post("/page_list")
async def page_list(param: CategoryPageParam,
                 user: Annotated[User, Depends(deps.get_current_user)],
                 category_service: Annotated[CategoryAdminService, Depends(deps.get_category_admin_service)]):
    return await category_service.page_list(param, user)
