import { odooService } from './odoo'
import { assistantService } from './assistant'

class BCMKpiService {
  constructor() {
    this.model = 'bcm.kpi'
  }

  // KPI Management
  async getKpis(filters = {}) {
    try {
      const domain = this.buildDomain(filters)
      return await odooService.searchRead(this.model, {
        domain,
        fields: [
          'id', 'name', 'code', 'description', 'category', 'measurement_unit',
          'target_value', 'current_value', 'threshold_red', 'threshold_yellow',
          'threshold_green', 'calculation_method', 'frequency', 'responsible_id',
          'dashboard_visible', 'trend', 'status', 'last_updated',
          'data_source', 'create_date', 'write_date'
        ]
      })
    } catch (error) {
      console.error('Error fetching KPIs:', error)
      throw error
    }
  }

  async getKpiById(id) {
    try {
      const kpi = await odooService.read(this.model, [id], {
        fields: [
          'id', 'name', 'code', 'description', 'category', 'measurement_unit',
          'target_value', 'current_value', 'threshold_red', 'threshold_yellow',
          'threshold_green', 'calculation_method', 'frequency', 'responsible_id',
          'dashboard_visible', 'trend', 'status', 'last_updated', 'data_source',
          'historical_data', 'benchmark_data', 'improvement_actions',
          'create_date', 'write_date'
        ]
      })
      return kpi[0]
    } catch (error) {
      console.error('Error fetching KPI:', error)
      throw error
    }
  }

  async createKpi(kpiData) {
    try {
      const id = await odooService.create(this.model, kpiData)

      // Get AI recommendations for KPI optimization
      const aiRecommendations = await assistantService.getKpiRecommendations({
        name: kpiData.name,
        category: kpiData.category,
        calculationMethod: kpiData.calculation_method,
        targetValue: kpiData.target_value
      })

      if (aiRecommendations) {
        await odooService.write(this.model, [id], {
          ai_recommendations: aiRecommendations,
          optimization_suggestions: aiRecommendations.optimizations
        })
      }

      return id
    } catch (error) {
      console.error('Error creating KPI:', error)
      throw error
    }
  }

  async updateKpi(id, kpiData) {
    try {
      return await odooService.write(this.model, [id], kpiData)
    } catch (error) {
      console.error('Error updating KPI:', error)
      throw error
    }
  }

  async deleteKpi(id) {
    try {
      return await odooService.unlink(this.model, [id])
    } catch (error) {
      console.error('Error deleting KPI:', error)
      throw error
    }
  }

  // KPI Data Collection
  async updateKpiValue(id, value, date = null) {
    try {
      const updateData = {
        current_value: value,
        last_updated: date || new Date().toISOString()
      }

      // Calculate status based on thresholds
      const kpi = await this.getKpiById(id)
      const status = this.calculateStatus(value, kpi)
      updateData.status = status

      // Update trend analysis
      const trend = await this.calculateTrend(id, value)
      updateData.trend = trend

      return await odooService.write(this.model, [id], updateData)
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
      return await odooService.callMethod(this.model, 'get_trend_data', [kpiId, period])
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
      return await odooService.callMethod(this.model, 'generate_kpi_report', [filters])
    } catch (error) {
      console.error('Error generating KPI report:', error)
      throw error
    }
  }

  async exportKpiData(filters = {}, format = 'xlsx') {
    try {
      return await odooService.callMethod(this.model, 'export_kpi_data', [filters, format])
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
      const insights = await assistantService.analyzeKpiPerformance({
        kpiIds,
        timeframe: '3M'
      })

      return {
        patterns: insights.patterns,
        recommendations: insights.recommendations,
        predictions: insights.predictions,
        anomalies: insights.anomalies
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