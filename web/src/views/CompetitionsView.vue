<script setup lang="ts">
import { onMounted } from 'vue'

import { fetchCompetitions } from '@/api/competitions'
import TableScroll from '@/components/TableScroll.vue'
import { useRequest } from '@/composables/useRequest'
import { formatDate, formatDateTime, PHASE_LABELS } from '@/lib/format'

// Popis treba samo ovaj prikaz, pa stanje ostaje u komponenti, a ne u pohrani
const { data: competitions, pending, error, run: load } = useRequest(fetchCompetitions)

onMounted(load)
</script>

<template>
  <div class="page-header">
    <h1>Natjecanja</h1>
  </div>

  <p v-if="!competitions && pending" class="state" aria-busy="true">Učitavanje natjecanja…</p>
  <div v-else-if="!competitions && error" class="state" role="alert">
    <p>Natjecanja se trenutno ne mogu učitati. {{ error.message }}</p>
    <button class="btn btn-secondary" type="button" @click="load">Pokušaj ponovno</button>
  </div>
  <p v-else-if="competitions && competitions.length === 0" class="state">
    Još nema objavljenih natjecanja.
  </p>
  <TableScroll v-else-if="competitions" label="Natjecanja">
    <table>
      <thead>
        <tr>
          <th scope="col">Natjecanje</th>
          <th scope="col">Mjesto</th>
          <th scope="col">Datum</th>
          <th scope="col">Preliminarni rok</th>
          <th scope="col">Konačni rok</th>
          <th scope="col">Razdoblje</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="c in competitions" :key="c.id">
          <td>
            <RouterLink :to="{ name: 'competition', params: { compId: c.id } }">{{ c.name }}</RouterLink>
          </td>
          <td>{{ c.location }}</td>
          <td>{{ formatDate(c.date) }}</td>
          <td>{{ formatDateTime(c.prelim_deadline) }}</td>
          <td>{{ formatDateTime(c.final_deadline) }}</td>
          <td>{{ PHASE_LABELS[c.phase] }}</td>
        </tr>
      </tbody>
    </table>
  </TableScroll>
</template>
