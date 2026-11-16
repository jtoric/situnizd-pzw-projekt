/** Natjecanja (api/app/routers/competitions.py): čitati smije svaki prijavljeni korisnik. */
import { request } from './http'
import type { Competition, CompetitionInput } from './types'

// Adrese popisa završavaju kosom crtom, kao rute na backendu. Bez nje backend odgovara
// preusmjerenjem 307 na apsolutnu adresu, koja iza posrednika (Vite, nginx) vodi na krivo mjesto.

/** GET /competitions/; natjecanja je malo, pa jedan zahtjev s najvećim dopuštenim limitom dohvaća sva. */
export function fetchCompetitions(): Promise<Competition[]> {
  return request('GET', '/competitions/', { query: { limit: 100 } })
}

/** GET /competitions/{id}; nepostojeće natjecanje daje ApiError 404 (code "not_found"). */
export function fetchCompetition(id: number): Promise<Competition> {
  return request('GET', `/competitions/${id}`)
}

/** POST /competitions/, samo organizator; rokovi bez oznake zone daju ApiError 422. */
export function createCompetition(input: CompetitionInput): Promise<Competition> {
  return request('POST', '/competitions/', { body: input })
}

/** PATCH; izmjena koja bi poremetila poredak rokova daje ApiError 400 (code "invalid_deadlines"). */
export function updateCompetition(
  id: number,
  changes: Partial<CompetitionInput>,
): Promise<Competition> {
  return request('PATCH', `/competitions/${id}`, { body: changes })
}
