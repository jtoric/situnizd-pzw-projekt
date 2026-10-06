"""Početni podatci za razvoj i obranu.

Pokreće se iz mape api/, nakon alembic upgrade head:
    python -m app.seed

Smije se pokrenuti bilo koliko puta: što već postoji, ne stvara se ponovno.
"""

import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal, engine
from app.core.security import hash_password
from app.models import Club, User

ADMIN_EMAIL = "admin@plreg.hr"
ADMIN_PASSWORD = "admin123"

DEMO_CLUB_NAME = "PLK Behemot"
DEMO_CLUB_CITY = "Zadar"
DEMO_CLUB_EMAIL = "behemot@plreg.hr"
DEMO_CLUB_PASSWORD = "behemot123"


async def get_or_create_user(
    session: AsyncSession, email: str, password: str, role: str, club_id: int | None
) -> User:
    result = await session.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if user is None:
        user = User(
            email=email,
            password_hash=hash_password(password),
            role=role,
            club_id=club_id,
        )
        session.add(user)
        await session.flush()
    return user


async def get_or_create_club(session: AsyncSession, name: str, city: str) -> Club:
    result = await session.execute(select(Club).where(Club.name == name))
    club = result.scalar_one_or_none()
    if club is None:
        club = Club(name=name, city=city)
        session.add(club)
        # flush šalje upis prije commita, da klub dobije id za strani ključ
        await session.flush()
    return club


async def seed() -> None:
    # Jedna transakcija: ili su svi retci upisani, ili nijedan
    async with AsyncSessionLocal() as session, session.begin():
        await get_or_create_user(session, ADMIN_EMAIL, ADMIN_PASSWORD, "admin", None)
        club = await get_or_create_club(session, DEMO_CLUB_NAME, DEMO_CLUB_CITY)
        await get_or_create_user(
            session, DEMO_CLUB_EMAIL, DEMO_CLUB_PASSWORD, "club", club.id
        )

    await engine.dispose()
    print("Seed gotov.")
    print(f"  organizator: {ADMIN_EMAIL} / {ADMIN_PASSWORD}")
    print(f"  klub:        {DEMO_CLUB_EMAIL} / {DEMO_CLUB_PASSWORD}")


if __name__ == "__main__":
    asyncio.run(seed())
