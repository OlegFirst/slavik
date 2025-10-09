'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { format } from 'date-fns'
import { useBCMStore } from '@/lib/store'
import { apiClient } from '@/lib/api-client'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { Checkbox } from '@/components/ui/checkbox'
import { Progress } from '@/components/ui/progress'
import { Separator } from '@/components/ui/separator'
import {
  Building2,
  Users,
  MapPin,
  Shield,
  Zap,
  Globe,
  Scale,
  Target,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  Clock,
  Plus,
  Edit,
  Search,
  Filter,
  Download,
  Upload,
  Eye,
  Network,
  FileText,
  Settings,
  BarChart3,
  PieChart
} from 'lucide-react'

// Types
interface Stakeholder {
  id: string
  name: string
  organization: string
  role: string
  type: 'internal' | 'external'
  category: 'employee' | 'customer' | 'supplier' | 'regulator' | 'partner' | 'investor' | 'community'
  influence: 'high' | 'medium' | 'low'
  interest: 'high' | 'medium' | 'low'
  requirements: string[]
  contactInfo: {
    email?: string
    phone?: string
    address?: string
  }
  engagementLevel: 'actively_engaged' | 'informed' | 'consulted' | 'minimal'
  lastEngagement?: string
}

interface ExternalContext {
  id: string
  type: 'political' | 'economic' | 'social' | 'technological' | 'legal' | 'environmental'
  title: string
  description: string
  impact: 'high' | 'medium' | 'low'
  likelihood: 'high' | 'medium' | 'low'
  timeframe: 'immediate' | 'short_term' | 'medium_term' | 'long_term'
  trends: string[]
  implications: string[]
  monitoringFrequency: 'daily' | 'weekly' | 'monthly' | 'quarterly'
  lastReviewed: string
  sources: string[]
}

interface InternalContext {
  id: string
  area: 'governance' | 'strategy' | 'operations' | 'culture' | 'resources' | 'capabilities'
  title: string
  description: string
  currentState: string
  desiredState: string
  gaps: string[]
  strengths: string[]
  weaknesses: string[]
  opportunities: string[]
  threats: string[]
  priority: 'critical' | 'high' | 'medium' | 'low'
  owner: string
  lastReviewed: string
}

interface Requirement {
  id: string
  source: 'iso_22301' | 'regulatory' | 'contractual' | 'internal' | 'stakeholder'
  category: 'legal' | 'regulatory' | 'contractual' | 'standard' | 'policy'
  title: string
  description: string
  mandatory: boolean
  applicability: 'full' | 'partial' | 'not_applicable'
  complianceStatus: 'compliant' | 'partial' | 'non_compliant' | 'unknown'
  evidenceRequired: boolean
  evidence: string[]
  reviewDate: string
  owner: string
  notes?: string
}

interface OrganizationalContext {
  mission: string
  vision: string
  values: string[]
  strategicObjectives: string[]
  businessModel: string
  organizationSize: 'small' | 'medium' | 'large' | 'enterprise'
  industry: string
  geographicScope: 'local' | 'national' | 'regional' | 'global'
  riskAppetite: 'conservative' | 'moderate' | 'aggressive'
  maturityLevel: 1 | 2 | 3 | 4 | 5
  lastUpdated: string
}

// Mock Data
const generateMockStakeholders = (): Stakeholder[] => [
  {
    id: 'stakeholder-001',
    name: 'Board of Directors',
    organization: 'Internal',
    role: 'Governance Oversight',
    type: 'internal',
    category: 'employee',
    influence: 'high',
    interest: 'high',
    requirements: ['Business continuity assurance', 'Risk management oversight', 'Regulatory compliance'],
    contactInfo: {
      email: 'board@company.com'
    },
    engagementLevel: 'actively_engaged',
    lastEngagement: '2024-10-15'
  },
  {
    id: 'stakeholder-002',
    name: 'Key Customers',
    organization: 'External',
    role: 'Service Recipients',
    type: 'external',
    category: 'customer',
    influence: 'high',
    interest: 'medium',
    requirements: ['Service continuity', 'Data protection', 'Communication during incidents'],
    contactInfo: {},
    engagementLevel: 'informed',
    lastEngagement: '2024-09-30'
  },
  {
    id: 'stakeholder-003',
    name: 'Critical Suppliers',
    organization: 'External',
    role: 'Service Providers',
    type: 'external',
    category: 'supplier',
    influence: 'medium',
    interest: 'medium',
    requirements: ['Contract compliance', 'Business continuity planning', 'Incident reporting'],
    contactInfo: {},
    engagementLevel: 'consulted',
    lastEngagement: '2024-10-01'
  },
  {
    id: 'stakeholder-004',
    name: 'Regulatory Bodies',
    organization: 'External',
    role: 'Compliance Oversight',
    type: 'external',
    category: 'regulator',
    influence: 'high',
    interest: 'high',
    requirements: ['Regulatory compliance', 'Incident reporting', 'Audit cooperation'],
    contactInfo: {},
    engagementLevel: 'consulted',
    lastEngagement: '2024-08-15'
  },
  {
    id: 'stakeholder-005',
    name: 'Employees',
    organization: 'Internal',
    role: 'Workforce',
    type: 'internal',
    category: 'employee',
    influence: 'medium',
    interest: 'high',
    requirements: ['Safety assurance', 'Clear communication', 'Training and awareness'],
    contactInfo: {},
    engagementLevel: 'informed',
    lastEngagement: '2024-10-10'
  }
]

const generateMockExternalContext = (): ExternalContext[] => [
  {
    id: 'external-001',
    type: 'technological',
    title: 'Cybersecurity Threat Evolution',
    description: 'Increasing sophistication of cyber attacks targeting critical infrastructure',
    impact: 'high',
    likelihood: 'high',
    timeframe: 'immediate',
    trends: ['AI-powered attacks', 'Supply chain vulnerabilities', 'Ransomware evolution'],
    implications: ['Enhanced security measures required', 'Incident response capabilities', 'Staff training needs'],
    monitoringFrequency: 'daily',
    lastReviewed: '2024-11-15',
    sources: ['CISA alerts', 'Security vendors', 'Industry reports']
  },
  {
    id: 'external-002',
    type: 'legal',
    title: 'Data Protection Regulations',
    description: 'Evolving privacy laws and data protection requirements',
    impact: 'high',
    likelihood: 'high',
    timeframe: 'medium_term',
    trends: ['Stricter penalty enforcement', 'Extended territorial reach', 'New consent requirements'],
    implications: ['Compliance program updates', 'Privacy by design', 'Data mapping requirements'],
    monitoringFrequency: 'monthly',
    lastReviewed: '2024-11-01',
    sources: ['Legal counsel', 'Regulatory websites', 'Industry associations']
  },
  {
    id: 'external-003',
    type: 'economic',
    title: 'Supply Chain Disruptions',
    description: 'Global supply chain volatility affecting business operations',
    impact: 'medium',
    likelihood: 'high',
    timeframe: 'short_term',
    trends: ['Geopolitical tensions', 'Transportation delays', 'Material shortages'],
    implications: ['Supplier diversification', 'Inventory management', 'Alternative sourcing'],
    monitoringFrequency: 'weekly',
    lastReviewed: '2024-11-10',
    sources: ['Economic reports', 'Supplier updates', 'Industry news']
  },
  {
    id: 'external-004',
    type: 'environmental',
    title: 'Climate Change Impacts',
    description: 'Increasing frequency and severity of extreme weather events',
    impact: 'medium',
    likelihood: 'medium',
    timeframe: 'long_term',
    trends: ['Severe weather patterns', 'Temperature extremes', 'Flooding risks'],
    implications: ['Facility resilience', 'Emergency preparedness', 'Business model adaptation'],
    monitoringFrequency: 'quarterly',
    lastReviewed: '2024-10-01',
    sources: ['Weather services', 'Climate reports', 'Emergency management']
  }
]

const generateMockInternalContext = (): InternalContext[] => [
  {
    id: 'internal-001',
    area: 'governance',
    title: 'Business Continuity Governance',
    description: 'Current governance structure for business continuity management',
    currentState: 'BCM program established with defined roles and responsibilities',
    desiredState: 'Fully integrated BCM governance with board oversight and clear accountability',
    gaps: ['Limited board engagement', 'Unclear escalation procedures'],
    strengths: ['Dedicated BCM team', 'Executive sponsorship'],
    weaknesses: ['Inconsistent reporting', 'Limited cross-functional coordination'],
    opportunities: ['Enhanced board reporting', 'Integration with risk management'],
    threats: ['Governance fatigue', 'Resource constraints'],
    priority: 'high',
    owner: 'BCM Manager',
    lastReviewed: '2024-11-01'
  },
  {
    id: 'internal-002',
    area: 'capabilities',
    title: 'Crisis Response Capabilities',
    description: 'Organization\'s ability to respond to and manage crisis situations',
    currentState: 'Basic crisis response procedures with designated response team',
    desiredState: 'Advanced crisis response capabilities with 24/7 readiness',
    gaps: ['Limited after-hours coverage', 'Communication gaps'],
    strengths: ['Trained response team', 'Clear procedures'],
    weaknesses: ['Technology limitations', 'Geographic coverage'],
    opportunities: ['Technology enhancement', 'Skills development'],
    threats: ['Staff turnover', 'Technology obsolescence'],
    priority: 'critical',
    owner: 'Crisis Manager',
    lastReviewed: '2024-10-15'
  },
  {
    id: 'internal-003',
    area: 'culture',
    title: 'Risk Awareness Culture',
    description: 'Organization\'s culture regarding risk awareness and business continuity',
    currentState: 'Growing awareness with some engagement across departments',
    desiredState: 'Embedded risk culture with proactive identification and management',
    gaps: ['Inconsistent awareness levels', 'Limited proactive reporting'],
    strengths: ['Management support', 'Training programs'],
    weaknesses: ['Departmental silos', 'Communication barriers'],
    opportunities: ['Cultural change program', 'Recognition systems'],
    threats: ['Complacency', 'Change resistance'],
    priority: 'medium',
    owner: 'HR Director',
    lastReviewed: '2024-09-30'
  }
]

const generateMockRequirements = (): Requirement[] => [
  {
    id: 'req-001',
    source: 'iso_22301',
    category: 'standard',
    title: 'Business Continuity Policy',
    description: 'Establish and maintain a business continuity policy',
    mandatory: true,
    applicability: 'full',
    complianceStatus: 'compliant',
    evidenceRequired: true,
    evidence: ['BC_Policy_v2.1.pdf', 'Board_Approval_Minutes.pdf'],
    reviewDate: '2024-12-01',
    owner: 'BCM Manager',
    notes: 'Policy reviewed annually and approved by board'
  },
  {
    id: 'req-002',
    source: 'regulatory',
    category: 'legal',
    title: 'Data Breach Notification',
    description: 'Notify regulatory authorities of data breaches within 72 hours',
    mandatory: true,
    applicability: 'full',
    complianceStatus: 'compliant',
    evidenceRequired: true,
    evidence: ['Incident_Response_Procedure.pdf', 'Notification_Templates.docx'],
    reviewDate: '2024-11-30',
    owner: 'Legal Counsel',
    notes: 'Procedure tested quarterly'
  },
  {
    id: 'req-003',
    source: 'contractual',
    category: 'contractual',
    title: 'Service Level Agreements',
    description: 'Maintain agreed service levels during disruptions',
    mandatory: true,
    applicability: 'partial',
    complianceStatus: 'partial',
    evidenceRequired: true,
    evidence: ['SLA_Matrix.xlsx'],
    reviewDate: '2024-12-15',
    owner: 'Service Manager',
    notes: 'Some SLAs need updating for new services'
  },
  {
    id: 'req-004',
    source: 'internal',
    category: 'policy',
    title: 'Employee Training Requirements',
    description: 'All employees must complete annual BCM awareness training',
    mandatory: true,
    applicability: 'full',
    complianceStatus: 'partial',
    evidenceRequired: true,
    evidence: ['Training_Records.xlsx'],
    reviewDate: '2024-12-01',
    owner: 'Training Manager',
    notes: '85% completion rate, targeting 95%'
  }
]

const generateMockOrganizationalContext = (): OrganizationalContext => ({
  mission: 'To provide innovative technology solutions that enable our clients to achieve their business objectives',
  vision: 'To be the leading provider of technology solutions in our market',
  values: ['Innovation', 'Integrity', 'Customer Focus', 'Excellence', 'Collaboration'],
  strategicObjectives: [
    'Achieve 20% annual growth in revenue',
    'Expand into new geographical markets',
    'Enhance customer satisfaction scores',
    'Develop innovative product offerings',
    'Build a sustainable business model'
  ],
  businessModel: 'Technology solutions and services provider with recurring revenue streams',
  organizationSize: 'medium',
  industry: 'Technology Services',
  geographicScope: 'national',
  riskAppetite: 'moderate',
  maturityLevel: 3,
  lastUpdated: '2024-10-01'
})

export function ContextManagementModule() {
  const [activeTab, setActiveTab] = useState('overview')
  const [searchTerm, setSearchTerm] = useState('')
  const [filterType, setFilterType] = useState<string>('all')
  const [filterCategory, setFilterCategory] = useState<string>('all')
  const [filterStatus, setFilterStatus] = useState<string>('all')

  // Store integration
  const { currentModule, setCurrentModule } = useBCMStore()

  // Data fetching
  const { data: stakeholders = [], isLoading: loadingStakeholders } = useQuery({
    queryKey: ['stakeholders'],
    queryFn: async () => {
      // API client doesn't have context endpoint, using mock data
      return generateMockStakeholders()
    }
  })

  const { data: externalContext = [], isLoading: loadingExternal } = useQuery({
    queryKey: ['external-context'],
    queryFn: async () => {
      // API client doesn't have context endpoint
      return generateMockExternalContext()
    }
  })

  const { data: internalContext = [], isLoading: loadingInternal } = useQuery({
    queryKey: ['internal-context'],
    queryFn: async () => {
      // API client doesn't have context endpoint
      return generateMockInternalContext()
    }
  })

  const { data: requirements = [], isLoading: loadingRequirements } = useQuery({
    queryKey: ['requirements'],
    queryFn: async () => {
      // API client doesn't have context endpoint
      return generateMockRequirements()
    }
  })

  const { data: organizationContext, isLoading: loadingOrganization } = useQuery({
    queryKey: ['organization-context'],
    queryFn: async () => {
      // API client doesn't have context endpoint
      return generateMockOrganizationalContext()
    }
  })

  // Metrics calculations
  const totalStakeholders = stakeholders.length
  const highInfluenceStakeholders = stakeholders.filter(s => s.influence === 'high').length
  const activelyEngaged = stakeholders.filter(s => s.engagementLevel === 'actively_engaged').length

  const totalRequirements = requirements.length
  const compliantRequirements = requirements.filter(r => r.complianceStatus === 'compliant').length
  const nonCompliantRequirements = requirements.filter(r => r.complianceStatus === 'non_compliant').length
  const partialCompliantRequirements = requirements.filter(r => r.complianceStatus === 'partial').length

  const highImpactExternal = externalContext.filter(e => e.impact === 'high').length
  const criticalInternal = internalContext.filter(i => i.priority === 'critical').length

  const getInfluenceColor = (influence: string) => {
    switch (influence) {
      case 'high': return 'text-red-600 bg-red-50'
      case 'medium': return 'text-yellow-600 bg-yellow-50'
      case 'low': return 'text-green-600 bg-green-50'
      default: return 'text-gray-600 bg-gray-50'
    }
  }

  const getComplianceColor = (status: string) => {
    switch (status) {
      case 'compliant': return 'text-green-600 bg-green-50'
      case 'partial': return 'text-yellow-600 bg-yellow-50'
      case 'non_compliant': return 'text-red-600 bg-red-50'
      case 'unknown': return 'text-gray-600 bg-gray-50'
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
          <h1 className="text-3xl font-bold text-gray-900">Context Management</h1>
          <p className="text-gray-600 mt-1">Understand organizational context, stakeholders, and requirements</p>
        </div>
        <div className="flex items-center space-x-3">
          <Button variant="outline">
            <Download className="h-4 w-4 mr-2" />
            Export Analysis
          </Button>
          <Button>
            <Plus className="h-4 w-4 mr-2" />
            Add Context Item
          </Button>
        </div>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="stakeholders">Stakeholders</TabsTrigger>
          <TabsTrigger value="external">External Context</TabsTrigger>
          <TabsTrigger value="internal">Internal Context</TabsTrigger>
          <TabsTrigger value="requirements">Requirements</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-6">
          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Stakeholders</CardTitle>
                <Users className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{totalStakeholders}</div>
                <div className="text-xs text-muted-foreground mt-1">
                  {highInfluenceStakeholders} high influence
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Compliance Rate</CardTitle>
                <CheckCircle className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {totalRequirements > 0 ? Math.round((compliantRequirements / totalRequirements) * 100) : 0}%
                </div>
                <div className="text-xs text-muted-foreground mt-1">
                  {compliantRequirements} of {totalRequirements} requirements
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">High Impact Items</CardTitle>
                <AlertTriangle className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{highImpactExternal}</div>
                <div className="text-xs text-muted-foreground mt-1">
                  External context factors
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Critical Areas</CardTitle>
                <Target className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{criticalInternal}</div>
                <div className="text-xs text-muted-foreground mt-1">
                  Internal priority areas
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Organization Context */}
          {organizationContext && (
            <Card>
              <CardHeader>
                <CardTitle>Organizational Context</CardTitle>
                <CardDescription>Current organizational profile and strategic direction</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <div>
                      <h4 className="font-medium mb-2">Mission</h4>
                      <p className="text-sm text-gray-600">{organizationContext.mission}</p>
                    </div>
                    <div>
                      <h4 className="font-medium mb-2">Vision</h4>
                      <p className="text-sm text-gray-600">{organizationContext.vision}</p>
                    </div>
                    <div>
                      <h4 className="font-medium mb-2">Values</h4>
                      <div className="flex flex-wrap gap-2">
                        {organizationContext.values.map((value, index) => (
                          <Badge key={index} variant="outline">{value}</Badge>
                        ))}
                      </div>
                    </div>
                  </div>
                  <div className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <span className="text-sm font-medium">Size:</span>
                        <p className="text-sm text-gray-600 capitalize">{organizationContext.organizationSize}</p>
                      </div>
                      <div>
                        <span className="text-sm font-medium">Industry:</span>
                        <p className="text-sm text-gray-600">{organizationContext.industry}</p>
                      </div>
                      <div>
                        <span className="text-sm font-medium">Scope:</span>
                        <p className="text-sm text-gray-600 capitalize">{organizationContext.geographicScope}</p>
                      </div>
                      <div>
                        <span className="text-sm font-medium">Risk Appetite:</span>
                        <p className="text-sm text-gray-600 capitalize">{organizationContext.riskAppetite}</p>
                      </div>
                    </div>
                    <div>
                      <span className="text-sm font-medium">BCM Maturity Level:</span>
                      <div className="flex items-center space-x-2 mt-1">
                        <Progress value={organizationContext.maturityLevel * 20} className="flex-1" />
                        <span className="text-sm text-gray-600">Level {organizationContext.maturityLevel}</span>
                      </div>
                    </div>
                    <div>
                      <h4 className="font-medium mb-2">Strategic Objectives</h4>
                      <ul className="text-sm text-gray-600 list-disc list-inside space-y-1">
                        {organizationContext.strategicObjectives.slice(0, 3).map((objective, index) => (
                          <li key={index}>{objective}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Stakeholder Matrix */}
          <Card>
            <CardHeader>
              <CardTitle>Stakeholder Influence-Interest Matrix</CardTitle>
              <CardDescription>Visual representation of stakeholder positioning</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-3 gap-4 h-64">
                {/* High Interest */}
                <div className="col-span-3 grid grid-cols-3 gap-4 h-full">
                  <div className="border-2 border-dashed border-gray-200 p-4 rounded-lg">
                    <div className="text-xs font-medium text-gray-500 mb-2">Low Influence, High Interest</div>
                    <div className="space-y-1">
                      {stakeholders
                        .filter(s => s.influence === 'low' && s.interest === 'high')
                        .map(s => (
                          <div key={s.id} className="text-xs p-1 bg-blue-50 rounded">{s.name}</div>
                        ))}
                    </div>
                  </div>
                  <div className="border-2 border-dashed border-gray-200 p-4 rounded-lg">
                    <div className="text-xs font-medium text-gray-500 mb-2">Medium Influence, High Interest</div>
                    <div className="space-y-1">
                      {stakeholders
                        .filter(s => s.influence === 'medium' && s.interest === 'high')
                        .map(s => (
                          <div key={s.id} className="text-xs p-1 bg-yellow-50 rounded">{s.name}</div>
                        ))}
                    </div>
                  </div>
                  <div className="border-2 border-dashed border-red-200 p-4 rounded-lg bg-red-50">
                    <div className="text-xs font-medium text-red-700 mb-2">High Influence, High Interest</div>
                    <div className="space-y-1">
                      {stakeholders
                        .filter(s => s.influence === 'high' && s.interest === 'high')
                        .map(s => (
                          <div key={s.id} className="text-xs p-1 bg-red-100 rounded font-medium">{s.name}</div>
                        ))}
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Context Summary */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>External Context Highlights</CardTitle>
                <CardDescription>Key external factors requiring attention</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {externalContext
                    .filter(e => e.impact === 'high')
                    .slice(0, 3)
                    .map((context) => (
                      <div key={context.id} className="p-3 border rounded-lg">
                        <div className="flex items-center justify-between mb-1">
                          <h4 className="font-medium text-sm">{context.title}</h4>
                          <Badge variant="outline" className={getPriorityColor(context.impact)}>
                            {context.impact} impact
                          </Badge>
                        </div>
                        <p className="text-xs text-gray-600">{context.description}</p>
                        <div className="flex items-center space-x-2 mt-2">
                          <Badge variant="outline" >
                            {context.type}
                          </Badge>
                          <span className="text-xs text-gray-500">{context.timeframe.replace('_', ' ')}</span>
                        </div>
                      </div>
                    ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Internal Context Priorities</CardTitle>
                <CardDescription>Critical internal areas needing attention</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {internalContext
                    .filter(i => i.priority === 'critical' || i.priority === 'high')
                    .slice(0, 3)
                    .map((context) => (
                      <div key={context.id} className="p-3 border rounded-lg">
                        <div className="flex items-center justify-between mb-1">
                          <h4 className="font-medium text-sm">{context.title}</h4>
                          <Badge variant="outline" className={getPriorityColor(context.priority)}>
                            {context.priority}
                          </Badge>
                        </div>
                        <p className="text-xs text-gray-600">{context.description}</p>
                        <div className="flex items-center space-x-2 mt-2">
                          <Badge variant="outline" >
                            {context.area}
                          </Badge>
                          <span className="text-xs text-gray-500">Owner: {context.owner}</span>
                        </div>
                      </div>
                    ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Stakeholders Tab */}
        <TabsContent value="stakeholders" className="space-y-6">
          {/* Stakeholder Filters */}
          <Card>
            <CardHeader>
              <CardTitle>Stakeholder Analysis</CardTitle>
              <CardDescription>Manage and analyze organizational stakeholders</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="relative">
                  <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                  <Input
                    placeholder="Search stakeholders..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10"
                  />
                </div>
                <Select value={filterType} onValueChange={setFilterType}>
                  <SelectTrigger>
                    <SelectValue placeholder="Filter by type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Types</SelectItem>
                    <SelectItem value="internal">Internal</SelectItem>
                    <SelectItem value="external">External</SelectItem>
                  </SelectContent>
                </Select>
                <Select value={filterCategory} onValueChange={setFilterCategory}>
                  <SelectTrigger>
                    <SelectValue placeholder="Filter by category" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Categories</SelectItem>
                    <SelectItem value="employee">Employee</SelectItem>
                    <SelectItem value="customer">Customer</SelectItem>
                    <SelectItem value="supplier">Supplier</SelectItem>
                    <SelectItem value="regulator">Regulator</SelectItem>
                    <SelectItem value="partner">Partner</SelectItem>
                  </SelectContent>
                </Select>
                <Button variant="outline">
                  <Filter className="h-4 w-4 mr-2" />
                  Apply Filters
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Stakeholders List */}
          <div className="grid gap-6">
            {stakeholders.map((stakeholder) => (
              <Card key={stakeholder.id}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="text-lg">{stakeholder.name}</CardTitle>
                      <CardDescription>{stakeholder.organization} - {stakeholder.role}</CardDescription>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Badge variant="outline" className={getInfluenceColor(stakeholder.influence)}>
                        {stakeholder.influence} influence
                      </Badge>
                      <Badge variant="outline" className={getInfluenceColor(stakeholder.interest)}>
                        {stakeholder.interest} interest
                      </Badge>
                      <Badge variant="outline">
                        {stakeholder.type}
                      </Badge>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div>
                        <span className="text-sm font-medium">Category:</span>
                        <p className="text-sm text-gray-600 capitalize">{stakeholder.category}</p>
                      </div>
                      <div>
                        <span className="text-sm font-medium">Engagement Level:</span>
                        <p className="text-sm text-gray-600">{stakeholder.engagementLevel.replace('_', ' ')}</p>
                      </div>
                      <div>
                        <span className="text-sm font-medium">Last Engagement:</span>
                        <p className="text-sm text-gray-600">
                          {stakeholder.lastEngagement ? format(new Date(stakeholder.lastEngagement), 'MMM dd, yyyy') : 'Never'}
                        </p>
                      </div>
                    </div>

                    <div>
                      <h4 className="font-medium mb-2">Requirements & Expectations</h4>
                      <div className="flex flex-wrap gap-2">
                        {stakeholder.requirements.map((requirement, index) => (
                          <Badge key={index} variant="outline" >
                            {requirement}
                          </Badge>
                        ))}
                      </div>
                    </div>

                    {(stakeholder.contactInfo.email || stakeholder.contactInfo.phone) && (
                      <div>
                        <h4 className="font-medium mb-2">Contact Information</h4>
                        <div className="text-sm text-gray-600 space-y-1">
                          {stakeholder.contactInfo.email && (
                            <div>Email: {stakeholder.contactInfo.email}</div>
                          )}
                          {stakeholder.contactInfo.phone && (
                            <div>Phone: {stakeholder.contactInfo.phone}</div>
                          )}
                        </div>
                      </div>
                    )}

                    <div className="flex items-center justify-between pt-4 border-t">
                      <div className="flex items-center space-x-2">
                        <Button variant="outline" >
                          <Edit className="h-4 w-4 mr-2" />
                          Edit Stakeholder
                        </Button>
                        <Button variant="outline" >
                          <Eye className="h-4 w-4 mr-2" />
                          View Details
                        </Button>
                      </div>
                      <span className="text-xs text-gray-500">
                        {stakeholder.influence === 'high' && stakeholder.interest === 'high' ? 'Key Stakeholder' : ''}
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* External Context Tab */}
        <TabsContent value="external" className="space-y-6">
          {/* PESTLE Analysis Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {['political', 'economic', 'social', 'technological', 'legal', 'environmental'].map((type) => (
              <Card key={type}>
                <CardHeader>
                  <CardTitle className="text-lg capitalize">{type}</CardTitle>
                  <CardDescription>
                    {externalContext.filter(c => c.type === type).length} factor(s)
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {externalContext
                      .filter(c => c.type === type)
                      .slice(0, 2)
                      .map((context) => (
                        <div key={context.id} className="p-3 border rounded-lg">
                          <div className="flex items-center justify-between mb-1">
                            <h4 className="font-medium text-sm">{context.title}</h4>
                            <Badge variant="outline" className={getPriorityColor(context.impact)}>
                              {context.impact}
                            </Badge>
                          </div>
                          <p className="text-xs text-gray-600 line-clamp-2">{context.description}</p>
                          <div className="flex items-center space-x-2 mt-2">
                            <span className="text-xs text-gray-500">{context.timeframe.replace('_', ' ')}</span>
                            <span className="text-xs text-gray-500">•</span>
                            <span className="text-xs text-gray-500">{context.likelihood} likelihood</span>
                          </div>
                        </div>
                      ))}
                    {externalContext.filter(c => c.type === type).length === 0 && (
                      <div className="text-center py-6">
                        <Globe className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                        <p className="text-sm text-gray-500">No {type} factors identified</p>
                        <Button variant="outline"  className="mt-2">
                          <Plus className="h-4 w-4 mr-2" />
                          Add Factor
                        </Button>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Detailed External Context */}
          <Card>
            <CardHeader>
              <CardTitle>External Context Details</CardTitle>
              <CardDescription>Comprehensive external factor analysis</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {externalContext.map((context) => (
                  <div key={context.id} className="p-4 border rounded-lg">
                    <div className="flex items-center justify-between mb-3">
                      <div>
                        <h4 className="font-medium">{context.title}</h4>
                        <p className="text-sm text-gray-600">{context.description}</p>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge variant="outline" className={getPriorityColor(context.impact)}>
                          {context.impact} impact
                        </Badge>
                        <Badge variant="outline">
                          {context.type}
                        </Badge>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                      <div>
                        <span className="text-sm font-medium">Likelihood:</span>
                        <p className="text-sm text-gray-600 capitalize">{context.likelihood}</p>
                      </div>
                      <div>
                        <span className="text-sm font-medium">Timeframe:</span>
                        <p className="text-sm text-gray-600">{context.timeframe.replace('_', ' ')}</p>
                      </div>
                      <div>
                        <span className="text-sm font-medium">Monitoring:</span>
                        <p className="text-sm text-gray-600 capitalize">{context.monitoringFrequency}</p>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <h5 className="font-medium mb-2">Key Trends</h5>
                        <ul className="text-sm text-gray-600 list-disc list-inside space-y-1">
                          {context.trends.map((trend, index) => (
                            <li key={index}>{trend}</li>
                          ))}
                        </ul>
                      </div>
                      <div>
                        <h5 className="font-medium mb-2">Business Implications</h5>
                        <ul className="text-sm text-gray-600 list-disc list-inside space-y-1">
                          {context.implications.map((implication, index) => (
                            <li key={index}>{implication}</li>
                          ))}
                        </ul>
                      </div>
                    </div>

                    <div className="flex items-center justify-between pt-4 border-t mt-4">
                      <div className="flex items-center space-x-2">
                        <Button variant="outline" >
                          <Edit className="h-4 w-4 mr-2" />
                          Edit Factor
                        </Button>
                        <Button variant="outline" >
                          <BarChart3 className="h-4 w-4 mr-2" />
                          View Analysis
                        </Button>
                      </div>
                      <span className="text-xs text-gray-500">
                        Last reviewed: {format(new Date(context.lastReviewed), 'MMM dd, yyyy')}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Internal Context Tab */}
        <TabsContent value="internal" className="space-y-6">
          {/* Internal Context Overview */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {['governance', 'strategy', 'operations', 'culture', 'resources', 'capabilities'].map((area) => (
              <Card key={area}>
                <CardHeader>
                  <CardTitle className="text-lg capitalize">{area}</CardTitle>
                  <CardDescription>
                    {internalContext.filter(c => c.area === area).length} area(s) identified
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {internalContext
                      .filter(c => c.area === area)
                      .slice(0, 1)
                      .map((context) => (
                        <div key={context.id} className="p-3 border rounded-lg">
                          <div className="flex items-center justify-between mb-1">
                            <h4 className="font-medium text-sm">{context.title}</h4>
                            <Badge variant="outline" className={getPriorityColor(context.priority)}>
                              {context.priority}
                            </Badge>
                          </div>
                          <p className="text-xs text-gray-600 line-clamp-2">{context.description}</p>
                          <div className="mt-2">
                            <span className="text-xs text-gray-500">Owner: {context.owner}</span>
                          </div>
                        </div>
                      ))}
                    {internalContext.filter(c => c.area === area).length === 0 && (
                      <div className="text-center py-6">
                        <Building2 className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                        <p className="text-sm text-gray-500">No {area} factors identified</p>
                        <Button variant="outline"  className="mt-2">
                          <Plus className="h-4 w-4 mr-2" />
                          Add Factor
                        </Button>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* SWOT Analysis */}
          <Card>
            <CardHeader>
              <CardTitle>Internal Context Analysis</CardTitle>
              <CardDescription>Detailed analysis of internal organizational factors</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {internalContext.map((context) => (
                  <div key={context.id} className="p-4 border rounded-lg">
                    <div className="flex items-center justify-between mb-3">
                      <div>
                        <h4 className="font-medium">{context.title}</h4>
                        <p className="text-sm text-gray-600">{context.description}</p>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge variant="outline" className={getPriorityColor(context.priority)}>
                          {context.priority}
                        </Badge>
                        <Badge variant="outline">
                          {context.area}
                        </Badge>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                      <div>
                        <span className="text-sm font-medium">Current State:</span>
                        <p className="text-sm text-gray-600">{context.currentState}</p>
                      </div>
                      <div>
                        <span className="text-sm font-medium">Desired State:</span>
                        <p className="text-sm text-gray-600">{context.desiredState}</p>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                      <div>
                        <h5 className="font-medium mb-2 text-green-700">Strengths</h5>
                        <ul className="text-sm text-gray-600 space-y-1">
                          {context.strengths.map((strength, index) => (
                            <li key={index} className="flex items-start space-x-1">
                              <span className="text-green-500 mt-1">•</span>
                              <span>{strength}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                      <div>
                        <h5 className="font-medium mb-2 text-red-700">Weaknesses</h5>
                        <ul className="text-sm text-gray-600 space-y-1">
                          {context.weaknesses.map((weakness, index) => (
                            <li key={index} className="flex items-start space-x-1">
                              <span className="text-red-500 mt-1">•</span>
                              <span>{weakness}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                      <div>
                        <h5 className="font-medium mb-2 text-blue-700">Opportunities</h5>
                        <ul className="text-sm text-gray-600 space-y-1">
                          {context.opportunities.map((opportunity, index) => (
                            <li key={index} className="flex items-start space-x-1">
                              <span className="text-blue-500 mt-1">•</span>
                              <span>{opportunity}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                      <div>
                        <h5 className="font-medium mb-2 text-orange-700">Threats</h5>
                        <ul className="text-sm text-gray-600 space-y-1">
                          {context.threats.map((threat, index) => (
                            <li key={index} className="flex items-start space-x-1">
                              <span className="text-orange-500 mt-1">•</span>
                              <span>{threat}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>

                    <div className="flex items-center justify-between pt-4 border-t mt-4">
                      <div className="flex items-center space-x-2">
                        <Button variant="outline" >
                          <Edit className="h-4 w-4 mr-2" />
                          Edit Analysis
                        </Button>
                        <Button variant="outline" >
                          <Target className="h-4 w-4 mr-2" />
                          Action Plan
                        </Button>
                      </div>
                      <div className="text-xs text-gray-500">
                        <span>Owner: {context.owner}</span>
                        <span className="mx-2">•</span>
                        <span>Last reviewed: {format(new Date(context.lastReviewed), 'MMM dd, yyyy')}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Requirements Tab */}
        <TabsContent value="requirements" className="space-y-6">
          {/* Compliance Overview */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Requirements</CardTitle>
                <FileText className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{totalRequirements}</div>
                <Progress value={100} className="mt-2" />
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Compliant</CardTitle>
                <CheckCircle className="h-4 w-4 text-green-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{compliantRequirements}</div>
                <Progress value={(compliantRequirements / totalRequirements) * 100} className="mt-2" />
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Partial</CardTitle>
                <Clock className="h-4 w-4 text-yellow-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{partialCompliantRequirements}</div>
                <Progress value={(partialCompliantRequirements / totalRequirements) * 100} className="mt-2" />
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Non-Compliant</CardTitle>
                <AlertTriangle className="h-4 w-4 text-red-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{nonCompliantRequirements}</div>
                <Progress value={(nonCompliantRequirements / totalRequirements) * 100} className="mt-2" />
              </CardContent>
            </Card>
          </div>

          {/* Requirements Filters */}
          <Card>
            <CardHeader>
              <CardTitle>Requirements Management</CardTitle>
              <CardDescription>Track compliance with applicable requirements and standards</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <Select value={filterStatus} onValueChange={setFilterStatus}>
                  <SelectTrigger>
                    <SelectValue placeholder="Filter by compliance" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Status</SelectItem>
                    <SelectItem value="compliant">Compliant</SelectItem>
                    <SelectItem value="partial">Partial</SelectItem>
                    <SelectItem value="non_compliant">Non-Compliant</SelectItem>
                    <SelectItem value="unknown">Unknown</SelectItem>
                  </SelectContent>
                </Select>
                <Select value={filterCategory} onValueChange={setFilterCategory}>
                  <SelectTrigger>
                    <SelectValue placeholder="Filter by category" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Categories</SelectItem>
                    <SelectItem value="legal">Legal</SelectItem>
                    <SelectItem value="regulatory">Regulatory</SelectItem>
                    <SelectItem value="standard">Standard</SelectItem>
                    <SelectItem value="contractual">Contractual</SelectItem>
                    <SelectItem value="policy">Policy</SelectItem>
                  </SelectContent>
                </Select>
                <Input placeholder="Search requirements..." />
                <Button variant="outline">
                  <Filter className="h-4 w-4 mr-2" />
                  Apply Filters
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Requirements List */}
          <div className="grid gap-6">
            {requirements.map((requirement) => (
              <Card key={requirement.id}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="text-lg">{requirement.title}</CardTitle>
                      <CardDescription>{requirement.description}</CardDescription>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Badge variant="outline" className={getComplianceColor(requirement.complianceStatus)}>
                        {requirement.complianceStatus.replace('_', ' ')}
                      </Badge>
                      <Badge variant="outline">
                        {requirement.category}
                      </Badge>
                      {requirement.mandatory && (
                        <Badge variant="destructive">
                          Mandatory
                        </Badge>
                      )}
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                      <div>
                        <span className="text-sm font-medium">Source:</span>
                        <p className="text-sm text-gray-600">{requirement.source.replace('_', ' ')}</p>
                      </div>
                      <div>
                        <span className="text-sm font-medium">Applicability:</span>
                        <p className="text-sm text-gray-600">{requirement.applicability.replace('_', ' ')}</p>
                      </div>
                      <div>
                        <span className="text-sm font-medium">Owner:</span>
                        <p className="text-sm text-gray-600">{requirement.owner}</p>
                      </div>
                      <div>
                        <span className="text-sm font-medium">Review Date:</span>
                        <p className="text-sm text-gray-600">{format(new Date(requirement.reviewDate), 'MMM dd, yyyy')}</p>
                      </div>
                    </div>

                    {requirement.evidence.length > 0 && (
                      <div>
                        <h4 className="font-medium mb-2">Evidence</h4>
                        <div className="flex flex-wrap gap-2">
                          {requirement.evidence.map((evidence, index) => (
                            <Badge key={index} variant="outline">
                              <FileText className="h-3 w-3 mr-1" />
                              {evidence}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}

                    {requirement.notes && (
                      <div>
                        <h4 className="font-medium mb-2">Notes</h4>
                        <p className="text-sm text-gray-600">{requirement.notes}</p>
                      </div>
                    )}

                    <div className="flex items-center justify-between pt-4 border-t">
                      <div className="flex items-center space-x-2">
                        <Button variant="outline" >
                          <Edit className="h-4 w-4 mr-2" />
                          Edit Requirement
                        </Button>
                        <Button variant="outline" >
                          <Upload className="h-4 w-4 mr-2" />
                          Add Evidence
                        </Button>
                      </div>
                      {requirement.evidenceRequired && requirement.evidence.length === 0 && (
                        <Badge variant="destructive" >
                          Evidence Required
                        </Badge>
                      )}
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