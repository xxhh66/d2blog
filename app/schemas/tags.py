from pydantic import Field,BaseModel


class TagBaseParam(BaseModel):
    id:int= Field(...,description="分类ID")
    name:str=Field(...,description="分类名称",max_length=64)

class TagStatResult(TagBaseParam):
    published_article_count:int = Field(...,description="发布文章数量")