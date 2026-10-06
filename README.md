# Prijave na powerlifting natjecanja

Referentni projekt kolegija **Programiranje za web** na SIT UNIZD.

Klubovi prijavljuju svoje natjecatelje na natjecanja, a organizator vidi prijave
svih klubova. Natjecanje ima dva roka nominacije koji određuju što se smije
mijenjati.

## Struktura

```
api/                 # backend: FastAPI
  app/
    main.py          # sastavljanje aplikacije
    core/            # konfiguracija, ovisnosti, pogreške, zapisnik
    routers/         # rute: primaju zahtjev, vraćaju odgovor
    schemas/         # Pydantic sheme ulaza i izlaza
    services/        # poslovna pravila
    repositories/    # upiti nad bazom
    models/          # SQLAlchemy modeli
web/                 # frontend: Vue, dolazi u 2. dijelu
docker-compose.yml   # baza podataka
.env.example         # predložak konfiguracije
```

## Preduvjeti

- Git
- Python 3.11 ili noviji
- [uv](https://docs.astral.sh/uv/)
- Docker Desktop s alatom Docker Compose

## Pokretanje

```bash
# 1) Konfiguracija
cp .env.example .env          # PowerShell: Copy-Item .env.example .env

# 2) Baza
docker compose up -d db

# 3) Backend
cd api
uv venv
source .venv/bin/activate     # PowerShell: .venv\Scripts\Activate.ps1
uv pip install -r requirements.txt
alembic upgrade head          # stvara tablice
python -m app.seed            # početni podatci
uvicorn app.main:app --reload
```

Provjera:

- http://127.0.0.1:8000/health vraća `{"status": "ok"}`
- http://127.0.0.1:8000/docs prikazuje Swagger UI s popisom ruta

## Baza podataka

Shema baze mijenja se isključivo migracijama, koje stoje u
`api/alembic/versions/`.

```bash
cd api

# nova migracija iz razlike između modela i baze
alembic revision --autogenerate --rev-id 002 -m "opis promjene"

alembic upgrade head      # primijeni sve što još nije primijenjeno
alembic downgrade -1      # poništi zadnju migraciju
alembic current           # na kojoj je migraciji baza
```

Svaka nastala migracija čita se **prije** pokretanja: preimenovanje stupca
`autogenerate` vidi kao `drop_column` + `add_column`, što briše podatke. Ispravak
je `op.alter_column(..., new_column_name=...)`.

### Početni podatci

`python -m app.seed` stvara organizatora, dva kluba s njihovim računima i
natjecateljima te natjecanje *Zimski kup* 14.03.2027., s preliminarnim rokom
14.02. i finalnim 07.03. Smije se pokrenuti više puta; što već postoji, ne
stvara se ponovno.

| Uloga | Prijava | Lozinka |
|-------|---------|---------|
| admin | `admin@plreg.hr` | `admin123` |
| club (PLK Behemot) | `behemot@plreg.hr` | `behemot123` |
| club (PK Sokol) | `sokol@plreg.hr` | `sokol123` |

### Prazna baza

```bash
docker compose down -v        # briše kontejner i volumen s podatcima
docker compose up -d db
cd api
alembic upgrade head
python -m app.seed
```

Isto vrijedi pri prelasku na raniji commit ili tag predavanja: baza može biti
na migraciji koju stariji kod ne poznaje.

## Testovi

```bash
docker compose up -d db
cd api
pytest
```

Testovi rade nad zasebnom bazom `pl_reg_test` na istom poslužitelju; stvara se
sama pri prvom pokretanju, a tablice se prazne prije svakog testa. Drugu bazu
moguće je zadati varijablom `TEST_DATABASE_URL`.

## Kvaliteta koda

```bash
cd api
ruff format .     # jedinstven stil
ruff check .      # pogreške vidljive iz koda
```

## API

Svi popisi primaju `limit` i `offset`. Zadano je 20 zapisa od početka popisa,
a `limit` smije biti najviše 100.

### Autentikacija

| Metoda | Putanja | Opis | Pristup |
|--------|---------|------|---------|
| POST | `/auth/login` | prijava, vraća access i refresh token | javno |
| POST | `/auth/refresh` | novi par tokena | refresh token |
| GET | `/auth/me` | trenutni korisnik | prijavljen |

Access token vrijedi 15 minuta, refresh token 7 dana. Access token šalje se u
zaglavlju `Authorization: Bearer <token>`.

### Klubovi

| Metoda | Putanja | Opis | Pristup |
|--------|---------|------|---------|
| GET | `/clubs/` | popis klubova | admin: svi, klub: samo svoj |
| POST | `/clubs/` | novi klub i njegov račun | admin |
| GET | `/clubs/{club_id}` | jedan klub | admin, vlastiti klub |
| PATCH | `/clubs/{club_id}` | izmjena kluba | admin |
| POST | `/clubs/{club_id}/reset-password` | nova lozinka računa kluba | admin |

### Natjecatelji

| Metoda | Putanja | Opis | Pristup |
|--------|---------|------|---------|
| GET | `/clubs/{club_id}/lifters/` | popis, filtar `gender` | admin, vlastiti klub |
| POST | `/clubs/{club_id}/lifters/` | novi natjecatelj | admin, vlastiti klub |
| GET | `/clubs/{club_id}/lifters/{id}` | jedan natjecatelj | admin, vlastiti klub |
| PATCH | `/clubs/{club_id}/lifters/{id}` | izmjena | admin, vlastiti klub |
| DELETE | `/clubs/{club_id}/lifters/{id}` | brisanje, samo ako nema prijava | admin, vlastiti klub |

### Natjecanja

| Metoda | Putanja | Opis | Pristup |
|--------|---------|------|---------|
| GET | `/competitions/` | popis, s izračunatom fazom | prijavljen |
| POST | `/competitions/` | novo natjecanje | admin |
| GET | `/competitions/{id}` | jedno natjecanje | prijavljen |
| PATCH | `/competitions/{id}` | izmjena | admin |

### Prijave

| Metoda | Putanja | Opis | Pristup |
|--------|---------|------|---------|
| GET | `/competitions/{id}/registrations/` | popis, filtar `status` | admin: sve, klub: svoje |
| POST | `/competitions/{id}/registrations/` | nova prijava | vlasnik natjecatelja, `OPEN` |
| GET | `/competitions/{id}/registrations/{rid}` | jedna prijava | vlasnik |
| PATCH | `/competitions/{id}/registrations/{rid}` | kategorija, total | vlasnik, `OPEN`/`PRELIM_PASSED` |
| POST | `/competitions/{id}/registrations/{rid}/withdraw` | odjava | vlasnik, `OPEN`/`PRELIM_PASSED` |
| POST | `/competitions/{id}/registrations/{rid}/reactivate` | povratak odjavljene | vlasnik, `OPEN`/`PRELIM_PASSED` |

## Faze natjecanja

Faza se ne pohranjuje nego računa pri svakom zahtjevu iz dvaju rokova, u
`app/core/phases.py`.

| Radnja | `OPEN` | `PRELIM_PASSED` | `CLOSED` |
|--------|:------:|:---------------:|:--------:|
| nova prijava | da | ne | ne |
| promjena kategorije | da | da | ne |
| odjava i povratak | da | da | ne |
| čitanje popisa | da | da | da |

`OPEN` traje do preliminarnog roka, `PRELIM_PASSED` do finalnog, a `CLOSED`
nakon njega. Težinske kategorije IPF-a: muškarci 59, 66, 74, 83, 93, 105, 120,
120+; žene 47, 52, 57, 63, 69, 76, 84, 84+.

## Pogreške

Svaki neuspjeh vraća tijelo istoga oblika:

```json
{ "code": "not_found", "message": "Not Found" }
```

`code` je stalan i namijenjen kodu klijenta, `message` je namijenjen čovjeku.
Pogreška u obliku podataka, sa statusom 422, uz to nosi polje `errors` s
popisom polja koja nisu prošla provjeru.

| `code` | HTTP | Kada |
|--------|------|------|
| `validation_error` | 422 | tijelo ili parametri ne odgovaraju shemi |
| `invalid_credentials` | 401 | prijava ili token ne vrijede |
| `token_expired` | 401 | access token je istekao |
| `forbidden` | 403 | uloga ili vlasništvo ne dopuštaju radnju |
| `not_found` | 404 | zapis ne postoji |
| `duplicate` | 409 | zapis bi prekršio jedinstvenost |
| `has_registrations` | 409 | natjecatelj s prijavama ne može se obrisati |
| `deadline_passed` | 400 | radnja nije moguća u ovoj fazi |
| `already_withdrawn` | 400 | prijava je već povučena |
| `already_active` | 400 | prijava je već aktivna |
| `invalid_category` | 400 | kategorija ne odgovara spolu natjecatelja |
| `invalid_deadlines` | 400 | izmjena bi poremetila poredak rokova |

## Tagovi predavanja

Stanje projekta na kraju svakog predavanja označeno je tagom:

| Tag | Predavanje |
|-----|------------|
| `predavanje-01` | Arhitektura backenda i kostur projekta |
| `predavanje-02` | Modeliranje podataka, ORM i migracije |
| `predavanje-03` | Autentikacija i sigurnost |
| `predavanje-04` | Autorizacija i vlasništvo nad zapisom |
| `predavanje-05` | Oblikovanje API-ja i CRUD domene |
| `predavanje-06` | Poslovna pravila i rokovi |

```bash
git log --oneline predavanje-02..predavanje-03    # commitovi jednog predavanja
git diff predavanje-02 predavanje-03              # sve promjene jednog predavanja
git checkout predavanje-03                        # projekt na kraju 3. predavanja
```

Nakon prelaska na drugi tag bazu treba vratiti u prazno stanje, kako je opisano
pod *Prazna baza*, i ponovno instalirati zavisnosti.

## Commitovi

Poruke prate oblik `vrsta(dio): namjera`, npr.
`feat(api): add JWT utilities`. Vrste: `feat`, `fix`, `refactor`, `test`,
`docs`, `chore`.
