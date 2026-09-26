import asyncio

from loguru import logger
from tortoise.expressions import F

from app.core.caches import article_view_count_cache
from app.models import Article


async def article_view_count_refresh_task():
    while True:
        await asyncio.sleep(30)
        logger.info("刷新文章浏览量缓存")
        try:

            for article_id in list(article_view_count_cache.cache.keys()):
                view_count = article_view_count_cache.get(article_id)
                if view_count and view_count > 0:
                    logger.info(f"刷新文章浏览量缓存, article_id: {article_id}, view_count: {view_count}")
                    await Article.filter(pk=article_id, is_deleted=False).update(view_count=F('view_count') + view_count)
                    # 清除缓存
                    article_view_count_cache.delete(article_id)
        except Exception as e:
            logger.exception(e)