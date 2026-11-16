from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db

router = APIRouter()


@router.get("/")
async def health(db: AsyncSession = Depends(get_db, scope="function")):
    """Radi li aplikacija: odgovara i baza.

    Poziva je Docker (healthcheck u docker-compose.prod.yml) i nadzor. Proces koji
    radi, a ne dolazi do baze, nije zdrav: na svaki pravi zahtjev odgovorio bi s 500.
    """
    try:
        await db.execute(text("SELECT 1"))
    except (SQLAlchemyError, OSError):
        return JSONResponse(status_code=503, content={"status": "error"})
    return {"status": "ok"}
