/** Klubovi (api/app/routers/clubs.py): organizator vidi sve, klub samo sebe. */
import { request } from './http'
import type { Club } from './types'

/** Tijelo za POST: klub i, u istoj transakciji, račun kojim se klub prijavljuje (ClubCreate). */
export interface ClubInput {
  name: string
  city: string
  username: string
  password: string // najmanje 8 znakova
}

export function fetchClubs(): Promise<Club[]> {
  return request('GET', '/clubs/', { query: { limit: 100 } })
}

/** POST /clubs/, samo organizator; zauzeto korisničko ime daje ApiError 409 (code "duplicate"). */
export function createClub(input: ClubInput): Promise<Club> {
  return request('POST', '/clubs/', { body: input })
}
