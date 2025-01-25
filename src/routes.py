import asyncio
import os

from fastapi import APIRouter, status, Depends
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_session
from src.repositories import QueryRepository
from src.schemas import WalletSchema, QueryDict, WalletDataDict
from src.tron import TronService


router = APIRouter(prefix='/api/v1/tron')

QPS_LIMIT = int(os.getenv('QPS_LIMIT', 15)) // 2 - 1


@router.post(
    '/wallet',
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RateLimiter(times=QPS_LIMIT, seconds=1))])
async def get_wallet(
        data: WalletSchema,
        session: AsyncSession = Depends(get_session)
) -> WalletDataDict:

    repo = QueryRepository(session)
    asyncio.create_task(repo.create(data.address))

    tron = TronService()
    wallet_data = await tron.fetch_tron_wallet(data.address)

    return wallet_data


@router.get('/queries', status_code=status.HTTP_200_OK)
async def get_queries(
        cursor: int = None,
        limit: int = 10,
        session: AsyncSession = Depends(get_session)
) -> QueryDict:

    repo = QueryRepository(session)
    return await repo.get_queries(cursor, limit)
