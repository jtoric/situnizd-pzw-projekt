// Ono što radi nginx (web/nginx.conf), a ne aplikacija: zaglavlja, predmemorija i povratak
// index.html za rute. Razvojni poslužitelj to ne radi isto, pa se testovi izvode samo nad
// izgrađenom aplikacijom (E2E_URL, npr. docker-compose.prod.yml u CI-ju).
import { expect, test } from '@playwright/test'

test.skip(!process.env.E2E_URL, 'samo nad izgrađenom aplikacijom (E2E_URL)')

test('svaki odgovor nosi sigurnosna zaglavlja', async ({ request }) => {
  for (const path of ['/', '/api/health/', '/nepostojeca/datoteka.js']) {
    const res = await request.get(path)
    const headers = res.headers()
    expect(headers['content-security-policy'], path).toContain("default-src 'self'")
    expect(headers['x-content-type-options'], path).toBe('nosniff')
  }
})

test('ruta aplikacije vraća index.html, a ne 404', async ({ request }) => {
  const res = await request.get('/natjecanja/1?stanje=active')
  expect(res.status()).toBe(200)
  expect(await res.text()).toContain('<div id="app">')
  expect(res.headers()['cache-control']).toBe('no-cache')
})

test('datoteke iz /assets/ smiju u predmemoriju, a nepostojeća daje 404', async ({ request }) => {
  const html = await (await request.get('/')).text()
  const script = /\/assets\/index-[^"]+\.js/.exec(html)?.[0]
  expect(script).toBeTruthy()
  const res = await request.get(script!)
  expect(res.headers()['cache-control']).toBe('max-age=31536000')
  expect((await request.get('/assets/nepostojeca.js')).status()).toBe(404)
})

test('opis API-ja nije javan u produkciji', async ({ request }) => {
  expect((await request.get('/api/openapi.json')).status()).toBe(404)
})

test('CSP ne blokira ništa od same aplikacije', async ({ page }) => {
  const errors: string[] = []
  page.on('console', (m) => {
    if (m.type() === 'error') errors.push(m.text())
  })
  await page.goto('/prijava')
  await expect(page.getByRole('heading', { name: 'Prijava' })).toBeVisible()
  expect(errors).toEqual([])
})
