<template>
  <div class="bcm-risk-management">
    <!-- Header Section -->
    <div class="risk-header">
      <div class="container-fluid">
        <div class="row align-items-center">
          <div class="col-md-8">
            <h1 class="page-title">Risk Management</h1>
            <p class="page-subtitle">Risk Register & Assessment Workflows</p>
          </div>
          <div class="col-md-4 text-end">
            <button class="btn btn-primary me-2" @click="showCreateModal = true">
              <i class="fas fa-plus"></i> Add Risk
            </button>
            <button class="btn btn-outline-primary" @click="refreshRisks">
              <i class="fas fa-sync"></i> Refresh
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Risk Overview -->
    <div class="overview-section">
      <div class="container-fluid">
        <div class="row">
          <div class="col-md-3">
            <div class="metric-card danger">
              <div class="metric-icon">
                <i class="fas fa-exclamation-triangle"></i>
              </div>
              <div class="metric-content">
                <h3 class="metric-value">{{ riskMetrics.criticalRisks }}</h3>
                <p class="metric-label">Critical Risks</p>
              </div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="metric-card warning">
              <div class="metric-icon">
                <i class="fas fa-shield-alt"></i>
              </div>
              <div class="metric-content">
                <h3 class="metric-value">{{ riskMetrics.totalRisks }}</h3>
                <p class="metric-label">Total Risks</p>
              </div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="metric-card success">
              <div class="metric-icon">
                <i class="fas fa-check-circle"></i>
              </div>
              <div class="metric-content">
                <h3 class="metric-value">{{ riskMetrics.mitigatedRisks }}%</h3>
                <p class="metric-label">Mitigated</p>
              </div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="metric-card info">
              <div class="metric-icon">
                <i class="fas fa-calendar"></i>
              </div>
              <div class="metric-content">
                <h3 class="metric-value">{{ riskMetrics.overdue }}</h3>
                <p class="metric-label">Overdue Reviews</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Risk Management Content -->
    <div class="content-section">
      <div class="container-fluid">
        <div class="row">
          <div class="col-12">
            <div class="content-card">
              <div class="card-header">
                <div class="d-flex justify-content-between align-items-center">
                  <h3>Risk Register</h3>
                  <div class="header-actions">
                    <div class="filter-group">
                      <select v-model="selectedCategory" @change="filterRisks" class="form-select">
                        <option value="">All Categories</option>
                        <option value="operational">Operational</option>
                        <option value="strategic">Strategic</option>
                        <option value="compliance">Compliance</option>
                        <option value="financial">Financial</option>
                        <option value="technology">Technology</option>
                      </select>
                      <select v-model="selectedSeverity" @change="filterRisks" class="form-select">
                        <option value="">All Severities</option>
                        <option value="critical">Critical</option>
                        <option value="high">High</option>
                        <option value="medium">Medium</option>
                        <option value="low">Low</option>
                      </select>
                      <select v-model="selectedStatus" @change="filterRisks" class="form-select">
                        <option value="">All Status</option>
                        <option value="identified">Identified</option>
                        <option value="assessed">Assessed</option>
                        <option value="mitigated">Mitigated</option>
                        <option value="monitored">Monitored</option>
                        <option value="closed">Closed</option>
                      </select>
                    </div>
                  </div>
                </div>
              </div>
              <div class="card-body">
                <div class="table-responsive" v-if="!loading">
                  <table class="table table-hover">
                    <thead>
                      <tr>
                        <th>Risk ID</th>
                        <th>Description</th>
                        <th>Category</th>
                        <th>Likelihood</th>
                        <th>Impact</th>
                        <th>Risk Score</th>
                        <th>Status</th>
                        <th>Owner</th>
                        <th>Next Review</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="risk in filteredRisks" :key="risk.id">
                        <td><strong>{{ risk.risk_id }}</strong></td>
                        <td>
                          <div class="risk-info">
                            <strong>{{ risk.name }}</strong>
                            <small class="text-muted d-block">{{ risk.description }}</small>
                          </div>
                        </td>
                        <td>
                          <span class="badge" :class="getCategoryBadge(risk.category)">
                            {{ risk.category }}
                          </span>
                        </td>
                        <td>
                          <div class="rating">
                            <span class="rating-value" :class="getLikelihoodClass(risk.likelihood)">
                              {{ risk.likelihood }}
                            </span>
                          </div>
                        </td>
                        <td>
                          <div class="rating">
                            <span class="rating-value" :class="getImpactClass(risk.impact)">
                              {{ risk.impact }}
                            </span>
                          </div>
                        </td>
                        <td>
                          <div class="risk-score" :class="getRiskScoreClass(risk.risk_score)">
                            {{ risk.risk_score }}
                          </div>
                        </td>
                        <td>
                          <span class="status-badge" :class="risk.status">
                            {{ getStatusLabel(risk.status) }}
                          </span>
                        </td>
                        <td>{{ risk.owner_name }}</td>
                        <td>{{ formatDate(risk.next_review_date) }}</td>
                        <td>
                          <div class="action-buttons">
                            <button class="btn btn-sm btn-outline-primary" @click="viewRisk(risk)">
                              <i class="fas fa-eye"></i>
                            </button>
                            <button class="btn btn-sm btn-outline-success" @click="editRisk(risk)">
                              <i class="fas fa-edit"></i>
                            </button>
                            <button class="btn btn-sm btn-outline-warning" @click="assessRisk(risk)">
                              <i class="fas fa-chart-bar"></i>
                            </button>
                            <div class="dropdown d-inline">
                              <button class="btn btn-sm btn-outline-secondary dropdown-toggle"
                                      type="button" data-bs-toggle="dropdown">
                                <i class="fas fa-ellipsis-v"></i>
                              </button>
                              <ul class="dropdown-menu">
                                <li><a class="dropdown-item" @click="createMitigation(risk)">Add Mitigation</a></li>
                                <li><a class="dropdown-item" @click="updateStatus(risk)">Update Status</a></li>
                                <li><a class="dropdown-item" @click="duplicateRisk(risk)">Duplicate</a></li>
                                <li><hr class="dropdown-divider"></li>
                                <li><a class="dropdown-item text-danger" @click="deleteRisk(risk)">Delete</a></li>
                              </ul>
                            </div>
                          </div>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                <div v-else class="text-center py-5">
                  <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Risk Matrix & Mitigation Actions -->
        <div class="row mt-4">
          <div class="col-md-8">
            <div class="content-card">
              <div class="card-header">
                <h3>Risk Heat Matrix</h3>
                <button class="btn btn-outline-primary btn-sm" @click="refreshMatrix">
                  <i class="fas fa-sync"></i> Refresh
                </button>
              </div>
              <div class="card-body">
                <div class="risk-matrix">
                  <div class="matrix-cell critical" data-likelihood="5" data-impact="5">
                    <div class="cell-risks">
                      <div v-for="risk in getMatrixRisks(5, 5)" :key="risk.id" class="matrix-risk">
                        {{ risk.risk_id }}
                      </div>
                    </div>
                  </div>
                  <div class="matrix-cell high" data-likelihood="4" data-impact="5">
                    <div class="cell-risks">
                      <div v-for="risk in getMatrixRisks(4, 5)" :key="risk.id" class="matrix-risk">
                        {{ risk.risk_id }}
                      </div>
                    </div>
                  </div>
                  <div class="matrix-cell high" data-likelihood="5" data-impact="4">
                    <div class="cell-risks">
                      <div v-for="risk in getMatrixRisks(5, 4)" :key="risk.id" class="matrix-risk">
                        {{ risk.risk_id }}
                      </div>
                    </div>
                  </div>
                  <div class="matrix-cell medium" data-likelihood="3" data-impact="4">
                    <div class="cell-risks">
                      <div v-for="risk in getMatrixRisks(3, 4)" :key="risk.id" class="matrix-risk">
                        {{ risk.risk_id }}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="col-md-4">
            <div class="content-card">
              <div class="card-header">
                <h3>Mitigation Actions</h3>
                <button class="btn btn-outline-primary btn-sm" @click="loadMitigations">
                  <i class="fas fa-sync"></i> Refresh
                </button>
              </div>
              <div class="card-body">
                <div class="mitigation-list">
                  <div v-for="mitigation in mitigations" :key="mitigation.id" class="mitigation-item">
                    <div class="mitigation-header">
                      <strong>{{ mitigation.action }}</strong>
                      <span class="priority-badge" :class="mitigation.priority">{{ mitigation.priority }}</span>
                    </div>
                    <div class="mitigation-details">
                      <small class="text-muted">{{ mitigation.risk_name }}</small>
                      <div class="progress-bar">
                        <div class="progress-fill" :style="`width: ${mitigation.completion}%`"></div>
                      </div>
                      <small>Due: {{ formatDate(mitigation.due_date) }}</small>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create/Edit Risk Modal -->
    <div class="modal fade" :class="{ show: showCreateModal }" tabindex="-1" v-if="showCreateModal">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ editingRisk ? 'Edit' : 'Add' }} Risk</h5>
            <button type="button" class="btn-close" @click="closeRiskModal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="saveRisk">
              <div class="row">
                <div class="col-md-6">
                  <div class="mb-3">
                    <label class="form-label">Risk Name *</label>
                    <input type="text" class="form-control" v-model="currentRisk.name" required>
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="mb-3">
                    <label class="form-label">Category *</label>
                    <select class="form-select" v-model="currentRisk.category" required>
                      <option value="operational">Operational</option>
                      <option value="strategic">Strategic</option>
                      <option value="compliance">Compliance</option>
                      <option value="financial">Financial</option>
                      <option value="technology">Technology</option>
                    </select>
                  </div>
                </div>
              </div>
              <div class="mb-3">
                <label class="form-label">Description</label>
                <textarea class="form-control" rows="3" v-model="currentRisk.description"></textarea>
              </div>
              <div class="row">
                <div class="col-md-4">
                  <div class="mb-3">
                    <label class="form-label">Likelihood (1-5)</label>
                    <select class="form-select" v-model="currentRisk.likelihood">
                      <option value="1">Very Low</option>
                      <option value="2">Low</option>
                      <option value="3">Medium</option>
                      <option value="4">High</option>
                      <option value="5">Very High</option>
                    </select>
                  </div>
                </div>
                <div class="col-md-4">
                  <div class="mb-3">
                    <label class="form-label">Impact (1-5)</label>
                    <select class="form-select" v-model="currentRisk.impact">
                      <option value="1">Very Low</option>
                      <option value="2">Low</option>
                      <option value="3">Medium</option>
                      <option value="4">High</option>
                      <option value="5">Very High</option>
                    </select>
                  </div>
                </div>
                <div class="col-md-4">
                  <div class="mb-3">
                    <label class="form-label">Owner *</label>
                    <select class="form-select" v-model="currentRisk.owner_id" required>
                      <option v-for="user in users" :key="user.id" :value="user.id">
                        {{ user.name }}
                      </option>
                    </select>
                  </div>
                </div>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="closeRiskModal">Cancel</button>
            <button type="button" class="btn btn-primary" @click="saveRisk" :disabled="saving">
              {{ saving ? 'Saving...' : 'Save Risk' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import bcmRiskManagementService from '@/services/bcmRiskManagement'
import { useToast } from 'vue-toastification'

export default {
  name: 'BCMRiskManagement',
  setup() {
    const router = useRouter()
    const toast = useToast()

    // Reactive data
    const loading = ref(false)
    const saving = ref(false)
    const showCreateModal = ref(false)
    const editingRisk = ref(false)
    const selectedCategory = ref('')
    const selectedSeverity = ref('')
    const selectedStatus = ref('')

    const riskMetrics = reactive({
      criticalRisks: 0,
      totalRisks: 0,
      mitigatedRisks: 0,
      overdue: 0
    })

    const currentRisk = reactive({
      id: null,
      name: '',
      description: '',
      category: 'operational',
      likelihood: 3,
      impact: 3,
      owner_id: null
    })

    const risks = ref([])
    const mitigations = ref([])
    const users = ref([])

    // Computed properties
    const filteredRisks = computed(() => {
      let filtered = risks.value

      if (selectedCategory.value) {
        filtered = filtered.filter(risk => risk.category === selectedCategory.value)
      }

      if (selectedSeverity.value) {
        filtered = filtered.filter(risk => risk.severity === selectedSeverity.value)
      }

      if (selectedStatus.value) {
        filtered = filtered.filter(risk => risk.status === selectedStatus.value)
      }

      return filtered
    })

    // Methods
    const loadRisks = async () => {
      loading.value = true
      try {
        const data = await bcmRiskManagementService.getRisks()
        risks.value = data.risks
        riskMetrics.criticalRisks = data.metrics.critical_risks
        riskMetrics.totalRisks = data.metrics.total_risks
        riskMetrics.mitigatedRisks = data.metrics.mitigated_risks
        riskMetrics.overdue = data.metrics.overdue
      } catch (error) {
        toast.error('Failed to load risks')
      } finally {
        loading.value = false
      }
    }

    const loadMitigations = async () => {
      try {
        mitigations.value = await bcmRiskManagementService.getMitigations()
      } catch (error) {
        console.error('Failed to load mitigations:', error)
      }
    }

    const loadUsers = async () => {
      try {
        users.value = await bcmRiskManagementService.getUsers()
      } catch (error) {
        console.error('Failed to load users:', error)
      }
    }

    const refreshRisks = () => {
      loadRisks()
      loadMitigations()
    }

    const refreshMatrix = () => {
      loadRisks()
    }

    const filterRisks = () => {
      // Filtering handled by computed property
    }

    const saveRisk = async () => {
      saving.value = true
      try {
        if (editingRisk.value) {
          await bcmRiskManagementService.updateRisk(currentRisk.id, currentRisk)
          toast.success('Risk updated successfully')
        } else {
          await bcmRiskManagementService.createRisk(currentRisk)
          toast.success('Risk created successfully')
        }
        closeRiskModal()
        loadRisks()
      } catch (error) {
        toast.error('Failed to save risk')
      } finally {
        saving.value = false
      }
    }

    const editRisk = (risk) => {
      editingRisk.value = true
      Object.assign(currentRisk, risk)
      showCreateModal.value = true
    }

    const viewRisk = (risk) => {
      router.push(`/risks/${risk.id}/view`)
    }

    const assessRisk = (risk) => {
      router.push(`/risks/${risk.id}/assess`)
    }

    const deleteRisk = async (risk) => {
      if (confirm(`Are you sure you want to delete "${risk.name}"?`)) {
        try {
          await bcmRiskManagementService.deleteRisk(risk.id)
          toast.success('Risk deleted successfully')
          loadRisks()
        } catch (error) {
          toast.error('Failed to delete risk')
        }
      }
    }

    const closeRiskModal = () => {
      showCreateModal.value = false
      editingRisk.value = false
      resetCurrentRisk()
    }

    const resetCurrentRisk = () => {
      Object.assign(currentRisk, {
        id: null,
        name: '',
        description: '',
        category: 'operational',
        likelihood: 3,
        impact: 3,
        owner_id: null
      })
    }

    const createMitigation = (risk) => {
      toast.info(`Create mitigation for ${risk.name} feature coming soon`)
    }

    const updateStatus = (risk) => {
      toast.info(`Update status for ${risk.name} feature coming soon`)
    }

    const duplicateRisk = async (risk) => {
      try {
        await bcmRiskManagementService.duplicateRisk(risk.id)
        toast.success('Risk duplicated successfully')
        loadRisks()
      } catch (error) {
        toast.error('Failed to duplicate risk')
      }
    }

    const getMatrixRisks = (likelihood, impact) => {
      return risks.value.filter(r =>
        parseInt(r.likelihood) === likelihood && parseInt(r.impact) === impact
      )
    }

    // Utility methods
    const getCategoryBadge = (category) => {
      const badges = {
        operational: 'bg-primary',
        strategic: 'bg-success',
        compliance: 'bg-warning',
        financial: 'bg-info',
        technology: 'bg-secondary'
      }
      return badges[category] || 'bg-secondary'
    }

    const getLikelihoodClass = (likelihood) => {
      const classes = {
        1: 'rating-very-low',
        2: 'rating-low',
        3: 'rating-medium',
        4: 'rating-high',
        5: 'rating-very-high'
      }
      return classes[likelihood] || 'rating-medium'
    }

    const getImpactClass = (impact) => {
      const classes = {
        1: 'rating-very-low',
        2: 'rating-low',
        3: 'rating-medium',
        4: 'rating-high',
        5: 'rating-very-high'
      }
      return classes[impact] || 'rating-medium'
    }

    const getRiskScoreClass = (score) => {
      if (score >= 20) return 'risk-critical'
      if (score >= 15) return 'risk-high'
      if (score >= 10) return 'risk-medium'
      return 'risk-low'
    }

    const getStatusLabel = (status) => {
      const labels = {
        identified: 'Identified',
        assessed: 'Assessed',
        mitigated: 'Mitigated',
        monitored: 'Monitored',
        closed: 'Closed'
      }
      return labels[status] || status
    }

    const formatDate = (dateString) => {
      if (!dateString) return 'N/A'
      return new Date(dateString).toLocaleDateString()
    }

    // Lifecycle
    onMounted(() => {
      loadRisks()
      loadMitigations()
      loadUsers()
    })

    return {
      // Data
      loading,
      saving,
      showCreateModal,
      editingRisk,
      selectedCategory,
      selectedSeverity,
      selectedStatus,
      riskMetrics,
      currentRisk,
      risks,
      filteredRisks,
      mitigations,
      users,

      // Methods
      refreshRisks,
      refreshMatrix,
      filterRisks,
      saveRisk,
      editRisk,
      viewRisk,
      assessRisk,
      deleteRisk,
      closeRiskModal,
      createMitigation,
      updateStatus,
      duplicateRisk,
      getMatrixRisks,
      getCategoryBadge,
      getLikelihoodClass,
      getImpactClass,
      getRiskScoreClass,
      getStatusLabel,
      formatDate
    }
  }
}
</script>

<style scoped>
/* Reusing the same Anthropic color scheme and styling patterns from previous components */
:root {
  --anthropic-orange: #FF6B35;
  --anthropic-blue: #4A90E2;
  --anthropic-dark: #1A1A1A;
  --anthropic-light: #F8F9FA;
  --anthropic-success: #28A745;
  --anthropic-warning: #FFC107;
  --anthropic-danger: #DC3545;
}

.bcm-risk-management {
  min-height: 100vh;
  background: linear-gradient(135deg, var(--anthropic-light) 0%, #E8F2FF 100%);
}

.risk-header {
  background: white;
  border-bottom: 2px solid var(--anthropic-blue);
  padding: 2rem 0;
  margin-bottom: 2rem;
}

.page-title {
  color: var(--anthropic-dark);
  font-weight: 700;
  font-size: 2.5rem;
  margin: 0;
}

.page-subtitle {
  color: #6C757D;
  font-size: 1.1rem;
  margin: 0.5rem 0 0 0;
}

.metric-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 1rem;
  border-left: 4px solid;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.metric-card.danger {
  border-left-color: var(--anthropic-danger);
}

.metric-card.warning {
  border-left-color: var(--anthropic-warning);
}

.metric-card.success {
  border-left-color: var(--anthropic-success);
}

.metric-card.info {
  border-left-color: var(--anthropic-orange);
}

.metric-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  color: white;
}

.metric-card.danger .metric-icon {
  background: var(--anthropic-danger);
}

.metric-card.warning .metric-icon {
  background: var(--anthropic-warning);
}

.metric-card.success .metric-icon {
  background: var(--anthropic-success);
}

.metric-card.info .metric-icon {
  background: var(--anthropic-orange);
}

.risk-score {
  padding: 0.5rem;
  border-radius: 8px;
  font-weight: bold;
  text-align: center;
}

.risk-score.risk-critical {
  background: #F8D7DA;
  color: var(--anthropic-danger);
}

.risk-score.risk-high {
  background: #FFF3CD;
  color: var(--anthropic-warning);
}

.risk-score.risk-medium {
  background: #D1ECF1;
  color: var(--anthropic-blue);
}

.risk-score.risk-low {
  background: #D4EDDA;
  color: var(--anthropic-success);
}

.rating-value {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 500;
}

.rating-very-high {
  background: var(--anthropic-danger);
  color: white;
}

.rating-high {
  background: var(--anthropic-warning);
  color: white;
}

.rating-medium {
  background: var(--anthropic-blue);
  color: white;
}

.rating-low {
  background: var(--anthropic-success);
  color: white;
}

.rating-very-low {
  background: #6C757D;
  color: white;
}

.risk-matrix {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 0.5rem;
  min-height: 300px;
}

.matrix-cell {
  border: 2px solid;
  border-radius: 8px;
  padding: 0.5rem;
  min-height: 60px;
}

.matrix-cell.critical {
  border-color: var(--anthropic-danger);
  background: rgba(220, 53, 69, 0.1);
}

.matrix-cell.high {
  border-color: var(--anthropic-warning);
  background: rgba(255, 193, 7, 0.1);
}

.matrix-cell.medium {
  border-color: var(--anthropic-blue);
  background: rgba(74, 144, 226, 0.1);
}

.matrix-risk {
  background: white;
  padding: 0.25rem;
  margin: 0.25rem 0;
  border-radius: 4px;
  font-size: 0.8rem;
  text-align: center;
}

.mitigation-list {
  max-height: 400px;
  overflow-y: auto;
}

.mitigation-item {
  border: 1px solid #E9ECEF;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1rem;
}

.mitigation-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.priority-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

.priority-badge.high {
  background: var(--anthropic-danger);
  color: white;
}

.priority-badge.medium {
  background: var(--anthropic-warning);
  color: white;
}

.priority-badge.low {
  background: var(--anthropic-success);
  color: white;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: #E9ECEF;
  border-radius: 4px;
  overflow: hidden;
  margin: 0.5rem 0;
}

.progress-fill {
  height: 100%;
  background: var(--anthropic-success);
  transition: width 0.3s ease;
}

/* Common styles for forms, modals, etc. follow the same pattern as previous components */
</style>