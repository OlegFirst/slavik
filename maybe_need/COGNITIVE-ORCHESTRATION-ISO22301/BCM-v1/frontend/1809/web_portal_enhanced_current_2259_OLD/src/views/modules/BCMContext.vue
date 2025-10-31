<template>
  <div class="bcm-context">
    <!-- Header Section -->
    <div class="context-header">
      <div class="container-fluid">
        <div class="row align-items-center">
          <div class="col-md-8">
            <h1 class="page-title">Organizational Context</h1>
            <p class="page-subtitle">Stakeholder Management & BCMS Scope</p>
          </div>
          <div class="col-md-4 text-end">
            <button class="btn btn-primary me-2" @click="showCreateModal = true">
              <i class="fas fa-plus"></i> Add Stakeholder
            </button>
            <button class="btn btn-outline-primary" @click="refreshContext">
              <i class="fas fa-sync"></i> Refresh
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Context Overview -->
    <div class="overview-section">
      <div class="container-fluid">
        <div class="row">
          <div class="col-md-3">
            <div class="metric-card primary">
              <div class="metric-icon">
                <i class="fas fa-users"></i>
              </div>
              <div class="metric-content">
                <h3 class="metric-value">{{ contextMetrics.totalStakeholders }}</h3>
                <p class="metric-label">Total Stakeholders</p>
              </div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="metric-card success">
              <div class="metric-icon">
                <i class="fas fa-check-circle"></i>
              </div>
              <div class="metric-content">
                <h3 class="metric-value">{{ contextMetrics.analysisComplete }}%</h3>
                <p class="metric-label">Analysis Complete</p>
              </div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="metric-card warning">
              <div class="metric-icon">
                <i class="fas fa-exclamation-triangle"></i>
              </div>
              <div class="metric-content">
                <h3 class="metric-value">{{ contextMetrics.criticalIssues }}</h3>
                <p class="metric-label">Critical Issues</p>
              </div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="metric-card info">
              <div class="metric-icon">
                <i class="fas fa-calendar"></i>
              </div>
              <div class="metric-content">
                <h3 class="metric-value">{{ formatDate(contextMetrics.lastUpdate) }}</h3>
                <p class="metric-label">Last Updated</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Context Management Tabs -->
    <div class="content-section">
      <div class="container-fluid">
        <div class="row">
          <div class="col-12">
            <div class="content-card">
              <div class="card-header">
                <div class="context-tabs">
                  <button
                    v-for="tab in contextTabs"
                    :key="tab.id"
                    class="tab-btn"
                    :class="{ active: activeTab === tab.id }"
                    @click="activeTab = tab.id"
                  >
                    <i :class="tab.icon"></i>
                    {{ tab.name }}
                  </button>
                </div>
              </div>
              <div class="card-body">
                <!-- Organization Profile Tab -->
                <div v-if="activeTab === 'profile'" class="context-tab-content">
                  <div class="row">
                    <div class="col-md-8">
                      <div class="org-profile-section">
                        <h4>Organization Profile</h4>
                        <form @submit.prevent="updateProfile">
                          <div class="row">
                            <div class="col-md-6">
                              <div class="mb-3">
                                <label class="form-label">Organization Name</label>
                                <input
                                  type="text"
                                  class="form-control"
                                  v-model="organizationProfile.name"
                                  required
                                >
                              </div>
                            </div>
                            <div class="col-md-6">
                              <div class="mb-3">
                                <label class="form-label">Industry</label>
                                <select class="form-select" v-model="organizationProfile.industry">
                                  <option v-for="industry in industries" :key="industry" :value="industry">
                                    {{ industry }}
                                  </option>
                                </select>
                              </div>
                            </div>
                          </div>
                          <div class="mb-3">
                            <label class="form-label">Description</label>
                            <textarea
                              class="form-control"
                              rows="3"
                              v-model="organizationProfile.description"
                              placeholder="Brief description of the organization"
                            ></textarea>
                          </div>
                          <div class="row">
                            <div class="col-md-6">
                              <div class="mb-3">
                                <label class="form-label">Size</label>
                                <select class="form-select" v-model="organizationProfile.size">
                                  <option value="small">Small (&lt; 50 employees)</option>
                                  <option value="medium">Medium (50-250 employees)</option>
                                  <option value="large">Large (250-1000 employees)</option>
                                  <option value="enterprise">Enterprise (&gt; 1000 employees)</option>
                                </select>
                              </div>
                            </div>
                            <div class="col-md-6">
                              <div class="mb-3">
                                <label class="form-label">Location</label>
                                <input
                                  type="text"
                                  class="form-control"
                                  v-model="organizationProfile.location"
                                  placeholder="Primary location"
                                >
                              </div>
                            </div>
                          </div>
                          <div class="mb-3">
                            <label class="form-label">BCMS Scope</label>
                            <textarea
                              class="form-control"
                              rows="4"
                              v-model="organizationProfile.bcmsScope"
                              placeholder="Define the scope and boundaries of your BCMS"
                            ></textarea>
                          </div>
                          <button type="submit" class="btn btn-primary" :disabled="updatingProfile">
                            {{ updatingProfile ? 'Updating...' : 'Update Profile' }}
                          </button>
                        </form>
                      </div>
                    </div>
                    <div class="col-md-4">
                      <div class="context-summary">
                        <h4>Context Summary</h4>
                        <div class="summary-item">
                          <span class="summary-label">Established</span>
                          <span class="summary-value">{{ organizationProfile.established || 'Not set' }}</span>
                        </div>
                        <div class="summary-item">
                          <span class="summary-label">Certification Status</span>
                          <span class="summary-value" :class="organizationProfile.certificationStatus">
                            {{ organizationProfile.certificationStatus || 'Not certified' }}
                          </span>
                        </div>
                        <div class="summary-item">
                          <span class="summary-label">Last Review</span>
                          <span class="summary-value">{{ formatDate(organizationProfile.lastReview) }}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Stakeholders Tab -->
                <div v-if="activeTab === 'stakeholders'" class="context-tab-content">
                  <div class="stakeholders-controls mb-3">
                    <div class="row align-items-center">
                      <div class="col-md-6">
                        <div class="search-box">
                          <input
                            type="text"
                            class="form-control"
                            v-model="stakeholderSearch"
                            placeholder="Search stakeholders..."
                          >
                        </div>
                      </div>
                      <div class="col-md-6 text-end">
                        <select class="form-select d-inline-block w-auto me-2" v-model="selectedStakeholderType">
                          <option value="">All Types</option>
                          <option value="internal">Internal</option>
                          <option value="external">External</option>
                          <option value="regulatory">Regulatory</option>
                        </select>
                        <select class="form-select d-inline-block w-auto" v-model="selectedInfluence">
                          <option value="">All Influence</option>
                          <option value="high">High</option>
                          <option value="medium">Medium</option>
                          <option value="low">Low</option>
                        </select>
                      </div>
                    </div>
                  </div>

                  <div class="table-responsive">
                    <table class="table table-hover">
                      <thead>
                        <tr>
                          <th>Stakeholder</th>
                          <th>Type</th>
                          <th>Interest</th>
                          <th>Influence</th>
                          <th>Engagement</th>
                          <th>Last Contact</th>
                          <th>Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr v-for="stakeholder in filteredStakeholders" :key="stakeholder.id">
                          <td>
                            <div class="stakeholder-info">
                              <strong>{{ stakeholder.name }}</strong>
                              <small class="text-muted d-block">{{ stakeholder.role }}</small>
                              <small class="text-muted">{{ stakeholder.organization }}</small>
                            </div>
                          </td>
                          <td>
                            <span class="badge" :class="getStakeholderTypeBadge(stakeholder.type)">
                              {{ stakeholder.type }}
                            </span>
                          </td>
                          <td>
                            <div class="interest-rating">
                              <div class="rating-stars">
                                <i
                                  v-for="n in 5"
                                  :key="n"
                                  class="fas fa-star"
                                  :class="{ active: n <= stakeholder.interest_level }"
                                ></i>
                              </div>
                            </div>
                          </td>
                          <td>
                            <span class="influence-badge" :class="stakeholder.influence_level">
                              {{ stakeholder.influence_level }}
                            </span>
                          </td>
                          <td>
                            <span class="engagement-badge" :class="stakeholder.engagement_status">
                              {{ stakeholder.engagement_status }}
                            </span>
                          </td>
                          <td>{{ formatDate(stakeholder.last_contact) }}</td>
                          <td>
                            <div class="action-buttons">
                              <button class="btn btn-sm btn-outline-primary" @click="editStakeholder(stakeholder)">
                                <i class="fas fa-edit"></i>
                              </button>
                              <button class="btn btn-sm btn-outline-info" @click="contactStakeholder(stakeholder)">
                                <i class="fas fa-envelope"></i>
                              </button>
                              <button class="btn btn-sm btn-outline-danger" @click="deleteStakeholder(stakeholder)">
                                <i class="fas fa-trash"></i>
                              </button>
                            </div>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>

                <!-- Analysis Tab -->
                <div v-if="activeTab === 'analysis'" class="context-tab-content">
                  <div class="row">
                    <div class="col-md-6">
                      <div class="analysis-section">
                        <h4>Internal Factors</h4>
                        <div class="factors-list">
                          <div
                            v-for="factor in internalFactors"
                            :key="factor.id"
                            class="factor-item"
                          >
                            <div class="factor-header">
                              <strong>{{ factor.name }}</strong>
                              <span class="impact-badge" :class="factor.impact">{{ factor.impact }}</span>
                            </div>
                            <p class="factor-description">{{ factor.description }}</p>
                            <div class="factor-actions">
                              <button class="btn btn-sm btn-outline-primary" @click="editFactor(factor)">
                                Edit
                              </button>
                            </div>
                          </div>
                        </div>
                        <button class="btn btn-outline-primary" @click="addFactor('internal')">
                          <i class="fas fa-plus"></i> Add Internal Factor
                        </button>
                      </div>
                    </div>
                    <div class="col-md-6">
                      <div class="analysis-section">
                        <h4>External Factors</h4>
                        <div class="factors-list">
                          <div
                            v-for="factor in externalFactors"
                            :key="factor.id"
                            class="factor-item"
                          >
                            <div class="factor-header">
                              <strong>{{ factor.name }}</strong>
                              <span class="impact-badge" :class="factor.impact">{{ factor.impact }}</span>
                            </div>
                            <p class="factor-description">{{ factor.description }}</p>
                            <div class="factor-actions">
                              <button class="btn btn-sm btn-outline-primary" @click="editFactor(factor)">
                                Edit
                              </button>
                            </div>
                          </div>
                        </div>
                        <button class="btn btn-outline-primary" @click="addFactor('external')">
                          <i class="fas fa-plus"></i> Add External Factor
                        </button>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Requirements Tab -->
                <div v-if="activeTab === 'requirements'" class="context-tab-content">
                  <div class="row">
                    <div class="col-12">
                      <div class="requirements-matrix">
                        <h4>Requirements & Expectations</h4>
                        <div class="table-responsive">
                          <table class="table table-bordered">
                            <thead>
                              <tr>
                                <th>Stakeholder</th>
                                <th>Requirements</th>
                                <th>Expectations</th>
                                <th>Compliance Status</th>
                                <th>Actions</th>
                              </tr>
                            </thead>
                            <tbody>
                              <tr v-for="req in requirements" :key="req.id">
                                <td>{{ req.stakeholder_name }}</td>
                                <td>
                                  <ul class="requirements-list">
                                    <li v-for="requirement in req.requirements" :key="requirement">
                                      {{ requirement }}
                                    </li>
                                  </ul>
                                </td>
                                <td>
                                  <ul class="expectations-list">
                                    <li v-for="expectation in req.expectations" :key="expectation">
                                      {{ expectation }}
                                    </li>
                                  </ul>
                                </td>
                                <td>
                                  <span class="compliance-badge" :class="req.compliance_status">
                                    {{ req.compliance_status }}
                                  </span>
                                </td>
                                <td>
                                  <button class="btn btn-sm btn-outline-primary" @click="editRequirement(req)">
                                    Edit
                                  </button>
                                </td>
                              </tr>
                            </tbody>
                          </table>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Stakeholder Matrix -->
        <div class="row mt-4">
          <div class="col-md-8">
            <div class="content-card">
              <div class="card-header">
                <h3>Stakeholder Influence/Interest Matrix</h3>
                <button class="btn btn-outline-primary btn-sm" @click="refreshMatrix">
                  <i class="fas fa-sync"></i> Refresh
                </button>
              </div>
              <div class="card-body">
                <div class="stakeholder-matrix">
                  <div class="matrix-quadrant high-high">
                    <h5>Manage Closely</h5>
                    <div class="quadrant-stakeholders">
                      <div
                        v-for="stakeholder in getMatrixStakeholders('high', 'high')"
                        :key="stakeholder.id"
                        class="matrix-stakeholder"
                      >
                        {{ stakeholder.name }}
                      </div>
                    </div>
                  </div>
                  <div class="matrix-quadrant high-low">
                    <h5>Keep Satisfied</h5>
                    <div class="quadrant-stakeholders">
                      <div
                        v-for="stakeholder in getMatrixStakeholders('high', 'low')"
                        :key="stakeholder.id"
                        class="matrix-stakeholder"
                      >
                        {{ stakeholder.name }}
                      </div>
                    </div>
                  </div>
                  <div class="matrix-quadrant low-high">
                    <h5>Keep Informed</h5>
                    <div class="quadrant-stakeholders">
                      <div
                        v-for="stakeholder in getMatrixStakeholders('low', 'high')"
                        :key="stakeholder.id"
                        class="matrix-stakeholder"
                      >
                        {{ stakeholder.name }}
                      </div>
                    </div>
                  </div>
                  <div class="matrix-quadrant low-low">
                    <h5>Monitor</h5>
                    <div class="quadrant-stakeholders">
                      <div
                        v-for="stakeholder in getMatrixStakeholders('low', 'low')"
                        :key="stakeholder.id"
                        class="matrix-stakeholder"
                      >
                        {{ stakeholder.name }}
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
                <h3>Recent Activities</h3>
              </div>
              <div class="card-body">
                <div class="activity-timeline">
                  <div
                    v-for="activity in recentActivities"
                    :key="activity.id"
                    class="activity-item"
                  >
                    <div class="activity-time">{{ formatDateTime(activity.timestamp) }}</div>
                    <div class="activity-content">
                      <strong>{{ activity.title }}</strong>
                      <p>{{ activity.description }}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create/Edit Stakeholder Modal -->
    <div class="modal fade" :class="{ show: showCreateModal }" tabindex="-1" v-if="showCreateModal">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ editingStakeholder ? 'Edit' : 'Add' }} Stakeholder</h5>
            <button type="button" class="btn-close" @click="closeStakeholderModal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="saveStakeholder">
              <div class="row">
                <div class="col-md-6">
                  <div class="mb-3">
                    <label class="form-label">Name *</label>
                    <input
                      type="text"
                      class="form-control"
                      v-model="currentStakeholder.name"
                      required
                    >
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="mb-3">
                    <label class="form-label">Role</label>
                    <input
                      type="text"
                      class="form-control"
                      v-model="currentStakeholder.role"
                    >
                  </div>
                </div>
              </div>
              <div class="row">
                <div class="col-md-6">
                  <div class="mb-3">
                    <label class="form-label">Organization</label>
                    <input
                      type="text"
                      class="form-control"
                      v-model="currentStakeholder.organization"
                    >
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="mb-3">
                    <label class="form-label">Type *</label>
                    <select class="form-select" v-model="currentStakeholder.type" required>
                      <option value="internal">Internal</option>
                      <option value="external">External</option>
                      <option value="regulatory">Regulatory</option>
                    </select>
                  </div>
                </div>
              </div>
              <div class="row">
                <div class="col-md-6">
                  <div class="mb-3">
                    <label class="form-label">Interest Level</label>
                    <select class="form-select" v-model="currentStakeholder.interest_level">
                      <option value="1">Very Low</option>
                      <option value="2">Low</option>
                      <option value="3">Medium</option>
                      <option value="4">High</option>
                      <option value="5">Very High</option>
                    </select>
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="mb-3">
                    <label class="form-label">Influence Level</label>
                    <select class="form-select" v-model="currentStakeholder.influence_level">
                      <option value="low">Low</option>
                      <option value="medium">Medium</option>
                      <option value="high">High</option>
                    </select>
                  </div>
                </div>
              </div>
              <div class="mb-3">
                <label class="form-label">Contact Information</label>
                <textarea
                  class="form-control"
                  rows="2"
                  v-model="currentStakeholder.contact_info"
                  placeholder="Email, phone, address"
                ></textarea>
              </div>
              <div class="mb-3">
                <label class="form-label">Notes</label>
                <textarea
                  class="form-control"
                  rows="3"
                  v-model="currentStakeholder.notes"
                ></textarea>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="closeStakeholderModal">Cancel</button>
            <button type="button" class="btn btn-primary" @click="saveStakeholder" :disabled="saving">
              {{ saving ? 'Saving...' : 'Save Stakeholder' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import bcmContextService from '@/services/bcmContext'
import { useToast } from 'vue-toastification'

export default {
  name: 'BCMContext',
  setup() {
    const toast = useToast()

    // Reactive data
    const loading = ref(false)
    const saving = ref(false)
    const updatingProfile = ref(false)
    const showCreateModal = ref(false)
    const editingStakeholder = ref(false)
    const activeTab = ref('profile')
    const stakeholderSearch = ref('')
    const selectedStakeholderType = ref('')
    const selectedInfluence = ref('')

    const contextMetrics = reactive({
      totalStakeholders: 0,
      analysisComplete: 0,
      criticalIssues: 0,
      lastUpdate: null
    })

    const organizationProfile = reactive({
      name: '',
      industry: '',
      description: '',
      size: 'medium',
      location: '',
      bcmsScope: '',
      established: '',
      certificationStatus: '',
      lastReview: null
    })

    const currentStakeholder = reactive({
      id: null,
      name: '',
      role: '',
      organization: '',
      type: 'internal',
      interest_level: 3,
      influence_level: 'medium',
      contact_info: '',
      notes: '',
      engagement_status: 'active'
    })

    const contextTabs = ref([
      { id: 'profile', name: 'Organization', icon: 'fas fa-building' },
      { id: 'stakeholders', name: 'Stakeholders', icon: 'fas fa-users' },
      { id: 'analysis', name: 'Analysis', icon: 'fas fa-chart-bar' },
      { id: 'requirements', name: 'Requirements', icon: 'fas fa-list-check' }
    ])

    const industries = ref([
      'Manufacturing', 'Financial Services', 'Healthcare', 'Technology',
      'Retail', 'Government', 'Education', 'Telecommunications',
      'Energy & Utilities', 'Transportation', 'Other'
    ])

    const stakeholders = ref([])
    const internalFactors = ref([])
    const externalFactors = ref([])
    const requirements = ref([])
    const recentActivities = ref([])

    // Computed properties
    const filteredStakeholders = computed(() => {
      let filtered = stakeholders.value

      if (stakeholderSearch.value) {
        const search = stakeholderSearch.value.toLowerCase()
        filtered = filtered.filter(s =>
          s.name.toLowerCase().includes(search) ||
          s.role.toLowerCase().includes(search) ||
          s.organization.toLowerCase().includes(search)
        )
      }

      if (selectedStakeholderType.value) {
        filtered = filtered.filter(s => s.type === selectedStakeholderType.value)
      }

      if (selectedInfluence.value) {
        filtered = filtered.filter(s => s.influence_level === selectedInfluence.value)
      }

      return filtered
    })

    // Methods
    const loadContextData = async () => {
      loading.value = true
      try {
        const data = await bcmContextService.getOrganizationalContext()

        // Update metrics
        contextMetrics.totalStakeholders = data.metrics.total_stakeholders
        contextMetrics.analysisComplete = data.metrics.analysis_complete
        contextMetrics.criticalIssues = data.metrics.critical_issues
        contextMetrics.lastUpdate = data.metrics.last_update

        // Update profile
        Object.assign(organizationProfile, data.organization_profile)

        // Update stakeholders and factors
        stakeholders.value = data.stakeholders
        internalFactors.value = data.internal_factors
        externalFactors.value = data.external_factors
        requirements.value = data.requirements
      } catch (error) {
        toast.error('Failed to load organizational context')
      } finally {
        loading.value = false
      }
    }

    const loadRecentActivities = async () => {
      try {
        recentActivities.value = await bcmContextService.getRecentActivities()
      } catch (error) {
        console.error('Failed to load recent activities:', error)
      }
    }

    const refreshContext = () => {
      loadContextData()
      loadRecentActivities()
    }

    const refreshMatrix = () => {
      // Trigger matrix refresh
      loadContextData()
    }

    const updateProfile = async () => {
      updatingProfile.value = true
      try {
        await bcmContextService.updateOrganizationProfile(organizationProfile)
        toast.success('Organization profile updated successfully')
      } catch (error) {
        toast.error('Failed to update organization profile')
      } finally {
        updatingProfile.value = false
      }
    }

    const editStakeholder = (stakeholder) => {
      editingStakeholder.value = true
      Object.assign(currentStakeholder, stakeholder)
      showCreateModal.value = true
    }

    const saveStakeholder = async () => {
      saving.value = true
      try {
        if (editingStakeholder.value) {
          await bcmContextService.updateStakeholder(currentStakeholder.id, currentStakeholder)
          toast.success('Stakeholder updated successfully')
        } else {
          const newStakeholder = await bcmContextService.createStakeholder(currentStakeholder)
          stakeholders.value.push(newStakeholder)
          toast.success('Stakeholder created successfully')
        }
        closeStakeholderModal()
        loadContextData()
      } catch (error) {
        toast.error('Failed to save stakeholder')
      } finally {
        saving.value = false
      }
    }

    const deleteStakeholder = async (stakeholder) => {
      if (confirm(`Are you sure you want to delete ${stakeholder.name}?`)) {
        try {
          await bcmContextService.deleteStakeholder(stakeholder.id)
          stakeholders.value = stakeholders.value.filter(s => s.id !== stakeholder.id)
          toast.success('Stakeholder deleted successfully')
          loadContextData()
        } catch (error) {
          toast.error('Failed to delete stakeholder')
        }
      }
    }

    const contactStakeholder = (stakeholder) => {
      // Implement contact functionality
      toast.info(`Contact feature for ${stakeholder.name} coming soon`)
    }

    const closeStakeholderModal = () => {
      showCreateModal.value = false
      editingStakeholder.value = false
      resetCurrentStakeholder()
    }

    const resetCurrentStakeholder = () => {
      Object.assign(currentStakeholder, {
        id: null,
        name: '',
        role: '',
        organization: '',
        type: 'internal',
        interest_level: 3,
        influence_level: 'medium',
        contact_info: '',
        notes: '',
        engagement_status: 'active'
      })
    }

    const addFactor = (type) => {
      // Implement add factor functionality
      toast.info(`Add ${type} factor feature coming soon`)
    }

    const editFactor = (factor) => {
      // Implement edit factor functionality
      toast.info(`Edit factor feature coming soon`)
    }

    const editRequirement = (requirement) => {
      // Implement edit requirement functionality
      toast.info(`Edit requirement feature coming soon`)
    }

    const getMatrixStakeholders = (influence, interest) => {
      const interestMap = {
        high: [4, 5],
        low: [1, 2, 3]
      }

      return stakeholders.value.filter(s =>
        s.influence_level === influence &&
        interestMap[interest].includes(parseInt(s.interest_level))
      )
    }

    // Utility methods
    const getStakeholderTypeBadge = (type) => {
      const badges = {
        internal: 'bg-primary',
        external: 'bg-info',
        regulatory: 'bg-warning'
      }
      return badges[type] || 'bg-secondary'
    }

    const formatDate = (dateString) => {
      if (!dateString) return 'N/A'
      return new Date(dateString).toLocaleDateString()
    }

    const formatDateTime = (dateString) => {
      if (!dateString) return 'N/A'
      return new Date(dateString).toLocaleString()
    }

    // Lifecycle
    onMounted(() => {
      loadContextData()
      loadRecentActivities()
    })

    return {
      // Data
      loading,
      saving,
      updatingProfile,
      showCreateModal,
      editingStakeholder,
      activeTab,
      stakeholderSearch,
      selectedStakeholderType,
      selectedInfluence,
      contextMetrics,
      organizationProfile,
      currentStakeholder,
      contextTabs,
      industries,
      stakeholders,
      filteredStakeholders,
      internalFactors,
      externalFactors,
      requirements,
      recentActivities,

      // Methods
      refreshContext,
      refreshMatrix,
      updateProfile,
      editStakeholder,
      saveStakeholder,
      deleteStakeholder,
      contactStakeholder,
      closeStakeholderModal,
      addFactor,
      editFactor,
      editRequirement,
      getMatrixStakeholders,
      getStakeholderTypeBadge,
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

.bcm-context {
  min-height: 100vh;
  background: linear-gradient(135deg, var(--anthropic-light) 0%, #E8F2FF 100%);
}

.context-header {
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
}

.card-body {
  padding: 1.5rem;
}

.context-tabs {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.tab-btn {
  padding: 0.75rem 1.5rem;
  border: none;
  background: #F8F9FA;
  color: #6C757D;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.tab-btn:hover {
  background: #E9ECEF;
  color: var(--anthropic-dark);
}

.tab-btn.active {
  background: var(--anthropic-blue);
  color: white;
}

.context-tab-content {
  margin-top: 1rem;
}

.org-profile-section {
  background: #F8F9FA;
  padding: 1.5rem;
  border-radius: 8px;
}

.org-profile-section h4 {
  color: var(--anthropic-dark);
  margin-bottom: 1rem;
}

.context-summary {
  background: #F8F9FA;
  padding: 1.5rem;
  border-radius: 8px;
}

.context-summary h4 {
  color: var(--anthropic-dark);
  margin-bottom: 1rem;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 0;
  border-bottom: 1px solid #E9ECEF;
}

.summary-item:last-child {
  border-bottom: none;
}

.summary-label {
  color: #6C757D;
  font-weight: 500;
}

.summary-value {
  color: var(--anthropic-dark);
  font-weight: 600;
}

.stakeholder-info strong {
  color: var(--anthropic-dark);
}

.interest-rating .rating-stars {
  display: flex;
  gap: 0.1rem;
}

.interest-rating .fa-star {
  color: #DEE2E6;
  font-size: 0.8rem;
}

.interest-rating .fa-star.active {
  color: var(--anthropic-warning);
}

.influence-badge,
.engagement-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
}

.influence-badge.high,
.engagement-badge.active {
  background: #D4EDDA;
  color: var(--anthropic-success);
}

.influence-badge.medium,
.engagement-badge.moderate {
  background: #FFF3CD;
  color: var(--anthropic-warning);
}

.influence-badge.low,
.engagement-badge.inactive {
  background: #F8D7DA;
  color: var(--anthropic-danger);
}

.compliance-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
}

.compliance-badge.compliant {
  background: #D4EDDA;
  color: var(--anthropic-success);
}

.compliance-badge.non-compliant {
  background: #F8D7DA;
  color: var(--anthropic-danger);
}

.compliance-badge.partial {
  background: #FFF3CD;
  color: var(--anthropic-warning);
}

.action-buttons {
  display: flex;
  gap: 0.25rem;
}

.analysis-section {
  background: #F8F9FA;
  padding: 1.5rem;
  border-radius: 8px;
  margin-bottom: 1rem;
}

.analysis-section h4 {
  color: var(--anthropic-dark);
  margin-bottom: 1rem;
}

.factors-list {
  max-height: 400px;
  overflow-y: auto;
  margin-bottom: 1rem;
}

.factor-item {
  background: white;
  border: 1px solid #E9ECEF;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1rem;
}

.factor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.impact-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
}

.impact-badge.high {
  background: #F8D7DA;
  color: var(--anthropic-danger);
}

.impact-badge.medium {
  background: #FFF3CD;
  color: var(--anthropic-warning);
}

.impact-badge.low {
  background: #D4EDDA;
  color: var(--anthropic-success);
}

.factor-description {
  color: #6C757D;
  margin-bottom: 1rem;
}

.requirements-list,
.expectations-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.requirements-list li,
.expectations-list li {
  padding: 0.25rem 0;
  color: #6C757D;
}

.stakeholder-matrix {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  min-height: 400px;
}

.matrix-quadrant {
  border: 2px solid #E9ECEF;
  border-radius: 8px;
  padding: 1rem;
  position: relative;
}

.matrix-quadrant h5 {
  color: var(--anthropic-dark);
  margin-bottom: 1rem;
  text-align: center;
  font-size: 1rem;
}

.matrix-quadrant.high-high {
  border-color: var(--anthropic-danger);
  background: rgba(220, 53, 69, 0.05);
}

.matrix-quadrant.high-low {
  border-color: var(--anthropic-warning);
  background: rgba(255, 193, 7, 0.05);
}

.matrix-quadrant.low-high {
  border-color: var(--anthropic-blue);
  background: rgba(74, 144, 226, 0.05);
}

.matrix-quadrant.low-low {
  border-color: #6C757D;
  background: rgba(108, 117, 125, 0.05);
}

.quadrant-stakeholders {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.matrix-stakeholder {
  background: white;
  padding: 0.5rem;
  border-radius: 4px;
  border: 1px solid #E9ECEF;
  font-size: 0.9rem;
  text-align: center;
}

.activity-timeline {
  max-height: 400px;
  overflow-y: auto;
}

.activity-item {
  padding: 1rem 0;
  border-bottom: 1px solid #E9ECEF;
}

.activity-item:last-child {
  border-bottom: none;
}

.activity-time {
  font-size: 0.8rem;
  color: #6C757D;
  margin-bottom: 0.5rem;
}

.activity-content strong {
  color: var(--anthropic-dark);
}

.activity-content p {
  color: #6C757D;
  margin: 0.25rem 0 0 0;
  font-size: 0.9rem;
}

.modal.show {
  display: block;
}

.modal-content {
  border-radius: 12px;
  border: none;
  box-shadow: 0 10px 30px rgba(0,0,0,0.3);
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

.btn-outline-primary {
  border: 1px solid var(--anthropic-blue);
  color: var(--anthropic-blue);
}

.btn-outline-info {
  border: 1px solid var(--anthropic-blue);
  color: var(--anthropic-blue);
}

.btn-outline-danger {
  border: 1px solid var(--anthropic-danger);
  color: var(--anthropic-danger);
}

/* Responsive Design */
@media (max-width: 768px) {
  .page-title {
    font-size: 2rem;
  }

  .context-tabs {
    flex-direction: column;
  }

  .tab-btn {
    justify-content: center;
  }

  .stakeholder-matrix {
    grid-template-columns: 1fr;
  }

  .action-buttons {
    flex-wrap: wrap;
  }
}
</style>