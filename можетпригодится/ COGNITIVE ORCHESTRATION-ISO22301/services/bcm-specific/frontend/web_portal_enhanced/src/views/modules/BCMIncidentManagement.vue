<template>
  <div class="bcm-incident-management">
    <!-- Header Section -->
    <div class="incident-header">
      <div class="container-fluid">
        <div class="row align-items-center">
          <div class="col-md-8">
            <h1 class="page-title">Advanced Incident Management</h1>
            <p class="page-subtitle">Crisis Management & Recovery Coordination</p>
          </div>
          <div class="col-md-4 text-end">
            <button class="btn btn-danger me-2" @click="declareEmergency">
              <i class="fas fa-exclamation-triangle"></i> Declare Emergency
            </button>
            <button class="btn btn-primary me-2" @click="showCreateModal = true">
              <i class="fas fa-plus"></i> New Incident
            </button>
            <button class="btn btn-outline-primary" @click="refreshIncidents">
              <i class="fas fa-sync"></i> Refresh
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Incident Overview Dashboard -->
    <div class="overview-section">
      <div class="container-fluid">
        <div class="row">
          <div class="col-md-3">
            <div class="metric-card danger">
              <div class="metric-icon">
                <i class="fas fa-fire-alt"></i>
              </div>
              <div class="metric-content">
                <h3 class="metric-value">{{ incidentMetrics.activeIncidents }}</h3>
                <p class="metric-label">Active Incidents</p>
              </div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="metric-card warning">
              <div class="metric-icon">
                <i class="fas fa-clock"></i>
              </div>
              <div class="metric-content">
                <h3 class="metric-value">{{ incidentMetrics.avgResponseTime }}m</h3>
                <p class="metric-label">Avg Response Time</p>
              </div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="metric-card success">
              <div class="metric-icon">
                <i class="fas fa-check-circle"></i>
              </div>
              <div class="metric-content">
                <h3 class="metric-value">{{ incidentMetrics.resolvedIncidents }}</h3>
                <p class="metric-label">Resolved This Month</p>
              </div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="metric-card info">
              <div class="metric-icon">
                <i class="fas fa-users"></i>
              </div>
              <div class="metric-content">
                <h3 class="metric-value">{{ incidentMetrics.teamMembers }}</h3>
                <p class="metric-label">Response Team</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Emergency Status Banner -->
    <div v-if="emergencyActive" class="emergency-banner">
      <div class="container-fluid">
        <div class="alert alert-danger d-flex align-items-center">
          <div class="emergency-pulse"></div>
          <div class="flex-grow-1">
            <strong>EMERGENCY ACTIVE:</strong> {{ activeEmergency.title }}
            <small class="d-block">Declared: {{ formatDateTime(activeEmergency.declared_at) }}</small>
          </div>
          <div class="emergency-actions">
            <button class="btn btn-outline-light btn-sm me-2" @click="viewEmergency">
              View Details
            </button>
            <button class="btn btn-light btn-sm" @click="endEmergency">
              End Emergency
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Incident Management Tabs -->
    <div class="content-section">
      <div class="container-fluid">
        <div class="row">
          <div class="col-12">
            <div class="content-card">
              <div class="card-header">
                <div class="incident-tabs">
                  <button
                    v-for="tab in incidentTabs"
                    :key="tab.id"
                    class="tab-btn"
                    :class="{ active: activeTab === tab.id }"
                    @click="activeTab = tab.id"
                  >
                    <i :class="tab.icon"></i>
                    {{ tab.name }}
                    <span v-if="tab.count" class="tab-count">{{ tab.count }}</span>
                  </button>
                </div>
              </div>
              <div class="card-body">
                <!-- Active Incidents Tab -->
                <div v-if="activeTab === 'active'" class="tab-content">
                  <div class="incident-controls mb-3">
                    <div class="row align-items-center">
                      <div class="col-md-6">
                        <div class="search-box">
                          <input
                            type="text"
                            class="form-control"
                            v-model="incidentSearch"
                            placeholder="Search incidents..."
                          >
                        </div>
                      </div>
                      <div class="col-md-6 text-end">
                        <select class="form-select d-inline-block w-auto me-2" v-model="selectedSeverity">
                          <option value="">All Severities</option>
                          <option value="critical">Critical</option>
                          <option value="high">High</option>
                          <option value="medium">Medium</option>
                          <option value="low">Low</option>
                        </select>
                      </div>
                    </div>
                  </div>

                  <div class="incidents-grid">
                    <div
                      v-for="incident in filteredIncidents"
                      :key="incident.id"
                      class="incident-card"
                      :class="getSeverityClass(incident.severity)"
                    >
                      <div class="incident-header">
                        <div class="incident-id">{{ incident.incident_id }}</div>
                        <div class="incident-time">{{ formatDateTime(incident.created_date) }}</div>
                      </div>
                      <div class="incident-content">
                        <h5 class="incident-title">{{ incident.title }}</h5>
                        <p class="incident-description">{{ incident.description }}</p>
                        <div class="incident-meta">
                          <span class="severity-badge" :class="incident.severity">
                            {{ incident.severity.toUpperCase() }}
                          </span>
                          <span class="status-badge" :class="incident.status">
                            {{ getStatusLabel(incident.status) }}
                          </span>
                        </div>
                      </div>
                      <div class="incident-footer">
                        <div class="incident-assignee">
                          <small class="text-muted">Assigned to:</small>
                          <strong>{{ incident.assignee_name }}</strong>
                        </div>
                        <div class="incident-actions">
                          <button class="btn btn-sm btn-outline-primary" @click="viewIncident(incident)">
                            <i class="fas fa-eye"></i>
                          </button>
                          <button class="btn btn-sm btn-outline-success" @click="updateStatus(incident)">
                            <i class="fas fa-edit"></i>
                          </button>
                          <button class="btn btn-sm btn-outline-warning" @click="escalateIncident(incident)">
                            <i class="fas fa-arrow-up"></i>
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Crisis Response Tab -->
                <div v-if="activeTab === 'crisis'" class="tab-content">
                  <div class="crisis-dashboard">
                    <div class="row">
                      <div class="col-md-8">
                        <div class="crisis-timeline">
                          <h4>Crisis Response Timeline</h4>
                          <div class="timeline-events">
                            <div
                              v-for="event in crisisEvents"
                              :key="event.id"
                              class="timeline-event"
                            >
                              <div class="event-time">{{ formatTime(event.timestamp) }}</div>
                              <div class="event-icon" :class="event.type">
                                <i :class="event.icon"></i>
                              </div>
                              <div class="event-content">
                                <strong>{{ event.title }}</strong>
                                <p>{{ event.description }}</p>
                                <small class="text-muted">{{ event.user_name }}</small>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                      <div class="col-md-4">
                        <div class="crisis-actions">
                          <h4>Quick Actions</h4>
                          <div class="action-buttons-vertical">
                            <button class="btn btn-danger mb-2" @click="activateCrisisTeam">
                              <i class="fas fa-users"></i> Activate Crisis Team
                            </button>
                            <button class="btn btn-warning mb-2" @click="sendCommunication">
                              <i class="fas fa-bullhorn"></i> Send Communication
                            </button>
                            <button class="btn btn-info mb-2" @click="activateRecovery">
                              <i class="fas fa-tools"></i> Activate Recovery
                            </button>
                            <button class="btn btn-secondary mb-2" @click="generateReport">
                              <i class="fas fa-file-alt"></i> Generate Report
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Recovery Tab -->
                <div v-if="activeTab === 'recovery'" class="tab-content">
                  <div class="recovery-dashboard">
                    <div class="row">
                      <div class="col-md-6">
                        <div class="recovery-processes">
                          <h4>Recovery Processes</h4>
                          <div class="process-list">
                            <div
                              v-for="process in recoveryProcesses"
                              :key="process.id"
                              class="process-item"
                            >
                              <div class="process-header">
                                <strong>{{ process.name }}</strong>
                                <span class="process-status" :class="process.status">
                                  {{ process.status }}
                                </span>
                              </div>
                              <div class="process-progress">
                                <div class="progress">
                                  <div
                                    class="progress-bar"
                                    :style="`width: ${process.completion}%`"
                                    :class="getProgressClass(process.completion)"
                                  ></div>
                                </div>
                                <small>{{ process.completion }}% Complete</small>
                              </div>
                              <div class="process-details">
                                <small class="text-muted">
                                  RTO: {{ process.rto }}h | RPO: {{ process.rpo }}h
                                </small>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                      <div class="col-md-6">
                        <div class="recovery-metrics">
                          <h4>Recovery Metrics</h4>
                          <div class="metrics-grid">
                            <div class="metric-item">
                              <div class="metric-label">Total Recovery Time</div>
                              <div class="metric-value">{{ recoveryMetrics.totalTime }}h</div>
                            </div>
                            <div class="metric-item">
                              <div class="metric-label">Data Recovery</div>
                              <div class="metric-value">{{ recoveryMetrics.dataRecovery }}%</div>
                            </div>
                            <div class="metric-item">
                              <div class="metric-label">Service Availability</div>
                              <div class="metric-value">{{ recoveryMetrics.availability }}%</div>
                            </div>
                            <div class="metric-item">
                              <div class="metric-label">Recovery Cost</div>
                              <div class="metric-value">${{ recoveryMetrics.cost }}</div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Analytics Tab -->
                <div v-if="activeTab === 'analytics'" class="tab-content">
                  <div class="analytics-dashboard">
                    <div class="row">
                      <div class="col-md-6">
                        <div class="chart-container">
                          <h4>Incident Trends</h4>
                          <canvas id="incidentTrendsChart"></canvas>
                        </div>
                      </div>
                      <div class="col-md-6">
                        <div class="chart-container">
                          <h4>Response Time Analysis</h4>
                          <canvas id="responseTimeChart"></canvas>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Incident Modal -->
    <div class="modal fade" :class="{ show: showCreateModal }" tabindex="-1" v-if="showCreateModal">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Create New Incident</h5>
            <button type="button" class="btn-close" @click="closeIncidentModal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="createIncident">
              <div class="mb-3">
                <label class="form-label">Incident Title *</label>
                <input type="text" class="form-control" v-model="newIncident.title" required>
              </div>
              <div class="mb-3">
                <label class="form-label">Description</label>
                <textarea class="form-control" rows="4" v-model="newIncident.description"></textarea>
              </div>
              <div class="row">
                <div class="col-md-6">
                  <div class="mb-3">
                    <label class="form-label">Severity *</label>
                    <select class="form-select" v-model="newIncident.severity" required>
                      <option value="critical">Critical</option>
                      <option value="high">High</option>
                      <option value="medium">Medium</option>
                      <option value="low">Low</option>
                    </select>
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="mb-3">
                    <label class="form-label">Category</label>
                    <select class="form-select" v-model="newIncident.category">
                      <option value="system">System Failure</option>
                      <option value="security">Security Incident</option>
                      <option value="data">Data Loss</option>
                      <option value="natural">Natural Disaster</option>
                      <option value="human">Human Error</option>
                    </select>
                  </div>
                </div>
              </div>
              <div class="mb-3">
                <label class="form-label">Affected Services</label>
                <input type="text" class="form-control" v-model="newIncident.affected_services">
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="closeIncidentModal">Cancel</button>
            <button type="button" class="btn btn-primary" @click="createIncident" :disabled="creating">
              {{ creating ? 'Creating...' : 'Create Incident' }}
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
import bcmIncidentManagementService from '@/services/bcmIncidentManagement'
import { useToast } from 'vue-toastification'

export default {
  name: 'BCMIncidentManagement',
  setup() {
    const router = useRouter()
    const toast = useToast()

    // Reactive data
    const loading = ref(false)
    const creating = ref(false)
    const showCreateModal = ref(false)
    const activeTab = ref('active')
    const incidentSearch = ref('')
    const selectedSeverity = ref('')
    const emergencyActive = ref(false)

    const incidentMetrics = reactive({
      activeIncidents: 0,
      avgResponseTime: 0,
      resolvedIncidents: 0,
      teamMembers: 0
    })

    const newIncident = reactive({
      title: '',
      description: '',
      severity: 'medium',
      category: 'system',
      affected_services: ''
    })

    const activeEmergency = reactive({})
    const recoveryMetrics = reactive({
      totalTime: 0,
      dataRecovery: 0,
      availability: 0,
      cost: 0
    })

    const incidentTabs = ref([
      { id: 'active', name: 'Active Incidents', icon: 'fas fa-fire-alt', count: 0 },
      { id: 'crisis', name: 'Crisis Response', icon: 'fas fa-exclamation-triangle' },
      { id: 'recovery', name: 'Recovery', icon: 'fas fa-tools' },
      { id: 'analytics', name: 'Analytics', icon: 'fas fa-chart-bar' }
    ])

    const incidents = ref([])
    const crisisEvents = ref([])
    const recoveryProcesses = ref([])

    // Computed properties
    const filteredIncidents = computed(() => {
      let filtered = incidents.value

      if (incidentSearch.value) {
        const search = incidentSearch.value.toLowerCase()
        filtered = filtered.filter(i =>
          i.title.toLowerCase().includes(search) ||
          i.incident_id.toLowerCase().includes(search)
        )
      }

      if (selectedSeverity.value) {
        filtered = filtered.filter(i => i.severity === selectedSeverity.value)
      }

      return filtered
    })

    // Methods
    const loadIncidents = async () => {
      loading.value = true
      try {
        const data = await bcmIncidentManagementService.getIncidents()
        incidents.value = data.incidents
        incidentMetrics.activeIncidents = data.metrics.active_incidents
        incidentMetrics.avgResponseTime = data.metrics.avg_response_time
        incidentMetrics.resolvedIncidents = data.metrics.resolved_incidents
        incidentMetrics.teamMembers = data.metrics.team_members

        // Update tab counts
        incidentTabs.value[0].count = incidentMetrics.activeIncidents
      } catch (error) {
        toast.error('Failed to load incidents')
      } finally {
        loading.value = false
      }
    }

    const loadCrisisData = async () => {
      try {
        crisisEvents.value = await bcmIncidentManagementService.getCrisisEvents()
      } catch (error) {
        console.error('Failed to load crisis data:', error)
      }
    }

    const loadRecoveryData = async () => {
      try {
        const data = await bcmIncidentManagementService.getRecoveryData()
        recoveryProcesses.value = data.processes
        Object.assign(recoveryMetrics, data.metrics)
      } catch (error) {
        console.error('Failed to load recovery data:', error)
      }
    }

    const refreshIncidents = () => {
      loadIncidents()
      loadCrisisData()
      loadRecoveryData()
    }

    const createIncident = async () => {
      creating.value = true
      try {
        await bcmIncidentManagementService.createIncident(newIncident)
        toast.success('Incident created successfully')
        closeIncidentModal()
        loadIncidents()
      } catch (error) {
        toast.error('Failed to create incident')
      } finally {
        creating.value = false
      }
    }

    const viewIncident = (incident) => {
      router.push(`/incidents/${incident.id}/view`)
    }

    const updateStatus = (incident) => {
      router.push(`/incidents/${incident.id}/update`)
    }

    const escalateIncident = async (incident) => {
      try {
        await bcmIncidentManagementService.escalateIncident(incident.id)
        toast.success('Incident escalated successfully')
        loadIncidents()
      } catch (error) {
        toast.error('Failed to escalate incident')
      }
    }

    const declareEmergency = () => {
      toast.info('Declare emergency feature coming soon')
    }

    const endEmergency = () => {
      emergencyActive.value = false
      toast.success('Emergency ended')
    }

    const activateCrisisTeam = () => {
      toast.info('Crisis team activation feature coming soon')
    }

    const sendCommunication = () => {
      toast.info('Communication feature coming soon')
    }

    const activateRecovery = () => {
      toast.info('Recovery activation feature coming soon')
    }

    const generateReport = () => {
      toast.info('Report generation feature coming soon')
    }

    const closeIncidentModal = () => {
      showCreateModal.value = false
      resetNewIncident()
    }

    const resetNewIncident = () => {
      Object.assign(newIncident, {
        title: '',
        description: '',
        severity: 'medium',
        category: 'system',
        affected_services: ''
      })
    }

    // Utility methods
    const getSeverityClass = (severity) => {
      const classes = {
        critical: 'incident-critical',
        high: 'incident-high',
        medium: 'incident-medium',
        low: 'incident-low'
      }
      return classes[severity] || 'incident-medium'
    }

    const getStatusLabel = (status) => {
      const labels = {
        open: 'Open',
        investigating: 'Investigating',
        resolving: 'Resolving',
        resolved: 'Resolved',
        closed: 'Closed'
      }
      return labels[status] || status
    }

    const getProgressClass = (progress) => {
      if (progress >= 80) return 'bg-success'
      if (progress >= 60) return 'bg-info'
      if (progress >= 40) return 'bg-warning'
      return 'bg-danger'
    }

    const formatDateTime = (dateString) => {
      if (!dateString) return 'N/A'
      return new Date(dateString).toLocaleString()
    }

    const formatTime = (dateString) => {
      if (!dateString) return 'N/A'
      return new Date(dateString).toLocaleTimeString()
    }

    // Lifecycle
    onMounted(() => {
      loadIncidents()
      loadCrisisData()
      loadRecoveryData()
    })

    return {
      // Data
      loading,
      creating,
      showCreateModal,
      activeTab,
      incidentSearch,
      selectedSeverity,
      emergencyActive,
      incidentMetrics,
      newIncident,
      activeEmergency,
      recoveryMetrics,
      incidentTabs,
      incidents,
      filteredIncidents,
      crisisEvents,
      recoveryProcesses,

      // Methods
      refreshIncidents,
      createIncident,
      viewIncident,
      updateStatus,
      escalateIncident,
      declareEmergency,
      endEmergency,
      activateCrisisTeam,
      sendCommunication,
      activateRecovery,
      generateReport,
      closeIncidentModal,
      getSeverityClass,
      getStatusLabel,
      getProgressClass,
      formatDateTime,
      formatTime
    }
  }
}
</script>

<style scoped>
/* Anthropic styling with incident-specific enhancements */
:root {
  --anthropic-orange: #FF6B35;
  --anthropic-blue: #4A90E2;
  --anthropic-dark: #1A1A1A;
  --anthropic-light: #F8F9FA;
  --anthropic-success: #28A745;
  --anthropic-warning: #FFC107;
  --anthropic-danger: #DC3545;
}

.emergency-banner {
  animation: pulse-red 2s infinite;
}

.emergency-pulse {
  width: 20px;
  height: 20px;
  background: #fff;
  border-radius: 50%;
  margin-right: 1rem;
  animation: pulse 1s infinite;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}

@keyframes pulse-red {
  0% { background-color: rgba(220, 53, 69, 0.1); }
  50% { background-color: rgba(220, 53, 69, 0.2); }
  100% { background-color: rgba(220, 53, 69, 0.1); }
}

.incidents-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 1rem;
}

.incident-card {
  background: white;
  border: 1px solid #E9ECEF;
  border-radius: 12px;
  padding: 1rem;
  transition: all 0.2s ease;
}

.incident-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0,0,0,0.12);
}

.incident-card.incident-critical {
  border-left: 4px solid var(--anthropic-danger);
}

.incident-card.incident-high {
  border-left: 4px solid var(--anthropic-warning);
}

.incident-card.incident-medium {
  border-left: 4px solid var(--anthropic-blue);
}

.incident-card.incident-low {
  border-left: 4px solid var(--anthropic-success);
}

.tab-count {
  background: var(--anthropic-danger);
  color: white;
  border-radius: 12px;
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
  margin-left: 0.5rem;
}

.timeline-event {
  display: flex;
  gap: 1rem;
  padding: 1rem 0;
  border-left: 2px solid #E9ECEF;
  margin-left: 1rem;
  position: relative;
}

.timeline-event::before {
  content: '';
  position: absolute;
  left: -5px;
  top: 1.5rem;
  width: 8px;
  height: 8px;
  background: var(--anthropic-blue);
  border-radius: 50%;
}

.action-buttons-vertical .btn {
  width: 100%;
  text-align: left;
}

.process-progress .progress {
  height: 8px;
  margin: 0.5rem 0;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.metric-item {
  background: #F8F9FA;
  padding: 1rem;
  border-radius: 8px;
  text-align: center;
}

.metric-label {
  font-size: 0.9rem;
  color: #6C757D;
  margin-bottom: 0.5rem;
}

.metric-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--anthropic-dark);
}
</style>