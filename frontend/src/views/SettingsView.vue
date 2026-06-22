<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">⚙️ Ajustes</h1>
      <p class="page-subtitle">Configuración de tu cuenta y preferencias</p>
    </div>

    <div v-if="error" class="alert error">{{ error }}</div>
    <div v-if="success" class="alert success">{{ success }}</div>

    <div class="card">
      <div class="card-title">👤 Perfil</div>
      <form @submit.prevent="saveProfile">
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:1rem;">
          <div class="form-group">
            <label>Nombre</label>
            <input v-model="profile.name" required />
          </div>
          <div class="form-group">
            <label>Email</label>
            <input v-model="profile.email" type="email" required />
          </div>
        </div>
        <button type="submit" class="primary" :disabled="saving">Guardar perfil</button>
      </form>
    </div>

    <div class="card">
      <div class="card-title">🔒 Cambiar contraseña</div>
      <form @submit.prevent="changePassword">
        <div class="form-group">
          <label>Nueva contraseña <small>(mín. 8 caracteres)</small></label>
          <input v-model="passwordForm.new_password" type="password" minlength="8" required />
        </div>
        <button type="submit" class="primary" :disabled="saving">Cambiar</button>
      </form>
    </div>

    <div class="card">
      <div class="card-title">📊 Datos del sistema</div>
      <div style="font-size:0.9rem; color:#888; display:flex; flex-direction:column; gap:0.5rem;">
        <div>User ID: <span style="color:#6366f1; font-family:monospace;">{{ store.user?.id }}</span></div>
        <div>Miembro desde: <span style="color:#e0e0e0;">{{ store.user?.created_at ? new Date(store.user.created_at).toLocaleDateString() : 'N/A' }}</span></div>
        <div>Canales: <span style="color:#e0e0e0;">{{ channelCount }}</span></div>
        <div>Contenido: <span style="color:#e0e0e0;">{{ contentCount }}</span></div>
        <div>Prompts propios: <span style="color:#e0e0e0;">{{ promptCount }}</span></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useStore, apiFetch } from '../main.js'

const store = useStore()
const error = ref(null)
const success = ref(null)
const saving = ref(false)
const profile = reactive({ name: '', email: '' })
const passwordForm = reactive({ new_password: '' })
const channelCount = ref(0)
const contentCount = ref(0)
const promptCount = ref(0)

onMounted(async () => {
  if (store.user) {
    profile.name = store.user.name
    profile.email = store.user.email
  }
  try {
    const [channels, content, prompts] = await Promise.all([
      apiFetch('/api/v3/channels'),
      apiFetch('/api/v3/content'),
      apiFetch('/api/v3/prompts'),
    ])
    channelCount.value = channels.length
    contentCount.value = content.length
    promptCount.value = prompts.length
  } catch (e) {
    // Ignore
  }
})

async function saveProfile() {
  saving.value = true
  error.value = null
  success.value = null
  try {
    const updated = await apiFetch('/api/v3/auth/me', {
      method: 'PUT',
      body: JSON.stringify(profile),
    })
    store.user = updated
    success.value = 'Perfil actualizado'
  } catch (e) {
    error.value = e.message
  } finally {
    saving.value = false
  }
}

async function changePassword() {
  saving.value = true
  error.value = null
  success.value = null
  // NOTE: endpoint not implemented yet in auth.py — placeholder
  try {
    // await apiFetch('/api/v3/auth/password', { method: 'POST', body: JSON.stringify(passwordForm) })
    success.value = 'Función de cambio de contraseña no implementada aún'
  } catch (e) {
    error.value = e.message
  } finally {
    saving.value = false
  }
}
</script>
