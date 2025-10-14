<template>
  <div class="response-time-chart">
    <div class="chart-container" style="position: relative; height: 100%;">
      <Bar
        v-if="chartData && chartData.datasets"
        :data="chartData"
        :options="chartOptions"
      />
      <div v-else class="empty-state flex items-center justify-center h-full">
        <div class="text-center text-gray-500">
          <ClockIcon class="w-12 h-12 mx-auto mb-2 opacity-50" />
          <p class="text-sm">No response time data available</p>
        </div>
      </div>
    </div>

    <!-- Response Time Statistics -->
    <div v-if="statistics" class="response-stats mt-4 grid grid-cols-2 md:grid-cols-4 gap-4">
      <div class="stat-card bg-blue-50 p-3 rounded-lg">
        <div class="stat-value text-lg font-bold text-blue-600">{{ statistics.average }}ms</div>
        <div class="stat-label text-xs text-gray-600">Average</div>
      </div>

      <div class="stat-card bg-green-50 p-3 rounded-lg">
        <div class="stat-value text-lg font-bold text-green-600">{{ statistics.min }}ms</div>
        <div class="stat-label text-xs text-gray-600">Minimum</div>
      </div>

      <div class="stat-card bg-yellow-50 p-3 rounded-lg">
        <div class="stat-value text-lg font-bold text-yellow-600">{{ statistics.max }}ms</div>
        <div class="stat-label text-xs text-gray-600">Maximum</div>
      </div>

      <div class="stat-card bg-purple-50 p-3 rounded-lg">
        <div class="stat-value text-lg font-bold text-purple-600">{{ statistics.p95 }}ms</div>
        <div class="stat-label text-xs text-gray-600">95th Percentile</div>
      </div>
    </div>

    <!-- SLA Performance Indicators -->
    <div v-if="slaTargets.length > 0" class="sla-indicators mt-4">
      <h5 class="font-medium text-gray-900 mb-3">SLA Performance</h5>
      <div class="space-y-2">
        <div
          v-for="(sla, index) in slaTargets"
          :key="index"
          class="sla-item flex items-center justify-between p-3 bg-gray-50 rounded-lg"
        >
          <div class="sla-info">
            <div class="font-medium text-sm text-gray-900">{{ sla.name }}</div>
            <div class="text-xs text-gray-500">Target: {{ sla.target }}ms</div>
          </div>

          <div class="sla-status flex items-center space-x-2">
            <div class="flex items-center">
              <div class="w-20 bg-gray-200 rounded-full h-2">
                <div
                  class="h-2 rounded-full transition-all duration-300"
                  :class="{
                    'bg-green-500': sla.compliance >= 95,
                    'bg-yellow-500': sla.compliance >= 85 && sla.compliance < 95,
                    'bg-red-500': sla.compliance < 85
                  }"
                  :style="{ width: `${sla.compliance}%` }"
                ></div>
              </div>
              <span class="ml-2 text-sm text-gray-600 min-w-[3rem]">{{ sla.compliance }}%</span>
            </div>

            <component
              :is="sla.compliance >= 95 ? CheckCircleIcon : sla.compliance >= 85 ? ExclamationTriangleIcon : XCircleIcon"
              class="w-5 h-5"
              :class="{
                'text-green-500': sla.compliance >= 95,
                'text-yellow-500': sla.compliance >= 85 && sla.compliance < 95,
                'text-red-500': sla.compliance < 85
              }"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Response Time Distribution -->
    <div v-if="distributionData.length > 0" class="response-distribution mt-4">
      <h5 class="font-medium text-gray-900 mb-3">Response Time Distribution</h5>
      <div class="chart-container" style="height: 200px;">
        <Bar
          :data="distributionChartData"
          :options="distributionChartOptions"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import {
  ClockIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  XCircleIcon
} from '@heroicons/vue/24/outline'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js'
import { Bar } from 'vue-chartjs'

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
)

interface ResponseTimeDataPoint {
  timestamp: string | Date
  responseTime: number
  endpoint?: string
  operation?: string
  status?: 'success' | 'warning' | 'error'
}

interface SLATarget {
  name: string
  target: number
  compliance: number
}

interface Props {
  data: ResponseTimeDataPoint[]
  slaTargets?: SLATarget[]
}

const props = withDefaults(defineProps<Props>(), {
  slaTargets: () => [
    { name: 'API Endpoints', target: 200, compliance: 92 },
    { name: 'Database Queries', target: 100, compliance: 87 },
    { name: 'External Services', target: 500, compliance: 95 }
  ]
})

const statistics = computed(() => {
  if (!props.data || props.data.length === 0) return null

  const responseTimes = props.data.map(point => point.responseTime).filter(rt => rt > 0)

  if (responseTimes.length === 0) return null

  const sorted = [...responseTimes].sort((a, b) => a - b)
  const sum = responseTimes.reduce((acc, rt) => acc + rt, 0)

  return {
    average: Math.round(sum / responseTimes.length),
    min: Math.min(...responseTimes),
    max: Math.max(...responseTimes),
    p95: Math.round(sorted[Math.floor(sorted.length * 0.95)] || 0),
    p99: Math.round(sorted[Math.floor(sorted.length * 0.99)] || 0)
  }
})

const chartData = computed(() => {
  if (!props.data || props.data.length === 0) return null

  // Group data by time intervals (e.g., every 5 minutes)
  const timeGrouped = groupByTimeInterval(props.data, 5 * 60 * 1000) // 5 minutes

  const labels = timeGrouped.map(group => {
    const date = new Date(group.timestamp)
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  })

  const avgResponseTimes = timeGrouped.map(group => {
    const responseTimes = group.data.map(d => d.responseTime).filter(rt => rt > 0)
    return responseTimes.length > 0
      ? Math.round(responseTimes.reduce((sum, rt) => sum + rt, 0) / responseTimes.length)
      : 0
  })

  const maxResponseTimes = timeGrouped.map(group => {
    const responseTimes = group.data.map(d => d.responseTime).filter(rt => rt > 0)
    return responseTimes.length > 0 ? Math.max(...responseTimes) : 0
  })

  return {
    labels,
    datasets: [
      {
        label: 'Average Response Time',
        data: avgResponseTimes,
        backgroundColor: 'rgba(59, 130, 246, 0.6)',
        borderColor: 'rgb(59, 130, 246)',
        borderWidth: 1,
        borderRadius: 4,
        borderSkipped: false
      },
      {
        label: 'Peak Response Time',
        data: maxResponseTimes,
        backgroundColor: 'rgba(245, 158, 11, 0.6)',
        borderColor: 'rgb(245, 158, 11)',
        borderWidth: 1,
        borderRadius: 4,
        borderSkipped: false
      }
    ]
  }
})

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'top' as const,
      labels: {
        usePointStyle: true,
        pointStyle: 'rect',
        padding: 20,
        font: {
          size: 12
        }
      }
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
          const label = context.dataset.label || ''
          const value = context.parsed.y
          return `${label}: ${value}ms`
        }
      }
    }
  },
  scales: {
    x: {
      display: true,
      title: {
        display: true,
        text: 'Time',
        color: '#6b7280',
        font: {
          size: 12,
          weight: '500'
        }
      },
      grid: {
        color: 'rgba(0, 0, 0, 0.05)',
        drawBorder: false
      },
      ticks: {
        color: '#6b7280',
        font: {
          size: 11
        },
        maxTicksLimit: 10
      }
    },
    y: {
      display: true,
      title: {
        display: true,
        text: 'Response Time (ms)',
        color: '#6b7280',
        font: {
          size: 12,
          weight: '500'
        }
      },
      grid: {
        color: 'rgba(0, 0, 0, 0.05)',
        drawBorder: false
      },
      ticks: {
        color: '#6b7280',
        font: {
          size: 11
        },
        callback: function(value: any) {
          return value + 'ms'
        }
      },
      beginAtZero: true
    }
  },
  elements: {
    bar: {
      borderRadius: 4
    }
  }
}))

// Distribution data for histogram
const distributionData = computed(() => {
  if (!props.data || props.data.length === 0) return []

  const responseTimes = props.data.map(point => point.responseTime).filter(rt => rt > 0)

  if (responseTimes.length === 0) return []

  // Create buckets for histogram
  const max = Math.max(...responseTimes)
  const bucketSize = Math.ceil(max / 10)
  const buckets = []

  for (let i = 0; i < 10; i++) {
    const min = i * bucketSize
    const max = (i + 1) * bucketSize
    const count = responseTimes.filter(rt => rt >= min && rt < max).length

    buckets.push({
      range: `${min}-${max}ms`,
      count,
      percentage: Math.round((count / responseTimes.length) * 100)
    })
  }

  return buckets.filter(bucket => bucket.count > 0)
})

const distributionChartData = computed(() => {
  if (distributionData.value.length === 0) return null

  return {
    labels: distributionData.value.map(bucket => bucket.range),
    datasets: [
      {
        label: 'Request Count',
        data: distributionData.value.map(bucket => bucket.count),
        backgroundColor: 'rgba(16, 185, 129, 0.6)',
        borderColor: 'rgb(16, 185, 129)',
        borderWidth: 1,
        borderRadius: 4,
        borderSkipped: false
      }
    ]
  }
})

const distributionChartOptions = {
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
          const bucket = distributionData.value[context.dataIndex]
          return [
            `Count: ${bucket.count}`,
            `Percentage: ${bucket.percentage}%`
          ]
        }
      }
    }
  },
  scales: {
    x: {
      title: {
        display: true,
        text: 'Response Time Range',
        color: '#6b7280',
        font: {
          size: 11
        }
      },
      grid: {
        color: 'rgba(0, 0, 0, 0.05)'
      },
      ticks: {
        color: '#6b7280',
        font: {
          size: 10
        }
      }
    },
    y: {
      title: {
        display: true,
        text: 'Request Count',
        color: '#6b7280',
        font: {
          size: 11
        }
      },
      grid: {
        color: 'rgba(0, 0, 0, 0.05)'
      },
      ticks: {
        color: '#6b7280',
        font: {
          size: 10
        }
      },
      beginAtZero: true
    }
  }
}

// Utility function to group data by time intervals
function groupByTimeInterval(data: ResponseTimeDataPoint[], intervalMs: number) {
  const groups: { timestamp: string, data: ResponseTimeDataPoint[] }[] = []
  const sortedData = [...data].sort((a, b) =>
    new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
  )

  if (sortedData.length === 0) return groups

  const startTime = new Date(sortedData[0].timestamp).getTime()

  sortedData.forEach(point => {
    const pointTime = new Date(point.timestamp).getTime()
    const groupIndex = Math.floor((pointTime - startTime) / intervalMs)
    const groupTimestamp = new Date(startTime + groupIndex * intervalMs).toISOString()

    let group = groups.find(g => g.timestamp === groupTimestamp)
    if (!group) {
      group = { timestamp: groupTimestamp, data: [] }
      groups.push(group)
    }

    group.data.push(point)
  })

  return groups.sort((a, b) =>
    new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
  )
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

.stat-card {
  transition: transform 0.2s ease-in-out;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.sla-item {
  transition: all 0.2s ease-in-out;
}

.sla-item:hover {
  background-color: #f3f4f6;
  transform: translateX(2px);
}
</style>