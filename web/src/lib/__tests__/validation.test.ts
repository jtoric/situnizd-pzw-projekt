import { describe, expect, it } from 'vitest'

import type { LifterInput } from '@/api/types'

import { localToday, validateLifter } from '../validation'

const TODAY = '2026-11-26'
const VALID: LifterInput = { first_name: 'Ana', last_name: 'Horvat', birth_date: '2001-05-02', gender: 'F' }

describe('validateLifter', () => {
  it('ispravan natjecatelj nema pogrešaka', () => {
    expect(validateLifter(VALID, TODAY)).toEqual({})
  })

  it('ime od samih razmaka je prazno', () => {
    expect(validateLifter({ ...VALID, first_name: '   ' }, TODAY)).toEqual({
      first_name: 'Ime je obavezno.',
    })
  })

  it('prezime smije imati najviše 80 znakova', () => {
    expect(validateLifter({ ...VALID, last_name: 'A'.repeat(80) }, TODAY)).toEqual({})
    expect(validateLifter({ ...VALID, last_name: 'A'.repeat(81) }, TODAY)).toHaveProperty('last_name')
  })

  // Granica je današnji dan: rođen danas nije rođen u prošlosti (ista granica kao u shemi)
  it('datum rođenja mora biti prije današnjeg dana', () => {
    expect(validateLifter({ ...VALID, birth_date: '2026-11-25' }, TODAY)).toEqual({})
    expect(validateLifter({ ...VALID, birth_date: TODAY }, TODAY)).toEqual({
      birth_date: 'Datum rođenja mora biti u prošlosti.',
    })
  })

  it('prazan datum je obavezno polje, a ne datum u prošlosti', () => {
    expect(validateLifter({ ...VALID, birth_date: '' }, TODAY)).toEqual({
      birth_date: 'Datum rođenja je obavezan.',
    })
  })
})

describe('localToday', () => {
  // 23:30 lokalno je u zoni zapadno od UTC-a već sljedeći dan po UTC-u
  it('daje lokalni dan, a ne dan po UTC-u', () => {
    expect(localToday(new Date(2026, 10, 26, 23, 30))).toBe('2026-11-26')
  })
})
