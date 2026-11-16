/**
 * Pretraga i razvrstavanje popisa prijava u pregledniku.
 *
 * Obična usporedba nizova (a < b) gleda brojčane vrijednosti znakova, pa Č, Ć, Đ, Š i Ž stoje
 * iza svih slova bez dijakritika ("Čop" iza "Dude"). Intl.Collator uspoređuje po pravilima
 * hrvatskog jezika: C, Č, Ć, D, Dž, Đ...
 */
import type { Registration } from '@/api/types'

const collator = new Intl.Collator('hr', { sensitivity: 'base' })

/** Usporedba teksta po hrvatskoj abecedi, bez razlike između malih i velikih slova. */
export const compareText = (a: string, b: string): number => collator.compare(a, b)

// "č" -> "c": NFD rastavi slovo na osnovno i dijakritički znak, koji se zatim ukloni. Đ se tako
// ne rastavlja (zasebno je slovo), pa se zamjenjuje izričito.
function fold(text: string): string {
  return text
    .normalize('NFD')
    .replace(/\p{M}/gu, '')
    .replace(/đ/gi, 'd')
    .toLowerCase()
}

/** Sadrži li tekst upit, bez obzira na velika slova i dijakritike: "colak" nalazi "Čolak". */
export const matchesQuery = (text: string, query: string): boolean =>
  fold(text).includes(fold(query.trim()))

export type SortKey = 'name' | 'category' | 'total'
export type SortDir = 'asc' | 'desc'

// Kategorija "120+" je otvorena i ide iza "120"; ostale se uspoređuju kao brojevi
function categoryValue(category: string): number {
  const value = Number.parseFloat(category)
  return category.endsWith('+') ? value + 0.5 : value
}

const COMPARE: Record<SortKey, (a: Registration, b: Registration) => number> = {
  name: (a, b) =>
    compareText(a.lifter.last_name, b.lifter.last_name) ||
    compareText(a.lifter.first_name, b.lifter.first_name),
  category: (a, b) => categoryValue(a.category) - categoryValue(b.category),
  total: (a, b) => a.total - b.total,
}

/** Nova, razvrstana kopija; ulazni popis ostaje kakav jest, jer sort() mijenja polje nad kojim se zove. */
export function sortRegistrations(rows: Registration[], key: SortKey, dir: SortDir): Registration[] {
  const sign = dir === 'asc' ? 1 : -1
  return [...rows].sort((a, b) => sign * COMPARE[key](a, b))
}
