from datetime import datetime, timedelta, timezone

import jwt
from sqlalchemy import update

from app.core.config import settings
from app.models import User
from tests.conftest import auth_header


async def login(client, username, password):
    return await client.post(
        "/auth/login", json={"username": username, "password": password}
    )


# --- prijava -------------------------------------------------------------------


async def test_login_success_returns_both_tokens(client, admin_user):
    resp = await login(client, "testadmin", "admin123")
    assert resp.status_code == 200
    body = resp.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"] and body["refresh_token"]


async def test_login_wrong_password(client, admin_user):
    resp = await login(client, "testadmin", "kriva")
    assert resp.status_code == 401
    assert resp.json()["code"] == "invalid_credentials"


async def test_login_unknown_user_same_response_as_wrong_password(client, admin_user):
    wrong_password = await login(client, "testadmin", "kriva")
    unknown_user = await login(client, "nepostojeci", "kriva")
    assert unknown_user.status_code == 401
    # Odgovor ne smije odati postoji li korisničko ime
    assert unknown_user.json() == wrong_password.json()


async def test_login_inactive_user_rejected(client, inactive_user):
    resp = await login(client, "inactive", "pass123")
    assert resp.status_code == 401
    assert resp.json()["code"] == "invalid_credentials"


async def test_login_missing_password_is_validation_error(client):
    resp = await client.post("/auth/login", json={"username": "testadmin"})
    assert resp.status_code == 422
    assert resp.json()["code"] == "validation_error"
    assert resp.json()["errors"][0]["field"] == "password"


async def test_login_password_over_72_bytes_rejected(client, admin_user):
    resp = await login(client, "testadmin", "č" * 40)  # 40 znakova, 80 bajtova
    assert resp.status_code == 422


# --- token pri svakom zahtjevu ---------------------------------------------------


async def test_me_returns_current_user_without_password_hash(client, club_and_user):
    club, _ = club_and_user
    headers = await auth_header(client, "testclub", "klub123")
    resp = await client.get("/auth/me", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["username"] == "testclub"
    assert body["role"] == "club"
    assert body["club_id"] == club.id
    assert "password_hash" not in body


async def test_me_without_token(client):
    resp = await client.get("/auth/me")
    assert resp.status_code == 401
    assert resp.json()["code"] == "invalid_credentials"


async def test_me_with_tampered_token(client, admin_user):
    headers = await auth_header(client, "testadmin", "admin123")
    token = headers["Authorization"].removeprefix("Bearer ")
    resp = await client.get(
        "/auth/me", headers={"Authorization": f"Bearer {token[:-4]}abcd"}
    )
    assert resp.status_code == 401
    assert resp.json()["code"] == "invalid_credentials"


async def test_me_with_token_signed_by_other_key(client, admin_user):
    token = jwt.encode(
        {
            "sub": str(admin_user.id),
            "role": "admin",
            "type": "access",
            "iss": settings.JWT_ISSUER,
            "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
        },
        "neki-drugi-kljuc-koji-poslužitelj-ne-poznaje",
        algorithm="HS256",
    )
    resp = await client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 401


async def test_me_with_expired_token(client, admin_user):
    token = jwt.encode(
        {
            "sub": str(admin_user.id),
            "role": "admin",
            "type": "access",
            "iss": settings.JWT_ISSUER,
            "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
        },
        settings.JWT_SECRET,
        algorithm="HS256",
    )
    resp = await client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 401
    assert resp.json()["code"] == "token_expired"


async def test_me_rejects_refresh_token(client, admin_user):
    tokens = (await login(client, "testadmin", "admin123")).json()
    resp = await client.get(
        "/auth/me", headers={"Authorization": f"Bearer {tokens['refresh_token']}"}
    )
    assert resp.status_code == 401


async def test_me_rejected_after_deactivation(client, db, admin_user):
    headers = await auth_header(client, "testadmin", "admin123")
    await db.execute(
        update(User).where(User.id == admin_user.id).values(is_active=False)
    )
    await db.commit()
    # Token je i dalje potpisan i nije istekao, ali račun više nije aktivan
    resp = await client.get("/auth/me", headers=headers)
    assert resp.status_code == 401


# --- obnova tokena ---------------------------------------------------------------


async def test_refresh_returns_new_working_pair(client, admin_user):
    tokens = (await login(client, "testadmin", "admin123")).json()
    resp = await client.post(
        "/auth/refresh", json={"refresh_token": tokens["refresh_token"]}
    )
    assert resp.status_code == 200
    new_access = resp.json()["access_token"]
    me = await client.get("/auth/me", headers={"Authorization": f"Bearer {new_access}"})
    assert me.status_code == 200


async def test_refresh_rejects_access_token(client, admin_user):
    tokens = (await login(client, "testadmin", "admin123")).json()
    resp = await client.post(
        "/auth/refresh", json={"refresh_token": tokens["access_token"]}
    )
    assert resp.status_code == 401
    assert resp.json()["code"] == "invalid_credentials"


async def test_refresh_rejects_garbage(client):
    resp = await client.post("/auth/refresh", json={"refresh_token": "nije.jwt.token"})
    assert resp.status_code == 401
