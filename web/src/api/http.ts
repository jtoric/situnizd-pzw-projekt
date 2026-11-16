/**
 * Jedino mjesto na kojem aplikacija šalje zahtjeve backendu.
 *
 * Ovdje se jednom opisuje ono što je isto u svakom pozivu: adresa API-ja, zaglavlja, pretvorba
 * tijela u JSON i natrag, token uz zahtjev, obnova isteklog tokena i pretvorba neuspjelog
 * odgovora u ApiError. Pogledi i komponente ne zovu fetch, nego funkcije iz api/<resurs>.ts.
 *
 * Smjer poziva je jedan: views i components -> stores ili api/<resurs>.ts -> api/http.ts.
 * Ovaj modul ne zna za Vue, Piniju ni router; kad prijava propadne, javlja to funkcijom koju
 * mu je predao main.ts (setSessionLostHandler).
 */
import { buildQuery, type QueryValue } from '@/lib/query'

import { clearTokens, getAccessToken, getRefreshToken, saveTokens } from './tokens'
import type { ErrorBody, FieldError, TokenPair } from './types'

// Relativna adresa: u razvoju zahtjev prosljeđuje Vite (vite.config.ts), u produkciji nginx.
// Stranica i API tako dijele izvor. Kad je API na drugoj adresi, zadaje se pri izgradnji
// varijablom VITE_API_URL, a backend tada mora dopustiti taj izvor (CORS).
export const API_BASE: string = import.meta.env.VITE_API_URL ?? '/api'

/**
 * Neuspio zahtjev. message je spreman za prikaz, code je stalan i po njemu se grana obrada
 * ("deadline_passed", "duplicate"), a fieldErrors nosi polja koja nisu prošla provjeru (422).
 * status 0 znači da odgovora nije bilo.
 */
export class ApiError extends Error {
  readonly status: number
  readonly code: string
  readonly fieldErrors: FieldError[]

  constructor(status: number, body: ErrorBody) {
    super(body.message)
    this.name = 'ApiError'
    this.status = status
    this.code = body.code
    this.fieldErrors = body.errors ?? []
  }
}

type Method = 'GET' | 'POST' | 'PATCH' | 'DELETE'

interface RequestOptions {
  /** tijelo zahtjeva; šalje se kao JSON */
  body?: unknown
  /** parametri upita; prazne vrijednosti se ne šalju (lib/query.ts) */
  query?: Record<string, QueryValue>
  /** false za prijavu i obnovu: zahtjev ne nosi token, a 401 ne pokreće obnovu */
  auth?: boolean
}

let onSessionLost: () => void = () => {}

/** main.ts ovdje predaje što učiniti kad ni obnova tokena ne uspije: odjaviti i otvoriti prijavu. */
export function setSessionLostHandler(handler: () => void) {
  onSessionLost = handler
}

async function send(method: Method, path: string, options: RequestOptions): Promise<Response> {
  const headers: Record<string, string> = { Accept: 'application/json' }
  if (options.body !== undefined) headers['Content-Type'] = 'application/json'
  const token = options.auth === false ? null : getAccessToken()
  if (token) headers.Authorization = `Bearer ${token}`

  try {
    return await fetch(`${API_BASE}${path}${buildQuery(options.query ?? {})}`, {
      method,
      headers,
      body: options.body === undefined ? undefined : JSON.stringify(options.body),
    })
  } catch {
    // fetch odbija samo kad odgovora nema: poslužitelj ne radi ili veze nema
    throw new ApiError(0, {
      code: 'network_error',
      message: 'Poslužitelj nije dostupan. Provjerite vezu i pokušajte ponovno.',
    })
  }
}

// Tijelo odgovora s pogreškom ima oblik {code, message} (api/app/core/errors.py). Odgovor koji
// nije JSON, npr. stranica posrednika kad backend ne radi, dobiva poruku po statusu.
async function toApiError(res: Response): Promise<ApiError> {
  try {
    const body = (await res.json()) as Partial<ErrorBody>
    if (typeof body.code === 'string' && typeof body.message === 'string') {
      return new ApiError(res.status, body as ErrorBody)
    }
  } catch {
    // tijelo nije JSON
  }
  const message =
    res.status >= 502 && res.status <= 504
      ? 'Poslužitelj trenutno ne odgovara. Pokušajte ponovno za minutu.'
      : `Pogreška poslužitelja (HTTP ${res.status}).`
  return new ApiError(res.status, { code: 'http_error', message })
}

// Obnova koja je u tijeku. Kad više zahtjeva u istom trenutku dobije 401, obnovu pokreće prvi,
// a ostali čekaju njezin ishod. Bez toga bi svaki poslao svoj POST /auth/refresh, a uz
// poslužitelj koji pri obnovi poništava stari refresh token svi osim prvoga bi pali.
let refreshing: Promise<boolean> | null = null

function refreshTokens(): Promise<boolean> {
  refreshing ??= (async () => {
    const refreshToken = getRefreshToken()
    if (!refreshToken) return false
    try {
      const res = await send('POST', '/auth/refresh', {
        body: { refresh_token: refreshToken },
        auth: false,
      })
      if (!res.ok) return false
      saveTokens((await res.json()) as TokenPair)
      return true
    } catch {
      return false
    }
  })().finally(() => {
    refreshing = null
  })
  return refreshing
}

/**
 * Šalje zahtjev i vraća tijelo odgovora kao T; za 204 vraća undefined.
 *
 * Na 401 jednom pokušava obnoviti token i ponoviti isti zahtjev. Ako ni to ne uspije, briše
 * tokene i javlja da je prijava izgubljena. Svaki drugi neuspjeh baca ApiError.
 */
export async function request<T>(
  method: Method,
  path: string,
  options: RequestOptions = {},
): Promise<T> {
  let res = await send(method, path, options)

  if (res.status === 401 && options.auth !== false) {
    if (await refreshTokens()) res = await send(method, path, options)
    // I nakon obnove 401: račun je deaktiviran ili tokeni više ne vrijede
    if (res.status === 401) {
      clearTokens()
      onSessionLost()
    }
  }

  if (!res.ok) throw await toApiError(res)
  if (res.status === 204) return undefined as T
  return (await res.json()) as T
}
