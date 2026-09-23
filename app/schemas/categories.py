from pydantic import BaseModel, Field


class CategoryBaseParam(BaseModel):
    id: int = Field(..., description="分类ID")
    name: str = Field(..., description="分类名称", max_length=64)

class CategoryStatResult(CategoryBaseParam):
    published_article_count: int = Field(..., description="发布文章数量")