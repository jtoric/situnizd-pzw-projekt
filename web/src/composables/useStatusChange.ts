/**
 * Odjava i povratak prijave, zajednički popisu kluba i tablici organizatora.
 *
 * Poslužitelj ponovljeni prijelaz odbija (already_withdrawn, already_active), jer je radnja već
 * provedena: dvostruki klik ili druga kartica. Za korisnika to nije pogreška, nego znak da
 * prikazano stanje nije najnovije, pa se javlja kao obavijest i popis se osvježava.
 */
import { ApiError } from '@/api/http'
import { reactivateRegistration, withdrawRegistration } from '@/api/registrations'
import type { Registration } from '@/api/types'
import { useNotificationsStore } from '@/stores/notifications'

export function useStatusChange(options: {
  compId: () => number
  /** poslužitelj je vratio promijenjenu prijavu */
  onChanged: (registration: Registration) => void
  /** prikazano stanje nije najnovije */
  onStale: () => void
}) {
  const notifications = useNotificationsStore()

  async function changeStatus(registration: Registration) {
    const withdrawing = registration.status === 'active'
    try {
      const updated = withdrawing
        ? await withdrawRegistration(options.compId(), registration.id)
        : await reactivateRegistration(options.compId(), registration.id)
      options.onChanged(updated)
      notifications.success(withdrawing ? 'Prijava je odjavljena.' : 'Prijava je ponovno aktivna.')
    } catch (e) {
      if (e instanceof ApiError && (e.code === 'already_withdrawn' || e.code === 'already_active')) {
        notifications.success(e.message)
        options.onStale()
        return
      }
      // Rok je istekao dok je stranica bila otvorena: razdoblje na zaslonu je zastarjelo
      if (e instanceof ApiError && e.code === 'deadline_passed') options.onStale()
      throw e
    }
  }

  return { changeStatus }
}
