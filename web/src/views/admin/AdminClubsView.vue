<script setup lang="ts">
/** Klubovi i dodavanje novog kluba s računom za prijavu (organizator). */
import { onMounted, reactive, ref } from 'vue'

import { createClub, fetchClubs, type ClubInput } from '@/api/clubs'
import { ApiError } from '@/api/http'
import FormField from '@/components/FormField.vue'
import { useRequest } from '@/composables/useRequest'
import { toFieldErrors } from '@/lib/errors'
import type { FieldErrors } from '@/lib/validation'
import { useNotificationsStore } from '@/stores/notifications'

const notifications = useNotificationsStore()
const { data: clubs, pending, error, run: load } = useRequest(fetchClubs)
onMounted(load)

const empty = (): ClubInput => ({ name: '', city: '', username: '', password: '' })
const form = reactive<ClubInput>(empty())
const errors = ref<FieldErrors>({})
const formError = ref('')
const saving = ref(false)

// Ista pravila kao ClubCreate u api/app/schemas/club.py; mijenjati zajedno
function validate(input: ClubInput): FieldErrors {
  const result: FieldErrors = {}
  if (input.name === '') result.name = 'Naziv kluba je obavezan.'
  if (input.city === '') result.city = 'Grad je obavezan.'
  if (input.username.length < 3) result.username = 'Korisničko ime mora imati barem 3 znaka.'
  if (input.password.length < 8) result.password = 'Lozinka mora imati barem 8 znakova.'
  return result
}

async function submit() {
  formError.value = ''
  const input = { ...form, name: form.name.trim(), city: form.city.trim(), username: form.username.trim() }
  errors.value = validate(input)
  if (Object.keys(errors.value).length > 0) return
  saving.value = true
  try {
    const club = await createClub(input)
    clubs.value = [...(clubs.value ?? []), club]
    Object.assign(form, empty())
    notifications.success(`Klub ${club.name} je dodan.`)
  } catch (e) {
    if (!(e instanceof ApiError)) throw e
    if (e.code === 'validation_error') errors.value = toFieldErrors(e.fieldErrors)
    else if (e.code === 'duplicate') formError.value = e.message
    else throw e
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <h2>Klubovi</h2>
  <p v-if="!clubs && pending" class="state" aria-busy="true">Učitavanje klubova…</p>
  <div v-else-if="!clubs && error" class="state" role="alert">
    <p>Klubovi se trenutno ne mogu učitati.</p>
    <button class="btn btn-secondary" type="button" @click="load">Pokušaj ponovno</button>
  </div>
  <p v-else-if="clubs?.length === 0" class="state">Još nema klubova.</p>
  <div v-else-if="clubs" class="table-wrap">
    <table>
      <thead>
        <tr><th scope="col">Klub</th><th scope="col">Grad</th></tr>
      </thead>
      <tbody>
        <tr v-for="c in clubs" :key="c.id"><td>{{ c.name }}</td><td>{{ c.city }}</td></tr>
      </tbody>
    </table>
  </div>

  <form class="card form" novalidate @submit.prevent="submit">
    <h3>Novi klub</h3>
    <FormField id="club-name" v-model="form.name" label="Naziv kluba" required :error="errors.name" />
    <FormField id="club-city" v-model="form.city" label="Grad" required :error="errors.city" />
    <FormField
      id="club-username"
      v-model="form.username"
      label="Korisničko ime za prijavu"
      autocomplete="off"
      required
      :error="errors.username"
    />
    <FormField
      id="club-password"
      v-model="form.password"
      label="Početna lozinka"
      type="password"
      autocomplete="new-password"
      required
      :error="errors.password"
    />
    <p v-if="formError" class="form-error" role="alert">{{ formError }}</p>
    <button class="btn" type="submit" :disabled="saving">{{ saving ? 'Spremanje…' : 'Dodaj klub' }}</button>
  </form>
</template>

<style scoped>
.form { max-width: 480px; margin-top: 24px; }
.form h3 { margin-top: 0; color: var(--ink); }
</style>
