"""Prvi račun organizatora u produkciji.

Početni podatci (app/seed.py) su za razvoj: uz organizatora stvaraju izmišljene
klubove, a lozinke su im javne, jer stoje u kodu. U produkciji se upisuje samo
organizator, s lozinkom koja nije nigdje zapisana:

    ADMIN_USERNAME=organizator@savez.hr ADMIN_PASSWORD=... python -m app.create_admin

U kontejneru (docker-compose.prod.yml), iz korijena repozitorija:

    docker compose -f docker-compose.prod.yml --env-file .env.prod exec
        -e ADMIN_USERNAME=... -e ADMIN_PASSWORD=... api python -m app.create_admin

(naredba je jedan redak). Postojeći račun se ne mijenja, pa se naredba smije
pokrenuti više puta.
"""

import asyncio
import os
import sys

from sqlalchemy import select

from app.core.database import AsyncSessionLocal, engine
from app.core.security import hash_password
from app.models import User

MIN_PASSWORD_LENGTH = 12


async def create_admin(username: str, password: str) -> bool:
    """Stvara organizatora; vraća False ako račun tog imena već postoji."""
    async with AsyncSessionLocal() as session, session.begin():
        existing = await session.scalar(select(User).where(User.username == username))
        if existing is not None:
            return False
        session.add(
            User(
                username=username,
                password_hash=hash_password(password),
                role="admin",
                club_id=None,
            )
        )
    await engine.dispose()
    return True


def main() -> int:
    username = os.environ.get("ADMIN_USERNAME", "").strip()
    password = os.environ.get("ADMIN_PASSWORD", "")
    if not username or len(password) < MIN_PASSWORD_LENGTH:
        print(
            "Potrebni su ADMIN_USERNAME i ADMIN_PASSWORD "
            f"(barem {MIN_PASSWORD_LENGTH} znakova).",
            file=sys.stderr,
        )
        return 1
    created = asyncio.run(create_admin(username, password))
    print("Organizator je stvoren." if created else "Račun već postoji; nije mijenjan.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
