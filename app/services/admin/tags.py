from app.core.enums import BlogErrorEnum
from app.core.exceptions import BlogException
from app.models import User, Tag
from app.schemas.tags import TagCreateParam, TagUpdateParam, TagPageParam, TagPageItemResult
from app.schemas.common import IdParam, ApiPageResult


class TagAdminService:

    async def create(self, param: TagCreateParam, user: User) -> TagPageItemResult:
        tag = await Tag.get_or_none(name=param.name, is_deleted=False, user=user)
        if tag:
            raise BlogException(BlogErrorEnum.TAG_EXIST)
        tag = await Tag.create(name=param.name, user=user)
        return TagPageItemResult.model_validate(tag)


    async def update(self, param: TagUpdateParam, user: User) -> bool:
        tag = await Tag.get_or_none(pk=param.id, is_deleted=False, user=user)
        if not tag:
            raise BlogException(BlogErrorEnum.TAG_NOT_FOUND)
        tag.name = param.name
        await tag.save()
        return True

    async def delete(self, param: IdParam, user: User):
        # 软删除
        await Tag.filter(pk=param.id, is_deleted=False, user=user).update(is_deleted=True)
        return True

    async def page_list(self, param: TagPageParam, user: User):
        queryset = Tag.filter(is_deleted=False, user=user).order_by('-id')
        if param.name:
            queryset = queryset.filter(name__icontains=param.name)

        count = await queryset.count()
        tags = []
        if count > 0:
            tags = await queryset.offset( (param.page - 1) * param.page_size ).limit(param.page_size).all()
        result_list = [TagPageItemResult.model_validate(tag) for tag in tags]

        return ApiPageResult.success(param.page, param.page_size, count, result_list)