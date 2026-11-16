<script setup lang="ts">
/**
 * Obrazac kojim klub prijavljuje svog natjecatelja na natjecanje.
 *
 * Natjecatelje čita iz pohrane (stores/lifters.ts), koju dijeli s popisom natjecatelja. Nudi samo
 * one koji na ovom natjecanju još nemaju prijavu i samo kategorije njihova spola; poslužitelj
 * svejedno provjerava sve sam. Uspjelu prijavu javlja roditelju događajem created.
 */
import { computed, onMounted, ref, watch } from 'vue'

import { ApiError } from '@/api/http'
import { createRegistration } from '@/api/registrations'
import type { Registration } from '@/api/types'
import { CATEGORIES, categoryLabel } from '@/lib/categories'
import { toFieldErrors } from '@/lib/errors'
import type { FieldErrors } from '@/lib/validation'
import { useLiftersStore } from '@/stores/lifters'

const props = defineProps<{
  compId: number
  /** oznake natjecatelja koji na ovom natjecanju već imaju prijavu, aktivnu ili odjavljenu */
  registeredLifterIds: number[]
}>()

const emit = defineEmits<{ created: [registration: Registration] }>()

const lifters = useLiftersStore()
onMounted(() => lifters.ensureLoaded().catch(() => {}))

const lifterId = ref<number | null>(null)
const category = ref('')
const total = ref(0)
const errors = ref<FieldErrors>({})
const formError = ref('')
const pending = ref(false)

const available = computed(() =>
  lifters.items.filter((l) => !props.registeredLifterIds.includes(l.id)),
)
const selected = computed(() =>
  lifterId.value === null ? undefined : lifters.byId.get(lifterId.value),
)
const categories = computed(() => (selected.value ? CATEGORIES[selected.value.gender] : []))

// Promjena natjecatelja može promijeniti spol, a s njim i dopuštene kategorije
watch(selected, () => {
  if (!categories.value.includes(category.value)) category.value = ''
})

async function submit() {
  errors.value = {}
  formError.value = ''
  if (lifterId.value === null) errors.value.lifter_id = 'Odaberite natjecatelja.'
  if (category.value === '') errors.value.category = 'Odaberite kategoriju.'
  if (!Number.isInteger(total.value) || total.value < 0) {
    errors.value.total = 'Total mora biti cijeli broj, 0 ili veći.'
  }
  if (Object.keys(errors.value).length > 0) return

  pending.value = true
  try {
    const registration = await createRegistration(props.compId, {
      lifter_id: lifterId.value!,
      category: category.value,
      total: total.value,
    })
    emit('created', registration)
    lifterId.value = null
    category.value = ''
    total.value = 0
  } catch (e) {
    if (!(e instanceof ApiError)) throw e
    if (e.code === 'validation_error') errors.value = toFieldErrors(e.fieldErrors)
    // Pravila natjecanja (rok, kategorija i spol, dvostruka prijava): poruka iznad gumba
    else if (e.status === 400 || e.status === 409) formError.value = e.message
    else throw e
  } finally {
    pending.value = false
  }
}
</script>

<template>
  <form class="card registration-form" novalidate @submit.prevent="submit">
    <h2>Nova prijava</h2>
    <p v-if="lifters.loaded && available.length === 0" class="lead">
      Svi natjecatelji kluba već su prijavljeni ili klub još nema natjecatelja.
    </p>
    <div class="row">
      <div class="field">
        <label for="reg-lifter">Natjecatelj</label>
        <select
          id="reg-lifter"
          v-model="lifterId"
          :aria-invalid="errors.lifter_id ? 'true' : undefined"
          :aria-describedby="errors.lifter_id ? 'reg-lifter-error' : undefined"
        >
          <option :value="null" disabled>Odaberite natjecatelja</option>
          <option v-for="l in available" :key="l.id" :value="l.id">
            {{ l.last_name }}, {{ l.first_name }}
          </option>
        </select>
        <p v-if="errors.lifter_id" id="reg-lifter-error" class="field-error">{{ errors.lifter_id }}</p>
      </div>
      <div class="field">
        <label for="reg-category">Kategorija</label>
        <select
          id="reg-category"
          v-model="category"
          :disabled="!selected"
          :aria-invalid="errors.category ? 'true' : undefined"
          :aria-describedby="errors.category ? 'reg-category-error' : undefined"
        >
          <option value="" disabled>Odaberite kategoriju</option>
          <option v-for="c in categories" :key="c" :value="c">{{ categoryLabel(c) }}</option>
        </select>
        <p v-if="errors.category" id="reg-category-error" class="field-error">{{ errors.category }}</p>
      </div>
      <div class="field">
        <label for="reg-total">Prijavljeni total (kg)</label>
        <!-- v-model.number: vrijednost polja je uvijek tekst, a tijelo zahtjeva traži broj -->
        <input
          id="reg-total"
          v-model.number="total"
          type="number"
          min="0"
          step="1"
          inputmode="numeric"
          :aria-invalid="errors.total ? 'true' : undefined"
          :aria-describedby="errors.total ? 'reg-total-error' : undefined"
        />
        <p v-if="errors.total" id="reg-total-error" class="field-error">{{ errors.total }}</p>
      </div>
    </div>
    <p v-if="formError" class="form-error" role="alert">{{ formError }}</p>
    <button class="btn" type="submit" :disabled="pending">
      {{ pending ? 'Prijava u tijeku…' : 'Prijavi natjecatelja' }}
    </button>
  </form>
</template>

<style scoped>
.registration-form { margin: 24px 0; }
.registration-form h2 { margin-top: 0; }
.row { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 0 16px; }
</style>
