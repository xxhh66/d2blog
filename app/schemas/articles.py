from datetime import datetime

from pydantic import BaseModel, Field

from app.core.enums import ArticleStatusEnum
from app.schemas.categories import CategoryUpdateParam
from app.schemas.tags import TagUpdateParam


class ArticleCreateParam(BaseModel):
    category_id:int =Field(...,description="分类ID")
    tag_ids:list[int] |None = Field(default=[],description="标签ID列表")

    title:str = Field(...,description="文章标题",max_length=128)
    intro:str = Field(...,description="文章摘要",max_length=256)
    content:str = Field(...,description="文章内容",max_length=10000)

    seo_title:str|None = Field(default=None,description="文章SEO标题",max_length=256)
    seo_keywords:str|None = Field(default=None,description="文章SEO关键词",max_length=256)
    seo_description:str|None = Field(default=None,description="文章SEO描述",max_length=512)

class ArticleUpdateParam(ArticleCreateParam):
    id:int = Field(...,description="文章ID")

class ArticlePageParam(BaseModel):
    page:int = Field(1,description="页码")
    page_size:int = Field(10,description="每页页数")

    title:str|None = Field(default=None,description="文章标题")
    category_id:int|None= Field(default=None,description="分类ID")
    tag_ids:int|None = Field(default=None,description="标签ID列表")

class ArticlePageItemResult(BaseModel):
    id: int = Field(..., description="文章ID")
    title: str = Field(..., description="文章标题", max_length=128)
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    category: CategoryUpdateParam = Field(..., description="分类")
    tags: list[TagUpdateParam] | None = Field(default=[], description="标签列表")
    status: ArticleStatusEnum = Field(..., description="文章状态")

    class Config:
        from_attributes = True
