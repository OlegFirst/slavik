import React from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { 
  BarChart3, 
  TrendingUp, 
  TrendingDown, 
  AlertTriangle, 
  CheckCircle,
  Clock,
  Users,
  Shield,
  Zap
} from 'lucide-react'

interface MetricCardProps {
  title: string
  value: string | number
  change: number
  icon: React.ElementType
  description?: string
}

function MetricCard({ title, value, change, icon: Icon, description }: MetricCardProps) {
  const isPositive = change > 0
  const changeColor = isPositive ? 'text-green-600' : 'text-red-600'
  const TrendIcon = isPositive ? TrendingUp : TrendingDown

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        <Icon className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        <div className={`flex items-center text-xs ${changeColor}`}>
          <TrendIcon className="h-3 w-3 mr-1" />
          {Math.abs(change)}% from last month
        </div>
        {description && (
          <p className="text-xs text-muted-foreground mt-2">{description}</p>
        )}
      </CardContent>
    </Card>
  )
}

export function AnalyticsOverview() {
  const keyMetrics = [
    {
      title: 'BCM Maturity Score',
      value: '85%',
      change: 5.2,
      icon: Shield,
      description: 'Overall business continuity readiness'
    },
    {
      title: 'Risk Coverage',
      value: '92%',
      change: 3.1,
      icon: BarChart3,
      description: 'Percentage of identified risks with mitigation plans'
    },
    {
      title: 'Active Incidents',
      value: 3,
      change: -25,
      icon: AlertTriangle,
      description: 'Currently active incidents requiring attention'
    },
    {
      title: 'Recovery Time',
      value: '2.4h',
      change: -15.3,
      icon: Clock,
      description: 'Average incident recovery time'
    },
    {
      title: 'Staff Trained',
      value: '847',
      change: 12.7,
      icon: Users,
      description: 'Employees completed BCM training'
    },
    {
      title: 'Automation Level',
      value: '78%',
      change: 8.9,
      icon: Zap,
      description: 'Processes with automation coverage'
    }
  ]

  const recentInsights = [
    {
      id: 1,
      type: 'improvement',
      title: 'Risk Assessment Completion Rate Improved',
      description: 'Monthly risk assessments completion increased by 23% compared to last quarter.',
      timestamp: '2 hours ago',
      severity: 'low'
    },
    {
      id: 2,
      type: 'alert',
      title: 'Incident Response Time Threshold Exceeded',
      description: 'Average response time for P1 incidents exceeded target SLA by 15 minutes.',
      timestamp: '4 hours ago',
      severity: 'medium'
    },
    {
      id: 3,
      type: 'success',
      title: 'Training Compliance Target Achieved',
      description: 'Q4 BCM training compliance reached 95%, exceeding the 90% target.',
      timestamp: '1 day ago',
      severity: 'low'
    },
    {
      id: 4,
      type: 'trend',
      title: 'Business Impact Analysis Coverage Expanding',
      description: 'BIA coverage increased to 78% of critical business processes.',
      timestamp: '2 days ago',
      severity: 'low'
    }
  ]

  const getInsightIcon = (type: string) => {
    switch (type) {
      case 'improvement': return TrendingUp
      case 'alert': return AlertTriangle
      case 'success': return CheckCircle
      case 'trend': return BarChart3
      default: return BarChart3
    }
  }

  const getInsightColor = (severity: string) => {
    switch (severity) {
      case 'high': return 'destructive'
      case 'medium': return 'secondary'
      case 'low': return 'default'
      default: return 'outline'
    }
  }

  return (
    <div className="space-y-6">
      {/* Key Metrics */}
      <div>
        <h3 className="text-lg font-semibold mb-4">Key BCM Metrics</h3>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {keyMetrics.map((metric, index) => (
            <MetricCard key={index} {...metric} />
          ))}
        </div>
      </div>

      {/* Performance Overview */}
      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>BCM Health Score Trend</CardTitle>
            <CardDescription>Overall business continuity health over time</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm">Risk Management</span>
                  <span className="text-sm font-medium">92%</span>
                </div>
                <Progress value={92} className="h-2" />
              </div>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm">Incident Response</span>
                  <span className="text-sm font-medium">88%</span>
                </div>
                <Progress value={88} className="h-2" />
              </div>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm">Business Impact Analysis</span>
                  <span className="text-sm font-medium">78%</span>
                </div>
                <Progress value={78} className="h-2" />
              </div>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm">Recovery Planning</span>
                  <span className="text-sm font-medium">85%</span>
                </div>
                <Progress value={85} className="h-2" />
              </div>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm">Training & Awareness</span>
                  <span className="text-sm font-medium">90%</span>
                </div>
                <Progress value={90} className="h-2" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Incident Statistics</CardTitle>
            <CardDescription>Incident metrics for the past 30 days</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4 text-center">
                <div>
                  <div className="text-2xl font-bold text-blue-600">12</div>
                  <div className="text-xs text-gray-600">Total Incidents</div>
                </div>
                <div>
                  <div className="text-2xl font-bold text-green-600">9</div>
                  <div className="text-xs text-gray-600">Resolved</div>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4 text-center">
                <div>
                  <div className="text-lg font-bold text-yellow-600">3</div>
                  <div className="text-xs text-gray-600">In Progress</div>
                </div>
                <div>
                  <div className="text-lg font-bold text-gray-600">2.4h</div>
                  <div className="text-xs text-gray-600">Avg Resolution</div>
                </div>
              </div>
              <div className="text-center">
                <div className="text-sm text-gray-500 mb-2">Resolution Time Distribution</div>
                <div className="space-y-1">
                  <div className="flex justify-between text-xs">
                    <span>&lt; 1h</span>
                    <span>25%</span>
                  </div>
                  <Progress value={25} className="h-1" />
                  <div className="flex justify-between text-xs">
                    <span>1-4h</span>
                    <span>50%</span>
                  </div>
                  <Progress value={50} className="h-1" />
                  <div className="flex justify-between text-xs">
                    <span>&gt; 4h</span>
                    <span>25%</span>
                  </div>
                  <Progress value={25} className="h-1" />
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Insights */}
      <div>
        <h3 className="text-lg font-semibold mb-4">Recent Insights & Alerts</h3>
        <div className="space-y-3">
          {recentInsights.map((insight) => {
            const Icon = getInsightIcon(insight.type)
            return (
              <Card key={insight.id}>
                <CardContent className="pt-4">
                  <div className="flex items-start gap-3">
                    <Icon className="h-5 w-5 text-blue-600 mt-0.5 flex-shrink-0" />
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <h4 className="font-medium">{insight.title}</h4>
                        <Badge variant={getInsightColor(insight.severity)} className="text-xs">
                          {insight.severity}
                        </Badge>
                      </div>
                      <p className="text-sm text-gray-600 mb-2">{insight.description}</p>
                      <div className="text-xs text-gray-400">{insight.timestamp}</div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )
          })}
        </div>
      </div>
    </div>
  )
}
