<template>
  <div class="bcm-incident-management">
    <!-- Header Section -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-info">
          <h1 class="page-title">
            <i class="fas fa-exclamation-triangle"></i>
            Incident Management
          </h1>
          <p class="page-subtitle">
            Manage business continuity incidents with AI-powered classification and response coordination
          </p>
        </div>
        <div class="header-actions">
          <button
            class="btn btn-primary"
            @click="showCreateForm = true"
            :disabled="loading"
          >
            <i class="fas fa-plus"></i>
            New Incident
          </button>
        </div>
      </div>

      <!-- Quick Stats -->
      <div class="quick-stats">
        <div class="stat-card critical">
          <div class="stat-icon">
            <i class="fas fa-fire"></i>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.by_severity.critical || 0 }}</div>
            <div class="stat-label">Critical</div>
          </div>
        </div>
        <div class="stat-card high">
          <div class="stat-icon">
            <i class="fas fa-exclamation"></i>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.by_severity.high || 0 }}</div>
            <div class="stat-label">High Priority</div>
          </div>
        </div>
        <div class="stat-card medium">
          <div class="stat-icon">
            <i class="fas fa-minus-circle"></i>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ activeIncidents.length }}</div>
            <div class="stat-label">Active</div>
          </div>
        </div>
        <div class="stat-card success">
          <div class="stat-icon">
            <i class="fas fa-clock"></i>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.avg_resolution_time || 0 }}h</div>
            <div class="stat-label">Avg Resolution</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="main-content">
      <!-- Filters and Search -->
      <div class="content-toolbar">
        <div class="search-section">
          <div class="search-input">
            <i class="fas fa-search"></i>
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search incidents..."
              @input="debouncedSearch"
            />
          </div>
        </div>

        <div class="filter-section">
          <select v-model="filterSeverity" @change="applyFilters" class="filter-select">
            <option value="">All Severities</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>

          <select v-model="filterStatus" @change="applyFilters" class="filter-select">
            <option value="">All Statuses</option>
            <option value="open">Open</option>
            <option value="in_progress">In Progress</option>
            <option value="escalated">Escalated</option>
            <option value="resolved">Resolved</option>
          </select>

          <button class="btn btn-outline" @click="exportIncidents">
            <i class="fas fa-download"></i>
            Export
          </button>
        </div>
      </div>

      <!-- Incidents Table -->
      <div class="incidents-table-container">
        <div v-if="loading" class="loading-state">
          <div class="spinner"></div>
          <p>Loading incidents...</p>
        </div>

        <div v-else-if="error" class="error-state">
          <div class="error-icon">
            <i class="fas fa-exclamation-circle"></i>
          </div>
          <h3>Unable to Load Incidents</h3>
          <p>{{ error }}</p>
          <button class="btn btn-primary" @click="loadIncidents">
            <i class="fas fa-refresh"></i>
            Retry
          </button>
        </div>

        <div v-else>
          <table class="incidents-table">
            <thead>
              <tr>
                <th @click="sortBy('severity')" class="sortable">
                  Severity
                  <i class="fas fa-sort" v-if="sortField !== 'severity'"></i>
                  <i class="fas fa-sort-up" v-else-if="sortOrder === 'asc'"></i>
                  <i class="fas fa-sort-down" v-else></i>
                </th>
                <th @click="sortBy('name')" class="sortable">
                  Incident
                  <i class="fas fa-sort" v-if="sortField !== 'name'"></i>
                  <i class="fas fa-sort-up" v-else-if="sortOrder === 'asc'"></i>
                  <i class="fas fa-sort-down" v-else></i>
                </th>
                <th>Status</th>
                <th>Type</th>
                <th>Response Team</th>
                <th @click="sortBy('created_date')" class="sortable">
                  Created
                  <i class="fas fa-sort" v-if="sortField !== 'created_date'"></i>
                  <i class="fas fa-sort-up" v-else-if="sortOrder === 'asc'"></i>
                  <i class="fas fa-sort-down" v-else></i>
                </th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="incident in paginatedIncidents"
                :key="incident.id"
                class="incident-row"
                @click="selectIncident(incident)"
                :class="{ 'selected': selectedIncident?.id === incident.id }"
              >
                <td>
                  <span class="severity-badge" :class="incident.severity">
                    {{ incident.severity.toUpperCase() }}
                  </span>
                </td>
                <td class="incident-info">
                  <div class="incident-title">{{ incident.name }}</div>
                  <div class="incident-description">
                    {{ truncateText(incident.description, 100) }}
                  </div>
                </td>
                <td>
                  <span class="status-badge" :class="incident.status">
                    {{ formatStatus(incident.status) }}
                  </span>
                </td>
                <td>
                  <span class="type-tag">{{ formatType(incident.incident_type) }}</span>
                </td>
                <td>
                  <div class="team-info" v-if="incident.response_team_ids?.length">
                    <span class="team-count">{{ incident.response_team_ids.length }} team(s)</span>
                  </div>
                  <span v-else class="no-team">Not assigned</span>
                </td>
                <td class="date-cell">
                  {{ formatDate(incident.created_date) }}
                </td>
                <td class="actions-cell">
                  <div class="action-buttons">
                    <button
                      class="btn-icon"
                      @click.stop="viewIncident(incident)"
                      title="View Details"
                    >
                      <i class="fas fa-eye"></i>
                    </button>
                    <button
                      class="btn-icon"
                      @click.stop="editIncident(incident)"
                      title="Edit"
                      v-if="incident.status !== 'resolved'"
                    >
                      <i class="fas fa-edit"></i>
                    </button>
                    <button
                      class="btn-icon danger"
                      @click.stop="escalateIncident(incident)"
                      title="Escalate"
                      v-if="incident.status !== 'resolved' && incident.escalation_level < 3"
                    >
                      <i class="fas fa-arrow-up"></i>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>

          <!-- Pagination -->
          <div class="pagination-container" v-if="totalPages > 1">
            <button
              class="btn btn-outline"
              @click="currentPage--"
              :disabled="currentPage === 1"
            >
              <i class="fas fa-chevron-left"></i>
            </button>

            <span class="page-info">
              Page {{ currentPage }} of {{ totalPages }}
              ({{ filteredIncidents.length }} incidents)
            </span>

            <button
              class="btn btn-outline"
              @click="currentPage++"
              :disabled="currentPage === totalPages"
            >
              <i class="fas fa-chevron-right"></i>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Create/Edit Incident Form Modal -->
    <div v-if="showCreateForm || showEditForm" class="modal-overlay" @click="closeModal">
      <div class="modal-container" @click.stop>
        <div class="modal-header">
          <h2>
            <i class="fas fa-plus-circle" v-if="showCreateForm"></i>
            <i class="fas fa-edit" v-if="showEditForm"></i>
            {{ showCreateForm ? 'Create New Incident' : 'Edit Incident' }}
          </h2>
          <button class="btn-close" @click="closeModal">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-body">
          <form @submit.prevent="submitIncident" class="incident-form">
            <div class="form-grid">
              <div class="form-group">
                <label for="incident-title">Incident Title *</label>
                <input
                  id="incident-title"
                  v-model="form.title"
                  type="text"
                  class="form-input"
                  placeholder="Brief description of the incident"
                  required
                />
              </div>

              <div class="form-group">
                <label for="incident-severity">Severity *</label>
                <select id="incident-severity" v-model="form.severity" class="form-select" required>
                  <option value="">Select severity</option>
                  <option value="low">Low - Minor impact</option>
                  <option value="medium">Medium - Moderate impact</option>
                  <option value="high">High - Significant impact</option>
                  <option value="critical">Critical - Severe impact</option>
                </select>
              </div>

              <div class="form-group full-width">
                <label for="incident-description">Description *</label>
                <textarea
                  id="incident-description"
                  v-model="form.description"
                  class="form-textarea"
                  placeholder="Detailed description of the incident"
                  rows="4"
                  required
                ></textarea>
              </div>

              <div class="form-group">
                <label for="incident-type">Incident Type</label>
                <select id="incident-type" v-model="form.incident_type" class="form-select">
                  <option value="operational">Operational</option>
                  <option value="security">Security</option>
                  <option value="technology">Technology</option>
                  <option value="environmental">Environmental</option>
                  <option value="human_resources">Human Resources</option>
                  <option value="supply_chain">Supply Chain</option>
                </select>
              </div>

              <div class="form-group">
                <label for="incident-location">Location</label>
                <input
                  id="incident-location"
                  v-model="form.location"
                  type="text"
                  class="form-input"
                  placeholder="Incident location"
                />
              </div>

              <div class="form-group">
                <label for="impact-level">Impact Level</label>
                <select id="impact-level" v-model="form.impact_level" class="form-select">
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                </select>
              </div>

              <div class="form-group">
                <label for="response-team">Response Team</label>
                <select id="response-team" v-model="form.response_team_ids" class="form-select" multiple>
                  <option v-for="team in responseTeams" :key="team.id" :value="team.id">
                    {{ team.name }}
                  </option>
                </select>
              </div>

              <div class="form-group full-width">
                <label for="affected-systems">Affected Systems</label>
                <input
                  id="affected-systems"
                  v-model="form.affected_systems_text"
                  type="text"
                  class="form-input"
                  placeholder="Comma-separated list of affected systems"
                />
              </div>

              <div class="form-group full-width">
                <div class="checkbox-group">
                  <label class="checkbox-label">
                    <input
                      type="checkbox"
                      v-model="form.use_ai_classification"
                    />
                    <span class="checkmark"></span>
                    Use AI-powered incident classification
                  </label>
                </div>
              </div>
            </div>

            <div class="form-actions">
              <button type="button" class="btn btn-outline" @click="closeModal">
                Cancel
              </button>
              <button
                type="submit"
                class="btn btn-primary"
                :disabled="submitting"
              >
                <i class="fas fa-spinner fa-spin" v-if="submitting"></i>
                <i class="fas fa-save" v-else></i>
                {{ submitting ? 'Saving...' : (showCreateForm ? 'Create Incident' : 'Update Incident') }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Incident Detail Panel -->
    <div v-if="selectedIncident && showDetailPanel" class="detail-panel">
      <div class="detail-header">
        <h3>{{ selectedIncident.name }}</h3>
        <button class="btn-close" @click="closeDetailPanel">
          <i class="fas fa-times"></i>
        </button>
      </div>

      <div class="detail-content">
        <div class="detail-section">
          <h4>Information</h4>
          <div class="info-grid">
            <div class="info-item">
              <label>Status</label>
              <span class="status-badge" :class="selectedIncident.status">
                {{ formatStatus(selectedIncident.status) }}
              </span>
            </div>
            <div class="info-item">
              <label>Severity</label>
              <span class="severity-badge" :class="selectedIncident.severity">
                {{ selectedIncident.severity.toUpperCase() }}
              </span>
            </div>
            <div class="info-item">
              <label>Type</label>
              <span>{{ formatType(selectedIncident.incident_type) }}</span>
            </div>
            <div class="info-item">
              <label>Location</label>
              <span>{{ selectedIncident.location || 'Not specified' }}</span>
            </div>
          </div>
        </div>

        <div class="detail-section">
          <h4>Description</h4>
          <p>{{ selectedIncident.description }}</p>
        </div>

        <div class="detail-section" v-if="selectedIncident.classification">
          <h4>AI Classification</h4>
          <div class="ai-classification">
            <div class="classification-item">
              <strong>Category:</strong> {{ selectedIncident.classification }}
            </div>
            <div class="classification-item" v-if="selectedIncident.ai_confidence">
              <strong>Confidence:</strong>
              <div class="confidence-bar">
                <div
                  class="confidence-fill"
                  :style="{ width: (selectedIncident.ai_confidence * 100) + '%' }"
                ></div>
              </div>
              {{ Math.round(selectedIncident.ai_confidence * 100) }}%
            </div>
          </div>
        </div>

        <div class="detail-section">
          <h4>Timeline</h4>
          <div class="timeline" v-if="selectedIncident.timeline_ids?.length">
            <div class="timeline-item" v-for="entry in incidentTimeline" :key="entry.id">
              <div class="timeline-marker"></div>
              <div class="timeline-content">
                <div class="timeline-time">{{ formatDateTime(entry.timestamp) }}</div>
                <div class="timeline-description">{{ entry.description }}</div>
              </div>
            </div>
          </div>
          <div v-else class="empty-timeline">
            <p>No timeline entries yet.</p>
          </div>

          <div class="timeline-actions">
            <button class="btn btn-outline" @click="showTimelineForm = true">
              <i class="fas fa-plus"></i>
              Add Entry
            </button>
          </div>
        </div>
      </div>

      <div class="detail-actions">
        <button
          class="btn btn-success"
          @click="resolveIncident(selectedIncident)"
          v-if="selectedIncident.status !== 'resolved'"
        >
          <i class="fas fa-check"></i>
          Resolve
        </button>
        <button
          class="btn btn-warning"
          @click="escalateIncident(selectedIncident)"
          v-if="selectedIncident.status !== 'resolved'"
        >
          <i class="fas fa-arrow-up"></i>
          Escalate
        </button>
        <button class="btn btn-outline" @click="generateResponsePlan(selectedIncident)">
          <i class="fas fa-file-alt"></i>
          Generate Plan
        </button>
      </div>
    </div>

    <!-- Assistant Panel Integration -->
    <AssistantPanel ref="assistant" />

    <!-- Notification Toast -->
    <div v-if="notification" class="notification-toast" :class="notification.type">
      <i :class="getNotificationIcon(notification.type)"></i>
      <span>{{ notification.message }}</span>
      <button @click="notification = null" class="toast-close">
        <i class="fas fa-times"></i>
      </button>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, onUnmounted, watch } from 'vue'
import bcmIncidentService from '@/services/bcmIncident'
import AssistantPanel from '@/components/assistant/AssistantPanel.vue'
import eventBus from '@/services/eventbus'

export default {
  name: 'BCMIncident',
  components: {
    AssistantPanel
  },
  setup() {
    // Reactive data
    const loading = ref(false)
    const error = ref('')
    const incidents = ref([])
    const stats = ref({})
    const responseTeams = ref([])

    // UI state
    const showCreateForm = ref(false)
    const showEditForm = ref(false)
    const showDetailPanel = ref(false)
    const showTimelineForm = ref(false)
    const submitting = ref(false)
    const notification = ref(null)

    // Selected incident
    const selectedIncident = ref(null)
    const incidentTimeline = ref([])

    // Form data
    const form = reactive({
      title: '',
      description: '',
      severity: 'medium',
      incident_type: 'operational',
      location: '',
      impact_level: 'medium',
      response_team_ids: [],
      affected_systems_text: '',
      use_ai_classification: true
    })

    // Filters and search
    const searchQuery = ref('')
    const filterSeverity = ref('')
    const filterStatus = ref('')
    const sortField = ref('created_date')
    const sortOrder = ref('desc')

    // Pagination
    const currentPage = ref(1)
    const itemsPerPage = 10

    // Computed properties
    const activeIncidents = computed(() => {
      return incidents.value.filter(incident => incident.status !== 'resolved')
    })

    const filteredIncidents = computed(() => {
      let filtered = incidents.value

      // Search filter
      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase()
        filtered = filtered.filter(incident =>
          incident.name.toLowerCase().includes(query) ||
          incident.description.toLowerCase().includes(query)
        )
      }

      // Severity filter
      if (filterSeverity.value) {
        filtered = filtered.filter(incident => incident.severity === filterSeverity.value)
      }

      // Status filter
      if (filterStatus.value) {
        filtered = filtered.filter(incident => incident.status === filterStatus.value)
      }

      // Sort
      filtered.sort((a, b) => {
        const aVal = a[sortField.value]
        const bVal = b[sortField.value]

        if (sortOrder.value === 'asc') {
          return aVal > bVal ? 1 : -1
        } else {
          return aVal < bVal ? 1 : -1
        }
      })

      return filtered
    })

    const paginatedIncidents = computed(() => {
      const start = (currentPage.value - 1) * itemsPerPage
      return filteredIncidents.value.slice(start, start + itemsPerPage)
    })

    const totalPages = computed(() => {
      return Math.ceil(filteredIncidents.value.length / itemsPerPage)
    })

    // Methods
    const loadIncidents = async () => {
      loading.value = true
      error.value = ''

      try {
        const [incidentsData, statsData, teamsData] = await Promise.all([
          bcmIncidentService.getIncidents(),
          bcmIncidentService.getIncidentStats(),
          bcmIncidentService.getResponseTeams()
        ])

        incidents.value = incidentsData
        stats.value = statsData
        responseTeams.value = teamsData
      } catch (err) {
        error.value = err.message
        showNotification('Failed to load incidents', 'error')
      } finally {
        loading.value = false
      }
    }

    const createIncident = async () => {
      submitting.value = true

      try {
        const incidentData = {
          ...form,
          affected_systems: form.affected_systems_text.split(',').map(s => s.trim()).filter(Boolean),
          reported_by: 1 // Current user ID - should come from auth service
        }

        await bcmIncidentService.createIncident(incidentData)

        showNotification('Incident created successfully', 'success')
        closeModal()
        resetForm()
        loadIncidents()

        // Open AI assistant for contextual help
        openAssistantWithContext('New incident created', 'incident_created')
      } catch (err) {
        showNotification(err.message, 'error')
      } finally {
        submitting.value = false
      }
    }

    const updateIncident = async () => {
      if (!selectedIncident.value) return

      submitting.value = true

      try {
        const updates = {
          name: form.title,
          description: form.description,
          severity: form.severity,
          incident_type: form.incident_type,
          location: form.location,
          impact_level: form.impact_level,
          response_team_ids: form.response_team_ids.length ? [[6, 0, form.response_team_ids]] : [[5]],
          affected_systems: form.affected_systems_text.split(',').map(s => s.trim()).filter(Boolean)
        }

        await bcmIncidentService.updateIncident(selectedIncident.value.id, updates)

        showNotification('Incident updated successfully', 'success')
        closeModal()
        loadIncidents()
      } catch (err) {
        showNotification(err.message, 'error')
      } finally {
        submitting.value = false
      }
    }

    const submitIncident = () => {
      if (showCreateForm.value) {
        createIncident()
      } else if (showEditForm.value) {
        updateIncident()
      }
    }

    const selectIncident = (incident) => {
      selectedIncident.value = incident
      showDetailPanel.value = true
      loadIncidentTimeline(incident.id)
    }

    const viewIncident = (incident) => {
      selectIncident(incident)
    }

    const editIncident = (incident) => {
      selectedIncident.value = incident

      // Populate form
      form.title = incident.name
      form.description = incident.description
      form.severity = incident.severity
      form.incident_type = incident.incident_type
      form.location = incident.location || ''
      form.impact_level = incident.impact_level
      form.response_team_ids = incident.response_team_ids || []
      form.affected_systems_text = (incident.affected_systems || []).join(', ')
      form.use_ai_classification = false

      showEditForm.value = true
    }

    const resolveIncident = async (incident) => {
      try {
        const resolution = {
          notes: prompt('Resolution notes:') || 'Incident resolved',
          lessons_learned: '',
          recovery_time: null
        }

        await bcmIncidentService.resolveIncident(incident.id, resolution)

        showNotification('Incident resolved successfully', 'success')
        loadIncidents()
        closeDetailPanel()
      } catch (err) {
        showNotification(err.message, 'error')
      }
    }

    const escalateIncident = async (incident) => {
      try {
        const newLevel = (incident.escalation_level || 0) + 1
        await bcmIncidentService.escalateIncident(incident.id, newLevel)

        showNotification('Incident escalated', 'warning')
        loadIncidents()
      } catch (err) {
        showNotification(err.message, 'error')
      }
    }

    const generateResponsePlan = async (incident) => {
      try {
        await bcmIncidentService.generateResponsePlan(incident.id)
        showNotification('Response plan generation initiated', 'info')

        // Open AI assistant to show the generated plan
        openAssistantWithContext('Generate response plan', 'response_plan_generated')
      } catch (err) {
        showNotification(err.message, 'error')
      }
    }

    const loadIncidentTimeline = async (incidentId) => {
      try {
        // This would be implemented in the service
        incidentTimeline.value = []
      } catch (err) {
        console.error('Failed to load incident timeline:', err)
      }
    }

    const exportIncidents = async () => {
      try {
        const filters = {
          severity: filterSeverity.value,
          status: filterStatus.value,
          search: searchQuery.value
        }

        const csvData = await bcmIncidentService.exportIncidents(filters)
        downloadCSV(csvData, 'incidents_export.csv')

        showNotification('Incidents exported successfully', 'success')
      } catch (err) {
        showNotification(err.message, 'error')
      }
    }

    const downloadCSV = (csvData, filename) => {
      const blob = new Blob([csvData], { type: 'text/csv' })
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = filename
      link.click()
      URL.revokeObjectURL(url)
    }

    const closeModal = () => {
      showCreateForm.value = false
      showEditForm.value = false
      resetForm()
    }

    const closeDetailPanel = () => {
      showDetailPanel.value = false
      selectedIncident.value = null
      incidentTimeline.value = []
    }

    const resetForm = () => {
      Object.assign(form, {
        title: '',
        description: '',
        severity: 'medium',
        incident_type: 'operational',
        location: '',
        impact_level: 'medium',
        response_team_ids: [],
        affected_systems_text: '',
        use_ai_classification: true
      })
    }

    const applyFilters = () => {
      currentPage.value = 1 // Reset to first page when filtering
    }

    const sortBy = (field) => {
      if (sortField.value === field) {
        sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
      } else {
        sortField.value = field
        sortOrder.value = 'asc'
      }
    }

    const debouncedSearch = debounce(() => {
      currentPage.value = 1 // Reset to first page when searching
    }, 300)

    const showNotification = (message, type = 'info') => {
      notification.value = { message, type }
      setTimeout(() => {
        notification.value = null
      }, 5000)
    }

    const openAssistantWithContext = (context, action) => {
      window.dispatchEvent(new CustomEvent('openAssistant', {
        detail: {
          context,
          action,
          message: `I can help you with ${context.toLowerCase()}. What would you like to know?`,
          autoOpen: true
        }
      }))
    }

    const getNotificationIcon = (type) => {
      const icons = {
        success: 'fas fa-check-circle',
        error: 'fas fa-exclamation-circle',
        warning: 'fas fa-exclamation-triangle',
        info: 'fas fa-info-circle'
      }
      return icons[type] || icons.info
    }

    // Utility functions
    const formatStatus = (status) => {
      const statusMap = {
        open: 'Open',
        in_progress: 'In Progress',
        escalated: 'Escalated',
        resolved: 'Resolved'
      }
      return statusMap[status] || status
    }

    const formatType = (type) => {
      const typeMap = {
        operational: 'Operational',
        security: 'Security',
        technology: 'Technology',
        environmental: 'Environmental',
        human_resources: 'HR',
        supply_chain: 'Supply Chain'
      }
      return typeMap[type] || type
    }

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    }

    const formatDateTime = (dateString) => {
      return new Date(dateString).toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    const truncateText = (text, maxLength) => {
      if (!text) return ''
      return text.length > maxLength ? text.substring(0, maxLength) + '...' : text
    }

    // Debounce utility
    function debounce(func, wait) {
      let timeout
      return function executedFunction(...args) {
        const later = () => {
          clearTimeout(timeout)
          func(...args)
        }
        clearTimeout(timeout)
        timeout = setTimeout(later, wait)
      }
    }

    // Event bus listeners
    const handleIncidentEvent = (eventData) => {
      // Handle real-time incident updates
      loadIncidents()
    }

    // Lifecycle
    onMounted(() => {
      loadIncidents()

      // Listen for incident events
      eventBus.on('bcm.incident.*', handleIncidentEvent)
      eventBus.on('bcm.incident.created', handleIncidentEvent)
      eventBus.on('bcm.incident.updated', handleIncidentEvent)
      eventBus.on('bcm.incident.resolved', handleIncidentEvent)
    })

    onUnmounted(() => {
      eventBus.off('bcm.incident.*', handleIncidentEvent)
      eventBus.off('bcm.incident.created', handleIncidentEvent)
      eventBus.off('bcm.incident.updated', handleIncidentEvent)
      eventBus.off('bcm.incident.resolved', handleIncidentEvent)
    })

    // Watch for page changes to update pagination
    watch([filterSeverity, filterStatus, searchQuery], () => {
      currentPage.value = 1
    })

    return {
      // Data
      loading,
      error,
      incidents,
      stats,
      responseTeams,

      // UI state
      showCreateForm,
      showEditForm,
      showDetailPanel,
      showTimelineForm,
      submitting,
      notification,

      // Selected data
      selectedIncident,
      incidentTimeline,

      // Form
      form,

      // Filters
      searchQuery,
      filterSeverity,
      filterStatus,
      sortField,
      sortOrder,

      // Pagination
      currentPage,
      itemsPerPage,

      // Computed
      activeIncidents,
      filteredIncidents,
      paginatedIncidents,
      totalPages,

      // Methods
      loadIncidents,
      submitIncident,
      selectIncident,
      viewIncident,
      editIncident,
      resolveIncident,
      escalateIncident,
      generateResponsePlan,
      exportIncidents,
      closeModal,
      closeDetailPanel,
      applyFilters,
      sortBy,
      debouncedSearch,
      showNotification,
      getNotificationIcon,
      formatStatus,
      formatType,
      formatDate,
      formatDateTime,
      truncateText
    }
  }
}
</script>

<style scoped>
.bcm-incident-management {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* Header Section */
.page-header {
  background: white;
  padding: 2rem;
  border-bottom: 1px solid #e2e8f0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.page-title {
  color: #1a1a1a;
  font-size: 2rem;
  font-weight: 700;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.page-title i {
  color: #ff6b35;
}

.page-subtitle {
  color: #64748b;
  margin: 0.5rem 0 0 0;
  font-size: 1rem;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  text-decoration: none;
}

.btn-primary {
  background: linear-gradient(135deg, #4a90e2, #ff6b35);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(74, 144, 226, 0.4);
}

.btn-outline {
  background: white;
  border: 1px solid #e2e8f0;
  color: #64748b;
}

.btn-outline:hover:not(:disabled) {
  background: #f8fafc;
  border-color: #cbd5e1;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

/* Quick Stats */
.quick-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
}

.stat-card.critical .stat-icon {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.stat-card.high .stat-icon {
  background: rgba(255, 107, 53, 0.1);
  color: #ff6b35;
}

.stat-card.medium .stat-icon {
  background: rgba(74, 144, 226, 0.1);
  color: #4a90e2;
}

.stat-card.success .stat-icon {
  background: rgba(34, 197, 94, 0.1);
  color: #22c55e;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: #1a1a1a;
  line-height: 1;
}

.stat-label {
  color: #64748b;
  font-size: 0.875rem;
  margin-top: 0.25rem;
}

/* Main Content */
.main-content {
  padding: 2rem;
}

.content-toolbar {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  gap: 2rem;
}

.search-section {
  flex: 1;
  max-width: 400px;
}

.search-input {
  position: relative;
  display: flex;
  align-items: center;
}

.search-input i {
  position: absolute;
  left: 1rem;
  color: #64748b;
}

.search-input input {
  width: 100%;
  padding: 0.75rem 1rem 0.75rem 2.5rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.875rem;
}

.search-input input:focus {
  outline: none;
  border-color: #4a90e2;
  box-shadow: 0 0 0 3px rgba(74, 144, 226, 0.1);
}

.filter-section {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.filter-select {
  padding: 0.75rem 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: white;
  color: #64748b;
  cursor: pointer;
}

.filter-select:focus {
  outline: none;
  border-color: #4a90e2;
}

/* Incidents Table */
.incidents-table-container {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.loading-state,
.error-state {
  padding: 4rem;
  text-align: center;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e2e8f0;
  border-top: 4px solid #4a90e2;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.error-icon {
  font-size: 3rem;
  color: #ef4444;
  margin-bottom: 1rem;
}

.incidents-table {
  width: 100%;
  border-collapse: collapse;
}

.incidents-table th {
  background: #f8fafc;
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: #374151;
  border-bottom: 1px solid #e2e8f0;
  position: sticky;
  top: 0;
}

.incidents-table th.sortable {
  cursor: pointer;
  user-select: none;
}

.incidents-table th.sortable:hover {
  background: #f1f5f9;
}

.incidents-table th i {
  margin-left: 0.5rem;
  opacity: 0.5;
}

.incident-row {
  border-bottom: 1px solid #f1f5f9;
  transition: background-color 0.2s;
  cursor: pointer;
}

.incident-row:hover {
  background: #f8fafc;
}

.incident-row.selected {
  background: rgba(74, 144, 226, 0.1);
  border-color: #4a90e2;
}

.incidents-table td {
  padding: 1rem;
  vertical-align: top;
}

.severity-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.severity-badge.critical {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.severity-badge.high {
  background: rgba(255, 107, 53, 0.1);
  color: #ff6b35;
}

.severity-badge.medium {
  background: rgba(249, 115, 22, 0.1);
  color: #f97316;
}

.severity-badge.low {
  background: rgba(34, 197, 94, 0.1);
  color: #22c55e;
}

.incident-info {
  min-width: 250px;
}

.incident-title {
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 0.25rem;
}

.incident-description {
  color: #64748b;
  font-size: 0.875rem;
  line-height: 1.4;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: capitalize;
}

.status-badge.open {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.status-badge.in_progress {
  background: rgba(249, 115, 22, 0.1);
  color: #f97316;
}

.status-badge.escalated {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.status-badge.resolved {
  background: rgba(34, 197, 94, 0.1);
  color: #22c55e;
}

.type-tag {
  background: #f1f5f9;
  padding: 0.25rem 0.75rem;
  border-radius: 6px;
  font-size: 0.75rem;
  color: #64748b;
}

.team-info {
  font-size: 0.875rem;
}

.team-count {
  color: #4a90e2;
  font-weight: 500;
}

.no-team {
  color: #94a3b8;
  font-style: italic;
  font-size: 0.875rem;
}

.date-cell {
  color: #64748b;
  font-size: 0.875rem;
  white-space: nowrap;
}

.actions-cell {
  width: 120px;
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
}

.btn-icon {
  width: 32px;
  height: 32px;
  border: none;
  background: #f1f5f9;
  color: #64748b;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.btn-icon:hover:not(:disabled) {
  background: #e2e8f0;
  color: #374151;
}

.btn-icon.danger:hover:not(:disabled) {
  background: #fee2e2;
  color: #ef4444;
}

/* Pagination */
.pagination-container {
  padding: 1.5rem;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  border-top: 1px solid #f1f5f9;
}

.page-info {
  color: #64748b;
  font-size: 0.875rem;
}

/* Modal */
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
  padding: 2rem;
}

.modal-container {
  background: white;
  border-radius: 12px;
  max-width: 800px;
  width: 100%;
  max-height: 90vh;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.modal-header {
  padding: 2rem;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: #1a1a1a;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.btn-close {
  width: 40px;
  height: 40px;
  border: none;
  background: #f1f5f9;
  color: #64748b;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.btn-close:hover {
  background: #e2e8f0;
  color: #374151;
}

.modal-body {
  padding: 2rem;
  overflow-y: auto;
  max-height: calc(90vh - 200px);
}

/* Form Styles */
.incident-form {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group.full-width {
  grid-column: 1 / -1;
}

.form-group label {
  font-weight: 600;
  color: #374151;
  font-size: 0.875rem;
}

.form-input,
.form-select,
.form-textarea {
  padding: 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
  outline: none;
  border-color: #4a90e2;
  box-shadow: 0 0 0 3px rgba(74, 144, 226, 0.1);
}

.form-textarea {
  resize: vertical;
  min-height: 100px;
}

.checkbox-group {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
  font-size: 0.875rem;
}

.checkbox-label input[type="checkbox"] {
  appearance: none;
  width: 18px;
  height: 18px;
  border: 2px solid #d1d5db;
  border-radius: 4px;
  position: relative;
}

.checkbox-label input[type="checkbox"]:checked {
  background: #4a90e2;
  border-color: #4a90e2;
}

.checkbox-label input[type="checkbox"]:checked::after {
  content: "✓";
  position: absolute;
  top: -2px;
  left: 2px;
  color: white;
  font-size: 12px;
  font-weight: bold;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #e2e8f0;
}

/* Detail Panel */
.detail-panel {
  position: fixed;
  right: 0;
  top: 0;
  width: 500px;
  height: 100vh;
  background: white;
  box-shadow: -4px 0 20px rgba(0, 0, 0, 0.15);
  z-index: 999;
  display: flex;
  flex-direction: column;
}

.detail-header {
  padding: 2rem;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.detail-header h3 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: #1a1a1a;
}

.detail-content {
  flex: 1;
  overflow-y: auto;
  padding: 2rem;
}

.detail-section {
  margin-bottom: 2rem;
}

.detail-section h4 {
  margin: 0 0 1rem 0;
  font-size: 1rem;
  font-weight: 600;
  color: #374151;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.info-item label {
  font-size: 0.75rem;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.ai-classification {
  background: #f8fafc;
  padding: 1rem;
  border-radius: 8px;
}

.classification-item {
  margin-bottom: 0.5rem;
}

.confidence-bar {
  width: 100%;
  height: 6px;
  background: #e2e8f0;
  border-radius: 3px;
  overflow: hidden;
  margin: 0.25rem 0;
}

.confidence-fill {
  height: 100%;
  background: linear-gradient(90deg, #4a90e2, #22c55e);
  transition: width 0.3s ease;
}

.timeline {
  position: relative;
}

.timeline-item {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
  position: relative;
}

.timeline-item::before {
  content: '';
  position: absolute;
  left: 8px;
  top: 20px;
  width: 1px;
  height: calc(100% + 1rem);
  background: #e2e8f0;
}

.timeline-item:last-child::before {
  display: none;
}

.timeline-marker {
  width: 16px;
  height: 16px;
  background: #4a90e2;
  border-radius: 50%;
  flex-shrink: 0;
  margin-top: 4px;
}

.timeline-content {
  flex: 1;
}

.timeline-time {
  font-size: 0.75rem;
  color: #64748b;
  margin-bottom: 0.25rem;
}

.timeline-description {
  color: #374151;
  line-height: 1.5;
}

.empty-timeline {
  text-align: center;
  color: #64748b;
  font-style: italic;
  padding: 2rem;
}

.timeline-actions {
  margin-top: 1rem;
}

.detail-actions {
  padding: 2rem;
  border-top: 1px solid #e2e8f0;
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.btn-success {
  background: #22c55e;
  color: white;
}

.btn-success:hover:not(:disabled) {
  background: #16a34a;
}

.btn-warning {
  background: #f59e0b;
  color: white;
}

.btn-warning:hover:not(:disabled) {
  background: #d97706;
}

/* Notification Toast */
.notification-toast {
  position: fixed;
  top: 2rem;
  right: 2rem;
  background: white;
  border-radius: 8px;
  padding: 1rem 1.5rem;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
  display: flex;
  align-items: center;
  gap: 1rem;
  z-index: 1100;
  min-width: 300px;
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.notification-toast.success {
  border-left: 4px solid #22c55e;
}

.notification-toast.error {
  border-left: 4px solid #ef4444;
}

.notification-toast.warning {
  border-left: 4px solid #f59e0b;
}

.notification-toast.info {
  border-left: 4px solid #4a90e2;
}

.toast-close {
  background: none;
  border: none;
  color: #64748b;
  cursor: pointer;
  padding: 0.25rem;
}

.toast-close:hover {
  color: #374151;
}

/* Responsive Design */
@media (max-width: 768px) {
  .page-header {
    padding: 1rem;
  }

  .header-content {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }

  .quick-stats {
    grid-template-columns: 1fr 1fr;
  }

  .main-content {
    padding: 1rem;
  }

  .content-toolbar {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }

  .filter-section {
    justify-content: space-between;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .detail-panel {
    width: 100vw;
  }

  .incidents-table {
    font-size: 0.875rem;
  }

  .incidents-table th,
  .incidents-table td {
    padding: 0.75rem 0.5rem;
  }

  .incident-info {
    min-width: 200px;
  }
}

@media (max-width: 480px) {
  .quick-stats {
    grid-template-columns: 1fr;
  }

  .stat-card {
    padding: 1rem;
  }

  .stat-value {
    font-size: 1.5rem;
  }

  .modal-overlay {
    padding: 1rem;
  }

  .modal-body {
    padding: 1rem;
  }

  .form-actions {
    flex-direction: column;
  }
}
</style>