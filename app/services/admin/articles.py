from itertools import count

from tortoise.transactions import in_transaction, atomic
from unicodedata import category

from app.core.enums import BlogErrorEnum
from app.core.exceptions import BlogException
from app.models import User,Article,Category,Tag
from app.schemas import tags, articles
from app.schemas.articles import ArticleCreateParam, ArticleUpdateParam,ArticlePageParam,ArticlePageItemResult
from app.schemas.common import IdParam, ApiPageResult


class ArticleAdminService:
    async def create(self,param:ArticleCreateParam,user:User)->bool:
        # 检测文章是否存在
        article = await Article.get_or_none(title=param.title, is_deleted=False,user=user)
        if article:
            raise BlogException(BlogErrorEnum.ARTICLE_EXIST)
        # 检测分类是否存在
        category = await Category.get_or_none(pk=param.category_id, is_deleted=False,user=user)
        if not category:
            raise BlogException(BlogErrorEnum.ARTICLE_NOT_FOUND)
        # 检测标签是否存在
        tags = []
        if param.tag_ids:
            tags = await Tag.filter(pk__in=param.tag_ids, is_deleted=False,user=user)
            if len(tags) != len(param.tag_ids):
                raise BlogException(BlogErrorEnum.TAG_NOT_FOUND)

        async with in_transaction():
            article = Article()
            article.title = param.title
            article.intro = param.intro
            article.content = param.content
            article.seo_title = param.seo_title
            article.seo_keywords = param.seo_keywords
            article.seo_description = param.seo_description
            article.category = category
            article.user = user
            await article.save()

            if tags:
                await article.tags.add(*tags)

            # 更新缓存
            # await self.article_cache_service.update_article_by_id(article.pk)

        return True

    async def update(self,param:ArticleUpdateParam,user:User)->bool  :
        article = await Article.get_or_none(pk=param.id,is_deleted=False,user=user)
        if not article:
            raise BlogException(BlogErrorEnum.ARTICLE_NOT_FOUND)
        # 检测分类是否存在
        category = await Category.get_or_none(pk=param.category_id,is_deleted=False,user=user)
        if not category:
            raise BlogException(BlogErrorEnum.CATEGORY_NOT_FOUND)
        tags = []
        if param.tag_ids:
            tags = await Tag.filter(pk__in=param.tag_ids,is_deleted=False,user=user)
            if len(tags) != len(param.tag_ids):
                raise BlogException(BlogErrorEnum.TAG_NOT_FOUND)

        @atomic()
        async def save_article():
            article.title = param.title
            article.intro = param.intro
            article.content = param.content
            article.seo_title = param.seo_title
            article.seo_keywords = param.seo_keywords
            article.seo_description = param.seo_description
            article.category = category
            article.user = user
            await article.save()
            await article.tags.clear()
            if tags:
                await article.tags.add(*tags)

            # 更新缓存
            # await self.article_cache_service.update_article_by_id(article.pk)
        await save_article()
        return True
    async def delete(self,param:IdParam,user:User):
        await Article.filter(pk=param.id,is_deleted=False,user=user).update(is_deleted=True)
        return True

    async def page_list(self,param:ArticlePageParam,user:User):
        queryset = Article.filter(is_deleted=False,user=user).order_by('-id')
        if param.title:
            queryset = queryset.filter(title__contains=param.title)
        if param.category_id:
            queryset = queryset.filter(category_id=param.category_id)
        if param.tag_ids:
            queryset = queryset.filter(tags__in=param.tag_ids)
        count = await queryset.count()
        articles=[]
        if  count > 0:
            articles = await queryset.offset( (param.page - 1) * param.page_size ).limit(param.page_size).all()
        result_list = [articles.ArticlePageItemResult.model_validate(article) for article in articles]

        return ApiPageResult.success(param.page, param.page_size, count, result_list)

