import asyncio
from lib2to3.fixes.fix_print import parend_expr

from tortoise import Model
from app.core.caches import latest_articles_cache, article_lock_cache,cache_with_lock,article_cache
from typing import List
from app.core.enums import ArticleStatusEnum, BlogErrorEnum
from app.core.exceptions import BlogException
from app.models import Article
from app.schemas.common import BasePageParam, ApiPageResult
from app.schemas.articles import ArticlePageItemResult,ArticleDetailResult
LATEST_ARTICLES_LOCK = asyncio.Lock()
ARTICLE_GLOBAL_LOCK = asyncio.Lock()

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

    async def get_by_id(self,article_id:int)->ArticleDetailResult:
        article_lock_key = f'article:{article_id}'
        article_lock = article_lock_cache.get(article_lock_key)
        if not article_lock:
            async with  ARTICLE_GLOBAL_LOCK:
                article_lock = article_lock_cache.get(article_lock_key)
                if not article_lock:
                    article_lock = asyncio.Lock()
                    article_lock_cache.set(article_lock_key,article_lock)
        async def _fetch_from_db():
            _article = await (Article.get_or_none(pk=article_id,is_deleted=False,status=ArticleStatusEnum.PUBLISHED)
                              .select_related("category", "user"))   # ← 关键：预加载外键
            if not _article:
                raise BlogException(BlogErrorEnum.ARTICLE_NOT_FOUND)
            return ArticleDetailResult.model_validate(_article)
        return await cache_with_lock(f"{article_id}",article_cache,article_lock,_fetch_from_db)