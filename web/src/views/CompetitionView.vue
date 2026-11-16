<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
// Parametar adrese je uvijek tekst; ruta propušta samo znamenke (router/index.ts)
const compId = computed(() => Number(route.params.compId))
</script>

<template>
  <div class="page-header">
    <h1>Natjecanje {{ compId }}</h1>
  </div>
  <p class="lead">Podatci o natjecanju i prijave natjecatelja.</p>
</template>
