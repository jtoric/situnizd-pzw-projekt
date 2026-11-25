<script setup lang="ts">
/**
 * Okvir tablice koji se na uskom zaslonu pomiče vodoravno, pa redak ostaje jedan redak.
 *
 * Okvir koji se pomiče mora biti dostupan i tipkovnici (WCAG 2.1.1): tabindex mu daje fokus, a
 * strelice ga tada pomiču. role="region" i oznaka kažu čitaču zaslona što je u okviru.
 */
defineProps<{
  /** što tablica prikazuje, npr. "Natjecatelji kluba" */
  label: string
}>()
</script>

<template>
  <div class="table-wrap" tabindex="0" role="region" :aria-label="label">
    <slot />
  </div>
</template>
