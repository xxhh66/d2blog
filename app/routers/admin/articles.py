
from typing import Annotated, List

from fastapi import APIRouter, Depends
from fastapi.params import Path

from app.core import deps
from app.models import User
from app.schemas.articles import ArticleCreateParam
    # ArticleUpdateParam, ArticlePageParam, ArticlePageItemResult, ArticleUpdateStatusParam, ArticleDetailResult)

from app.schemas.common import ApiResult, IdParam, ApiPageResult
from app.services.admin.articles import ArticleAdminService

router = APIRouter(prefix="/articles", tags=["后端-文章管理接口"])


@router.post("/create", response_model=ApiResult[bool])
async def create(param: ArticleCreateParam,
                 user: Annotated[User, Depends(deps.get_current_user)],
                 article_service: Annotated[ArticleAdminService, Depends(deps.get_article_admin_service)]):
    return ApiResult.success(await article_service.create(param, user))