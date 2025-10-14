<template>
  <div class="bcm-reporting">
    <!-- Header -->
    <div class="page-header">
      <div class="header-content">
        <h1>Comprehensive Reporting</h1>
        <p>Generate, schedule, and manage comprehensive BCM reports with AI insights</p>
      </div>
      <div class="header-actions">
        <button @click="showCreateReport = true" class="btn-primary">
          <i class="icon-plus"></i>
          New Report
        </button>
        <button @click="showAssistant = true" class="btn-secondary">
          <i class="icon-ai"></i>
          AI Insights
        </button>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="quick-actions">
      <div class="quick-action-card" @click="generateExecutiveSummary">
        <div class="action-icon">
          <i class="icon-executive"></i>
        </div>
        <div class="action-content">
          <h4>Executive Summary</h4>
          <p>Generate comprehensive executive dashboard</p>
        </div>
      </div>
      <div class="quick-action-card" @click="generateComplianceReport">
        <div class="action-icon">
          <i class="icon-compliance"></i>
        </div>
        <div class="action-content">
          <h4>Compliance Report</h4>
          <p>ISO 22301 compliance status</p>
        </div>
      </div>
      <div class="quick-action-card" @click="generateRiskReport">
        <div class="action-icon">
          <i class="icon-risk"></i>
        </div>
        <div class="action-content">
          <h4>Risk Assessment</h4>
          <p>Current risk landscape overview</p>
        </div>
      </div>
      <div class="quick-action-card" @click="generateIncidentReport">
        <div class="action-icon">
          <i class="icon-incident"></i>
        </div>
        <div class="action-content">
          <h4>Incident Analysis</h4>
          <p>Recent incidents and trends</p>
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
            placeholder="Search reports..."
            class="search-input"
          />
        </div>
        <select v-model="filters.report_type" class="filter-select">
          <option value="">All Types</option>
          <option value="dashboard">Dashboard</option>
          <option value="compliance">Compliance</option>
          <option value="risk">Risk Assessment</option>
          <option value="incident">Incident Analysis</option>
          <option value="audit">Audit Reports</option>
          <option value="bia">BIA Reports</option>
          <option value="kpi">KPI Reports</option>
          <option value="custom">Custom</option>
        </select>
        <select v-model="filters.category" class="filter-select">
          <option value="">All Categories</option>
          <option value="operational">Operational</option>
          <option value="strategic">Strategic</option>
          <option value="regulatory">Regulatory</option>
          <option value="financial">Financial</option>
        </select>
        <select v-model="filters.status" class="filter-select">
          <option value="">All Status</option>
          <option value="draft">Draft</option>
          <option value="completed">Completed</option>
          <option value="scheduled">Scheduled</option>
          <option value="failed">Failed</option>
        </select>
      </div>
      <div class="action-group">
        <button @click="viewMode = 'grid'" :class="['view-btn', { active: viewMode === 'grid' }]">
          <i class="icon-grid"></i>
        </button>
        <button @click="viewMode = 'list'" :class="['view-btn', { active: viewMode === 'list' }]">
          <i class="icon-list"></i>
        </button>
        <button @click="exportBulk" class="btn-outline">
          <i class="icon-download"></i>
          Export
        </button>
        <button @click="refreshReports" class="btn-outline">
          <i class="icon-refresh"></i>
          Refresh
        </button>
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
        <i :class="tab.icon"></i>
        {{ tab.label }}
      </button>
    </div>

    <!-- Reports Grid View -->
    <div v-if="activeTab === 'reports' && viewMode === 'grid'" class="reports-grid">
      <div
        v-for="report in filteredReports"
        :key="report.id"
        class="report-card"
        @click="viewReport(report)"
      >
        <div class="report-header">
          <div class="report-icon">
            <i :class="getReportIcon(report.report_type)"></i>
          </div>
          <div class="report-status">
            <span :class="['status-indicator', report.status]"></span>
          </div>
        </div>

        <div class="report-content">
          <h4>{{ report.name }}</h4>
          <p class="report-type">{{ formatReportType(report.report_type) }}</p>
          <p class="report-category">{{ formatCategory(report.category) }}</p>
        </div>

        <div class="report-meta">
          <div class="meta-item">
            <i class="icon-calendar"></i>
            <span>{{ formatDate(report.generated_date) }}</span>
          </div>
          <div class="meta-item">
            <i class="icon-file"></i>
            <span>{{ formatFileSize(report.file_size) }}</span>
          </div>
          <div class="meta-item">
            <i class="icon-download"></i>
            <span>{{ report.download_count || 0 }} downloads</span>
          </div>
        </div>

        <div class="report-actions">
          <button @click.stop="downloadReport(report)" class="btn-sm">
            <i class="icon-download"></i>
            Download
          </button>
          <button @click.stop="shareReport(report)" class="btn-sm">
            <i class="icon-share"></i>
            Share
          </button>
          <button @click.stop="editReport(report)" class="btn-sm btn-primary">
            <i class="icon-edit"></i>
            Edit
          </button>
        </div>
      </div>
    </div>

    <!-- Reports List View -->
    <div v-if="activeTab === 'reports' && viewMode === 'list'" class="reports-list">
      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>Report Name</th>
              <th>Type</th>
              <th>Category</th>
              <th>Status</th>
              <th>Generated</th>
              <th>Size</th>
              <th>Downloads</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="report in filteredReports" :key="report.id">
              <td>
                <div class="report-name-cell">
                  <i :class="getReportIcon(report.report_type)"></i>
                  <div>
                    <strong>{{ report.name }}</strong>
                    <span class="report-desc">{{ report.description }}</span>
                  </div>
                </div>
              </td>
              <td>
                <span class="report-type-badge">{{ formatReportType(report.report_type) }}</span>
              </td>
              <td>{{ formatCategory(report.category) }}</td>
              <td>
                <span :class="['status-badge', report.status]">
                  {{ formatStatus(report.status) }}
                </span>
              </td>
              <td>{{ formatDate(report.generated_date) }}</td>
              <td>{{ formatFileSize(report.file_size) }}</td>
              <td>{{ report.download_count || 0 }}</td>
              <td>
                <div class="action-buttons">
                  <button @click="viewReport(report)" class="btn-icon" title="View">
                    <i class="icon-view"></i>
                  </button>
                  <button @click="downloadReport(report)" class="btn-icon" title="Download">
                    <i class="icon-download"></i>
                  </button>
                  <button @click="shareReport(report)" class="btn-icon" title="Share">
                    <i class="icon-share"></i>
                  </button>
                  <button @click="editReport(report)" class="btn-icon" title="Edit">
                    <i class="icon-edit"></i>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Scheduled Reports Tab -->
    <div v-if="activeTab === 'scheduled'" class="scheduled-reports">
      <div class="scheduled-header">
        <h3>Scheduled Reports</h3>
        <button @click="showScheduleModal = true" class="btn-primary">
          <i class="icon-clock"></i>
          Schedule Report
        </button>
      </div>

      <div class="scheduled-list">
        <div
          v-for="scheduled in scheduledReports"
          :key="scheduled.id"
          class="scheduled-card"
        >
          <div class="scheduled-info">
            <h4>{{ scheduled.name }}</h4>
            <p>{{ formatReportType(scheduled.report_type) }} • {{ scheduled.frequency }}</p>
            <p class="next-run">Next run: {{ formatDate(scheduled.next_run) }}</p>
          </div>
          <div class="scheduled-actions">
            <button @click="runNow(scheduled)" class="btn-sm">Run Now</button>
            <button @click="editSchedule(scheduled)" class="btn-sm">Edit</button>
            <button @click="unschedule(scheduled)" class="btn-sm btn-danger">Remove</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Templates Tab -->
    <div v-if="activeTab === 'templates'" class="templates-section">
      <div class="templates-grid">
        <div
          v-for="template in reportTemplates"
          :key="template.id"
          class="template-card"
          @click="createFromTemplate(template)"
        >
          <div class="template-preview">
            <img v-if="template.preview_image" :src="template.preview_image" :alt="template.name" />
            <div v-else class="preview-placeholder">
              <i :class="getReportIcon(template.report_type)"></i>
            </div>
          </div>
          <div class="template-content">
            <h4>{{ template.name }}</h4>
            <p>{{ template.description }}</p>
            <span class="template-category">{{ formatCategory(template.category) }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Analytics Tab -->
    <div v-if="activeTab === 'analytics'" class="analytics-section">
      <div class="analytics-grid">
        <div class="chart-container">
          <h3>Report Generation Trends</h3>
          <canvas ref="trendsChart"></canvas>
        </div>
        <div class="chart-container">
          <h3>Popular Report Types</h3>
          <canvas ref="typesChart"></canvas>
        </div>
        <div class="chart-container">
          <h3>Download Statistics</h3>
          <canvas ref="downloadsChart"></canvas>
        </div>
        <div class="chart-container">
          <h3>Usage by Category</h3>
          <canvas ref="categoryChart"></canvas>
        </div>
      </div>
    </div>

    <!-- Assistant Panel -->
    <AssistantPanel
      v-if="showAssistant"
      @close="showAssistant = false"
      :context="assistantContext"
      module="reporting"
    />

    <!-- Create Report Modal -->
    <div v-if="showCreateReport" class="modal-overlay" @click="closeCreateModal">
      <div class="modal-content large" @click.stop>
        <div class="modal-header">
          <h3>Create New Report</h3>
          <button @click="closeCreateModal" class="close-btn">&times;</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="createReport">
            <div class="form-steps">
              <div class="step" :class="{ active: currentStep === 1 }">
                <div class="step-number">1</div>
                <span>Basic Info</span>
              </div>
              <div class="step" :class="{ active: currentStep === 2 }">
                <div class="step-number">2</div>
                <span>Configuration</span>
              </div>
              <div class="step" :class="{ active: currentStep === 3 }">
                <div class="step-number">3</div>
                <span>Schedule</span>
              </div>
            </div>

            <!-- Step 1: Basic Info -->
            <div v-if="currentStep === 1" class="form-step">
              <div class="form-grid">
                <div class="form-group">
                  <label>Report Name</label>
                  <input v-model="newReport.name" type="text" required />
                </div>
                <div class="form-group">
                  <label>Report Type</label>
                  <select v-model="newReport.report_type" required>
                    <option value="dashboard">Dashboard</option>
                    <option value="compliance">Compliance</option>
                    <option value="risk">Risk Assessment</option>
                    <option value="incident">Incident Analysis</option>
                    <option value="audit">Audit Reports</option>
                    <option value="bia">BIA Reports</option>
                    <option value="kpi">KPI Reports</option>
                    <option value="custom">Custom</option>
                  </select>
                </div>
                <div class="form-group">
                  <label>Category</label>
                  <select v-model="newReport.category" required>
                    <option value="operational">Operational</option>
                    <option value="strategic">Strategic</option>
                    <option value="regulatory">Regulatory</option>
                    <option value="financial">Financial</option>
                  </select>
                </div>
                <div class="form-group">
                  <label>Format</label>
                  <select v-model="newReport.format" required>
                    <option value="pdf">PDF</option>
                    <option value="excel">Excel</option>
                    <option value="word">Word</option>
                    <option value="powerpoint">PowerPoint</option>
                  </select>
                </div>
                <div class="form-group full-width">
                  <label>Description</label>
                  <textarea v-model="newReport.description" rows="3"></textarea>
                </div>
              </div>
            </div>

            <!-- Step 2: Configuration -->
            <div v-if="currentStep === 2" class="form-step">
              <div class="config-section">
                <h4>Data Sources</h4>
                <div class="checkbox-group">
                  <label class="checkbox-label">
                    <input type="checkbox" v-model="newReport.dataSources" value="incidents" />
                    Incidents
                  </label>
                  <label class="checkbox-label">
                    <input type="checkbox" v-model="newReport.dataSources" value="risks" />
                    Risks
                  </label>
                  <label class="checkbox-label">
                    <input type="checkbox" v-model="newReport.dataSources" value="audits" />
                    Audits
                  </label>
                  <label class="checkbox-label">
                    <input type="checkbox" v-model="newReport.dataSources" value="kpis" />
                    KPIs
                  </label>
                  <label class="checkbox-label">
                    <input type="checkbox" v-model="newReport.dataSources" value="bia" />
                    BIA
                  </label>
                </div>
              </div>

              <div class="config-section">
                <h4>Time Range</h4>
                <div class="form-grid">
                  <div class="form-group">
                    <label>From Date</label>
                    <input v-model="newReport.dateFrom" type="date" />
                  </div>
                  <div class="form-group">
                    <label>To Date</label>
                    <input v-model="newReport.dateTo" type="date" />
                  </div>
                </div>
              </div>

              <div class="config-section">
                <h4>Options</h4>
                <div class="checkbox-group">
                  <label class="checkbox-label">
                    <input type="checkbox" v-model="newReport.includeCharts" />
                    Include Charts & Visualizations
                  </label>
                  <label class="checkbox-label">
                    <input type="checkbox" v-model="newReport.includeAiInsights" />
                    Include AI Insights
                  </label>
                  <label class="checkbox-label">
                    <input type="checkbox" v-model="newReport.includeTrends" />
                    Include Trend Analysis
                  </label>
                </div>
              </div>
            </div>

            <!-- Step 3: Schedule -->
            <div v-if="currentStep === 3" class="form-step">
              <div class="schedule-options">
                <label class="radio-label">
                  <input type="radio" v-model="newReport.scheduleType" value="once" />
                  Generate Once
                </label>
                <label class="radio-label">
                  <input type="radio" v-model="newReport.scheduleType" value="recurring" />
                  Recurring Schedule
                </label>
              </div>

              <div v-if="newReport.scheduleType === 'recurring'" class="recurring-config">
                <div class="form-grid">
                  <div class="form-group">
                    <label>Frequency</label>
                    <select v-model="newReport.frequency">
                      <option value="daily">Daily</option>
                      <option value="weekly">Weekly</option>
                      <option value="monthly">Monthly</option>
                      <option value="quarterly">Quarterly</option>
                    </select>
                  </div>
                  <div class="form-group">
                    <label>Start Date</label>
                    <input v-model="newReport.startDate" type="date" />
                  </div>
                </div>

                <div class="form-group">
                  <label>Recipients</label>
                  <textarea v-model="newReport.recipients" placeholder="Enter email addresses, separated by commas"></textarea>
                </div>
              </div>
            </div>

            <div class="modal-actions">
              <button type="button" @click="closeCreateModal" class="btn-secondary">Cancel</button>
              <button
                v-if="currentStep > 1"
                type="button"
                @click="currentStep--"
                class="btn-outline"
              >
                Previous
              </button>
              <button
                v-if="currentStep < 3"
                type="button"
                @click="currentStep++"
                class="btn-primary"
              >
                Next
              </button>
              <button
                v-if="currentStep === 3"
                type="submit"
                class="btn-primary"
              >
                Create Report
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Loading Overlay -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading-content">
        <div class="loading-spinner"></div>
        <p>{{ loadingMessage }}</p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { bcmReportingService } from '../../services/bcmReporting.js'
import AssistantPanel from '@/components/assistant/AssistantPanel.vue'

export default {
  name: 'BcmReporting',
  components: {
    AssistantPanel
  },
  setup() {
    // Reactive data
    const reports = ref([])
    const scheduledReports = ref([])
    const reportTemplates = ref([])
    const loading = ref(false)
    const loadingMessage = ref('')
    const showAssistant = ref(false)
    const showCreateReport = ref(false)
    const showScheduleModal = ref(false)
    const activeTab = ref('reports')
    const viewMode = ref('grid')
    const currentStep = ref(1)

    // Filters
    const filters = reactive({
      search: '',
      report_type: '',
      category: '',
      status: '',
      scheduled: undefined
    })

    // Form data
    const newReport = reactive({
      name: '',
      description: '',
      report_type: 'dashboard',
      category: 'operational',
      format: 'pdf',
      dataSources: [],
      dateFrom: '',
      dateTo: '',
      includeCharts: true,
      includeAiInsights: true,
      includeTrends: true,
      scheduleType: 'once',
      frequency: 'monthly',
      startDate: '',
      recipients: ''
    })

    // Tabs configuration
    const tabs = [
      { id: 'reports', label: 'Reports', icon: 'icon-file' },
      { id: 'scheduled', label: 'Scheduled', icon: 'icon-clock' },
      { id: 'templates', label: 'Templates', icon: 'icon-template' },
      { id: 'analytics', label: 'Analytics', icon: 'icon-chart' }
    ]

    // Computed properties
    const filteredReports = computed(() => {
      return reports.value.filter(report => {
        const matchesSearch = !filters.search ||
          report.name.toLowerCase().includes(filters.search.toLowerCase())
        const matchesType = !filters.report_type ||
          report.report_type === filters.report_type
        const matchesCategory = !filters.category ||
          report.category === filters.category
        const matchesStatus = !filters.status ||
          report.status === filters.status

        return matchesSearch && matchesType && matchesCategory && matchesStatus
      })
    })

    const assistantContext = computed(() => ({
      module: 'reporting',
      totalReports: reports.value.length,
      scheduledReports: scheduledReports.value.length,
      recentReports: reports.value.filter(r => {
        const oneWeekAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)
        return new Date(r.generated_date) > oneWeekAgo
      }).length,
      filters: filters
    }))

    // Methods
    const loadData = async () => {
      loading.value = true
      loadingMessage.value = 'Loading reports...'

      try {
        const [reportsData, scheduledData, templatesData] = await Promise.all([
          bcmReportingService.getReports(filters),
          bcmReportingService.getScheduledReports(),
          bcmReportingService.getReportTemplates()
        ])

        reports.value = reportsData || []
        scheduledReports.value = scheduledData || []
        reportTemplates.value = templatesData || []
      } catch (error) {
        console.error('Error loading reporting data:', error)
      } finally {
        loading.value = false
      }
    }

    const createReport = async () => {
      try {
        loading.value = true
        loadingMessage.value = 'Creating report...'

        const reportData = {
          name: newReport.name,
          description: newReport.description,
          report_type: newReport.report_type,
          category: newReport.category,
          format: newReport.format,
          data_sources: newReport.dataSources,
          parameters: {
            date_from: newReport.dateFrom,
            date_to: newReport.dateTo,
            include_charts: newReport.includeCharts,
            include_ai_insights: newReport.includeAiInsights,
            include_trends: newReport.includeTrends
          },
          scheduled: newReport.scheduleType === 'recurring',
          frequency: newReport.frequency,
          recipients: newReport.recipients ? newReport.recipients.split(',').map(email => email.trim()) : []
        }

        await bcmReportingService.createReport(reportData)
        await loadData()
        closeCreateModal()
        resetNewReport()
      } catch (error) {
        console.error('Error creating report:', error)
      } finally {
        loading.value = false
      }
    }

    const generateExecutiveSummary = async () => {
      try {
        loading.value = true
        loadingMessage.value = 'Generating executive summary...'
        await bcmReportingService.getExecutiveSummary()
      } catch (error) {
        console.error('Error generating executive summary:', error)
      } finally {
        loading.value = false
      }
    }

    const generateComplianceReport = async () => {
      try {
        loading.value = true
        loadingMessage.value = 'Generating compliance report...'
        await bcmReportingService.getComplianceReport()
      } catch (error) {
        console.error('Error generating compliance report:', error)
      } finally {
        loading.value = false
      }
    }

    const generateRiskReport = async () => {
      try {
        loading.value = true
        loadingMessage.value = 'Generating risk report...'
        await bcmReportingService.getRiskReport()
      } catch (error) {
        console.error('Error generating risk report:', error)
      } finally {
        loading.value = false
      }
    }

    const generateIncidentReport = async () => {
      try {
        loading.value = true
        loadingMessage.value = 'Generating incident report...'
        await bcmReportingService.getIncidentReport()
      } catch (error) {
        console.error('Error generating incident report:', error)
      } finally {
        loading.value = false
      }
    }

    const viewReport = (report) => {
      console.log('View report:', report)
      // Navigate to report detail view
    }

    const downloadReport = async (report) => {
      try {
        loading.value = true
        loadingMessage.value = 'Preparing download...'
        // Implement download logic
        console.log('Download report:', report)
      } catch (error) {
        console.error('Error downloading report:', error)
      } finally {
        loading.value = false
      }
    }

    const shareReport = (report) => {
      console.log('Share report:', report)
      // Open share modal
    }

    const editReport = (report) => {
      console.log('Edit report:', report)
      // Open edit modal
    }

    const exportBulk = async () => {
      try {
        loading.value = true
        loadingMessage.value = 'Exporting reports...'
        await bcmReportingService.bulkExport(filteredReports.value.map(r => r.id))
      } catch (error) {
        console.error('Error bulk exporting:', error)
      } finally {
        loading.value = false
      }
    }

    const refreshReports = () => {
      loadData()
    }

    const createFromTemplate = (template) => {
      console.log('Create from template:', template)
      // Implement template creation
    }

    const runNow = async (scheduled) => {
      try {
        loading.value = true
        loadingMessage.value = 'Running scheduled report...'
        await bcmReportingService.generateReport(scheduled.id)
        await loadData()
      } catch (error) {
        console.error('Error running scheduled report:', error)
      } finally {
        loading.value = false
      }
    }

    const editSchedule = (scheduled) => {
      console.log('Edit schedule:', scheduled)
    }

    const unschedule = async (scheduled) => {
      try {
        await bcmReportingService.unscheduleReport(scheduled.id)
        await loadData()
      } catch (error) {
        console.error('Error unscheduling report:', error)
      }
    }

    const closeCreateModal = () => {
      showCreateReport.value = false
      currentStep.value = 1
    }

    const resetNewReport = () => {
      Object.keys(newReport).forEach(key => {
        if (typeof newReport[key] === 'string') {
          newReport[key] = key === 'report_type' ? 'dashboard' :
                            key === 'category' ? 'operational' :
                            key === 'format' ? 'pdf' :
                            key === 'scheduleType' ? 'once' :
                            key === 'frequency' ? 'monthly' : ''
        } else if (Array.isArray(newReport[key])) {
          newReport[key] = []
        } else if (typeof newReport[key] === 'boolean') {
          newReport[key] = key === 'includeCharts' ||
                            key === 'includeAiInsights' ||
                            key === 'includeTrends'
        }
      })
    }

    // Utility functions
    const formatDate = (date) => {
      return date ? new Date(date).toLocaleDateString() : ''
    }

    const formatReportType = (type) => {
      const types = {
        dashboard: 'Dashboard',
        compliance: 'Compliance',
        risk: 'Risk Assessment',
        incident: 'Incident Analysis',
        audit: 'Audit Reports',
        bia: 'BIA Reports',
        kpi: 'KPI Reports',
        custom: 'Custom'
      }
      return types[type] || type
    }

    const formatCategory = (category) => {
      const categories = {
        operational: 'Operational',
        strategic: 'Strategic',
        regulatory: 'Regulatory',
        financial: 'Financial'
      }
      return categories[category] || category
    }

    const formatStatus = (status) => {
      const statuses = {
        draft: 'Draft',
        generating: 'Generating',
        completed: 'Completed',
        failed: 'Failed',
        scheduled: 'Scheduled'
      }
      return statuses[status] || status
    }

    const formatFileSize = (bytes) => {
      return bcmReportingService.formatReportSize(bytes)
    }

    const getReportIcon = (type) => {
      return bcmReportingService.getReportTypeIcon(type)
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
      reports,
      scheduledReports,
      reportTemplates,
      loading,
      loadingMessage,
      showAssistant,
      showCreateReport,
      showScheduleModal,
      activeTab,
      viewMode,
      currentStep,
      filters,
      newReport,
      tabs,

      // Computed
      filteredReports,
      assistantContext,

      // Methods
      loadData,
      createReport,
      generateExecutiveSummary,
      generateComplianceReport,
      generateRiskReport,
      generateIncidentReport,
      viewReport,
      downloadReport,
      shareReport,
      editReport,
      exportBulk,
      refreshReports,
      createFromTemplate,
      runNow,
      editSchedule,
      unschedule,
      closeCreateModal,
      resetNewReport,
      formatDate,
      formatReportType,
      formatCategory,
      formatStatus,
      formatFileSize,
      getReportIcon
    }
  }
}
</script>

<style scoped>
.bcm-reporting {
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

.quick-actions {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.quick-action-card {
  display: flex;
  align-items: center;
  padding: 24px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  cursor: pointer;
  transition: all 0.2s;
}

.quick-action-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.action-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  background: linear-gradient(135deg, #FF6B35, #4A90E2);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
}

.action-icon i {
  font-size: 24px;
  color: white;
}

.action-content h4 {
  margin: 0 0 4px 0;
  color: #1A1A1A;
  font-weight: 600;
}

.action-content p {
  margin: 0;
  color: #666;
  font-size: 14px;
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
  align-items: center;
}

.view-btn {
  width: 40px;
  height: 40px;
  border: 2px solid #e1e5e9;
  background: white;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.view-btn.active {
  border-color: #4A90E2;
  background: #4A90E2;
  color: white;
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
  display: flex;
  align-items: center;
  gap: 8px;
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

.reports-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 24px;
}

.report-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  overflow: hidden;
  cursor: pointer;
  transition: all 0.2s;
}

.report-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #e1e5e9;
}

.report-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: linear-gradient(135deg, #FF6B35, #4A90E2);
  display: flex;
  align-items: center;
  justify-content: center;
}

.report-icon i {
  font-size: 20px;
  color: white;
}

.status-indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.status-indicator.completed { background: #4caf50; }
.status-indicator.draft { background: #666; }
.status-indicator.generating { background: #ff9800; }
.status-indicator.failed { background: #f44336; }
.status-indicator.scheduled { background: #2196f3; }

.report-content {
  padding: 20px;
}

.report-content h4 {
  margin: 0 0 8px 0;
  color: #1A1A1A;
  font-weight: 600;
  font-size: 18px;
}

.report-type {
  margin: 0 0 4px 0;
  color: #4A90E2;
  font-size: 14px;
  font-weight: 500;
}

.report-category {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.report-meta {
  padding: 20px;
  border-top: 1px solid #e1e5e9;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #666;
  font-size: 14px;
}

.meta-item i {
  width: 16px;
  color: #4A90E2;
}

.report-actions {
  padding: 20px;
  border-top: 1px solid #e1e5e9;
  display: flex;
  gap: 12px;
}

.btn-sm {
  display: flex;
  align-items: center;
  gap: 6px;
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

.btn-sm.btn-danger {
  background: #f44336;
  border-color: #f44336;
  color: white;
}

.btn-sm.btn-danger:hover {
  background: #d32f2f;
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

.report-name-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.report-name-cell i {
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, #FF6B35, #4A90E2);
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 14px;
}

.report-name-cell strong {
  display: block;
  color: #1A1A1A;
  margin-bottom: 4px;
}

.report-desc {
  color: #666;
  font-size: 14px;
}

.report-type-badge {
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  background: #e3f2fd;
  color: #1976d2;
}

.status-badge {
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.completed { background: #e8f5e8; color: #4caf50; }
.status-badge.draft { background: #f5f5f5; color: #666; }
.status-badge.generating { background: #fff3e0; color: #ff9800; }
.status-badge.failed { background: #ffebee; color: #f44336; }
.status-badge.scheduled { background: #e3f2fd; color: #2196f3; }

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

.scheduled-reports {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  padding: 24px;
}

.scheduled-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.scheduled-header h3 {
  margin: 0;
  color: #1A1A1A;
  font-weight: 600;
}

.scheduled-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.scheduled-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border: 2px solid #e1e5e9;
  border-radius: 12px;
  transition: border-color 0.2s;
}

.scheduled-card:hover {
  border-color: #4A90E2;
}

.scheduled-info h4 {
  margin: 0 0 8px 0;
  color: #1A1A1A;
  font-weight: 600;
}

.scheduled-info p {
  margin: 0 0 4px 0;
  color: #666;
  font-size: 14px;
}

.next-run {
  color: #4A90E2;
  font-weight: 500;
}

.scheduled-actions {
  display: flex;
  gap: 12px;
}

.templates-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 24px;
}

.template-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  overflow: hidden;
  cursor: pointer;
  transition: all 0.2s;
}

.template-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.template-preview {
  height: 200px;
  background: #f8f9fa;
  display: flex;
  align-items: center;
  justify-content: center;
}

.template-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.preview-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #FF6B35, #4A90E2);
}

.preview-placeholder i {
  font-size: 48px;
  color: white;
}

.template-content {
  padding: 20px;
}

.template-content h4 {
  margin: 0 0 8px 0;
  color: #1A1A1A;
  font-weight: 600;
}

.template-content p {
  margin: 0 0 12px 0;
  color: #666;
  font-size: 14px;
}

.template-category {
  display: inline-block;
  padding: 4px 8px;
  background: #e3f2fd;
  color: #1976d2;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.analytics-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
}

.chart-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  padding: 24px;
}

.chart-container h3 {
  margin: 0 0 20px 0;
  color: #1A1A1A;
  font-weight: 600;
}

.chart-container canvas {
  width: 100%;
  height: 300px;
  background: #f8f9fa;
  border-radius: 8px;
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

.modal-content.large {
  max-width: 800px;
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

.form-steps {
  display: flex;
  justify-content: center;
  margin-bottom: 32px;
}

.step {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 20px;
  color: #666;
  font-weight: 500;
}

.step.active {
  color: #FF6B35;
}

.step-number {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #e1e5e9;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  color: #666;
}

.step.active .step-number {
  background: #FF6B35;
  color: white;
}

.form-step {
  min-height: 300px;
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

.config-section {
  margin-bottom: 32px;
}

.config-section h4 {
  margin: 0 0 16px 0;
  color: #1A1A1A;
  font-weight: 600;
}

.checkbox-group {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.checkbox-label, .radio-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 12px;
  border: 2px solid #e1e5e9;
  border-radius: 8px;
  transition: border-color 0.2s;
}

.checkbox-label:hover, .radio-label:hover {
  border-color: #4A90E2;
}

.checkbox-label input, .radio-label input {
  margin: 0;
}

.schedule-options {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 24px;
}

.recurring-config {
  margin-top: 24px;
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

.loading-content {
  text-align: center;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e1e5e9;
  border-top: 4px solid #FF6B35;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px auto;
}

.loading-content p {
  color: #666;
  font-weight: 500;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Responsive */
@media (max-width: 768px) {
  .bcm-reporting {
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

  .quick-actions {
    grid-template-columns: 1fr;
  }

  .controls-section {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }

  .filters-group {
    flex-direction: column;
  }

  .reports-grid {
    grid-template-columns: 1fr;
  }

  .templates-grid {
    grid-template-columns: 1fr;
  }

  .analytics-grid {
    grid-template-columns: 1fr;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .checkbox-group {
    grid-template-columns: 1fr;
  }
}
</style>