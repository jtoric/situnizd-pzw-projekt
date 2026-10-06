from tests.conftest import add_registration, auth_header

NEW_LIFTER = {
    "first_name": "Ana",
    "last_name": "Horvat",
    "birth_date": "2001-05-02",
    "gender": "F",
}


# --- stvaranje i validacija ------------------------------------------------------


async def test_club_creates_lifter_in_own_club(client, club_and_user):
    club, _ = club_and_user
    headers = await auth_header(client, "testclub", "klub123")
    resp = await client.post(
        f"/clubs/{club.id}/lifters/", json=NEW_LIFTER, headers=headers
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["id"] > 0
    # club_id dolazi iz adrese, ne iz tijela
    assert body["club_id"] == club.id


async def test_club_cannot_create_lifter_in_other_club(
    client, club_and_user, club_b_and_user
):
    club_b, _ = club_b_and_user
    headers = await auth_header(client, "testclub", "klub123")
    resp = await client.post(
        f"/clubs/{club_b.id}/lifters/", json=NEW_LIFTER, headers=headers
    )
    assert resp.status_code == 403


async def test_admin_creates_lifter_in_any_club(client, admin_user, club_b_and_user):
    club_b, _ = club_b_and_user
    headers = await auth_header(client, "testadmin", "admin123")
    resp = await client.post(
        f"/clubs/{club_b.id}/lifters/", json=NEW_LIFTER, headers=headers
    )
    assert resp.status_code == 201


async def test_create_lifter_birth_date_in_future_is_422(client, club_and_user):
    club, _ = club_and_user
    headers = await auth_header(client, "testclub", "klub123")
    resp = await client.post(
        f"/clubs/{club.id}/lifters/",
        json={**NEW_LIFTER, "birth_date": "2999-01-01"},
        headers=headers,
    )
    assert resp.status_code == 422
    assert resp.json()["errors"][0]["field"] == "birth_date"


async def test_create_lifter_unknown_gender_is_422(client, club_and_user):
    club, _ = club_and_user
    headers = await auth_header(client, "testclub", "klub123")
    resp = await client.post(
        f"/clubs/{club.id}/lifters/",
        json={**NEW_LIFTER, "gender": "X"},
        headers=headers,
    )
    assert resp.status_code == 422
    assert resp.json()["errors"][0]["field"] == "gender"


async def test_create_lifter_in_missing_club_is_404(client, admin_user):
    headers = await auth_header(client, "testadmin", "admin123")
    resp = await client.post("/clubs/9999/lifters/", json=NEW_LIFTER, headers=headers)
    assert resp.status_code == 404


# --- popis: vlasništvo, straničenje, filtar -----------------------------------------


async def test_club_lists_own_lifters(client, club_and_user, lifter):
    club, _ = club_and_user
    headers = await auth_header(client, "testclub", "klub123")
    resp = await client.get(f"/clubs/{club.id}/lifters/", headers=headers)
    assert resp.status_code == 200
    assert [lf["first_name"] for lf in resp.json()] == ["Marko"]


async def test_club_cannot_list_other_club_lifters(client, club_and_user, rival_lifter):
    headers = await auth_header(client, "testclub", "klub123")
    resp = await client.get(f"/clubs/{rival_lifter.club_id}/lifters/", headers=headers)
    assert resp.status_code == 403


async def test_list_lifters_without_token_is_401(client, club_and_user):
    club, _ = club_and_user
    resp = await client.get(f"/clubs/{club.id}/lifters/")
    assert resp.status_code == 401


async def test_list_lifters_pagination(client, club_and_user):
    club, _ = club_and_user
    headers = await auth_header(client, "testclub", "klub123")
    for name in ["Ana", "Bruno", "Cvita"]:
        await client.post(
            f"/clubs/{club.id}/lifters/",
            json={**NEW_LIFTER, "first_name": name},
            headers=headers,
        )
    url = f"/clubs/{club.id}/lifters/"
    first = await client.get(url, params={"limit": 2}, headers=headers)
    rest = await client.get(url, params={"limit": 2, "offset": 2}, headers=headers)
    assert [lf["first_name"] for lf in first.json()] == ["Ana", "Bruno"]
    assert [lf["first_name"] for lf in rest.json()] == ["Cvita"]


async def test_list_lifters_limit_has_upper_bound(client, club_and_user):
    club, _ = club_and_user
    headers = await auth_header(client, "testclub", "klub123")
    resp = await client.get(
        f"/clubs/{club.id}/lifters/", params={"limit": 101}, headers=headers
    )
    assert resp.status_code == 422


async def test_list_lifters_gender_filter(client, club_and_user, lifter):
    club, _ = club_and_user
    headers = await auth_header(client, "testclub", "klub123")
    await client.post(f"/clubs/{club.id}/lifters/", json=NEW_LIFTER, headers=headers)
    resp = await client.get(
        f"/clubs/{club.id}/lifters/", params={"gender": "F"}, headers=headers
    )
    assert [lf["first_name"] for lf in resp.json()] == ["Ana"]


# --- jedan zapis, izmjena, brisanje ------------------------------------------------


async def test_lifter_of_other_club_not_found_under_own_club_url(
    client, club_and_user, rival_lifter
):
    club, _ = club_and_user
    headers = await auth_header(client, "testclub", "klub123")
    # Vlastiti klub u adresi, tuđi natjecatelj: pod ovom adresom ne postoji
    resp = await client.get(
        f"/clubs/{club.id}/lifters/{rival_lifter.id}", headers=headers
    )
    assert resp.status_code == 404


async def test_patch_lifter_changes_only_sent_fields(client, club_and_user, lifter):
    club, _ = club_and_user
    headers = await auth_header(client, "testclub", "klub123")
    resp = await client.patch(
        f"/clubs/{club.id}/lifters/{lifter.id}",
        json={"last_name": "Marić"},
        headers=headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["last_name"] == "Marić"
    assert body["first_name"] == "Marko"
    assert body["birth_date"] == "2000-01-15"


async def test_patch_lifter_empty_body_changes_nothing(client, club_and_user, lifter):
    club, _ = club_and_user
    headers = await auth_header(client, "testclub", "klub123")
    resp = await client.patch(
        f"/clubs/{club.id}/lifters/{lifter.id}", json={}, headers=headers
    )
    assert resp.status_code == 200
    assert resp.json()["last_name"] == "Markić"


async def test_patch_lifter_explicit_null_is_422(client, club_and_user, lifter):
    club, _ = club_and_user
    headers = await auth_header(client, "testclub", "klub123")
    resp = await client.patch(
        f"/clubs/{club.id}/lifters/{lifter.id}",
        json={"first_name": None},
        headers=headers,
    )
    assert resp.status_code == 422


async def test_club_cannot_patch_other_club_lifter(client, club_and_user, rival_lifter):
    headers = await auth_header(client, "testclub", "klub123")
    resp = await client.patch(
        f"/clubs/{rival_lifter.club_id}/lifters/{rival_lifter.id}",
        json={"last_name": "X"},
        headers=headers,
    )
    assert resp.status_code == 403


async def test_delete_lifter(client, club_and_user, lifter):
    club, _ = club_and_user
    headers = await auth_header(client, "testclub", "klub123")
    url = f"/clubs/{club.id}/lifters/{lifter.id}"
    resp = await client.delete(url, headers=headers)
    assert resp.status_code == 204
    assert resp.content == b""
    assert (await client.get(url, headers=headers)).status_code == 404


async def test_delete_lifter_with_registrations_is_409(
    client, db, club_and_user, lifter, competition
):
    club, _ = club_and_user
    await add_registration(db, lifter, competition, "83")
    headers = await auth_header(client, "testclub", "klub123")
    resp = await client.delete(f"/clubs/{club.id}/lifters/{lifter.id}", headers=headers)
    assert resp.status_code == 409
    assert resp.json()["code"] == "has_registrations"


async def test_club_cannot_delete_other_club_lifter(
    client, club_and_user, rival_lifter
):
    headers = await auth_header(client, "testclub", "klub123")
    resp = await client.delete(
        f"/clubs/{rival_lifter.club_id}/lifters/{rival_lifter.id}", headers=headers
    )
    assert resp.status_code == 403
