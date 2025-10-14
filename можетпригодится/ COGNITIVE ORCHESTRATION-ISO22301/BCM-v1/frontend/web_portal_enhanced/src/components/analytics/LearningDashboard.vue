<template>
  <div class="learning-analytics-dashboard">
    <!-- Dashboard Header -->
    <div class="dashboard-header bg-white rounded-lg shadow-sm p-6 mb-6">
      <div class="flex justify-between items-center">
        <div>
          <h2 class="text-2xl font-bold text-gray-900 flex items-center">
            <i class="fas fa-brain text-blue-600 mr-3"></i>
            AI Learning Analytics
          </h2>
          <p class="text-gray-600 mt-1">Real-time insights and performance metrics</p>
        </div>
        <div class="flex items-center space-x-4">
          <span class="text-sm text-gray-500">
            Last updated: {{ lastUpdated || 'Never' }}
          </span>
          <button
            @click="refreshAnalytics"
            class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center"
            :disabled="isRefreshing"
          >
            <i class="fas fa-sync mr-2" :class="{ 'fa-spin': isRefreshing }"></i>
            {{ isRefreshing ? 'Refreshing...' : 'Refresh' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Key Metrics Overview -->
    <div class="metrics-overview grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <div class="metric-card bg-white rounded-lg shadow-sm p-6 border-l-4 border-blue-500">
        <div class="flex items-center">
          <div class="metric-icon w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mr-4">
            <i class="fas fa-file-text text-blue-600 text-xl"></i>
          </div>
          <div class="metric-content">
            <h3 class="text-2xl font-bold text-gray-900">{{ learningData.total_scenarios_with_data || 0 }}</h3>
            <p class="text-gray-600 text-sm">Scenarios with Learning Data</p>
          </div>
        </div>
      </div>

      <div class="metric-card bg-white rounded-lg shadow-sm p-6 border-l-4 border-green-500">
        <div class="flex items-center">
          <div class="metric-icon w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mr-4">
            <i class="fas fa-chart-line text-green-600 text-xl"></i>
          </div>
          <div class="metric-content">
            <h3 class="text-2xl font-bold text-gray-900">{{ learningData.avg_platform_effectiveness || 0 }}%</h3>
            <p class="text-gray-600 text-sm">Platform Effectiveness</p>
          </div>
        </div>
      </div>

      <div class="metric-card bg-white rounded-lg shadow-sm p-6 border-l-4 border-purple-500">
        <div class="flex items-center">
          <div class="metric-icon w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mr-4">
            <i class="fas fa-dumbbell text-purple-600 text-xl"></i>
          </div>
          <div class="metric-content">
            <h3 class="text-2xl font-bold text-gray-900">{{ learningData.total_exercises_completed || 0 }}</h3>
            <p class="text-gray-600 text-sm">Exercises Completed</p>
          </div>
        </div>
      </div>

      <div class="metric-card bg-white rounded-lg shadow-sm p-6 border-l-4 border-yellow-500">
        <div class="flex items-center">
          <div class="metric-icon w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center mr-4">
            <i class="fas fa-lightbulb text-yellow-600 text-xl"></i>
          </div>
          <div class="metric-content">
            <h3 class="text-2xl font-bold text-gray-900">{{ improvementRecommendations.length || 0 }}</h3>
            <p class="text-gray-600 text-sm">AI Recommendations</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Analytics Charts -->
    <div class="analytics-charts grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
      <!-- Effectiveness Trend Chart -->
      <div class="chart-card bg-white rounded-lg shadow-sm p-6">
        <div class="chart-header mb-4">
          <h5 class="text-lg font-semibold text-gray-900 flex items-center">
            <i class="fas fa-chart-line text-blue-600 mr-2"></i>
            Effectiveness Trend
          </h5>
        </div>
        <div class="chart-body">
          <Line
            v-if="effectivenessTrendData.datasets"
            :data="effectivenessTrendData"
            :options="chartOptions"
            class="w-full h-64"
          />
          <div v-else class="h-64 flex items-center justify-center text-gray-500">
            <div class="text-center">
              <i class="fas fa-chart-line text-4xl mb-2"></i>
              <p>Loading chart data...</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Scenario Performance Distribution -->
      <div class="chart-card bg-white rounded-lg shadow-sm p-6">
        <div class="chart-header mb-4">
          <h5 class="text-lg font-semibold text-gray-900 flex items-center">
            <i class="fas fa-pie-chart text-green-600 mr-2"></i>
            Scenario Performance
          </h5>
        </div>
        <div class="chart-body">
          <Doughnut
            v-if="scenarioPerformanceData.datasets"
            :data="scenarioPerformanceData"
            :options="doughnutOptions"
            class="w-full h-64"
          />
          <div v-else class="h-64 flex items-center justify-center text-gray-500">
            <div class="text-center">
              <i class="fas fa-pie-chart text-4xl mb-2"></i>
              <p>Loading chart data...</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Exercise Type Effectiveness -->
      <div class="chart-card bg-white rounded-lg shadow-sm p-6">
        <div class="chart-header mb-4">
          <h5 class="text-lg font-semibold text-gray-900 flex items-center">
            <i class="fas fa-bar-chart text-purple-600 mr-2"></i>
            Exercise Type Effectiveness
          </h5>
        </div>
        <div class="chart-body">
          <Bar
            v-if="exerciseTypeData.datasets"
            :data="exerciseTypeData"
            :options="chartOptions"
            class="w-full h-64"
          />
          <div v-else class="h-64 flex items-center justify-center text-gray-500">
            <div class="text-center">
              <i class="fas fa-bar-chart text-4xl mb-2"></i>
              <p>Loading chart data...</p>
            </div>
          </div>
        </div>
      </div>

      <!-- AI vs Manual Scenarios -->
      <div class="chart-card bg-white rounded-lg shadow-sm p-6">
        <div class="chart-header mb-4">
          <h5 class="text-lg font-semibold text-gray-900 flex items-center">
            <i class="fas fa-robot text-indigo-600 mr-2"></i>
            AI vs Manual Scenarios
          </h5>
        </div>
        <div class="chart-body">
          <Bar
            v-if="aiVsManualData.datasets"
            :data="aiVsManualData"
            :options="chartOptions"
            class="w-full h-64"
          />
          <div v-else class="h-64 flex items-center justify-center text-gray-500">
            <div class="text-center">
              <i class="fas fa-robot text-4xl mb-2"></i>
              <p>Loading chart data...</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Top Performing Scenarios -->
    <div class="top-scenarios-section bg-white rounded-lg shadow-sm p-6 mb-8">
      <div class="section-header flex justify-between items-center mb-6">
        <h4 class="text-xl font-semibold text-gray-900 flex items-center">
          <i class="fas fa-trophy text-yellow-500 mr-3"></i>
          Top Performing Scenarios
        </h4>
        <button
          @click="viewAllScenarios"
          class="text-blue-600 hover:text-blue-800 flex items-center text-sm font-medium"
        >
          View All Scenarios
          <i class="fas fa-arrow-right ml-1"></i>
        </button>
      </div>

      <div class="scenarios-grid grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div
          v-for="scenario in topScenarios"
          :key="scenario.id"
          class="scenario-performance-card bg-gray-50 rounded-lg p-4 hover:shadow-md transition-shadow"
        >
          <div class="card-header mb-3">
            <h6 class="font-semibold text-gray-900 text-sm mb-2">{{ scenario.title }}</h6>
            <div class="performance-badges flex flex-wrap gap-2">
              <span class="badge bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full">
                {{ scenario.avg_rating }}/10 Rating
              </span>
              <span class="badge bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full">
                {{ scenario.exercise_count }} Uses
              </span>
              <span
                v-if="scenario.ai_generated"
                class="badge bg-purple-100 text-purple-800 text-xs px-2 py-1 rounded-full"
              >
                <i class="fas fa-robot mr-1"></i>AI
              </span>
            </div>
          </div>

          <div class="card-body mb-3">
            <div class="performance-metrics space-y-2">
              <div class="metric-row flex justify-between text-sm">
                <span class="text-gray-600">Category:</span>
                <span class="font-medium">{{ scenario.category }}</span>
              </div>
              <div class="metric-row">
                <span class="text-gray-600 text-sm">Effectiveness:</span>
                <div class="effectiveness-bar mt-1">
                  <div class="progress bg-gray-200 rounded-full h-2">
                    <div
                      class="progress-bar bg-green-500 h-2 rounded-full transition-all duration-300"
                      :style="{ width: scenario.effectiveness + '%' }"
                    ></div>
                  </div>
                  <span class="text-sm font-medium text-gray-700">{{ scenario.effectiveness }}%</span>
                </div>
              </div>
            </div>
          </div>

          <div class="card-footer flex gap-2">
            <button
              @click="viewScenarioInsights(scenario.id)"
              class="flex-1 bg-blue-50 text-blue-600 text-xs px-3 py-2 rounded hover:bg-blue-100 transition-colors"
            >
              <i class="fas fa-chart-line mr-1"></i>Insights
            </button>
            <button
              @click="createExercise(scenario.id)"
              class="flex-1 bg-green-50 text-green-600 text-xs px-3 py-2 rounded hover:bg-green-100 transition-colors"
            >
              <i class="fas fa-play mr-1"></i>Exercise
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- AI Recommendations Panel -->
    <div class="ai-recommendations-section bg-white rounded-lg shadow-sm p-6">
      <div class="section-header mb-6">
        <h4 class="text-xl font-semibold text-gray-900 flex items-center">
          <i class="fas fa-lightbulb text-yellow-500 mr-3"></i>
          AI Improvement Recommendations
        </h4>
      </div>

      <div class="recommendations-list space-y-4">
        <div
          v-for="recommendation in improvementRecommendations"
          :key="recommendation.id"
          class="recommendation-card border border-gray-200 rounded-lg p-4 hover:shadow-sm transition-shadow"
        >
          <div class="recommendation-header flex justify-between items-start mb-3">
            <div class="rec-type flex items-center">
              <i
                :class="getRecommendationIcon(recommendation.type)"
                class="text-blue-600 mr-2"
              ></i>
              <span class="font-medium text-gray-900">{{ recommendation.type }}</span>
            </div>
            <div
              class="rec-priority px-2 py-1 rounded text-xs font-medium"
              :class="getPriorityClass(recommendation.priority)"
            >
              {{ recommendation.priority }}
            </div>
          </div>

          <div class="recommendation-body mb-4">
            <h6 class="font-semibold text-gray-900 mb-2">{{ recommendation.title }}</h6>
            <p class="text-gray-600 text-sm mb-3">{{ recommendation.description }}</p>
            <div class="rec-details flex gap-4 text-sm text-gray-500">
              <span class="confidence flex items-center">
                <i class="fas fa-percentage mr-1"></i>
                {{ recommendation.confidence }}% Confidence
              </span>
              <span class="impact flex items-center">
                <i class="fas fa-arrow-up mr-1"></i>
                {{ recommendation.expected_impact }}% Expected Improvement
              </span>
            </div>
          </div>

          <div class="recommendation-actions flex gap-2">
            <button
              @click="implementRecommendation(recommendation.id)"
              class="bg-green-600 text-white text-sm px-3 py-2 rounded hover:bg-green-700 transition-colors"
            >
              <i class="fas fa-check mr-1"></i>Implement
            </button>
            <button
              @click="viewRecommendationDetails(recommendation.id)"
              class="bg-gray-100 text-gray-700 text-sm px-3 py-2 rounded hover:bg-gray-200 transition-colors"
            >
              <i class="fas fa-info-circle mr-1"></i>Details
            </button>
          </div>
        </div>
      </div>

      <div v-if="improvementRecommendations.length === 0" class="text-center py-8 text-gray-500">
        <i class="fas fa-lightbulb text-4xl mb-3"></i>
        <p>No recommendations available yet.</p>
        <p class="text-sm">Complete more exercises to generate AI insights.</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { Line, Doughnut, Bar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  BarElement
} from 'chart.js'
import { useToast } from 'vue-toastification'

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  BarElement
)

// Reactive data
const learningData = ref<any>({})
const topScenarios = ref<any[]>([])
const improvementRecommendations = ref<any[]>([])
const isRefreshing = ref(false)
const lastUpdated = ref<string | null>(null)
const ws = ref<WebSocket | null>(null)
const toast = useToast()

// Chart data
const effectivenessTrendData = ref<any>({})
const scenarioPerformanceData = ref<any>({})
const exerciseTypeData = ref<any>({})
const aiVsManualData = ref<any>({})

// Chart options
const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom' as const
    }
  },
  scales: {
    y: {
      beginAtZero: true
    }
  }
}

const doughnutOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom' as const
    }
  }
}

// Methods
const loadAnalytics = async () => {
  try {
    // Load learning data from Scenario Orchestrator
    const response = await fetch('http://localhost:8085/learning/dashboard')

    if (response.ok) {
      const data = await response.json()
      learningData.value = data.dashboard || {}

      // Load top scenarios
      topScenarios.value = learningData.value.top_performing_scenarios || []

      // Load improvement recommendations
      await loadImprovementRecommendations()

      // Update charts
      updateChartData()

      lastUpdated.value = new Date().toLocaleString()
    } else {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }
  } catch (error: any) {
    console.error('Failed to load learning analytics:', error)
    toast.error('Failed to load learning analytics: ' + error.message)

    // Load fallback data
    loadFallbackData()
  }
}

const loadImprovementRecommendations = async () => {
  try {
    const response = await fetch('http://localhost:8085/learning/recommendations')

    if (response.ok) {
      const recommendations = await response.json()
      improvementRecommendations.value = recommendations || []
    } else {
      // Generate fallback recommendations
      generateFallbackRecommendations()
    }
  } catch (error) {
    generateFallbackRecommendations()
  }
}

const loadFallbackData = () => {
  // Provide fallback data when backend is not available
  learningData.value = {
    total_scenarios_with_data: 15,
    avg_platform_effectiveness: 78,
    total_exercises_completed: 45
  }

  topScenarios.value = [
    {
      id: 1,
      title: "Critical System Failure Response",
      avg_rating: 8.5,
      exercise_count: 12,
      ai_generated: true,
      category: "IT Disaster",
      effectiveness: 85
    },
    {
      id: 2,
      title: "Supply Chain Disruption",
      avg_rating: 7.8,
      exercise_count: 8,
      ai_generated: false,
      category: "Business Continuity",
      effectiveness: 78
    }
  ]

  generateFallbackRecommendations()
  updateChartData()
  lastUpdated.value = new Date().toLocaleString()
}

const generateFallbackRecommendations = () => {
  improvementRecommendations.value = [
    {
      id: 'rec_001',
      type: 'Exercise Completion',
      priority: 'High',
      title: 'Improve Exercise Completion Rate',
      description: 'Current completion rate is below target. Consider reviewing exercise complexity and providing better guidance.',
      confidence: 85,
      expected_impact: 15
    },
    {
      id: 'rec_002',
      type: 'AI Enhancement',
      priority: 'Medium',
      title: 'Increase AI-Generated Scenarios',
      description: 'Consider using AI to generate more diverse scenarios for better coverage.',
      confidence: 75,
      expected_impact: 20
    }
  ]
}

const updateChartData = () => {
  // Effectiveness Trend Chart
  effectivenessTrendData.value = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    datasets: [{
      label: 'Platform Effectiveness',
      data: [65, 70, 75, 72, 78, 80],
      borderColor: 'rgb(59, 130, 246)',
      backgroundColor: 'rgba(59, 130, 246, 0.1)',
      tension: 0.4
    }]
  }

  // Scenario Performance Distribution
  scenarioPerformanceData.value = {
    labels: ['High (>80%)', 'Medium (60-80%)', 'Low (<60%)'],
    datasets: [{
      data: [12, 8, 3],
      backgroundColor: ['#10B981', '#F59E0B', '#EF4444']
    }]
  }

  // Exercise Type Effectiveness
  exerciseTypeData.value = {
    labels: ['Tabletop', 'Simulation', 'Full Scale', 'Walkthrough'],
    datasets: [{
      label: 'Effectiveness %',
      data: [75, 82, 88, 70],
      backgroundColor: 'rgba(147, 51, 234, 0.8)'
    }]
  }

  // AI vs Manual Scenarios
  aiVsManualData.value = {
    labels: ['AI Generated', 'Manual Created'],
    datasets: [{
      label: 'Count',
      data: [15, 25],
      backgroundColor: ['rgba(99, 102, 241, 0.8)', 'rgba(107, 114, 128, 0.8)']
    }]
  }
}

const refreshAnalytics = async () => {
  isRefreshing.value = true
  await loadAnalytics()
  isRefreshing.value = false
  toast.success('Analytics refreshed successfully')
}

const setupRealTimeUpdates = () => {
  // WebSocket for real-time learning updates
  if (ws.value) {
    ws.value.close()
  }

  try {
    ws.value = new WebSocket('ws://localhost:8085/ws/learning-updates')

    ws.value.onmessage = (event) => {
      const data = JSON.parse(event.data)

      if (data.type === 'learning_update') {
        // Update specific scenario data
        updateScenarioLearning(data.scenario_id, data.learning_data)
      } else if (data.type === 'new_recommendation') {
        // Add new AI recommendation
        improvementRecommendations.value.unshift(data.recommendation)
        toast.info('New AI recommendation available')
      }
    }

    ws.value.onerror = () => {
      console.warn('WebSocket connection failed - continuing without real-time updates')
    }
  } catch (error) {
    console.warn('WebSocket not available - continuing without real-time updates')
  }
}

const updateScenarioLearning = (scenarioId: string, learningData: any) => {
  const scenarioIndex = topScenarios.value.findIndex(s => s.id === scenarioId)
  if (scenarioIndex !== -1) {
    topScenarios.value[scenarioIndex] = { ...topScenarios.value[scenarioIndex], ...learningData }
  }
}

const getRecommendationIcon = (type: string) => {
  const icons: Record<string, string> = {
    'Exercise Completion': 'fas fa-tasks',
    'AI Enhancement': 'fas fa-robot',
    'Performance': 'fas fa-chart-line',
    'Training': 'fas fa-graduation-cap'
  }
  return icons[type] || 'fas fa-lightbulb'
}

const getPriorityClass = (priority: string) => {
  const classes: Record<string, string> = {
    'High': 'bg-red-100 text-red-800',
    'Medium': 'bg-yellow-100 text-yellow-800',
    'Low': 'bg-green-100 text-green-800'
  }
  return classes[priority] || 'bg-gray-100 text-gray-800'
}

// Action methods
const viewAllScenarios = () => {
  // Navigate to scenarios page
  console.log('Navigate to all scenarios')
}

const viewScenarioInsights = (scenarioId: string) => {
  console.log('View insights for scenario:', scenarioId)
}

const createExercise = (scenarioId: string) => {
  console.log('Create exercise for scenario:', scenarioId)
}

const implementRecommendation = (recommendationId: string) => {
  console.log('Implement recommendation:', recommendationId)
}

const viewRecommendationDetails = (recommendationId: string) => {
  console.log('View recommendation details:', recommendationId)
}

// Lifecycle
onMounted(async () => {
  await loadAnalytics()
  setupRealTimeUpdates()
})

onUnmounted(() => {
  if (ws.value) {
    ws.value.close()
  }
})
</script>

<style scoped>
.learning-analytics-dashboard {
  @apply p-6 bg-gray-50 min-h-screen;
}

.metric-card {
  @apply transition-transform hover:scale-105;
}

.chart-card {
  @apply transition-shadow hover:shadow-lg;
}

.scenario-performance-card {
  @apply transition-all hover:bg-gray-100;
}

.recommendation-card {
  @apply transition-all hover:border-blue-200;
}

.progress {
  @apply overflow-hidden;
}

.progress-bar {
  @apply transition-all duration-500 ease-out;
}
</style>