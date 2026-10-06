from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Jedna sesija, a time i jedna transakcija, po zahtjevu.

    commit tek kad cijela obrada prođe; iznimka iz bilo kojeg sloja
    poništava sve što je zahtjev upisao.

    Rute je traže s Depends(get_db, scope="function"): tada se commit izvodi
    čim funkcija rute završi, prije slanja odgovora. Uz zadani scope="request"
    FastAPI kod iza yield izvodi tek nakon slanja, pa bi klijent mogao dobiti
    odgovor, a sljedećim zahtjevom ne vidjeti ono što je upisano.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
