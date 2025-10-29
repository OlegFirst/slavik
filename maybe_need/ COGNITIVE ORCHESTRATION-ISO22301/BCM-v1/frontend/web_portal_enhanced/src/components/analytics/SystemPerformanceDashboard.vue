<template>
  <div class="system-performance-dashboard">
    <!-- System Health Overview -->
    <div class="health-overview grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <div class="health-card bg-white rounded-lg shadow-sm p-6 border-l-4"
           :class="getHealthCardClass('cpu')">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">CPU Usage</p>
            <p class="text-3xl font-bold text-gray-900">{{ systemMetrics.cpu_usage || 0 }}%</p>
          </div>
          <div class="w-12 h-12 rounded-lg flex items-center justify-center"
               :class="getHealthIconClass('cpu')">
            <i class="fas fa-microchip text-xl"></i>
          </div>
        </div>
        <div class="mt-4">
          <div class="progress bg-gray-200 rounded-full h-2">
            <div
              class="h-2 rounded-full transition-all duration-300"
              :class="getProgressBarClass(systemMetrics.cpu_usage)"
              :style="{ width: systemMetrics.cpu_usage + '%' }"
            ></div>
          </div>
        </div>
      </div>

      <div class="health-card bg-white rounded-lg shadow-sm p-6 border-l-4"
           :class="getHealthCardClass('memory')">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Memory Usage</p>
            <p class="text-3xl font-bold text-gray-900">{{ systemMetrics.memory_usage || 0 }}%</p>
          </div>
          <div class="w-12 h-12 rounded-lg flex items-center justify-center"
               :class="getHealthIconClass('memory')">
            <i class="fas fa-memory text-xl"></i>
          </div>
        </div>
        <div class="mt-4">
          <div class="progress bg-gray-200 rounded-full h-2">
            <div
              class="h-2 rounded-full transition-all duration-300"
              :class="getProgressBarClass(systemMetrics.memory_usage)"
              :style="{ width: systemMetrics.memory_usage + '%' }"
            ></div>
          </div>
        </div>
      </div>

      <div class="health-card bg-white rounded-lg shadow-sm p-6 border-l-4"
           :class="getHealthCardClass('disk')">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Disk Usage</p>
            <p class="text-3xl font-bold text-gray-900">{{ systemMetrics.disk_usage || 0 }}%</p>
          </div>
          <div class="w-12 h-12 rounded-lg flex items-center justify-center"
               :class="getHealthIconClass('disk')">
            <i class="fas fa-hdd text-xl"></i>
          </div>
        </div>
        <div class="mt-4">
          <div class="progress bg-gray-200 rounded-full h-2">
            <div
              class="h-2 rounded-full transition-all duration-300"
              :class="getProgressBarClass(systemMetrics.disk_usage)"
              :style="{ width: systemMetrics.disk_usage + '%' }"
            ></div>
          </div>
        </div>
      </div>

      <div class="health-card bg-white rounded-lg shadow-sm p-6 border-l-4 border-blue-500">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Response Time</p>
            <p class="text-3xl font-bold text-gray-900">{{ systemMetrics.response_time || 0 }}ms</p>
          </div>
          <div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
            <i class="fas fa-clock text-blue-600 text-xl"></i>
          </div>
        </div>
        <div class="mt-4">
          <span class="text-xs text-gray-500">
            <i class="fas fa-arrow-down text-green-500 mr-1"></i>
            12ms improvement from last hour
          </span>
        </div>
      </div>
    </div>

    <!-- Performance Charts -->
    <div class="performance-charts grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
      <!-- System Resource Usage -->
      <div class="chart-card bg-white rounded-lg shadow-sm p-6">
        <div class="chart-header flex justify-between items-center mb-4">
          <h3 class="text-lg font-semibold text-gray-900">System Resource Usage</h3>
          <div class="chart-controls">
            <select v-model="resourceTimeRange" class="text-sm border rounded px-2 py-1">
              <option value="1h">Last Hour</option>
              <option value="24h">Last 24 Hours</option>
              <option value="7d">Last 7 Days</option>
            </select>
          </div>
        </div>
        <div class="chart-body">
          <Line
            v-if="resourceUsageData.datasets"
            :data="resourceUsageData"
            :options="lineChartOptions"
            class="w-full h-80"
          />
        </div>
      </div>

      <!-- Response Time Distribution -->
      <div class="chart-card bg-white rounded-lg shadow-sm p-6">
        <div class="chart-header mb-4">
          <h3 class="text-lg font-semibold text-gray-900">Response Time Distribution</h3>
        </div>
        <div class="chart-body">
          <Bar
            v-if="responseTimeData.datasets"
            :data="responseTimeData"
            :options="barChartOptions"
            class="w-full h-80"
          />
        </div>
      </div>
    </div>

    <!-- Service Status Grid -->
    <div class="service-status bg-white rounded-lg shadow-sm p-6 mb-8">
      <h3 class="text-lg font-semibold text-gray-900 mb-6">Service Status</h3>

      <div class="services-grid grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div
          v-for="service in services"
          :key="service.name"
          class="service-card rounded-lg p-4 border-2 transition-all hover:shadow-md"
          :class="getServiceCardClass(service.status)"
        >
          <div class="flex items-center justify-between">
            <div class="service-info">
              <h4 class="font-semibold text-gray-900">{{ service.name }}</h4>
              <p class="text-sm text-gray-600">{{ service.description }}</p>
            </div>
            <div class="service-status-indicator">
              <div
                class="w-4 h-4 rounded-full"
                :class="getStatusIndicatorClass(service.status)"
              ></div>
            </div>
          </div>

          <div class="service-metrics mt-4 space-y-2">
            <div class="metric-row flex justify-between text-sm">
              <span class="text-gray-600">Uptime:</span>
              <span class="font-medium">{{ service.uptime }}%</span>
            </div>
            <div class="metric-row flex justify-between text-sm">
              <span class="text-gray-600">Last Check:</span>
              <span class="font-medium">{{ formatTime(service.last_check) }}</span>
            </div>
            <div v-if="service.response_time" class="metric-row flex justify-between text-sm">
              <span class="text-gray-600">Response:</span>
              <span class="font-medium">{{ service.response_time }}ms</span>
            </div>
          </div>

          <div v-if="service.status !== 'healthy'" class="service-actions mt-4">
            <button
              @click="restartService(service.name)"
              class="w-full bg-blue-600 text-white text-xs px-3 py-2 rounded hover:bg-blue-700 transition-colors"
            >
              <i class="fas fa-redo mr-1"></i>
              Restart Service
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Performance Metrics Table -->
    <div class="metrics-table bg-white rounded-lg shadow-sm p-6 mb-8">
      <div class="table-header flex justify-between items-center mb-4">
        <h3 class="text-lg font-semibold text-gray-900">Detailed Performance Metrics</h3>
        <button
          @click="exportMetrics"
          class="bg-gray-100 text-gray-700 text-sm px-3 py-2 rounded hover:bg-gray-200 transition-colors"
        >
          <i class="fas fa-download mr-1"></i>
          Export CSV
        </button>
      </div>

      <div class="table-container overflow-x-auto">
        <table class="w-full table-auto">
          <thead>
            <tr class="bg-gray-50">
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Metric
              </th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Current Value
              </th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Threshold
              </th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Last Updated
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200">
            <tr
              v-for="metric in detailedMetrics"
              :key="metric.name"
              class="hover:bg-gray-50"
            >
              <td class="px-4 py-4 text-sm font-medium text-gray-900">
                {{ metric.name }}
              </td>
              <td class="px-4 py-4 text-sm text-gray-900">
                {{ metric.current_value }}{{ metric.unit }}
              </td>
              <td class="px-4 py-4 text-sm text-gray-600">
                {{ metric.threshold }}{{ metric.unit }}
              </td>
              <td class="px-4 py-4 text-sm">
                <span
                  class="px-2 py-1 text-xs font-medium rounded-full"
                  :class="getMetricStatusClass(metric.status)"
                >
                  {{ metric.status }}
                </span>
              </td>
              <td class="px-4 py-4 text-sm text-gray-600">
                {{ formatTime(metric.last_updated) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- System Logs -->
    <div class="system-logs bg-white rounded-lg shadow-sm p-6">
      <div class="logs-header flex justify-between items-center mb-4">
        <h3 class="text-lg font-semibold text-gray-900">Recent System Events</h3>
        <div class="log-controls flex space-x-2">
          <select v-model="logLevel" class="text-sm border rounded px-2 py-1">
            <option value="all">All Levels</option>
            <option value="error">Errors</option>
            <option value="warning">Warnings</option>
            <option value="info">Info</option>
          </select>
          <button
            @click="refreshLogs"
            class="bg-blue-600 text-white text-sm px-3 py-2 rounded hover:bg-blue-700 transition-colors"
          >
            <i class="fas fa-sync mr-1"></i>
            Refresh
          </button>
        </div>
      </div>

      <div class="logs-container max-h-96 overflow-y-auto">
        <div class="logs-list space-y-2">
          <div
            v-for="log in filteredLogs"
            :key="log.id"
            class="log-entry p-3 rounded border-l-4 text-sm"
            :class="getLogEntryClass(log.level)"
          >
            <div class="log-header flex justify-between items-start mb-1">
              <span class="font-medium">{{ log.service }}</span>
              <span class="text-xs text-gray-500">{{ formatTime(log.timestamp) }}</span>
            </div>
            <p class="log-message">{{ log.message }}</p>
            <div v-if="log.details" class="log-details mt-2 text-xs text-gray-600">
              {{ log.details }}
            </div>
          </div>
        </div>
      </div>

      <div v-if="filteredLogs.length === 0" class="text-center py-8 text-gray-500">
        <i class="fas fa-list text-2xl mb-2"></i>
        <p>No system events to display</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { Line, Bar } from 'vue-chartjs'
import { format } from 'date-fns'

// Reactive data
const systemMetrics = ref<any>({})
const services = ref<any[]>([])
const detailedMetrics = ref<any[]>([])
const systemLogs = ref<any[]>([])
const resourceTimeRange = ref('24h')
const logLevel = ref('all')

// Chart data
const resourceUsageData = ref<any>({})
const responseTimeData = ref<any>({})

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

const barChartOptions = {
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

// Computed properties
const filteredLogs = computed(() => {
  if (logLevel.value === 'all') {
    return systemLogs.value
  }
  return systemLogs.value.filter(log => log.level === logLevel.value)
})

// Methods
const loadSystemMetrics = async () => {
  try {
    // In a real implementation, this would call the actual monitoring API
    // For now, we'll simulate the data
    loadMockSystemData()
  } catch (error) {
    console.error('Failed to load system metrics:', error)
    loadMockSystemData()
  }
}

const loadMockSystemData = () => {
  systemMetrics.value = {
    cpu_usage: 45,
    memory_usage: 62,
    disk_usage: 78,
    response_time: 234
  }

  services.value = [
    {
      name: 'Odoo Backend',
      description: 'Main BCM platform backend',
      status: 'healthy',
      uptime: 99.8,
      last_check: new Date(Date.now() - 1000 * 60 * 2),
      response_time: 180
    },
    {
      name: 'Vue.js Frontend',
      description: 'Web portal frontend',
      status: 'healthy',
      uptime: 99.9,
      last_check: new Date(Date.now() - 1000 * 60 * 1),
      response_time: 120
    },
    {
      name: 'Scenario Orchestrator',
      description: 'AI scenario management service',
      status: 'warning',
      uptime: 98.5,
      last_check: new Date(Date.now() - 1000 * 60 * 5),
      response_time: 450
    },
    {
      name: 'PostgreSQL Database',
      description: 'Primary database server',
      status: 'healthy',
      uptime: 99.99,
      last_check: new Date(Date.now() - 1000 * 30),
      response_time: 45
    },
    {
      name: 'Redis Cache',
      description: 'Caching service',
      status: 'healthy',
      uptime: 99.95,
      last_check: new Date(Date.now() - 1000 * 60),
      response_time: 12
    },
    {
      name: 'Grafana Monitoring',
      description: 'System monitoring dashboard',
      status: 'degraded',
      uptime: 97.2,
      last_check: new Date(Date.now() - 1000 * 60 * 10),
      response_time: 890
    }
  ]

  detailedMetrics.value = [
    {
      name: 'CPU Usage',
      current_value: 45,
      threshold: 80,
      unit: '%',
      status: 'normal',
      last_updated: new Date(Date.now() - 1000 * 60)
    },
    {
      name: 'Memory Usage',
      current_value: 62,
      threshold: 85,
      unit: '%',
      status: 'normal',
      last_updated: new Date(Date.now() - 1000 * 60)
    },
    {
      name: 'Disk I/O',
      current_value: 1250,
      threshold: 5000,
      unit: ' IOPS',
      status: 'normal',
      last_updated: new Date(Date.now() - 1000 * 30)
    },
    {
      name: 'Network Latency',
      current_value: 23,
      threshold: 100,
      unit: 'ms',
      status: 'normal',
      last_updated: new Date(Date.now() - 1000 * 45)
    },
    {
      name: 'Database Connections',
      current_value: 87,
      threshold: 200,
      unit: '',
      status: 'normal',
      last_updated: new Date(Date.now() - 1000 * 120)
    }
  ]

  systemLogs.value = [
    {
      id: 1,
      service: 'Scenario Orchestrator',
      level: 'warning',
      message: 'High response time detected',
      details: 'Response time: 450ms (threshold: 300ms)',
      timestamp: new Date(Date.now() - 1000 * 60 * 5)
    },
    {
      id: 2,
      service: 'Grafana',
      level: 'error',
      message: 'Connection timeout to metrics endpoint',
      details: 'Failed to connect to prometheus:9090',
      timestamp: new Date(Date.now() - 1000 * 60 * 10)
    },
    {
      id: 3,
      service: 'Odoo Backend',
      level: 'info',
      message: 'Analytics dashboard refreshed successfully',
      details: 'Processed 152 scenarios, 45 exercises',
      timestamp: new Date(Date.now() - 1000 * 60 * 15)
    },
    {
      id: 4,
      service: 'PostgreSQL',
      level: 'info',
      message: 'Database maintenance completed',
      details: 'Vacuum and reindex operations finished',
      timestamp: new Date(Date.now() - 1000 * 60 * 60)
    }
  ]

  updateCharts()
}

const updateCharts = () => {
  // Resource Usage Chart
  resourceUsageData.value = {
    labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'],
    datasets: [
      {
        label: 'CPU Usage',
        data: [35, 42, 48, 52, 45, 40],
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.4
      },
      {
        label: 'Memory Usage',
        data: [58, 61, 65, 68, 62, 60],
        borderColor: 'rgb(16, 185, 129)',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        tension: 0.4
      },
      {
        label: 'Disk Usage',
        data: [76, 77, 78, 78, 78, 78],
        borderColor: 'rgb(245, 158, 11)',
        backgroundColor: 'rgba(245, 158, 11, 0.1)',
        tension: 0.4
      }
    ]
  }

  // Response Time Distribution
  responseTimeData.value = {
    labels: ['0-100ms', '100-200ms', '200-500ms', '500ms+'],
    datasets: [{
      label: 'Request Count',
      data: [1250, 850, 230, 45],
      backgroundColor: [
        'rgba(34, 197, 94, 0.8)',
        'rgba(59, 130, 246, 0.8)',
        'rgba(245, 158, 11, 0.8)',
        'rgba(239, 68, 68, 0.8)'
      ]
    }]
  }
}

// Utility methods
const getHealthCardClass = (metric: string) => {
  const value = systemMetrics.value[`${metric}_usage`]
  if (value > 80) return 'border-red-500'
  if (value > 60) return 'border-yellow-500'
  return 'border-green-500'
}

const getHealthIconClass = (metric: string) => {
  const value = systemMetrics.value[`${metric}_usage`]
  if (value > 80) return 'bg-red-100 text-red-600'
  if (value > 60) return 'bg-yellow-100 text-yellow-600'
  return 'bg-green-100 text-green-600'
}

const getProgressBarClass = (value: number) => {
  if (value > 80) return 'bg-red-500'
  if (value > 60) return 'bg-yellow-500'
  return 'bg-green-500'
}

const getServiceCardClass = (status: string) => {
  const classes: Record<string, string> = {
    'healthy': 'border-green-200 bg-green-50',
    'warning': 'border-yellow-200 bg-yellow-50',
    'degraded': 'border-orange-200 bg-orange-50',
    'down': 'border-red-200 bg-red-50'
  }
  return classes[status] || 'border-gray-200 bg-gray-50'
}

const getStatusIndicatorClass = (status: string) => {
  const classes: Record<string, string> = {
    'healthy': 'bg-green-500',
    'warning': 'bg-yellow-500',
    'degraded': 'bg-orange-500',
    'down': 'bg-red-500'
  }
  return classes[status] || 'bg-gray-500'
}

const getMetricStatusClass = (status: string) => {
  const classes: Record<string, string> = {
    'normal': 'bg-green-100 text-green-800',
    'warning': 'bg-yellow-100 text-yellow-800',
    'critical': 'bg-red-100 text-red-800'
  }
  return classes[status] || 'bg-gray-100 text-gray-800'
}

const getLogEntryClass = (level: string) => {
  const classes: Record<string, string> = {
    'error': 'border-red-500 bg-red-50',
    'warning': 'border-yellow-500 bg-yellow-50',
    'info': 'border-blue-500 bg-blue-50'
  }
  return classes[level] || 'border-gray-500 bg-gray-50'
}

const formatTime = (date: Date) => {
  return format(date, 'MMM dd, HH:mm')
}

// Action methods
const restartService = (serviceName: string) => {
  console.log('Restart service:', serviceName)
  // In a real implementation, this would call the service management API
}

const exportMetrics = () => {
  console.log('Export metrics as CSV')
  // In a real implementation, this would generate and download a CSV file
}

const refreshLogs = () => {
  console.log('Refresh system logs')
  // In a real implementation, this would reload the logs from the API
}

const refreshAnalytics = async () => {
  await loadSystemMetrics()
}

// Expose method for parent component
defineExpose({
  refreshAnalytics
})

// Lifecycle
onMounted(() => {
  loadSystemMetrics()

  // Set up auto-refresh every 30 seconds
  const interval = setInterval(() => {
    loadSystemMetrics()
  }, 30000)

  // Cleanup on unmount
  return () => clearInterval(interval)
})
</script>

<style scoped>
.system-performance-dashboard {
  @apply space-y-6;
}

.health-card {
  @apply transition-transform hover:scale-105;
}

.chart-card {
  @apply transition-shadow hover:shadow-lg;
}

.service-card {
  @apply transition-all hover:shadow-md;
}

.log-entry {
  @apply transition-colors hover:bg-opacity-75;
}

.progress {
  @apply relative overflow-hidden;
}

.table-container {
  @apply -mx-4 sm:mx-0;
}

.logs-container {
  @apply border border-gray-200 rounded;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .health-overview {
    @apply grid-cols-1;
  }

  .performance-charts {
    @apply grid-cols-1;
  }

  .services-grid {
    @apply grid-cols-1;
  }
}
</style>