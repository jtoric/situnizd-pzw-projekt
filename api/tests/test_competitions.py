from tests.conftest import auth_header

NEW_COMPETITION = {
    "name": "Zimski kup",
    "location": "Zadar",
    "date": "2027-03-14",
    "prelim_deadline": "2027-02-14T23:59:00+01:00",
    "final_deadline": "2027-03-07T23:59:00+01:00",
}


# --- čitanje: svaki prijavljeni korisnik -------------------------------------------


async def test_club_lists_competitions(client, club_and_user, competition):
    headers = await auth_header(client, "testclub", "klub123")
    resp = await client.get("/competitions/", headers=headers)
    assert resp.status_code == 200
    assert [c["name"] for c in resp.json()] == ["Test Kup"]


async def test_list_competitions_without_token_is_401(client, competition):
    resp = await client.get("/competitions/")
    assert resp.status_code == 401


async def test_get_competition(client, club_and_user, competition):
    headers = await auth_header(client, "testclub", "klub123")
    resp = await client.get(f"/competitions/{competition.id}", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["location"] == "Zadar"


async def test_get_missing_competition_is_404(client, club_and_user):
    headers = await auth_header(client, "testclub", "klub123")
    resp = await client.get("/competitions/9999", headers=headers)
    assert resp.status_code == 404


# --- pisanje: samo organizator -----------------------------------------------------


async def test_admin_creates_competition(client, admin_user):
    headers = await auth_header(client, "testadmin", "admin123")
    resp = await client.post("/competitions/", json=NEW_COMPETITION, headers=headers)
    assert resp.status_code == 201
    assert resp.json()["id"] > 0


async def test_club_cannot_create_competition(client, club_and_user):
    headers = await auth_header(client, "testclub", "klub123")
    resp = await client.post("/competitions/", json=NEW_COMPETITION, headers=headers)
    assert resp.status_code == 403


async def test_deadline_without_timezone_is_422(client, admin_user):
    headers = await auth_header(client, "testadmin", "admin123")
    resp = await client.post(
        "/competitions/",
        json={**NEW_COMPETITION, "prelim_deadline": "2027-02-14T23:59:00"},
        headers=headers,
    )
    assert resp.status_code == 422
    assert resp.json()["errors"][0]["field"] == "prelim_deadline"


async def test_final_before_prelim_is_422(client, admin_user):
    headers = await auth_header(client, "testadmin", "admin123")
    resp = await client.post(
        "/competitions/",
        json={**NEW_COMPETITION, "final_deadline": "2027-02-01T23:59:00+01:00"},
        headers=headers,
    )
    assert resp.status_code == 422
    assert resp.json()["errors"][0]["field"] == "final_deadline"


async def test_deadline_after_competition_day_is_422(client, admin_user):
    headers = await auth_header(client, "testadmin", "admin123")
    resp = await client.post(
        "/competitions/",
        json={**NEW_COMPETITION, "date": "2027-03-01"},
        headers=headers,
    )
    assert resp.status_code == 422


async def test_admin_patches_competition_partially(client, admin_user, competition):
    headers = await auth_header(client, "testadmin", "admin123")
    resp = await client.patch(
        f"/competitions/{competition.id}", json={"location": "Split"}, headers=headers
    )
    assert resp.status_code == 200
    assert resp.json()["location"] == "Split"
    assert resp.json()["name"] == "Test Kup"


async def test_patch_prelim_after_existing_final_is_400(
    client, admin_user, competition
):
    headers = await auth_header(client, "testadmin", "admin123")
    # Shema vidi samo poslano polje; sukob s postojećim rokom otkriva servis
    resp = await client.patch(
        f"/competitions/{competition.id}",
        json={"prelim_deadline": "2026-05-10T00:00:00Z"},
        headers=headers,
    )
    assert resp.status_code == 400
    assert resp.json()["code"] == "invalid_deadlines"


async def test_club_cannot_patch_competition(client, club_and_user, competition):
    headers = await auth_header(client, "testclub", "klub123")
    resp = await client.patch(
        f"/competitions/{competition.id}", json={"location": "X"}, headers=headers
    )
    assert resp.status_code == 403
