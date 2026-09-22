from typing import Annotated,List
from fastapi import APIRouter, Depends, Query
from app.schemas.articles import ArticlePageItemResult
from app.schemas.common import BasePageParam,ApiPageResult
from app.services.articles import ArticleService
from app.core import deps


router = APIRouter(prefix="/articles", tags=['文章相关接口'])
@router.get("/latest", response_model=ApiPageResult[List[ArticlePageItemResult]])
async def page_latest_articles(param: Annotated[BasePageParam, Query()],
                               article_service: Annotated[ArticleService, Depends(deps.get_article_service)]):
    """
    分页查询文章
    """

    return await article_service.page_latest_articles(param)