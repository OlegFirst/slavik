'use client'

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { apiClient } from '@/lib/api-client'
import useBCMStore from '@/lib/bcm-store'
import { toast } from 'sonner'
import {
  Building,
  Users,
  Shield,
  Network,
  AlertCircle,
  Plus,
  Edit,
  Trash2,
  ChevronRight,
  ChevronDown,
  Target,
  FileText,
  UserCheck,
  Layers,
  GitBranch,
  Settings,
  Activity,
  Globe,
  MapPin,
  Phone,
  Mail,
  Calendar,
  Clock,
  CheckCircle,
  XCircle,
  Info
} from 'lucide-react'

// TypeScript interfaces
interface Organization {
  id: string
  name: string
  industry: string
  size: 'small' | 'medium' | 'large' | 'enterprise'
  headquarters: string
  employees: number
  bcmMaturityLevel: number
  establishedDate: string
  description: string
  website?: string
  phone?: string
  email?: string
}

interface BusinessUnit {
  id: string
  name: string
  parentId: string | null
  organizationId: string
  level: number
  headCount: number
  manager: string
  department: string
  location: string
  status: 'active' | 'inactive' | 'restructuring'
  criticalityLevel: 'low' | 'medium' | 'high' | 'critical'
  children?: BusinessUnit[]
}

interface CriticalFunction {
  id: string
  name: string
  businessUnitId: string
  description: string
  category: string
  criticality: 'low' | 'medium' | 'high' | 'critical'
  rto: number // Recovery Time Objective in hours
  rpo: number // Recovery Point Objective in hours
  dependencies: string[]
  resources: string[]
  owner: string
  lastReview: string
  status: 'active' | 'under_review' | 'deprecated'
}

interface Stakeholder {
  id: string
  name: string
  role: string
  type: 'internal' | 'external' | 'regulatory' | 'supplier' | 'customer'
  email: string
  phone: string
  organization: string
  influence: 'low' | 'medium' | 'high'
  interest: 'low' | 'medium' | 'high'
  communicationFrequency: 'daily' | 'weekly' | 'monthly' | 'quarterly'
  notes: string
  status: 'active' | 'inactive'
}

interface Dependency {
  id: string
  sourceId: string
  sourceName: string
  sourceType: 'function' | 'unit' | 'system' | 'supplier'
  targetId: string
  targetName: string
  targetType: 'function' | 'unit' | 'system' | 'supplier'
  dependencyType: 'critical' | 'important' | 'supporting'
  description: string
  impactLevel: 'low' | 'medium' | 'high' | 'critical'
}

interface BCMContext {
  scope: string
  objectives: string[]
  policy: string
  approvedBy: string
  approvalDate: string
  nextReview: string
  complianceStandards: string[]
}

export function BCMCoreModule() {
  const router = useRouter()
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState<'organization' | 'units' | 'functions' | 'stakeholders' | 'dependencies' | 'context'>('organization')
  const [selectedUnit, setSelectedUnit] = useState<string | null>(null)
  const [expandedUnits, setExpandedUnits] = useState<Set<string>>(new Set())
  const [showAddModal, setShowAddModal] = useState(false)
  const [editingItem, setEditingItem] = useState<any>(null)

  // Zustand store
  const { publishEvent, addNotification } = useBCMStore()

  // Fetch organization data
  const { data: organization, isLoading: orgLoading } = useQuery<Organization>({
    queryKey: ['organization'],
    queryFn: async () => {
      const response = await apiClient.getOrganizations()
      return response.data[0] // Single organization for now
    }
  })

  // Fetch business units
  const { data: businessUnits, isLoading: unitsLoading } = useQuery<BusinessUnit[]>({
    queryKey: ['business-units'],
    queryFn: async () => {
      const response = await apiClient.getBusinessUnits()
      return buildUnitHierarchy(response.data)
    }
  })

  // Fetch critical functions
  const { data: criticalFunctions } = useQuery<CriticalFunction[]>({
    queryKey: ['critical-functions'],
    queryFn: async () => getMockCriticalFunctions()
  })

  // Fetch stakeholders
  const { data: stakeholders } = useQuery<Stakeholder[]>({
    queryKey: ['stakeholders'],
    queryFn: async () => getMockStakeholders()
  })

  // Fetch dependencies
  const { data: dependencies } = useQuery<Dependency[]>({
    queryKey: ['dependencies'],
    queryFn: async () => getMockDependencies()
  })

  // Fetch BCM context
  const { data: bcmContext } = useQuery<BCMContext>({
    queryKey: ['bcm-context'],
    queryFn: async () => getMockBCMContext()
  })

  // Build business unit hierarchy
  const buildUnitHierarchy = (units: any[]): BusinessUnit[] => {
    const unitMap = new Map(units.map(u => [u.id, { ...u, children: [] }]))
    const roots: BusinessUnit[] = []

    units.forEach(unit => {
      if (unit.parentId) {
        const parent = unitMap.get(unit.parentId)
        if (parent) {
          parent.children.push(unitMap.get(unit.id))
        }
      } else {
        roots.push(unitMap.get(unit.id))
      }
    })

    return roots
  }

  // Toggle unit expansion
  const toggleUnitExpansion = (unitId: string) => {
    const newExpanded = new Set(expandedUnits)
    if (newExpanded.has(unitId)) {
      newExpanded.delete(unitId)
    } else {
      newExpanded.add(unitId)
    }
    setExpandedUnits(newExpanded)
  }

  // Calculate metrics
  const metrics = {
    totalUnits: businessUnits?.length || 0,
    criticalFunctions: criticalFunctions?.filter(f => f.criticality === 'critical').length || 0,
    activeStakeholders: stakeholders?.filter(s => s.status === 'active').length || 0,
    maturityLevel: organization?.bcmMaturityLevel || 0,
    complianceScore: 85 // Mock value
  }

  if (orgLoading || unitsLoading) {
    return <LoadingState />
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <Building className="h-8 w-8 text-blue-600" />
            BCM Core Management
          </h1>
          <p className="text-gray-600 mt-1">Organization context and business continuity foundation</p>
        </div>
        <div className="flex gap-3">
          <Button variant="outline" onClick={() => router.push('/modules/config')}>
            <Settings className="h-4 w-4 mr-2" />
            BCM Settings
          </Button>
          <Button onClick={() => setShowAddModal(true)}>
            <Plus className="h-4 w-4 mr-2" />
            Add New
          </Button>
        </div>
      </div>

      {/* Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
        <MetricCard
          title="Business Units"
          value={metrics.totalUnits}
          icon={Layers}
          color="blue"
        />
        <MetricCard
          title="Critical Functions"
          value={metrics.criticalFunctions}
          icon={Target}
          color="red"
        />
        <MetricCard
          title="Stakeholders"
          value={metrics.activeStakeholders}
          icon={Users}
          color="green"
        />
        <MetricCard
          title="BCM Maturity"
          value={`Level ${metrics.maturityLevel}`}
          icon={Activity}
          color="purple"
        />
        <MetricCard
          title="Compliance"
          value={`${metrics.complianceScore}%`}
          icon={Shield}
          color="yellow"
        />
      </div>

      {/* Tabs */}
      <div className="border-b">
        <nav className="flex space-x-8">
          {[
            { id: 'organization', label: 'Organization', icon: Building },
            { id: 'units', label: 'Business Units', icon: Layers },
            { id: 'functions', label: 'Critical Functions', icon: Target },
            { id: 'stakeholders', label: 'Stakeholders', icon: Users },
            { id: 'dependencies', label: 'Dependencies', icon: Network },
            { id: 'context', label: 'BCM Context', icon: FileText }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={cn(
                "flex items-center gap-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors",
                activeTab === tab.id
                  ? "border-blue-500 text-blue-600"
                  : "border-transparent text-gray-500 hover:text-gray-700"
              )}
            >
              <tab.icon className="h-4 w-4" />
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="mt-6">
        {activeTab === 'organization' && (
          <OrganizationTab organization={organization} />
        )}
        {activeTab === 'units' && (
          <BusinessUnitsTab
            units={businessUnits || []}
            expandedUnits={expandedUnits}
            selectedUnit={selectedUnit}
            onToggleExpand={toggleUnitExpansion}
            onSelectUnit={setSelectedUnit}
          />
        )}
        {activeTab === 'functions' && (
          <CriticalFunctionsTab
            functions={criticalFunctions || []}
            businessUnits={businessUnits || []}
          />
        )}
        {activeTab === 'stakeholders' && (
          <StakeholdersTab stakeholders={stakeholders || []} />
        )}
        {activeTab === 'dependencies' && (
          <DependenciesTab dependencies={dependencies || []} />
        )}
        {activeTab === 'context' && (
          <BCMContextTab context={bcmContext} />
        )}
      </div>
    </div>
  )
}

// Organization Tab Component
function OrganizationTab({ organization }: { organization?: Organization }) {
  if (!organization) return <div>No organization data</div>

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div className="lg:col-span-2 space-y-6">
        {/* Organization Details */}
        <div className="bg-white rounded-lg border shadow-sm p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Organization Profile</h3>
          <dl className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <dt className="text-sm font-medium text-gray-500">Name</dt>
              <dd className="mt-1 text-sm text-gray-900">{organization.name}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Industry</dt>
              <dd className="mt-1 text-sm text-gray-900">{organization.industry}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Size</dt>
              <dd className="mt-1 text-sm text-gray-900 capitalize">{organization.size}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Employees</dt>
              <dd className="mt-1 text-sm text-gray-900">{organization.employees.toLocaleString()}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Headquarters</dt>
              <dd className="mt-1 text-sm text-gray-900 flex items-center gap-1">
                <MapPin className="h-3 w-3" />
                {organization.headquarters}
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Established</dt>
              <dd className="mt-1 text-sm text-gray-900 flex items-center gap-1">
                <Calendar className="h-3 w-3" />
                {new Date(organization.establishedDate).toLocaleDateString()}
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Website</dt>
              <dd className="mt-1 text-sm text-gray-900 flex items-center gap-1">
                <Globe className="h-3 w-3" />
                {organization.website || 'N/A'}
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Contact</dt>
              <dd className="mt-1 text-sm text-gray-900 flex items-center gap-1">
                <Phone className="h-3 w-3" />
                {organization.phone || 'N/A'}
              </dd>
            </div>
          </dl>
          <div className="mt-4 pt-4 border-t">
            <dt className="text-sm font-medium text-gray-500">Description</dt>
            <dd className="mt-1 text-sm text-gray-900">{organization.description}</dd>
          </div>
        </div>

        {/* BCM Maturity Assessment */}
        <div className="bg-white rounded-lg border shadow-sm p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">BCM Maturity Assessment</h3>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium text-gray-700">Current Level</span>
                <span className="text-2xl font-bold text-blue-600">Level {organization.bcmMaturityLevel}</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div
                  className="bg-blue-600 h-3 rounded-full transition-all duration-500"
                  style={{ width: `${(organization.bcmMaturityLevel / 5) * 100}%` }}
                />
              </div>
            </div>
            <div className="grid grid-cols-5 gap-2 text-center text-xs">
              {['Initial', 'Developing', 'Established', 'Predictable', 'Optimizing'].map((level, idx) => (
                <div
                  key={level}
                  className={cn(
                    "p-2 rounded",
                    idx < organization.bcmMaturityLevel
                      ? "bg-blue-100 text-blue-700 font-medium"
                      : "bg-gray-100 text-gray-500"
                  )}
                >
                  {level}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="space-y-6">
        <div className="bg-white rounded-lg border shadow-sm p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
          <div className="space-y-3">
            <Button variant="outline" className="w-full justify-start">
              <Edit className="h-4 w-4 mr-2" />
              Edit Organization Profile
            </Button>
            <Button variant="outline" className="w-full justify-start">
              <FileText className="h-4 w-4 mr-2" />
              Update BCM Policy
            </Button>
            <Button variant="outline" className="w-full justify-start">
              <UserCheck className="h-4 w-4 mr-2" />
              Manage Roles & Responsibilities
            </Button>
            <Button variant="outline" className="w-full justify-start">
              <Shield className="h-4 w-4 mr-2" />
              Compliance Review
            </Button>
          </div>
        </div>

        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h4 className="font-medium text-blue-900 mb-2 flex items-center gap-2">
            <Info className="h-4 w-4" />
            Next Steps
          </h4>
          <ul className="space-y-1 text-sm text-blue-800">
            <li>• Complete business unit mapping</li>
            <li>• Identify all critical functions</li>
            <li>• Update stakeholder registry</li>
            <li>• Review dependency matrix</li>
          </ul>
        </div>
      </div>
    </div>
  )
}

// Business Units Tab Component
function BusinessUnitsTab({
  units,
  expandedUnits,
  selectedUnit,
  onToggleExpand,
  onSelectUnit
}: {
  units: BusinessUnit[]
  expandedUnits: Set<string>
  selectedUnit: string | null
  onToggleExpand: (id: string) => void
  onSelectUnit: (id: string | null) => void
}) {
  const renderUnit = (unit: BusinessUnit, level: number = 0) => {
    const hasChildren = unit.children && unit.children.length > 0
    const isExpanded = expandedUnits.has(unit.id)
    const isSelected = selectedUnit === unit.id

    const criticalityColors = {
      low: 'bg-gray-100 text-gray-700',
      medium: 'bg-yellow-100 text-yellow-700',
      high: 'bg-orange-100 text-orange-700',
      critical: 'bg-red-100 text-red-700'
    }

    return (
      <div key={unit.id}>
        <div
          className={cn(
            "flex items-center gap-2 p-3 rounded-lg cursor-pointer transition-colors",
            isSelected ? "bg-blue-50 border-blue-200" : "hover:bg-gray-50"
          )}
          style={{ marginLeft: `${level * 24}px` }}
          onClick={() => onSelectUnit(isSelected ? null : unit.id)}
        >
          {hasChildren && (
            <button
              onClick={(e) => {
                e.stopPropagation()
                onToggleExpand(unit.id)
              }}
              className="p-1 hover:bg-gray-200 rounded"
            >
              {isExpanded ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
            </button>
          )}
          {!hasChildren && <div className="w-6" />}

          <Layers className="h-4 w-4 text-gray-400" />
          <div className="flex-1">
            <div className="flex items-center gap-2">
              <span className="font-medium text-gray-900">{unit.name}</span>
              <span className={cn("px-2 py-0.5 rounded-full text-xs", criticalityColors[unit.criticalityLevel])}>
                {unit.criticalityLevel}
              </span>
              {unit.status !== 'active' && (
                <span className="px-2 py-0.5 rounded-full text-xs bg-gray-100 text-gray-600">
                  {unit.status}
                </span>
              )}
            </div>
            <div className="text-xs text-gray-500 mt-1">
              {unit.department} • {unit.headCount} employees • {unit.location}
            </div>
          </div>
        </div>

        {hasChildren && isExpanded && (
          <div>
            {unit.children!.map(child => renderUnit(child, level + 1))}
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div className="lg:col-span-2">
        <div className="bg-white rounded-lg border shadow-sm">
          <div className="p-4 border-b">
            <h3 className="text-lg font-semibold text-gray-900">Business Unit Hierarchy</h3>
          </div>
          <div className="p-4">
            {units.map(unit => renderUnit(unit))}
          </div>
        </div>
      </div>

      {selectedUnit && (
        <div className="bg-white rounded-lg border shadow-sm p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Unit Details</h3>
          {/* Unit details would go here */}
          <div className="space-y-3 text-sm">
            <div>
              <span className="text-gray-500">Manager:</span>
              <span className="ml-2 text-gray-900">John Smith</span>
            </div>
            <div>
              <span className="text-gray-500">Critical Functions:</span>
              <span className="ml-2 text-gray-900">5</span>
            </div>
            <div>
              <span className="text-gray-500">Dependencies:</span>
              <span className="ml-2 text-gray-900">12</span>
            </div>
          </div>
          <div className="mt-4 pt-4 border-t">
            <Button variant="outline" size="sm" className="w-full">
              <Edit className="h-3 w-3 mr-1" />
              Edit Unit
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}

// Critical Functions Tab
function CriticalFunctionsTab({
  functions,
  businessUnits
}: {
  functions: CriticalFunction[]
  businessUnits: BusinessUnit[]
}) {
  const criticalityColors = {
    low: 'bg-gray-100 text-gray-700',
    medium: 'bg-yellow-100 text-yellow-700',
    high: 'bg-orange-100 text-orange-700',
    critical: 'bg-red-100 text-red-700'
  }

  return (
    <div className="bg-white rounded-lg border shadow-sm">
      <div className="p-4 border-b">
        <h3 className="text-lg font-semibold text-gray-900">Critical Business Functions</h3>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b bg-gray-50">
              <th className="text-left py-3 px-4 font-medium text-gray-500 text-sm">Function</th>
              <th className="text-left py-3 px-4 font-medium text-gray-500 text-sm">Business Unit</th>
              <th className="text-left py-3 px-4 font-medium text-gray-500 text-sm">Criticality</th>
              <th className="text-left py-3 px-4 font-medium text-gray-500 text-sm">RTO</th>
              <th className="text-left py-3 px-4 font-medium text-gray-500 text-sm">RPO</th>
              <th className="text-left py-3 px-4 font-medium text-gray-500 text-sm">Owner</th>
              <th className="text-left py-3 px-4 font-medium text-gray-500 text-sm">Status</th>
              <th className="text-left py-3 px-4 font-medium text-gray-500 text-sm">Actions</th>
            </tr>
          </thead>
          <tbody>
            {functions.map(func => (
              <tr key={func.id} className="border-b hover:bg-gray-50">
                <td className="py-3 px-4">
                  <div>
                    <div className="font-medium text-gray-900">{func.name}</div>
                    <div className="text-xs text-gray-500">{func.category}</div>
                  </div>
                </td>
                <td className="py-3 px-4 text-sm text-gray-600">
                  {businessUnits.find(u => u.id === func.businessUnitId)?.name || 'N/A'}
                </td>
                <td className="py-3 px-4">
                  <span className={cn("px-2 py-1 rounded-full text-xs", criticalityColors[func.criticality])}>
                    {func.criticality}
                  </span>
                </td>
                <td className="py-3 px-4 text-sm text-gray-900">{func.rto}h</td>
                <td className="py-3 px-4 text-sm text-gray-900">{func.rpo}h</td>
                <td className="py-3 px-4 text-sm text-gray-900">{func.owner}</td>
                <td className="py-3 px-4">
                  <span className={cn(
                    "px-2 py-1 rounded-full text-xs",
                    func.status === 'active' ? 'bg-green-100 text-green-700' :
                    func.status === 'under_review' ? 'bg-yellow-100 text-yellow-700' :
                    'bg-gray-100 text-gray-700'
                  )}>
                    {func.status}
                  </span>
                </td>
                <td className="py-3 px-4">
                  <div className="flex gap-2">
                    <Button variant="ghost" size="sm">
                      <Edit className="h-3 w-3" />
                    </Button>
                    <Button variant="ghost" size="sm">
                      <Trash2 className="h-3 w-3" />
                    </Button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

// Stakeholders Tab
function StakeholdersTab({ stakeholders }: { stakeholders: Stakeholder[] }) {
  const getStakeholderMatrix = (influence: string, interest: string) => {
    if (influence === 'high' && interest === 'high') return 'Manage Closely'
    if (influence === 'high' && interest === 'low') return 'Keep Satisfied'
    if (influence === 'low' && interest === 'high') return 'Keep Informed'
    return 'Monitor'
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div className="lg:col-span-2">
        <div className="bg-white rounded-lg border shadow-sm">
          <div className="p-4 border-b">
            <h3 className="text-lg font-semibold text-gray-900">Stakeholder Registry</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b bg-gray-50">
                  <th className="text-left py-3 px-4 font-medium text-gray-500 text-sm">Name</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-500 text-sm">Type</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-500 text-sm">Organization</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-500 text-sm">Strategy</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-500 text-sm">Contact</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-500 text-sm">Status</th>
                </tr>
              </thead>
              <tbody>
                {stakeholders.map(stakeholder => (
                  <tr key={stakeholder.id} className="border-b hover:bg-gray-50">
                    <td className="py-3 px-4">
                      <div>
                        <div className="font-medium text-gray-900">{stakeholder.name}</div>
                        <div className="text-xs text-gray-500">{stakeholder.role}</div>
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      <span className="px-2 py-1 rounded-full text-xs bg-blue-100 text-blue-700">
                        {stakeholder.type}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-sm text-gray-600">{stakeholder.organization}</td>
                    <td className="py-3 px-4">
                      <span className="text-xs font-medium text-gray-700">
                        {getStakeholderMatrix(stakeholder.influence, stakeholder.interest)}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex gap-2">
                        <Mail className="h-3 w-3 text-gray-400" />
                        <Phone className="h-3 w-3 text-gray-400" />
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      {stakeholder.status === 'active' ? (
                        <CheckCircle className="h-4 w-4 text-green-500" />
                      ) : (
                        <XCircle className="h-4 w-4 text-red-500" />
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Stakeholder Matrix */}
      <div className="bg-white rounded-lg border shadow-sm p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Stakeholder Matrix</h3>
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-red-50 border border-red-200 rounded-lg p-3">
            <div className="text-xs font-medium text-red-700 mb-1">Manage Closely</div>
            <div className="text-2xl font-bold text-red-600">
              {stakeholders.filter(s => s.influence === 'high' && s.interest === 'high').length}
            </div>
          </div>
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
            <div className="text-xs font-medium text-yellow-700 mb-1">Keep Satisfied</div>
            <div className="text-2xl font-bold text-yellow-600">
              {stakeholders.filter(s => s.influence === 'high' && s.interest === 'low').length}
            </div>
          </div>
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
            <div className="text-xs font-medium text-blue-700 mb-1">Keep Informed</div>
            <div className="text-2xl font-bold text-blue-600">
              {stakeholders.filter(s => s.influence === 'low' && s.interest === 'high').length}
            </div>
          </div>
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
            <div className="text-xs font-medium text-gray-700 mb-1">Monitor</div>
            <div className="text-2xl font-bold text-gray-600">
              {stakeholders.filter(s => s.influence === 'low' && s.interest === 'low').length}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

// Dependencies Tab
function DependenciesTab({ dependencies }: { dependencies: Dependency[] }) {
  return (
    <div className="bg-white rounded-lg border shadow-sm">
      <div className="p-4 border-b">
        <h3 className="text-lg font-semibold text-gray-900">Dependency Matrix</h3>
      </div>
      <div className="p-4">
        <div className="space-y-3">
          {dependencies.map(dep => (
            <div key={dep.id} className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50">
              <div className="flex items-center gap-4">
                <div className="text-sm">
                  <span className="font-medium text-gray-900">{dep.sourceName}</span>
                  <span className="text-gray-500 mx-2">→</span>
                  <span className="font-medium text-gray-900">{dep.targetName}</span>
                </div>
                <span className={cn(
                  "px-2 py-1 rounded-full text-xs",
                  dep.dependencyType === 'critical' ? 'bg-red-100 text-red-700' :
                  dep.dependencyType === 'important' ? 'bg-yellow-100 text-yellow-700' :
                  'bg-gray-100 text-gray-700'
                )}>
                  {dep.dependencyType}
                </span>
              </div>
              <div className="text-xs text-gray-500">{dep.description}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

// BCM Context Tab
function BCMContextTab({ context }: { context?: BCMContext }) {
  if (!context) return <div>No context data</div>

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div className="bg-white rounded-lg border shadow-sm p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">BCM Scope & Objectives</h3>
        <div className="space-y-4">
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-2">Scope</h4>
            <p className="text-sm text-gray-600">{context.scope}</p>
          </div>
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-2">Objectives</h4>
            <ul className="space-y-1">
              {context.objectives.map((obj, idx) => (
                <li key={idx} className="text-sm text-gray-600 flex items-start">
                  <CheckCircle className="h-3 w-3 text-green-500 mr-2 mt-0.5" />
                  {obj}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg border shadow-sm p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Policy & Compliance</h3>
        <div className="space-y-4">
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-2">BCM Policy</h4>
            <p className="text-sm text-gray-600">{context.policy}</p>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <span className="text-xs text-gray-500">Approved By</span>
              <p className="text-sm font-medium text-gray-900">{context.approvedBy}</p>
            </div>
            <div>
              <span className="text-xs text-gray-500">Approval Date</span>
              <p className="text-sm font-medium text-gray-900">
                {new Date(context.approvalDate).toLocaleDateString()}
              </p>
            </div>
          </div>
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-2">Compliance Standards</h4>
            <div className="flex flex-wrap gap-2">
              {context.complianceStandards.map(standard => (
                <span key={standard} className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs">
                  {standard}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

// Helper Components
function MetricCard({ title, value, icon: Icon, color }: any) {
  const colorMap: Record<string, string> = {
    blue: 'bg-blue-100 text-blue-600',
    red: 'bg-red-100 text-red-600',
    green: 'bg-green-100 text-green-600',
    purple: 'bg-purple-100 text-purple-600',
    yellow: 'bg-yellow-100 text-yellow-600'
  }
  const colorClasses = colorMap[color] || 'bg-gray-100 text-gray-600'

  return (
    <div className="bg-white rounded-lg border shadow-sm p-6">
      <div className="flex items-center justify-between">
        <div className={cn("w-12 h-12 rounded-lg flex items-center justify-center", colorClasses)}>
          <Icon className="h-6 w-6" />
        </div>
      </div>
      <div className="mt-4">
        <div className="text-2xl font-bold text-gray-900">{value}</div>
        <div className="text-sm text-gray-500">{title}</div>
      </div>
    </div>
  )
}

function LoadingState() {
  return (
    <div className="flex items-center justify-center h-96">
      <div className="text-center">
        <Building className="h-12 w-12 text-blue-600 animate-pulse mx-auto mb-4" />
        <p className="text-gray-600">Loading BCM Core...</p>
      </div>
    </div>
  )
}

// Mock Data Functions
function getMockCriticalFunctions(): CriticalFunction[] {
  return [
    {
      id: '1',
      name: 'Customer Service Operations',
      businessUnitId: '2',
      description: 'Core customer support and service delivery',
      category: 'Operations',
      criticality: 'critical',
      rto: 4,
      rpo: 2,
      dependencies: ['IT Systems', 'Call Center', 'CRM'],
      resources: ['Support Staff', 'Communication Systems'],
      owner: 'Sarah Johnson',
      lastReview: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
      status: 'active'
    },
    {
      id: '2',
      name: 'Manufacturing Operations',
      businessUnitId: '3',
      description: 'Primary production and manufacturing processes',
      category: 'Production',
      criticality: 'critical',
      rto: 8,
      rpo: 4,
      dependencies: ['Supply Chain', 'Equipment', 'Workforce'],
      resources: ['Production Line', 'Raw Materials'],
      owner: 'Michael Chen',
      lastReview: new Date(Date.now() - 15 * 24 * 60 * 60 * 1000).toISOString(),
      status: 'active'
    },
    {
      id: '3',
      name: 'Financial Transactions',
      businessUnitId: '4',
      description: 'Payment processing and financial operations',
      category: 'Finance',
      criticality: 'critical',
      rto: 2,
      rpo: 0,
      dependencies: ['Banking Systems', 'Payment Gateways'],
      resources: ['Finance Team', 'Banking Infrastructure'],
      owner: 'David Thompson',
      lastReview: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
      status: 'active'
    },
    {
      id: '4',
      name: 'Supply Chain Management',
      businessUnitId: '5',
      description: 'Supplier relationships and inventory management',
      category: 'Supply Chain',
      criticality: 'high',
      rto: 12,
      rpo: 6,
      dependencies: ['Supplier Network', 'Logistics'],
      resources: ['Warehouse', 'Transportation'],
      owner: 'Lisa Martinez',
      lastReview: new Date(Date.now() - 45 * 24 * 60 * 60 * 1000).toISOString(),
      status: 'under_review'
    }
  ]
}

function getMockStakeholders(): Stakeholder[] {
  return [
    {
      id: '1',
      name: 'John Smith',
      role: 'CEO',
      type: 'internal',
      email: 'john.smith@company.com',
      phone: '+1 555-0100',
      organization: 'Acme Corporation',
      influence: 'high',
      interest: 'high',
      communicationFrequency: 'weekly',
      notes: 'Key decision maker for BCM strategy',
      status: 'active'
    },
    {
      id: '2',
      name: 'Regional Regulator',
      role: 'Compliance Officer',
      type: 'regulatory',
      email: 'compliance@regulator.gov',
      phone: '+1 555-0200',
      organization: 'Government Agency',
      influence: 'high',
      interest: 'medium',
      communicationFrequency: 'quarterly',
      notes: 'Primary regulatory contact',
      status: 'active'
    },
    {
      id: '3',
      name: 'Major Supplier Corp',
      role: 'Account Manager',
      type: 'supplier',
      email: 'contact@supplier.com',
      phone: '+1 555-0300',
      organization: 'Major Supplier Corp',
      influence: 'medium',
      interest: 'high',
      communicationFrequency: 'monthly',
      notes: 'Critical supplier for raw materials',
      status: 'active'
    },
    {
      id: '4',
      name: 'Enterprise Client Inc',
      role: 'Procurement Director',
      type: 'customer',
      email: 'procurement@client.com',
      phone: '+1 555-0400',
      organization: 'Enterprise Client Inc',
      influence: 'medium',
      interest: 'medium',
      communicationFrequency: 'monthly',
      notes: 'Largest enterprise customer',
      status: 'active'
    },
    {
      id: '5',
      name: 'Sarah Johnson',
      role: 'BCM Coordinator',
      type: 'internal',
      email: 'sarah.johnson@company.com',
      phone: '+1 555-0500',
      organization: 'Acme Corporation',
      influence: 'medium',
      interest: 'high',
      communicationFrequency: 'daily',
      notes: 'BCM program coordinator',
      status: 'active'
    }
  ]
}

function getMockDependencies(): Dependency[] {
  return [
    {
      id: '1',
      sourceId: 'func-1',
      sourceName: 'Customer Service',
      sourceType: 'function',
      targetId: 'sys-1',
      targetName: 'CRM System',
      targetType: 'system',
      dependencyType: 'critical',
      description: 'Customer service depends on CRM for customer data',
      impactLevel: 'critical'
    },
    {
      id: '2',
      sourceId: 'func-2',
      sourceName: 'Manufacturing',
      sourceType: 'function',
      targetId: 'sup-1',
      targetName: 'Raw Material Supplier',
      targetType: 'supplier',
      dependencyType: 'critical',
      description: 'Manufacturing requires continuous supply of raw materials',
      impactLevel: 'high'
    },
    {
      id: '3',
      sourceId: 'unit-1',
      sourceName: 'IT Department',
      sourceType: 'unit',
      targetId: 'sys-2',
      targetName: 'Data Center',
      targetType: 'system',
      dependencyType: 'critical',
      description: 'IT operations depend on data center availability',
      impactLevel: 'critical'
    },
    {
      id: '4',
      sourceId: 'func-3',
      sourceName: 'Financial Transactions',
      sourceType: 'function',
      targetId: 'sys-3',
      targetName: 'Banking API',
      targetType: 'system',
      dependencyType: 'critical',
      description: 'Payment processing requires banking system connectivity',
      impactLevel: 'critical'
    }
  ]
}

function getMockBCMContext(): BCMContext {
  return {
    scope: 'All business operations and critical functions across the organization, including subsidiaries and key supplier relationships',
    objectives: [
      'Ensure continuity of critical business functions during disruptions',
      'Minimize financial and operational impact of incidents',
      'Protect stakeholder interests and maintain customer trust',
      'Comply with regulatory requirements and industry standards',
      'Continuously improve BCM maturity and resilience'
    ],
    policy: 'The organization is committed to maintaining a comprehensive BCM program that ensures the continuity of critical operations, protects stakeholder interests, and complies with all applicable regulations.',
    approvedBy: 'Board of Directors',
    approvalDate: new Date(Date.now() - 90 * 24 * 60 * 60 * 1000).toISOString(),
    nextReview: new Date(Date.now() + 275 * 24 * 60 * 60 * 1000).toISOString(),
    complianceStandards: ['ISO 22301', 'ISO 27001', 'SOC 2', 'GDPR', 'Industry Specific']
  }
}