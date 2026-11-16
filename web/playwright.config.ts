/**
 * Testovi kroz pravi preglednik (e2e/): cijela aplikacija, od obrasca do baze.
 *
 * Lokalno: backend i baza rade kao u README.md (Pokretanje), s početnim podatcima
 * (python -m app.seed); razvojni poslužitelj Playwright pokreće sam ako već ne radi.
 * Uz E2E_URL testovi idu na tu adresu, npr. na aplikaciju u Dockeru u CI-ju.
 */
import { defineConfig, devices } from '@playwright/test'

const BASE_URL = process.env.E2E_URL ?? 'http://127.0.0.1:5173'

export default defineConfig({
  testDir: 'e2e',
  // Test koji ponekad padne ne ponavlja se, nego popravlja: ponavljanje bi skrilo nestabilnost
  retries: 0,
  reporter: process.env.CI ? [['list'], ['html', { open: 'never' }]] : 'list',
  use: {
    baseURL: BASE_URL,
    locale: 'hr-HR',
    timezoneId: 'Europe/Zagreb',
    // Zapis cijelog tijeka (snimke, mreža, konzola) samo za test koji je pao
    trace: 'retain-on-failure',
  },
  projects: [
    { name: 'računalo', use: { ...devices['Desktop Chrome'] } },
    { name: 'mobitel', use: { ...devices['Pixel 7'] } },
  ],
  webServer: process.env.E2E_URL
    ? undefined
    : { command: 'npm run dev', url: BASE_URL, reuseExistingServer: true },
})
