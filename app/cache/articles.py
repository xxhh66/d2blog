from pydantic import BaseModel

from app.core.caches import load_cache, article_cache
from app.core.enums import ArticleStatusEnum
from app.models import Article
from app.schemas.articles import ArticlePydantic


# 涉及业务的放在cache/articles下面
class ArticleCacheService:
    async def get_article_by_id(self,article_id:int):
        article_cache_key = f"article_{article_id}"
        async def _fetch_from_db():
            _article = await (Article.get_or_none(pk=article_id,is_deleted=False,status=ArticleStatusEnum.PUBLISHED)
                              .prefetch_related("category", "user"))
            if not _article:
                return None
            return ArticlePydantic.model_validate(_article).model_dump()

        return await load_cache(article_cache_key,article_cache,_fetch_from_db)