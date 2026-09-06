from datetime import datetime

from pydantic import BaseModel,Field


class CategoryCreateParam(BaseModel):
    name: str = Field(..., description="分类名称", max_length=64)

class CategoryUpdateParam(BaseModel):
    id:int= Field(...,description="分类ID")
    name:str=Field(...,description="分类名称",max_length=64)

class CategoryPageParam(BaseModel):
    page:int=Field(1,description="页码")
    page_size:int=Field(10,description="每页数量")
    name:str|None=Field(default=None,description="分类名称")


class CategoryPageItemResult(BaseModel):
    id: int
    name: str
    created_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.strftime("%Y-%m-%d %H:%M:%S")
        }