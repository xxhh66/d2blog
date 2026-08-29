"""通用响应模型。

所有 API 接口都建议返回统一的结构，便于前端统一解析状态码、提示语和数据字段。
"""

from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ApiResult(BaseModel, Generic[T]):
    """统一 API 返回结构。

    code 表示业务状态码，msg 是用户提示信息，data 中放置实际返回数据。
    """

    code: int = 200
    msg: str = "success"
    data: T | None = None

    @staticmethod
    def success(data: T | None = None):
        """返回成功响应。"""
        return ApiResult(data=data)

    @staticmethod
    def fail(message: str, code: int = 500):
        """返回失败响应。"""
        return ApiResult(code=code, msg=message, data=None)
