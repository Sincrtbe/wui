<template>
  <div class="login-page">
    <div class="login-box">
      <h1>🎬 WUI</h1>
      <p class="subtitle">Automatización Multimedia para YouTube</p>

      <div v-if="error" class="alert error">{{ error }}</div>

      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label>Email</label>
          <input v-model="form.email" type="email" placeholder="tu@email.com" required />
        </div>
        <div class="form-group">
          <label>Contraseña</label>
          <input v-model="form.password" type="password" placeholder="••••••••" required />
        </div>
        <button type="submit" class="primary" :disabled="loading">
          {{ loading ? 'Entrando...' : 'Iniciar sesión' }}
        </button>
      </form>

      <p class="register-link">
        ¿No tienes cuenta? <a href="#" @click.prevent="showRegister = !showRegister">Regístrate</a>
      </p>

      <div v-if="showRegister">
        <hr style="margin: 1.5rem 0; border-color: #2a2d3a;" />
        <h3 style="color:#e0e0e0; margin-bottom:1rem;">Crear cuenta</h3>
        <form @submit.prevent="handleRegister">
          <div class="form-group">
            <label>Nombre</label>
            <input v-model="regForm.name" type="text" required />
          </div>
          <div class="form-group">
            <label>Email</label>
            <input v-model="regForm.email" type="email" required />
          </div>
          <div class="form-group">
            <label>Contraseña <small>(mín. 8 caracteres)</small></label>
            <input v-model="regForm.password" type="password" minlength="8" required />
          </div>
          <button type="submit" class="primary" :disabled="loading">
            {{ loading ? 'Creando...' : 'Crear cuenta' }}
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { apiFetch, setToken } from '../main.js'

const router = useRouter()
const loading = ref(false)
const error = ref(null)
const showRegister = ref(false)
const form = reactive({ email: '', password: '' })
const regForm = reactive({ name: '', email: '', password: '' })

async function handleLogin() {
  loading.value = true
  error.value = null
  try {
    const data = await apiFetch('/api/v3/auth/login', {
      method: 'POST',
      body: JSON.stringify(form),
    })
    setToken(data.access_token)
    router.push('/dashboard')
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

async function handleRegister() {
  loading.value = true
  error.value = null
  try {
    const data = await apiFetch('/api/v3/auth/register', {
      method: 'POST',
      body: JSON.stringify(regForm),
    })
    setToken(data.access_token)
    router.push('/dashboard')
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page { display: flex; align-items: center; justify-content: center; min-height: 80vh; }
.login-box { background: #1a1d27; border: 1px solid #2a2d3a; border-radius: 12px; padding: 2.5rem; width: 100%; max-width: 400px; }
.login-box h1 { text-align: center; color: #6366f1; margin-bottom: 0.25rem; }
.subtitle { text-align: center; color: #666; font-size: 0.9rem; margin-bottom: 2rem; }
.login-box form { display: flex; flex-direction: column; }
.login-box button.primary { width: 100%; margin-top: 0.5rem; padding: 0.75rem; }
.register-link { text-align: center; margin-top: 1.5rem; font-size: 0.9rem; color: #666; }
</style>
