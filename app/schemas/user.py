from pydantic import BaseModel, EmailStr, Field


class RegisterParam(BaseModel):
    email: EmailStr=Field(...,description="邮箱",max_length=128)
    password:str = Field(...,description="密码",max_length=20,min_length=6)
    code:str = Field(...,description="验证码",max_length=6,min_length=6)