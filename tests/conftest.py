import pytest_asyncio

from typing import AsyncIterator
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock

from fakeredis import FakeAsyncRedis
from fastapi import FastAPI
from fastapi_limiter import FastAPILimiter
from httpx import ASGITransport, AsyncClient
from asgi_lifespan import LifespanManager

from src.db import get_session
from src.routes import router


@pytest_asyncio.fixture()
async def db_session() -> AsyncMock:
    session = AsyncMock()

    session.add.return_value = None
    session.commit.return_value = None
    session.refresh.return_value = None

    yield session


@pytest_asyncio.fixture()
async def app(db_session) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        await FastAPILimiter.init(FakeAsyncRedis())
        yield


    app = FastAPI(lifespan=lifespan)
    app.include_router(router)
    app.dependency_overrides[get_session] = lambda: db_session

    async with LifespanManager(app) as manager:
        yield manager.app


@pytest_asyncio.fixture()
async def client(app: FastAPI) -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://testserver') as client:
        yield client
