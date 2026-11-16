/**
 * Popis ruta: koja adresa prikazuje koji pogled.
 *
 * Adrese stranica su na hrvatskom (/natjecanja), jer ih korisnik vidi i dijeli. Adrese API-ja
 * (/competitions) su drugi popis i ne moraju im odgovarati: ova adresa imenuje prikaz, a ona
 * podatke. Na rutu se u kodu upućuje imenom (name), pa promjena adrese ne traži izmjenu
 * poveznica.
 */
import { nextTick } from 'vue'
import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'

import type { Role } from '@/api/types'
import { useAuthStore } from '@/stores/auth'
import CompetitionsView from '@/views/CompetitionsView.vue'
import NotFoundView from '@/views/NotFoundView.vue'

const APP_NAME = 'Prijave na natjecanja'

declare module 'vue-router' {
  interface RouteMeta {
    /** naslov kartice preglednika, uz ime aplikacije */
    title?: string
    /** ruta se otvara i bez prijave */
    public?: boolean
    /** ruta je samo za tu ulogu; dijete nasljeđuje vrijednost roditelja */
    role?: Role
  }
}

const routes: RouteRecordRaw[] = [
  { path: '/', redirect: { name: 'competitions' } },
  {
    path: '/prijava',
    name: 'login',
    component: () => import('@/views/LoginView.vue'),
    meta: { title: 'Prijava', public: true },
  },
  // Početni prikaz je u datoteci koja se preuzima pri pokretanju; ostali se preuzimaju tek pri
  // prvom odlasku na rutu (() => import(...)), pa prvo učitavanje ne nosi kod koji možda ne treba
  {
    path: '/natjecanja',
    name: 'competitions',
    component: CompetitionsView,
    meta: { title: 'Natjecanja' },
  },
  {
    // (\\d+): ruta prihvaća samo znamenke, pa /natjecanja/abc ide na NotFoundView
    path: '/natjecanja/:compId(\\d+)',
    name: 'competition',
    component: () => import('@/views/CompetitionView.vue'),
    meta: { title: 'Natjecanje' },
  },
  {
    path: '/natjecatelji',
    name: 'lifters',
    component: () => import('@/views/LiftersView.vue'),
    // Natjecatelji pripadaju klubu; organizator nema svoj klub
    meta: { title: 'Natjecatelji', role: 'club' },
  },
  {
    path: '/natjecatelji/novi',
    name: 'lifter-new',
    component: () => import('@/views/LifterFormView.vue'),
    meta: { title: 'Dodavanje natjecatelja', role: 'club' },
  },
  {
    // Isti pogled kao za novog natjecatelja; parametar odlučuje dodaje li se ili uređuje
    path: '/natjecatelji/:lifterId(\\d+)',
    name: 'lifter-edit',
    component: () => import('@/views/LifterFormView.vue'),
    meta: { title: 'Uređivanje natjecatelja', role: 'club' },
  },
  {
    // Ugniježđene rute dijele okvir AdminLayout; dijete se prikazuje u njegovu RouterView
    path: '/admin',
    component: () => import('@/views/admin/AdminLayout.vue'),
    // meta roditelja vrijedi za svako dijete, pa se uvjet piše jednom
    meta: { role: 'admin' },
    children: [
      { path: '', redirect: { name: 'admin-competitions' } },
      {
        path: 'natjecanja',
        name: 'admin-competitions',
        component: () => import('@/views/admin/AdminCompetitionsView.vue'),
        meta: { title: 'Administracija natjecanja' },
      },
      {
        path: 'klubovi',
        name: 'admin-clubs',
        component: () => import('@/views/admin/AdminClubsView.vue'),
        meta: { title: 'Klubovi' },
      },
    ],
  },
  // Svaka adresa koju nijedna ruta iznad ne prepozna
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: NotFoundView,
    meta: { title: 'Stranica nije pronađena', public: true },
  },
]

const router = createRouter({
  // Adrese bez ljestvice (/natjecanja, a ne /#/natjecanja); poslužitelj zato za svaku
  // nepoznatu adresu mora vratiti index.html (vite to radi sam, nginx po postavci)
  history: createWebHistory(),
  routes,
})

// Provjera prije svake navigacije. Postoji radi korisnika, da ne otvori prikaz čiji bi svaki
// zahtjev poslužitelj odbio; podatke štiti poslužitelj, koji svaki zahtjev provjerava sam.
router.beforeEach(async (to) => {
  const auth = useAuthStore()
  // Nakon osvježavanja stranice korisnik se tek dohvaća; prva navigacija čeka ishod
  await auth.restore()

  if (to.meta.public) {
    // Prijavljeni korisnik na obrascu za prijavu nema što raditi
    if (to.name === 'login' && auth.isLoggedIn) return { name: 'competitions' }
    return true
  }
  if (!auth.isLoggedIn) return { name: 'login', query: { redirect: to.fullPath } }
  if (to.meta.role && to.meta.role !== auth.user?.role) return { name: 'competitions' }
  return true
})

// Jednostranična aplikacija ne učitava novu stranicu, pa preglednik sam ne mijenja naslov kartice
// i ne pomiče fokus. Čitač zaslona bi nakon klika ostao na poveznici koja je nestala sa starim
// prikazom, a korisnik tipkovnice na vrhu stranice. Zato se oboje radi nakon svakog prijelaza.
router.afterEach((to, from, failure) => {
  if (failure) return
  document.title = to.meta.title ? `${to.meta.title} - ${APP_NAME}` : APP_NAME
  // Pri prvom učitavanju fokus ostaje na početku dokumenta, kao na svakoj drugoj stranici
  if (from.matched.length === 0) return
  nextTick(() => document.getElementById('main')?.focus({ preventScroll: true }))
})

export default router
