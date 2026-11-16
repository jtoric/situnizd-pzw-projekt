/**
 * Povratak nakon prijave. Provjera prije navigacije neprijavljenog korisnika šalje na
 * /prijava?redirect=<adresa koju je tražio>, a nakon prijave on se vraća na tu adresu.
 */

/**
 * Adresa iz parametra redirect, ako je unutarnja putanja aplikacije; inače "/". Parametar je u
 * adresi, pa ga može postaviti bilo tko, i to je ulaz kojemu se ne vjeruje. Aplikacija nakon
 * prijave vodi samo na svoje stranice, bez obzira na to što bi s tuđom adresom učinio router.
 */
export function safeRedirect(value: unknown): string {
  if (typeof value !== 'string') return '/'
  // "//host" i "/\host" preglednik čita kao adresu drugog domaćina
  if (!value.startsWith('/') || value.startsWith('//') || value.startsWith('/\\')) return '/'
  return value
}
