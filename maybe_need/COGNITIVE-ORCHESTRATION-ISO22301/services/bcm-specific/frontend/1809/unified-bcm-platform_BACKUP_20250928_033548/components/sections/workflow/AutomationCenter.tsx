'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Progress } from '@/components/ui/progress'
import { SectionTabContent, SectionHeader } from '@/components/sections/SectionLayout'
import {
  Zap,
  Plus,
  Play,
  Pause,
  Settings,
  Clock,
  CheckCircle,
  AlertTriangle,
  TrendingUp,
  Bot,
  Mail,
  MessageSquare,
  Bell,
  Calendar,
  FileText,
  Users,
  Database,
  Workflow,
  Activity,
  MoreHorizontal,
  Edit,
  Trash2,
  Copy
} from 'lucide-react'

interface AutomationRule {
  id: string
  name: string
  description: string
  trigger: {
    type: 'incident' | 'schedule' | 'event' | 'condition'
    config: Record<string, any>
  }
  actions: AutomationAction[]
  status: 'active' | 'paused' | 'draft'
  category: 'notification' | 'escalation' | 'workflow' | 'reporting' | 'compliance'
  lastExecuted?: string
  executionCount: number
  successRate: number
  avgExecutionTime: string
}

interface AutomationAction {
  id: string
  type: 'notification' | 'email' | 'webhook' | 'workflow_start' | 'data_update' | 'report_generate'
  config: Record<string, any>
  order: number
}

interface AutomationTemplate {
  id: string
  name: string
  description: string
  category: string
  actions: number
  popularity: number
  useCase: string
}

// Mock data
const mockRules: AutomationRule[] = [
  {
    id: '1',
    name: 'Critical Incident Auto-Escalation',
    description: 'Automatically escalate critical incidents to management within 15 minutes',
    trigger: {
      type: 'incident',
      config: { severity: 'critical', timeThreshold: 15 }
    },
    actions: [
      {
        id: 'action1',
        type: 'notification',
        config: { recipients: ['management'], message: 'Critical incident requires attention' },
        order: 1
      },
      {
        id: 'action2',
        type: 'email',
        config: { template: 'critical_escalation', to: 'executives@company.com' },
        order: 2
      }
    ],
    status: 'active',
    category: 'escalation',
    lastExecuted: '2024-01-15 14:30',
    executionCount: 42,
    successRate: 98.5,
    avgExecutionTime: '2.3s'
  },
  {
    id: '2',
    name: 'Weekly BCP Report Generation',
    description: 'Generate and distribute weekly business continuity status reports',
    trigger: {
      type: 'schedule',
      config: { frequency: 'weekly', day: 'monday', time: '09:00' }
    },
    actions: [
      {
        id: 'action3',
        type: 'report_generate',
        config: { template: 'weekly_bcp_status', format: 'pdf' },
        order: 1
      },
      {
        id: 'action4',
        type: 'email',
        config: { template: 'report_distribution', attachReport: true },
        order: 2
      }
    ],
    status: 'active',
    category: 'reporting',
    lastExecuted: '2024-01-15 09:00',
    executionCount: 12,
    successRate: 100,
    avgExecutionTime: '45s'
  },
  {
    id: '3',
    name: 'Training Completion Reminder',
    description: 'Send reminders for overdue training completions',
    trigger: {
      type: 'schedule',
      config: { frequency: 'daily', time: '10:00' }
    },
    actions: [
      {
        id: 'action5',
        type: 'notification',
        config: { type: 'training_reminder', target: 'overdue_users' },
        order: 1
      }
    ],
    status: 'active',
    category: 'notification',
    lastExecuted: '2024-01-15 10:00',
    executionCount: 156,
    successRate: 95.2,
    avgExecutionTime: '1.1s'
  },
  {
    id: '4',
    name: 'Audit Evidence Collection',
    description: 'Automatically collect and organize audit evidence monthly',
    trigger: {
      type: 'schedule',
      config: { frequency: 'monthly', day: 1, time: '08:00' }
    },
    actions: [
      {
        id: 'action6',
        type: 'data_update',
        config: { source: 'compliance_data', target: 'audit_repository' },
        order: 1
      },
      {
        id: 'action7',
        type: 'workflow_start',
        config: { workflow: 'audit_preparation', assignee: 'compliance_team' },
        order: 2
      }
    ],
    status: 'paused',
    category: 'compliance',
    lastExecuted: '2024-01-01 08:00',
    executionCount: 3,
    successRate: 100,
    avgExecutionTime: '12.5s'
  }
]

const mockTemplates: AutomationTemplate[] = [
  {
    id: '1',
    name: 'Incident Response Automation',
    description: 'Complete incident response automation workflow',
    category: 'Incident Management',
    actions: 5,
    popularity: 85,
    useCase: 'Automatic incident classification, notification, and initial response'
  },
  {
    id: '2',
    name: 'Compliance Monitoring',
    description: 'Automated compliance status monitoring and reporting',
    category: 'Compliance',
    actions: 3,
    popularity: 72,
    useCase: 'Regular compliance checks and automated remediation alerts'
  },
  {
    id: '3',
    name: 'Training Automation',
    description: 'Automated training assignment and completion tracking',
    category: 'Training',
    actions: 4,
    popularity: 68,
    useCase: 'Automatic training assignment based on role and completion reminders'
  }
]

function getStatusColor(status: string) {
  switch (status) {
    case 'active': return 'bg-green-100 text-green-700'
    case 'paused': return 'bg-yellow-100 text-yellow-700'
    case 'draft': return 'bg-gray-100 text-gray-700'
    default: return 'bg-gray-100 text-gray-700'
  }
}

function getCategoryIcon(category: string) {
  switch (category) {
    case 'notification': return <Bell className="h-4 w-4" />
    case 'escalation': return <AlertTriangle className="h-4 w-4" />
    case 'workflow': return <Workflow className="h-4 w-4" />
    case 'reporting': return <FileText className="h-4 w-4" />
    case 'compliance': return <CheckCircle className="h-4 w-4" />
    default: return <Zap className="h-4 w-4" />
  }
}

function getTriggerIcon(triggerType: string) {
  switch (triggerType) {
    case 'incident': return <AlertTriangle className="h-4 w-4" />
    case 'schedule': return <Calendar className="h-4 w-4" />
    case 'event': return <Activity className="h-4 w-4" />
    case 'condition': return <Settings className="h-4 w-4" />
    default: return <Zap className="h-4 w-4" />
  }
}

export function AutomationCenter() {
  const [rules, setRules] = useState<AutomationRule[]>(mockRules)
  const [selectedRule, setSelectedRule] = useState<AutomationRule | null>(null)
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false)

  const handleToggleRule = (ruleId: string) => {
    setRules(rules.map(rule =>
      rule.id === ruleId
        ? { ...rule, status: rule.status === 'active' ? 'paused' : 'active' }
        : rule
    ))
  }

  const handleEditRule = (rule: AutomationRule) => {
    setSelectedRule(rule)
    console.log('Editing rule:', rule.name)
  }

  const handleDeleteRule = (ruleId: string) => {
    setRules(rules.filter(r => r.id !== ruleId))
    console.log('Deleting rule:', ruleId)
  }

  const handleExecuteRule = (ruleId: string) => {
    console.log('Executing rule:', ruleId)
    // Simulate rule execution
  }

  const totalExecutions = rules.reduce((sum, rule) => sum + rule.executionCount, 0)
  const avgSuccessRate = rules.reduce((sum, rule) => sum + rule.successRate, 0) / rules.length
  const activeRules = rules.filter(rule => rule.status === 'active').length

  return (
    <SectionTabContent>
      <SectionHeader
        title="Automation Center"
        description="Create and manage automated workflows to streamline BCM processes"
      >
        <div className="flex items-center gap-2">
          <Button variant="outline">
            <Bot className="h-4 w-4 mr-2" />
            AI Assistant
          </Button>
          <Button onClick={() => setIsCreateDialogOpen(true)}>
            <Plus className="h-4 w-4 mr-2" />
            New Rule
          </Button>
        </div>
      </SectionHeader>

      <Tabs defaultValue="rules" className="space-y-6">
        <TabsList>
          <TabsTrigger value="rules">Automation Rules</TabsTrigger>
          <TabsTrigger value="templates">Rule Templates</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
          <TabsTrigger value="settings">Settings</TabsTrigger>
        </TabsList>

        <TabsContent value="rules" className="space-y-6">
          {/* Overview Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Active Rules</CardTitle>
                <Zap className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{activeRules}</div>
                <p className="text-xs text-muted-foreground">of {rules.length} total</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Executions</CardTitle>
                <Activity className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{totalExecutions}</div>
                <p className="text-xs text-muted-foreground">+25 this week</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
                <CheckCircle className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{avgSuccessRate.toFixed(1)}%</div>
                <Progress value={avgSuccessRate} className="mt-2" />
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Time Saved</CardTitle>
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">32.5h</div>
                <p className="text-xs text-muted-foreground">this month</p>
              </CardContent>
            </Card>
          </div>

          {/* Rules List */}
          <Card>
            <CardHeader>
              <CardTitle>Automation Rules</CardTitle>
              <CardDescription>
                Manage your automated workflow rules and their execution
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Rule</TableHead>
                    <TableHead>Trigger</TableHead>
                    <TableHead>Category</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Performance</TableHead>
                    <TableHead>Last Executed</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {rules.map((rule) => (
                    <TableRow key={rule.id}>
                      <TableCell>
                        <div>
                          <div className="font-medium">{rule.name}</div>
                          <div className="text-sm text-gray-500">{rule.description}</div>
                          <div className="flex items-center mt-1 space-x-2">
                            <Badge variant="outline" className="text-xs">
                              {rule.actions.length} actions
                            </Badge>
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center space-x-2">
                          {getTriggerIcon(rule.trigger.type)}
                          <span className="capitalize">{rule.trigger.type}</span>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center space-x-2">
                          {getCategoryIcon(rule.category)}
                          <span className="capitalize">{rule.category}</span>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center space-x-2">
                          <Badge
                            variant="secondary"
                            className={getStatusColor(rule.status)}
                          >
                            {rule.status}
                          </Badge>
                          <Switch
                            checked={rule.status === 'active'}
                            onCheckedChange={() => handleToggleRule(rule.id)}
                            size="sm"
                          />
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="text-sm">
                          <div>{rule.successRate}% success</div>
                          <div className="text-gray-500">{rule.executionCount} runs</div>
                          <div className="text-gray-500">Avg: {rule.avgExecutionTime}</div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="text-sm text-gray-500">
                          {rule.lastExecuted || 'Never'}
                        </div>
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex items-center justify-end space-x-2">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleExecuteRule(rule.id)}
                            title="Execute now"
                          >
                            <Play className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleEditRule(rule)}
                            title="Edit rule"
                          >
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => console.log('Copy rule:', rule.id)}
                            title="Copy rule"
                          >
                            <Copy className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleDeleteRule(rule.id)}
                            title="Delete rule"
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="templates" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Automation Templates</CardTitle>
              <CardDescription>
                Pre-built automation templates for common BCM scenarios
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {mockTemplates.map((template) => (
                  <Card key={template.id} className="cursor-pointer hover:shadow-md transition-shadow">
                    <CardHeader>
                      <CardTitle className="text-lg">{template.name}</CardTitle>
                      <CardDescription>{template.description}</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        <div className="flex justify-between text-sm">
                          <span className="text-gray-500">Category:</span>
                          <span>{template.category}</span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span className="text-gray-500">Actions:</span>
                          <span>{template.actions}</span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span className="text-gray-500">Popularity:</span>
                          <span>{template.popularity}%</span>
                        </div>
                        <div>
                          <span className="text-sm text-gray-500">Use Case:</span>
                          <p className="text-sm mt-1">{template.useCase}</p>
                        </div>
                        <div className="mt-4">
                          <Button className="w-full" size="sm">
                            Use Template
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="analytics" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Execution Trends</CardTitle>
                <CardDescription>
                  Automation execution patterns over time
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between text-sm mb-2">
                      <span>This Week</span>
                      <span>125 executions</span>
                    </div>
                    <Progress value={85} />
                  </div>
                  <div>
                    <div className="flex justify-between text-sm mb-2">
                      <span>Last Week</span>
                      <span>98 executions</span>
                    </div>
                    <Progress value={68} />
                  </div>
                  <div>
                    <div className="flex justify-between text-sm mb-2">
                      <span>Two Weeks Ago</span>
                      <span>87 executions</span>
                    </div>
                    <Progress value={60} />
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Rule Performance</CardTitle>
                <CardDescription>
                  Success rates by rule category
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {['notification', 'escalation', 'reporting', 'compliance', 'workflow'].map(category => {
                    const categoryRules = rules.filter(r => r.category === category)
                    const avgSuccess = categoryRules.length > 0
                      ? categoryRules.reduce((sum, r) => sum + r.successRate, 0) / categoryRules.length
                      : 0

                    return (
                      <div key={category}>
                        <div className="flex justify-between text-sm mb-2">
                          <span className="capitalize">{category}</span>
                          <span>{avgSuccess.toFixed(1)}%</span>
                        </div>
                        <Progress value={avgSuccess} />
                      </div>
                    )
                  })}
                </div>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Resource Impact</CardTitle>
              <CardDescription>
                Time and resource savings from automation
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="text-center">
                  <div className="text-3xl font-bold text-green-600">32.5h</div>
                  <div className="text-sm text-gray-500">Time Saved This Month</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-blue-600">$4,800</div>
                  <div className="text-sm text-gray-500">Cost Savings</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-purple-600">96.2%</div>
                  <div className="text-sm text-gray-500">Process Efficiency</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="settings" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Automation Settings</CardTitle>
              <CardDescription>
                Configure global automation preferences and limits
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <h4 className="font-medium">Execution Limits</h4>
                  <div>
                    <Label htmlFor="max-concurrent">Max Concurrent Executions</Label>
                    <Input
                      id="max-concurrent"
                      type="number"
                      defaultValue="10"
                      className="mt-1"
                    />
                  </div>
                  <div>
                    <Label htmlFor="retry-attempts">Retry Attempts on Failure</Label>
                    <Input
                      id="retry-attempts"
                      type="number"
                      defaultValue="3"
                      className="mt-1"
                    />
                  </div>
                  <div>
                    <Label htmlFor="timeout">Execution Timeout (seconds)</Label>
                    <Input
                      id="timeout"
                      type="number"
                      defaultValue="300"
                      className="mt-1"
                    />
                  </div>
                </div>

                <div className="space-y-4">
                  <h4 className="font-medium">Notifications</h4>
                  <div className="flex items-center justify-between">
                    <Label htmlFor="failure-notifications">Notify on Failures</Label>
                    <Switch id="failure-notifications" defaultChecked />
                  </div>
                  <div className="flex items-center justify-between">
                    <Label htmlFor="success-notifications">Notify on Success</Label>
                    <Switch id="success-notifications" />
                  </div>
                  <div className="flex items-center justify-between">
                    <Label htmlFor="daily-summary">Daily Summary Reports</Label>
                    <Switch id="daily-summary" defaultChecked />
                  </div>
                  <div>
                    <Label htmlFor="notification-email">Notification Email</Label>
                    <Input
                      id="notification-email"
                      type="email"
                      defaultValue="admin@company.com"
                      className="mt-1"
                    />
                  </div>
                </div>
              </div>

              <div className="pt-4 border-t">
                <div className="flex justify-end space-x-2">
                  <Button variant="outline">Reset to Defaults</Button>
                  <Button>Save Settings</Button>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Integration Settings</CardTitle>
              <CardDescription>
                Configure external system integrations for automation
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center space-x-3">
                      <Mail className="h-5 w-5" />
                      <div>
                        <div className="font-medium">Email Service</div>
                        <div className="text-sm text-gray-500">SMTP Configuration</div>
                      </div>
                    </div>
                    <Badge variant="secondary" className="bg-green-100 text-green-700">
                      Connected
                    </Badge>
                  </div>

                  <div className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center space-x-3">
                      <MessageSquare className="h-5 w-5" />
                      <div>
                        <div className="font-medium">Slack Integration</div>
                        <div className="text-sm text-gray-500">Team Notifications</div>
                      </div>
                    </div>
                    <Badge variant="secondary" className="bg-yellow-100 text-yellow-700">
                      Pending
                    </Badge>
                  </div>

                  <div className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center space-x-3">
                      <Database className="h-5 w-5" />
                      <div>
                        <div className="font-medium">Database Webhook</div>
                        <div className="text-sm text-gray-500">Data Synchronization</div>
                      </div>
                    </div>
                    <Badge variant="secondary" className="bg-green-100 text-green-700">
                      Connected
                    </Badge>
                  </div>

                  <div className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center space-x-3">
                      <Bot className="h-5 w-5" />
                      <div>
                        <div className="font-medium">AI Service</div>
                        <div className="text-sm text-gray-500">Intelligent Automation</div>
                      </div>
                    </div>
                    <Badge variant="secondary" className="bg-green-100 text-green-700">
                      Connected
                    </Badge>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Create Automation Rule Dialog */}
      <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
        <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Create Automation Rule</DialogTitle>
            <DialogDescription>
              Define triggers and actions for your automation workflow
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-6 py-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="rule-name">Rule Name</Label>
                <Input
                  id="rule-name"
                  placeholder="Enter rule name"
                />
              </div>
              <div>
                <Label htmlFor="rule-category">Category</Label>
                <Select>
                  <SelectTrigger>
                    <SelectValue placeholder="Select category" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="notification">Notification</SelectItem>
                    <SelectItem value="escalation">Escalation</SelectItem>
                    <SelectItem value="workflow">Workflow</SelectItem>
                    <SelectItem value="reporting">Reporting</SelectItem>
                    <SelectItem value="compliance">Compliance</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div>
              <Label htmlFor="rule-description">Description</Label>
              <Input
                id="rule-description"
                placeholder="Describe what this rule does"
              />
            </div>

            <div>
              <h4 className="font-medium mb-3">Trigger Configuration</h4>
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <Label htmlFor="trigger-type">Trigger Type</Label>
                  <Select>
                    <SelectTrigger>
                      <SelectValue placeholder="Select trigger" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="incident">Incident Created</SelectItem>
                      <SelectItem value="schedule">Scheduled</SelectItem>
                      <SelectItem value="event">System Event</SelectItem>
                      <SelectItem value="condition">Condition Met</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="trigger-condition">Condition</Label>
                  <Input
                    id="trigger-condition"
                    placeholder="e.g., severity = critical"
                  />
                </div>
                <div>
                  <Label htmlFor="trigger-delay">Delay (minutes)</Label>
                  <Input
                    id="trigger-delay"
                    type="number"
                    placeholder="0"
                  />
                </div>
              </div>
            </div>

            <div>
              <h4 className="font-medium mb-3">Actions</h4>
              <div className="space-y-3">
                <div className="flex items-center space-x-3 p-3 border rounded-lg">
                  <Select defaultValue="notification">
                    <SelectTrigger className="w-40">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="notification">Send Notification</SelectItem>
                      <SelectItem value="email">Send Email</SelectItem>
                      <SelectItem value="webhook">Call Webhook</SelectItem>
                      <SelectItem value="workflow_start">Start Workflow</SelectItem>
                    </SelectContent>
                  </Select>
                  <Input
                    placeholder="Action configuration"
                    className="flex-1"
                  />
                  <Button variant="ghost" size="sm">
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
                <Button variant="outline" size="sm">
                  <Plus className="h-4 w-4 mr-2" />
                  Add Action
                </Button>
              </div>
            </div>

            <div className="flex justify-end space-x-2 pt-4">
              <Button variant="outline" onClick={() => setIsCreateDialogOpen(false)}>
                Cancel
              </Button>
              <Button onClick={() => setIsCreateDialogOpen(false)}>
                Create Rule
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </SectionTabContent>
  )
}