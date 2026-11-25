/**
 * Par tokena u pohrani preglednika (localStorage).
 *
 * Tokeni stoje u localStorage, a ne u memoriji, da prijava preživi osvježavanje stranice. Cijena
 * je da ih može pročitati svaka skripta koja se izvede na ovoj stranici, pa aplikacija ne smije
 * izvoditi tuđi kod (Vue tekst iz podataka ispisuje kao tekst; v-html se ne koristi).
 *
 * Ključevi imaju predmetak aplikacije: localStorage pripada izvoru (shema, domaćin i vrata), a
 * na http://127.0.0.1:5173 u razvoju redom rade i drugi projekti.
 */
import type { TokenPair } from './types'

const ACCESS_KEY = 'plreg.access_token'
const REFRESH_KEY = 'plreg.refresh_token'

// Pohrana može baciti iznimku kad je korisnik u pregledniku blokirao podatke stranica;
// prijava tada vrijedi samo do osvježavanja, ali aplikacija radi
function read(key: string): string | null {
  try {
    return localStorage.getItem(key)
  } catch {
    return null
  }
}

function write(key: string, value: string | null) {
  try {
    if (value === null) localStorage.removeItem(key)
    else localStorage.setItem(key, value)
  } catch {
    // vidi read()
  }
}

export const getAccessToken = () => read(ACCESS_KEY)
export const getRefreshToken = () => read(REFRESH_KEY)

/** Sprema par koji su vratili POST /auth/login ili POST /auth/refresh. */
export function saveTokens(pair: TokenPair) {
  write(ACCESS_KEY, pair.access_token)
  write(REFRESH_KEY, pair.refresh_token)
}

/** Briše oba tokena. Izdani token time ne prestaje vrijediti, nego prestaje biti dostupan ovoj stranici. */
export function clearTokens() {
  write(ACCESS_KEY, null)
  write(REFRESH_KEY, null)
}
