"""Zajednička testna infrastruktura.

Testovi rade nad zasebnom bazom pl_reg_test na istom PostgreSQL
poslužitelju, pa razvojni podatci u pl_reg ostaju netaknuti.
Prije pokretanja: docker compose up -d db
"""

import asyncio
import os
from collections.abc import AsyncGenerator

import bcrypt
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import make_url, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.core.deps import get_db
from app.main import create_app
from app.models import Base, Club, User


def _test_database_url() -> str:
    if url := os.environ.get("TEST_DATABASE_URL"):
        return url
    url = make_url(settings.DATABASE_URL)
    url = url.set(database=f"{url.database}_test")
    return url.render_as_string(hide_password=False)


TEST_DATABASE_URL = _test_database_url()

# NullPool: svaki test ima svoju petlju događaja, pa veze ne smiju preživjeti test
engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
TestSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)


async def _prepare_database() -> None:
    url = make_url(TEST_DATABASE_URL)
    server = create_async_engine(
        url.set(database="postgres"), isolation_level="AUTOCOMMIT", poolclass=NullPool
    )
    async with server.connect() as conn:
        exists = await conn.scalar(
            text("SELECT 1 FROM pg_database WHERE datname = :name"),
            {"name": url.database},
        )
        if not exists:
            await conn.execute(text(f'CREATE DATABASE "{url.database}"'))
    await server.dispose()

    # Shema iz modela, svaki put iznova
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@pytest.fixture(scope="session", autouse=True)
def test_database():
    asyncio.run(_prepare_database())


@pytest.fixture(autouse=True)
async def clean_tables():
    """Svaki test počinje od praznih tablica."""
    tables = ", ".join(table.name for table in Base.metadata.sorted_tables)
    async with engine.begin() as conn:
        await conn.execute(text(f"TRUNCATE {tables} RESTART IDENTITY CASCADE"))


async def _get_test_db() -> AsyncGenerator[AsyncSession, None]:
    async with TestSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """HTTP klijent nad aplikacijom, bez pokretanja poslužitelja."""
    app = create_app()
    app.dependency_overrides[get_db] = _get_test_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def db() -> AsyncGenerator[AsyncSession, None]:
    """Sesija za pripremu podataka izravno u bazi."""
    async with TestSessionLocal() as session:
        yield session


def fast_hash(password: str) -> str:
    # Faktor rada 4 umjesto zadanih 12: hash je jednako valjan, a testovi brži
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=4)).decode()


async def auth_header(client: AsyncClient, username: str, password: str) -> dict:
    resp = await client.post(
        "/auth/login", json={"username": username, "password": password}
    )
    assert resp.status_code == 200, resp.text
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


@pytest.fixture
async def admin_user(db: AsyncSession) -> User:
    """Organizator: testadmin / admin123."""
    user = User(username="testadmin", password_hash=fast_hash("admin123"), role="admin")
    db.add(user)
    await db.commit()
    return user


@pytest.fixture
async def club_and_user(db: AsyncSession) -> tuple[Club, User]:
    """Klub i njegov račun: testclub / klub123."""
    club = Club(name="TestClub", city="Zadar")
    db.add(club)
    await db.flush()
    user = User(
        username="testclub",
        password_hash=fast_hash("klub123"),
        role="club",
        club_id=club.id,
    )
    db.add(user)
    await db.commit()
    return club, user


@pytest.fixture
async def club_b_and_user(db: AsyncSession) -> tuple[Club, User]:
    """Drugi klub, za provjere vlasništva: rivalclub / rival123."""
    club = Club(name="RivalClub", city="Split")
    db.add(club)
    await db.flush()
    user = User(
        username="rivalclub",
        password_hash=fast_hash("rival123"),
        role="club",
        club_id=club.id,
    )
    db.add(user)
    await db.commit()
    return club, user


@pytest.fixture
async def inactive_user(db: AsyncSession) -> User:
    """Deaktiviran račun: inactive / pass123."""
    user = User(
        username="inactive",
        password_hash=fast_hash("pass123"),
        role="admin",
        is_active=False,
    )
    db.add(user)
    await db.commit()
    return user
