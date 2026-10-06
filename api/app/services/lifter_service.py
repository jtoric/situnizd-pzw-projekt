from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.models.lifter import Lifter
from app.models.user import User
from app.repositories import lifter_repo
from app.schemas.lifter import LifterCreate, LifterUpdate
from app.services import club_service


async def list_lifters(
    db: AsyncSession,
    club_id: int,
    current_user: User,
    gender: str | None,
    limit: int,
    offset: int,
) -> list[Lifter]:
    # Klub iz adrese mora postojati, inače 404, i pripadati korisniku, inače 403
    await club_service.get_club(db, club_id, current_user)
    return await lifter_repo.get_by_club(db, club_id, gender, limit, offset)


async def get_lifter(
    db: AsyncSession, club_id: int, lifter_id: int, current_user: User
) -> Lifter:
    await club_service.get_club(db, club_id, current_user)
    lifter = await lifter_repo.get_by_id(db, lifter_id)
    # Natjecatelj drugog kluba pod ovom adresom ne postoji
    if not lifter or lifter.club_id != club_id:
        raise AppError("not_found", "Natjecatelj nije pronađen", 404)
    return lifter


async def create_lifter(
    db: AsyncSession, club_id: int, body: LifterCreate, current_user: User
) -> Lifter:
    await club_service.get_club(db, club_id, current_user)
    lifter = Lifter(club_id=club_id, **body.model_dump())
    return await lifter_repo.create(db, lifter)


async def update_lifter(
    db: AsyncSession,
    club_id: int,
    lifter_id: int,
    body: LifterUpdate,
    current_user: User,
) -> Lifter:
    lifter = await get_lifter(db, club_id, lifter_id, current_user)
    # Samo poslana polja: izostalo polje ostaje kakvo je bilo
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(lifter, field, value)
    await db.flush()
    return lifter


async def delete_lifter(
    db: AsyncSession, club_id: int, lifter_id: int, current_user: User
) -> None:
    lifter = await get_lifter(db, club_id, lifter_id, current_user)
    # Natjecatelj s prijavama se ne briše: povijest prijava mora ostati
    if await lifter_repo.has_registrations(db, lifter.id):
        raise AppError(
            "has_registrations", "Natjecatelj ima prijave i ne može se obrisati", 409
        )
    try:
        await lifter_repo.delete(db, lifter)
    except IntegrityError:
        # Prijava je nastala između provjere i brisanja; strani ključ je odbio brisanje
        raise AppError(
            "has_registrations", "Natjecatelj ima prijave i ne može se obrisati", 409
        )
