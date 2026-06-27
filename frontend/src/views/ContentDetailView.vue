<template>
  <div>
    <div class="page-header">
      <button class="secondary" @click="router.push('/content')" style="margin-bottom:0.5rem;">← Volver</button>
      <h1 class="page-title">{{ item.title || 'Detalle de contenido' }}</h1>
      <p class="page-subtitle">Canal: {{ item.channel_id }}</p>
    </div>

    <div v-if="error" class="alert error">{{ error }}</div>

    <!-- Stage + Nav -->
    <div class="card">
      <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:1rem;">
        <div style="display:flex; align-items:center; gap:1rem;">
          <span :class="['stage-badge', 'stage-' + item.stage]" style="font-size:1rem; padding:0.3rem 0.8rem;">{{ item.stage }}</span>
          <span style="color:#666;">{{ item.status }}</span>
        </div>
        <div style="display:flex; gap:0.5rem;">
          <button class="secondary" @click="revert" :disabled="item.stage === 'idea'">← Retroceder</button>
          <button class="primary" @click="advance" :disabled="item.stage === 'published'">Avanzar →</button>
        </div>
      </div>

      <!-- Pipeline bar -->
      <div class="pipeline-flow" style="margin-top:1rem; justify-content:center;">
        <span v-for="(s, i) in stages" :key="s" :class="['pip-stage', { active: s === item.stage, done: isDone(s) }]">
          {{ s }}
          <span v-if="i < stages.length - 1" class="pipeline-arrow">→</span>
        </span>
      </div>
    </div>

    <div style="display:grid; grid-template-columns:1fr 1fr; gap:1rem; margin-top:1rem;">
      <!-- Notes (visible en todos los stages) -->
      <div class="card">
        <div class="card-title">📝 Notas</div>
        <div v-for="note in item.notes" :key="note.id" class="note-item">
          <span :class="['note-type', note.note_type]">{{ note.note_type }}</span>
          <span style="font-size:0.85rem; color:#ccc;">{{ note.content }}</span>
          <button class="danger" @click="deleteNote(note.id)" style="padding:0.1rem 0.3rem; font-size:0.7rem;">✕</button>
        </div>
        <div style="margin-top:0.75rem;">
          <select v-model="newNoteType" style="margin-right:0.5rem;">
            <option value="strength">Fortaleza</option>
            <option value="weakness">Debilidad</option>
            <option value="improvement">Mejora</option>
            <option value="general">General</option>
          </select>
          <input v-model="newNoteContent" placeholder="Nueva nota..." style="flex:1;" @keyup.enter="addNote" />
          <button class="secondary" @click="addNote" style="margin-left:0.5rem;">+</button>
        </div>
      </div>

      <!-- Scores -->
      <div class="card">
        <div class="card-title">📊 Scores</div>
        <div v-for="score in item.scores" :key="score.id" style="display:flex; justify-content:space-between; font-size:0.85rem; padding:0.25rem 0; border-bottom:1px solid #1f2230;">
          <span>{{ score.metric_type }} <span style="color:#666;">({{ score.source }})</span></span>
          <span style="color:#6366f1; font-weight:600;">{{ score.value }}</span>
        </div>
        <div style="margin-top:0.75rem; display:flex; gap:0.5rem; flex-wrap:wrap;">
          <select v-model="newScoreMetric" style="flex:1; min-width:100px;">
            <option value="views">Views</option>
            <option value="ctr">CTR</option>
            <option value="retention">Retención</option>
            <option value="likes_ratio">Likes %</option>
            <option value="ai_score">AI Score</option>
          </select>
          <input v-model.number="newScoreValue" type="number" placeholder="0" style="width:80px;" />
          <button class="secondary" @click="addScore">+</button>
        </div>
      </div>
    </div>

    <!-- Stage-specific content -->
    <div class="card" style="margin-top:1rem;">
      <!-- IDEA -->
      <template v-if="item.stage === 'idea'">
        <div class="card-title">💡 Idea</div>
        <div class="form-group">
          <label>Título</label>
          <input v-model="edit.title" @blur="saveField('title', edit.title)" />
        </div>

        <!-- Structured ideas from brainstorm -->
        <div v-if="item.structured_ideas && item.structured_ideas.length" style="margin-bottom:1.5rem;">
          <div style="font-size:0.85rem; color:#888; margin-bottom:0.75rem;">🎯 Ideas generadas ({{ item.structured_ideas.length }})</div>
          <div class="ideas-grid">
            <div v-for="(idea, i) in item.structured_ideas" :key="i" class="idea-card">
              <div class="idea-header">
                <span class="idea-number">{{ i + 1 }}</span>
                <strong>{{ idea.titulo || idea.title || idea.name || 'Idea sin título' }}</strong>
                <span v-if="idea.score_potencial || idea.score" class="score-badge">
                  {{ idea.score_potencial || idea.score }}/10
                </span>
              </div>
              <div v-if="idea.concepto || idea.concept" class="idea-row">💬 {{ idea.concepto || idea.concept }}</div>
              <div v-if="idea.angulo_viral || idea.viral_angle" class="idea-row">🔥 {{ idea.angulo_viral || idea.viral_angle }}</div>
              <div v-if="idea.hook_visual || idea.hook" class="idea-row">👁️ {{ idea.hook_visual || idea.hook }}</div>
              <div v-if="idea.duracion || idea.duration" class="idea-meta">
                ⏱️ {{ idea.duracion || idea.duration }}
                <span v-if="idea.formato || idea.format"> · {{ idea.formato || idea.format }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="form-group">
          <label>Notas de la idea</label>
          <textarea v-model="edit.idea_notes" @blur="saveField('idea_notes', edit.idea_notes)" style="min-height:120px;" />
        </div>
        <div class="form-group">
          <label>Tags</label>
          <input v-model="edit.tags_input" @blur="saveTags" placeholder="tag1, tag2" />
        </div>
      </template>

      <!-- SCRIPT -->
      <template v-else-if="item.stage === 'script'">
        <div class="card-title">📜 Guión</div>
        <div class="form-group">
          <label>Contenido del guión</label>
          <textarea v-model="edit.script_content" @blur="saveField('script_content', edit.script_content)" style="min-height:200px; font-family:monospace;" />
        </div>
        <!-- Render prompt for script -->
        <div v-if="scriptPrompt" style="margin-top:1rem;">
          <div style="font-size:0.85rem; color:#888; margin-bottom:0.5rem;">Prompt para generar guión:</div>
          <div class="prompt-preview">{{ scriptPrompt.content?.slice(0,200) }}...</div>
          <button class="secondary" @click="renderScriptPrompt" style="margin-top:0.5rem;">Renderizar prompt</button>
          <div v-if="renderedScript" class="rendered-output">{{ renderedScript }}</div>
        </div>
      </template>

      <!-- GRAPHIC -->
      <template v-else-if="item.stage === 'graphic'">
        <div class="card-title">🎨 Escenas gráficas</div>
        <div v-for="(scene, i) in (edit.scene_prompts || [])" :key="i" class="scene-item">
          <div style="font-size:0.8rem; color:#666; margin-bottom:0.25rem;">Escena {{ i + 1 }}</div>
          <textarea v-model="scene.prompt" style="font-family:monospace; font-size:0.85rem;" />
        </div>
        <button class="secondary" @click="saveScenes" style="margin-top:0.5rem; margin-left:0.5rem;">Guardar escenas</button>
        <!-- NocoDB Export -->
        <div style="margin-top:1rem; padding-top:1rem; border-top: 1px solid #333;">
          <div style="font-size:0.85rem; color:#888; margin-bottom:0.5rem;">📦 Exportar a NocoDB:</div>
          <div style="display:flex; gap:0.5rem; flex-wrap:wrap;">
            <input v-model="nocodbUrl" placeholder="http://192.168.10.22:8080" style="flex:1; min-width:200px; background:#1a1a2e; border:1px solid #333; color:#ccc; border-radius:4px; padding:0.3rem 0.5rem; font-size:0.85rem;" />
            <input v-model="nocodbToken" type="password" placeholder="Token NocoDB" style="flex:1; min-width:150px; background:#1a1a2e; border:1px solid #333; color:#ccc; border-radius:4px; padding:0.3rem 0.5rem; font-size:0.85rem;" />
            <input v-model="nocodbTable" placeholder="Tabla ID" style="width:120px; background:#1a1a2e; border:1px solid #333; color:#ccc; border-radius:4px; padding:0.3rem 0.5rem; font-size:0.85rem;" />
            <button class="secondary" @click="exportToNocodb" :disabled="!edit.scene_prompts?.length" style="font-size:0.85rem;">Exportar</button>
          </div>
          <div v-if="nocodbStatus" :class="['nocodb-msg', nocodbStatus.ok ? 'success' : 'error']" style="margin-top:0.5rem; font-size:0.85rem;">{{ nocodbStatus.msg }}</div>
        </div>
        <div v-if="edit.generated_images?.length" style="margin-top:1rem;">
          <div style="font-size:0.85rem; color:#888; margin-bottom:0.5rem;">Imágenes generadas:</div>
          <div style="display:flex; gap:0.5rem; flex-wrap:wrap;">
            <img v-for="img in edit.generated_images" :key="img.url" :src="img.url" style="width:120px; height:80px; object-fit:cover; border-radius:4px;" />
          </div>
        </div>
      </template>

      <!-- VIDEO -->
      <template v-else-if="item.stage === 'video'">
        <div class="card-title">🎬 Escenas de video</div>
        <div v-for="(vid, i) in (edit.generated_videos || [])" :key="i" class="scene-item">
          <div style="font-size:0.8rem; color:#666; margin-bottom:0.25rem;">Clip {{ i + 1 }}</div>
          <div v-if="vid.url" style="background:#0f1117; padding:0.5rem; border-radius:4px; font-size:0.8rem; color:#4ade80;">✓ {{ vid.url }}</div>
        </div>
        <div v-if="edit.tts_result" style="margin-top:1rem;">
          <div style="font-size:0.85rem; color:#888;">🎙️ TTS:</div>
          <div style="color:#4ade80; font-size:0.85rem;">{{ edit.tts_result.audio_url || edit.tts_result.status }}</div>
        </div>
      </template>

      <!-- PUBLISHED -->
      <template v-else-if="item.stage === 'published'">
        <div class="card-title">✅ Published</div>
        <div style="color:#4ade80;">Este contenido ha sido marcado como publicado.</div>
        <div v-if="item.scores?.length" style="margin-top:1rem;">
          <div style="font-size:0.85rem; color:#888; margin-bottom:0.5rem;">Resumen de scores:</div>
          <div v-for="score in item.scores" :key="score.id" style="display:flex; justify-content:space-between; font-size:0.85rem; padding:0.25rem 0; border-bottom:1px solid #1f2230;">
            <span>{{ score.metric_type }}</span>
            <span style="color:#6366f1;">{{ score.value }}</span>
          </div>
        </div>
      </template>
    </div>

    <!-- Versions -->
    <div class="card" style="margin-top:1rem;">
      <div class="card-title">📜 Historial de versiones ({{ versions.length }})</div>
      <div v-if="versions.length === 0" style="color:#666; font-size:0.9rem;">Sin versiones aún.</div>
      <div v-for="v in versions" :key="v.version_number" class="version-item">
        <div>
          <span style="font-weight:600; color:#e0e0e0;">v{{ v.version_number }}</span>
          <span style="color:#666; font-size:0.8rem; margin-left:0.5rem;">{{ v.stage_snapshot }} · {{ new Date(v.created_at).toLocaleString() }}</span>
        </div>
        <button class="secondary" @click="revertToVersion(v.version_number)" style="font-size:0.75rem;">Revertir</button>
      </div>
      <button class="secondary" @click="createVersion" style="margin-top:0.5rem;">+ Crear snapshot</button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useStore, apiFetch } from '../main.js'

const store = useStore()
const router = useRouter()
const route = useRoute()
const error = ref(null)

const item = ref({})
const edit = ref({})
const versions = ref([])
const scriptPrompt = ref(null)
const renderedScript = ref('')
const newNoteType = ref('general')
const newNoteContent = ref('')
const newScoreMetric = ref('views')
const newScoreValue = ref(0)
const stages = ['idea', 'script', 'graphic', 'video', 'published']
const nocodbUrl = ref('')
const nocodbToken = ref('')
const nocodbTable = ref('')
const nocodbStatus = ref(null)

onMounted(async () => {
  await loadItem()
})

async function loadItem() {
  const contentId = route.params.id
  const channelId = route.query.channel
  try {
    item.value = await apiFetch(`/api/v3/content/${contentId}?channel_id=${channelId}`)
    edit.value = { ...item.value, tags_input: (item.value.tags || []).join(', '), scene_prompts: item.value.scene_prompts || [] }
    versions.value = await apiFetch(`/api/v3/content/${contentId}/versions?channel_id=${channelId}`)
    // Load pipeline prompt for script stage
    try {
      scriptPrompt.value = await apiFetch(`/api/v3/pipeline/resolve/script_writing?channel_id=${channelId}`)
    } catch { scriptPrompt.value = null }
  } catch (e) {
    error.value = e.message
  }
}

function isDone(s) {
  const order = stages
  return order.indexOf(s) < order.indexOf(item.value.stage)
}

async function advance() {
  try {
    const updated = await apiFetch(`/api/v3/content/${item.value.id}/advance?channel_id=${item.value.channel_id}`, { method: 'POST' })
    item.value.stage = updated.stage
    item.value.status = updated.status
  } catch (e) { error.value = e.message }
}

async function revert() {
  try {
    const updated = await apiFetch(`/api/v3/content/${item.value.id}/revert?channel_id=${item.value.channel_id}`, { method: 'POST' })
    item.value.stage = updated.stage
    item.value.status = updated.status
  } catch (e) { error.value = e.message }
}

async function saveField(field, value) {
  try {
    const updated = await apiFetch(`/api/v3/content/${item.value.id}?channel_id=${item.value.channel_id}`, {
      method: 'PUT',
      body: JSON.stringify({ [field]: value }),
    })
    item.value[field] = updated[field]
  } catch (e) { error.value = e.message }
}

async function saveTags() {
  const tags = edit.value.tags_input.split(',').map(t => t.trim()).filter(Boolean)
  await saveField('tags', tags)
}

async function addScene() {
  if (!edit.value.scene_prompts) edit.value.scene_prompts = []
  edit.value.scene_prompts.push({ prompt: '', image_url: '' })
}

async function saveScenes() {
  await saveField('scene_prompts', edit.value.scene_prompts)
}

async function exportToNocodb() {
  if (!nocodbUrl.value || !nocodbToken.value || !nocodbTable.value) {
    nocodbStatus.value = { ok: false, msg: 'Completa URL, token y tabla ID' }
    return
  }
  nocodbStatus.value = null
  try {
    const scenes = edit.value.scene_prompts || []
    let imported = 0
    let failed = 0
    for (const scene of scenes) {
      const title = `${item.value.title}-${scene.prompt.substring(0, 20)}`.replace(/[^a-zA-Z0-9-_]/g, '_')
      const record = {
        Title: title,
        prompt: scene.prompt || '',
        imagenref: scene.image_url || '',
        promptv: scene.prompt_video || '',
        visto: false,
        video: false,
      }
      const res = await fetch(`${nocodbUrl.value}/api/v2/tables/${nocodbTable.value}/records`, {
        method: 'POST',
        headers: {
          'xc-token': nocodbToken.value,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify([record])
      })
      if (res.ok) {
        imported++
      } else {
        failed++
      }
    }
    nocodbStatus.value = {
      ok: failed === 0,
      msg: `Exportados ${imported} escena${imported !== 1 ? 's' : ''}${failed > 0 ? `, ${failed} fallo${failed !== 1 ? 's' : ''}` : ''}`
    }
  } catch (e) {
    nocodbStatus.value = { ok: false, msg: `Error: ${e.message}` }
  }
}

async function renderScriptPrompt() {
  if (!scriptPrompt.value) return
  try {
    // Usar el endpoint correcto que usa build_render_context con content_id
    const res = await apiFetch(`/api/v3/prompts/render/${item.value.channel_id}?content_id=${item.value.id}&prompt_id=${scriptPrompt.value.id}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({}),
    })
    renderedScript.value = res.rendered
  } catch (e) { error.value = e.message }
}

async function addNote() {
  if (!newNoteContent.value.trim()) return
  try {
    const note = await apiFetch(`/api/v3/content/${item.value.id}/notes?channel_id=${item.value.channel_id}`, {
      method: 'POST',
      body: JSON.stringify({ note_type: newNoteType.value, content: newNoteContent.value }),
    })
    if (!item.value.notes) item.value.notes = []
    item.value.notes.push(note)
    newNoteContent.value = ''
  } catch (e) { error.value = e.message }
}

async function deleteNote(noteId) {
  try {
    await apiFetch(`/api/v3/content/${item.value.id}/notes/${noteId}?channel_id=${item.value.channel_id}`, { method: 'DELETE' })
    item.value.notes = item.value.notes.filter(n => n.id !== noteId)
  } catch (e) { error.value = e.message }
}

async function addScore() {
  try {
    const score = await apiFetch(`/api/v3/content/${item.value.id}/scores?channel_id=${item.value.channel_id}`, {
      method: 'POST',
      body: JSON.stringify({ metric_type: newScoreMetric.value, value: newScoreValue.value }),
    })
    if (!item.value.scores) item.value.scores = []
    item.value.scores.push(score)
    newScoreValue.value = 0
  } catch (e) { error.value = e.message }
}

async function createVersion() {
  try {
    const v = await apiFetch(`/api/v3/content/${item.value.id}/versions?channel_id=${item.value.channel_id}`, {
      method: 'POST',
      body: JSON.stringify({}),
    })
    versions.value.push(v)
  } catch (e) { error.value = e.message }
}

async function revertToVersion(vNum) {
  if (!confirm(`¿Revertir a versión ${vNum}?`)) return
  try {
    const updated = await apiFetch(`/api/v3/content/${item.value.id}/revert/${vNum}?channel_id=${item.value.channel_id}`, { method: 'POST' })
    item.value = updated
  } catch (e) { error.value = e.message }
}
</script>

<style scoped>
.pipeline-flow { display: flex; align-items: center; gap: 0.25rem; flex-wrap: wrap; }
.pip-stage { color: #3a3d4a; font-size: 0.85rem; transition: color 0.2s; }
.pip-stage.active { color: #6366f1; font-weight: 600; }
.pip-stage.done { color: #4ade80; }
.pipeline-arrow { color: #3a3d4a; margin: 0 0.1rem; }
.note-item { display: flex; align-items: center; gap: 0.5rem; padding: 0.4rem 0; border-bottom: 1px solid #1f2230; }
.note-type { font-size: 0.7rem; padding: 0.1rem 0.4rem; border-radius: 4px; font-weight: 600; text-transform: uppercase; }
.note-type.strength { background: rgba(34,197,94,0.2); color: #4ade80; }
.note-type.weakness { background: rgba(239,68,68,0.2); color: #f87171; }
.note-type.improvement { background: rgba(99,102,241,0.2); color: #a5b4fc; }
.note-type.general { background: rgba(156,163,175,0.2); color: #9ca3af; }
.scene-item { background: #0f1117; padding: 0.75rem; border-radius: 6px; margin-bottom: 0.5rem; }
.rendered-output { margin-top: 0.75rem; background: #0f1117; padding: 0.75rem; border-radius: 6px; font-size: 0.85rem; color: #4ade80; white-space: pre-wrap; }
.version-item { display: flex; justify-content: space-between; align-items: center; padding: 0.4rem 0; border-bottom: 1px solid #1f2230; }
.prompt-preview { background: #0f1117; padding: 0.5rem; border-radius: 4px; font-family: monospace; font-size: 0.8rem; color: #67e8f9; }
.ideas-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 0.75rem; }
.idea-card { background: #0f1117; border: 1px solid #1e2030; border-radius: 8px; padding: 0.875rem; display: flex; flex-direction: column; gap: 0.35rem; }
.idea-header { display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap; }
.idea-number { background: #6366f1; color: white; border-radius: 50%; width: 20px; height: 20px; display: flex; align-items: center; justify-content: center; font-size: 0.7rem; flex-shrink: 0; }
.idea-card strong { color: #e0e0e0; font-size: 0.9rem; flex: 1; }
.score-badge { background: rgba(99,102,241,0.2); color: #a5b4fc; padding: 0.1rem 0.4rem; border-radius: 4px; font-size: 0.75rem; }
.idea-row { font-size: 0.82rem; color: #9ca3af; line-height: 1.4; }
.idea-meta { font-size: 0.78rem; color: #6b7280; margin-top: 0.25rem; }
.nocodb-msg.success { color: #4ade80; }
.nocodb-msg.error { color: #f87171; }
</style>
