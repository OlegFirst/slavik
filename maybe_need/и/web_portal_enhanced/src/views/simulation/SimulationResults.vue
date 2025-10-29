<template>
  <div class="simulation-results">
    <!-- Page Header -->
    <div class="page-header mb-8">
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
            <h1 class="text-3xl font-bold text-gray-900">Simulation Results</h1>
            <p class="text-gray-600 mt-1">
              {{ exerciseData?.name || 'Loading...' }} - {{ formatDateTime(exerciseData?.completed_at) }}
            </p>
          </div>
        </div>

        <div class="header-actions flex items-center space-x-3">
          <button
            @click="shareResults"
            class="btn btn-outline flex items-center space-x-2"
          >
            <ShareIcon class="w-4 h-4" />
            <span>Share</span>
          </button>

          <button
            @click="exportResults"
            class="btn btn-outline flex items-center space-x-2"
          >
            <ArrowDownTrayIcon class="w-4 h-4" />
            <span>Export</span>
          </button>

          <button
            @click="generateReport"
            class="btn btn-primary flex items-center space-x-2"
          >
            <DocumentTextIcon class="w-4 h-4" />
            <span>Generate Report</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Results Overview -->
    <div class="results-overview bg-white rounded-lg shadow-sm p-6 mb-8">
      <h2 class="text-xl font-semibold text-gray-900 mb-6">Exercise Overview</h2>

      <div class="overview-grid grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div class="overview-card bg-blue-50 p-6 rounded-lg">
          <div class="flex items-center justify-between">
            <div>
              <div class="text-3xl font-bold text-blue-600">{{ overview.duration }}</div>
              <div class="text-sm text-gray-600 mt-1">Total Duration</div>
            </div>
            <ClockIcon class="w-12 h-12 text-blue-500 opacity-20" />
          </div>
        </div>

        <div class="overview-card bg-green-50 p-6 rounded-lg">
          <div class="flex items-center justify-between">
            <div>
              <div class="text-3xl font-bold text-green-600">{{ overview.completionRate }}%</div>
              <div class="text-sm text-gray-600 mt-1">Completion Rate</div>
            </div>
            <CheckCircleIcon class="w-12 h-12 text-green-500 opacity-20" />
          </div>
        </div>

        <div class="overview-card bg-yellow-50 p-6 rounded-lg">
          <div class="flex items-center justify-between">
            <div>
              <div class="text-3xl font-bold text-yellow-600">{{ overview.participants }}</div>
              <div class="text-sm text-gray-600 mt-1">Participants</div>
            </div>
            <UsersIcon class="w-12 h-12 text-yellow-500 opacity-20" />
          </div>
        </div>

        <div class="overview-card bg-purple-50 p-6 rounded-lg">
          <div class="flex items-center justify-between">
            <div>
              <div class="text-3xl font-bold text-purple-600">{{ overview.effectivenessScore }}</div>
              <div class="text-sm text-gray-600 mt-1">Effectiveness Score</div>
            </div>
            <StarIcon class="w-12 h-12 text-purple-500 opacity-20" />
          </div>
        </div>
      </div>
    </div>

    <!-- Results Navigation -->
    <div class="results-tabs mb-8">
      <div class="border-b border-gray-200">
        <nav class="flex space-x-8">
          <button
            v-for="tab in resultTabs"
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
      <!-- Summary Tab -->
      <div v-if="activeTab === 'summary'" class="summary-tab space-y-8">
        <!-- Performance Summary -->
        <div class="performance-summary bg-white rounded-lg shadow-sm p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Performance Summary</h3>
          <SimulationSummaryChart :data="summaryData" />
        </div>

        <!-- Key Achievements -->
        <div class="achievements bg-white rounded-lg shadow-sm p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Key Achievements</h3>

          <div class="achievements-grid grid grid-cols-1 md:grid-cols-2 gap-6">
            <div
              v-for="achievement in achievements"
              :key="achievement.id"
              class="achievement-card p-4 border rounded-lg"
              :class="{
                'border-green-200 bg-green-50': achievement.status === 'completed',
                'border-yellow-200 bg-yellow-50': achievement.status === 'partial',
                'border-red-200 bg-red-50': achievement.status === 'missed'
              }"
            >
              <div class="flex items-center justify-between mb-2">
                <h4 class="font-medium text-gray-900">{{ achievement.title }}</h4>
                <component
                  :is="achievement.status === 'completed' ? CheckCircleIcon : achievement.status === 'partial' ? ExclamationTriangleIcon : XCircleIcon"
                  class="w-5 h-5"
                  :class="{
                    'text-green-500': achievement.status === 'completed',
                    'text-yellow-500': achievement.status === 'partial',
                    'text-red-500': achievement.status === 'missed'
                  }"
                />
              </div>

              <p class="text-sm text-gray-600 mb-3">{{ achievement.description }}</p>

              <div class="progress-bar bg-gray-200 rounded-full h-2">
                <div
                  class="progress-fill h-2 rounded-full transition-all duration-500"
                  :class="{
                    'bg-green-500': achievement.status === 'completed',
                    'bg-yellow-500': achievement.status === 'partial',
                    'bg-red-500': achievement.status === 'missed'
                  }"
                  :style="{ width: `${achievement.progress}%` }"
                ></div>
              </div>

              <div class="flex items-center justify-between mt-2 text-xs text-gray-500">
                <span>{{ achievement.progress }}% complete</span>
                <span>{{ achievement.points }} points</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Recommendations -->
        <div class="recommendations bg-white rounded-lg shadow-sm p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Recommendations</h3>

          <div class="recommendations-list space-y-4">
            <div
              v-for="recommendation in recommendations"
              :key="recommendation.id"
              class="recommendation-item p-4 bg-blue-50 border border-blue-200 rounded-lg"
            >
              <div class="flex items-start space-x-3">
                <div
                  class="recommendation-icon w-8 h-8 rounded-full flex items-center justify-center"
                  :class="{
                    'bg-green-100': recommendation.priority === 'low',
                    'bg-yellow-100': recommendation.priority === 'medium',
                    'bg-red-100': recommendation.priority === 'high'
                  }"
                >
                  <component
                    :is="recommendation.priority === 'high' ? ExclamationTriangleIcon : LightBulbIcon"
                    class="w-4 h-4"
                    :class="{
                      'text-green-600': recommendation.priority === 'low',
                      'text-yellow-600': recommendation.priority === 'medium',
                      'text-red-600': recommendation.priority === 'high'
                    }"
                  />
                </div>

                <div class="flex-1">
                  <div class="flex items-center justify-between mb-1">
                    <h4 class="font-medium text-gray-900">{{ recommendation.title }}</h4>
                    <span
                      class="priority-badge px-2 py-1 rounded-full text-xs font-medium"
                      :class="{
                        'bg-green-100 text-green-800': recommendation.priority === 'low',
                        'bg-yellow-100 text-yellow-800': recommendation.priority === 'medium',
                        'bg-red-100 text-red-800': recommendation.priority === 'high'
                      }"
                    >
                      {{ recommendation.priority }} priority
                    </span>
                  </div>
                  <p class="text-sm text-gray-600">{{ recommendation.description }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Metrics Tab -->
      <div v-if="activeTab === 'metrics'" class="metrics-tab">
        <div class="metrics-analysis bg-white rounded-lg shadow-sm p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Detailed Metrics Analysis</h3>
          <SimulationMetricsTable :data="metricsData" />
        </div>
      </div>

      <!-- Participants Tab -->
      <div v-if="activeTab === 'participants'" class="participants-tab space-y-8">
        <!-- Participant Performance -->
        <div class="participant-performance bg-white rounded-lg shadow-sm p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Participant Performance</h3>

          <div class="participants-table overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Participant
                  </th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Role
                  </th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Completion
                  </th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Score
                  </th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Response Time
                  </th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr
                  v-for="participant in participantResults"
                  :key="participant.id"
                  class="hover:bg-gray-50"
                >
                  <td class="px-4 py-3">
                    <div class="flex items-center">
                      <div class="flex-shrink-0 h-8 w-8">
                        <div class="h-8 w-8 rounded-full bg-gray-300 flex items-center justify-center">
                          <span class="text-xs font-medium text-gray-700">
                            {{ participant.name.charAt(0).toUpperCase() }}
                          </span>
                        </div>
                      </div>
                      <div class="ml-3">
                        <div class="text-sm font-medium text-gray-900">{{ participant.name }}</div>
                        <div class="text-sm text-gray-500">{{ participant.email }}</div>
                      </div>
                    </div>
                  </td>
                  <td class="px-4 py-3 text-sm text-gray-900">{{ participant.role }}</td>
                  <td class="px-4 py-3">
                    <div class="flex items-center">
                      <div class="w-16 bg-gray-200 rounded-full h-2 mr-2">
                        <div
                          class="bg-blue-500 h-2 rounded-full"
                          :style="{ width: `${participant.completion}%` }"
                        ></div>
                      </div>
                      <span class="text-sm text-gray-600">{{ participant.completion }}%</span>
                    </div>
                  </td>
                  <td class="px-4 py-3">
                    <span
                      class="inline-flex px-2 py-1 text-xs font-semibold rounded-full"
                      :class="{
                        'bg-green-100 text-green-800': participant.score >= 80,
                        'bg-yellow-100 text-yellow-800': participant.score >= 60 && participant.score < 80,
                        'bg-red-100 text-red-800': participant.score < 60
                      }"
                    >
                      {{ participant.score }}/100
                    </span>
                  </td>
                  <td class="px-4 py-3 text-sm text-gray-900">{{ participant.avgResponseTime }}ms</td>
                  <td class="px-4 py-3">
                    <button
                      @click="viewParticipantDetails(participant.id)"
                      class="text-blue-600 hover:text-blue-800"
                    >
                      View Details
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Team Performance -->
        <div class="team-performance bg-white rounded-lg shadow-sm p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Team Performance Analysis</h3>

          <div class="team-stats grid grid-cols-1 md:grid-cols-3 gap-6">
            <div class="team-stat bg-blue-50 p-4 rounded-lg">
              <h4 class="font-medium text-blue-900 mb-2">Communication</h4>
              <div class="text-2xl font-bold text-blue-600 mb-1">{{ teamStats.communication }}%</div>
              <p class="text-sm text-blue-700">Effective communication rate</p>
            </div>

            <div class="team-stat bg-green-50 p-4 rounded-lg">
              <h4 class="font-medium text-green-900 mb-2">Collaboration</h4>
              <div class="text-2xl font-bold text-green-600 mb-1">{{ teamStats.collaboration }}%</div>
              <p class="text-sm text-green-700">Team collaboration score</p>
            </div>

            <div class="team-stat bg-purple-50 p-4 rounded-lg">
              <h4 class="font-medium text-purple-900 mb-2">Decision Making</h4>
              <div class="text-2xl font-bold text-purple-600 mb-1">{{ teamStats.decisionMaking }}%</div>
              <p class="text-sm text-purple-700">Decision making efficiency</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Learning Tab -->
      <div v-if="activeTab === 'learning'" class="learning-tab space-y-8">
        <!-- Learning Objectives -->
        <div class="learning-objectives bg-white rounded-lg shadow-sm p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Learning Objectives Assessment</h3>

          <div class="objectives-list space-y-4">
            <div
              v-for="objective in learningObjectives"
              :key="objective.id"
              class="objective-item p-4 border rounded-lg"
            >
              <div class="flex items-center justify-between mb-2">
                <h4 class="font-medium text-gray-900">{{ objective.title }}</h4>
                <span
                  class="achievement-badge px-2 py-1 rounded-full text-xs font-medium"
                  :class="{
                    'bg-green-100 text-green-800': objective.achievement >= 80,
                    'bg-yellow-100 text-yellow-800': objective.achievement >= 60,
                    'bg-red-100 text-red-800': objective.achievement < 60
                  }"
                >
                  {{ objective.achievement }}% achieved
                </span>
              </div>

              <p class="text-sm text-gray-600 mb-3">{{ objective.description }}</p>

              <div class="progress-bar bg-gray-200 rounded-full h-2 mb-2">
                <div
                  class="progress-fill h-2 rounded-full transition-all duration-500"
                  :class="{
                    'bg-green-500': objective.achievement >= 80,
                    'bg-yellow-500': objective.achievement >= 60,
                    'bg-red-500': objective.achievement < 60
                  }"
                  :style="{ width: `${objective.achievement}%` }"
                ></div>
              </div>

              <div class="objective-details text-xs text-gray-500">
                <span>Target: {{ objective.target }}% | </span>
                <span>Actual: {{ objective.achievement }}%</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Skill Development -->
        <div class="skill-development bg-white rounded-lg shadow-sm p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Skill Development Areas</h3>

          <div class="skills-grid grid grid-cols-1 md:grid-cols-2 gap-6">
            <div
              v-for="skill in skillDevelopment"
              :key="skill.name"
              class="skill-item"
            >
              <div class="flex items-center justify-between mb-2">
                <h4 class="font-medium text-gray-900">{{ skill.name }}</h4>
                <span class="text-sm text-gray-600">{{ skill.level }}/5</span>
              </div>

              <div class="skill-progress bg-gray-200 rounded-full h-3 mb-2">
                <div
                  class="skill-fill h-3 rounded-full transition-all duration-500"
                  :class="{
                    'bg-red-500': skill.level <= 2,
                    'bg-yellow-500': skill.level === 3,
                    'bg-green-500': skill.level >= 4
                  }"
                  :style="{ width: `${(skill.level / 5) * 100}%` }"
                ></div>
              </div>

              <p class="text-sm text-gray-600">{{ skill.feedback }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Raw Data Tab -->
      <div v-if="activeTab === 'raw'" class="raw-data-tab">
        <div class="raw-data-container bg-white rounded-lg shadow-sm p-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-semibold text-gray-900">Raw Simulation Data</h3>

            <div class="data-controls flex items-center space-x-2">
              <button
                @click="downloadRawData"
                class="btn btn-outline btn-sm flex items-center space-x-1"
              >
                <ArrowDownTrayIcon class="w-3 h-3" />
                <span>Download JSON</span>
              </button>

              <button
                @click="downloadCSV"
                class="btn btn-outline btn-sm flex items-center space-x-1"
              >
                <DocumentTextIcon class="w-3 h-3" />
                <span>Download CSV</span>
              </button>
            </div>
          </div>

          <div class="raw-data-viewer bg-gray-900 text-green-400 p-4 rounded-lg font-mono text-sm overflow-x-auto max-h-96 overflow-y-auto">
            <pre>{{ JSON.stringify(rawData, null, 2) }}</pre>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import {
  ArrowLeftIcon,
  ShareIcon,
  ArrowDownTrayIcon,
  DocumentTextIcon,
  ClockIcon,
  CheckCircleIcon,
  UsersIcon,
  StarIcon,
  ChartBarIcon,
  UserGroupIcon,
  AcademicCapIcon,
  CodeBracketIcon,
  ExclamationTriangleIcon,
  XCircleIcon,
  LightBulbIcon
} from '@heroicons/vue/24/outline'
import { useToast } from 'vue-toastification'
import { simulationService } from '@/services/simulationService'
import SimulationSummaryChart from '@/components/simulation/SimulationSummaryChart.vue'
import SimulationMetricsTable from '@/components/simulation/SimulationMetricsTable.vue'

interface Props {
  exerciseId: string
}

const props = defineProps<Props>()
const toast = useToast()

// Reactive state
const activeTab = ref('summary')
const exerciseData = ref(null)

// Mock data (in real implementation, this would come from the simulation service)
const overview = ref({
  duration: '2h 34m',
  completionRate: 94,
  participants: 12,
  effectivenessScore: 87
})

const summaryData = ref({
  totalEvents: 15420,
  totalDuration: 9240,
  completionRate: 94,
  efficiency: 87
})

const metricsData = ref([])

const achievements = ref([
  {
    id: 'obj-1',
    title: 'Crisis Response Time',
    description: 'Respond to initial crisis notification within 15 minutes',
    status: 'completed',
    progress: 100,
    points: 25
  },
  {
    id: 'obj-2',
    title: 'Team Coordination',
    description: 'Establish effective communication channels between all teams',
    status: 'partial',
    progress: 75,
    points: 18
  },
  {
    id: 'obj-3',
    title: 'Recovery Procedures',
    description: 'Execute recovery procedures according to BCP guidelines',
    status: 'completed',
    progress: 100,
    points: 30
  }
])

const recommendations = ref([
  {
    id: 'rec-1',
    title: 'Improve Initial Response Time',
    description: 'Consider implementing automated alert systems to reduce manual notification delays',
    priority: 'high'
  },
  {
    id: 'rec-2',
    title: 'Enhance Team Communication',
    description: 'Regular communication drills would improve coordination effectiveness',
    priority: 'medium'
  },
  {
    id: 'rec-3',
    title: 'Update Documentation',
    description: 'Some procedure documents need updating based on exercise findings',
    priority: 'low'
  }
])

const participantResults = ref([
  {
    id: 'p-1',
    name: 'John Smith',
    email: 'john.smith@company.com',
    role: 'Incident Commander',
    completion: 95,
    score: 87,
    avgResponseTime: 245
  },
  {
    id: 'p-2',
    name: 'Sarah Johnson',
    email: 'sarah.johnson@company.com',
    role: 'Communications Lead',
    completion: 98,
    score: 92,
    avgResponseTime: 189
  }
])

const teamStats = ref({
  communication: 85,
  collaboration: 78,
  decisionMaking: 91
})

const learningObjectives = ref([
  {
    id: 'lo-1',
    title: 'Crisis Management Procedures',
    description: 'Demonstrate understanding of crisis management protocols',
    target: 80,
    achievement: 87
  },
  {
    id: 'lo-2',
    title: 'Emergency Communication',
    description: 'Effectively use emergency communication systems',
    target: 85,
    achievement: 92
  }
])

const skillDevelopment = ref([
  {
    name: 'Leadership',
    level: 4,
    feedback: 'Strong leadership skills demonstrated throughout the exercise'
  },
  {
    name: 'Decision Making',
    level: 3,
    feedback: 'Good decision making, but could benefit from faster responses'
  },
  {
    name: 'Communication',
    level: 5,
    feedback: 'Excellent communication skills and clarity'
  }
])

const rawData = ref({
  exercise_id: props.exerciseId,
  simulation_data: {
    events: [],
    metrics: [],
    participant_actions: []
  }
})

const resultTabs = [
  { id: 'summary', label: 'Summary', icon: ChartBarIcon },
  { id: 'metrics', label: 'Metrics', icon: ChartBarIcon },
  { id: 'participants', label: 'Participants', icon: UserGroupIcon },
  { id: 'learning', label: 'Learning', icon: AcademicCapIcon },
  { id: 'raw', label: 'Raw Data', icon: CodeBracketIcon }
]

// Methods
const loadResultsData = async () => {
  try {
    const [exercise, results, metrics] = await Promise.all([
      simulationService.getExerciseDetails(props.exerciseId),
      simulationService.getSimulationResults(props.exerciseId),
      simulationService.getMetricsData(props.exerciseId)
    ])

    exerciseData.value = exercise
    if (results) {
      summaryData.value = results.summary
      rawData.value = results.raw
    }
    metricsData.value = metrics
  } catch (error) {
    console.error('Error loading results data:', error)
    toast.error('Failed to load simulation results')
  }
}

const shareResults = () => {
  const url = window.location.href
  navigator.clipboard.writeText(url)
  toast.success('Results URL copied to clipboard')
}

const exportResults = async () => {
  try {
    const data = await simulationService.exportExerciseData(props.exerciseId)
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)

    const a = document.createElement('a')
    a.href = url
    a.download = `simulation-results-${props.exerciseId}.json`
    a.click()

    URL.revokeObjectURL(url)
    toast.success('Results exported successfully')
  } catch (error) {
    toast.error('Failed to export results')
  }
}

const generateReport = async () => {
  try {
    const report = await simulationService.generateDetailedReport(props.exerciseId)
    const blob = new Blob([report], { type: 'application/pdf' })
    const url = URL.createObjectURL(blob)

    const a = document.createElement('a')
    a.href = url
    a.download = `simulation-report-${props.exerciseId}.pdf`
    a.click()

    URL.revokeObjectURL(url)
    toast.success('Report generated successfully')
  } catch (error) {
    toast.error('Failed to generate report')
  }
}

const viewParticipantDetails = (participantId: string) => {
  // Open participant details modal
  toast.info('Participant details feature coming soon')
}

const downloadRawData = () => {
  const blob = new Blob([JSON.stringify(rawData.value, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)

  const a = document.createElement('a')
  a.href = url
  a.download = `raw-data-${props.exerciseId}.json`
  a.click()

  URL.revokeObjectURL(url)
}

const downloadCSV = async () => {
  try {
    const csv = await simulationService.exportResultsToCSV(rawData.value)
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)

    const a = document.createElement('a')
    a.href = url
    a.download = `simulation-data-${props.exerciseId}.csv`
    a.click()

    URL.revokeObjectURL(url)
  } catch (error) {
    toast.error('Failed to export CSV')
  }
}

const formatDateTime = (timestamp: string) => {
  if (!timestamp) return ''
  return new Date(timestamp).toLocaleString()
}

// Lifecycle
onMounted(async () => {
  await loadResultsData()
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

.overview-card {
  transition: transform 0.2s ease-in-out;
}

.overview-card:hover {
  transform: translateY(-2px);
}

.achievement-card {
  transition: all 0.2s ease-in-out;
}

.achievement-card:hover {
  transform: translateX(4px);
}

.recommendation-item {
  transition: all 0.2s ease-in-out;
}

.recommendation-item:hover {
  transform: translateX(2px);
}

.raw-data-viewer {
  scrollbar-width: thin;
  scrollbar-color: #4ade80 #1f2937;
}

.raw-data-viewer::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

.raw-data-viewer::-webkit-scrollbar-track {
  background: #1f2937;
}

.raw-data-viewer::-webkit-scrollbar-thumb {
  background: #4ade80;
  border-radius: 4px;
}
</style>