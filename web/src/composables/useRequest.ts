/**
 * Dohvat podataka za jedan prikaz, sa stanjem koje prikaz treba: podatci, dohvat u tijeku i
 * pogreška. Isti obrazac ponavlja se u svakom prikazu koji nešto učitava, pa je izdvojen ovamo.
 *
 * Funkcija čije ime počinje s use i koja vraća praćene vrijednosti naziva se composable. Svaki
 * poziv daje vlastite vrijednosti; dijeli se kod, a ne stanje (za dijeljeno stanje su stores/).
 */
import { ref, shallowRef, type Ref } from 'vue'

import { ApiError } from '@/api/http'

export function useRequest<T>(fetcher: () => Promise<T>) {
  // shallowRef: odgovor se zamjenjuje cijeli, pa Vue ne mora pratiti svako polje unutar njega
  const data = shallowRef<T | null>(null) as Ref<T | null>
  const pending = ref(false)
  const error = ref<ApiError | null>(null)

  // Redni broj zadnjeg pokrenutog dohvata. Korisnik koji brzo promijeni filtar pokrene dva
  // dohvata; ako stariji odgovor stigne zadnji, prepisao bi noviji. Zato vrijedi samo zadnji.
  let latest = 0

  /** Pokreće dohvat. Prethodni podatci ostaju vidljivi dok novi ne stignu, i kad dohvat ne uspije. */
  async function run() {
    const call = ++latest
    pending.value = true
    error.value = null
    try {
      const result = await fetcher()
      if (call === latest) data.value = result
    } catch (e) {
      // Pogreška koja nije odgovor poslužitelja je kvar u kodu: ide globalnom rukovatelju
      if (!(e instanceof ApiError)) throw e
      if (call === latest) error.value = e
    } finally {
      if (call === latest) pending.value = false
    }
  }

  return { data, pending, error, run }
}
