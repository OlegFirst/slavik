import React, { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  Target,
  TrendingUp,
  TrendingDown,
  AlertCircle,
  CheckCircle,
  Clock,
  BarChart3,
  PieChart,
  Activity,
  Filter
} from 'lucide-react'

interface KPIMetric {
  id: string
  name: string
  category: 'operational' | 'strategic' | 'compliance' | 'financial'
  value: number
  target: number
  unit: string
  trend: 'up' | 'down' | 'stable'
  status: 'good' | 'warning' | 'critical'
  description: string
  lastUpdated: string
  frequency: 'daily' | 'weekly' | 'monthly' | 'quarterly'
}

export function KPIMonitoring() {
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  
  const kpiMetrics: KPIMetric[] = [
    {
      id: 'rto-achievement',
      name: 'RTO Achievement Rate',
      category: 'operational',
      value: 87,
      target: 95,
      unit: '%',
      trend: 'down',
      status: 'warning',
      description: 'Percentage of incidents meeting Recovery Time Objective',
      lastUpdated: '2 hours ago',
      frequency: 'daily'
    },
    {
      id: 'rpo-achievement',
      name: 'RPO Achievement Rate',
      category: 'operational',
      value: 94,
      target: 98,
      unit: '%',
      trend: 'up',
      status: 'good',
      description: 'Percentage of incidents meeting Recovery Point Objective',
      lastUpdated: '2 hours ago',
      frequency: 'daily'
    },
    {
      id: 'incident-response-time',
      name: 'Average Incident Response Time',
      category: 'operational',
      value: 23,
      target: 15,
      unit: 'min',
      trend: 'up',
      status: 'critical',
      description: 'Time from incident detection to initial response',
      lastUpdated: '1 hour ago',
      frequency: 'daily'
    },
    {
      id: 'risk-assessment-coverage',
      name: 'Risk Assessment Coverage',
      category: 'strategic',
      value: 89,
      target: 95,
      unit: '%',
      trend: 'up',
      status: 'good',
      description: 'Percentage of critical processes with risk assessments',
      lastUpdated: '1 day ago',
      frequency: 'weekly'
    },
    {
      id: 'bia-completion',
      name: 'BIA Completion Rate',
      category: 'strategic',
      value: 78,
      target: 85,
      unit: '%',
      trend: 'stable',
      status: 'warning',
      description: 'Percentage of critical processes with completed BIA',
      lastUpdated: '3 days ago',
      frequency: 'monthly'
    },
    {
      id: 'training-completion',
      name: 'BCM Training Completion',
      category: 'compliance',
      value: 92,
      target: 95,
      unit: '%',
      trend: 'up',
      status: 'good',
      description: 'Staff completed mandatory BCM training',
      lastUpdated: '1 week ago',
      frequency: 'monthly'
    },
    {
      id: 'exercise-frequency',
      name: 'Exercise Execution Rate',
      category: 'compliance',
      value: 4,
      target: 6,
      unit: 'per quarter',
      trend: 'down',
      status: 'warning',
      description: 'Number of BCM exercises conducted per quarter',
      lastUpdated: '2 weeks ago',
      frequency: 'quarterly'
    },
    {
      id: 'audit-compliance',
      name: 'Audit Compliance Score',
      category: 'compliance',
      value: 96,
      target: 98,
      unit: '%',
      trend: 'stable',
      status: 'good',
      description: 'Compliance with internal and external audit requirements',
      lastUpdated: '1 month ago',
      frequency: 'quarterly'
    },
    {
      id: 'cost-per-incident',
      name: 'Average Cost per Incident',
      category: 'financial',
      value: 45000,
      target: 35000,
      unit: '$',
      trend: 'up',
      status: 'warning',
      description: 'Average total cost impact per business continuity incident',
      lastUpdated: '1 week ago',
      frequency: 'monthly'
    },
    {
      id: 'bcm-investment-roi',
      name: 'BCM Investment ROI',
      category: 'financial',
      value: 340,
      target: 300,
      unit: '%',
      trend: 'up',
      status: 'good',
      description: 'Return on investment for BCM program',
      lastUpdated: '1 month ago',
      frequency: 'quarterly'
    }
  ]

  const categories = [
    { id: 'all', label: 'All KPIs', count: kpiMetrics.length },
    { id: 'operational', label: 'Operational', count: kpiMetrics.filter(k => k.category === 'operational').length },
    { id: 'strategic', label: 'Strategic', count: kpiMetrics.filter(k => k.category === 'strategic').length },
    { id: 'compliance', label: 'Compliance', count: kpiMetrics.filter(k => k.category === 'compliance').length },
    { id: 'financial', label: 'Financial', count: kpiMetrics.filter(k => k.category === 'financial').length }
  ]

  const filteredMetrics = selectedCategory === 'all' 
    ? kpiMetrics 
    : kpiMetrics.filter(metric => metric.category === selectedCategory)

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'good': return 'default'
      case 'warning': return 'secondary'
      case 'critical': return 'destructive'
      default: return 'outline'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'good': return CheckCircle
      case 'warning': return Clock
      case 'critical': return AlertCircle
      default: return Clock
    }
  }

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up': return TrendingUp
      case 'down': return TrendingDown
      case 'stable': return Activity
      default: return Activity
    }
  }

  const getTrendColor = (trend: string, status: string) => {
    if (status === 'critical') return 'text-red-600'
    if (status === 'warning') return 'text-yellow-600'
    
    switch (trend) {
      case 'up': return 'text-green-600'
      case 'down': return 'text-red-600'
      case 'stable': return 'text-gray-600'
      default: return 'text-gray-600'
    }
  }

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'operational': return Activity
      case 'strategic': return Target
      case 'compliance': return CheckCircle
      case 'financial': return BarChart3
      default: return PieChart
    }
  }

  const formatValue = (value: number, unit: string) => {
    if (unit === '$') {
      return `$${value.toLocaleString()}`
    }
    return `${value}${unit}`
  }

  const calculateProgress = (value: number, target: number) => {
    return Math.min((value / target) * 100, 100)
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <Target className="h-6 w-6 text-blue-600" />
            KPI Monitoring Dashboard
          </h2>
          <p className="text-gray-600 mt-1">
            Real-time monitoring of key business continuity performance indicators
          </p>
        </div>
        <Button variant="outline" className="flex items-center gap-2">
          <Filter className="h-4 w-4" />
          Configure KPIs
        </Button>
      </div>

      {/* Category Filters */}
      <div className="flex gap-2 overflow-x-auto pb-2">
        {categories.map((category) => {
          const Icon = getCategoryIcon(category.id)
          return (
            <Button
              key={category.id}
              variant={selectedCategory === category.id ? 'default' : 'outline'}
              size="sm"
              onClick={() => setSelectedCategory(category.id)}
              className="flex items-center gap-2 whitespace-nowrap"
            >
              <Icon className="h-4 w-4" />
              {category.label}
              <Badge variant="secondary" className="ml-1">
                {category.count}
              </Badge>
            </Button>
          )
        })}
      </div>

      <Tabs defaultValue="grid" className="w-full">
        <TabsList>
          <TabsTrigger value="grid">Grid View</TabsTrigger>
          <TabsTrigger value="detailed">Detailed View</TabsTrigger>
          <TabsTrigger value="trends">Trend Analysis</TabsTrigger>
        </TabsList>

        <TabsContent value="grid">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {filteredMetrics.map((metric) => {
              const StatusIcon = getStatusIcon(metric.status)
              const TrendIcon = getTrendIcon(metric.trend)
              const progress = calculateProgress(metric.value, metric.target)

              return (
                <Card key={metric.id}>
                  <CardHeader className="pb-3">
                    <div className="flex items-start justify-between">
                      <div className="space-y-1">
                        <CardTitle className="text-base">{metric.name}</CardTitle>
                        <Badge variant={getStatusColor(metric.status)} className="text-xs">
                          <StatusIcon className="h-3 w-3 mr-1" />
                          {metric.status.toUpperCase()}
                        </Badge>
                      </div>
                      <TrendIcon className={`h-5 w-5 ${getTrendColor(metric.trend, metric.status)}`} />
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div className="flex items-baseline justify-between">
                        <div className="text-2xl font-bold">
                          {formatValue(metric.value, metric.unit)}
                        </div>
                        <div className="text-sm text-gray-500">
                          Target: {formatValue(metric.target, metric.unit)}
                        </div>
                      </div>
                      <Progress value={progress} className="h-2" />
                      <div className="text-xs text-gray-500">
                        <div>{metric.description}</div>
                        <div className="mt-1 flex justify-between">
                          <span>Updated: {metric.lastUpdated}</span>
                          <span className="capitalize">{metric.frequency}</span>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )
            })}
          </div>
        </TabsContent>

        <TabsContent value="detailed">
          <div className="space-y-4">
            {filteredMetrics.map((metric) => {
              const StatusIcon = getStatusIcon(metric.status)
              const TrendIcon = getTrendIcon(metric.trend)
              const progress = calculateProgress(metric.value, metric.target)

              return (
                <Card key={metric.id}>
                  <CardContent className="pt-4">
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center gap-3">
                        <div className="space-y-1">
                          <h3 className="font-medium">{metric.name}</h3>
                          <div className="flex items-center gap-2">
                            <Badge variant="outline" className="text-xs capitalize">
                              {metric.category}
                            </Badge>
                            <Badge variant={getStatusColor(metric.status)} className="text-xs">
                              <StatusIcon className="h-3 w-3 mr-1" />
                              {metric.status}
                            </Badge>
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-2xl font-bold">
                          {formatValue(metric.value, metric.unit)}
                        </div>
                        <div className="text-sm text-gray-500">
                          Target: {formatValue(metric.target, metric.unit)}
                        </div>
                        <div className={`flex items-center justify-end mt-1 text-sm ${getTrendColor(metric.trend, metric.status)}`}>
                          <TrendIcon className="h-3 w-3 mr-1" />
                          {metric.trend}
                        </div>
                      </div>
                    </div>
                    
                    <div className="space-y-3">
                      <Progress value={progress} className="h-3" />
                      <div className="flex justify-between text-xs text-gray-500">
                        <span>{progress.toFixed(1)}% of target</span>
                        <span className="capitalize">Updated {metric.frequency}</span>
                      </div>
                      <p className="text-sm text-gray-600">{metric.description}</p>
                      <div className="text-xs text-gray-400">
                        Last updated: {metric.lastUpdated}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )
            })}
          </div>
        </TabsContent>

        <TabsContent value="trends">
          <div className="grid gap-6 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="h-5 w-5 text-blue-600" />
                  Performance Trends
                </CardTitle>
                <CardDescription>KPI performance over time</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {['good', 'warning', 'critical'].map((status) => {
                    const count = filteredMetrics.filter(m => m.status === status).length
                    const percentage = (count / filteredMetrics.length) * 100
                    
                    return (
                      <div key={status} className="space-y-2">
                        <div className="flex justify-between">
                          <span className="text-sm capitalize">{status} KPIs</span>
                          <span className="text-sm font-medium">{count} ({percentage.toFixed(1)}%)</span>
                        </div>
                        <Progress value={percentage} className="h-2" />
                      </div>
                    )
                  })}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <PieChart className="h-5 w-5 text-green-600" />
                  Category Distribution
                </CardTitle>
                <CardDescription>KPIs by category</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {categories.filter(c => c.id !== 'all').map((category) => {
                    const percentage = (category.count / kpiMetrics.length) * 100
                    
                    return (
                      <div key={category.id} className="space-y-2">
                        <div className="flex justify-between">
                          <span className="text-sm">{category.label}</span>
                          <span className="text-sm font-medium">{category.count} ({percentage.toFixed(1)}%)</span>
                        </div>
                        <Progress value={percentage} className="h-2" />
                      </div>
                    )
                  })}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}
