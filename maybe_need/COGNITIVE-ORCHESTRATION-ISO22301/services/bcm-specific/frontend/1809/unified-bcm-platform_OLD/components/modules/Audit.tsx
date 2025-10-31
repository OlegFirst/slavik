'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useBCMStore } from '@/lib/store'
import { apiClient } from '@/lib/api-client'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Calendar } from '@/components/ui/calendar'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { Textarea } from '@/components/ui/textarea'
import { Checkbox } from '@/components/ui/checkbox'
import { Progress } from '@/components/ui/progress'
import {
  FileText,
  Calendar as CalendarIcon,
  Filter,
  Plus,
  Search,
  Download,
  Upload,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Clock,
  Users,
  Target,
  BarChart3,
  TrendingUp,
  Eye,
  Edit,
  Send,
  BookOpen,
  Shield,
  Award,
  AlertCircle
} from 'lucide-react'
import { format } from 'date-fns'
import { cn } from '@/lib/utils'

// Types
interface AuditAction {
  id: string
  title: string
  description: string
  responsible: string
  priority: 'critical' | 'high' | 'medium' | 'low'
  status: 'open' | 'in_progress' | 'completed' | 'overdue'
  dueDate: string
  createdDate: string
  category: string
  evidence?: string[]
}

interface AuditFinding {
  id: string
  title: string
  description: string
  severity: 'critical' | 'major' | 'minor' | 'observation'
  category: 'documentation' | 'process' | 'system' | 'compliance' | 'training'
  status: 'open' | 'addressed' | 'verified' | 'closed'
  auditId: string
  actions: AuditAction[]
  evidence: string[]
  createdDate: string
  updatedDate: string
}

interface Audit {
  id: string
  title: string
  type: 'internal' | 'external' | 'management_review' | 'certification'
  scope: string[]
  status: 'planned' | 'in_progress' | 'completed' | 'cancelled'
  startDate: string
  endDate: string
  auditors: string[]
  auditees: string[]
  objectives: string[]
  findings: AuditFinding[]
  overallRating: 'excellent' | 'good' | 'satisfactory' | 'needs_improvement' | 'unsatisfactory'
  reportUrl?: string
  nextAuditDate?: string
}

interface AuditPlan {
  id: string
  year: number
  objectives: string[]
  scope: string[]
  schedule: {
    quarter: 1 | 2 | 3 | 4
    audits: Audit[]
  }[]
  resources: {
    internalAuditors: number
    externalAuditors: number
    budget: number
  }
  riskAreas: string[]
}

// Mock Data
const generateMockAudits = (): Audit[] => [
  {
    id: 'audit-001',
    title: 'ISO 22301 Annual Certification Audit',
    type: 'certification',
    scope: ['BCM Policy', 'Risk Assessment', 'BIA', 'Business Continuity Plans', 'Testing'],
    status: 'completed',
    startDate: '2024-09-01',
    endDate: '2024-09-05',
    auditors: ['John Smith (Lead)', 'Sarah Johnson', 'Mike Chen'],
    auditees: ['BCM Manager', 'IT Director', 'HR Manager', 'Operations Manager'],
    objectives: [
      'Verify compliance with ISO 22301:2019',
      'Assess effectiveness of BCM system',
      'Identify areas for improvement'
    ],
    findings: [
      {
        id: 'finding-001',
        title: 'Incomplete BIA for New Department',
        description: 'Business Impact Analysis was not updated to include the newly established Digital Innovation Department',
        severity: 'major',
        category: 'documentation',
        status: 'addressed',
        auditId: 'audit-001',
        actions: [
          {
            id: 'action-001',
            title: 'Complete BIA for Digital Innovation Department',
            description: 'Conduct comprehensive BIA including RTO/RPO analysis',
            responsible: 'BCM Manager',
            priority: 'high',
            status: 'completed',
            dueDate: '2024-10-15',
            createdDate: '2024-09-03',
            category: 'documentation'
          }
        ],
        evidence: ['BIA_Digital_Innovation_v1.0.pdf', 'Impact_Analysis_Report.pdf'],
        createdDate: '2024-09-03',
        updatedDate: '2024-10-10'
      }
    ],
    overallRating: 'good',
    reportUrl: '/reports/audit-001-final-report.pdf',
    nextAuditDate: '2025-09-01'
  },
  {
    id: 'audit-002',
    title: 'Business Continuity Plans Review',
    type: 'internal',
    scope: ['Recovery Plans', 'Communication Plans', 'Crisis Management'],
    status: 'in_progress',
    startDate: '2024-11-01',
    endDate: '2024-11-15',
    auditors: ['Internal Audit Team', 'BCM Coordinator'],
    auditees: ['Department Heads', 'Crisis Team Members'],
    objectives: [
      'Review plan adequacy and currency',
      'Test plan accessibility',
      'Verify staff awareness'
    ],
    findings: [],
    overallRating: 'satisfactory'
  },
  {
    id: 'audit-003',
    title: 'Q4 Management Review',
    type: 'management_review',
    scope: ['BCM Performance', 'Resource Allocation', 'Strategic Alignment'],
    status: 'planned',
    startDate: '2024-12-15',
    endDate: '2024-12-15',
    auditors: ['Executive Management'],
    auditees: ['BCM Manager', 'Department Heads'],
    objectives: [
      'Review BCM effectiveness',
      'Assess resource needs',
      'Set objectives for next year'
    ],
    findings: [],
    overallRating: 'satisfactory'
  }
]

const generateMockFindings = (): AuditFinding[] => [
  {
    id: 'finding-002',
    title: 'Outdated Emergency Contact List',
    description: 'Several key personnel contact details in the emergency contact database are outdated',
    severity: 'minor',
    category: 'documentation',
    status: 'open',
    auditId: 'audit-002',
    actions: [
      {
        id: 'action-002',
        title: 'Update Emergency Contact Database',
        description: 'Verify and update all emergency contact information',
        responsible: 'HR Manager',
        priority: 'medium',
        status: 'in_progress',
        dueDate: '2024-11-30',
        createdDate: '2024-11-05',
        category: 'documentation'
      }
    ],
    evidence: ['Contact_Audit_Report.xlsx'],
    createdDate: '2024-11-05',
    updatedDate: '2024-11-05'
  },
  {
    id: 'finding-003',
    title: 'Insufficient Training Records',
    description: 'BCM training completion records are incomplete for 15% of staff',
    severity: 'major',
    category: 'training',
    status: 'open',
    auditId: 'audit-001',
    actions: [
      {
        id: 'action-003',
        title: 'Complete Training Record Audit',
        description: 'Identify missing training records and schedule makeup sessions',
        responsible: 'Training Coordinator',
        priority: 'high',
        status: 'open',
        dueDate: '2024-12-01',
        createdDate: '2024-09-04',
        category: 'training'
      }
    ],
    evidence: ['Training_Records_Audit.xlsx', 'Staff_Training_Matrix.pdf'],
    createdDate: '2024-09-04',
    updatedDate: '2024-09-04'
  }
]

const generateMockActions = (): AuditAction[] => [
  {
    id: 'action-004',
    title: 'Implement Automated Backup Verification',
    description: 'Set up automated system to verify backup integrity daily',
    responsible: 'IT Manager',
    priority: 'critical',
    status: 'overdue',
    dueDate: '2024-10-01',
    createdDate: '2024-08-15',
    category: 'system',
    evidence: ['Backup_System_Spec.pdf']
  },
  {
    id: 'action-005',
    title: 'Update BCM Policy Documentation',
    description: 'Revise BCM policy to reflect organizational changes',
    responsible: 'BCM Manager',
    priority: 'medium',
    status: 'in_progress',
    dueDate: '2024-12-15',
    createdDate: '2024-10-01',
    category: 'documentation'
  }
]

const generateMockAuditPlan = (): AuditPlan => ({
  id: 'plan-2024',
  year: 2024,
  objectives: [
    'Maintain ISO 22301 certification',
    'Improve BCM maturity level',
    'Enhance crisis response capabilities',
    'Strengthen vendor resilience'
  ],
  scope: [
    'Business Continuity Management System',
    'Crisis Management Procedures',
    'IT Recovery Plans',
    'Communication Systems',
    'Training and Awareness'
  ],
  schedule: [
    {
      quarter: 1,
      audits: []
    },
    {
      quarter: 2,
      audits: []
    },
    {
      quarter: 3,
      audits: [
        {
          id: 'audit-001',
          title: 'ISO 22301 Annual Certification Audit',
          type: 'certification',
          scope: ['BCM Policy', 'Risk Assessment', 'BIA'],
          status: 'completed',
          startDate: '2024-09-01',
          endDate: '2024-09-05',
          auditors: ['John Smith (Lead)'],
          auditees: ['BCM Manager'],
          objectives: [],
          findings: [],
          overallRating: 'good'
        }
      ]
    },
    {
      quarter: 4,
      audits: [
        {
          id: 'audit-002',
          title: 'Business Continuity Plans Review',
          type: 'internal',
          scope: ['Recovery Plans'],
          status: 'in_progress',
          startDate: '2024-11-01',
          endDate: '2024-11-15',
          auditors: ['Internal Audit Team'],
          auditees: ['Department Heads'],
          objectives: [],
          findings: [],
          overallRating: 'satisfactory'
        }
      ]
    }
  ],
  resources: {
    internalAuditors: 3,
    externalAuditors: 2,
    budget: 25000
  },
  riskAreas: [
    'IT Infrastructure',
    'Supply Chain',
    'Human Resources',
    'Facilities'
  ]
})

export function AuditModule() {
  const [activeTab, setActiveTab] = useState('overview')
  const [searchTerm, setSearchTerm] = useState('')
  const [filterStatus, setFilterStatus] = useState<string>('all')
  const [filterType, setFilterType] = useState<string>('all')
  const [filterSeverity, setFilterSeverity] = useState<string>('all')
  const [selectedDate, setSelectedDate] = useState<Date>()

  // Store integration
  const { currentModule, setCurrentModule } = useBCMStore()

  // Data fetching
  const { data: audits = [], isLoading: loadingAudits } = useQuery({
    queryKey: ['audits'],
    queryFn: async () => {
      if (process.env.NEXT_PUBLIC_USE_REAL_API === 'true') {
        // return await apiClient.audits.getAll() // API not implemented yet
        return generateMockAudits()
      }
      return generateMockAudits()
    }
  })

  const { data: findings = [], isLoading: loadingFindings } = useQuery({
    queryKey: ['audit-findings'],
    queryFn: async () => {
      if (process.env.NEXT_PUBLIC_USE_REAL_API === 'true') {
        // return await apiClient.audits.getFindings() // API not implemented yet
        return generateMockFindings()
      }
      return generateMockFindings()
    }
  })

  const { data: actions = [], isLoading: loadingActions } = useQuery({
    queryKey: ['audit-actions'],
    queryFn: async () => {
      if (process.env.NEXT_PUBLIC_USE_REAL_API === 'true') {
        // return await apiClient.audits.getActions() // API not implemented yet
        return generateMockActions()
      }
      return generateMockActions()
    }
  })

  const { data: auditPlan, isLoading: loadingPlan } = useQuery({
    queryKey: ['audit-plan'],
    queryFn: async () => {
      if (process.env.NEXT_PUBLIC_USE_REAL_API === 'true') {
        // return await apiClient.audits.getPlan() // API not implemented yet
        return generateMockAuditPlan()
      }
      return generateMockAuditPlan()
    }
  })

  // Metrics calculations
  const totalAudits = audits.length
  const completedAudits = audits.filter(a => a.status === 'completed').length
  const inProgressAudits = audits.filter(a => a.status === 'in_progress').length
  const plannedAudits = audits.filter(a => a.status === 'planned').length

  const totalFindings = findings.length
  const openFindings = findings.filter(f => f.status === 'open').length
  const addressedFindings = findings.filter(f => f.status === 'addressed').length
  const closedFindings = findings.filter(f => f.status === 'closed').length

  const criticalFindings = findings.filter(f => f.severity === 'critical').length
  const majorFindings = findings.filter(f => f.severity === 'major').length
  const minorFindings = findings.filter(f => f.severity === 'minor').length

  const totalActions = actions.length
  const openActions = actions.filter(a => a.status === 'open').length
  const inProgressActions = actions.filter(a => a.status === 'in_progress').length
  const completedActions = actions.filter(a => a.status === 'completed').length
  const overdueActions = actions.filter(a => a.status === 'overdue').length

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'text-red-600 bg-red-50'
      case 'major': return 'text-orange-600 bg-orange-50'
      case 'minor': return 'text-yellow-600 bg-yellow-50'
      case 'observation': return 'text-blue-600 bg-blue-50'
      default: return 'text-gray-600 bg-gray-50'
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': case 'closed': case 'addressed': return 'text-green-600 bg-green-50'
      case 'in_progress': case 'verified': return 'text-blue-600 bg-blue-50'
      case 'open': case 'planned': return 'text-orange-600 bg-orange-50'
      case 'overdue': case 'cancelled': return 'text-red-600 bg-red-50'
      default: return 'text-gray-600 bg-gray-50'
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical': return 'text-red-600 bg-red-50'
      case 'high': return 'text-orange-600 bg-orange-50'
      case 'medium': return 'text-yellow-600 bg-yellow-50'
      case 'low': return 'text-green-600 bg-green-50'
      default: return 'text-gray-600 bg-gray-50'
    }
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Audit Management</h1>
          <p className="text-gray-600 mt-1">Manage internal and external audits, findings, and corrective actions</p>
        </div>
        <div className="flex items-center space-x-3">
          <Button variant="outline">
            <Download className="h-4 w-4 mr-2" />
            Export Reports
          </Button>
          <Button>
            <Plus className="h-4 w-4 mr-2" />
            Schedule Audit
          </Button>
        </div>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="audits">Audits</TabsTrigger>
          <TabsTrigger value="findings">Findings</TabsTrigger>
          <TabsTrigger value="actions">Actions</TabsTrigger>
          <TabsTrigger value="planning">Planning</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-6">
          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Audits</CardTitle>
                <BookOpen className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{totalAudits}</div>
                <div className="text-xs text-muted-foreground mt-1">
                  {completedAudits} completed, {inProgressAudits} in progress
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Open Findings</CardTitle>
                <AlertTriangle className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{openFindings}</div>
                <div className="text-xs text-muted-foreground mt-1">
                  {criticalFindings} critical, {majorFindings} major
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Pending Actions</CardTitle>
                <Target className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{openActions + inProgressActions}</div>
                <div className="text-xs text-muted-foreground mt-1">
                  {overdueActions} overdue actions
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Completion Rate</CardTitle>
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {totalActions > 0 ? Math.round((completedActions / totalActions) * 100) : 0}%
                </div>
                <div className="text-xs text-muted-foreground mt-1">
                  Action completion rate
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Recent Audits */}
          <Card>
            <CardHeader>
              <CardTitle>Recent Audits</CardTitle>
              <CardDescription>Latest audit activities and status updates</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {audits.slice(0, 3).map((audit) => (
                  <div key={audit.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex-1">
                      <h4 className="font-medium">{audit.title}</h4>
                      <p className="text-sm text-gray-600">{audit.scope.join(', ')}</p>
                      <div className="flex items-center space-x-4 mt-2">
                        <span className="text-xs text-gray-500">
                          {format(new Date(audit.startDate), 'MMM dd, yyyy')} - {format(new Date(audit.endDate), 'MMM dd, yyyy')}
                        </span>
                        <Badge variant="outline" className={getStatusColor(audit.status)}>
                          {audit.status.replace('_', ' ')}
                        </Badge>
                        <Badge variant="outline">
                          {audit.type.replace('_', ' ')}
                        </Badge>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      {audit.overallRating && (
                        <Badge className={
                          audit.overallRating === 'excellent' ? 'bg-green-100 text-green-800' :
                          audit.overallRating === 'good' ? 'bg-blue-100 text-blue-800' :
                          audit.overallRating === 'satisfactory' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-red-100 text-red-800'
                        }>
                          {audit.overallRating}
                        </Badge>
                      )}
                      <Button variant="ghost" >
                        <Eye className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Critical Findings */}
          <Card>
            <CardHeader>
              <CardTitle>Critical & High Priority Findings</CardTitle>
              <CardDescription>Findings requiring immediate attention</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {findings
                  .filter(f => f.severity === 'critical' || f.severity === 'major')
                  .slice(0, 5)
                  .map((finding) => (
                    <div key={finding.id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex-1">
                        <h4 className="font-medium">{finding.title}</h4>
                        <p className="text-sm text-gray-600">{finding.description}</p>
                        <div className="flex items-center space-x-4 mt-2">
                          <Badge variant="outline" className={getSeverityColor(finding.severity)}>
                            {finding.severity}
                          </Badge>
                          <Badge variant="outline" className={getStatusColor(finding.status)}>
                            {finding.status.replace('_', ' ')}
                          </Badge>
                          <span className="text-xs text-gray-500">
                            {finding.actions.length} action(s)
                          </span>
                        </div>
                      </div>
                      <Button variant="ghost" >
                        <Edit className="h-4 w-4" />
                      </Button>
                    </div>
                  ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Audits Tab */}
        <TabsContent value="audits" className="space-y-6">
          {/* Filters */}
          <Card>
            <CardHeader>
              <CardTitle>Filters & Search</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="relative">
                  <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                  <Input
                    placeholder="Search audits..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10"
                  />
                </div>
                <Select value={filterStatus} onValueChange={setFilterStatus}>
                  <SelectTrigger>
                    <SelectValue placeholder="Filter by status" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Status</SelectItem>
                    <SelectItem value="planned">Planned</SelectItem>
                    <SelectItem value="in_progress">In Progress</SelectItem>
                    <SelectItem value="completed">Completed</SelectItem>
                    <SelectItem value="cancelled">Cancelled</SelectItem>
                  </SelectContent>
                </Select>
                <Select value={filterType} onValueChange={setFilterType}>
                  <SelectTrigger>
                    <SelectValue placeholder="Filter by type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Types</SelectItem>
                    <SelectItem value="internal">Internal</SelectItem>
                    <SelectItem value="external">External</SelectItem>
                    <SelectItem value="certification">Certification</SelectItem>
                    <SelectItem value="management_review">Management Review</SelectItem>
                  </SelectContent>
                </Select>
                <Popover>
                  <PopoverTrigger asChild>
                    <Button variant="outline" className={cn("justify-start text-left font-normal", !selectedDate && "text-muted-foreground")}>
                      <CalendarIcon className="mr-2 h-4 w-4" />
                      {selectedDate ? format(selectedDate, "PPP") : "Pick a date"}
                    </Button>
                  </PopoverTrigger>
                  <PopoverContent className="w-auto p-0">
                    <Calendar
                      mode="single"
                      selected={selectedDate}
                      onSelect={setSelectedDate}
                      initialFocus
                    />
                  </PopoverContent>
                </Popover>
              </div>
            </CardContent>
          </Card>

          {/* Audits List */}
          <div className="grid gap-6">
            {audits.map((audit) => (
              <Card key={audit.id}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="text-lg">{audit.title}</CardTitle>
                      <CardDescription>
                        {format(new Date(audit.startDate), 'MMM dd, yyyy')} - {format(new Date(audit.endDate), 'MMM dd, yyyy')}
                      </CardDescription>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Badge variant="outline" className={getStatusColor(audit.status)}>
                        {audit.status.replace('_', ' ')}
                      </Badge>
                      <Badge variant="outline">
                        {audit.type.replace('_', ' ')}
                      </Badge>
                      {audit.overallRating && (
                        <Badge className={
                          audit.overallRating === 'excellent' ? 'bg-green-100 text-green-800' :
                          audit.overallRating === 'good' ? 'bg-blue-100 text-blue-800' :
                          audit.overallRating === 'satisfactory' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-red-100 text-red-800'
                        }>
                          {audit.overallRating}
                        </Badge>
                      )}
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <h4 className="font-medium mb-2">Scope</h4>
                      <p className="text-sm text-gray-600">{audit.scope.join(', ')}</p>
                    </div>
                    <div>
                      <h4 className="font-medium mb-2">Objectives</h4>
                      <ul className="text-sm text-gray-600 list-disc list-inside space-y-1">
                        {audit.objectives.map((objective, index) => (
                          <li key={index}>{objective}</li>
                        ))}
                      </ul>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <h4 className="font-medium mb-2">Auditors</h4>
                        <p className="text-sm text-gray-600">{audit.auditors.join(', ')}</p>
                      </div>
                      <div>
                        <h4 className="font-medium mb-2">Auditees</h4>
                        <p className="text-sm text-gray-600">{audit.auditees.join(', ')}</p>
                      </div>
                    </div>
                    {audit.findings.length > 0 && (
                      <div>
                        <h4 className="font-medium mb-2">Findings Summary</h4>
                        <div className="flex items-center space-x-4">
                          <span className="text-sm text-red-600">{audit.findings.filter(f => f.severity === 'critical').length} Critical</span>
                          <span className="text-sm text-orange-600">{audit.findings.filter(f => f.severity === 'major').length} Major</span>
                          <span className="text-sm text-yellow-600">{audit.findings.filter(f => f.severity === 'minor').length} Minor</span>
                          <span className="text-sm text-blue-600">{audit.findings.filter(f => f.severity === 'observation').length} Observations</span>
                        </div>
                      </div>
                    )}
                    <div className="flex items-center justify-between pt-4 border-t">
                      <div className="flex items-center space-x-4">
                        {audit.reportUrl && (
                          <Button variant="outline" >
                            <FileText className="h-4 w-4 mr-2" />
                            View Report
                          </Button>
                        )}
                        <Button variant="outline" >
                          <Eye className="h-4 w-4 mr-2" />
                          Details
                        </Button>
                      </div>
                      {audit.nextAuditDate && (
                        <span className="text-xs text-gray-500">
                          Next audit: {format(new Date(audit.nextAuditDate), 'MMM dd, yyyy')}
                        </span>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Findings Tab */}
        <TabsContent value="findings" className="space-y-6">
          {/* Findings Filters */}
          <Card>
            <CardHeader>
              <CardTitle>Filter Findings</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <Select value={filterSeverity} onValueChange={setFilterSeverity}>
                  <SelectTrigger>
                    <SelectValue placeholder="Filter by severity" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Severities</SelectItem>
                    <SelectItem value="critical">Critical</SelectItem>
                    <SelectItem value="major">Major</SelectItem>
                    <SelectItem value="minor">Minor</SelectItem>
                    <SelectItem value="observation">Observation</SelectItem>
                  </SelectContent>
                </Select>
                <Select value={filterStatus} onValueChange={setFilterStatus}>
                  <SelectTrigger>
                    <SelectValue placeholder="Filter by status" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Status</SelectItem>
                    <SelectItem value="open">Open</SelectItem>
                    <SelectItem value="addressed">Addressed</SelectItem>
                    <SelectItem value="verified">Verified</SelectItem>
                    <SelectItem value="closed">Closed</SelectItem>
                  </SelectContent>
                </Select>
                <Input placeholder="Search findings..." />
                <Button variant="outline">
                  <Filter className="h-4 w-4 mr-2" />
                  Apply Filters
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Findings List */}
          <div className="grid gap-6">
            {findings.map((finding) => (
              <Card key={finding.id}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="text-lg">{finding.title}</CardTitle>
                      <CardDescription>{finding.description}</CardDescription>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Badge variant="outline" className={getSeverityColor(finding.severity)}>
                        {finding.severity}
                      </Badge>
                      <Badge variant="outline" className={getStatusColor(finding.status)}>
                        {finding.status.replace('_', ' ')}
                      </Badge>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div>
                        <span className="text-sm font-medium">Category:</span>
                        <p className="text-sm text-gray-600 capitalize">{finding.category.replace('_', ' ')}</p>
                      </div>
                      <div>
                        <span className="text-sm font-medium">Created:</span>
                        <p className="text-sm text-gray-600">{format(new Date(finding.createdDate), 'MMM dd, yyyy')}</p>
                      </div>
                      <div>
                        <span className="text-sm font-medium">Last Updated:</span>
                        <p className="text-sm text-gray-600">{format(new Date(finding.updatedDate), 'MMM dd, yyyy')}</p>
                      </div>
                    </div>

                    {finding.evidence.length > 0 && (
                      <div>
                        <h4 className="font-medium mb-2">Evidence</h4>
                        <div className="flex flex-wrap gap-2">
                          {finding.evidence.map((evidence, index) => (
                            <Badge key={index} variant="outline">
                              <FileText className="h-3 w-3 mr-1" />
                              {evidence}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}

                    {finding.actions.length > 0 && (
                      <div>
                        <h4 className="font-medium mb-2">Corrective Actions ({finding.actions.length})</h4>
                        <div className="space-y-2">
                          {finding.actions.map((action) => (
                            <div key={action.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                              <div className="flex-1">
                                <h5 className="font-medium text-sm">{action.title}</h5>
                                <p className="text-xs text-gray-600">{action.description}</p>
                                <div className="flex items-center space-x-4 mt-1">
                                  <span className="text-xs text-gray-500">Due: {format(new Date(action.dueDate), 'MMM dd, yyyy')}</span>
                                  <Badge variant="outline" className={getPriorityColor(action.priority)} >
                                    {action.priority}
                                  </Badge>
                                  <Badge variant="outline" className={getStatusColor(action.status)} >
                                    {action.status.replace('_', ' ')}
                                  </Badge>
                                </div>
                              </div>
                              <div className="text-xs text-gray-500">
                                {action.responsible}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    <div className="flex items-center justify-between pt-4 border-t">
                      <div className="flex items-center space-x-2">
                        <Button variant="outline" >
                          <Edit className="h-4 w-4 mr-2" />
                          Edit Finding
                        </Button>
                        <Button variant="outline" >
                          <Plus className="h-4 w-4 mr-2" />
                          Add Action
                        </Button>
                      </div>
                      <span className="text-xs text-gray-500">
                        {finding.actions.filter(a => a.status === 'completed').length} of {finding.actions.length} actions completed
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Actions Tab */}
        <TabsContent value="actions" className="space-y-6">
          {/* Actions Summary */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Open Actions</CardTitle>
                <AlertCircle className="h-4 w-4 text-orange-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{openActions}</div>
                <Progress value={(openActions / totalActions) * 100} className="mt-2" />
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">In Progress</CardTitle>
                <Clock className="h-4 w-4 text-blue-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{inProgressActions}</div>
                <Progress value={(inProgressActions / totalActions) * 100} className="mt-2" />
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Completed</CardTitle>
                <CheckCircle className="h-4 w-4 text-green-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{completedActions}</div>
                <Progress value={(completedActions / totalActions) * 100} className="mt-2" />
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Overdue</CardTitle>
                <XCircle className="h-4 w-4 text-red-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{overdueActions}</div>
                <Progress value={(overdueActions / totalActions) * 100} className="mt-2" />
              </CardContent>
            </Card>
          </div>

          {/* Actions List */}
          <Card>
            <CardHeader>
              <CardTitle>Corrective Actions</CardTitle>
              <CardDescription>Track and manage corrective actions from audit findings</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {actions.map((action) => (
                  <div key={action.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <h4 className="font-medium">{action.title}</h4>
                        <Badge variant="outline" className={getPriorityColor(action.priority)}>
                          {action.priority}
                        </Badge>
                        <Badge variant="outline" className={getStatusColor(action.status)}>
                          {action.status.replace('_', ' ')}
                        </Badge>
                      </div>
                      <p className="text-sm text-gray-600 mb-2">{action.description}</p>
                      <div className="flex items-center space-x-4 text-xs text-gray-500">
                        <span>Responsible: {action.responsible}</span>
                        <span>Due: {format(new Date(action.dueDate), 'MMM dd, yyyy')}</span>
                        <span>Category: {action.category}</span>
                        {action.status === 'overdue' && (
                          <Badge variant="destructive" >OVERDUE</Badge>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Button variant="ghost" >
                        <Edit className="h-4 w-4" />
                      </Button>
                      <Button variant="ghost" >
                        <Send className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Planning Tab */}
        <TabsContent value="planning" className="space-y-6">
          {/* Audit Plan Overview */}
          {auditPlan && (
            <>
              <Card>
                <CardHeader>
                  <CardTitle>Audit Plan {auditPlan.year}</CardTitle>
                  <CardDescription>Annual audit schedule and resource allocation</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-6">
                    <div>
                      <h4 className="font-medium mb-3">Plan Objectives</h4>
                      <ul className="space-y-2">
                        {auditPlan.objectives.map((objective, index) => (
                          <li key={index} className="flex items-center space-x-2">
                            <CheckCircle className="h-4 w-4 text-green-500" />
                            <span className="text-sm">{objective}</span>
                          </li>
                        ))}
                      </ul>
                    </div>

                    <div>
                      <h4 className="font-medium mb-3">Scope Areas</h4>
                      <div className="flex flex-wrap gap-2">
                        {auditPlan.scope.map((area, index) => (
                          <Badge key={index} variant="outline">{area}</Badge>
                        ))}
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                      <div>
                        <h4 className="font-medium mb-2">Resources</h4>
                        <div className="space-y-2 text-sm">
                          <div className="flex justify-between">
                            <span>Internal Auditors:</span>
                            <span>{auditPlan.resources.internalAuditors}</span>
                          </div>
                          <div className="flex justify-between">
                            <span>External Auditors:</span>
                            <span>{auditPlan.resources.externalAuditors}</span>
                          </div>
                          <div className="flex justify-between">
                            <span>Budget:</span>
                            <span>${auditPlan.resources.budget.toLocaleString()}</span>
                          </div>
                        </div>
                      </div>

                      <div>
                        <h4 className="font-medium mb-2">Risk Areas</h4>
                        <div className="space-y-1">
                          {auditPlan.riskAreas.map((area, index) => (
                            <div key={index} className="text-sm text-gray-600">{area}</div>
                          ))}
                        </div>
                      </div>

                      <div>
                        <h4 className="font-medium mb-2">Schedule Overview</h4>
                        <div className="space-y-2 text-sm">
                          {auditPlan.schedule.map((quarter) => (
                            <div key={quarter.quarter} className="flex justify-between">
                              <span>Q{quarter.quarter}:</span>
                              <span>{quarter.audits.length} audit(s)</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Quarterly Schedule */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {auditPlan.schedule.map((quarter) => (
                  <Card key={quarter.quarter}>
                    <CardHeader>
                      <CardTitle>Q{quarter.quarter} {auditPlan.year}</CardTitle>
                      <CardDescription>{quarter.audits.length} scheduled audits</CardDescription>
                    </CardHeader>
                    <CardContent>
                      {quarter.audits.length > 0 ? (
                        <div className="space-y-3">
                          {quarter.audits.map((audit) => (
                            <div key={audit.id} className="p-3 border rounded-lg">
                              <div className="flex items-center justify-between mb-2">
                                <h4 className="font-medium text-sm">{audit.title}</h4>
                                <Badge variant="outline" className={getStatusColor(audit.status)}>
                                  {audit.status.replace('_', ' ')}
                                </Badge>
                              </div>
                              <p className="text-xs text-gray-600 mb-2">{audit.scope.join(', ')}</p>
                              <div className="text-xs text-gray-500">
                                {format(new Date(audit.startDate), 'MMM dd')} - {format(new Date(audit.endDate), 'MMM dd')}
                              </div>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div className="text-center py-6">
                          <Calendar className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                          <p className="text-sm text-gray-500">No audits scheduled</p>
                          <Button variant="outline"  className="mt-2">
                            <Plus className="h-4 w-4 mr-2" />
                            Schedule Audit
                          </Button>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                ))}
              </div>
            </>
          )}
        </TabsContent>
      </Tabs>
    </div>
  )
}