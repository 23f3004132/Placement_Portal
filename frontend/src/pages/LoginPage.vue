<template>
  <div class="full-page-center theme-gradient-bg">
    <div class="auth-card">
      <h1 class="auth-title"> Placement Portal</h1>
      <p class="auth-subtitle">Sign in to your account</p>

      <div v-if="error" class="auth-error">{{ error }}</div>

      <form @submit.prevent="handleLogin">
        <div class="auth-form-group">
          <label>Email Address</label>
          <input v-model="form.email" type="email" class="auth-field"
            placeholder="you@example.com" required autocomplete="email" />
        </div>
        <div class="auth-form-group">
          <label>Password</label>
          <input v-model="form.password" type="password" class="auth-field"
            placeholder="••••••••" required autocomplete="current-password" />
        </div>
        <button type="submit" class="auth-submit" :disabled="loading">
          {{ loading ? 'Signing in…' : 'Login' }}
        </button>
      </form>

      <p class="auth-footer">
        New here?
        <router-link to="/register">Create an account</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useStore }  from 'vuex'
import { useRouter } from 'vue-router'

const store = useStore()
const router  = useRouter()
const loading = ref(false)
const error = ref('')
const form = ref({ email: '', password: '' })

async function handleLogin() {
  loading.value = true
  error.value = ''
  try {
    await store.dispatch('login', form.value)
    router.push(store.getters.dashboardRoute)
  } catch (e) {
    error.value = e.message || 'Login failed. Check your credentials.'
  } finally {
    loading.value = false
  }
}
</script>
