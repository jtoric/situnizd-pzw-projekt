/** Prijava i podatci o prijavljenom korisniku (api/app/routers/auth.py). */
import { request } from './http'
import type { TokenPair, User } from './types'

/** POST /auth/login; neispravni podatci daju ApiError 401 s istom porukom za ime i za lozinku. */
export function login(username: string, password: string): Promise<TokenPair> {
  return request('POST', '/auth/login', { body: { username, password }, auth: false })
}

/** GET /auth/me: tko je vlasnik tokena, prema zapisu u bazi, a ne prema sadržaju tokena. */
export function fetchMe(): Promise<User> {
  return request('GET', '/auth/me')
}
