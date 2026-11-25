<script setup lang="ts">
/**
 * Potvrda prije radnje koja se ne može poništiti.
 *
 * Gradi se na elementu <dialog> preglednika, otvorenom s showModal(). Preglednik tada sam
 * radi ono što bi se inače pisalo rukom: fokus premješta u dijalog i drži ga ondje, ostatak
 * stranice čini nedostupnim mišu, tipkovnici i čitaču zaslona, Escape zatvara dijalog, a fokus
 * se nakon zatvaranja vraća na gumb koji ga je otvorio. Dijalog se iscrtava u gornjem sloju,
 * iznad cijele stranice, pa ga ne odsijeca ni element s overflow: hidden u kojem stoji.
 */
import { onMounted, ref, useId, watch } from 'vue'

const props = defineProps<{
  open: boolean
  title: string
  /** natpis gumba koji izvodi radnju, npr. "Obriši"; glagol, ne "U redu" */
  confirmLabel: string
  /** crveni gumb za radnju koja briše */
  danger?: boolean
}>()

const emit = defineEmits<{ confirm: []; cancel: [] }>()

const dialog = ref<HTMLDialogElement | null>(null)
const titleId = useId()

function sync(open: boolean) {
  if (!dialog.value) return
  if (open && !dialog.value.open) dialog.value.showModal()
  if (!open && dialog.value.open) dialog.value.close()
}

watch(() => props.open, sync)
onMounted(() => sync(props.open))
</script>

<template>
  <!-- cancel: Escape; preglednik bi dijalog zatvorio sam, a roditelj mora znati da je odustao -->
  <dialog ref="dialog" class="dialog" :aria-labelledby="titleId" @cancel.prevent="emit('cancel')">
    <h2 :id="titleId">{{ title }}</h2>
    <slot />
    <div class="form-actions">
      <!-- Fokus pri otvaranju ide na Odustani: Enter tako ne izvodi radnju koja se ne poništava -->
      <button class="btn btn-secondary" type="button" autofocus @click="emit('cancel')">Odustani</button>
      <button class="btn" :class="{ 'btn-danger': danger }" type="button" @click="emit('confirm')">
        {{ confirmLabel }}
      </button>
    </div>
  </dialog>
</template>

<style scoped>
.dialog {
  width: min(480px, calc(100vw - 32px));
  padding: 24px;
  border: 0;
  border-radius: var(--radius);
  box-shadow: 0 12px 40px rgb(0 0 0 / 30%);
  color: var(--text);
}
.dialog::backdrop { background: rgb(12 20 33 / 55%); }
.dialog h2 { margin-top: 0; }
</style>
