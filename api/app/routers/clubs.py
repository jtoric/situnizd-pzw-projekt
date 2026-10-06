from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, require_role
from app.models.user import User
from app.schemas.club import ClubCreate, ClubResponse, ClubUpdate, PasswordReset
from app.services import club_service

router = APIRouter()


@router.get("/", response_model=list[ClubResponse])
async def list_clubs(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("admin", "club")),
):
    return await club_service.list_clubs(db, user)


@router.get("/{club_id}", response_model=ClubResponse)
async def get_club(
    club_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("admin", "club")),
):
    return await club_service.get_club(db, club_id, user)


@router.post("/", response_model=ClubResponse, status_code=201)
async def create_club(
    body: ClubCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_role("admin")),
):
    return await club_service.create_club(db, body)


@router.patch("/{club_id}", response_model=ClubResponse)
async def update_club(
    club_id: int,
    body: ClubUpdate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_role("admin")),
):
    return await club_service.update_club(db, club_id, body)


@router.post("/{club_id}/reset-password", status_code=204)
async def reset_password(
    club_id: int,
    body: PasswordReset,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_role("admin")),
):
    await club_service.reset_password(db, club_id, body.new_password)
