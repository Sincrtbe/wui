<template>
  <div>
    <div class="page-header" style="display:flex; justify-content:space-between; align-items:center;">
      <div>
        <h1 class="page-title">🎬 Contenido</h1>
        <p class="page-subtitle">Ideas, guiones y proyectos de video</p>
      </div>
      <button class="primary" @click="showCreate = true">+ Nueva idea</button>
    </div>

    <!-- Filters -->
    <div class="card filters" style="padding:1rem;">
      <div style="display:flex; gap:1rem; flex-wrap:wrap; align-items:center;">
        <div class="form-group" style="margin:0; flex:1; min-width:200px;">
          <label>Canal</label>
          <select v-model="filterChannel">
            <option value="">Todos</option>
            <option v-for="ch in channels" :key="ch.id" :value="ch.id">{{ ch.name }}</option>
          </select>
        </div>
        <div class="form-group" style="margin:0;">
          <label>Etapa</label>
          <select v-model="filterStage">
            <option value="">Todas</option>
            <option v-for="s in stages" :key="s" :value="s">{{ s }}</option>
          </select>
        </div>
        <button class="secondary" @click="loadContent" style="align-self:flex-end;">Filtrar</button>
      </div>
    </div>

    <div v-if="error" class="alert error">{{ error }}</div>

    <!-- Create -->
    <div v-if="showCreate" class="card">
      <div class="card-title">Nueva idea</div>
      <form @submit.prevent="createContent">
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:1rem;">
          <div class="form-group">
            <label>Título</label>
            <input v-model="form.title" required />
          </div>
          <div class="form-group">
            <label>Canal</label>
            <select v-model="form.channel_id" required>
              <option value="">Selecciona canal</option>
              <option v-for="ch in channels" :key="ch.id" :value="ch.id">{{ ch.name }}</option>
            </select>
          </div>
        </div>
        <div class="form-group">
          <label>Notas iniciales</label>
          <textarea v-model="form.idea_notes" style="min-height:80px;" />
        </div>
        <div style="display:flex; gap:0.5rem;">
          <button type="submit" class="primary" :disabled="saving">Crear</button>
          <button type="button" class="secondary" @click="showCreate = false">Cancelar</button>
        </div>
      </form>
    </div>

    <!-- List -->
    <div v-if="content.length === 0" class="card" style="color:#666;">
      Sin contenido{{ filterChannel || filterStage ? ' con esos filtros' : '' }}. <router-link to="/prompts">Crea prompts</router-link> primero si no lo has hecho.
    </div>
    <div v-else class="grid-2">
      <div v-for="item in content" :key="item.id" class="card content-card" @click="goToContent(item)">
        <div style="display:flex; justify-content:space-between; align-items:start;">
          <div style="font-weight:600; color:#e0e0e0;">{{ item.title }}</div>
          <span :class="['stage-badge', 'stage-' + item.stage]">{{ item.stage }}</span>
        </div>
        <div style="font-size:0.8rem; color:#666; margin-top:0.25rem;">{{ item.channel_id }}</div>
        <div style="margin-top:0.5rem; display:flex; gap:0.5rem;">
          <button class="secondary" style="padding:0.3rem 0.6rem; font-size:0.8rem;" @click.stop="goToContent(item)">Ver</button>
          <button v-if="item.stage !== 'published'" class="secondary" style="padding:0.3rem 0.6rem; font-size:0.8rem;" @click.stop="advanceItem(item)">→ Avanzar</button>
          <button v-if="item.stage !== 'idea'" class="secondary" style="padding:0.3rem 0.6rem; font-size:0.8rem;" @click.stop="revertItem(item)">← Retroceder</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useStore, apiFetch } from '../main.js'

const store = useStore()
const router = useRouter()
const route = useRoute()
const error = ref(null)
const content = ref([])
const channels = ref([])
const showCreate = ref(false)
const saving = ref(false)
const filterChannel = ref(route.query.channel || '')
const filterStage = ref('')
const stages = ['idea', 'script', 'graphic', 'video', 'published']
const form = ref({ title: '', channel_id: '', idea_notes: '' })

onMounted(async () => {
  try {
    channels.value = await apiFetch('/api/v3/channels')
    await loadContent()
  } catch (e) {
    error.value = e.message
  }
})

async function loadContent() {
  const params = new URLSearchParams()
  if (filterChannel.value) params.set('channel_id', filterChannel.value)
  if (filterStage.value) params.set('stage', filterStage.value)
  const url = '/api/v3/content' + (params.toString() ? '?' + params.toString() : '')
  content.value = await apiFetch(url)
}

async function createContent() {
  saving.value = true
  try {
    const item = await apiFetch('/api/v3/content', {
      method: 'POST',
      body: JSON.stringify(form.value),
    })
    content.value.unshift(item)
    showCreate.value = false
    form.value = { title: '', channel_id: '', idea_notes: '' }
  } catch (e) {
    error.value = e.message
  } finally {
    saving.value = false
  }
}

function goToContent(item) {
  router.push(`/content/${item.id}?channel=${item.channel_id}`)
}

async function advanceItem(item) {
  try {
    const updated = await apiFetch(`/api/v3/content/${item.id}/advance?channel_id=${item.channel_id}`, { method: 'POST' })
    item.stage = updated.stage
    item.status = updated.status
  } catch (e) {
    error.value = e.message
  }
}

async function revertItem(item) {
  try {
    const updated = await apiFetch(`/api/v3/content/${item.id}/revert?channel_id=${item.channel_id}`, { method: 'POST' })
    item.stage = updated.stage
    item.status = updated.status
  } catch (e) {
    error.value = e.message
  }
}
</script>

<style scoped>
.content-card { cursor: pointer; transition: border-color 0.2s; }
.content-card:hover { border-color: #6366f1; }
.filters input, .filters select { margin-bottom: 0; }
</style>
