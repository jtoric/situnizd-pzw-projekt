from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

# engine drži skup otvorenih veza prema bazi
engine = create_async_engine(settings.DATABASE_URL, pool_pre_ping=True)

# expire_on_commit=False: nakon commita objekti zadržavaju učitane vrijednosti,
# pa ih shema odgovora može pročitati bez novog lijenog upita
AsyncSessionLocal = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


class Base(DeclarativeBase):
    pass
