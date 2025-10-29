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
import { Textarea } from '@/components/ui/textarea'
import { Progress } from '@/components/ui/progress'
import { Separator } from '@/components/ui/separator'
import {
  Building2,
  Users,
  MapPin,
  Phone,
  Mail,
  Globe,
  Shield,
  AlertTriangle,
  CheckCircle,
  Clock,
  TrendingUp,
  TrendingDown,
  Star,
  Plus,
  Search,
  Filter,
  Edit,
  Eye,
  Download,
  Upload,
  Send,
  Calendar,
  BarChart3,
  FileText,
  Handshake,
  Target,
  DollarSign
} from 'lucide-react'
import { format } from 'date-fns'
import { cn } from '@/lib/utils'

// Types
interface ClientContact {
  id: string
  name: string
  title: string
  department?: string
  email: string
  phone?: string
  mobile?: string
  isPrimary: boolean
  role: 'decision_maker' | 'technical_contact' | 'administrative' | 'billing' | 'emergency'
  lastContact?: string
  notes?: string
}

interface ClientContract {
  id: string
  contractNumber: string
  type: 'service_agreement' | 'support_contract' | 'licensing' | 'consulting' | 'maintenance'
  status: 'active' | 'expired' | 'pending' | 'terminated'
  startDate: string
  endDate: string
  value: number
  currency: 'USD' | 'EUR' | 'GBP'
  renewalDate?: string
  autoRenewal: boolean
  slaLevel: 'basic' | 'standard' | 'premium' | 'enterprise'
  services: string[]
  terms: {
    rto: number // hours
    rpo: number // hours
    availabilityTarget: number // percentage
    responseTime: number // hours
  }
}

interface ClientAssessment {
  id: string
  type: 'bia' | 'risk_assessment' | 'compliance_audit' | 'maturity_assessment'
  status: 'planned' | 'in_progress' | 'completed' | 'overdue'
  scheduledDate: string
  completedDate?: string
  score?: number
  findings: string[]
  recommendations: string[]
  nextAssessment?: string
  assessor: string
}

interface Client {
  id: string
  name: string
  legalName: string
  industry: string
  sector: 'public' | 'private' | 'non_profit'
  size: 'small' | 'medium' | 'large' | 'enterprise'
  tier: 'bronze' | 'silver' | 'gold' | 'platinum'
  status: 'active' | 'inactive' | 'prospect' | 'suspended'

  // Contact Information
  address: {
    street: string
    city: string
    state: string
    country: string
    postalCode: string
  }
  website?: string
  phone?: string

  // Business Information
  employeeCount?: number
  annualRevenue?: number
  establishedDate?: string

  // BCM Information
  bcmMaturity: 'initial' | 'developing' | 'defined' | 'managed' | 'optimizing'
  riskProfile: 'low' | 'medium' | 'high' | 'critical'
  complianceRequirements: string[]
  criticalProcesses: string[]

  // Relationship
  accountManager: string
  relationshipStart: string
  lastContact?: string
  nextReview?: string
  satisfactionScore?: number

  // Contacts and Contracts
  contacts: ClientContact[]
  contracts: ClientContract[]
  assessments: ClientAssessment[]

  // Metadata
  tags: string[]
  notes?: string
  createdDate: string
  updatedDate: string
}

interface ClientMetrics {
  totalClients: number
  activeClients: number
  newClientsThisMonth: number
  churnRate: number
  averageSatisfaction: number
  totalRevenue: number
  renewalRate: number
  assessmentCompliance: number
}

// Mock Data
const generateMockClients = (): Client[] => [
  {
    id: 'client-001',
    name: 'TechCorp Solutions',
    legalName: 'TechCorp Solutions Inc.',
    industry: 'Technology',
    sector: 'private',
    size: 'large',
    tier: 'gold',
    status: 'active',
    address: {
      street: '123 Innovation Drive',
      city: 'San Francisco',
      state: 'CA',
      country: 'United States',
      postalCode: '94105'
    },
    website: 'https://techcorp.com',
    phone: '+1-555-0123',
    employeeCount: 2500,
    annualRevenue: 150000000,
    establishedDate: '2010-03-15',
    bcmMaturity: 'managed',
    riskProfile: 'medium',
    complianceRequirements: ['SOX', 'ISO 27001', 'GDPR'],
    criticalProcesses: ['Customer Portal', 'Payment Processing', 'Data Analytics'],
    accountManager: 'Sarah Johnson',
    relationshipStart: '2020-01-15',
    lastContact: '2024-11-10',
    nextReview: '2024-12-15',
    satisfactionScore: 4.2,
    contacts: [
      {
        id: 'contact-001',
        name: 'Michael Chen',
        title: 'CTO',
        department: 'Technology',
        email: 'michael.chen@techcorp.com',
        phone: '+1-555-0124',
        mobile: '+1-555-0125',
        isPrimary: true,
        role: 'decision_maker',
        lastContact: '2024-11-10'
      },
      {
        id: 'contact-002',
        name: 'Lisa Wang',
        title: 'Risk Manager',
        department: 'Risk Management',
        email: 'lisa.wang@techcorp.com',
        phone: '+1-555-0126',
        isPrimary: false,
        role: 'technical_contact',
        lastContact: '2024-10-20'
      }
    ],
    contracts: [
      {
        id: 'contract-001',
        contractNumber: 'TC-2024-001',
        type: 'service_agreement',
        status: 'active',
        startDate: '2024-01-01',
        endDate: '2024-12-31',
        value: 120000,
        currency: 'USD',
        renewalDate: '2024-11-01',
        autoRenewal: true,
        slaLevel: 'premium',
        services: ['BCM Consulting', 'Risk Assessment', 'Training'],
        terms: {
          rto: 4,
          rpo: 1,
          availabilityTarget: 99.9,
          responseTime: 2
        }
      }
    ],
    assessments: [
      {
        id: 'assessment-001',
        type: 'maturity_assessment',
        status: 'completed',
        scheduledDate: '2024-10-01',
        completedDate: '2024-10-15',
        score: 85,
        findings: ['Strong BCM governance', 'Well-documented procedures'],
        recommendations: ['Enhance crisis communication', 'Improve exercise frequency'],
        nextAssessment: '2025-04-01',
        assessor: 'John Smith'
      }
    ],
    tags: ['Technology', 'Large Enterprise', 'High Value'],
    notes: 'Key strategic client with strong BCM program',
    createdDate: '2020-01-15',
    updatedDate: '2024-11-10'
  },
  {
    id: 'client-002',
    name: 'Healthcare Plus',
    legalName: 'Healthcare Plus Medical Group',
    industry: 'Healthcare',
    sector: 'private',
    size: 'medium',
    tier: 'silver',
    status: 'active',
    address: {
      street: '456 Medical Center Blvd',
      city: 'Chicago',
      state: 'IL',
      country: 'United States',
      postalCode: '60601'
    },
    website: 'https://healthcareplus.com',
    phone: '+1-555-0200',
    employeeCount: 850,
    annualRevenue: 45000000,
    establishedDate: '2008-06-20',
    bcmMaturity: 'developing',
    riskProfile: 'high',
    complianceRequirements: ['HIPAA', 'Joint Commission', 'CMS'],
    criticalProcesses: ['Patient Care Systems', 'Medical Records', 'Emergency Services'],
    accountManager: 'David Brown',
    relationshipStart: '2021-03-10',
    lastContact: '2024-11-05',
    nextReview: '2024-12-01',
    satisfactionScore: 3.8,
    contacts: [
      {
        id: 'contact-003',
        name: 'Dr. Amanda Rodriguez',
        title: 'Chief Medical Officer',
        email: 'a.rodriguez@healthcareplus.com',
        phone: '+1-555-0201',
        isPrimary: true,
        role: 'decision_maker',
        lastContact: '2024-11-05'
      }
    ],
    contracts: [
      {
        id: 'contract-002',
        contractNumber: 'HP-2024-002',
        type: 'consulting',
        status: 'active',
        startDate: '2024-03-01',
        endDate: '2025-02-28',
        value: 75000,
        currency: 'USD',
        renewalDate: '2025-01-01',
        autoRenewal: false,
        slaLevel: 'standard',
        services: ['BIA Development', 'Plan Creation', 'Staff Training'],
        terms: {
          rto: 8,
          rpo: 4,
          availabilityTarget: 99.5,
          responseTime: 4
        }
      }
    ],
    assessments: [
      {
        id: 'assessment-002',
        type: 'bia',
        status: 'in_progress',
        scheduledDate: '2024-11-01',
        assessor: 'Sarah Johnson',
        findings: [],
        recommendations: []
      }
    ],
    tags: ['Healthcare', 'Compliance Critical', 'Growth Potential'],
    notes: 'Developing BCM program, high regulatory requirements',
    createdDate: '2021-03-10',
    updatedDate: '2024-11-05'
  },
  {
    id: 'client-003',
    name: 'Metro Financial',
    legalName: 'Metro Financial Services LLC',
    industry: 'Financial Services',
    sector: 'private',
    size: 'large',
    tier: 'platinum',
    status: 'active',
    address: {
      street: '789 Wall Street',
      city: 'New York',
      state: 'NY',
      country: 'United States',
      postalCode: '10005'
    },
    website: 'https://metrofinancial.com',
    phone: '+1-555-0300',
    employeeCount: 5000,
    annualRevenue: 500000000,
    establishedDate: '1995-09-12',
    bcmMaturity: 'optimizing',
    riskProfile: 'critical',
    complianceRequirements: ['SOX', 'FFIEC', 'Basel III', 'GDPR'],
    criticalProcesses: ['Trading Systems', 'Customer Banking', 'Risk Management', 'Regulatory Reporting'],
    accountManager: 'Lisa Wang',
    relationshipStart: '2018-07-01',
    lastContact: '2024-11-12',
    nextReview: '2024-12-20',
    satisfactionScore: 4.7,
    contacts: [
      {
        id: 'contact-004',
        name: 'Robert Taylor',
        title: 'Chief Risk Officer',
        email: 'r.taylor@metrofinancial.com',
        phone: '+1-555-0301',
        isPrimary: true,
        role: 'decision_maker',
        lastContact: '2024-11-12'
      }
    ],
    contracts: [
      {
        id: 'contract-003',
        contractNumber: 'MF-2024-003',
        type: 'service_agreement',
        status: 'active',
        startDate: '2024-01-01',
        endDate: '2026-12-31',
        value: 350000,
        currency: 'USD',
        renewalDate: '2025-10-01',
        autoRenewal: true,
        slaLevel: 'enterprise',
        services: ['Full BCM Program', '24/7 Support', 'Regulatory Compliance'],
        terms: {
          rto: 1,
          rpo: 0.5,
          availabilityTarget: 99.99,
          responseTime: 1
        }
      }
    ],
    assessments: [
      {
        id: 'assessment-003',
        type: 'compliance_audit',
        status: 'completed',
        scheduledDate: '2024-09-01',
        completedDate: '2024-09-30',
        score: 95,
        findings: ['Excellent BCM maturity', 'Strong compliance posture'],
        recommendations: ['Enhance automation', 'Expand scenario testing'],
        nextAssessment: '2025-03-01',
        assessor: 'Michael Chen'
      }
    ],
    tags: ['Financial Services', 'Enterprise', 'Strategic Account'],
    notes: 'Premier client with sophisticated BCM requirements',
    createdDate: '2018-07-01',
    updatedDate: '2024-11-12'
  },
  {
    id: 'client-004',
    name: 'City Government',
    legalName: 'City of Springfield',
    industry: 'Government',
    sector: 'public',
    size: 'large',
    tier: 'silver',
    status: 'active',
    address: {
      street: '100 City Hall Plaza',
      city: 'Springfield',
      state: 'IL',
      country: 'United States',
      postalCode: '62701'
    },
    website: 'https://springfield.gov',
    phone: '+1-555-0400',
    employeeCount: 1200,
    bcmMaturity: 'defined',
    riskProfile: 'medium',
    complianceRequirements: ['FEMA Guidelines', 'State Emergency Management'],
    criticalProcesses: ['Emergency Services', 'Public Safety', 'Utilities Management'],
    accountManager: 'John Smith',
    relationshipStart: '2022-01-15',
    lastContact: '2024-10-30',
    nextReview: '2025-01-15',
    satisfactionScore: 4.0,
    contacts: [
      {
        id: 'contact-005',
        name: 'Jennifer Martinez',
        title: 'Emergency Management Director',
        email: 'j.martinez@springfield.gov',
        phone: '+1-555-0401',
        isPrimary: true,
        role: 'decision_maker',
        lastContact: '2024-10-30'
      }
    ],
    contracts: [
      {
        id: 'contract-004',
        contractNumber: 'SG-2024-004',
        type: 'consulting',
        status: 'active',
        startDate: '2024-04-01',
        endDate: '2025-03-31',
        value: 85000,
        currency: 'USD',
        renewalDate: '2025-02-01',
        autoRenewal: false,
        slaLevel: 'standard',
        services: ['Emergency Planning', 'Training Services', 'Exercise Support'],
        terms: {
          rto: 12,
          rpo: 8,
          availabilityTarget: 99.0,
          responseTime: 8
        }
      }
    ],
    assessments: [
      {
        id: 'assessment-004',
        type: 'risk_assessment',
        status: 'planned',
        scheduledDate: '2024-12-01',
        assessor: 'David Brown',
        findings: [],
        recommendations: []
      }
    ],
    tags: ['Government', 'Public Sector', 'Emergency Management'],
    notes: 'Focus on emergency preparedness and public safety continuity',
    createdDate: '2022-01-15',
    updatedDate: '2024-10-30'
  },
  {
    id: 'client-005',
    name: 'EduTech University',
    legalName: 'EduTech University',
    industry: 'Education',
    sector: 'non_profit',
    size: 'medium',
    tier: 'bronze',
    status: 'prospect',
    address: {
      street: '200 Campus Drive',
      city: 'Boston',
      state: 'MA',
      country: 'United States',
      postalCode: '02115'
    },
    website: 'https://edutech.edu',
    phone: '+1-555-0500',
    employeeCount: 800,
    establishedDate: '1985-08-30',
    bcmMaturity: 'initial',
    riskProfile: 'low',
    complianceRequirements: ['FERPA', 'Title IX'],
    criticalProcesses: ['Student Information Systems', 'Online Learning', 'Research Data'],
    accountManager: 'Sarah Johnson',
    relationshipStart: '2024-09-01',
    lastContact: '2024-11-08',
    nextReview: '2024-11-30',
    contacts: [
      {
        id: 'contact-006',
        name: 'Dr. William Thompson',
        title: 'Vice Provost for IT',
        email: 'w.thompson@edutech.edu',
        phone: '+1-555-0501',
        isPrimary: true,
        role: 'decision_maker',
        lastContact: '2024-11-08'
      }
    ],
    contracts: [],
    assessments: [
      {
        id: 'assessment-005',
        type: 'maturity_assessment',
        status: 'planned',
        scheduledDate: '2024-11-20',
        assessor: 'Lisa Wang',
        findings: [],
        recommendations: []
      }
    ],
    tags: ['Education', 'Prospect', 'Emerging Needs'],
    notes: 'Potential new client, initial BCM awareness stage',
    createdDate: '2024-09-01',
    updatedDate: '2024-11-08'
  }
]

const generateMockMetrics = (): ClientMetrics => ({
  totalClients: 5,
  activeClients: 4,
  newClientsThisMonth: 1,
  churnRate: 5.2,
  averageSatisfaction: 4.1,
  totalRevenue: 630000,
  renewalRate: 92.5,
  assessmentCompliance: 85.0
})

export function ClientsModule() {
  const [activeTab, setActiveTab] = useState('overview')
  const [searchTerm, setSearchTerm] = useState('')
  const [filterStatus, setFilterStatus] = useState<string>('all')
  const [filterTier, setFilterTier] = useState<string>('all')
  const [filterIndustry, setFilterIndustry] = useState<string>('all')
  const [selectedClient, setSelectedClient] = useState<Client | null>(null)

  // Store integration
  const { currentModule, setCurrentModule } = useBCMStore()

  // Data fetching
  const { data: clients = [], isLoading: loadingClients } = useQuery({
    queryKey: ['clients'],
    queryFn: async () => {
      // API client doesn't have clients endpoint, using mock data
      return generateMockClients()
    }
  })

  const { data: metrics, isLoading: loadingMetrics } = useQuery({
    queryKey: ['client-metrics'],
    queryFn: async () => {
      // API client doesn't have clients endpoint, using mock data
      return generateMockMetrics()
    }
  })

  // Filtered clients
  const filteredClients = clients.filter(client => {
    const matchesSearch = client.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         client.industry.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = filterStatus === 'all' || client.status === filterStatus
    const matchesTier = filterTier === 'all' || client.tier === filterTier
    const matchesIndustry = filterIndustry === 'all' || client.industry === filterIndustry

    return matchesSearch && matchesStatus && matchesTier && matchesIndustry
  })

  // Metrics calculations
  const activeContracts = clients.reduce((sum, client) =>
    sum + client.contracts.filter(c => c.status === 'active').length, 0)

  const pendingAssessments = clients.reduce((sum, client) =>
    sum + client.assessments.filter(a => a.status === 'planned' || a.status === 'in_progress').length, 0)

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'text-green-600 bg-green-50'
      case 'inactive': return 'text-gray-600 bg-gray-50'
      case 'prospect': return 'text-blue-600 bg-blue-50'
      case 'suspended': return 'text-red-600 bg-red-50'
      default: return 'text-gray-600 bg-gray-50'
    }
  }

  const getTierColor = (tier: string) => {
    switch (tier) {
      case 'platinum': return 'text-purple-600 bg-purple-50'
      case 'gold': return 'text-yellow-600 bg-yellow-50'
      case 'silver': return 'text-gray-600 bg-gray-50'
      case 'bronze': return 'text-orange-600 bg-orange-50'
      default: return 'text-gray-600 bg-gray-50'
    }
  }

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'low': return 'text-green-600 bg-green-50'
      case 'medium': return 'text-yellow-600 bg-yellow-50'
      case 'high': return 'text-orange-600 bg-orange-50'
      case 'critical': return 'text-red-600 bg-red-50'
      default: return 'text-gray-600 bg-gray-50'
    }
  }

  const getMaturityColor = (maturity: string) => {
    switch (maturity) {
      case 'optimizing': return 'text-purple-600 bg-purple-50'
      case 'managed': return 'text-blue-600 bg-blue-50'
      case 'defined': return 'text-green-600 bg-green-50'
      case 'developing': return 'text-yellow-600 bg-yellow-50'
      case 'initial': return 'text-orange-600 bg-orange-50'
      default: return 'text-gray-600 bg-gray-50'
    }
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Client Management</h1>
          <p className="text-gray-600 mt-1">Manage client relationships, contracts, and BCM assessments</p>
        </div>
        <div className="flex items-center space-x-3">
          <Button variant="outline">
            <Download className="h-4 w-4 mr-2" />
            Export Report
          </Button>
          <Button>
            <Plus className="h-4 w-4 mr-2" />
            Add Client
          </Button>
        </div>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="clients">Clients</TabsTrigger>
          <TabsTrigger value="contracts">Contracts</TabsTrigger>
          <TabsTrigger value="assessments">Assessments</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-6">
          {/* Key Metrics */}
          {metrics && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Total Clients</CardTitle>
                  <Building2 className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{metrics.totalClients}</div>
                  <div className="text-xs text-muted-foreground mt-1">
                    {metrics.activeClients} active clients
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Total Revenue</CardTitle>
                  <DollarSign className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">${metrics.totalRevenue.toLocaleString()}</div>
                  <div className="text-xs text-muted-foreground mt-1">
                    Annual recurring revenue
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Satisfaction Score</CardTitle>
                  <Star className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{metrics.averageSatisfaction}</div>
                  <div className="text-xs text-muted-foreground mt-1">
                    Average client rating
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Renewal Rate</CardTitle>
                  <TrendingUp className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{metrics.renewalRate}%</div>
                  <div className="text-xs text-muted-foreground mt-1">
                    Contract renewal rate
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {/* Client Distribution */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Clients by Tier</CardTitle>
                <CardDescription>Distribution of clients across service tiers</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {['platinum', 'gold', 'silver', 'bronze'].map((tier) => {
                    const count = clients.filter(c => c.tier === tier).length
                    const percentage = clients.length > 0 ? (count / clients.length) * 100 : 0
                    return (
                      <div key={tier} className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <Badge variant="outline" className={getTierColor(tier)}>
                            {tier}
                          </Badge>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Progress value={percentage} className="w-20" />
                          <span className="text-sm font-medium">{count}</span>
                        </div>
                      </div>
                    )
                  })}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>BCM Maturity Levels</CardTitle>
                <CardDescription>Client BCM program maturity distribution</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {['optimizing', 'managed', 'defined', 'developing', 'initial'].map((maturity) => {
                    const count = clients.filter(c => c.bcmMaturity === maturity).length
                    const percentage = clients.length > 0 ? (count / clients.length) * 100 : 0
                    return (
                      <div key={maturity} className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <Badge variant="outline" className={getMaturityColor(maturity)}>
                            {maturity}
                          </Badge>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Progress value={percentage} className="w-20" />
                          <span className="text-sm font-medium">{count}</span>
                        </div>
                      </div>
                    )
                  })}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Recent Activity */}
          <Card>
            <CardHeader>
              <CardTitle>Recent Client Activity</CardTitle>
              <CardDescription>Latest client interactions and updates</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {clients
                  .filter(c => c.lastContact)
                  .sort((a, b) => new Date(b.lastContact!).getTime() - new Date(a.lastContact!).getTime())
                  .slice(0, 5)
                  .map((client) => (
                    <div key={client.id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                          <Building2 className="h-5 w-5 text-blue-600" />
                        </div>
                        <div>
                          <h4 className="font-medium">{client.name}</h4>
                          <p className="text-sm text-gray-600">{client.industry}</p>
                          <div className="flex items-center space-x-2 mt-1">
                            <Badge variant="outline" className={getStatusColor(client.status)}>
                              {client.status}
                            </Badge>
                            <Badge variant="outline" className={getTierColor(client.tier)}>
                              {client.tier}
                            </Badge>
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-sm font-medium">
                          Last Contact: {client.lastContact ? format(new Date(client.lastContact), 'MMM dd, yyyy') : 'Never'}
                        </div>
                        <div className="text-xs text-gray-500">
                          Account Manager: {client.accountManager}
                        </div>
                      </div>
                    </div>
                  ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Clients Tab */}
        <TabsContent value="clients" className="space-y-6">
          {/* Client Filters */}
          <Card>
            <CardHeader>
              <CardTitle>Client Directory</CardTitle>
              <CardDescription>Comprehensive client information and relationship management</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
                <div className="relative">
                  <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                  <Input
                    placeholder="Search clients..."
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
                    <SelectItem value="active">Active</SelectItem>
                    <SelectItem value="inactive">Inactive</SelectItem>
                    <SelectItem value="prospect">Prospect</SelectItem>
                    <SelectItem value="suspended">Suspended</SelectItem>
                  </SelectContent>
                </Select>
                <Select value={filterTier} onValueChange={setFilterTier}>
                  <SelectTrigger>
                    <SelectValue placeholder="Filter by tier" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Tiers</SelectItem>
                    <SelectItem value="platinum">Platinum</SelectItem>
                    <SelectItem value="gold">Gold</SelectItem>
                    <SelectItem value="silver">Silver</SelectItem>
                    <SelectItem value="bronze">Bronze</SelectItem>
                  </SelectContent>
                </Select>
                <Select value={filterIndustry} onValueChange={setFilterIndustry}>
                  <SelectTrigger>
                    <SelectValue placeholder="Filter by industry" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Industries</SelectItem>
                    <SelectItem value="Technology">Technology</SelectItem>
                    <SelectItem value="Healthcare">Healthcare</SelectItem>
                    <SelectItem value="Financial Services">Financial Services</SelectItem>
                    <SelectItem value="Government">Government</SelectItem>
                    <SelectItem value="Education">Education</SelectItem>
                  </SelectContent>
                </Select>
                <Button variant="outline">
                  <Filter className="h-4 w-4 mr-2" />
                  Apply
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Clients Grid */}
          <div className="grid gap-6">
            {filteredClients.map((client) => (
              <Card key={client.id} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                        <Building2 className="h-6 w-6 text-blue-600" />
                      </div>
                      <div>
                        <CardTitle className="text-lg">{client.name}</CardTitle>
                        <CardDescription>{client.industry} • {client.address.city}, {client.address.state}</CardDescription>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Badge variant="outline" className={getStatusColor(client.status)}>
                        {client.status}
                      </Badge>
                      <Badge variant="outline" className={getTierColor(client.tier)}>
                        {client.tier}
                      </Badge>
                      <Badge variant="outline" className={getRiskColor(client.riskProfile)}>
                        {client.riskProfile} risk
                      </Badge>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div>
                        <span className="text-sm font-medium">Account Manager:</span>
                        <p className="text-sm text-gray-600">{client.accountManager}</p>
                      </div>
                      <div>
                        <span className="text-sm font-medium">BCM Maturity:</span>
                        <Badge variant="outline" className={getMaturityColor(client.bcmMaturity)}>
                          {client.bcmMaturity}
                        </Badge>
                      </div>
                      <div>
                        <span className="text-sm font-medium">Employees:</span>
                        <p className="text-sm text-gray-600">{client.employeeCount?.toLocaleString() || 'N/A'}</p>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <span className="text-sm font-medium">Active Contracts:</span>
                        <p className="text-sm text-gray-600">{client.contracts.filter(c => c.status === 'active').length}</p>
                      </div>
                      <div>
                        <span className="text-sm font-medium">Satisfaction Score:</span>
                        <div className="flex items-center space-x-1">
                          <Star className="h-4 w-4 text-yellow-500" />
                          <span className="text-sm text-gray-600">{client.satisfactionScore || 'N/A'}</span>
                        </div>
                      </div>
                    </div>

                    {client.complianceRequirements.length > 0 && (
                      <div>
                        <span className="text-sm font-medium">Compliance Requirements:</span>
                        <div className="flex flex-wrap gap-1 mt-1">
                          {client.complianceRequirements.slice(0, 3).map((req, index) => (
                            <Badge key={index} variant="outline" >
                              {req}
                            </Badge>
                          ))}
                          {client.complianceRequirements.length > 3 && (
                            <Badge variant="outline" >
                              +{client.complianceRequirements.length - 3}
                            </Badge>
                          )}
                        </div>
                      </div>
                    )}

                    <div className="flex items-center justify-between pt-4 border-t">
                      <div className="flex items-center space-x-2">
                        <Button variant="outline" >
                          <Eye className="h-4 w-4 mr-2" />
                          View Details
                        </Button>
                        <Button variant="outline" >
                          <Edit className="h-4 w-4 mr-2" />
                          Edit
                        </Button>
                        <Button variant="outline" >
                          <Send className="h-4 w-4 mr-2" />
                          Contact
                        </Button>
                      </div>
                      <div className="text-xs text-gray-500">
                        {client.lastContact ? `Last contact: ${format(new Date(client.lastContact), 'MMM dd, yyyy')}` : 'No recent contact'}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Contracts Tab */}
        <TabsContent value="contracts" className="space-y-6">
          {/* Contract Overview */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Active Contracts</CardTitle>
                <FileText className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{activeContracts}</div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Contract Value</CardTitle>
                <DollarSign className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  ${clients.reduce((sum, client) =>
                    sum + client.contracts.filter(c => c.status === 'active').reduce((cSum, contract) => cSum + contract.value, 0), 0
                  ).toLocaleString()}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Expiring Soon</CardTitle>
                <AlertTriangle className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {clients.reduce((sum, client) =>
                    sum + client.contracts.filter(c =>
                      c.status === 'active' &&
                      new Date(c.endDate) < new Date(Date.now() + 90 * 24 * 60 * 60 * 1000)
                    ).length, 0
                  )}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Auto Renewals</CardTitle>
                <CheckCircle className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {clients.reduce((sum, client) =>
                    sum + client.contracts.filter(c => c.autoRenewal).length, 0
                  )}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Contracts List */}
          <Card>
            <CardHeader>
              <CardTitle>Contract Details</CardTitle>
              <CardDescription>Comprehensive view of all client contracts</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {clients.flatMap(client =>
                  client.contracts.map(contract => (
                    <div key={contract.id} className="p-4 border rounded-lg">
                      <div className="flex items-center justify-between mb-3">
                        <div>
                          <h4 className="font-medium">{client.name} - {contract.contractNumber}</h4>
                          <p className="text-sm text-gray-600">{contract.type.replace('_', ' ')}</p>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Badge variant="outline" className={
                            contract.status === 'active' ? 'text-green-600 bg-green-50' :
                            contract.status === 'expired' ? 'text-red-600 bg-red-50' :
                            'text-gray-600 bg-gray-50'
                          }>
                            {contract.status}
                          </Badge>
                          <Badge variant="outline" className={
                            contract.slaLevel === 'enterprise' ? 'text-purple-600 bg-purple-50' :
                            contract.slaLevel === 'premium' ? 'text-blue-600 bg-blue-50' :
                            'text-gray-600 bg-gray-50'
                          }>
                            {contract.slaLevel}
                          </Badge>
                        </div>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                        <div>
                          <span className="text-sm font-medium">Value:</span>
                          <p className="text-sm text-gray-600">${contract.value.toLocaleString()} {contract.currency}</p>
                        </div>
                        <div>
                          <span className="text-sm font-medium">Period:</span>
                          <p className="text-sm text-gray-600">
                            {format(new Date(contract.startDate), 'MMM dd, yyyy')} - {format(new Date(contract.endDate), 'MMM dd, yyyy')}
                          </p>
                        </div>
                        <div>
                          <span className="text-sm font-medium">RTO/RPO:</span>
                          <p className="text-sm text-gray-600">{contract.terms.rto}h / {contract.terms.rpo}h</p>
                        </div>
                        <div>
                          <span className="text-sm font-medium">Availability:</span>
                          <p className="text-sm text-gray-600">{contract.terms.availabilityTarget}%</p>
                        </div>
                      </div>

                      {contract.services.length > 0 && (
                        <div className="mt-3">
                          <span className="text-sm font-medium">Services:</span>
                          <div className="flex flex-wrap gap-1 mt-1">
                            {contract.services.map((service, index) => (
                              <Badge key={index} variant="outline" >
                                {service}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      )}

                      <div className="flex items-center justify-between pt-3 border-t mt-3">
                        <div className="text-xs text-gray-500">
                          {contract.autoRenewal ? 'Auto-renewal enabled' : 'Manual renewal required'}
                          {contract.renewalDate && ` • Renewal: ${format(new Date(contract.renewalDate), 'MMM dd, yyyy')}`}
                        </div>
                        <div className="flex items-center space-x-2">
                          <Button variant="outline" >
                            <Eye className="h-4 w-4 mr-2" />
                            View Contract
                          </Button>
                          <Button variant="outline" >
                            <Edit className="h-4 w-4 mr-2" />
                            Amend
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Assessments Tab */}
        <TabsContent value="assessments" className="space-y-6">
          {/* Assessment Overview */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Assessments</CardTitle>
                <Target className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {clients.reduce((sum, client) => sum + client.assessments.length, 0)}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Completed</CardTitle>
                <CheckCircle className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {clients.reduce((sum, client) =>
                    sum + client.assessments.filter(a => a.status === 'completed').length, 0
                  )}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">In Progress</CardTitle>
                <Clock className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {clients.reduce((sum, client) =>
                    sum + client.assessments.filter(a => a.status === 'in_progress').length, 0
                  )}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Overdue</CardTitle>
                <AlertTriangle className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {clients.reduce((sum, client) =>
                    sum + client.assessments.filter(a => a.status === 'overdue').length, 0
                  )}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Assessments List */}
          <Card>
            <CardHeader>
              <CardTitle>Client Assessments</CardTitle>
              <CardDescription>Track BCM assessments and evaluation progress</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {clients.flatMap(client =>
                  client.assessments.map(assessment => (
                    <div key={assessment.id} className="p-4 border rounded-lg">
                      <div className="flex items-center justify-between mb-3">
                        <div>
                          <h4 className="font-medium">{client.name} - {assessment.type.replace('_', ' ')}</h4>
                          <p className="text-sm text-gray-600">Assessor: {assessment.assessor}</p>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Badge variant="outline" className={
                            assessment.status === 'completed' ? 'text-green-600 bg-green-50' :
                            assessment.status === 'in_progress' ? 'text-blue-600 bg-blue-50' :
                            assessment.status === 'overdue' ? 'text-red-600 bg-red-50' :
                            'text-orange-600 bg-orange-50'
                          }>
                            {assessment.status.replace('_', ' ')}
                          </Badge>
                          {assessment.score && (
                            <Badge variant="outline">
                              Score: {assessment.score}%
                            </Badge>
                          )}
                        </div>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div>
                          <span className="text-sm font-medium">Scheduled:</span>
                          <p className="text-sm text-gray-600">{format(new Date(assessment.scheduledDate), 'MMM dd, yyyy')}</p>
                        </div>
                        {assessment.completedDate && (
                          <div>
                            <span className="text-sm font-medium">Completed:</span>
                            <p className="text-sm text-gray-600">{format(new Date(assessment.completedDate), 'MMM dd, yyyy')}</p>
                          </div>
                        )}
                        {assessment.nextAssessment && (
                          <div>
                            <span className="text-sm font-medium">Next Assessment:</span>
                            <p className="text-sm text-gray-600">{format(new Date(assessment.nextAssessment), 'MMM dd, yyyy')}</p>
                          </div>
                        )}
                      </div>

                      {assessment.findings.length > 0 && (
                        <div className="mt-3">
                          <span className="text-sm font-medium">Key Findings:</span>
                          <ul className="text-sm text-gray-600 mt-1 list-disc list-inside">
                            {assessment.findings.slice(0, 2).map((finding, index) => (
                              <li key={index}>{finding}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      <div className="flex items-center justify-between pt-3 border-t mt-3">
                        <span className="text-xs text-gray-500">
                          {assessment.recommendations.length} recommendation(s)
                        </span>
                        <div className="flex items-center space-x-2">
                          <Button variant="outline" >
                            <Eye className="h-4 w-4 mr-2" />
                            View Report
                          </Button>
                          <Button variant="outline" >
                            <Calendar className="h-4 w-4 mr-2" />
                            Schedule Follow-up
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Analytics Tab */}
        <TabsContent value="analytics" className="space-y-6">
          {/* Analytics Overview */}
          <Card>
            <CardHeader>
              <CardTitle>Client Analytics Dashboard</CardTitle>
              <CardDescription>Comprehensive analysis of client portfolio performance</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">{clients.length}</div>
                  <div className="text-sm text-gray-600">Total Clients</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">
                    ${clients.reduce((sum, client) =>
                      sum + client.contracts.filter(c => c.status === 'active').reduce((cSum, contract) => cSum + contract.value, 0), 0
                    ).toLocaleString()}
                  </div>
                  <div className="text-sm text-gray-600">Annual Revenue</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-yellow-600">
                    {(clients.filter(c => c.satisfactionScore).reduce((sum, c) => sum + c.satisfactionScore!, 0) /
                      clients.filter(c => c.satisfactionScore).length || 0).toFixed(1)}
                  </div>
                  <div className="text-sm text-gray-600">Avg Satisfaction</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-purple-600">
                    {Math.round((clients.filter(c => c.status === 'active').length / clients.length) * 100)}%
                  </div>
                  <div className="text-sm text-gray-600">Client Retention</div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Industry Distribution */}
          <Card>
            <CardHeader>
              <CardTitle>Industry Distribution</CardTitle>
              <CardDescription>Client portfolio by industry sector</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {Array.from(new Set(clients.map(c => c.industry))).map((industry) => {
                  const count = clients.filter(c => c.industry === industry).length
                  const percentage = (count / clients.length) * 100
                  const revenue = clients
                    .filter(c => c.industry === industry)
                    .reduce((sum, client) =>
                      sum + client.contracts.filter(c => c.status === 'active').reduce((cSum, contract) => cSum + contract.value, 0), 0
                    )

                  return (
                    <div key={industry} className="flex items-center justify-between p-3 border rounded-lg">
                      <div>
                        <h4 className="font-medium">{industry}</h4>
                        <p className="text-sm text-gray-600">{count} clients • ${revenue.toLocaleString()} revenue</p>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Progress value={percentage} className="w-24" />
                        <span className="text-sm font-medium">{percentage.toFixed(1)}%</span>
                      </div>
                    </div>
                  )
                })}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}