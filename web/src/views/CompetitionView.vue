<script setup lang="ts">
/**
 * Jedno natjecanje: podatci, rokovi i prijave. Klub ovdje prijavljuje i odjavljuje svoje
 * natjecatelje (ClubRegistrations), a organizator pregledava prijave svih klubova
 * (AdminRegistrations). Isti API iza obaju prikaza vraća različite popise prema ulozi.
 */
import { computed, onBeforeUnmount, watch } from 'vue'
import { useRoute } from 'vue-router'

import { fetchCompetition } from '@/api/competitions'
import AdminRegistrations from '@/components/AdminRegistrations.vue'
import ClubRegistrations from '@/components/ClubRegistrations.vue'
import { useRequest } from '@/composables/useRequest'
import { formatDate, formatDateTime, PHASE_LABELS } from '@/lib/format'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const auth = useAuthStore()

// Parametar adrese je uvijek tekst; ruta propušta samo znamenke (router/index.ts)
const compId = computed(() => Number(route.params.compId))

const { data: competition, pending, error, run: load } = useRequest(() => fetchCompetition(compId.value))

// watch, a ne onMounted: prijelaz na drugo natjecanje zadržava istu instancu komponente
watch(compId, load, { immediate: true })

// Razdoblje je pročitano pri otvaranju stranice. Kad poslužitelj radnju odbije zbog roka, ono je
// zastarjelo, pa se natjecanje dohvaća ponovno i gumbi se usklađuju s novim razdobljem.
// Isto vrijedi kad se korisnik vrati na karticu koju je ostavio otvorenu.
function refreshWhenVisible() {
  if (document.visibilityState === 'visible' && competition.value) load()
}
document.addEventListener('visibilitychange', refreshWhenVisible)
onBeforeUnmount(() => document.removeEventListener('visibilitychange', refreshWhenVisible))
</script>

<template>
  <p v-if="!competition && pending" class="state" aria-busy="true">Učitavanje natjecanja…</p>
  <div v-else-if="!competition && error" class="state" role="alert">
    <p v-if="error.status === 404">Natjecanje nije pronađeno.</p>
    <template v-else>
      <p>Natjecanje se trenutno ne može učitati.</p>
      <button class="btn btn-secondary" type="button" @click="load">Pokušaj ponovno</button>
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

    <template v-if="auth.isAdmin">
      <h2>Prijave svih klubova</h2>
      <AdminRegistrations :competition="competition" @stale="load" />
    </template>
    <ClubRegistrations v-else :competition="competition" @stale="load" />
  </template>
</template>

<style scoped>
.phase { padding: 2px 10px; border-radius: 999px; background: var(--tint); color: var(--ink); font-weight: 600; }
.facts { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; margin: 0 0 8px; }
.facts div { background: var(--surface); border: 1px solid var(--line); border-radius: var(--radius); padding: 12px 16px; }
.facts dt { color: var(--muted); font-size: 14px; }
.facts dd { margin: 0; font-weight: 600; }
</style>
