'use client'

import { useState, useEffect } from 'react'
import { useWorkflowMetrics, useActiveWorkflows } from '@/lib/hooks/useWorkflow'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { SectionTabContent, SectionHeader } from '@/components/sections/SectionLayout'
import { ProcessPerformanceAnalytics } from './analytics/ProcessPerformanceAnalytics'
import { SLAMonitor } from './analytics/SLAMonitor'
import {
  Activity,
  CheckCircle,
  Clock,
  AlertTriangle,
  TrendingUp,
  Workflow,
  Play,
  Pause,
  MoreHorizontal,
  Users,
  Settings,
  BarChart3,
  Timer
} from 'lucide-react'

interface WorkflowMetrics {
  totalWorkflows: number
  activeWorkflows: number
  completedToday: number
  averageCompletionTime: string
  automationRate: number
}

interface ActiveWorkflow {
  id: string
  name: string
  type: 'bcp' | 'incident' | 'training' | 'audit'
  status: 'running' | 'paused' | 'waiting' | 'completed'
  progress: number
  assignedTo: string
  startTime: string
  estimatedCompletion: string
}

// Mock data
const mockMetrics: WorkflowMetrics = {
  totalWorkflows: 24,
  activeWorkflows: 8,
  completedToday: 15,
  averageCompletionTime: '2.5 hours',
  automationRate: 73
}

const mockActiveWorkflows: ActiveWorkflow[] = [
  {
    id: '1',
    name: 'BCP Plan Review Workflow',
    type: 'bcp',
    status: 'running',
    progress: 65,
    assignedTo: 'John Smith',
    startTime: '09:30',
    estimatedCompletion: '14:30'
  },
  {
    id: '2',
    name: 'Incident Response Protocol',
    type: 'incident',
    status: 'waiting',
    progress: 30,
    assignedTo: 'Sarah Johnson',
    startTime: '11:00',
    estimatedCompletion: '16:00'
  },
  {
    id: '3',
    name: 'Training Completion Tracking',
    type: 'training',
    status: 'running',
    progress: 90,
    assignedTo: 'Mike Davis',
    startTime: '08:00',
    estimatedCompletion: '12:00'
  },
  {
    id: '4',
    name: 'Compliance Audit Workflow',
    type: 'audit',
    status: 'paused',
    progress: 45,
    assignedTo: 'Lisa Wilson',
    startTime: '10:15',
    estimatedCompletion: '15:15'
  }
]

function getWorkflowTypeColor(type: string) {
  switch (type) {
    case 'bcp': return 'bg-blue-100 text-blue-700'
    case 'incident': return 'bg-red-100 text-red-700'
    case 'training': return 'bg-green-100 text-green-700'
    case 'audit': return 'bg-purple-100 text-purple-700'
    default: return 'bg-gray-100 text-gray-700'
  }
}

function getStatusIcon(status: string) {
  switch (status) {
    case 'running': return <Play className="h-4 w-4 text-green-600" />
    case 'paused': return <Pause className="h-4 w-4 text-yellow-600" />
    case 'waiting': return <Clock className="h-4 w-4 text-blue-600" />
    case 'completed': return <CheckCircle className="h-4 w-4 text-green-600" />
    default: return <Activity className="h-4 w-4 text-gray-600" />
  }
}

export function WorkflowDashboard() {
  const [metrics, setMetrics] = useState<WorkflowMetrics>(mockMetrics)
  const [activeWorkflows, setActiveWorkflows] = useState<ActiveWorkflow[]>(mockActiveWorkflows)

  return (
    <SectionTabContent>
      <SectionHeader
        title="Workflow Dashboard"
        description="Overview of all workflow activities and performance metrics"
      >
        <Button>
          <Workflow className="h-4 w-4 mr-2" />
          New Workflow
        </Button>
      </SectionHeader>

      {/* Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Workflows</CardTitle>
            <Workflow className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metrics.totalWorkflows}</div>
            <p className="text-xs text-muted-foreground">+2 from last month</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Now</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metrics.activeWorkflows}</div>
            <p className="text-xs text-muted-foreground">+1 from yesterday</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Completed Today</CardTitle>
            <CheckCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metrics.completedToday}</div>
            <p className="text-xs text-muted-foreground">+5 from yesterday</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Automation Rate</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metrics.automationRate}%</div>
            <Progress value={metrics.automationRate} className="mt-2" />
          </CardContent>
        </Card>
      </div>

      {/* Active Workflows */}
      <Card>
        <CardHeader>
          <CardTitle>Active Workflows</CardTitle>
          <CardDescription>
            Currently running and scheduled workflows
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {activeWorkflows.map((workflow) => (
              <div
                key={workflow.id}
                className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50"
              >
                <div className="flex items-center space-x-4">
                  <div className="flex items-center space-x-2">
                    {getStatusIcon(workflow.status)}
                    <div>
                      <h4 className="font-medium">{workflow.name}</h4>
                      <div className="flex items-center space-x-2 mt-1">
                        <Badge
                          variant="secondary"
                          className={getWorkflowTypeColor(workflow.type)}
                        >
                          {workflow.type.toUpperCase()}
                        </Badge>
                        <span className="text-sm text-muted-foreground">
                          Started: {workflow.startTime}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="flex items-center space-x-4">
                  <div className="text-right">
                    <div className="text-sm font-medium">{workflow.progress}%</div>
                    <Progress value={workflow.progress} className="w-20 mt-1" />
                  </div>

                  <div className="text-right">
                    <div className="text-sm text-muted-foreground">Assigned to</div>
                    <div className="text-sm font-medium">{workflow.assignedTo}</div>
                  </div>

                  <div className="text-right">
                    <div className="text-sm text-muted-foreground">ETA</div>
                    <div className="text-sm font-medium">{workflow.estimatedCompletion}</div>
                  </div>

                  <Button variant="ghost" size="sm">
                    <MoreHorizontal className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* 🆕 NEW: Enhanced Analytics Section */}
      <Tabs defaultValue="overview" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="overview" className="flex items-center gap-2">
            <Activity className="h-4 w-4" />
            Overview
          </TabsTrigger>
          <TabsTrigger value="analytics" className="flex items-center gap-2">
            <BarChart3 className="h-4 w-4" />
            Analytics
          </TabsTrigger>
          <TabsTrigger value="sla" className="flex items-center gap-2">
            <Timer className="h-4 w-4" />
            SLA Monitor
          </TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          {/* Quick Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Performance Insights</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-sm text-muted-foreground">Avg. Completion Time</span>
                    <span className="text-sm font-medium">{metrics.averageCompletionTime}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-muted-foreground">Success Rate</span>
                    <span className="text-sm font-medium">96.5%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-muted-foreground">Time Saved (Automation)</span>
                    <span className="text-sm font-medium">15.3 hours/week</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Resource Utilization</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">Team Capacity</span>
                    <span className="text-sm font-medium">78%</span>
                  </div>
                  <Progress value={78} className="w-full" />
                  <div className="flex justify-between text-xs text-muted-foreground">
                    <span>Available: 22%</span>
                    <span>Utilized: 78%</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Recent Issues</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center space-x-2">
                    <AlertTriangle className="h-4 w-4 text-yellow-500" />
                    <span className="text-sm">2 workflows pending approval</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Clock className="h-4 w-4 text-blue-500" />
                    <span className="text-sm">1 workflow exceeded deadline</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <CheckCircle className="h-4 w-4 text-green-500" />
                    <span className="text-sm">All automations running smoothly</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="analytics" className="space-y-6">
          <ProcessPerformanceAnalytics />
        </TabsContent>

        <TabsContent value="sla" className="space-y-6">
          <SLAMonitor autoRefresh={true} showBreaches={true} />
        </TabsContent>
      </Tabs>
    </SectionTabContent>
  )
}