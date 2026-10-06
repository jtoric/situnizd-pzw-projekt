"""Početni podatci za razvoj i obranu.

Pokreće se iz mape api/, nakon alembic upgrade head:
    python -m app.seed

Smije se pokrenuti bilo koliko puta: što već postoji, ne stvara se ponovno.
"""

import asyncio
from datetime import date, datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal, engine
from app.core.security import hash_password
from app.models import Club, Competition, Lifter, User

ADMIN_USERNAME = "admin@plreg.hr"
ADMIN_PASSWORD = "admin123"

# Dva kluba, da se vlasništvo može isprobati: klub A ne smije do podataka kluba B
# Polja: naziv, grad, korisničko ime, lozinka
DEMO_CLUBS = [
    ("PLK Behemot", "Zadar", "behemot@plreg.hr", "behemot123"),
    ("PK Sokol", "Split", "sokol@plreg.hr", "sokol123"),
]

# Natjecatelji po klubu; polja: ime, prezime, datum rođenja, spol
DEMO_LIFTERS = {
    "PLK Behemot": [
        ("Ana", "Horvat", date(2001, 5, 2), "F"),
        ("Ivan", "Perić", date(1998, 11, 20), "M"),
    ],
    "PK Sokol": [
        ("Marko", "Babić", date(2000, 1, 15), "M"),
    ],
}

# Radni primjer iz uvodnog predavanja; rokovi su po srednjoeuropskom vremenu, UTC+1
CET = timezone(timedelta(hours=1))
DEMO_COMPETITION = {
    "name": "Zimski kup",
    "location": "Zadar",
    "date": date(2027, 3, 14),
    "prelim_deadline": datetime(2027, 2, 14, 23, 59, tzinfo=CET),
    "final_deadline": datetime(2027, 3, 7, 23, 59, tzinfo=CET),
}


async def get_or_create_user(
    session: AsyncSession, username: str, password: str, role: str, club_id: int | None
) -> User:
    result = await session.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if user is None:
        user = User(
            username=username,
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


async def get_or_create_lifter(
    session: AsyncSession,
    club_id: int,
    first_name: str,
    last_name: str,
    birth_date: date,
    gender: str,
) -> Lifter:
    result = await session.execute(
        select(Lifter).where(
            Lifter.club_id == club_id,
            Lifter.first_name == first_name,
            Lifter.last_name == last_name,
        )
    )
    lifter = result.scalar_one_or_none()
    if lifter is None:
        lifter = Lifter(
            club_id=club_id,
            first_name=first_name,
            last_name=last_name,
            birth_date=birth_date,
            gender=gender,
        )
        session.add(lifter)
        await session.flush()
    return lifter


async def get_or_create_competition(session: AsyncSession, data: dict) -> Competition:
    result = await session.execute(
        select(Competition).where(Competition.name == data["name"])
    )
    competition = result.scalar_one_or_none()
    if competition is None:
        competition = Competition(**data)
        session.add(competition)
        await session.flush()
    return competition


async def seed() -> None:
    # Jedna transakcija: ili su svi retci upisani, ili nijedan
    async with AsyncSessionLocal() as session, session.begin():
        await get_or_create_user(session, ADMIN_USERNAME, ADMIN_PASSWORD, "admin", None)
        for name, city, username, password in DEMO_CLUBS:
            club = await get_or_create_club(session, name, city)
            await get_or_create_user(session, username, password, "club", club.id)
            for lifter in DEMO_LIFTERS[name]:
                await get_or_create_lifter(session, club.id, *lifter)
        await get_or_create_competition(session, DEMO_COMPETITION)

    await engine.dispose()
    print("Seed gotov.")
    print(f"  organizator: {ADMIN_USERNAME} / {ADMIN_PASSWORD}")
    for name, _, username, password in DEMO_CLUBS:
        print(f"  {name}: {username} / {password}")
    print(f"  natjecanje: {DEMO_COMPETITION['name']} ({DEMO_COMPETITION['date']})")


if __name__ == "__main__":
    asyncio.run(seed())
