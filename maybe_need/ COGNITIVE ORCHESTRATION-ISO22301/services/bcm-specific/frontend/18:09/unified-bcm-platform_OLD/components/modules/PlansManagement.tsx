'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Textarea } from '@/components/ui/textarea'
import { Progress } from '@/components/ui/progress'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Separator } from '@/components/ui/separator'
import {
  FileText,
  Users,
  Clock,
  CheckCircle,
  AlertTriangle,
  Target,
  Activity,
  Calendar,
  MapPin,
  Zap,
  Shield,
  RefreshCw,
  BookOpen,
  Play,
  Pause,
  RotateCcw,
  Download,
  Upload,
  Copy,
  Edit,
  Eye,
  Search,
  Filter,
  ChevronRight,
  ChevronDown,
  Settings,
  AlertCircle,
  TrendingUp,
  Archive,
  Plus
} from 'lucide-react'
import { apiClient } from '@/lib/api-client'
import { useBCMStore } from '@/lib/bcm-store'

// Types
interface BCMPlan {
  id: string
  name: string
  type: 'business_continuity' | 'disaster_recovery' | 'crisis_management' | 'emergency_response' | 'it_recovery' | 'communication'
  status: 'draft' | 'review' | 'approved' | 'active' | 'testing' | 'archived'
  version: string
  priority: 'critical' | 'high' | 'medium' | 'low'
  owner: string
  approvedBy?: string[]
  lastUpdated: string
  lastTested: string
  nextTestDate: string
  activationTriggers: string[]
  rto: number // minutes
  rpo: number // minutes
  scope: string[]
  dependencies: string[]
  resources: PlanResource[]
  steps: PlanStep[]
  roles: PlanRole[]
  communications: CommunicationPlan[]
  testResults?: TestResult[]
  effectiveness?: number
  completeness: number
  tags: string[]
}

interface PlanStep {
  id: string
  phase: 'preparation' | 'activation' | 'response' | 'recovery' | 'resumption'
  sequenceNumber: number
  title: string
  description: string
  responsible: string
  estimatedDuration: number // minutes
  dependencies: string[]
  resources: string[]
  checklists: ChecklistItem[]
  status?: 'pending' | 'in_progress' | 'completed' | 'blocked'
  startedAt?: string
  completedAt?: string
  notes?: string
}

interface ChecklistItem {
  id: string
  description: string
  required: boolean
  completed?: boolean
  completedBy?: string
  completedAt?: string
  evidence?: string
}

interface PlanResource {
  id: string
  name: string
  type: 'personnel' | 'equipment' | 'facility' | 'service' | 'contact' | 'document'
  description?: string
  availability: 'always' | 'business_hours' | 'on_call' | 'limited'
  location?: string
  contactInfo?: string
  alternates?: string[]
  status: 'available' | 'unavailable' | 'limited' | 'unknown'
}

interface PlanRole {
  id: string
  title: string
  responsibilities: string[]
  skills: string[]
  primaryAssignee: string
  backupAssignees: string[]
  contactMethods: string[]
  location: string
}

interface CommunicationPlan {
  id: string
  audience: 'internal' | 'external' | 'stakeholders' | 'media' | 'customers' | 'suppliers'
  channel: 'email' | 'phone' | 'sms' | 'website' | 'social_media' | 'meeting'
  frequency: 'immediate' | 'hourly' | 'every_4h' | 'daily' | 'as_needed'
  responsible: string
  template?: string
  recipients: string[]
  escalation?: string[]
}

interface TestResult {
  id: string
  date: string
  type: 'tabletop' | 'walkthrough' | 'simulation' | 'full_scale'
  scope: string[]
  participants: string[]
  duration: number
  objectives: string[]
  results: TestFinding[]
  overallRating: number
  improvementActions: string[]
  nextTestDate?: string
}

interface TestFinding {
  id: string
  category: 'strength' | 'weakness' | 'gap' | 'improvement'
  description: string
  impact: 'high' | 'medium' | 'low'
  recommendation?: string
  responsible?: string
  targetDate?: string
}

interface PlanMetrics {
  totalPlans: number
  activePlans: number
  plansNeedingTest: number
  averageCompleteness: number
  overduePlans: number
  testCoverage: number
  planEffectiveness: number
  resourceReadiness: number
}

// Mock data
const generateMockPlans = (): BCMPlan[] => {
  return [
    {
      id: 'PLAN-001',
      name: 'IT Disaster Recovery Plan',
      type: 'disaster_recovery',
      status: 'active',
      version: '3.1',
      priority: 'critical',
      owner: 'IT Manager',
      approvedBy: ['CTO', 'BCM Manager'],
      lastUpdated: '2024-01-15',
      lastTested: '2023-11-20',
      nextTestDate: '2024-05-20',
      activationTriggers: [
        'Complete IT system failure',
        'Data center unavailable',
        'Cyber security incident'
      ],
      rto: 240, // 4 hours
      rpo: 60,  // 1 hour
      scope: ['Core IT Systems', 'Data Centers', 'Network Infrastructure'],
      dependencies: ['Power Supply', 'Telecommunications', 'Security'],
      resources: [
        {
          id: 'R001',
          name: 'Backup Data Center',
          type: 'facility',
          description: 'Secondary data center with full redundancy',
          availability: 'always',
          location: 'Site B',
          status: 'available'
        },
        {
          id: 'R002',
          name: 'IT Recovery Team',
          type: 'personnel',
          description: '24/7 IT recovery specialists',
          availability: 'always',
          contactInfo: '+1-555-IT-HELP',
          status: 'available'
        }
      ],
      steps: [
        {
          id: 'S001',
          phase: 'activation',
          sequenceNumber: 1,
          title: 'Assess IT Impact',
          description: 'Evaluate extent of IT system failure and determine recovery strategy',
          responsible: 'IT Manager',
          estimatedDuration: 30,
          dependencies: [],
          resources: ['IT Recovery Team'],
          checklists: [
            {
              id: 'C001',
              description: 'Identify affected systems',
              required: true
            },
            {
              id: 'C002',
              description: 'Estimate downtime duration',
              required: true
            }
          ]
        },
        {
          id: 'S002',
          phase: 'recovery',
          sequenceNumber: 2,
          title: 'Activate Backup Systems',
          description: 'Switch to backup data center and restore critical services',
          responsible: 'Technical Lead',
          estimatedDuration: 120,
          dependencies: ['S001'],
          resources: ['Backup Data Center', 'IT Recovery Team'],
          checklists: [
            {
              id: 'C003',
              description: 'Verify backup data integrity',
              required: true
            },
            {
              id: 'C004',
              description: 'Test network connectivity',
              required: true
            }
          ]
        }
      ],
      roles: [
        {
          id: 'ROLE001',
          title: 'IT Recovery Coordinator',
          responsibilities: [
            'Coordinate recovery activities',
            'Communication with stakeholders',
            'Resource allocation'
          ],
          skills: ['IT Infrastructure', 'Project Management'],
          primaryAssignee: 'John Smith',
          backupAssignees: ['Jane Doe', 'Mike Johnson'],
          contactMethods: ['Mobile', 'Email', 'Radio'],
          location: 'Primary Command Center'
        }
      ],
      communications: [
        {
          id: 'COMM001',
          audience: 'internal',
          channel: 'email',
          frequency: 'immediate',
          responsible: 'IT Manager',
          recipients: ['All Staff', 'Management Team'],
          escalation: ['CEO']
        }
      ],
      testResults: [
        {
          id: 'TEST001',
          date: '2023-11-20',
          type: 'simulation',
          scope: ['Core Systems Recovery'],
          participants: ['IT Team', 'BCM Team'],
          duration: 180,
          objectives: [
            'Test backup activation',
            'Validate communication procedures',
            'Assess recovery time'
          ],
          results: [
            {
              id: 'F001',
              category: 'strength',
              description: 'Backup systems activated successfully within RTO',
              impact: 'high'
            },
            {
              id: 'F002',
              category: 'weakness',
              description: 'Communication delays to external stakeholders',
              impact: 'medium',
              recommendation: 'Implement automated notification system'
            }
          ],
          overallRating: 85,
          improvementActions: [
            'Automate stakeholder notifications',
            'Update contact database',
            'Enhance monitoring alerts'
          ]
        }
      ],
      effectiveness: 85,
      completeness: 92,
      tags: ['it', 'disaster-recovery', 'critical']
    },
    {
      id: 'PLAN-002',
      name: 'Crisis Communication Plan',
      type: 'communication',
      status: 'active',
      version: '2.0',
      priority: 'high',
      owner: 'Communications Manager',
      approvedBy: ['CEO'],
      lastUpdated: '2024-02-01',
      lastTested: '2023-12-15',
      nextTestDate: '2024-06-15',
      activationTriggers: [
        'Major incident with media attention',
        'Regulatory investigation',
        'Customer data breach'
      ],
      rto: 60, // 1 hour
      rpo: 0,  // immediate
      scope: ['External Communications', 'Media Relations', 'Stakeholder Updates'],
      dependencies: ['Legal Team', 'Senior Management'],
      resources: [],
      steps: [],
      roles: [],
      communications: [],
      effectiveness: 78,
      completeness: 88,
      tags: ['communication', 'crisis', 'media']
    },
    {
      id: 'PLAN-003',
      name: 'Facility Emergency Evacuation Plan',
      type: 'emergency_response',
      status: 'review',
      version: '1.5',
      priority: 'critical',
      owner: 'Facilities Manager',
      lastUpdated: '2024-01-30',
      lastTested: '2023-10-10',
      nextTestDate: '2024-04-10',
      activationTriggers: [
        'Fire alarm activation',
        'Gas leak detection',
        'Security threat',
        'Natural disaster warning'
      ],
      rto: 15, // 15 minutes
      rpo: 0,
      scope: ['All Buildings', 'Personnel Safety'],
      dependencies: ['Security Team', 'Emergency Services'],
      resources: [],
      steps: [],
      roles: [],
      communications: [],
      effectiveness: 95,
      completeness: 75,
      tags: ['emergency', 'evacuation', 'safety']
    }
  ]
}

export function PlansManagementModule() {
  const queryClient = useQueryClient()
  const { publishEvent } = useBCMStore()

  const [activeTab, setActiveTab] = useState<'overview' | 'plans' | 'testing' | 'resources' | 'analytics'>('overview')
  const [selectedPlan, setSelectedPlan] = useState<BCMPlan | null>(null)
  const [showNewPlanDialog, setShowNewPlanDialog] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterType, setFilterType] = useState<string>('all')
  const [filterStatus, setFilterStatus] = useState<string>('all')
  const [expandedPlan, setExpandedPlan] = useState<string | null>(null)

  // Fetch plans
  const { data: plans = [], isLoading: plansLoading } = useQuery({
    queryKey: ['bcm-plans'],
    queryFn: async () => {
      const response = await apiClient.get('/api/plans')
      if (response.data) {
        return response.data
      }
      return generateMockPlans()
    }
  })

  // Calculate metrics
  const metrics: PlanMetrics = {
    totalPlans: plans.length,
    activePlans: plans.filter((p: BCMPlan) => p.status === 'active').length,
    plansNeedingTest: plans.filter((p: BCMPlan) =>
      new Date(p.nextTestDate) < new Date(Date.now() + 30 * 24 * 60 * 60 * 1000) // within 30 days
    ).length,
    averageCompleteness: plans.reduce((acc: number, p: BCMPlan) => acc + p.completeness, 0) / (plans.length || 1),
    overduePlans: plans.filter((p: BCMPlan) =>
      new Date(p.nextTestDate) < new Date()
    ).length,
    testCoverage: plans.filter((p: BCMPlan) => p.testResults && p.testResults.length > 0).length / (plans.length || 1) * 100,
    planEffectiveness: plans.reduce((acc: number, p: BCMPlan) => acc + (p.effectiveness || 0), 0) / (plans.length || 1),
    resourceReadiness: 85 // Mock calculation
  }

  // Filter plans
  const filteredPlans = plans.filter((plan: BCMPlan) => {
    const matchesSearch = plan.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         plan.scope.some(s => s.toLowerCase().includes(searchTerm.toLowerCase()))
    const matchesType = filterType === 'all' || plan.type === filterType
    const matchesStatus = filterStatus === 'all' || plan.status === filterStatus
    return matchesSearch && matchesType && matchesStatus
  })

  // Get status color
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-500'
      case 'approved': return 'bg-blue-500'
      case 'testing': return 'bg-purple-500'
      case 'review': return 'bg-yellow-500'
      case 'draft': return 'bg-gray-500'
      case 'archived': return 'bg-red-500'
      default: return 'bg-gray-500'
    }
  }

  // Get priority color
  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical': return 'text-red-600'
      case 'high': return 'text-orange-600'
      case 'medium': return 'text-yellow-600'
      case 'low': return 'text-blue-600'
      default: return 'text-gray-600'
    }
  }

  // Get phase color
  const getPhaseColor = (phase: string) => {
    switch (phase) {
      case 'preparation': return 'bg-blue-100 text-blue-800'
      case 'activation': return 'bg-yellow-100 text-yellow-800'
      case 'response': return 'bg-red-100 text-red-800'
      case 'recovery': return 'bg-green-100 text-green-800'
      case 'resumption': return 'bg-purple-100 text-purple-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Plans Management</h1>
          <p className="text-muted-foreground mt-1">
            Create, maintain and test business continuity plans
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={() => queryClient.invalidateQueries({ queryKey: ['bcm-plans'] })}
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </Button>
          <Dialog open={showNewPlanDialog} onOpenChange={setShowNewPlanDialog}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="w-4 h-4 mr-2" />
                New Plan
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>Create New BCM Plan</DialogTitle>
                <DialogDescription>
                  Define a new business continuity, disaster recovery, or emergency response plan
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4 mt-4">
                <div>
                  <Label>Plan Name</Label>
                  <Input placeholder="Enter plan name" />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label>Plan Type</Label>
                    <Select>
                      <SelectTrigger>
                        <SelectValue placeholder="Select type" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="business_continuity">Business Continuity</SelectItem>
                        <SelectItem value="disaster_recovery">Disaster Recovery</SelectItem>
                        <SelectItem value="crisis_management">Crisis Management</SelectItem>
                        <SelectItem value="emergency_response">Emergency Response</SelectItem>
                        <SelectItem value="it_recovery">IT Recovery</SelectItem>
                        <SelectItem value="communication">Communication</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label>Priority</Label>
                    <Select>
                      <SelectTrigger>
                        <SelectValue placeholder="Select priority" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="critical">Critical</SelectItem>
                        <SelectItem value="high">High</SelectItem>
                        <SelectItem value="medium">Medium</SelectItem>
                        <SelectItem value="low">Low</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <div>
                  <Label>Plan Owner</Label>
                  <Input placeholder="Enter plan owner" />
                </div>
                <div>
                  <Label>Scope</Label>
                  <Input placeholder="Define plan scope (comma-separated)" />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label>RTO (Recovery Time Objective)</Label>
                    <Input type="number" placeholder="Minutes" />
                  </div>
                  <div>
                    <Label>RPO (Recovery Point Objective)</Label>
                    <Input type="number" placeholder="Minutes" />
                  </div>
                </div>
                <div>
                  <Label>Description</Label>
                  <Textarea placeholder="Plan description and objectives" rows={3} />
                </div>
                <div className="flex justify-end gap-2">
                  <Button variant="outline" onClick={() => setShowNewPlanDialog(false)}>
                    Cancel
                  </Button>
                  <Button>
                    <FileText className="w-4 h-4 mr-2" />
                    Create Plan
                  </Button>
                </div>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Critical Alerts */}
      {metrics.overduePlans > 0 && (
        <Alert className="border-red-500 bg-red-50">
          <AlertTriangle className="h-4 w-4 text-red-600" />
          <AlertDescription className="text-red-800">
            <strong>{metrics.overduePlans} plan{metrics.overduePlans > 1 ? 's' : ''}</strong> overdue for testing.
            Regular testing ensures plan effectiveness and compliance.
          </AlertDescription>
        </Alert>
      )}

      {/* Plan Metrics Overview */}
      <div className="grid grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <div className="flex justify-between items-center">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Active Plans
              </CardTitle>
              <Shield className="w-4 h-4 text-green-500" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{metrics.activePlans}</div>
            <div className="text-xs text-muted-foreground mt-1">
              of {metrics.totalPlans} total plans
            </div>
            <Progress value={metrics.activePlans / metrics.totalPlans * 100} className="mt-2" />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <div className="flex justify-between items-center">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Test Coverage
              </CardTitle>
              <Activity className="w-4 h-4 text-blue-500" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">{Math.round(metrics.testCoverage)}%</div>
            <div className="text-xs text-muted-foreground mt-1">
              Plans tested recently
            </div>
            <Progress value={metrics.testCoverage} className="mt-2" />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <div className="flex justify-between items-center">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Avg Effectiveness
              </CardTitle>
              <Target className="w-4 h-4 text-purple-500" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-purple-600">{Math.round(metrics.planEffectiveness)}%</div>
            <div className="text-xs text-muted-foreground mt-1">
              Based on test results
            </div>
            <Progress value={metrics.planEffectiveness} className="mt-2" />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <div className="flex justify-between items-center">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Plans Need Testing
              </CardTitle>
              <Clock className="w-4 h-4 text-orange-500" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">{metrics.plansNeedingTest}</div>
            <div className="text-xs text-muted-foreground mt-1">
              Due within 30 days
            </div>
            <Progress value={metrics.plansNeedingTest / metrics.totalPlans * 100} className="mt-2" />
          </CardContent>
        </Card>
      </div>

      {/* Main Content Tabs */}
      <Tabs value={activeTab} onValueChange={(v: any) => setActiveTab(v)}>
        <TabsList className="grid grid-cols-5 w-full">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="plans">Plans</TabsTrigger>
          <TabsTrigger value="testing">Testing</TabsTrigger>
          <TabsTrigger value="resources">Resources</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="mt-6">
          <div className="grid grid-cols-3 gap-6">
            {/* Recent Activity */}
            <Card>
              <CardHeader>
                <CardTitle>Recent Activity</CardTitle>
                <CardDescription>Latest plan updates and tests</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-green-500 mt-0.5" />
                    <div>
                      <div className="font-medium text-sm">IT DR Plan Tested</div>
                      <div className="text-xs text-muted-foreground">
                        Simulation completed successfully • 2 hours ago
                      </div>
                    </div>
                  </div>
                  <div className="flex items-start gap-2">
                    <FileText className="w-4 h-4 text-blue-500 mt-0.5" />
                    <div>
                      <div className="font-medium text-sm">Crisis Plan Updated</div>
                      <div className="text-xs text-muted-foreground">
                        Version 2.1 approved • 1 day ago
                      </div>
                    </div>
                  </div>
                  <div className="flex items-start gap-2">
                    <AlertTriangle className="w-4 h-4 text-yellow-500 mt-0.5" />
                    <div>
                      <div className="font-medium text-sm">Test Due Soon</div>
                      <div className="text-xs text-muted-foreground">
                        Evacuation plan test in 5 days • Required
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Plan Status Distribution */}
            <Card>
              <CardHeader>
                <CardTitle>Plan Status</CardTitle>
                <CardDescription>Distribution by status</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                      <span className="text-sm">Active</span>
                    </div>
                    <span className="text-sm font-medium">{plans.filter((p: BCMPlan) => p.status === 'active').length}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                      <span className="text-sm">Review</span>
                    </div>
                    <span className="text-sm font-medium">{plans.filter((p: BCMPlan) => p.status === 'review').length}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                      <span className="text-sm">Approved</span>
                    </div>
                    <span className="text-sm font-medium">{plans.filter((p: BCMPlan) => p.status === 'approved').length}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 bg-gray-500 rounded-full"></div>
                      <span className="text-sm">Draft</span>
                    </div>
                    <span className="text-sm font-medium">{plans.filter((p: BCMPlan) => p.status === 'draft').length}</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Quick Actions */}
            <Card>
              <CardHeader>
                <CardTitle>Quick Actions</CardTitle>
                <CardDescription>Common plan management tasks</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <Button variant="outline" className="w-full justify-start">
                    <Play className="w-4 h-4 mr-2" />
                    Schedule Plan Test
                  </Button>
                  <Button variant="outline" className="w-full justify-start">
                    <FileText className="w-4 h-4 mr-2" />
                    Review Pending Plans
                  </Button>
                  <Button variant="outline" className="w-full justify-start">
                    <Users className="w-4 h-4 mr-2" />
                    Update Team Assignments
                  </Button>
                  <Button variant="outline" className="w-full justify-start">
                    <Download className="w-4 h-4 mr-2" />
                    Export Plan Library
                  </Button>
                  <Button variant="outline" className="w-full justify-start">
                    <Calendar className="w-4 h-4 mr-2" />
                    Testing Calendar
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="plans" className="mt-6">
          <Card>
            <CardHeader>
              <div className="flex justify-between items-center">
                <div>
                  <CardTitle>BCM Plans Registry</CardTitle>
                  <CardDescription>Manage all business continuity plans</CardDescription>
                </div>
                <div className="flex gap-2">
                  <div className="relative">
                    <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                    <Input
                      placeholder="Search plans..."
                      className="pl-8 w-64"
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                    />
                  </div>
                  <Select value={filterType} onValueChange={setFilterType}>
                    <SelectTrigger className="w-40">
                      <SelectValue placeholder="Type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Types</SelectItem>
                      <SelectItem value="business_continuity">Business Continuity</SelectItem>
                      <SelectItem value="disaster_recovery">Disaster Recovery</SelectItem>
                      <SelectItem value="crisis_management">Crisis Management</SelectItem>
                      <SelectItem value="emergency_response">Emergency Response</SelectItem>
                      <SelectItem value="it_recovery">IT Recovery</SelectItem>
                      <SelectItem value="communication">Communication</SelectItem>
                    </SelectContent>
                  </Select>
                  <Select value={filterStatus} onValueChange={setFilterStatus}>
                    <SelectTrigger className="w-32">
                      <SelectValue placeholder="Status" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Status</SelectItem>
                      <SelectItem value="draft">Draft</SelectItem>
                      <SelectItem value="review">Review</SelectItem>
                      <SelectItem value="approved">Approved</SelectItem>
                      <SelectItem value="active">Active</SelectItem>
                      <SelectItem value="testing">Testing</SelectItem>
                      <SelectItem value="archived">Archived</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {filteredPlans.map((plan: BCMPlan) => (
                  <div key={plan.id} className="border rounded-lg">
                    <div className="p-4">
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-2">
                            <h3
                              className="font-medium text-lg cursor-pointer hover:text-blue-600"
                              onClick={() => setSelectedPlan(plan)}
                            >
                              {plan.name}
                            </h3>
                            <Badge className={getStatusColor(plan.status)}>
                              {plan.status}
                            </Badge>
                            <Badge
                              variant="outline"
                              className={getPriorityColor(plan.priority)}
                            >
                              {plan.priority}
                            </Badge>
                          </div>
                          <div className="text-sm text-muted-foreground mb-2">
                            {plan.id} • v{plan.version} • {plan.type.replace('_', ' ')} • Owner: {plan.owner}
                          </div>
                          <div className="flex items-center gap-4 text-xs text-muted-foreground">
                            <div className="flex items-center gap-1">
                              <Target className="w-3 h-3" />
                              RTO: {plan.rto} min
                            </div>
                            <div className="flex items-center gap-1">
                              <Clock className="w-3 h-3" />
                              RPO: {plan.rpo} min
                            </div>
                            <div className="flex items-center gap-1">
                              <Calendar className="w-3 h-3" />
                              Last tested: {new Date(plan.lastTested).toLocaleDateString()}
                            </div>
                            <div className="flex items-center gap-1">
                              <MapPin className="w-3 h-3" />
                              Scope: {plan.scope.join(', ')}
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <div className="text-right mr-4">
                            <div className="text-sm font-medium">
                              {plan.completeness}% Complete
                            </div>
                            <Progress value={plan.completeness} className="w-20 mt-1" />
                          </div>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => setExpandedPlan(
                              expandedPlan === plan.id ? null : plan.id
                            )}
                          >
                            {expandedPlan === plan.id ? (
                              <ChevronDown className="w-4 h-4" />
                            ) : (
                              <ChevronRight className="w-4 h-4" />
                            )}
                          </Button>
                        </div>
                      </div>

                      {/* Plan Actions */}
                      <div className="flex gap-2 mt-3">
                        <Button size="sm" variant="outline">
                          <Eye className="w-4 h-4 mr-1" />
                          View
                        </Button>
                        <Button size="sm" variant="outline">
                          <Edit className="w-4 h-4 mr-1" />
                          Edit
                        </Button>
                        <Button size="sm" variant="outline">
                          <Play className="w-4 h-4 mr-1" />
                          Test
                        </Button>
                        <Button size="sm" variant="outline">
                          <Copy className="w-4 h-4 mr-1" />
                          Clone
                        </Button>
                        <Button size="sm" variant="outline">
                          <Download className="w-4 h-4 mr-1" />
                          Export
                        </Button>
                      </div>
                    </div>

                    {/* Expanded Details */}
                    {expandedPlan === plan.id && (
                      <div className="border-t p-4 bg-muted/30">
                        <div className="grid grid-cols-3 gap-4">
                          {/* Plan Steps */}
                          <div>
                            <h4 className="font-medium text-sm mb-2">Plan Steps ({plan.steps.length})</h4>
                            <div className="space-y-1 max-h-40 overflow-y-auto">
                              {plan.steps.slice(0, 5).map((step) => (
                                <div key={step.id} className="text-xs p-2 border rounded">
                                  <div className="flex items-center gap-2 mb-1">
                                    <Badge className={getPhaseColor(step.phase)}>
                                      {step.phase}
                                    </Badge>
                                    <span>#{step.sequenceNumber}</span>
                                  </div>
                                  <div className="font-medium">{step.title}</div>
                                  <div className="text-muted-foreground">
                                    {step.responsible} • {step.estimatedDuration} min
                                  </div>
                                </div>
                              ))}
                              {plan.steps.length > 5 && (
                                <div className="text-xs text-center text-muted-foreground">
                                  +{plan.steps.length - 5} more steps
                                </div>
                              )}
                            </div>
                          </div>

                          {/* Resources */}
                          <div>
                            <h4 className="font-medium text-sm mb-2">Resources ({plan.resources.length})</h4>
                            <div className="space-y-1 max-h-40 overflow-y-auto">
                              {plan.resources.slice(0, 5).map((resource) => (
                                <div key={resource.id} className="text-xs p-2 border rounded">
                                  <div className="font-medium">{resource.name}</div>
                                  <div className="text-muted-foreground capitalize">
                                    {resource.type} • {resource.availability}
                                  </div>
                                  <Badge
                                    variant="outline"
                                    className={
                                      resource.status === 'available' ? 'border-green-500' :
                                      resource.status === 'limited' ? 'border-yellow-500' :
                                      'border-red-500'
                                    }
                                  >
                                    {resource.status}
                                  </Badge>
                                </div>
                              ))}
                              {plan.resources.length > 5 && (
                                <div className="text-xs text-center text-muted-foreground">
                                  +{plan.resources.length - 5} more resources
                                </div>
                              )}
                            </div>
                          </div>

                          {/* Test Results */}
                          <div>
                            <h4 className="font-medium text-sm mb-2">
                              Test Results ({plan.testResults?.length || 0})
                            </h4>
                            {plan.testResults && plan.testResults.length > 0 ? (
                              <div className="space-y-1 max-h-40 overflow-y-auto">
                                {plan.testResults.slice(0, 3).map((test) => (
                                  <div key={test.id} className="text-xs p-2 border rounded">
                                    <div className="font-medium">{test.type} Test</div>
                                    <div className="text-muted-foreground">
                                      {new Date(test.date).toLocaleDateString()} • {test.duration} min
                                    </div>
                                    <div className="flex items-center gap-1 mt-1">
                                      <span>Rating:</span>
                                      <span className={`font-medium ${
                                        test.overallRating >= 80 ? 'text-green-600' :
                                        test.overallRating >= 60 ? 'text-yellow-600' :
                                        'text-red-600'
                                      }`}>
                                        {test.overallRating}%
                                      </span>
                                    </div>
                                  </div>
                                ))}
                              </div>
                            ) : (
                              <div className="text-xs text-muted-foreground">
                                No test results available
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="testing" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Plan Testing</CardTitle>
              <CardDescription>Schedule and track plan testing activities</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {/* Testing Calendar */}
                <div className="grid grid-cols-2 gap-6">
                  <div>
                    <h3 className="text-lg font-medium mb-3">Upcoming Tests</h3>
                    <div className="space-y-3">
                      {plans
                        .filter((p: BCMPlan) => new Date(p.nextTestDate) > new Date())
                        .sort((a: BCMPlan, b: BCMPlan) => new Date(a.nextTestDate).getTime() - new Date(b.nextTestDate).getTime())
                        .slice(0, 5)
                        .map((plan: BCMPlan) => (
                          <div key={plan.id} className="border rounded-lg p-3">
                            <div className="flex justify-between items-center">
                              <div>
                                <div className="font-medium">{plan.name}</div>
                                <div className="text-sm text-muted-foreground">
                                  {plan.type.replace('_', ' ')} • {plan.priority} priority
                                </div>
                              </div>
                              <div className="text-right">
                                <div className="font-medium">
                                  {new Date(plan.nextTestDate).toLocaleDateString()}
                                </div>
                                <Badge
                                  className={
                                    new Date(plan.nextTestDate) < new Date(Date.now() + 7 * 24 * 60 * 60 * 1000)
                                      ? 'bg-red-500' : 'bg-blue-500'
                                  }
                                >
                                  {new Date(plan.nextTestDate) < new Date(Date.now() + 7 * 24 * 60 * 60 * 1000)
                                    ? 'Due Soon' : 'Scheduled'}
                                </Badge>
                              </div>
                            </div>
                            <div className="flex gap-2 mt-2">
                              <Button size="sm">Schedule Test</Button>
                              <Button size="sm" variant="outline">View Plan</Button>
                            </div>
                          </div>
                        ))}
                    </div>
                  </div>

                  <div>
                    <h3 className="text-lg font-medium mb-3">Recent Test Results</h3>
                    <div className="space-y-3">
                      {plans
                        .filter((p: BCMPlan) => p.testResults && p.testResults.length > 0)
                        .slice(0, 5)
                        .map((plan: BCMPlan) => {
                          const latestTest = plan.testResults![0]
                          return (
                            <div key={plan.id} className="border rounded-lg p-3">
                              <div className="flex justify-between items-start">
                                <div>
                                  <div className="font-medium">{plan.name}</div>
                                  <div className="text-sm text-muted-foreground">
                                    {latestTest.type} test • {new Date(latestTest.date).toLocaleDateString()}
                                  </div>
                                </div>
                                <div className="text-right">
                                  <div className={`text-lg font-bold ${
                                    latestTest.overallRating >= 80 ? 'text-green-600' :
                                    latestTest.overallRating >= 60 ? 'text-yellow-600' :
                                    'text-red-600'
                                  }`}>
                                    {latestTest.overallRating}%
                                  </div>
                                  <div className="text-xs text-muted-foreground">
                                    {latestTest.results.length} findings
                                  </div>
                                </div>
                              </div>
                              <div className="mt-2">
                                <Button size="sm" variant="outline">View Results</Button>
                              </div>
                            </div>
                          )
                        })}
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="resources" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Plan Resources</CardTitle>
              <CardDescription>Manage resources across all plans</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {/* Resource Summary */}
                <div className="grid grid-cols-5 gap-4">
                  <Card>
                    <CardContent className="p-4 text-center">
                      <Users className="w-6 h-6 mx-auto mb-2 text-blue-500" />
                      <div className="text-2xl font-bold">45</div>
                      <div className="text-xs text-muted-foreground">Personnel</div>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardContent className="p-4 text-center">
                      <Settings className="w-6 h-6 mx-auto mb-2 text-green-500" />
                      <div className="text-2xl font-bold">23</div>
                      <div className="text-xs text-muted-foreground">Equipment</div>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardContent className="p-4 text-center">
                      <MapPin className="w-6 h-6 mx-auto mb-2 text-purple-500" />
                      <div className="text-2xl font-bold">8</div>
                      <div className="text-xs text-muted-foreground">Facilities</div>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardContent className="p-4 text-center">
                      <Zap className="w-6 h-6 mx-auto mb-2 text-yellow-500" />
                      <div className="text-2xl font-bold">12</div>
                      <div className="text-xs text-muted-foreground">Services</div>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardContent className="p-4 text-center">
                      <FileText className="w-6 h-6 mx-auto mb-2 text-red-500" />
                      <div className="text-2xl font-bold">156</div>
                      <div className="text-xs text-muted-foreground">Documents</div>
                    </CardContent>
                  </Card>
                </div>

                {/* Resource Status */}
                <div>
                  <h3 className="text-lg font-medium mb-3">Resource Readiness</h3>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between p-3 border rounded">
                      <div className="flex items-center gap-3">
                        <CheckCircle className="w-5 h-5 text-green-500" />
                        <div>
                          <div className="font-medium">Critical Resources</div>
                          <div className="text-sm text-muted-foreground">All critical resources available</div>
                        </div>
                      </div>
                      <Badge className="bg-green-500">100% Ready</Badge>
                    </div>
                    <div className="flex items-center justify-between p-3 border rounded">
                      <div className="flex items-center gap-3">
                        <AlertCircle className="w-5 h-5 text-yellow-500" />
                        <div>
                          <div className="font-medium">Backup Facilities</div>
                          <div className="text-sm text-muted-foreground">Some facilities under maintenance</div>
                        </div>
                      </div>
                      <Badge className="bg-yellow-500">85% Ready</Badge>
                    </div>
                    <div className="flex items-center justify-between p-3 border rounded">
                      <div className="flex items-center gap-3">
                        <Users className="w-5 h-5 text-blue-500" />
                        <div>
                          <div className="font-medium">Response Teams</div>
                          <div className="text-sm text-muted-foreground">All teams trained and available</div>
                        </div>
                      </div>
                      <Badge className="bg-green-500">98% Ready</Badge>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="analytics" className="mt-6">
          <div className="grid grid-cols-2 gap-6">
            {/* Plan Effectiveness Trends */}
            <Card>
              <CardHeader>
                <CardTitle>Plan Effectiveness Trends</CardTitle>
                <CardDescription>Test results over time</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {plans
                    .filter((p: BCMPlan) => p.effectiveness)
                    .sort((a: BCMPlan, b: BCMPlan) => (b.effectiveness || 0) - (a.effectiveness || 0))
                    .slice(0, 5)
                    .map((plan: BCMPlan) => (
                      <div key={plan.id} className="space-y-2">
                        <div className="flex justify-between items-center">
                          <span className="text-sm font-medium">{plan.name}</span>
                          <span className={`text-sm font-bold ${
                            (plan.effectiveness || 0) >= 80 ? 'text-green-600' :
                            (plan.effectiveness || 0) >= 60 ? 'text-yellow-600' :
                            'text-red-600'
                          }`}>
                            {plan.effectiveness}%
                          </span>
                        </div>
                        <Progress value={plan.effectiveness || 0} className="h-2" />
                      </div>
                    ))}
                </div>
              </CardContent>
            </Card>

            {/* Plan Maturity Assessment */}
            <Card>
              <CardHeader>
                <CardTitle>Plan Maturity</CardTitle>
                <CardDescription>Overall plan quality assessment</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-sm">Documentation Completeness</span>
                      <span className="text-sm font-medium">{Math.round(metrics.averageCompleteness)}%</span>
                    </div>
                    <Progress value={metrics.averageCompleteness} className="h-2" />
                  </div>
                  <div>
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-sm">Test Coverage</span>
                      <span className="text-sm font-medium">{Math.round(metrics.testCoverage)}%</span>
                    </div>
                    <Progress value={metrics.testCoverage} className="h-2" />
                  </div>
                  <div>
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-sm">Resource Readiness</span>
                      <span className="text-sm font-medium">{metrics.resourceReadiness}%</span>
                    </div>
                    <Progress value={metrics.resourceReadiness} className="h-2" />
                  </div>
                  <div>
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-sm">Plan Effectiveness</span>
                      <span className="text-sm font-medium">{Math.round(metrics.planEffectiveness)}%</span>
                    </div>
                    <Progress value={metrics.planEffectiveness} className="h-2" />
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>

      {/* Selected Plan Detail Modal */}
      {selectedPlan && (
        <Dialog open={!!selectedPlan} onOpenChange={() => setSelectedPlan(null)}>
          <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
            <DialogHeader>
              <div className="flex justify-between items-start">
                <div>
                  <DialogTitle className="text-xl">{selectedPlan.name}</DialogTitle>
                  <DialogDescription>
                    {selectedPlan.id} • Version {selectedPlan.version} • {selectedPlan.type.replace('_', ' ')}
                  </DialogDescription>
                </div>
                <div className="flex gap-2">
                  <Badge className={getStatusColor(selectedPlan.status)}>
                    {selectedPlan.status}
                  </Badge>
                  <Badge variant="outline" className={getPriorityColor(selectedPlan.priority)}>
                    {selectedPlan.priority}
                  </Badge>
                </div>
              </div>
            </DialogHeader>
            <div className="space-y-6 mt-6">
              {/* Plan Summary */}
              <div>
                <h3 className="font-medium mb-2">Plan Summary</h3>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-muted-foreground">Owner:</span>
                    <span className="ml-2">{selectedPlan.owner}</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Last Updated:</span>
                    <span className="ml-2">{new Date(selectedPlan.lastUpdated).toLocaleDateString()}</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">RTO:</span>
                    <span className="ml-2">{selectedPlan.rto} minutes</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">RPO:</span>
                    <span className="ml-2">{selectedPlan.rpo} minutes</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Last Tested:</span>
                    <span className="ml-2">{new Date(selectedPlan.lastTested).toLocaleDateString()}</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Next Test:</span>
                    <span className="ml-2">{new Date(selectedPlan.nextTestDate).toLocaleDateString()}</span>
                  </div>
                </div>
              </div>

              {/* Activation Triggers */}
              <div>
                <h3 className="font-medium mb-2">Activation Triggers</h3>
                <ul className="list-disc list-inside space-y-1 text-sm">
                  {selectedPlan.activationTriggers.map((trigger, i) => (
                    <li key={i}>{trigger}</li>
                  ))}
                </ul>
              </div>

              {/* Scope */}
              <div>
                <h3 className="font-medium mb-2">Scope</h3>
                <div className="flex flex-wrap gap-2">
                  {selectedPlan.scope.map((item) => (
                    <Badge key={item} variant="secondary">{item}</Badge>
                  ))}
                </div>
              </div>

              {/* Plan Steps Preview */}
              {selectedPlan.steps.length > 0 && (
                <div>
                  <h3 className="font-medium mb-2">Plan Steps ({selectedPlan.steps.length})</h3>
                  <div className="space-y-2 max-h-60 overflow-y-auto">
                    {selectedPlan.steps.slice(0, 10).map((step) => (
                      <div key={step.id} className="border rounded p-2">
                        <div className="flex items-center justify-between mb-1">
                          <div className="flex items-center gap-2">
                            <Badge className={getPhaseColor(step.phase)}>
                              {step.phase}
                            </Badge>
                            <span className="text-sm font-medium">#{step.sequenceNumber} {step.title}</span>
                          </div>
                          <span className="text-xs text-muted-foreground">
                            {step.estimatedDuration} min
                          </span>
                        </div>
                        <div className="text-xs text-muted-foreground">
                          {step.description}
                        </div>
                        <div className="text-xs text-muted-foreground mt-1">
                          Responsible: {step.responsible}
                        </div>
                      </div>
                    ))}
                    {selectedPlan.steps.length > 10 && (
                      <div className="text-center text-sm text-muted-foreground">
                        +{selectedPlan.steps.length - 10} more steps
                      </div>
                    )}
                  </div>
                </div>
              )}

              <div className="flex justify-end gap-2 pt-4 border-t">
                <Button variant="outline">
                  <Download className="w-4 h-4 mr-2" />
                  Export
                </Button>
                <Button variant="outline">
                  <Edit className="w-4 h-4 mr-2" />
                  Edit
                </Button>
                <Button>
                  <Play className="w-4 h-4 mr-2" />
                  Test Plan
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      )}
    </div>
  )
}