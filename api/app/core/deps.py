from collections.abc import AsyncGenerator

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.core.errors import AppError
from app.core.jwt import ExpiredSignatureError, InvalidTokenError, decode_token
from app.models.user import User
from app.repositories import user_repo


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Jedna sesija, a time i jedna transakcija, po zahtjevu.

    commit tek kad cijela obrada prođe; iznimka iz bilo kojeg sloja
    poništava sve što je zahtjev upisao.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# auto_error=False: bez zaglavlja dobivamo None i sami vraćamo 401 u našem obliku
_bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    # 1) je li token uopće poslan
    if credentials is None:
        raise AppError("invalid_credentials", "Nedostaje token", 401)
    # 2) može li se dekodirati: potpis, istek, izdavatelj
    try:
        payload = decode_token(credentials.credentials)
    except ExpiredSignatureError:
        raise AppError("token_expired", "Token je istekao", 401)
    except InvalidTokenError:
        raise AppError("invalid_credentials", "Neispravan token", 401)
    # 3) je li pristupni, a ne refresh token
    if payload.get("type") != "access":
        raise AppError("invalid_credentials", "Neispravan token", 401)

    # Token opisuje stanje u trenutku izdavanja; račun je u međuvremenu
    # mogao biti deaktiviran, pa zapis čitamo iz baze
    user = await user_repo.get_by_id(db, int(payload["sub"]))
    if not user or not user.is_active:
        raise AppError("invalid_credentials", "Neispravan token", 401)
    return user
