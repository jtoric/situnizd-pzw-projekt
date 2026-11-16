<script setup lang="ts">
// Glavna navigacija; stoji u App.vue, izvan RouterView, pa ostaje pri svakoj promjeni adrese
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
// Poveznica vodi na prvu karticu administracije, a istaknuta je na svakoj ruti pod /admin
const inAdmin = computed(() => route.path.startsWith('/admin'))
</script>

<template>
  <header class="nav-bar">
    <nav class="nav-inner" aria-label="Glavna navigacija">
      <RouterLink class="brand" :to="{ name: 'competitions' }">Prijave na natjecanja</RouterLink>
      <ul class="links">
        <li><RouterLink :to="{ name: 'competitions' }">Natjecanja</RouterLink></li>
        <li><RouterLink :to="{ name: 'lifters' }">Natjecatelji</RouterLink></li>
        <li>
          <RouterLink :to="{ name: 'admin-competitions' }" :class="{ 'router-link-active': inAdmin }">
            Administracija
          </RouterLink>
        </li>
      </ul>
    </nav>
  </header>
</template>

<style scoped>
.nav-bar { background: var(--ink); color: #fff; }
.nav-inner {
  max-width: 1040px;
  margin: 0 auto;
  padding: 0 16px;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 4px 24px;
  min-height: 56px;
}
.brand { color: #fff; font-weight: 600; text-decoration: none; }
.links { display: flex; flex-wrap: wrap; gap: 4px 16px; margin: 0; padding: 0; list-style: none; }
.links a { color: #fff; text-decoration: none; padding: 4px 0; border-bottom: 2px solid transparent; }
.links a:hover { border-bottom-color: rgb(255 255 255 / 60%); }
/* RouterLink postavlja aria-current="page" na poveznicu trenutne stranice */
.links a[aria-current='page'],
.links a.router-link-active { border-bottom-color: #fff; }
.nav-bar :focus-visible { outline-color: #fff; }
</style>
