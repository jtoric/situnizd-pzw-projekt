import pytest
from pydantic import ValidationError

from app.core.config import Settings


async def test_health_returns_ok(client):
    resp = await client.get("/health/")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


async def test_unknown_route_uses_error_format(client):
    resp = await client.get("/nepostojeca-ruta")
    assert resp.status_code == 404
    assert resp.json()["code"] == "not_found"


@pytest.mark.parametrize(
    "secret",
    ["change-me", "dev-only-secret-change-me-in-production-0123456789", "kratak"],
    ids=["zadani", "iz-env-example", "prekratak"],
)
def test_production_refuses_public_or_short_secret(secret):
    with pytest.raises(ValidationError, match="JWT_SECRET"):
        Settings(ENV="prod", DATABASE_URL="postgresql+asyncpg://x", JWT_SECRET=secret)


def test_production_accepts_long_private_secret():
    settings = Settings(
        ENV="prod", DATABASE_URL="postgresql+asyncpg://x", JWT_SECRET="a" * 64
    )
    assert not settings.is_dev


def test_development_accepts_example_secret():
    Settings(ENV="dev", DATABASE_URL="postgresql+asyncpg://x", JWT_SECRET="change-me")
