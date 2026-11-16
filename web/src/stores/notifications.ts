/**
 * Kratke obavijesti na vrhu zaslona: potvrda uspjele radnje i pogreška koju nijedan prikaz nije
 * obradio sam. Prikazuje ih NotificationList.vue u App.vue, pa ih svaka komponenta može dodati.
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'

export type NoticeKind = 'success' | 'error'

export interface Notice {
  id: number
  kind: NoticeKind
  text: string
}

// Pogreška ostaje dulje, jer se čita pažljivije; obje se mogu zatvoriti i ranije
const DURATION_MS: Record<NoticeKind, number> = { success: 5000, error: 10000 }

export const useNotificationsStore = defineStore('notifications', () => {
  const items = ref<Notice[]>([])
  let nextId = 1

  function dismiss(id: number) {
    items.value = items.value.filter((n) => n.id !== id)
  }

  function push(kind: NoticeKind, text: string) {
    // Ista poruka dvaput zaredom (npr. dva zahtjeva koja padnu zbog iste mreže) prikazuje se jednom
    if (items.value.some((n) => n.kind === kind && n.text === text)) return
    const id = nextId++
    items.value.push({ id, kind, text })
    window.setTimeout(() => dismiss(id), DURATION_MS[kind])
  }

  return {
    items,
    dismiss,
    success: (text: string) => push('success', text),
    error: (text: string) => push('error', text),
  }
})
