<template>
  <div>
    <div class="page-header" style="display:flex; justify-content:space-between; align-items:center;">
      <div>
        <h1 class="page-title">💡 Prompts</h1>
        <p class="page-subtitle">Plantillas con {"{{variable}}"} para cada etapa del pipeline</p>
      </div>
      <button class="primary" @click="openCreate">+ Nuevo prompt</button>
    </div>

    <div v-if="error" class="alert error">{{ error }}</div>

    <!-- Tabs -->
    <div class="tabs" style="margin-bottom:1rem; display:flex; gap:0.5rem; border-bottom:1px solid #2a2d3a; padding-bottom:0.5rem;">
      <button v-for="cat in categories" :key="cat" @click="selectedCategory = cat" :class="['tab-btn', {active: selectedCategory === cat}]">{{ cat }}</button>
    </div>

    <div v-if="filteredPrompts.length === 0" class="card" style="color:#666;">No hay prompts en esta categoría.</div>
    <div v-else class="grid-2">
      <div v-for="prompt in filteredPrompts" :key="prompt.id" class="card prompt-card">
        <div style="display:flex; justify-content:space-between; align-items:start; margin-bottom:0.5rem;">
          <div>
            <div style="font-weight:600; color:#e0e0e0;">{{ prompt.name }}</div>
            <div style="font-size:0.75rem; color:#6366f1;">{{ prompt.category }}</div>
          </div>
          <div style="display:flex; gap:0.3rem;">
            <button class="secondary" @click="openEdit(prompt)" style="padding:0.25rem 0.5rem; font-size:0.75rem;">Editar</button>
            <button class="danger" @click="deletePrompt(prompt.id)" style="padding:0.25rem 0.5rem; font-size:0.75rem;">✕</button>
          </div>
        </div>
        <div v-if="prompt.description" style="font-size:0.85rem; color:#888; margin-bottom:0.5rem;">{{ prompt.description }}</div>
        <div class="prompt-preview">{{ prompt.content.slice(0, 150) }}{{ prompt.content.length > 150 ? '...' : '' }}</div>
        <div v-if="prompt.tags.length" style="margin-top:0.5rem; display:flex; gap:0.3rem; flex-wrap:wrap;">
          <span v-for="tag in prompt.tags" :key="tag" style="font-size:0.7rem; background:#2a2d3a; padding:0.1rem 0.4rem; border-radius:4px; color:#888;">#{{ tag }}</span>
        </div>
      </div>
    </div>

    <!-- Modal -->
    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal">
        <h3 style="color:#e0e0e0; margin-bottom:1rem;">{{ editing ? 'Editar prompt' : 'Nuevo prompt' }}</h3>
        <form @submit.prevent="savePrompt">
          <div class="form-group">
            <label>Nombre</label>
            <input v-model="form.name" required />
          </div>
          <div class="form-group">
            <label>Categoría</label>
            <select v-model="form.category">
              <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
            </select>
          </div>
          <div class="form-group">
            <label>Descripción</label>
            <input v-model="form.description" />
          </div>
          <div class="form-group">
            <label>Contenido <small>(usa {"{{variable}}"} para variables)</small></label>
            <textarea v-model="form.content" required style="min-height:150px; font-family:monospace;" />
          </div>
          <div class="form-group">
            <label>Tags <small>(separados por coma)</small></label>
            <input v-model="tagsInput" placeholder="youtube, short, tutorial" />
          </div>
          <div style="display:flex; gap:0.5rem;">
            <button type="submit" class="primary" :disabled="saving">{{ saving ? 'Guardando...' : 'Guardar' }}</button>
            <button type="button" class="secondary" @click="showModal = false">Cancelar</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useStore, apiFetch } from '../main.js'

const store = useStore()
const error = ref(null)
const prompts = ref([])
const showModal = ref(false)
const editing = ref(null)
const saving = ref(false)
const selectedCategory = ref('all')
const tagsInput = ref('')
const form = ref({ name: '', category: 'custom', description: '', content: '' })
const categories = ['all', 'storming', 'development', 'scene_graphic', 'scene_video', 'tts', 'custom']

const filteredPrompts = computed(() => {
  if (selectedCategory.value === 'all') return prompts.value
  return prompts.value.filter(p => p.category === selectedCategory.value)
})

onMounted(async () => {
  try {
    const [userPrompts, systemPrompts] = await Promise.all([
      apiFetch('/api/v3/prompts'),
      apiFetch('/api/v3/prompts/templates'),
    ])
    prompts.value = [...userPrompts, ...systemPrompts]
  } catch (e) {
    error.value = e.message
  }
})

function openCreate() {
  editing.value = null
  form.value = { name: '', category: 'custom', description: '', content: '' }
  tagsInput.value = ''
  showModal.value = true
}

function openEdit(prompt) {
  editing.value = prompt.id
  form.value = { name: prompt.name, category: prompt.category, description: prompt.description, content: prompt.content }
  tagsInput.value = prompt.tags?.join(', ') || ''
  showModal.value = true
}

async function savePrompt() {
  saving.value = true
  try {
    const payload = {
      ...form.value,
      tags: tagsInput.value.split(',').map(t => t.trim()).filter(Boolean),
    }
    let saved
    if (editing.value) {
      saved = await apiFetch(`/api/v3/prompts/${editing.value}`, {
        method: 'PUT',
        body: JSON.stringify(payload),
      })
      const idx = prompts.value.findIndex(p => p.id === editing.value)
      if (idx !== -1) prompts.value[idx] = saved
    } else {
      saved = await apiFetch('/api/v3/prompts', {
        method: 'POST',
        body: JSON.stringify(payload),
      })
      prompts.value.push(saved)
    }
    showModal.value = false
  } catch (e) {
    error.value = e.message
  } finally {
    saving.value = false
  }
}

async function deletePrompt(id) {
  if (!confirm('¿Eliminar este prompt?')) return
  try {
    await apiFetch(`/api/v3/prompts/${id}`, { method: 'DELETE' })
    prompts.value = prompts.value.filter(p => p.id !== id)
  } catch (e) {
    error.value = e.message
  }
}
</script>

<style scoped>
.tab-btn { background: none; border: 1px solid #2a2d3a; color: #888; padding: 0.3rem 0.75rem; border-radius: 4px; font-size: 0.85rem; transition: all 0.2s; }
.tab-btn:hover { border-color: #6366f1; color: #e0e0e0; }
.tab-btn.active { background: #6366f1; border-color: #6366f1; color: #fff; }
.prompt-card { transition: border-color 0.2s; cursor: default; }
.prompt-card:hover { border-color: #3a3d4a; }
.prompt-preview { font-size: 0.8rem; color: #666; background: #0f1117; padding: 0.5rem; border-radius: 4px; font-family: monospace; margin-top: 0.5rem; }
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.7); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal { background: #1a1d27; border: 1px solid #2a2d3a; border-radius: 12px; padding: 2rem; width: 100%; max-width: 600px; max-height: 90vh; overflow-y: auto; }
</style>
