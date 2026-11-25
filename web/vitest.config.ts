import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vitest/config'

// Testovi se izvode u zoni zapadno od UTC-a. Oblikovanje datuma i pretvorba rokova
// (lib/format.ts, lib/datetime.ts) moraju dati zagrebački dan i sat bez obzira na zonu računala
// na kojem se izvode; u zoni Europe/Zagreb pogreška koja miješa zone ne bi se vidjela.
// Postavlja se prije pokretanja radnih procesa, koji je nasljeđuju.
process.env.TZ = 'America/Los_Angeles'

export default defineConfig({
  resolve: {
    alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) },
  },
  test: {
    include: ['src/**/__tests__/*.test.ts'],
    // Testirane funkcije ne trebaju DOM; testovi su brži i ne ovise o simulaciji preglednika
    environment: 'node',
  },
})
