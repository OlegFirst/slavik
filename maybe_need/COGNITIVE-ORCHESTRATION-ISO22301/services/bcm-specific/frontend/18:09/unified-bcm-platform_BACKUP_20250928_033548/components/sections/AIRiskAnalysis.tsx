'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  Brain,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  Target,
  Lightbulb,
  RefreshCw,
  Eye,
  BarChart3
} from 'lucide-react'

interface RiskPrediction {
  risk_id: string
  risk_name: string
  current_score: number
  predicted_score: number
  confidence: number
  trend: 'increasing' | 'decreasing' | 'stable'
  time_horizon: '30d' | '90d' | '180d'
  impact_areas: string[]
  mitigation_priority: 'high' | 'medium' | 'low'
}

interface MLInsight {
  id: string
  type: 'pattern' | 'anomaly' | 'correlation' | 'prediction'
  title: string
  description: string
  confidence: number
  actionable: boolean
  recommendation?: string
  affected_processes: string[]
}

interface AIRiskAnalysisProps {
  className?: string
}

export function AIRiskAnalysis({ className }: AIRiskAnalysisProps) {
  const [activeView, setActiveView] = useState<'heatmap' | 'predictions' | 'insights'>('heatmap')
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date())

  // Mock ML predictions
  const riskPredictions: RiskPrediction[] = [
    {
      risk_id: 'RISK_001',
      risk_name: 'Cyber Security Breach',
      current_score: 67,
      predicted_score: 78,
      confidence: 89,
      trend: 'increasing',
      time_horizon: '30d',
      impact_areas: ['IT Systems', 'Data Security', 'Operations'],
      mitigation_priority: 'high'
    },
    {
      risk_id: 'RISK_002',
      risk_name: 'Supply Chain Disruption',
      current_score: 45,
      predicted_score: 52,
      confidence: 76,
      trend: 'increasing',
      time_horizon: '90d',
      impact_areas: ['Operations', 'Manufacturing', 'Customer Service'],
      mitigation_priority: 'medium'
    }
  ]

  // Mock ML insights
  const mlInsights: MLInsight[] = [
    {
      id: 'insight_1',
      type: 'pattern',
      title: 'Incident Clustering Detected',
      description: 'ML analysis identified 73% increase in IT-related incidents during Q4.',
      confidence: 91,
      actionable: true,
      recommendation: 'Strengthen remote access security protocols.',
      affected_processes: ['IT Security', 'Remote Work', 'Access Management']
    }
  ]

  const runMLAnalysis = async () => {
    setIsAnalyzing(true)
    await new Promise(resolve => setTimeout(resolve, 3000))
    setLastUpdate(new Date())
    setIsAnalyzing(false)
  }

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'increasing': return <TrendingUp className="h-4 w-4 text-red-500" />
      case 'decreasing': return <TrendingDown className="h-4 w-4 text-green-500" />
      default: return <BarChart3 className="h-4 w-4 text-gray-500" />
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'bg-red-100 text-red-800'
      case 'medium': return 'bg-yellow-100 text-yellow-800'
      case 'low': return 'bg-green-100 text-green-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className={`space-y-6 ${className}`}>
      <div className="flex justify-between items-center">
        <div>
          <h3 className="text-xl font-semibold flex items-center gap-2">
            <Brain className="h-6 w-6 text-purple-600" />
            AI Risk Analysis
          </h3>
          <p className="text-sm text-gray-600 mt-1">
            Machine learning powered risk prediction and pattern analysis
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="text-sm text-gray-600">
            Last update: {lastUpdate.toLocaleTimeString()}
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={runMLAnalysis}
            disabled={isAnalyzing}
          >
            {isAnalyzing ? (
              <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
            ) : (
              <Brain className="h-4 w-4 mr-2" />
            )}
            {isAnalyzing ? 'Analyzing...' : 'Run AI Analysis'}
          </Button>
        </div>
      </div>

      <Tabs value={activeView} onValueChange={(value) => setActiveView(value as any)}>
        <TabsList className="mb-6">
          <TabsTrigger value="heatmap">Risk Heat Map</TabsTrigger>
          <TabsTrigger value="predictions">ML Predictions</TabsTrigger>
          <TabsTrigger value="insights">AI Insights</TabsTrigger>
        </TabsList>

        <TabsContent value="heatmap" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Risk Landscape Heat Map</CardTitle>
              <CardDescription>
                ML-generated visualization of risk distribution across categories
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-64 bg-gradient-to-br from-red-50 to-orange-50 rounded-lg flex items-center justify-center">
                <div className="text-center">
                  <BarChart3 className="h-16 w-16 mx-auto mb-4 text-gray-400" />
                  <h3 className="text-lg font-medium text-gray-700 mb-2">Risk Heat Map</h3>
                  <p className="text-gray-600">Interactive risk visualization will be implemented here</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="predictions" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {riskPredictions.map((prediction) => (
              <Card key={prediction.risk_id} className="cursor-pointer hover:shadow-md transition-shadow">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-base">{prediction.risk_name}</CardTitle>
                    <div className="flex items-center gap-2">
                      {getTrendIcon(prediction.trend)}
                      <Badge className={getPriorityColor(prediction.mitigation_priority)}>
                        {prediction.mitigation_priority}
                      </Badge>
                    </div>
                  </div>
                  <CardDescription>ID: {prediction.risk_id}</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-3">
                    <div>
                      <div className="flex justify-between mb-1">
                        <span className="text-sm text-gray-600">Current Score</span>
                        <span className="text-sm font-medium">{prediction.current_score}</span>
                      </div>
                      <Progress value={prediction.current_score} className="h-2" />
                    </div>

                    <div>
                      <div className="flex justify-between mb-1">
                        <span className="text-sm text-gray-600">Predicted Score ({prediction.time_horizon})</span>
                        <span className="text-sm font-medium">{prediction.predicted_score}</span>
                      </div>
                      <Progress value={prediction.predicted_score} className="h-2" />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">ML Confidence:</span>
                      <span className="font-medium">{prediction.confidence}%</span>
                    </div>
                    <div className="flex flex-wrap gap-1">
                      {prediction.impact_areas.map((area, index) => (
                        <Badge key={index} variant="outline" className="text-xs">
                          {area}
                        </Badge>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="insights" className="space-y-6">
          <div className="space-y-4">
            {mlInsights.map((insight) => (
              <Card key={insight.id}>
                <CardContent className="p-6">
                  <div className="flex items-start gap-4">
                    <div className="p-2 bg-gray-100 rounded-lg">
                      <Target className="h-4 w-4 text-blue-500" />
                    </div>
                    <div className="flex-1 space-y-3">
                      <div className="flex items-center justify-between">
                        <h4 className="font-medium">{insight.title}</h4>
                        <div className="flex items-center gap-2">
                          <Badge variant="outline" className="text-xs">
                            {insight.type}
                          </Badge>
                          <span className="text-sm text-gray-600">
                            {insight.confidence}% confidence
                          </span>
                        </div>
                      </div>

                      <p className="text-sm text-gray-700">{insight.description}</p>

                      {insight.recommendation && (
                        <div className="p-3 bg-blue-50 rounded-lg">
                          <div className="flex items-start gap-2">
                            <Lightbulb className="h-4 w-4 text-blue-600 mt-0.5" />
                            <div>
                              <div className="text-sm font-medium text-blue-900">Recommendation:</div>
                              <div className="text-sm text-blue-800">{insight.recommendation}</div>
                            </div>
                          </div>
                        </div>
                      )}

                      <div className="flex flex-wrap gap-1">
                        {insight.affected_processes.map((process, index) => (
                          <Badge key={index} variant="secondary" className="text-xs">
                            {process}
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
      </Tabs>
    </div>
  )
}