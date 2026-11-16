/**
 * Natjecatelji prijavljenog kluba.
 *
 * Isti popis trebaju dva prikaza: popis natjecatelja (LiftersView) i obrazac prijave na
 * natjecanje (CompetitionView), koji nudi izbor natjecatelja. Zato je u pohrani, a ne u
 * komponenti: natjecatelj dodan na jednom mjestu odmah se vidi na drugom, bez novog dohvata.
 *
 * Pohrana drži i stanje dohvata, da prikaz razlikuje učitavanje, neuspjeh i prazan popis.
 */
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

import { fetchLifters } from '@/api/lifters'
import type { Lifter } from '@/api/types'

import { useAuthStore } from './auth'

export const useLiftersStore = defineStore('lifters', () => {
  const items = ref<Lifter[]>([])
  // Popis je barem jednom stigao; i prazan popis tada je pravi odgovor, a ne početno stanje
  const loaded = ref(false)
  const pending = ref(false)
  const failed = ref(false)

  const byId = computed(() => new Map(items.value.map((l) => [l.id, l])))

  /** Dohvaća popis kluba; prikazani popis ostaje vidljiv dok novi ne stigne, i kad dohvat ne uspije. */
  async function load() {
    const clubId = useAuthStore().clubId
    if (clubId === null) return
    pending.value = true
    failed.value = false
    try {
      items.value = await fetchLifters(clubId)
      loaded.value = true
    } catch (error) {
      failed.value = true
      throw error
    } finally {
      pending.value = false
    }
  }

  /** Dohvaća samo ako popis još nije stigao; prikaz ga zove pri otvaranju. */
  async function ensureLoaded() {
    if (!loaded.value && !pending.value) await load()
  }

  /** Upisuje natjecatelja kojeg je vratio poslužitelj: novog dodaje, postojećeg zamjenjuje. */
  function upsert(lifter: Lifter) {
    const index = items.value.findIndex((l) => l.id === lifter.id)
    if (index === -1) items.value.push(lifter)
    else items.value[index] = lifter
  }

  return { items, loaded, pending, failed, byId, load, ensureLoaded, upsert }
})
