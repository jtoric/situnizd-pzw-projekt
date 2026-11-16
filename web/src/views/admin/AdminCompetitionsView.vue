<script setup lang="ts">
import { onMounted } from 'vue'

import { fetchCompetitions } from '@/api/competitions'
import { useRequest } from '@/composables/useRequest'
import { formatDate, formatDateTime, PHASE_LABELS } from '@/lib/format'

const { data: competitions, pending, error, run: load } = useRequest(fetchCompetitions)
onMounted(load)
</script>

<template>
  <div class="page-header">
    <h2>Natjecanja</h2>
    <RouterLink class="btn" :to="{ name: 'admin-competition-new' }">+ Dodaj natjecanje</RouterLink>
  </div>

  <p v-if="!competitions && pending" class="state" aria-busy="true">Učitavanje natjecanja…</p>
  <div v-else-if="!competitions && error" class="state" role="alert">
    <p>Natjecanja se trenutno ne mogu učitati.</p>
    <button class="btn btn-secondary" type="button" @click="load">Pokušaj ponovno</button>
  </div>
  <p v-else-if="competitions?.length === 0" class="state">
    Još nema natjecanja.
    <RouterLink :to="{ name: 'admin-competition-new' }">Dodajte prvo.</RouterLink>
  </p>
  <div v-else-if="competitions" class="table-wrap">
    <table>
      <thead>
        <tr>
          <th scope="col">Natjecanje</th>
          <th scope="col">Datum</th>
          <th scope="col">Preliminarni rok</th>
          <th scope="col">Konačni rok</th>
          <th scope="col">Razdoblje</th>
          <th scope="col"><span class="sr-only">Radnje</span></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="c in competitions" :key="c.id">
          <td>
            <RouterLink :to="{ name: 'competition', params: { compId: c.id } }">{{ c.name }}</RouterLink>
          </td>
          <td>{{ formatDate(c.date) }}</td>
          <td>{{ formatDateTime(c.prelim_deadline) }}</td>
          <td>{{ formatDateTime(c.final_deadline) }}</td>
          <td>{{ PHASE_LABELS[c.phase] }}</td>
          <td class="actions">
            <RouterLink :to="{ name: 'admin-competition-edit', params: { compId: c.id } }">
              Uredi<span class="sr-only"> natjecanje {{ c.name }}</span>
            </RouterLink>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
