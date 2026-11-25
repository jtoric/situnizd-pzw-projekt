import { describe, expect, it } from 'vitest'

import { formatDate, formatDateTime } from '../format'

describe('formatDate', () => {
  it('prikazuje datum bez vodećih nula', () => {
    expect(formatDate('2027-03-04')).toBe('4. 3. 2027.')
  })

  // Testovi rade u zoni America/Los_Angeles (vitest.config.ts). new Date('2027-03-14') bi tu
  // bio 13. ožujka navečer; datum se zato čita kao tekst.
  it('daje isti dan i zapadno od UTC-a', () => {
    expect(formatDate('2027-03-14')).toBe('14. 3. 2027.')
  })

  it('tekst koji nije datum vraća nepromijenjen', () => {
    expect(formatDate('uskoro')).toBe('uskoro')
  })
})

describe('formatDateTime', () => {
  it('prikazuje rok po zagrebačkom vremenu zimi', () => {
    expect(formatDateTime('2027-02-14T22:59:00Z')).toBe('14. 2. 2027. u 23:59')
  })

  it('prikazuje rok po zagrebačkom vremenu ljeti', () => {
    expect(formatDateTime('2027-04-20T21:59:00Z')).toBe('20. 4. 2027. u 23:59')
  })

  it('ponoć je 00:00, a ne 24:00', () => {
    expect(formatDateTime('2027-02-14T23:00:00Z')).toBe('15. 2. 2027. u 00:00')
  })
})
