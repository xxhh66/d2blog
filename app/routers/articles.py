from typing import Annotated,List
from fastapi import APIRouter, Depends, Query,Path
from app.schemas.articles import ArticlePageItemResult, ArticleDetailResult, ArticlePageParam
from app.schemas.common import BasePageParam,ApiResult,ApiPageResult
from app.services.articles import ArticleService
from app.core import deps
from loguru import logger


router = APIRouter(prefix="/articles", tags=['文章相关接口'])
@router.get("/latest", response_model=ApiPageResult[List[ArticlePageItemResult]])
async def page_latest_articles(param: Annotated[BasePageParam, Query()],
                               article_service: Annotated[ArticleService, Depends(deps.get_article_service)]):
    """
    分页查询文章
    """
    logger.info(f"test loguru logger")
    return await article_service.page_latest_articles(param)

# 查找、筛选
@router.get("/page_list")
async def page_list(param:Annotated[ArticlePageParam,Query()],
                    article_service: Annotated[ArticleService, Depends(deps.get_article_service)]):
    return await article_service.page_list(param)
# 获取文章详细内容
@router.get("/{article_id}", response_model=ApiResult[ArticleDetailResult])
async def get_by_id(article_id: Annotated[int, Path()],
                    article_service: Annotated[ArticleService, Depends(deps.get_article_service)]):
    return ApiResult.success(await article_service.get_by_id(article_id))