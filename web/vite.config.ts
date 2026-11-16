import { fileURLToPath, URL } from 'node:url'

import vue from '@vitejs/plugin-vue'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      // import '@/api/types' umjesto '../../api/types', neovisno o dubini datoteke
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  // 127.0.0.1, a ne localhost: na Windowsu localhost može biti samo IPv6 adresa ::1
  server: { host: '127.0.0.1', port: 5173, strictPort: true },
})
