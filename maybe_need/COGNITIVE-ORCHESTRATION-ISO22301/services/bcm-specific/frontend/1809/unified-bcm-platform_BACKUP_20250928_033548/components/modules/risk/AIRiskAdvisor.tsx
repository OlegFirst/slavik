'use client'

import React, { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { Progress } from '@/components/ui/progress'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { cn } from '@/lib/utils'
import {
  Brain,
  Shield,
  TrendingUp,
  AlertTriangle,
  Target,
  Zap,
  Eye,
  MessageSquare,
  BarChart3,
  Activity,
  CheckCircle,
  Clock,
  Settings,
  Sparkles,
  Lightbulb,
  Gauge,
  Users
} from 'lucide-react'
import {
  riskManagementAPI,
  type Risk,
  type AIRiskAdvisor,
  type RiskPrediction,
  type AdvisorPersonality
} from '@/services/risk-management-api'

interface AIRiskAdvisorProps {
  risks: Risk[]
  onAdvisorChange?: (advisorId: string) => void
}

export function AIRiskAdvisor({ risks, onAdvisorChange }: AIRiskAdvisorProps) {
  const [selectedAdvisor, setSelectedAdvisor] = useState<AdvisorPersonality>('balanced')
  const [analysisQuery, setAnalysisQuery] = useState('')
  const [activeTab, setActiveTab] = useState('advisors')
  const queryClient = useQueryClient()

  // Get AI advisor data
  const { data: advisorData, isLoading: advisorLoading } = useQuery({
    queryKey: ['risk', 'ai-advisor', selectedAdvisor],
    queryFn: () => riskManagementAPI.getAIRiskAdvisor(selectedAdvisor),
    refetchInterval: 30000 // Update every 30 seconds
  })

  // Get risk predictions
  const { data: predictions, isLoading: predictionsLoading } = useQuery({
    queryKey: ['risk', 'predictions', selectedAdvisor],
    queryFn: () => riskManagementAPI.getRiskPredictions(selectedAdvisor, risks.map(r => r.id)),
    enabled: risks.length > 0
  })

  // Get advisor performance metrics
  const { data: metrics, isLoading: metricsLoading } = useQuery({
    queryKey: ['risk', 'advisor-metrics', selectedAdvisor],
    queryFn: () => riskManagementAPI.getAdvisorMetrics(selectedAdvisor)
  })

  // AI analysis mutation
  const analysisMutation = useMutation({
    mutationFn: (query: string) => riskManagementAPI.runAIRiskAnalysis(selectedAdvisor, query, risks),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['risk', 'ai-advisor'] })
      setAnalysisQuery('')
    }
  })

  // Advisor configurations
  const advisorConfigs = {
    cautious: {
      name: '⚠️ Cautious Advisor',
      description: 'Conservative risk assessment with maximum security focus',
      color: 'bg-orange-100 text-orange-800',
      personality: 'Focuses on worst-case scenarios and comprehensive mitigation strategies',
      avatar: '⚠️'
    },
    balanced: {
      name: '⚖️ Balanced Advisor',
      description: 'Moderate risk approach balancing security and efficiency',
      color: 'bg-blue-100 text-blue-800',
      personality: 'Provides well-rounded analysis considering multiple perspectives',
      avatar: '⚖️'
    },
    aggressive: {
      name: '🎯 Aggressive Advisor',
      description: 'High-risk tolerance with growth-focused recommendations',
      color: 'bg-red-100 text-red-800',
      personality: 'Emphasizes opportunities and calculated risk-taking',
      avatar: '🎯'
    },
    adaptive: {
      name: '🔄 Adaptive Advisor',
      description: 'Context-sensitive analysis that adapts to changing conditions',
      color: 'bg-purple-100 text-purple-800',
      personality: 'Dynamically adjusts recommendations based on current context',
      avatar: '🔄'
    },
    predictive: {
      name: '🔮 Predictive Advisor',
      description: 'Future-focused analysis with trend prediction capabilities',
      color: 'bg-green-100 text-green-800',
      personality: 'Leverages historical data to predict future risk scenarios',
      avatar: '🔮'
    }
  }

  const handleAdvisorChange = (advisor: AdvisorPersonality) => {
    setSelectedAdvisor(advisor)
    onAdvisorChange?.(advisor)
  }

  const handleAnalysis = () => {
    if (analysisQuery.trim()) {
      analysisMutation.mutate(analysisQuery)
    }
  }

  return (
    <div className="space-y-6">
      {/* AI Advisor Header */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Brain className="h-6 w-6 text-purple-600" />
              <div>
                <CardTitle>AI Risk Advisor</CardTitle>
                <p className="text-sm text-gray-600 mt-1">
                  Intelligent risk analysis with personality-driven insights
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant="outline" className="flex items-center gap-1">
                <Activity className="h-3 w-3" />
                {advisorData?.status || 'Active'}
              </Badge>
              <Badge variant="secondary">
                {metrics?.accuracy_rate ? `${Math.round(metrics.accuracy_rate)}% Accurate` : 'Learning'}
              </Badge>
            </div>
          </div>
        </CardHeader>
      </Card>

      {/* Advisor Selection and Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="advisors">
            <Users className="h-4 w-4 mr-2" />
            Advisors
          </TabsTrigger>
          <TabsTrigger value="predictions">
            <TrendingUp className="h-4 w-4 mr-2" />
            Predictions
          </TabsTrigger>
          <TabsTrigger value="analysis">
            <MessageSquare className="h-4 w-4 mr-2" />
            Analysis
          </TabsTrigger>
          <TabsTrigger value="performance">
            <BarChart3 className="h-4 w-4 mr-2" />
            Performance
          </TabsTrigger>
        </TabsList>

        {/* Advisors Tab */}
        <TabsContent value="advisors" className="mt-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.entries(advisorConfigs).map(([key, config]) => (
              <Card
                key={key}
                className={cn(
                  "cursor-pointer transition-all hover:shadow-md",
                  selectedAdvisor === key && "ring-2 ring-blue-500"
                )}
                onClick={() => handleAdvisorChange(key as AdvisorPersonality)}
              >
                <CardHeader className="pb-3">
                  <div className="flex items-center gap-3">
                    <Avatar className="h-12 w-12">
                      <AvatarFallback className={config.color}>
                        {config.avatar}
                      </AvatarFallback>
                    </Avatar>
                    <div className="flex-1">
                      <h3 className="font-semibold text-sm">{config.name}</h3>
                      <p className="text-xs text-gray-600 mt-1">{config.description}</p>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="pt-0">
                  <p className="text-xs text-gray-500 mb-3">{config.personality}</p>
                  {metrics && selectedAdvisor === key && (
                    <div className="space-y-2">
                      <div className="flex justify-between text-xs">
                        <span>Accuracy Rate</span>
                        <span>{Math.round(metrics.accuracy_rate || 0)}%</span>
                      </div>
                      <Progress value={metrics.accuracy_rate || 0} className="h-2" />
                      <div className="flex justify-between text-xs text-gray-500">
                        <span>{metrics.risks_analyzed || 0} risks analyzed</span>
                        <span>{metrics.predictions_made || 0} predictions</span>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Current Advisor Insights */}
          {advisorData && (
            <Card className="mt-6">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Lightbulb className="h-5 w-5 text-yellow-600" />
                  Current Advisor Insights
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {advisorData.ai_risk_analysis && (
                  <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                    <h4 className="font-medium text-blue-900 mb-2">Latest Risk Analysis</h4>
                    <div
                      className="text-sm text-blue-800"
                      dangerouslySetInnerHTML={{ __html: advisorData.ai_risk_analysis }}
                    />
                  </div>
                )}

                {advisorData.mitigation_recommendations && (
                  <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                    <h4 className="font-medium text-green-900 mb-2">Mitigation Recommendations</h4>
                    <div
                      className="text-sm text-green-800"
                      dangerouslySetInnerHTML={{ __html: advisorData.mitigation_recommendations }}
                    />
                  </div>
                )}

                {advisorData.advisor_wisdom && (
                  <div className="p-4 bg-purple-50 border border-purple-200 rounded-lg">
                    <h4 className="font-medium text-purple-900 mb-2">Advisor Wisdom</h4>
                    <p className="text-sm text-purple-800">{advisorData.advisor_wisdom}</p>
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Predictions Tab */}
        <TabsContent value="predictions" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5 text-blue-600" />
                Risk Predictions & Trends
              </CardTitle>
            </CardHeader>
            <CardContent>
              {predictionsLoading ? (
                <div className="animate-pulse space-y-4">
                  {[1,2,3].map(i => (
                    <div key={i} className="h-4 bg-gray-200 rounded w-full"></div>
                  ))}
                </div>
              ) : predictions?.length ? (
                <div className="space-y-4">
                  {predictions.map((prediction: RiskPrediction) => (
                    <div key={prediction.id} className="p-4 border rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <Target className="h-4 w-4 text-blue-600" />
                          <span className="font-medium">{prediction.risk_title}</span>
                        </div>
                        <Badge
                          variant={prediction.confidence > 0.8 ? "default" : "outline"}
                          className="flex items-center gap-1"
                        >
                          <Gauge className="h-3 w-3" />
                          {Math.round(prediction.confidence * 100)}% confidence
                        </Badge>
                      </div>
                      <p className="text-sm text-gray-600 mb-3">{prediction.description}</p>
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <span className="text-gray-500">Predicted Impact:</span>
                          <span className="ml-2 font-medium">{prediction.predicted_impact}/10</span>
                        </div>
                        <div>
                          <span className="text-gray-500">Timeline:</span>
                          <span className="ml-2 font-medium">{prediction.timeline}</span>
                        </div>
                      </div>
                      {prediction.recommendations && prediction.recommendations.length > 0 && (
                        <div className="mt-3 p-3 bg-gray-50 rounded">
                          <h5 className="text-sm font-medium mb-2">Recommendations:</h5>
                          <ul className="text-sm space-y-1">
                            {prediction.recommendations.map((rec, index) => (
                              <li key={index} className="flex items-start gap-2">
                                <CheckCircle className="h-3 w-3 text-green-600 mt-0.5 flex-shrink-0" />
                                {rec}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <TrendingUp className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                  <p>No predictions available yet. Analyzing risk patterns...</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Analysis Tab */}
        <TabsContent value="analysis" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MessageSquare className="h-5 w-5 text-green-600" />
                Interactive Risk Analysis
              </CardTitle>
              <p className="text-sm text-gray-600">
                Ask the AI advisor specific questions about your risk landscape
              </p>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="analysis-query">Ask your AI Risk Advisor</Label>
                <Textarea
                  id="analysis-query"
                  placeholder="e.g., 'What are the top 3 risks that need immediate attention?' or 'How can we improve our risk mitigation strategy?'"
                  value={analysisQuery}
                  onChange={(e) => setAnalysisQuery(e.target.value)}
                  className="mt-2 min-h-[100px]"
                />
              </div>

              <div className="flex items-center gap-3">
                <Button
                  onClick={handleAnalysis}
                  disabled={!analysisQuery.trim() || analysisMutation.isPending}
                  className="flex items-center gap-2"
                >
                  {analysisMutation.isPending ? (
                    <>
                      <Activity className="h-4 w-4 animate-spin" />
                      Analyzing...
                    </>
                  ) : (
                    <>
                      <Sparkles className="h-4 w-4" />
                      Analyze
                    </>
                  )}
                </Button>

                <Select value={selectedAdvisor} onValueChange={handleAdvisorChange}>
                  <SelectTrigger className="w-48">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {Object.entries(advisorConfigs).map(([key, config]) => (
                      <SelectItem key={key} value={key}>
                        {config.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {analysisMutation.data && (
                <Alert>
                  <Brain className="h-4 w-4" />
                  <AlertDescription>
                    <div className="font-medium mb-2">AI Analysis Complete</div>
                    <div
                      className="text-sm"
                      dangerouslySetInnerHTML={{ __html: analysisMutation.data.analysis }}
                    />
                  </AlertDescription>
                </Alert>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Performance Tab */}
        <TabsContent value="performance" className="mt-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="h-5 w-5 text-blue-600" />
                  Advisor Performance
                </CardTitle>
              </CardHeader>
              <CardContent>
                {metricsLoading ? (
                  <div className="animate-pulse space-y-4">
                    <div className="h-4 bg-gray-200 rounded w-full"></div>
                    <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                  </div>
                ) : metrics ? (
                  <div className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div className="text-center">
                        <div className="text-2xl font-bold text-blue-600">{metrics.risks_analyzed}</div>
                        <div className="text-sm text-gray-500">Risks Analyzed</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-green-600">{metrics.predictions_made}</div>
                        <div className="text-sm text-gray-500">Predictions Made</div>
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between text-sm mb-2">
                        <span>Accuracy Rate</span>
                        <span>{Math.round(metrics.accuracy_rate)}%</span>
                      </div>
                      <Progress value={metrics.accuracy_rate} className="h-3" />
                    </div>
                  </div>
                ) : (
                  <p className="text-gray-500">No performance data available</p>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Settings className="h-5 w-5 text-gray-600" />
                  Advisor Configuration
                </CardTitle>
              </CardHeader>
              <CardContent>
                {advisorData ? (
                  <div className="space-y-3">
                    <div className="flex justify-between text-sm">
                      <span>FAIR Analysis:</span>
                      <Badge variant={advisorData.fair_analysis_enabled ? "default" : "outline"}>
                        {advisorData.fair_analysis_enabled ? "Enabled" : "Disabled"}
                      </Badge>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Monte Carlo Iterations:</span>
                      <span className="font-medium">{advisorData.monte_carlo_simulations?.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Personality:</span>
                      <Badge variant="outline">{advisorConfigs[selectedAdvisor]?.name}</Badge>
                    </div>
                  </div>
                ) : (
                  <p className="text-gray-500">Loading configuration...</p>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}