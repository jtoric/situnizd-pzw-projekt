from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.models.lifter import Lifter
from app.models.registration import Registration
from app.models.user import User
from app.repositories import lifter_repo, registration_repo
from app.schemas.registration import (
    CATEGORIES_BY_GENDER,
    RegistrationCreate,
    RegistrationUpdate,
)
from app.services.competition_service import get_competition_or_404


def _check_lifter_ownership(lifter: Lifter, current_user: User) -> None:
    if current_user.role == "club" and lifter.club_id != current_user.club_id:
        raise AppError("forbidden", "Natjecatelj ne pripada vašem klubu", 403)


def _check_category(lifter: Lifter, category: str) -> None:
    # Shema zna je li kategorija na popisu; odgovara li spolu natjecatelja
    # zna se tek kad je natjecatelj dohvaćen iz baze
    if category not in CATEGORIES_BY_GENDER[lifter.gender]:
        raise AppError(
            "invalid_category",
            f"Kategorija {category} ne odgovara spolu natjecatelja",
            400,
        )


async def _get_registration_or_404(
    db: AsyncSession, comp_id: int, reg_id: int
) -> Registration:
    reg = await registration_repo.get_by_id(db, reg_id)
    if not reg or reg.competition_id != comp_id:
        raise AppError("not_found", "Prijava nije pronađena", 404)
    return reg


async def list_registrations(
    db: AsyncSession,
    comp_id: int,
    current_user: User,
    status: str | None,
    limit: int,
    offset: int,
) -> list[Registration]:
    await get_competition_or_404(db, comp_id)
    # Organizator vidi sve prijave, klub samo prijave svojih natjecatelja
    club_id = current_user.club_id if current_user.role == "club" else None
    return await registration_repo.list_for_competition(
        db, comp_id, club_id, status, limit, offset
    )


async def get_registration(
    db: AsyncSession, comp_id: int, reg_id: int, current_user: User
) -> Registration:
    await get_competition_or_404(db, comp_id)
    reg = await _get_registration_or_404(db, comp_id, reg_id)
    _check_lifter_ownership(reg.lifter, current_user)
    return reg


async def create_registration(
    db: AsyncSession, comp_id: int, body: RegistrationCreate, current_user: User
) -> Registration:
    await get_competition_or_404(db, comp_id)

    lifter = await lifter_repo.get_by_id(db, body.lifter_id)
    if not lifter:
        raise AppError("not_found", "Natjecatelj nije pronađen", 404)
    # Oznaka natjecatelja stiže u tijelu zahtjeva; i nju treba provjeriti, inače IDOR
    _check_lifter_ownership(lifter, current_user)
    _check_category(lifter, body.category)

    reg = Registration(
        competition_id=comp_id,
        lifter=lifter,
        category=body.category,
        total=body.total,
    )
    return await registration_repo.create(db, reg)


async def update_registration(
    db: AsyncSession,
    comp_id: int,
    reg_id: int,
    body: RegistrationUpdate,
    current_user: User,
) -> Registration:
    reg = await get_registration(db, comp_id, reg_id, current_user)
    changes = body.model_dump(exclude_unset=True)
    if "category" in changes:
        _check_category(reg.lifter, changes["category"])
    for field, value in changes.items():
        setattr(reg, field, value)
    await db.flush()
    return reg
