// Isti podatak na dvije strane: popis kategorija postoji i u shemi backenda. Test čita
// api/app/schemas/registration.py kao tekst i pada čim se popisi razilaze, pa "mijenjati
// zajedno" ne ovisi o tome hoće li se netko sjetiti komentara.
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'

import { describe, expect, it } from 'vitest'

import { CATEGORIES } from '../categories'

const SCHEMA = fileURLToPath(new URL('../../../../api/app/schemas/registration.py', import.meta.url))

function pythonList(source: string, name: string): string[] {
  const match = new RegExp(`^${name} = \\[(.*)\\]$`, 'm').exec(source)
  if (!match) throw new Error(`${name} nije pronađen u ${SCHEMA}`)
  return [...match[1]!.matchAll(/"([^"]+)"/g)].map((m) => m[1]!)
}

describe('CATEGORIES', () => {
  const source = readFileSync(SCHEMA, 'utf8')

  it('muške kategorije jednake su onima u shemi backenda', () => {
    expect([...CATEGORIES.M]).toEqual(pythonList(source, 'MALE_CATEGORIES'))
  })

  it('ženske kategorije jednake su onima u shemi backenda', () => {
    expect([...CATEGORIES.F]).toEqual(pythonList(source, 'FEMALE_CATEGORIES'))
  })
})
