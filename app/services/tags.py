import asyncio

from tortoise.expressions import Q
from tortoise.functions import Count

from app.core.caches import stat_cache,cache_with_lock
from app.core.enums import ArticleStatusEnum
from app.models import Tag
from app.schemas.tags import TagStatResult


TAG_STAT_LOCK = asyncio.Lock()

class TagService:
    # V1
    async def stat_tags(self) -> list[TagStatResult]:
        # 先从缓存中获取
        cache_key = "tag_stat"

        async def _fetch_from_db():
            # 从db中获取
            queryset = Tag.filter(is_deleted=False)
            queryset = queryset.annotate(published_article_count=
                                         Count("articles",
                                               _filter=Q(articles__status=ArticleStatusEnum.PUBLISHED,
                                                         articles__is_deleted=False)))
            # 并进行排序
            queryset = queryset.filter(published_article_count__gt=0).order_by("-published_article_count")
            tags = await queryset.values("id", "name", "published_article_count")

            result =  [TagStatResult.model_validate(tag) for tag in tags]
            return result
        return await cache_with_lock(cache_key, stat_cache, TAG_STAT_LOCK, _fetch_from_db)


    # V1
    # async def stat_tags(self) -> list[TagStatResult]:
    #     # 先从缓存中获取
    #     cache_key = "tag_stat"
    #     result = stat_cache.get(cache_key)
    #     if result:
    #         return result
    #
    #     async with TAG_STAT_LOCK:
    #         result = stat_cache.get(cache_key)
    #         if result:
    #             return result
    #
    #         # 从db中获取
    #         queryset = Tag.filter(is_deleted=False)
    #         queryset = queryset.annotate(published_article_count=
    #                                      Count("articles",
    #                                            _filter=Q(articles__status=ArticleStatusEnum.PUBLISHED,
    #                                                      articles__is_deleted=False)))
    #         # 并进行排序
    #         queryset = queryset.filter(published_article_count__gt=0).order_by("-published_article_count")
    #         tags = await queryset.values("id", "name", "published_article_count")
    #
    #         result =  [TagStatResult.model_validate(tag) for tag in tags]
    #
    #         # 将结果存入缓存
    #         stat_cache.set(cache_key, result)
    #         return result
    #     # return await load_cache_with_lock(cache_key, stat_cache, TAG_STAT_LOCK, _fetch_from_db)