<template>
  <div class="bcm-audit">
    <!-- Header -->
    <div class="page-header">
      <div class="header-content">
        <h1>BCM Audit Management</h1>
        <p>Internal & External Audits, Compliance Tracking, and Certification Management</p>
      </div>
      <div class="header-actions">
        <button @click="showCreateAudit = true" class="btn-primary">
          <i class="icon-plus"></i>
          New Audit
        </button>
        <button @click="generateComprehensiveReport" class="btn-secondary">
          <i class="icon-report"></i>
          Generate Report
        </button>
      </div>
    </div>

    <!-- Filters & Search -->
    <div class="filters-section">
      <div class="search-box">
        <input
          v-model="filters.search"
          type="text"
          placeholder="Search audits..."
          class="search-input"
        />
      </div>
      <div class="filter-controls">
        <select v-model="filters.audit_type" class="filter-select">
          <option value="">All Types</option>
          <option value="internal">Internal Audit</option>
          <option value="external">External Audit</option>
          <option value="certification">Certification Audit</option>
          <option value="surveillance">Surveillance Audit</option>
        </select>
        <select v-model="filters.status" class="filter-select">
          <option value="">All Status</option>
          <option value="planned">Planned</option>
          <option value="in_progress">In Progress</option>
          <option value="completed">Completed</option>
          <option value="cancelled">Cancelled</option>
        </select>
        <select v-model="filters.priority" class="filter-select">
          <option value="">All Priorities</option>
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
          <option value="critical">Critical</option>
        </select>
      </div>
    </div>

    <!-- Dashboard Cards -->
    <div class="dashboard-cards">
      <div class="metric-card">
        <div class="metric-icon">
          <i class="icon-audit"></i>
        </div>
        <div class="metric-content">
          <h3>{{ metrics.total_audits || 0 }}</h3>
          <p>Total Audits</p>
        </div>
      </div>
      <div class="metric-card">
        <div class="metric-icon">
          <i class="icon-progress"></i>
        </div>
        <div class="metric-content">
          <h3>{{ metrics.active_audits || 0 }}</h3>
          <p>Active Audits</p>
        </div>
      </div>
      <div class="metric-card">
        <div class="metric-icon">
          <i class="icon-finding"></i>
        </div>
        <div class="metric-content">
          <h3>{{ metrics.open_findings || 0 }}</h3>
          <p>Open Findings</p>
        </div>
      </div>
      <div class="metric-card">
        <div class="metric-icon">
          <i class="icon-certificate"></i>
        </div>
        <div class="metric-content">
          <h3>{{ metrics.active_certificates || 0 }}</h3>
          <p>Active Certificates</p>
        </div>
      </div>
    </div>

    <!-- Main Content Tabs -->
    <div class="content-tabs">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        @click="activeTab = tab.id"
        :class="['tab-button', { active: activeTab === tab.id }]"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- Audits List -->
    <div v-if="activeTab === 'audits'" class="audits-list">
      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>Audit Name</th>
              <th>Type</th>
              <th>Status</th>
              <th>Priority</th>
              <th>Progress</th>
              <th>Findings</th>
              <th>Due Date</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="audit in filteredAudits" :key="audit.id">
              <td>
                <div class="audit-info">
                  <strong>{{ audit.name }}</strong>
                  <span class="audit-scope">{{ audit.audit_scope }}</span>
                </div>
              </td>
              <td>
                <span :class="['badge', `badge-${audit.audit_type}`]">
                  {{ formatAuditType(audit.audit_type) }}
                </span>
              </td>
              <td>
                <span :class="['status-badge', `status-${audit.status}`]">
                  {{ formatStatus(audit.status) }}
                </span>
              </td>
              <td>
                <span :class="['priority-badge', `priority-${audit.priority}`]">
                  {{ formatPriority(audit.priority) }}
                </span>
              </td>
              <td>
                <div class="progress-bar">
                  <div
                    class="progress-fill"
                    :style="{ width: `${audit.completion_percentage || 0}%` }"
                  ></div>
                  <span class="progress-text">{{ audit.completion_percentage || 0 }}%</span>
                </div>
              </td>
              <td>
                <div class="findings-summary">
                  <span class="finding-count">{{ audit.findings_count || 0 }}</span>
                  <span class="nonconformity-count">{{ audit.nonconformities_count || 0 }} NC</span>
                </div>
              </td>
              <td>{{ formatDate(audit.end_date) }}</td>
              <td>
                <div class="action-buttons">
                  <button @click="viewAudit(audit)" class="btn-icon" title="View">
                    <i class="icon-view"></i>
                  </button>
                  <button @click="editAudit(audit)" class="btn-icon" title="Edit">
                    <i class="icon-edit"></i>
                  </button>
                  <button @click="generateAuditReport(audit.id)" class="btn-icon" title="Report">
                    <i class="icon-report"></i>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Findings Tab -->
    <div v-if="activeTab === 'findings'" class="findings-section">
      <div class="findings-grid">
        <div
          v-for="finding in findings"
          :key="finding.id"
          class="finding-card"
        >
          <div class="finding-header">
            <h4>{{ finding.name }}</h4>
            <span :class="['severity-badge', `severity-${finding.severity}`]">
              {{ formatSeverity(finding.severity) }}
            </span>
          </div>
          <div class="finding-content">
            <p>{{ finding.description }}</p>
            <div class="finding-meta">
              <span>Status: {{ formatStatus(finding.status) }}</span>
              <span>Due: {{ formatDate(finding.due_date) }}</span>
            </div>
          </div>
          <div class="finding-actions">
            <button @click="viewFinding(finding)" class="btn-sm">View Details</button>
            <button @click="updateFinding(finding)" class="btn-sm btn-primary">Update</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Certificates Tab -->
    <div v-if="activeTab === 'certificates'" class="certificates-section">
      <div class="certificates-grid">
        <div
          v-for="certificate in certificates"
          :key="certificate.id"
          class="certificate-card"
        >
          <div class="certificate-header">
            <h4>{{ certificate.name }}</h4>
            <span :class="['cert-status', getCertificateStatus(certificate)]">
              {{ getCertificateStatusText(certificate) }}
            </span>
          </div>
          <div class="certificate-content">
            <div class="cert-info">
              <span><strong>Standard:</strong> {{ certificate.standard }}</span>
              <span><strong>Body:</strong> {{ certificate.certification_body }}</span>
              <span><strong>Expires:</strong> {{ formatDate(certificate.expiry_date) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Assistant Panel -->
    <AssistantPanel
      v-if="showAssistant"
      @close="showAssistant = false"
      :context="assistantContext"
      module="audit"
    />

    <!-- Create Audit Modal -->
    <div v-if="showCreateAudit" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Create New Audit</h3>
          <button @click="closeModal" class="close-btn">&times;</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="createAudit">
            <div class="form-grid">
              <div class="form-group">
                <label>Audit Name</label>
                <input v-model="newAudit.name" type="text" required />
              </div>
              <div class="form-group">
                <label>Audit Type</label>
                <select v-model="newAudit.audit_type" required>
                  <option value="internal">Internal Audit</option>
                  <option value="external">External Audit</option>
                  <option value="certification">Certification Audit</option>
                  <option value="surveillance">Surveillance Audit</option>
                </select>
              </div>
              <div class="form-group">
                <label>Priority</label>
                <select v-model="newAudit.priority" required>
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="critical">Critical</option>
                </select>
              </div>
              <div class="form-group">
                <label>Audit Scope</label>
                <textarea v-model="newAudit.audit_scope" required></textarea>
              </div>
              <div class="form-group">
                <label>Start Date</label>
                <input v-model="newAudit.start_date" type="date" required />
              </div>
              <div class="form-group">
                <label>End Date</label>
                <input v-model="newAudit.end_date" type="date" required />
              </div>
            </div>
            <div class="modal-actions">
              <button type="button" @click="closeModal" class="btn-secondary">Cancel</button>
              <button type="submit" class="btn-primary">Create Audit</button>
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
import { bcmAuditService } from '../services/bcmAudit'
import AssistantPanel from '@/components/assistant/AssistantPanel.vue'

export default {
  name: 'BcmAudit',
  components: {
    AssistantPanel
  },
  setup() {
    // Reactive data
    const audits = ref([])
    const findings = ref([])
    const certificates = ref([])
    const metrics = ref({})
    const loading = ref(false)
    const showAssistant = ref(false)
    const showCreateAudit = ref(false)
    const activeTab = ref('audits')

    // Filters
    const filters = reactive({
      search: '',
      audit_type: '',
      status: '',
      priority: '',
      auditor_id: '',
      date_from: '',
      date_to: ''
    })

    // New audit form
    const newAudit = reactive({
      name: '',
      audit_type: 'internal',
      audit_scope: '',
      priority: 'medium',
      start_date: '',
      end_date: '',
      auditor_ids: [],
      audit_criteria: ''
    })

    // Tabs configuration
    const tabs = [
      { id: 'audits', label: 'Audits' },
      { id: 'findings', label: 'Findings' },
      { id: 'certificates', label: 'Certificates' },
      { id: 'analytics', label: 'Analytics' }
    ]

    // Computed properties
    const filteredAudits = computed(() => {
      return audits.value.filter(audit => {
        const matchesSearch = !filters.search ||
          audit.name.toLowerCase().includes(filters.search.toLowerCase())
        const matchesType = !filters.audit_type ||
          audit.audit_type === filters.audit_type
        const matchesStatus = !filters.status ||
          audit.status === filters.status
        const matchesPriority = !filters.priority ||
          audit.priority === filters.priority

        return matchesSearch && matchesType && matchesStatus && matchesPriority
      })
    })

    const assistantContext = computed(() => ({
      module: 'audit',
      currentAudits: audits.value.length,
      openFindings: findings.value.filter(f => f.status !== 'closed').length,
      filters: filters
    }))

    // Methods
    const loadData = async () => {
      loading.value = true
      try {
        const [auditsData, findingsData, certificatesData, metricsData] = await Promise.all([
          bcmAuditService.getAudits(filters),
          bcmAuditService.getAuditFindings(),
          bcmAuditService.getCertificates(),
          bcmAuditService.getAuditMetrics(filters)
        ])

        audits.value = auditsData || []
        findings.value = findingsData || []
        certificates.value = certificatesData || []
        metrics.value = metricsData || {}
      } catch (error) {
        console.error('Error loading audit data:', error)
      } finally {
        loading.value = false
      }
    }

    const createAudit = async () => {
      try {
        loading.value = true
        await bcmAuditService.createAudit(newAudit)
        await loadData()
        closeModal()
        resetNewAudit()
      } catch (error) {
        console.error('Error creating audit:', error)
      } finally {
        loading.value = false
      }
    }

    const viewAudit = (audit) => {
      // Implement audit detail view
      console.log('View audit:', audit)
    }

    const editAudit = (audit) => {
      // Implement audit editing
      console.log('Edit audit:', audit)
    }

    const generateAuditReport = async (auditId) => {
      try {
        loading.value = true
        const report = await bcmAuditService.generateAuditReport(auditId)
        // Handle report download/display
        console.log('Generated report:', report)
      } catch (error) {
        console.error('Error generating report:', error)
      } finally {
        loading.value = false
      }
    }

    const generateComprehensiveReport = async () => {
      try {
        loading.value = true
        // Generate comprehensive audit report
        await bcmAuditService.getAuditMetrics(filters)
      } catch (error) {
        console.error('Error generating comprehensive report:', error)
      } finally {
        loading.value = false
      }
    }

    const viewFinding = (finding) => {
      console.log('View finding:', finding)
    }

    const updateFinding = (finding) => {
      console.log('Update finding:', finding)
    }

    const closeModal = () => {
      showCreateAudit.value = false
    }

    const resetNewAudit = () => {
      Object.keys(newAudit).forEach(key => {
        newAudit[key] = typeof newAudit[key] === 'string' ? '' :
                       Array.isArray(newAudit[key]) ? [] :
                       key === 'audit_type' ? 'internal' :
                       key === 'priority' ? 'medium' : ''
      })
    }

    // Utility functions
    const formatDate = (date) => {
      return date ? new Date(date).toLocaleDateString() : ''
    }

    const formatAuditType = (type) => {
      const types = {
        internal: 'Internal',
        external: 'External',
        certification: 'Certification',
        surveillance: 'Surveillance'
      }
      return types[type] || type
    }

    const formatStatus = (status) => {
      const statuses = {
        planned: 'Planned',
        in_progress: 'In Progress',
        completed: 'Completed',
        cancelled: 'Cancelled',
        open: 'Open',
        closed: 'Closed'
      }
      return statuses[status] || status
    }

    const formatPriority = (priority) => {
      const priorities = {
        low: 'Low',
        medium: 'Medium',
        high: 'High',
        critical: 'Critical'
      }
      return priorities[priority] || priority
    }

    const formatSeverity = (severity) => {
      const severities = {
        minor: 'Minor',
        major: 'Major',
        critical: 'Critical'
      }
      return severities[severity] || severity
    }

    const getCertificateStatus = (certificate) => {
      const today = new Date()
      const expiryDate = new Date(certificate.expiry_date)
      const daysUntilExpiry = Math.ceil((expiryDate - today) / (1000 * 60 * 60 * 24))

      if (daysUntilExpiry < 0) return 'expired'
      if (daysUntilExpiry < 30) return 'expiring'
      return 'valid'
    }

    const getCertificateStatusText = (certificate) => {
      const status = getCertificateStatus(certificate)
      const statusTexts = {
        valid: 'Valid',
        expiring: 'Expiring Soon',
        expired: 'Expired'
      }
      return statusTexts[status] || 'Unknown'
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
      audits,
      findings,
      certificates,
      metrics,
      loading,
      showAssistant,
      showCreateAudit,
      activeTab,
      filters,
      newAudit,
      tabs,

      // Computed
      filteredAudits,
      assistantContext,

      // Methods
      loadData,
      createAudit,
      viewAudit,
      editAudit,
      generateAuditReport,
      generateComprehensiveReport,
      viewFinding,
      updateFinding,
      closeModal,
      resetNewAudit,
      formatDate,
      formatAuditType,
      formatStatus,
      formatPriority,
      formatSeverity,
      getCertificateStatus,
      getCertificateStatusText
    }
  }
}
</script>

<style scoped>
.bcm-audit {
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

.btn-primary, .btn-secondary {
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

.filters-section {
  display: flex;
  gap: 24px;
  margin-bottom: 24px;
  padding: 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.search-box {
  flex: 1;
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

.filter-controls {
  display: flex;
  gap: 12px;
}

.filter-select {
  padding: 12px 16px;
  border: 2px solid #e1e5e9;
  border-radius: 8px;
  background: white;
  font-size: 14px;
  min-width: 150px;
}

.dashboard-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.metric-card {
  display: flex;
  align-items: center;
  padding: 24px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: transform 0.2s;
}

.metric-card:hover {
  transform: translateY(-2px);
}

.metric-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  background: linear-gradient(135deg, #FF6B35, #4A90E2);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
}

.metric-icon i {
  font-size: 24px;
  color: white;
}

.metric-content h3 {
  margin: 0 0 4px 0;
  font-size: 32px;
  font-weight: 700;
  color: #1A1A1A;
}

.metric-content p {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.content-tabs {
  display: flex;
  gap: 4px;
  margin-bottom: 24px;
  background: white;
  padding: 8px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.tab-button {
  padding: 12px 24px;
  border: none;
  background: transparent;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  color: #666;
  transition: all 0.2s;
}

.tab-button.active {
  background: #FF6B35;
  color: white;
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

.audit-info strong {
  display: block;
  color: #1A1A1A;
  margin-bottom: 4px;
}

.audit-scope {
  color: #666;
  font-size: 14px;
}

.badge {
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  text-transform: uppercase;
}

.badge-internal { background: #e3f2fd; color: #1976d2; }
.badge-external { background: #f3e5f5; color: #7b1fa2; }
.badge-certification { background: #e8f5e8; color: #388e3c; }
.badge-surveillance { background: #fff3e0; color: #f57c00; }

.status-badge {
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
}

.status-planned { background: #e3f2fd; color: #1976d2; }
.status-in_progress { background: #fff3e0; color: #f57c00; }
.status-completed { background: #e8f5e8; color: #388e3c; }
.status-cancelled { background: #ffebee; color: #d32f2f; }

.priority-badge {
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
}

.priority-low { background: #e8f5e8; color: #388e3c; }
.priority-medium { background: #fff3e0; color: #f57c00; }
.priority-high { background: #ffebee; color: #d32f2f; }
.priority-critical { background: #1A1A1A; color: white; }

.progress-bar {
  position: relative;
  width: 100px;
  height: 20px;
  background: #e1e5e9;
  border-radius: 10px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #FF6B35, #4A90E2);
  border-radius: 10px;
  transition: width 0.3s;
}

.progress-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 11px;
  font-weight: 500;
  color: #1A1A1A;
}

.findings-summary {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.finding-count, .nonconformity-count {
  font-size: 12px;
  padding: 2px 6px;
  border-radius: 4px;
}

.finding-count {
  background: #e3f2fd;
  color: #1976d2;
}

.nonconformity-count {
  background: #ffebee;
  color: #d32f2f;
}

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

.findings-grid, .certificates-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 24px;
}

.finding-card, .certificate-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  overflow: hidden;
  transition: transform 0.2s;
}

.finding-card:hover, .certificate-card:hover {
  transform: translateY(-2px);
}

.finding-header, .certificate-header {
  padding: 20px;
  border-bottom: 1px solid #e1e5e9;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.finding-header h4, .certificate-header h4 {
  margin: 0;
  color: #1A1A1A;
  font-weight: 600;
}

.severity-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
  text-transform: uppercase;
}

.severity-minor { background: #e8f5e8; color: #388e3c; }
.severity-major { background: #fff3e0; color: #f57c00; }
.severity-critical { background: #ffebee; color: #d32f2f; }

.finding-content, .certificate-content {
  padding: 20px;
}

.finding-meta {
  display: flex;
  gap: 16px;
  margin-top: 12px;
  font-size: 14px;
  color: #666;
}

.cert-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.cert-info span {
  font-size: 14px;
  color: #666;
}

.cert-status {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
  text-transform: uppercase;
}

.cert-status.valid { background: #e8f5e8; color: #388e3c; }
.cert-status.expiring { background: #fff3e0; color: #f57c00; }
.cert-status.expired { background: #ffebee; color: #d32f2f; }

.finding-actions {
  padding: 20px;
  border-top: 1px solid #e1e5e9;
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
  max-width: 600px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
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

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
}

.modal-body {
  padding: 24px;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-weight: 500;
  color: #1A1A1A;
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

.form-group textarea {
  resize: vertical;
  min-height: 100px;
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
  .bcm-audit {
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

  .filters-section {
    flex-direction: column;
  }

  .filter-controls {
    flex-wrap: wrap;
  }

  .dashboard-cards {
    grid-template-columns: 1fr;
  }

  .findings-grid, .certificates-grid {
    grid-template-columns: 1fr;
  }
}
</style>