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

`python -m app.seed` stvara organizatora te dva kluba s njihovim računima. Smije se
pokrenuti više puta; što već postoji, ne stvara se ponovno.

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

## Pogreške

Svaki neuspjeh vraća tijelo istoga oblika:

```json
{ "code": "not_found", "message": "Not Found" }
```

`code` je stalan i namijenjen kodu klijenta, `message` je namijenjen čovjeku.
Pogreška u obliku podataka, sa statusom 422, uz to nosi polje `errors` s
popisom polja koja nisu prošla provjeru.

## Commitovi

Poruke prate oblik `vrsta(dio): namjera`, npr.
`feat(api): add JWT utilities`. Vrste: `feat`, `fix`, `refactor`, `test`,
`docs`, `chore`.
