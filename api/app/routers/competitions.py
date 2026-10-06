from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db, require_role
from app.models.user import User
from app.schemas.competition import (
    CompetitionCreate,
    CompetitionResponse,
    CompetitionUpdate,
)
from app.services import competition_service

router = APIRouter()


# Čitanje smije svaki prijavljeni korisnik, pa je dovoljan get_current_user
@router.get("/", response_model=list[CompetitionResponse])
async def list_competitions(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    return await competition_service.list_competitions(db, limit, offset)


@router.get("/{competition_id}", response_model=CompetitionResponse)
async def get_competition(
    competition_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await competition_service.get_competition_or_404(db, competition_id)


# Pisanje smije samo organizator, pa ruta traži require_role
@router.post("/", response_model=CompetitionResponse, status_code=201)
async def create_competition(
    body: CompetitionCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_role("admin")),
):
    return await competition_service.create_competition(db, body)


@router.patch("/{competition_id}", response_model=CompetitionResponse)
async def update_competition(
    competition_id: int,
    body: CompetitionUpdate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_role("admin")),
):
    return await competition_service.update_competition(db, competition_id, body)
