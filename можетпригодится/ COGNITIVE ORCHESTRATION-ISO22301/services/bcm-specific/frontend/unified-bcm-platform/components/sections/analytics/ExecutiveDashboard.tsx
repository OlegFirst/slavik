import React from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { 
  TrendingUp, 
  TrendingDown,
  Crown,
  Target,
  AlertTriangle,
  CheckCircle,
  Clock,
  DollarSign,
  Calendar
} from 'lucide-react'

interface ExecutiveMetric {
  title: string
  value: string
  target: string
  progress: number
  status: 'on-track' | 'at-risk' | 'off-track'
  trend: 'up' | 'down' | 'stable'
  changePercent: number
}

export function ExecutiveDashboard() {
  const executiveMetrics: ExecutiveMetric[] = [
    {
      title: 'Business Continuity Maturity',
      value: '4.2/5.0',
      target: '4.5/5.0',
      progress: 84,
      status: 'on-track',
      trend: 'up',
      changePercent: 7.3
    },
    {
      title: 'Risk Mitigation Coverage',
      value: '89%',
      target: '95%',
      progress: 94,
      status: 'on-track',
      trend: 'up',
      changePercent: 4.2
    },
    {
      title: 'Incident Response Readiness',
      value: '92%',
      target: '90%',
      progress: 102,
      status: 'on-track',
      trend: 'stable',
      changePercent: 0.8
    },
    {
      title: 'Recovery Time Objective Achievement',
      value: '87%',
      target: '95%',
      progress: 92,
      status: 'at-risk',
      trend: 'down',
      changePercent: -2.1
    },
    {
      title: 'Staff BCM Competency',
      value: '78%',
      target: '85%',
      progress: 92,
      status: 'at-risk',
      trend: 'up',
      changePercent: 3.5
    },
    {
      title: 'Regulatory Compliance Score',
      value: '94%',
      target: '100%',
      progress: 94,
      status: 'on-track',
      trend: 'up',
      changePercent: 6.7
    }
  ]

  const strategicInitiatives = [
    {
      id: 1,
      title: 'Digital Transformation BCM Initiative',
      status: 'in-progress',
      progress: 68,
      priority: 'high',
      dueDate: '2024-06-30',
      owner: 'CTO Office',
      description: 'Modernize BCM processes with AI and automation capabilities'
    },
    {
      id: 2,
      title: 'Supply Chain Resilience Program',
      status: 'planning',
      progress: 25,
      priority: 'high',
      dueDate: '2024-09-15',
      owner: 'Supply Chain',
      description: 'Enhance supply chain risk management and alternative sourcing'
    },
    {
      id: 3,
      title: 'Cyber Resilience Enhancement',
      status: 'in-progress',
      progress: 82,
      priority: 'critical',
      dueDate: '2024-03-31',
      owner: 'CISO Office',
      description: 'Strengthen cybersecurity incident response and recovery capabilities'
    },
    {
      id: 4,
      title: 'Third-Party Risk Management Upgrade',
      status: 'completed',
      progress: 100,
      priority: 'medium',
      dueDate: '2024-01-15',
      owner: 'Risk Management',
      description: 'Implement comprehensive third-party risk assessment framework'
    }
  ]

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'on-track': return 'default'
      case 'at-risk': return 'secondary'
      case 'off-track': return 'destructive'
      default: return 'outline'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'on-track': return CheckCircle
      case 'at-risk': return Clock
      case 'off-track': return AlertTriangle
      default: return Clock
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical': return 'destructive'
      case 'high': return 'secondary'
      case 'medium': return 'default'
      case 'low': return 'outline'
      default: return 'outline'
    }
  }

  const getInitiativeStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'default'
      case 'in-progress': return 'secondary'
      case 'planning': return 'outline'
      case 'on-hold': return 'destructive'
      default: return 'outline'
    }
  }

  return (
    <div className="space-y-6">
      {/* Executive Summary */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Crown className="h-5 w-5 text-yellow-600" />
            <CardTitle>Executive Summary</CardTitle>
          </div>
          <CardDescription>High-level BCM performance overview for leadership</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-4">
              <div className="bg-green-50 p-4 rounded-lg">
                <h4 className="font-medium text-green-900 mb-2">Strengths</h4>
                <ul className="text-sm text-green-800 space-y-1">
                  <li>• Incident response readiness exceeds target (92% vs 90%)</li>
                  <li>• Regulatory compliance maintaining high standards (94%)</li>
                  <li>• Digital transformation initiative progressing well</li>
                </ul>
              </div>
              <div className="bg-yellow-50 p-4 rounded-lg">
                <h4 className="font-medium text-yellow-900 mb-2">Areas for Attention</h4>
                <ul className="text-sm text-yellow-800 space-y-1">
                  <li>• Recovery time objectives need improvement (87% vs 95% target)</li>
                  <li>• Staff BCM competency requires focused training</li>
                  <li>• Supply chain resilience program needs acceleration</li>
                </ul>
              </div>
            </div>
            <div className="space-y-4">
              <div className="bg-blue-50 p-4 rounded-lg">
                <h4 className="font-medium text-blue-900 mb-2">Key Actions Recommended</h4>
                <ul className="text-sm text-blue-800 space-y-1">
                  <li>• Accelerate RTO improvement initiatives</li>
                  <li>• Implement enhanced BCM training program</li>
                  <li>• Review and optimize incident recovery processes</li>
                </ul>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg text-center">
                <div className="text-2xl font-bold text-gray-700 mb-1">Q4 2024</div>
                <div className="text-sm text-gray-600">Strategic Planning Cycle</div>
                <Button variant="outline" size="sm" className="mt-2">
                  <Calendar className="h-3 w-3 mr-1" />
                  Schedule Review
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Strategic KPIs - остальной код продолжается... */}
      <div>
        <h3 className="text-lg font-semibold mb-4">Strategic KPIs</h3>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {executiveMetrics.map((metric, index) => {
            const StatusIcon = getStatusIcon(metric.status)
            const TrendIcon = metric.trend === 'up' ? TrendingUp : 
                             metric.trend === 'down' ? TrendingDown : Target

            return (
              <Card key={index}>
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-sm font-medium">{metric.title}</CardTitle>
                    <Badge variant={getStatusColor(metric.status)}>
                      <StatusIcon className="h-3 w-3 mr-1" />
                      {metric.status.replace('-', ' ')}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="flex items-baseline justify-between">
                      <div className="text-2xl font-bold">{metric.value}</div>
                      <div className="text-sm text-gray-500">Target: {metric.target}</div>
                    </div>
                    <Progress value={metric.progress} className="h-2" />
                    <div className="flex items-center justify-between text-xs">
                      <div className="flex items-center text-gray-600">
                        <TrendIcon className="h-3 w-3 mr-1" />
                        {metric.changePercent > 0 ? '+' : ''}{metric.changePercent}%
                      </div>
                      <div className="text-gray-500">{metric.progress}% of target</div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )
          })}
        </div>
      </div>

      {/* Investment Overview */}
      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <DollarSign className="h-5 w-5 text-green-600" />
              BCM Investment Analysis
            </CardTitle>
            <CardDescription>Financial investment in BCM capabilities</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4 text-center">
                <div>
                  <div className="text-lg font-bold text-blue-600">$2.4M</div>
                  <div className="text-xs text-gray-600">Annual BCM Budget</div>
                </div>
                <div>
                  <div className="text-lg font-bold text-green-600">$8.7M</div>
                  <div className="text-xs text-gray-600">Risk Avoidance Value</div>
                </div>
              </div>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Technology & Tools</span>
                  <span>45%</span>
                </div>
                <Progress value={45} className="h-2" />
                <div className="flex justify-between text-sm">
                  <span>Training & Development</span>
                  <span>25%</span>
                </div>
                <Progress value={25} className="h-2" />
                <div className="flex justify-between text-sm">
                  <span>Process Improvement</span>
                  <span>20%</span>
                </div>
                <Progress value={20} className="h-2" />
                <div className="flex justify-between text-sm">
                  <span>External Services</span>
                  <span>10%</span>
                </div>
                <Progress value={10} className="h-2" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Target className="h-5 w-5 text-purple-600" />
              Maturity Roadmap
            </CardTitle>
            <CardDescription>BCM maturity progression timeline</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center gap-3">
                <div className="w-3 h-3 rounded-full bg-green-500"></div>
                <div className="flex-1">
                  <div className="font-medium text-sm">Level 3: Defined (Current)</div>
                  <div className="text-xs text-gray-500">Standardized BCM processes</div>
                </div>
                <div className="text-xs text-gray-400">Q4 2023</div>
              </div>
              <div className="flex items-center gap-3">
                <div className="w-3 h-3 rounded-full bg-blue-500"></div>
                <div className="flex-1">
                  <div className="font-medium text-sm">Level 4: Managed (Target)</div>
                  <div className="text-xs text-gray-500">Metrics-driven optimization</div>
                </div>
                <div className="text-xs text-gray-400">Q2 2024</div>
              </div>
              <div className="flex items-center gap-3">
                <div className="w-3 h-3 rounded-full bg-gray-300"></div>
                <div className="flex-1">
                  <div className="font-medium text-sm">Level 5: Optimizing (Future)</div>
                  <div className="text-xs text-gray-500">Continuous improvement culture</div>
                </div>
                <div className="text-xs text-gray-400">Q4 2024</div>
              </div>
            </div>
            <div className="mt-4 pt-4 border-t">
              <div className="text-center">
                <div className="text-sm text-gray-600 mb-2">Overall Maturity Progress</div>
                <Progress value={72} className="mb-2" />
                <div className="text-xs text-gray-500">72% to Level 4 (Managed)</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
