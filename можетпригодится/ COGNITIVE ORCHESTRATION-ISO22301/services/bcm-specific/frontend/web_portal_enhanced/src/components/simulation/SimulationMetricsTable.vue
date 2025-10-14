<template>
  <div class="simulation-metrics-table">
    <div class="table-header mb-4">
      <div class="flex items-center justify-between">
        <div>
          <h4 class="text-lg font-semibold text-gray-900">Detailed Metrics</h4>
          <p class="text-sm text-gray-600">Comprehensive simulation performance data</p>
        </div>

        <div class="table-actions flex items-center space-x-2">
          <button
            @click="toggleAutoRefresh"
            :class="[
              'btn btn-sm flex items-center space-x-1',
              autoRefresh ? 'btn-primary' : 'btn-outline'
            ]"
          >
            <ArrowPathIcon class="w-3 h-3" :class="{ 'animate-spin': autoRefresh }" />
            <span class="text-xs">{{ autoRefresh ? 'Auto' : 'Manual' }}</span>
          </button>

          <button
            @click="exportToCSV"
            class="btn btn-outline btn-sm flex items-center space-x-1"
          >
            <ArrowDownTrayIcon class="w-3 h-3" />
            <span class="text-xs">Export</span>
          </button>

          <div class="relative">
            <button
              @click="showFilters = !showFilters"
              class="btn btn-outline btn-sm flex items-center space-x-1"
            >
              <FunnelIcon class="w-3 h-3" />
              <span class="text-xs">Filter</span>
            </button>

            <!-- Filter Dropdown -->
            <div
              v-if="showFilters"
              class="absolute right-0 mt-2 w-64 bg-white rounded-lg shadow-lg border z-10"
            >
              <div class="p-4">
                <h5 class="font-medium text-gray-900 mb-3">Filter Options</h5>

                <div class="space-y-3">
                  <div>
                    <label class="block text-xs font-medium text-gray-700 mb-1">Time Range</label>
                    <select v-model="filters.timeRange" class="w-full text-xs border rounded px-2 py-1">
                      <option value="1h">Last Hour</option>
                      <option value="6h">Last 6 Hours</option>
                      <option value="24h">Last 24 Hours</option>
                      <option value="all">All Time</option>
                    </select>
                  </div>

                  <div>
                    <label class="block text-xs font-medium text-gray-700 mb-1">Metric Type</label>
                    <select v-model="filters.metricType" class="w-full text-xs border rounded px-2 py-1">
                      <option value="all">All Metrics</option>
                      <option value="performance">Performance</option>
                      <option value="utilization">Utilization</option>
                      <option value="errors">Errors</option>
                    </select>
                  </div>

                  <div>
                    <label class="block text-xs font-medium text-gray-700 mb-1">Min Value</label>
                    <input
                      v-model="filters.minValue"
                      type="number"
                      class="w-full text-xs border rounded px-2 py-1"
                      placeholder="0"
                    />
                  </div>
                </div>

                <div class="flex items-center justify-between mt-4 pt-3 border-t">
                  <button @click="resetFilters" class="text-xs text-gray-500 hover:text-gray-700">
                    Reset
                  </button>
                  <button @click="applyFilters" class="btn btn-primary btn-xs">
                    Apply
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Metrics Summary Cards -->
    <div class="metrics-summary grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      <div class="summary-card bg-blue-50 p-4 rounded-lg">
        <div class="flex items-center justify-between">
          <div>
            <div class="text-2xl font-bold text-blue-600">{{ summary.totalRecords }}</div>
            <div class="text-xs text-gray-600">Total Records</div>
          </div>
          <ChartBarIcon class="w-8 h-8 text-blue-500 opacity-20" />
        </div>
      </div>

      <div class="summary-card bg-green-50 p-4 rounded-lg">
        <div class="flex items-center justify-between">
          <div>
            <div class="text-2xl font-bold text-green-600">{{ summary.avgUtilization }}%</div>
            <div class="text-xs text-gray-600">Avg Utilization</div>
          </div>
          <CpuChipIcon class="w-8 h-8 text-green-500 opacity-20" />
        </div>
      </div>

      <div class="summary-card bg-yellow-50 p-4 rounded-lg">
        <div class="flex items-center justify-between">
          <div>
            <div class="text-2xl font-bold text-yellow-600">{{ summary.peakValue }}</div>
            <div class="text-xs text-gray-600">Peak Value</div>
          </div>
          <ArrowTrendingUpIcon class="w-8 h-8 text-yellow-500 opacity-20" />
        </div>
      </div>

      <div class="summary-card bg-purple-50 p-4 rounded-lg">
        <div class="flex items-center justify-between">
          <div>
            <div class="text-2xl font-bold text-purple-600">{{ summary.anomalies }}</div>
            <div class="text-xs text-gray-600">Anomalies</div>
          </div>
          <ExclamationTriangleIcon class="w-8 h-8 text-purple-500 opacity-20" />
        </div>
      </div>
    </div>

    <!-- Main Data Table -->
    <div class="data-table bg-white border rounded-lg overflow-hidden">
      <div class="table-responsive">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th
                v-for="column in columns"
                :key="column.key"
                @click="sortBy(column.key)"
                class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
              >
                <div class="flex items-center space-x-1">
                  <span>{{ column.label }}</span>
                  <div class="flex flex-col">
                    <ChevronUpIcon
                      class="w-3 h-3"
                      :class="{
                        'text-blue-500': sortColumn === column.key && sortDirection === 'asc',
                        'text-gray-300': sortColumn !== column.key || sortDirection !== 'asc'
                      }"
                    />
                    <ChevronDownIcon
                      class="w-3 h-3 -mt-1"
                      :class="{
                        'text-blue-500': sortColumn === column.key && sortDirection === 'desc',
                        'text-gray-300': sortColumn !== column.key || sortDirection !== 'desc'
                      }"
                    />
                  </div>
                </div>
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr
              v-for="(row, index) in paginatedData"
              :key="index"
              class="hover:bg-gray-50 transition-colors"
            >
              <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-900">
                {{ formatTimestamp(row.timestamp) }}
              </td>
              <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-900">
                {{ row.processedEvents?.toLocaleString() || 0 }}
              </td>
              <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-900">
                {{ row.activeEntities || 0 }}
              </td>
              <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-900">
                {{ row.queueLength || 0 }}
              </td>
              <td class="px-4 py-3 whitespace-nowrap text-sm">
                <div class="flex items-center">
                  <div class="flex-1 bg-gray-200 rounded-full h-2 mr-2">
                    <div
                      class="h-2 rounded-full transition-all duration-300"
                      :class="{
                        'bg-green-500': row.utilization >= 0 && row.utilization < 60,
                        'bg-yellow-500': row.utilization >= 60 && row.utilization < 80,
                        'bg-red-500': row.utilization >= 80
                      }"
                      :style="{ width: `${row.utilization || 0}%` }"
                    ></div>
                  </div>
                  <span class="text-xs text-gray-600 min-w-[3rem]">{{ row.utilization || 0 }}%</span>
                </div>
              </td>
              <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-900">
                {{ row.responseTime || 0 }}ms
              </td>
              <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-900">
                {{ row.throughput || 0 }}/s
              </td>
              <td class="px-4 py-3 whitespace-nowrap text-sm">
                <span
                  class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium"
                  :class="{
                    'bg-green-100 text-green-800': row.status === 'normal',
                    'bg-yellow-100 text-yellow-800': row.status === 'warning',
                    'bg-red-100 text-red-800': row.status === 'error'
                  }"
                >
                  {{ row.status || 'normal' }}
                </span>
              </td>
              <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                <div class="flex items-center space-x-2">
                  <button
                    @click="viewDetails(row)"
                    class="text-blue-600 hover:text-blue-800"
                    title="View Details"
                  >
                    <EyeIcon class="w-4 h-4" />
                  </button>
                  <button
                    @click="exportRow(row)"
                    class="text-gray-600 hover:text-gray-800"
                    title="Export Row"
                  >
                    <ArrowDownTrayIcon class="w-4 h-4" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Empty State -->
      <div v-if="filteredData.length === 0" class="text-center py-12">
        <ChartBarIcon class="w-16 h-16 mx-auto text-gray-300 mb-4" />
        <h3 class="text-lg font-medium text-gray-900 mb-2">No data available</h3>
        <p class="text-gray-500">
          {{ filters.timeRange !== 'all' || filters.metricType !== 'all' || filters.minValue
            ? 'Try adjusting your filters'
            : 'Simulation metrics will appear here once the exercise starts'
          }}
        </p>
      </div>

      <!-- Pagination -->
      <div v-if="filteredData.length > 0" class="bg-gray-50 px-4 py-3 border-t">
        <div class="flex items-center justify-between">
          <div class="text-sm text-gray-700">
            Showing {{ (currentPage - 1) * pageSize + 1 }} to
            {{ Math.min(currentPage * pageSize, filteredData.length) }} of
            {{ filteredData.length }} results
          </div>

          <div class="flex items-center space-x-2">
            <button
              @click="previousPage"
              :disabled="currentPage === 1"
              class="btn btn-outline btn-sm"
            >
              <ChevronLeftIcon class="w-4 h-4" />
            </button>

            <div class="flex items-center space-x-1">
              <button
                v-for="page in visiblePages"
                :key="page"
                @click="currentPage = page"
                :class="[
                  'btn btn-sm',
                  page === currentPage ? 'btn-primary' : 'btn-outline'
                ]"
              >
                {{ page }}
              </button>
            </div>

            <button
              @click="nextPage"
              :disabled="currentPage === totalPages"
              class="btn btn-outline btn-sm"
            >
              <ChevronRightIcon class="w-4 h-4" />
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
  ArrowPathIcon,
  ArrowDownTrayIcon,
  FunnelIcon,
  ChartBarIcon,
  CpuChipIcon,
  ArrowTrendingUpIcon,
  ExclamationTriangleIcon,
  ChevronUpIcon,
  ChevronDownIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  EyeIcon
} from '@heroicons/vue/24/outline'

interface MetricData {
  timestamp: string
  processedEvents: number
  activeEntities: number
  queueLength: number
  utilization: number
  responseTime: number
  throughput: number
  status: 'normal' | 'warning' | 'error'
}

interface Props {
  data: MetricData[]
}

const props = defineProps<Props>()

// Reactive state
const autoRefresh = ref(false)
const showFilters = ref(false)
const currentPage = ref(1)
const pageSize = ref(25)
const sortColumn = ref('timestamp')
const sortDirection = ref<'asc' | 'desc'>('desc')

const filters = ref({
  timeRange: 'all',
  metricType: 'all',
  minValue: null
})

let refreshInterval: NodeJS.Timeout | null = null

// Table columns configuration
const columns = [
  { key: 'timestamp', label: 'Timestamp' },
  { key: 'processedEvents', label: 'Events' },
  { key: 'activeEntities', label: 'Entities' },
  { key: 'queueLength', label: 'Queue' },
  { key: 'utilization', label: 'Utilization' },
  { key: 'responseTime', label: 'Response Time' },
  { key: 'throughput', label: 'Throughput' },
  { key: 'status', label: 'Status' },
  { key: 'actions', label: 'Actions' }
]

// Computed properties
const filteredData = computed(() => {
  let data = [...(props.data || [])]

  // Apply time range filter
  if (filters.value.timeRange !== 'all') {
    const now = new Date()
    const hoursBack = parseInt(filters.value.timeRange.replace('h', ''))
    const cutoff = new Date(now.getTime() - hoursBack * 60 * 60 * 1000)

    data = data.filter(row => new Date(row.timestamp) >= cutoff)
  }

  // Apply metric type filter (this is a simplified example)
  if (filters.value.metricType !== 'all') {
    // In a real implementation, you might filter based on specific metric thresholds
    // For now, we'll just keep all data
  }

  // Apply minimum value filter
  if (filters.value.minValue !== null && filters.value.minValue !== '') {
    const minVal = parseFloat(filters.value.minValue.toString())
    data = data.filter(row => row.utilization >= minVal)
  }

  return data
})

const sortedData = computed(() => {
  const data = [...filteredData.value]

  return data.sort((a, b) => {
    let aVal = a[sortColumn.value]
    let bVal = b[sortColumn.value]

    // Handle timestamp sorting
    if (sortColumn.value === 'timestamp') {
      aVal = new Date(aVal).getTime()
      bVal = new Date(bVal).getTime()
    }

    // Handle numeric sorting
    if (typeof aVal === 'number' && typeof bVal === 'number') {
      return sortDirection.value === 'asc' ? aVal - bVal : bVal - aVal
    }

    // Handle string sorting
    const aStr = String(aVal).toLowerCase()
    const bStr = String(bVal).toLowerCase()

    if (sortDirection.value === 'asc') {
      return aStr < bStr ? -1 : aStr > bStr ? 1 : 0
    } else {
      return aStr > bStr ? -1 : aStr < bStr ? 1 : 0
    }
  })
})

const paginatedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return sortedData.value.slice(start, end)
})

const totalPages = computed(() => {
  return Math.ceil(filteredData.value.length / pageSize.value)
})

const visiblePages = computed(() => {
  const pages = []
  const start = Math.max(1, currentPage.value - 2)
  const end = Math.min(totalPages.value, currentPage.value + 2)

  for (let i = start; i <= end; i++) {
    pages.push(i)
  }

  return pages
})

const summary = computed(() => {
  const data = filteredData.value

  if (data.length === 0) {
    return {
      totalRecords: 0,
      avgUtilization: 0,
      peakValue: 0,
      anomalies: 0
    }
  }

  const totalUtilization = data.reduce((sum, row) => sum + (row.utilization || 0), 0)
  const avgUtilization = Math.round(totalUtilization / data.length)
  const peakValue = Math.max(...data.map(row => row.utilization || 0))
  const anomalies = data.filter(row => row.status === 'error').length

  return {
    totalRecords: data.length,
    avgUtilization,
    peakValue,
    anomalies
  }
})

// Methods
const toggleAutoRefresh = () => {
  autoRefresh.value = !autoRefresh.value

  if (autoRefresh.value) {
    refreshInterval = setInterval(() => {
      // Emit refresh event to parent component
      // In a real implementation, this would trigger data refresh
      console.log('Auto-refreshing metrics data...')
    }, 5000)
  } else if (refreshInterval) {
    clearInterval(refreshInterval)
    refreshInterval = null
  }
}

const sortBy = (column: string) => {
  if (column === 'actions') return

  if (sortColumn.value === column) {
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortColumn.value = column
    sortDirection.value = 'asc'
  }
}

const previousPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
  }
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
  }
}

const resetFilters = () => {
  filters.value = {
    timeRange: 'all',
    metricType: 'all',
    minValue: null
  }
  currentPage.value = 1
}

const applyFilters = () => {
  currentPage.value = 1
  showFilters.value = false
}

const exportToCSV = () => {
  const headers = ['Timestamp', 'Events', 'Entities', 'Queue', 'Utilization', 'Response Time', 'Throughput', 'Status']
  const rows = filteredData.value.map(row => [
    row.timestamp,
    row.processedEvents,
    row.activeEntities,
    row.queueLength,
    row.utilization,
    row.responseTime,
    row.throughput,
    row.status
  ])

  const csvContent = [
    headers.join(','),
    ...rows.map(row => row.join(','))
  ].join('\n')

  const blob = new Blob([csvContent], { type: 'text/csv' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `simulation-metrics-${Date.now()}.csv`
  a.click()
  URL.revokeObjectURL(url)
}

const exportRow = (row: MetricData) => {
  const csvContent = `${Object.keys(row).join(',')}\n${Object.values(row).join(',')}`
  const blob = new Blob([csvContent], { type: 'text/csv' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `metric-${row.timestamp}.csv`
  a.click()
  URL.revokeObjectURL(url)
}

const viewDetails = (row: MetricData) => {
  // In a real implementation, this might open a modal with detailed information
  console.log('Viewing details for:', row)
}

const formatTimestamp = (timestamp: string) => {
  return new Date(timestamp).toLocaleString()
}

// Lifecycle
onMounted(() => {
  // Component mounted
})

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
})
</script>

<style scoped>
.btn {
  @apply px-3 py-1.5 rounded font-medium transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed;
}

.btn-primary {
  @apply bg-blue-600 text-white hover:bg-blue-700;
}

.btn-outline {
  @apply border border-gray-300 text-gray-700 hover:bg-gray-50;
}

.btn-sm {
  @apply px-2 py-1 text-sm;
}

.btn-xs {
  @apply px-2 py-0.5 text-xs;
}

.table-responsive {
  max-height: 600px;
  overflow-y: auto;
}

.summary-card {
  transition: transform 0.2s ease-in-out;
}

.summary-card:hover {
  transform: translateY(-2px);
}

/* Custom scrollbar for table */
.table-responsive::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

.table-responsive::-webkit-scrollbar-track {
  background: #f1f5f9;
}

.table-responsive::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 4px;
}

.table-responsive::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}
</style>