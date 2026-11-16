<script setup lang="ts">
// Obavijesti iz stores/notifications.ts; stoji u App.vue, pa je vidljiva na svakoj stranici
import { useNotificationsStore } from '@/stores/notifications'

const notifications = useNotificationsStore()
</script>

<template>
  <!-- aria-live: čitač zaslona pročita obavijest kad se pojavi, bez pomicanja fokusa -->
  <div class="notices" aria-live="polite">
    <div v-for="n in notifications.items" :key="n.id" class="notice" :class="n.kind">
      <span>{{ n.text }}</span>
      <button type="button" class="close" @click="notifications.dismiss(n.id)">
        <span aria-hidden="true">×</span>
        <span class="sr-only">Zatvori obavijest</span>
      </button>
    </div>
  </div>
</template>

<style scoped>
.notices {
  position: fixed;
  right: 16px;
  bottom: 16px;
  z-index: 20;
  display: grid;
  gap: 8px;
  width: min(420px, calc(100vw - 32px));
}
.notice {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px 12px 12px 16px;
  border-radius: var(--radius);
  border-left: 4px solid;
  background: var(--surface);
  box-shadow: 0 4px 16px rgb(0 0 0 / 15%);
}
.notice.success { border-color: var(--success); }
.notice.error { border-color: var(--danger); }
.notice span:first-child { flex: 1; }
.close {
  min-width: 32px;
  min-height: 32px;
  border: 0;
  background: transparent;
  color: var(--muted);
  font-size: 20px;
  line-height: 1;
  cursor: pointer;
}
</style>
