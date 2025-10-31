<template>
  <div class="bcm-kpi">
    <!-- Header -->
    <div class="page-header">
      <div class="header-content">
        <h1>Performance Metrics & Analytics</h1>
        <p>Monitor KPIs, track performance trends, and gain actionable insights</p>
      </div>
      <div class="header-actions">
        <button @click="showCreateKpi = true" class="btn-primary">
          <i class="icon-plus"></i>
          New KPI
        </button>
        <button @click="showAssistant = true" class="btn-secondary">
          <i class="icon-ai"></i>
          AI Insights
        </button>
      </div>
    </div>

    <!-- KPI Summary Cards -->
    <div class="kpi-summary">
      <div class="summary-card total">
        <div class="card-icon">
          <i class="icon-gauge"></i>
        </div>
        <div class="card-content">
          <h3>{{ dashboardData.summary?.total || 0 }}</h3>
          <p>Total KPIs</p>
        </div>
      </div>
      <div class="summary-card green">
        <div class="card-icon">
          <i class="icon-check-circle"></i>
        </div>
        <div class="card-content">
          <h3>{{ dashboardData.summary?.green || 0 }}</h3>
          <p>On Target</p>
          <span class="percentage">{{ getPercentage('green') }}%</span>
        </div>
      </div>
      <div class="summary-card yellow">
        <div class="card-icon">
          <i class="icon-warning"></i>
        </div>
        <div class="card-content">
          <h3>{{ dashboardData.summary?.yellow || 0 }}</h3>
          <p>At Risk</p>
          <span class="percentage">{{ getPercentage('yellow') }}%</span>
        </div>
      </div>
      <div class="summary-card red">
        <div class="card-icon">
          <i class="icon-alert"></i>
        </div>
        <div class="card-content">
          <h3>{{ dashboardData.summary?.red || 0 }}</h3>
          <p>Off Target</p>
          <span class="percentage">{{ getPercentage('red') }}%</span>
        </div>
      </div>
    </div>

    <!-- Filters & Controls -->
    <div class="controls-section">
      <div class="filters-group">
        <div class="search-box">
          <input
            v-model="filters.search"
            type="text"
            placeholder="Search KPIs..."
            class="search-input"
          />
        </div>
        <select v-model="filters.category" class="filter-select">
          <option value="">All Categories</option>
          <option value="operational">Operational</option>
          <option value="financial">Financial</option>
          <option value="quality">Quality</option>
          <option value="customer">Customer</option>
          <option value="learning">Learning & Growth</option>
          <option value="risk">Risk Management</option>
        </select>
        <select v-model="filters.status" class="filter-select">
          <option value="">All Status</option>
          <option value="green">On Target</option>
          <option value="yellow">At Risk</option>
          <option value="red">Off Target</option>
        </select>
        <select v-model="viewMode" class="filter-select">
          <option value="cards">Card View</option>
          <option value="table">Table View</option>
          <option value="charts">Chart View</option>
        </select>
      </div>
      <div class="action-group">
        <button @click="exportData" class="btn-outline">
          <i class="icon-download"></i>
          Export
        </button>
        <button @click="generateReport" class="btn-outline">
          <i class="icon-report"></i>
          Report
        </button>
        <button @click="refreshData" class="btn-outline">
          <i class="icon-refresh"></i>
          Refresh
        </button>
      </div>
    </div>

    <!-- KPI Cards View -->
    <div v-if="viewMode === 'cards'" class="kpi-cards">
      <div
        v-for="kpi in filteredKpis"
        :key="kpi.id"
        class="kpi-card"
        @click="selectKpi(kpi)"
      >
        <div class="kpi-header">
          <div class="kpi-info">
            <h4>{{ kpi.name }}</h4>
            <span class="kpi-code">{{ kpi.code }}</span>
          </div>
          <div :class="['status-indicator', kpi.status]">
            <i :class="getStatusIcon(kpi.status)"></i>
          </div>
        </div>

        <div class="kpi-value">
          <div class="current-value">
            <span class="value">{{ formatValue(kpi.current_value, kpi.measurement_unit) }}</span>
            <span class="unit">{{ kpi.measurement_unit }}</span>
          </div>
          <div class="target-value">
            Target: {{ formatValue(kpi.target_value, kpi.measurement_unit) }}
          </div>
        </div>

        <div class="kpi-progress">
          <div class="progress-bar">
            <div
              :class="['progress-fill', kpi.status]"
              :style="{ width: `${calculateProgress(kpi)}%` }"
            ></div>
          </div>
          <div class="progress-labels">
            <span>0</span>
            <span>{{ kpi.target_value }}</span>
          </div>
        </div>

        <div class="kpi-trend">
          <div :class="['trend-indicator', kpi.trend]">
            <i :class="getTrendIcon(kpi.trend)"></i>
            <span>{{ formatTrend(kpi.trend) }}</span>
          </div>
          <div class="last-updated">
            Updated: {{ formatDate(kpi.last_updated) }}
          </div>
        </div>

        <div class="kpi-actions">
          <button @click.stop="updateKpiValue(kpi)" class="btn-sm">Update</button>
          <button @click.stop="viewTrends(kpi)" class="btn-sm">Trends</button>
          <button @click.stop="editKpi(kpi)" class="btn-sm btn-primary">Edit</button>
        </div>
      </div>
    </div>

    <!-- Table View -->
    <div v-if="viewMode === 'table'" class="kpi-table">
      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>KPI Name</th>
              <th>Category</th>
              <th>Current Value</th>
              <th>Target</th>
              <th>Progress</th>
              <th>Status</th>
              <th>Trend</th>
              <th>Last Updated</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="kpi in filteredKpis" :key="kpi.id">
              <td>
                <div class="kpi-name-cell">
                  <strong>{{ kpi.name }}</strong>
                  <span class="kpi-code">{{ kpi.code }}</span>
                </div>
              </td>
              <td>
                <span :class="['category-badge', kpi.category]">
                  {{ formatCategory(kpi.category) }}
                </span>
              </td>
              <td class="value-cell">
                {{ formatValue(kpi.current_value, kpi.measurement_unit) }}
              </td>
              <td class="value-cell">
                {{ formatValue(kpi.target_value, kpi.measurement_unit) }}
              </td>
              <td>
                <div class="progress-cell">
                  <div class="mini-progress-bar">
                    <div
                      :class="['mini-progress-fill', kpi.status]"
                      :style="{ width: `${calculateProgress(kpi)}%` }"
                    ></div>
                  </div>
                  <span>{{ calculateProgress(kpi) }}%</span>
                </div>
              </td>
              <td>
                <span :class="['status-badge', kpi.status]">
                  {{ formatStatus(kpi.status) }}
                </span>
              </td>
              <td>
                <div :class="['trend-cell', kpi.trend]">
                  <i :class="getTrendIcon(kpi.trend)"></i>
                  {{ formatTrend(kpi.trend) }}
                </div>
              </td>
              <td>{{ formatDate(kpi.last_updated) }}</td>
              <td>
                <div class="action-buttons">
                  <button @click="viewKpiDetail(kpi)" class="btn-icon" title="View">
                    <i class="icon-view"></i>
                  </button>
                  <button @click="updateKpiValue(kpi)" class="btn-icon" title="Update">
                    <i class="icon-edit"></i>
                  </button>
                  <button @click="viewTrends(kpi)" class="btn-icon" title="Trends">
                    <i class="icon-chart"></i>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Charts View -->
    <div v-if="viewMode === 'charts'" class="charts-view">
      <div class="charts-grid">
        <div class="chart-container">
          <h3>KPI Status Distribution</h3>
          <div class="chart-placeholder">
            <!-- Pie chart showing status distribution -->
            <canvas ref="statusChart"></canvas>
          </div>
        </div>
        <div class="chart-container">
          <h3>Performance Trends</h3>
          <div class="chart-placeholder">
            <!-- Line chart showing trends -->
            <canvas ref="trendsChart"></canvas>
          </div>
        </div>
        <div class="chart-container">
          <h3>Category Performance</h3>
          <div class="chart-placeholder">
            <!-- Bar chart by category -->
            <canvas ref="categoryChart"></canvas>
          </div>
        </div>
        <div class="chart-container">
          <h3>Target Achievement</h3>
          <div class="chart-placeholder">
            <!-- Gauge charts for top KPIs -->
            <canvas ref="achievementChart"></canvas>
          </div>
        </div>
      </div>
    </div>

    <!-- AI Insights Panel -->
    <div v-if="showInsights" class="insights-panel">
      <div class="insights-header">
        <h3>AI Insights & Recommendations</h3>
        <button @click="showInsights = false" class="close-btn">&times;</button>
      </div>
      <div class="insights-content">
        <div v-if="aiInsights.patterns?.length" class="insight-section">
          <h4>Patterns Detected</h4>
          <ul>
            <li v-for="pattern in aiInsights.patterns" :key="pattern.id">
              {{ pattern.description }}
            </li>
          </ul>
        </div>
        <div v-if="aiInsights.recommendations?.length" class="insight-section">
          <h4>Recommendations</h4>
          <ul>
            <li v-for="rec in aiInsights.recommendations" :key="rec.id">
              {{ rec.description }}
            </li>
          </ul>
        </div>
        <div v-if="aiInsights.anomalies?.length" class="insight-section">
          <h4>Anomalies Detected</h4>
          <ul>
            <li v-for="anomaly in aiInsights.anomalies" :key="anomaly.id">
              {{ anomaly.description }}
            </li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Assistant Panel -->
    <AssistantPanel
      v-if="showAssistant"
      @close="showAssistant = false"
      :context="assistantContext"
      module="kpi"
    />

    <!-- Create KPI Modal -->
    <div v-if="showCreateKpi" class="modal-overlay" @click="closeCreateModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Create New KPI</h3>
          <button @click="closeCreateModal" class="close-btn">&times;</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="createKpi">
            <div class="form-grid">
              <div class="form-group">
                <label>KPI Name</label>
                <input v-model="newKpi.name" type="text" required />
              </div>
              <div class="form-group">
                <label>KPI Code</label>
                <input v-model="newKpi.code" type="text" required />
              </div>
              <div class="form-group">
                <label>Category</label>
                <select v-model="newKpi.category" required>
                  <option value="operational">Operational</option>
                  <option value="financial">Financial</option>
                  <option value="quality">Quality</option>
                  <option value="customer">Customer</option>
                  <option value="learning">Learning & Growth</option>
                  <option value="risk">Risk Management</option>
                </select>
              </div>
              <div class="form-group">
                <label>Measurement Unit</label>
                <input v-model="newKpi.measurement_unit" type="text" required />
              </div>
              <div class="form-group">
                <label>Target Value</label>
                <input v-model="newKpi.target_value" type="number" step="0.01" required />
              </div>
              <div class="form-group">
                <label>Green Threshold</label>
                <input v-model="newKpi.threshold_green" type="number" step="0.01" required />
              </div>
              <div class="form-group">
                <label>Yellow Threshold</label>
                <input v-model="newKpi.threshold_yellow" type="number" step="0.01" required />
              </div>
              <div class="form-group">
                <label>Red Threshold</label>
                <input v-model="newKpi.threshold_red" type="number" step="0.01" required />
              </div>
              <div class="form-group full-width">
                <label>Description</label>
                <textarea v-model="newKpi.description" rows="3"></textarea>
              </div>
              <div class="form-group">
                <label>Calculation Method</label>
                <select v-model="newKpi.calculation_method">
                  <option value="manual">Manual Entry</option>
                  <option value="formula">Formula-based</option>
                  <option value="external">External Data</option>
                </select>
              </div>
              <div class="form-group">
                <label>Update Frequency</label>
                <select v-model="newKpi.frequency">
                  <option value="daily">Daily</option>
                  <option value="weekly">Weekly</option>
                  <option value="monthly">Monthly</option>
                  <option value="quarterly">Quarterly</option>
                </select>
              </div>
            </div>
            <div class="form-options">
              <label class="checkbox-label">
                <input v-model="newKpi.dashboard_visible" type="checkbox" />
                Show on Dashboard
              </label>
            </div>
            <div class="modal-actions">
              <button type="button" @click="closeCreateModal" class="btn-secondary">Cancel</button>
              <button type="submit" class="btn-primary">Create KPI</button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Update Value Modal -->
    <div v-if="showUpdateValue" class="modal-overlay" @click="closeUpdateModal">
      <div class="modal-content small" @click.stop>
        <div class="modal-header">
          <h3>Update KPI Value</h3>
          <button @click="closeUpdateModal" class="close-btn">&times;</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="saveKpiValue">
            <div class="form-group">
              <label>KPI: {{ selectedKpi?.name }}</label>
              <p class="kpi-current">Current: {{ formatValue(selectedKpi?.current_value, selectedKpi?.measurement_unit) }}</p>
            </div>
            <div class="form-group">
              <label>New Value</label>
              <input v-model="updateValue" type="number" step="0.01" required />
            </div>
            <div class="form-group">
              <label>Date</label>
              <input v-model="updateDate" type="date" />
            </div>
            <div class="modal-actions">
              <button type="button" @click="closeUpdateModal" class="btn-secondary">Cancel</button>
              <button type="submit" class="btn-primary">Update</button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Loading Overlay -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading-spinner"></div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { bcmKpiService } from '@/services/bcmKpi'
import AssistantPanel from '@/components/assistant/AssistantPanel.vue'

export default {
  name: 'BcmKpi',
  components: {
    AssistantPanel
  },
  setup() {
    // Reactive data
    const kpis = ref([])
    const dashboardData = ref({})
    const aiInsights = ref({})
    const loading = ref(false)
    const showAssistant = ref(false)
    const showInsights = ref(false)
    const showCreateKpi = ref(false)
    const showUpdateValue = ref(false)
    const selectedKpi = ref(null)
    const viewMode = ref('cards')

    // Filters
    const filters = reactive({
      search: '',
      category: '',
      status: '',
      responsible_id: ''
    })

    // Form data
    const newKpi = reactive({
      name: '',
      code: '',
      description: '',
      category: 'operational',
      measurement_unit: '',
      target_value: 0,
      threshold_green: 0,
      threshold_yellow: 0,
      threshold_red: 0,
      calculation_method: 'manual',
      frequency: 'monthly',
      dashboard_visible: true
    })

    const updateValue = ref('')
    const updateDate = ref(new Date().toISOString().split('T')[0])

    // Computed properties
    const filteredKpis = computed(() => {
      return kpis.value.filter(kpi => {
        const matchesSearch = !filters.search ||
          kpi.name.toLowerCase().includes(filters.search.toLowerCase()) ||
          kpi.code.toLowerCase().includes(filters.search.toLowerCase())
        const matchesCategory = !filters.category ||
          kpi.category === filters.category
        const matchesStatus = !filters.status ||
          kpi.status === filters.status

        return matchesSearch && matchesCategory && matchesStatus
      })
    })

    const assistantContext = computed(() => ({
      module: 'kpi',
      totalKpis: kpis.value.length,
      onTargetKpis: kpis.value.filter(k => k.status === 'green').length,
      atRiskKpis: kpis.value.filter(k => k.status === 'yellow').length,
      offTargetKpis: kpis.value.filter(k => k.status === 'red').length,
      filters: filters
    }))

    // Methods
    const loadData = async () => {
      loading.value = true
      try {
        const [kpiData, dashboard, insights] = await Promise.all([
          bcmKpiService.getKpis(filters),
          bcmKpiService.getDashboardData(filters),
          bcmKpiService.getAiInsights()
        ])

        kpis.value = kpiData || []
        dashboardData.value = dashboard || {}
        aiInsights.value = insights || {}
      } catch (error) {
        console.error('Error loading KPI data:', error)
      } finally {
        loading.value = false
      }
    }

    const createKpi = async () => {
      try {
        loading.value = true
        await bcmKpiService.createKpi(newKpi)
        await loadData()
        closeCreateModal()
        resetNewKpi()
      } catch (error) {
        console.error('Error creating KPI:', error)
      } finally {
        loading.value = false
      }
    }

    const updateKpiValue = (kpi) => {
      selectedKpi.value = kpi
      updateValue.value = kpi.current_value
      showUpdateValue.value = true
    }

    const saveKpiValue = async () => {
      try {
        loading.value = true
        await bcmKpiService.updateKpiValue(
          selectedKpi.value.id,
          parseFloat(updateValue.value),
          updateDate.value
        )
        await loadData()
        closeUpdateModal()
      } catch (error) {
        console.error('Error updating KPI value:', error)
      } finally {
        loading.value = false
      }
    }

    const selectKpi = (kpi) => {
      selectedKpi.value = kpi
      // Show KPI detail view or modal
    }

    const viewKpiDetail = (kpi) => {
      selectedKpi.value = kpi
      // Navigate to detail view
    }

    const editKpi = (kpi) => {
      // Open edit modal
      console.log('Edit KPI:', kpi)
    }

    const viewTrends = async (kpi) => {
      try {
        const trends = await bcmKpiService.getKpiTrends(kpi.id)
        console.log('KPI trends:', trends)
        // Show trends modal or navigate to trends view
      } catch (error) {
        console.error('Error fetching trends:', error)
      }
    }

    const exportData = async () => {
      try {
        loading.value = true
        const exportData = await bcmKpiService.exportKpiData(filters, 'xlsx')
        // Handle file download
        console.log('Export data:', exportData)
      } catch (error) {
        console.error('Error exporting data:', error)
      } finally {
        loading.value = false
      }
    }

    const generateReport = async () => {
      try {
        loading.value = true
        const report = await bcmKpiService.generateKpiReport(filters)
        // Handle report generation
        console.log('Generated report:', report)
      } catch (error) {
        console.error('Error generating report:', error)
      } finally {
        loading.value = false
      }
    }

    const refreshData = () => {
      loadData()
    }

    const closeCreateModal = () => {
      showCreateKpi.value = false
    }

    const closeUpdateModal = () => {
      showUpdateValue.value = false
      selectedKpi.value = null
    }

    const resetNewKpi = () => {
      Object.keys(newKpi).forEach(key => {
        if (typeof newKpi[key] === 'string') {
          newKpi[key] = ''
        } else if (typeof newKpi[key] === 'number') {
          newKpi[key] = 0
        } else if (typeof newKpi[key] === 'boolean') {
          newKpi[key] = key === 'dashboard_visible'
        }
      })
      newKpi.category = 'operational'
      newKpi.calculation_method = 'manual'
      newKpi.frequency = 'monthly'
    }

    // Utility functions
    const formatValue = (value, unit) => {
      if (value == null) return '—'
      return `${parseFloat(value).toLocaleString()}`
    }

    const formatDate = (date) => {
      return date ? new Date(date).toLocaleDateString() : ''
    }

    const formatCategory = (category) => {
      const categories = {
        operational: 'Operational',
        financial: 'Financial',
        quality: 'Quality',
        customer: 'Customer',
        learning: 'Learning & Growth',
        risk: 'Risk Management'
      }
      return categories[category] || category
    }

    const formatStatus = (status) => {
      const statuses = {
        green: 'On Target',
        yellow: 'At Risk',
        red: 'Off Target'
      }
      return statuses[status] || status
    }

    const formatTrend = (trend) => {
      const trends = {
        increasing: 'Improving',
        decreasing: 'Declining',
        stable: 'Stable'
      }
      return trends[trend] || trend
    }

    const getStatusIcon = (status) => {
      const icons = {
        green: 'icon-check-circle',
        yellow: 'icon-warning',
        red: 'icon-alert'
      }
      return icons[status] || 'icon-help'
    }

    const getTrendIcon = (trend) => {
      const icons = {
        increasing: 'icon-arrow-up',
        decreasing: 'icon-arrow-down',
        stable: 'icon-minus'
      }
      return icons[trend] || 'icon-minus'
    }

    const calculateProgress = (kpi) => {
      if (!kpi.current_value || !kpi.target_value) return 0
      return Math.min(100, Math.max(0, (kpi.current_value / kpi.target_value) * 100))
    }

    const getPercentage = (status) => {
      const total = dashboardData.value.summary?.total || 0
      if (total === 0) return 0
      const count = dashboardData.value.summary?.[status] || 0
      return Math.round((count / total) * 100)
    }

    // Watchers
    watch(filters, () => {
      loadData()
    }, { deep: true })

    // Lifecycle
    onMounted(() => {
      loadData()
    })

    return {
      // Data
      kpis,
      dashboardData,
      aiInsights,
      loading,
      showAssistant,
      showInsights,
      showCreateKpi,
      showUpdateValue,
      selectedKpi,
      viewMode,
      filters,
      newKpi,
      updateValue,
      updateDate,

      // Computed
      filteredKpis,
      assistantContext,

      // Methods
      loadData,
      createKpi,
      updateKpiValue,
      saveKpiValue,
      selectKpi,
      viewKpiDetail,
      editKpi,
      viewTrends,
      exportData,
      generateReport,
      refreshData,
      closeCreateModal,
      closeUpdateModal,
      resetNewKpi,
      formatValue,
      formatDate,
      formatCategory,
      formatStatus,
      formatTrend,
      getStatusIcon,
      getTrendIcon,
      calculateProgress,
      getPercentage
    }
  }
}
</script>

<style scoped>
.bcm-kpi {
  padding: 24px;
  background: #f8f9fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 32px;
  padding: 24px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.header-content h1 {
  color: #1A1A1A;
  margin: 0 0 8px 0;
  font-size: 28px;
  font-weight: 600;
}

.header-content p {
  color: #666;
  margin: 0;
  font-size: 16px;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.btn-primary, .btn-secondary, .btn-outline {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: #FF6B35;
  color: white;
}

.btn-primary:hover {
  background: #e55a2b;
  transform: translateY(-1px);
}

.btn-secondary {
  background: #4A90E2;
  color: white;
}

.btn-secondary:hover {
  background: #357abd;
  transform: translateY(-1px);
}

.btn-outline {
  background: white;
  color: #666;
  border: 2px solid #e1e5e9;
}

.btn-outline:hover {
  border-color: #4A90E2;
  color: #4A90E2;
  transform: translateY(-1px);
}

.kpi-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.summary-card {
  display: flex;
  align-items: center;
  padding: 24px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: transform 0.2s;
}

.summary-card:hover {
  transform: translateY(-2px);
}

.summary-card.total .card-icon {
  background: linear-gradient(135deg, #1A1A1A, #4A90E2);
}

.summary-card.green .card-icon {
  background: linear-gradient(135deg, #4caf50, #81c784);
}

.summary-card.yellow .card-icon {
  background: linear-gradient(135deg, #ff9800, #ffb74d);
}

.summary-card.red .card-icon {
  background: linear-gradient(135deg, #f44336, #e57373);
}

.card-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
}

.card-icon i {
  font-size: 24px;
  color: white;
}

.card-content h3 {
  margin: 0 0 4px 0;
  font-size: 32px;
  font-weight: 700;
  color: #1A1A1A;
}

.card-content p {
  margin: 0 0 4px 0;
  color: #666;
  font-size: 14px;
}

.percentage {
  font-size: 12px;
  color: #4A90E2;
  font-weight: 500;
}

.controls-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding: 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.filters-group {
  display: flex;
  gap: 16px;
  flex: 1;
}

.search-box {
  flex: 1;
  max-width: 300px;
}

.search-input {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e1e5e9;
  border-radius: 8px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.search-input:focus {
  outline: none;
  border-color: #4A90E2;
}

.filter-select {
  padding: 12px 16px;
  border: 2px solid #e1e5e9;
  border-radius: 8px;
  background: white;
  font-size: 14px;
  min-width: 150px;
}

.action-group {
  display: flex;
  gap: 12px;
}

.kpi-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 24px;
}

.kpi-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  padding: 24px;
  cursor: pointer;
  transition: all 0.2s;
}

.kpi-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.kpi-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}

.kpi-info h4 {
  margin: 0 0 4px 0;
  color: #1A1A1A;
  font-weight: 600;
  font-size: 18px;
}

.kpi-code {
  color: #666;
  font-size: 14px;
  font-weight: 500;
}

.status-indicator {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.status-indicator.green {
  background: #e8f5e8;
  color: #4caf50;
}

.status-indicator.yellow {
  background: #fff3e0;
  color: #ff9800;
}

.status-indicator.red {
  background: #ffebee;
  color: #f44336;
}

.kpi-value {
  margin-bottom: 20px;
}

.current-value {
  display: flex;
  align-items: baseline;
  gap: 8px;
  margin-bottom: 8px;
}

.current-value .value {
  font-size: 32px;
  font-weight: 700;
  color: #1A1A1A;
}

.current-value .unit {
  font-size: 16px;
  color: #666;
  font-weight: 500;
}

.target-value {
  color: #666;
  font-size: 14px;
}

.kpi-progress {
  margin-bottom: 20px;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: #e1e5e9;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 8px;
}

.progress-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s;
}

.progress-fill.green {
  background: linear-gradient(90deg, #4caf50, #81c784);
}

.progress-fill.yellow {
  background: linear-gradient(90deg, #ff9800, #ffb74d);
}

.progress-fill.red {
  background: linear-gradient(90deg, #f44336, #e57373);
}

.progress-labels {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #666;
}

.kpi-trend {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.trend-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 500;
}

.trend-indicator.increasing {
  color: #4caf50;
}

.trend-indicator.decreasing {
  color: #f44336;
}

.trend-indicator.stable {
  color: #666;
}

.last-updated {
  color: #666;
  font-size: 12px;
}

.kpi-actions {
  display: flex;
  gap: 12px;
}

.btn-sm {
  padding: 8px 16px;
  border: 2px solid #e1e5e9;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-sm:hover {
  border-color: #4A90E2;
  color: #4A90E2;
}

.btn-sm.btn-primary {
  background: #FF6B35;
  border-color: #FF6B35;
  color: white;
}

.btn-sm.btn-primary:hover {
  background: #e55a2b;
}

.table-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  background: #f8f9fa;
  padding: 16px;
  text-align: left;
  font-weight: 600;
  color: #1A1A1A;
  border-bottom: 1px solid #e1e5e9;
}

.data-table td {
  padding: 16px;
  border-bottom: 1px solid #e1e5e9;
}

.kpi-name-cell strong {
  display: block;
  color: #1A1A1A;
  margin-bottom: 4px;
}

.category-badge {
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  text-transform: capitalize;
}

.category-badge.operational { background: #e3f2fd; color: #1976d2; }
.category-badge.financial { background: #e8f5e8; color: #388e3c; }
.category-badge.quality { background: #f3e5f5; color: #7b1fa2; }
.category-badge.customer { background: #fff3e0; color: #f57c00; }
.category-badge.learning { background: #e1f5fe; color: #0288d1; }
.category-badge.risk { background: #ffebee; color: #d32f2f; }

.value-cell {
  font-weight: 600;
  color: #1A1A1A;
}

.progress-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.mini-progress-bar {
  width: 60px;
  height: 4px;
  background: #e1e5e9;
  border-radius: 2px;
  overflow: hidden;
}

.mini-progress-fill {
  height: 100%;
  border-radius: 2px;
}

.mini-progress-fill.green { background: #4caf50; }
.mini-progress-fill.yellow { background: #ff9800; }
.mini-progress-fill.red { background: #f44336; }

.status-badge {
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.green { background: #e8f5e8; color: #4caf50; }
.status-badge.yellow { background: #fff3e0; color: #ff9800; }
.status-badge.red { background: #ffebee; color: #f44336; }

.trend-cell {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 500;
}

.trend-cell.increasing { color: #4caf50; }
.trend-cell.decreasing { color: #f44336; }
.trend-cell.stable { color: #666; }

.action-buttons {
  display: flex;
  gap: 8px;
}

.btn-icon {
  width: 32px;
  height: 32px;
  border: none;
  background: #f8f9fa;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.btn-icon:hover {
  background: #4A90E2;
  color: white;
  transform: translateY(-1px);
}

.charts-view {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  padding: 24px;
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 32px;
}

.chart-container h3 {
  margin: 0 0 20px 0;
  color: #1A1A1A;
  font-weight: 600;
}

.chart-placeholder {
  height: 300px;
  background: #f8f9fa;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
}

.insights-panel {
  position: fixed;
  top: 0;
  right: 0;
  width: 400px;
  height: 100vh;
  background: white;
  box-shadow: -4px 0 20px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  overflow-y: auto;
}

.insights-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  border-bottom: 1px solid #e1e5e9;
}

.insights-header h3 {
  margin: 0;
  color: #1A1A1A;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
}

.insights-content {
  padding: 24px;
}

.insight-section {
  margin-bottom: 24px;
}

.insight-section h4 {
  margin: 0 0 12px 0;
  color: #1A1A1A;
  font-weight: 600;
}

.insight-section ul {
  margin: 0;
  padding-left: 20px;
}

.insight-section li {
  margin-bottom: 8px;
  color: #666;
  line-height: 1.5;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
  max-width: 800px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-content.small {
  max-width: 400px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  border-bottom: 1px solid #e1e5e9;
}

.modal-header h3 {
  margin: 0;
  color: #1A1A1A;
  font-weight: 600;
}

.modal-body {
  padding: 24px;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group.full-width {
  grid-column: 1 / -1;
}

.form-group label {
  font-weight: 500;
  color: #1A1A1A;
}

.kpi-current {
  color: #666;
  font-size: 14px;
  margin: 0;
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 12px;
  border: 2px solid #e1e5e9;
  border-radius: 8px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #4A90E2;
}

.form-options {
  margin: 20px 0;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.checkbox-label input {
  margin: 0;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #e1e5e9;
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1001;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e1e5e9;
  border-top: 4px solid #FF6B35;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Responsive */
@media (max-width: 768px) {
  .bcm-kpi {
    padding: 16px;
  }

  .page-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }

  .header-actions {
    justify-content: center;
  }

  .controls-section {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }

  .filters-group {
    flex-direction: column;
  }

  .kpi-summary {
    grid-template-columns: 1fr;
  }

  .kpi-cards {
    grid-template-columns: 1fr;
  }

  .charts-grid {
    grid-template-columns: 1fr;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .insights-panel {
    width: 100%;
  }
}
</style>