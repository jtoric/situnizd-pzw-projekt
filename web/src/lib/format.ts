/**
 * Prikaz datuma i oznaka iz API-ja na hrvatskom.
 *
 * Datum bez vremena ("2027-03-14") čita se kao tekst, a ne kroz new Date: new Date("2027-03-14")
 * je ponoć u UTC-u, pa bi preglednik zapadno od Greenwicha prikazao dan ranije. Trenutak s
 * oznakom zone (rok prijave) prikazuje se u zoni Europe/Zagreb, gdje rokove postavlja organizator.
 */
import type { Gender, Phase, RegistrationStatus } from '@/api/types'

/** "2027-03-14" -> "14. 3. 2027."; tekst koji nije datum vraća nepromijenjen. */
export function formatDate(value: string): string {
  const match = /^(\d{4})-(\d{2})-(\d{2})/.exec(value)
  if (!match) return value
  const [, year, month, day] = match
  return `${Number(day)}. ${Number(month)}. ${year}.`
}

const DATE_TIME = new Intl.DateTimeFormat('hr-HR', {
  timeZone: 'Europe/Zagreb',
  day: 'numeric',
  month: 'numeric',
  year: 'numeric',
  hour: '2-digit',
  minute: '2-digit',
  hourCycle: 'h23',
})

/** "2027-02-14T22:59:00Z" -> "14. 2. 2027. u 23:59" (zagrebačko vrijeme). */
export function formatDateTime(value: string): string {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  const parts = Object.fromEntries(DATE_TIME.formatToParts(date).map((p) => [p.type, p.value]))
  return `${Number(parts.day)}. ${Number(parts.month)}. ${parts.year}. u ${parts.hour}:${parts.minute}`
}

export const GENDER_LABELS: Record<Gender, string> = { M: 'muški', F: 'ženski' }

export const PHASE_LABELS: Record<Phase, string> = {
  open: 'prijave otvorene',
  prelim_passed: 'samo izmjene i odjave',
  closed: 'prijave zatvorene',
}

export const STATUS_LABELS: Record<RegistrationStatus, string> = {
  active: 'aktivna',
  withdrawn: 'odjavljena',
}
