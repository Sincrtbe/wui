<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">🔄 Pipeline</h1>
      <p class="page-subtitle">Asigna prompts a cada etapa del pipeline para este usuario</p>
    </div>

    <div v-if="error" class="alert error">{{ error }}</div>

    <div class="card">
      <div class="card-title">Asignaciones globales del usuario</div>
      <div style="margin-bottom:1.5rem; font-size:0.85rem; color:#888;">
        Estos prompts se usan cuando no hay asignación específica por canal.
      </div>

      <div v-for="stage in stages" :key="stage" class="pipeline-row">
        <div class="stage-label">
          <span :class="['stage-badge', 'stage-' + stageMap[stage]]">{{ stageMap[stage] }}</span>
        </div>
        <div class="stage-prompt">
          <div v-if="assignments[stage]" class="assigned-prompt">
            <span style="color:#4ade80;">✓</span>
            <span style="font-weight:600; color:#e0e0e0;">{{ assignments[stage].prompt?.name || assignments[stage].prompt_id }}</span>
            <span style="color:#666; font-size:0.8rem; margin-left:0.5rem;">{{ assignments[stage].prompt?.category }}</span>
            <button class="danger" @click="removeAssignment(stage)" style="margin-left:auto; padding:0.2rem 0.4rem; font-size:0.7rem;">Quitar</button>
          </div>
          <div v-else style="color:#444; font-size:0.85rem;">Sin asignar</div>
        </div>
        <select v-model="newAssignments[stage]" @change="assignPrompt(stage)" style="min-width:200px;">
          <option value="">-- Asignar prompt --</option>
          <option v-for="p in allPrompts" :key="p.id" :value="p.id">{{ p.name }} ({{ p.category }})</option>
        </select>
      </div>
    </div>

    <div class="card">
      <div class="card-title">📋 Pipeline completo</div>
      <div class="pipeline-flow" style="justify-content:center; font-size:1rem;">
        <span v-for="(s, i) in stageNames" :key="s" class="pip-step">
          {{ s }}
          <span v-if="i < stageNames.length - 1" class="pipeline-arrow">→</span>
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useStore, apiFetch } from '../main.js'

const store = useStore()
const error = ref(null)
const stages = ['idea_generation', 'script_writing', 'scene_graphic', 'scene_video', 'tts']
const stageNames = ['Idea', 'Guión', 'Gráfico', 'Video', 'TTS']
const stageMap = { idea_generation: 'idea', script_writing: 'script', scene_graphic: 'graphic', scene_video: 'video', tts: 'video' }
const assignments = ref({})
const allPrompts = ref([])
const newAssignments = reactive({})

onMounted(async () => {
  try {
    const [assignmentsData, userPrompts, systemPrompts] = await Promise.all([
      apiFetch('/api/v3/pipeline/assignments'),
      apiFetch('/api/v3/prompts'),
      apiFetch('/api/v3/prompts/templates'),
    ])
    assignments.value = assignmentsData
    allPrompts.value = [...userPrompts, ...systemPrompts]
  } catch (e) {
    error.value = e.message
  }
})

async function assignPrompt(stage) {
  const promptId = newAssignments[stage]
  if (!promptId) return
  try {
    const result = await apiFetch('/api/v3/pipeline/assignments', {
      method: 'POST',
      body: JSON.stringify({ stage, prompt_id: promptId }),
    })
    assignments.value[stage] = { prompt_id: promptId, prompt: allPrompts.value.find(p => p.id === promptId) }
    newAssignments[stage] = ''
  } catch (e) {
    error.value = e.message
  }
}

async function removeAssignment(stage) {
  try {
    await apiFetch(`/api/v3/pipeline/assignments/${stage}`, { method: 'DELETE' })
    delete assignments.value[stage]
  } catch (e) {
    error.value = e.message
  }
}
</script>

<style scoped>
.pipeline-row { display: grid; grid-template-columns: 160px 1fr 220px; gap: 1rem; align-items: center; padding: 0.75rem 0; border-bottom: 1px solid #1f2230; }
.pipeline-row:last-child { border-bottom: none; }
.stage-label { display: flex; align-items: center; }
.assigned-prompt { display: flex; align-items: center; gap: 0.5rem; }
.pipeline-flow { display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap; }
.pip-step { color: #a0a0b0; }
.pipeline-arrow { color: #6366f1; margin: 0 0.25rem; }
</style>
