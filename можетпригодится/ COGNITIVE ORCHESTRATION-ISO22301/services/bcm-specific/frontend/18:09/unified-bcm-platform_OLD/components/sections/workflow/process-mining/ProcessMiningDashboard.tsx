'use client'

import React, { useState, useMemo } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Progress } from '@/components/ui/progress'
import { Alert, AlertDescription } from '@/components/ui/alert'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from '@/components/ui/select'
import {
  useProcessMiningAnalysis,
  useComprehensiveAnalysis,
  calculateProcessHealthScore,
  formatDeviationSeverity,
  formatPatternConfidence,
  type ProcessMiningRequest
} from '@/lib/hooks/useProcessMining'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  ScatterChart,
  Scatter,
  ResponsiveContainer
} from 'recharts'
import {
  Search,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  CheckCircle,
  Clock,
  Users,
  Activity,
  RefreshCw,
  Download,
  Filter,
  BarChart3,
  GitBranch,
  AlertCircle,
  Target
} from 'lucide-react'

interface ProcessMiningDashboardProps {
  processId?: string
  onProcessSelect?: (processId: string) => void
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8']
const SEVERITY_COLORS = {
  critical: '#dc2626',
  high: '#ea580c',
  medium: '#d97706',
  low: '#2563eb'
}

export default function ProcessMiningDashboard({
  processId = '',
  onProcessSelect
}: ProcessMiningDashboardProps) {
  const [selectedProcess, setSelectedProcess] = useState(processId)
  const [analysisTimeframe, setAnalysisTimeframe] = useState(30)
  const [activeTab, setActiveTab] = useState('overview')

  // Process Mining hooks
  const {
    performanceAnalysis,
    patternDiscovery,
    deviationDetection,
    processSummary,
    isLoading,
    isError,
    error
  } = useProcessMiningAnalysis(selectedProcess, analysisTimeframe, !!selectedProcess)

  const comprehensiveAnalysis = useComprehensiveAnalysis()

  // Calculate health score
  const healthScore = useMemo(() => {
    if (!performanceAnalysis.data || !deviationDetection.data) return 0
    return calculateProcessHealthScore(
      performanceAnalysis.data,
      deviationDetection.data,
      patternDiscovery.data
    )
  }, [performanceAnalysis.data, deviationDetection.data, patternDiscovery.data])

  // Performance chart data
  const performanceChartData = useMemo(() => {
    if (!performanceAnalysis.data?.trends) return []
    return performanceAnalysis.data.trends.map(trend => ({
      date: new Date(trend.date).toLocaleDateString(),
      executions: trend.executions,
      avgDuration: Math.round(trend.avg_duration),
      successRate: Math.round(trend.success_rate)
    }))
  }, [performanceAnalysis.data])

  // Pattern frequency data
  const patternChartData = useMemo(() => {
    if (!patternDiscovery.data?.patterns) return []

    const allPatterns = [
      ...patternDiscovery.data.patterns.sequence_patterns.map(p => ({
        name: p.pattern.join(' → '),
        frequency: p.frequency,
        type: 'Sequence',
        confidence: p.confidence
      })),
      ...patternDiscovery.data.patterns.parallel_patterns.map(p => ({
        name: p.pattern.join(' ∥ '),
        frequency: p.frequency,
        type: 'Parallel',
        confidence: p.confidence
      })),
      ...patternDiscovery.data.patterns.loop_patterns.map(p => ({
        name: p.pattern.join(' ↻ '),
        frequency: p.frequency,
        type: 'Loop',
        confidence: p.avg_iterations || 0
      }))
    ]

    return allPatterns.slice(0, 10) // Top 10 patterns
  }, [patternDiscovery.data])

  // Deviation breakdown data
  const deviationBreakdownData = useMemo(() => {
    if (!deviationDetection.data?.severity_breakdown) return []

    const breakdown = deviationDetection.data.severity_breakdown
    return Object.entries(breakdown)
      .filter(([_, count]) => count > 0)
      .map(([severity, count]) => ({
        severity: severity.charAt(0).toUpperCase() + severity.slice(1),
        count,
        fill: SEVERITY_COLORS[severity as keyof typeof SEVERITY_COLORS]
      }))
  }, [deviationDetection.data])

  const handleProcessChange = (newProcessId: string) => {
    setSelectedProcess(newProcessId)
    onProcessSelect?.(newProcessId)
  }

  const handleRunComprehensiveAnalysis = async () => {
    if (!selectedProcess) return

    const request: ProcessMiningRequest = {
      process_id: selectedProcess,
      include_patterns: true,
      include_deviations: true,
      include_performance: true
    }

    try {
      await comprehensiveAnalysis.mutateAsync(request)
      // Refresh all queries
      performanceAnalysis.refetch()
      patternDiscovery.refetch()
      deviationDetection.refetch()
      processSummary.refetch()
    } catch (error) {
      console.error('Comprehensive analysis failed:', error)
    }
  }

  if (!selectedProcess) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5" />
            Process Mining Dashboard
          </CardTitle>
          <CardDescription>
            Select a process to analyze execution patterns, performance metrics, and deviations
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-4">
            <Select onValueChange={handleProcessChange}>
              <SelectTrigger className="w-64">
                <SelectValue placeholder="Select a process to analyze" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="incident-response">Incident Response</SelectItem>
                <SelectItem value="change-management">Change Management</SelectItem>
                <SelectItem value="asset-review">Asset Review Process</SelectItem>
                <SelectItem value="compliance-audit">Compliance Audit</SelectItem>
                <SelectItem value="risk-assessment">Risk Assessment</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (isLoading) {
    return (
      <Card className="w-full">
        <CardContent className="p-6">
          <div className="flex items-center justify-center space-x-2">
            <RefreshCw className="h-4 w-4 animate-spin" />
            <span>Analyzing process data...</span>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (isError) {
    return (
      <Alert variant="destructive" className="w-full">
        <AlertTriangle className="h-4 w-4" />
        <AlertDescription>
          Failed to load process mining data: {error?.message}
        </AlertDescription>
      </Alert>
    )
  }

  return (
    <div className="w-full space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Process Mining Analysis</h2>
          <p className="text-muted-foreground">
            Process: {selectedProcess} • Timeframe: {analysisTimeframe} days
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Select
            value={analysisTimeframe.toString()}
            onValueChange={(value) => setAnalysisTimeframe(parseInt(value))}
          >
            <SelectTrigger className="w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="7">7 days</SelectItem>
              <SelectItem value="30">30 days</SelectItem>
              <SelectItem value="90">90 days</SelectItem>
              <SelectItem value="365">1 year</SelectItem>
            </SelectContent>
          </Select>
          <Button
            onClick={handleRunComprehensiveAnalysis}
            disabled={comprehensiveAnalysis.isPending}
            variant="outline"
          >
            {comprehensiveAnalysis.isPending ? (
              <RefreshCw className="h-4 w-4 animate-spin mr-2" />
            ) : (
              <Activity className="h-4 w-4 mr-2" />
            )}
            Refresh Analysis
          </Button>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Process Health</p>
                <p className="text-2xl font-bold">{healthScore}%</p>
              </div>
              <div className={`p-3 rounded-full ${healthScore >= 80 ? 'bg-green-100' : healthScore >= 60 ? 'bg-yellow-100' : 'bg-red-100'}`}>
                {healthScore >= 80 ? (
                  <CheckCircle className="h-6 w-6 text-green-600" />
                ) : (
                  <AlertTriangle className="h-6 w-6 text-red-600" />
                )}
              </div>
            </div>
            <Progress value={healthScore} className="mt-2" />
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Success Rate</p>
                <p className="text-2xl font-bold">
                  {performanceAnalysis.data?.performance_metrics.success_rate.toFixed(1)}%
                </p>
              </div>
              <Target className="h-6 w-6 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Avg Duration</p>
                <p className="text-2xl font-bold">
                  {performanceAnalysis.data?.performance_metrics.average_duration.toFixed(0)}m
                </p>
              </div>
              <Clock className="h-6 w-6 text-purple-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Deviations</p>
                <p className="text-2xl font-bold">
                  {deviationDetection.data?.total_deviations || 0}
                </p>
              </div>
              <AlertCircle className="h-6 w-6 text-orange-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Analysis Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="patterns">Patterns</TabsTrigger>
          <TabsTrigger value="deviations">Deviations</TabsTrigger>
          <TabsTrigger value="insights">Insights</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Performance Trends */}
            <Card>
              <CardHeader>
                <CardTitle>Performance Trends</CardTitle>
                <CardDescription>Execution metrics over time</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={performanceChartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis yAxisId="left" />
                    <YAxis yAxisId="right" orientation="right" />
                    <Tooltip />
                    <Legend />
                    <Line
                      yAxisId="left"
                      type="monotone"
                      dataKey="avgDuration"
                      stroke="#8884d8"
                      name="Avg Duration (min)"
                    />
                    <Line
                      yAxisId="right"
                      type="monotone"
                      dataKey="successRate"
                      stroke="#82ca9d"
                      name="Success Rate (%)"
                    />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Status Distribution */}
            <Card>
              <CardHeader>
                <CardTitle>Execution Status Distribution</CardTitle>
                <CardDescription>Breakdown of process outcomes</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={Object.entries(performanceAnalysis.data?.performance_metrics.status_distribution || {}).map(([status, count]) => ({
                        name: status.charAt(0).toUpperCase() + status.slice(1),
                        value: count
                      }))}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={120}
                      paddingAngle={5}
                      dataKey="value"
                    >
                      {Object.keys(performanceAnalysis.data?.performance_metrics.status_distribution || {}).map((_, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>

          {/* Recent Insights */}
          <Card>
            <CardHeader>
              <CardTitle>Key Insights</CardTitle>
              <CardDescription>Recent findings from process analysis</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {performanceAnalysis.data?.insights.map((insight, index) => (
                  <div key={index} className="flex items-start gap-2 p-3 bg-muted/50 rounded-lg">
                    <Activity className="h-4 w-4 mt-0.5 text-blue-600" />
                    <span className="text-sm">{insight}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Patterns Tab */}
        <TabsContent value="patterns" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Pattern Frequency Chart */}
            <Card>
              <CardHeader>
                <CardTitle>Discovered Patterns</CardTitle>
                <CardDescription>Most frequent execution patterns</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={patternChartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis
                      dataKey="name"
                      angle={-45}
                      textAnchor="end"
                      height={100}
                    />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="frequency" fill="#8884d8" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Pattern Types */}
            <Card>
              <CardHeader>
                <CardTitle>Pattern Types</CardTitle>
                <CardDescription>Different types of discovered patterns</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {/* Sequence Patterns */}
                  <div>
                    <h4 className="font-medium mb-2 flex items-center gap-2">
                      <GitBranch className="h-4 w-4" />
                      Sequence Patterns ({patternDiscovery.data?.patterns.sequence_patterns.length || 0})
                    </h4>
                    <div className="space-y-2">
                      {patternDiscovery.data?.patterns.sequence_patterns.slice(0, 3).map((pattern, index) => (
                        <div key={index} className="flex items-center justify-between p-2 bg-muted/50 rounded">
                          <span className="text-sm font-mono">{pattern.pattern.join(' → ')}</span>
                          <Badge variant="secondary">
                            {formatPatternConfidence(pattern.confidence)}
                          </Badge>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Parallel Patterns */}
                  <div>
                    <h4 className="font-medium mb-2 flex items-center gap-2">
                      <Activity className="h-4 w-4" />
                      Parallel Patterns ({patternDiscovery.data?.patterns.parallel_patterns.length || 0})
                    </h4>
                    <div className="space-y-2">
                      {patternDiscovery.data?.patterns.parallel_patterns.slice(0, 3).map((pattern, index) => (
                        <div key={index} className="flex items-center justify-between p-2 bg-muted/50 rounded">
                          <span className="text-sm font-mono">{pattern.pattern.join(' ∥ ')}</span>
                          <Badge variant="secondary">
                            {formatPatternConfidence(pattern.confidence)}
                          </Badge>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Loop Patterns */}
                  <div>
                    <h4 className="font-medium mb-2 flex items-center gap-2">
                      <RefreshCw className="h-4 w-4" />
                      Loop Patterns ({patternDiscovery.data?.patterns.loop_patterns.length || 0})
                    </h4>
                    <div className="space-y-2">
                      {patternDiscovery.data?.patterns.loop_patterns.slice(0, 3).map((pattern, index) => (
                        <div key={index} className="flex items-center justify-between p-2 bg-muted/50 rounded">
                          <span className="text-sm font-mono">{pattern.pattern.join(' ↻ ')}</span>
                          <Badge variant="outline">
                            {pattern.frequency} iterations
                          </Badge>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Deviations Tab */}
        <TabsContent value="deviations" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Deviation Severity Breakdown */}
            <Card>
              <CardHeader>
                <CardTitle>Deviation Severity</CardTitle>
                <CardDescription>Distribution of deviation severities</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={deviationBreakdownData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={120}
                      paddingAngle={5}
                      dataKey="count"
                    >
                      {deviationBreakdownData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.fill} />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Deviation Types */}
            <Card>
              <CardHeader>
                <CardTitle>Deviation Types</CardTitle>
                <CardDescription>Count of different deviation types</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {Object.entries(deviationDetection.data?.deviations || {}).map(([type, deviations]) => (
                    <div key={type} className="flex items-center justify-between p-3 border rounded-lg">
                      <div>
                        <h4 className="font-medium capitalize">{type.replace('_', ' ')}</h4>
                        <p className="text-sm text-muted-foreground">
                          {Array.isArray(deviations) ? deviations.length : 0} occurrences
                        </p>
                      </div>
                      <Badge
                        variant={Array.isArray(deviations) && deviations.length > 5 ? "destructive" : "secondary"}
                      >
                        {Array.isArray(deviations) ? deviations.length : 0}
                      </Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Critical Deviations */}
          <Card>
            <CardHeader>
              <CardTitle>Critical Deviations</CardTitle>
              <CardDescription>High-priority deviations requiring attention</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {Object.entries(deviationDetection.data?.deviations || {}).flatMap(([type, deviations]) =>
                  Array.isArray(deviations)
                    ? deviations.filter(d => d.severity === 'critical' || d.severity === 'high')
                    : []
                ).slice(0, 10).map((deviation, index) => {
                  const severityInfo = formatDeviationSeverity(deviation.severity)
                  return (
                    <div key={index} className="flex items-center justify-between p-3 border-l-4 border-red-500 bg-red-50 rounded-r">
                      <div>
                        <div className="flex items-center gap-2">
                          <Badge style={{ backgroundColor: severityInfo.color, color: 'white' }}>
                            {severityInfo.label}
                          </Badge>
                          <span className="font-medium">{deviation.deviation_type}</span>
                        </div>
                        <p className="text-sm text-muted-foreground mt-1">
                          {deviation.description || `Step: ${deviation.step}`}
                        </p>
                      </div>
                      <AlertTriangle className="h-5 w-5 text-red-600" />
                    </div>
                  )
                })}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Insights Tab */}
        <TabsContent value="insights" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Comprehensive Insights</CardTitle>
              <CardDescription>AI-generated insights and recommendations</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {/* Performance Insights */}
                <div>
                  <h4 className="font-medium mb-3 flex items-center gap-2">
                    <TrendingUp className="h-4 w-4" />
                    Performance Insights
                  </h4>
                  <div className="space-y-2">
                    {performanceAnalysis.data?.insights.map((insight, index) => (
                      <div key={index} className="p-3 bg-blue-50 border-l-4 border-blue-500 rounded-r">
                        <p className="text-sm">{insight}</p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Pattern Insights */}
                <div>
                  <h4 className="font-medium mb-3 flex items-center gap-2">
                    <GitBranch className="h-4 w-4" />
                    Pattern Insights
                  </h4>
                  <div className="space-y-2">
                    {patternDiscovery.data?.insights.map((insight, index) => (
                      <div key={index} className="p-3 bg-green-50 border-l-4 border-green-500 rounded-r">
                        <p className="text-sm">{insight}</p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Deviation Insights */}
                <div>
                  <h4 className="font-medium mb-3 flex items-center gap-2">
                    <AlertTriangle className="h-4 w-4" />
                    Deviation Insights
                  </h4>
                  <div className="space-y-2">
                    {deviationDetection.data?.insights.map((insight, index) => (
                      <div key={index} className="p-3 bg-orange-50 border-l-4 border-orange-500 rounded-r">
                        <p className="text-sm">{insight}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}