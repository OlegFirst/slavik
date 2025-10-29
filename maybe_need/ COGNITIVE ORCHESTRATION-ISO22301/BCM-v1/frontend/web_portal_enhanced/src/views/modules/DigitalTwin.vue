<template>
  <div class="digital-twin-container">
    <!-- Header -->
    <div class="dt-header">
      <h1 class="dt-title">
        <i class="fas fa-cube"></i>
        Digital Twin Control Center
      </h1>
      <p class="dt-subtitle">4-Block Architecture: Data → Intelligence → Simulation → Decision</p>
    </div>

    <!-- 3D Visualization -->
    <div class="dt-3d-section">
      <DigitalTwin3D :data="digitalTwinData" />
    </div>

    <!-- Status Bar -->
    <div class="dt-status-bar">
      <div class="status-item" :class="{ active: dataCollectionActive }">
        <i class="fas fa-database"></i>
        <span>Data Collection</span>
        <span class="status-indicator"></span>
      </div>
      <div class="status-item" :class="{ active: intelligenceActive }">
        <i class="fas fa-brain"></i>
        <span>AI Processing</span>
        <span class="status-indicator"></span>
      </div>
      <div class="status-item" :class="{ active: simulationActive }">
        <i class="fas fa-project-diagram"></i>
        <span>Simulation Engine</span>
        <span class="status-indicator"></span>
      </div>
      <div class="status-item" :class="{ active: decisionActive }">
        <i class="fas fa-chart-line"></i>
        <span>Decision Support</span>
        <span class="status-indicator"></span>
      </div>
    </div>

    <!-- Main Content Area -->
    <div class="dt-content">
      <!-- Block 1: Data Collection & Event Bus -->
      <div class="dt-block" :class="{ expanded: activeBlock === 1 }">
        <div class="block-header" @click="toggleBlock(1)">
          <h2>
            <i class="fas fa-stream"></i>
            Block 1: Real-Time Data Collection
          </h2>
          <i class="fas fa-chevron-down toggle-icon"></i>
        </div>
        <div class="block-content" v-show="activeBlock === 1">
          <div class="metrics-grid">
            <div class="metric-card">
              <h3>Event Bus Status</h3>
              <div class="metric-value">{{ eventBusMetrics.messagesPerSec }} msg/s</div>
              <div class="metric-chart">
                <canvas ref="eventBusChart"></canvas>
              </div>
            </div>
            <div class="metric-card">
              <h3>Data Sources</h3>
              <ul class="data-sources-list">
                <li v-for="source in dataSources" :key="source.id" :class="source.status">
                  <i :class="source.icon"></i>
                  {{ source.name }}
                  <span class="source-count">{{ source.eventCount }}</span>
                </li>
              </ul>
            </div>
            <div class="metric-card">
              <h3>Recent Events</h3>
              <div class="event-stream">
                <div v-for="event in recentEvents" :key="event.id" class="event-item">
                  <span class="event-time">{{ formatTime(event.timestamp) }}</span>
                  <span class="event-type">{{ event.type }}</span>
                  <span class="event-data">{{ event.summary }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Block 2: Intelligent Assembly -->
      <div class="dt-block" :class="{ expanded: activeBlock === 2 }">
        <div class="block-header" @click="toggleBlock(2)">
          <h2>
            <i class="fas fa-network-wired"></i>
            Block 2: Intelligent Assembly & Organization Profile
          </h2>
          <i class="fas fa-chevron-down toggle-icon"></i>
        </div>
        <div class="block-content" v-show="activeBlock === 2">
          <div class="org-profile">
            <div class="profile-visualization">
              <canvas ref="orgGraph"></canvas>
            </div>
            <div class="profile-details">
              <h3>Organization Digital Profile</h3>
              <div class="profile-stats">
                <div class="stat-item">
                  <label>Departments</label>
                  <span>{{ orgProfile.departments }}</span>
                </div>
                <div class="stat-item">
                  <label>Processes</label>
                  <span>{{ orgProfile.processes }}</span>
                </div>
                <div class="stat-item">
                  <label>Risk Points</label>
                  <span>{{ orgProfile.riskPoints }}</span>
                </div>
                <div class="stat-item">
                  <label>Resilience Score</label>
                  <span>{{ orgProfile.resilienceScore }}%</span>
                </div>
              </div>
              <div class="ai-insights">
                <h4>AI Insights</h4>
                <div v-for="insight in aiInsights" :key="insight.id" class="insight-item">
                  <i class="fas fa-lightbulb"></i>
                  {{ insight.message }}
                  <span class="insight-confidence">{{ insight.confidence }}%</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Block 3: Simulation (JaamSim Integration) -->
      <div class="dt-block" :class="{ expanded: activeBlock === 3 }">
        <div class="block-header" @click="toggleBlock(3)">
          <h2>
            <i class="fas fa-cogs"></i>
            Block 3: JaamSim Simulation Engine
          </h2>
          <i class="fas fa-chevron-down toggle-icon"></i>
        </div>
        <div class="block-content" v-show="activeBlock === 3">
          <div class="simulation-control">
            <div class="sim-toolbar">
              <button @click="startSimulation" :disabled="simulationRunning" class="btn btn-primary">
                <i class="fas fa-play"></i> Start
              </button>
              <button @click="pauseSimulation" :disabled="!simulationRunning" class="btn btn-warning">
                <i class="fas fa-pause"></i> Pause
              </button>
              <button @click="stopSimulation" :disabled="!simulationRunning" class="btn btn-danger">
                <i class="fas fa-stop"></i> Stop
              </button>
              <select v-model="selectedScenario" class="scenario-select">
                <option v-for="scenario in scenarios" :key="scenario.id" :value="scenario.id">
                  {{ scenario.name }}
                </option>
              </select>
            </div>
            <div class="sim-visualization">
              <div v-if="vncEnabled" class="vnc-container">
                <iframe :src="vncUrl" frameborder="0"></iframe>
              </div>
              <div v-else class="sim-metrics">
                <div class="metric-display">
                  <h4>Simulation Metrics</h4>
                  <div class="metric-row">
                    <span>Processed Events:</span>
                    <span>{{ simMetrics.processedEvents }}</span>
                  </div>
                  <div class="metric-row">
                    <span>Active Entities:</span>
                    <span>{{ simMetrics.activeEntities }}</span>
                  </div>
                  <div class="metric-row">
                    <span>Queue Length:</span>
                    <span>{{ simMetrics.queueLength }}</span>
                  </div>
                  <div class="metric-row">
                    <span>Utilization:</span>
                    <span>{{ simMetrics.utilization }}%</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Block 4: Decision Support -->
      <div class="dt-block" :class="{ expanded: activeBlock === 4 }">
        <div class="block-header" @click="toggleBlock(4)">
          <h2>
            <i class="fas fa-chess-king"></i>
            Block 4: Decision Making & Implementation
          </h2>
          <i class="fas fa-chevron-down toggle-icon"></i>
        </div>
        <div class="block-content" v-show="activeBlock === 4">
          <div class="decision-dashboard">
            <div class="recommendations">
              <h3>AI Recommendations</h3>
              <div v-for="rec in recommendations" :key="rec.id" class="rec-card" :class="rec.priority">
                <div class="rec-header">
                  <span class="rec-priority">{{ rec.priority }}</span>
                  <span class="rec-confidence">{{ rec.confidence }}% confidence</span>
                </div>
                <h4>{{ rec.title }}</h4>
                <p>{{ rec.description }}</p>
                <div class="rec-actions">
                  <button @click="implementRecommendation(rec)" class="btn btn-sm btn-primary">
                    Implement
                  </button>
                  <button @click="analyzeRecommendation(rec)" class="btn btn-sm btn-secondary">
                    Analyze
                  </button>
                </div>
              </div>
            </div>
            <div class="implementation-log">
              <h3>Implementation History</h3>
              <div class="log-entries">
                <div v-for="entry in implementationLog" :key="entry.id" class="log-entry">
                  <span class="log-time">{{ formatTime(entry.timestamp) }}</span>
                  <span class="log-action">{{ entry.action }}</span>
                  <span class="log-result" :class="entry.result">{{ entry.result }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, computed } from 'vue'
import { simulationService } from '@/services/simulationService'
import { bcmService } from '@/services/bcm'
import { analyticsService } from '@/services/analyticsService'
import DigitalTwin3D from '@/components/digital-twin/DigitalTwin3D.vue'
import Chart from 'chart.js/auto'

// Reactive state
const activeBlock = ref(1)
const simulationRunning = ref(false)
const selectedScenario = ref('')
const vncEnabled = ref(false)
const vncUrl = ref('')

// Block status indicators
const dataCollectionActive = ref(true)
const intelligenceActive = ref(true)
const simulationActive = ref(false)
const decisionActive = ref(true)

// Data structures
const eventBusMetrics = reactive({
  messagesPerSec: 0,
  totalMessages: 0,
  queueDepth: 0
})

const dataSources = ref([
  { id: 1, name: 'BCM Core', icon: 'fas fa-database', status: 'active', eventCount: 0 },
  { id: 2, name: 'Risk Engine', icon: 'fas fa-exclamation-triangle', status: 'active', eventCount: 0 },
  { id: 3, name: 'Incident Manager', icon: 'fas fa-bell', status: 'active', eventCount: 0 },
  { id: 4, name: 'Training System', icon: 'fas fa-graduation-cap', status: 'idle', eventCount: 0 }
])

const recentEvents = ref([])
const orgProfile = reactive({
  departments: 12,
  processes: 47,
  riskPoints: 23,
  resilienceScore: 78
})

const aiInsights = ref([])
const simMetrics = reactive({
  processedEvents: 0,
  activeEntities: 0,
  queueLength: 0,
  utilization: 0
})

const scenarios = ref([
  { id: 'scenario-1', name: 'Critical System Failure' },
  { id: 'scenario-2', name: 'Pandemic Response' },
  { id: 'scenario-3', name: 'Supply Chain Disruption' },
  { id: 'scenario-4', name: 'Cyber Attack Response' }
])

const recommendations = ref([])
const implementationLog = ref([])
const digitalTwinData = reactive({
  nodes: [],
  connections: [],
  status: 'active'
})

// Websocket connection
let wsConnection: WebSocket | null = null
let updateInterval: NodeJS.Timeout | null = null

// Methods
const toggleBlock = (block: number) => {
  activeBlock.value = activeBlock.value === block ? 0 : block
}

const startSimulation = async () => {
  if (!selectedScenario.value) {
    alert('Please select a scenario')
    return
  }

  try {
    const result = await simulationService.startSimulation(selectedScenario.value)
    simulationRunning.value = true
    simulationActive.value = true

    if (result.vnc_url) {
      vncEnabled.value = true
      vncUrl.value = result.vnc_url
    }

    // Start metrics polling
    startMetricsPolling()
  } catch (error) {
    console.error('Failed to start simulation:', error)
    alert('Failed to start simulation')
  }
}

const pauseSimulation = async () => {
  try {
    await simulationService.pauseSimulation(selectedScenario.value)
    simulationRunning.value = false
  } catch (error) {
    console.error('Failed to pause simulation:', error)
  }
}

const stopSimulation = async () => {
  try {
    await simulationService.stopSimulation(selectedScenario.value)
    simulationRunning.value = false
    simulationActive.value = false
    vncEnabled.value = false
    stopMetricsPolling()
  } catch (error) {
    console.error('Failed to stop simulation:', error)
  }
}

const startMetricsPolling = () => {
  updateInterval = setInterval(async () => {
    if (simulationRunning.value && selectedScenario.value) {
      const metrics = await simulationService.getJaamSimMetrics(selectedScenario.value)
      Object.assign(simMetrics, metrics)
    }
  }, 2000)
}

const stopMetricsPolling = () => {
  if (updateInterval) {
    clearInterval(updateInterval)
    updateInterval = null
  }
}

const implementRecommendation = async (rec: any) => {
  implementationLog.value.unshift({
    id: Date.now(),
    timestamp: new Date().toISOString(),
    action: `Implemented: ${rec.title}`,
    result: 'success'
  })
}

const analyzeRecommendation = async (rec: any) => {
  // Open detailed analysis
  console.log('Analyzing recommendation:', rec)
}

const formatTime = (timestamp: string) => {
  return new Date(timestamp).toLocaleTimeString()
}

const connectWebSocket = () => {
  wsConnection = simulationService.createWebSocketConnection('digital-twin', (data) => {
    if (data.type === 'metrics_update') {
      eventBusMetrics.messagesPerSec = data.metrics?.messagesPerSec || 0
    }
    if (data.type === 'event') {
      recentEvents.value.unshift({
        id: Date.now(),
        timestamp: new Date().toISOString(),
        type: data.eventType,
        summary: data.summary
      })
      if (recentEvents.value.length > 10) {
        recentEvents.value.pop()
      }
    }
  })
}

const loadInitialData = async () => {
  try {
    // Load dashboard metrics
    const metrics = await bcmService.getDashboardMetrics()
    orgProfile.riskPoints = metrics.totalRisks
    orgProfile.resilienceScore = metrics.complianceScore

    // Load AI insights
    const insights = await analyticsService.getAIRecommendations()
    aiInsights.value = insights.slice(0, 3).map(r => ({
      id: r.id,
      message: r.title,
      confidence: r.confidence
    }))

    // Load recommendations
    recommendations.value = insights.map(r => ({
      ...r,
      priority: r.priority.toLowerCase()
    }))

  } catch (error) {
    console.error('Failed to load initial data:', error)
  }
}

// Lifecycle
onMounted(() => {
  loadInitialData()
  connectWebSocket()
})

onUnmounted(() => {
  stopMetricsPolling()
  if (wsConnection) {
    wsConnection.close()
  }
})
</script>

<style scoped lang="scss">
.digital-twin-container {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.dt-header {
  margin-bottom: 30px;
  text-align: center;

  .dt-title {
    font-size: 2rem;
    font-weight: 600;
    color: #1a1a1a;
    margin-bottom: 10px;

    i {
      color: #3b82f6;
      margin-right: 10px;
    }
  }

  .dt-subtitle {
    color: #666;
    font-size: 1.1rem;
  }
}

.dt-3d-section {
  margin-bottom: 30px;
}

.dt-status-bar {
  display: flex;
  gap: 20px;
  margin-bottom: 30px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 10px;

  .status-item {
    flex: 1;
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 10px;
    background: white;
    border-radius: 8px;
    border: 2px solid #e0e0e0;
    transition: all 0.3s;

    &.active {
      border-color: #10b981;
      background: #f0fdf4;

      .status-indicator {
        background: #10b981;
        animation: pulse 2s infinite;
      }
    }

    i {
      font-size: 1.2rem;
      color: #666;
    }

    span {
      font-size: 0.9rem;
      font-weight: 500;
    }

    .status-indicator {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: #ccc;
      margin-left: auto;
    }
  }
}

.dt-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.dt-block {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  overflow: hidden;
  transition: all 0.3s;

  &.expanded {
    box-shadow: 0 4px 20px rgba(0,0,0,0.15);

    .toggle-icon {
      transform: rotate(180deg);
    }
  }

  .block-header {
    padding: 20px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    cursor: pointer;
    display: flex;
    justify-content: space-between;
    align-items: center;

    h2 {
      margin: 0;
      font-size: 1.3rem;
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .toggle-icon {
      transition: transform 0.3s;
    }
  }

  .block-content {
    padding: 20px;
  }
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;

  .metric-card {
    padding: 15px;
    background: #f8f9fa;
    border-radius: 8px;

    h3 {
      margin: 0 0 15px 0;
      font-size: 1rem;
      color: #666;
    }

    .metric-value {
      font-size: 2rem;
      font-weight: 600;
      color: #3b82f6;
    }
  }
}

.data-sources-list {
  list-style: none;
  padding: 0;
  margin: 0;

  li {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 0;
    border-bottom: 1px solid #e0e0e0;

    &:last-child {
      border-bottom: none;
    }

    &.active {
      color: #10b981;
    }

    .source-count {
      margin-left: auto;
      background: #3b82f6;
      color: white;
      padding: 2px 8px;
      border-radius: 12px;
      font-size: 0.8rem;
    }
  }
}

.event-stream {
  max-height: 200px;
  overflow-y: auto;

  .event-item {
    display: grid;
    grid-template-columns: auto 100px 1fr;
    gap: 10px;
    padding: 8px 0;
    border-bottom: 1px solid #e0e0e0;
    font-size: 0.85rem;

    .event-time {
      color: #666;
    }

    .event-type {
      color: #3b82f6;
      font-weight: 500;
    }

    .event-data {
      color: #333;
    }
  }
}

.simulation-control {
  .sim-toolbar {
    display: flex;
    gap: 10px;
    margin-bottom: 20px;
    align-items: center;

    .scenario-select {
      margin-left: auto;
      padding: 8px 12px;
      border: 1px solid #ddd;
      border-radius: 6px;
    }
  }

  .vnc-container {
    width: 100%;
    height: 500px;
    border: 1px solid #ddd;
    border-radius: 8px;
    overflow: hidden;

    iframe {
      width: 100%;
      height: 100%;
    }
  }

  .sim-metrics {
    .metric-display {
      padding: 20px;
      background: #f8f9fa;
      border-radius: 8px;

      h4 {
        margin: 0 0 15px 0;
      }

      .metric-row {
        display: flex;
        justify-content: space-between;
        padding: 8px 0;
        border-bottom: 1px solid #e0e0e0;

        &:last-child {
          border-bottom: none;
        }

        span:last-child {
          font-weight: 600;
          color: #3b82f6;
        }
      }
    }
  }
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s;
  display: inline-flex;
  align-items: center;
  gap: 5px;

  &.btn-primary {
    background: #3b82f6;
    color: white;

    &:hover:not(:disabled) {
      background: #2563eb;
    }
  }

  &.btn-warning {
    background: #f59e0b;
    color: white;

    &:hover:not(:disabled) {
      background: #d97706;
    }
  }

  &.btn-danger {
    background: #ef4444;
    color: white;

    &:hover:not(:disabled) {
      background: #dc2626;
    }
  }

  &.btn-secondary {
    background: #6b7280;
    color: white;

    &:hover:not(:disabled) {
      background: #4b5563;
    }
  }

  &.btn-sm {
    padding: 5px 10px;
    font-size: 0.85rem;
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}

.recommendations {
  margin-bottom: 30px;

  .rec-card {
    padding: 15px;
    margin-bottom: 15px;
    border-radius: 8px;
    border-left: 4px solid;

    &.high {
      border-color: #ef4444;
      background: #fef2f2;
    }

    &.medium {
      border-color: #f59e0b;
      background: #fffbeb;
    }

    &.low {
      border-color: #10b981;
      background: #f0fdf4;
    }

    .rec-header {
      display: flex;
      justify-content: space-between;
      margin-bottom: 10px;
      font-size: 0.85rem;

      .rec-priority {
        text-transform: uppercase;
        font-weight: 600;
      }

      .rec-confidence {
        color: #666;
      }
    }

    h4 {
      margin: 0 0 8px 0;
    }

    p {
      margin: 0 0 10px 0;
      color: #666;
    }

    .rec-actions {
      display: flex;
      gap: 10px;
    }
  }
}

.log-entries {
  max-height: 300px;
  overflow-y: auto;

  .log-entry {
    display: grid;
    grid-template-columns: auto 1fr auto;
    gap: 15px;
    padding: 10px 0;
    border-bottom: 1px solid #e0e0e0;

    .log-time {
      color: #666;
      font-size: 0.85rem;
    }

    .log-action {
      color: #333;
    }

    .log-result {
      font-weight: 500;

      &.success {
        color: #10b981;
      }

      &.warning {
        color: #f59e0b;
      }

      &.error {
        color: #ef4444;
      }
    }
  }
}
</style>