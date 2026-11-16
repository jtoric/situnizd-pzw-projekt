/** Natjecatelji jednog kluba (api/app/routers/lifters.py); adresa nosi oznaku kluba. */
import { request } from './http'
import type { Lifter, LifterInput } from './types'

/** GET /clubs/{clubId}/lifters/; najviše 100, što je za jedan klub dovoljno. */
export function fetchLifters(clubId: number): Promise<Lifter[]> {
  return request('GET', `/clubs/${clubId}/lifters/`, { query: { limit: 100 } })
}

export function fetchLifter(clubId: number, lifterId: number): Promise<Lifter> {
  return request('GET', `/clubs/${clubId}/lifters/${lifterId}`)
}

/** POST; neispravno tijelo daje ApiError 422 s popisom polja (fieldErrors). */
export function createLifter(clubId: number, input: LifterInput): Promise<Lifter> {
  return request('POST', `/clubs/${clubId}/lifters/`, { body: input })
}

/** PATCH šalje samo polja koja se mijenjaju; izostalo polje ostaje kakvo je bilo. */
export function updateLifter(
  clubId: number,
  lifterId: number,
  changes: Partial<LifterInput>,
): Promise<Lifter> {
  return request('PATCH', `/clubs/${clubId}/lifters/${lifterId}`, { body: changes })
}

/** DELETE; natjecatelj s prijavama se ne briše (ApiError 409, code "has_registrations"). */
export function deleteLifter(clubId: number, lifterId: number): Promise<void> {
  return request('DELETE', `/clubs/${clubId}/lifters/${lifterId}`)
}
