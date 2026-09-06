from tortoise import Model
from unicodedata import category

from app.core.enums import BlogErrorEnum
from app.core.exceptions import BlogException
from app.schemas.common import IdParam,ApiPageResult
from app.schemas.categories import CategoryCreateParam,CategoryUpdateParam,CategoryPageParam,CategoryPageItemResult
from app.models import User,Category


class CategoryAdminService:
    async def create(self, param: CategoryCreateParam, user: User) -> bool:
        category = await Category.get_or_none(name=param.name, is_deleted=False, user=user)
        if category:
            raise BlogException(BlogErrorEnum.CATEGORY_EXIST)
        await Category.create(name=param.name, user=user)
        return True
    
    async def update(self,param:CategoryUpdateParam,user:User)->bool:
        category = await Category.get_or_none(pk=param.id, is_deleted=False, user=user)
        if not category:
            raise BlogException(BlogErrorEnum.CATEGORY_NOT_FOUND)
        category.name = param.name
        await category.save()
        return True


    async def delete(self,param:IdParam,user:User)->bool:
        await Category.filter(pk=param.id, is_deleted=False, user=user).update(is_deleted=True)
        return True

    async def page_list(self,param:CategoryPageParam,user:User):
        queryset=Category.filter(is_deleted=False,user=user).order_by('-id')
        if param.name:
            queryset =queryset.filter(name__icontains=param.name)
        count = await queryset.count()
        categories = []
        if count>0:
            categories = await queryset.offset((param.page-1)*param.page_size).limit(param.page_size).all()

        result_list = [CategoryPageItemResult.model_validate(category) for category in categories]

        return ApiPageResult.success(param.page, param.page_size, count, result_list)