<template>
  <div class="metrics-chart">
    <div class="chart-container" style="position: relative; height: 100%;">
      <Line
        v-if="chartData && chartData.datasets"
        :data="chartData"
        :options="chartOptions"
      />
      <div v-else class="empty-state flex items-center justify-center h-full">
        <div class="text-center text-gray-500">
          <ChartBarIcon class="w-12 h-12 mx-auto mb-2 opacity-50" />
          <p class="text-sm">No metrics data available</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ChartBarIcon } from '@heroicons/vue/24/outline'
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

interface MetricDataPoint {
  timestamp: string | Date
  processedEvents?: number
  activeEntities?: number
  queueLength?: number
  utilization?: number
  responseTime?: number
}

interface Props {
  data: MetricDataPoint[]
  type?: 'line' | 'area'
  showLegend?: boolean
  height?: number
}

const props = withDefaults(defineProps<Props>(), {
  type: 'line',
  showLegend: true,
  height: 300
})

const chartData = computed(() => {
  if (!props.data || props.data.length === 0) return null

  const labels = props.data.map(point => {
    const date = new Date(point.timestamp)
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  })

  const datasets = []

  // Events processed line
  if (props.data.some(point => point.processedEvents !== undefined)) {
    datasets.push({
      label: 'Events Processed',
      data: props.data.map(point => point.processedEvents || 0),
      borderColor: 'rgb(59, 130, 246)',
      backgroundColor: props.type === 'area' ? 'rgba(59, 130, 246, 0.1)' : 'rgba(59, 130, 246, 0.05)',
      fill: props.type === 'area',
      tension: 0.4,
      pointRadius: 2,
      pointHoverRadius: 6,
      borderWidth: 2,
      yAxisID: 'y'
    })
  }

  // Active entities line
  if (props.data.some(point => point.activeEntities !== undefined)) {
    datasets.push({
      label: 'Active Entities',
      data: props.data.map(point => point.activeEntities || 0),
      borderColor: 'rgb(16, 185, 129)',
      backgroundColor: props.type === 'area' ? 'rgba(16, 185, 129, 0.1)' : 'rgba(16, 185, 129, 0.05)',
      fill: props.type === 'area',
      tension: 0.4,
      pointRadius: 2,
      pointHoverRadius: 6,
      borderWidth: 2,
      yAxisID: 'y'
    })
  }

  // Queue length line
  if (props.data.some(point => point.queueLength !== undefined)) {
    datasets.push({
      label: 'Queue Length',
      data: props.data.map(point => point.queueLength || 0),
      borderColor: 'rgb(245, 158, 11)',
      backgroundColor: props.type === 'area' ? 'rgba(245, 158, 11, 0.1)' : 'rgba(245, 158, 11, 0.05)',
      fill: props.type === 'area',
      tension: 0.4,
      pointRadius: 2,
      pointHoverRadius: 6,
      borderWidth: 2,
      yAxisID: 'y'
    })
  }

  // Utilization percentage (on secondary axis)
  if (props.data.some(point => point.utilization !== undefined)) {
    datasets.push({
      label: 'Utilization (%)',
      data: props.data.map(point => point.utilization || 0),
      borderColor: 'rgb(236, 72, 153)',
      backgroundColor: props.type === 'area' ? 'rgba(236, 72, 153, 0.1)' : 'rgba(236, 72, 153, 0.05)',
      fill: props.type === 'area',
      tension: 0.4,
      pointRadius: 2,
      pointHoverRadius: 6,
      borderWidth: 2,
      yAxisID: 'y1'
    })
  }

  return {
    labels,
    datasets
  }
})

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  interaction: {
    mode: 'index' as const,
    intersect: false,
  },
  plugins: {
    legend: {
      display: props.showLegend,
      position: 'top' as const,
      labels: {
        usePointStyle: true,
        pointStyle: 'circle',
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
      displayColors: true,
      callbacks: {
        title: (context: any) => {
          const index = context[0].dataIndex
          const timestamp = props.data[index]?.timestamp
          return new Date(timestamp).toLocaleString()
        },
        label: (context: any) => {
          const label = context.dataset.label || ''
          const value = context.parsed.y

          if (label.includes('%')) {
            return `${label}: ${value}%`
          } else if (label.includes('Time')) {
            return `${label}: ${value}ms`
          } else {
            return `${label}: ${value.toLocaleString()}`
          }
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
      type: 'linear' as const,
      display: true,
      position: 'left' as const,
      title: {
        display: true,
        text: 'Count',
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
          if (value >= 1000000) {
            return (value / 1000000).toFixed(1) + 'M'
          } else if (value >= 1000) {
            return (value / 1000).toFixed(1) + 'K'
          }
          return value.toLocaleString()
        }
      }
    },
    y1: {
      type: 'linear' as const,
      display: props.data?.some(point => point.utilization !== undefined) || false,
      position: 'right' as const,
      title: {
        display: true,
        text: 'Utilization (%)',
        color: '#ec4899',
        font: {
          size: 12,
          weight: '500'
        }
      },
      grid: {
        drawOnChartArea: false,
        color: 'rgba(236, 72, 153, 0.1)'
      },
      ticks: {
        color: '#ec4899',
        font: {
          size: 11
        },
        callback: function(value: any) {
          return value + '%'
        }
      },
      min: 0,
      max: 100
    }
  },
  elements: {
    point: {
      radius: 2,
      hoverRadius: 6,
      hitRadius: 10
    },
    line: {
      borderWidth: 2
    }
  },
  animation: {
    duration: 750,
    easing: 'easeInOutQuart'
  }
}))
</script>

<style scoped>
.chart-container {
  min-height: 200px;
}

.empty-state {
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-radius: 8px;
  border: 2px dashed #e2e8f0;
}
</style>