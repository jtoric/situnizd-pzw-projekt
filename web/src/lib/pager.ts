/**
 * Popis po stranicama nad API-jem koji prima limit i offset, a ne vraća ukupan broj zapisa.
 *
 * Stranica se traži s jednim zapisom više od veličine stranice. Ako taj zapis stigne, postoji
 * sljedeća stranica; prikazuje se samo prvih size. Bez toga bi se kraj popisa prepoznao tek po
 * kraćem odgovoru, a popis s točno 20 zapisa nudio bi prijelaz na praznu stranicu.
 */

export const PAGE_SIZE = 20

/** Broj stranice iz adrese (?stranica=2); sve što nije cijeli broj od 1 naviše daje 1. */
export function pageFromQuery(value: unknown): number {
  const page = Number(typeof value === 'string' ? value : NaN)
  return Number.isInteger(page) && page >= 1 ? page : 1
}

/** Parametri zahtjeva za stranicu: zapis više od veličine, od početka te stranice. */
export function pageRequest(page: number, size: number = PAGE_SIZE) {
  return { limit: size + 1, offset: (page - 1) * size }
}

/** Zapisi za prikaz i postoji li sljedeća stranica. */
export function splitPage<T>(items: T[], size: number = PAGE_SIZE) {
  return { rows: items.slice(0, size), hasNext: items.length > size }
}
