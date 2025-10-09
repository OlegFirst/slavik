import React, { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Switch } from '@/components/ui/switch'
import { 
  Play,
  Pause,
  Settings,
  Workflow,
  Zap,
  Clock,
  CheckCircle,
  AlertCircle,
  ArrowRight,
  Bot,
  Activity,
  BarChart3
} from 'lucide-react'

interface WorkflowStep {
  id: string
  name: string
  type: 'trigger' | 'condition' | 'action' | 'ai_decision'
  status: 'pending' | 'running' | 'completed' | 'failed'
  duration?: number
  description: string
}

interface AutomationWorkflow {
  id: string
  name: string
  description: string
  status: 'active' | 'inactive' | 'running'
  trigger: string
  lastRun?: string
  successRate: number
  steps: WorkflowStep[]
  category: 'incident' | 'risk' | 'compliance' | 'general'
}

interface AutomationWorkflowsProps {
  className?: string
}

export function AutomationWorkflows({ className }: AutomationWorkflowsProps) {
  const [activeTab, setActiveTab] = useState('workflows')
  const [selectedWorkflow, setSelectedWorkflow] = useState<string | null>(null)

  const workflows: AutomationWorkflow[] = [
    {
      id: '1',
      name: 'Incident Response Automation',
      description: 'Automatically escalate high-priority incidents and notify stakeholders',
      status: 'active',
      trigger: 'High Severity Incident Created',
      lastRun: '2 minutes ago',
      successRate: 96,
      category: 'incident',
      steps: [
        {
          id: '1',
          name: 'Incident Detection',
          type: 'trigger',
          status: 'completed',
          duration: 5,
          description: 'Monitor for new high-severity incidents'
        },
        {
          id: '2',
          name: 'AI Risk Assessment',
          type: 'ai_decision',
          status: 'completed',
          duration: 15,
          description: 'AI evaluates incident impact and urgency'
        },
        {
          id: '3',
          name: 'Stakeholder Notification',
          type: 'action',
          status: 'completed',
          duration: 3,
          description: 'Send alerts to relevant team members'
        },
        {
          id: '4',
          name: 'Crisis Team Assembly',
          type: 'action',
          status: 'running',
          description: 'Activate crisis response team'
        }
      ]
    },
    {
      id: '2',
      name: 'Risk Monitoring Workflow',
      description: 'Continuous risk monitoring with AI-powered early warnings',
      status: 'active',
      trigger: 'Risk Threshold Exceeded',
      lastRun: '1 hour ago',
      successRate: 89,
      category: 'risk',
      steps: [
        {
          id: '1',
          name: 'Risk Metric Collection',
          type: 'trigger',
          status: 'completed',
          duration: 10,
          description: 'Gather risk indicators from all sources'
        },
        {
          id: '2',
          name: 'AI Risk Prediction',
          type: 'ai_decision',
          status: 'completed',
          duration: 25,
          description: 'AI predicts risk trajectory and impact'
        },
        {
          id: '3',
          name: 'Generate Risk Report',
          type: 'action',
          status: 'completed',
          duration: 8,
          description: 'Create automated risk assessment report'
        },
        {
          id: '4',
          name: 'Update Risk Register',
          type: 'action',
          status: 'completed',
          duration: 5,
          description: 'Automatically update risk database'
        }
      ]
    },
    {
      id: '3',
      name: 'Compliance Monitoring',
      description: 'Automated compliance checking and reporting workflow',
      status: 'inactive',
      trigger: 'Scheduled Daily Check',
      lastRun: '1 day ago',
      successRate: 94,
      category: 'compliance',
      steps: [
        {
          id: '1',
          name: 'Compliance Data Scan',
          type: 'trigger',
          status: 'pending',
          description: 'Scan all systems for compliance status'
        },
        {
          id: '2',
          name: 'AI Gap Analysis',
          type: 'ai_decision',
          status: 'pending',
          description: 'AI identifies compliance gaps and risks'
        },
        {
          id: '3',
          name: 'Generate Compliance Report',
          type: 'action',
          status: 'pending',
          description: 'Create comprehensive compliance report'
        }
      ]
    }
  ]

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'default'
      case 'running': return 'secondary'
      case 'inactive': return 'outline'
      case 'completed': return 'default'
      case 'failed': return 'destructive'
      default: return 'outline'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running': return Activity
      case 'completed': return CheckCircle
      case 'failed': return AlertCircle
      default: return Clock
    }
  }

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'incident': return 'destructive'
      case 'risk': return 'secondary'
      case 'compliance': return 'default'
      default: return 'outline'
    }
  }

  const toggleWorkflow = (workflowId: string) => {
    // In real implementation, this would call API
    console.log(`Toggle workflow ${workflowId}`)
  }

  const runWorkflow = (workflowId: string) => {
    // In real implementation, this would trigger workflow
    console.log(`Run workflow ${workflowId}`)
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <Workflow className="h-6 w-6 text-purple-600" />
            Automation Workflows
          </h2>
          <p className="text-gray-600 mt-1">
            AI-powered automation workflows for BCM processes
          </p>
        </div>
        <Button className="flex items-center gap-2">
          <Zap className="h-4 w-4" />
          Create Workflow
        </Button>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="workflows">Active Workflows</TabsTrigger>
          <TabsTrigger value="builder">Workflow Builder</TabsTrigger>
          <TabsTrigger value="templates">Templates</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
        </TabsList>

        <TabsContent value="workflows" className="space-y-4">
          <div className="grid gap-4">
            {workflows.map((workflow) => (
              <Card key={workflow.id}>
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between">
                    <div className="space-y-2">
                      <div className="flex items-center gap-2">
                        <CardTitle className="text-lg">{workflow.name}</CardTitle>
                        <Badge variant={getStatusColor(workflow.status)}>
                          {workflow.status.toUpperCase()}
                        </Badge>
                        <Badge variant={getCategoryColor(workflow.category)}>
                          {workflow.category}
                        </Badge>
                      </div>
                      <CardDescription>{workflow.description}</CardDescription>
                      <div className="flex items-center gap-4 text-sm text-gray-500">
                        <span>Trigger: {workflow.trigger}</span>
                        {workflow.lastRun && <span>Last run: {workflow.lastRun}</span>}
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="text-right mr-4">
                        <div className="text-sm text-gray-500">Success Rate</div>
                        <div className="text-lg font-bold text-green-600">
                          {workflow.successRate}%
                        </div>
                      </div>
                      <Switch 
                        checked={workflow.status === 'active'}
                        onCheckedChange={() => toggleWorkflow(workflow.id)}
                      />
                      <Button 
                        size="sm" 
                        variant="outline"
                        onClick={() => runWorkflow(workflow.id)}
                        className="flex items-center gap-1"
                      >
                        <Play className="h-3 w-3" />
                        Run
                      </Button>
                      <Button 
                        size="sm" 
                        variant="ghost"
                        onClick={() => setSelectedWorkflow(workflow.id)}
                      >
                        <Settings className="h-3 w-3" />
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="text-sm font-medium">Workflow Steps:</div>
                    <div className="flex items-center gap-2 overflow-x-auto pb-2">
                      {workflow.steps.map((step, index) => {
                        const StatusIcon = getStatusIcon(step.status)
                        return (
                          <React.Fragment key={step.id}>
                            <div className="flex flex-col items-center min-w-[120px]">
                              <div className={`
                                w-8 h-8 rounded-full flex items-center justify-center mb-1
                                ${step.status === 'completed' ? 'bg-green-100 text-green-600' : 
                                  step.status === 'running' ? 'bg-blue-100 text-blue-600' :
                                  step.status === 'failed' ? 'bg-red-100 text-red-600' :
                                  'bg-gray-100 text-gray-400'}
                              `}>
                                <StatusIcon className="h-4 w-4" />
                              </div>
                              <div className="text-xs text-center">
                                <div className="font-medium">{step.name}</div>
                                {step.duration && (
                                  <div className="text-gray-500">{step.duration}s</div>
                                )}
                              </div>
                            </div>
                            {index < workflow.steps.length - 1 && (
                              <ArrowRight className="h-4 w-4 text-gray-400 flex-shrink-0" />
                            )}
                          </React.Fragment>
                        )
                      })}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="builder" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Settings className="h-5 w-5 text-blue-600" />
                Workflow Builder
              </CardTitle>
              <CardDescription>
                Drag-and-drop workflow builder with AI assistance
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-6 md:grid-cols-2">
                <div>
                  <h4 className="font-medium mb-3">Available Components</h4>
                  <div className="space-y-2">
                    <div className="p-3 border rounded-lg bg-blue-50 hover:bg-blue-100 cursor-pointer">
                      <div className="flex items-center gap-2">
                        <Zap className="h-4 w-4 text-blue-600" />
                        <span className="font-medium">Trigger</span>
                      </div>
                      <p className="text-xs text-gray-600 mt-1">
                        Event that starts the workflow
                      </p>
                    </div>
                    <div className="p-3 border rounded-lg bg-purple-50 hover:bg-purple-100 cursor-pointer">
                      <div className="flex items-center gap-2">
                        <Bot className="h-4 w-4 text-purple-600" />
                        <span className="font-medium">AI Decision</span>
                      </div>
                      <p className="text-xs text-gray-600 mt-1">
                        AI-powered decision point
                      </p>
                    </div>
                    <div className="p-3 border rounded-lg bg-green-50 hover:bg-green-100 cursor-pointer">
                      <div className="flex items-center gap-2">
                        <Play className="h-4 w-4 text-green-600" />
                        <span className="font-medium">Action</span>
                      </div>
                      <p className="text-xs text-gray-600 mt-1">
                        Execute specific action
                      </p>
                    </div>
                  </div>
                </div>
                <div>
                  <h4 className="font-medium mb-3">Canvas</h4>
                  <div className="border-2 border-dashed border-gray-300 rounded-lg h-64 flex items-center justify-center">
                    <div className="text-center text-gray-500">
                      <Workflow className="h-8 w-8 mx-auto mb-2" />
                      <p>Drag components here to build workflow</p>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="templates" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Incident Response Template</CardTitle>
                <CardDescription>
                  Pre-built workflow for automated incident handling
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Steps: 6</span>
                    <span>Avg Duration: 45min</span>
                  </div>
                  <Button className="w-full" variant="outline">
                    Use Template
                  </Button>
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader>
                <CardTitle>Risk Assessment Template</CardTitle>
                <CardDescription>
                  Automated risk evaluation and reporting workflow
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Steps: 4</span>
                    <span>Avg Duration: 20min</span>
                  </div>
                  <Button className="w-full" variant="outline">
                    Use Template
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="analytics" className="space-y-4">
          <div className="grid gap-6 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="h-5 w-5 text-green-600" />
                  Workflow Performance
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-sm">Success Rate</span>
                      <span className="text-sm font-medium">93%</span>
                    </div>
                    <Progress value={93} className="h-2" />
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-sm">Average Duration</span>
                      <span className="text-sm font-medium">32 minutes</span>
                    </div>
                    <Progress value={75} className="h-2" />
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-sm">Cost Savings</span>
                      <span className="text-sm font-medium">$45,000/month</span>
                    </div>
                    <Progress value={85} className="h-2" />
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Activity className="h-5 w-5 text-blue-600" />
                  Usage Statistics
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-600">1,247</div>
                    <div className="text-sm text-gray-600">Workflows executed this month</div>
                  </div>
                  <div className="grid grid-cols-2 gap-4 text-center">
                    <div>
                      <div className="text-lg font-bold">23</div>
                      <div className="text-xs text-gray-600">Active workflows</div>
                    </div>
                    <div>
                      <div className="text-lg font-bold">156h</div>
                      <div className="text-xs text-gray-600">Time saved</div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}
