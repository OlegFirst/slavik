<template>
  <div class="exercise-simulation">
    <!-- Page Header -->
    <div class="page-header mb-6">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-4">
          <button
            @click="$router.go(-1)"
            class="btn btn-outline flex items-center space-x-2"
          >
            <ArrowLeftIcon class="w-4 h-4" />
            <span>Back</span>
          </button>

          <div>
            <h1 class="text-2xl font-bold text-gray-900">{{ exerciseData?.name || 'Loading...' }}</h1>
            <p class="text-gray-600">{{ exerciseData?.description }}</p>
          </div>
        </div>

        <div class="header-actions flex items-center space-x-2">
          <button
            @click="toggleFullscreen"
            class="btn btn-outline flex items-center space-x-2"
          >
            <ArrowsPointingOutIcon class="w-4 h-4" />
            <span>Fullscreen</span>
          </button>

          <button
            @click="openSettings"
            class="btn btn-outline flex items-center space-x-2"
          >
            <Cog6ToothIcon class="w-4 h-4" />
            <span>Settings</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Navigation Tabs -->
    <div class="simulation-tabs mb-6">
      <div class="border-b border-gray-200">
        <nav class="flex space-x-8">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            @click="activeTab = tab.id"
            :class="[
              'py-2 px-1 border-b-2 font-medium text-sm transition-colors',
              activeTab === tab.id
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            <component :is="tab.icon" class="w-4 h-4 inline mr-2" />
            {{ tab.label }}
          </button>
        </nav>
      </div>
    </div>

    <!-- Tab Content -->
    <div class="tab-content">
      <!-- Control Panel Tab -->
      <div v-if="activeTab === 'control'" class="control-panel-tab">
        <SimulationControlPanel :exercise-id="exerciseId" />
      </div>

      <!-- Monitor Tab -->
      <div v-if="activeTab === 'monitor'" class="monitor-tab">
        <ExerciseMonitor :exercise-id="exerciseId" />
      </div>

      <!-- VNC Viewer Tab -->
      <div v-if="activeTab === 'vnc'" class="vnc-viewer-tab">
        <div class="vnc-container bg-white rounded-lg shadow-sm p-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-semibold">JaamSim VNC Viewer</h3>

            <div class="vnc-controls flex items-center space-x-2">
              <span class="text-sm text-gray-500">{{ vncConnectionStatus }}</span>

              <div
                class="status-indicator w-3 h-3 rounded-full"
                :class="{
                  'bg-green-500': vncConnectionStatus === 'Connected',
                  'bg-yellow-500': vncConnectionStatus === 'Connecting',
                  'bg-red-500': vncConnectionStatus === 'Disconnected'
                }"
              ></div>

              <button
                @click="openExternalVNC"
                class="btn btn-outline btn-sm flex items-center space-x-1"
              >
                <ArrowTopRightOnSquareIcon class="w-3 h-3" />
                <span>External</span>
              </button>

              <button
                @click="reconnectVNC"
                class="btn btn-outline btn-sm flex items-center space-x-1"
              >
                <ArrowPathIcon class="w-3 h-3" />
                <span>Reconnect</span>
              </button>
            </div>
          </div>

          <div class="vnc-display bg-gray-900 rounded border relative" style="height: 600px;">
            <iframe
              ref="vncFrame"
              :src="vncUrl"
              width="100%"
              height="100%"
              frameborder="0"
              class="rounded"
              @load="onVNCLoad"
            ></iframe>

            <div
              v-if="vncConnectionStatus !== 'Connected'"
              class="absolute inset-0 bg-gray-800 bg-opacity-75 flex items-center justify-center rounded"
            >
              <div class="text-center text-white">
                <ComputerDesktopIcon class="w-16 h-16 mx-auto mb-4 opacity-50" />
                <p class="text-lg font-medium">{{ vncConnectionStatus }}</p>
                <p class="text-sm opacity-75 mt-2">
                  {{ vncConnectionStatus === 'Connecting' ? 'Establishing connection...' : 'VNC connection unavailable' }}
                </p>
                <button
                  v-if="vncConnectionStatus === 'Disconnected'"
                  @click="reconnectVNC"
                  class="btn btn-primary mt-4"
                >
                  Retry Connection
                </button>
              </div>
            </div>
          </div>

          <div class="vnc-info mt-4 flex items-center justify-between text-sm text-gray-600">
            <div>
              <span>VNC Server: localhost:5900</span>
              <span class="ml-4">Resolution: 1280x720</span>
            </div>
            <div class="flex items-center space-x-4">
              <span>Simulation Time: {{ simulationTime }}</span>
              <span>FPS: {{ vncFps }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Participants Tab -->
      <div v-if="activeTab === 'participants'" class="participants-tab">
        <div class="participants-overview bg-white rounded-lg shadow-sm p-6">
          <div class="flex items-center justify-between mb-6">
            <h3 class="text-lg font-semibold">Exercise Participants</h3>

            <div class="participant-stats flex items-center space-x-4">
              <div class="stat-item text-center">
                <div class="text-2xl font-bold text-blue-600">{{ participants.length }}</div>
                <div class="text-sm text-gray-500">Total</div>
              </div>
              <div class="stat-item text-center">
                <div class="text-2xl font-bold text-green-600">{{ activeParticipants }}</div>
                <div class="text-sm text-gray-500">Active</div>
              </div>
              <div class="stat-item text-center">
                <div class="text-2xl font-bold text-yellow-600">{{ idleParticipants }}</div>
                <div class="text-sm text-gray-500">Idle</div>
              </div>
            </div>
          </div>

          <div class="participants-grid grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div
              v-for="participant in participants"
              :key="participant.id"
              class="participant-card p-4 border rounded-lg"
              :class="{
                'border-green-200 bg-green-50': participant.status === 'active',
                'border-yellow-200 bg-yellow-50': participant.status === 'idle',
                'border-red-200 bg-red-50': participant.status === 'disconnected'
              }"
            >
              <div class="flex items-center justify-between mb-2">
                <div class="participant-info">
                  <h4 class="font-medium text-gray-900">{{ participant.name }}</h4>
                  <p class="text-sm text-gray-600">{{ participant.role }}</p>
                </div>
                <div
                  class="status-dot w-3 h-3 rounded-full"
                  :class="{
                    'bg-green-500': participant.status === 'active',
                    'bg-yellow-500': participant.status === 'idle',
                    'bg-red-500': participant.status === 'disconnected'
                  }"
                ></div>
              </div>

              <div v-if="participant.current_action" class="current-action mb-3">
                <div class="text-xs text-gray-500 mb-1">Current Action:</div>
                <div class="text-sm text-gray-800">{{ participant.current_action }}</div>
              </div>

              <div class="participant-metrics grid grid-cols-2 gap-2 text-xs">
                <div class="metric">
                  <span class="text-gray-500">Actions:</span>
                  <span class="font-medium">{{ participant.actions_completed || 0 }}</span>
                </div>
                <div class="metric">
                  <span class="text-gray-500">Score:</span>
                  <span class="font-medium">{{ participant.score || 0 }}</span>
                </div>
                <div class="metric">
                  <span class="text-gray-500">Response:</span>
                  <span class="font-medium">{{ participant.avg_response_time || 0 }}ms</span>
                </div>
                <div class="metric">
                  <span class="text-gray-500">Online:</span>
                  <span class="font-medium">{{ formatDuration(participant.session_duration || 0) }}</span>
                </div>
              </div>

              <div class="participant-actions mt-3 flex space-x-2">
                <button
                  @click="messageParticipant(participant.id)"
                  class="btn btn-outline btn-xs flex-1"
                >
                  Message
                </button>
                <button
                  @click="viewParticipantDetails(participant.id)"
                  class="btn btn-outline btn-xs"
                  title="View Details"
                >
                  <EyeIcon class="w-3 h-3" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Analytics Tab -->
      <div v-if="activeTab === 'analytics'" class="analytics-tab">
        <div class="analytics-dashboard space-y-6">
          <!-- Real-time Charts -->
          <div class="charts-section bg-white rounded-lg shadow-sm p-6">
            <h3 class="text-lg font-semibold mb-4">Real-time Performance Analytics</h3>

            <div class="charts-grid grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div class="chart-container">
                <h4 class="font-medium text-gray-900 mb-2">System Metrics</h4>
                <MetricsChart :data="metricsData" :height="250" />
              </div>

              <div class="chart-container">
                <h4 class="font-medium text-gray-900 mb-2">Resource Utilization</h4>
                <UtilizationChart :data="utilizationData" />
              </div>

              <div class="chart-container">
                <h4 class="font-medium text-gray-900 mb-2">Response Times</h4>
                <ResponseTimeChart :data="responseTimeData" />
              </div>

              <div class="chart-container">
                <h4 class="font-medium text-gray-900 mb-2">Participant Activity</h4>
                <div class="activity-heatmap bg-gray-50 rounded p-4" style="height: 250px;">
                  <!-- Activity heatmap would go here -->
                  <div class="flex items-center justify-center h-full text-gray-500">
                    <div class="text-center">
                      <ChartBarIcon class="w-12 h-12 mx-auto mb-2 opacity-50" />
                      <p>Activity heatmap coming soon</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- KPI Summary -->
          <div class="kpi-summary bg-white rounded-lg shadow-sm p-6">
            <h3 class="text-lg font-semibold mb-4">Key Performance Indicators</h3>

            <div class="kpi-grid grid grid-cols-2 md:grid-cols-4 gap-4">
              <div class="kpi-card bg-blue-50 p-4 rounded-lg text-center">
                <div class="kpi-value text-2xl font-bold text-blue-600">
                  {{ kpis.exerciseCompletion }}%
                </div>
                <div class="kpi-label text-sm text-gray-600">Exercise Completion</div>
              </div>

              <div class="kpi-card bg-green-50 p-4 rounded-lg text-center">
                <div class="kpi-value text-2xl font-bold text-green-600">
                  {{ kpis.participantEngagement }}%
                </div>
                <div class="kpi-label text-sm text-gray-600">Participant Engagement</div>
              </div>

              <div class="kpi-card bg-yellow-50 p-4 rounded-lg text-center">
                <div class="kpi-value text-2xl font-bold text-yellow-600">
                  {{ kpis.systemEfficiency }}%
                </div>
                <div class="kpi-label text-sm text-gray-600">System Efficiency</div>
              </div>

              <div class="kpi-card bg-purple-50 p-4 rounded-lg text-center">
                <div class="kpi-value text-2xl font-bold text-purple-600">
                  {{ kpis.learningObjectives }}%
                </div>
                <div class="kpi-label text-sm text-gray-600">Learning Objectives</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Settings Tab -->
      <div v-if="activeTab === 'settings'" class="settings-tab">
        <div class="settings-panel bg-white rounded-lg shadow-sm p-6">
          <h3 class="text-lg font-semibold mb-6">Simulation Settings</h3>

          <div class="settings-sections space-y-6">
            <!-- Display Settings -->
            <div class="setting-section">
              <h4 class="font-medium text-gray-900 mb-3">Display Settings</h4>
              <div class="space-y-3">
                <div class="setting-item flex items-center justify-between">
                  <label class="text-sm text-gray-700">Auto-refresh interval</label>
                  <select v-model="settings.refreshInterval" class="select">
                    <option value="1000">1 second</option>
                    <option value="5000">5 seconds</option>
                    <option value="10000">10 seconds</option>
                    <option value="30000">30 seconds</option>
                  </select>
                </div>

                <div class="setting-item flex items-center justify-between">
                  <label class="text-sm text-gray-700">Show real-time notifications</label>
                  <input
                    v-model="settings.showNotifications"
                    type="checkbox"
                    class="checkbox"
                  />
                </div>

                <div class="setting-item flex items-center justify-between">
                  <label class="text-sm text-gray-700">VNC quality</label>
                  <select v-model="settings.vncQuality" class="select">
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                  </select>
                </div>
              </div>
            </div>

            <!-- Monitoring Settings -->
            <div class="setting-section">
              <h4 class="font-medium text-gray-900 mb-3">Monitoring Settings</h4>
              <div class="space-y-3">
                <div class="setting-item flex items-center justify-between">
                  <label class="text-sm text-gray-700">Log level</label>
                  <select v-model="settings.logLevel" class="select">
                    <option value="debug">Debug</option>
                    <option value="info">Info</option>
                    <option value="warn">Warning</option>
                    <option value="error">Error</option>
                  </select>
                </div>

                <div class="setting-item flex items-center justify-between">
                  <label class="text-sm text-gray-700">Track participant actions</label>
                  <input
                    v-model="settings.trackActions"
                    type="checkbox"
                    class="checkbox"
                  />
                </div>

                <div class="setting-item flex items-center justify-between">
                  <label class="text-sm text-gray-700">Record session</label>
                  <input
                    v-model="settings.recordSession"
                    type="checkbox"
                    class="checkbox"
                  />
                </div>
              </div>
            </div>

            <!-- Actions -->
            <div class="settings-actions flex space-x-3">
              <button @click="saveSettings" class="btn btn-primary">
                Save Settings
              </button>
              <button @click="resetSettings" class="btn btn-outline">
                Reset to Default
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import {
  ArrowLeftIcon,
  ArrowsPointingOutIcon,
  Cog6ToothIcon,
  PlayIcon,
  EyeIcon,
  ComputerDesktopIcon,
  UsersIcon,
  ChartBarIcon,
  ArrowTopRightOnSquareIcon,
  ArrowPathIcon
} from '@heroicons/vue/24/outline'
import { useToast } from 'vue-toastification'
import { simulationService } from '@/services/simulationService'
import SimulationControlPanel from '@/components/simulation/SimulationControlPanel.vue'
import ExerciseMonitor from '@/components/simulation/ExerciseMonitor.vue'
import MetricsChart from '@/components/simulation/charts/MetricsChart.vue'
import UtilizationChart from '@/components/simulation/charts/UtilizationChart.vue'
import ResponseTimeChart from '@/components/simulation/charts/ResponseTimeChart.vue'

interface Props {
  exerciseId: string
}

const props = defineProps<Props>()
const route = useRoute()
const toast = useToast()

// Reactive state
const activeTab = ref(route.query.tab as string || 'control')
const exerciseData = ref(null)
const participants = ref([])
const vncConnectionStatus = ref('Disconnected')
const vncUrl = ref('http://localhost:5900')
const simulationTime = ref('00:00:00')
const vncFps = ref(0)

const metricsData = ref([])
const utilizationData = ref([])
const responseTimeData = ref([])

const settings = ref({
  refreshInterval: 5000,
  showNotifications: true,
  vncQuality: 'medium',
  logLevel: 'info',
  trackActions: true,
  recordSession: false
})

const kpis = ref({
  exerciseCompletion: 65,
  participantEngagement: 78,
  systemEfficiency: 92,
  learningObjectives: 71
})

// Computed properties
const activeParticipants = computed(() =>
  participants.value.filter(p => p.status === 'active').length
)

const idleParticipants = computed(() =>
  participants.value.filter(p => p.status === 'idle').length
)

const tabs = [
  { id: 'control', label: 'Control Panel', icon: PlayIcon },
  { id: 'monitor', label: 'Monitor', icon: EyeIcon },
  { id: 'vnc', label: 'VNC Viewer', icon: ComputerDesktopIcon },
  { id: 'participants', label: 'Participants', icon: UsersIcon },
  { id: 'analytics', label: 'Analytics', icon: ChartBarIcon },
  { id: 'settings', label: 'Settings', icon: Cog6ToothIcon }
]

let vncCheckInterval: NodeJS.Timeout | null = null
let simulationTimeInterval: NodeJS.Timeout | null = null

// Methods
const loadExerciseData = async () => {
  try {
    const [exercise, participantData] = await Promise.all([
      simulationService.getExerciseDetails(props.exerciseId),
      simulationService.getParticipants(props.exerciseId)
    ])

    exerciseData.value = exercise
    participants.value = participantData
  } catch (error) {
    console.error('Error loading exercise data:', error)
    toast.error('Failed to load exercise data')
  }
}

const checkVNCConnection = async () => {
  try {
    const status = await simulationService.getSimulationStatus(props.exerciseId)
    vncConnectionStatus.value = status.vnc_available ? 'Connected' : 'Disconnected'
  } catch (error) {
    vncConnectionStatus.value = 'Disconnected'
  }
}

const onVNCLoad = () => {
  vncConnectionStatus.value = 'Connected'
  vncFps.value = 30 // Mock FPS
}

const reconnectVNC = async () => {
  vncConnectionStatus.value = 'Connecting'

  try {
    await simulationService.restartVNCConnection(props.exerciseId)
    setTimeout(() => {
      checkVNCConnection()
    }, 2000)
  } catch (error) {
    vncConnectionStatus.value = 'Disconnected'
    toast.error('Failed to reconnect VNC')
  }
}

const openExternalVNC = () => {
  window.open(`vnc://localhost:5900?exercise=${props.exerciseId}`, '_blank')
}

const toggleFullscreen = () => {
  if (document.fullscreenElement) {
    document.exitFullscreen()
  } else {
    document.documentElement.requestFullscreen()
  }
}

const openSettings = () => {
  activeTab.value = 'settings'
}

const messageParticipant = (participantId: string) => {
  // Open messaging modal/interface
  toast.info('Messaging feature coming soon')
}

const viewParticipantDetails = (participantId: string) => {
  // Open participant details modal
  toast.info('Participant details feature coming soon')
}

const saveSettings = () => {
  localStorage.setItem('simulation-settings', JSON.stringify(settings.value))
  toast.success('Settings saved successfully')
}

const resetSettings = () => {
  settings.value = {
    refreshInterval: 5000,
    showNotifications: true,
    vncQuality: 'medium',
    logLevel: 'info',
    trackActions: true,
    recordSession: false
  }
  toast.info('Settings reset to default')
}

const formatDuration = (seconds: number) => {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = seconds % 60

  return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

const updateSimulationTime = () => {
  // Mock simulation time update
  const now = new Date()
  const start = new Date(exerciseData.value?.started_at || now)
  const elapsed = Math.floor((now.getTime() - start.getTime()) / 1000)
  simulationTime.value = formatDuration(elapsed)
}

// Lifecycle
onMounted(async () => {
  await loadExerciseData()

  // Load saved settings
  const savedSettings = localStorage.getItem('simulation-settings')
  if (savedSettings) {
    settings.value = { ...settings.value, ...JSON.parse(savedSettings) }
  }

  // Start VNC connection monitoring
  vncCheckInterval = setInterval(checkVNCConnection, 10000)

  // Start simulation time update
  simulationTimeInterval = setInterval(updateSimulationTime, 1000)

  await checkVNCConnection()
})

onUnmounted(() => {
  if (vncCheckInterval) {
    clearInterval(vncCheckInterval)
  }

  if (simulationTimeInterval) {
    clearInterval(simulationTimeInterval)
  }
})
</script>

<style scoped>
.btn {
  @apply px-4 py-2 rounded-lg font-medium transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed;
}

.btn-primary {
  @apply bg-blue-600 text-white hover:bg-blue-700;
}

.btn-outline {
  @apply border border-gray-300 text-gray-700 hover:bg-gray-50;
}

.btn-sm {
  @apply px-3 py-1.5 text-sm;
}

.btn-xs {
  @apply px-2 py-1 text-xs;
}

.select {
  @apply border border-gray-300 rounded-md px-3 py-1 text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500;
}

.checkbox {
  @apply w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500;
}

.participant-card {
  transition: all 0.2s ease-in-out;
}

.participant-card:hover {
  transform: translateY(-2px);
}

.kpi-card {
  transition: transform 0.2s ease-in-out;
}

.kpi-card:hover {
  transform: translateY(-2px);
}

.vnc-display iframe {
  border-radius: 4px;
}

.status-indicator {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: .5;
  }
}
</style>