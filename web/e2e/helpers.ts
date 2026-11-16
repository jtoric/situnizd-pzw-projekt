/**
 * Zajedničko testovima kroz preglednik: računi iz početnih podataka, prijava kroz obrazac,
 * priprema podataka izravno preko API-ja i provjera pristupačnosti.
 *
 * Podatke koje test treba (natjecanje, natjecatelj, prijava) test stvara sam, preko API-ja i s
 * jedinstvenim imenom. Tako ne ovisi o redoslijedu ni o tome što su ostavili drugi testovi, a
 * sučelje se provjerava samo ondje gdje je ono predmet testa.
 */
import AxeBuilder from '@axe-core/playwright'
import { expect, type APIRequestContext, type Page } from '@playwright/test'

// Računi iz api/app/seed.py
export const ADMIN = { username: 'admin@plreg.hr', password: 'admin123' }
export const CLUB = { username: 'behemot@plreg.hr', password: 'behemot123' }

type Account = typeof ADMIN

/** Jedinstven nastavak imena, da se zapisi istodobnih i ponovljenih testova ne sudare. */
export const unique = () => `${Date.now()}${Math.floor(Math.random() * 1000)}`

/** Prijava kroz obrazac; završava kad aplikacija otvori popis natjecanja. */
export async function login(page: Page, account: Account) {
  await page.goto('/prijava')
  await page.getByLabel('Korisničko ime').fill(account.username)
  await page.getByLabel('Lozinka').fill(account.password)
  await page.getByRole('button', { name: 'Prijavi se' }).click()
  await expect(page).toHaveURL(/\/natjecanja$/)
}

/** Klijent za pripremu podataka: šalje zahtjeve na /api s tokenom računa. */
export async function apiAs(request: APIRequestContext, account: Account) {
  const res = await request.post('/api/auth/login', { data: account })
  expect(res.ok()).toBe(true)
  const { access_token } = await res.json()
  const headers = { Authorization: `Bearer ${access_token}` }

  async function call(method: 'GET' | 'POST' | 'PATCH', path: string, data?: unknown) {
    const response = await request.fetch(`/api${path}`, { method, headers, data })
    expect(response.ok(), `${method} ${path}: ${await response.text()}`).toBe(true)
    return response.json()
  }
  return call
}

const DAY = 24 * 60 * 60 * 1000
const at = (days: number) => new Date(Date.now() + days * DAY).toISOString()

/** Natjecanje za 60 dana, s rokovima za 20 i 40 dana: razdoblje open. */
export async function createOpenCompetition(request: APIRequestContext) {
  const admin = await apiAs(request, ADMIN)
  const competition = await admin('POST', '/competitions/', {
    name: `E2E kup ${unique()}`,
    location: 'Zadar',
    date: at(60).slice(0, 10),
    prelim_deadline: at(20),
    final_deadline: at(40),
  })
  return {
    competition,
    /** Pomiče preliminarni rok u prošlost: razdoblje prelim_passed. */
    passPrelim: () => admin('PATCH', `/competitions/${competition.id}`, { prelim_deadline: at(-2) }),
    /** Pomiče oba roka u prošlost: razdoblje closed. */
    close: () =>
      admin('PATCH', `/competitions/${competition.id}`, { prelim_deadline: at(-2), final_deadline: at(-1) }),
  }
}

/** Novi natjecatelj kluba CLUB, po želji odmah prijavljen na natjecanje. */
export async function createLifter(request: APIRequestContext, registerTo?: number) {
  const club = await apiAs(request, CLUB)
  const me = await club('GET', '/auth/me')
  const lifter = await club('POST', `/clubs/${me.club_id}/lifters/`, {
    first_name: 'Test',
    last_name: `Natjecatelj${unique()}`,
    birth_date: '2000-01-01',
    gender: 'M',
  })
  if (registerTo !== undefined) {
    await club('POST', `/competitions/${registerTo}/registrations/`, {
      lifter_id: lifter.id,
      category: '83',
      total: 500,
    })
  }
  return lifter as { id: number; first_name: string; last_name: string }
}

/** Nema prekršaja WCAG 2.2 razine A i AA koje axe može otkriti na trenutnom stanju stranice. */
export async function expectAccessible(page: Page) {
  const results = await new AxeBuilder({ page })
    .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa'])
    .analyze()
  expect(results.violations.map((v) => `${v.id}: ${v.help} (${v.nodes.length})`)).toEqual([])
}

/** Stranica nije šira od zaslona: na mobitelu se ne pomiče vodoravno. */
export async function expectNoHorizontalScroll(page: Page) {
  const overflow = await page.evaluate(
    () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
  )
  expect(overflow, 'stranica je šira od zaslona').toBeLessThanOrEqual(0)
}
