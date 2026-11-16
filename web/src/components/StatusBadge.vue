<script setup lang="ts">
// Oznaka stanja prijave; isti izgled u popisu kluba i u tablici organizatora
import type { RegistrationStatus } from '@/api/types'
import { STATUS_LABELS } from '@/lib/format'

defineProps<{ status: RegistrationStatus }>()
</script>

<template>
  <!-- Stanje se čita iz teksta, ne samo iz boje (WCAG 1.4.1) -->
  <span class="badge" :class="status">{{ STATUS_LABELS[status] }}</span>
</template>

<style scoped>
.badge {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 999px;
  font-size: 14px;
  font-weight: 600;
}
.active { background: var(--success-soft); color: var(--success); }
.withdrawn { background: var(--tint); color: var(--muted); }
</style>
