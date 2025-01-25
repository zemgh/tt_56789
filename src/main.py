from contextlib import asynccontextmanager

import redis.asyncio as redis

from fastapi import FastAPI
from fastapi_limiter import FastAPILimiter

from src.db import init_db
from src.routes import router


@asynccontextmanager
async def lifespan(app):
    await init_db()

    redis_connection = redis.from_url('redis://redis', encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(redis_connection)

    yield


app = FastAPI(lifespan=lifespan)

app.include_router(router)
