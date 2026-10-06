from tests.conftest import auth_header

NEW_CLUB = {
    "name": "PK Novi",
    "city": "Rijeka",
    "username": "novi",
    "password": "novi12345",
}


# --- uloga: stvaranje, izmjena i reset lozinke smije samo organizator ----------


async def test_admin_creates_club_with_working_login(client, admin_user):
    headers = await auth_header(client, "testadmin", "admin123")
    resp = await client.post("/clubs/", json=NEW_CLUB, headers=headers)
    assert resp.status_code == 201
    assert resp.json()["name"] == "PK Novi"
    # Račun kluba nastao je u istoj transakciji i odmah radi
    club_headers = await auth_header(client, "novi", "novi12345")
    me = await client.get("/auth/me", headers=club_headers)
    assert me.json()["club_id"] == resp.json()["id"]


async def test_create_club_without_token_is_401(client):
    resp = await client.post("/clubs/", json=NEW_CLUB)
    assert resp.status_code == 401


async def test_club_cannot_create_club(client, club_and_user):
    headers = await auth_header(client, "testclub", "klub123")
    resp = await client.post("/clubs/", json=NEW_CLUB, headers=headers)
    assert resp.status_code == 403
    assert resp.json()["code"] == "forbidden"


async def test_create_club_duplicate_name_is_409(client, admin_user, club_and_user):
    headers = await auth_header(client, "testadmin", "admin123")
    resp = await client.post(
        "/clubs/", json={**NEW_CLUB, "name": "TestClub"}, headers=headers
    )
    assert resp.status_code == 409
    assert resp.json()["code"] == "duplicate"


async def test_create_club_duplicate_username_is_409(client, admin_user, club_and_user):
    headers = await auth_header(client, "testadmin", "admin123")
    resp = await client.post(
        "/clubs/", json={**NEW_CLUB, "username": "testclub"}, headers=headers
    )
    assert resp.status_code == 409
    # Ništa nije ostalo upisano: ni klub
    clubs = await client.get("/clubs/", headers=headers)
    assert [c["name"] for c in clubs.json()] == ["TestClub"]


async def test_create_club_short_password_is_422(client, admin_user):
    headers = await auth_header(client, "testadmin", "admin123")
    resp = await client.post(
        "/clubs/", json={**NEW_CLUB, "password": "kratka"}, headers=headers
    )
    assert resp.status_code == 422
    assert resp.json()["errors"][0]["field"] == "password"


async def test_admin_updates_club_partially(client, admin_user, club_and_user):
    club, _ = club_and_user
    headers = await auth_header(client, "testadmin", "admin123")
    resp = await client.patch(
        f"/clubs/{club.id}", json={"city": "Šibenik"}, headers=headers
    )
    assert resp.status_code == 200
    assert resp.json() == {"id": club.id, "name": "TestClub", "city": "Šibenik"}


async def test_club_cannot_update_own_club(client, club_and_user):
    club, _ = club_and_user
    headers = await auth_header(client, "testclub", "klub123")
    resp = await client.patch(f"/clubs/{club.id}", json={"city": "X"}, headers=headers)
    assert resp.status_code == 403


async def test_update_club_to_existing_name_is_409(
    client, admin_user, club_and_user, club_b_and_user
):
    club, _ = club_and_user
    headers = await auth_header(client, "testadmin", "admin123")
    resp = await client.patch(
        f"/clubs/{club.id}", json={"name": "RivalClub"}, headers=headers
    )
    assert resp.status_code == 409


async def test_admin_resets_club_password(client, admin_user, club_and_user):
    club, _ = club_and_user
    headers = await auth_header(client, "testadmin", "admin123")
    resp = await client.post(
        f"/clubs/{club.id}/reset-password",
        json={"new_password": "novalozinka"},
        headers=headers,
    )
    assert resp.status_code == 204
    old = await client.post(
        "/auth/login", json={"username": "testclub", "password": "klub123"}
    )
    assert old.status_code == 401
    await auth_header(client, "testclub", "novalozinka")


async def test_club_cannot_reset_password(client, club_and_user):
    club, _ = club_and_user
    headers = await auth_header(client, "testclub", "klub123")
    resp = await client.post(
        f"/clubs/{club.id}/reset-password",
        json={"new_password": "novalozinka"},
        headers=headers,
    )
    assert resp.status_code == 403


# --- vlasništvo: klub vidi samo svoj klub ---------------------------------------


async def test_admin_lists_all_clubs(
    client, admin_user, club_and_user, club_b_and_user
):
    headers = await auth_header(client, "testadmin", "admin123")
    resp = await client.get("/clubs/", headers=headers)
    assert resp.status_code == 200
    assert {c["name"] for c in resp.json()} == {"TestClub", "RivalClub"}


async def test_club_list_is_narrowed_to_own_club(
    client, club_and_user, club_b_and_user
):
    headers = await auth_header(client, "testclub", "klub123")
    resp = await client.get("/clubs/", headers=headers)
    # Nije 403 nego popis od jednog zapisa
    assert resp.status_code == 200
    assert [c["name"] for c in resp.json()] == ["TestClub"]


async def test_club_gets_own_club(client, club_and_user):
    club, _ = club_and_user
    headers = await auth_header(client, "testclub", "klub123")
    resp = await client.get(f"/clubs/{club.id}", headers=headers)
    assert resp.status_code == 200


async def test_club_cannot_get_other_club(client, club_and_user, club_b_and_user):
    club_b, _ = club_b_and_user
    headers = await auth_header(client, "testclub", "klub123")
    # IDOR: valjan token, ispravna uloga, tuđa oznaka u adresi
    resp = await client.get(f"/clubs/{club_b.id}", headers=headers)
    assert resp.status_code == 403
    assert resp.json()["code"] == "forbidden"


async def test_admin_gets_any_club(client, admin_user, club_b_and_user):
    club_b, _ = club_b_and_user
    headers = await auth_header(client, "testadmin", "admin123")
    resp = await client.get(f"/clubs/{club_b.id}", headers=headers)
    assert resp.status_code == 200


async def test_get_missing_club_is_404(client, admin_user):
    headers = await auth_header(client, "testadmin", "admin123")
    resp = await client.get("/clubs/9999", headers=headers)
    assert resp.status_code == 404
    assert resp.json()["code"] == "not_found"


async def test_list_clubs_without_token_is_401(client):
    resp = await client.get("/clubs/")
    assert resp.status_code == 401


async def test_patch_club_explicit_null_is_422(client, admin_user, club_and_user):
    club, _ = club_and_user
    headers = await auth_header(client, "testadmin", "admin123")
    resp = await client.patch(f"/clubs/{club.id}", json={"name": None}, headers=headers)
    assert resp.status_code == 422


async def test_list_clubs_pagination(
    client, admin_user, club_and_user, club_b_and_user
):
    headers = await auth_header(client, "testadmin", "admin123")
    resp = await client.get(
        "/clubs/", params={"limit": 1, "offset": 1}, headers=headers
    )
    assert [c["name"] for c in resp.json()] == ["RivalClub"]
