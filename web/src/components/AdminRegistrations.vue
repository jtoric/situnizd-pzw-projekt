<script setup lang="ts">
/**
 * Prijave svih klubova na jedno natjecanje, za organizatora: filtar po stanju, stranice,
 * pretraga, razvrstavanje i izvoz u CSV.
 *
 * Podjela posla s poslužiteljem:
 * - filtar po stanju i stranice su parametri zahtjeva (status, limit, offset): biraju koje
 *   zapise poslužitelj vraća, pa vrijede za cijeli popis. Stoje u adresi (?stanje=, ?stranica=),
 *   da se filtrirani popis može poslati poveznicom, a tipka Natrag vraća na istu stranicu.
 * - pretraga i razvrstavanje rade se u pregledniku, nad prikazanom stranicom. API ih ne nudi,
 *   pa obuhvaćaju samo nju; to piše i uz polje za pretragu.
 */
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { fetchAllRegistrations, fetchRegistrations } from '@/api/registrations'
import type { Competition, Registration, RegistrationStatus } from '@/api/types'
import StatusBadge from '@/components/StatusBadge.vue'
import TableScroll from '@/components/TableScroll.vue'
import { useRequest } from '@/composables/useRequest'
import { useStatusChange } from '@/composables/useStatusChange'
import { categoryLabel } from '@/lib/categories'
import { toCsv } from '@/lib/csv'
import { downloadText } from '@/lib/download'
import { formatDateTime, STATUS_LABELS } from '@/lib/format'
import { pageFromQuery, pageRequest, PAGE_SIZE, splitPage } from '@/lib/pager'
import { allowedActions, REASONS } from '@/lib/phase'
import { matchesQuery, sortRegistrations, type SortDir, type SortKey } from '@/lib/sort'

const props = defineProps<{ competition: Competition }>()
const emit = defineEmits<{ stale: [] }>()

const route = useRoute()
const router = useRouter()

// ---------- Filtar i stranica: u adresi ----------
const STATUS_VALUES: RegistrationStatus[] = ['active', 'withdrawn']
// Nevaljana vrijednost u adresi (?stanje=xyz) znači "bez filtra", a ne zahtjev s 422
const status = computed<RegistrationStatus | undefined>(() =>
  STATUS_VALUES.find((s) => s === route.query.stanje),
)
const page = computed(() => pageFromQuery(route.query.stranica))

function setStatus(value: string) {
  // replace: promjena filtra ne dodaje korak u povijest; stranica se vraća na prvu
  router.replace({ query: { ...route.query, stanje: value || undefined, stranica: undefined } })
}

const pageLink = (n: number) => ({ query: { ...route.query, stranica: n === 1 ? undefined : n } })

// ---------- Dohvat ----------
const { data, pending, error, run: load } = useRequest(() =>
  fetchRegistrations(props.competition.id, { status: status.value, ...pageRequest(page.value) }),
)
watch([() => props.competition.id, status, page], load, { immediate: true })

const current = computed(() => splitPage(data.value ?? [], PAGE_SIZE))

// ---------- Pretraga i razvrstavanje: nad prikazanom stranicom ----------
const query = ref('')
const sortKey = ref<SortKey>('name')
const sortDir = ref<SortDir>('asc')

// Niz izvedenih vrijednosti: odgovor -> stranica -> pretraga -> poredak -> prikaz
const searched = computed(() =>
  current.value.rows.filter((r) => matchesQuery(`${r.lifter.first_name} ${r.lifter.last_name}`, query.value)),
)
const shown = computed(() => sortRegistrations(searched.value, sortKey.value, sortDir.value))

function sortBy(key: SortKey) {
  if (sortKey.value === key) sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc'
  else {
    sortKey.value = key
    sortDir.value = 'asc'
  }
}

const ariaSort = (key: SortKey) =>
  sortKey.value === key ? (sortDir.value === 'asc' ? 'ascending' : 'descending') : undefined

// ---------- Radnje ----------
const allowed = computed(() => allowedActions(props.competition.phase))

function replaceRow(updated: Registration) {
  // Uz filtar po stanju odjavljena prijava više ne pripada popisu, pa se dohvaća ponovno
  if (status.value) load()
  else data.value = (data.value ?? []).map((r) => (r.id === updated.id ? updated : r))
}

const { changeStatus } = useStatusChange({
  compId: () => props.competition.id,
  onChanged: replaceRow,
  onStale: () => {
    load()
    emit('stale')
  },
})

// ---------- Izvoz ----------
const exporting = ref(false)

async function exportCsv() {
  exporting.value = true
  try {
    // Cijeli popis uz isti filtar, a ne samo stranica na zaslonu
    const all = await fetchAllRegistrations(props.competition.id, status.value)
    const rows: (string | number)[][] = [
      ['Prezime', 'Ime', 'Kategorija', 'Zbroj (kg)', 'Stanje', 'Prijavljeno'],
      ...sortRegistrations(all, 'name', 'asc').map((r) => [
        r.lifter.last_name,
        r.lifter.first_name,
        r.category,
        r.total,
        STATUS_LABELS[r.status],
        formatDateTime(r.registered_at),
      ]),
    ]
    downloadText(`prijave-${props.competition.date}.csv`, toCsv(rows), 'text/csv;charset=utf-8')
  } finally {
    exporting.value = false
  }
}
</script>

<template>
  <div class="toolbar">
    <div class="field">
      <label for="filter-status">Stanje</label>
      <select id="filter-status" :value="status ?? ''" @change="setStatus(($event.target as HTMLSelectElement).value)">
        <option value="">sve prijave</option>
        <option value="active">aktivne</option>
        <option value="withdrawn">odjavljene</option>
      </select>
    </div>
    <div class="field search">
      <label for="filter-query">Pretraga po imenu</label>
      <input id="filter-query" v-model="query" type="search" aria-describedby="filter-query-hint" />
      <p id="filter-query-hint" class="hint">Pretražuje samo prikazanu stranicu.</p>
    </div>
    <button class="btn btn-secondary" type="button" :disabled="exporting" @click="exportCsv">
      {{ exporting ? 'Izvoz u tijeku…' : 'Preuzmi CSV' }}
    </button>
  </div>

  <p v-if="!data && pending" class="state" aria-busy="true">Učitavanje prijava…</p>
  <div v-else-if="!data && error" class="state" role="alert">
    <p>Prijave se trenutno ne mogu učitati.</p>
    <button class="btn btn-secondary" type="button" @click="load">Pokušaj ponovno</button>
  </div>
  <!-- Prazno zbog filtra nije isto što i prazno natjecanje: prva poruka kaže da se filtar može ublažiti -->
  <p v-else-if="current.rows.length === 0" class="state">
    {{ status ? 'Nijedna prijava nema odabrano stanje.' : 'Još nema prijava na ovo natjecanje.' }}
  </p>
  <template v-else>
    <p v-if="!allowed.changeStatus" id="admin-change-reason" class="note">{{ REASONS.changeStatus }}</p>
    <TableScroll label="Prijave svih klubova" :aria-busy="pending">
      <table>
        <caption class="sr-only">Prijave, stranica {{ page }}</caption>
        <thead>
          <tr>
            <th scope="col" :aria-sort="ariaSort('name')">
              <button class="sort" type="button" @click="sortBy('name')">Natjecatelj</button>
            </th>
            <th scope="col" :aria-sort="ariaSort('category')">
              <button class="sort" type="button" @click="sortBy('category')">Kategorija</button>
            </th>
            <th scope="col" :aria-sort="ariaSort('total')">
              <button class="sort" type="button" @click="sortBy('total')">Zbroj</button>
            </th>
            <th scope="col">Prijavljeno</th>
            <th scope="col">Stanje</th>
            <th scope="col"><span class="sr-only">Radnje</span></th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="shown.length === 0">
            <td colspan="6">Na ovoj stranici nijedno ime ne odgovara pretrazi.</td>
          </tr>
          <tr v-for="r in shown" :key="r.id">
            <td>{{ r.lifter.last_name }}, {{ r.lifter.first_name }}</td>
            <td>{{ categoryLabel(r.category) }}</td>
            <td>{{ r.total }} kg</td>
            <td>{{ formatDateTime(r.registered_at) }}</td>
            <td><StatusBadge :status="r.status" /></td>
            <td class="actions">
              <button
                class="btn btn-secondary btn-small"
                type="button"
                :disabled="!allowed.changeStatus"
                :aria-describedby="allowed.changeStatus ? undefined : 'admin-change-reason'"
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

  <!-- Gumb koji nema kamo voditi ostaje na mjestu, da se ostatak retka ne pomiče -->
  <nav v-if="page > 1 || current.hasNext" class="pager" aria-label="Stranice prijava">
    <RouterLink v-if="page > 1" :to="pageLink(page - 1)">Prethodna</RouterLink>
    <span v-else class="disabled" aria-hidden="true">Prethodna</span>
    <span aria-current="page">Stranica {{ page }}</span>
    <RouterLink v-if="current.hasNext" :to="pageLink(page + 1)">Sljedeća</RouterLink>
    <span v-else class="disabled" aria-hidden="true">Sljedeća</span>
  </nav>
</template>

<style scoped>
.toolbar { display: flex; flex-wrap: wrap; align-items: flex-start; gap: 0 16px; margin-bottom: 8px; }
.toolbar .btn { margin-top: 28px; }
.search { flex: 1 1 220px; }
.hint { margin: 0; color: var(--muted); font-size: 14px; }
.sort {
  padding: 0;
  border: 0;
  background: none;
  color: inherit;
  font: inherit;
  font-weight: 600;
  cursor: pointer;
}
th[aria-sort='ascending'] .sort::after { content: ' ▲'; }
th[aria-sort='descending'] .sort::after { content: ' ▼'; }
.pager { display: flex; align-items: center; gap: 16px; margin-top: 16px; }
.pager .disabled { color: var(--muted); opacity: 0.6; }
</style>
