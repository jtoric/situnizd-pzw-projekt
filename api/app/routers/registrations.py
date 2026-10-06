from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, require_role
from app.models.user import User
from app.schemas.registration import (
    RegistrationCreate,
    RegistrationResponse,
    RegistrationUpdate,
)
from app.services import registration_service

# Putanje su bez prefiksa; /competitions/{comp_id}/registrations dodaje main.py
router = APIRouter()


@router.get("/", response_model=list[RegistrationResponse])
async def list_registrations(
    comp_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("admin", "club")),
    status: str | None = Query(default=None, pattern=r"^(active|withdrawn)$"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    return await registration_service.list_registrations(
        db, comp_id, user, status, limit, offset
    )


@router.post("/", response_model=RegistrationResponse, status_code=201)
async def create_registration(
    comp_id: int,
    body: RegistrationCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("admin", "club")),
):
    return await registration_service.create_registration(db, comp_id, body, user)


@router.get("/{reg_id}", response_model=RegistrationResponse)
async def get_registration(
    comp_id: int,
    reg_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("admin", "club")),
):
    return await registration_service.get_registration(db, comp_id, reg_id, user)


@router.patch("/{reg_id}", response_model=RegistrationResponse)
async def update_registration(
    comp_id: int,
    reg_id: int,
    body: RegistrationUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("admin", "club")),
):
    return await registration_service.update_registration(
        db, comp_id, reg_id, body, user
    )
