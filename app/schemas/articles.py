from pydantic import BaseModel, Field


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
