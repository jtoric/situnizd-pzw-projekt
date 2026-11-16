<script setup lang="ts">
/**
 * Polje obrasca: oznaka, unos i poruka o pogrešci, povezani tako da ih čitač zaslona čita
 * zajedno. Koristi se kao obično polje: <FormField v-model="form.first_name" id="first-name" ... />.
 */
import { computed } from 'vue'

// defineModel: vrijednost dolazi iz v-model roditelja, a upis u nju šalje događaj
// update:modelValue; komponenta tako ne mijenja vrijednost koju je dobila
const model = defineModel<string>({ required: true })

const props = defineProps<{
  /** id elementa input; oznaka i poruka vežu se na njega */
  id: string
  label: string
  /** poruka o pogrešci; prazno ili izostavljeno znači da je polje ispravno */
  error?: string
  type?: 'text' | 'date' | 'number' | 'password'
  autocomplete?: string
  required?: boolean
}>()

const errorId = computed(() => `${props.id}-error`)
</script>

<template>
  <div class="field">
    <label :for="id">{{ label }}</label>
    <!-- aria-invalid i aria-describedby: čitač zaslona uz polje pročita i poruku o pogrešci -->
    <input
      :id="id"
      v-model="model"
      :type="type ?? 'text'"
      :autocomplete="autocomplete"
      :required="required"
      :aria-invalid="error ? 'true' : undefined"
      :aria-describedby="error ? errorId : undefined"
    />
    <p v-if="error" :id="errorId" class="field-error">{{ error }}</p>
  </div>
</template>
