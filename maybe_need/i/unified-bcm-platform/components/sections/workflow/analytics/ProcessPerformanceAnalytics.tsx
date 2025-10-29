'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Alert, AlertDescription } from '@/components/ui/alert'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell
} from 'recharts'
import {
  TrendingUp,
  TrendingDown,
  Clock,
  CheckCircle,
  AlertTriangle,
  Download,
  RefreshCw,
  Filter
} from 'lucide-react'
import { useProcessPerformance, useGenerateAnalyticsReport } from '@/lib/hooks/useWorkflow'
import type { ProcessPerformanceMetrics } from '@/lib/services/workflow-api'

interface ProcessPerformanceAnalyticsProps {
  filters?: {
    processIds?: string[]
    department?: string
    category?: string
    dateRange?: { from: string; to: string }
  }
  onFiltersChange?: (filters: any) => void
}

const PERFORMANCE_COLORS = {
  excellent: '#10b981', // green-500
  good: '#f59e0b',      // amber-500
  warning: '#f97316',   // orange-500
  critical: '#ef4444'   // red-500
}

export function ProcessPerformanceAnalytics({
  filters,
  onFiltersChange
}: ProcessPerformanceAnalyticsProps) {
  const [selectedMetric, setSelectedMetric] = useState<'efficiency' | 'executionTime' | 'successRate'>('efficiency')
  const [viewMode, setViewMode] = useState<'chart' | 'table'>('chart')

  const {
    data: performanceData,
    isLoading,
    error,
    refetch
  } = useProcessPerformance(filters)

  const generateReport = useGenerateAnalyticsReport()

  // Helper functions
  const getPerformanceColor = (efficiency: number) => {
    if (efficiency >= 90) return PERFORMANCE_COLORS.excellent
    if (efficiency >= 75) return PERFORMANCE_COLORS.good
    if (efficiency >= 60) return PERFORMANCE_COLORS.warning
    return PERFORMANCE_COLORS.critical
  }

  const getPerformanceBadge = (efficiency: number) => {
    if (efficiency >= 90) return { variant: 'default' as const, text: 'Excellent' }
    if (efficiency >= 75) return { variant: 'secondary' as const, text: 'Good' }
    if (efficiency >= 60) return { variant: 'outline' as const, text: 'Warning' }
    return { variant: 'destructive' as const, text: 'Critical' }
  }

  const formatExecutionTime = (minutes: number) => {
    if (minutes < 60) return `${minutes}m`
    const hours = Math.floor(minutes / 60)
    const remainingMinutes = minutes % 60
    return remainingMinutes > 0 ? `${hours}h ${remainingMinutes}m` : `${hours}h`
  }

  // Chart data preparation
  const chartData = performanceData?.map(process => ({
    name: process.processName,
    efficiency: process.efficiency,
    executionTime: process.averageExecutionTime,
    successRate: process.successRate,
    slaCompliance: process.slaCompliance
  })) || []

  const aggregatedStats = performanceData ? {
    avgEfficiency: Math.round(performanceData.reduce((sum, p) => sum + p.efficiency, 0) / performanceData.length),
    avgExecutionTime: Math.round(performanceData.reduce((sum, p) => sum + p.averageExecutionTime, 0) / performanceData.length),
    avgSuccessRate: Math.round(performanceData.reduce((sum, p) => sum + p.successRate, 0) / performanceData.length),
    totalExecutions: performanceData.reduce((sum, p) => sum + p.executionCount, 0)
  } : null

  const handleExportReport = async () => {
    if (!performanceData?.length) return

    try {
      await generateReport.mutateAsync({
        processIds: performanceData.map(p => p.processId),
        metrics: ['efficiency', 'executionTime', 'successRate', 'slaCompliance'],
        format: 'pdf',
        dateRange: filters?.dateRange || {
          from: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
          to: new Date().toISOString()
        }
      })
    } catch (error) {
      console.error('Export failed:', error)
    }
  }

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <RefreshCw className="h-5 w-5 animate-spin" />
            Loading Performance Analytics
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[1, 2, 3].map(i => (
              <div key={i} className="h-16 bg-gray-200 rounded animate-pulse" />
            ))}
          </div>
        </CardContent>
      </Card>
    )
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertTriangle className="h-4 w-4" />
        <AlertDescription>
          Failed to load performance analytics: {error.message}
          <Button variant="outline" size="sm" onClick={() => refetch()} className="ml-2">
            Retry
          </Button>
        </AlertDescription>
      </Alert>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header with controls */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold">Process Performance Analytics</h3>
          <p className="text-sm text-gray-600">
            Analyze execution efficiency, timing, and success rates across your workflows
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Select value={selectedMetric} onValueChange={(value: any) => setSelectedMetric(value)}>
            <SelectTrigger className="w-40">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="efficiency">Efficiency</SelectItem>
              <SelectItem value="executionTime">Execution Time</SelectItem>
              <SelectItem value="successRate">Success Rate</SelectItem>
            </SelectContent>
          </Select>

          <Select value={viewMode} onValueChange={(value: any) => setViewMode(value)}>
            <SelectTrigger className="w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="chart">Chart</SelectItem>
              <SelectItem value="table">Table</SelectItem>
            </SelectContent>
          </Select>

          <Button variant="outline" size="sm" onClick={() => refetch()}>
            <RefreshCw className="h-4 w-4" />
          </Button>

          <Button
            variant="outline"
            size="sm"
            onClick={handleExportReport}
            disabled={generateReport.isPending}
          >
            <Download className="h-4 w-4 mr-1" />
            Export
          </Button>
        </div>
      </div>

      {/* Summary Stats */}
      {aggregatedStats && (
        <div className="grid grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Avg Efficiency</p>
                  <p className="text-2xl font-bold">{aggregatedStats.avgEfficiency}%</p>
                </div>
                <TrendingUp className="h-8 w-8 text-green-500" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Avg Execution Time</p>
                  <p className="text-2xl font-bold">{formatExecutionTime(aggregatedStats.avgExecutionTime)}</p>
                </div>
                <Clock className="h-8 w-8 text-blue-500" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Avg Success Rate</p>
                  <p className="text-2xl font-bold">{aggregatedStats.avgSuccessRate}%</p>
                </div>
                <CheckCircle className="h-8 w-8 text-green-500" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Total Executions</p>
                  <p className="text-2xl font-bold">{aggregatedStats.totalExecutions.toLocaleString()}</p>
                </div>
                <TrendingUp className="h-8 w-8 text-purple-500" />
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Main Content */}
      {viewMode === 'chart' ? (
        <Card>
          <CardHeader>
            <CardTitle>Performance Visualization</CardTitle>
            <CardDescription>
              {selectedMetric === 'efficiency' && 'Process efficiency scores (higher is better)'}
              {selectedMetric === 'executionTime' && 'Average execution time in minutes'}
              {selectedMetric === 'successRate' && 'Success rate percentage'}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-96">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    dataKey="name"
                    angle={-45}
                    textAnchor="end"
                    height={80}
                  />
                  <YAxis />
                  <Tooltip
                    formatter={(value, name) => [
                      selectedMetric === 'executionTime'
                        ? formatExecutionTime(value as number)
                        : `${value}${selectedMetric === 'efficiency' || selectedMetric === 'successRate' ? '%' : ''}`,
                      name
                    ]}
                  />
                  <Bar
                    dataKey={selectedMetric}
                    fill={PERFORMANCE_COLORS.good}
                    radius={[4, 4, 0, 0]}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardHeader>
            <CardTitle>Performance Details</CardTitle>
            <CardDescription>
              Detailed performance metrics for each process
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left p-2">Process</th>
                    <th className="text-left p-2">Efficiency</th>
                    <th className="text-left p-2">Execution Time</th>
                    <th className="text-left p-2">Success Rate</th>
                    <th className="text-left p-2">SLA Compliance</th>
                    <th className="text-left p-2">Executions</th>
                  </tr>
                </thead>
                <tbody>
                  {performanceData?.map((process) => (
                    <tr key={process.processId} className="border-b hover:bg-gray-50">
                      <td className="p-2">
                        <div>
                          <p className="font-medium">{process.processName}</p>
                          <p className="text-xs text-gray-500">{process.processId}</p>
                        </div>
                      </td>
                      <td className="p-2">
                        <Badge {...getPerformanceBadge(process.efficiency)}>
                          {process.efficiency}%
                        </Badge>
                      </td>
                      <td className="p-2">{formatExecutionTime(process.averageExecutionTime)}</td>
                      <td className="p-2">
                        <span className={`font-medium ${process.successRate >= 95 ? 'text-green-600' : process.successRate >= 90 ? 'text-yellow-600' : 'text-red-600'}`}>
                          {process.successRate}%
                        </span>
                      </td>
                      <td className="p-2">
                        <span className={`font-medium ${process.slaCompliance >= 95 ? 'text-green-600' : process.slaCompliance >= 90 ? 'text-yellow-600' : 'text-red-600'}`}>
                          {process.slaCompliance}%
                        </span>
                      </td>
                      <td className="p-2">{process.executionCount.toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}