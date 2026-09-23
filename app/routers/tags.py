from typing import Annotated, List

from fastapi import APIRouter, Depends

from app.core import deps
from app.schemas.common import ApiResult
from app.schemas.tags import TagStatResult
from app.services.tags import TagService

router = APIRouter(prefix="/tags", tags=["标签接口"])


@router.get("/stat", response_model=ApiResult[List[TagStatResult]], description="统计标签")
async def stat_tags(tag_service: Annotated[TagService, Depends(deps.get_tag_service)]):
    return ApiResult.success(await tag_service.stat_tags())