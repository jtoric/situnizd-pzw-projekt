<script setup lang="ts">
import { onMounted, ref } from 'vue'

import { fetchCompetitions } from '@/api/competitions'
import type { Competition } from '@/api/types'

const competitions = ref<Competition[]>([])
const loading = ref(false)

// await zaustavlja samo ovu funkciju; prikaz se za to vrijeme iscrtava i odgovara na klikove
async function load() {
  loading.value = true
  try {
    competitions.value = await fetchCompetitions()
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <div class="page-header">
    <h1>Natjecanja</h1>
  </div>
  <p class="lead">Natjecanja na koja klub prijavljuje natjecatelje, s rokovima prijave.</p>
  <p v-if="loading">Učitavanje…</p>
  <ul v-else class="list">
    <li v-for="c in competitions" :key="c.id">
      <RouterLink :to="{ name: 'competition', params: { compId: c.id } }">{{ c.name }}</RouterLink>
      <span class="meta">{{ c.location }}, {{ c.date }}</span>
    </li>
  </ul>
</template>

<style scoped>
.list { padding: 0; list-style: none; display: grid; gap: 8px; }
.list li { display: flex; flex-wrap: wrap; gap: 4px 12px; padding: 12px 16px; background: var(--surface); border: 1px solid var(--line); border-radius: var(--radius); }
.meta { color: var(--muted); }
</style>
