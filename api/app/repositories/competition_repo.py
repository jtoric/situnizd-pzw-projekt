from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.competition import Competition


async def get_by_id(db: AsyncSession, competition_id: int) -> Competition | None:
    return await db.get(Competition, competition_id)


async def get_all(db: AsyncSession, limit: int, offset: int) -> list[Competition]:
    stmt = (
        select(Competition)
        .order_by(Competition.date, Competition.id)
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def create(db: AsyncSession, competition: Competition) -> Competition:
    db.add(competition)
    await db.flush()
    return competition
