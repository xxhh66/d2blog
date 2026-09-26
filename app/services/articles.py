import asyncio
from lib2to3.fixes.fix_print import parend_expr

from tortoise import Model

from app.cache.articles import ArticleCacheService
from app.core.caches import latest_articles_cache, article_lock_cache,cache_with_lock,article_cache
from typing import List
from app.core.enums import ArticleStatusEnum, BlogErrorEnum
from app.core.exceptions import BlogException
from app.models import Article
from app.schemas.common import BasePageParam, ApiPageResult
from app.schemas.articles import ArticlePageItemResult, ArticleDetailResult, ArticlePageParam

LATEST_ARTICLES_LOCK = asyncio.Lock()
ARTICLE_GLOBAL_LOCK = asyncio.Lock()

class ArticleService:
    def __init__(self,article_cache_service:ArticleCacheService):
        self.article_cache_service = article_cache_service

    # async def page_latest_articles(self, param: BasePageParam) -> ApiPageResult[List[ArticlePageItemResult]]:
    #     # 先从缓存中获取,但会存在如果页码不一样，会在多个地方进行缓存，导致重复缓存，如果数据进行更新， 没办法处理
    #     cache_key = f'latest:{param.page}:{param.page_size}'
    #     result = latest_articles_cache.get(cache_key)
    #
    #     if result:
    #         return result
    #
    #     async with LATEST_ARTICLES_LOCK:
    #         result = latest_articles_cache.get(cache_key)
    #         if result:
    #             return result
    #         # 缓存中没有, 从db中获取
    #         queryset = Article.filter(is_deleted=False, status=ArticleStatusEnum.PUBLISHED).prefetch_related('category', 'tags').order_by('-id')
    #         count = await queryset.count()
    #         articles = []
    #         if count > 0:
    #             articles = await queryset.offset((param.page - 1) * param.page_size).limit(param.page_size).all()
    #         result_list = [ArticlePageItemResult.model_validate(article) for article in articles]
    #
    #         # 将结果放入缓存
    #         result = ApiPageResult.success(param.page, param.page_size, count, result_list)
    #         latest_articles_cache.set(cache_key,result)
    #
    #     return result
    async def page_latest_articles(self, param: BasePageParam) -> ApiPageResult[List[ArticlePageItemResult]]:
        # 先从缓存中获取
        cache_key = f'latest:{param.page}:{param.page_size}'
        result = await self.article_cache_service.page_list(cache_key,param.page,param.page_size)

        if result:
            return result


        # 缓存中没有, 从db中获取
        queryset = (Article.filter(is_deleted=False, status=ArticleStatusEnum.PUBLISHED)
                    .prefetch_related('category', 'tags')
                    .order_by('-id'))
        count = await queryset.count()
        articles = []
        if count > 0:
            articles = await queryset.offset((param.page - 1) * param.page_size).limit(param.page_size).all()
        result_list = [ArticlePageItemResult.model_validate(article) for article in articles]

        ids = [article.id for article in articles]

        result = ApiPageResult.success(param.page, param.page_size, count, result_list)
        # 将结果放入缓存
        await self.article_cache_service.page_list_set(cache_key, count, ids)

        return result
    # async def get_by_id(self,article_id:int)->ArticleDetailResult:
    #     article_lock_key = f'article:{article_id}'
    #     article_lock = article_lock_cache.get(article_lock_key)
    #     if not article_lock:
    #         async with  ARTICLE_GLOBAL_LOCK:
    #             article_lock = article_lock_cache.get(article_lock_key)
    #             if not article_lock:
    #                 article_lock = asyncio.Lock()
    #                 article_lock_cache.set(article_lock_key,article_lock)
    #     async def _fetch_from_db():
    #         _article = await (Article.get_or_none(pk=article_id,is_deleted=False,status=ArticleStatusEnum.PUBLISHED)
    #                           .select_related("category", "user"))   # ← 关键：预加载外键
    #         if not _article:
    #             raise BlogException(BlogErrorEnum.ARTICLE_NOT_FOUND)
    #         return ArticleDetailResult.model_validate(_article)
    #     return await cache_with_lock(f"{article_id}",article_cache,article_lock,_fetch_from_db)

    async def get_by_id(self,article_id:int)->ArticleDetailResult:
        article = await (Article.get_or_none(pk=article_id,is_deleted=False,status=ArticleStatusEnum.PUBLISHED)
                         .prefetch_related('category', 'user'))
        if not article:
            raise BlogException(BlogErrorEnum.ARTICLE_NOT_FOUND)
        return ArticleDetailResult.model_validate(article)

    # async def page_list(self,param:ArticlePageParam)->ApiPageResult[List[ArticlePageItemResult]]:
    #     queryset = Article.filter(is_deleted=False, status=ArticleStatusEnum.PUBLISHED).prefetch_related('category',
    #                                                                                                      'tags').order_by(
    #         '-id')
    #     if param.category_id:
    #         queryset = queryset.filter(category__id=param.category_id)
    #     if param.tag_id:
    #         queryset = queryset.filter(tags__id=param.tag_id)
    #     if param.title:
    #         queryset = queryset.filter(title__contains=param.title)
    #     count = await queryset.count()
    #
    #     articles = []
    #     if count>0:
    #         articles = await queryset.offset((param.page - 1) * param.page_size).limit(param.page_size).all()
    #     result_list = [ArticlePageItemResult.model_validate(article) for article in articles]
    #     return ApiPageResult.success(param.page, param.page_size, count, result_list)


    async def page_list(self,param:ArticlePageParam)->ApiPageResult[List[ArticlePageItemResult]]:
        # 先从缓存中获取
        cache_key = f'page:{param.page}:{param.page_size}:{param.title}:{param.tag_id}:{param.category_id}'
        result = await self.article_cache_service.page_list(cache_key,param.page,param.page_size)

        if result:
            return result


        queryset = (Article.filter(is_deleted=False, status=ArticleStatusEnum.PUBLISHED)
                                                            .prefetch_related('category','tags')
                                                            .order_by('-id'))
        if param.category_id:
            queryset = queryset.filter(category__id=param.category_id)
        if param.tag_id:
            queryset = queryset.filter(tags__id=param.tag_id)
        if param.title:
            queryset = queryset.filter(title__contains=param.title)
        count = await queryset.count()

        articles = []
        if count>0:
            articles = await queryset.offset((param.page - 1) * param.page_size).limit(param.page_size).all()
        result_list = [ArticlePageItemResult.model_validate(article) for article in articles]

        ids = [article.id for article in articles]
        # 将结果放入缓存
        await self.article_cache_service.page_list_set(cache_key,count,ids)

        return ApiPageResult.success(param.page, param.page_size, count, result_list)
