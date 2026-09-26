from pydantic import BaseModel
from typing import List
from app.core.caches import load_cache, article_cache, article_page_cache
from app.core.enums import ArticleStatusEnum
from app.models import Article
from app.schemas.articles import ArticlePageItemResult
from app.schemas.articles import ArticlePydantic
from app.schemas.common import ApiPageResult


# 涉及业务的放在cache/articles下面
class ArticleCacheService:
    async def get_article_by_id(self,article_id:int):
        article_cache_key = f"article_{article_id}"
        async def _fetch_from_db():
            _article = await (Article.get_or_none(pk=article_id,is_deleted=False,status=ArticleStatusEnum.PUBLISHED)
                              .prefetch_related('category', 'tags'))
            if not _article:
                return None
            return ArticlePydantic.model_validate(_article).model_dump()

        return await load_cache(article_cache_key,article_cache,_fetch_from_db)

    async def update_article_by_id(self, article_id: int):
        article_cache_key = f'article_{article_id}'
        article = await Article.get_or_none(pk=article_id, is_deleted=False).prefetch_related('category', 'tags')
        if not article:
            return
        article_cache.set(article_cache_key, ArticlePydantic.model_validate(article).model_dump())

    async def delete_article_by_id(self, article_id: int):
        article_cache_key = f'article_{article_id}'
        article_cache.delete(article_cache_key)

    async def page_list(self,cache_key:str,page:int,page_size:int)->ApiPageResult[List[ArticlePageItemResult]]:
        result = article_page_cache.get(cache_key)
        if  result is None:
            return None
        count = result.get('count')
        result_list = []

        if count>0:
            ids = result.get('ids')
            for article_id in ids:
                article = await self.get_article_by_id(article_id)
                if article and article.get('status') == ArticleStatusEnum.PUBLISHED:
                    result_list.append(ArticlePageItemResult.model_validate(article))
        return ApiPageResult.success(page,page_size,count,result_list)

    async def page_list_set(self, cache_key, count:int,ids:List[int]):
        article_page_cache.set(cache_key, {
            'count': count,
            'ids': ids
        })
