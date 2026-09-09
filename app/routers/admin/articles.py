
from typing import Annotated, List

from fastapi import APIRouter, Depends
from fastapi.params import Path

from app.core import deps
from app.models import User
from app.schemas.articles import ArticleCreateParam, ArticleUpdateParam
# ArticleUpdateParam, ArticlePageParam, ArticlePageItemResult, ArticleUpdateStatusParam, ArticleDetailResult)

from app.schemas.common import ApiResult, IdParam, ApiPageResult
from app.services.admin.articles import ArticleAdminService

router = APIRouter(prefix="/articles", tags=["后端-文章管理接口"])


@router.post("/create", response_model=ApiResult[bool])
async def create(param: ArticleCreateParam,
                 user: Annotated[User, Depends(deps.get_current_user)],
                 article_service: Annotated[ArticleAdminService, Depends(deps.get_article_admin_service)]):
    return ApiResult.success(await article_service.create(param, user))

@router.post("/update", response_model=ApiResult[bool])
async def create(param: ArticleUpdateParam,
                 user: Annotated[User, Depends(deps.get_current_user)],
                 article_service: Annotated[ArticleAdminService, Depends(deps.get_article_admin_service)]):
    return ApiResult.success(await article_service.update(param, user))

@router.post("/delete", response_model=ApiResult[bool])
async def create(param: IdParam,
                 user: Annotated[User, Depends(deps.get_current_user)],
                 article_service: Annotated[ArticleAdminService, Depends(deps.get_article_admin_service)]):
    return ApiResult.success(await article_service.delete(param, user))