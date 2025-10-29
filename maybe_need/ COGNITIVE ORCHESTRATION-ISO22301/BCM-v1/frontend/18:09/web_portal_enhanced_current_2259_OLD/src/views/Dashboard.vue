<template>
  <div class="dashboard">
    <!-- Dashboard Header -->
    <div class="dashboard-header">
      <div>
        <h1 class="dashboard-title">BCM Dashboard</h1>
        <p class="dashboard-subtitle">Business Continuity Management Overview</p>
      </div>
      <div class="header-actions">
        <button @click="refresh" class="refresh-button" :disabled="isLoading">
          <ArrowPathIcon class="w-4 h-4" :class="{ 'animate-spin': isLoading }" />
          Refresh
        </button>
      </div>
    </div>

    <!-- KPI Overview -->
    <div class="kpi-grid">
      <div v-for="kpi in kpiData" :key="kpi.id" class="kpi-card">
        <div class="kpi-header">
          <component :is="kpi.icon" class="kpi-icon" :class="kpi.iconColor" />
          <span class="kpi-trend" :class="kpi.trend">
            <ArrowUpIcon v-if="kpi.trend === 'up'" class="w-3 h-3" />
            <ArrowDownIcon v-if="kpi.trend === 'down'" class="w-3 h-3" />
          </span>
        </div>
        <div class="kpi-value">{{ kpi.value }}</div>
        <div class="kpi-label">{{ kpi.label }}</div>
        <div class="kpi-change" :class="kpi.changeType">
          {{ kpi.change }}
        </div>
      </div>
    </div>

    <!-- Main Content Grid -->
    <div class="content-grid">
      <!-- System Health -->
      <div class="dashboard-card">
        <div class="card-header">
          <h3 class="card-title">System Health</h3>
          <span class="health-status" :class="healthStatus.level">
            {{ healthStatus.label }}
          </span>
        </div>
        <div class="health-overview">
          <div class="health-circle" :class="healthStatus.level">
            <div class="health-percentage">{{ healthStatus.percentage }}%</div>
          </div>
        </div>
        <div class="health-status-text">{{ healthStatus.description }}</div>
        <div class="health-details">
          <div v-for="item in healthDetails" :key="item.name" class="health-item">
            <div class="flex items-center gap-2">
              <div class="health-indicator" :class="{ 'healthy': item.status === 'healthy' }"></div>
              <span class="text-sm text-slate-900 dark:text-white">{{ item.name }}</span>
            </div>
            <span class="health-value">{{ item.value }}</span>
          </div>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="dashboard-card">
        <div class="card-header">
          <h3 class="card-title">Quick Actions</h3>
        </div>
        <div class="quick-actions-grid">
          <button
            v-for="action in quickActions"
            :key="action.id"
            @click="executeAction(action.id)"
            class="quick-action-button"
          >
            <component :is="action.icon" class="action-icon" />
            <span class="action-title">{{ action.title }}</span>
            <span class="action-description">{{ action.description }}</span>
          </button>
        </div>
      </div>

      <!-- Recent Activity -->
      <div class="dashboard-card">
        <div class="card-header">
          <h3 class="card-title">Recent Activity</h3>
          <div class="activity-controls">
            <div class="activity-filters">
              <button
                v-for="filter in activityFilters"
                :key="filter"
                @click="activeFilter = filter"
                class="filter-button"
                :class="{ 'active': activeFilter === filter }"
              >
                {{ filter }}
              </button>
            </div>
            <div class="activity-live-indicator" :class="{ 'active': isLiveUpdates }">
              <div class="live-dot"></div>
              Live
            </div>
          </div>
        </div>
        <div class="activity-list">
          <div
            v-for="activity in filteredActivities"
            :key="activity.id"
            class="activity-item"
            @click="viewActivity(activity.id)"
          >
            <div class="activity-icon" :class="`activity-${activity.type}`">
              <component :is="activity.icon" class="w-4 h-4" />
            </div>
            <div class="activity-content">
              <div class="activity-header">
                <h4 class="activity-title">{{ activity.title }}</h4>
                <span class="activity-severity" :class="activity.severity">
                  {{ activity.severity }}
                </span>
              </div>
              <p class="activity-description">{{ activity.description }}</p>
              <div class="activity-meta">
                <span class="activity-user">{{ activity.user }}</span>
                <span>{{ formatTime(activity.timestamp) }}</span>
                <span>{{ activity.module }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Risk Overview -->
      <div class="dashboard-card">
        <div class="card-header">
          <h3 class="card-title">Risk Overview</h3>
        </div>
        <div class="risk-container">
          <div class="risk-chart">
            <!-- Chart will be rendered here -->
            <canvas ref="riskChart"></canvas>
          </div>
          <div class="risk-summary">
            <div class="risk-item high">
              <div class="risk-indicator"></div>
              <span>{{ riskData.high }} High</span>
            </div>
            <div class="risk-item medium">
              <div class="risk-indicator"></div>
              <span>{{ riskData.medium }} Medium</span>
            </div>
            <div class="risk-item low">
              <div class="risk-indicator"></div>
              <span>{{ riskData.low }} Low</span>
            </div>
          </div>
          <div class="risk-actions">
            <Button size="sm" variant="secondary" @click="viewRisks">
              View All Risks
            </Button>
            <Button size="sm" variant="primary" @click="createRisk">
              New Assessment
            </Button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import {
  ArrowPathIcon,
  ArrowUpIcon,
  ArrowDownIcon,
  ShieldExclamationIcon,
  DocumentTextIcon,
  ExclamationTriangleIcon,
  BellIcon,
  AcademicCapIcon,
  MagnifyingGlassIcon
} from '@heroicons/vue/24/outline'
import Button from '@/components/ui/Button.vue'

const router = useRouter()

// Reactive data
const isLoading = ref(false)
const isLiveUpdates = ref(true)
const activeFilter = ref('All')

// KPI Data
const kpiData = ref([
  {
    id: 'total-risks',
    label: 'Total Risks',
    value: '47',
    change: '+5 this month',
    changeType: 'positive',
    trend: 'up',
    icon: ShieldExclamationIcon,
    iconColor: 'text-red-500'
  },
  {
    id: 'bcp-plans',
    label: 'BCP Plans',
    value: '23',
    change: '+2 updated',
    changeType: 'positive',
    trend: 'up',
    icon: DocumentTextIcon,
    iconColor: 'text-blue-500'
  },
  {
    id: 'incidents',
    label: 'Open Incidents',
    value: '3',
    change: '-1 resolved',
    changeType: 'positive',
    trend: 'down',
    icon: ExclamationTriangleIcon,
    iconColor: 'text-yellow-500'
  },
  {
    id: 'compliance',
    label: 'Compliance Score',
    value: '94%',
    change: '+2% improved',
    changeType: 'positive',
    trend: 'up',
    icon: BellIcon,
    iconColor: 'text-green-500'
  }
])

// Health Status
const healthStatus = ref({
  percentage: 94,
  level: 'healthy',
  label: 'Healthy',
  description: 'All systems are operating normally'
})

const healthDetails = ref([
  { name: 'API Services', status: 'healthy', value: '99.9%' },
  { name: 'Database', status: 'healthy', value: '100%' },
  { name: 'Background Jobs', status: 'healthy', value: '98.5%' },
  { name: 'External Integrations', status: 'healthy', value: '97.2%' }
])

// Quick Actions
const quickActions = ref([
  {
    id: 'create-risk',
    title: 'New Risk Assessment',
    description: 'Start a new risk assessment',
    icon: ShieldExclamationIcon
  },
  {
    id: 'update-bcp',
    title: 'Update BCP',
    description: 'Review and update business continuity plans',
    icon: DocumentTextIcon
  },
  {
    id: 'schedule-training',
    title: 'Schedule Training',
    description: 'Plan new training sessions',
    icon: AcademicCapIcon
  },
  {
    id: 'run-audit',
    title: 'Run Audit',
    description: 'Initiate compliance audit',
    icon: MagnifyingGlassIcon
  }
])

// Activity Data
const activityFilters = ['All', 'Risk', 'BCP', 'Incidents', 'Training', 'Audit']

const activities = ref([
  {
    id: 1,
    type: 'risk',
    title: 'High-risk vulnerability identified',
    description: 'Critical security vulnerability found in payment processing system',
    severity: 'high',
    user: 'John Smith',
    timestamp: new Date(Date.now() - 1000 * 60 * 15),
    module: 'Risk Management',
    icon: ShieldExclamationIcon
  },
  {
    id: 2,
    type: 'bcp',
    title: 'BCP plan updated',
    description: 'Emergency response plan for data center outage has been revised',
    severity: 'medium',
    user: 'Sarah Johnson',
    timestamp: new Date(Date.now() - 1000 * 60 * 45),
    module: 'BCP Management',
    icon: DocumentTextIcon
  }
])

// Risk Data
const riskData = ref({
  high: 12,
  medium: 23,
  low: 12
})

// Computed
const filteredActivities = computed(() => {
  if (activeFilter.value === 'All') {
    return activities.value
  }
  return activities.value.filter(activity =>
    activity.type.toLowerCase() === activeFilter.value.toLowerCase()
  )
})

// Methods
const refresh = async () => {
  isLoading.value = true
  // Simulate API call
  await new Promise(resolve => setTimeout(resolve, 1000))
  isLoading.value = false
}

const executeAction = (actionId: string) => {
  switch (actionId) {
    case 'create-risk':
      router.push('/risk-assessment')
      break
    case 'update-bcp':
      router.push('/bcp-development')
      break
    case 'schedule-training':
      router.push('/training-management')
      break
    case 'run-audit':
      router.push('/audit-management')
      break
  }
}

const viewActivity = (activityId: number) => {
  console.log('View activity:', activityId)
}

const viewRisks = () => {
  router.push('/risk-assessment')
}

const createRisk = () => {
  router.push('/risk-assessment/new')
}

const formatTime = (timestamp: Date) => {
  const now = new Date()
  const diff = now.getTime() - timestamp.getTime()
  const minutes = Math.floor(diff / (1000 * 60))

  if (minutes < 60) {
    return `${minutes}m ago`
  }

  const hours = Math.floor(minutes / 60)
  if (hours < 24) {
    return `${hours}h ago`
  }

  const days = Math.floor(hours / 24)
  return `${days}d ago`
}

onMounted(() => {
  // Initialize dashboard
  refresh()
})
</script>

<style lang="scss" scoped>
.dashboard {
  @apply p-6 min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800;
}

.dashboard-header {
  @apply flex items-center justify-between mb-8;
}

.dashboard-title {
  @apply text-3xl font-bold text-slate-900 dark:text-white;
}

.dashboard-subtitle {
  @apply text-slate-600 dark:text-slate-400 mt-1;
}

.header-actions {
  @apply flex gap-3;
}

.refresh-button {
  @apply flex items-center gap-2 px-4 py-2 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors disabled:opacity-50;
}

.kpi-grid {
  @apply grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8;
}

.kpi-card {
  @apply bg-white dark:bg-slate-800 p-6 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700;
}

.kpi-header {
  @apply flex items-center justify-between mb-4;
}

.kpi-icon {
  @apply w-8 h-8;
}

.kpi-trend {
  @apply flex items-center justify-center w-6 h-6 rounded-full;

  &.up {
    @apply bg-green-100 text-green-600 dark:bg-green-900/50 dark:text-green-400;
  }

  &.down {
    @apply bg-red-100 text-red-600 dark:bg-red-900/50 dark:text-red-400;
  }
}

.kpi-value {
  @apply text-2xl font-bold text-slate-900 dark:text-white mb-1;
}

.kpi-label {
  @apply text-sm text-slate-600 dark:text-slate-400 mb-2;
}

.kpi-change {
  @apply text-xs font-medium;

  &.positive {
    @apply text-green-600 dark:text-green-400;
  }

  &.negative {
    @apply text-red-600 dark:text-red-400;
  }
}

.content-grid {
  @apply grid grid-cols-1 lg:grid-cols-2 gap-6;
}

.dashboard-card {
  @apply bg-white dark:bg-slate-800 p-6 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700;
}

.card-header {
  @apply flex items-center justify-between mb-6;
}

.card-title {
  @apply text-lg font-semibold text-slate-900 dark:text-white;
}

.health-status {
  @apply px-3 py-1 text-sm font-medium rounded-full;

  &.healthy {
    @apply bg-green-100 text-green-800 dark:bg-green-900/50 dark:text-green-300;
  }

  &.warning {
    @apply bg-yellow-100 text-yellow-800 dark:bg-yellow-900/50 dark:text-yellow-300;
  }

  &.critical {
    @apply bg-red-100 text-red-800 dark:bg-red-900/50 dark:text-red-300;
  }
}

.health-overview {
  @apply flex justify-center mb-6;
}

.health-circle {
  @apply w-24 h-24 rounded-full flex items-center justify-center text-center border-4 transition-all;

  &.healthy {
    @apply border-green-500 bg-green-50 dark:bg-green-900/20;
  }

  &.warning {
    @apply border-yellow-500 bg-yellow-50 dark:bg-yellow-900/20;
  }

  &.critical {
    @apply border-red-500 bg-red-50 dark:bg-red-900/20;
  }
}

.health-percentage {
  @apply text-xl font-bold text-slate-900 dark:text-white;
}

.health-status-text {
  @apply text-center text-sm text-slate-600 dark:text-slate-400 mt-2;
}

.health-details {
  @apply space-y-3;
}

.health-item {
  @apply flex items-center gap-3 justify-between;
}

.health-indicator {
  @apply w-3 h-3 rounded-full bg-red-500 flex-shrink-0;

  &.healthy {
    @apply bg-green-500;
  }
}

.health-value {
  @apply text-sm text-slate-600 dark:text-slate-400;
}

.activity-controls {
  @apply flex items-center justify-between mb-4 pb-3 border-b border-slate-200 dark:border-slate-700;
}

.activity-filters {
  @apply flex gap-2;
}

.filter-button {
  @apply px-3 py-1 text-sm rounded-full border border-slate-200 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors;

  &.active {
    @apply bg-blue-100 border-blue-300 text-blue-700 dark:bg-blue-900/50 dark:border-blue-600 dark:text-blue-300;
  }
}

.activity-live-indicator {
  @apply flex items-center gap-2 text-xs font-medium text-slate-500 dark:text-slate-500;

  &.active {
    @apply text-green-600 dark:text-green-400;
  }
}

.live-dot {
  @apply w-2 h-2 rounded-full bg-slate-400 dark:bg-slate-600;

  .activity-live-indicator.active & {
    @apply bg-green-500 animate-pulse;
  }
}

.activity-list {
  @apply space-y-3 max-h-96 overflow-y-auto;
}

.activity-item {
  @apply flex gap-3 p-3 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-800 cursor-pointer transition-colors;
}

.activity-icon {
  @apply flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center;

  &.activity-risk {
    @apply bg-red-100 text-red-600 dark:bg-red-900/50 dark:text-red-400;
  }

  &.activity-bcp {
    @apply bg-blue-100 text-blue-600 dark:bg-blue-900/50 dark:text-blue-400;
  }

  &.activity-incident {
    @apply bg-yellow-100 text-yellow-600 dark:bg-yellow-900/50 dark:text-yellow-400;
  }

  &.activity-training {
    @apply bg-purple-100 text-purple-600 dark:bg-purple-900/50 dark:text-purple-400;
  }

  &.activity-audit {
    @apply bg-green-100 text-green-600 dark:bg-green-900/50 dark:text-green-400;
  }
}

.activity-content {
  @apply flex-1 min-w-0;
}

.activity-header {
  @apply flex items-start justify-between gap-2 mb-1;
}

.activity-title {
  @apply text-sm font-medium text-slate-900 dark:text-white;
}

.activity-severity {
  @apply px-2 py-0.5 text-xs font-medium rounded-full flex-shrink-0;

  &.high {
    @apply bg-red-100 text-red-800 dark:bg-red-900/50 dark:text-red-300;
  }

  &.medium {
    @apply bg-yellow-100 text-yellow-800 dark:bg-yellow-900/50 dark:text-yellow-300;
  }

  &.low {
    @apply bg-green-100 text-green-800 dark:bg-green-900/50 dark:text-green-300;
  }
}

.activity-description {
  @apply text-sm text-slate-600 dark:text-slate-400 mb-2;
}

.activity-meta {
  @apply flex items-center gap-3 text-xs text-slate-500 dark:text-slate-500;
}

.activity-user {
  @apply font-medium;
}

.quick-actions-grid {
  @apply grid grid-cols-1 sm:grid-cols-2 gap-4;
}

.quick-action-button {
  @apply p-4 border border-slate-200 dark:border-slate-700 rounded-lg hover:shadow-md hover:border-blue-300 dark:hover:border-blue-600 transition-all text-left;
}

.action-icon {
  @apply w-8 h-8 text-blue-600 dark:text-blue-400 mb-2;
}

.action-title {
  @apply block font-semibold text-slate-900 dark:text-white mb-1;
}

.action-description {
  @apply block text-sm text-slate-600 dark:text-slate-400;
}

.risk-container {
  @apply space-y-4;
}

.risk-chart {
  @apply h-48 cursor-pointer;

  canvas {
    @apply w-full h-full;
  }
}

.risk-summary {
  @apply flex justify-around py-3 border-y border-slate-200 dark:border-slate-700;
}

.risk-item {
  @apply flex items-center gap-2 text-sm;
}

.risk-indicator {
  @apply w-3 h-3 rounded-full;

  .risk-item.high & {
    @apply bg-red-500;
  }

  .risk-item.medium & {
    @apply bg-yellow-500;
  }

  .risk-item.low & {
    @apply bg-green-500;
  }
}

.risk-actions {
  @apply flex gap-2;
}

// Responsive adjustments
@media (max-width: 768px) {
  .dashboard {
    @apply p-4;
  }

  .dashboard-header {
    @apply flex-col gap-4;
  }

  .content-grid {
    @apply grid-cols-1;
  }

  .kpi-grid {
    @apply grid-cols-1 sm:grid-cols-2;
  }
}

// Dark mode adjustments
@media (prefers-color-scheme: dark) {
  .dashboard {
    @apply bg-gradient-to-br from-slate-900 to-slate-800;
  }
}

// Print styles
@media print {
  .dashboard {
    @apply bg-white text-black;
  }

  .header-actions,
  .quick-actions-grid,
  .refresh-button {
    @apply hidden;
  }
}
</style>