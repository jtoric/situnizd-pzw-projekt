import logging

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.core.security import hash_password
from app.models.club import Club
from app.models.user import User
from app.repositories import club_repo, user_repo
from app.schemas.club import ClubCreate, ClubUpdate

logger = logging.getLogger(__name__)


async def _get_or_404(db: AsyncSession, club_id: int) -> Club:
    club = await club_repo.get_by_id(db, club_id)
    if not club:
        raise AppError("not_found", "Klub nije pronađen", 404)
    return club


def ensure_club_access(current_user: User, club_id: int) -> None:
    """Vlasništvo: račun kluba smije samo do svojega kluba; organizator do svih."""
    if current_user.role == "club" and current_user.club_id != club_id:
        raise AppError("forbidden", "Nemate pristup podatcima drugoga kluba", 403)


async def get_club(db: AsyncSession, club_id: int, current_user: User) -> Club:
    # Prvo postoji li zapis, tek onda smije li ga pošiljatelj vidjeti
    club = await _get_or_404(db, club_id)
    ensure_club_access(current_user, club_id)
    return club


async def list_clubs(
    db: AsyncSession, current_user: User, limit: int, offset: int
) -> list[Club]:
    # Popis ne imenuje nijedan zapis, pa se ne odbija nego sužava
    if current_user.role == "admin":
        return await club_repo.get_all(db, limit, offset)
    club = await club_repo.get_by_id(db, current_user.club_id)
    return [club] if club else []


async def create_club(db: AsyncSession, body: ClubCreate) -> Club:
    # Provjera unaprijed daje jasnu poruku za uobičajen slučaj
    if await club_repo.get_by_name(db, body.name):
        raise AppError("duplicate", "Klub s tim nazivom već postoji", 409)
    if await user_repo.get_by_username(db, body.username):
        raise AppError("duplicate", "Korisničko ime je zauzeto", 409)

    # Ograničenje UNIQUE u bazi hvata i dva istodobna zahtjeva koja prođu provjeru
    try:
        club = await club_repo.create(db, Club(name=body.name, city=body.city))
        await user_repo.create(
            db,
            User(
                username=body.username,
                password_hash=hash_password(body.password),
                role="club",
                club_id=club.id,
            ),
        )
    except IntegrityError:
        raise AppError("duplicate", "Klub ili korisničko ime već postoji", 409)

    logger.info("club created: id=%s", club.id)
    return club


async def update_club(db: AsyncSession, club_id: int, body: ClubUpdate) -> Club:
    club = await _get_or_404(db, club_id)
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(club, field, value)
    try:
        await db.flush()
    except IntegrityError:
        raise AppError("duplicate", "Klub s tim nazivom već postoji", 409)
    return club


async def reset_password(db: AsyncSession, club_id: int, new_password: str) -> None:
    await _get_or_404(db, club_id)
    user = await user_repo.get_by_club_id(db, club_id)
    if not user:
        raise AppError("not_found", "Klub nema korisnički račun", 404)
    user.password_hash = hash_password(new_password)
    await db.flush()
    logger.info("club password reset: club_id=%s", club_id)
