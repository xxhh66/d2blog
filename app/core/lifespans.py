import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger

from app.tasks import articles


@asynccontextmanager
async def lifespan(app: FastAPI):

    task = asyncio.create_task(articles.article_view_count_refresh_task())
    yield

    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass