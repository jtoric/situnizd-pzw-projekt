/**
 * Rok kao trenutak: pretvorba između polja datetime-local i vrijednosti s oznakom zone.
 *
 * Polje <input type="datetime-local"> daje "2027-02-14T23:59", bez zone. Poslužitelj takvu
 * vrijednost odbija (AwareDatetime, 422), jer ne određuje trenutak: 23:59 u Zadru i u Londonu
 * nisu isti trenutak. Rokove postavlja organizator po zagrebačkom vremenu, pa se pomak računa za
 * zonu Europe/Zagreb, a ne za zonu preglednika, koja kod organizatora na putu može biti druga.
 * Pomak nije stalan: zimi je +01:00, ljeti +02:00.
 */

export const TIME_ZONE = 'Europe/Zagreb'

// Pomak zone u minutama za zadani trenutak, npr. 60 za "GMT+01:00"
function offsetMinutes(utcMs: number, timeZone: string): number {
  const name = new Intl.DateTimeFormat('en-US', { timeZone, timeZoneName: 'longOffset' })
    .formatToParts(new Date(utcMs))
    .find((p) => p.type === 'timeZoneName')?.value
  const match = /GMT([+-])(\d{2}):(\d{2})/.exec(name ?? '')
  if (!match) return 0 // "GMT" bez pomaka
  const minutes = Number(match[2]) * 60 + Number(match[3])
  return match[1] === '-' ? -minutes : minutes
}

const pad = (n: number) => String(n).padStart(2, '0')

/**
 * "2027-02-14T23:59" (lokalno vrijeme zone) -> "2027-02-14T23:59:00+01:00".
 * Vraća null za vrijednost koja nije u obliku polja datetime-local.
 */
export function fromLocalInput(value: string, timeZone: string = TIME_ZONE): string | null {
  const match = /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})$/.exec(value)
  if (!match) return null
  const [, y, mo, d, h, mi] = match.map(Number) as [number, number, number, number, number, number]
  // Prvo se znamenke čitaju kao UTC, pa se oduzme pomak zone. Pomak se računa još jednom za
  // dobiveni trenutak, jer se oko prelaska na ljetno vrijeme dva trenutka razlikuju u pomaku.
  const asUtc = Date.UTC(y, mo - 1, d, h, mi)
  const offset = offsetMinutes(asUtc - offsetMinutes(asUtc, timeZone) * 60_000, timeZone)
  const sign = offset < 0 ? '-' : '+'
  const abs = Math.abs(offset)
  return `${value}:00${sign}${pad(Math.floor(abs / 60))}:${pad(abs % 60)}`
}

/** "2027-02-14T22:59:00Z" -> "2027-02-14T23:59", vrijednost za polje datetime-local u zoni. */
export function toLocalInput(iso: string, timeZone: string = TIME_ZONE): string {
  const date = new Date(iso)
  if (Number.isNaN(date.getTime())) return ''
  const parts = Object.fromEntries(
    new Intl.DateTimeFormat('en-CA', {
      timeZone,
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      hourCycle: 'h23',
    })
      .formatToParts(date)
      .map((p) => [p.type, p.value]),
  )
  return `${parts.year}-${parts.month}-${parts.day}T${parts.hour}:${parts.minute}`
}
