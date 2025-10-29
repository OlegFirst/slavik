import { NextResponse } from 'next/server'

export async function GET() {
  try {
    // Генерируем реалистичные метрики
    const currentHour = new Date().getHours()
    const baseUsers = currentHour >= 9 && currentHour <= 17 ? 120 : 45 // Рабочее время
    
    // Имитируем hourly data за последние 24 часа
    const hourlyData = Array.from({ length: 24 }, (_, i) => {
      const hour = (new Date().getHours() - 23 + i) % 24
      const isWorkingHour = hour >= 9 && hour <= 17
      
      return {
        hour: `${hour.toString().padStart(2, '0')}:00`,
        users: Math.floor(Math.random() * 40) + (isWorkingHour ? 80 : 20),
        pageViews: Math.floor(Math.random() * 200) + (isWorkingHour ? 400 : 100),
        responseTime: Math.floor(Math.random() * 100) + (isWorkingHour ? 250 : 180),
        errors: Math.floor(Math.random() * 3) + (isWorkingHour ? 2 : 0)
      }
    })

    // Section usage analytics
    const sectionUsage = {
      'risk-assessment': {
        dailyViews: Math.floor(Math.random() * 200) + 450,
        avgSessionTime: '8m 32s',
        bounceRate: '23%',
        topPages: ['BIA Dashboard', 'Risk Matrix', 'AI Analysis'],
        userGrowth: '+12%'
      },
      'ai-automation': {
        dailyViews: Math.floor(Math.random() * 150) + 320,
        avgSessionTime: '12m 45s',
        bounceRate: '18%',
        topPages: ['AI Control Center', 'Automation Workflows', 'AI Consultant'],
        userGrowth: '+28%'
      },
      'analytics': {
        dailyViews: Math.floor(Math.random() * 180) + 380,
        avgSessionTime: '15m 12s',
        bounceRate: '15%',
        topPages: ['Executive Dashboard', 'KPI Monitor', 'Custom Reports'],
        userGrowth: '+8%'
      },
      'incident-management': {
        dailyViews: Math.floor(Math.random() * 100) + 220,
        avgSessionTime: '6m 28s',
        bounceRate: '32%',
        topPages: ['Crisis Communication', 'Recovery Coordination', 'Incidents'],
        userGrowth: '+15%'
      },
      'strategy-planning': {
        dailyViews: Math.floor(Math.random() * 120) + 280,
        avgSessionTime: '18m 54s',
        bounceRate: '12%',
        topPages: ['Plan Builder', 'Plans Management', 'Governance'],
        userGrowth: '+5%'
      },
      'workspace': {
        dailyViews: Math.floor(Math.random() * 300) + 650,
        avgSessionTime: '22m 18s',
        bounceRate: '8%',
        topPages: ['Personal Dashboard', 'User Settings', 'My Tasks'],
        userGrowth: '+18%'
      }
    }

    // Performance metrics
    const performanceMetrics = {
      avgResponseTime: Math.floor(Math.random() * 50) + 220, // 220-270ms
      p95ResponseTime: Math.floor(Math.random() * 100) + 450, // 450-550ms
      errorRate: (Math.random() * 0.08 + 0.01).toFixed(3), // 0.01-0.09%
      throughput: Math.floor(Math.random() * 200) + 800, // 800-1000 req/min
      uptime: 99.8 + (Math.random() * 0.19), // 99.8-99.99%
      
      // Breakdown by section
      sectionPerformance: Object.keys(sectionUsage).map(section => ({
        section,
        avgResponseTime: Math.floor(Math.random() * 80) + 180,
        errorRate: (Math.random() * 0.05).toFixed(3),
        requests: Math.floor(Math.random() * 1000) + 500
      }))
    }

    // User analytics
    const userAnalytics = {
      activeUsers: baseUsers + Math.floor(Math.random() * 30),
      uniqueVisitors: Math.floor(Math.random() * 100) + 890,
      newUsers: Math.floor(Math.random() * 25) + 45,
      returningUsers: Math.floor(Math.random() * 80) + 420,
      averageSessionDuration: '14m 32s',
      
      // User engagement
      engagement: {
        dailyActiveUsers: Math.floor(Math.random() * 50) + 180,
        weeklyActiveUsers: Math.floor(Math.random() * 200) + 450,
        monthlyActiveUsers: Math.floor(Math.random() * 500) + 1200,
        userRetention: '76%'
      },
      
      // Geographic data (mock)
      topCountries: [
        { country: 'United States', users: Math.floor(Math.random() * 100) + 200 },
        { country: 'United Kingdom', users: Math.floor(Math.random() * 50) + 80 },
        { country: 'Canada', users: Math.floor(Math.random() * 30) + 45 },
        { country: 'Australia', users: Math.floor(Math.random() * 25) + 35 },
        { country: 'Germany', users: Math.floor(Math.random() * 20) + 25 }
      ]
    }

    // Alert conditions
    const alerts = []
    if (performanceMetrics.avgResponseTime > 300) {
      alerts.push({
        severity: 'medium',
        type: 'performance',
        message: `High response time: ${performanceMetrics.avgResponseTime}ms`,
        timestamp: new Date().toISOString()
      })
    }
    if (parseFloat(performanceMetrics.errorRate) > 0.05) {
      alerts.push({
        severity: 'high',
        type: 'errors',
        message: `Elevated error rate: ${performanceMetrics.errorRate}%`,
        timestamp: new Date().toISOString()
      })
    }
    if (userAnalytics.activeUsers < 50) {
      alerts.push({
        severity: 'low',
        type: 'usage',
        message: `Low user activity: ${userAnalytics.activeUsers} active users`,
        timestamp: new Date().toISOString()
      })
    }

    return NextResponse.json({
      timestamp: new Date().toISOString(),
      platform: 'Unified BCM Platform',
      
      // Real-time metrics
      realtime: {
        activeUsers: userAnalytics.activeUsers,
        requestsPerSecond: Math.floor(performanceMetrics.throughput / 60),
        responseTime: `${performanceMetrics.avgResponseTime}ms`,
        errorRate: `${performanceMetrics.errorRate}%`,
        uptime: `${performanceMetrics.uptime.toFixed(2)}%`
      },
      
      // Detailed analytics
      performance: performanceMetrics,
      usage: userAnalytics,
      sections: sectionUsage,
      
      // Time-series data
      timeSeries: {
        last24Hours: hourlyData,
        updateInterval: '1 hour'
      },
      
      // Alerts and issues
      alerts,
      alertCount: {
        critical: alerts.filter(a => a.severity === 'critical').length,
        high: alerts.filter(a => a.severity === 'high').length,
        medium: alerts.filter(a => a.severity === 'medium').length,
        low: alerts.filter(a => a.severity === 'low').length
      }
    })
    
  } catch (error) {
    console.error('Metrics collection failed:', error)
    
    return NextResponse.json({
      timestamp: new Date().toISOString(),
      platform: 'Unified BCM Platform',
      error: 'Metrics collection failed',
      message: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 })
  }
}