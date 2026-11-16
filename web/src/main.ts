/**
 * Ulazna točka aplikacije: sastavlja dijelove prije nego aplikacija počne raditi.
 *
 * Redoslijed je važan: Pinia mora postojati prije routera, jer provjera prije navigacije
 * (router/index.ts) čita pohranu prijave.
 */
import { createPinia } from 'pinia'
import { createApp } from 'vue'

import { ApiError, setSessionLostHandler } from './api/http'
import App from './App.vue'
import router from './router'
import { useAuthStore } from './stores/auth'
import { useNotificationsStore } from './stores/notifications'
import './assets/main.css'

const app = createApp(App)
app.use(createPinia())

const auth = useAuthStore()
const notifications = useNotificationsStore()

// Ni obnova tokena nije uspjela (api/http.ts): korisnik se prijavljuje ponovno, a nakon prijave
// vraća se na prikaz na kojem je bio. Za vrijeme pokretanja to rješava provjera prije navigacije.
setSessionLostHandler(() => {
  auth.forget()
  const current = router.currentRoute.value
  if (!auth.ready || current.meta.public) return
  notifications.error('Prijava je istekla. Prijavite se ponovno.')
  router.push({ name: 'login', query: { redirect: current.fullPath } })
})

// Pogreška koju nijedan prikaz nije obradio sam. Bez ovoga bi iznimka u komponenti prekinula
// prikaz, a korisnik ne bi znao zašto. Prikaz hvata samo ono na što reagira posebno (422 uz polja
// obrasca, 409); sve ostalo dolazi ovamo.
function reportError(error: unknown) {
  if (error instanceof ApiError) {
    notifications.error(error.message)
    return
  }
  console.error(error)
  notifications.error('Dogodila se neočekivana pogreška. Osvježite stranicu i pokušajte ponovno.')
}

// Iznimke iz komponenata, izvedenih vrijednosti, promatrača i rukovatelja događajima
app.config.errorHandler = (error) => reportError(error)
// Odbijeno obećanje koje nitko ne čeka, npr. dohvat pokrenut bez await
window.addEventListener('unhandledrejection', (event) => {
  event.preventDefault()
  reportError(event.reason)
})

app.use(router)
app.mount('#app')
