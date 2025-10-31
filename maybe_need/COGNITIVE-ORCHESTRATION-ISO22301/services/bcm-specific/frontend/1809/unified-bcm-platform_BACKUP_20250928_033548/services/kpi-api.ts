'use client'

// KPI API Service for BCM Performance Metrics
export interface KPIMetric {
  id: string
  name: string
  value: number
  target: number
  unit: string
  category: 'risk' | 'incident' | 'bia' | 'compliance' | 'performance'
  trend: 'up' | 'down' | 'stable'
  change: number
  description: string
  lastUpdated: string
}

export interface KPIDashboard {
  id: string
  name: string
  description: string
  metrics: KPIMetric[]
  overallScore: number
  categories: {
    category: string
    score: number
    weight: number
  }[]
}

export interface KPITarget {
  metricId: string
  target: number
  deadline: string
  priority: 'critical' | 'high' | 'medium' | 'low'
  description: string
}

export interface KPITimeSeriesData {
  timestamp: string
  value: number
  target: number
}

class KPIAPI {
  private baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080'

  // Get KPI metrics for analytics
  async getKPIMetrics(timeRange: string = '30d'): Promise<{
    data: {
      overallScore: number
      scoreChange: number
      metrics: KPIMetric[]
      categoryScores: Record<string, number>
    }
  }> {
    const mockMetrics: KPIMetric[] = [
      {
        id: 'bcm-overall-score',
        name: 'BCM Overall Score',
        value: 86,
        target: 90,
        unit: '%',
        category: 'performance',
        trend: 'up',
        change: 3.2,
        description: 'Overall Business Continuity Management effectiveness score',
        lastUpdated: new Date().toISOString()
      },
      {
        id: 'risk-coverage',
        name: 'Risk Coverage',
        value: 87,
        target: 95,
        unit: '%',
        category: 'risk',
        trend: 'up',
        change: 5.1,
        description: 'Percentage of identified risks with active mitigation plans',
        lastUpdated: new Date().toISOString()
      },
      {
        id: 'incident-mttr',
        name: 'Mean Time to Resolution',
        value: 4.2,
        target: 3.0,
        unit: 'hours',
        category: 'incident',
        trend: 'down',
        change: -8.7,
        description: 'Average time to resolve incidents',
        lastUpdated: new Date().toISOString()
      },
      {
        id: 'bia-completion',
        name: 'BIA Completion Rate',
        value: 78,
        target: 85,
        unit: '%',
        category: 'bia',
        trend: 'up',
        change: 2.3,
        description: 'Percentage of business processes with completed BIA',
        lastUpdated: new Date().toISOString()
      },
      {
        id: 'compliance-score',
        name: 'Compliance Score',
        value: 84,
        target: 90,
        unit: '%',
        category: 'compliance',
        trend: 'down',
        change: -1.2,
        description: 'Overall regulatory compliance score',
        lastUpdated: new Date().toISOString()
      }
    ]

    const categoryScores = {
      risk: 87,
      incident: 82,
      bia: 78,
      compliance: 84,
      performance: 86
    }

    return new Promise((resolve) => {
      setTimeout(() => resolve({
        data: {
          overallScore: 86,
          scoreChange: 2.1,
          metrics: mockMetrics,
          categoryScores
        }
      }), 600)
    })
  }

  // Get detailed KPI dashboard
  async getKPIDashboard(dashboardId?: string): Promise<{ data: KPIDashboard }> {
    const dashboard: KPIDashboard = {
      id: dashboardId || 'default',
      name: 'BCM Performance Dashboard',
      description: 'Comprehensive view of Business Continuity Management performance',
      metrics: await this.getKPIMetrics().then(result => result.data.metrics),
      overallScore: 86,
      categories: [
        { category: 'Risk Management', score: 87, weight: 0.25 },
        { category: 'Incident Response', score: 82, weight: 0.20 },
        { category: 'BIA Assessment', score: 78, weight: 0.20 },
        { category: 'Compliance', score: 84, weight: 0.15 },
        { category: 'Performance', score: 86, weight: 0.20 }
      ]
    }

    return new Promise((resolve) => {
      setTimeout(() => resolve({ data: dashboard }), 500)
    })
  }

  // Get KPI time series data for trends
  async getKPITimeSeries(
    metricId: string,
    timeRange: string = '30d'
  ): Promise<{ data: KPITimeSeriesData[] }> {
    // Generate mock time series data
    const periods = this.generateTimePeriods(timeRange)
    const baseValue = 85
    const baseTarget = 90

    const timeSeries: KPITimeSeriesData[] = periods.map((timestamp, index) => ({
      timestamp,
      value: baseValue + Math.random() * 10 - 5 + (index * 0.2),
      target: baseTarget
    }))

    return new Promise((resolve) => {
      setTimeout(() => resolve({ data: timeSeries }), 400)
    })
  }

  // Update KPI targets
  async updateKPITarget(target: KPITarget): Promise<{ success: boolean }> {
    // Mock implementation
    return new Promise((resolve) => {
      setTimeout(() => resolve({ success: true }), 800)
    })
  }

  // Get KPI benchmarks (industry comparisons)
  async getKPIBenchmarks(category?: string): Promise<{
    data: {
      metric: string
      ourValue: number
      industryAverage: number
      topQuartile: number
      percentile: number
    }[]
  }> {
    const benchmarks = [
      {
        metric: 'BCM Overall Score',
        ourValue: 86,
        industryAverage: 82,
        topQuartile: 91,
        percentile: 68
      },
      {
        metric: 'Risk Coverage',
        ourValue: 87,
        industryAverage: 84,
        topQuartile: 95,
        percentile: 72
      },
      {
        metric: 'Incident MTTR',
        ourValue: 4.2,
        industryAverage: 5.1,
        topQuartile: 2.8,
        percentile: 78
      },
      {
        metric: 'Compliance Score',
        ourValue: 84,
        industryAverage: 87,
        topQuartile: 93,
        percentile: 45
      }
    ]

    return new Promise((resolve) => {
      setTimeout(() => resolve({ data: benchmarks }), 700)
    })
  }

  // Generate KPI reports
  async generateKPIReport(
    timeRange: string = '30d',
    categories?: string[]
  ): Promise<{
    data: {
      summary: {
        totalMetrics: number
        metricsOnTarget: number
        averageScore: number
        trends: Record<string, number>
      }
      details: KPIMetric[]
      recommendations: string[]
    }
  }> {
    const metrics = await this.getKPIMetrics(timeRange).then(result => result.data.metrics)
    const metricsOnTarget = metrics.filter(m => m.value >= m.target).length

    const report = {
      summary: {
        totalMetrics: metrics.length,
        metricsOnTarget,
        averageScore: 84.2,
        trends: {
          improving: 3,
          declining: 1,
          stable: 1
        }
      },
      details: metrics,
      recommendations: [
        'Focus on improving compliance score to meet industry standards',
        'Continue efforts to reduce incident resolution time',
        'Accelerate BIA completion across remaining business processes',
        'Maintain current risk management effectiveness'
      ]
    }

    return new Promise((resolve) => {
      setTimeout(() => resolve({ data: report }), 1000)
    })
  }

  // Get real-time KPI alerts
  async getKPIAlerts(): Promise<{
    data: {
      id: string
      metricId: string
      metricName: string
      type: 'target_missed' | 'threshold_breach' | 'trend_negative'
      severity: 'critical' | 'high' | 'medium' | 'low'
      message: string
      timestamp: string
    }[]
  }> {
    const alerts = [
      {
        id: 'alert-1',
        metricId: 'compliance-score',
        metricName: 'Compliance Score',
        type: 'target_missed' as const,
        severity: 'high' as const,
        message: 'Compliance score (84%) is below target (90%)',
        timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString()
      },
      {
        id: 'alert-2',
        metricId: 'incident-mttr',
        metricName: 'Mean Time to Resolution',
        type: 'threshold_breach' as const,
        severity: 'medium' as const,
        message: 'MTTR exceeded 4 hours threshold',
        timestamp: new Date(Date.now() - 30 * 60 * 1000).toISOString()
      }
    ]

    return new Promise((resolve) => {
      setTimeout(() => resolve({ data: alerts }), 300)
    })
  }

  // Helper method to generate time periods
  private generateTimePeriods(timeRange: string): string[] {
    const periods: string[] = []
    const now = new Date()

    let interval: number
    let count: number

    switch (timeRange) {
      case '24h':
        interval = 60 * 60 * 1000 // 1 hour
        count = 24
        break
      case '7d':
        interval = 24 * 60 * 60 * 1000 // 1 day
        count = 7
        break
      case '30d':
        interval = 24 * 60 * 60 * 1000 // 1 day
        count = 30
        break
      case '90d':
        interval = 7 * 24 * 60 * 60 * 1000 // 1 week
        count = 13
        break
      case '1y':
        interval = 30 * 24 * 60 * 60 * 1000 // 1 month
        count = 12
        break
      default:
        interval = 24 * 60 * 60 * 1000
        count = 30
    }

    for (let i = count - 1; i >= 0; i--) {
      const time = new Date(now.getTime() - (i * interval))
      periods.push(time.toISOString())
    }

    return periods
  }
}

export const kpiAPI = new KPIAPI()

// Export query keys for React Query
export const kpiQueryKeys = {
  all: ['kpi'] as const,
  metrics: (timeRange: string) => [...kpiQueryKeys.all, 'metrics', timeRange] as const,
  dashboard: (id?: string) => [...kpiQueryKeys.all, 'dashboard', id] as const,
  timeSeries: (metricId: string, timeRange: string) =>
    [...kpiQueryKeys.all, 'timeSeries', metricId, timeRange] as const,
  benchmarks: (category?: string) => [...kpiQueryKeys.all, 'benchmarks', category] as const,
  alerts: () => [...kpiQueryKeys.all, 'alerts'] as const
}

// Re-export types
export type {
  KPIMetric,
  KPIDashboard,
  KPITarget,
  KPITimeSeriesData
}