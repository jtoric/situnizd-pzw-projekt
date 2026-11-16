<script setup lang="ts">
import AppNav from '@/components/AppNav.vue'
</script>

<template>
  <a class="skip-link" href="#main">Preskoči na sadržaj</a>
  <AppNav />
  <!-- Sve izvan RouterView ostaje na zaslonu pri promjeni adrese -->
  <main id="main" class="container" tabindex="-1">
    <RouterView />
  </main>
</template>
