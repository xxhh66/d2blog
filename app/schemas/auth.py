from pydantic import BaseModel, EmailStr, Field


class RegisterParam(BaseModel):
    email: EmailStr=Field(...,description="邮箱",max_length=128)
    password:str = Field(...,description="密码",max_length=20,min_length=6)
    code:str = Field(...,description="验证码",max_length=6,min_length=6)
#  登录请求参数验证
class LoginParam(BaseModel):
    email:EmailStr = Field(...,description="邮箱",max_length=128)
    password:str = Field(...,description="密码",max_length=20,min_length=6)
# 登录响应数据格式
class LoginResult(BaseModel):
    access_token:str = Field(...,description="访问令牌")
    expires_in:int = Field(...,description="令牌有效期")
    refresh_token:str = Field(...,description="刷新令牌")

# Token 刷新请求验证
class RefreshTokenParam(BaseModel):
    token:str = Field(...,description="刷新令牌")