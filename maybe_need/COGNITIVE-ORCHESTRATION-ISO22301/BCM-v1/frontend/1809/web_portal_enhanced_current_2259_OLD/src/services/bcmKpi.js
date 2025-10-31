// Mock data for development
const mockKpis = [
  {
    id: 1,
    name: 'System Uptime',
    code: 'SYS-001',
    description: 'Percentage of system availability',
    category: 'operational',
    measurement_unit: '%',
    target_value: 99.9,
    current_value: 99.7,
    threshold_green: 99.5,
    threshold_yellow: 98.0,
    threshold_red: 95.0,
    status: 'green',
    trend: 'stable',
    last_updated: '2024-01-15',
    dashboard_visible: true
  },
  {
    id: 2,
    name: 'Recovery Time Objective',
    code: 'RTO-001',
    description: 'Maximum acceptable downtime',
    category: 'operational',
    measurement_unit: 'hours',
    target_value: 4,
    current_value: 2.5,
    threshold_green: 4,
    threshold_yellow: 6,
    threshold_red: 8,
    status: 'green',
    trend: 'improving',
    last_updated: '2024-01-14',
    dashboard_visible: true
  },
  {
    id: 3,
    name: 'Training Completion Rate',
    code: 'TRN-001',
    description: 'Percentage of staff completed BCM training',
    category: 'learning',
    measurement_unit: '%',
    target_value: 100,
    current_value: 85,
    threshold_green: 95,
    threshold_yellow: 80,
    threshold_red: 70,
    status: 'yellow',
    trend: 'increasing',
    last_updated: '2024-01-13',
    dashboard_visible: true
  }
]

class BCMKpiService {
  constructor() {
    this.model = 'bcm.kpi'
  }

  // KPI Management
  async getKpis(filters = {}) {
    try {
      // Return mock data filtered by any filters
      let filteredKpis = [...mockKpis]

      if (filters.category) {
        filteredKpis = filteredKpis.filter(kpi => kpi.category === filters.category)
      }
      if (filters.status) {
        filteredKpis = filteredKpis.filter(kpi => kpi.status === filters.status)
      }
      if (filters.search) {
        const search = filters.search.toLowerCase()
        filteredKpis = filteredKpis.filter(kpi =>
          kpi.name.toLowerCase().includes(search) ||
          kpi.code.toLowerCase().includes(search)
        )
      }

      return filteredKpis
    } catch (error) {
      console.error('Error fetching KPIs:', error)
      throw error
    }
  }

  async getKpiById(id) {
    try {
      const kpi = mockKpis.find(k => k.id === id)
      return kpi || null
    } catch (error) {
      console.error('Error fetching KPI:', error)
      throw error
    }
  }

  async createKpi(kpiData) {
    try {
      // Create new KPI with mock ID
      const newId = Math.max(...mockKpis.map(k => k.id)) + 1
      const newKpi = {
        ...kpiData,
        id: newId,
        status: 'green',
        trend: 'stable',
        current_value: 0,
        last_updated: new Date().toISOString().split('T')[0]
      }

      mockKpis.push(newKpi)
      return newId
    } catch (error) {
      console.error('Error creating KPI:', error)
      throw error
    }
  }

  async updateKpi(id, kpiData) {
    try {
      const kpiIndex = mockKpis.findIndex(k => k.id === id)
      if (kpiIndex !== -1) {
        mockKpis[kpiIndex] = { ...mockKpis[kpiIndex], ...kpiData }
      }
      return true
    } catch (error) {
      console.error('Error updating KPI:', error)
      throw error
    }
  }

  async deleteKpi(id) {
    try {
      const kpiIndex = mockKpis.findIndex(k => k.id === id)
      if (kpiIndex !== -1) {
        mockKpis.splice(kpiIndex, 1)
      }
      return true
    } catch (error) {
      console.error('Error deleting KPI:', error)
      throw error
    }
  }

  // KPI Data Collection
  async updateKpiValue(id, value, date = null) {
    try {
      const kpiIndex = mockKpis.findIndex(k => k.id === id)
      if (kpiIndex !== -1) {
        const kpi = mockKpis[kpiIndex]
        kpi.current_value = value
        kpi.last_updated = date || new Date().toISOString().split('T')[0]
        kpi.status = this.calculateStatus(value, kpi)
        // Simple trend calculation
        kpi.trend = value > kpi.target_value * 0.9 ? 'increasing' : 'stable'
      }
      return true
    } catch (error) {
      console.error('Error updating KPI value:', error)
      throw error
    }
  }

  async bulkUpdateKpis(updates) {
    try {
      const results = []
      for (const update of updates) {
        const result = await this.updateKpiValue(update.id, update.value, update.date)
        results.push(result)
      }
      return results
    } catch (error) {
      console.error('Error bulk updating KPIs:', error)
      throw error
    }
  }

  // Dashboard & Analytics
  async getDashboardData(filters = {}) {
    try {
      const kpis = await this.getKpis({ ...filters, dashboard_visible: true })

      const dashboardData = {
        kpis,
        summary: {
          total: kpis.length,
          green: kpis.filter(k => k.status === 'green').length,
          yellow: kpis.filter(k => k.status === 'yellow').length,
          red: kpis.filter(k => k.status === 'red').length
        },
        trends: {},
        categories: {}
      }

      // Group by category
      kpis.forEach(kpi => {
        if (!dashboardData.categories[kpi.category]) {
          dashboardData.categories[kpi.category] = []
        }
        dashboardData.categories[kpi.category].push(kpi)
      })

      return dashboardData
    } catch (error) {
      console.error('Error fetching dashboard data:', error)
      throw error
    }
  }

  async getKpiTrends(kpiId, period = '6M') {
    try {
      // Return mock trend data
      return [
        { date: '2024-01-01', value: 95 },
        { date: '2024-01-15', value: 97 },
        { date: '2024-02-01', value: 99 }
      ]
    } catch (error) {
      console.error('Error fetching KPI trends:', error)
      throw error
    }
  }

  async getAnalyticsData(filters = {}) {
    try {
      return await odooService.callMethod(this.model, 'get_analytics_data', [filters])
    } catch (error) {
      console.error('Error fetching analytics data:', error)
      throw error
    }
  }

  // Reporting
  async generateKpiReport(filters = {}) {
    try {
      // Return mock report data
      return {
        success: true,
        message: 'Report generated successfully',
        url: '/mock-reports/kpi-report.pdf'
      }
    } catch (error) {
      console.error('Error generating KPI report:', error)
      throw error
    }
  }

  async exportKpiData(filters = {}, format = 'xlsx') {
    try {
      // Return mock export data
      return {
        success: true,
        message: 'Data exported successfully',
        url: `/mock-exports/kpi-data.${format}`
      }
    } catch (error) {
      console.error('Error exporting KPI data:', error)
      throw error
    }
  }

  // Benchmarking
  async getBenchmarkData(category = null) {
    try {
      return await odooService.callMethod('bcm.kpi.benchmark', 'get_benchmark_data', [category])
    } catch (error) {
      console.error('Error fetching benchmark data:', error)
      throw error
    }
  }

  async compareToBenchmark(kpiId) {
    try {
      return await odooService.callMethod(this.model, 'compare_to_benchmark', [kpiId])
    } catch (error) {
      console.error('Error comparing to benchmark:', error)
      throw error
    }
  }

  // Targets & Goals
  async setKpiTarget(kpiId, targetValue, targetDate = null) {
    try {
      return await odooService.write(this.model, [kpiId], {
        target_value: targetValue,
        target_date: targetDate
      })
    } catch (error) {
      console.error('Error setting KPI target:', error)
      throw error
    }
  }

  async getGoalProgress(filters = {}) {
    try {
      return await odooService.callMethod(this.model, 'get_goal_progress', [filters])
    } catch (error) {
      console.error('Error fetching goal progress:', error)
      throw error
    }
  }

  // Alerts & Notifications
  async getKpiAlerts() {
    try {
      return await odooService.searchRead('bcm.kpi.alert', {
        domain: [['active', '=', true]],
        fields: [
          'id', 'kpi_id', 'alert_type', 'threshold_value', 'message',
          'severity', 'notification_sent', 'create_date'
        ]
      })
    } catch (error) {
      console.error('Error fetching KPI alerts:', error)
      throw error
    }
  }

  async createAlert(alertData) {
    try {
      return await odooService.create('bcm.kpi.alert', alertData)
    } catch (error) {
      console.error('Error creating alert:', error)
      throw error
    }
  }

  // Data Integration
  async syncExternalData(dataSource) {
    try {
      return await odooService.callMethod(this.model, 'sync_external_data', [dataSource])
    } catch (error) {
      console.error('Error syncing external data:', error)
      throw error
    }
  }

  async getDataSources() {
    try {
      return await odooService.searchRead('bcm.kpi.data_source', {
        domain: [],
        fields: ['id', 'name', 'source_type', 'connection_status', 'last_sync']
      })
    } catch (error) {
      console.error('Error fetching data sources:', error)
      throw error
    }
  }

  // AI Analytics
  async getAiInsights(kpiIds = []) {
    try {
      // Return mock AI insights
      return {
        patterns: [
          { id: 1, description: 'System uptime shows consistent performance during business hours' },
          { id: 2, description: 'Training completion rates improve significantly after reminder campaigns' }
        ],
        recommendations: [
          { id: 1, description: 'Consider implementing automated backup procedures to improve RTO' },
          { id: 2, description: 'Schedule monthly training refreshers to maintain high completion rates' }
        ],
        predictions: [
          { id: 1, description: 'System uptime expected to remain stable with current infrastructure' }
        ],
        anomalies: []
      }
    } catch (error) {
      console.error('Error getting AI insights:', error)
      throw error
    }
  }

  async predictKpiTrend(kpiId, horizon = '3M') {
    try {
      return await assistantService.predictKpiTrend({
        kpiId,
        horizon,
        includeSeasonality: true
      })
    } catch (error) {
      console.error('Error predicting KPI trend:', error)
      throw error
    }
  }

  // Utility Methods
  buildDomain(filters) {
    const domain = []

    if (filters.category) {
      domain.push(['category', '=', filters.category])
    }
    if (filters.status) {
      domain.push(['status', 'in', Array.isArray(filters.status) ? filters.status : [filters.status]])
    }
    if (filters.responsible_id) {
      domain.push(['responsible_id', '=', filters.responsible_id])
    }
    if (filters.dashboard_visible !== undefined) {
      domain.push(['dashboard_visible', '=', filters.dashboard_visible])
    }
    if (filters.search) {
      domain.push(['|', ['name', 'ilike', filters.search], ['code', 'ilike', filters.search]])
    }

    return domain
  }

  calculateStatus(value, kpi) {
    if (value >= kpi.threshold_green) return 'green'
    if (value >= kpi.threshold_yellow) return 'yellow'
    return 'red'
  }

  async calculateTrend(kpiId, currentValue) {
    try {
      const historicalData = await this.getKpiTrends(kpiId, '3M')
      if (!historicalData || historicalData.length < 2) return 'stable'

      const previousValue = historicalData[historicalData.length - 2].value
      const change = ((currentValue - previousValue) / previousValue) * 100

      if (change > 5) return 'increasing'
      if (change < -5) return 'decreasing'
      return 'stable'
    } catch (error) {
      console.error('Error calculating trend:', error)
      return 'stable'
    }
  }

  // KPI Templates
  async getKpiTemplates() {
    try {
      return await odooService.searchRead('bcm.kpi.template', {
        domain: [],
        fields: [
          'id', 'name', 'category', 'description', 'measurement_unit',
          'calculation_method', 'frequency', 'industry_standard'
        ]
      })
    } catch (error) {
      console.error('Error fetching KPI templates:', error)
      throw error
    }
  }

  async createKpiFromTemplate(templateId, customization = {}) {
    try {
      return await odooService.callMethod('bcm.kpi.template', 'create_kpi_from_template', [templateId, customization])
    } catch (error) {
      console.error('Error creating KPI from template:', error)
      throw error
    }
  }
}

export const bcmKpiService = new BCMKpiService()