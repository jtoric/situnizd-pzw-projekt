// Prijava natjecatelja na natjecanje i radnje koje ovise o razdoblju natjecanja
import { expect, test } from '@playwright/test'

import {
  CLUB,
  createLifter,
  createOpenCompetition,
  expectAccessible,
  expectNoHorizontalScroll,
  login,
} from './helpers'

test('klub prijavljuje natjecatelja i odjavljuje prijavu', async ({ page, request }) => {
  const { competition } = await createOpenCompetition(request)
  const lifter = await createLifter(request)
  const name = `${lifter.last_name}, ${lifter.first_name}`

  await login(page, CLUB)
  await page.goto(`/natjecanja/${competition.id}`)
  await page.getByLabel('Natjecatelj').selectOption({ label: name })
  await page.getByLabel('Kategorija').selectOption('83')
  await page.getByLabel('Prijavljeni total (kg)').fill('520')
  await page.getByRole('button', { name: 'Prijavi natjecatelja' }).click()

  const row = page.getByRole('row').filter({ hasText: name })
  await expect(row).toContainText('aktivna')
  await expectAccessible(page)
  await expectNoHorizontalScroll(page)

  await row.getByRole('button', { name: /Odjavi/ }).click()
  await expect(row).toContainText('odjavljena')
  await expect(row.getByRole('button', { name: /Vrati prijavu/ })).toBeVisible()
})

test('nakon preliminarnog roka nema nove prijave, a odjava je dopuštena', async ({ page, request }) => {
  const { competition, passPrelim } = await createOpenCompetition(request)
  const lifter = await createLifter(request, competition.id)
  await passPrelim()

  await login(page, CLUB)
  await page.goto(`/natjecanja/${competition.id}`)
  await expect(page.getByText('Rok za nove prijave je istekao.')).toBeVisible()
  await expect(page.getByRole('button', { name: 'Prijavi natjecatelja' })).toHaveCount(0)
  const row = page.getByRole('row').filter({ hasText: lifter.last_name })
  await expect(row.getByRole('button', { name: /Odjavi/ })).toBeEnabled()
})

test('nakon konačnog roka radnje su vidljive, ali onemogućene, uz razlog', async ({ page, request }) => {
  const { competition, close } = await createOpenCompetition(request)
  const lifter = await createLifter(request, competition.id)
  await close()

  await login(page, CLUB)
  await page.goto(`/natjecanja/${competition.id}`)
  await expect(page.getByText('Nakon konačnog roka prijave se ne mogu mijenjati.')).toBeVisible()
  const row = page.getByRole('row').filter({ hasText: lifter.last_name })
  await expect(row.getByRole('button', { name: /Odjavi/ })).toBeDisabled()
  await expectAccessible(page)
})

// Stranica je otvorena dok je razdoblje open, a rok prođe prije nego klub pošalje obrazac
test('istekli rok na otvorenoj stranici: poslužitelj odbija, a stranica se usklađuje', async ({ page, request }) => {
  const { competition, passPrelim } = await createOpenCompetition(request)
  const lifter = await createLifter(request)

  await login(page, CLUB)
  await page.goto(`/natjecanja/${competition.id}`)
  await page.getByLabel('Natjecatelj').selectOption({ label: `${lifter.last_name}, ${lifter.first_name}` })
  await page.getByLabel('Kategorija').selectOption('83')
  await passPrelim()
  await page.getByRole('button', { name: 'Prijavi natjecatelja' }).click()

  // Natjecanje se dohvaća ponovno, pa obrazac nestaje i ostaje razlog
  await expect(page.getByText('Rok za nove prijave je istekao.')).toBeVisible()
  await expect(page.getByRole('button', { name: 'Prijavi natjecatelja' })).toHaveCount(0)
})
