import { createApp } from 'vue'
import { createRouter, createWebHashHistory } from 'vue-router'
import App from './App.vue'

// Views
import LoginView from './views/LoginView.vue'
import DashboardView from './views/DashboardView.vue'
import ChannelsView from './views/ChannelsView.vue'
import PromptsView from './views/PromptsView.vue'
import ContentView from './views/ContentView.vue'
import ContentDetailView from './views/ContentDetailView.vue'
import PipelineView from './views/PipelineView.vue'
import SettingsView from './views/SettingsView.vue'

// ─── Router ───────────────────────────────────────────────────────────────────

const routes = [
  { path: '/', redirect: '/dashboard' },
  { path: '/login', component: LoginView },
  { path: '/dashboard', component: DashboardView, meta: { requiresAuth: true } },
  { path: '/channels', component: ChannelsView, meta: { requiresAuth: true } },
  { path: '/prompts', component: PromptsView, meta: { requiresAuth: true } },
  { path: '/content', component: ContentView, meta: { requiresAuth: true } },
  { path: '/content/:id', component: ContentDetailView, meta: { requiresAuth: true } },
  { path: '/pipeline', component: PipelineView, meta: { requiresAuth: true } },
  { path: '/settings', component: SettingsView, meta: { requiresAuth: true } },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

// ─── Auth Guard ───────────────────────────────────────────────────────────────

const TOKEN_KEY = 'wui_token'

export function getToken() {
  return localStorage.getItem(TOKEN_KEY)
}

export function setToken(t) {
  localStorage.setItem(TOKEN_KEY, t)
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY)
}

let authCheckDone = false

router.beforeEach((to) => {
  if (!authCheckDone) {
    // First load — try to restore user from token
    const token = getToken()
    if (token) {
      apiFetch('/api/v3/auth/me', { token }).then(user => {
        if (user) store.user = user
      }).catch(() => clearToken())
    }
    authCheckDone = true
  }
  if (to.meta.requiresAuth && !getToken()) {
    return '/login'
  }
  return true
})

// ─── Global Store (simple reactive) ───────────────────────────────────────────

import { reactive, readonly } from 'vue'

const store = reactive({
  user: null,
  loading: false,
  error: null,
})

export const useStore = () => store

// ─── API Helper ───────────────────────────────────────────────────────────────

export async function apiFetch(url, options = {}) {
  const token = getToken()
  const headers = { 'Content-Type': 'application/json' }
  if (token) headers['Authorization'] = `Bearer ${token}`

  const res = await fetch(url, { ...options, headers: { ...headers, ...options.headers } })
  if (res.status === 401) {
    clearToken()
    window.location.hash = '#/login'
    throw new Error('Unauthorized')
  }
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new Error(body.detail || `HTTP ${res.status}`)
  }
  if (res.status === 204) return null
  return res.json()
}

// ─── App ──────────────────────────────────────────────────────────────────────

createApp(App).use(router).mount('#app')
