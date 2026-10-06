from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.club import Club


async def get_by_id(db: AsyncSession, club_id: int) -> Club | None:
    return await db.get(Club, club_id)


async def get_by_name(db: AsyncSession, name: str) -> Club | None:
    result = await db.execute(select(Club).where(Club.name == name))
    return result.scalar_one_or_none()


async def get_all(db: AsyncSession) -> list[Club]:
    result = await db.execute(select(Club).order_by(Club.id))
    return list(result.scalars().all())


async def create(db: AsyncSession, club: Club) -> Club:
    db.add(club)
    # flush, ne commit: transakciju potvrđuje get_db kad cijeli zahtjev prođe
    await db.flush()
    return club
