'use client'

import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Alert, AlertDescription } from '@/components/ui/alert'
import {
  Bot,
  TrendingUp,
  AlertTriangle,
  Target,
  Zap,
  Users,
  Clock,
  DollarSign,
  Brain,
  Activity,
  Gauge,
  Lightbulb,
  CheckCircle,
  XCircle,
  BarChart3,
  PieChart,
  ArrowUp,
  ArrowDown,
  Minus
} from 'lucide-react'

interface ProcessData {
  processId: string
  processName: string
  complexity: 'simple' | 'medium' | 'complex'
  resourceCount: number
  stakeholderCount: number
  stepCount: number
  executionTimeMinutes: number
  successRate: number
  department: string
  category: string
}

interface OptimizationPrediction {
  processId: string
  predictions: {
    execution_time: number
    bottleneck_probability: number
    resource_optimization: {
      current_allocation: { resources: number; estimated_time: number; estimated_cost: number }
      recommended_allocation: { resources: number; estimated_time: number; estimated_cost: number }
      expected_improvement: { time_saved_minutes: number; cost_saved: number; efficiency_gain: number }
    }
  }
  recommendations: Array<{
    type: string
    priority: string
    title: string
    description: string
    impact: string
    effort: string
  }>
  confidenceScore: number
  estimatedImprovement: {
    time_reduction: number
    efficiency_gain: number
  }
}

interface BottleneckAnalysis {
  processId: string
  bottlenecks: Array<{
    type: string
    severity: string
    description: string
    impact_score: number
  }>
  severity: string
  recommendations: string[]
  estimatedImpact: {
    time_delay: number
    cost_impact: number
  }
}

interface AnomalyDetection {
  processId: string
  anomalies: Array<{
    type: string
    description: string
    severity: string
  }>
  riskLevel: string
  recommendations: string[]
}

const mockProcesses: ProcessData[] = [
  {
    processId: 'proc_001',
    processName: 'Emergency Response Protocol',
    complexity: 'complex',
    resourceCount: 4,
    stakeholderCount: 18,
    stepCount: 12,
    executionTimeMinutes: 165,
    successRate: 0.78,
    department: 'Operations',
    category: 'emergency'
  },
  {
    processId: 'proc_002',
    processName: 'Incident Management',
    complexity: 'medium',
    resourceCount: 6,
    stakeholderCount: 12,
    stepCount: 8,
    executionTimeMinutes: 95,
    successRate: 0.92,
    department: 'IT',
    category: 'incident'
  },
  {
    processId: 'proc_003',
    processName: 'Business Continuity Plan Review',
    complexity: 'complex',
    resourceCount: 3,
    stakeholderCount: 25,
    stepCount: 15,
    executionTimeMinutes: 280,
    successRate: 0.65,
    department: 'BCM',
    category: 'bcm'
  }
]

export default function AIWorkflowOptimizer() {
  const [selectedProcess, setSelectedProcess] = useState<ProcessData>(mockProcesses[0])
  const [optimization, setOptimization] = useState<OptimizationPrediction | null>(null)
  const [bottleneckAnalysis, setBottleneckAnalysis] = useState<BottleneckAnalysis | null>(null)
  const [anomalyDetection, setAnomalyDetection] = useState<AnomalyDetection | null>(null)
  const [loading, setLoading] = useState(false)
  const [activeTab, setActiveTab] = useState('optimization')

  useEffect(() => {
    if (selectedProcess) {
      runAIAnalysis()
    }
  }, [selectedProcess])

  const runAIAnalysis = async () => {
    setLoading(true)

    try {
      // Simulate API calls
      await new Promise(resolve => setTimeout(resolve, 1500))

      // Mock optimization data
      const mockOptimization: OptimizationPrediction = {
        processId: selectedProcess.processId,
        predictions: {
          execution_time: selectedProcess.executionTimeMinutes * 0.85, // 15% improvement
          bottleneck_probability: selectedProcess.resourceCount < 5 ? 0.75 : 0.35,
          resource_optimization: {
            current_allocation: {
              resources: selectedProcess.resourceCount,
              estimated_time: selectedProcess.executionTimeMinutes,
              estimated_cost: selectedProcess.resourceCount * 50 + selectedProcess.executionTimeMinutes * 2
            },
            recommended_allocation: {
              resources: Math.max(selectedProcess.resourceCount, Math.min(8, selectedProcess.stepCount * 0.6)),
              estimated_time: selectedProcess.executionTimeMinutes * 0.8,
              estimated_cost: Math.max(selectedProcess.resourceCount, Math.min(8, selectedProcess.stepCount * 0.6)) * 50 + selectedProcess.executionTimeMinutes * 0.8 * 2
            },
            expected_improvement: {
              time_saved_minutes: selectedProcess.executionTimeMinutes * 0.2,
              cost_saved: (selectedProcess.resourceCount * 50 + selectedProcess.executionTimeMinutes * 2) * 0.15,
              efficiency_gain: 22.5
            }
          }
        },
        recommendations: [
          {
            type: 'resource_allocation',
            priority: 'high',
            title: 'Optimize Resource Allocation',
            description: `Increase resources from ${selectedProcess.resourceCount} to ${Math.max(selectedProcess.resourceCount, Math.min(8, selectedProcess.stepCount * 0.6))} members for better efficiency`,
            impact: 'high',
            effort: 'medium'
          },
          {
            type: 'process_automation',
            priority: 'medium',
            title: 'Automate Routine Steps',
            description: 'Identify and automate 3-4 routine steps to reduce manual effort',
            impact: 'medium',
            effort: 'high'
          },
          {
            type: 'stakeholder_optimization',
            priority: 'medium',
            title: 'Streamline Communication',
            description: 'Reduce stakeholder coordination overhead with automated notifications',
            impact: 'medium',
            effort: 'low'
          }
        ],
        confidenceScore: 0.87,
        estimatedImprovement: {
          time_reduction: selectedProcess.executionTimeMinutes * 0.15,
          efficiency_gain: 18.7
        }
      }

      const mockBottlenecks: BottleneckAnalysis = {
        processId: selectedProcess.processId,
        bottlenecks: [
          {
            type: 'resource_shortage',
            severity: selectedProcess.resourceCount < 5 ? 'high' : 'low',
            description: `Resource count (${selectedProcess.resourceCount}) may cause delays`,
            impact_score: selectedProcess.resourceCount < 5 ? 0.8 : 0.2
          },
          {
            type: 'communication_overhead',
            severity: selectedProcess.stakeholderCount > 15 ? 'medium' : 'low',
            description: `High stakeholder count (${selectedProcess.stakeholderCount}) may slow coordination`,
            impact_score: selectedProcess.stakeholderCount > 15 ? 0.6 : 0.3
          }
        ],
        severity: selectedProcess.resourceCount < 5 || selectedProcess.stakeholderCount > 15 ? 'high' : 'medium',
        recommendations: [
          'Increase resource allocation by 2-3 team members',
          'Implement stakeholder hierarchy with designated leads',
          'Use automated notification systems to reduce manual coordination'
        ],
        estimatedImpact: {
          time_delay: (selectedProcess.resourceCount < 5 ? 45 : 15),
          cost_impact: (selectedProcess.resourceCount < 5 ? 850 : 250)
        }
      }

      const mockAnomalies: AnomalyDetection = {
        processId: selectedProcess.processId,
        anomalies: selectedProcess.successRate < 0.8 ? [
          {
            type: 'success_rate_anomaly',
            description: `Success rate (${(selectedProcess.successRate * 100).toFixed(1)}%) is unusually low`,
            severity: 'high'
          },
          {
            type: 'execution_time_anomaly',
            description: `Execution time (${selectedProcess.executionTimeMinutes}m) exceeds expected baseline`,
            severity: 'medium'
          }
        ] : [],
        riskLevel: selectedProcess.successRate < 0.8 ? 'high' : 'low',
        recommendations: selectedProcess.successRate < 0.8 ? [
          'Review process documentation and training materials',
          'Implement additional quality checks',
          'Investigate recent process changes or environmental factors'
        ] : ['Process operating within normal parameters']
      }

      setOptimization(mockOptimization)
      setBottleneckAnalysis(mockBottlenecks)
      setAnomalyDetection(mockAnomalies)

    } catch (error) {
      console.error('Error running AI analysis:', error)
    } finally {
      setLoading(false)
    }
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high': return 'bg-red-100 text-red-700 border-red-200'
      case 'medium': return 'bg-yellow-100 text-yellow-700 border-yellow-200'
      case 'low': return 'bg-green-100 text-green-700 border-green-200'
      default: return 'bg-gray-100 text-gray-700 border-gray-200'
    }
  }

  const getPriorityIcon = (priority: string) => {
    switch (priority) {
      case 'high': return <ArrowUp className="h-4 w-4 text-red-500" />
      case 'medium': return <Minus className="h-4 w-4 text-yellow-500" />
      case 'low': return <ArrowDown className="h-4 w-4 text-green-500" />
      default: return <Minus className="h-4 w-4 text-gray-500" />
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">AI analyzing workflow...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-blue-600 rounded-lg p-6 text-white">
        <div className="flex items-center gap-3 mb-4">
          <Bot className="h-8 w-8" />
          <div>
            <h2 className="text-2xl font-bold">AI Workflow Optimizer</h2>
            <p className="text-purple-100">ML-powered process optimization and prediction</p>
          </div>
        </div>

        <div className="grid grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold">{optimization?.confidenceScore ? (optimization.confidenceScore * 100).toFixed(1) : 87}%</div>
            <div className="text-purple-100 text-sm">AI Confidence</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold">{optimization?.estimatedImprovement?.efficiency_gain?.toFixed(1) || 18.7}%</div>
            <div className="text-purple-100 text-sm">Efficiency Gain</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold">{optimization?.estimatedImprovement?.time_reduction?.toFixed(0) || 25}m</div>
            <div className="text-purple-100 text-sm">Time Saved</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold">{anomalyDetection?.anomalies?.length || 0}</div>
            <div className="text-purple-100 text-sm">Anomalies</div>
          </div>
        </div>
      </div>

      {/* Process Selection */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="h-5 w-5" />
            Process Selection
          </CardTitle>
          <CardDescription>Select a process for AI-powered optimization analysis</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4 items-center">
            <Select value={selectedProcess.processId} onValueChange={(value) => {
              const process = mockProcesses.find(p => p.processId === value)
              if (process) setSelectedProcess(process)
            }}>
              <SelectTrigger className="w-64">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {mockProcesses.map(process => (
                  <SelectItem key={process.processId} value={process.processId}>
                    {process.processName}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            <Button onClick={runAIAnalysis} className="flex items-center gap-2">
              <Brain className="h-4 w-4" />
              Run AI Analysis
            </Button>
          </div>

          {/* Process Info */}
          <div className="grid grid-cols-4 gap-4 mt-4 p-4 bg-gray-50 rounded-lg">
            <div className="text-center">
              <div className="text-lg font-semibold">{selectedProcess.resourceCount}</div>
              <div className="text-sm text-gray-600">Resources</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-semibold">{selectedProcess.stepCount}</div>
              <div className="text-sm text-gray-600">Steps</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-semibold">{selectedProcess.executionTimeMinutes}m</div>
              <div className="text-sm text-gray-600">Avg Time</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-semibold">{(selectedProcess.successRate * 100).toFixed(1)}%</div>
              <div className="text-sm text-gray-600">Success Rate</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Analysis Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="optimization">Optimization</TabsTrigger>
          <TabsTrigger value="bottlenecks">Bottlenecks</TabsTrigger>
          <TabsTrigger value="anomalies">Anomalies</TabsTrigger>
          <TabsTrigger value="insights">AI Insights</TabsTrigger>
        </TabsList>

        <TabsContent value="optimization" className="space-y-6">
          {optimization && (
            <>
              {/* Resource Optimization */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Users className="h-5 w-5" />
                    Resource Optimization
                  </CardTitle>
                  <CardDescription>AI-recommended resource allocation improvements</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 gap-6">
                    <div className="space-y-4">
                      <h4 className="font-semibold">Current Allocation</h4>
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span>Resources:</span>
                          <span className="font-medium">{optimization.predictions.resource_optimization.current_allocation.resources}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Est. Time:</span>
                          <span className="font-medium">{optimization.predictions.resource_optimization.current_allocation.estimated_time.toFixed(0)}m</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Est. Cost:</span>
                          <span className="font-medium">${optimization.predictions.resource_optimization.current_allocation.estimated_cost.toFixed(0)}</span>
                        </div>
                      </div>
                    </div>

                    <div className="space-y-4">
                      <h4 className="font-semibold">Recommended Allocation</h4>
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span>Resources:</span>
                          <span className="font-medium text-green-600">{optimization.predictions.resource_optimization.recommended_allocation.resources}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Est. Time:</span>
                          <span className="font-medium text-green-600">{optimization.predictions.resource_optimization.recommended_allocation.estimated_time.toFixed(0)}m</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Est. Cost:</span>
                          <span className="font-medium text-green-600">${optimization.predictions.resource_optimization.recommended_allocation.estimated_cost.toFixed(0)}</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="mt-6 p-4 bg-green-50 rounded-lg">
                    <h5 className="font-semibold text-green-800 mb-2">Expected Improvement</h5>
                    <div className="grid grid-cols-3 gap-4 text-sm">
                      <div className="text-center">
                        <div className="text-lg font-bold text-green-600">{optimization.predictions.resource_optimization.expected_improvement.time_saved_minutes.toFixed(0)}m</div>
                        <div className="text-green-700">Time Saved</div>
                      </div>
                      <div className="text-center">
                        <div className="text-lg font-bold text-green-600">${optimization.predictions.resource_optimization.expected_improvement.cost_saved.toFixed(0)}</div>
                        <div className="text-green-700">Cost Saved</div>
                      </div>
                      <div className="text-center">
                        <div className="text-lg font-bold text-green-600">{optimization.predictions.resource_optimization.expected_improvement.efficiency_gain.toFixed(1)}%</div>
                        <div className="text-green-700">Efficiency Gain</div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* AI Recommendations */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Lightbulb className="h-5 w-5" />
                    AI Recommendations
                  </CardTitle>
                  <CardDescription>Prioritized optimization recommendations</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {optimization.recommendations.map((rec, index) => (
                      <div key={index} className="border rounded-lg p-4">
                        <div className="flex items-start justify-between mb-2">
                          <div className="flex items-center gap-2">
                            {getPriorityIcon(rec.priority)}
                            <h5 className="font-semibold">{rec.title}</h5>
                          </div>
                          <div className="flex gap-2">
                            <Badge className={getSeverityColor(rec.priority)}>
                              {rec.priority} priority
                            </Badge>
                            <Badge variant="outline">{rec.impact} impact</Badge>
                          </div>
                        </div>
                        <p className="text-gray-700 mb-2">{rec.description}</p>
                        <div className="text-sm text-gray-600">
                          Effort required: {rec.effort}
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </>
          )}
        </TabsContent>

        <TabsContent value="bottlenecks" className="space-y-6">
          {bottleneckAnalysis && (
            <>
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <AlertTriangle className="h-5 w-5" />
                    Bottleneck Analysis
                  </CardTitle>
                  <CardDescription>AI-identified process bottlenecks and impact assessment</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="mb-6">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="font-semibold">Overall Severity:</span>
                      <Badge className={getSeverityColor(bottleneckAnalysis.severity)}>
                        {bottleneckAnalysis.severity.toUpperCase()}
                      </Badge>
                    </div>
                    <div className="grid grid-cols-2 gap-4 mt-4">
                      <div className="text-center p-3 bg-red-50 rounded-lg">
                        <div className="text-lg font-bold text-red-600">{bottleneckAnalysis.estimatedImpact.time_delay}m</div>
                        <div className="text-red-700 text-sm">Estimated Delay</div>
                      </div>
                      <div className="text-center p-3 bg-red-50 rounded-lg">
                        <div className="text-lg font-bold text-red-600">${bottleneckAnalysis.estimatedImpact.cost_impact}</div>
                        <div className="text-red-700 text-sm">Cost Impact</div>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <h5 className="font-semibold">Identified Bottlenecks</h5>
                    {bottleneckAnalysis.bottlenecks.map((bottleneck, index) => (
                      <div key={index} className="border rounded-lg p-4">
                        <div className="flex items-center justify-between mb-2">
                          <h6 className="font-medium capitalize">{bottleneck.type.replace('_', ' ')}</h6>
                          <Badge className={getSeverityColor(bottleneck.severity)}>
                            {bottleneck.severity}
                          </Badge>
                        </div>
                        <p className="text-gray-700 mb-2">{bottleneck.description}</p>
                        <div className="flex items-center gap-2">
                          <span className="text-sm text-gray-600">Impact Score:</span>
                          <Progress value={bottleneck.impact_score * 100} className="flex-1" />
                          <span className="text-sm font-medium">{(bottleneck.impact_score * 100).toFixed(0)}%</span>
                        </div>
                      </div>
                    ))}
                  </div>

                  <div className="mt-6">
                    <h5 className="font-semibold mb-3">Recommendations</h5>
                    <div className="space-y-2">
                      {bottleneckAnalysis.recommendations.map((rec, index) => (
                        <div key={index} className="flex items-center gap-2">
                          <CheckCircle className="h-4 w-4 text-green-500" />
                          <span className="text-sm">{rec}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>
            </>
          )}
        </TabsContent>

        <TabsContent value="anomalies" className="space-y-6">
          {anomalyDetection && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Activity className="h-5 w-5" />
                  Anomaly Detection
                </CardTitle>
                <CardDescription>AI-powered detection of unusual process patterns</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="mb-6">
                  <div className="flex items-center gap-2 mb-4">
                    <span className="font-semibold">Risk Level:</span>
                    <Badge className={getSeverityColor(anomalyDetection.riskLevel)}>
                      {anomalyDetection.riskLevel.toUpperCase()}
                    </Badge>
                  </div>
                </div>

                {anomalyDetection.anomalies.length > 0 ? (
                  <div className="space-y-4">
                    <h5 className="font-semibold">Detected Anomalies</h5>
                    {anomalyDetection.anomalies.map((anomaly, index) => (
                      <Alert key={index} className={anomaly.severity === 'high' ? 'border-red-200 bg-red-50' : 'border-yellow-200 bg-yellow-50'}>
                        <AlertTriangle className="h-4 w-4" />
                        <AlertDescription>
                          <div className="flex items-center justify-between">
                            <span>{anomaly.description}</span>
                            <Badge className={getSeverityColor(anomaly.severity)}>
                              {anomaly.severity}
                            </Badge>
                          </div>
                        </AlertDescription>
                      </Alert>
                    ))}

                    <div className="mt-6">
                      <h5 className="font-semibold mb-3">Recommended Actions</h5>
                      <div className="space-y-2">
                        {anomalyDetection.recommendations.map((rec, index) => (
                          <div key={index} className="flex items-center gap-2">
                            <CheckCircle className="h-4 w-4 text-green-500" />
                            <span className="text-sm">{rec}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <CheckCircle className="h-16 w-16 text-green-500 mx-auto mb-4" />
                    <h4 className="text-lg font-semibold text-green-800 mb-2">No Anomalies Detected</h4>
                    <p className="text-green-600">Process is operating within normal parameters</p>
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="insights" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Performance Insights */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="h-5 w-5" />
                  Performance Insights
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span>Execution Efficiency</span>
                    <div className="flex items-center gap-2">
                      <Progress value={selectedProcess.successRate * 100} className="w-20" />
                      <span className="text-sm font-medium">{(selectedProcess.successRate * 100).toFixed(1)}%</span>
                    </div>
                  </div>

                  <div className="flex items-center justify-between">
                    <span>Resource Utilization</span>
                    <div className="flex items-center gap-2">
                      <Progress value={(selectedProcess.resourceCount / 10) * 100} className="w-20" />
                      <span className="text-sm font-medium">{selectedProcess.resourceCount}/10</span>
                    </div>
                  </div>

                  <div className="flex items-center justify-between">
                    <span>Process Complexity</span>
                    <Badge className={selectedProcess.complexity === 'complex' ? 'bg-red-100 text-red-700' :
                                      selectedProcess.complexity === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                                      'bg-green-100 text-green-700'}>
                      {selectedProcess.complexity}
                    </Badge>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* AI Model Status */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Brain className="h-5 w-5" />
                  AI Model Status
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span>Performance Predictor</span>
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                      <span className="text-sm">87% accuracy</span>
                    </div>
                  </div>

                  <div className="flex items-center justify-between">
                    <span>Bottleneck Detector</span>
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                      <span className="text-sm">91% accuracy</span>
                    </div>
                  </div>

                  <div className="flex items-center justify-between">
                    <span>Anomaly Detector</span>
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                      <span className="text-sm">85% accuracy</span>
                    </div>
                  </div>

                  <div className="pt-2 border-t">
                    <Button variant="outline" size="sm" className="w-full">
                      <Brain className="h-4 w-4 mr-2" />
                      Retrain Models
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* AI Recommendations Summary */}
          <Card>
            <CardHeader>
              <CardTitle>AI-Powered Recommendations Summary</CardTitle>
              <CardDescription>Key insights and action items from AI analysis</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="text-center p-4 bg-blue-50 rounded-lg">
                  <TrendingUp className="h-8 w-8 text-blue-600 mx-auto mb-2" />
                  <div className="font-semibold text-blue-800">Optimization Potential</div>
                  <div className="text-sm text-blue-600">18.7% efficiency improvement possible</div>
                </div>

                <div className="text-center p-4 bg-yellow-50 rounded-lg">
                  <AlertTriangle className="h-8 w-8 text-yellow-600 mx-auto mb-2" />
                  <div className="font-semibold text-yellow-800">Risk Areas</div>
                  <div className="text-sm text-yellow-600">Resource allocation needs attention</div>
                </div>

                <div className="text-center p-4 bg-green-50 rounded-lg">
                  <Target className="h-8 w-8 text-green-600 mx-auto mb-2" />
                  <div className="font-semibold text-green-800">Quick Wins</div>
                  <div className="text-sm text-green-600">3 high-impact optimizations identified</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}