<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { ApiError } from '@/api/http'
import { safeRedirect } from '@/lib/navigation'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

const username = ref('')
const password = ref('')
const error = ref('')
const pending = ref(false)

async function submit() {
  error.value = ''
  pending.value = true
  try {
    await auth.login(username.value.trim(), password.value)
    // replace, a ne push: povratak unatrag na obrazac za prijavu prijavljenom korisniku ne treba
    await router.replace(safeRedirect(route.query.redirect))
  } catch (e) {
    if (!(e instanceof ApiError)) throw e
    // Poruka poslužitelja ista je za nepoznato ime i za krivu lozinku, pa ne otkriva postoji li račun
    error.value = e.message
  } finally {
    pending.value = false
  }
}
</script>

<template>
  <div class="login card">
    <h1>Prijava</h1>
    <p class="lead">Prijava za klubove i organizatora natjecanja.</p>
    <!-- .prevent: bez njega preglednik šalje obrazac sam i učitava stranicu ispočetka -->
    <form @submit.prevent="submit">
      <div class="field">
        <label for="username">Korisničko ime</label>
        <input id="username" v-model="username" autocomplete="username" required />
      </div>
      <div class="field">
        <label for="password">Lozinka</label>
        <input
          id="password"
          v-model="password"
          type="password"
          autocomplete="current-password"
          required
        />
      </div>
      <p v-if="error" class="form-error" role="alert">{{ error }}</p>
      <button class="btn" type="submit" :disabled="pending">
        {{ pending ? 'Prijava u tijeku…' : 'Prijavi se' }}
      </button>
    </form>
  </div>
</template>

<style scoped>
.login { max-width: 400px; margin: 32px auto; padding: 24px; }
.login .btn { width: 100%; justify-content: center; }
</style>
