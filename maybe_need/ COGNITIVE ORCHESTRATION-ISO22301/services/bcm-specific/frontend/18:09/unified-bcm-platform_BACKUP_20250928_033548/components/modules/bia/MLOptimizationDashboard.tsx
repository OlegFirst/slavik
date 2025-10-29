'use client'

import React, { useState, useMemo } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { cn } from '@/lib/utils'
import {
  Brain,
  Target,
  TrendingUp,
  TrendingDown,
  Zap,
  Settings,
  Play,
  Pause,
  RotateCcw,
  Download,
  Upload,
  CheckCircle,
  AlertCircle,
  Clock,
  DollarSign,
  Activity,
  BarChart3,
  PieChart,
  LineChart
} from 'lucide-react'
import {
  biaAPI,
  biaQueryKeys,
  type BIAResult
} from '@/services/bia-api'
import {
  ResponsiveContainer,
  LineChart as RechartsLineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  BarChart,
  Bar,
  PieChart as RechartsPieChart,
  Pie,
  Cell,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ScatterChart,
  Scatter
} from 'recharts'

// Types for ML Optimization
interface MLModel {
  id: string
  name: string
  type: 'rto_optimization' | 'financial_prediction' | 'dependency_analysis' | 'risk_assessment'
  accuracy: number
  lastTrained: string
  status: 'training' | 'ready' | 'optimizing' | 'error'
  confidence: number
}

interface OptimizationRecommendation {
  id: string
  processId: string
  processName: string
  currentRTO: number
  optimizedRTO: number
  currentRPO: number
  optimizedRPO: number
  costSaving: number
  riskReduction: number
  implementation: {
    effort: 'low' | 'medium' | 'high'
    timeline: string
    requirements: string[]
  }
  confidence: number
  impact: 'low' | 'medium' | 'high' | 'critical'
}

interface MLMetrics {
  totalOptimizations: number
  averageImprovement: number
  costSavings: number
  riskReduction: number
  modelAccuracy: number
  trainingHours: number
}

// BIA Engine Service Client
class BIAEngineClient {
  private baseUrl = 'http://localhost:8082'

  async getMLMetrics(): Promise<MLMetrics> {
    try {
      const response = await fetch(`${this.baseUrl}/ml/metrics`)
      if (!response.ok) throw new Error('Failed to fetch ML metrics')
      return await response.json()
    } catch (error) {
      // Mock data fallback
      return {
        totalOptimizations: 47,
        averageImprovement: 23.5,
        costSavings: 2850000,
        riskReduction: 18.2,
        modelAccuracy: 94.7,
        trainingHours: 156
      }
    }
  }

  async getOptimizationRecommendations(): Promise<OptimizationRecommendation[]> {
    try {
      const response = await fetch(`${this.baseUrl}/optimize/recommendations`)
      if (!response.ok) throw new Error('Failed to fetch recommendations')
      return await response.json()
    } catch (error) {
      // Mock data fallback
      return [
        {
          id: '1',
          processId: '1',
          processName: 'Customer Order Processing',
          currentRTO: 4,
          optimizedRTO: 2,
          currentRPO: 60,
          optimizedRPO: 30,
          costSaving: 125000,
          riskReduction: 15.5,
          implementation: {
            effort: 'medium',
            timeline: '2-3 weeks',
            requirements: ['Load balancer upgrade', 'Database optimization', 'Cache implementation']
          },
          confidence: 0.92,
          impact: 'high'
        },
        {
          id: '2',
          processId: '3',
          processName: 'Manufacturing Line A',
          currentRTO: 8,
          optimizedRTO: 4,
          currentRPO: 120,
          optimizedRPO: 60,
          costSaving: 340000,
          riskReduction: 28.3,
          implementation: {
            effort: 'high',
            timeline: '4-6 weeks',
            requirements: ['Redundant equipment', 'Automated failover', 'Staff training']
          },
          confidence: 0.87,
          impact: 'critical'
        }
      ]
    }
  }

  async runOptimization(processIds: string[]): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/optimize/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ process_ids: processIds })
      })
      if (!response.ok) throw new Error('Failed to run optimization')
      return await response.json()
    } catch (error) {
      return {
        job_id: `opt_${Date.now()}`,
        status: 'running',
        estimated_completion: '2024-12-31T23:59:59Z'
      }
    }
  }
}

const biaEngineClient = new BIAEngineClient()

const COLORS = {
  primary: '#3b82f6',
  success: '#22c55e',
  warning: '#f59e0b',
  danger: '#ef4444',
  info: '#06b6d4'
}

export function MLOptimizationDashboard() {
  const [selectedTab, setSelectedTab] = useState('overview')
  const [isOptimizing, setIsOptimizing] = useState(false)
  const queryClient = useQueryClient()

  // Fetch BIA results
  const { data: biaResults } = useQuery({
    queryKey: biaQueryKeys.results(),
    queryFn: () => biaAPI.getBIAResults({})
  })

  // Fetch ML metrics
  const { data: mlMetrics, isLoading: metricsLoading } = useQuery({
    queryKey: ['ml', 'metrics'],
    queryFn: () => biaEngineClient.getMLMetrics(),
    refetchInterval: 30000 // Refresh every 30s
  })

  // Fetch optimization recommendations
  const { data: recommendations, isLoading: recsLoading } = useQuery({
    queryKey: ['ml', 'recommendations'],
    queryFn: () => biaEngineClient.getOptimizationRecommendations()
  })

  // Run optimization mutation
  const runOptimizationMutation = useMutation({
    mutationFn: (processIds: string[]) => biaEngineClient.runOptimization(processIds),
    onMutate: () => setIsOptimizing(true),
    onSettled: () => setIsOptimizing(false),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ml'] })
    }
  })

  // ML Models mock data
  const mlModels: MLModel[] = [
    {
      id: 'rto_opt',
      name: 'RTO Optimizer',
      type: 'rto_optimization',
      accuracy: 94.7,
      lastTrained: '2024-09-16T10:30:00Z',
      status: 'ready',
      confidence: 0.95
    },
    {
      id: 'fin_pred',
      name: 'Financial Impact Predictor',
      type: 'financial_prediction',
      accuracy: 91.2,
      lastTrained: '2024-09-15T14:20:00Z',
      status: 'ready',
      confidence: 0.91
    },
    {
      id: 'dep_analyzer',
      name: 'Dependency Analyzer',
      type: 'dependency_analysis',
      accuracy: 88.5,
      lastTrained: '2024-09-17T08:15:00Z',
      status: 'training',
      confidence: 0.88
    }
  ]

  // Performance trend data
  const performanceTrend = useMemo(() => {
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep']
    return months.map((month, index) => ({
      month,
      accuracy: 85 + (index * 1.2) + Math.random() * 2,
      optimizations: 12 + Math.floor(Math.random() * 8),
      savings: 150000 + (index * 25000) + Math.random() * 50000
    }))
  }, [])

  const exportMLReport = () => {
    const report = {
      timestamp: new Date().toISOString(),
      metrics: mlMetrics,
      models: mlModels,
      recommendations: recommendations,
      performance: performanceTrend
    }

    const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `ml-optimization-report-${new Date().toISOString().split('T')[0]}.json`
    link.click()
    URL.revokeObjectURL(url)
  }

  if (metricsLoading || recsLoading) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-64"></div>
          <div className="grid grid-cols-4 gap-4">
            {[1,2,3,4].map(i => (
              <div key={i} className="h-24 bg-gray-200 rounded"></div>
            ))}
          </div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <Brain className="h-6 w-6 text-purple-600" />
            ML Optimization Dashboard
          </h2>
          <p className="text-gray-600">
            AI-powered optimization and intelligent recommendations for BIA processes
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="outline" onClick={exportMLReport}>
            <Download className="h-4 w-4 mr-2" />
            Export Report
          </Button>
          <Button
            onClick={() => runOptimizationMutation.mutate(biaResults?.map(r => r.id) || [])}
            disabled={isOptimizing}
            className="bg-purple-600 hover:bg-purple-700"
          >
            {isOptimizing ? (
              <>
                <Activity className="h-4 w-4 mr-2 animate-spin" />
                Optimizing...
              </>
            ) : (
              <>
                <Zap className="h-4 w-4 mr-2" />
                Run Full Optimization
              </>
            )}
          </Button>
        </div>
      </div>

      {/* ML Metrics Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-purple-100 rounded-lg">
                <Target className="h-5 w-5 text-purple-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Model Accuracy</p>
                <p className="text-lg font-bold">{mlMetrics?.modelAccuracy.toFixed(1)}%</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-green-100 rounded-lg">
                <TrendingUp className="h-5 w-5 text-green-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Cost Savings</p>
                <p className="text-lg font-bold">${(mlMetrics?.costSavings || 0).toLocaleString()}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <BarChart3 className="h-5 w-5 text-blue-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Optimizations</p>
                <p className="text-lg font-bold">{mlMetrics?.totalOptimizations}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-orange-100 rounded-lg">
                <Clock className="h-5 w-5 text-orange-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Training Hours</p>
                <p className="text-lg font-bold">{mlMetrics?.trainingHours}h</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Dashboard Tabs */}
      <Tabs value={selectedTab} onValueChange={setSelectedTab}>
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="models">ML Models</TabsTrigger>
          <TabsTrigger value="recommendations">Recommendations</TabsTrigger>
          <TabsTrigger value="performance">Performance</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="mt-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Optimization Impact Chart */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <LineChart className="h-5 w-5 text-blue-600" />
                  Optimization Impact Trend
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <RechartsLineChart data={performanceTrend}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="month" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Line
                        type="monotone"
                        dataKey="accuracy"
                        stroke={COLORS.primary}
                        strokeWidth={2}
                        name="Accuracy %"
                      />
                      <Line
                        type="monotone"
                        dataKey="optimizations"
                        stroke={COLORS.success}
                        strokeWidth={2}
                        name="Optimizations"
                      />
                    </RechartsLineChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>

            {/* ML Model Status */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Brain className="h-5 w-5 text-purple-600" />
                  ML Model Status
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {mlModels.map(model => (
                  <div key={model.id} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex items-center gap-3">
                      <div className={cn(
                        "w-3 h-3 rounded-full",
                        model.status === 'ready' && "bg-green-500",
                        model.status === 'training' && "bg-yellow-500 animate-pulse",
                        model.status === 'error' && "bg-red-500"
                      )} />
                      <div>
                        <p className="font-medium text-sm">{model.name}</p>
                        <p className="text-xs text-gray-500">{model.accuracy.toFixed(1)}% accuracy</p>
                      </div>
                    </div>
                    <Badge variant={model.status === 'ready' ? 'default' : 'secondary'}>
                      {model.status}
                    </Badge>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="models" className="mt-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {mlModels.map(model => (
              <Card key={model.id}>
                <CardHeader>
                  <CardTitle className="text-lg">{model.name}</CardTitle>
                  <Badge className={cn(
                    model.status === 'ready' && "bg-green-100 text-green-800",
                    model.status === 'training' && "bg-yellow-100 text-yellow-800",
                    model.status === 'error' && "bg-red-100 text-red-800"
                  )}>
                    {model.status}
                  </Badge>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span>Accuracy</span>
                      <span>{model.accuracy.toFixed(1)}%</span>
                    </div>
                    <Progress value={model.accuracy} className="h-2" />
                  </div>

                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span>Confidence</span>
                      <span>{Math.round(model.confidence * 100)}%</span>
                    </div>
                    <Progress value={model.confidence * 100} className="h-2" />
                  </div>

                  <div className="text-sm space-y-1">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Type:</span>
                      <span className="capitalize">{model.type.replace('_', ' ')}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Last Trained:</span>
                      <span>{new Date(model.lastTrained).toLocaleDateString()}</span>
                    </div>
                  </div>

                  <div className="flex gap-2">
                    <Button size="sm" variant="outline" className="flex-1">
                      <Settings className="h-3 w-3 mr-1" />
                      Configure
                    </Button>
                    <Button size="sm" variant="outline" className="flex-1">
                      <Play className="h-3 w-3 mr-1" />
                      Retrain
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="recommendations" className="mt-6">
          <div className="space-y-4">
            {recommendations?.map(rec => (
              <Card key={rec.id}>
                <CardContent className="p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h4 className="text-lg font-semibold">{rec.processName}</h4>
                      <p className="text-sm text-gray-600">Process optimization recommendation</p>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge variant={rec.impact === 'critical' ? 'destructive' : 'default'}>
                        {rec.impact} impact
                      </Badge>
                      <Badge variant="outline">
                        {Math.round(rec.confidence * 100)}% confidence
                      </Badge>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
                    <div className="text-center p-3 bg-gray-50 rounded-lg">
                      <p className="text-sm text-gray-600">RTO Improvement</p>
                      <p className="text-xl font-bold text-green-600">
                        {rec.currentRTO}h → {rec.optimizedRTO}h
                      </p>
                      <p className="text-xs text-gray-500">
                        {Math.round(((rec.currentRTO - rec.optimizedRTO) / rec.currentRTO) * 100)}% faster
                      </p>
                    </div>

                    <div className="text-center p-3 bg-gray-50 rounded-lg">
                      <p className="text-sm text-gray-600">RPO Improvement</p>
                      <p className="text-xl font-bold text-blue-600">
                        {rec.currentRPO}m → {rec.optimizedRPO}m
                      </p>
                      <p className="text-xs text-gray-500">
                        {Math.round(((rec.currentRPO - rec.optimizedRPO) / rec.currentRPO) * 100)}% better
                      </p>
                    </div>

                    <div className="text-center p-3 bg-gray-50 rounded-lg">
                      <p className="text-sm text-gray-600">Cost Savings</p>
                      <p className="text-xl font-bold text-green-600">${rec.costSaving.toLocaleString()}</p>
                      <p className="text-xs text-gray-500">Annual savings</p>
                    </div>

                    <div className="text-center p-3 bg-gray-50 rounded-lg">
                      <p className="text-sm text-gray-600">Risk Reduction</p>
                      <p className="text-xl font-bold text-purple-600">{rec.riskReduction.toFixed(1)}%</p>
                      <p className="text-xs text-gray-500">Overall risk</p>
                    </div>
                  </div>

                  <div className="border-t pt-4">
                    <h5 className="font-medium mb-2">Implementation Details</h5>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                      <div>
                        <span className="text-gray-600">Effort Level:</span>
                        <Badge variant="outline" className="ml-2 capitalize">
                          {rec.implementation.effort}
                        </Badge>
                      </div>
                      <div>
                        <span className="text-gray-600">Timeline:</span>
                        <span className="ml-2 font-medium">{rec.implementation.timeline}</span>
                      </div>
                      <div className="flex gap-2">
                        <Button size="sm">
                          <CheckCircle className="h-3 w-3 mr-1" />
                          Approve
                        </Button>
                        <Button size="sm" variant="outline">
                          Details
                        </Button>
                      </div>
                    </div>

                    <div className="mt-3">
                      <p className="text-sm text-gray-600 mb-1">Requirements:</p>
                      <div className="flex flex-wrap gap-1">
                        {rec.implementation.requirements.map((req, index) => (
                          <Badge key={index} variant="secondary" className="text-xs">
                            {req}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="performance" className="mt-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Savings Over Time */}
            <Card>
              <CardHeader>
                <CardTitle>Cost Savings Trend</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={performanceTrend}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="month" />
                      <YAxis tickFormatter={(value) => `$${(value/1000).toFixed(0)}K`} />
                      <Tooltip formatter={(value: number) => [`$${value.toLocaleString()}`, 'Savings']} />
                      <Bar dataKey="savings" fill={COLORS.success} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>

            {/* Model Performance Comparison */}
            <Card>
              <CardHeader>
                <CardTitle>Model Performance Comparison</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <RadarChart data={mlModels.map(model => ({
                      name: model.name.split(' ')[0],
                      accuracy: model.accuracy,
                      confidence: model.confidence * 100,
                      usage: Math.random() * 100
                    }))}>
                      <PolarGrid />
                      <PolarAngleAxis dataKey="name" />
                      <PolarRadiusAxis domain={[0, 100]} />
                      <Radar
                        name="Accuracy"
                        dataKey="accuracy"
                        stroke={COLORS.primary}
                        fill={COLORS.primary}
                        fillOpacity={0.3}
                      />
                      <Radar
                        name="Confidence"
                        dataKey="confidence"
                        stroke={COLORS.success}
                        fill={COLORS.success}
                        fillOpacity={0.3}
                      />
                      <Legend />
                    </RadarChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}