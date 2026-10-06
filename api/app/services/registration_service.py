import logging

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.core.phases import Phase, get_competition_phase
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

logger = logging.getLogger(__name__)


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
    comp = await get_competition_or_404(db, comp_id)
    # Pravilo roka prije svega ostaloga: zahtjev koji ne prolazi ne pokreće
    # ni dohvat natjecatelja ni provjeru vlasništva.
    # "!= OPEN", a ne nabrajanje faza: nova faza ne bi tiho dopustila prijavu
    if get_competition_phase(comp) != Phase.OPEN:
        raise AppError("deadline_passed", "Rok za nove prijave je istekao", 400)

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
    # Dvostruku prijavu odbija baza: UNIQUE nad lifter_id i competition_id.
    # Provjera prije upisa ne bi bila dovoljna: dva istodobna zahtjeva prošla bi
    # oba. Bez ovog prevođenja klijent bi dobio 500.
    try:
        return await registration_repo.create(db, reg)
    except IntegrityError:
        raise AppError(
            "duplicate", "Natjecatelj je već prijavljen na ovo natjecanje", 409
        )


async def _get_registration_for_change(
    db: AsyncSession, comp_id: int, reg_id: int, current_user: User
) -> Registration:
    """Zajednički put izmjene, odjave i ponovne prijave: rok, postojanje, vlasništvo."""
    comp = await get_competition_or_404(db, comp_id)
    # Dopušteno i nakon nominacijskog roka, pa se odbija samo CLOSED
    if get_competition_phase(comp) == Phase.CLOSED:
        raise AppError(
            "deadline_passed", "Izmjene nisu moguće nakon finalnog roka", 400
        )
    reg = await _get_registration_or_404(db, comp_id, reg_id)
    _check_lifter_ownership(reg.lifter, current_user)
    return reg


async def update_registration(
    db: AsyncSession,
    comp_id: int,
    reg_id: int,
    body: RegistrationUpdate,
    current_user: User,
) -> Registration:
    reg = await _get_registration_for_change(db, comp_id, reg_id, current_user)
    changes = body.model_dump(exclude_unset=True)
    if "category" in changes:
        _check_category(reg.lifter, changes["category"])
    for field, value in changes.items():
        setattr(reg, field, value)
    await db.flush()
    return reg


async def withdraw_registration(
    db: AsyncSession, comp_id: int, reg_id: int, current_user: User
) -> Registration:
    """Odjava je prijelaz stanja, a ne brisanje: zapis i povijest ostaju."""
    reg = await _get_registration_for_change(db, comp_id, reg_id, current_user)
    # Ponovljeni zahtjev se odbija, pa sučelje zna da je odjava već provedena
    if reg.status == "withdrawn":
        raise AppError("already_withdrawn", "Prijava je već povučena", 400)
    reg.status = "withdrawn"
    await db.flush()
    logger.info("registration withdrawn: id=%s", reg.id)
    return reg


async def reactivate_registration(
    db: AsyncSession, comp_id: int, reg_id: int, current_user: User
) -> Registration:
    """Obrnuta radnja od odjave, dopuštena dok konačni rok nije prošao."""
    reg = await _get_registration_for_change(db, comp_id, reg_id, current_user)
    if reg.status == "active":
        raise AppError("already_active", "Prijava je već aktivna", 400)
    reg.status = "active"
    await db.flush()
    logger.info("registration reactivated: id=%s", reg.id)
    return reg
