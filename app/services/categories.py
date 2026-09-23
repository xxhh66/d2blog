import asyncio

from tortoise.expressions import Q
from tortoise.functions import Count

from app.core.caches import stat_cache
from app.core.enums import ArticleStatusEnum
from app.models import Category
from app.schemas.categories import CategoryStatResult

CATEGORY_STAT_LOCK = asyncio.Lock()


class CategoryService:

    async def stat_categories(self) -> list[CategoryStatResult]:
        # 从db中获取
        categories = await (Category.filter(is_deleted=False).order_by('-id')
                            .annotate(published_article_count=
                                      Count("articles",
                                            _filter=Q(articles__status=ArticleStatusEnum.PUBLISHED,
                                                      articles__is_deleted=False)))
                            .filter(published_article_count__gt=0)
                            .values("id", "name", "published_article_count"))
        result_list =  [CategoryStatResult.model_validate(category) for category in categories]
        return result_list

        # # 先从缓存中获取
        # cache_key = "category_stat"
        # result = stat_cache.get(cache_key)
        # if result:
        #     return result

        # async def CATEGORY_STAT_LOCK():
        #     result = stat_cache.get(cache_key)
        #     if result:
        #         return result
        #     # 从db中获取
        #     categories = await (Category.filter(is_deleted=False).order_by('-id')
        #                         .annotate(published_article_count=
        #                                   Count("articles",
        #                                         _filter=Q(articles__status=ArticleStatusEnum.PUBLISHED,
        #                                                   articles__is_deleted=False)))
        #                         .filter(published_article_count__gt=0)
        #                         .values("id", "name", "published_article_count"))
        #     return [CategoryStatResult.model_validate(category) for category in categories]
        # # 放入缓存
        # stat_cache.set(cache_key,result)
        # return result