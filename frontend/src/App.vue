<template>
  <div id="app-root">
    <nav v-if="store.user" class="top-nav">
      <span class="logo">🎬 WUI</span>
      <router-link to="/dashboard">Dashboard</router-link>
      <router-link to="/channels">Canales</router-link>
      <router-link to="/content">Contenido</router-link>
      <router-link to="/prompts">Prompts</router-link>
      <router-link to="/pipeline">Pipeline</router-link>
      <router-link to="/settings">⚙️ Ajustes</router-link>
      <div class="user-menu">
        <div class="user-avatar">{{ store.user.name ? store.user.name[0].toUpperCase() : '?' }}</div>
        <span class="user-name">{{ store.user.name || store.user.email }}</span>
        <button class="logout-btn" @click="logout">Cerrar sesión</button>
      </div>
    </nav>
    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { useStore, clearToken } from './main.js'
import { useRouter } from 'vue-router'

const store = useStore()
const router = useRouter()

function logout() {
  clearToken()
  store.user = null
  router.push('/login')
}
</script>

<style>
#app-root { display: flex; flex-direction: column; min-height: 100vh; }

.top-nav {
  display: flex; align-items: center; gap: 1.5rem;
  padding: 0.75rem 1.5rem;
  background: #1a1d27; border-bottom: 1px solid #2a2d3a;
  position: sticky; top: 0; z-index: 100;
}
.top-nav .logo { font-weight: 700; font-size: 1.1rem; color: #6366f1; margin-right: auto; }
.top-nav a { color: #a0a0b0; font-size: 0.9rem; transition: color 0.2s; }
.top-nav a:hover, .top-nav a.router-link-active { color: #e0e0e0; text-decoration: none; }
.top-nav .user-menu { display: flex; align-items: center; gap: 0.6rem; margin-left: auto; }
.top-nav .user-avatar {
  width: 32px; height: 32px; border-radius: 50%;
  background: #6366f1; color: #fff;
  display: flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: 0.85rem;
}
.top-nav .user-name { color: #a0a0b0; font-size: 0.85rem; }
.logout-btn { background: none; border: 1px solid #3a3d4a; color: #888; font-size: 0.8rem; padding: 0.25rem 0.6rem; border-radius: 4px; cursor: pointer; }
.logout-btn:hover { border-color: #ef4444; color: #ef4444; }

.main-content { flex: 1; padding: 2rem; max-width: 1200px; margin: 0 auto; width: 100%; }

/* Cards */
.card { background: #1a1d27; border: 1px solid #2a2d3a; border-radius: 8px; padding: 1.5rem; margin-bottom: 1rem; }
.card-title { font-size: 1.1rem; font-weight: 600; margin-bottom: 1rem; color: #e0e0e0; }

/* Forms */
.form-group { display: flex; flex-direction: column; gap: 0.4rem; margin-bottom: 1rem; }
label { font-size: 0.85rem; color: #888; }
input, textarea, select {
  background: #0f1117; border: 1px solid #2a2d3a; color: #e0e0e0;
  padding: 0.5rem 0.75rem; border-radius: 6px; font-size: 0.95rem;
  transition: border-color 0.2s; width: 100%;
}
input:focus, textarea:focus, select:focus { outline: none; border-color: #6366f1; }
textarea { resize: vertical; min-height: 100px; }
button.primary { background: #6366f1; color: #fff; border: none; padding: 0.6rem 1.2rem; border-radius: 6px; font-size: 0.9rem; font-weight: 500; cursor: pointer; }
button.primary:hover { background: #4f46e5; }
button.primary:disabled { opacity: 0.5; cursor: not-allowed; }
button.danger { background: #ef4444; color: #fff; border: none; padding: 0.4rem 0.8rem; border-radius: 4px; font-size: 0.85rem; cursor: pointer; }
button.secondary { background: #2a2d3a; color: #e0e0e0; border: 1px solid #2a2d3a; padding: 0.4rem 0.8rem; border-radius: 4px; font-size: 0.85rem; cursor: pointer; }
button.secondary:hover { border-color: #6366f1; }

/* Tables */
table { width: 100%; border-collapse: collapse; }
th { text-align: left; padding: 0.5rem; font-size: 0.8rem; color: #666; border-bottom: 1px solid #2a2d3a; font-weight: 500; text-transform: uppercase; }
td { padding: 0.75rem 0.5rem; border-bottom: 1px solid #1f2230; font-size: 0.9rem; }
tr:hover td { background: #1f2230; }

/* Alerts */
.alert { padding: 0.75rem 1rem; border-radius: 6px; margin-bottom: 1rem; font-size: 0.9rem; }
.alert.error { background: rgba(239,68,68,0.15); border: 1px solid rgba(239,68,68,0.3); color: #f87171; }
.alert.success { background: rgba(34,197,94,0.15); border: 1px solid rgba(34,197,94,0.3); color: #4ade80; }

/* Stage badges */
.stage-badge { display: inline-block; padding: 0.2rem 0.6rem; border-radius: 12px; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; }
.stage-idea { background: #3b3b6d; color: #a5b4fc; }
.stage-script { background: #3b4d5a; color: #67e8f9; }
.stage-graphic { background: #4a3b5a; color: #d8b4fe; }
.stage-video { background: #4a3b2a; color: #fcd34d; }
.stage-published { background: #1b4a3a; color: #4ade80; }

/* Grid helpers */
.grid-2 { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 1rem; }
.grid-3 { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 1rem; }

/* Page headers */
.page-header { margin-bottom: 1.5rem; }
.page-title { font-size: 1.5rem; font-weight: 700; color: #e0e0e0; }
.page-subtitle { font-size: 0.9rem; color: #666; margin-top: 0.25rem; }

/* Tabs */
.tabs { display: flex; gap: 0.25rem; border-bottom: 1px solid #2a2d3a; margin-bottom: 1.5rem; }
.tab { background: none; border: none; color: #666; padding: 0.5rem 1rem; cursor: pointer; font-size: 0.9rem; border-bottom: 2px solid transparent; transition: all 0.2s; }
.tab:hover { color: #e0e0e0; }
.tab.active { color: #6366f1; border-bottom-color: #6366f1; }

/* API config card */
.api-card { border: 1px solid #2a2d3a; border-radius: 8px; padding: 1.25rem; margin-bottom: 1rem; }
.api-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem; }
.api-name { font-weight: 600; color: #e0e0e0; font-size: 1rem; }
.toggle { position: relative; width: 40px; height: 22px; }
.toggle input { opacity: 0; width: 0; height: 0; }
.toggle-slider { position: absolute; cursor: pointer; inset: 0; background: #2a2d3a; border-radius: 22px; transition: 0.2s; }
.toggle-slider:before { position: absolute; content: ''; height: 16px; width: 16px; left: 3px; bottom: 3px; background: white; border-radius: 50%; transition: 0.2s; }
.toggle input:checked + .toggle-slider { background: #6366f1; }
.toggle input:checked + .toggle-slider:before { transform: translateX(18px); }

/* Backup list */
.backup-item { display: flex; align-items: center; justify-content: space-between; padding: 0.75rem; border: 1px solid #2a2d3a; border-radius: 6px; margin-bottom: 0.5rem; }
.backup-info { display: flex; flex-direction: column; gap: 0.2rem; }
.backup-id { font-size: 0.75rem; color: #6366f1; font-family: monospace; }
.backup-meta { font-size: 0.8rem; color: #666; }
.backup-actions { display: flex; gap: 0.5rem; }
</style>
