from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse

from app.core.enums import BlogErrorEnum
from app.schemas.common import ApiResult


class BlogException(Exception):
    def __init__(self, err: str | BlogErrorEnum, code: int=500):
        if isinstance(err, BlogErrorEnum):
            self.msg = err.err_msg
            self.code = err.err_code
        else:
            self.msg = err
            self.code = code

        super().__init__(self.msg)
async def blog_exception_handler(request, exc: BlogException):
    return JSONResponse(
        status_code=200,
        content=ApiResult(code=exc.code, msg=exc.msg).model_dump(),
    )
async def validation_exception_handler(request,exc:RequestValidationError):
    return JSONResponse(
        status_code=200,
        content=ApiResult(
            code=BlogErrorEnum.VALIDATE_ERROR.err_code,
            msg=exc.errors()[0].get('msg')
        ).model_dump(),
    )

async def global_exception_handler(request, exc: Exception):
    return JSONResponse(
        status_code=200,
        content=ApiResult(
            code=BlogErrorEnum.SYSTEM_ERROR.err_code,
            msg=BlogErrorEnum.SYSTEM_ERROR.err_msg
        ).model_dump(),
    )

