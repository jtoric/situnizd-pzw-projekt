// Tablica prijava: stranice, pretraga, razvrstavanje, CSV i radnje po razdoblju
import { describe, expect, it } from 'vitest'

import type { Registration } from '@/api/types'

import { toCsv } from '../csv'
import { pageFromQuery, pageRequest, splitPage } from '../pager'
import { allowedActions } from '../phase'
import { matchesQuery, sortRegistrations } from '../sort'

function reg(id: number, lastName: string, category: string, total = 500): Registration {
  return {
    id,
    lifter_id: id,
    competition_id: 1,
    category,
    total,
    status: 'active',
    registered_at: '2026-11-20T10:00:00Z',
    lifter: { first_name: 'Ime', last_name: lastName },
  }
}

describe('pager', () => {
  it('broj stranice iz adrese', () => {
    expect(pageFromQuery('3')).toBe(3)
    expect(pageFromQuery(undefined)).toBe(1)
    expect(pageFromQuery('0')).toBe(1)
    expect(pageFromQuery('2.5')).toBe(1)
    expect(pageFromQuery('abc')).toBe(1)
  })

  it('traži zapis više od veličine stranice', () => {
    expect(pageRequest(1, 20)).toEqual({ limit: 21, offset: 0 })
    expect(pageRequest(3, 20)).toEqual({ limit: 21, offset: 40 })
  })

  // Točno 20 zapisa: bez zapisa viška prikaz bi nudio prijelaz na praznu stranicu
  it('sljedeća stranica postoji samo kad je stigao zapis viška', () => {
    const twenty = Array.from({ length: 20 }, (_, i) => i)
    expect(splitPage(twenty, 20)).toEqual({ rows: twenty, hasNext: false })
    expect(splitPage([...twenty, 20], 20)).toEqual({ rows: twenty, hasNext: true })
  })
})

describe('sort i pretraga', () => {
  it('razvrstava prezimena po hrvatskoj abecedi', () => {
    const rows = [reg(1, 'Duda', '83'), reg(2, 'Čop', '83'), reg(3, 'Cvor', '83'), reg(4, 'Ćosić', '83')]
    const names = sortRegistrations(rows, 'name', 'asc').map((r) => r.lifter.last_name)
    expect(names).toEqual(['Cvor', 'Čop', 'Ćosić', 'Duda'])
  })

  it('otvorena kategorija ide iza zatvorene iste granice', () => {
    const rows = [reg(1, 'A', '120+'), reg(2, 'B', '59'), reg(3, 'C', '120'), reg(4, 'D', '105')]
    expect(sortRegistrations(rows, 'category', 'asc').map((r) => r.category)).toEqual(['59', '105', '120', '120+'])
  })

  it('ne mijenja ulazni popis', () => {
    const rows = [reg(1, 'Babić', '83'), reg(2, 'Anić', '83')]
    sortRegistrations(rows, 'name', 'asc')
    expect(rows.map((r) => r.id)).toEqual([1, 2])
  })

  it('pretraga ne razlikuje velika slova ni dijakritike', () => {
    expect(matchesQuery('Luka Čolak', 'colak')).toBe(true)
    expect(matchesQuery('Ivan Đurić', 'duric')).toBe(true)
    expect(matchesQuery('Ivan Perić', 'ana')).toBe(false)
  })
})

describe('toCsv', () => {
  it('počinje oznakom BOM i retke odvaja s CRLF', () => {
    expect(toCsv([['a', 'b'], [1, 2]])).toBe('\uFEFFa;b\r\n1;2\r\n')
  })

  it('vrijednost s razdjelnikom ili navodnikom stavlja u navodnike', () => {
    expect(toCsv([['PK "Sokol"; Split']])).toBe('\uFEFF"PK ""Sokol""; Split"\r\n')
  })

  // Ime upisuje klub; kalkulator bi =HYPERLINK(...) izveo kao formulu
  it('vrijednost koja bi bila formula ostaje tekst', () => {
    expect(toCsv([['=HYPERLINK("http://x")']])).toBe('\uFEFF"\'=HYPERLINK(""http://x"")"\r\n')
    expect(toCsv([['@SUM(A1)']])).toBe("\uFEFF'@SUM(A1)\r\n")
  })
})

describe('allowedActions', () => {
  it('prati matricu faza iz README.md', () => {
    expect(allowedActions('open')).toEqual({ register: true, changeStatus: true })
    expect(allowedActions('prelim_passed')).toEqual({ register: false, changeStatus: true })
    expect(allowedActions('closed')).toEqual({ register: false, changeStatus: false })
  })
})
