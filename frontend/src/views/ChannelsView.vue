<template>
  <div>
    <div class="page-header" style="display:flex; justify-content:space-between; align-items:center;">
      <div>
        <h1 class="page-title">📡 Canales</h1>
        <p class="page-subtitle">Gestiona tus canales de YouTube</p>
      </div>
      <button class="primary" @click="showCreate = true">+ Nuevo canal</button>
    </div>

    <div v-if="error" class="alert error">{{ error }}</div>

    <!-- Create form -->
    <div v-if="showCreate" class="card">
      <div class="card-title">Nuevo canal</div>
      <form @submit.prevent="createChannel">
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:1rem;">
          <div class="form-group">
            <label>Nombre</label>
            <input v-model="form.name" required />
          </div>
          <div class="form-group">
            <label>URL del canal</label>
            <input v-model="form.url" placeholder="https://youtube.com/@tu-canal" />
          </div>
        </div>
        <div style="display:flex; gap:0.5rem;">
          <button type="submit" class="primary" :disabled="saving">Guardar</button>
          <button type="button" class="secondary" @click="showCreate = false">Cancelar</button>
        </div>
      </form>
    </div>

    <!-- Channel list -->
    <div v-if="channels.length === 0" class="card" style="color:#666;">
      No tienes canales. Crea uno para empezar.
    </div>
    <div v-else class="grid-2">
      <div v-for="ch in channels" :key="ch.id" class="card channel-card">
        <div style="display:flex; justify-content:space-between; align-items:start;">
          <div>
            <div style="font-weight:600; color:#e0e0e0; font-size:1rem;">{{ ch.name }}</div>
            <div style="font-size:0.8rem; color:#666; margin-top:0.25rem;">{{ ch.platform }} · {{ ch.status }}</div>
          </div>
          <button class="danger" @click="deleteChannel(ch.id)" style="font-size:0.75rem;">Eliminar</button>
        </div>
        <div v-if="ch.url" style="margin-top:0.5rem;">
          <a :href="ch.url" target="_blank" style="font-size:0.85rem;">{{ ch.url }}</a>
        </div>
        <div style="margin-top:1rem; display:flex; gap:0.5rem;">
          <router-link :to="'/content?channel=' + ch.id" class="secondary" style="padding:0.4rem 0.8rem; border-radius:4px; font-size:0.85rem; background:#2a2d3a; color:#e0e0e0;">Ver contenido</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useStore, apiFetch } from '../main.js'

const store = useStore()
const error = ref(null)
const channels = ref([])
const showCreate = ref(false)
const saving = ref(false)
const form = ref({ name: '', url: '' })

onMounted(async () => {
  try {
    channels.value = await apiFetch('/api/v3/channels')
  } catch (e) {
    error.value = e.message
  }
})

async function createChannel() {
  saving.value = true
  try {
    const ch = await apiFetch('/api/v3/channels', {
      method: 'POST',
      body: JSON.stringify({ name: form.value.name, url: form.value.url }),
    })
    channels.value.push(ch)
    showCreate.value = false
    form.value = { name: '', url: '' }
  } catch (e) {
    error.value = e.message
  } finally {
    saving.value = false
  }
}

async function deleteChannel(id) {
  if (!confirm('¿Eliminar este canal?')) return
  try {
    await apiFetch(`/api/v3/channels/${id}`, { method: 'DELETE' })
    channels.value = channels.value.filter(c => c.id !== id)
  } catch (e) {
    error.value = e.message
  }
}
</script>

<style scoped>
.channel-card { transition: border-color 0.2s; }
.channel-card:hover { border-color: #3a3d4a; }
</style>
