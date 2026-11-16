<script setup lang="ts">
import { onMounted, ref } from 'vue'

import { ApiError } from '@/api/http'
import { deleteLifter } from '@/api/lifters'
import type { Lifter } from '@/api/types'
import ConfirmDialog from '@/components/ConfirmDialog.vue'
import TableScroll from '@/components/TableScroll.vue'
import { formatDate, GENDER_LABELS } from '@/lib/format'
import { useAuthStore } from '@/stores/auth'
import { useLiftersStore } from '@/stores/lifters'
import { useNotificationsStore } from '@/stores/notifications'

const auth = useAuthStore()
const lifters = useLiftersStore()
const notifications = useNotificationsStore()

// Popis u pohrani prikazuje se odmah, a dohvat ga osvježava. Neuspjeh se prikazuje ovdje
// (lifters.failed), pa se iznimka ne prosljeđuje globalnom rukovatelju kao druga poruka.
function load() {
  lifters.load().catch(() => {})
}

onMounted(load)

// Brisanje se ne može poništiti, pa prvi klik samo otvara potvrdu s imenom natjecatelja:
// korisnik u tom trenutku gleda dijalog, a ne redak u kojem je kliknuo
const toDelete = ref<Lifter | null>(null)

async function confirmDelete() {
  const lifter = toDelete.value
  if (!lifter) return
  toDelete.value = null
  try {
    await deleteLifter(auth.clubId!, lifter.id)
    lifters.remove(lifter.id)
    notifications.success(`Natjecatelj ${lifter.first_name} ${lifter.last_name} je obrisan.`)
  } catch (e) {
    // Natjecatelj s prijavama se ne briše; poruka poslužitelja kaže zašto
    if (e instanceof ApiError && e.code === 'has_registrations') notifications.error(e.message)
    else throw e
  }
}
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
    <TableScroll label="Natjecatelji kluba">
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
              <button class="link-danger" type="button" @click="toDelete = l">
                Obriši<span class="sr-only"> natjecatelja {{ l.first_name }} {{ l.last_name }}</span>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </TableScroll>
  </template>

  <ConfirmDialog
    :open="toDelete !== null"
    title="Brisanje natjecatelja"
    confirm-label="Obriši"
    danger
    @confirm="confirmDelete"
    @cancel="toDelete = null"
  >
    <p>
      Natjecatelj <strong>{{ toDelete?.first_name }} {{ toDelete?.last_name }}</strong> bit će
      obrisan. Brisanje se ne može poništiti.
    </p>
  </ConfirmDialog>
</template>

<style scoped>
.link-danger {
  margin-left: 16px;
  padding: 0;
  border: 0;
  background: none;
  color: var(--danger);
  font: inherit;
  text-decoration: underline;
  cursor: pointer;
}
</style>
