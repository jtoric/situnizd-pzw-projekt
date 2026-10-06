from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, require_role
from app.models.user import User
from app.schemas.lifter import LifterCreate, LifterResponse, LifterUpdate
from app.services import lifter_service

# Putanje su bez prefiksa; /clubs/{club_id}/lifters dodaje main.py
router = APIRouter()


@router.get("/", response_model=list[LifterResponse])
async def list_lifters(
    club_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("admin", "club")),
    gender: str | None = Query(default=None, pattern=r"^[MF]$"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    return await lifter_service.list_lifters(db, club_id, user, gender, limit, offset)


@router.post("/", response_model=LifterResponse, status_code=201)
async def create_lifter(
    club_id: int,
    body: LifterCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("admin", "club")),
):
    return await lifter_service.create_lifter(db, club_id, body, user)


@router.get("/{lifter_id}", response_model=LifterResponse)
async def get_lifter(
    club_id: int,
    lifter_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("admin", "club")),
):
    return await lifter_service.get_lifter(db, club_id, lifter_id, user)


@router.patch("/{lifter_id}", response_model=LifterResponse)
async def update_lifter(
    club_id: int,
    lifter_id: int,
    body: LifterUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("admin", "club")),
):
    return await lifter_service.update_lifter(db, club_id, lifter_id, body, user)


@router.delete("/{lifter_id}", status_code=204)
async def delete_lifter(
    club_id: int,
    lifter_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("admin", "club")),
):
    await lifter_service.delete_lifter(db, club_id, lifter_id, user)
