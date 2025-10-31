<template>
  <div class="utilization-chart">
    <div class="chart-container" style="position: relative; height: 100%;">
      <Doughnut
        v-if="chartData && chartData.datasets"
        :data="chartData"
        :options="chartOptions"
      />
      <div v-else class="empty-state flex items-center justify-center h-full">
        <div class="text-center text-gray-500">
          <CpuChipIcon class="w-12 h-12 mx-auto mb-2 opacity-50" />
          <p class="text-sm">No utilization data available</p>
        </div>
      </div>

      <!-- Center Label -->
      <div
        v-if="chartData && chartData.datasets"
        class="absolute inset-0 flex items-center justify-center pointer-events-none"
      >
        <div class="text-center">
          <div class="text-2xl font-bold text-gray-900">{{ averageUtilization }}%</div>
          <div class="text-sm text-gray-500">Average</div>
        </div>
      </div>
    </div>

    <!-- Resource Breakdown -->
    <div v-if="resourceBreakdown.length > 0" class="resource-breakdown mt-4">
      <h5 class="font-medium text-gray-900 mb-3">Resource Breakdown</h5>
      <div class="space-y-2">
        <div
          v-for="(resource, index) in resourceBreakdown"
          :key="index"
          class="flex items-center justify-between p-2 bg-gray-50 rounded"
        >
          <div class="flex items-center space-x-2">
            <div
              class="w-3 h-3 rounded-full"
              :style="{ backgroundColor: chartColors[index % chartColors.length] }"
            ></div>
            <span class="text-sm font-medium text-gray-700">{{ resource.name }}</span>
          </div>
          <div class="flex items-center space-x-2">
            <div class="w-20 bg-gray-200 rounded-full h-2">
              <div
                class="h-2 rounded-full transition-all duration-300"
                :style="{
                  width: `${resource.utilization}%`,
                  backgroundColor: chartColors[index % chartColors.length]
                }"
              ></div>
            </div>
            <span class="text-sm text-gray-600 min-w-[3rem]">{{ resource.utilization }}%</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Utilization Trends -->
    <div v-if="trendData.length > 0" class="utilization-trends mt-4">
      <h5 class="font-medium text-gray-900 mb-3">Utilization Trends</h5>
      <div class="chart-container" style="height: 150px;">
        <Line
          :data="trendChartData"
          :options="trendChartOptions"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { CpuChipIcon } from '@heroicons/vue/24/outline'
import {
  Chart as ChartJS,
  ArcElement,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js'
import { Doughnut, Line } from 'vue-chartjs'

ChartJS.register(
  ArcElement,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
)

interface UtilizationDataPoint {
  timestamp: string | Date
  cpu?: number
  memory?: number
  network?: number
  storage?: number
  overall?: number
}

interface Props {
  data: UtilizationDataPoint[]
}

const props = defineProps<Props>()

const chartColors = [
  '#3b82f6', // Blue
  '#10b981', // Green
  '#f59e0b', // Yellow
  '#ef4444', // Red
  '#8b5cf6', // Purple
  '#06b6d4', // Cyan
  '#f97316', // Orange
  '#84cc16'  // Lime
]

const resourceBreakdown = computed(() => {
  if (!props.data || props.data.length === 0) return []

  const latest = props.data[props.data.length - 1]
  const resources = []

  if (latest.cpu !== undefined) {
    resources.push({ name: 'CPU', utilization: latest.cpu })
  }
  if (latest.memory !== undefined) {
    resources.push({ name: 'Memory', utilization: latest.memory })
  }
  if (latest.network !== undefined) {
    resources.push({ name: 'Network', utilization: latest.network })
  }
  if (latest.storage !== undefined) {
    resources.push({ name: 'Storage', utilization: latest.storage })
  }

  return resources.sort((a, b) => b.utilization - a.utilization)
})

const averageUtilization = computed(() => {
  if (!props.data || props.data.length === 0) return 0

  if (props.data.some(point => point.overall !== undefined)) {
    const totalOverall = props.data.reduce((sum, point) => sum + (point.overall || 0), 0)
    return Math.round(totalOverall / props.data.length)
  }

  // Calculate from individual resources
  const resources = ['cpu', 'memory', 'network', 'storage']
  let totalSum = 0
  let count = 0

  resources.forEach(resource => {
    if (props.data.some(point => point[resource] !== undefined)) {
      const sum = props.data.reduce((s, point) => s + (point[resource] || 0), 0)
      totalSum += sum / props.data.length
      count++
    }
  })

  return count > 0 ? Math.round(totalSum / count) : 0
})

const chartData = computed(() => {
  if (resourceBreakdown.value.length === 0) return null

  return {
    labels: resourceBreakdown.value.map(r => r.name),
    datasets: [
      {
        data: resourceBreakdown.value.map(r => r.utilization),
        backgroundColor: chartColors.slice(0, resourceBreakdown.value.length),
        borderColor: chartColors.slice(0, resourceBreakdown.value.length).map(color => color + '40'),
        borderWidth: 2,
        hoverBorderWidth: 3,
        cutout: '60%'
      }
    ]
  }
})

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false
    },
    tooltip: {
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      titleColor: 'white',
      bodyColor: 'white',
      borderColor: 'rgba(255, 255, 255, 0.2)',
      borderWidth: 1,
      cornerRadius: 8,
      callbacks: {
        label: (context: any) => {
          const label = context.label || ''
          const value = context.parsed
          return `${label}: ${value}%`
        }
      }
    }
  },
  animation: {
    animateRotate: true,
    duration: 1000
  }
}))

// Trend data for the line chart
const trendData = computed(() => {
  if (!props.data || props.data.length < 2) return []
  return props.data.slice(-20) // Last 20 data points for trend
})

const trendChartData = computed(() => {
  if (trendData.value.length === 0) return null

  const labels = trendData.value.map(point => {
    const date = new Date(point.timestamp)
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  })

  const datasets = []

  // Add trend lines for each resource
  if (trendData.value.some(point => point.cpu !== undefined)) {
    datasets.push({
      label: 'CPU',
      data: trendData.value.map(point => point.cpu || 0),
      borderColor: chartColors[0],
      backgroundColor: chartColors[0] + '20',
      tension: 0.4,
      pointRadius: 1,
      borderWidth: 1.5
    })
  }

  if (trendData.value.some(point => point.memory !== undefined)) {
    datasets.push({
      label: 'Memory',
      data: trendData.value.map(point => point.memory || 0),
      borderColor: chartColors[1],
      backgroundColor: chartColors[1] + '20',
      tension: 0.4,
      pointRadius: 1,
      borderWidth: 1.5
    })
  }

  if (trendData.value.some(point => point.network !== undefined)) {
    datasets.push({
      label: 'Network',
      data: trendData.value.map(point => point.network || 0),
      borderColor: chartColors[2],
      backgroundColor: chartColors[2] + '20',
      tension: 0.4,
      pointRadius: 1,
      borderWidth: 1.5
    })
  }

  if (trendData.value.some(point => point.storage !== undefined)) {
    datasets.push({
      label: 'Storage',
      data: trendData.value.map(point => point.storage || 0),
      borderColor: chartColors[3],
      backgroundColor: chartColors[3] + '20',
      tension: 0.4,
      pointRadius: 1,
      borderWidth: 1.5
    })
  }

  return {
    labels,
    datasets
  }
})

const trendChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  interaction: {
    mode: 'index' as const,
    intersect: false,
  },
  plugins: {
    legend: {
      display: false
    },
    tooltip: {
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      titleColor: 'white',
      bodyColor: 'white',
      borderColor: 'rgba(255, 255, 255, 0.2)',
      borderWidth: 1,
      cornerRadius: 6,
      callbacks: {
        label: (context: any) => {
          const label = context.dataset.label || ''
          const value = context.parsed.y
          return `${label}: ${value}%`
        }
      }
    }
  },
  scales: {
    x: {
      display: false
    },
    y: {
      display: true,
      min: 0,
      max: 100,
      grid: {
        color: 'rgba(0, 0, 0, 0.05)'
      },
      ticks: {
        color: '#6b7280',
        font: {
          size: 10
        },
        callback: function(value: any) {
          return value + '%'
        }
      }
    }
  },
  elements: {
    point: {
      radius: 1,
      hoverRadius: 3
    }
  }
}
</script>

<style scoped>
.chart-container {
  position: relative;
  min-height: 200px;
}

.empty-state {
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-radius: 8px;
  border: 2px dashed #e2e8f0;
}

.resource-breakdown .flex:hover {
  background-color: #f9fafb;
  transform: translateX(2px);
  transition: all 0.2s ease-in-out;
}
</style>