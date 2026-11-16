/**
 * Preuzimanje datoteke koju je sastavio preglednik, bez zahtjeva prema poslužitelju.
 *
 * Jedina funkcija u lib/ koja dira DOM, pa nema jedinični test; sadržaj datoteke sastavljaju
 * čiste funkcije (lib/csv.ts) koje ga imaju.
 */

/** Nudi tekst kao datoteku zadanog imena. */
export function downloadText(filename: string, text: string, type: string) {
  const url = URL.createObjectURL(new Blob([text], { type }))
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  link.click()
  // Adresa drži sadržaj u memoriji dok se ne oslobodi; preuzimanje je u tom trenutku već pokrenuto
  URL.revokeObjectURL(url)
}
