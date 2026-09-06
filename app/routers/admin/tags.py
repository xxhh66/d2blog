from typing import Annotated, List

from fastapi import APIRouter, Depends

from app.core import deps
from app.models import User
from app.schemas.tags import TagCreateParam, TagUpdateParam, TagPageParam, TagPageItemResult
from app.schemas.common import ApiResult, IdParam, ApiPageResult
from app.services.admin.tags import TagAdminService

router = APIRouter(prefix="/tags", tags=["后端-标签管理接口"])

@router.post("/create", response_model=ApiResult[TagPageItemResult])
async def create(param: TagCreateParam,
                 user: Annotated[User, Depends(deps.get_current_user)],
                 tag_service: Annotated[TagAdminService, Depends(deps.get_tag_admin_service)]) -> ApiResult[bool]:
    return ApiResult.success(await tag_service.create(param, user))


@router.post("/update", response_model=ApiResult[bool])
async def update(param: TagUpdateParam,
                 user: Annotated[User, Depends(deps.get_current_user)],
                 tag_service: Annotated[TagAdminService, Depends(deps.get_tag_admin_service)]):
    return ApiResult.success(await tag_service.update(param, user))


@router.post("/delete", response_model=ApiResult[bool])
async def delete(param: IdParam,
                 user: Annotated[User, Depends(deps.get_current_user)],
                 tag_service: Annotated[TagAdminService, Depends(deps.get_tag_admin_service)]):
    return ApiResult.success(await tag_service.delete(param, user))

@router.post("/page_list", response_model=ApiPageResult[List[TagPageItemResult]])
async def page_list(param: TagPageParam,
                    user: Annotated[User, Depends(deps.get_current_user)],
                    tag_service: Annotated[TagAdminService, Depends(deps.get_tag_admin_service)]):
    return await tag_service.page_list(param, user)
