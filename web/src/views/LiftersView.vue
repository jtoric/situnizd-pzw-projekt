<script setup lang="ts">
import { onMounted } from 'vue'

import { formatDate, GENDER_LABELS } from '@/lib/format'
import { useLiftersStore } from '@/stores/lifters'

const lifters = useLiftersStore()

// Popis u pohrani prikazuje se odmah, a dohvat ga osvježava. Neuspjeh se prikazuje ovdje
// (lifters.failed), pa se iznimka ne prosljeđuje globalnom rukovatelju kao druga poruka.
function load() {
  lifters.load().catch(() => {})
}

onMounted(load)
</script>

<template>
  <div class="page-header">
    <h1>Natjecatelji</h1>
    <RouterLink class="btn" :to="{ name: 'lifter-new' }">+ Dodaj natjecatelja</RouterLink>
  </div>

  <!-- Četiri stanja: prvi dohvat traje, prvi dohvat nije uspio, popis je prazan, popis ima zapise -->
  <p v-if="!lifters.loaded && lifters.pending" class="state" aria-busy="true">
    Učitavanje natjecatelja…
  </p>
  <div v-else-if="!lifters.loaded && lifters.failed" class="state" role="alert">
    <p>Natjecatelji se trenutno ne mogu učitati.</p>
    <button class="btn btn-secondary" type="button" @click="load">Pokušaj ponovno</button>
  </div>
  <p v-else-if="lifters.items.length === 0" class="state">
    Klub još nema natjecatelja.
    <RouterLink :to="{ name: 'lifter-new' }">Dodajte prvoga.</RouterLink>
  </p>
  <template v-else>
    <p v-if="lifters.failed" class="form-error" role="alert">
      Popis se nije mogao osvježiti, pa možda nije najnoviji.
    </p>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th scope="col">Prezime i ime</th>
            <th scope="col">Datum rođenja</th>
            <th scope="col">Spol</th>
            <th scope="col"><span class="sr-only">Radnje</span></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="l in lifters.items" :key="l.id">
            <td>{{ l.last_name }}, {{ l.first_name }}</td>
            <td>{{ formatDate(l.birth_date) }}</td>
            <td>{{ GENDER_LABELS[l.gender] }}</td>
            <td class="actions">
              <RouterLink :to="{ name: 'lifter-edit', params: { lifterId: l.id } }">
                Uredi<span class="sr-only"> natjecatelja {{ l.first_name }} {{ l.last_name }}</span>
              </RouterLink>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </template>
</template>
