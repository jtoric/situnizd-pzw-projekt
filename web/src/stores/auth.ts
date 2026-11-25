/**
 * Prijavljeni korisnik: tko je, koja mu je uloga i kojem klubu pripada.
 *
 * Te podatke čita navigacija, provjera prije navigacije (router/index.ts) i gotovo svaki popis,
 * pa ne pripadaju nijednoj komponenti nego pohrani koju dijele. Tokeni su u api/tokens.ts;
 * ovdje je samo korisnik kojeg je za njih vratio GET /auth/me.
 */
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

import { fetchMe, login as apiLogin } from '@/api/auth'
import { clearTokens, getAccessToken, getRefreshToken, saveTokens } from '@/api/tokens'
import type { User } from '@/api/types'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  // true kad je restore() završio; do tada se još ne zna je li korisnik prijavljen
  const ready = ref(false)

  const isLoggedIn = computed(() => user.value !== null)
  const isAdmin = computed(() => user.value?.role === 'admin')
  const clubId = computed(() => user.value?.club_id ?? null)

  let restoring: Promise<void> | null = null

  /**
   * Pri pokretanju aplikacije token iz pohrane pretvara u korisnika. Osvježavanje stranice briše
   * sve iz memorije, a token ostaje u localStorage, pa se korisnik dohvaća ponovno. Izvodi se
   * jednom; svaki sljedeći poziv čeka isti ishod.
   */
  function restore(): Promise<void> {
    restoring ??= (async () => {
      if (getAccessToken() || getRefreshToken()) {
        try {
          user.value = await fetchMe()
        } catch {
          // Token ne vrijedi ili poslužitelj ne odgovara: korisnik se prijavljuje ponovno
          user.value = null
        }
      }
      ready.value = true
    })()
    return restoring
  }

  /** Prijava: sprema tokene, pa dohvaća korisnika. Neuspjeh baca ApiError iz api/http.ts. */
  async function login(username: string, password: string) {
    saveTokens(await apiLogin(username, password))
    user.value = await fetchMe()
  }

  /** Zaboravlja korisnika i tokene; poziva se kad poslužitelj više ne prihvaća prijavu. */
  function forget() {
    clearTokens()
    user.value = null
  }

  return { user, ready, isLoggedIn, isAdmin, clubId, restore, login, forget }
})
