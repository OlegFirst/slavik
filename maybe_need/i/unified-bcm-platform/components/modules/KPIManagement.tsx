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
  BarChart3,
  LineChart,
  TrendingUp,
  TrendingDown,
  Target,
  Activity,
  AlertTriangle,
  CheckCircle,
  Clock,
  Calendar,
  Users,
  Shield,
  Zap,
  Award,
  Eye,
  Edit,
  Copy,
  Download,
  Upload,
  RefreshCw,
  Plus,
  Search,
  Filter,
  Settings,
  Info,
  AlertCircle,
  XCircle,
  Gauge,
  PieChart,
  BarChart,
  Timer,
  Building
} from 'lucide-react'
import { apiClient } from '@/lib/api-client'
import { useBCMStore } from '@/lib/bcm-store'

// Types
interface KPI {
  id: string
  name: string
  description: string
  category: 'operational' | 'strategic' | 'compliance' | 'financial' | 'risk' | 'performance'
  type: 'percentage' | 'count' | 'duration' | 'currency' | 'ratio' | 'score'
  unit: string
  currentValue: number
  targetValue: number
  thresholds: KPIThreshold[]
  status: 'on_target' | 'warning' | 'critical' | 'unknown'
  trend: 'up' | 'down' | 'stable'
  frequency: 'real_time' | 'daily' | 'weekly' | 'monthly' | 'quarterly' | 'annually'
  dataSource: string
  formula?: string
  owner: string
  stakeholders: string[]
  history: KPIDataPoint[]
  lastUpdated: string
  isActive: boolean
  tags: string[]
  benchmarks?: KPIBenchmark[]
}

interface KPIThreshold {
  id: string
  name: string
  operator: 'gt' | 'gte' | 'lt' | 'lte' | 'eq' | 'between'
  value: number | [number, number]
  severity: 'good' | 'warning' | 'critical'
  color: string
  action?: string
}

interface KPIDataPoint {
  timestamp: string
  value: number
  notes?: string
  source?: string
}

interface KPIBenchmark {
  name: string
  value: number
  source: string
  date: string
}

interface KPIDashboard {
  id: string
  name: string
  description: string
  kpis: string[]
  layout: DashboardLayout[]
  isDefault: boolean
  owner: string
  shareSettings: {
    isPublic: boolean
    allowedUsers: string[]
    allowedRoles: string[]
  }
  refreshInterval: number
  lastModified: string
}

interface DashboardLayout {
  kpiId: string
  position: { x: number; y: number; width: number; height: number }
  visualization: 'gauge' | 'chart' | 'metric' | 'trend' | 'table'
  config: any
}

interface KPIReport {
  id: string
  name: string
  kpis: string[]
  period: 'daily' | 'weekly' | 'monthly' | 'quarterly' | 'annually'
  format: 'pdf' | 'excel' | 'csv'
  recipients: string[]
  schedule?: string
  lastGenerated?: string
  nextScheduled?: string
}

interface KPIAlert {
  id: string
  kpiId: string
  type: 'threshold' | 'trend' | 'missing_data'
  condition: string
  message: string
  severity: 'low' | 'medium' | 'high' | 'critical'
  channels: ('email' | 'sms' | 'slack' | 'webhook')[]
  recipients: string[]
  isActive: boolean
  lastTriggered?: string
  triggerCount: number
}

// Mock data
const generateMockKPIs = (): KPI[] => {
  return [
    {
      id: 'KPI-001',
      name: 'Incident Response Time',
      description: 'Average time to respond to critical incidents',
      category: 'operational',
      type: 'duration',
      unit: 'minutes',
      currentValue: 15,
      targetValue: 30,
      thresholds: [
        {
          id: 'T001',
          name: 'Excellent',
          operator: 'lte',
          value: 15,
          severity: 'good',
          color: '#10b981'
        },
        {
          id: 'T002',
          name: 'Good',
          operator: 'between',
          value: [15, 30],
          severity: 'warning',
          color: '#f59e0b'
        },
        {
          id: 'T003',
          name: 'Poor',
          operator: 'gt',
          value: 30,
          severity: 'critical',
          color: '#ef4444'
        }
      ],
      status: 'on_target',
      trend: 'down',
      frequency: 'real_time',
      dataSource: 'incident_management',
      owner: 'Operations Manager',
      stakeholders: ['BCM Manager', 'CEO'],
      history: [
        { timestamp: '2024-01-01', value: 25 },
        { timestamp: '2024-01-08', value: 22 },
        { timestamp: '2024-01-15', value: 15 }
      ],
      lastUpdated: '2024-01-15T10:30:00Z',
      isActive: true,
      tags: ['incident', 'response', 'time'],
      benchmarks: [
        { name: 'Industry Average', value: 45, source: 'BCM Benchmark Study 2024', date: '2024-01-01' }
      ]
    },
    {
      id: 'KPI-002',
      name: 'BCM Plan Test Coverage',
      description: 'Percentage of BCM plans tested within the last 12 months',
      category: 'compliance',
      type: 'percentage',
      unit: '%',
      currentValue: 85,
      targetValue: 90,
      thresholds: [
        {
          id: 'T004',
          name: 'Compliant',
          operator: 'gte',
          value: 90,
          severity: 'good',
          color: '#10b981'
        },
        {
          id: 'T005',
          name: 'At Risk',
          operator: 'between',
          value: [70, 90],
          severity: 'warning',
          color: '#f59e0b'
        },
        {
          id: 'T006',
          name: 'Non-Compliant',
          operator: 'lt',
          value: 70,
          severity: 'critical',
          color: '#ef4444'
        }
      ],
      status: 'warning',
      trend: 'up',
      frequency: 'monthly',
      dataSource: 'plans_management',
      owner: 'BCM Manager',
      stakeholders: ['Compliance Officer', 'Auditor'],
      history: [
        { timestamp: '2023-11-01', value: 75 },
        { timestamp: '2023-12-01', value: 80 },
        { timestamp: '2024-01-01', value: 85 }
      ],
      lastUpdated: '2024-01-15T09:00:00Z',
      isActive: true,
      tags: ['compliance', 'testing', 'plans']
    },
    {
      id: 'KPI-003',
      name: 'Recovery Time Objective Achievement',
      description: 'Percentage of incidents recovered within defined RTO',
      category: 'performance',
      type: 'percentage',
      unit: '%',
      currentValue: 92,
      targetValue: 95,
      thresholds: [
        {
          id: 'T007',
          name: 'Excellent',
          operator: 'gte',
          value: 95,
          severity: 'good',
          color: '#10b981'
        },
        {
          id: 'T008',
          name: 'Good',
          operator: 'between',
          value: [85, 95],
          severity: 'warning',
          color: '#f59e0b'
        },
        {
          id: 'T009',
          name: 'Poor',
          operator: 'lt',
          value: 85,
          severity: 'critical',
          color: '#ef4444'
        }
      ],
      status: 'warning',
      trend: 'stable',
      frequency: 'monthly',
      dataSource: 'incident_management',
      owner: 'Recovery Manager',
      stakeholders: ['Operations Manager', 'CTO'],
      history: [
        { timestamp: '2023-11-01', value: 88 },
        { timestamp: '2023-12-01', value: 91 },
        { timestamp: '2024-01-01', value: 92 }
      ],
      lastUpdated: '2024-01-15T08:45:00Z',
      isActive: true,
      tags: ['rto', 'recovery', 'performance']
    },
    {
      id: 'KPI-004',
      name: 'BCM Training Completion Rate',
      description: 'Percentage of staff who completed BCM training this year',
      category: 'strategic',
      type: 'percentage',
      unit: '%',
      currentValue: 68,
      targetValue: 85,
      thresholds: [
        {
          id: 'T010',
          name: 'Target Met',
          operator: 'gte',
          value: 85,
          severity: 'good',
          color: '#10b981'
        },
        {
          id: 'T011',
          name: 'Behind Schedule',
          operator: 'between',
          value: [70, 85],
          severity: 'warning',
          color: '#f59e0b'
        },
        {
          id: 'T012',
          name: 'Critical Gap',
          operator: 'lt',
          value: 70,
          severity: 'critical',
          color: '#ef4444'
        }
      ],
      status: 'critical',
      trend: 'up',
      frequency: 'monthly',
      dataSource: 'training_management',
      owner: 'HR Manager',
      stakeholders: ['BCM Manager', 'Training Coordinator'],
      history: [
        { timestamp: '2023-11-01', value: 55 },
        { timestamp: '2023-12-01', value: 62 },
        { timestamp: '2024-01-01', value: 68 }
      ],
      lastUpdated: '2024-01-15T07:30:00Z',
      isActive: true,
      tags: ['training', 'compliance', 'hr']
    },
    {
      id: 'KPI-005',
      name: 'Supplier BCM Assessment Coverage',
      description: 'Percentage of critical suppliers with BCM assessments',
      category: 'risk',
      type: 'percentage',
      unit: '%',
      currentValue: 78,
      targetValue: 90,
      thresholds: [
        {
          id: 'T013',
          name: 'Comprehensive',
          operator: 'gte',
          value: 90,
          severity: 'good',
          color: '#10b981'
        },
        {
          id: 'T014',
          name: 'Partial',
          operator: 'between',
          value: [70, 90],
          severity: 'warning',
          color: '#f59e0b'
        },
        {
          id: 'T015',
          name: 'Inadequate',
          operator: 'lt',
          value: 70,
          severity: 'critical',
          color: '#ef4444'
        }
      ],
      status: 'warning',
      trend: 'up',
      frequency: 'quarterly',
      dataSource: 'supplier_management',
      owner: 'Procurement Manager',
      stakeholders: ['Risk Manager', 'BCM Manager'],
      history: [
        { timestamp: '2023-10-01', value: 65 },
        { timestamp: '2024-01-01', value: 78 }
      ],
      lastUpdated: '2024-01-15T06:00:00Z',
      isActive: true,
      tags: ['suppliers', 'risk', 'assessment']
    }
  ]
}

const generateMockDashboards = (): KPIDashboard[] => {
  return [
    {
      id: 'DASH-KPI-001',
      name: 'Executive KPI Dashboard',
      description: 'High-level BCM performance metrics for senior management',
      kpis: ['KPI-001', 'KPI-002', 'KPI-003', 'KPI-004'],
      layout: [
        {
          kpiId: 'KPI-001',
          position: { x: 0, y: 0, width: 2, height: 1 },
          visualization: 'gauge',
          config: { showTrend: true }
        },
        {
          kpiId: 'KPI-002',
          position: { x: 2, y: 0, width: 2, height: 1 },
          visualization: 'metric',
          config: { showTarget: true }
        }
      ],
      isDefault: true,
      owner: 'BCM Manager',
      shareSettings: {
        isPublic: false,
        allowedUsers: ['CEO', 'COO'],
        allowedRoles: ['Executive']
      },
      refreshInterval: 300,
      lastModified: '2024-01-15T10:00:00Z'
    }
  ]
}

export function KPIManagementModule() {
  const queryClient = useQueryClient()
  const { publishEvent } = useBCMStore()

  const [activeTab, setActiveTab] = useState<'overview' | 'kpis' | 'dashboards' | 'reports' | 'alerts'>('overview')
  const [selectedKPI, setSelectedKPI] = useState<KPI | null>(null)
  const [showNewKPIDialog, setShowNewKPIDialog] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterCategory, setFilterCategory] = useState<string>('all')
  const [filterStatus, setFilterStatus] = useState<string>('all')

  // Fetch KPIs
  const { data: kpis = [], isLoading: kpisLoading } = useQuery({
    queryKey: ['kpis'],
    queryFn: async () => {
      const response = await apiClient.get('/api/kpis')
      if (response.data) {
        return response.data
      }
      return generateMockKPIs()
    }
  })

  // Fetch dashboards
  const { data: dashboards = [] } = useQuery({
    queryKey: ['kpi-dashboards'],
    queryFn: async () => {
      const response = await apiClient.get('/api/kpis/dashboards')
      if (response.data) {
        return response.data
      }
      return generateMockDashboards()
    }
  })

  // Calculate KPI metrics
  const kpiMetrics = {
    totalKPIs: kpis.length,
    activeKPIs: kpis.filter((k: KPI) => k.isActive).length,
    onTargetKPIs: kpis.filter((k: KPI) => k.status === 'on_target').length,
    warningKPIs: kpis.filter((k: KPI) => k.status === 'warning').length,
    criticalKPIs: kpis.filter((k: KPI) => k.status === 'critical').length,
    overallHealth: kpis.length > 0 ?
      (kpis.filter((k: KPI) => k.status === 'on_target').length / kpis.length * 100) : 0,
    avgAchievement: kpis.length > 0 ?
      kpis.reduce((acc: number, k: KPI) => acc + (k.currentValue / k.targetValue * 100), 0) / kpis.length : 0
  }

  // Filter KPIs
  const filteredKPIs = kpis.filter((kpi: KPI) => {
    const matchesSearch = kpi.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         kpi.description.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesCategory = filterCategory === 'all' || kpi.category === filterCategory
    const matchesStatus = filterStatus === 'all' || kpi.status === filterStatus
    return matchesSearch && matchesCategory && matchesStatus
  })

  // Get status color
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'on_target': return 'bg-green-500'
      case 'warning': return 'bg-yellow-500'
      case 'critical': return 'bg-red-500'
      case 'unknown': return 'bg-gray-500'
      default: return 'bg-gray-500'
    }
  }

  // Get trend icon
  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up': return <TrendingUp className="w-4 h-4 text-green-500" />
      case 'down': return <TrendingDown className="w-4 h-4 text-red-500" />
      case 'stable': return <Activity className="w-4 h-4 text-blue-500" />
      default: return null
    }
  }

  // Format KPI value
  const formatKPIValue = (kpi: KPI) => {
    const { currentValue, type, unit } = kpi
    switch (type) {
      case 'percentage':
        return `${currentValue}%`
      case 'duration':
        return `${currentValue} ${unit}`
      case 'currency':
        return `$${currentValue.toLocaleString()}`
      case 'count':
        return currentValue.toString()
      default:
        return `${currentValue} ${unit}`
    }
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">KPI Management</h1>
          <p className="text-muted-foreground mt-1">
            Track and analyze key performance indicators for BCM
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={() => queryClient.invalidateQueries({ queryKey: ['kpis'] })}
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </Button>
          <Dialog open={showNewKPIDialog} onOpenChange={setShowNewKPIDialog}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="w-4 h-4 mr-2" />
                New KPI
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>Create New KPI</DialogTitle>
                <DialogDescription>
                  Define a new key performance indicator for BCM monitoring
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4 mt-4">
                <div>
                  <Label>KPI Name</Label>
                  <Input placeholder="Enter KPI name" />
                </div>
                <div>
                  <Label>Description</Label>
                  <Textarea placeholder="Describe what this KPI measures" rows={2} />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label>Category</Label>
                    <Select>
                      <SelectTrigger>
                        <SelectValue placeholder="Select category" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="operational">Operational</SelectItem>
                        <SelectItem value="strategic">Strategic</SelectItem>
                        <SelectItem value="compliance">Compliance</SelectItem>
                        <SelectItem value="financial">Financial</SelectItem>
                        <SelectItem value="risk">Risk</SelectItem>
                        <SelectItem value="performance">Performance</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label>Type</Label>
                    <Select>
                      <SelectTrigger>
                        <SelectValue placeholder="Select type" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="percentage">Percentage</SelectItem>
                        <SelectItem value="count">Count</SelectItem>
                        <SelectItem value="duration">Duration</SelectItem>
                        <SelectItem value="currency">Currency</SelectItem>
                        <SelectItem value="ratio">Ratio</SelectItem>
                        <SelectItem value="score">Score</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label>Target Value</Label>
                    <Input type="number" placeholder="Enter target value" />
                  </div>
                  <div>
                    <Label>Unit</Label>
                    <Input placeholder="e.g., %, minutes, $" />
                  </div>
                </div>
                <div>
                  <Label>Data Source</Label>
                  <Select>
                    <SelectTrigger>
                      <SelectValue placeholder="Select data source" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="incident_management">Incident Management</SelectItem>
                      <SelectItem value="plans_management">Plans Management</SelectItem>
                      <SelectItem value="risk_management">Risk Management</SelectItem>
                      <SelectItem value="training_management">Training Management</SelectItem>
                      <SelectItem value="compliance">Compliance</SelectItem>
                      <SelectItem value="manual">Manual Input</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label>Owner</Label>
                  <Input placeholder="Enter KPI owner" />
                </div>
                <div className="flex justify-end gap-2">
                  <Button variant="outline" onClick={() => setShowNewKPIDialog(false)}>
                    Cancel
                  </Button>
                  <Button>
                    <Target className="w-4 h-4 mr-2" />
                    Create KPI
                  </Button>
                </div>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Critical KPI Alert */}
      {kpiMetrics.criticalKPIs > 0 && (
        <Alert className="border-red-500 bg-red-50">
          <AlertTriangle className="h-4 w-4 text-red-600" />
          <AlertDescription className="text-red-800">
            <strong>{kpiMetrics.criticalKPIs} KPI{kpiMetrics.criticalKPIs > 1 ? 's' : ''}</strong> are in critical status.
            Immediate attention required to meet targets.
          </AlertDescription>
        </Alert>
      )}

      {/* KPI Metrics Overview */}
      <div className="grid grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <div className="flex justify-between items-center">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Overall Health
              </CardTitle>
              <Gauge className="w-4 h-4 text-blue-500" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">{Math.round(kpiMetrics.overallHealth)}%</div>
            <div className="text-xs text-muted-foreground mt-1">
              {kpiMetrics.onTargetKPIs} of {kpiMetrics.totalKPIs} on target
            </div>
            <Progress value={kpiMetrics.overallHealth} className="mt-2" />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <div className="flex justify-between items-center">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Critical KPIs
              </CardTitle>
              <AlertCircle className="w-4 h-4 text-red-500" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{kpiMetrics.criticalKPIs}</div>
            <div className="text-xs text-muted-foreground mt-1">
              Require immediate action
            </div>
            <Progress value={kpiMetrics.criticalKPIs / kpiMetrics.totalKPIs * 100} className="mt-2" />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <div className="flex justify-between items-center">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Warning KPIs
              </CardTitle>
              <AlertTriangle className="w-4 h-4 text-yellow-500" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">{kpiMetrics.warningKPIs}</div>
            <div className="text-xs text-muted-foreground mt-1">
              Need monitoring
            </div>
            <Progress value={kpiMetrics.warningKPIs / kpiMetrics.totalKPIs * 100} className="mt-2" />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <div className="flex justify-between items-center">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Avg Achievement
              </CardTitle>
              <Target className="w-4 h-4 text-green-500" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{Math.round(kpiMetrics.avgAchievement)}%</div>
            <div className="text-xs text-muted-foreground mt-1">
              Against targets
            </div>
            <Progress value={kpiMetrics.avgAchievement} className="mt-2" />
          </CardContent>
        </Card>
      </div>

      {/* Main Content Tabs */}
      <Tabs value={activeTab} onValueChange={(v: any) => setActiveTab(v)}>
        <TabsList className="grid grid-cols-5 w-full">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="kpis">KPIs</TabsTrigger>
          <TabsTrigger value="dashboards">Dashboards</TabsTrigger>
          <TabsTrigger value="reports">Reports</TabsTrigger>
          <TabsTrigger value="alerts">Alerts</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="mt-6">
          <div className="grid grid-cols-3 gap-6">
            {/* Top Performing KPIs */}
            <Card>
              <CardHeader>
                <CardTitle>Top Performing KPIs</CardTitle>
                <CardDescription>KPIs exceeding targets</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {kpis
                    .filter((kpi: KPI) => kpi.status === 'on_target')
                    .slice(0, 5)
                    .map((kpi: KPI) => (
                      <div key={kpi.id} className="flex items-center justify-between p-2 border rounded">
                        <div>
                          <div className="font-medium text-sm">{kpi.name}</div>
                          <div className="text-xs text-muted-foreground">{kpi.category}</div>
                        </div>
                        <div className="text-right">
                          <div className="font-bold text-green-600">{formatKPIValue(kpi)}</div>
                          <div className="text-xs text-muted-foreground">
                            Target: {kpi.targetValue}{kpi.unit}
                          </div>
                        </div>
                      </div>
                    ))}
                </div>
              </CardContent>
            </Card>

            {/* KPIs Needing Attention */}
            <Card>
              <CardHeader>
                <CardTitle>Needs Attention</CardTitle>
                <CardDescription>KPIs below target or critical</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {kpis
                    .filter((kpi: KPI) => kpi.status === 'critical' || kpi.status === 'warning')
                    .slice(0, 5)
                    .map((kpi: KPI) => (
                      <div key={kpi.id} className="flex items-center justify-between p-2 border rounded">
                        <div>
                          <div className="font-medium text-sm">{kpi.name}</div>
                          <div className="text-xs text-muted-foreground">{kpi.category}</div>
                        </div>
                        <div className="text-right">
                          <div className={`font-bold ${
                            kpi.status === 'critical' ? 'text-red-600' : 'text-yellow-600'
                          }`}>
                            {formatKPIValue(kpi)}
                          </div>
                          <div className="text-xs text-muted-foreground">
                            Target: {kpi.targetValue}{kpi.unit}
                          </div>
                        </div>
                      </div>
                    ))}
                </div>
              </CardContent>
            </Card>

            {/* KPI Categories */}
            <Card>
              <CardHeader>
                <CardTitle>KPI Categories</CardTitle>
                <CardDescription>Distribution by category</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {['operational', 'strategic', 'compliance', 'financial', 'risk', 'performance'].map((category) => {
                    const categoryKPIs = kpis.filter((k: KPI) => k.category === category)
                    const onTarget = categoryKPIs.filter((k: KPI) => k.status === 'on_target').length

                    return (
                      <div key={category} className="flex items-center justify-between">
                        <div className="capitalize">{category}</div>
                        <div className="flex items-center gap-2">
                          <Progress
                            value={categoryKPIs.length > 0 ? (onTarget / categoryKPIs.length * 100) : 0}
                            className="w-20"
                          />
                          <span className="text-sm w-12">{onTarget}/{categoryKPIs.length}</span>
                        </div>
                      </div>
                    )
                  })}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="kpis" className="mt-6">
          <Card>
            <CardHeader>
              <div className="flex justify-between items-center">
                <div>
                  <CardTitle>KPI Registry</CardTitle>
                  <CardDescription>All key performance indicators</CardDescription>
                </div>
                <div className="flex gap-2">
                  <div className="relative">
                    <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                    <Input
                      placeholder="Search KPIs..."
                      className="pl-8 w-64"
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                    />
                  </div>
                  <Select value={filterCategory} onValueChange={setFilterCategory}>
                    <SelectTrigger className="w-40">
                      <SelectValue placeholder="Category" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Categories</SelectItem>
                      <SelectItem value="operational">Operational</SelectItem>
                      <SelectItem value="strategic">Strategic</SelectItem>
                      <SelectItem value="compliance">Compliance</SelectItem>
                      <SelectItem value="financial">Financial</SelectItem>
                      <SelectItem value="risk">Risk</SelectItem>
                      <SelectItem value="performance">Performance</SelectItem>
                    </SelectContent>
                  </Select>
                  <Select value={filterStatus} onValueChange={setFilterStatus}>
                    <SelectTrigger className="w-32">
                      <SelectValue placeholder="Status" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Status</SelectItem>
                      <SelectItem value="on_target">On Target</SelectItem>
                      <SelectItem value="warning">Warning</SelectItem>
                      <SelectItem value="critical">Critical</SelectItem>
                      <SelectItem value="unknown">Unknown</SelectItem>
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
                      <th className="text-left p-3 font-medium">KPI</th>
                      <th className="text-left p-3 font-medium">Current Value</th>
                      <th className="text-left p-3 font-medium">Target</th>
                      <th className="text-left p-3 font-medium">Status</th>
                      <th className="text-left p-3 font-medium">Trend</th>
                      <th className="text-left p-3 font-medium">Owner</th>
                      <th className="text-left p-3 font-medium">Last Updated</th>
                      <th className="text-left p-3 font-medium">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredKPIs.map((kpi: KPI) => (
                      <tr key={kpi.id} className="border-b hover:bg-accent">
                        <td className="p-3">
                          <div>
                            <div className="font-medium">{kpi.name}</div>
                            <div className="text-xs text-muted-foreground capitalize">
                              {kpi.category} • {kpi.frequency.replace('_', ' ')}
                            </div>
                          </div>
                        </td>
                        <td className="p-3">
                          <div className="font-bold">{formatKPIValue(kpi)}</div>
                        </td>
                        <td className="p-3">
                          <div>{kpi.targetValue}{kpi.unit}</div>
                        </td>
                        <td className="p-3">
                          <Badge className={getStatusColor(kpi.status)}>
                            {kpi.status.replace('_', ' ')}
                          </Badge>
                        </td>
                        <td className="p-3">
                          <div className="flex items-center gap-1">
                            {getTrendIcon(kpi.trend)}
                            <span className="text-sm capitalize">{kpi.trend}</span>
                          </div>
                        </td>
                        <td className="p-3">{kpi.owner}</td>
                        <td className="p-3 text-sm">
                          {new Date(kpi.lastUpdated).toLocaleDateString()}
                        </td>
                        <td className="p-3">
                          <div className="flex gap-1">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => setSelectedKPI(kpi)}
                            >
                              <Eye className="w-4 h-4" />
                            </Button>
                            <Button variant="ghost" size="sm">
                              <Edit className="w-4 h-4" />
                            </Button>
                            <Button variant="ghost" size="sm">
                              <BarChart3 className="w-4 h-4" />
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

        <TabsContent value="dashboards" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>KPI Dashboards</CardTitle>
              <CardDescription>Visual KPI monitoring dashboards</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-6">
                {dashboards.map((dashboard: KPIDashboard) => (
                  <div key={dashboard.id} className="border rounded-lg p-4">
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <h3 className="font-medium text-lg">{dashboard.name}</h3>
                        <p className="text-sm text-muted-foreground">{dashboard.description}</p>
                      </div>
                      {dashboard.isDefault && (
                        <Badge className="bg-blue-500">Default</Badge>
                      )}
                    </div>
                    <div className="flex justify-between items-center text-xs text-muted-foreground mb-3">
                      <span>{dashboard.kpis.length} KPIs</span>
                      <span>Refresh: {dashboard.refreshInterval}s</span>
                      <span>Owner: {dashboard.owner}</span>
                    </div>
                    <div className="flex gap-2">
                      <Button size="sm">
                        <Eye className="w-4 h-4 mr-1" />
                        View
                      </Button>
                      <Button size="sm" variant="outline">
                        <Edit className="w-4 h-4 mr-1" />
                        Edit
                      </Button>
                      <Button size="sm" variant="outline">
                        <Copy className="w-4 h-4 mr-1" />
                        Clone
                      </Button>
                    </div>
                  </div>
                ))}

                {/* Create New Dashboard */}
                <div className="border-2 border-dashed rounded-lg p-6 text-center">
                  <BarChart3 className="w-8 h-8 mx-auto mb-2 text-muted-foreground" />
                  <h3 className="font-medium mb-1">Create Dashboard</h3>
                  <p className="text-sm text-muted-foreground mb-3">
                    Build custom KPI dashboard
                  </p>
                  <Button variant="outline">
                    <Plus className="w-4 h-4 mr-2" />
                    New Dashboard
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="reports" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>KPI Reports</CardTitle>
              <CardDescription>Scheduled and on-demand KPI reports</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <h3 className="text-lg font-medium">Available Reports</h3>
                  <Button>
                    <Plus className="w-4 h-4 mr-2" />
                    New Report
                  </Button>
                </div>

                {/* Sample Reports */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="border rounded-lg p-4">
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <h4 className="font-medium">Monthly Executive KPI Report</h4>
                        <p className="text-sm text-muted-foreground">Executive summary of all KPIs</p>
                      </div>
                      <Badge variant="outline">Scheduled</Badge>
                    </div>
                    <div className="text-xs text-muted-foreground mb-3">
                      5 KPIs • PDF Format • Monthly • Next: Feb 1, 2024
                    </div>
                    <div className="flex gap-2">
                      <Button size="sm" variant="outline">
                        <Download className="w-4 h-4 mr-1" />
                        Download
                      </Button>
                      <Button size="sm" variant="outline">
                        <Settings className="w-4 h-4 mr-1" />
                        Configure
                      </Button>
                    </div>
                  </div>

                  <div className="border rounded-lg p-4">
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <h4 className="font-medium">Operational KPI Dashboard</h4>
                        <p className="text-sm text-muted-foreground">Daily operational metrics</p>
                      </div>
                      <Badge variant="outline">On-Demand</Badge>
                    </div>
                    <div className="text-xs text-muted-foreground mb-3">
                      3 KPIs • Excel Format • Daily
                    </div>
                    <div className="flex gap-2">
                      <Button size="sm">
                        <Download className="w-4 h-4 mr-1" />
                        Generate
                      </Button>
                      <Button size="sm" variant="outline">
                        <Edit className="w-4 h-4 mr-1" />
                        Edit
                      </Button>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="alerts" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>KPI Alerts</CardTitle>
              <CardDescription>Automated notifications for KPI thresholds</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <h3 className="text-lg font-medium">Alert Rules</h3>
                  <Button>
                    <Plus className="w-4 h-4 mr-2" />
                    New Alert
                  </Button>
                </div>

                {/* Sample Alerts */}
                <div className="space-y-3">
                  <div className="border rounded-lg p-4">
                    <div className="flex justify-between items-start">
                      <div>
                        <h4 className="font-medium">Critical Incident Response Time</h4>
                        <p className="text-sm text-muted-foreground">
                          Alert when incident response time exceeds 30 minutes
                        </p>
                        <div className="text-xs text-muted-foreground mt-1">
                          Email, Slack • Recipients: Operations Team
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge className="bg-red-500">High</Badge>
                        <Badge variant="outline">Active</Badge>
                      </div>
                    </div>
                    <div className="flex justify-between items-center mt-3 text-xs text-muted-foreground">
                      <span>Last triggered: Never</span>
                      <span>Trigger count: 0</span>
                    </div>
                  </div>

                  <div className="border rounded-lg p-4">
                    <div className="flex justify-between items-start">
                      <div>
                        <h4 className="font-medium">BCM Training Completion</h4>
                        <p className="text-sm text-muted-foreground">
                          Alert when training completion falls below 70%
                        </p>
                        <div className="text-xs text-muted-foreground mt-1">
                          Email • Recipients: HR Manager, BCM Manager
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge className="bg-yellow-500">Medium</Badge>
                        <Badge variant="outline">Active</Badge>
                      </div>
                    </div>
                    <div className="flex justify-between items-center mt-3 text-xs text-muted-foreground">
                      <span>Last triggered: Jan 10, 2024</span>
                      <span>Trigger count: 2</span>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Selected KPI Detail Modal */}
      {selectedKPI && (
        <Dialog open={!!selectedKPI} onOpenChange={() => setSelectedKPI(null)}>
          <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
            <DialogHeader>
              <div className="flex justify-between items-start">
                <div>
                  <DialogTitle className="text-xl">{selectedKPI.name}</DialogTitle>
                  <DialogDescription>{selectedKPI.description}</DialogDescription>
                </div>
                <div className="flex gap-2">
                  <Badge className={getStatusColor(selectedKPI.status)}>
                    {selectedKPI.status.replace('_', ' ')}
                  </Badge>
                  <Badge variant="outline" className="capitalize">
                    {selectedKPI.category}
                  </Badge>
                </div>
              </div>
            </DialogHeader>
            <div className="space-y-6 mt-6">
              {/* KPI Summary */}
              <div className="grid grid-cols-3 gap-4">
                <Card>
                  <CardContent className="p-4 text-center">
                    <div className="text-2xl font-bold">{formatKPIValue(selectedKPI)}</div>
                    <div className="text-sm text-muted-foreground">Current Value</div>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="p-4 text-center">
                    <div className="text-2xl font-bold">{selectedKPI.targetValue}{selectedKPI.unit}</div>
                    <div className="text-sm text-muted-foreground">Target Value</div>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="p-4 text-center">
                    <div className="text-2xl font-bold flex items-center justify-center gap-1">
                      {Math.round((selectedKPI.currentValue / selectedKPI.targetValue) * 100)}%
                      {getTrendIcon(selectedKPI.trend)}
                    </div>
                    <div className="text-sm text-muted-foreground">Achievement</div>
                  </CardContent>
                </Card>
              </div>

              {/* KPI Details */}
              <div>
                <h3 className="font-medium mb-2">KPI Information</h3>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-muted-foreground">Owner:</span>
                    <span className="ml-2">{selectedKPI.owner}</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Data Source:</span>
                    <span className="ml-2">{selectedKPI.dataSource}</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Frequency:</span>
                    <span className="ml-2 capitalize">{selectedKPI.frequency.replace('_', ' ')}</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Last Updated:</span>
                    <span className="ml-2">{new Date(selectedKPI.lastUpdated).toLocaleString()}</span>
                  </div>
                </div>
              </div>

              {/* Thresholds */}
              <div>
                <h3 className="font-medium mb-2">Thresholds</h3>
                <div className="space-y-2">
                  {selectedKPI.thresholds.map((threshold) => (
                    <div key={threshold.id} className="flex items-center justify-between p-2 border rounded">
                      <div className="flex items-center gap-2">
                        <div
                          className="w-3 h-3 rounded-full"
                          style={{ backgroundColor: threshold.color }}
                        ></div>
                        <span className="font-medium text-sm">{threshold.name}</span>
                      </div>
                      <div className="text-sm">
                        {threshold.operator} {Array.isArray(threshold.value) ?
                          `${threshold.value[0]} - ${threshold.value[1]}` :
                          threshold.value
                        } {selectedKPI.unit}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Stakeholders */}
              {selectedKPI.stakeholders.length > 0 && (
                <div>
                  <h3 className="font-medium mb-2">Stakeholders</h3>
                  <div className="flex flex-wrap gap-2">
                    {selectedKPI.stakeholders.map((stakeholder) => (
                      <Badge key={stakeholder} variant="secondary">{stakeholder}</Badge>
                    ))}
                  </div>
                </div>
              )}

              {/* Historical Data */}
              {selectedKPI.history.length > 0 && (
                <div>
                  <h3 className="font-medium mb-2">Recent History</h3>
                  <div className="border rounded">
                    <table className="w-full text-sm">
                      <thead className="border-b bg-muted/50">
                        <tr>
                          <th className="text-left p-2">Date</th>
                          <th className="text-left p-2">Value</th>
                          <th className="text-left p-2">vs Target</th>
                        </tr>
                      </thead>
                      <tbody>
                        {selectedKPI.history.slice(-5).map((point, i) => (
                          <tr key={i} className="border-b">
                            <td className="p-2">{new Date(point.timestamp).toLocaleDateString()}</td>
                            <td className="p-2">{point.value}{selectedKPI.unit}</td>
                            <td className="p-2">
                              <span className={`${
                                point.value >= selectedKPI.targetValue ? 'text-green-600' : 'text-red-600'
                              }`}>
                                {Math.round((point.value / selectedKPI.targetValue) * 100)}%
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              <div className="flex justify-end gap-2 pt-4 border-t">
                <Button variant="outline">
                  <Edit className="w-4 h-4 mr-2" />
                  Edit KPI
                </Button>
                <Button variant="outline">
                  <BarChart3 className="w-4 h-4 mr-2" />
                  View Chart
                </Button>
                <Button variant="outline">
                  <Download className="w-4 h-4 mr-2" />
                  Export Data
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      )}
    </div>
  )
}