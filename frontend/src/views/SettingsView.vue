<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">⚙️ Ajustes</h1>
      <p class="page-subtitle">Configuración de tu cuenta, APIs y respaldos</p>
    </div>

    <div v-if="error" class="alert error">{{ error }}</div>
    <div v-if="success" class="alert success">{{ success }}</div>

    <!-- Tabs -->
    <div class="tabs">
      <button v-for="t in tabs" :key="t.id" :class="['tab', { active: tab === t.id }]" @click="tab = t.id">{{ t.label }}</button>
    </div>

    <!-- ── Usuario ── -->
    <div v-if="tab === 'usuario'">
      <div class="card">
        <div class="card-title">Datos de cuenta</div>
        <div class="form-group">
          <label>Nombre</label>
          <input v-model="userForm.name" />
        </div>
        <div class="form-group">
          <label>Email</label>
          <input v-model="userForm.email" type="email" />
        </div>
        <div class="form-group">
          <label>Nueva contraseña <small>(dejar en blanco para no cambiar)</small></label>
          <input v-model="userForm.new_password" type="password" placeholder="••••••••" />
        </div>
        <div class="form-group">
          <label>Contraseña actual <small>(requerida para cambiar datos)</small></label>
          <input v-model="userForm.current_password" type="password" placeholder="••••••••" />
        </div>
        <button class="primary" @click="saveUser" :disabled="saving">Guardar cambios</button>
      </div>
    </div>

    <!-- ── Canales ── -->
    <div v-if="tab === 'canales'">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
        <p class="page-subtitle">Gestiona tus canales YouTube</p>
        <button class="primary" @click="openChannelModal()">+ Nuevo canal</button>
      </div>
      <div v-if="!channels.length" class="card" style="color:#666;">No hay canales configurados.</div>
      <div v-else>
        <div v-for="ch in channels" :key="ch.id" class="card channel-item">
          <div style="display:flex; justify-content:space-between; align-items:center;">
            <div>
              <div style="font-weight:600; color:#e0e0e0;">{{ ch.name }}</div>
              <div style="font-size:0.8rem; color:#666;">{{ ch.platform }} · {{ ch.url || 'sin URL' }}</div>
            </div>
            <div style="display:flex; gap:0.5rem;">
              <button class="secondary" @click="openChannelModal(ch)">Editar</button>
              <button class="danger" @click="deleteChannel(ch.id)">Eliminar</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Modal canal -->
      <div v-if="showChannelModal" class="modal-overlay" @click.self="showChannelModal=false">
        <div class="modal">
          <h3 style="color:#e0e0e0; margin-bottom:1rem;">{{ editingChannel ? 'Editar canal' : 'Nuevo canal' }}</h3>
          <div class="form-group">
            <label>Nombre</label>
            <input v-model="channelForm.name" />
          </div>
          <div class="form-group">
            <label>Plataforma</label>
            <select v-model="channelForm.platform">
              <option value="youtube">YouTube</option>
              <option value="tiktok">TikTok</option>
              <option value="instagram">Instagram</option>
            </select>
          </div>
          <div class="form-group">
            <label>URL del canal</label>
            <input v-model="channelForm.url" placeholder="https://www.youtube.com/@tu-canal" />
          </div>
          <div class="form-group">
            <label>ID de canal <small>(opcional, extraído de la URL)</small></label>
            <input v-model="channelForm.platform_id" />
          </div>
          <div style="display:flex; gap:0.5rem; margin-top:1rem;">
            <button class="primary" @click="saveChannel" :disabled="savingChannel">{{ savingChannel ? 'Guardando...' : 'Guardar' }}</button>
            <button class="secondary" @click="showChannelModal=false">Cancelar</button>
          </div>
        </div>
      </div>
    </div>

    <!-- ── APIs ── -->
    <div v-if="tab === 'apis'">
      <p class="page-subtitle" style="margin-bottom:1.5rem;">Configura las APIs que usa WUI para generar contenido.</p>
      <div v-for="(cfg, key) in apiConfigs" :key="key" class="api-card">
        <div class="api-header">
          <span class="api-name">{{ apiLabels[key] || key }}</span>
          <label class="toggle">
            <input type="checkbox" v-model="cfg.enabled" @change="saveApi(key, cfg)" />
            <span class="toggle-slider"></span>
          </label>
        </div>
        <div v-if="cfg.enabled" style="display:grid; gap:0.75rem;">
          <div class="form-group" style="margin-bottom:0">
            <label>API Key</label>
            <input v-model="cfg.api_key" type="password" :placeholder="cfg.api_key ? '••••••••' : 'sk-...'" />
          </div>
          <div class="form-group" style="margin-bottom:0">
            <label>Base URL <small>(opcional)</small></label>
            <input v-model="cfg.base_url" placeholder="https://api.minimax.chat/..." />
          </div>
          <div class="form-group" style="margin-bottom:0">
            <label>Modelo <small>(opcional)</small></label>
            <input v-model="cfg.model" placeholder="MBXM-..." />
          </div>
          <button class="secondary" style="align-self:start;" @click="saveApi(key, cfg)">Guardar</button>
        </div>
      </div>
    </div>

    <!-- ── Respaldos ── -->
    <div v-if="tab === 'backup'">
      <div class="card">
        <div class="card-title">Configuración de respaldo</div>
        <div class="form-group">
          <label>Directorio de datos</label>
          <input v-model="backupConfig.data_directory" />
        </div>
        <div style="display:flex; gap:1rem; margin-bottom:1rem;">
          <label class="toggle" style="display:flex; align-items:center; gap:0.5rem;">
            <input type="checkbox" v-model="backupConfig.auto_backup" />
            <span class="toggle-slider"></span>
            <span style="font-size:0.85rem; color:#a0a0b0;">Auto-respaldo</span>
          </label>
          <label class="toggle" style="display:flex; align-items:center; gap:0.5rem;">
            <input type="checkbox" v-model="backupConfig.enabled" />
            <span class="toggle-slider"></span>
            <span style="font-size:0.85rem; color:#a0a0b0;">Respaldos activos</span>
          </label>
        </div>
        <div class="form-group">
          <label>Máximo de respaldos a mantener</label>
          <input v-model.number="backupConfig.max_backups" type="number" min="1" max="50" style="max-width:120px;" />
        </div>
        <button class="primary" @click="saveBackupConfig">Guardar</button>
      </div>

      <div style="display:flex; justify-content:space-between; align-items:center; margin:1.5rem 0 1rem;">
        <h3 style="color:#e0e0e0; font-size:1rem;">Respaldos disponibles</h3>
        <button class="primary" @click="doBackup" :disabled="backingUp">
          {{ backingUp ? 'Creando...' : '+ Crear respaldo ahora' }}
        </button>
      </div>
      <div v-if="!backups.length" class="card" style="color:#666;">No hay respaldos creados.</div>
      <div v-else>
        <div v-for="bk in backups" :key="bk.id" class="backup-item">
          <div class="backup-info">
            <span class="backup-id">{{ bk.id }}</span>
            <span class="backup-meta">{{ formatDate(bk.created_at) }} · {{ bk.size_mb }} MB · {{ bk.content.join(', ') }}</span>
          </div>
          <div class="backup-actions">
            <a :href="`/api/v3/config/backups/${bk.id}/download`" class="secondary" style="text-decoration:none; display:inline-block;" target="_blank">Descargar</a>
            <button class="danger" @click="restoreBackup(bk.id)">Restaurar</button>
          </div>
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
const success = ref(null)
const tab = ref('usuario')
const tabs = [
  { id: 'usuario', label: '👤 Usuario' },
  { id: 'canales', label: '📡 Canales' },
  { id: 'apis', label: '🔌 APIs' },
  { id: 'backup', label: '💾 Respaldos' },
]

// ── Usuario ──────────────────────────────────────────────────────────────────
const userForm = ref({ name: '', email: '', current_password: '', new_password: '' })

async function loadMe() {
  try {
    const u = await apiFetch('/api/v3/auth/me')
    userForm.value = { name: u.name || '', email: u.email || '', current_password: '', new_password: '' }
  } catch (e) {
    error.value = e.message
  }
}

async function saveUser() {
  error.value = null; success.value = null
  try {
    const body = { name: userForm.value.name }
    if (userForm.value.new_password) {
      body.password = userForm.value.new_password
      body.current_password = userForm.value.current_password
    }
    const updated = await apiFetch('/api/v3/auth/me', { method: 'PUT', body: JSON.stringify(body) })
    store.user = updated
    success.value = 'Cambios guardados.'
    setTimeout(() => success.value = null, 3000)
  } catch (e) { error.value = e.message }
}

// ── Canales ───────────────────────────────────────────────────────────────────
const channels = ref([])
const showChannelModal = ref(false)
const editingChannel = ref(null)
const savingChannel = ref(false)
const channelForm = ref({ name: '', platform: 'youtube', url: '', platform_id: '' })

async function loadChannels() {
  try { channels.value = await apiFetch('/api/v3/channels') } catch (e) { error.value = e.message }
}

function openChannelModal(ch = null) {
  editingChannel.value = ch
  channelForm.value = ch ? { name: ch.name, platform: ch.platform, url: ch.url || '', platform_id: ch.platform_id || '' } : { name: '', platform: 'youtube', url: '', platform_id: '' }
  showChannelModal.value = true
}

async function saveChannel() {
  savingChannel.value = true
  try {
    if (editingChannel.value) {
      await apiFetch(`/api/v3/channels/${editingChannel.value.id}`, { method: 'PUT', body: JSON.stringify(channelForm.value) })
    } else {
      await apiFetch('/api/v3/channels', { method: 'POST', body: JSON.stringify(channelForm.value) })
    }
    showChannelModal.value = false
    await loadChannels()
  } catch (e) { error.value = e.message }
  finally { savingChannel.value = false }
}

async function deleteChannel(id) {
  if (!confirm('¿Eliminar este canal?')) return
  try { await apiFetch(`/api/v3/channels/${id}`, { method: 'DELETE' }); await loadChannels() }
  catch (e) { error.value = e.message }
}

// ── APIs ─────────────────────────────────────────────────────────────────────
const apiConfigs = ref({})
const apiLabels = {
  minimax: 'Minimax',
  openai: 'OpenAI',
  elevenlabs: 'ElevenLabs',
  minimax_tts: 'Minimax TTS',
  comfyui: 'ComfyUI',
  flux: 'Flux',
}

async function loadConfig() {
  try {
    const cfg = await apiFetch('/api/v3/config')
    if (cfg.apis) apiConfigs.value = cfg.apis
    if (cfg.backup) backupConfig.value = { ...backupConfig.value, ...cfg.backup }
  } catch (e) { error.value = e.message }
}

async function saveApi(key, cfg) {
  try {
    await apiFetch(`/api/v3/config/apis/${key}`, { method: 'PUT', body: JSON.stringify(cfg) })
    success.value = `${apiLabels[key] || key} guardado.`
    setTimeout(() => success.value = null, 3000)
  } catch (e) { error.value = e.message }
}

// ── Respaldos ─────────────────────────────────────────────────────────────────
const backupConfig = ref({ data_directory: 'data', enabled: true, auto_backup: true, max_backups: 5 })
const backups = ref([])
const backingUp = ref(false)

async function saveBackupConfig() {
  try {
    await apiFetch('/api/v3/config', { method: 'PATCH', body: JSON.stringify({ backup: backupConfig.value }) })
    success.value = 'Configuración de respaldo guardada.'
    setTimeout(() => success.value = null, 3000)
  } catch (e) { error.value = e.message }
}

async function doBackup() {
  backingUp.value = true
  try {
    await apiFetch('/api/v3/config/backups', { method: 'POST' })
    await loadBackups()
    success.value = 'Respaldo creado.'
    setTimeout(() => success.value = null, 3000)
  } catch (e) { error.value = e.message }
  finally { backingUp.value = false }
}

async function loadBackups() {
  try { backups.value = await apiFetch('/api/v3/config/backups') } catch (e) { error.value = e.message }
}

async function restoreBackup(id) {
  if (!confirm('¿Restaurar este respaldo? Se hará un backup de seguridad antes.')) return
  try {
    await apiFetch(`/api/v3/config/backups/${id}/restore`, { method: 'POST' })
    success.value = 'Restaurado correctamente.'
    setTimeout(() => success.value = null, 3000)
  } catch (e) { error.value = e.message }
}

function formatDate(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleString('es-ES', { dateStyle: 'short', timeStyle: 'short' })
}

onMounted(async () => {
  await loadMe()
  await Promise.all([loadChannels(), loadConfig(), loadBackups()])
})
</script>

<style scoped>
.channel-item { padding: 1rem 1.5rem; }
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.7); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal { background: #1a1d27; border: 1px solid #2a2d3a; border-radius: 12px; padding: 2rem; width: 100%; max-width: 500px; max-height: 90vh; overflow-y: auto; }
</style>
