<template>
  <div class="exercise-monitor">
    <!-- Header with Exercise Overview -->
    <div class="monitor-header bg-white rounded-lg shadow-sm p-6 mb-6">
      <div class="flex items-center justify-between">
        <div class="exercise-info">
          <h1 class="text-2xl font-bold text-gray-900">{{ exercise?.name || 'Loading Exercise...' }}</h1>
          <p class="text-gray-600 mt-1">{{ exercise?.description }}</p>

          <div class="flex items-center space-x-4 mt-4">
            <div class="status-badge" :class="exerciseStatusClass">
              <component :is="statusIcon" class="w-4 h-4" />
              <span class="ml-1 text-sm font-medium">{{ exercise?.status || 'Unknown' }}</span>
            </div>

            <div class="text-sm text-gray-500">
              <CalendarIcon class="w-4 h-4 inline mr-1" />
              Started: {{ formatDateTime(exercise?.started_at) }}
            </div>

            <div v-if="exercise?.duration" class="text-sm text-gray-500">
              <ClockIcon class="w-4 h-4 inline mr-1" />
              Duration: {{ formatDuration(exercise.duration) }}
            </div>
          </div>
        </div>

        <div class="exercise-actions flex space-x-2">
          <button
            @click="exportExerciseData"
            class="btn btn-outline flex items-center space-x-2"
          >
            <ArrowDownTrayIcon class="w-4 h-4" />
            <span>Export Data</span>
          </button>

          <button
            @click="openFullScreenMonitor"
            class="btn btn-primary flex items-center space-x-2"
          >
            <ArrowsPointingOutIcon class="w-4 h-4" />
            <span>Full Screen</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Main Monitoring Dashboard -->
    <div class="monitoring-dashboard grid grid-cols-1 lg:grid-cols-4 gap-6">

      <!-- Left Column: Participants & Activity -->
      <div class="lg:col-span-1 space-y-6">

        <!-- Participants List -->
        <div class="participants-panel bg-white rounded-lg shadow-sm p-6">
          <h3 class="text-lg font-semibold mb-4 flex items-center">
            <UsersIcon class="w-5 h-5 mr-2 text-blue-500" />
            Participants ({{ participants.length }})
          </h3>

          <div class="participants-list space-y-3 max-h-80 overflow-y-auto">
            <div
              v-for="participant in participants"
              :key="participant.id"
              class="participant-item p-3 bg-gray-50 rounded-lg"
            >
              <div class="flex items-center justify-between">
                <div class="participant-info">
                  <div class="font-medium text-sm">{{ participant.name }}</div>
                  <div class="text-xs text-gray-500">{{ participant.role }}</div>
                </div>

                <div class="participant-status">
                  <div
                    class="status-dot"
                    :class="{
                      'bg-green-500': participant.status === 'active',
                      'bg-yellow-500': participant.status === 'idle',
                      'bg-red-500': participant.status === 'disconnected'
                    }"
                  ></div>
                </div>
              </div>

              <div v-if="participant.current_action" class="mt-2">
                <div class="text-xs text-gray-600">
                  Current: {{ participant.current_action }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Activity Feed -->
        <div class="activity-feed bg-white rounded-lg shadow-sm p-6">
          <h3 class="text-lg font-semibold mb-4 flex items-center">
            <ChatBubbleLeftRightIcon class="w-5 h-5 mr-2 text-green-500" />
            Activity Feed
          </h3>

          <div class="activity-list space-y-3 max-h-64 overflow-y-auto">
            <div
              v-for="activity in activityFeed"
              :key="activity.id"
              class="activity-item p-3 border-l-4 bg-gray-50"
              :class="{
                'border-blue-500': activity.type === 'action',
                'border-green-500': activity.type === 'success',
                'border-yellow-500': activity.type === 'warning',
                'border-red-500': activity.type === 'error'
              }"
            >
              <div class="flex items-start justify-between">
                <div class="activity-content flex-1">
                  <div class="text-sm font-medium">{{ activity.user_name }}</div>
                  <div class="text-sm text-gray-600 mt-1">{{ activity.message }}</div>
                </div>
                <div class="text-xs text-gray-500">
                  {{ formatRelativeTime(activity.timestamp) }}
                </div>
              </div>
            </div>

            <div v-if="activityFeed.length === 0" class="text-center text-gray-500 py-8">
              <ChatBubbleLeftRightIcon class="w-8 h-8 mx-auto mb-2 opacity-50" />
              <p class="text-sm">No recent activity</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Middle Column: Simulation Metrics -->
      <div class="lg:col-span-2 space-y-6">

        <!-- Real-time Metrics Dashboard -->
        <div class="metrics-dashboard bg-white rounded-lg shadow-sm p-6">
          <h3 class="text-lg font-semibold mb-4 flex items-center">
            <ChartBarIcon class="w-5 h-5 mr-2 text-purple-500" />
            Real-time Simulation Metrics
          </h3>

          <!-- Key Performance Indicators -->
          <div class="kpi-grid grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div class="kpi-card bg-blue-50 p-4 rounded-lg text-center">
              <div class="kpi-value text-2xl font-bold text-blue-600">
                {{ metrics.processedEvents?.toLocaleString() || 0 }}
              </div>
              <div class="kpi-label text-sm text-gray-600">Events Processed</div>
              <div class="kpi-trend text-xs text-green-600 mt-1">
                +{{ eventsTrend }}% from last hour
              </div>
            </div>

            <div class="kpi-card bg-green-50 p-4 rounded-lg text-center">
              <div class="kpi-value text-2xl font-bold text-green-600">
                {{ metrics.activeEntities || 0 }}
              </div>
              <div class="kpi-label text-sm text-gray-600">Active Entities</div>
              <div class="kpi-trend text-xs text-blue-600 mt-1">
                {{ entityTrend > 0 ? '+' : '' }}{{ entityTrend }}% from baseline
              </div>
            </div>

            <div class="kpi-card bg-yellow-50 p-4 rounded-lg text-center">
              <div class="kpi-value text-2xl font-bold text-yellow-600">
                {{ metrics.queueLength || 0 }}
              </div>
              <div class="kpi-label text-sm text-gray-600">Queue Length</div>
              <div class="kpi-trend text-xs" :class="queueTrend > 5 ? 'text-red-600' : 'text-green-600'">
                Avg: {{ avgQueueLength }}
              </div>
            </div>

            <div class="kpi-card bg-purple-50 p-4 rounded-lg text-center">
              <div class="kpi-value text-2xl font-bold text-purple-600">
                {{ metrics.utilization || 0 }}%
              </div>
              <div class="kpi-label text-sm text-gray-600">Resource Utilization</div>
              <div class="kpi-trend text-xs" :class="metrics.utilization > 80 ? 'text-red-600' : 'text-green-600'">
                {{ metrics.utilization > 80 ? 'High' : 'Optimal' }}
              </div>
            </div>
          </div>

          <!-- Performance Charts -->
          <div class="performance-charts">
            <div class="chart-tabs mb-4">
              <div class="border-b border-gray-200">
                <nav class="flex space-x-8">
                  <button
                    v-for="chart in chartTabs"
                    :key="chart.id"
                    @click="activeChart = chart.id"
                    :class="[
                      'py-2 px-1 border-b-2 font-medium text-sm',
                      activeChart === chart.id
                        ? 'border-blue-500 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    ]"
                  >
                    {{ chart.label }}
                  </button>
                </nav>
              </div>
            </div>

            <div class="chart-container" style="height: 300px;">
              <MetricsChart
                v-if="activeChart === 'metrics'"
                :data="metricsHistory"
                :type="'line'"
              />
              <UtilizationChart
                v-else-if="activeChart === 'utilization'"
                :data="utilizationHistory"
              />
              <ResponseTimeChart
                v-else-if="activeChart === 'response'"
                :data="responseTimeHistory"
              />
            </div>
          </div>
        </div>

        <!-- Exercise Progress Timeline -->
        <div class="progress-timeline bg-white rounded-lg shadow-sm p-6">
          <h3 class="text-lg font-semibold mb-4 flex items-center">
            <ClipboardDocumentListIcon class="w-5 h-5 mr-2 text-indigo-500" />
            Exercise Progress
          </h3>

          <div class="timeline-container">
            <div class="progress-bar bg-gray-200 rounded-full h-2 mb-6">
              <div
                class="progress-fill bg-blue-500 h-2 rounded-full transition-all duration-500"
                :style="{ width: `${overallProgress}%` }"
              ></div>
            </div>

            <div class="phases-timeline space-y-4">
              <div
                v-for="(phase, index) in phases"
                :key="phase.id"
                class="phase-item flex items-start space-x-4"
                :class="{
                  'opacity-50': phase.status === 'pending',
                  'text-green-600': phase.status === 'completed'
                }"
              >
                <div class="phase-marker mt-1">
                  <CheckCircleIcon
                    v-if="phase.status === 'completed'"
                    class="w-6 h-6 text-green-500"
                  />
                  <ClockIcon
                    v-else-if="phase.status === 'active'"
                    class="w-6 h-6 text-blue-500 animate-pulse"
                  />
                  <div
                    v-else
                    class="w-6 h-6 rounded-full border-2 border-gray-300 bg-white"
                  ></div>
                </div>

                <div class="phase-content flex-1">
                  <div class="flex items-center justify-between">
                    <h4 class="font-medium">{{ phase.name }}</h4>
                    <span v-if="phase.status === 'active'" class="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                      Active
                    </span>
                  </div>
                  <p class="text-sm text-gray-600 mt-1">{{ phase.description }}</p>

                  <div v-if="phase.status === 'active' && phase.progress" class="mt-2">
                    <div class="flex items-center justify-between text-xs text-gray-500 mb-1">
                      <span>Progress</span>
                      <span>{{ phase.progress }}%</span>
                    </div>
                    <div class="progress-bar bg-gray-200 rounded-full h-1">
                      <div
                        class="progress-fill bg-blue-500 h-1 rounded-full transition-all duration-300"
                        :style="{ width: `${phase.progress}%` }"
                      ></div>
                    </div>
                  </div>

                  <div v-if="phase.completedAt" class="text-xs text-gray-500 mt-2">
                    Completed: {{ formatDateTime(phase.completedAt) }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Column: System Status & Controls -->
      <div class="lg:col-span-1 space-y-6">

        <!-- System Status Panel -->
        <div class="system-status bg-white rounded-lg shadow-sm p-6">
          <h3 class="text-lg font-semibold mb-4 flex items-center">
            <CpuChipIcon class="w-5 h-5 mr-2 text-red-500" />
            System Status
          </h3>

          <div class="status-items space-y-3">
            <div
              v-for="service in systemServices"
              :key="service.name"
              class="service-status flex items-center justify-between p-3 bg-gray-50 rounded"
            >
              <div class="service-info">
                <div class="font-medium text-sm">{{ service.name }}</div>
                <div class="text-xs text-gray-500">{{ service.endpoint }}</div>
              </div>
              <div class="status-indicator">
                <div
                  class="status-dot"
                  :class="{
                    'bg-green-500': service.status === 'healthy',
                    'bg-yellow-500': service.status === 'degraded',
                    'bg-red-500': service.status === 'unhealthy'
                  }"
                ></div>
              </div>
            </div>
          </div>

          <button
            @click="refreshSystemStatus"
            class="btn btn-outline w-full mt-4 flex items-center justify-center space-x-2"
            :disabled="refreshingStatus"
          >
            <ArrowPathIcon class="w-4 h-4" :class="{ 'animate-spin': refreshingStatus }" />
            <span>Refresh Status</span>
          </button>
        </div>

        <!-- Quick Actions -->
        <div class="quick-actions bg-white rounded-lg shadow-sm p-6">
          <h3 class="text-lg font-semibold mb-4 flex items-center">
            <BoltIcon class="w-5 h-5 mr-2 text-yellow-500" />
            Quick Actions
          </h3>

          <div class="actions-grid space-y-3">
            <button
              @click="takeSnapshot"
              class="action-btn w-full p-3 bg-blue-50 hover:bg-blue-100 rounded-lg text-left transition-colors"
            >
              <div class="flex items-center space-x-3">
                <CameraIcon class="w-5 h-5 text-blue-500" />
                <div>
                  <div class="font-medium text-sm">Take Snapshot</div>
                  <div class="text-xs text-gray-500">Save current state</div>
                </div>
              </div>
            </button>

            <button
              @click="generateReport"
              class="action-btn w-full p-3 bg-green-50 hover:bg-green-100 rounded-lg text-left transition-colors"
            >
              <div class="flex items-center space-x-3">
                <DocumentTextIcon class="w-5 h-5 text-green-500" />
                <div>
                  <div class="font-medium text-sm">Generate Report</div>
                  <div class="text-xs text-gray-500">Create progress report</div>
                </div>
              </div>
            </button>

            <button
              @click="broadcastMessage"
              class="action-btn w-full p-3 bg-purple-50 hover:bg-purple-100 rounded-lg text-left transition-colors"
            >
              <div class="flex items-center space-x-3">
                <SpeakerWaveIcon class="w-5 h-5 text-purple-500" />
                <div>
                  <div class="font-medium text-sm">Broadcast Message</div>
                  <div class="text-xs text-gray-500">Send to all participants</div>
                </div>
              </div>
            </button>

            <button
              @click="openVNCViewer"
              class="action-btn w-full p-3 bg-orange-50 hover:bg-orange-100 rounded-lg text-left transition-colors"
            >
              <div class="flex items-center space-x-3">
                <ComputerDesktopIcon class="w-5 h-5 text-orange-500" />
                <div>
                  <div class="font-medium text-sm">Open VNC Viewer</div>
                  <div class="text-xs text-gray-500">View JaamSim display</div>
                </div>
              </div>
            </button>
          </div>
        </div>

        <!-- Exercise Controls -->
        <div class="exercise-controls bg-white rounded-lg shadow-sm p-6">
          <h3 class="text-lg font-semibold mb-4 flex items-center">
            <Cog6ToothIcon class="w-5 h-5 mr-2 text-gray-500" />
            Exercise Controls
          </h3>

          <div class="controls-grid space-y-3">
            <button
              @click="pauseExercise"
              :disabled="exercise?.status !== 'running'"
              class="btn btn-warning w-full flex items-center justify-center space-x-2"
            >
              <PauseIcon class="w-4 h-4" />
              <span>Pause Exercise</span>
            </button>

            <button
              @click="extendTime"
              :disabled="exercise?.status !== 'running'"
              class="btn btn-outline w-full flex items-center justify-center space-x-2"
            >
              <ClockIcon class="w-4 h-4" />
              <span>Extend Time</span>
            </button>

            <button
              @click="endExercise"
              :disabled="exercise?.status === 'completed'"
              class="btn btn-danger w-full flex items-center justify-center space-x-2"
            >
              <StopIcon class="w-4 h-4" />
              <span>End Exercise</span>
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
  UsersIcon,
  ChatBubbleLeftRightIcon,
  ChartBarIcon,
  ClipboardDocumentListIcon,
  CpuChipIcon,
  BoltIcon,
  Cog6ToothIcon,
  CalendarIcon,
  ClockIcon,
  CheckCircleIcon,
  ArrowDownTrayIcon,
  ArrowsPointingOutIcon,
  ArrowPathIcon,
  CameraIcon,
  DocumentTextIcon,
  SpeakerWaveIcon,
  ComputerDesktopIcon,
  PauseIcon,
  StopIcon
} from '@heroicons/vue/24/outline'
import { useToast } from 'vue-toastification'
import { simulationService } from '@/services/simulationService'
import MetricsChart from './charts/MetricsChart.vue'
import UtilizationChart from './charts/UtilizationChart.vue'
import ResponseTimeChart from './charts/ResponseTimeChart.vue'

interface Props {
  exerciseId: string
}

const props = defineProps<Props>()
const toast = useToast()

// Reactive data
const exercise = ref(null)
const participants = ref([])
const activityFeed = ref([])
const metrics = ref({})
const phases = ref([])
const systemServices = ref([])
const refreshingStatus = ref(false)
const activeChart = ref('metrics')

const metricsHistory = ref([])
const utilizationHistory = ref([])
const responseTimeHistory = ref([])

let ws: WebSocket | null = null
let metricsInterval: NodeJS.Timeout | null = null

// Computed properties
const exerciseStatusClass = computed(() => ({
  'bg-green-100 text-green-800': exercise.value?.status === 'running',
  'bg-yellow-100 text-yellow-800': exercise.value?.status === 'paused',
  'bg-blue-100 text-blue-800': exercise.value?.status === 'completed',
  'bg-gray-100 text-gray-800': exercise.value?.status === 'stopped'
}))

const statusIcon = computed(() => {
  // This would return the appropriate icon based on status
  return CheckCircleIcon // Placeholder
})

const overallProgress = computed(() => {
  if (phases.value.length === 0) return 0
  const completedPhases = phases.value.filter(p => p.status === 'completed').length
  return Math.round((completedPhases / phases.value.length) * 100)
})

const eventsTrend = computed(() => {
  // Calculate trend from metrics history
  return Math.round(Math.random() * 20) // Placeholder
})

const entityTrend = computed(() => {
  // Calculate entity trend
  return Math.round((Math.random() - 0.5) * 30) // Placeholder
})

const queueTrend = computed(() => {
  return metrics.value.queueLength || 0
})

const avgQueueLength = computed(() => {
  if (metricsHistory.value.length === 0) return 0
  const sum = metricsHistory.value.reduce((acc, m) => acc + (m.queueLength || 0), 0)
  return Math.round(sum / metricsHistory.value.length)
})

const chartTabs = [
  { id: 'metrics', label: 'System Metrics' },
  { id: 'utilization', label: 'Utilization' },
  { id: 'response', label: 'Response Times' }
]

// Methods
const loadExerciseData = async () => {
  try {
    const [exerciseData, participantData, activityData, phaseData] = await Promise.all([
      simulationService.getExerciseDetails(props.exerciseId),
      simulationService.getParticipants(props.exerciseId),
      simulationService.getRecentActivity(props.exerciseId),
      simulationService.getExercisePhases(props.exerciseId)
    ])

    exercise.value = exerciseData
    participants.value = participantData
    activityFeed.value = activityData
    phases.value = phaseData
  } catch (error) {
    console.error('Error loading exercise data:', error)
    toast.error('Failed to load exercise data')
  }
}

const refreshSystemStatus = async () => {
  refreshingStatus.value = true
  try {
    const status = await simulationService.checkServiceHealth()
    systemServices.value = status
  } catch (error) {
    console.error('Error refreshing system status:', error)
    toast.error('Failed to refresh system status')
  } finally {
    refreshingStatus.value = false
  }
}

const startRealTimeMonitoring = () => {
  // WebSocket connection for real-time updates
  ws = simulationService.createWebSocketConnection(props.exerciseId, (data) => {
    switch (data.type) {
      case 'metrics_update':
        metrics.value = { ...metrics.value, ...data.metrics }
        metricsHistory.value.push({
          timestamp: new Date(),
          ...data.metrics
        })
        // Keep only last 100 data points
        if (metricsHistory.value.length > 100) {
          metricsHistory.value = metricsHistory.value.slice(-100)
        }
        break

      case 'participant_update':
        const participantIndex = participants.value.findIndex(p => p.id === data.participant.id)
        if (participantIndex !== -1) {
          participants.value[participantIndex] = { ...participants.value[participantIndex], ...data.participant }
        }
        break

      case 'activity_update':
        activityFeed.value.unshift(data.activity)
        if (activityFeed.value.length > 50) {
          activityFeed.value = activityFeed.value.slice(0, 50)
        }
        break

      case 'phase_update':
        const phaseIndex = phases.value.findIndex(p => p.id === data.phase.id)
        if (phaseIndex !== -1) {
          phases.value[phaseIndex] = { ...phases.value[phaseIndex], ...data.phase }
        }
        break
    }
  })

  // Periodic metrics collection
  metricsInterval = setInterval(async () => {
    try {
      const currentMetrics = await simulationService.getJaamSimMetrics(props.exerciseId)
      metrics.value = currentMetrics
    } catch (error) {
      console.error('Error fetching metrics:', error)
    }
  }, 5000)
}

const stopRealTimeMonitoring = () => {
  if (ws) {
    ws.close()
    ws = null
  }

  if (metricsInterval) {
    clearInterval(metricsInterval)
    metricsInterval = null
  }
}

// Action handlers
const takeSnapshot = async () => {
  try {
    await simulationService.takeSnapshot(props.exerciseId)
    toast.success('Snapshot saved successfully')
  } catch (error) {
    toast.error('Failed to take snapshot')
  }
}

const generateReport = async () => {
  try {
    const report = await simulationService.generateProgressReport(props.exerciseId)
    // Download report
    const blob = new Blob([report], { type: 'application/pdf' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `exercise-report-${props.exerciseId}.pdf`
    a.click()
    URL.revokeObjectURL(url)
    toast.success('Report generated successfully')
  } catch (error) {
    toast.error('Failed to generate report')
  }
}

const broadcastMessage = () => {
  // Open broadcast message modal
  // Implementation would depend on your modal system
  toast.info('Broadcast message feature coming soon')
}

const openVNCViewer = () => {
  window.open('vnc://localhost:5900', '_blank')
}

const pauseExercise = async () => {
  try {
    await simulationService.pauseSimulation(props.exerciseId)
    exercise.value.status = 'paused'
    toast.success('Exercise paused')
  } catch (error) {
    toast.error('Failed to pause exercise')
  }
}

const extendTime = () => {
  // Open time extension modal
  toast.info('Time extension feature coming soon')
}

const endExercise = async () => {
  if (confirm('Are you sure you want to end this exercise? This action cannot be undone.')) {
    try {
      await simulationService.stopSimulation(props.exerciseId)
      exercise.value.status = 'completed'
      toast.success('Exercise ended successfully')
    } catch (error) {
      toast.error('Failed to end exercise')
    }
  }
}

const exportExerciseData = async () => {
  try {
    const data = await simulationService.exportExerciseData(props.exerciseId)
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `exercise-data-${props.exerciseId}.json`
    a.click()
    URL.revokeObjectURL(url)
    toast.success('Exercise data exported successfully')
  } catch (error) {
    toast.error('Failed to export exercise data')
  }
}

const openFullScreenMonitor = () => {
  // Open in new window for full screen monitoring
  window.open(`/exercise/${props.exerciseId}/monitor/fullscreen`, '_blank')
}

// Utility functions
const formatDateTime = (timestamp: string) => {
  return new Date(timestamp).toLocaleString()
}

const formatDuration = (seconds: number) => {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  return `${hours}h ${minutes}m`
}

const formatRelativeTime = (timestamp: string) => {
  const now = new Date()
  const time = new Date(timestamp)
  const diff = Math.floor((now.getTime() - time.getTime()) / 1000)

  if (diff < 60) return `${diff}s ago`
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`
  return time.toLocaleDateString()
}

// Lifecycle
onMounted(async () => {
  await loadExerciseData()
  await refreshSystemStatus()
  startRealTimeMonitoring()
})

onUnmounted(() => {
  stopRealTimeMonitoring()
})
</script>

<style scoped>
.btn {
  @apply px-4 py-2 rounded-lg font-medium transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed;
}

.btn-primary {
  @apply bg-blue-600 text-white hover:bg-blue-700;
}

.btn-warning {
  @apply bg-yellow-600 text-white hover:bg-yellow-700;
}

.btn-danger {
  @apply bg-red-600 text-white hover:bg-red-700;
}

.btn-outline {
  @apply border border-gray-300 text-gray-700 hover:bg-gray-50;
}

.status-badge {
  @apply inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium;
}

.status-dot {
  @apply w-3 h-3 rounded-full;
}

.kpi-card {
  transition: transform 0.2s ease-in-out;
}

.kpi-card:hover {
  transform: translateY(-2px);
}

.action-btn {
  transition: all 0.2s ease-in-out;
}

.action-btn:hover {
  transform: translateX(4px);
}

.participants-list,
.activity-list {
  scrollbar-width: thin;
  scrollbar-color: #cbd5e0 #f7fafc;
}

.participants-list::-webkit-scrollbar,
.activity-list::-webkit-scrollbar {
  width: 6px;
}

.participants-list::-webkit-scrollbar-track,
.activity-list::-webkit-scrollbar-track {
  @apply bg-gray-100 rounded;
}

.participants-list::-webkit-scrollbar-thumb,
.activity-list::-webkit-scrollbar-thumb {
  @apply bg-gray-300 rounded;
}

.participants-list::-webkit-scrollbar-thumb:hover,
.activity-list::-webkit-scrollbar-thumb:hover {
  @apply bg-gray-400;
}
</style>