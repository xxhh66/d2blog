from datetime import datetime
from pydantic import BaseModel,Field


class CategoryParam(BaseModel):
    id:int= Field(...,description="分类ID")
    name:str=Field(...,description="分类名称",max_length=64)
    class Config:
        from_attributes = True

class TagParam(BaseModel):
    id: int = Field(..., description="标签ID")
    name: str = Field(..., description="标签名称", max_length=64)

    class Config:
        from_attributes = True

class ArticlePageItemResult(BaseModel):
    id: int = Field(..., description="文章ID")
    title: str = Field(..., description="文章标题", max_length=128)
    intro: str = Field(..., description="文章简介", max_length=256)
    view_count: int = Field(..., description="文章浏览次数")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    category: CategoryParam = Field(..., description="分类")
    tags: list[TagParam] | None = Field(default=[], description="标签列表")

    class Config:
        from_attributes = True