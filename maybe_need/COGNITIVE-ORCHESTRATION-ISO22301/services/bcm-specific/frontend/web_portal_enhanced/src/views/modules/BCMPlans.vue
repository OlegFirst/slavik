<template>
  <div class="bcm-plans">
    <!-- Header Section -->
    <div class="plans-header">
      <div class="container-fluid">
        <div class="row align-items-center">
          <div class="col-md-8">
            <h1 class="page-title">Business Continuity Plans</h1>
            <p class="page-subtitle">BCP/DRP Management & Activation</p>
          </div>
          <div class="col-md-4 text-end">
            <button class="btn btn-primary me-2" @click="showCreateModal = true">
              <i class="fas fa-plus"></i> Create Plan
            </button>
            <button class="btn btn-outline-primary" @click="refreshPlans">
              <i class="fas fa-sync"></i> Refresh
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Plans Overview Cards -->
    <div class="overview-section">
      <div class="container-fluid">
        <div class="row">
          <div class="col-md-3">
            <div class="metric-card primary">
              <div class="metric-icon">
                <i class="fas fa-file-alt"></i>
              </div>
              <div class="metric-content">
                <h3 class="metric-value">{{ planStats.total }}</h3>
                <p class="metric-label">Total Plans</p>
              </div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="metric-card success">
              <div class="metric-icon">
                <i class="fas fa-check-circle"></i>
              </div>
              <div class="metric-content">
                <h3 class="metric-value">{{ planStats.approved }}</h3>
                <p class="metric-label">Approved Plans</p>
              </div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="metric-card warning">
              <div class="metric-icon">
                <i class="fas fa-exclamation-triangle"></i>
              </div>
              <div class="metric-content">
                <h3 class="metric-value">{{ planStats.expiring }}</h3>
                <p class="metric-label">Expiring Soon</p>
              </div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="metric-card info">
              <div class="metric-icon">
                <i class="fas fa-play-circle"></i>
              </div>
              <div class="metric-content">
                <h3 class="metric-value">{{ planStats.active }}</h3>
                <p class="metric-label">Active Plans</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Plans Management Section -->
    <div class="content-section">
      <div class="container-fluid">
        <div class="row">
          <div class="col-12">
            <div class="content-card">
              <div class="card-header">
                <div class="d-flex justify-content-between align-items-center">
                  <h3>Business Continuity Plans</h3>
                  <div class="header-actions">
                    <div class="filter-group">
                      <select v-model="selectedStatus" @change="filterPlans" class="form-select">
                        <option value="">All Status</option>
                        <option value="draft">Draft</option>
                        <option value="review">Under Review</option>
                        <option value="approved">Approved</option>
                        <option value="active">Active</option>
                        <option value="expired">Expired</option>
                      </select>
                      <select v-model="selectedType" @change="filterPlans" class="form-select">
                        <option value="">All Types</option>
                        <option value="bcp">Business Continuity Plan</option>
                        <option value="drp">Disaster Recovery Plan</option>
                        <option value="emergency">Emergency Response</option>
                        <option value="crisis">Crisis Management</option>
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
                        <th>Plan Name</th>
                        <th>Type</th>
                        <th>Version</th>
                        <th>Status</th>
                        <th>Owner</th>
                        <th>Last Updated</th>
                        <th>Next Review</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="plan in filteredPlans" :key="plan.id">
                        <td>
                          <div class="plan-info">
                            <strong>{{ plan.name }}</strong>
                            <small class="text-muted d-block">{{ plan.description }}</small>
                          </div>
                        </td>
                        <td>
                          <span class="badge" :class="getPlanTypeBadge(plan.plan_type)">
                            {{ getPlanTypeLabel(plan.plan_type) }}
                          </span>
                        </td>
                        <td>{{ plan.version }}</td>
                        <td>
                          <span class="status-badge" :class="plan.status">
                            {{ getStatusLabel(plan.status) }}
                          </span>
                        </td>
                        <td>{{ plan.owner_name }}</td>
                        <td>{{ formatDate(plan.write_date) }}</td>
                        <td>{{ formatDate(plan.next_review_date) }}</td>
                        <td>
                          <div class="action-buttons">
                            <button class="btn btn-sm btn-outline-primary" @click="viewPlan(plan)" title="View Plan">
                              <i class="fas fa-eye"></i>
                            </button>
                            <button class="btn btn-sm btn-outline-success" @click="editPlan(plan)" title="Edit Plan">
                              <i class="fas fa-edit"></i>
                            </button>
                            <button class="btn btn-sm btn-outline-info" @click="activatePlan(plan)"
                                    :disabled="plan.status !== 'approved'" title="Activate Plan">
                              <i class="fas fa-play"></i>
                            </button>
                            <button class="btn btn-sm btn-outline-warning" @click="versionPlan(plan)" title="Create Version">
                              <i class="fas fa-code-branch"></i>
                            </button>
                            <div class="dropdown d-inline">
                              <button class="btn btn-sm btn-outline-secondary dropdown-toggle"
                                      type="button" data-bs-toggle="dropdown">
                                <i class="fas fa-ellipsis-v"></i>
                              </button>
                              <ul class="dropdown-menu">
                                <li><a class="dropdown-item" @click="testPlan(plan)">Test Plan</a></li>
                                <li><a class="dropdown-item" @click="duplicatePlan(plan)">Duplicate</a></li>
                                <li><a class="dropdown-item" @click="exportPlan(plan)">Export</a></li>
                                <li><hr class="dropdown-divider"></li>
                                <li><a class="dropdown-item text-danger" @click="deletePlan(plan)">Delete</a></li>
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

        <!-- Plan Testing Schedule -->
        <div class="row mt-4">
          <div class="col-md-6">
            <div class="content-card">
              <div class="card-header">
                <h3>Testing Schedule</h3>
                <button class="btn btn-outline-primary btn-sm" @click="showTestModal = true">
                  <i class="fas fa-plus"></i> Schedule Test
                </button>
              </div>
              <div class="card-body">
                <div class="test-schedule">
                  <div class="test-item" v-for="test in upcomingTests" :key="test.id">
                    <div class="test-date">
                      {{ formatDate(test.scheduled_date) }}
                    </div>
                    <div class="test-details">
                      <strong>{{ test.plan_name }}</strong>
                      <small class="text-muted d-block">{{ test.test_type }} - {{ test.participants }} participants</small>
                    </div>
                    <div class="test-status">
                      <span class="status-badge" :class="test.status">{{ test.status }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Activation History -->
          <div class="col-md-6">
            <div class="content-card">
              <div class="card-header">
                <h3>Activation History</h3>
                <router-link to="/activations" class="btn btn-outline-primary btn-sm">
                  View All
                </router-link>
              </div>
              <div class="card-body">
                <div class="activation-history">
                  <div class="activation-item" v-for="activation in recentActivations" :key="activation.id">
                    <div class="activation-time">
                      {{ formatDateTime(activation.activation_date) }}
                    </div>
                    <div class="activation-details">
                      <strong>{{ activation.plan_name }}</strong>
                      <small class="text-muted d-block">{{ activation.reason }}</small>
                    </div>
                    <div class="activation-status">
                      <span class="status-badge" :class="activation.status">{{ activation.status }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Plan Modal -->
    <div class="modal fade" :class="{ show: showCreateModal }" tabindex="-1" v-if="showCreateModal">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Create New Plan</h5>
            <button type="button" class="btn-close" @click="showCreateModal = false"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="createPlan">
              <div class="row">
                <div class="col-md-6">
                  <div class="mb-3">
                    <label class="form-label">Plan Name *</label>
                    <input type="text" class="form-control" v-model="newPlan.name" required>
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="mb-3">
                    <label class="form-label">Plan Type *</label>
                    <select class="form-select" v-model="newPlan.plan_type" required>
                      <option value="bcp">Business Continuity Plan</option>
                      <option value="drp">Disaster Recovery Plan</option>
                      <option value="emergency">Emergency Response</option>
                      <option value="crisis">Crisis Management</option>
                    </select>
                  </div>
                </div>
              </div>
              <div class="mb-3">
                <label class="form-label">Description</label>
                <textarea class="form-control" rows="3" v-model="newPlan.description"></textarea>
              </div>
              <div class="row">
                <div class="col-md-6">
                  <div class="mb-3">
                    <label class="form-label">Owner *</label>
                    <select class="form-select" v-model="newPlan.owner_id" required>
                      <option v-for="user in users" :key="user.id" :value="user.id">
                        {{ user.name }}
                      </option>
                    </select>
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="mb-3">
                    <label class="form-label">Priority Level</label>
                    <select class="form-select" v-model="newPlan.priority">
                      <option value="low">Low</option>
                      <option value="medium">Medium</option>
                      <option value="high">High</option>
                      <option value="critical">Critical</option>
                    </select>
                  </div>
                </div>
              </div>
              <div class="mb-3">
                <label class="form-label">Scope</label>
                <textarea class="form-control" rows="2" v-model="newPlan.scope"
                         placeholder="Define the scope and boundaries of this plan"></textarea>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="showCreateModal = false">Cancel</button>
            <button type="button" class="btn btn-primary" @click="createPlan" :disabled="creating">
              {{ creating ? 'Creating...' : 'Create Plan' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Test Schedule Modal -->
    <div class="modal fade" :class="{ show: showTestModal }" tabindex="-1" v-if="showTestModal">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Schedule Plan Test</h5>
            <button type="button" class="btn-close" @click="showTestModal = false"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="scheduleTest">
              <div class="mb-3">
                <label class="form-label">Select Plan *</label>
                <select class="form-select" v-model="newTest.plan_id" required>
                  <option v-for="plan in approvedPlans" :key="plan.id" :value="plan.id">
                    {{ plan.name }}
                  </option>
                </select>
              </div>
              <div class="mb-3">
                <label class="form-label">Test Type *</label>
                <select class="form-select" v-model="newTest.test_type" required>
                  <option value="tabletop">Tabletop Exercise</option>
                  <option value="walkthrough">Walkthrough</option>
                  <option value="simulation">Simulation</option>
                  <option value="full_scale">Full-Scale Exercise</option>
                </select>
              </div>
              <div class="mb-3">
                <label class="form-label">Scheduled Date *</label>
                <input type="datetime-local" class="form-control" v-model="newTest.scheduled_date" required>
              </div>
              <div class="mb-3">
                <label class="form-label">Duration (hours)</label>
                <input type="number" class="form-control" v-model="newTest.duration" min="1" max="24">
              </div>
              <div class="mb-3">
                <label class="form-label">Test Objectives</label>
                <textarea class="form-control" rows="3" v-model="newTest.objectives"></textarea>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="showTestModal = false">Cancel</button>
            <button type="button" class="btn btn-primary" @click="scheduleTest" :disabled="scheduling">
              {{ scheduling ? 'Scheduling...' : 'Schedule Test' }}
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
import bcmPlansService from '@/services/bcmPlans'
import { useToast } from 'vue-toastification'

export default {
  name: 'BCMPlans',
  setup() {
    const router = useRouter()
    const toast = useToast()

    // Reactive data
    const loading = ref(false)
    const creating = ref(false)
    const scheduling = ref(false)
    const showCreateModal = ref(false)
    const showTestModal = ref(false)
    const selectedStatus = ref('')
    const selectedType = ref('')

    const plans = ref([])
    const upcomingTests = ref([])
    const recentActivations = ref([])
    const users = ref([])

    const planStats = reactive({
      total: 0,
      approved: 0,
      expiring: 0,
      active: 0
    })

    const newPlan = reactive({
      name: '',
      description: '',
      plan_type: 'bcp',
      owner_id: null,
      priority: 'medium',
      scope: ''
    })

    const newTest = reactive({
      plan_id: null,
      test_type: 'tabletop',
      scheduled_date: '',
      duration: 2,
      objectives: ''
    })

    // Computed properties
    const filteredPlans = computed(() => {
      let filtered = plans.value

      if (selectedStatus.value) {
        filtered = filtered.filter(plan => plan.status === selectedStatus.value)
      }

      if (selectedType.value) {
        filtered = filtered.filter(plan => plan.plan_type === selectedType.value)
      }

      return filtered
    })

    const approvedPlans = computed(() => {
      return plans.value.filter(plan => plan.status === 'approved')
    })

    // Methods
    const loadPlans = async () => {
      loading.value = true
      try {
        const data = await bcmPlansService.getPlans()
        plans.value = data.plans
        planStats.total = data.stats.total
        planStats.approved = data.stats.approved
        planStats.expiring = data.stats.expiring
        planStats.active = data.stats.active
      } catch (error) {
        toast.error('Failed to load plans')
      } finally {
        loading.value = false
      }
    }

    const loadTestingSchedule = async () => {
      try {
        const data = await bcmPlansService.getTestingSchedule()
        upcomingTests.value = data
      } catch (error) {
        console.error('Failed to load testing schedule:', error)
      }
    }

    const loadActivationHistory = async () => {
      try {
        const data = await bcmPlansService.getActivationHistory(10)
        recentActivations.value = data
      } catch (error) {
        console.error('Failed to load activation history:', error)
      }
    }

    const loadUsers = async () => {
      try {
        const data = await bcmPlansService.getUsers()
        users.value = data
      } catch (error) {
        console.error('Failed to load users:', error)
      }
    }

    const refreshPlans = () => {
      loadPlans()
      loadTestingSchedule()
      loadActivationHistory()
    }

    const filterPlans = () => {
      // Filtering is handled by computed property
    }

    const createPlan = async () => {
      creating.value = true
      try {
        await bcmPlansService.createPlan(newPlan)
        toast.success('Plan created successfully')
        showCreateModal.value = false
        resetNewPlan()
        loadPlans()
      } catch (error) {
        toast.error('Failed to create plan')
      } finally {
        creating.value = false
      }
    }

    const scheduleTest = async () => {
      scheduling.value = true
      try {
        await bcmPlansService.scheduleTest(newTest)
        toast.success('Test scheduled successfully')
        showTestModal.value = false
        resetNewTest()
        loadTestingSchedule()
      } catch (error) {
        toast.error('Failed to schedule test')
      } finally {
        scheduling.value = false
      }
    }

    const viewPlan = (plan) => {
      router.push(`/plans/${plan.id}/view`)
    }

    const editPlan = (plan) => {
      router.push(`/plans/${plan.id}/edit`)
    }

    const activatePlan = async (plan) => {
      if (confirm(`Are you sure you want to activate "${plan.name}"?`)) {
        try {
          await bcmPlansService.activatePlan(plan.id)
          toast.success('Plan activated successfully')
          loadPlans()
          loadActivationHistory()
        } catch (error) {
          toast.error('Failed to activate plan')
        }
      }
    }

    const versionPlan = async (plan) => {
      try {
        const newVersion = await bcmPlansService.createVersion(plan.id)
        toast.success(`New version ${newVersion.version} created`)
        loadPlans()
      } catch (error) {
        toast.error('Failed to create version')
      }
    }

    const testPlan = (plan) => {
      newTest.plan_id = plan.id
      showTestModal.value = true
    }

    const duplicatePlan = async (plan) => {
      try {
        await bcmPlansService.duplicatePlan(plan.id)
        toast.success('Plan duplicated successfully')
        loadPlans()
      } catch (error) {
        toast.error('Failed to duplicate plan')
      }
    }

    const exportPlan = async (plan) => {
      try {
        await bcmPlansService.exportPlan(plan.id)
        toast.success('Plan exported successfully')
      } catch (error) {
        toast.error('Failed to export plan')
      }
    }

    const deletePlan = async (plan) => {
      if (confirm(`Are you sure you want to delete "${plan.name}"? This action cannot be undone.`)) {
        try {
          await bcmPlansService.deletePlan(plan.id)
          toast.success('Plan deleted successfully')
          loadPlans()
        } catch (error) {
          toast.error('Failed to delete plan')
        }
      }
    }

    // Utility methods
    const resetNewPlan = () => {
      Object.assign(newPlan, {
        name: '',
        description: '',
        plan_type: 'bcp',
        owner_id: null,
        priority: 'medium',
        scope: ''
      })
    }

    const resetNewTest = () => {
      Object.assign(newTest, {
        plan_id: null,
        test_type: 'tabletop',
        scheduled_date: '',
        duration: 2,
        objectives: ''
      })
    }

    const getPlanTypeBadge = (type) => {
      const badges = {
        bcp: 'bg-primary',
        drp: 'bg-info',
        emergency: 'bg-warning',
        crisis: 'bg-danger'
      }
      return badges[type] || 'bg-secondary'
    }

    const getPlanTypeLabel = (type) => {
      const labels = {
        bcp: 'BCP',
        drp: 'DRP',
        emergency: 'Emergency',
        crisis: 'Crisis'
      }
      return labels[type] || type
    }

    const getStatusLabel = (status) => {
      const labels = {
        draft: 'Draft',
        review: 'Under Review',
        approved: 'Approved',
        active: 'Active',
        expired: 'Expired'
      }
      return labels[status] || status
    }

    const formatDate = (dateString) => {
      if (!dateString) return 'N/A'
      const date = new Date(dateString)
      return date.toLocaleDateString()
    }

    const formatDateTime = (dateString) => {
      if (!dateString) return 'N/A'
      const date = new Date(dateString)
      return date.toLocaleString()
    }

    // Lifecycle
    onMounted(() => {
      loadPlans()
      loadTestingSchedule()
      loadActivationHistory()
      loadUsers()
    })

    return {
      // Data
      loading,
      creating,
      scheduling,
      showCreateModal,
      showTestModal,
      selectedStatus,
      selectedType,
      plans,
      filteredPlans,
      approvedPlans,
      upcomingTests,
      recentActivations,
      users,
      planStats,
      newPlan,
      newTest,

      // Methods
      refreshPlans,
      filterPlans,
      createPlan,
      scheduleTest,
      viewPlan,
      editPlan,
      activatePlan,
      versionPlan,
      testPlan,
      duplicatePlan,
      exportPlan,
      deletePlan,
      getPlanTypeBadge,
      getPlanTypeLabel,
      getStatusLabel,
      formatDate,
      formatDateTime
    }
  }
}
</script>

<style scoped>
/* Anthropic Color Palette */
:root {
  --anthropic-orange: #FF6B35;
  --anthropic-blue: #4A90E2;
  --anthropic-dark: #1A1A1A;
  --anthropic-light: #F8F9FA;
  --anthropic-success: #28A745;
  --anthropic-warning: #FFC107;
  --anthropic-danger: #DC3545;
}

.bcm-plans {
  min-height: 100vh;
  background: linear-gradient(135deg, var(--anthropic-light) 0%, #E8F2FF 100%);
}

.plans-header {
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

.overview-section {
  margin-bottom: 2rem;
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
  transition: transform 0.2s ease;
}

.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0,0,0,0.12);
}

.metric-card.primary {
  border-left-color: var(--anthropic-blue);
}

.metric-card.success {
  border-left-color: var(--anthropic-success);
}

.metric-card.warning {
  border-left-color: var(--anthropic-warning);
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

.metric-card.primary .metric-icon {
  background: var(--anthropic-blue);
}

.metric-card.success .metric-icon {
  background: var(--anthropic-success);
}

.metric-card.warning .metric-icon {
  background: var(--anthropic-warning);
}

.metric-card.info .metric-icon {
  background: var(--anthropic-orange);
}

.metric-value {
  font-size: 2rem;
  font-weight: 700;
  color: var(--anthropic-dark);
  margin: 0;
}

.metric-label {
  color: #6C757D;
  margin: 0;
  font-size: 0.9rem;
}

.content-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  margin-bottom: 1.5rem;
}

.card-header {
  padding: 1.5rem 1.5rem 0 1.5rem;
  border-bottom: 1px solid #E9ECEF;
  margin-bottom: 1rem;
}

.card-header h3 {
  color: var(--anthropic-dark);
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
}

.card-body {
  padding: 0 1.5rem 1.5rem 1.5rem;
}

.filter-group {
  display: flex;
  gap: 0.5rem;
}

.filter-group .form-select {
  width: auto;
  min-width: 120px;
}

.plan-info strong {
  color: var(--anthropic-dark);
}

.badge {
  font-size: 0.75rem;
  padding: 0.375rem 0.75rem;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
}

.status-badge.draft {
  background: #E9ECEF;
  color: #6C757D;
}

.status-badge.review {
  background: #FFF3CD;
  color: var(--anthropic-warning);
}

.status-badge.approved {
  background: #D4EDDA;
  color: var(--anthropic-success);
}

.status-badge.active {
  background: #D1ECF1;
  color: var(--anthropic-blue);
}

.status-badge.expired {
  background: #F8D7DA;
  color: var(--anthropic-danger);
}

.action-buttons {
  display: flex;
  gap: 0.25rem;
}

.test-schedule,
.activation-history {
  max-height: 400px;
  overflow-y: auto;
}

.test-item,
.activation-item {
  display: flex;
  gap: 1rem;
  padding: 1rem 0;
  border-bottom: 1px solid #F8F9FA;
  align-items: center;
}

.test-item:last-child,
.activation-item:last-child {
  border-bottom: none;
}

.test-date,
.activation-time {
  min-width: 100px;
  font-size: 0.9rem;
  color: #6C757D;
}

.test-details,
.activation-details {
  flex: 1;
}

.test-details strong,
.activation-details strong {
  color: var(--anthropic-dark);
}

.modal.show {
  display: block;
}

.modal-content {
  border-radius: 12px;
  border: none;
  box-shadow: 0 10px 30px rgba(0,0,0,0.3);
}

.modal-header {
  border-bottom: 1px solid #E9ECEF;
  padding: 1.5rem;
}

.modal-title {
  color: var(--anthropic-dark);
  font-weight: 600;
}

.modal-body {
  padding: 1.5rem;
}

.modal-footer {
  border-top: 1px solid #E9ECEF;
  padding: 1rem 1.5rem;
}

.form-label {
  color: var(--anthropic-dark);
  font-weight: 500;
  margin-bottom: 0.5rem;
}

.form-control,
.form-select {
  border: 1px solid #DEE2E6;
  border-radius: 8px;
  padding: 0.75rem;
  font-size: 0.95rem;
}

.form-control:focus,
.form-select:focus {
  border-color: var(--anthropic-blue);
  box-shadow: 0 0 0 0.2rem rgba(74, 144, 226, 0.25);
}

.btn {
  border-radius: 8px;
  font-weight: 500;
  padding: 0.5rem 1rem;
  border: none;
}

.btn-primary {
  background: var(--anthropic-blue);
  color: white;
}

.btn-primary:hover {
  background: #357ABD;
}

.btn-outline-primary {
  border: 1px solid var(--anthropic-blue);
  color: var(--anthropic-blue);
}

.btn-outline-primary:hover {
  background: var(--anthropic-blue);
  color: white;
}

.btn-outline-success:hover {
  background: var(--anthropic-success);
  border-color: var(--anthropic-success);
}

.btn-outline-info:hover {
  background: var(--anthropic-blue);
  border-color: var(--anthropic-blue);
}

.btn-outline-warning:hover {
  background: var(--anthropic-warning);
  border-color: var(--anthropic-warning);
}

/* Responsive Design */
@media (max-width: 768px) {
  .page-title {
    font-size: 2rem;
  }

  .metric-card {
    margin-bottom: 0.5rem;
  }

  .filter-group {
    flex-direction: column;
  }

  .filter-group .form-select {
    width: 100%;
  }

  .action-buttons {
    flex-wrap: wrap;
  }
}
</style>