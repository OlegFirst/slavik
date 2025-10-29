<template>
  <div class="risk-assessment">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">Risk Assessment</h1>
        <p class="page-subtitle">
          Identify, analyze, and evaluate potential risks to business operations
        </p>
      </div>
      <div class="header-actions">
        <Button
          variant="primary"
          leftIcon="PlusIcon"
          @click="showCreateModal = true"
        >
          New Risk Assessment
        </Button>
      </div>
    </div>

    <!-- Risk Matrix Overview -->
    <div class="risk-matrix-section">
      <Card title="Risk Matrix" :icon="ChartBarIcon" variant="elevated">
        <div class="risk-matrix">
          <div class="matrix-grid">
            <div class="matrix-header">
              <div></div>
              <div class="probability-label">Very Low</div>
              <div class="probability-label">Low</div>
              <div class="probability-label">Medium</div>
              <div class="probability-label">High</div>
              <div class="probability-label">Very High</div>
            </div>

            <div
              v-for="(impact, impactIndex) in impactLevels"
              :key="impact"
              class="matrix-row"
            >
              <div class="impact-label">{{ impact }}</div>
              <div
                v-for="(probability, probIndex) in probabilityLevels"
                :key="probability"
                class="matrix-cell"
                :class="getRiskLevelClass(impactIndex, probIndex)"
                @click="openRiskDetails(impactIndex, probIndex)"
              >
                <span class="risk-count">{{ getRiskCount(impactIndex, probIndex) }}</span>
              </div>
            </div>
          </div>

          <div class="risk-legend">
            <div class="legend-item low">
              <div class="legend-color"></div>
              <span>Low Risk</span>
            </div>
            <div class="legend-item medium">
              <div class="legend-color"></div>
              <span>Medium Risk</span>
            </div>
            <div class="legend-item high">
              <div class="legend-color"></div>
              <span>High Risk</span>
            </div>
            <div class="legend-item critical">
              <div class="legend-color"></div>
              <span>Critical Risk</span>
            </div>
          </div>
        </div>
      </Card>
    </div>

    <!-- Risk Statistics -->
    <div class="risk-stats">
      <div class="stats-grid">
        <Card v-for="stat in riskStats" :key="stat.label" variant="bordered">
          <div class="stat-content">
            <div class="stat-value" :class="stat.colorClass">{{ stat.value }}</div>
            <div class="stat-label">{{ stat.label }}</div>
            <div class="stat-change" :class="stat.changeClass">
              {{ stat.change }}
            </div>
          </div>
        </Card>
      </div>
    </div>

    <!-- Risk List -->
    <Card title="Risk Register" :icon="ListBulletIcon">
      <template #actions>
        <div class="flex items-center space-x-2">
          <select v-model="filterCategory" class="filter-select">
            <option value="">All Categories</option>
            <option value="operational">Operational</option>
            <option value="financial">Financial</option>
            <option value="strategic">Strategic</option>
            <option value="compliance">Compliance</option>
          </select>

          <select v-model="filterRiskLevel" class="filter-select">
            <option value="">All Risk Levels</option>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
            <option value="critical">Critical</option>
          </select>
        </div>
      </template>

      <div class="risk-table">
        <div class="table-header">
          <div class="header-cell">Risk ID</div>
          <div class="header-cell">Description</div>
          <div class="header-cell">Category</div>
          <div class="header-cell">Impact</div>
          <div class="header-cell">Probability</div>
          <div class="header-cell">Risk Level</div>
          <div class="header-cell">Owner</div>
          <div class="header-cell">Actions</div>
        </div>

        <div
          v-for="risk in filteredRisks"
          :key="risk.id"
          class="table-row"
        >
          <div class="table-cell">{{ risk.id }}</div>
          <div class="table-cell">
            <div class="risk-description">
              <h4 class="risk-title">{{ risk.title }}</h4>
              <p class="risk-subtitle">{{ risk.description }}</p>
            </div>
          </div>
          <div class="table-cell">
            <span class="category-badge" :class="getCategoryClass(risk.category)">
              {{ risk.category }}
            </span>
          </div>
          <div class="table-cell">{{ risk.impact }}</div>
          <div class="table-cell">{{ risk.probability }}</div>
          <div class="table-cell">
            <span class="risk-level-badge" :class="getRiskBadgeClass(risk.riskLevel)">
              {{ risk.riskLevel }}
            </span>
          </div>
          <div class="table-cell">{{ risk.owner }}</div>
          <div class="table-cell">
            <div class="action-buttons">
              <Button size="sm" variant="ghost" @click="viewRisk(risk.id)">
                View
              </Button>
              <Button size="sm" variant="ghost" @click="editRisk(risk.id)">
                Edit
              </Button>
            </div>
          </div>
        </div>
      </div>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ChartBarIcon, ListBulletIcon } from '@heroicons/vue/24/outline'
import Card from '@components/ui/Card.vue'
import Button from '@components/ui/Button.vue'

// Reactive data
const showCreateModal = ref(false)
const filterCategory = ref('')
const filterRiskLevel = ref('')

const impactLevels = ['Very High', 'High', 'Medium', 'Low', 'Very Low']
const probabilityLevels = ['Very Low', 'Low', 'Medium', 'High', 'Very High']

const riskStats = ref([
  {
    value: '23',
    label: 'Critical Risks',
    change: '+2 this month',
    colorClass: 'text-red-600',
    changeClass: 'text-red-500'
  },
  {
    value: '67',
    label: 'High Risks',
    change: '+5 this month',
    colorClass: 'text-orange-600',
    changeClass: 'text-orange-500'
  },
  {
    value: '124',
    label: 'Medium Risks',
    change: '-3 this month',
    colorClass: 'text-yellow-600',
    changeClass: 'text-green-500'
  },
  {
    value: '89',
    label: 'Low Risks',
    change: '+1 this month',
    colorClass: 'text-green-600',
    changeClass: 'text-green-500'
  }
])

const risks = ref([
  {
    id: 'RSK-001',
    title: 'Data Center Power Failure',
    description: 'Risk of power outage affecting primary data center operations',
    category: 'operational',
    impact: 'Very High',
    probability: 'Low',
    riskLevel: 'medium',
    owner: 'John Smith'
  },
  {
    id: 'RSK-002',
    title: 'Cybersecurity Breach',
    description: 'Risk of unauthorized access to sensitive customer data',
    category: 'security',
    impact: 'Very High',
    probability: 'Medium',
    riskLevel: 'high',
    owner: 'Sarah Johnson'
  },
  {
    id: 'RSK-003',
    title: 'Key Personnel Departure',
    description: 'Risk of critical staff leaving the organization',
    category: 'operational',
    impact: 'High',
    probability: 'Medium',
    riskLevel: 'medium',
    owner: 'Mike Davis'
  }
])

// Computed
const filteredRisks = computed(() => {
  return risks.value.filter(risk => {
    const categoryMatch = !filterCategory.value || risk.category === filterCategory.value
    const riskLevelMatch = !filterRiskLevel.value || risk.riskLevel === filterRiskLevel.value
    return categoryMatch && riskLevelMatch
  })
})

// Methods
function getRiskLevelClass(impactIndex: number, probIndex: number): string {
  const riskScore = impactIndex + probIndex
  if (riskScore >= 7) return 'matrix-critical'
  if (riskScore >= 5) return 'matrix-high'
  if (riskScore >= 3) return 'matrix-medium'
  return 'matrix-low'
}

function getRiskCount(impactIndex: number, probIndex: number): number {
  // Mock data - in real app, this would come from API
  return Math.floor(Math.random() * 10)
}

function getCategoryClass(category: string): string {
  const classes: Record<string, string> = {
    operational: 'category-operational',
    financial: 'category-financial',
    strategic: 'category-strategic',
    compliance: 'category-compliance',
    security: 'category-security'
  }
  return classes[category] || 'category-default'
}

function getRiskBadgeClass(riskLevel: string): string {
  const classes: Record<string, string> = {
    low: 'risk-low',
    medium: 'risk-medium',
    high: 'risk-high',
    critical: 'risk-critical'
  }
  return classes[riskLevel] || 'risk-low'
}

function openRiskDetails(impactIndex: number, probIndex: number): void {
  console.log('Opening risk details for matrix cell:', impactIndex, probIndex)
}

function viewRisk(riskId: string): void {
  console.log('Viewing risk:', riskId)
}

function editRisk(riskId: string): void {
  console.log('Editing risk:', riskId)
}
</script>

<style lang="scss" scoped>
.risk-assessment {
  @apply space-y-6;
}

.page-header {
  @apply flex items-center justify-between;
}

.header-content {
  @apply space-y-1;
}

.page-title {
  @apply text-2xl font-bold text-gray-900 dark:text-white;
}

.page-subtitle {
  @apply text-gray-600 dark:text-gray-400;
}

.header-actions {
  @apply flex items-center space-x-3;
}

.risk-matrix-section {
  @apply mb-8;
}

.risk-matrix {
  @apply space-y-6;
}

.matrix-grid {
  @apply grid grid-cols-6 gap-1 text-sm;
}

.matrix-header {
  @apply contents;

  .probability-label {
    @apply text-center font-medium text-gray-700 dark:text-gray-300 p-2;
  }
}

.matrix-row {
  @apply contents;
}

.impact-label {
  @apply flex items-center justify-center font-medium text-gray-700 dark:text-gray-300 p-2;
}

.matrix-cell {
  @apply aspect-square flex items-center justify-center cursor-pointer
         border border-gray-300 dark:border-gray-600 rounded transition-all
         hover:scale-105;

  &.matrix-low {
    @apply bg-green-200 text-green-800 hover:bg-green-300;
  }

  &.matrix-medium {
    @apply bg-yellow-200 text-yellow-800 hover:bg-yellow-300;
  }

  &.matrix-high {
    @apply bg-orange-200 text-orange-800 hover:bg-orange-300;
  }

  &.matrix-critical {
    @apply bg-red-200 text-red-800 hover:bg-red-300;
  }
}

.risk-count {
  @apply font-bold text-lg;
}

.risk-legend {
  @apply flex items-center justify-center space-x-6 pt-4;
}

.legend-item {
  @apply flex items-center space-x-2 text-sm;
}

.legend-color {
  @apply w-4 h-4 rounded;

  .legend-item.low & {
    @apply bg-green-200;
  }

  .legend-item.medium & {
    @apply bg-yellow-200;
  }

  .legend-item.high & {
    @apply bg-orange-200;
  }

  .legend-item.critical & {
    @apply bg-red-200;
  }
}

.risk-stats {
  @apply mb-8;
}

.stats-grid {
  @apply grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4;
}

.stat-content {
  @apply text-center space-y-2;
}

.stat-value {
  @apply text-3xl font-bold;
}

.stat-label {
  @apply text-sm font-medium text-gray-600 dark:text-gray-400;
}

.stat-change {
  @apply text-xs;
}

.filter-select {
  @apply px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md
         bg-white dark:bg-gray-700 text-sm;
}

.risk-table {
  @apply overflow-x-auto;
}

.table-header {
  @apply grid grid-cols-8 gap-4 p-4 bg-gray-50 dark:bg-gray-700
         text-sm font-medium text-gray-700 dark:text-gray-300 border-b;
}

.header-cell {
  @apply truncate;
}

.table-row {
  @apply grid grid-cols-8 gap-4 p-4 border-b border-gray-200 dark:border-gray-700
         hover:bg-gray-50 dark:hover:bg-gray-700/50;
}

.table-cell {
  @apply truncate text-sm;
}

.risk-description {
  @apply space-y-1;
}

.risk-title {
  @apply font-medium text-gray-900 dark:text-white;
}

.risk-subtitle {
  @apply text-gray-500 dark:text-gray-400 text-xs;
}

.category-badge {
  @apply px-2 py-1 text-xs font-medium rounded-full;

  &.category-operational {
    @apply bg-blue-100 text-blue-800 dark:bg-blue-900/50 dark:text-blue-300;
  }

  &.category-financial {
    @apply bg-green-100 text-green-800 dark:bg-green-900/50 dark:text-green-300;
  }

  &.category-strategic {
    @apply bg-purple-100 text-purple-800 dark:bg-purple-900/50 dark:text-purple-300;
  }

  &.category-compliance {
    @apply bg-indigo-100 text-indigo-800 dark:bg-indigo-900/50 dark:text-indigo-300;
  }

  &.category-security {
    @apply bg-red-100 text-red-800 dark:bg-red-900/50 dark:text-red-300;
  }
}

.risk-level-badge {
  @apply px-2 py-1 text-xs font-medium rounded-full;

  &.risk-low {
    @apply bg-green-100 text-green-800 dark:bg-green-900/50 dark:text-green-300;
  }

  &.risk-medium {
    @apply bg-yellow-100 text-yellow-800 dark:bg-yellow-900/50 dark:text-yellow-300;
  }

  &.risk-high {
    @apply bg-orange-100 text-orange-800 dark:bg-orange-900/50 dark:text-orange-300;
  }

  &.risk-critical {
    @apply bg-red-100 text-red-800 dark:bg-red-900/50 dark:text-red-300;
  }
}

.action-buttons {
  @apply flex items-center space-x-1;
}
</style>