# Техническое Задание: UI Core - Каркас и Базовая Логика

## Цель
Создать стабильный каркас фронтенда по утвержденной информационной архитектуре (IA), без прикладных функций. Чистая основа для последующего развития BCM Platform.

## Техническая База

### Технологический Стек
- **Frontend Framework**: Vue 3.4+ с Composition API
- **Routing**: Vue Router 4.x
- **UI Framework**: Bootstrap 5.3+
- **Icons**: FontAwesome 6.x
- **Charts**: Chart.js 4.x
- **State Management**: Pinia (для Vue 3)
- **HTTP Client**: Axios
- **Build Tool**: Vite

### Архитектурные Принципы
- **JWT Authentication**: Middleware для всех API вызовов
- **Role-Based Access**: Route guards на основе ролей
- **Real-time Updates**: SSE/WebSocket для EventBus
- **Multi-tenancy**: tenant_id во всех запросах
- **Error Handling**: Централизованная обработка ошибок

## Задача 1: Роутинг и Навигация

### 1.1 Структура Маршрутов
```javascript
// router/index.js
const routes = [
  {
    path: '/',
    redirect: '/overview'
  },
  {
    path: '/overview',
    name: 'Overview',
    component: () => import('@/views/Overview.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/events',
    name: 'Events',
    component: () => import('@/views/Events.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/orchestrator',
    name: 'Orchestrator',
    component: () => import('@/views/Orchestrator.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/documents',
    name: 'Documents',
    component: () => import('@/views/Documents.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/admin',
    name: 'Admin',
    component: () => import('@/views/Admin.vue'),
    meta: { requiresAuth: true, requiresRole: 'bcm_manager' }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { guest: true }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue')
  }
]
```

### 1.2 Навигационная Панель
```vue
<!-- components/NavBar.vue -->
<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
    <div class="container-fluid">
      <a class="navbar-brand" href="/">
        <i class="fas fa-shield-alt"></i> BCM Platform
      </a>
      
      <div class="navbar-nav">
        <router-link to="/overview" class="nav-link" 
                     :class="{ active: $route.path === '/overview' }">
          <i class="fas fa-dashboard"></i> Overview
        </router-link>
        
        <router-link to="/events" class="nav-link"
                     :class="{ active: $route.path === '/events' }">
          <i class="fas fa-stream"></i> Events
        </router-link>
        
        <router-link to="/orchestrator" class="nav-link"
                     :class="{ active: $route.path === '/orchestrator' }">
          <i class="fas fa-robot"></i> Orchestrator
        </router-link>
        
        <router-link to="/documents" class="nav-link"
                     :class="{ active: $route.path === '/documents' }">
          <i class="fas fa-file-alt"></i> Documents
        </router-link>
        
        <router-link v-if="userRole === 'bcm_manager'" 
                     to="/admin" class="nav-link"
                     :class="{ active: $route.path === '/admin' }">
          <i class="fas fa-cog"></i> Admin
        </router-link>
      </div>
      
      <div class="navbar-nav ms-auto">
        <span class="navbar-text me-3">
          <i class="fas fa-building"></i> {{ tenantName }}
        </span>
        <span class="navbar-text me-3">
          <i class="fas fa-user"></i> {{ userName }}
        </span>
        <button @click="logout" class="btn btn-outline-light btn-sm">
          <i class="fas fa-sign-out-alt"></i> Logout
        </button>
      </div>
    </div>
  </nav>
</template>
```

## Задача 2: Аутентификация и JWT

### 2.1 JWT Parser и Storage
```javascript
// services/auth.js
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

class AuthService {
  constructor() {
    this.token = localStorage.getItem('jwt_token')
    this.refreshToken = localStorage.getItem('refresh_token')
    this.initializeAxiosInterceptors()
  }

  parseJWT(token) {
    try {
      const base64Url = token.split('.')[1]
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
      const jsonPayload = decodeURIComponent(
        atob(base64).split('').map(c => 
          '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2)
        ).join('')
      )
      return JSON.parse(jsonPayload)
    } catch (error) {
      console.error('Invalid JWT token')
      return null
    }
  }

  getTokenData() {
    if (!this.token) return null
    const payload = this.parseJWT(this.token)
    return {
      tenant_id: payload?.tenant_id,
      user_id: payload?.user_id,
      role: payload?.role,
      exp: payload?.exp,
      email: payload?.email
    }
  }

  setToken(token, refreshToken) {
    this.token = token
    this.refreshToken = refreshToken
    localStorage.setItem('jwt_token', token)
    localStorage.setItem('refresh_token', refreshToken)
    
    // Update store
    const authStore = useAuthStore()
    const tokenData = this.getTokenData()
    authStore.setUser(tokenData)
  }

  async refreshAccessToken() {
    try {
      const response = await axios.post('/api/auth/refresh', {
        refresh_token: this.refreshToken
      })
      this.setToken(response.data.access_token, response.data.refresh_token)
      return response.data.access_token
    } catch (error) {
      this.logout()
      throw error
    }
  }

  initializeAxiosInterceptors() {
    // Request interceptor - add JWT to all requests
    axios.interceptors.request.use(
      config => {
        if (this.token) {
          config.headers.Authorization = `Bearer ${this.token}`
          const tokenData = this.getTokenData()
          if (tokenData?.tenant_id) {
            config.headers['X-Tenant-ID'] = tokenData.tenant_id
          }
        }
        return config
      },
      error => Promise.reject(error)
    )

    // Response interceptor - handle 401 and refresh token
    axios.interceptors.response.use(
      response => response,
      async error => {
        const originalRequest = error.config
        
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true
          try {
            const newToken = await this.refreshAccessToken()
            originalRequest.headers.Authorization = `Bearer ${newToken}`
            return axios(originalRequest)
          } catch (refreshError) {
            window.location.href = '/login'
            return Promise.reject(refreshError)
          }
        }
        
        return Promise.reject(error)
      }
    )
  }

  logout() {
    this.token = null
    this.refreshToken = null
    localStorage.removeItem('jwt_token')
    localStorage.removeItem('refresh_token')
    window.location.href = '/login'
  }
}

export default new AuthService()
```

### 2.2 Route Guards
```javascript
// router/guards.js
import authService from '@/services/auth'

export const authGuard = (to, from, next) => {
  const tokenData = authService.getTokenData()
  
  // Check if route requires authentication
  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!tokenData || !tokenData.user_id) {
      next({ path: '/login', query: { redirect: to.fullPath } })
      return
    }
    
    // Check token expiration
    if (tokenData.exp && tokenData.exp * 1000 < Date.now()) {
      authService.logout()
      return
    }
  }
  
  // Check role requirements
  if (to.matched.some(record => record.meta.requiresRole)) {
    const requiredRole = to.meta.requiresRole
    if (tokenData.role !== requiredRole) {
      next({ path: '/overview' }) // Redirect to safe page
      return
    }
  }
  
  // Guest routes (login page)
  if (to.matched.some(record => record.meta.guest)) {
    if (tokenData && tokenData.user_id) {
      next({ path: '/overview' })
      return
    }
  }
  
  next()
}
```

## Задача 3: Overview - KPI и PDCA

### 3.1 KPI Service
```javascript
// services/kpi.js
import axios from 'axios'

class KPIService {
  async getCurrentKPIs() {
    try {
      const response = await axios.get('/bcm/kpi', {
        headers: {
          'Company-ID': authService.getTokenData()?.tenant_id
        }
      })
      
      return {
        bia_coverage: response.data.bia_coverage || 0,
        plans_up_to_date: response.data.plans_up_to_date || 0,
        capa_on_time: response.data.capa_on_time || 0,
        incident_response_time: response.data.incident_response_time || 0,
        exercise_completion: response.data.exercise_completion || 0,
        training_completion: response.data.training_completion || 0
      }
    } catch (error) {
      console.error('Failed to fetch KPIs:', error)
      // Return default values on error
      return {
        bia_coverage: 0,
        plans_up_to_date: 0,
        capa_on_time: 0,
        incident_response_time: 0,
        exercise_completion: 0,
        training_completion: 0
      }
    }
  }

  calculateHealthScore(kpis) {
    // Weighted average calculation
    const weights = {
      bia_coverage: 0.20,
      plans_up_to_date: 0.20,
      capa_on_time: 0.15,
      incident_response_time: 0.15,
      exercise_completion: 0.15,
      training_completion: 0.15
    }
    
    let score = 0
    score += kpis.bia_coverage * weights.bia_coverage
    score += kpis.plans_up_to_date * weights.plans_up_to_date
    score += kpis.capa_on_time * weights.capa_on_time
    score += (100 - Math.min(kpis.incident_response_time * 10, 100)) * weights.incident_response_time
    score += kpis.exercise_completion * weights.exercise_completion
    score += kpis.training_completion * weights.training_completion
    
    return Math.round(score)
  }

  determineCurrentPDCAPhase(kpis) {
    // Logic to determine current PDCA phase based on KPIs
    if (kpis.incident_response_time > 4) {
      return 'DO' // Active incident response
    }
    if (kpis.capa_on_time < 80) {
      return 'ACT' // CAPA management needed
    }
    if (kpis.bia_coverage < 80 || kpis.plans_up_to_date < 75) {
      return 'PLAN' // Planning needed
    }
    if (kpis.exercise_completion < 85 || kpis.training_completion < 85) {
      return 'CHECK' // Validation needed
    }
    return 'PLAN' // Default to continuous planning
  }
}

export default new KPIService()
```

### 3.2 Overview Component
```vue
<!-- views/Overview.vue -->
<template>
  <div class="container-fluid p-4">
    <!-- PDCA Phase Indicator -->
    <div class="row mb-4">
      <div class="col-12">
        <div class="card">
          <div class="card-body">
            <h5 class="card-title">Current PDCA Phase</h5>
            <div class="pdca-indicator d-flex justify-content-around">
              <div v-for="phase in ['PLAN', 'DO', 'CHECK', 'ACT']" :key="phase"
                   class="pdca-phase" 
                   :class="{ 'active': currentPhase === phase }">
                <div class="phase-circle">
                  <i :class="getPhaseIcon(phase)"></i>
                </div>
                <div class="phase-label">{{ phase }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- KPI Cards -->
    <div class="row mb-4">
      <div class="col-md-4 mb-3" v-for="kpi in kpiData" :key="kpi.name">
        <div class="card h-100">
          <div class="card-body">
            <h6 class="card-subtitle mb-2 text-muted">
              <i :class="kpi.icon"></i> {{ kpi.label }}
            </h6>
            <div class="d-flex align-items-center">
              <h2 class="mb-0 me-2" :class="getKPIColorClass(kpi)">
                {{ formatKPIValue(kpi) }}
              </h2>
              <small class="text-muted">
                Target: {{ kpi.target }}
              </small>
            </div>
            <div class="progress mt-2" style="height: 5px;">
              <div class="progress-bar" 
                   :class="getKPIProgressClass(kpi)"
                   :style="{ width: getKPIProgress(kpi) + '%' }">
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Health Score Chart -->
    <div class="row">
      <div class="col-md-6">
        <div class="card">
          <div class="card-body">
            <h5 class="card-title">BCM Health Score</h5>
            <canvas id="healthScoreChart"></canvas>
          </div>
        </div>
      </div>
      
      <div class="col-md-6">
        <div class="card">
          <div class="card-body">
            <h5 class="card-title">KPI Trends</h5>
            <canvas id="kpiTrendsChart"></canvas>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import Chart from 'chart.js/auto'
import kpiService from '@/services/kpi'

const kpiData = ref([])
const currentPhase = ref('PLAN')
const healthScore = ref(0)
let healthChart = null
let trendsChart = null

const kpiDefinitions = [
  {
    name: 'bia_coverage',
    label: 'BIA Coverage',
    icon: 'fas fa-chart-pie',
    target: '≥80%',
    threshold: 80,
    unit: '%'
  },
  {
    name: 'plans_up_to_date',
    label: 'Plans Current',
    icon: 'fas fa-file-alt',
    target: '≥75%',
    threshold: 75,
    unit: '%'
  },
  {
    name: 'capa_on_time',
    label: 'CAPA On-time',
    icon: 'fas fa-tasks',
    target: '≥90%',
    threshold: 90,
    unit: '%'
  },
  {
    name: 'incident_response_time',
    label: 'Response Time',
    icon: 'fas fa-clock',
    target: '<4h',
    threshold: 4,
    unit: 'h',
    inverse: true
  },
  {
    name: 'exercise_completion',
    label: 'Exercise Completion',
    icon: 'fas fa-dumbbell',
    target: '≥85%',
    threshold: 85,
    unit: '%'
  },
  {
    name: 'training_completion',
    label: 'Training Completion',
    icon: 'fas fa-graduation-cap',
    target: '≥85%',
    threshold: 85,
    unit: '%'
  }
]

onMounted(async () => {
  await loadKPIs()
  initializeCharts()
  // Refresh KPIs every 60 seconds
  const refreshInterval = setInterval(loadKPIs, 60000)
  
  onUnmounted(() => {
    clearInterval(refreshInterval)
    if (healthChart) healthChart.destroy()
    if (trendsChart) trendsChart.destroy()
  })
})

async function loadKPIs() {
  const kpis = await kpiService.getCurrentKPIs()
  
  kpiData.value = kpiDefinitions.map(def => ({
    ...def,
    value: kpis[def.name]
  }))
  
  healthScore.value = kpiService.calculateHealthScore(kpis)
  currentPhase.value = kpiService.determineCurrentPDCAPhase(kpis)
  
  updateCharts()
}

function initializeCharts() {
  // Health Score Gauge Chart
  const healthCtx = document.getElementById('healthScoreChart')
  healthChart = new Chart(healthCtx, {
    type: 'doughnut',
    data: {
      datasets: [{
        data: [healthScore.value, 100 - healthScore.value],
        backgroundColor: [getHealthColor(healthScore.value), '#e9ecef'],
        borderWidth: 0
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '70%',
      plugins: {
        legend: { display: false },
        tooltip: { enabled: false }
      }
    }
  })
  
  // KPI Trends Line Chart
  const trendsCtx = document.getElementById('kpiTrendsChart')
  trendsChart = new Chart(trendsCtx, {
    type: 'line',
    data: {
      labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
      datasets: kpiData.value.map((kpi, index) => ({
        label: kpi.label,
        data: generateMockTrendData(),
        borderColor: getChartColor(index),
        tension: 0.4
      }))
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          max: 100
        }
      }
    }
  })
}

function getPhaseIcon(phase) {
  const icons = {
    PLAN: 'fas fa-clipboard-list',
    DO: 'fas fa-play-circle',
    CHECK: 'fas fa-check-circle',
    ACT: 'fas fa-sync-alt'
  }
  return icons[phase]
}

function formatKPIValue(kpi) {
  if (kpi.unit === '%') {
    return `${Math.round(kpi.value)}%`
  }
  if (kpi.unit === 'h') {
    return `${kpi.value.toFixed(1)}h`
  }
  return kpi.value
}

function getKPIColorClass(kpi) {
  const meetsThreshold = kpi.inverse 
    ? kpi.value <= kpi.threshold 
    : kpi.value >= kpi.threshold
  
  if (meetsThreshold) return 'text-success'
  if (kpi.value >= kpi.threshold * 0.9) return 'text-warning'
  return 'text-danger'
}

function getKPIProgress(kpi) {
  if (kpi.inverse) {
    return Math.max(0, Math.min(100, (1 - kpi.value / 10) * 100))
  }
  return Math.min(100, kpi.value)
}

function getKPIProgressClass(kpi) {
  const progress = getKPIProgress(kpi)
  if (progress >= 80) return 'bg-success'
  if (progress >= 60) return 'bg-warning'
  return 'bg-danger'
}

function getHealthColor(score) {
  if (score >= 80) return '#28a745'
  if (score >= 60) return '#ffc107'
  return '#dc3545'
}

function getChartColor(index) {
  const colors = [
    '#007bff', '#28a745', '#dc3545', 
    '#ffc107', '#17a2b8', '#6610f2'
  ]
  return colors[index % colors.length]
}

function generateMockTrendData() {
  // Mock data for demonstration
  return Array.from({ length: 6 }, () => 
    Math.floor(Math.random() * 30) + 70
  )
}

function updateCharts() {
  if (healthChart) {
    healthChart.data.datasets[0].data = [healthScore.value, 100 - healthScore.value]
    healthChart.data.datasets[0].backgroundColor[0] = getHealthColor(healthScore.value)
    healthChart.update()
  }
}
</script>

<style scoped>
.pdca-indicator {
  padding: 20px 0;
}

.pdca-phase {
  text-align: center;
  opacity: 0.4;
  transition: all 0.3s ease;
}

.pdca-phase.active {
  opacity: 1;
  transform: scale(1.1);
}

.phase-circle {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: #f8f9fa;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 10px;
  font-size: 24px;
  border: 3px solid #dee2e6;
}

.pdca-phase.active .phase-circle {
  background: #007bff;
  color: white;
  border-color: #007bff;
}

.phase-label {
  font-weight: bold;
  font-size: 14px;
}

#healthScoreChart,
#kpiTrendsChart {
  height: 300px;
}
</style>
```

## Задача 4: Events - EventMonitor

### 4.1 EventBus Service
```javascript
// services/eventbus.js
import axios from 'axios'
import authService from './auth'

class EventBusService {
  constructor() {
    this.eventSource = null
    this.websocket = null
    this.listeners = new Map()
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 5
    this.reconnectDelay = 1000
  }

  // Get historical events
  async history(filters = {}) {
    const params = {
      tenant_id: authService.getTokenData()?.tenant_id,
      ...filters
    }
    
    try {
      const response = await axios.get('/api/events/history', { params })
      return response.data.events || []
    } catch (error) {
      console.error('Failed to fetch event history:', error)
      return []
    }
  }

  // Publish event
  async publish(eventType, data) {
    const payload = {
      event_type: eventType,
      tenant_id: authService.getTokenData()?.tenant_id,
      data: data,
      timestamp: new Date().toISOString()
    }
    
    try {
      const response = await axios.post('/api/events/publish', payload)
      return response.data
    } catch (error) {
      console.error('Failed to publish event:', error)
      throw error
    }
  }

  // Connect via Server-Sent Events
  connectSSE(onMessage, onError) {
    const tenantId = authService.getTokenData()?.tenant_id
    const token = authService.token
    
    if (!tenantId || !token) {
      console.error('Missing tenant_id or token for SSE connection')
      return
    }
    
    const url = `/api/events/stream?tenant_id=${tenantId}&token=${token}`
    
    this.eventSource = new EventSource(url)
    
    this.eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        onMessage(data)
        
        // Notify all registered listeners
        this.notifyListeners(data.event_type, data)
      } catch (error) {
        console.error('Failed to parse SSE message:', error)
      }
    }
    
    this.eventSource.onerror = (error) => {
      console.error('SSE connection error:', error)
      onError?.(error)
      
      // Auto-reconnect logic
      if (this.reconnectAttempts < this.maxReconnectAttempts) {
        setTimeout(() => {
          this.reconnectAttempts++
          this.connectSSE(onMessage, onError)
        }, this.reconnectDelay * Math.pow(2, this.reconnectAttempts))
      }
    }
    
    this.eventSource.onopen = () => {
      console.log('SSE connection established')
      this.reconnectAttempts = 0
    }
  }

  // Connect via WebSocket
  connectWS(onMessage, onError) {
    const tenantId = authService.getTokenData()?.tenant_id
    const token = authService.token
    
    if (!tenantId || !token) {
      console.error('Missing tenant_id or token for WebSocket connection')
      return
    }
    
    const wsUrl = `ws://localhost:8001/api/events/ws?tenant_id=${tenantId}&token=${token}`
    
    this.websocket = new WebSocket(wsUrl)
    
    this.websocket.onopen = () => {
      console.log('WebSocket connection established')
      this.reconnectAttempts = 0
    }
    
    this.websocket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        onMessage(data)
        
        // Notify all registered listeners
        this.notifyListeners(data.event_type, data)
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error)
      }
    }
    
    this.websocket.onerror = (error) => {
      console.error('WebSocket error:', error)
      onError?.(error)
    }
    
    this.websocket.onclose = () => {
      console.log('WebSocket connection closed')
      
      // Auto-reconnect logic
      if (this.reconnectAttempts < this.maxReconnectAttempts) {
        setTimeout(() => {
          this.reconnectAttempts++
          this.connectWS(onMessage, onError)
        }, this.reconnectDelay * Math.pow(2, this.reconnectAttempts))
      }
    }
  }

  // Disconnect
  disconnect() {
    if (this.eventSource) {
      this.eventSource.close()
      this.eventSource = null
    }
    
    if (this.websocket) {
      this.websocket.close()
      this.websocket = null
    }
    
    this.listeners.clear()
  }

  // Register event listener
  on(eventType, callback) {
    if (!this.listeners.has(eventType)) {
      this.listeners.set(eventType, new Set())
    }
    this.listeners.get(eventType).add(callback)
  }

  // Unregister event listener
  off(eventType, callback) {
    if (this.listeners.has(eventType)) {
      this.listeners.get(eventType).delete(callback)
    }
  }

  // Notify listeners
  notifyListeners(eventType, data) {
    // Exact match listeners
    if (this.listeners.has(eventType)) {
      this.listeners.get(eventType).forEach(callback => callback(data))
    }
    
    // Wildcard listeners
    if (this.listeners.has('*')) {
      this.listeners.get('*').forEach(callback => callback(data))
    }
    
    // Pattern match listeners (e.g., 'bcm.*')
    this.listeners.forEach((callbacks, pattern) => {
      if (pattern.includes('*')) {
        const regex = new RegExp(pattern.replace('*', '.*'))
        if (regex.test(eventType)) {
          callbacks.forEach(callback => callback(data))
        }
      }
    })
  }

  // Export events to CSV
  exportToCSV(events) {
    const headers = ['Timestamp', 'Event Type', 'Tenant ID', 'Data']
    const rows = events.map(event => [
      event.timestamp,
      event.event_type,
      event.tenant_id,
      JSON.stringify(event.data)
    ])
    
    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
    ].join('\n')
    
    const blob = new Blob([csvContent], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `events_${new Date().toISOString()}.csv`
    link.click()
    URL.revokeObjectURL(url)
  }

  // Export events to JSON
  exportToJSON(events) {
    const jsonContent = JSON.stringify(events, null, 2)
    const blob = new Blob([jsonContent], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `events_${new Date().toISOString()}.json`
    link.click()
    URL.revokeObjectURL(url)
  }
}

export default new EventBusService()
```

### 4.2 EventMonitor Component
```vue
<!-- views/Events.vue -->
<template>
  <div class="container-fluid p-4">
    <!-- Header and Controls -->
    <div class="row mb-4">
      <div class="col-12">
        <div class="card">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <h5 class="card-title mb-0">
                <i class="fas fa-stream"></i> Event Monitor
              </h5>
              <div class="btn-group">
                <button class="btn btn-sm" 
                        :class="connectionType === 'sse' ? 'btn-primary' : 'btn-outline-primary'"
                        @click="switchConnection('sse')">
                  <i class="fas fa-satellite-dish"></i> SSE
                </button>
                <button class="btn btn-sm"
                        :class="connectionType === 'ws' ? 'btn-primary' : 'btn-outline-primary'"
                        @click="switchConnection('ws')">
                  <i class="fas fa-plug"></i> WebSocket
                </button>
              </div>
            </div>
            
            <!-- Filters -->
            <div class="row g-2">
              <div class="col-md-3">
                <div class="input-group input-group-sm">
                  <span class="input-group-text">
                    <i class="fas fa-filter"></i>
                  </span>
                  <input v-model="filters.event_type" 
                         type="text" 
                         class="form-control"
                         placeholder="Event type (e.g., bcm.*)">
                </div>
              </div>
              
              <div class="col-md-3">
                <div class="input-group input-group-sm">
                  <span class="input-group-text">
                    <i class="fas fa-calendar"></i>
                  </span>
                  <input v-model="filters.date_from" 
                         type="datetime-local" 
                         class="form-control">
                </div>
              </div>
              
              <div class="col-md-3">
                <div class="input-group input-group-sm">
                  <span class="input-group-text">
                    <i class="fas fa-calendar"></i>
                  </span>
                  <input v-model="filters.date_to" 
                         type="datetime-local" 
                         class="form-control">
                </div>
              </div>
              
              <div class="col-md-3">
                <div class="btn-group btn-group-sm">
                  <button @click="applyFilters" class="btn btn-primary">
                    <i class="fas fa-search"></i> Apply
                  </button>
                  <button @click="clearFilters" class="btn btn-outline-secondary">
                    <i class="fas fa-times"></i> Clear
                  </button>
                  <button @click="exportEvents" class="btn btn-outline-success">
                    <i class="fas fa-download"></i> Export
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Connection Status -->
    <div class="row mb-3">
      <div class="col-12">
        <div class="alert" :class="connectionStatusClass">
          <i :class="connectionStatusIcon"></i>
          {{ connectionStatusText }}
          <span v-if="isConnected" class="float-end">
            Events: {{ events.length }} | Live: {{ liveEventCount }}
          </span>
        </div>
      </div>
    </div>

    <!-- Events Table -->
    <div class="row">
      <div class="col-12">
        <div class="card">
          <div class="card-body">
            <div class="table-responsive">
              <table class="table table-sm table-hover">
                <thead>
                  <tr>
                    <th width="180">Timestamp</th>
                    <th width="200">Event Type</th>
                    <th width="150">Tenant</th>
                    <th>Data</th>
                    <th width="100">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="event in paginatedEvents" :key="event.id" 
                      :class="{ 'table-info': event.isLive }">
                    <td>
                      <small>{{ formatTimestamp(event.timestamp) }}</small>
                    </td>
                    <td>
                      <span class="badge" :class="getEventTypeBadgeClass(event.event_type)">
                        {{ event.event_type }}
                      </span>
                    </td>
                    <td>
                      <small>{{ event.tenant_id }}</small>
                    </td>
                    <td>
                      <code class="event-data" @click="showEventDetails(event)">
                        {{ truncateJSON(event.data) }}
                      </code>
                    </td>
                    <td>
                      <button @click="showEventDetails(event)" 
                              class="btn btn-sm btn-outline-primary">
                        <i class="fas fa-eye"></i>
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            
            <!-- Pagination -->
            <nav v-if="totalPages > 1">
              <ul class="pagination pagination-sm justify-content-center">
                <li class="page-item" :class="{ disabled: currentPage === 1 }">
                  <a class="page-link" @click="currentPage--">Previous</a>
                </li>
                <li v-for="page in displayedPages" :key="page"
                    class="page-item" :class="{ active: currentPage === page }">
                  <a class="page-link" @click="currentPage = page">{{ page }}</a>
                </li>
                <li class="page-item" :class="{ disabled: currentPage === totalPages }">
                  <a class="page-link" @click="currentPage++">Next</a>
                </li>
              </ul>
            </nav>
          </div>
        </div>
      </div>
    </div>

    <!-- Event Details Modal -->
    <div class="modal fade" id="eventDetailsModal" tabindex="-1">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Event Details</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <pre>{{ JSON.stringify(selectedEvent, null, 2) }}</pre>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
              Close
            </button>
            <button @click="copyEventJSON" class="btn btn-primary">
              <i class="fas fa-copy"></i> Copy JSON
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { Modal } from 'bootstrap'
import eventBusService from '@/services/eventbus'

// State
const events = ref([])
const liveEventCount = ref(0)
const connectionType = ref('sse')
const isConnected = ref(false)
const connectionError = ref(null)
const filters = ref({
  event_type: '',
  date_from: '',
  date_to: '',
  tenant_id: ''
})
const selectedEvent = ref(null)
const currentPage = ref(1)
const itemsPerPage = 20

// Computed
const filteredEvents = computed(() => {
  let filtered = [...events.value]
  
  if (filters.value.event_type) {
    const pattern = filters.value.event_type.replace('*', '.*')
    const regex = new RegExp(pattern)
    filtered = filtered.filter(e => regex.test(e.event_type))
  }
  
  if (filters.value.date_from) {
    const fromDate = new Date(filters.value.date_from)
    filtered = filtered.filter(e => new Date(e.timestamp) >= fromDate)
  }
  
  if (filters.value.date_to) {
    const toDate = new Date(filters.value.date_to)
    filtered = filtered.filter(e => new Date(e.timestamp) <= toDate)
  }
  
  return filtered.sort((a, b) => 
    new Date(b.timestamp) - new Date(a.timestamp)
  )
})

const paginatedEvents = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return filteredEvents.value.slice(start, end)
})

const totalPages = computed(() => 
  Math.ceil(filteredEvents.value.length / itemsPerPage)
)

const displayedPages = computed(() => {
  const pages = []
  const maxPages = 5
  let start = Math.max(1, currentPage.value - 2)
  let end = Math.min(totalPages.value, start + maxPages - 1)
  
  if (end - start < maxPages - 1) {
    start = Math.max(1, end - maxPages + 1)
  }
  
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  
  return pages
})

const connectionStatusClass = computed(() => {
  if (isConnected.value) return 'alert-success'
  if (connectionError.value) return 'alert-danger'
  return 'alert-warning'
})

const connectionStatusIcon = computed(() => {
  if (isConnected.value) return 'fas fa-circle text-success'
  if (connectionError.value) return 'fas fa-exclamation-circle'
  return 'fas fa-spinner fa-spin'
})

const connectionStatusText = computed(() => {
  if (isConnected.value) {
    return `Connected via ${connectionType.value.toUpperCase()}`
  }
  if (connectionError.value) {
    return `Connection Error: ${connectionError.value}`
  }
  return 'Connecting...'
})

// Methods
async function loadHistoricalEvents() {
  const history = await eventBusService.history(filters.value)
  events.value = history.map(e => ({ ...e, isLive: false }))
}

function handleNewEvent(event) {
  // Add to beginning with live indicator
  events.value.unshift({ ...event, isLive: true, id: Date.now() })
  liveEventCount.value++
  
  // Remove live indicator after 3 seconds
  setTimeout(() => {
    const index = events.value.findIndex(e => e.id === event.id)
    if (index !== -1) {
      events.value[index].isLive = false
    }
  }, 3000)
  
  // Limit total events to prevent memory issues
  if (events.value.length > 1000) {
    events.value = events.value.slice(0, 1000)
  }
}

function handleConnectionError(error) {
  connectionError.value = error.message || 'Connection failed'
  isConnected.value = false
}

function switchConnection(type) {
  eventBusService.disconnect()
  connectionType.value = type
  connectToEventBus()
}

function connectToEventBus() {
  isConnected.value = false
  connectionError.value = null
  
  if (connectionType.value === 'sse') {
    eventBusService.connectSSE(
      (event) => {
        isConnected.value = true
        handleNewEvent(event)
      },
      handleConnectionError
    )
  } else {
    eventBusService.connectWS(
      (event) => {
        isConnected.value = true
        handleNewEvent(event)
      },
      handleConnectionError
    )
  }
}

async function applyFilters() {
  currentPage.value = 1
  await loadHistoricalEvents()
}

function clearFilters() {
  filters.value = {
    event_type: '',
    date_from: '',
    date_to: '',
    tenant_id: ''
  }
  applyFilters()
}

function exportEvents() {
  const format = confirm('Export as JSON? (Cancel for CSV)') ? 'json' : 'csv'
  
  if (format === 'json') {
    eventBusService.exportToJSON(filteredEvents.value)
  } else {
    eventBusService.exportToCSV(filteredEvents.value)
  }
}

function formatTimestamp(timestamp) {
  return new Date(timestamp).toLocaleString()
}

function getEventTypeBadgeClass(eventType) {
  if (eventType.startsWith('bcm.incident')) return 'bg-danger'
  if (eventType.startsWith('bcm.audit')) return 'bg-warning'
  if (eventType.startsWith('bcm.plan')) return 'bg-info'
  if (eventType.startsWith('assistant')) return 'bg-success'
  return 'bg-secondary'
}

function truncateJSON(data) {
  const str = JSON.stringify(data)
  if (str.length > 100) {
    return str.substring(0, 100) + '...'
  }
  return str
}

function showEventDetails(event) {
  selectedEvent.value = event
  const modal = new Modal(document.getElementById('eventDetailsModal'))
  modal.show()
}

function copyEventJSON() {
  navigator.clipboard.writeText(JSON.stringify(selectedEvent.value, null, 2))
    .then(() => alert('JSON copied to clipboard'))
}

// Lifecycle
onMounted(async () => {
  await loadHistoricalEvents()
  connectToEventBus()
})

onUnmounted(() => {
  eventBusService.disconnect()
})
</script>

<style scoped>
.event-data {
  cursor: pointer;
  max-width: 400px;
  display: inline-block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.event-data:hover {
  background-color: #f8f9fa;
}

.table-info {
  animation: highlight 3s ease-out;
}

@keyframes highlight {
  0% { background-color: #cff4fc; }
  100% { background-color: transparent; }
}
</style>
```

## Задача 5: Stores и State Management

```javascript
// stores/auth.js
import { defineStore } from 'pinia'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    tenant_id: null,
    role: null,
    isAuthenticated: false
  }),
  
  getters: {
    isBCMManager: (state) => state.role === 'bcm_manager',
    isAdmin: (state) => state.role === 'admin',
    canAccessAdmin: (state) => ['bcm_manager', 'admin'].includes(state.role)
  },
  
  actions: {
    setUser(userData) {
      this.user = userData
      this.tenant_id = userData?.tenant_id
      this.role = userData?.role
      this.isAuthenticated = !!userData
    },
    
    clearUser() {
      this.user = null
      this.tenant_id = null
      this.role = null
      this.isAuthenticated = false
    }
  }
})
```

## Задача 6: Базовые Компоненты

### Login Component
```vue
<!-- views/Login.vue -->
<template>
  <div class="container">
    <div class="row justify-content-center mt-5">
      <div class="col-md-4">
        <div class="card">
          <div class="card-body">
            <h4 class="card-title text-center mb-4">
              <i class="fas fa-shield-alt"></i> BCM Platform Login
            </h4>
            
            <form @submit.prevent="handleLogin">
              <div class="mb-3">
                <label class="form-label">Email</label>
                <input v-model="credentials.email" 
                       type="email" 
                       class="form-control"
                       required>
              </div>
              
              <div class="mb-3">
                <label class="form-label">Password</label>
                <input v-model="credentials.password" 
                       type="password" 
                       class="form-control"
                       required>
              </div>
              
              <div v-if="error" class="alert alert-danger">
                {{ error }}
              </div>
              
              <button type="submit" 
                      class="btn btn-primary w-100"
                      :disabled="loading">
                <span v-if="loading">
                  <i class="fas fa-spinner fa-spin"></i> Logging in...
                </span>
                <span v-else>
                  <i class="fas fa-sign-in-alt"></i> Login
                </span>
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'
import authService from '@/services/auth'

const router = useRouter()
const route = useRoute()

const credentials = ref({
  email: '',
  password: ''
})
const loading = ref(false)
const error = ref(null)

async function handleLogin() {
  loading.value = true
  error.value = null
  
  try {
    const response = await axios.post('/api/auth/login', credentials.value)
    authService.setToken(response.data.access_token, response.data.refresh_token)
    
    const redirect = route.query.redirect || '/overview'
    router.push(redirect)
  } catch (err) {
    error.value = err.response?.data?.message || 'Login failed'
  } finally {
    loading.value = false
  }
}
</script>
```

### Placeholder Components
```vue
<!-- views/Orchestrator.vue -->
<template>
  <div class="container-fluid p-4">
    <div class="card">
      <div class="card-body text-center">
        <i class="fas fa-robot fa-3x text-muted mb-3"></i>
        <h5>AI Orchestrator</h5>
        <p class="text-muted">Coming soon in Phase 2</p>
      </div>
    </div>
  </div>
</template>

<!-- views/Documents.vue -->
<template>
  <div class="container-fluid p-4">
    <div class="card">
      <div class="card-body text-center">
        <i class="fas fa-file-alt fa-3x text-muted mb-3"></i>
        <h5>Document Processor</h5>
        <p class="text-muted">Coming soon in Phase 2</p>
      </div>
    </div>
  </div>
</template>

<!-- views/Admin.vue -->
<template>
  <div class="container-fluid p-4">
    <div class="card">
      <div class="card-body text-center">
        <i class="fas fa-cog fa-3x text-muted mb-3"></i>
        <h5>Administration</h5>
        <p class="text-muted">Admin panel - BCM Managers only</p>
      </div>
    </div>
  </div>
</template>
```

## Acceptance Criteria

### ✅ Навигация и Роутинг
- [ ] Навбар отображает 5 разделов согласно IA
- [ ] Роутинг работает для всех разделов
- [ ] Admin видим только для bcm_manager роли
- [ ] Активный раздел подсвечивается

### ✅ JWT и Аутентификация
- [ ] JWT токен парсится корректно
- [ ] tenant_id и role сохраняются в store
- [ ] Route guards блокируют неавторизованный доступ
- [ ] Admin доступен только менеджерам
- [ ] Token refresh работает автоматически

### ✅ Overview - KPI и PDCA
- [ ] Запрос к /bcm/kpi выполняется успешно
- [ ] 6 метрик отображаются корректно
- [ ] Chart.js графики рендерятся
- [ ] PDCA фаза подсвечивается на основе KPI
- [ ] Health Score рассчитывается правильно

### ✅ Events - EventMonitor
- [ ] SSE/WebSocket подключение устанавливается
- [ ] События отображаются в реальном времени
- [ ] Фильтры работают (event_type, date_range)
- [ ] JSON payload можно просмотреть
- [ ] Экспорт в CSV/JSON работает

### ✅ Сервисы
- [ ] eventbus.js: history(), publish(), connect методы работают
- [ ] kpi.js: getCurrentKPIs() возвращает данные
- [ ] auth.js: токен управление и refresh работают
- [ ] Все сервисы используют tenant_id из JWT

### ✅ UI/UX
- [ ] Bootstrap 5 стили применены корректно
- [ ] FontAwesome иконки отображаются
- [ ] Интерфейс адаптивный (responsive)
- [ ] Нет legacy страниц в меню
- [ ] Чистый, минималистичный дизайн

## Структура Проекта

```
frontend/web_portal/
├── src/
│   ├── components/
│   │   └── NavBar.vue
│   ├── views/
│   │   ├── Overview.vue
│   │   ├── Events.vue
│   │   ├── Orchestrator.vue
│   │   ├── Documents.vue
│   │   ├── Admin.vue
│   │   ├── Login.vue
│   │   └── NotFound.vue
│   ├── services/
│   │   ├── auth.js
│   │   ├── eventbus.js
│   │   └── kpi.js
│   ├── stores/
│   │   └── auth.js
│   ├── router/
│   │   ├── index.js
│   │   └── guards.js
│   ├── App.vue
│   └── main.js
├── package.json
└── vite.config.js
```

## Команды для Запуска

```bash
# Установка зависимостей
npm install

# Запуск dev сервера
npm run dev

# Сборка для продакшена
npm run build

# Превью production сборки
npm run preview
```

## Зависимости (package.json)

```json
{
  "name": "bcm-platform-ui",
  "version": "1.0.0",
  "dependencies": {
    "vue": "^3.4.0",
    "vue-router": "^4.2.0",
    "pinia": "^2.1.0",
    "axios": "^1.6.0",
    "bootstrap": "^5.3.0",
    "@fortawesome/fontawesome-free": "^6.5.0",
    "chart.js": "^4.4.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.0",
    "vite": "^5.0.0"
  }
}
```

---

**Результат**: Стабильный каркас фронтенда без прикладной логики, готовый для наращивания функциональности в следующих фазах.
