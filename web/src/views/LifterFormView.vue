<script setup lang="ts">
/**
 * Dodavanje i uređivanje natjecatelja; ista stranica za /natjecatelji/novi i /natjecatelji/:id.
 *
 * Obrazac prvo provjerava sam (lib/validation.ts), pa tek ispravan šalje. Pogreške poslužitelja
 * (422) prikazuju se na istom mjestu kao i vlastite, uz polje na koje se odnose.
 */
import { computed, nextTick, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { ApiError } from '@/api/http'
import { createLifter, fetchLifter, updateLifter } from '@/api/lifters'
import type { Lifter, LifterInput } from '@/api/types'
import FormField from '@/components/FormField.vue'
import { changedFields } from '@/lib/diff'
import { toFieldErrors } from '@/lib/errors'
import { localToday, validateLifter, type FieldErrors } from '@/lib/validation'
import { useAuthStore } from '@/stores/auth'
import { useLiftersStore } from '@/stores/lifters'
import { useNotificationsStore } from '@/stores/notifications'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const lifters = useLiftersStore()
const notifications = useNotificationsStore()

const lifterId = computed(() =>
  route.params.lifterId === undefined ? null : Number(route.params.lifterId),
)
const isEdit = computed(() => lifterId.value !== null)

const emptyForm = (): LifterInput => ({ first_name: '', last_name: '', birth_date: '', gender: 'M' })
const form = reactive<LifterInput>(emptyForm())
// Stanje kakvo je stiglo s poslužitelja; izmjena šalje samo polja koja se od njega razlikuju
let original: LifterInput = emptyForm()

const errors = ref<FieldErrors>({})
const pending = ref(false)
const loadFailed = ref(false)

function fill(lifter: Lifter) {
  original = {
    first_name: lifter.first_name,
    last_name: lifter.last_name,
    birth_date: lifter.birth_date,
    gender: lifter.gender,
  }
  Object.assign(form, original)
}

// watch, a ne onMounted: prijelaz s jednog natjecatelja na drugog zadržava istu instancu
// komponente, pa se ona ne montira ponovno, a parametar u adresi se promijeni
watch(
  lifterId,
  async (id) => {
    errors.value = {}
    loadFailed.value = false
    if (id === null) {
      original = emptyForm()
      Object.assign(form, original)
      return
    }
    const cached = lifters.byId.get(id)
    if (cached) {
      fill(cached)
      return
    }
    try {
      const lifter = await fetchLifter(auth.clubId!, id)
      // Odgovor za natjecatelja s kojeg je korisnik u međuvremenu otišao se odbacuje
      if (lifterId.value === id) fill(lifter)
    } catch (e) {
      if (!(e instanceof ApiError)) throw e
      loadFailed.value = true
    }
  },
  { immediate: true },
)

// Fokus na prvo neispravno polje: korisnik tipkovnice i čitača zaslona ne mora tražiti pogrešku
function focusFirstError() {
  nextTick(() => document.querySelector<HTMLElement>('[aria-invalid="true"]')?.focus())
}

async function submit() {
  const input: LifterInput = {
    ...form,
    first_name: form.first_name.trim(),
    last_name: form.last_name.trim(),
  }
  errors.value = validateLifter(input, localToday())
  if (Object.keys(errors.value).length > 0) {
    focusFirstError()
    return
  }

  pending.value = true
  try {
    const clubId = auth.clubId!
    const saved =
      lifterId.value === null
        ? await createLifter(clubId, input)
        : await updateLifter(clubId, lifterId.value, changedFields(original, input))
    lifters.upsert(saved)
    notifications.success(isEdit.value ? 'Natjecatelj je spremljen.' : 'Natjecatelj je dodan.')
    await router.push({ name: 'lifters' })
  } catch (e) {
    // 422 je odgovor na ovaj obrazac, pa ga obrađuje ovaj prikaz; sve ostalo ide dalje
    if (e instanceof ApiError && e.code === 'validation_error') {
      errors.value = toFieldErrors(e.fieldErrors)
      focusFirstError()
      return
    }
    throw e
  } finally {
    pending.value = false
  }
}
</script>

<template>
  <div class="page-header">
    <h1>{{ isEdit ? 'Uređivanje natjecatelja' : 'Dodavanje natjecatelja' }}</h1>
  </div>

  <div v-if="loadFailed" class="state" role="alert">
    <p>Natjecatelj nije pronađen ili se trenutno ne može učitati.</p>
    <RouterLink :to="{ name: 'lifters' }">Na popis natjecatelja</RouterLink>
  </div>

  <!-- novalidate: provjeru radi lib/validation.ts, s porukama na hrvatskom uz svako polje -->
  <form v-else class="card form" novalidate @submit.prevent="submit">
    <FormField
      id="first-name"
      v-model="form.first_name"
      label="Ime"
      autocomplete="off"
      required
      :error="errors.first_name"
    />
    <FormField
      id="last-name"
      v-model="form.last_name"
      label="Prezime"
      autocomplete="off"
      required
      :error="errors.last_name"
    />
    <FormField
      id="birth-date"
      v-model="form.birth_date"
      label="Datum rođenja"
      type="date"
      required
      :error="errors.birth_date"
    />
    <div class="field">
      <label for="gender">Spol</label>
      <select
        id="gender"
        v-model="form.gender"
        :aria-invalid="errors.gender ? 'true' : undefined"
        :aria-describedby="errors.gender ? 'gender-error' : undefined"
      >
        <option value="M">muški</option>
        <option value="F">ženski</option>
      </select>
      <p v-if="errors.gender" id="gender-error" class="field-error">{{ errors.gender }}</p>
    </div>
    <div class="form-actions">
      <button class="btn" type="submit" :disabled="pending">
        {{ pending ? 'Spremanje…' : 'Spremi' }}
      </button>
      <RouterLink class="btn btn-secondary" :to="{ name: 'lifters' }">Odustani</RouterLink>
    </div>
  </form>
</template>

<style scoped>
.form { max-width: 480px; }
</style>
