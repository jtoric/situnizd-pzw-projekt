/**
 * Težinske kategorije IPF-a po spolu.
 *
 * Isti popisi su u api/app/schemas/registration.py; mijenjati zajedno. Poslužitelj ih provjerava
 * sam, a ovdje služe da obrazac ponudi samo kategorije koje odgovaraju spolu natjecatelja.
 */
import type { Gender } from '@/api/types'

export const CATEGORIES: Record<Gender, readonly string[]> = {
  M: ['59', '66', '74', '83', '93', '105', '120', '120+'],
  F: ['47', '52', '57', '63', '69', '76', '84', '84+'],
}

/** "83" -> "83 kg", "120+" -> "120+ kg" */
export const categoryLabel = (category: string): string => `${category} kg`
