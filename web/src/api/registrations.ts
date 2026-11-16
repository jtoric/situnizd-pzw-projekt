/**
 * Prijave na natjecanje (api/app/routers/registrations.py). Isti zahtjev organizatoru vraća sve
 * prijave, a klubu samo prijave njegovih natjecatelja; razliku provodi poslužitelj.
 */
import { request } from './http'
import type { Registration, RegistrationInput, RegistrationStatus } from './types'

export interface RegistrationQuery {
  status?: RegistrationStatus // bez vrijednosti: sve prijave
  limit?: number // zadano 20, najviše 100
  offset?: number
}

export function fetchRegistrations(
  compId: number,
  query: RegistrationQuery = {},
): Promise<Registration[]> {
  return request('GET', `/competitions/${compId}/registrations/`, { query: { ...query } })
}

/** POST; ponovljena prijava istog natjecatelja daje ApiError 409 (code "duplicate"). */
export function createRegistration(compId: number, input: RegistrationInput): Promise<Registration> {
  return request('POST', `/competitions/${compId}/registrations/`, { body: input })
}

/** Odjava je prijelaz stanja s vlastitom adresom, a ne PATCH polja status. */
export function withdrawRegistration(compId: number, regId: number): Promise<Registration> {
  return request('POST', `/competitions/${compId}/registrations/${regId}/withdraw`)
}

export function reactivateRegistration(compId: number, regId: number): Promise<Registration> {
  return request('POST', `/competitions/${compId}/registrations/${regId}/reactivate`)
}
