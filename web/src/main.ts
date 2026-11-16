/**
 * Ulazna točka aplikacije: sastavlja dijelove prije nego aplikacija počne raditi.
 *
 * Redoslijed je važan: Pinia mora postojati prije routera, jer provjere prije navigacije
 * (router/index.ts) čitaju pohranu prijave.
 */
import { createPinia } from 'pinia'
import { createApp } from 'vue'

import App from './App.vue'
import router from './router'
import './assets/main.css'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')
