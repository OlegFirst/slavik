<template>
  <div class="simulation-summary-chart">
    <div class="chart-header mb-4">
      <h4 class="text-lg font-semibold text-gray-900">Simulation Summary</h4>
      <p class="text-sm text-gray-600">Overall performance and key metrics</p>
    </div>

    <!-- Key Metrics Grid -->
    <div class="summary-metrics grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
      <div class="metric-card bg-blue-50 p-4 rounded-lg">
        <div class="metric-icon mb-2">
          <ChartBarIcon class="w-6 h-6 text-blue-500" />
        </div>
        <div class="metric-value text-2xl font-bold text-blue-600">
          {{ data?.totalEvents?.toLocaleString() || 0 }}
        </div>
        <div class="metric-label text-sm text-gray-600">Total Events</div>
        <div class="metric-change text-xs text-green-600 mt-1">
          +{{ calculateChange(data?.totalEvents, data?.previousTotalEvents) }}%
        </div>
      </div>

      <div class="metric-card bg-green-50 p-4 rounded-lg">
        <div class="metric-icon mb-2">
          <ClockIcon class="w-6 h-6 text-green-500" />
        </div>
        <div class="metric-value text-2xl font-bold text-green-600">
          {{ formatDuration(data?.totalDuration) }}
        </div>
        <div class="metric-label text-sm text-gray-600">Total Duration</div>
        <div class="metric-change text-xs text-blue-600 mt-1">
          {{ data?.efficiency > 80 ? 'Efficient' : 'Needs Improvement' }}
        </div>
      </div>

      <div class="metric-card bg-yellow-50 p-4 rounded-lg">
        <div class="metric-icon mb-2">
          <CheckCircleIcon class="w-6 h-6 text-yellow-500" />
        </div>
        <div class="metric-value text-2xl font-bold text-yellow-600">
          {{ data?.completionRate || 0 }}%
        </div>
        <div class="metric-label text-sm text-gray-600">Completion Rate</div>
        <div class="metric-change text-xs" :class="data?.completionRate >= 90 ? 'text-green-600' : 'text-red-600'">
          {{ data?.completionRate >= 90 ? 'Excellent' : 'Below Target' }}
        </div>
      </div>

      <div class="metric-card bg-purple-50 p-4 rounded-lg">
        <div class="metric-icon mb-2">
          <CpuChipIcon class="w-6 h-6 text-purple-500" />
        </div>
        <div class="metric-value text-2xl font-bold text-purple-600">
          {{ data?.efficiency || 0 }}%
        </div>
        <div class="metric-label text-sm text-gray-600">Efficiency Score</div>
        <div class="metric-change text-xs" :class="data?.efficiency > 75 ? 'text-green-600' : 'text-yellow-600'">
          {{ getEfficiencyRating(data?.efficiency) }}
        </div>
      </div>
    </div>

    <!-- Performance Timeline Chart -->
    <div class="performance-timeline bg-white border rounded-lg p-4 mb-6">
      <h5 class="font-medium text-gray-900 mb-4">Performance Timeline</h5>
      <div class="chart-container" style="height: 300px;">
        <Line
          v-if="chartData && chartData.datasets"
          :data="chartData"
          :options="chartOptions"
        />
        <div v-else class="flex items-center justify-center h-full text-gray-500">
          <div class="text-center">
            <ChartBarIcon class="w-12 h-12 mx-auto mb-2 opacity-50" />
            <p>No timeline data available</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Phase Performance Breakdown -->
    <div class="phase-breakdown bg-white border rounded-lg p-4 mb-6">
      <h5 class="font-medium text-gray-900 mb-4">Phase Performance Breakdown</h5>

      <div class="phases-list space-y-3">
        <div
          v-for="(phase, index) in data?.phaseBreakdown || []"
          :key="index"
          class="phase-item p-3 bg-gray-50 rounded-lg"
        >
          <div class="flex items-center justify-between mb-2">
            <h6 class="font-medium text-gray-900">{{ phase.name }}</h6>
            <span class="text-sm text-gray-500">{{ formatDuration(phase.duration) }}</span>
          </div>

          <div class="progress-bar bg-gray-200 rounded-full h-2 mb-2">
            <div
              class="progress-fill rounded-full h-2 transition-all duration-500"
              :class="{
                'bg-green-500': phase.performance >= 90,
                'bg-yellow-500': phase.performance >= 70 && phase.performance < 90,
                'bg-red-500': phase.performance < 70
              }"
              :style="{ width: `${phase.performance}%` }"
            ></div>
          </div>

          <div class="flex items-center justify-between text-xs text-gray-600">
            <span>Performance: {{ phase.performance }}%</span>
            <span>{{ phase.events }} events processed</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Resource Utilization Heatmap -->
    <div class="resource-heatmap bg-white border rounded-lg p-4">
      <h5 class="font-medium text-gray-900 mb-4">Resource Utilization Heatmap</h5>

      <div class="heatmap-grid">
        <div class="grid grid-cols-12 gap-1 mb-2">
          <div
            v-for="(hour, index) in 24"
            :key="index"
            class="text-xs text-center text-gray-500"
          >
            {{ index.toString().padStart(2, '0') }}
          </div>
        </div>

        <div
          v-for="(resource, resourceIndex) in resourceUtilization"
          :key="resourceIndex"
          class="flex items-center mb-2"
        >
          <div class="w-24 text-xs text-gray-700 font-medium mr-2">
            {{ resource.name }}
          </div>
          <div class="grid grid-cols-12 gap-1 flex-1">
            <div
              v-for="(utilization, hourIndex) in resource.hourlyData"
              :key="hourIndex"
              class="h-4 rounded-sm"
              :class="getUtilizationColor(utilization)"
              :title="`${resource.name} at ${hourIndex}:00 - ${utilization}% utilization`"
            ></div>
          </div>
        </div>
      </div>

      <div class="heatmap-legend flex items-center justify-center mt-4 space-x-4">
        <div class="flex items-center space-x-1">
          <div class="w-3 h-3 bg-green-200 rounded-sm"></div>
          <span class="text-xs text-gray-600">Low (0-30%)</span>
        </div>
        <div class="flex items-center space-x-1">
          <div class="w-3 h-3 bg-yellow-300 rounded-sm"></div>
          <span class="text-xs text-gray-600">Medium (30-70%)</span>
        </div>
        <div class="flex items-center space-x-1">
          <div class="w-3 h-3 bg-orange-400 rounded-sm"></div>
          <span class="text-xs text-gray-600">High (70-90%)</span>
        </div>
        <div class="flex items-center space-x-1">
          <div class="w-3 h-3 bg-red-500 rounded-sm"></div>
          <span class="text-xs text-gray-600">Critical (90-100%)</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import {
  ChartBarIcon,
  ClockIcon,
  CheckCircleIcon,
  CpuChipIcon
} from '@heroicons/vue/24/outline'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'
import { Line } from 'vue-chartjs'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

interface Props {
  data: {
    totalEvents?: number
    previousTotalEvents?: number
    totalDuration?: number
    completionRate?: number
    efficiency?: number
    phaseBreakdown?: Array<{
      name: string
      duration: number
      performance: number
      events: number
    }>
    timelineData?: Array<{
      timestamp: string
      events: number
      utilization: number
      responseTime: number
    }>
  }
}

const props = defineProps<Props>()

// Mock resource utilization data for demonstration
const resourceUtilization = ref([
  {
    name: 'CPU',
    hourlyData: Array.from({ length: 24 }, () => Math.floor(Math.random() * 100))
  },
  {
    name: 'Memory',
    hourlyData: Array.from({ length: 24 }, () => Math.floor(Math.random() * 100))
  },
  {
    name: 'Network',
    hourlyData: Array.from({ length: 24 }, () => Math.floor(Math.random() * 100))
  },
  {
    name: 'Storage',
    hourlyData: Array.from({ length: 24 }, () => Math.floor(Math.random() * 100))
  }
])

// Chart configuration
const chartData = computed(() => {
  if (!props.data?.timelineData) return null

  const labels = props.data.timelineData.map(point =>
    new Date(point.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  )

  return {
    labels,
    datasets: [
      {
        label: 'Events/min',
        data: props.data.timelineData.map(point => point.events),
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        fill: true,
        tension: 0.4,
        yAxisID: 'y'
      },
      {
        label: 'Utilization %',
        data: props.data.timelineData.map(point => point.utilization),
        borderColor: 'rgb(16, 185, 129)',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        fill: true,
        tension: 0.4,
        yAxisID: 'y1'
      },
      {
        label: 'Response Time (ms)',
        data: props.data.timelineData.map(point => point.responseTime),
        borderColor: 'rgb(245, 158, 11)',
        backgroundColor: 'rgba(245, 158, 11, 0.1)',
        fill: true,
        tension: 0.4,
        yAxisID: 'y2'
      }
    ]
  }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  interaction: {
    mode: 'index' as const,
    intersect: false,
  },
  plugins: {
    legend: {
      position: 'top' as const,
    },
    tooltip: {
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      titleColor: 'white',
      bodyColor: 'white',
      borderColor: 'rgba(255, 255, 255, 0.2)',
      borderWidth: 1
    }
  },
  scales: {
    x: {
      display: true,
      title: {
        display: true,
        text: 'Time'
      },
      grid: {
        color: 'rgba(0, 0, 0, 0.1)'
      }
    },
    y: {
      type: 'linear' as const,
      display: true,
      position: 'left' as const,
      title: {
        display: true,
        text: 'Events/min',
        color: 'rgb(59, 130, 246)'
      },
      grid: {
        color: 'rgba(0, 0, 0, 0.1)'
      }
    },
    y1: {
      type: 'linear' as const,
      display: true,
      position: 'right' as const,
      title: {
        display: true,
        text: 'Utilization %',
        color: 'rgb(16, 185, 129)'
      },
      grid: {
        drawOnChartArea: false,
      },
      max: 100
    },
    y2: {
      type: 'linear' as const,
      display: false,
      position: 'right' as const,
    }
  },
  elements: {
    point: {
      radius: 2,
      hoverRadius: 6
    }
  }
}

// Utility functions
const calculateChange = (current: number = 0, previous: number = 0): number => {
  if (previous === 0) return 0
  return Math.round(((current - previous) / previous) * 100)
}

const formatDuration = (seconds: number = 0): string => {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)

  if (hours > 0) {
    return `${hours}h ${minutes}m`
  } else if (minutes > 0) {
    return `${minutes}m`
  } else {
    return `${seconds}s`
  }
}

const getEfficiencyRating = (efficiency: number = 0): string => {
  if (efficiency >= 90) return 'Excellent'
  if (efficiency >= 75) return 'Good'
  if (efficiency >= 60) return 'Fair'
  return 'Poor'
}

const getUtilizationColor = (utilization: number): string => {
  if (utilization >= 90) return 'bg-red-500'
  if (utilization >= 70) return 'bg-orange-400'
  if (utilization >= 30) return 'bg-yellow-300'
  return 'bg-green-200'
}
</script>

<style scoped>
.metric-card {
  transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
}

.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.chart-container {
  position: relative;
}

.heatmap-grid {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
}

.progress-fill {
  transition: width 0.5s ease-in-out;
}

.phase-item {
  transition: all 0.2s ease-in-out;
}

.phase-item:hover {
  background-color: #f3f4f6;
  transform: translateX(4px);
}
</style>