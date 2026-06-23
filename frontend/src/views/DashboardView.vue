<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">👋 Bienvenido{{ store.user?.name ? ', ' + store.user.name : '' }}</h1>
      <p class="page-subtitle">Resumen de tu actividad</p>
    </div>

    <div v-if="error" class="alert error">{{ error }}</div>

    <!-- Lluvia de ideas -->
    <div class="card brainstorm-card">
      <div class="card-title">💡 Lluvia de ideas</div>
      <p style="font-size:0.85rem; color:#888; margin-bottom:1rem;">Genera ideas de contenido automáticamente para un canal usando IA.</p>

      <div class="storm-grid">
        <div class="form-group" style="margin-bottom:0; flex:2;">
          <label>Canal</label>
          <select v-model="stormForm.channel_id">
            <option value="">— Selecciona un canal —</option>
            <option v-for="ch in channels" :key="ch.id" :value="ch.id">
              {{ ch.name }}<span v-if="ch.topic"> ({{ ch.topic }})</span>
            </option>
          </select>
        </div>
        <div class="form-group" style="margin-bottom:0; flex:1;">
          <label>API</label>
          <select v-model="stormForm.provider">
            <option value="minimax">Minimax</option>
            <option value="openai">OpenAI</option>
          </select>
        </div>
        <div class="form-group" style="margin-bottom:0; flex:1;">
          <label>Tema adicional <small>(opcional)</small></label>
          <input v-model="stormForm.topic" placeholder="Sobre qué..." />
        </div>
        <div style="display:flex; align-items:flex-end; gap:0.5rem;">
          <button class="primary" @click="doStorm" :disabled="storming || !stormForm.channel_id">
            {{ storming ? '⏳ Generando...' : '💡 Generar ideas' }}
          </button>
        </div>
      </div>

      <!-- Resultados — una tarjeta por idea -->
      <div v-if="stormItems.length > 0" style="margin-top:1rem;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.75rem;">
          <strong style="color:#10b981;">✅ {{ stormItems.length }} ideas generadas</strong>
          <button class="secondary" style="font-size:0.75rem;" @click="stormItems=[]">Cerrar</button>
        </div>
        <div style="display:grid;gap:0.75rem;">
          <div v-for="item in stormItems" :key="item.id" class="storm-result" style="cursor:pointer;" @click="viewContent(item)">
            <div style="font-weight:600;color:#e0e0e0;margin-bottom:0.4rem;">{{ item.title }}</div>
            <div v-if="getStructuredIdea(item).concept" style="font-size:0.82rem;color:#888;">{{ getStructuredIdea(item).concept }}</div>
            <div style="margin-top:0.5rem;font-size:0.75rem;color:#555;">
              Canal: {{ item.channel_id.slice(0,8) }}... · Etapa: {{ item.stage }}
            </div>
          </div>
        </div>
      </div>

      <!-- Error de storm -->
      <div v-if="stormError" class="alert error" style="margin-top:1rem;">{{ stormError }}</div>
    </div>

    <!-- Stats -->
    <div class="grid-3" style="margin-bottom: 2rem;">
      <div class="card stat-card">
        <div class="stat-value">{{ stats.channels }}</div>
        <div class="stat-label">Canales</div>
      </div>
      <div class="card stat-card">
        <div class="stat-value">{{ stats.content }}</div>
        <div class="stat-label">Contenido</div>
      </div>
      <div class="card stat-card">
        <div class="stat-value">{{ stats.prompts }}</div>
        <div class="stat-label">Prompts</div>
      </div>
    </div>

    <!-- Recent content -->
    <div class="card">
      <div class="card-title">📋 Contenido reciente</div>
      <div v-if="recentContent.length === 0" style="color:#666; font-size:0.9rem;">Sin contenido aún.</div>
      <table v-else>
        <thead>
          <tr>
            <th>Título</th>
            <th>Canal</th>
            <th>Etapa</th>
            <th>Estado</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in recentContent" :key="item.id" @click="viewContent(item)" style="cursor:pointer;">
            <td>{{ item.title }}</td>
            <td>{{ item.channel_id.slice(0,8) }}...</td>
            <td><span :class="['stage-badge', 'stage-' + item.stage]">{{ item.stage }}</span></td>
            <td>{{ item.status }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pipeline overview -->
    <div class="card">
      <div class="card-title">🔄 Pipeline</div>
      <div class="pipeline-flow">
        <span v-for="(stage, i) in stages" :key="stage" class="pipeline-stage">
          {{ stage }}
          <span v-if="i < stages.length - 1" class="pipeline-arrow">→</span>
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useStore, apiFetch } from '../main.js'

const store = useStore()
const router = useRouter()
const error = ref(null)
const stats = reactive({ channels: 0, content: 0, prompts: 0 })
const recentContent = ref([])
const channels = ref([])
const stages = ['idea', 'script', 'graphic', 'video', 'published']

const stormForm = reactive({ channel_id: '', provider: 'minimax', topic: '' })
const storming = ref(false)
const stormItems = ref([])
const stormError = ref(null)

onMounted(async () => {
  try {
    const [ch, content, prompts] = await Promise.all([
      apiFetch('/api/v3/channels'),
      apiFetch('/api/v3/content'),
      apiFetch('/api/v3/prompts'),
    ])
    channels.value = ch
    stats.channels = ch.length
    stats.content = content.length
    stats.prompts = prompts.length
    recentContent.value = content.slice(-5).reverse()
  } catch (e) {
    error.value = e.message
  }
})

async function doStorm() {
  storming.value = true
  stormError.value = null
  stormItems.value = []
  try {
    const params = new URLSearchParams()
    params.set('provider', stormForm.provider)
    if (stormForm.topic) params.set('extra_topic', stormForm.topic)
    const res = await apiFetch(`/api/v3/brainstorm/${stormForm.channel_id}?${params}`, { method: 'POST' })
    stormItems.value = res.items || []
    // Recargar stats
    const content = await apiFetch('/api/v3/content')
    stats.content = content.length
    recentContent.value = content.slice(-5).reverse()
  } catch (e) {
    stormError.value = e.message
  } finally {
    storming.value = false
  }
}

function getStructuredIdea(item) {
  try { return JSON.parse(item.structured_ideas || '{}') }
  catch { return {} }
}

function viewContent(item) {
  router.push(`/content/${item.id}?channel=${item.channel_id}`)
}
</script>

<style scoped>
.brainstorm-card { margin-bottom: 1.5rem; }
.storm-grid { display: flex; gap: 1rem; align-items: flex-end; flex-wrap: wrap; }
.storm-result {
  margin-top: 1rem;
  padding: 1rem;
  background: #0f1117;
  border-radius: 8px;
  border: 1px solid #1e2030;
}
.ideas-text {
  white-space: pre-wrap;
  font-family: monospace;
  font-size: 0.85rem;
  color: #c0c0d0;
  max-height: 300px;
  overflow-y: auto;
}
.stat-card { text-align: center; }
.stat-value { font-size: 2rem; font-weight: 700; color: #6366f1; }
.stat-label { font-size: 0.85rem; color: #888; margin-top: 0.25rem; }
.pipeline-flow { display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap; }
.pipeline-stage { color: #a0a0b0; font-size: 0.9rem; }
.pipeline-arrow { color: #6366f1; margin: 0 0.25rem; }
</style>
