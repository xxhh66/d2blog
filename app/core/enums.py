from enum import Enum, IntEnum


class BlogErrorEnum(Enum):
    VALIDATE_ERROR = (400, "参数错误")
    ACCESS_TOKEN_INVALID = (401, "无效的access_token")
    ACCESS_TOKEN_EXPIRED = (402, "access_token已过期")
    SYSTEM_ERROR = (500, "系统错误")

    INVALID_TOKEN = (600, "无效的token")
    VERIFY_CODE_EXPIRED = (601, "验证码已过期")
    VERIFY_CODE_EXPIRED_OR_INVALID = (602, "验证码已过期或者不正确")

    # 1000 用户相关
    USER_NOT_FOUND_OR_PASSWORD_ERROR = (1001, "用户不存在或者密码错误")
    USER_NOT_FOUND = (1002, "用户不存在")
    USER_EXISTS = (1003, "用户已存在")

    # 2000 博客相关
    CATEGORY_EXIST = (2001, "分类已存在")
    CATEGORY_NOT_FOUND = (2002, "分类不存在")
    TAG_EXIST = (2003, "标签已存在")
    TAG_NOT_FOUND = (2004, "标签不存在")
    ARTICLE_EXIST = (2005, "文章已存在")
    ARTICLE_NOT_FOUND = (2006, "文章不存在")


    @property
    def err_code(self):
        return self.value[0]

    @property
    def err_msg(self):
        return self.value[1]

class ArticleStatusEnum(IntEnum):
    UB_PUBLISHED = 0
    PUBLISHED = 1