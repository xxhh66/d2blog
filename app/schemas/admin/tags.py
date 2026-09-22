from datetime import datetime

from pydantic import BaseModel, Field


class TagCreateParam(BaseModel):
    name: str = Field(..., description="标签名称", max_length=64)

class TagUpdateParam(BaseModel):
    id: int = Field(..., description="标签ID")
    name: str = Field(..., description="标签名称", max_length=64)

    class Config:
        from_attributes = True

class TagPageParam(BaseModel):
    page: int = Field(1, description="页码")
    page_size: int = Field(10, description="每页数量")
    name: str | None = Field(default=None, description="标签名称")

class TagPageItemResult(BaseModel):
    id: int
    name: str
    created_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.strftime("%Y-%m-%d %H:%M:%S")
        }