<script setup lang="ts">
// Zajednički okvir svih ruta pod /admin: naslov i podizbornik, a ispod njih prikaz djeteta
</script>

<template>
  <div class="page-header">
    <h1>Administracija</h1>
  </div>
  <nav class="sub-nav" aria-label="Administracija">
    <RouterLink :to="{ name: 'admin-competitions' }">Natjecanja</RouterLink>
    <RouterLink :to="{ name: 'admin-clubs' }">Klubovi</RouterLink>
  </nav>
  <RouterView />
</template>

<style scoped>
.sub-nav { display: flex; gap: 8px; margin-bottom: 16px; border-bottom: 1px solid var(--line); }
.sub-nav a { padding: 8px 12px; text-decoration: none; border-bottom: 3px solid transparent; }
.sub-nav a.router-link-active { border-bottom-color: var(--ink); font-weight: 600; }
</style>
