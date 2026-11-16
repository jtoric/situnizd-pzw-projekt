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
web/                 # frontend: Vue 3, TypeScript, Vite
  src/
    main.ts          # sastavljanje aplikacije
    App.vue          # okvir: navigacija i mjesto za prikaz rute
    router/          # popis ruta
    views/           # stranice, jedna po ruti
    components/      # dijelovi prikaza koje dijeli više stranica
    api/             # oblici podataka i pozivi prema backendu
    stores/          # stanje koje dijeli više prikaza (prijava, natjecatelji, obavijesti)
    composables/     # logika koju dijeli više komponenata (useRequest)
    lib/             # čiste funkcije bez Vuea: provjera obrasca, oblikovanje, kategorije
    assets/          # zajednički stilovi
docker-compose.yml   # baza podataka
.env.example         # predložak konfiguracije
```

## Preduvjeti

- Git
- Python 3.11 ili noviji
- [uv](https://docs.astral.sh/uv/)
- Docker Desktop s alatom Docker Compose
- Node.js 22.12 ili noviji (frontend)

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

### Frontend

U drugom terminalu, uz pokrenut backend:

```bash
cd web
npm install                   # pakete iz package.json, prvi put i nakon promjene popisa
npm run dev                   # razvojni poslužitelj na http://127.0.0.1:5173
```

| Naredba | Što radi |
|---------|----------|
| `npm run dev` | razvojni poslužitelj; promijenjenu datoteku mijenja bez ponovnog učitavanja |
| `npm run type-check` | provjera tipova u cijelom projektu, uključujući datoteke `.vue` |
| `npm run build` | provjera tipova i izgradnja u mapu `dist/` |
| `npm run preview` | poslužuje izgrađenu mapu `dist/` |

Dogovori u kodu frontenda:

- stranica je u `views/` i završava s `View` (`LiftersView.vue`), dijeljeni dio prikaza je u
  `components/` (`AppNav.vue`); imena datoteka komponenata počinju velikim slovom
- adrese stranica su na hrvatskom (`/natjecanja`), a imena ruta, varijabli i funkcija na
  engleskom, kao i na backendu; tekst koji korisnik vidi je na hrvatskom
- oblik svakog odgovora API-ja opisan je jednom, u `api/types.ts`, istim imenima polja kao
  sheme u `api/app/schemas`
- boje i razmaci zadani su varijablama u `assets/main.css`; komponenta ih koristi kao
  `var(--ink)`, a vlastite stilove drži u `<style scoped>`
- linter nije postavljen; vrata kvalitete su provjera tipova, koju `npm run build` pokreće prije
  izgradnje, pa kod s pogreškom u tipovima ne može biti izgrađen

### Put jednog zahtjeva u frontendu

Klub otvori `/natjecanja`:

1. `router/index.ts`, provjera prije navigacije: nakon osvježavanja stranice čeka
   `stores/auth.ts` (`restore`, `GET /auth/me`), pa neprijavljenog korisnika šalje na
   `/prijava?redirect=/natjecanja`, a korisnika krive uloge na popis natjecanja.
2. `views/CompetitionsView.vue` poziva `fetchCompetitions()` iz `api/competitions.ts`.
3. `api/http.ts` dodaje token iz `api/tokens.ts` i šalje `GET /api/competitions/?limit=100`.
4. Vite (`vite.config.ts`) zahtjev prosljeđuje backendu kao `GET /competitions/`. Stranica i
   API tako dijele izvor, pa backend ne treba dopuštenje CORS.
5. Na `401` `api/http.ts` jednom traži novi par tokena (`POST /auth/refresh`) i ponavlja
   zahtjev; ako ni to ne uspije, `main.ts` korisnika šalje na prijavu.
6. Svaki drugi neuspjeh postaje `ApiError` s poljima `status`, `code` i `message`. Prikaz
   hvata samo ono na što reagira posebno, a ostalo kao obavijest prikazuje `main.ts`.

Tokeni su u `localStorage`, pod ključevima `plreg.access_token` i `plreg.refresh_token`.

### Gdje stoji stanje

| Podatak | Mjesto | Zašto |
|---------|--------|-------|
| prijavljeni korisnik | `stores/auth.ts` | čitaju ga navigacija, router i gotovo svaki prikaz |
| natjecatelji kluba | `stores/lifters.ts` | dijele ga popis natjecatelja i obrazac prijave |
| popis natjecanja, jedno natjecanje, prijave | komponenta, `useRequest` | treba ga samo jedan prikaz |
| vrijednosti obrasca i pogreške uz polja | komponenta | žive dok je obrazac otvoren |

### Sučelje organizatora

- natjecanja se dodaju i mijenjaju pod `/admin/natjecanja`; rokovi se upisuju po zagrebačkom
  vremenu, a `lib/datetime.ts` im dodaje pomak zone (`+01:00` zimi, `+02:00` ljeti), bez kojega
  ih API odbija
- tablica prijava na stranici natjecanja ima filtar po stanju i stranice u adresi
  (`?stanje=withdrawn&stranica=2`); pretraga i razvrstavanje rade nad prikazanom stranicom,
  a izvoz u CSV dohvaća cijeli popis
- koje radnje nad prijavama sučelje nudi, određuje razdoblje natjecanja (`lib/phase.ts`, ista
  matrica kao pod *Faze natjecanja*); radnja koja više nije dopuštena ostaje vidljiva i
  onemogućena, uz razlog

Prikaz koji nešto dohvaća razlikuje četiri stanja: prvi dohvat traje, prvi dohvat nije
uspio (s gumbom *Pokušaj ponovno*), popis je prazan i popis ima zapise. Obrazac provjerava
podatke prije slanja (`lib/validation.ts`, ista pravila kao sheme na backendu), a odgovor
`422` prikazuje uz polja na isti način (`lib/errors.ts`).

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
natjecateljima te natjecanje *16. Državno prvenstvo za mlađe juniore, juniore i
veterane u powerliftingu* 27.02.2027. u Zadru, s preliminarnim rokom 27.01. i
finalnim 20.02. Smije se pokrenuti više puta; što već postoji, ne stvara se
ponovno.

| Uloga | Prijava | Lozinka |
|-------|---------|---------|
| admin | `admin@plreg.hr` | `admin123` |
| club (PLK Behemot) | `behemot@plreg.hr` | `behemot123` |
| club (PLK Nabildani Mozak) | `nabildanimozak@plreg.hr` | `nabildanimozak123` |

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
| `predavanje-07` | Arhitektura jednostranične aplikacije |
| `predavanje-08` | Komunikacija s API-jem i prijava korisnika |
| `predavanje-09` | Upravljanje stanjem i stanja sučelja |
| `predavanje-10` | Tablice, filtri i administratorsko sučelje |

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
