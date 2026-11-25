// Kratke čiste funkcije: parametri upita, povratak nakon prijave, pogreške uz polja, izmjene
import { describe, expect, it } from 'vitest'

import { changedFields } from '../diff'
import { toFieldErrors } from '../errors'
import { safeRedirect } from '../navigation'
import { buildQuery } from '../query'

describe('buildQuery', () => {
  it('izostavlja prazne vrijednosti, jer bi ?status= dalo 422', () => {
    expect(buildQuery({ limit: 21, offset: 0, status: '' })).toBe('?limit=21&offset=0')
    expect(buildQuery({ status: undefined, gender: null })).toBe('')
  })

  it('kodira znakove koji imaju značenje u adresi', () => {
    expect(buildQuery({ q: 'a&b=c' })).toBe('?q=a%26b%3Dc')
  })
})

describe('safeRedirect', () => {
  it('propušta unutarnju putanju s upitom', () => {
    expect(safeRedirect('/natjecanja/1?stanje=active')).toBe('/natjecanja/1?stanje=active')
  })

  it.each([
    ['https://drugi.example/'],
    ['//drugi.example/'],
    ['/\\drugi.example/'],
    ['javascript:alert(1)'],
    [undefined],
    [['/natjecanja', '/admin']],
  ])('tuđu ili neispravnu vrijednost %j zamjenjuje početnom stranicom', (value) => {
    expect(safeRedirect(value)).toBe('/')
  })
})

describe('toFieldErrors', () => {
  it('slaže pogreške po polju i zadržava prvu poruku', () => {
    expect(
      toFieldErrors([
        { field: 'birth_date', message: 'Datum rođenja mora biti u prošlosti' },
        { field: 'birth_date', message: 'druga poruka' },
        { field: 'query.limit', message: 'najviše 100' },
      ]),
    ).toEqual({ birth_date: 'Datum rođenja mora biti u prošlosti', 'query.limit': 'najviše 100' })
  })
})

describe('changedFields', () => {
  it('vraća samo promijenjena polja', () => {
    const before = { first_name: 'Ana', last_name: 'Horvat', gender: 'F' }
    const after = { first_name: 'Ana', last_name: 'Horvat-Kos', gender: 'F' }
    expect(changedFields(before, after)).toEqual({ last_name: 'Horvat-Kos' })
  })

  it('bez izmjene vraća prazan objekt, pa PATCH ne mijenja ništa', () => {
    const value = { name: '16. Državno prvenstvo u powerliftingu' }
    expect(changedFields(value, { ...value })).toEqual({})
  })
})
