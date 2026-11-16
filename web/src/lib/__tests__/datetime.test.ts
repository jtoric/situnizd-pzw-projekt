import { describe, expect, it } from 'vitest'

import { fromLocalInput, toLocalInput } from '../datetime'

describe('fromLocalInput', () => {
  it('zimi dodaje pomak +01:00', () => {
    expect(fromLocalInput('2027-02-14T23:59')).toBe('2027-02-14T23:59:00+01:00')
  })

  it('ljeti dodaje pomak +02:00', () => {
    expect(fromLocalInput('2027-04-20T23:59')).toBe('2027-04-20T23:59:00+02:00')
  })

  // Prelazak na ljetno vrijeme 2027. je 28. ožujka u 2:00; dan prije i dan poslije imaju
  // različit pomak, iako se zona računala testa (Los Angeles) mijenja drugog datuma
  it('prati prelazak na ljetno vrijeme u Zagrebu, a ne u zoni računala', () => {
    expect(fromLocalInput('2027-03-27T12:00')).toBe('2027-03-27T12:00:00+01:00')
    expect(fromLocalInput('2027-03-28T12:00')).toBe('2027-03-28T12:00:00+02:00')
  })

  it('vrijednost koja nije iz polja datetime-local daje null', () => {
    expect(fromLocalInput('')).toBeNull()
    expect(fromLocalInput('14.2.2027. 23:59')).toBeNull()
  })
})

describe('toLocalInput', () => {
  it('trenutak u UTC-u daje zagrebačko vrijeme za polje', () => {
    expect(toLocalInput('2027-02-14T22:59:00Z')).toBe('2027-02-14T23:59')
    expect(toLocalInput('2027-04-20T21:59:00Z')).toBe('2027-04-20T23:59')
  })

  it('pretvorba tamo i natrag ne mijenja trenutak', () => {
    const value = '2027-10-31T01:30'
    const iso = fromLocalInput(value)!
    expect(toLocalInput(iso)).toBe(value)
  })
})
