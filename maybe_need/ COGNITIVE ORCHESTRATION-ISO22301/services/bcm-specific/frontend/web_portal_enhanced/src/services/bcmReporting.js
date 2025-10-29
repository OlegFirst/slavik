import { odooService } from './odoo'
import { assistantService } from './assistant'

class BCMReportingService {
  constructor() {
    this.model = 'bcm.report'
  }

  // Report Management
  async getReports(filters = {}) {
    try {
      const domain = this.buildDomain(filters)
      return await odooService.searchRead(this.model, {
        domain,
        fields: [
          'id', 'name', 'report_type', 'category', 'status', 'format',
          'generated_date', 'scheduled', 'frequency', 'next_run',
          'recipients', 'file_size', 'download_count', 'public',
          'create_uid', 'create_date', 'write_date'
        ]
      })
    } catch (error) {
      console.error('Error fetching reports:', error)
      throw error
    }
  }

  async getReportById(id) {
    try {
      const report = await odooService.read(this.model, [id], {
        fields: [
          'id', 'name', 'description', 'report_type', 'category', 'status',
          'format', 'generated_date', 'scheduled', 'frequency', 'next_run',
          'recipients', 'file_size', 'download_count', 'public',
          'parameters', 'filters', 'data_sources', 'visualization_config',
          'template_id', 'create_uid', 'create_date', 'write_date'
        ]
      })
      return report[0]
    } catch (error) {
      console.error('Error fetching report:', error)
      throw error
    }
  }

  async createReport(reportData) {
    try {
      const id = await odooService.create(this.model, reportData)

      // Get AI recommendations for report optimization
      const aiSuggestions = await assistantService.getReportingSuggestions({
        reportType: reportData.report_type,
        category: reportData.category,
        dataSource: reportData.data_sources
      })

      if (aiSuggestions) {
        await odooService.write(this.model, [id], {
          ai_suggestions: aiSuggestions,
          optimization_recommendations: aiSuggestions.optimizations
        })
      }

      return id
    } catch (error) {
      console.error('Error creating report:', error)
      throw error
    }
  }

  async updateReport(id, reportData) {
    try {
      return await odooService.write(this.model, [id], reportData)
    } catch (error) {
      console.error('Error updating report:', error)
      throw error
    }
  }

  async deleteReport(id) {
    try {
      return await odooService.unlink(this.model, [id])
    } catch (error) {
      console.error('Error deleting report:', error)
      throw error
    }
  }

  // Report Generation
  async generateReport(reportId, parameters = {}) {
    try {
      return await odooService.callMethod(this.model, 'generate_report', [reportId, parameters])
    } catch (error) {
      console.error('Error generating report:', error)
      throw error
    }
  }

  async generateCustomReport(config) {
    try {
      return await odooService.callMethod(this.model, 'generate_custom_report', [config])
    } catch (error) {
      console.error('Error generating custom report:', error)
      throw error
    }
  }

  async previewReport(reportId, parameters = {}) {
    try {
      return await odooService.callMethod(this.model, 'preview_report', [reportId, parameters])
    } catch (error) {
      console.error('Error previewing report:', error)
      throw error
    }
  }

  // Dashboard & Analytics Reports
  async getDashboardReport(timeframe = '30d') {
    try {
      return await odooService.callMethod(this.model, 'get_dashboard_report', [timeframe])
    } catch (error) {
      console.error('Error fetching dashboard report:', error)
      throw error
    }
  }

  async getExecutiveSummary(filters = {}) {
    try {
      return await odooService.callMethod(this.model, 'get_executive_summary', [filters])
    } catch (error) {
      console.error('Error fetching executive summary:', error)
      throw error
    }
  }

  async getComplianceReport(standard = 'ISO22301') {
    try {
      return await odooService.callMethod(this.model, 'get_compliance_report', [standard])
    } catch (error) {
      console.error('Error fetching compliance report:', error)
      throw error
    }
  }

  async getRiskReport(riskLevel = null) {
    try {
      return await odooService.callMethod(this.model, 'get_risk_report', [riskLevel])
    } catch (error) {
      console.error('Error fetching risk report:', error)
      throw error
    }
  }

  async getIncidentReport(timeframe = '90d') {
    try {
      return await odooService.callMethod(this.model, 'get_incident_report', [timeframe])
    } catch (error) {
      console.error('Error fetching incident report:', error)
      throw error
    }
  }

  async getAuditReport(auditType = null) {
    try {
      return await odooService.callMethod(this.model, 'get_audit_report', [auditType])
    } catch (error) {
      console.error('Error fetching audit report:', error)
      throw error
    }
  }

  async getBIAReport(criticality = null) {
    try {
      return await odooService.callMethod(this.model, 'get_bia_report', [criticality])
    } catch (error) {
      console.error('Error fetching BIA report:', error)
      throw error
    }
  }

  async getKPIReport(category = null) {
    try {
      return await odooService.callMethod(this.model, 'get_kpi_report', [category])
    } catch (error) {
      console.error('Error fetching KPI report:', error)
      throw error
    }
  }

  // Report Scheduling
  async getScheduledReports() {
    try {
      return await odooService.searchRead(this.model, {
        domain: [['scheduled', '=', true]],
        fields: [
          'id', 'name', 'report_type', 'frequency', 'next_run',
          'recipients', 'status', 'last_generated'
        ]
      })
    } catch (error) {
      console.error('Error fetching scheduled reports:', error)
      throw error
    }
  }

  async scheduleReport(reportId, scheduleConfig) {
    try {
      return await odooService.callMethod(this.model, 'schedule_report', [reportId, scheduleConfig])
    } catch (error) {
      console.error('Error scheduling report:', error)
      throw error
    }
  }

  async unscheduleReport(reportId) {
    try {
      return await odooService.write(this.model, [reportId], {
        scheduled: false,
        frequency: false,
        next_run: false
      })
    } catch (error) {
      console.error('Error unscheduling report:', error)
      throw error
    }
  }

  // Report Templates
  async getReportTemplates() {
    try {
      return await odooService.searchRead('bcm.report.template', {
        domain: [],
        fields: [
          'id', 'name', 'description', 'category', 'report_type',
          'default_format', 'parameters', 'preview_image'
        ]
      })
    } catch (error) {
      console.error('Error fetching report templates:', error)
      throw error
    }
  }

  async createReportFromTemplate(templateId, customization = {}) {
    try {
      return await odooService.callMethod('bcm.report.template', 'create_from_template', [templateId, customization])
    } catch (error) {
      console.error('Error creating report from template:', error)
      throw error
    }
  }

  // Data Export
  async exportData(dataType, filters = {}, format = 'xlsx') {
    try {
      return await odooService.callMethod(this.model, 'export_data', [dataType, filters, format])
    } catch (error) {
      console.error('Error exporting data:', error)
      throw error
    }
  }

  async bulkExport(exportConfigs) {
    try {
      return await odooService.callMethod(this.model, 'bulk_export', [exportConfigs])
    } catch (error) {
      console.error('Error bulk exporting:', error)
      throw error
    }
  }

  // Report Sharing & Distribution
  async shareReport(reportId, shareConfig) {
    try {
      return await odooService.callMethod(this.model, 'share_report', [reportId, shareConfig])
    } catch (error) {
      console.error('Error sharing report:', error)
      throw error
    }
  }

  async getSharedReports() {
    try {
      return await odooService.searchRead(this.model, {
        domain: [['public', '=', true]],
        fields: [
          'id', 'name', 'report_type', 'category', 'generated_date',
          'download_count', 'shared_by'
        ]
      })
    } catch (error) {
      console.error('Error fetching shared reports:', error)
      throw error
    }
  }

  async sendReportByEmail(reportId, recipients, message = '') {
    try {
      return await odooService.callMethod(this.model, 'send_by_email', [reportId, recipients, message])
    } catch (error) {
      console.error('Error sending report by email:', error)
      throw error
    }
  }

  // Analytics & Insights
  async getReportAnalytics(reportId) {
    try {
      return await odooService.callMethod(this.model, 'get_analytics', [reportId])
    } catch (error) {
      console.error('Error fetching report analytics:', error)
      throw error
    }
  }

  async getReportingTrends(timeframe = '12M') {
    try {
      return await odooService.callMethod(this.model, 'get_reporting_trends', [timeframe])
    } catch (error) {
      console.error('Error fetching reporting trends:', error)
      throw error
    }
  }

  async getPopularReports(limit = 10) {
    try {
      return await odooService.searchRead(this.model, {
        domain: [],
        fields: ['id', 'name', 'report_type', 'download_count', 'generated_date'],
        order: 'download_count desc',
        limit
      })
    } catch (error) {
      console.error('Error fetching popular reports:', error)
      throw error
    }
  }

  // AI-Powered Reporting
  async getAiReportInsights(reportId) {
    try {
      const report = await this.getReportById(reportId)
      const insights = await assistantService.analyzeReportData({
        reportType: report.report_type,
        dataPoints: report.parameters,
        historical: true
      })

      return {
        keyFindings: insights.findings,
        trends: insights.trends,
        recommendations: insights.recommendations,
        anomalies: insights.anomalies
      }
    } catch (error) {
      console.error('Error getting AI report insights:', error)
      throw error
    }
  }

  async generateAiSummary(reportId) {
    try {
      return await assistantService.generateReportSummary({
        reportId,
        includeVisualizationSuggestions: true,
        includeActionItems: true
      })
    } catch (error) {
      console.error('Error generating AI summary:', error)
      throw error
    }
  }

  async predictReportUsage(reportId) {
    try {
      return await assistantService.predictReportUsage({
        reportId,
        timeframe: '6M',
        includeTrends: true
      })
    } catch (error) {
      console.error('Error predicting report usage:', error)
      throw error
    }
  }

  // Report Collaboration
  async addComment(reportId, comment) {
    try {
      return await odooService.callMethod(this.model, 'add_comment', [reportId, comment])
    } catch (error) {
      console.error('Error adding comment:', error)
      throw error
    }
  }

  async getComments(reportId) {
    try {
      return await odooService.callMethod(this.model, 'get_comments', [reportId])
    } catch (error) {
      console.error('Error fetching comments:', error)
      throw error
    }
  }

  async bookmarkReport(reportId) {
    try {
      return await odooService.callMethod(this.model, 'bookmark_report', [reportId])
    } catch (error) {
      console.error('Error bookmarking report:', error)
      throw error
    }
  }

  async getBookmarkedReports() {
    try {
      return await odooService.callMethod(this.model, 'get_bookmarked_reports', [])
    } catch (error) {
      console.error('Error fetching bookmarked reports:', error)
      throw error
    }
  }

  // Utility Methods
  buildDomain(filters) {
    const domain = []

    if (filters.report_type) {
      domain.push(['report_type', '=', filters.report_type])
    }
    if (filters.category) {
      domain.push(['category', '=', filters.category])
    }
    if (filters.status) {
      domain.push(['status', 'in', Array.isArray(filters.status) ? filters.status : [filters.status]])
    }
    if (filters.scheduled !== undefined) {
      domain.push(['scheduled', '=', filters.scheduled])
    }
    if (filters.date_from) {
      domain.push(['generated_date', '>=', filters.date_from])
    }
    if (filters.date_to) {
      domain.push(['generated_date', '<=', filters.date_to])
    }
    if (filters.search) {
      domain.push(['name', 'ilike', filters.search])
    }

    return domain
  }

  formatReportSize(bytes) {
    if (!bytes) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  getReportTypeIcon(type) {
    const icons = {
      dashboard: 'icon-dashboard',
      compliance: 'icon-shield',
      risk: 'icon-warning',
      incident: 'icon-alert',
      audit: 'icon-check',
      bia: 'icon-business',
      kpi: 'icon-gauge',
      custom: 'icon-settings'
    }
    return icons[type] || 'icon-file'
  }

  getStatusColor(status) {
    const colors = {
      draft: '#666',
      generating: '#ff9800',
      completed: '#4caf50',
      failed: '#f44336',
      scheduled: '#2196f3'
    }
    return colors[status] || '#666'
  }
}

export const bcmReportingService = new BCMReportingService()