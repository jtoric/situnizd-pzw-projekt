/**
 * Provjera obrasca prije slanja.
 *
 * Postoji radi korisnika: pogrešku vidi odmah, uz polje, bez čekanja odgovora. Poslužitelj
 * jednako provjerava sve sam (api/app/schemas/lifter.py), jer zahtjev ne mora doći iz ovog
 * obrasca. Pravila su ista kao u shemi; mijenjati zajedno.
 */
import type { LifterInput } from '@/api/types'

/** Pogreške po imenu polja; prazan objekt znači da je obrazac ispravan. */
export type FieldErrors = Record<string, string>

const NAME_MAX = 80

function checkName(value: string, label: string): string | null {
  const trimmed = value.trim()
  if (trimmed === '') return `${label} je obavezno.`
  if (trimmed.length > NAME_MAX) return `${label} smije imati najviše ${NAME_MAX} znakova.`
  return null
}

/**
 * Provjerava natjecatelja. today je "GGGG-MM-DD" lokalnog dana; zadaje ga pozivatelj, pa je
 * funkcija čista i test ne ovisi o danu kad se pokreće.
 */
export function validateLifter(input: LifterInput, today: string): FieldErrors {
  const errors: FieldErrors = {}
  const first = checkName(input.first_name, 'Ime')
  if (first) errors.first_name = first
  const last = checkName(input.last_name, 'Prezime')
  if (last) errors.last_name = last
  if (!/^\d{4}-\d{2}-\d{2}$/.test(input.birth_date)) {
    errors.birth_date = 'Datum rođenja je obavezan.'
  } else if (input.birth_date >= today) {
    // Tekst "GGGG-MM-DD" uspoređuje se kao datum, jer su znamenke poredane od godine prema danu
    errors.birth_date = 'Datum rođenja mora biti u prošlosti.'
  }
  if (input.gender !== 'M' && input.gender !== 'F') errors.gender = 'Odaberite spol.'
  return errors
}

/** Lokalni dan kao "GGGG-MM-DD"; toISOString() bi dao dan po UTC-u, koji oko ponoći nije isti. */
export function localToday(now: Date = new Date()): string {
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  return `${now.getFullYear()}-${month}-${day}`
}
