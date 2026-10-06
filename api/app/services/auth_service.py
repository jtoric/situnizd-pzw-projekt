from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.core.jwt import (
    InvalidTokenError,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.core.security import hash_password, verify_password
from app.models.user import User
from app.repositories import user_repo

INVALID_CREDENTIALS = "Neispravno korisničko ime ili lozinka"

# Hash lozinke koja ne pripada nikome: provjera se izvodi i kad korisnik ne postoji,
# pa ni trajanje odgovora ne odaje postoji li korisničko ime
_DUMMY_HASH = hash_password("dummy-password-for-timing")


async def authenticate_user(db: AsyncSession, username: str, password: str) -> User:
    user = await user_repo.get_by_username(db, username)
    password_ok = verify_password(password, user.password_hash if user else _DUMMY_HASH)
    # Nepostojeći korisnik, kriva lozinka i deaktiviran račun: isti odgovor
    if not user or not password_ok:
        raise AppError("invalid_credentials", INVALID_CREDENTIALS, 401)
    if not user.is_active:
        raise AppError("invalid_credentials", INVALID_CREDENTIALS, 401)
    return user


def create_tokens(user: User) -> tuple[str, str]:
    access = create_access_token(user.id, user.role, user.club_id)
    refresh = create_refresh_token(user.id)
    return access, refresh


async def refresh_tokens(db: AsyncSession, refresh_token: str) -> tuple[str, str]:
    try:
        payload = decode_token(refresh_token)
    except InvalidTokenError:
        raise AppError("invalid_credentials", "Neispravan refresh token", 401)
    # Access token potpisan je istim ključem, pa vrsta mora biti provjerena
    if payload.get("type") != "refresh":
        raise AppError("invalid_credentials", "Neispravan refresh token", 401)
    user = await user_repo.get_by_id(db, int(payload["sub"]))
    if not user or not user.is_active:
        raise AppError("invalid_credentials", "Neispravan refresh token", 401)
    # Novi par: i refresh token dobiva novi vijek
    return create_tokens(user)
