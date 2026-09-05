from enum import Enum


class BlogErrorEnum(Enum):
    VALIDATE_ERROR = (400, "参数错误")
    ACCESS_TOKEN_INVALID = (401, "访问令牌无效")
    ACCESS_TOKEN_EXPIRE = (401, "访问令牌过期")
    SYSTEM_ERROR  = (500, "系统错误")

    #用户相关
    USER_NOT_FOUND_OR_PASSWORD_ERROR=(1001,"用户不存在或密码错误")
    USER_NOT_FOUND=(1002,"用户不存在")
    USER_EXISTS=(1003,"用户已存在")

    @property
    def err_code(self):
        return self.value[0]
    @property
    def err_msg(self):
        return self.value[1]
