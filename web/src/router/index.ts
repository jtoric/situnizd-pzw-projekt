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

import CompetitionsView from '@/views/CompetitionsView.vue'
import NotFoundView from '@/views/NotFoundView.vue'

const APP_NAME = 'Prijave na natjecanja'

declare module 'vue-router' {
  interface RouteMeta {
    /** naslov kartice preglednika, uz ime aplikacije */
    title?: string
  }
}

const routes: RouteRecordRaw[] = [
  { path: '/', redirect: { name: 'competitions' } },
  {
    path: '/prijava',
    name: 'login',
    component: () => import('@/views/LoginView.vue'),
    meta: { title: 'Prijava' },
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
    meta: { title: 'Natjecatelji' },
  },
  {
    // Ugniježđene rute dijele okvir AdminLayout; dijete se prikazuje u njegovu RouterView
    path: '/admin',
    component: () => import('@/views/admin/AdminLayout.vue'),
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
    meta: { title: 'Stranica nije pronađena' },
  },
]

const router = createRouter({
  // Adrese bez ljestvice (/natjecanja, a ne /#/natjecanja); poslužitelj zato za svaku
  // nepoznatu adresu mora vratiti index.html (vite to radi sam, nginx po postavci)
  history: createWebHistory(),
  routes,
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
