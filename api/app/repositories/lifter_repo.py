from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.lifter import Lifter
from app.models.registration import Registration


async def get_by_id(db: AsyncSession, lifter_id: int) -> Lifter | None:
    return await db.get(Lifter, lifter_id)


async def get_by_club(
    db: AsyncSession,
    club_id: int,
    gender: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> list[Lifter]:
    # Upit se gradi postupno: klub uvijek, spol samo ako je filtar poslan
    stmt = select(Lifter).where(Lifter.club_id == club_id)
    if gender is not None:
        stmt = stmt.where(Lifter.gender == gender)
    # Bez order_by straničenje nije pouzdano: baza sama ne jamči poredak
    stmt = stmt.order_by(Lifter.id).limit(limit).offset(offset)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def create(db: AsyncSession, lifter: Lifter) -> Lifter:
    db.add(lifter)
    await db.flush()
    return lifter


async def delete(db: AsyncSession, lifter: Lifter) -> None:
    await db.delete(lifter)
    await db.flush()


async def has_registrations(db: AsyncSession, lifter_id: int) -> bool:
    stmt = select(exists().where(Registration.lifter_id == lifter_id))
    return bool(await db.scalar(stmt))
