// Pohrana natjecatelja bez poslužitelja: modul api/lifters.ts zamijenjen je lažnim, pa test
// određuje što "poslužitelj" vraća i provjerava stanje pohrane, a ne mrežu.
import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { fetchLifters } from '@/api/lifters'
import type { Lifter } from '@/api/types'

import { useAuthStore } from '../auth'
import { useLiftersStore } from '../lifters'

vi.mock('@/api/lifters', () => ({ fetchLifters: vi.fn() }))

const ANA: Lifter = { id: 1, first_name: 'Ana', last_name: 'Horvat', birth_date: '2005-05-02', gender: 'F', club_id: 7 }
const IVAN: Lifter = { id: 2, first_name: 'Ivan', last_name: 'Perić', birth_date: '2004-11-20', gender: 'M', club_id: 7 }

beforeEach(() => {
  // Svaki test dobiva nove, prazne pohrane
  setActivePinia(createPinia())
  vi.mocked(fetchLifters).mockReset()
  useAuthStore().user = { id: 5, username: 'behemot@plreg.hr', role: 'club', club_id: 7, is_active: true }
})

describe('useLiftersStore', () => {
  it('dohvaća natjecatelje kluba prijavljenog korisnika', async () => {
    vi.mocked(fetchLifters).mockResolvedValue([ANA, IVAN])
    const store = useLiftersStore()
    await store.load()
    expect(fetchLifters).toHaveBeenCalledWith(7)
    expect(store.items).toEqual([ANA, IVAN])
    expect(store.loaded).toBe(true)
    expect(store.pending).toBe(false)
  })

  it('prazan odgovor je učitan popis, a ne popis koji još nije stigao', async () => {
    vi.mocked(fetchLifters).mockResolvedValue([])
    const store = useLiftersStore()
    await store.load()
    expect(store.loaded).toBe(true)
    expect(store.items).toEqual([])
  })

  it('neuspjeli dohvat ostavlja prikazani popis i bilježi neuspjeh', async () => {
    vi.mocked(fetchLifters).mockResolvedValueOnce([ANA]).mockRejectedValueOnce(new Error('mreža'))
    const store = useLiftersStore()
    await store.load()
    await expect(store.load()).rejects.toThrow('mreža')
    expect(store.items).toEqual([ANA])
    expect(store.failed).toBe(true)
    expect(store.pending).toBe(false)
  })

  it('ensureLoaded ne šalje drugi zahtjev za popis koji već ima', async () => {
    vi.mocked(fetchLifters).mockResolvedValue([ANA])
    const store = useLiftersStore()
    await store.ensureLoaded()
    await store.ensureLoaded()
    expect(fetchLifters).toHaveBeenCalledTimes(1)
  })

  it('upsert dodaje novog i zamjenjuje postojećeg natjecatelja', () => {
    const store = useLiftersStore()
    store.upsert(ANA)
    store.upsert({ ...ANA, last_name: 'Horvat-Kos' })
    store.upsert(IVAN)
    expect(store.items.map((l) => l.last_name)).toEqual(['Horvat-Kos', 'Perić'])
    expect(store.byId.get(2)).toEqual(IVAN)
  })
})
