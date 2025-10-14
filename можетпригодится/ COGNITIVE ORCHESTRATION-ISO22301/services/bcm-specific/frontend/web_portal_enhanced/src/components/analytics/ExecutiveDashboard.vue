<template>
  <div class="executive-dashboard">
    <!-- Executive Summary Cards -->
    <div class="summary-cards grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <div class="summary-card bg-white rounded-lg shadow-sm p-6 border-l-4 border-blue-500">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Total Scenarios</p>
            <p class="text-3xl font-bold text-gray-900">{{ metrics.total_scenarios || 0 }}</p>
          </div>
          <div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
            <i class="fas fa-file-text text-blue-600 text-xl"></i>
          </div>
        </div>
        <div class="mt-4">
          <span class="text-xs text-gray-500">{{ metrics.ai_generated_scenarios || 0 }} AI Generated</span>
        </div>
      </div>

      <div class="summary-card bg-white rounded-lg shadow-sm p-6 border-l-4 border-green-500">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Total Exercises</p>
            <p class="text-3xl font-bold text-gray-900">{{ metrics.total_exercises || 0 }}</p>
          </div>
          <div class="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
            <i class="fas fa-dumbbell text-green-600 text-xl"></i>
          </div>
        </div>
        <div class="mt-4">
          <span class="text-xs text-gray-500">{{ metrics.total_exercises_completed || 0 }} Completed</span>
        </div>
      </div>

      <div class="summary-card bg-white rounded-lg shadow-sm p-6 border-l-4 border-purple-500">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Platform Effectiveness</p>
            <p class="text-3xl font-bold text-gray-900">{{ metrics.platform_effectiveness || 0 }}%</p>
          </div>
          <div class="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
            <i class="fas fa-chart-line text-purple-600 text-xl"></i>
          </div>
        </div>
        <div class="mt-4">
          <div class="flex items-center">
            <i class="fas fa-arrow-up text-green-500 text-xs mr-1"></i>
            <span class="text-xs text-green-600">+5.2% from last month</span>
          </div>
        </div>
      </div>

      <div class="summary-card bg-white rounded-lg shadow-sm p-6 border-l-4 border-yellow-500">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Risk Coverage</p>
            <p class="text-3xl font-bold text-gray-900">{{ riskCoverage }}%</p>
          </div>
          <div class="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center">
            <i class="fas fa-shield-alt text-yellow-600 text-xl"></i>
          </div>
        </div>
        <div class="mt-4">
          <span class="text-xs text-gray-500">{{ coveredRisks }} of {{ totalRisks }} risks covered</span>
        </div>
      </div>
    </div>

    <!-- Charts Row 1 -->
    <div class="charts-row-1 grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
      <!-- Platform Performance Trend -->
      <div class="chart-card bg-white rounded-lg shadow-sm p-6">
        <div class="chart-header flex justify-between items-center mb-4">
          <h3 class="text-lg font-semibold text-gray-900">Platform Performance Trend</h3>
          <div class="chart-controls">
            <select v-model="performancePeriod" class="text-sm border rounded px-2 py-1">
              <option value="7d">Last 7 days</option>
              <option value="30d">Last 30 days</option>
              <option value="90d">Last 90 days</option>
            </select>
          </div>
        </div>
        <div class="chart-body">
          <Line
            v-if="performanceTrendData.datasets"
            :data="performanceTrendData"
            :options="lineChartOptions"
            class="w-full h-80"
          />
        </div>
      </div>

      <!-- Risk Category Distribution -->
      <div class="chart-card bg-white rounded-lg shadow-sm p-6">
        <div class="chart-header mb-4">
          <h3 class="text-lg font-semibold text-gray-900">Risk Category Distribution</h3>
        </div>
        <div class="chart-body">
          <Doughnut
            v-if="riskDistributionData.datasets"
            :data="riskDistributionData"
            :options="doughnutOptions"
            class="w-full h-80"
          />
        </div>
      </div>
    </div>

    <!-- Key Performance Indicators -->
    <div class="kpi-section bg-white rounded-lg shadow-sm p-6 mb-8">
      <h3 class="text-lg font-semibold text-gray-900 mb-6">Key Performance Indicators</h3>

      <div class="kpi-grid grid grid-cols-1 md:grid-cols-3 gap-6">
        <div class="kpi-item">
          <div class="kpi-header flex justify-between items-center mb-2">
            <span class="text-sm font-medium text-gray-600">Exercise Completion Rate</span>
            <span class="text-lg font-bold text-gray-900">{{ kpis.exercise_completion_rate }}%</span>
          </div>
          <div class="kpi-progress bg-gray-200 rounded-full h-2">
            <div
              class="bg-green-500 h-2 rounded-full transition-all duration-300"
              :style="{ width: kpis.exercise_completion_rate + '%' }"
            ></div>
          </div>
          <div class="kpi-target mt-1 text-xs text-gray-500">Target: 85%</div>
        </div>

        <div class="kpi-item">
          <div class="kpi-header flex justify-between items-center mb-2">
            <span class="text-sm font-medium text-gray-600">Scenario Coverage</span>
            <span class="text-lg font-bold text-gray-900">{{ kpis.scenario_coverage }}%</span>
          </div>
          <div class="kpi-progress bg-gray-200 rounded-full h-2">
            <div
              class="bg-blue-500 h-2 rounded-full transition-all duration-300"
              :style="{ width: kpis.scenario_coverage + '%' }"
            ></div>
          </div>
          <div class="kpi-target mt-1 text-xs text-gray-500">Target: 90%</div>
        </div>

        <div class="kpi-item">
          <div class="kpi-header flex justify-between items-center mb-2">
            <span class="text-sm font-medium text-gray-600">User Engagement</span>
            <span class="text-lg font-bold text-gray-900">{{ kpis.user_engagement }}%</span>
          </div>
          <div class="kpi-progress bg-gray-200 rounded-full h-2">
            <div
              class="bg-purple-500 h-2 rounded-full transition-all duration-300"
              :style="{ width: kpis.user_engagement + '%' }"
            ></div>
          </div>
          <div class="kpi-target mt-1 text-xs text-gray-500">Target: 75%</div>
        </div>
      </div>
    </div>

    <!-- Recent Activities and Alerts -->
    <div class="bottom-section grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Recent Activities -->
      <div class="activities-card bg-white rounded-lg shadow-sm p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Recent Activities</h3>
        <div class="activities-list space-y-4">
          <div
            v-for="activity in recentActivities"
            :key="activity.id"
            class="activity-item flex items-start space-x-3"
          >
            <div class="activity-icon w-8 h-8 rounded-full flex items-center justify-center"
                 :class="getActivityIconClass(activity.type)">
              <i :class="getActivityIcon(activity.type)" class="text-xs"></i>
            </div>
            <div class="activity-content flex-1">
              <p class="text-sm text-gray-900">{{ activity.description }}</p>
              <p class="text-xs text-gray-500">{{ formatDate(activity.timestamp) }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- System Alerts -->
      <div class="alerts-card bg-white rounded-lg shadow-sm p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">System Alerts</h3>
        <div class="alerts-list space-y-3">
          <div
            v-for="alert in systemAlerts"
            :key="alert.id"
            class="alert-item p-3 rounded-lg border-l-4"
            :class="getAlertClass(alert.severity)"
          >
            <div class="flex justify-between items-start">
              <div class="flex-1">
                <p class="text-sm font-medium">{{ alert.title }}</p>
                <p class="text-xs text-gray-600 mt-1">{{ alert.description }}</p>
              </div>
              <span class="text-xs px-2 py-1 rounded-full"
                    :class="getAlertBadgeClass(alert.severity)">
                {{ alert.severity }}
              </span>
            </div>
          </div>
        </div>

        <div v-if="systemAlerts.length === 0" class="text-center py-4 text-gray-500">
          <i class="fas fa-check-circle text-green-500 text-2xl mb-2"></i>
          <p class="text-sm">All systems operational</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { Line, Doughnut } from 'vue-chartjs'
import { format } from 'date-fns'
import analyticsService from '@/services/analyticsService'

// Reactive data
const metrics = ref<any>({})
const performancePeriod = ref('30d')
const performanceTrendData = ref<any>({})
const riskDistributionData = ref<any>({})
const recentActivities = ref<any[]>([])
const systemAlerts = ref<any[]>([])

const kpis = ref({
  exercise_completion_rate: 78,
  scenario_coverage: 85,
  user_engagement: 72
})

// Computed properties
const riskCoverage = computed(() => {
  return Math.round((coveredRisks.value / totalRisks.value) * 100)
})

const coveredRisks = ref(18)
const totalRisks = ref(25)

// Chart options
const lineChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom' as const
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      max: 100
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
const loadExecutiveData = async () => {
  try {
    const data = await analyticsService.getDashboardData()
    metrics.value = data.dashboard

    updateCharts()
    loadActivities()
    loadAlerts()
  } catch (error) {
    console.error('Failed to load executive data:', error)
    loadMockData()
  }
}

const updateCharts = () => {
  // Performance Trend Chart
  performanceTrendData.value = {
    labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
    datasets: [
      {
        label: 'Exercise Success Rate',
        data: [72, 75, 78, 82],
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.4
      },
      {
        label: 'Platform Effectiveness',
        data: [68, 71, 76, 78],
        borderColor: 'rgb(16, 185, 129)',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        tension: 0.4
      }
    ]
  }

  // Risk Distribution Chart
  riskDistributionData.value = {
    labels: ['IT Systems', 'Supply Chain', 'Natural Disasters', 'Human Resources', 'Financial', 'Others'],
    datasets: [{
      data: [25, 20, 15, 12, 18, 10],
      backgroundColor: [
        '#3B82F6',
        '#10B981',
        '#F59E0B',
        '#EF4444',
        '#8B5CF6',
        '#6B7280'
      ]
    }]
  }
}

const loadActivities = () => {
  recentActivities.value = [
    {
      id: 1,
      type: 'exercise_completed',
      description: 'IT Disaster Recovery exercise completed by Team Alpha',
      timestamp: new Date(Date.now() - 1000 * 60 * 30) // 30 minutes ago
    },
    {
      id: 2,
      type: 'scenario_created',
      description: 'New AI-generated scenario: "Supply Chain Disruption" created',
      timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2) // 2 hours ago
    },
    {
      id: 3,
      type: 'user_registered',
      description: 'New user registered: John Smith (Risk Manager)',
      timestamp: new Date(Date.now() - 1000 * 60 * 60 * 4) // 4 hours ago
    },
    {
      id: 4,
      type: 'report_generated',
      description: 'Monthly compliance report generated',
      timestamp: new Date(Date.now() - 1000 * 60 * 60 * 6) // 6 hours ago
    }
  ]
}

const loadAlerts = () => {
  systemAlerts.value = [
    {
      id: 1,
      severity: 'warning',
      title: 'Scenario Coverage Below Target',
      description: 'IT Disaster scenarios need attention - only 65% coverage'
    },
    {
      id: 2,
      severity: 'info',
      title: 'Scheduled Maintenance',
      description: 'System maintenance scheduled for this weekend'
    }
  ]
}

const loadMockData = () => {
  metrics.value = {
    total_scenarios: 23,
    total_exercises: 52,
    ai_generated_scenarios: 8,
    platform_effectiveness: 78.5,
    total_exercises_completed: 45
  }

  updateCharts()
  loadActivities()
  loadAlerts()
}

const getActivityIcon = (type: string) => {
  const icons: Record<string, string> = {
    'exercise_completed': 'fas fa-check',
    'scenario_created': 'fas fa-plus',
    'user_registered': 'fas fa-user',
    'report_generated': 'fas fa-file-alt'
  }
  return icons[type] || 'fas fa-info'
}

const getActivityIconClass = (type: string) => {
  const classes: Record<string, string> = {
    'exercise_completed': 'bg-green-100 text-green-600',
    'scenario_created': 'bg-blue-100 text-blue-600',
    'user_registered': 'bg-purple-100 text-purple-600',
    'report_generated': 'bg-yellow-100 text-yellow-600'
  }
  return classes[type] || 'bg-gray-100 text-gray-600'
}

const getAlertClass = (severity: string) => {
  const classes: Record<string, string> = {
    'critical': 'bg-red-50 border-red-500',
    'warning': 'bg-yellow-50 border-yellow-500',
    'info': 'bg-blue-50 border-blue-500'
  }
  return classes[severity] || 'bg-gray-50 border-gray-500'
}

const getAlertBadgeClass = (severity: string) => {
  const classes: Record<string, string> = {
    'critical': 'bg-red-100 text-red-800',
    'warning': 'bg-yellow-100 text-yellow-800',
    'info': 'bg-blue-100 text-blue-800'
  }
  return classes[severity] || 'bg-gray-100 text-gray-800'
}

const formatDate = (date: Date) => {
  return format(date, 'MMM dd, HH:mm')
}

const refreshAnalytics = async () => {
  await loadExecutiveData()
}

// Expose method for parent component
defineExpose({
  refreshAnalytics
})

// Lifecycle
onMounted(() => {
  loadExecutiveData()
})
</script>

<style scoped>
.executive-dashboard {
  @apply space-y-6;
}

.summary-card {
  @apply transition-transform hover:scale-105;
}

.chart-card {
  @apply transition-shadow hover:shadow-lg;
}

.kpi-progress {
  @apply relative overflow-hidden;
}

.activity-item {
  @apply transition-colors hover:bg-gray-50 rounded p-2 -m-2;
}

.alert-item {
  @apply transition-all hover:shadow-sm;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .summary-cards {
    @apply grid-cols-1;
  }

  .charts-row-1 {
    @apply grid-cols-1;
  }

  .bottom-section {
    @apply grid-cols-1;
  }
}
</style>