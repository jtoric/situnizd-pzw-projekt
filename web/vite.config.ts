import { fileURLToPath, URL } from 'node:url'

import vue from '@vitejs/plugin-vue'
import { defineConfig } from 'vite'

// Backend pokrenut naredbom uvicorn app.main:app (README.md, Pokretanje)
const BACKEND = 'http://127.0.0.1:8000'

// Zahtjev na /api/competitions/ razvojni poslužitelj prosljeđuje backendu kao /competitions/.
// Preglednik tako sve zahtjeve šalje istom izvoru s kojeg je došla stranica, pa pravilo istoga
// izvora ne smeta i backend ne treba dopuštenje CORS. U produkciji istu ulogu ima nginx.
const proxy = {
  '/api': { target: BACKEND, rewrite: (path: string) => path.replace(/^\/api/, '') },
}

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      // import '@/api/types' umjesto '../../api/types', neovisno o dubini datoteke
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  // 127.0.0.1, a ne localhost: na Windowsu localhost može biti samo IPv6 adresa ::1
  server: { host: '127.0.0.1', port: 5173, strictPort: true, proxy },
  preview: { host: '127.0.0.1', port: 4173, strictPort: true, proxy },
})
