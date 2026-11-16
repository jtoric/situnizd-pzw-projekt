<script setup lang="ts">
/**
 * Jedno natjecanje: podatci, rokovi i prijave. Klub ovdje prijavljuje svoje natjecatelje i
 * odjavljuje ih, a organizator vidi prijave svih klubova.
 */
import { computed, watch } from 'vue'
import { useRoute } from 'vue-router'

import { fetchCompetition } from '@/api/competitions'
import { ApiError } from '@/api/http'
import {
  fetchRegistrations,
  reactivateRegistration,
  withdrawRegistration,
} from '@/api/registrations'
import type { Registration } from '@/api/types'
import RegistrationForm from '@/components/RegistrationForm.vue'
import StatusBadge from '@/components/StatusBadge.vue'
import { useRequest } from '@/composables/useRequest'
import { categoryLabel } from '@/lib/categories'
import { formatDate, formatDateTime, PHASE_LABELS } from '@/lib/format'
import { useAuthStore } from '@/stores/auth'
import { useNotificationsStore } from '@/stores/notifications'

const route = useRoute()
const auth = useAuthStore()
const notifications = useNotificationsStore()

// Parametar adrese je uvijek tekst; ruta propušta samo znamenke (router/index.ts)
const compId = computed(() => Number(route.params.compId))

// Ref unutar objekta predložak ne raspakira sam, pa se vrijednosti odmah raspakiraju u imena
const {
  data: competition,
  pending: competitionPending,
  error: competitionError,
  run: loadCompetition,
} = useRequest(() => fetchCompetition(compId.value))
// Klub ima nekoliko prijava po natjecanju, pa jedan dohvat s najvećim limitom dohvaća sve
const {
  data: registrations,
  pending: registrationsPending,
  error: registrationsError,
  run: loadRegistrations,
} = useRequest(() => fetchRegistrations(compId.value, { limit: 100 }))

// watch, a ne onMounted: prijelaz na drugo natjecanje zadržava istu instancu komponente
watch(
  compId,
  () => {
    loadCompetition()
    loadRegistrations()
  },
  { immediate: true },
)

const registeredLifterIds = computed(() => (registrations.value ?? []).map((r) => r.lifter_id))

function replaceRow(updated: Registration) {
  registrations.value = (registrations.value ?? []).map((r) => (r.id === updated.id ? updated : r))
}

function onCreated(registration: Registration) {
  registrations.value = [...(registrations.value ?? []), registration]
  const { first_name, last_name } = registration.lifter
  notifications.success(`Prijava je spremljena: ${first_name} ${last_name}.`)
}

async function changeStatus(registration: Registration) {
  const withdrawing = registration.status === 'active'
  try {
    const updated = withdrawing
      ? await withdrawRegistration(compId.value, registration.id)
      : await reactivateRegistration(compId.value, registration.id)
    replaceRow(updated)
    notifications.success(withdrawing ? 'Prijava je odjavljena.' : 'Prijava je ponovno aktivna.')
  } catch (e) {
    // Ponovljeni zahtjev (dvostruki klik, druga kartica): radnja je već provedena, pa to nije
    // pogreška za korisnika. Popis se osvježava, jer prikazano stanje očito nije najnovije.
    if (e instanceof ApiError && (e.code === 'already_withdrawn' || e.code === 'already_active')) {
      notifications.success(e.message)
      loadRegistrations()
      return
    }
    throw e
  }
}
</script>

<template>
  <p v-if="!competition && competitionPending" class="state" aria-busy="true">
    Učitavanje natjecanja…
  </p>
  <div v-else-if="!competition && competitionError" class="state" role="alert">
    <p v-if="competitionError.status === 404">Natjecanje nije pronađeno.</p>
    <template v-else>
      <p>Natjecanje se trenutno ne može učitati.</p>
      <button class="btn btn-secondary" type="button" @click="loadCompetition()">Pokušaj ponovno</button>
    </template>
  </div>

  <template v-else-if="competition">
    <div class="page-header">
      <h1>{{ competition.name }}</h1>
      <span class="phase">{{ PHASE_LABELS[competition.phase] }}</span>
    </div>
    <dl class="facts">
      <div><dt>Mjesto</dt><dd>{{ competition.location }}</dd></div>
      <div><dt>Datum</dt><dd>{{ formatDate(competition.date) }}</dd></div>
      <div><dt>Preliminarni rok</dt><dd>{{ formatDateTime(competition.prelim_deadline) }}</dd></div>
      <div><dt>Konačni rok</dt><dd>{{ formatDateTime(competition.final_deadline) }}</dd></div>
    </dl>

    <RegistrationForm
      v-if="!auth.isAdmin"
      :comp-id="compId"
      :registered-lifter-ids="registeredLifterIds"
      @created="onCreated"
    />

    <h2>{{ auth.isAdmin ? 'Prijave svih klubova' : 'Prijave kluba' }}</h2>
    <p v-if="!registrations && registrationsPending" class="state" aria-busy="true">
      Učitavanje prijava…
    </p>
    <div v-else-if="!registrations && registrationsError" class="state" role="alert">
      <p>Prijave se trenutno ne mogu učitati.</p>
      <button class="btn btn-secondary" type="button" @click="loadRegistrations()">Pokušaj ponovno</button>
    </div>
    <p v-else-if="registrations?.length === 0" class="state">Još nema prijava.</p>
    <div v-else-if="registrations" class="table-wrap">
      <table>
        <thead>
          <tr>
            <th scope="col">Natjecatelj</th>
            <th scope="col">Kategorija</th>
            <th scope="col">Total</th>
            <th scope="col">Stanje</th>
            <th scope="col"><span class="sr-only">Radnje</span></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in registrations" :key="r.id">
            <td>{{ r.lifter.last_name }}, {{ r.lifter.first_name }}</td>
            <td>{{ categoryLabel(r.category) }}</td>
            <td>{{ r.total }} kg</td>
            <td><StatusBadge :status="r.status" /></td>
            <td class="actions">
              <button class="btn btn-secondary btn-small" type="button" @click="changeStatus(r)">
                {{ r.status === 'active' ? 'Odjavi' : 'Vrati prijavu' }}
                <span class="sr-only">{{ r.lifter.first_name }} {{ r.lifter.last_name }}</span>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </template>
</template>

<style scoped>
.phase { padding: 2px 10px; border-radius: 999px; background: var(--tint); color: var(--ink); font-weight: 600; }
.facts { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; margin: 0; }
.facts div { background: var(--surface); border: 1px solid var(--line); border-radius: var(--radius); padding: 12px 16px; }
.facts dt { color: var(--muted); font-size: 14px; }
.facts dd { margin: 0; font-weight: 600; }
</style>
