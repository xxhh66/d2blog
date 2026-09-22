import asyncio
from lib2to3.fixes.fix_print import parend_expr

from tortoise import Model
from app.core.caches import latest_articles_cache
from typing import List
from app.core.enums import ArticleStatusEnum
from app.models import Article
from app.schemas.common import BasePageParam, ApiPageResult
from app.schemas.articles import ArticlePageItemResult

LATEST_ARTICLES_LOCK = asyncio.Lock()

class ArticleService:
    async def page_latest_articles(self, param: BasePageParam) -> ApiPageResult[List[ArticlePageItemResult]]:
        # 先从缓存中获取
        cache_key = f'latest:{param.page}:{param.page_size}'
        result = latest_articles_cache.get(cache_key)

        if result:
            return result

        async with LATEST_ARTICLES_LOCK:
            result = latest_articles_cache.get(cache_key)
            if result:
                return result
            # 缓存中没有, 从db中获取
            queryset = Article.filter(is_deleted=False, status=ArticleStatusEnum.PUBLISHED).prefetch_related('category', 'tags').order_by('-id')
            count = await queryset.count()
            articles = []
            if count > 0:
                articles = await queryset.offset((param.page - 1) * param.page_size).limit(param.page_size).all()
            result_list = [ArticlePageItemResult.model_validate(article) for article in articles]

            # 将结果放入缓存
            result = ApiPageResult.success(param.page, param.page_size, count, result_list)
            latest_articles_cache.set(cache_key,result)

        return result