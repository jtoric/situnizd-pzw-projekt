<script setup lang="ts">
/**
 * Dodavanje i uređivanje natjecanja (organizator).
 *
 * Rokovi se upisuju u polja datetime-local, koja nemaju vremensku zonu. lib/datetime.ts ih
 * pretvara u trenutak po zagrebačkom vremenu (s pomakom +01:00 ili +02:00), jer ih poslužitelj
 * bez oznake zone odbija (422).
 */
import { computed, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { createCompetition, fetchCompetition, updateCompetition } from '@/api/competitions'
import { ApiError } from '@/api/http'
import type { CompetitionInput } from '@/api/types'
import FormField from '@/components/FormField.vue'
import { fromLocalInput, toLocalInput } from '@/lib/datetime'
import { changedFields } from '@/lib/diff'
import { toFieldErrors } from '@/lib/errors'
import type { FieldErrors } from '@/lib/validation'
import { useNotificationsStore } from '@/stores/notifications'

const route = useRoute()
const router = useRouter()
const notifications = useNotificationsStore()

const compId = computed(() => (route.params.compId === undefined ? null : Number(route.params.compId)))
const isEdit = computed(() => compId.value !== null)

// Vrijednosti polja obrasca: rokovi u obliku polja datetime-local ("2027-02-14T23:59")
interface FormValues {
  name: string
  location: string
  date: string
  prelim: string
  final: string
}
const empty = (): FormValues => ({ name: '', location: '', date: '', prelim: '', final: '' })
const form = reactive<FormValues>(empty())
let original: CompetitionInput | null = null

const errors = ref<FieldErrors>({})
const formError = ref('')
const pending = ref(false)
const loadFailed = ref(false)

watch(
  compId,
  async (id) => {
    errors.value = {}
    formError.value = ''
    loadFailed.value = false
    original = null
    Object.assign(form, empty())
    if (id === null) return
    try {
      const c = await fetchCompetition(id)
      if (compId.value !== id) return
      original = {
        name: c.name,
        location: c.location,
        date: c.date,
        prelim_deadline: fromLocalInput(toLocalInput(c.prelim_deadline))!,
        final_deadline: fromLocalInput(toLocalInput(c.final_deadline))!,
      }
      Object.assign(form, {
        name: c.name,
        location: c.location,
        date: c.date,
        prelim: toLocalInput(c.prelim_deadline),
        final: toLocalInput(c.final_deadline),
      })
    } catch (e) {
      if (!(e instanceof ApiError)) throw e
      loadFailed.value = true
    }
  },
  { immediate: true },
)

// Ista pravila kao CompetitionCreate u api/app/schemas/competition.py; mijenjati zajedno
function validate(input: CompetitionInput | null): FieldErrors {
  const result: FieldErrors = {}
  if (form.name.trim() === '') result.name = 'Naziv je obavezan.'
  if (form.location.trim() === '') result.location = 'Mjesto je obavezno.'
  if (form.date === '') result.date = 'Datum natjecanja je obavezan.'
  if (form.prelim === '') result.prelim_deadline = 'Preliminarni rok je obavezan.'
  if (form.final === '') result.final_deadline = 'Konačni rok je obavezan.'
  if (input && !result.prelim_deadline && !result.final_deadline) {
    // Polja datetime-local iste zone uspoređuju se kao tekst, jer su znamenke od godine prema minuti
    if (form.final <= form.prelim) result.final_deadline = 'Konačni rok mora biti nakon preliminarnog.'
    else if (form.date && form.final.slice(0, 10) >= form.date) {
      result.final_deadline = 'Rokovi moraju isteći prije dana natjecanja.'
    }
  }
  return result
}

function toInput(): CompetitionInput | null {
  const prelim = fromLocalInput(form.prelim)
  const final = fromLocalInput(form.final)
  if (!prelim || !final) return null
  return {
    name: form.name.trim(),
    location: form.location.trim(),
    date: form.date,
    prelim_deadline: prelim,
    final_deadline: final,
  }
}

async function submit() {
  formError.value = ''
  const input = toInput()
  errors.value = validate(input)
  if (Object.keys(errors.value).length > 0 || !input) return

  pending.value = true
  try {
    if (compId.value === null) await createCompetition(input)
    else await updateCompetition(compId.value, changedFields(original!, input))
    notifications.success(isEdit.value ? 'Natjecanje je spremljeno.' : 'Natjecanje je dodano.')
    await router.push({ name: 'admin-competitions' })
  } catch (e) {
    if (!(e instanceof ApiError)) throw e
    if (e.code === 'validation_error') {
      const fields = toFieldErrors(e.fieldErrors)
      // Pravilo nad cijelim tijelom (model_validator) nema polje: poruka ide iznad gumba
      formError.value = fields[''] ?? ''
      errors.value = fields
    } else if (e.status === 400) formError.value = e.message
    else throw e
  } finally {
    pending.value = false
  }
}
</script>

<template>
  <div class="page-header">
    <h2>{{ isEdit ? 'Uređivanje natjecanja' : 'Dodavanje natjecanja' }}</h2>
  </div>

  <div v-if="loadFailed" class="state" role="alert">
    <p>Natjecanje nije pronađeno ili se trenutno ne može učitati.</p>
    <RouterLink :to="{ name: 'admin-competitions' }">Na popis natjecanja</RouterLink>
  </div>

  <form v-else class="card form" novalidate @submit.prevent="submit">
    <FormField id="comp-name" v-model="form.name" label="Naziv" required :error="errors.name" />
    <FormField id="comp-location" v-model="form.location" label="Mjesto" required :error="errors.location" />
    <FormField id="comp-date" v-model="form.date" label="Datum natjecanja" type="date" required :error="errors.date" />
    <p id="tz-hint" class="hint">Rokovi se upisuju po zagrebačkom vremenu.</p>
    <div class="field">
      <label for="comp-prelim">Preliminarni rok</label>
      <input
        id="comp-prelim"
        v-model="form.prelim"
        type="datetime-local"
        :aria-invalid="errors.prelim_deadline ? 'true' : undefined"
        :aria-describedby="errors.prelim_deadline ? 'tz-hint comp-prelim-error' : 'tz-hint'"
      />
      <p v-if="errors.prelim_deadline" id="comp-prelim-error" class="field-error">{{ errors.prelim_deadline }}</p>
    </div>
    <div class="field">
      <label for="comp-final">Konačni rok</label>
      <input
        id="comp-final"
        v-model="form.final"
        type="datetime-local"
        :aria-invalid="errors.final_deadline ? 'true' : undefined"
        :aria-describedby="errors.final_deadline ? 'tz-hint comp-final-error' : 'tz-hint'"
      />
      <p v-if="errors.final_deadline" id="comp-final-error" class="field-error">{{ errors.final_deadline }}</p>
    </div>
    <p v-if="formError" class="form-error" role="alert">{{ formError }}</p>
    <div class="form-actions">
      <button class="btn" type="submit" :disabled="pending">{{ pending ? 'Spremanje…' : 'Spremi' }}</button>
      <RouterLink class="btn btn-secondary" :to="{ name: 'admin-competitions' }">Odustani</RouterLink>
    </div>
  </form>
</template>

<style scoped>
.form { max-width: 520px; }
.hint { margin: 0 0 8px; color: var(--muted); font-size: 14px; }
</style>
