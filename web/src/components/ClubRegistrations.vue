<script setup lang="ts">
/**
 * Prijave kluba na jedno natjecanje: obrazac za novu prijavu i popis s odjavom i povratkom.
 *
 * Klub ima nekoliko prijava po natjecanju, pa se popis dohvaća cijeli, jednim zahtjevom. Koje
 * radnje su ponuđene, ovisi o razdoblju natjecanja (lib/phase.ts).
 */
import { computed, watch } from 'vue'

import { fetchRegistrations } from '@/api/registrations'
import type { Competition, Registration } from '@/api/types'
import RegistrationForm from '@/components/RegistrationForm.vue'
import StatusBadge from '@/components/StatusBadge.vue'
import TableScroll from '@/components/TableScroll.vue'
import { useRequest } from '@/composables/useRequest'
import { useStatusChange } from '@/composables/useStatusChange'
import { categoryLabel } from '@/lib/categories'
import { allowedActions, REASONS } from '@/lib/phase'
import { useNotificationsStore } from '@/stores/notifications'

const props = defineProps<{ competition: Competition }>()
// Razdoblje u prikazu je možda zastarjelo (rok je istekao dok je stranica otvorena)
const emit = defineEmits<{ stale: [] }>()

const notifications = useNotificationsStore()

const { data: registrations, pending, error, run: load } = useRequest(() =>
  fetchRegistrations(props.competition.id, { limit: 100 }),
)
watch(() => props.competition.id, load, { immediate: true })

// Ime kaže što se smije, a ne koje je razdoblje: novo razdoblje mijenja samo lib/phase.ts
const allowed = computed(() => allowedActions(props.competition.phase))
const registeredLifterIds = computed(() => (registrations.value ?? []).map((r) => r.lifter_id))

function replaceRow(updated: Registration) {
  registrations.value = (registrations.value ?? []).map((r) => (r.id === updated.id ? updated : r))
}

function onCreated(registration: Registration) {
  registrations.value = [...(registrations.value ?? []), registration]
  const { first_name, last_name } = registration.lifter
  notifications.success(`Prijava je spremljena: ${first_name} ${last_name}.`)
}

const { changeStatus } = useStatusChange({
  compId: () => props.competition.id,
  onChanged: replaceRow,
  onStale: () => {
    load()
    emit('stale')
  },
})
</script>

<template>
  <RegistrationForm
    v-if="allowed.register"
    :comp-id="competition.id"
    :registered-lifter-ids="registeredLifterIds"
    @created="onCreated"
    @stale="emit('stale')"
  />
  <p v-else class="note">{{ REASONS.register }}</p>

  <h2>Prijave kluba</h2>
  <p v-if="!registrations && pending" class="state" aria-busy="true">Učitavanje prijava…</p>
  <div v-else-if="!registrations && error" class="state" role="alert">
    <p>Prijave se trenutno ne mogu učitati.</p>
    <button class="btn btn-secondary" type="button" @click="load">Pokušaj ponovno</button>
  </div>
  <p v-else-if="registrations?.length === 0" class="state">Klub još nema prijava na ovo natjecanje.</p>
  <template v-else-if="registrations">
    <p v-if="!allowed.changeStatus" id="change-reason" class="note">{{ REASONS.changeStatus }}</p>
    <TableScroll label="Prijave kluba">
      <table>
        <thead>
          <tr>
            <th scope="col">Natjecatelj</th>
            <th scope="col">Kategorija</th>
            <th scope="col">Zbroj</th>
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
              <!-- Onemogućen, a ne skriven: radnja je postojala, a razlog stoji iznad tablice -->
              <button
                class="btn btn-secondary btn-small"
                type="button"
                :disabled="!allowed.changeStatus"
                :aria-describedby="allowed.changeStatus ? undefined : 'change-reason'"
                @click="changeStatus(r)"
              >
                {{ r.status === 'active' ? 'Odjavi' : 'Vrati prijavu' }}
                <span class="sr-only">{{ r.lifter.first_name }} {{ r.lifter.last_name }}</span>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </TableScroll>
  </template>
</template>
