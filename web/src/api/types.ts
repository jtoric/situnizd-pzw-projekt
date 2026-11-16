/**
 * Oblici podataka koje šalje i vraća API.
 *
 * Svako sučelje preslikava jednu shemu iz api/app/schemas, istim imenima polja. Kad se shema
 * na poslužitelju promijeni, mijenja se i ovdje: provjera tipova (npm run type-check) tada
 * pokaže svako mjesto u klijentu koje još računa na staro polje.
 *
 * Datumi stižu kao tekst u obliku ISO 8601: datum bez vremena ("2027-03-14") i trenutak s
 * oznakom zone ("2027-02-14T22:59:00Z"). JSON nema tip za datum, pa string ostaje string dok ga
 * netko izričito ne pretvori.
 */

/** Uloga korisnika; isto u api/app/models/user.py */
export type Role = 'admin' | 'club'

/** app/schemas/user.py, UserResponse; vraća GET /auth/me */
export interface User {
  id: number
  username: string
  role: Role
  club_id: number | null // null za organizatora, koji ne pripada klubu
  is_active: boolean
}

/** app/schemas/auth.py, TokenResponse; vraćaju POST /auth/login i POST /auth/refresh */
export interface TokenPair {
  access_token: string // ide uz svaki zahtjev, vrijedi 15 minuta
  refresh_token: string // samo za POST /auth/refresh, vrijedi 7 dana
  token_type: 'bearer'
}

/** app/schemas/club.py, ClubResponse */
export interface Club {
  id: number
  name: string
  city: string
}

export type Gender = 'M' | 'F'

/** app/schemas/lifter.py, LifterResponse */
export interface Lifter {
  id: number
  first_name: string
  last_name: string
  birth_date: string // "GGGG-MM-DD"
  gender: Gender
  club_id: number
}

/** Tijelo za POST; bez id, koji dodjeljuje baza, i bez club_id, koji je u adresi (LifterCreate) */
export type LifterInput = Omit<Lifter, 'id' | 'club_id'>

/** Razdoblje natjecanja; računa ga poslužitelj iz dvaju rokova (app/core/phases.py) */
export type Phase = 'open' | 'prelim_passed' | 'closed'

/** app/schemas/competition.py, CompetitionResponse */
export interface Competition {
  id: number
  name: string
  location: string
  date: string // "GGGG-MM-DD"
  prelim_deadline: string // trenutak s oznakom zone
  final_deadline: string
  phase: Phase // izvedena vrijednost, ne postoji u bazi
}

/** Tijelo za POST; rokovi moraju nositi oznaku zone, inače 422 (AwareDatetime) */
export type CompetitionInput = Omit<Competition, 'id' | 'phase'>

export type RegistrationStatus = 'active' | 'withdrawn'

/** app/schemas/registration.py, LifterBrief: suženi natjecatelj unutar prijave */
export interface LifterBrief {
  first_name: string
  last_name: string
}

/** app/schemas/registration.py, RegistrationResponse */
export interface Registration {
  id: number
  lifter_id: number
  competition_id: number
  category: string // težinska kategorija IPF-a, npr. "83" ili "84+"
  total: number // prijavljeni total u kilogramima
  status: RegistrationStatus
  registered_at: string // trenutak upisa, daje ga baza
  lifter: LifterBrief
}

/** Tijelo za POST /competitions/{id}/registrations (RegistrationCreate) */
export interface RegistrationInput {
  lifter_id: number
  category: string
  total: number
}

/** Polje koje nije prošlo provjeru sheme; dolazi uz code "validation_error" */
export interface FieldError {
  field: string // npr. "birth_date" ili "query.limit"
  message: string
}

/** Tijelo svakog odgovora s pogreškom (app/core/errors.py) */
export interface ErrorBody {
  code: string // stalan, za program: "deadline_passed", "not_found"...
  message: string // za čovjeka, smije se mijenjati
  errors?: FieldError[] // samo uz "validation_error"
}
