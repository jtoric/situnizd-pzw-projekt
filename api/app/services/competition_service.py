from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.models.competition import Competition
from app.repositories import competition_repo
from app.schemas.competition import CompetitionCreate, CompetitionUpdate


async def get_competition_or_404(db: AsyncSession, competition_id: int) -> Competition:
    competition = await competition_repo.get_by_id(db, competition_id)
    if not competition:
        raise AppError("not_found", "Natjecanje nije pronađeno", 404)
    return competition


async def list_competitions(
    db: AsyncSession, limit: int, offset: int
) -> list[Competition]:
    return await competition_repo.get_all(db, limit, offset)


async def create_competition(db: AsyncSession, body: CompetitionCreate) -> Competition:
    return await competition_repo.create(db, Competition(**body.model_dump()))


async def update_competition(
    db: AsyncSession, competition_id: int, body: CompetitionUpdate
) -> Competition:
    competition = await get_competition_or_404(db, competition_id)
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(competition, field, value)

    # Shema vidi samo poslana polja; poredak rokova provjerava se nad spojenim
    # stanjem: novi prelim_deadline mora biti prije postojećeg final_deadline
    if competition.prelim_deadline >= competition.final_deadline:
        raise AppError(
            "invalid_deadlines", "final_deadline mora biti nakon prelim_deadline", 400
        )
    if competition.final_deadline.date() >= competition.date:
        raise AppError(
            "invalid_deadlines", "Rokovi moraju isteći prije dana natjecanja", 400
        )
    await db.flush()
    return competition
