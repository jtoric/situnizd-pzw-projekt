from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.lifter import Lifter
from app.models.registration import Registration


async def get_by_id(db: AsyncSession, registration_id: int) -> Registration | None:
    # Natjecatelj se dohvaća unaprijed: u asinkronom radu lijeno učitavanje
    # registration.lifter podiže iznimku tek pri popunjavanju odgovora
    stmt = (
        select(Registration)
        .options(selectinload(Registration.lifter))
        .where(Registration.id == registration_id)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def list_for_competition(
    db: AsyncSession,
    competition_id: int,
    club_id: int | None,
    status: str | None,
    limit: int,
    offset: int,
) -> list[Registration]:
    # selectinload: dva upita ukupno, jedan za prijave i jedan za sve njihove
    # natjecatelje. Bez njega slijedi po jedan upit za svaku prijavu: problem N+1
    stmt = (
        select(Registration)
        .options(selectinload(Registration.lifter))
        .where(Registration.competition_id == competition_id)
    )
    if club_id is not None:
        # Sužavanje u upitu: tuđe prijave ni ne izlaze iz baze
        stmt = stmt.join(Registration.lifter).where(Lifter.club_id == club_id)
    if status is not None:
        stmt = stmt.where(Registration.status == status)
    stmt = stmt.order_by(Registration.id).limit(limit).offset(offset)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def create(db: AsyncSession, registration: Registration) -> Registration:
    db.add(registration)
    await db.flush()
    return registration
