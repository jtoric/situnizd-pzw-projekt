/**
 * Izmjena zapisa šalje se kao PATCH sa samo promijenjenim poljima. Polje koje se ne šalje
 * poslužitelj ostavlja kakvo jest (api/app/services, model_dump(exclude_unset=True)), pa
 * izmjena ne prepisuje polje koje je u međuvremenu promijenio netko drugi.
 */

/** Polja iz after čija se vrijednost razlikuje od one u before; bez razlike vraća {}. */
export function changedFields<T extends object>(before: T, after: T): Partial<T> {
  const changes: Partial<T> = {}
  for (const key of Object.keys(after) as (keyof T)[]) {
    if (after[key] !== before[key]) changes[key] = after[key]
  }
  return changes
}
