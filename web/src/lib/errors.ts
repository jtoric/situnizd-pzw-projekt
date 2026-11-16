/**
 * Pogreške poslužitelja uz polja obrasca.
 *
 * Odgovor 422 nosi popis polja koja nisu prošla provjeru sheme (api/app/core/errors.py):
 * {"code": "validation_error", "errors": [{"field": "birth_date", "message": "..."}]}.
 * Obrazac ih prikazuje na istom mjestu kao i pogreške vlastite provjere (lib/validation.ts).
 */
import type { FieldError } from '@/api/types'

import type { FieldErrors } from './validation'

/**
 * Pretvara popis u objekt po imenu polja. Ime polja iz tijela stiže bez predmetka ("birth_date"),
 * a polje upita s njim ("query.limit"); za drugo obrazac nema polje, pa ostaje pod punim imenom.
 * Uz više poruka za isto polje zadržava se prva.
 */
export function toFieldErrors(errors: FieldError[]): FieldErrors {
  const result: FieldErrors = {}
  for (const error of errors) {
    if (!(error.field in result)) result[error.field] = error.message
  }
  return result
}
