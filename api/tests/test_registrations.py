import pytest
from freezegun import freeze_time

from tests.conftest import add_registration, auth_header


@pytest.fixture(autouse=True)
def open_phase():
    """Zadano vrijeme za testove u ovoj datoteci: prije nominacijskog roka.

    Natjecanje iz fixturea ima rokove 15.04. i 01.05.2026.; bez zamrzavanja
    ishod testa ovisio bi o danu pokretanja.
    """
    with freeze_time("2026-04-01 10:00:00"):
        yield


def url(competition, reg_id=None):
    base = f"/competitions/{competition.id}/registrations/"
    return base if reg_id is None else f"{base}{reg_id}"


# --- stvaranje ---------------------------------------------------------------------


async def test_club_registers_own_lifter(client, lifter, competition):
    headers = await auth_header(client, "testclub", "klub123")
    resp = await client.post(
        url(competition),
        json={"lifter_id": lifter.id, "category": "83", "total": 500},
        headers=headers,
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["status"] == "active"
    assert body["competition_id"] == competition.id
    # Povezani zapis u odgovoru, suženo na ime i prezime
    assert body["lifter"] == {"first_name": "Marko", "last_name": "Markić"}
    assert body["registered_at"]


async def test_club_cannot_register_other_club_lifter(
    client, lifter, rival_lifter, competition
):
    headers = await auth_header(client, "testclub", "klub123")
    # Tuđa oznaka stiže u tijelu zahtjeva, ne u adresi
    resp = await client.post(
        url(competition),
        json={"lifter_id": rival_lifter.id, "category": "63"},
        headers=headers,
    )
    assert resp.status_code == 403


async def test_register_unknown_lifter_is_404(client, club_and_user, competition):
    headers = await auth_header(client, "testclub", "klub123")
    resp = await client.post(
        url(competition), json={"lifter_id": 9999, "category": "83"}, headers=headers
    )
    assert resp.status_code == 404


async def test_register_to_unknown_competition_is_404(client, lifter):
    headers = await auth_header(client, "testclub", "klub123")
    resp = await client.post(
        "/competitions/9999/registrations/",
        json={"lifter_id": lifter.id, "category": "83"},
        headers=headers,
    )
    assert resp.status_code == 404


async def test_unknown_category_is_422(client, lifter, competition):
    headers = await auth_header(client, "testclub", "klub123")
    resp = await client.post(
        url(competition),
        json={"lifter_id": lifter.id, "category": "85"},
        headers=headers,
    )
    assert resp.status_code == 422
    assert resp.json()["errors"][0]["field"] == "category"


async def test_category_of_other_gender_is_400(client, lifter, competition):
    headers = await auth_header(client, "testclub", "klub123")
    # "63" je valjana kategorija, ali ženska: za to treba pogledati natjecatelja u bazi
    resp = await client.post(
        url(competition),
        json={"lifter_id": lifter.id, "category": "63"},
        headers=headers,
    )
    assert resp.status_code == 400
    assert resp.json()["code"] == "invalid_category"


async def test_negative_total_is_422(client, lifter, competition):
    headers = await auth_header(client, "testclub", "klub123")
    resp = await client.post(
        url(competition),
        json={"lifter_id": lifter.id, "category": "83", "total": -1},
        headers=headers,
    )
    assert resp.status_code == 422


# --- popis i jedan zapis ------------------------------------------------------------


async def test_admin_sees_all_registrations(
    client, db, admin_user, lifter, rival_lifter, competition
):
    await add_registration(db, lifter, competition, "83")
    await add_registration(db, rival_lifter, competition, "63")
    headers = await auth_header(client, "testadmin", "admin123")
    resp = await client.get(url(competition), headers=headers)
    assert resp.status_code == 200
    assert [r["lifter"]["first_name"] for r in resp.json()] == ["Marko", "Iva"]


async def test_club_sees_only_own_registrations(
    client, db, lifter, rival_lifter, competition
):
    await add_registration(db, lifter, competition, "83")
    await add_registration(db, rival_lifter, competition, "63")
    headers = await auth_header(client, "testclub", "klub123")
    resp = await client.get(url(competition), headers=headers)
    assert resp.status_code == 200
    assert [r["lifter"]["first_name"] for r in resp.json()] == ["Marko"]


async def test_list_registrations_pagination(
    client, db, admin_user, lifter, rival_lifter, competition
):
    await add_registration(db, lifter, competition, "83")
    await add_registration(db, rival_lifter, competition, "63")
    headers = await auth_header(client, "testadmin", "admin123")
    resp = await client.get(url(competition), params={"limit": 1}, headers=headers)
    assert len(resp.json()) == 1


async def test_club_cannot_get_other_club_registration(
    client, db, lifter, rival_lifter, competition
):
    reg = await add_registration(db, rival_lifter, competition, "63")
    headers = await auth_header(client, "testclub", "klub123")
    resp = await client.get(url(competition, reg.id), headers=headers)
    assert resp.status_code == 403


async def test_registration_under_wrong_competition_is_404(
    client, db, lifter, competition
):
    reg = await add_registration(db, lifter, competition, "83")
    headers = await auth_header(client, "testclub", "klub123")
    resp = await client.get(
        f"/competitions/9999/registrations/{reg.id}", headers=headers
    )
    assert resp.status_code == 404


# --- izmjena --------------------------------------------------------------------


async def test_patch_registration_category(client, db, lifter, competition):
    reg = await add_registration(db, lifter, competition, "83")
    headers = await auth_header(client, "testclub", "klub123")
    resp = await client.patch(
        url(competition, reg.id), json={"category": "93"}, headers=headers
    )
    assert resp.status_code == 200
    assert resp.json()["category"] == "93"
    assert resp.json()["total"] == 500


async def test_patch_registration_category_of_other_gender_is_400(
    client, db, lifter, competition
):
    reg = await add_registration(db, lifter, competition, "83")
    headers = await auth_header(client, "testclub", "klub123")
    resp = await client.patch(
        url(competition, reg.id), json={"category": "84+"}, headers=headers
    )
    assert resp.status_code == 400
    assert resp.json()["code"] == "invalid_category"


async def test_club_cannot_patch_other_club_registration(
    client, db, lifter, rival_lifter, competition
):
    reg = await add_registration(db, rival_lifter, competition, "63")
    headers = await auth_header(client, "testclub", "klub123")
    resp = await client.patch(
        url(competition, reg.id), json={"category": "69"}, headers=headers
    )
    assert resp.status_code == 403


# --- faze: nova prijava samo u OPEN, izmjena i u PRELIM_PASSED --------------------


@freeze_time("2026-04-01 10:00:00")
async def test_create_registration_open(client, lifter, competition):
    headers = await auth_header(client, "testclub", "klub123")
    resp = await client.post(
        url(competition),
        json={"lifter_id": lifter.id, "category": "83", "total": 500},
        headers=headers,
    )
    assert resp.status_code == 201


@freeze_time("2026-04-20 10:00:00")
async def test_create_registration_prelim_passed(client, lifter, competition):
    headers = await auth_header(client, "testclub", "klub123")
    resp = await client.post(
        url(competition),
        json={"lifter_id": lifter.id, "category": "83", "total": 500},
        headers=headers,
    )
    assert resp.status_code == 400
    # Kod pogreške potvrđuje da je razlog odbijanja rok, a ne nešto drugo
    assert resp.json()["code"] == "deadline_passed"


@freeze_time("2026-05-02 10:00:00")
async def test_create_registration_closed(client, lifter, competition):
    headers = await auth_header(client, "testclub", "klub123")
    resp = await client.post(
        url(competition),
        json={"lifter_id": lifter.id, "category": "83", "total": 500},
        headers=headers,
    )
    assert resp.status_code == 400
    assert resp.json()["code"] == "deadline_passed"


@freeze_time("2026-04-20 10:00:00")
async def test_update_category_prelim_passed(client, db, lifter, competition):
    reg = await add_registration(db, lifter, competition, "83")
    headers = await auth_header(client, "testclub", "klub123")
    resp = await client.patch(
        url(competition, reg.id), json={"category": "93"}, headers=headers
    )
    assert resp.status_code == 200
    assert resp.json()["category"] == "93"


@freeze_time("2026-05-02 10:00:00")
async def test_update_category_closed(client, db, lifter, competition):
    reg = await add_registration(db, lifter, competition, "83")
    headers = await auth_header(client, "testclub", "klub123")
    resp = await client.patch(
        url(competition, reg.id), json={"category": "93"}, headers=headers
    )
    assert resp.status_code == 400
    assert resp.json()["code"] == "deadline_passed"


@freeze_time("2026-05-02 10:00:00")
async def test_list_registrations_allowed_when_closed(client, db, lifter, competition):
    await add_registration(db, lifter, competition, "83")
    headers = await auth_header(client, "testclub", "klub123")
    resp = await client.get(url(competition), headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 1


@freeze_time("2026-04-20 10:00:00")
async def test_competition_response_carries_phase(client, club_and_user, competition):
    headers = await auth_header(client, "testclub", "klub123")
    resp = await client.get(f"/competitions/{competition.id}", headers=headers)
    assert resp.json()["phase"] == "prelim_passed"
