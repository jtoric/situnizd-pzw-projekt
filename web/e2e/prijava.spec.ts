import { expect, test } from '@playwright/test'

import { ADMIN, CLUB, expectAccessible, login } from './helpers'

test('kriva lozinka daje poruku i ostavlja korisnika na obrascu', async ({ page }) => {
  await page.goto('/prijava')
  await expectAccessible(page)
  await page.getByLabel('Korisničko ime').fill(CLUB.username)
  await page.getByLabel('Lozinka').fill('kriva-lozinka')
  await page.getByRole('button', { name: 'Prijavi se' }).click()
  await expect(page.getByRole('alert')).toHaveText('Neispravno korisničko ime ili lozinka')
  await expect(page).toHaveURL(/\/prijava$/)
})

test('neprijavljeni korisnik ide na prijavu, a nakon nje na stranicu koju je tražio', async ({ page }) => {
  await page.goto('/natjecatelji')
  await expect(page).toHaveURL(/\/prijava\?redirect=/)
  await page.getByLabel('Korisničko ime').fill(CLUB.username)
  await page.getByLabel('Lozinka').fill(CLUB.password)
  await page.getByRole('button', { name: 'Prijavi se' }).click()
  await expect(page).toHaveURL(/\/natjecatelji$/)
  await expect(page.getByRole('heading', { level: 1 })).toHaveText('Natjecatelji')
})

test('klub koji upiše adresu administracije ostaje na popisu natjecanja', async ({ page }) => {
  await login(page, CLUB)
  await page.goto('/admin/klubovi')
  await expect(page).toHaveURL(/\/natjecanja$/)
})

test('prijava preživi osvježavanje stranice', async ({ page }) => {
  await login(page, ADMIN)
  await page.reload()
  await expect(page).toHaveURL(/\/natjecanja$/)
  await expect(page.getByRole('navigation', { name: 'Glavna navigacija' })).toContainText(ADMIN.username)
})
