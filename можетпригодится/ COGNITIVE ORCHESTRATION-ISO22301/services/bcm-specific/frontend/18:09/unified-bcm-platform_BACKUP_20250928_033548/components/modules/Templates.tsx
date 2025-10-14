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
import { Checkbox } from '@/components/ui/checkbox'
import { Separator } from '@/components/ui/separator'
import {
  FileText,
  Download,
  Upload,
  Copy,
  Edit,
  Plus,
  Search,
  Filter,
  Eye,
  Star,
  Clock,
  Users,
  Folder,
  FolderOpen,
  File,
  BookOpen,
  Shield,
  AlertTriangle,
  CheckCircle,
  Settings,
  Share,
  Archive,
  BarChart3
} from 'lucide-react'
import { format } from 'date-fns'
import { cn } from '@/lib/utils'

// Types
interface TemplateSection {
  id: string
  title: string
  description?: string
  content: string
  order: number
  required: boolean
  placeholder?: string
  fieldType: 'text' | 'textarea' | 'date' | 'number' | 'select' | 'checkbox' | 'table'
  options?: string[]
  validation?: {
    required: boolean
    minLength?: number
    maxLength?: number
    pattern?: string
  }
}

interface Template {
  id: string
  name: string
  description: string
  category: 'plan' | 'policy' | 'procedure' | 'form' | 'report' | 'checklist' | 'communication' | 'exercise'
  type: 'business_continuity_plan' | 'crisis_communication' | 'incident_report' | 'risk_assessment' | 'bia_form' | 'exercise_scenario' | 'policy_document' | 'procedure_sop' | 'checklist_audit' | 'notification_template'
  version: string
  status: 'draft' | 'active' | 'archived' | 'under_review'
  author: string
  lastModifiedBy: string
  createdDate: string
  modifiedDate: string
  approvedDate?: string
  approvedBy?: string
  tags: string[]
  sections: TemplateSection[]
  metadata: {
    industry?: string[]
    compliance?: string[]
    applicableStandards?: string[]
    targetAudience?: string[]
    complexity: 'simple' | 'moderate' | 'complex'
    estimatedCompletionTime: number // minutes
  }
  usage: {
    timesUsed: number
    lastUsed?: string
    averageRating: number
    totalRatings: number
  }
  permissions: {
    viewRoles: string[]
    editRoles: string[]
    approveRoles: string[]
  }
}

interface TemplateInstance {
  id: string
  templateId: string
  templateName: string
  instanceName: string
  createdBy: string
  createdDate: string
  lastModified: string
  status: 'draft' | 'in_progress' | 'completed' | 'approved' | 'rejected'
  completedSections: string[]
  assignedTo?: string
  dueDate?: string
  completionPercentage: number
  content: Record<string, any>
  notes?: string
  reviewHistory: {
    date: string
    reviewer: string
    action: 'created' | 'modified' | 'reviewed' | 'approved' | 'rejected'
    comments?: string
  }[]
}

interface TemplateLibrary {
  id: string
  name: string
  description: string
  isPublic: boolean
  organization: string
  templates: Template[]
  subscribers: number
  lastUpdated: string
  maintainer: string
}

interface TemplateCategory {
  id: string
  name: string
  description: string
  icon: string
  templateCount: number
  subcategories?: string[]
}

// Mock Data
const generateMockTemplates = (): Template[] => [
  {
    id: 'template-001',
    name: 'Business Continuity Plan Template',
    description: 'Comprehensive template for creating business continuity plans following ISO 22301 standards',
    category: 'plan',
    type: 'business_continuity_plan',
    version: '2.1',
    status: 'active',
    author: 'BCM Team',
    lastModifiedBy: 'Sarah Johnson',
    createdDate: '2024-01-15',
    modifiedDate: '2024-10-01',
    approvedDate: '2024-10-05',
    approvedBy: 'John Smith',
    tags: ['ISO 22301', 'BCP', 'Core Template'],
    sections: [
      {
        id: 'section-001',
        title: 'Executive Summary',
        description: 'High-level overview of the business continuity plan',
        content: 'This section provides an executive summary of the business continuity plan...',
        order: 1,
        required: true,
        fieldType: 'textarea',
        validation: { required: true, minLength: 100, maxLength: 1000 }
      },
      {
        id: 'section-002',
        title: 'Scope and Objectives',
        description: 'Define the scope and objectives of the business continuity plan',
        content: 'Define the scope of this business continuity plan...',
        order: 2,
        required: true,
        fieldType: 'textarea',
        validation: { required: true, minLength: 50 }
      },
      {
        id: 'section-003',
        title: 'Business Impact Analysis',
        description: 'Summary of business impact analysis findings',
        content: 'Based on the business impact analysis conducted...',
        order: 3,
        required: true,
        fieldType: 'table'
      },
      {
        id: 'section-004',
        title: 'Recovery Strategies',
        description: 'Detailed recovery strategies for critical business functions',
        content: 'Recovery strategies have been developed for each critical function...',
        order: 4,
        required: true,
        fieldType: 'textarea'
      },
      {
        id: 'section-005',
        title: 'Plan Activation',
        description: 'Procedures for activating the business continuity plan',
        content: 'The business continuity plan is activated when...',
        order: 5,
        required: true,
        fieldType: 'textarea'
      }
    ],
    metadata: {
      industry: ['All Industries'],
      compliance: ['ISO 22301', 'SOX', 'GDPR'],
      applicableStandards: ['ISO 22301:2019', 'NIST Cybersecurity Framework'],
      targetAudience: ['BCM Managers', 'Business Unit Managers', 'Executive Team'],
      complexity: 'complex',
      estimatedCompletionTime: 480
    },
    usage: {
      timesUsed: 45,
      lastUsed: '2024-11-10',
      averageRating: 4.6,
      totalRatings: 12
    },
    permissions: {
      viewRoles: ['All Users'],
      editRoles: ['BCM Manager', 'Administrator'],
      approveRoles: ['BCM Manager', 'Executive']
    }
  },
  {
    id: 'template-002',
    name: 'Crisis Communication Template',
    description: 'Template for creating crisis communication messages for different stakeholder groups',
    category: 'communication',
    type: 'crisis_communication',
    version: '1.3',
    status: 'active',
    author: 'Communications Team',
    lastModifiedBy: 'Mike Chen',
    createdDate: '2024-02-20',
    modifiedDate: '2024-09-15',
    approvedDate: '2024-09-20',
    approvedBy: 'Lisa Wang',
    tags: ['Crisis', 'Communication', 'Stakeholders'],
    sections: [
      {
        id: 'section-006',
        title: 'Incident Details',
        description: 'Basic information about the incident',
        content: 'Incident: [Brief description of the incident]',
        order: 1,
        required: true,
        placeholder: 'Describe the incident briefly',
        fieldType: 'textarea',
        validation: { required: true, maxLength: 500 }
      },
      {
        id: 'section-007',
        title: 'Impact Assessment',
        description: 'Assessment of the impact on operations and stakeholders',
        content: 'Impact: [Description of current and potential impact]',
        order: 2,
        required: true,
        fieldType: 'textarea'
      },
      {
        id: 'section-008',
        title: 'Actions Taken',
        description: 'Immediate actions taken to address the situation',
        content: 'Actions: [List of actions taken or being taken]',
        order: 3,
        required: true,
        fieldType: 'textarea'
      },
      {
        id: 'section-009',
        title: 'Next Steps',
        description: 'Planned next steps and timeline',
        content: 'Next steps: [Planned actions and timeline]',
        order: 4,
        required: false,
        fieldType: 'textarea'
      }
    ],
    metadata: {
      industry: ['All Industries'],
      compliance: ['Crisis Management Standards'],
      targetAudience: ['Crisis Team', 'Communications Team', 'Management'],
      complexity: 'simple',
      estimatedCompletionTime: 30
    },
    usage: {
      timesUsed: 23,
      lastUsed: '2024-11-05',
      averageRating: 4.3,
      totalRatings: 8
    },
    permissions: {
      viewRoles: ['All Users'],
      editRoles: ['Crisis Team', 'Communications Team'],
      approveRoles: ['Crisis Manager', 'Communications Director']
    }
  },
  {
    id: 'template-003',
    name: 'Incident Report Form',
    description: 'Standardized form for reporting and documenting incidents',
    category: 'form',
    type: 'incident_report',
    version: '3.0',
    status: 'active',
    author: 'Risk Management',
    lastModifiedBy: 'David Brown',
    createdDate: '2024-03-10',
    modifiedDate: '2024-10-20',
    tags: ['Incident', 'Reporting', 'Documentation'],
    sections: [
      {
        id: 'section-010',
        title: 'Incident Information',
        description: 'Basic incident details',
        content: '',
        order: 1,
        required: true,
        fieldType: 'text'
      },
      {
        id: 'section-011',
        title: 'Date and Time',
        description: 'When the incident occurred',
        content: '',
        order: 2,
        required: true,
        fieldType: 'date'
      },
      {
        id: 'section-012',
        title: 'Severity Level',
        description: 'Assessment of incident severity',
        content: '',
        order: 3,
        required: true,
        fieldType: 'select',
        options: ['Low', 'Medium', 'High', 'Critical']
      },
      {
        id: 'section-013',
        title: 'Description',
        description: 'Detailed description of what happened',
        content: '',
        order: 4,
        required: true,
        fieldType: 'textarea',
        validation: { required: true, minLength: 50 }
      }
    ],
    metadata: {
      targetAudience: ['All Employees', 'Security Team', 'Management'],
      complexity: 'simple',
      estimatedCompletionTime: 15
    },
    usage: {
      timesUsed: 67,
      lastUsed: '2024-11-12',
      averageRating: 4.1,
      totalRatings: 15
    },
    permissions: {
      viewRoles: ['All Users'],
      editRoles: ['All Users'],
      approveRoles: ['Security Manager', 'Risk Manager']
    }
  },
  {
    id: 'template-004',
    name: 'Exercise Scenario Template',
    description: 'Template for creating business continuity exercise scenarios',
    category: 'exercise',
    type: 'exercise_scenario',
    version: '1.5',
    status: 'active',
    author: 'BCM Team',
    lastModifiedBy: 'Sarah Johnson',
    createdDate: '2024-04-05',
    modifiedDate: '2024-08-30',
    tags: ['Exercise', 'Testing', 'Scenario'],
    sections: [
      {
        id: 'section-014',
        title: 'Exercise Objectives',
        description: 'Define what the exercise aims to achieve',
        content: 'This exercise aims to test...',
        order: 1,
        required: true,
        fieldType: 'textarea'
      },
      {
        id: 'section-015',
        title: 'Scenario Description',
        description: 'Detailed scenario narrative',
        content: 'Scenario: [Describe the disruptive event]',
        order: 2,
        required: true,
        fieldType: 'textarea'
      },
      {
        id: 'section-016',
        title: 'Participant Roles',
        description: 'Define roles and responsibilities for participants',
        content: 'Participants will assume the following roles...',
        order: 3,
        required: true,
        fieldType: 'table'
      }
    ],
    metadata: {
      targetAudience: ['BCM Team', 'Exercise Coordinators'],
      complexity: 'moderate',
      estimatedCompletionTime: 120
    },
    usage: {
      timesUsed: 18,
      lastUsed: '2024-10-25',
      averageRating: 4.4,
      totalRatings: 5
    },
    permissions: {
      viewRoles: ['BCM Team', 'Exercise Participants'],
      editRoles: ['BCM Manager', 'Exercise Coordinator'],
      approveRoles: ['BCM Manager']
    }
  },
  {
    id: 'template-005',
    name: 'BIA Assessment Checklist',
    description: 'Comprehensive checklist for conducting business impact analysis',
    category: 'checklist',
    type: 'bia_form',
    version: '2.0',
    status: 'active',
    author: 'BIA Team',
    lastModifiedBy: 'Lisa Wang',
    createdDate: '2024-05-15',
    modifiedDate: '2024-09-10',
    tags: ['BIA', 'Assessment', 'Checklist'],
    sections: [
      {
        id: 'section-017',
        title: 'Business Function Identification',
        description: 'Identify and list business functions to be assessed',
        content: '',
        order: 1,
        required: true,
        fieldType: 'table'
      },
      {
        id: 'section-018',
        title: 'Impact Categories',
        description: 'Define impact categories and measurement criteria',
        content: '',
        order: 2,
        required: true,
        fieldType: 'checklist'
      },
      {
        id: 'section-019',
        title: 'Time Sensitivity Analysis',
        description: 'Analyze time sensitivity for each function',
        content: '',
        order: 3,
        required: true,
        fieldType: 'table'
      }
    ],
    metadata: {
      compliance: ['ISO 22301'],
      targetAudience: ['BIA Analysts', 'Business Unit Managers'],
      complexity: 'complex',
      estimatedCompletionTime: 240
    },
    usage: {
      timesUsed: 12,
      lastUsed: '2024-11-01',
      averageRating: 4.7,
      totalRatings: 3
    },
    permissions: {
      viewRoles: ['BIA Team', 'BCM Team'],
      editRoles: ['BIA Analyst', 'BCM Manager'],
      approveRoles: ['BCM Manager']
    }
  }
]

const generateMockInstances = (): TemplateInstance[] => [
  {
    id: 'instance-001',
    templateId: 'template-001',
    templateName: 'Business Continuity Plan Template',
    instanceName: 'IT Department BCP 2024',
    createdBy: 'John Smith',
    createdDate: '2024-10-15',
    lastModified: '2024-11-10',
    status: 'in_progress',
    completedSections: ['section-001', 'section-002'],
    assignedTo: 'IT Manager',
    dueDate: '2024-12-01',
    completionPercentage: 40,
    content: {
      'section-001': 'Executive summary for IT Department BCP...',
      'section-002': 'Scope covers all IT services and infrastructure...'
    },
    notes: 'Initial sections completed, pending BIA data',
    reviewHistory: [
      {
        date: '2024-10-15',
        reviewer: 'John Smith',
        action: 'created',
        comments: 'Initial creation of IT BCP'
      },
      {
        date: '2024-11-01',
        reviewer: 'IT Manager',
        action: 'modified',
        comments: 'Updated scope section'
      }
    ]
  },
  {
    id: 'instance-002',
    templateId: 'template-002',
    templateName: 'Crisis Communication Template',
    instanceName: 'Server Outage Communication',
    createdBy: 'Sarah Johnson',
    createdDate: '2024-11-12',
    lastModified: '2024-11-12',
    status: 'completed',
    completedSections: ['section-006', 'section-007', 'section-008', 'section-009'],
    completionPercentage: 100,
    content: {
      'section-006': 'Critical server infrastructure experiencing outage affecting customer services',
      'section-007': 'Approximately 1000 customers affected, estimated service disruption 2-4 hours',
      'section-008': 'IT team mobilized, backup systems activated, vendor support engaged',
      'section-009': 'Full service restoration expected within 2 hours, customer updates every 30 minutes'
    },
    reviewHistory: [
      {
        date: '2024-11-12',
        reviewer: 'Sarah Johnson',
        action: 'created'
      },
      {
        date: '2024-11-12',
        reviewer: 'Crisis Manager',
        action: 'approved',
        comments: 'Approved for immediate distribution'
      }
    ]
  },
  {
    id: 'instance-003',
    templateId: 'template-003',
    templateName: 'Incident Report Form',
    instanceName: 'Security Breach Report - Nov 2024',
    createdBy: 'David Brown',
    createdDate: '2024-11-08',
    lastModified: '2024-11-09',
    status: 'approved',
    completedSections: ['section-010', 'section-011', 'section-012', 'section-013'],
    completionPercentage: 100,
    content: {
      'section-010': 'Unauthorized access attempt to customer database',
      'section-011': '2024-11-08 14:30',
      'section-012': 'Medium',
      'section-013': 'Multiple failed login attempts detected on customer portal, followed by successful breach of test account'
    },
    reviewHistory: [
      {
        date: '2024-11-08',
        reviewer: 'David Brown',
        action: 'created'
      },
      {
        date: '2024-11-09',
        reviewer: 'Security Manager',
        action: 'approved',
        comments: 'Incident confirmed and investigation initiated'
      }
    ]
  }
]

const generateMockCategories = (): TemplateCategory[] => [
  {
    id: 'cat-001',
    name: 'Business Continuity Plans',
    description: 'Comprehensive templates for creating business continuity plans',
    icon: 'shield',
    templateCount: 8,
    subcategories: ['Department Plans', 'Function-Specific Plans', 'Site Plans']
  },
  {
    id: 'cat-002',
    name: 'Communication Templates',
    description: 'Crisis and stakeholder communication templates',
    icon: 'users',
    templateCount: 12,
    subcategories: ['Internal Communications', 'External Communications', 'Media Relations']
  },
  {
    id: 'cat-003',
    name: 'Assessment Forms',
    description: 'Various assessment and evaluation forms',
    icon: 'checklist',
    templateCount: 6,
    subcategories: ['BIA Forms', 'Risk Assessments', 'Audit Checklists']
  },
  {
    id: 'cat-004',
    name: 'Exercise Templates',
    description: 'Templates for planning and conducting exercises',
    icon: 'target',
    templateCount: 5,
    subcategories: ['Tabletop Exercises', 'Functional Exercises', 'Full-Scale Exercises']
  }
]

export function TemplatesModule() {
  const [activeTab, setActiveTab] = useState('overview')
  const [searchTerm, setSearchTerm] = useState('')
  const [filterCategory, setFilterCategory] = useState<string>('all')
  const [filterStatus, setFilterStatus] = useState<string>('all')
  const [filterComplexity, setFilterComplexity] = useState<string>('all')
  const [selectedTemplate, setSelectedTemplate] = useState<Template | null>(null)

  // Store integration
  const { currentModule, setCurrentModule } = useBCMStore()

  // Data fetching
  const { data: templates = [], isLoading: loadingTemplates } = useQuery({
    queryKey: ['templates'],
    queryFn: async () => {
      if (process.env.NEXT_PUBLIC_USE_REAL_API === 'true') {
        return await apiClient.templates.getAll()
      }
      return generateMockTemplates()
    }
  })

  const { data: instances = [], isLoading: loadingInstances } = useQuery({
    queryKey: ['template-instances'],
    queryFn: async () => {
      if (process.env.NEXT_PUBLIC_USE_REAL_API === 'true') {
        return await apiClient.templates.getInstances()
      }
      return generateMockInstances()
    }
  })

  const { data: categories = [], isLoading: loadingCategories } = useQuery({
    queryKey: ['template-categories'],
    queryFn: async () => {
      if (process.env.NEXT_PUBLIC_USE_REAL_API === 'true') {
        return await apiClient.templates.getCategories()
      }
      return generateMockCategories()
    }
  })

  // Metrics calculations
  const totalTemplates = templates.length
  const activeTemplates = templates.filter(t => t.status === 'active').length
  const draftTemplates = templates.filter(t => t.status === 'draft').length

  const totalInstances = instances.length
  const completedInstances = instances.filter(i => i.status === 'completed').length
  const inProgressInstances = instances.filter(i => i.status === 'in_progress').length
  const approvedInstances = instances.filter(i => i.status === 'approved').length

  const averageRating = templates.length > 0
    ? Math.round((templates.reduce((sum, t) => sum + t.usage.averageRating, 0) / templates.length) * 10) / 10
    : 0

  const totalUsage = templates.reduce((sum, t) => sum + t.usage.timesUsed, 0)

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'text-green-600 bg-green-50'
      case 'draft': return 'text-orange-600 bg-orange-50'
      case 'archived': return 'text-gray-600 bg-gray-50'
      case 'under_review': return 'text-blue-600 bg-blue-50'
      case 'completed': return 'text-green-600 bg-green-50'
      case 'in_progress': return 'text-blue-600 bg-blue-50'
      case 'approved': return 'text-purple-600 bg-purple-50'
      case 'rejected': return 'text-red-600 bg-red-50'
      default: return 'text-gray-600 bg-gray-50'
    }
  }

  const getComplexityColor = (complexity: string) => {
    switch (complexity) {
      case 'simple': return 'text-green-600 bg-green-50'
      case 'moderate': return 'text-yellow-600 bg-yellow-50'
      case 'complex': return 'text-red-600 bg-red-50'
      default: return 'text-gray-600 bg-gray-50'
    }
  }

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'plan': return <Shield className="h-4 w-4" />
      case 'policy': return <BookOpen className="h-4 w-4" />
      case 'procedure': return <Settings className="h-4 w-4" />
      case 'form': return <FileText className="h-4 w-4" />
      case 'report': return <BarChart3 className="h-4 w-4" />
      case 'checklist': return <CheckCircle className="h-4 w-4" />
      case 'communication': return <Users className="h-4 w-4" />
      case 'exercise': return <AlertTriangle className="h-4 w-4" />
      default: return <File className="h-4 w-4" />
    }
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Template Management</h1>
          <p className="text-gray-600 mt-1">Create, manage, and use standardized BCM document templates</p>
        </div>
        <div className="flex items-center space-x-3">
          <Button variant="outline">
            <Upload className="h-4 w-4 mr-2" />
            Import Templates
          </Button>
          <Button>
            <Plus className="h-4 w-4 mr-2" />
            Create Template
          </Button>
        </div>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="templates">Templates</TabsTrigger>
          <TabsTrigger value="instances">Instances</TabsTrigger>
          <TabsTrigger value="categories">Categories</TabsTrigger>
          <TabsTrigger value="library">Library</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-6">
          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Templates</CardTitle>
                <FileText className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{totalTemplates}</div>
                <div className="text-xs text-muted-foreground mt-1">
                  {activeTemplates} active, {draftTemplates} draft
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Active Instances</CardTitle>
                <FileText className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{totalInstances}</div>
                <div className="text-xs text-muted-foreground mt-1">
                  {inProgressInstances} in progress, {completedInstances} completed
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Template Usage</CardTitle>
                <BarChart3 className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{totalUsage}</div>
                <div className="text-xs text-muted-foreground mt-1">
                  Total times used
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Average Rating</CardTitle>
                <Star className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{averageRating}</div>
                <div className="text-xs text-muted-foreground mt-1">
                  User satisfaction
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Popular Templates */}
          <Card>
            <CardHeader>
              <CardTitle>Most Used Templates</CardTitle>
              <CardDescription>Templates with highest usage and ratings</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {templates
                  .sort((a, b) => b.usage.timesUsed - a.usage.timesUsed)
                  .slice(0, 5)
                  .map((template) => (
                    <div key={template.id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex items-center space-x-3">
                        {getCategoryIcon(template.category)}
                        <div>
                          <h4 className="font-medium">{template.name}</h4>
                          <p className="text-sm text-gray-600">{template.description}</p>
                          <div className="flex items-center space-x-4 mt-2">
                            <Badge variant="outline" className={getStatusColor(template.status)}>
                              {template.status}
                            </Badge>
                            <span className="text-xs text-gray-500">v{template.version}</span>
                            <div className="flex items-center space-x-1">
                              <Star className="h-3 w-3 text-yellow-500" />
                              <span className="text-xs">{template.usage.averageRating}</span>
                            </div>
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-sm font-medium">{template.usage.timesUsed} uses</div>
                        <div className="text-xs text-gray-500">
                          Last used: {template.usage.lastUsed ? format(new Date(template.usage.lastUsed), 'MMM dd') : 'Never'}
                        </div>
                      </div>
                    </div>
                  ))}
              </div>
            </CardContent>
          </Card>

          {/* Recent Activity */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Recent Template Updates</CardTitle>
                <CardDescription>Latest template modifications and approvals</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {templates
                    .sort((a, b) => new Date(b.modifiedDate).getTime() - new Date(a.modifiedDate).getTime())
                    .slice(0, 4)
                    .map((template) => (
                      <div key={template.id} className="flex items-center justify-between">
                        <div>
                          <h5 className="font-medium text-sm">{template.name}</h5>
                          <p className="text-xs text-gray-600">Modified by {template.lastModifiedBy}</p>
                        </div>
                        <div className="text-right">
                          <div className="text-xs text-gray-500">
                            {format(new Date(template.modifiedDate), 'MMM dd, yyyy')}
                          </div>
                          <Badge variant="outline" size="sm">
                            v{template.version}
                          </Badge>
                        </div>
                      </div>
                    ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Active Document Instances</CardTitle>
                <CardDescription>Documents currently being worked on</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {instances
                    .filter(i => i.status === 'in_progress')
                    .slice(0, 4)
                    .map((instance) => (
                      <div key={instance.id} className="flex items-center justify-between">
                        <div>
                          <h5 className="font-medium text-sm">{instance.instanceName}</h5>
                          <p className="text-xs text-gray-600">by {instance.createdBy}</p>
                        </div>
                        <div className="text-right">
                          <div className="text-xs font-medium">{instance.completionPercentage}%</div>
                          <div className="text-xs text-gray-500">
                            {instance.dueDate ? format(new Date(instance.dueDate), 'MMM dd') : 'No deadline'}
                          </div>
                        </div>
                      </div>
                    ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Templates Tab */}
        <TabsContent value="templates" className="space-y-6">
          {/* Template Filters */}
          <Card>
            <CardHeader>
              <CardTitle>Template Library</CardTitle>
              <CardDescription>Browse and manage all available templates</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="relative">
                  <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                  <Input
                    placeholder="Search templates..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10"
                  />
                </div>
                <Select value={filterCategory} onValueChange={setFilterCategory}>
                  <SelectTrigger>
                    <SelectValue placeholder="Filter by category" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Categories</SelectItem>
                    <SelectItem value="plan">Plans</SelectItem>
                    <SelectItem value="policy">Policies</SelectItem>
                    <SelectItem value="procedure">Procedures</SelectItem>
                    <SelectItem value="form">Forms</SelectItem>
                    <SelectItem value="checklist">Checklists</SelectItem>
                    <SelectItem value="communication">Communication</SelectItem>
                    <SelectItem value="exercise">Exercise</SelectItem>
                  </SelectContent>
                </Select>
                <Select value={filterStatus} onValueChange={setFilterStatus}>
                  <SelectTrigger>
                    <SelectValue placeholder="Filter by status" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Status</SelectItem>
                    <SelectItem value="active">Active</SelectItem>
                    <SelectItem value="draft">Draft</SelectItem>
                    <SelectItem value="under_review">Under Review</SelectItem>
                    <SelectItem value="archived">Archived</SelectItem>
                  </SelectContent>
                </Select>
                <Button variant="outline">
                  <Filter className="h-4 w-4 mr-2" />
                  Apply Filters
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Templates Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {templates.map((template) => (
              <Card key={template.id} className="hover:shadow-lg transition-shadow cursor-pointer">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      {getCategoryIcon(template.category)}
                      <Badge variant="outline" className={getStatusColor(template.status)}>
                        {template.status}
                      </Badge>
                    </div>
                    <div className="flex items-center space-x-1">
                      <Star className="h-4 w-4 text-yellow-500" />
                      <span className="text-sm">{template.usage.averageRating}</span>
                    </div>
                  </div>
                  <CardTitle className="text-lg">{template.name}</CardTitle>
                  <CardDescription>{template.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="font-medium">Category:</span>
                        <p className="text-gray-600 capitalize">{template.category}</p>
                      </div>
                      <div>
                        <span className="font-medium">Version:</span>
                        <p className="text-gray-600">v{template.version}</p>
                      </div>
                      <div>
                        <span className="font-medium">Complexity:</span>
                        <Badge variant="outline" className={getComplexityColor(template.metadata.complexity)} size="sm">
                          {template.metadata.complexity}
                        </Badge>
                      </div>
                      <div>
                        <span className="font-medium">Sections:</span>
                        <p className="text-gray-600">{template.sections.length}</p>
                      </div>
                    </div>

                    <div>
                      <span className="font-medium text-sm">Estimated Time:</span>
                      <p className="text-sm text-gray-600">
                        {Math.floor(template.metadata.estimatedCompletionTime / 60)}h {template.metadata.estimatedCompletionTime % 60}m
                      </p>
                    </div>

                    {template.tags.length > 0 && (
                      <div>
                        <span className="font-medium text-sm">Tags:</span>
                        <div className="flex flex-wrap gap-1 mt-1">
                          {template.tags.slice(0, 3).map((tag, index) => (
                            <Badge key={index} variant="outline" size="sm">
                              {tag}
                            </Badge>
                          ))}
                          {template.tags.length > 3 && (
                            <Badge variant="outline" size="sm">
                              +{template.tags.length - 3}
                            </Badge>
                          )}
                        </div>
                      </div>
                    )}

                    <div className="text-sm text-gray-500">
                      <div>Used {template.usage.timesUsed} times</div>
                      <div>Modified: {format(new Date(template.modifiedDate), 'MMM dd, yyyy')}</div>
                    </div>

                    <div className="flex items-center justify-between pt-4 border-t">
                      <div className="flex items-center space-x-2">
                        <Button variant="outline" size="sm">
                          <Eye className="h-4 w-4 mr-2" />
                          Preview
                        </Button>
                        <Button variant="outline" size="sm">
                          <Copy className="h-4 w-4 mr-2" />
                          Use
                        </Button>
                      </div>
                      <Button variant="outline" size="sm">
                        <Edit className="h-4 w-4 mr-2" />
                        Edit
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Instances Tab */}
        <TabsContent value="instances" className="space-y-6">
          {/* Instance Filters */}
          <Card>
            <CardHeader>
              <CardTitle>Document Instances</CardTitle>
              <CardDescription>Track progress of documents created from templates</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <Input placeholder="Search instances..." />
                <Select>
                  <SelectTrigger>
                    <SelectValue placeholder="Filter by status" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Status</SelectItem>
                    <SelectItem value="draft">Draft</SelectItem>
                    <SelectItem value="in_progress">In Progress</SelectItem>
                    <SelectItem value="completed">Completed</SelectItem>
                    <SelectItem value="approved">Approved</SelectItem>
                  </SelectContent>
                </Select>
                <Select>
                  <SelectTrigger>
                    <SelectValue placeholder="Filter by template" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Templates</SelectItem>
                    {templates.map((template) => (
                      <SelectItem key={template.id} value={template.id}>
                        {template.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <Button variant="outline">
                  <Filter className="h-4 w-4 mr-2" />
                  Apply Filters
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Instances List */}
          <div className="grid gap-6">
            {instances.map((instance) => (
              <Card key={instance.id}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="text-lg">{instance.instanceName}</CardTitle>
                      <CardDescription>Based on: {instance.templateName}</CardDescription>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Badge variant="outline" className={getStatusColor(instance.status)}>
                        {instance.status.replace('_', ' ')}
                      </Badge>
                      <div className="text-right">
                        <div className="text-sm font-medium">{instance.completionPercentage}%</div>
                        <div className="text-xs text-gray-500">Complete</div>
                      </div>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                      <div>
                        <span className="text-sm font-medium">Created By:</span>
                        <p className="text-sm text-gray-600">{instance.createdBy}</p>
                      </div>
                      <div>
                        <span className="text-sm font-medium">Created:</span>
                        <p className="text-sm text-gray-600">{format(new Date(instance.createdDate), 'MMM dd, yyyy')}</p>
                      </div>
                      <div>
                        <span className="text-sm font-medium">Last Modified:</span>
                        <p className="text-sm text-gray-600">{format(new Date(instance.lastModified), 'MMM dd, yyyy')}</p>
                      </div>
                      <div>
                        <span className="text-sm font-medium">Due Date:</span>
                        <p className="text-sm text-gray-600">
                          {instance.dueDate ? format(new Date(instance.dueDate), 'MMM dd, yyyy') : 'No deadline'}
                        </p>
                      </div>
                    </div>

                    {instance.assignedTo && (
                      <div>
                        <span className="text-sm font-medium">Assigned To:</span>
                        <p className="text-sm text-gray-600">{instance.assignedTo}</p>
                      </div>
                    )}

                    <div>
                      <span className="text-sm font-medium">Progress:</span>
                      <div className="flex items-center space-x-2 mt-1">
                        <div className="flex-1 bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-blue-600 h-2 rounded-full"
                            style={{ width: `${instance.completionPercentage}%` }}
                          />
                        </div>
                        <span className="text-sm text-gray-600">
                          {instance.completedSections.length} sections completed
                        </span>
                      </div>
                    </div>

                    {instance.notes && (
                      <div>
                        <span className="text-sm font-medium">Notes:</span>
                        <p className="text-sm text-gray-600">{instance.notes}</p>
                      </div>
                    )}

                    <div className="flex items-center justify-between pt-4 border-t">
                      <div className="flex items-center space-x-2">
                        <Button variant="outline" size="sm">
                          <Eye className="h-4 w-4 mr-2" />
                          View
                        </Button>
                        <Button variant="outline" size="sm">
                          <Edit className="h-4 w-4 mr-2" />
                          Edit
                        </Button>
                        <Button variant="outline" size="sm">
                          <Download className="h-4 w-4 mr-2" />
                          Export
                        </Button>
                      </div>
                      {instance.status === 'completed' && (
                        <Button variant="outline" size="sm">
                          <Share className="h-4 w-4 mr-2" />
                          Share
                        </Button>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Categories Tab */}
        <TabsContent value="categories" className="space-y-6">
          {/* Categories Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {categories.map((category) => (
              <Card key={category.id} className="hover:shadow-lg transition-shadow cursor-pointer">
                <CardHeader>
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                      {category.icon === 'shield' && <Shield className="h-5 w-5 text-blue-600" />}
                      {category.icon === 'users' && <Users className="h-5 w-5 text-blue-600" />}
                      {category.icon === 'checklist' && <CheckCircle className="h-5 w-5 text-blue-600" />}
                      {category.icon === 'target' && <AlertTriangle className="h-5 w-5 text-blue-600" />}
                    </div>
                    <div>
                      <CardTitle className="text-lg">{category.name}</CardTitle>
                      <CardDescription>{category.templateCount} templates</CardDescription>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <p className="text-sm text-gray-600">{category.description}</p>

                    {category.subcategories && (
                      <div>
                        <span className="text-sm font-medium">Subcategories:</span>
                        <div className="flex flex-wrap gap-1 mt-1">
                          {category.subcategories.map((sub, index) => (
                            <Badge key={index} variant="outline" size="sm">
                              {sub}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}

                    <div className="flex items-center justify-between pt-4 border-t">
                      <Button variant="outline" size="sm">
                        <Eye className="h-4 w-4 mr-2" />
                        Browse Templates
                      </Button>
                      <span className="text-sm text-gray-500">{category.templateCount} templates</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Library Tab */}
        <TabsContent value="library" className="space-y-6">
          {/* Library Management */}
          <Card>
            <CardHeader>
              <CardTitle>Template Libraries</CardTitle>
              <CardDescription>Manage and browse template libraries from different sources</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                <div className="flex items-center justify-between">
                  <h4 className="font-medium">Available Libraries</h4>
                  <Button variant="outline">
                    <Plus className="h-4 w-4 mr-2" />
                    Add Library
                  </Button>
                </div>

                {/* Library List */}
                <div className="space-y-4">
                  <div className="p-4 border rounded-lg">
                    <div className="flex items-center justify-between">
                      <div>
                        <h5 className="font-medium">ISO 22301 Standard Templates</h5>
                        <p className="text-sm text-gray-600">Official templates for ISO 22301 compliance</p>
                        <div className="flex items-center space-x-4 mt-2">
                          <Badge variant="outline">Public</Badge>
                          <span className="text-sm text-gray-500">15 templates</span>
                          <span className="text-sm text-gray-500">Updated: Oct 2024</span>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Button variant="outline" size="sm">
                          <Eye className="h-4 w-4 mr-2" />
                          Browse
                        </Button>
                        <Button size="sm">
                          <Download className="h-4 w-4 mr-2" />
                          Subscribe
                        </Button>
                      </div>
                    </div>
                  </div>

                  <div className="p-4 border rounded-lg">
                    <div className="flex items-center justify-between">
                      <div>
                        <h5 className="font-medium">Industry Best Practices</h5>
                        <p className="text-sm text-gray-600">Curated templates from industry experts</p>
                        <div className="flex items-center space-x-4 mt-2">
                          <Badge variant="outline">Community</Badge>
                          <span className="text-sm text-gray-500">28 templates</span>
                          <span className="text-sm text-gray-500">Updated: Nov 2024</span>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Button variant="outline" size="sm">
                          <Eye className="h-4 w-4 mr-2" />
                          Browse
                        </Button>
                        <Button size="sm">
                          <Download className="h-4 w-4 mr-2" />
                          Subscribe
                        </Button>
                      </div>
                    </div>
                  </div>

                  <div className="p-4 border rounded-lg">
                    <div className="flex items-center justify-between">
                      <div>
                        <h5 className="font-medium">Organization Templates</h5>
                        <p className="text-sm text-gray-600">Internal templates created by your organization</p>
                        <div className="flex items-center space-x-4 mt-2">
                          <Badge variant="outline">Private</Badge>
                          <span className="text-sm text-gray-500">{totalTemplates} templates</span>
                          <span className="text-sm text-gray-500">Last updated: Nov 2024</span>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Button variant="outline" size="sm">
                          <Settings className="h-4 w-4 mr-2" />
                          Manage
                        </Button>
                        <Button size="sm">
                          <Share className="h-4 w-4 mr-2" />
                          Share
                        </Button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}