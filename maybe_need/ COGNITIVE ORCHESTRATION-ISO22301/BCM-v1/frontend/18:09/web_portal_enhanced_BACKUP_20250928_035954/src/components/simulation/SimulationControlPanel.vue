<template>
  <div class="simulation-control-panel">
    <!-- Simulation Status Header -->
    <div class="simulation-header bg-white rounded-lg shadow-sm p-6 mb-6">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-4">
          <div class="status-indicator" :class="simulationStatusClass">
            <component :is="statusIcon" class="w-8 h-8" />
            <span class="ml-2 text-lg font-semibold">{{ simulationStatusText }}</span>
          </div>

          <div class="exercise-info text-gray-600">
            <span class="text-sm">Exercise: </span>
            <span class="font-medium">{{ exerciseData?.name || 'Loading...' }}</span>
          </div>
        </div>

        <div class="simulation-controls flex space-x-2">
          <button
            @click="startSimulation"
            :disabled="simulationStatus === 'running'"
            class="btn btn-success flex items-center space-x-2"
          >
            <PlayIcon class="w-4 h-4" />
            <span>Start</span>
          </button>

          <button
            @click="pauseSimulation"
            :disabled="simulationStatus !== 'running'"
            class="btn btn-warning flex items-center space-x-2"
          >
            <PauseIcon class="w-4 h-4" />
            <span>Pause</span>
          </button>

          <button
            @click="stopSimulation"
            :disabled="simulationStatus === 'stopped'"
            class="btn btn-danger flex items-center space-x-2"
          >
            <StopIcon class="w-4 h-4" />
            <span>Stop</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Main Simulation Display -->
    <div class="simulation-display">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">

        <!-- Left Column: JaamSim Display & Metrics -->
        <div class="lg:col-span-2 space-y-6">

          <!-- JaamSim VNC Viewer -->
          <div class="jaamsim-viewer bg-white rounded-lg shadow-sm p-6">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-lg font-semibold flex items-center">
                <ComputerDesktopIcon class="w-5 h-5 mr-2 text-blue-500" />
                JaamSim Simulation View
              </h3>

              <div class="flex items-center space-x-2">
                <span class="text-xs text-gray-500">VNC: localhost:5900</span>
                <button
                  @click="openVNCExternal"
                  class="btn btn-outline-sm flex items-center space-x-1"
                >
                  <ArrowTopRightOnSquareIcon class="w-3 h-3" />
                  <span class="text-xs">External</span>
                </button>
              </div>
            </div>

            <div class="vnc-container bg-gray-100 rounded border relative">
              <iframe
                :src="vncViewerUrl"
                width="100%"
                height="400"
                frameborder="0"
                class="rounded"
              ></iframe>

              <div v-if="simulationStatus === 'stopped'"
                   class="absolute inset-0 bg-gray-800 bg-opacity-75 flex items-center justify-center rounded">
                <div class="text-center text-white">
                  <ComputerDesktopIcon class="w-16 h-16 mx-auto mb-4 opacity-50" />
                  <p class="text-lg font-medium">Simulation Stopped</p>
                  <p class="text-sm opacity-75">Start simulation to view JaamSim</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Real-time Metrics -->
          <div class="simulation-metrics bg-white rounded-lg shadow-sm p-6">
            <h3 class="text-lg font-semibold mb-4 flex items-center">
              <ChartBarIcon class="w-5 h-5 mr-2 text-green-500" />
              Real-time Metrics
            </h3>

            <div class="metrics-grid grid grid-cols-2 md:grid-cols-4 gap-4">
              <div class="metric-card bg-blue-50 p-4 rounded-lg text-center">
                <div class="metric-value text-2xl font-bold text-blue-600">
                  {{ metrics.processedEvents || 0 }}
                </div>
                <div class="metric-label text-sm text-gray-600">Events Processed</div>
              </div>

              <div class="metric-card bg-green-50 p-4 rounded-lg text-center">
                <div class="metric-value text-2xl font-bold text-green-600">
                  {{ metrics.activeEntities || 0 }}
                </div>
                <div class="metric-label text-sm text-gray-600">Active Entities</div>
              </div>

              <div class="metric-card bg-yellow-50 p-4 rounded-lg text-center">
                <div class="metric-value text-2xl font-bold text-yellow-600">
                  {{ metrics.queueLength || 0 }}
                </div>
                <div class="metric-label text-sm text-gray-600">Queue Length</div>
              </div>

              <div class="metric-card bg-purple-50 p-4 rounded-lg text-center">
                <div class="metric-value text-2xl font-bold text-purple-600">
                  {{ metrics.utilization || 0 }}%
                </div>
                <div class="metric-label text-sm text-gray-600">Resource Utilization</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Right Column: Exercise Progress & Activity -->
        <div class="space-y-6">

          <!-- Exercise Progress -->
          <div class="exercise-progress bg-white rounded-lg shadow-sm p-6">
            <h3 class="text-lg font-semibold mb-4 flex items-center">
              <ClipboardDocumentListIcon class="w-5 h-5 mr-2 text-indigo-500" />
              Exercise Progress
            </h3>

            <div class="progress-timeline space-y-4">
              <div
                v-for="(phase, index) in exercisePhases"
                :key="index"
                class="timeline-item flex items-start space-x-3"
                :class="{
                  'opacity-50': phase.status === 'pending',
                  'text-green-600': phase.status === 'completed'
                }"
              >
                <div class="timeline-marker mt-1">
                  <CheckCircleIcon
                    v-if="phase.status === 'completed'"
                    class="w-5 h-5 text-green-500"
                  />
                  <ClockIcon
                    v-else-if="phase.status === 'active'"
                    class="w-5 h-5 text-blue-500 animate-pulse"
                  />
                  <div
                    v-else
                    class="w-5 h-5 rounded-full border-2 border-gray-300"
                  ></div>
                </div>

                <div class="timeline-content flex-1">
                  <h4 class="font-medium">{{ phase.name }}</h4>
                  <p class="text-sm text-gray-600">{{ phase.description }}</p>
                  <small v-if="phase.completedAt" class="text-xs text-gray-500">
                    Completed: {{ formatTime(phase.completedAt) }}
                  </small>
                </div>
              </div>
            </div>
          </div>

          <!-- Participant Activity -->
          <div class="participant-activity bg-white rounded-lg shadow-sm p-6">
            <h3 class="text-lg font-semibold mb-4 flex items-center">
              <UsersIcon class="w-5 h-5 mr-2 text-orange-500" />
              Participant Activity
            </h3>

            <div class="activity-list space-y-3 max-h-64 overflow-y-auto">
              <div
                v-for="activity in recentActivity"
                :key="activity.id"
                class="activity-item p-3 bg-gray-50 rounded-lg"
              >
                <div class="flex items-center justify-between">
                  <div class="activity-user font-medium text-sm">
                    {{ activity.user_name }}
                  </div>
                  <div class="activity-time text-xs text-gray-500">
                    {{ formatTime(activity.timestamp) }}
                  </div>
                </div>
                <div class="activity-action text-sm text-gray-600 mt-1">
                  {{ activity.action }}
                </div>
              </div>

              <div v-if="recentActivity.length === 0" class="text-center text-gray-500 py-8">
                <UsersIcon class="w-8 h-8 mx-auto mb-2 opacity-50" />
                <p class="text-sm">No recent activity</p>
              </div>
            </div>
          </div>

          <!-- NICS Integration Panel -->
          <div v-if="nicsEnabled" class="nics-integration bg-white rounded-lg shadow-sm p-6">
            <h3 class="text-lg font-semibold mb-4 flex items-center">
              <BuildingOfficeIcon class="w-5 h-5 mr-2 text-red-500" />
              NICS Command Structure
            </h3>

            <div class="nics-roles space-y-2">
              <div
                v-for="role in nicsRoles"
                :key="role.code"
                class="role-assignment flex justify-between items-center p-2 bg-gray-50 rounded"
              >
                <div class="role-info">
                  <div class="role-title font-medium text-sm">{{ role.name }}</div>
                  <div class="role-code text-xs text-gray-500">({{ role.code }})</div>
                </div>
                <div class="role-assignee text-sm">
                  {{ role.assignee || 'Unassigned' }}
                </div>
              </div>
            </div>

            <button
              @click="openNICSPlatform"
              class="btn btn-outline w-full mt-4 flex items-center justify-center space-x-2"
            >
              <ArrowTopRightOnSquareIcon class="w-4 h-4" />
              <span>Open NICS Platform</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Simulation Results Panel -->
    <div v-if="simulationResults" class="simulation-results bg-white rounded-lg shadow-sm p-6 mt-6">
      <h3 class="text-lg font-semibold mb-4 flex items-center">
        <ChartBarIcon class="w-5 h-5 mr-2 text-purple-500" />
        Simulation Results
      </h3>

      <div class="results-tabs">
        <div class="border-b border-gray-200 mb-4">
          <nav class="flex space-x-8">
            <button
              v-for="tab in resultTabs"
              :key="tab.id"
              @click="activeTab = tab.id"
              :class="[
                'py-2 px-1 border-b-2 font-medium text-sm',
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              ]"
            >
              {{ tab.label }}
            </button>
          </nav>
        </div>

        <div class="tab-content">
          <!-- Summary Tab -->
          <div v-if="activeTab === 'summary'" class="tab-pane">
            <SimulationSummaryChart :data="simulationResults.summary" />
          </div>

          <!-- Metrics Tab -->
          <div v-if="activeTab === 'metrics'" class="tab-pane">
            <SimulationMetricsTable :data="simulationResults.metrics" />
          </div>

          <!-- Raw Data Tab -->
          <div v-if="activeTab === 'raw'" class="tab-pane">
            <div class="bg-gray-900 text-green-400 p-4 rounded-lg font-mono text-sm overflow-x-auto">
              <pre>{{ JSON.stringify(simulationResults.raw, null, 2) }}</pre>
            </div>
            <button
              @click="downloadResults"
              class="btn btn-outline mt-4 flex items-center space-x-2"
            >
              <ArrowDownTrayIcon class="w-4 h-4" />
              <span>Download CSV</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import {
  PlayIcon,
  PauseIcon,
  StopIcon,
  ComputerDesktopIcon,
  ChartBarIcon,
  ClipboardDocumentListIcon,
  UsersIcon,
  BuildingOfficeIcon,
  ArrowTopRightOnSquareIcon,
  ArrowDownTrayIcon,
  CheckCircleIcon,
  ClockIcon
} from '@heroicons/vue/24/outline'
import { useToast } from 'vue-toastification'
import { simulationService } from '@/services/simulationService'
import SimulationSummaryChart from './SimulationSummaryChart.vue'
import SimulationMetricsTable from './SimulationMetricsTable.vue'

interface Props {
  exerciseId: string
}

const props = defineProps<Props>()
const toast = useToast()

// Reactive data
const simulationStatus = ref<'stopped' | 'running' | 'paused'>('stopped')
const metrics = ref({
  processedEvents: 0,
  activeEntities: 0,
  queueLength: 0,
  utilization: 0
})
const exerciseData = ref(null)
const exercisePhases = ref([])
const recentActivity = ref([])
const nicsEnabled = ref(false)
const nicsRoles = ref([])
const simulationResults = ref(null)
const activeTab = ref('summary')
const vncViewerUrl = ref('http://localhost:5900')
let ws: WebSocket | null = null

// Computed properties
const simulationStatusClass = computed(() => ({
  'text-green-600': simulationStatus.value === 'running',
  'text-yellow-600': simulationStatus.value === 'paused',
  'text-gray-600': simulationStatus.value === 'stopped'
}))

const simulationStatusText = computed(() => ({
  'running': 'Simulation Running',
  'paused': 'Simulation Paused',
  'stopped': 'Simulation Stopped'
})[simulationStatus.value] || 'Unknown')

const statusIcon = computed(() => ({
  'running': PlayIcon,
  'paused': PauseIcon,
  'stopped': StopIcon
})[simulationStatus.value] || StopIcon)

const resultTabs = [
  { id: 'summary', label: 'Summary' },
  { id: 'metrics', label: 'Metrics' },
  { id: 'raw', label: 'Raw Data' }
]

// Methods
const startSimulation = async () => {
  try {
    const response = await simulationService.startSimulation(props.exerciseId)

    if (response.success) {
      simulationStatus.value = 'running'
      startRealTimeUpdates()
      toast.success('Simulation started successfully')
    }
  } catch (error) {
    toast.error(`Failed to start simulation: ${error.message}`)
    console.error('Simulation start error:', error)
  }
}

const pauseSimulation = async () => {
  try {
    const response = await simulationService.pauseSimulation(props.exerciseId)

    if (response.success) {
      simulationStatus.value = 'paused'
      toast.info('Simulation paused')
    }
  } catch (error) {
    toast.error(`Failed to pause simulation: ${error.message}`)
  }
}

const stopSimulation = async () => {
  try {
    const response = await simulationService.stopSimulation(props.exerciseId)

    if (response.success) {
      simulationStatus.value = 'stopped'
      closeWebSocket()
      toast.info('Simulation stopped')
    }
  } catch (error) {
    toast.error(`Failed to stop simulation: ${error.message}`)
  }
}

const startRealTimeUpdates = () => {
  closeWebSocket()

  ws = new WebSocket(`ws://localhost:8094/ws/simulation/${props.exerciseId}`)

  ws.onopen = () => {
    console.log('WebSocket connected for simulation updates')
  }

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)

      switch (data.type) {
        case 'metrics_update':
          metrics.value = { ...metrics.value, ...data.metrics }
          break

        case 'phase_update':
          updateExercisePhase(data.phase)
          break

        case 'participant_activity':
          recentActivity.value.unshift(data.activity)
          if (recentActivity.value.length > 10) {
            recentActivity.value = recentActivity.value.slice(0, 10)
          }
          break

        case 'simulation_completed':
          simulationStatus.value = 'stopped'
          simulationResults.value = data.results
          toast.success('Simulation completed successfully')
          break

        default:
          console.log('Unknown WebSocket message type:', data.type)
      }
    } catch (error) {
      console.error('Error parsing WebSocket message:', error)
    }
  }

  ws.onerror = (error) => {
    console.error('WebSocket error:', error)
    toast.error('Real-time connection lost')
  }

  ws.onclose = () => {
    console.log('WebSocket disconnected')
  }
}

const closeWebSocket = () => {
  if (ws) {
    ws.close()
    ws = null
  }
}

const updateExercisePhase = (phaseUpdate: any) => {
  const phaseIndex = exercisePhases.value.findIndex(p => p.id === phaseUpdate.id)
  if (phaseIndex !== -1) {
    exercisePhases.value[phaseIndex] = { ...exercisePhases.value[phaseIndex], ...phaseUpdate }
  }
}

const openVNCExternal = () => {
  window.open('vnc://localhost:5900', '_blank')
}

const openNICSPlatform = () => {
  window.open('http://localhost:8080/nics', '_blank')
}

const downloadResults = () => {
  if (!simulationResults.value) return

  const csv = simulationService.exportResultsToCSV(simulationResults.value)
  const blob = new Blob([csv], { type: 'text/csv' })
  const url = URL.createObjectURL(blob)

  const a = document.createElement('a')
  a.href = url
  a.download = `simulation-results-${props.exerciseId}-${Date.now()}.csv`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

const formatTime = (timestamp: string | number) => {
  return new Date(timestamp).toLocaleTimeString()
}

const loadExerciseData = async () => {
  try {
    const [exercise, phases, activity, nics] = await Promise.all([
      simulationService.getExerciseDetails(props.exerciseId),
      simulationService.getExercisePhases(props.exerciseId),
      simulationService.getRecentActivity(props.exerciseId),
      simulationService.getNICSIntegration(props.exerciseId)
    ])

    exerciseData.value = exercise
    exercisePhases.value = phases
    recentActivity.value = activity
    nicsEnabled.value = nics.enabled
    nicsRoles.value = nics.roles || []
  } catch (error) {
    console.error('Error loading exercise data:', error)
    toast.error('Failed to load exercise data')
  }
}

const checkSimulationStatus = async () => {
  try {
    const status = await simulationService.getSimulationStatus(props.exerciseId)
    simulationStatus.value = status.status

    if (status.status === 'running') {
      startRealTimeUpdates()
    }
  } catch (error) {
    console.error('Error checking simulation status:', error)
  }
}

// Lifecycle
onMounted(async () => {
  await loadExerciseData()
  await checkSimulationStatus()
})

onUnmounted(() => {
  closeWebSocket()
})
</script>

<style scoped>
.btn {
  @apply px-4 py-2 rounded-lg font-medium transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed;
}

.btn-success {
  @apply bg-green-600 text-white hover:bg-green-700 disabled:hover:bg-green-600;
}

.btn-warning {
  @apply bg-yellow-600 text-white hover:bg-yellow-700 disabled:hover:bg-yellow-600;
}

.btn-danger {
  @apply bg-red-600 text-white hover:bg-red-700 disabled:hover:bg-red-600;
}

.btn-outline {
  @apply border border-gray-300 text-gray-700 hover:bg-gray-50;
}

.btn-outline-sm {
  @apply border border-gray-300 text-gray-700 hover:bg-gray-50 px-2 py-1 text-xs;
}

.vnc-container {
  min-height: 400px;
}

.metrics-grid .metric-card {
  transition: transform 0.2s ease-in-out;
}

.metrics-grid .metric-card:hover {
  transform: translateY(-2px);
}

.timeline-item {
  transition: all 0.3s ease;
}

.activity-list {
  scrollbar-width: thin;
  scrollbar-color: #cbd5e0 #f7fafc;
}

.activity-list::-webkit-scrollbar {
  width: 6px;
}

.activity-list::-webkit-scrollbar-track {
  @apply bg-gray-100 rounded;
}

.activity-list::-webkit-scrollbar-thumb {
  @apply bg-gray-300 rounded;
}

.activity-list::-webkit-scrollbar-thumb:hover {
  @apply bg-gray-400;
}
</style>