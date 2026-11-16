// HTTP sloj bez poslužitelja: fetch i localStorage zamijenjeni su lažnima, pa test vidi svaki
// poslani zahtjev i određuje odgovor na njega.
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { ApiError, request, setSessionLostHandler } from '../http'
import { getAccessToken, saveTokens } from '../tokens'

// Lažni localStorage: Node ga nema, a tokeni se čitaju iz njega
function memoryStorage() {
  const data = new Map<string, string>()
  return {
    getItem: (key: string) => data.get(key) ?? null,
    setItem: (key: string, value: string) => void data.set(key, value),
    removeItem: (key: string) => void data.delete(key),
  }
}

const json = (status: number, body: unknown) =>
  new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } })

// Poslužitelj prihvaća samo token "novi"; na /auth/refresh vraća par s njim
function fakeServer() {
  return vi.fn(async (url: string, init: RequestInit) => {
    if (url.endsWith('/auth/refresh')) {
      const body = JSON.parse(String(init.body))
      if (body.refresh_token !== 'obnova') return json(401, { code: 'invalid_credentials', message: 'Neispravan refresh token' })
      return json(200, { access_token: 'novi', refresh_token: 'obnova', token_type: 'bearer' })
    }
    const auth = (init.headers as Record<string, string>).Authorization
    if (auth !== 'Bearer novi') return json(401, { code: 'token_expired', message: 'Token je istekao' })
    return json(200, { url })
  })
}

let server: ReturnType<typeof fakeServer>

beforeEach(() => {
  vi.stubGlobal('localStorage', memoryStorage())
  server = fakeServer()
  vi.stubGlobal('fetch', server)
})

afterEach(() => {
  vi.unstubAllGlobals()
})

const refreshCalls = () => server.mock.calls.filter(([url]) => String(url).endsWith('/auth/refresh'))

describe('request', () => {
  it('na 401 obnavlja token i ponavlja isti zahtjev', async () => {
    saveTokens({ access_token: 'stari', refresh_token: 'obnova', token_type: 'bearer' })
    await expect(request('GET', '/auth/me')).resolves.toEqual({ url: '/api/auth/me' })
    expect(refreshCalls()).toHaveLength(1)
    expect(getAccessToken()).toBe('novi')
  })

  it('tri istodobna odgovora 401 pokreću jednu obnovu', async () => {
    saveTokens({ access_token: 'stari', refresh_token: 'obnova', token_type: 'bearer' })
    await Promise.all([
      request('GET', '/competitions/'),
      request('GET', '/auth/me'),
      request('GET', '/clubs/'),
    ])
    expect(refreshCalls()).toHaveLength(1)
  })

  it('kad ni obnova ne uspije, briše tokene i javlja da je prijava izgubljena', async () => {
    saveTokens({ access_token: 'stari', refresh_token: 'pokvaren', token_type: 'bearer' })
    const lost = vi.fn()
    setSessionLostHandler(lost)
    const error = await request('GET', '/auth/me').catch((e: unknown) => e)
    expect(error).toBeInstanceOf(ApiError)
    expect((error as ApiError).status).toBe(401)
    expect(getAccessToken()).toBeNull()
    expect(lost).toHaveBeenCalledOnce()
  })

  it('pogrešku s tijelom {code, message} pretvara u ApiError s poljima', async () => {
    server.mockResolvedValueOnce(
      json(422, {
        code: 'validation_error',
        message: 'Neispravni podatci u zahtjevu',
        errors: [{ field: 'birth_date', message: 'Datum rođenja mora biti u prošlosti' }],
      }),
    )
    const error = (await request('POST', '/clubs/1/lifters/', { body: {}, auth: false }).catch((e: unknown) => e)) as ApiError
    expect(error.code).toBe('validation_error')
    expect(error.fieldErrors).toEqual([{ field: 'birth_date', message: 'Datum rođenja mora biti u prošlosti' }])
  })

  it('odgovor koji nije JSON dobiva poruku po statusu', async () => {
    server.mockResolvedValueOnce(new Response('<html>Bad Gateway</html>', { status: 502 }))
    const error = (await request('GET', '/health', { auth: false }).catch((e: unknown) => e)) as ApiError
    expect(error.status).toBe(502)
    expect(error.message).toBe('Poslužitelj trenutno ne odgovara. Pokušajte ponovno za minutu.')
  })

  it('bez odgovora baca ApiError sa statusom 0', async () => {
    server.mockRejectedValueOnce(new TypeError('Failed to fetch'))
    const error = (await request('GET', '/health', { auth: false }).catch((e: unknown) => e)) as ApiError
    expect(error.status).toBe(0)
    expect(error.code).toBe('network_error')
  })
})
