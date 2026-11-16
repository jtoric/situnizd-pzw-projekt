/**
 * Parametri upita u adresi zahtjeva.
 *
 * Izostavljen parametar za API znači "bez filtra". Prazan tekst nije isto: ?status= stiže kao
 * prazna vrijednost, ne prolazi provjeru oblika i vraća 422. Zato se prazne vrijednosti ne šalju.
 */

export type QueryValue = string | number | null | undefined

/** "?limit=20&status=active" iz objekta; undefined, null i prazan tekst izostavlja, a bez parametara vraća "". */
export function buildQuery(params: Record<string, QueryValue>): string {
  const search = new URLSearchParams()
  for (const [key, value] of Object.entries(params)) {
    if (value === undefined || value === null || value === '') continue
    search.append(key, String(value))
  }
  const text = search.toString()
  return text ? `?${text}` : ''
}
