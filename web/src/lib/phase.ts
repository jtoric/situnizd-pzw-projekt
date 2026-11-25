/**
 * Koje radnje nad prijavama sučelje nudi u kojem razdoblju natjecanja.
 *
 * Matrica je ista kao u README.md (Faze natjecanja), a provodi je poslužitelj
 * (api/app/services/registration_service.py); mijenjati zajedno. Sučelje je samo prikazuje:
 * zahtjev koji stigne mimo njega poslužitelj odbija s kodom deadline_passed.
 */
import type { Phase } from '@/api/types'

export interface AllowedActions {
  /** nova prijava */
  register: boolean
  /** odjava i povratak odjavljene prijave */
  changeStatus: boolean
}

const MATRIX: Record<Phase, AllowedActions> = {
  open: { register: true, changeStatus: true },
  prelim_passed: { register: false, changeStatus: true },
  closed: { register: false, changeStatus: false },
}

/** Dopuštene radnje za razdoblje. */
export const allowedActions = (phase: Phase): AllowedActions => MATRIX[phase]

/** Zašto radnja nije ponuđena; tekst uz onemogućeni gumb. */
export const REASONS = {
  register: 'Rok za nove prijave je istekao.',
  changeStatus: 'Nakon konačnog roka prijave se ne mogu mijenjati.',
} as const
