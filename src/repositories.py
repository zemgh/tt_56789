from typing import Optional

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Query
from src.schemas import QueryDict
from src.utils import errors_handler


class QueryRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    @errors_handler
    async def create(self, address: str) -> None:
        model = Query(address=address)
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)

    @errors_handler
    async def get_queries(self, cursor: Optional[int], limit: int) -> QueryDict:
        if cursor:
            stmt = select(Query).where(Query.id < cursor).order_by(desc(Query.id)).limit(limit)
        else:
            stmt = select(Query).order_by(desc(Query.id)).limit(limit)

        results = (await self._session.execute(stmt)).scalars().all()

        last_id = results[-1].id if results and results[-1].id != 1 else None
        addresses = [a.address for a in results]

        return QueryDict(
            cursor=last_id,
            queries=addresses,
        )
