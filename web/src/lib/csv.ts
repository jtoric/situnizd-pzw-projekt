/**
 * Popis kao datoteka CSV koju organizator otvara u tabličnom kalkulatoru.
 *
 * - Razdjelnik je točka sa zarezom: Excel s hrvatskim postavkama zarez čita kao decimalni znak
 *   i cijeli bi redak stavio u jedan stupac.
 * - Na početku je oznaka BOM, po kojoj Excel prepoznaje UTF-8; bez nje "Čolak" postaje "ÄŒolak".
 * - Vrijednost s razdjelnikom, navodnikom ili prijelomom retka ide u navodnike (RFC 4180).
 * - Vrijednost koja počinje s =, +, - ili @ kalkulator bi izveo kao formulu. Ime natjecatelja
 *   upisuje klub, pa bi se tako u organizatorov kalkulator mogla podmetnuti formula. Takva
 *   vrijednost dobiva apostrof na početku i ostaje tekst.
 */

export const SEPARATOR = ';'
const BOM = '\uFEFF'

function cell(value: string | number): string {
  let text = String(value)
  if (/^[=+\-@\t\r]/.test(text)) text = `'${text}`
  if (/[";\r\n]/.test(text)) text = `"${text.replaceAll('"', '""')}"`
  return text
}

/** Redci (prvi je zaglavlje) kao tekst CSV-a s oznakom BOM i prijelomom retka CRLF. */
export function toCsv(rows: (string | number)[][]): string {
  return BOM + rows.map((row) => row.map(cell).join(SEPARATOR)).join('\r\n') + '\r\n'
}
