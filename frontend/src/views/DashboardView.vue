<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">👋 Bienvenido{{ store.user?.name ? ', ' + store.user.name : '' }}</h1>
      <p class="page-subtitle">Resumen de tu actividad</p>
    </div>

    <div v-if="error" class="alert error">{{ error }}</div>

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
      <div v-if="recentContent.length === 0" style="color:#666; font-size:0.9rem;">Sin contenido aún. <router-link to="/content">Crea el primero</router-link></div>
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
          <tr v-for="item in recentContent" :key="item.id" @click="goToContent(item)" style="cursor:pointer;">
            <td>{{ item.title }}</td>
            <td>{{ item.channel_id }}</td>
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
const stages = ['idea', 'script', 'graphic', 'video', 'published']

onMounted(async () => {
  try {
    const [channels, content, prompts] = await Promise.all([
      apiFetch('/api/v3/channels'),
      apiFetch('/api/v3/content'),
      apiFetch('/api/v3/prompts'),
    ])
    stats.channels = channels.length
    stats.content = content.length
    stats.prompts = prompts.length
    recentContent.value = content.slice(-5).reverse()
  } catch (e) {
    error.value = e.message
  }
})

function goToContent(item) {
  router.push(`/content/${item.id}?channel=${item.channel_id}`)
}
</script>

<style scoped>
.stat-card { text-align: center; }
.stat-value { font-size: 2rem; font-weight: 700; color: #6366f1; }
.stat-label { font-size: 0.85rem; color: #888; margin-top: 0.25rem; }
.pipeline-flow { display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap; }
.pipeline-stage { color: #a0a0b0; font-size: 0.9rem; }
.pipeline-arrow { color: #6366f1; margin: 0 0.25rem; }
</style>
