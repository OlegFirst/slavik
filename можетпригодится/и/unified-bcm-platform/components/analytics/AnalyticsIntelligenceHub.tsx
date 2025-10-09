'use client'

import React, { useState, useEffect, useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from '@/components/ui/select'
import { cn } from '@/lib/utils'
import {
  BarChart3,
  TrendingUp,
  TrendingDown,
  Target,
  AlertTriangle,
  Brain,
  Shield,
  Activity,
  Users,
  Clock,
  Zap,
  Download,
  RefreshCw,
  Calendar,
  Filter,
  Search,
  Eye,
  Settings,
  Database,
  PieChart,
  LineChart,
  BarChart,
  Layers,
  Map,
  CheckCircle2,
  XCircle,
  Minus
} from 'lucide-react'

// Import APIs
import { riskManagementAPI } from '@/services/risk-management-api'
import { biaAPI } from '@/services/bia-api'
import { kpiAPI } from '@/services/kpi-api'
import { analyticsAPI } from '@/services/analytics-api'
import { incidentAPI } from '@/services/incident-api'
import { auditAPI } from '@/services/audit-api'

// Types
interface AnalyticsMetric {
  id: string
  title: string
  value: number | string
  change: number
  trend: 'up' | 'down' | 'stable'
  format: 'number' | 'percentage' | 'currency' | 'time'
  category: 'risk' | 'bia' | 'kpi' | 'incident' | 'audit' | 'compliance'
  priority: 'critical' | 'high' | 'medium' | 'low'
}

interface IntelligenceInsight {
  id: string
  type: 'prediction' | 'anomaly' | 'recommendation' | 'alert'
  title: string
  description: string
  confidence: number
  severity: 'critical' | 'high' | 'medium' | 'low'
  category: string
  timestamp: string
  actionItems?: string[]
}

interface AnalyticsFilter {
  timeRange: '24h' | '7d' | '30d' | '90d' | '1y'
  categories: string[]
  priority: string[]
}

export function AnalyticsIntelligenceHub() {
  const [activeTab, setActiveTab] = useState('overview')
  const [filters, setFilters] = useState<AnalyticsFilter>({
    timeRange: '30d',
    categories: [],
    priority: []
  })
  const [autoRefresh, setAutoRefresh] = useState(true)

  // Fetch consolidated analytics data
  const { data: metrics, isLoading: metricsLoading, refetch: refetchMetrics } = useQuery({
    queryKey: ['analytics', 'consolidated-metrics', filters],
    queryFn: async () => {
      const [risks, bia, kpis, incidents, audits] = await Promise.all([
        riskManagementAPI.getRiskMetrics(filters.timeRange),
        biaAPI.getBIAMetrics(filters.timeRange),
        kpiAPI.getKPIMetrics(filters.timeRange),
        incidentAPI.getIncidentMetrics(filters.timeRange),
        auditAPI.getAuditMetrics(filters.timeRange)
      ])

      return {
        risks: risks.data,
        bia: bia.data,
        kpis: kpis.data,
        incidents: incidents.data,
        audits: audits.data
      }
    },
    refetchInterval: autoRefresh ? 30000 : false
  })

  // Fetch AI insights
  const { data: insights, isLoading: insightsLoading } = useQuery({
    queryKey: ['analytics', 'ai-insights', filters.timeRange],
    queryFn: () => analyticsAPI.getAIInsights(filters.timeRange),
    refetchInterval: autoRefresh ? 60000 : false
  })

  // Process metrics into unified format
  const unifiedMetrics = useMemo<AnalyticsMetric[]>(() => {
    if (!metrics) return []

    return [
      // Risk Metrics
      {
        id: 'total-risks',
        title: 'Total Risks',
        value: metrics.risks?.totalRisks || 0,
        change: metrics.risks?.riskGrowth || 0,
        trend: (metrics.risks?.riskGrowth || 0) > 0 ? 'up' : 'down',
        format: 'number',
        category: 'risk',
        priority: 'high'
      },
      {
        id: 'critical-risks',
        title: 'Critical Risks',
        value: metrics.risks?.criticalRisks || 0,
        change: metrics.risks?.criticalRiskChange || 0,
        trend: (metrics.risks?.criticalRiskChange || 0) > 0 ? 'up' : 'down',
        format: 'number',
        category: 'risk',
        priority: 'critical'
      },
      {
        id: 'risk-coverage',
        title: 'Risk Coverage',
        value: metrics.risks?.coverage || 0,
        change: metrics.risks?.coverageChange || 0,
        trend: (metrics.risks?.coverageChange || 0) > 0 ? 'up' : 'down',
        format: 'percentage',
        category: 'risk',
        priority: 'medium'
      },

      // BIA Metrics
      {
        id: 'bia-assessments',
        title: 'BIA Assessments',
        value: metrics.bia?.totalAssessments || 0,
        change: metrics.bia?.assessmentGrowth || 0,
        trend: (metrics.bia?.assessmentGrowth || 0) > 0 ? 'up' : 'down',
        format: 'number',
        category: 'bia',
        priority: 'medium'
      },
      {
        id: 'critical-processes',
        title: 'Critical Processes',
        value: metrics.bia?.criticalProcesses || 0,
        change: metrics.bia?.criticalProcessChange || 0,
        trend: (metrics.bia?.criticalProcessChange || 0) > 0 ? 'up' : 'down',
        format: 'number',
        category: 'bia',
        priority: 'high'
      },

      // KPI Metrics
      {
        id: 'overall-score',
        title: 'Overall BCM Score',
        value: metrics.kpis?.overallScore || 0,
        change: metrics.kpis?.scoreChange || 0,
        trend: (metrics.kpis?.scoreChange || 0) > 0 ? 'up' : 'down',
        format: 'percentage',
        category: 'kpi',
        priority: 'critical'
      },

      // Incident Metrics
      {
        id: 'active-incidents',
        title: 'Active Incidents',
        value: metrics.incidents?.activeIncidents || 0,
        change: metrics.incidents?.incidentChange || 0,
        trend: (metrics.incidents?.incidentChange || 0) > 0 ? 'up' : 'down',
        format: 'number',
        category: 'incident',
        priority: 'critical'
      },
      {
        id: 'mttr',
        title: 'Avg Resolution Time',
        value: metrics.incidents?.avgResolutionTime || 0,
        change: metrics.incidents?.mttrChange || 0,
        trend: (metrics.incidents?.mttrChange || 0) > 0 ? 'down' : 'up',
        format: 'time',
        category: 'incident',
        priority: 'high'
      }
    ]
  }, [metrics])

  // Get trend icon
  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up': return <TrendingUp className="h-4 w-4 text-green-600" />
      case 'down': return <TrendingDown className="h-4 w-4 text-red-600" />
      default: return <Minus className="h-4 w-4 text-gray-600" />
    }
  }

  // Get priority color
  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical': return 'border-red-500 bg-red-50'
      case 'high': return 'border-orange-500 bg-orange-50'
      case 'medium': return 'border-yellow-500 bg-yellow-50'
      default: return 'border-gray-300 bg-gray-50'
    }
  }

  // Format value based on type
  const formatValue = (value: number | string, format: string) => {
    if (typeof value === 'string') return value

    switch (format) {
      case 'percentage': return `${value}%`
      case 'currency': return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value)
      case 'time': return `${value}h`
      default: return value.toLocaleString()
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Brain className="h-6 w-6 text-blue-600" />
          <div>
            <h1 className="text-2xl font-bold">Analytics & Intelligence Hub</h1>
            <p className="text-gray-600">Consolidated insights across all BCM modules</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setAutoRefresh(!autoRefresh)}
          >
            <RefreshCw className={cn("h-4 w-4 mr-2", autoRefresh && "animate-spin")} />
            Auto-refresh: {autoRefresh ? 'On' : 'Off'}
          </Button>
          <Select value={filters.timeRange} onValueChange={(value: any) => setFilters({...filters, timeRange: value})}>
            <SelectTrigger className="w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="24h">24 Hours</SelectItem>
              <SelectItem value="7d">7 Days</SelectItem>
              <SelectItem value="30d">30 Days</SelectItem>
              <SelectItem value="90d">90 Days</SelectItem>
              <SelectItem value="1y">1 Year</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Analytics Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-6">
          <TabsTrigger value="overview" className="flex items-center gap-2">
            <BarChart3 className="h-4 w-4" />
            Overview
          </TabsTrigger>
          <TabsTrigger value="intelligence" className="flex items-center gap-2">
            <Brain className="h-4 w-4" />
            AI Insights
          </TabsTrigger>
          <TabsTrigger value="risks" className="flex items-center gap-2">
            <Shield className="h-4 w-4" />
            Risk Analytics
          </TabsTrigger>
          <TabsTrigger value="performance" className="flex items-center gap-2">
            <Target className="h-4 w-4" />
            Performance
          </TabsTrigger>
          <TabsTrigger value="trends" className="flex items-center gap-2">
            <TrendingUp className="h-4 w-4" />
            Trends
          </TabsTrigger>
          <TabsTrigger value="reports" className="flex items-center gap-2">
            <Database className="h-4 w-4" />
            Reports
          </TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="mt-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            {unifiedMetrics.map((metric) => (
              <Card key={metric.id} className={cn("border-l-4", getPriorityColor(metric.priority))}>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">{metric.title}</p>
                      <p className="text-2xl font-bold">{formatValue(metric.value, metric.format)}</p>
                    </div>
                    <div className="flex items-center gap-2">
                      {getTrendIcon(metric.trend)}
                      <span className={cn(
                        "text-sm font-medium",
                        metric.trend === 'up' ? "text-green-600" : metric.trend === 'down' ? "text-red-600" : "text-gray-600"
                      )}>
                        {Math.abs(metric.change)}%
                      </span>
                    </div>
                  </div>
                  <Badge variant="outline" className="mt-2 text-xs">
                    {metric.category.toUpperCase()}
                  </Badge>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Quick Status Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Activity className="h-5 w-5" />
                  System Health
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span>Risk Management</span>
                    <div className="flex items-center gap-2">
                      <CheckCircle2 className="h-4 w-4 text-green-600" />
                      <span className="text-sm text-green-600">Operational</span>
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>BIA Assessment</span>
                    <div className="flex items-center gap-2">
                      <CheckCircle2 className="h-4 w-4 text-green-600" />
                      <span className="text-sm text-green-600">Operational</span>
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Incident Response</span>
                    <div className="flex items-center gap-2">
                      <AlertTriangle className="h-4 w-4 text-yellow-600" />
                      <span className="text-sm text-yellow-600">Monitoring</span>
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Audit & Compliance</span>
                    <div className="flex items-center gap-2">
                      <CheckCircle2 className="h-4 w-4 text-green-600" />
                      <span className="text-sm text-green-600">Operational</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Users className="h-5 w-5" />
                  Active Sessions
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span>Risk Assessments</span>
                    <Badge variant="secondary">3 active</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>BIA Collaborations</span>
                    <Badge variant="secondary">5 active</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Incident Responses</span>
                    <Badge variant="destructive">1 critical</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Audit Reviews</span>
                    <Badge variant="secondary">2 active</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* AI Insights Tab */}
        <TabsContent value="intelligence" className="mt-6">
          <div className="space-y-6">
            {insightsLoading ? (
              <Card>
                <CardContent className="p-6">
                  <div className="animate-pulse space-y-4">
                    <div className="h-4 bg-gray-200 rounded w-1/3"></div>
                    <div className="h-4 bg-gray-200 rounded w-2/3"></div>
                    <div className="h-4 bg-gray-200 rounded w-1/2"></div>
                  </div>
                </CardContent>
              </Card>
            ) : (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {insights?.data?.map((insight: IntelligenceInsight) => (
                  <Card key={insight.id} className={cn(
                    "border-l-4",
                    insight.severity === 'critical' ? 'border-red-500' :
                    insight.severity === 'high' ? 'border-orange-500' :
                    insight.severity === 'medium' ? 'border-yellow-500' : 'border-blue-500'
                  )}>
                    <CardHeader>
                      <div className="flex items-center justify-between">
                        <CardTitle className="text-lg">{insight.title}</CardTitle>
                        <Badge variant={insight.type === 'alert' ? 'destructive' : 'secondary'}>
                          {insight.type}
                        </Badge>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <p className="text-gray-600 mb-4">{insight.description}</p>
                      <div className="flex items-center justify-between mb-3">
                        <span className="text-sm text-gray-500">Confidence: {insight.confidence}%</span>
                        <span className="text-sm text-gray-500">{insight.category}</span>
                      </div>
                      {insight.actionItems && insight.actionItems.length > 0 && (
                        <div className="space-y-2">
                          <p className="text-sm font-medium">Recommended Actions:</p>
                          <ul className="text-sm text-gray-600 space-y-1">
                            {insight.actionItems.map((action, index) => (
                              <li key={index} className="flex items-start gap-2">
                                <Zap className="h-3 w-3 mt-1 text-blue-600 flex-shrink-0" />
                                {action}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </div>
        </TabsContent>

        {/* Risk Analytics Tab */}
        <TabsContent value="risks" className="mt-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Risk Distribution</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-64 flex items-center justify-center bg-gray-50 rounded-lg">
                  <PieChart className="h-16 w-16 text-gray-400" />
                  <span className="ml-2 text-gray-500">Risk distribution chart</span>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Risk Trend</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-64 flex items-center justify-center bg-gray-50 rounded-lg">
                  <LineChart className="h-16 w-16 text-gray-400" />
                  <span className="ml-2 text-gray-500">Risk trend chart</span>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Performance Tab */}
        <TabsContent value="performance" className="mt-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>KPI Performance</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-64 flex items-center justify-center bg-gray-50 rounded-lg">
                  <BarChart className="h-16 w-16 text-gray-400" />
                  <span className="ml-2 text-gray-500">KPI performance chart</span>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Compliance Score</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-64 flex items-center justify-center bg-gray-50 rounded-lg">
                  <Target className="h-16 w-16 text-gray-400" />
                  <span className="ml-2 text-gray-500">Compliance score visualization</span>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Trends Tab */}
        <TabsContent value="trends" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Historical Trends</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-96 flex items-center justify-center bg-gray-50 rounded-lg">
                <TrendingUp className="h-16 w-16 text-gray-400" />
                <span className="ml-2 text-gray-500">Historical trends visualization</span>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Reports Tab */}
        <TabsContent value="reports" className="mt-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Executive Summary</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600 mb-4">Comprehensive overview for leadership</p>
                <Button className="w-full">
                  <Download className="h-4 w-4 mr-2" />
                  Generate Report
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Risk Assessment</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600 mb-4">Detailed risk analysis and recommendations</p>
                <Button className="w-full">
                  <Download className="h-4 w-4 mr-2" />
                  Generate Report
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Compliance Status</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600 mb-4">Current compliance position</p>
                <Button className="w-full">
                  <Download className="h-4 w-4 mr-2" />
                  Generate Report
                </Button>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}