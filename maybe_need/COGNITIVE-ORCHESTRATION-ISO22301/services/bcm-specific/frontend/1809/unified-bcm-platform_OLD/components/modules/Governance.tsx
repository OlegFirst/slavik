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
import { Checkbox } from '@/components/ui/checkbox'
import {
  FileText,
  Users,
  Shield,
  CheckCircle,
  XCircle,
  Clock,
  AlertCircle,
  TrendingUp,
  BookOpen,
  Gavel,
  Award,
  Calendar,
  GitBranch,
  Lock,
  Unlock,
  Edit,
  Eye,
  Download,
  Upload,
  RefreshCw,
  Search,
  Filter,
  ChevronRight,
  BarChart3,
  Target,
  Activity,
  Archive,
  Settings,
  Info
} from 'lucide-react'
import { apiClient } from '@/lib/api-client'
import { useBCMStore } from '@/lib/bcm-store'

// Types
interface Policy {
  id: string
  title: string
  type: 'policy' | 'procedure' | 'guideline' | 'standard'
  category: string
  version: string
  status: 'draft' | 'review' | 'approved' | 'published' | 'archived'
  owner: string
  approvedBy?: string[]
  effectiveDate: string
  reviewDate: string
  nextReviewDate: string
  compliance: number // percentage
  relatedDocuments: string[]
  tags: string[]
  content?: string
  changeLog: ChangeRecord[]
  approvalWorkflow?: ApprovalStep[]
}

interface ChangeRecord {
  id: string
  version: string
  date: string
  author: string
  description: string
  type: 'major' | 'minor' | 'editorial'
}

interface ApprovalStep {
  id: string
  role: string
  approver?: string
  status: 'pending' | 'approved' | 'rejected'
  comments?: string
  date?: string
}

interface ComplianceFramework {
  id: string
  name: string
  standard: string
  version: string
  requirements: ComplianceRequirement[]
  overallCompliance: number
  lastAuditDate?: string
  nextAuditDate?: string
  certificationStatus?: 'certified' | 'in_progress' | 'expired' | 'not_started'
  certificationExpiry?: string
}

interface ComplianceRequirement {
  id: string
  clause: string
  description: string
  status: 'compliant' | 'partial' | 'non_compliant' | 'not_applicable'
  evidence?: string[]
  controls: string[]
  gaps?: string[]
  remediation?: string
  responsible: string
  dueDate?: string
}

interface GovernanceMetric {
  id: string
  name: string
  category: 'policy' | 'compliance' | 'training' | 'audit'
  value: number
  target: number
  trend: 'up' | 'down' | 'stable'
  period: string
}

interface AuditRecord {
  id: string
  type: 'internal' | 'external' | 'certification'
  scope: string
  auditor: string
  date: string
  status: 'planned' | 'in_progress' | 'completed' | 'cancelled'
  findings: AuditFinding[]
  recommendations: string[]
  followUpRequired: boolean
  nextAuditDate?: string
}

interface AuditFinding {
  id: string
  severity: 'critical' | 'major' | 'minor' | 'observation'
  category: string
  description: string
  evidence?: string
  recommendation: string
  responsibleParty: string
  targetDate: string
  status: 'open' | 'in_progress' | 'closed'
}

interface Role {
  id: string
  name: string
  description: string
  responsibilities: string[]
  permissions: Permission[]
  members: string[]
  reportingTo?: string
  delegates?: string[]
  lastReviewed: string
}

interface Permission {
  resource: string
  actions: ('create' | 'read' | 'update' | 'delete' | 'approve')[]
}

// Mock data
const generateMockPolicies = (): Policy[] => {
  return [
    {
      id: 'POL-001',
      title: 'Business Continuity Management Policy',
      type: 'policy',
      category: 'Core BCM',
      version: '2.0',
      status: 'published',
      owner: 'BCM Manager',
      approvedBy: ['CEO', 'Board of Directors'],
      effectiveDate: '2024-01-01',
      reviewDate: '2024-01-01',
      nextReviewDate: '2025-01-01',
      compliance: 95,
      relatedDocuments: ['PROC-001', 'PROC-002'],
      tags: ['bcm', 'governance', 'iso-22301'],
      changeLog: [
        {
          id: 'CH001',
          version: '2.0',
          date: '2024-01-01',
          author: 'John Doe',
          description: 'Annual review and update',
          type: 'minor'
        }
      ]
    },
    {
      id: 'PROC-001',
      title: 'Incident Response Procedure',
      type: 'procedure',
      category: 'Operations',
      version: '1.5',
      status: 'published',
      owner: 'Operations Manager',
      approvedBy: ['BCM Manager', 'COO'],
      effectiveDate: '2024-02-01',
      reviewDate: '2024-02-01',
      nextReviewDate: '2024-08-01',
      compliance: 88,
      relatedDocuments: ['POL-001', 'GUIDE-003'],
      tags: ['incident', 'response', 'operations'],
      changeLog: []
    },
    {
      id: 'STD-001',
      title: 'BCM Documentation Standards',
      type: 'standard',
      category: 'Documentation',
      version: '1.0',
      status: 'review',
      owner: 'Quality Manager',
      effectiveDate: '2024-03-01',
      reviewDate: '2024-03-01',
      nextReviewDate: '2024-09-01',
      compliance: 75,
      relatedDocuments: [],
      tags: ['documentation', 'standards'],
      changeLog: [],
      approvalWorkflow: [
        {
          id: 'AW001',
          role: 'BCM Manager',
          status: 'approved',
          approver: 'John Doe',
          date: '2024-03-10'
        },
        {
          id: 'AW002',
          role: 'Quality Manager',
          status: 'pending'
        }
      ]
    }
  ]
}

const generateMockFrameworks = (): ComplianceFramework[] => {
  return [
    {
      id: 'FW-001',
      name: 'ISO 22301:2019',
      standard: 'Business Continuity Management Systems',
      version: '2019',
      requirements: [
        {
          id: 'REQ-4.1',
          clause: '4.1',
          description: 'Understanding the organization and its context',
          status: 'compliant',
          controls: ['CTR-001', 'CTR-002'],
          responsible: 'BCM Manager'
        },
        {
          id: 'REQ-4.2',
          clause: '4.2',
          description: 'Understanding the needs and expectations of interested parties',
          status: 'partial',
          controls: ['CTR-003'],
          gaps: ['Stakeholder register incomplete'],
          remediation: 'Complete stakeholder analysis by Q2 2024',
          responsible: 'BCM Manager',
          dueDate: '2024-06-30'
        },
        {
          id: 'REQ-5.1',
          clause: '5.1',
          description: 'Leadership and commitment',
          status: 'compliant',
          controls: ['CTR-004', 'CTR-005'],
          responsible: 'Senior Management'
        }
      ],
      overallCompliance: 82,
      lastAuditDate: '2023-11-15',
      nextAuditDate: '2024-11-15',
      certificationStatus: 'certified',
      certificationExpiry: '2025-11-15'
    },
    {
      id: 'FW-002',
      name: 'NIST Cybersecurity Framework',
      standard: 'Cybersecurity Framework',
      version: '1.1',
      requirements: [],
      overallCompliance: 75,
      certificationStatus: 'in_progress'
    }
  ]
}

const generateMockAudits = (): AuditRecord[] => {
  return [
    {
      id: 'AUD-001',
      type: 'internal',
      scope: 'BCM Process Audit',
      auditor: 'Internal Audit Team',
      date: '2024-01-15',
      status: 'completed',
      findings: [
        {
          id: 'F001',
          severity: 'minor',
          category: 'Documentation',
          description: 'Some procedures lack version control',
          recommendation: 'Implement document management system',
          responsibleParty: 'Quality Manager',
          targetDate: '2024-03-31',
          status: 'in_progress'
        },
        {
          id: 'F002',
          severity: 'major',
          category: 'Training',
          description: 'BCM training completion rate below target',
          evidence: 'Training records show 65% completion',
          recommendation: 'Mandate BCM training for all staff',
          responsibleParty: 'HR Manager',
          targetDate: '2024-02-28',
          status: 'open'
        }
      ],
      recommendations: [
        'Enhance document control process',
        'Increase training frequency',
        'Implement automated compliance monitoring'
      ],
      followUpRequired: true,
      nextAuditDate: '2024-07-15'
    }
  ]
}

export function GovernanceModule() {
  const queryClient = useQueryClient()
  const { publishEvent } = useBCMStore()

  const [activeTab, setActiveTab] = useState<'policies' | 'compliance' | 'roles' | 'audit' | 'metrics'>('policies')
  const [selectedPolicy, setSelectedPolicy] = useState<Policy | null>(null)
  const [showNewPolicyDialog, setShowNewPolicyDialog] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterType, setFilterType] = useState<string>('all')
  const [filterStatus, setFilterStatus] = useState<string>('all')

  // Fetch policies
  const { data: policies = [], isLoading: policiesLoading } = useQuery({
    queryKey: ['governance-policies'],
    queryFn: async () => {
      // API client doesn't have get method, using mock data
      return generateMockPolicies()
    }
  })

  // Fetch compliance frameworks
  const { data: frameworks = [] } = useQuery({
    queryKey: ['compliance-frameworks'],
    queryFn: async () => {
      // API client doesn't have get method
      return generateMockFrameworks()
    }
  })

  // Fetch audit records
  const { data: audits = [] } = useQuery({
    queryKey: ['audit-records'],
    queryFn: async () => {
      // API client doesn't have get method
      return generateMockAudits()
    }
  })

  // Calculate governance metrics
  const metrics: GovernanceMetric[] = [
    {
      id: 'M001',
      name: 'Policy Compliance',
      category: 'policy',
      value: policies.reduce((acc, p) => acc + p.compliance, 0) / (policies.length || 1),
      target: 90,
      trend: 'up',
      period: 'Monthly'
    },
    {
      id: 'M002',
      name: 'ISO 22301 Compliance',
      category: 'compliance',
      value: frameworks.find(f => f.id === 'FW-001')?.overallCompliance || 0,
      target: 85,
      trend: 'stable',
      period: 'Quarterly'
    },
    {
      id: 'M003',
      name: 'Audit Findings Closure',
      category: 'audit',
      value: 72,
      target: 95,
      trend: 'up',
      period: 'Monthly'
    },
    {
      id: 'M004',
      name: 'Training Completion',
      category: 'training',
      value: 65,
      target: 90,
      trend: 'down',
      period: 'Monthly'
    }
  ]

  // Filter policies
  const filteredPolicies = policies.filter((policy: Policy) => {
    const matchesSearch = policy.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         policy.category.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesType = filterType === 'all' || policy.type === filterType
    const matchesStatus = filterStatus === 'all' || policy.status === filterStatus
    return matchesSearch && matchesType && matchesStatus
  })

  // Get status color
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'published': return 'bg-green-500'
      case 'approved': return 'bg-blue-500'
      case 'review': return 'bg-yellow-500'
      case 'draft': return 'bg-gray-500'
      case 'archived': return 'bg-red-500'
      default: return 'bg-gray-500'
    }
  }

  // Get compliance color
  const getComplianceColor = (value: number) => {
    if (value >= 90) return 'text-green-600'
    if (value >= 70) return 'text-yellow-600'
    return 'text-red-600'
  }

  // Get severity color
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'bg-red-500'
      case 'major': return 'bg-orange-500'
      case 'minor': return 'bg-yellow-500'
      case 'observation': return 'bg-blue-500'
      default: return 'bg-gray-500'
    }
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Governance</h1>
          <p className="text-muted-foreground mt-1">
            Manage policies, compliance, roles and audit activities
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={() => queryClient.invalidateQueries({ queryKey: ['governance-policies'] })}
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </Button>
          <Dialog open={showNewPolicyDialog} onOpenChange={setShowNewPolicyDialog}>
            <DialogTrigger asChild>
              <Button>
                <FileText className="w-4 h-4 mr-2" />
                New Policy
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>Create New Policy Document</DialogTitle>
                <DialogDescription>
                  Define a new policy, procedure, guideline or standard
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4 mt-4">
                <div>
                  <Label>Document Title</Label>
                  <Input placeholder="Enter document title" />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label>Type</Label>
                    <Select>
                      <SelectTrigger>
                        <SelectValue placeholder="Select type" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="policy">Policy</SelectItem>
                        <SelectItem value="procedure">Procedure</SelectItem>
                        <SelectItem value="guideline">Guideline</SelectItem>
                        <SelectItem value="standard">Standard</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label>Category</Label>
                    <Select>
                      <SelectTrigger>
                        <SelectValue placeholder="Select category" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="core-bcm">Core BCM</SelectItem>
                        <SelectItem value="operations">Operations</SelectItem>
                        <SelectItem value="hr">Human Resources</SelectItem>
                        <SelectItem value="it">Information Technology</SelectItem>
                        <SelectItem value="compliance">Compliance</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <div>
                  <Label>Document Owner</Label>
                  <Input placeholder="Enter owner name or role" />
                </div>
                <div>
                  <Label>Description</Label>
                  <Textarea placeholder="Brief description of the document" rows={3} />
                </div>
                <div>
                  <Label>Related Documents</Label>
                  <Input placeholder="Enter related document IDs (comma-separated)" />
                </div>
                <div>
                  <Label>Tags</Label>
                  <Input placeholder="Enter tags (comma-separated)" />
                </div>
                <div className="flex justify-end gap-2">
                  <Button variant="outline" onClick={() => setShowNewPolicyDialog(false)}>
                    Cancel
                  </Button>
                  <Button>
                    <FileText className="w-4 h-4 mr-2" />
                    Create Document
                  </Button>
                </div>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Governance Metrics Overview */}
      <div className="grid grid-cols-4 gap-4">
        {metrics.map((metric) => (
          <Card key={metric.id}>
            <CardHeader className="pb-2">
              <div className="flex justify-between items-center">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  {metric.name}
                </CardTitle>
                {metric.trend === 'up' ? (
                  <TrendingUp className="w-4 h-4 text-green-500" />
                ) : metric.trend === 'down' ? (
                  <TrendingUp className="w-4 h-4 text-red-500 rotate-180" />
                ) : (
                  <Activity className="w-4 h-4 text-blue-500" />
                )}
              </div>
            </CardHeader>
            <CardContent>
              <div className={`text-2xl font-bold ${getComplianceColor(metric.value)}`}>
                {Math.round(metric.value)}%
              </div>
              <Progress
                value={metric.value}
                className="mt-2"
              />
              <div className="flex justify-between text-xs text-muted-foreground mt-1">
                <span>Target: {metric.target}%</span>
                <span>{metric.period}</span>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Compliance Alert */}
      {metrics.some(m => m.value < m.target * 0.8) && (
        <Alert className="border-yellow-500 bg-yellow-50">
          <AlertCircle className="h-4 w-4 text-yellow-600" />
          <AlertDescription className="text-yellow-800">
            Some governance metrics are below target. Review compliance requirements and take corrective actions.
          </AlertDescription>
        </Alert>
      )}

      {/* Main Content Tabs */}
      <Tabs value={activeTab} onValueChange={(v: any) => setActiveTab(v)}>
        <TabsList className="grid grid-cols-5 w-full">
          <TabsTrigger value="policies">Policies</TabsTrigger>
          <TabsTrigger value="compliance">Compliance</TabsTrigger>
          <TabsTrigger value="roles">Roles & Responsibilities</TabsTrigger>
          <TabsTrigger value="audit">Audit</TabsTrigger>
          <TabsTrigger value="metrics">Metrics</TabsTrigger>
        </TabsList>

        <TabsContent value="policies" className="mt-6">
          <Card>
            <CardHeader>
              <div className="flex justify-between items-center">
                <div>
                  <CardTitle>Policy Documents</CardTitle>
                  <CardDescription>Manage organizational policies, procedures and standards</CardDescription>
                </div>
                <div className="flex gap-2">
                  <div className="relative">
                    <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                    <Input
                      placeholder="Search documents..."
                      className="pl-8 w-64"
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                    />
                  </div>
                  <Select value={filterType} onValueChange={setFilterType}>
                    <SelectTrigger className="w-32">
                      <SelectValue placeholder="Type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Types</SelectItem>
                      <SelectItem value="policy">Policy</SelectItem>
                      <SelectItem value="procedure">Procedure</SelectItem>
                      <SelectItem value="guideline">Guideline</SelectItem>
                      <SelectItem value="standard">Standard</SelectItem>
                    </SelectContent>
                  </Select>
                  <Select value={filterStatus} onValueChange={setFilterStatus}>
                    <SelectTrigger className="w-32">
                      <SelectValue placeholder="Status" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Status</SelectItem>
                      <SelectItem value="draft">Draft</SelectItem>
                      <SelectItem value="review">In Review</SelectItem>
                      <SelectItem value="approved">Approved</SelectItem>
                      <SelectItem value="published">Published</SelectItem>
                      <SelectItem value="archived">Archived</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="border rounded-lg">
                <table className="w-full">
                  <thead className="border-b bg-muted/50">
                    <tr>
                      <th className="text-left p-3 font-medium">Document</th>
                      <th className="text-left p-3 font-medium">Type</th>
                      <th className="text-left p-3 font-medium">Version</th>
                      <th className="text-left p-3 font-medium">Status</th>
                      <th className="text-left p-3 font-medium">Owner</th>
                      <th className="text-left p-3 font-medium">Compliance</th>
                      <th className="text-left p-3 font-medium">Next Review</th>
                      <th className="text-left p-3 font-medium">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredPolicies.map((policy: Policy) => (
                      <tr key={policy.id} className="border-b hover:bg-accent">
                        <td className="p-3">
                          <div>
                            <div className="font-medium">{policy.title}</div>
                            <div className="text-xs text-muted-foreground">
                              {policy.id} • {policy.category}
                            </div>
                          </div>
                        </td>
                        <td className="p-3 capitalize">{policy.type}</td>
                        <td className="p-3">v{policy.version}</td>
                        <td className="p-3">
                          <Badge className={getStatusColor(policy.status)}>
                            {policy.status}
                          </Badge>
                        </td>
                        <td className="p-3">{policy.owner}</td>
                        <td className="p-3">
                          <div className="flex items-center gap-2">
                            <Progress value={policy.compliance} className="w-16" />
                            <span className={`text-sm font-medium ${getComplianceColor(policy.compliance)}`}>
                              {policy.compliance}%
                            </span>
                          </div>
                        </td>
                        <td className="p-3 text-sm">
                          {new Date(policy.nextReviewDate).toLocaleDateString()}
                        </td>
                        <td className="p-3">
                          <div className="flex gap-1">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => setSelectedPolicy(policy)}
                            >
                              <Eye className="w-4 h-4" />
                            </Button>
                            <Button variant="ghost" size="sm">
                              <Edit className="w-4 h-4" />
                            </Button>
                            <Button variant="ghost" size="sm">
                              <Download className="w-4 h-4" />
                            </Button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="compliance" className="mt-6">
          <div className="space-y-6">
            {frameworks.map((framework: ComplianceFramework) => (
              <Card key={framework.id}>
                <CardHeader>
                  <div className="flex justify-between items-center">
                    <div>
                      <CardTitle>{framework.name}</CardTitle>
                      <CardDescription>
                        {framework.standard} • Version {framework.version}
                      </CardDescription>
                    </div>
                    <div className="flex items-center gap-4">
                      {framework.certificationStatus && (
                        <Badge
                          className={
                            framework.certificationStatus === 'certified' ? 'bg-green-500' :
                            framework.certificationStatus === 'in_progress' ? 'bg-yellow-500' :
                            framework.certificationStatus === 'expired' ? 'bg-red-500' :
                            'bg-gray-500'
                          }
                        >
                          <Award className="w-3 h-3 mr-1" />
                          {framework.certificationStatus === 'certified' ? 'Certified' :
                           framework.certificationStatus === 'in_progress' ? 'In Progress' :
                           framework.certificationStatus === 'expired' ? 'Expired' :
                           'Not Started'}
                        </Badge>
                      )}
                      <div className="text-right">
                        <div className={`text-2xl font-bold ${getComplianceColor(framework.overallCompliance)}`}>
                          {framework.overallCompliance}%
                        </div>
                        <div className="text-xs text-muted-foreground">Overall Compliance</div>
                      </div>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex justify-between text-sm text-muted-foreground">
                      <div>
                        Last Audit: {framework.lastAuditDate ? new Date(framework.lastAuditDate).toLocaleDateString() : 'N/A'}
                      </div>
                      <div>
                        Next Audit: {framework.nextAuditDate ? new Date(framework.nextAuditDate).toLocaleDateString() : 'N/A'}
                      </div>
                      {framework.certificationExpiry && (
                        <div>
                          Certification Expires: {new Date(framework.certificationExpiry).toLocaleDateString()}
                        </div>
                      )}
                    </div>

                    {framework.requirements.length > 0 && (
                      <>
                        <Separator />
                        <div>
                          <h4 className="text-sm font-medium mb-3">Requirements Status</h4>
                          <div className="space-y-2">
                            {framework.requirements.slice(0, 5).map((req) => (
                              <div key={req.id} className="flex items-center justify-between p-2 border rounded">
                                <div className="flex items-center gap-2">
                                  {req.status === 'compliant' ? (
                                    <CheckCircle className="w-4 h-4 text-green-500" />
                                  ) : req.status === 'partial' ? (
                                    <AlertCircle className="w-4 h-4 text-yellow-500" />
                                  ) : req.status === 'non_compliant' ? (
                                    <AlertCircle className="w-4 h-4 text-red-500" />
                                  ) : (
                                    <Info className="w-4 h-4 text-gray-500" />
                                  )}
                                  <div>
                                    <div className="font-medium text-sm">Clause {req.clause}</div>
                                    <div className="text-xs text-muted-foreground">{req.description}</div>
                                  </div>
                                </div>
                                <div className="text-right">
                                  <Badge
                                    variant="outline"
                                    className={
                                      req.status === 'compliant' ? 'border-green-500 text-green-700' :
                                      req.status === 'partial' ? 'border-yellow-500 text-yellow-700' :
                                      req.status === 'non_compliant' ? 'border-red-500 text-red-700' :
                                      'border-gray-500 text-gray-700'
                                    }
                                  >
                                    {req.status.replace('_', ' ')}
                                  </Badge>
                                  {req.dueDate && (
                                    <div className="text-xs text-muted-foreground mt-1">
                                      Due: {new Date(req.dueDate).toLocaleDateString()}
                                    </div>
                                  )}
                                </div>
                              </div>
                            ))}
                          </div>
                          {framework.requirements.length > 5 && (
                            <Button variant="link" className="w-full mt-2">
                              View all {framework.requirements.length} requirements
                              <ChevronRight className="w-4 h-4 ml-1" />
                            </Button>
                          )}
                        </div>
                      </>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="roles" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Roles & Responsibilities</CardTitle>
              <CardDescription>Define and manage BCM roles and permissions</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {/* BCM Organization Chart */}
                <div className="border rounded-lg p-4">
                  <h3 className="text-lg font-medium mb-4">BCM Organization Structure</h3>
                  <div className="space-y-3">
                    <div className="flex items-center gap-4 p-3 border rounded bg-blue-50">
                      <Shield className="w-5 h-5 text-blue-600" />
                      <div className="flex-1">
                        <div className="font-medium">BCM Steering Committee</div>
                        <div className="text-sm text-muted-foreground">Strategic oversight and governance</div>
                      </div>
                      <Badge>5 members</Badge>
                    </div>
                    <div className="ml-8 space-y-2">
                      <div className="flex items-center gap-4 p-3 border rounded">
                        <Users className="w-5 h-5" />
                        <div className="flex-1">
                          <div className="font-medium">BCM Manager</div>
                          <div className="text-sm text-muted-foreground">Day-to-day BCM operations</div>
                        </div>
                        <Badge variant="outline">John Doe</Badge>
                      </div>
                      <div className="ml-8 space-y-2">
                        <div className="flex items-center gap-4 p-2 border rounded">
                          <div className="flex-1">
                            <div className="text-sm font-medium">Crisis Management Team</div>
                            <div className="text-xs text-muted-foreground">Incident response coordination</div>
                          </div>
                          <Badge variant="outline">8 members</Badge>
                        </div>
                        <div className="flex items-center gap-4 p-2 border rounded">
                          <div className="flex-1">
                            <div className="text-sm font-medium">Recovery Teams</div>
                            <div className="text-xs text-muted-foreground">Operational recovery execution</div>
                          </div>
                          <Badge variant="outline">15 members</Badge>
                        </div>
                        <div className="flex items-center gap-4 p-2 border rounded">
                          <div className="flex-1">
                            <div className="text-sm font-medium">BCM Coordinators</div>
                            <div className="text-xs text-muted-foreground">Department-level BCM activities</div>
                          </div>
                          <Badge variant="outline">12 members</Badge>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Role Permissions Matrix */}
                <div className="border rounded-lg p-4">
                  <h3 className="text-lg font-medium mb-4">Role Permissions</h3>
                  <div className="border rounded">
                    <table className="w-full text-sm">
                      <thead className="border-b bg-muted/50">
                        <tr>
                          <th className="text-left p-2">Role</th>
                          <th className="text-center p-2">View</th>
                          <th className="text-center p-2">Create</th>
                          <th className="text-center p-2">Edit</th>
                          <th className="text-center p-2">Approve</th>
                          <th className="text-center p-2">Delete</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr className="border-b">
                          <td className="p-2 font-medium">BCM Manager</td>
                          <td className="text-center p-2"><CheckCircle className="w-4 h-4 text-green-500 mx-auto" /></td>
                          <td className="text-center p-2"><CheckCircle className="w-4 h-4 text-green-500 mx-auto" /></td>
                          <td className="text-center p-2"><CheckCircle className="w-4 h-4 text-green-500 mx-auto" /></td>
                          <td className="text-center p-2"><CheckCircle className="w-4 h-4 text-green-500 mx-auto" /></td>
                          <td className="text-center p-2"><CheckCircle className="w-4 h-4 text-green-500 mx-auto" /></td>
                        </tr>
                        <tr className="border-b">
                          <td className="p-2 font-medium">BCM Coordinator</td>
                          <td className="text-center p-2"><CheckCircle className="w-4 h-4 text-green-500 mx-auto" /></td>
                          <td className="text-center p-2"><CheckCircle className="w-4 h-4 text-green-500 mx-auto" /></td>
                          <td className="text-center p-2"><CheckCircle className="w-4 h-4 text-green-500 mx-auto" /></td>
                          <td className="text-center p-2">-</td>
                          <td className="text-center p-2">-</td>
                        </tr>
                        <tr className="border-b">
                          <td className="p-2 font-medium">Team Member</td>
                          <td className="text-center p-2"><CheckCircle className="w-4 h-4 text-green-500 mx-auto" /></td>
                          <td className="text-center p-2">-</td>
                          <td className="text-center p-2">-</td>
                          <td className="text-center p-2">-</td>
                          <td className="text-center p-2">-</td>
                        </tr>
                        <tr>
                          <td className="p-2 font-medium">Auditor</td>
                          <td className="text-center p-2"><CheckCircle className="w-4 h-4 text-green-500 mx-auto" /></td>
                          <td className="text-center p-2">-</td>
                          <td className="text-center p-2">-</td>
                          <td className="text-center p-2">-</td>
                          <td className="text-center p-2">-</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="audit" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Audit Management</CardTitle>
              <CardDescription>Track audit activities and findings</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {audits.map((audit: AuditRecord) => (
                  <div key={audit.id} className="border rounded-lg p-4">
                    <div className="flex justify-between items-start mb-4">
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          <h3 className="font-medium text-lg">{audit.scope}</h3>
                          <Badge
                            className={
                              audit.status === 'completed' ? 'bg-green-500' :
                              audit.status === 'in_progress' ? 'bg-yellow-500' :
                              audit.status === 'planned' ? 'bg-blue-500' :
                              'bg-gray-500'
                            }
                          >
                            {audit.status.replace('_', ' ')}
                          </Badge>
                          <Badge variant="outline" className="capitalize">
                            {audit.type} Audit
                          </Badge>
                        </div>
                        <div className="text-sm text-muted-foreground">
                          {audit.id} • Auditor: {audit.auditor} • Date: {new Date(audit.date).toLocaleDateString()}
                        </div>
                      </div>
                      {audit.followUpRequired && (
                        <Badge className="bg-orange-500">
                          <Clock className="w-3 h-3 mr-1" />
                          Follow-up Required
                        </Badge>
                      )}
                    </div>

                    {audit.findings.length > 0 && (
                      <div className="space-y-2 mb-4">
                        <h4 className="text-sm font-medium">Findings</h4>
                        {audit.findings.map((finding) => (
                          <div key={finding.id} className="flex items-start gap-2 p-2 border rounded">
                            <Badge className={`mt-0.5 ${getSeverityColor(finding.severity)}`}>
                              {finding.severity}
                            </Badge>
                            <div className="flex-1">
                              <div className="text-sm">{finding.description}</div>
                              <div className="text-xs text-muted-foreground mt-1">
                                {finding.category} • Responsible: {finding.responsibleParty} •
                                Target: {new Date(finding.targetDate).toLocaleDateString()}
                              </div>
                            </div>
                            <Badge
                              variant="outline"
                              className={
                                finding.status === 'closed' ? 'border-green-500' :
                                finding.status === 'in_progress' ? 'border-yellow-500' :
                                'border-red-500'
                              }
                            >
                              {finding.status.replace('_', ' ')}
                            </Badge>
                          </div>
                        ))}
                      </div>
                    )}

                    {audit.recommendations.length > 0 && (
                      <div>
                        <h4 className="text-sm font-medium mb-2">Recommendations</h4>
                        <ul className="list-disc list-inside space-y-1 text-sm text-muted-foreground">
                          {audit.recommendations.map((rec, i) => (
                            <li key={i}>{rec}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {audit.nextAuditDate && (
                      <div className="mt-4 pt-4 border-t text-sm text-muted-foreground">
                        Next Audit Scheduled: {new Date(audit.nextAuditDate).toLocaleDateString()}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="metrics" className="mt-6">
          <div className="grid grid-cols-2 gap-6">
            {/* Metric Trends */}
            <Card>
              <CardHeader>
                <CardTitle>Governance Metrics Trends</CardTitle>
                <CardDescription>Performance over time</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {metrics.map((metric) => (
                    <div key={metric.id} className="border rounded-lg p-3">
                      <div className="flex justify-between items-center mb-2">
                        <span className="font-medium text-sm">{metric.name}</span>
                        <div className="flex items-center gap-2">
                          <span className={`text-lg font-bold ${getComplianceColor(metric.value)}`}>
                            {Math.round(metric.value)}%
                          </span>
                          {metric.trend === 'up' ? (
                            <TrendingUp className="w-4 h-4 text-green-500" />
                          ) : metric.trend === 'down' ? (
                            <TrendingUp className="w-4 h-4 text-red-500 rotate-180" />
                          ) : (
                            <Activity className="w-4 h-4 text-blue-500" />
                          )}
                        </div>
                      </div>
                      <Progress value={metric.value} className="h-2" />
                      <div className="flex justify-between text-xs text-muted-foreground mt-1">
                        <span>Target: {metric.target}%</span>
                        <span>{metric.period}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Action Items */}
            <Card>
              <CardHeader>
                <CardTitle>Action Items</CardTitle>
                <CardDescription>Pending governance activities</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-start gap-2">
                    <Clock className="w-4 h-4 text-orange-500 mt-0.5" />
                    <div>
                      <div className="font-medium text-sm">Policy Reviews Due</div>
                      <div className="text-xs text-muted-foreground">3 policies require annual review</div>
                      <Button size="sm" variant="link" className="px-0 h-auto">
                        Review Now <ChevronRight className="w-3 h-3 ml-1" />
                      </Button>
                    </div>
                  </div>
                  <Separator />
                  <div className="flex items-start gap-2">
                    <AlertCircle className="w-4 h-4 text-red-500 mt-0.5" />
                    <div>
                      <div className="font-medium text-sm">Open Audit Findings</div>
                      <div className="text-xs text-muted-foreground">5 findings pending closure</div>
                      <Button size="sm" variant="link" className="px-0 h-auto">
                        View Findings <ChevronRight className="w-3 h-3 ml-1" />
                      </Button>
                    </div>
                  </div>
                  <Separator />
                  <div className="flex items-start gap-2">
                    <Target className="w-4 h-4 text-yellow-500 mt-0.5" />
                    <div>
                      <div className="font-medium text-sm">Compliance Gaps</div>
                      <div className="text-xs text-muted-foreground">2 requirements need attention</div>
                      <Button size="sm" variant="link" className="px-0 h-auto">
                        Address Gaps <ChevronRight className="w-3 h-3 ml-1" />
                      </Button>
                    </div>
                  </div>
                  <Separator />
                  <div className="flex items-start gap-2">
                    <Users className="w-4 h-4 text-blue-500 mt-0.5" />
                    <div>
                      <div className="font-medium text-sm">Training Completion</div>
                      <div className="text-xs text-muted-foreground">BCM training at 65% completion</div>
                      <Button size="sm" variant="link" className="px-0 h-auto">
                        View Report <ChevronRight className="w-3 h-3 ml-1" />
                      </Button>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>

      {/* Selected Policy Detail Modal */}
      {selectedPolicy && (
        <Dialog open={!!selectedPolicy} onOpenChange={() => setSelectedPolicy(null)}>
          <DialogContent className="max-w-3xl max-h-[80vh] overflow-y-auto">
            <DialogHeader>
              <div className="flex justify-between items-start">
                <div>
                  <DialogTitle className="text-xl">{selectedPolicy.title}</DialogTitle>
                  <DialogDescription>
                    {selectedPolicy.id} • Version {selectedPolicy.version} • {selectedPolicy.category}
                  </DialogDescription>
                </div>
                <div className="flex gap-2">
                  <Badge className={getStatusColor(selectedPolicy.status)}>
                    {selectedPolicy.status}
                  </Badge>
                </div>
              </div>
            </DialogHeader>
            <div className="space-y-6 mt-6">
              {/* Policy Details */}
              <div>
                <h3 className="font-medium mb-2">Document Information</h3>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-muted-foreground">Owner:</span>
                    <span className="ml-2">{selectedPolicy.owner}</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Type:</span>
                    <span className="ml-2 capitalize">{selectedPolicy.type}</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Effective Date:</span>
                    <span className="ml-2">{new Date(selectedPolicy.effectiveDate).toLocaleDateString()}</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Review Date:</span>
                    <span className="ml-2">{new Date(selectedPolicy.reviewDate).toLocaleDateString()}</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Next Review:</span>
                    <span className="ml-2">{new Date(selectedPolicy.nextReviewDate).toLocaleDateString()}</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Compliance:</span>
                    <span className={`ml-2 font-medium ${getComplianceColor(selectedPolicy.compliance)}`}>
                      {selectedPolicy.compliance}%
                    </span>
                  </div>
                </div>
              </div>

              {/* Approval Workflow */}
              {selectedPolicy.approvalWorkflow && selectedPolicy.approvalWorkflow.length > 0 && (
                <div>
                  <h3 className="font-medium mb-2">Approval Workflow</h3>
                  <div className="space-y-2">
                    {selectedPolicy.approvalWorkflow.map((step) => (
                      <div key={step.id} className="flex items-center justify-between p-2 border rounded">
                        <div className="flex items-center gap-2">
                          {step.status === 'approved' ? (
                            <CheckCircle className="w-4 h-4 text-green-500" />
                          ) : step.status === 'rejected' ? (
                            <XCircle className="w-4 h-4 text-red-500" />
                          ) : (
                            <Clock className="w-4 h-4 text-yellow-500" />
                          )}
                          <span className="text-sm">{step.role}</span>
                        </div>
                        {step.approver && (
                          <div className="text-sm text-muted-foreground">
                            {step.approver} • {step.date}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Related Documents */}
              {selectedPolicy.relatedDocuments.length > 0 && (
                <div>
                  <h3 className="font-medium mb-2">Related Documents</h3>
                  <div className="flex flex-wrap gap-2">
                    {selectedPolicy.relatedDocuments.map((docId) => (
                      <Badge key={docId} variant="outline">
                        <FileText className="w-3 h-3 mr-1" />
                        {docId}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              {/* Tags */}
              {selectedPolicy.tags.length > 0 && (
                <div>
                  <h3 className="font-medium mb-2">Tags</h3>
                  <div className="flex flex-wrap gap-2">
                    {selectedPolicy.tags.map((tag) => (
                      <Badge key={tag} variant="secondary">
                        {tag}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              {/* Change Log */}
              {selectedPolicy.changeLog.length > 0 && (
                <div>
                  <h3 className="font-medium mb-2">Change History</h3>
                  <div className="space-y-2">
                    {selectedPolicy.changeLog.map((change) => (
                      <div key={change.id} className="text-sm border rounded p-2">
                        <div className="flex justify-between">
                          <span className="font-medium">Version {change.version}</span>
                          <span className="text-muted-foreground">{new Date(change.date).toLocaleDateString()}</span>
                        </div>
                        <div className="text-muted-foreground">
                          {change.description} • {change.author}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="flex justify-end gap-2 pt-4 border-t">
                <Button variant="outline">
                  <Download className="w-4 h-4 mr-2" />
                  Download
                </Button>
                <Button variant="outline">
                  <Edit className="w-4 h-4 mr-2" />
                  Edit
                </Button>
                <Button variant="outline">
                  <Archive className="w-4 h-4 mr-2" />
                  Archive
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      )}
    </div>
  )
}