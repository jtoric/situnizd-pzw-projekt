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
uvicorn app.main:app --reload
```

Provjera:

- http://127.0.0.1:8000/health vraća `{"status": "ok"}`
- http://127.0.0.1:8000/docs prikazuje Swagger UI s popisom ruta

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
