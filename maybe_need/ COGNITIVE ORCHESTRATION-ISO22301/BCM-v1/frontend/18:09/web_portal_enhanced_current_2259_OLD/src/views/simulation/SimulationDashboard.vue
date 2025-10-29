<template>
  <div class="simulation-dashboard">
    <!-- Page Header -->
    <div class="page-header mb-8">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold text-gray-900">Simulation Dashboard</h1>
          <p class="text-gray-600 mt-2">
            Monitor and manage exercise simulations with real-time insights
          </p>
        </div>

        <div class="header-actions flex items-center space-x-3">
          <button
            @click="refreshDashboard"
            :disabled="isRefreshing"
            class="btn btn-outline flex items-center space-x-2"
          >
            <ArrowPathIcon class="w-4 h-4" :class="{ 'animate-spin': isRefreshing }" />
            <span>Refresh</span>
          </button>

          <button
            @click="createNewExercise"
            class="btn btn-primary flex items-center space-x-2"
          >
            <PlusIcon class="w-4 h-4" />
            <span>New Exercise</span>
          </button>
        </div>
      </div>
    </div>

    <!-- System Health Status -->
    <div class="system-status bg-white rounded-lg shadow-sm p-6 mb-8">
      <h2 class="text-lg font-semibold text-gray-900 mb-4 flex items-center">
        <CpuChipIcon class="w-5 h-5 mr-2 text-green-500" />
        System Health Status
      </h2>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div
          v-for="service in systemServices"
          :key="service.name"
          class="service-card p-4 border rounded-lg"
          :class="{
            'border-green-200 bg-green-50': service.status === 'healthy',
            'border-yellow-200 bg-yellow-50': service.status === 'degraded',
            'border-red-200 bg-red-50': service.status === 'unhealthy'
          }"
        >
          <div class="flex items-center justify-between mb-2">
            <h3 class="font-medium text-gray-900">{{ service.name }}</h3>
            <div
              class="status-indicator w-3 h-3 rounded-full"
              :class="{
                'bg-green-500': service.status === 'healthy',
                'bg-yellow-500': service.status === 'degraded',
                'bg-red-500': service.status === 'unhealthy'
              }"
            ></div>
          </div>

          <div class="text-sm text-gray-600 mb-2">{{ service.endpoint }}</div>

          <div class="flex items-center justify-between text-xs">
            <span class="text-gray-500">Uptime: {{ service.uptime }}%</span>
            <span
              class="px-2 py-1 rounded-full text-xs font-medium"
              :class="{
                'bg-green-100 text-green-800': service.status === 'healthy',
                'bg-yellow-100 text-yellow-800': service.status === 'degraded',
                'bg-red-100 text-red-800': service.status === 'unhealthy'
              }"
            >
              {{ service.status }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Active Exercises -->
    <div class="active-exercises bg-white rounded-lg shadow-sm p-6 mb-8">
      <div class="flex items-center justify-between mb-6">
        <h2 class="text-lg font-semibold text-gray-900 flex items-center">
          <PlayIcon class="w-5 h-5 mr-2 text-blue-500" />
          Active Exercises ({{ activeExercises.length }})
        </h2>

        <div class="view-controls flex items-center space-x-2">
          <button
            @click="viewMode = 'grid'"
            :class="[
              'btn btn-sm',
              viewMode === 'grid' ? 'btn-primary' : 'btn-outline'
            ]"
          >
            <Squares2X2Icon class="w-4 h-4" />
          </button>
          <button
            @click="viewMode = 'list'"
            :class="[
              'btn btn-sm',
              viewMode === 'list' ? 'btn-primary' : 'btn-outline'
            ]"
          >
            <ListBulletIcon class="w-4 h-4" />
          </button>
        </div>
      </div>

      <!-- Grid View -->
      <div v-if="viewMode === 'grid'" class="exercises-grid grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div
          v-for="exercise in activeExercises"
          :key="exercise.id"
          class="exercise-card bg-gray-50 border rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
          @click="openExercise(exercise.id)"
        >
          <div class="flex items-center justify-between mb-3">
            <h3 class="font-medium text-gray-900 truncate">{{ exercise.name }}</h3>
            <span
              class="status-badge px-2 py-1 rounded-full text-xs font-medium"
              :class="{
                'bg-green-100 text-green-800': exercise.status === 'running',
                'bg-yellow-100 text-yellow-800': exercise.status === 'paused',
                'bg-blue-100 text-blue-800': exercise.status === 'preparing'
              }"
            >
              {{ exercise.status }}
            </span>
          </div>

          <div class="exercise-info space-y-2 mb-4">
            <div class="flex items-center text-sm text-gray-600">
              <UsersIcon class="w-4 h-4 mr-1" />
              <span>{{ exercise.participants }} participants</span>
            </div>

            <div class="flex items-center text-sm text-gray-600">
              <ClockIcon class="w-4 h-4 mr-1" />
              <span>{{ formatDuration(exercise.elapsed_time) }}</span>
            </div>

            <div class="flex items-center text-sm text-gray-600">
              <ComputerDesktopIcon class="w-4 h-4 mr-1" />
              <span>{{ exercise.simulation_engine }}</span>
            </div>
          </div>

          <div class="progress-section">
            <div class="flex items-center justify-between text-xs text-gray-500 mb-1">
              <span>Progress</span>
              <span>{{ exercise.progress }}%</span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2">
              <div
                class="bg-blue-500 h-2 rounded-full transition-all duration-300"
                :style="{ width: `${exercise.progress}%` }"
              ></div>
            </div>
          </div>

          <div class="exercise-actions mt-4 flex space-x-2">
            <button
              @click.stop="openMonitor(exercise.id)"
              class="btn btn-sm btn-outline flex-1"
            >
              Monitor
            </button>
            <button
              @click.stop="openVNC(exercise.id)"
              class="btn btn-sm btn-outline"
              title="VNC Viewer"
            >
              <ComputerDesktopIcon class="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      <!-- List View -->
      <div v-else class="exercises-list">
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Exercise
                </th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Participants
                </th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Duration
                </th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Progress
                </th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr
                v-for="exercise in activeExercises"
                :key="exercise.id"
                class="hover:bg-gray-50 cursor-pointer"
                @click="openExercise(exercise.id)"
              >
                <td class="px-4 py-3">
                  <div>
                    <div class="font-medium text-gray-900">{{ exercise.name }}</div>
                    <div class="text-sm text-gray-500">{{ exercise.type }}</div>
                  </div>
                </td>
                <td class="px-4 py-3">
                  <span
                    class="inline-flex px-2 py-1 text-xs font-semibold rounded-full"
                    :class="{
                      'bg-green-100 text-green-800': exercise.status === 'running',
                      'bg-yellow-100 text-yellow-800': exercise.status === 'paused',
                      'bg-blue-100 text-blue-800': exercise.status === 'preparing'
                    }"
                  >
                    {{ exercise.status }}
                  </span>
                </td>
                <td class="px-4 py-3 text-sm text-gray-900">
                  {{ exercise.participants }}
                </td>
                <td class="px-4 py-3 text-sm text-gray-900">
                  {{ formatDuration(exercise.elapsed_time) }}
                </td>
                <td class="px-4 py-3">
                  <div class="flex items-center">
                    <div class="w-16 bg-gray-200 rounded-full h-2 mr-2">
                      <div
                        class="bg-blue-500 h-2 rounded-full"
                        :style="{ width: `${exercise.progress}%` }"
                      ></div>
                    </div>
                    <span class="text-sm text-gray-600">{{ exercise.progress }}%</span>
                  </div>
                </td>
                <td class="px-4 py-3">
                  <div class="flex space-x-2">
                    <button
                      @click.stop="openMonitor(exercise.id)"
                      class="text-blue-600 hover:text-blue-800"
                      title="Monitor"
                    >
                      <EyeIcon class="w-4 h-4" />
                    </button>
                    <button
                      @click.stop="openVNC(exercise.id)"
                      class="text-gray-600 hover:text-gray-800"
                      title="VNC Viewer"
                    >
                      <ComputerDesktopIcon class="w-4 h-4" />
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="activeExercises.length === 0" class="empty-state text-center py-12">
        <PlayIcon class="w-16 h-16 mx-auto text-gray-300 mb-4" />
        <h3 class="text-lg font-medium text-gray-900 mb-2">No Active Exercises</h3>
        <p class="text-gray-500 mb-6">
          Get started by creating your first exercise simulation
        </p>
        <button @click="createNewExercise" class="btn btn-primary">
          Create Exercise
        </button>
      </div>
    </div>

    <!-- Recent Activity & Statistics -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
      <!-- Recent Activity -->
      <div class="recent-activity bg-white rounded-lg shadow-sm p-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <ClockIcon class="w-5 h-5 mr-2 text-purple-500" />
          Recent Activity
        </h2>

        <div class="activity-list space-y-4">
          <div
            v-for="activity in recentActivity"
            :key="activity.id"
            class="activity-item flex items-start space-x-3 p-3 bg-gray-50 rounded-lg"
          >
            <div
              class="activity-icon w-8 h-8 rounded-full flex items-center justify-center"
              :class="{
                'bg-green-100': activity.type === 'exercise_completed',
                'bg-blue-100': activity.type === 'exercise_started',
                'bg-yellow-100': activity.type === 'exercise_paused',
                'bg-red-100': activity.type === 'exercise_error'
              }"
            >
              <component
                :is="getActivityIcon(activity.type)"
                class="w-4 h-4"
                :class="{
                  'text-green-600': activity.type === 'exercise_completed',
                  'text-blue-600': activity.type === 'exercise_started',
                  'text-yellow-600': activity.type === 'exercise_paused',
                  'text-red-600': activity.type === 'exercise_error'
                }"
              />
            </div>

            <div class="activity-content flex-1">
              <div class="activity-message text-sm text-gray-900">
                {{ activity.message }}
              </div>
              <div class="activity-time text-xs text-gray-500 mt-1">
                {{ formatRelativeTime(activity.timestamp) }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Statistics -->
      <div class="statistics bg-white rounded-lg shadow-sm p-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <ChartBarIcon class="w-5 h-5 mr-2 text-indigo-500" />
          Statistics
        </h2>

        <div class="stats-grid space-y-4">
          <div class="stat-item flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div>
              <div class="stat-label text-sm text-gray-600">Total Exercises</div>
              <div class="stat-value text-2xl font-bold text-gray-900">{{ statistics.totalExercises }}</div>
            </div>
            <div class="stat-icon">
              <FolderIcon class="w-8 h-8 text-gray-400" />
            </div>
          </div>

          <div class="stat-item flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div>
              <div class="stat-label text-sm text-gray-600">This Month</div>
              <div class="stat-value text-2xl font-bold text-blue-600">{{ statistics.thisMonth }}</div>
            </div>
            <div class="stat-icon">
              <CalendarIcon class="w-8 h-8 text-blue-400" />
            </div>
          </div>

          <div class="stat-item flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div>
              <div class="stat-label text-sm text-gray-600">Success Rate</div>
              <div class="stat-value text-2xl font-bold text-green-600">{{ statistics.successRate }}%</div>
            </div>
            <div class="stat-icon">
              <CheckCircleIcon class="w-8 h-8 text-green-400" />
            </div>
          </div>

          <div class="stat-item flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div>
              <div class="stat-label text-sm text-gray-600">Avg Duration</div>
              <div class="stat-value text-lg font-bold text-purple-600">{{ statistics.avgDuration }}</div>
            </div>
            <div class="stat-icon">
              <ClockIcon class="w-8 h-8 text-purple-400" />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  ArrowPathIcon,
  PlusIcon,
  CpuChipIcon,
  PlayIcon,
  Squares2X2Icon,
  ListBulletIcon,
  UsersIcon,
  ClockIcon,
  ComputerDesktopIcon,
  EyeIcon,
  ChartBarIcon,
  FolderIcon,
  CalendarIcon,
  CheckCircleIcon,
  PauseIcon,
  ExclamationTriangleIcon
} from '@heroicons/vue/24/outline'
import { useToast } from 'vue-toastification'
import { simulationService } from '@/services/simulationService'

const router = useRouter()
const toast = useToast()

// Reactive state
const isRefreshing = ref(false)
const viewMode = ref<'grid' | 'list'>('grid')

const systemServices = ref([
  {
    name: 'Exercise Simulators Bridge',
    endpoint: ':8094',
    status: 'healthy',
    uptime: 99.8
  },
  {
    name: 'JaamSim Engine',
    endpoint: ':5900',
    status: 'healthy',
    uptime: 98.5
  },
  {
    name: 'Simulation Adapter',
    endpoint: ':8012',
    status: 'healthy',
    uptime: 99.2
  }
])

const activeExercises = ref([
  {
    id: 'ex-001',
    name: 'Cyber Security Incident Response',
    type: 'Crisis Management',
    status: 'running',
    participants: 12,
    elapsed_time: 3600,
    progress: 65,
    simulation_engine: 'JaamSim'
  },
  {
    id: 'ex-002',
    name: 'Natural Disaster Recovery',
    type: 'Disaster Recovery',
    status: 'paused',
    participants: 8,
    elapsed_time: 2400,
    progress: 45,
    simulation_engine: 'JaamSim'
  }
])

const recentActivity = ref([
  {
    id: 'act-001',
    type: 'exercise_started',
    message: 'Exercise "Cyber Security Incident Response" started',
    timestamp: new Date(Date.now() - 300000).toISOString()
  },
  {
    id: 'act-002',
    type: 'exercise_paused',
    message: 'Exercise "Natural Disaster Recovery" paused by admin',
    timestamp: new Date(Date.now() - 600000).toISOString()
  },
  {
    id: 'act-003',
    type: 'exercise_completed',
    message: 'Exercise "Supply Chain Disruption" completed successfully',
    timestamp: new Date(Date.now() - 1800000).toISOString()
  }
])

const statistics = ref({
  totalExercises: 47,
  thisMonth: 12,
  successRate: 94,
  avgDuration: '2h 15m'
})

// Methods
const refreshDashboard = async () => {
  isRefreshing.value = true
  try {
    const [health, exercises, activity] = await Promise.all([
      simulationService.checkServiceHealth(),
      simulationService.getActiveExercises(),
      simulationService.getRecentActivity()
    ])

    systemServices.value = health
    activeExercises.value = exercises
    recentActivity.value = activity

    toast.success('Dashboard refreshed successfully')
  } catch (error) {
    console.error('Error refreshing dashboard:', error)
    toast.error('Failed to refresh dashboard')
  } finally {
    isRefreshing.value = false
  }
}

const createNewExercise = () => {
  router.push('/testing-exercises?action=create')
}

const openExercise = (exerciseId: string) => {
  router.push(`/simulation/exercise/${exerciseId}`)
}

const openMonitor = (exerciseId: string) => {
  router.push(`/simulation/exercise/${exerciseId}?tab=monitor`)
}

const openVNC = (exerciseId: string) => {
  window.open(`vnc://localhost:5900?exercise=${exerciseId}`, '_blank')
}

const getActivityIcon = (type: string) => {
  switch (type) {
    case 'exercise_started': return PlayIcon
    case 'exercise_completed': return CheckCircleIcon
    case 'exercise_paused': return PauseIcon
    case 'exercise_error': return ExclamationTriangleIcon
    default: return ClockIcon
  }
}

const formatDuration = (seconds: number) => {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)

  if (hours > 0) {
    return `${hours}h ${minutes}m`
  } else {
    return `${minutes}m`
  }
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
  await refreshDashboard()
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

.service-card {
  transition: all 0.2s ease-in-out;
}

.service-card:hover {
  transform: translateY(-2px);
}

.exercise-card {
  transition: all 0.2s ease-in-out;
}

.exercise-card:hover {
  transform: translateY(-2px);
}

.stat-item {
  transition: all 0.2s ease-in-out;
}

.stat-item:hover {
  transform: translateX(4px);
}

.activity-item {
  transition: all 0.2s ease-in-out;
}

.activity-item:hover {
  background-color: #f3f4f6;
}
</style>