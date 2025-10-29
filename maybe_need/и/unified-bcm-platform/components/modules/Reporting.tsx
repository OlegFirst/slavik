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
import { Calendar } from '@/components/ui/calendar'
import { Checkbox } from '@/components/ui/checkbox'
import {
  BarChart3,
  LineChart,
  PieChart,
  TrendingUp,
  TrendingDown,
  Download,
  Upload,
  FileText,
  Calendar as CalendarIcon,
  Clock,
  Users,
  Target,
  Activity,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Eye,
  Edit,
  Copy,
  Share,
  Printer,
  Mail,
  Filter,
  Search,
  RefreshCw,
  Settings,
  Info,
  Zap,
  Shield,
  Building,
  GitBranch,
  BookOpen,
  Award
} from 'lucide-react'
import { apiClient } from '@/lib/api-client'
import { useBCMStore } from '@/lib/bcm-store'

// Types
interface Report {
  id: string
  name: string
  type: 'dashboard' | 'compliance' | 'incident' | 'plan' | 'risk' | 'kpi' | 'executive' | 'regulatory'
  category: 'operational' | 'strategic' | 'compliance' | 'audit'
  status: 'scheduled' | 'generating' | 'completed' | 'failed' | 'draft'
  format: 'pdf' | 'excel' | 'word' | 'html' | 'csv'
  frequency: 'on_demand' | 'daily' | 'weekly' | 'monthly' | 'quarterly' | 'annually'
  lastGenerated?: string
  nextScheduled?: string
  createdBy: string
  recipients: string[]
  parameters: ReportParameter[]
  metrics: ReportMetric[]
  sections: ReportSection[]
  template?: string
  size?: number
  downloadUrl?: string
  schedule?: ReportSchedule
}

interface ReportParameter {
  id: string
  name: string
  type: 'date_range' | 'department' | 'risk_level' | 'incident_type' | 'plan_type' | 'status'
  value: any
  required: boolean
  options?: string[]
}

interface ReportMetric {
  id: string
  name: string
  value: number
  target?: number
  trend: 'up' | 'down' | 'stable'
  unit: string
  category: string
}

interface ReportSection {
  id: string
  title: string
  type: 'summary' | 'chart' | 'table' | 'text' | 'metrics'
  order: number
  content?: any
  config?: any
}

interface ReportSchedule {
  frequency: string
  time: string
  dayOfWeek?: number
  dayOfMonth?: number
  recipients: string[]
  enabled: boolean
}

interface Dashboard {
  id: string
  name: string
  description: string
  widgets: DashboardWidget[]
  layout: string
  isDefault: boolean
  createdBy: string
  lastModified: string
  shareSettings: {
    isPublic: boolean
    allowedUsers: string[]
    allowedRoles: string[]
  }
}

interface DashboardWidget {
  id: string
  type: 'metric' | 'chart' | 'table' | 'gauge' | 'trend' | 'alert'
  title: string
  size: 'small' | 'medium' | 'large' | 'full'
  position: { x: number; y: number; width: number; height: number }
  dataSource: string
  config: any
  refreshInterval?: number
}

interface ReportTemplate {
  id: string
  name: string
  description: string
  type: string
  sections: string[]
  parameters: string[]
  isBuiltIn: boolean
  category: string
  lastUsed?: string
}

// Mock data
const generateMockReports = (): Report[] => {
  return [
    {
      id: 'RPT-001',
      name: 'Monthly BCM Performance Report',
      type: 'dashboard',
      category: 'operational',
      status: 'completed',
      format: 'pdf',
      frequency: 'monthly',
      lastGenerated: '2024-01-15T10:30:00Z',
      nextScheduled: '2024-02-15T10:30:00Z',
      createdBy: 'BCM Manager',
      recipients: ['CEO', 'COO', 'Board'],
      parameters: [
        {
          id: 'date_range',
          name: 'Reporting Period',
          type: 'date_range',
          value: { from: '2024-01-01', to: '2024-01-31' },
          required: true
        }
      ],
      metrics: [
        {
          id: 'incidents_resolved',
          name: 'Incidents Resolved',
          value: 12,
          target: 15,
          trend: 'up',
          unit: 'count',
          category: 'incident'
        },
        {
          id: 'plan_test_coverage',
          name: 'Plan Test Coverage',
          value: 85,
          target: 90,
          trend: 'stable',
          unit: 'percentage',
          category: 'plan'
        }
      ],
      sections: [
        {
          id: 'executive_summary',
          title: 'Executive Summary',
          type: 'summary',
          order: 1
        },
        {
          id: 'kpi_metrics',
          title: 'Key Performance Indicators',
          type: 'metrics',
          order: 2
        }
      ],
      size: 2048000, // 2MB
      downloadUrl: '/api/reports/RPT-001/download'
    },
    {
      id: 'RPT-002',
      name: 'ISO 22301 Compliance Assessment',
      type: 'compliance',
      category: 'compliance',
      status: 'scheduled',
      format: 'word',
      frequency: 'quarterly',
      nextScheduled: '2024-03-31T09:00:00Z',
      createdBy: 'Compliance Officer',
      recipients: ['Auditor', 'BCM Manager', 'Quality Manager'],
      parameters: [],
      metrics: [],
      sections: [],
      template: 'iso22301_template'
    },
    {
      id: 'RPT-003',
      name: 'Incident Response Analysis',
      type: 'incident',
      category: 'operational',
      status: 'generating',
      format: 'excel',
      frequency: 'on_demand',
      createdBy: 'Operations Manager',
      recipients: ['Crisis Team'],
      parameters: [],
      metrics: [],
      sections: []
    }
  ]
}

const generateMockDashboards = (): Dashboard[] => {
  return [
    {
      id: 'DASH-001',
      name: 'Executive Dashboard',
      description: 'High-level BCM overview for senior management',
      widgets: [
        {
          id: 'W001',
          type: 'metric',
          title: 'Active Incidents',
          size: 'small',
          position: { x: 0, y: 0, width: 1, height: 1 },
          dataSource: 'incidents',
          config: { metric: 'active_count' }
        },
        {
          id: 'W002',
          type: 'chart',
          title: 'Monthly Incidents Trend',
          size: 'medium',
          position: { x: 1, y: 0, width: 2, height: 1 },
          dataSource: 'incidents',
          config: { chartType: 'line', timeRange: '6M' }
        }
      ],
      layout: 'grid',
      isDefault: true,
      createdBy: 'System',
      lastModified: '2024-01-15T08:00:00Z',
      shareSettings: {
        isPublic: false,
        allowedUsers: ['CEO', 'COO'],
        allowedRoles: ['Executive']
      }
    },
    {
      id: 'DASH-002',
      name: 'Operational Dashboard',
      description: 'Detailed operational metrics for BCM team',
      widgets: [],
      layout: 'grid',
      isDefault: false,
      createdBy: 'BCM Manager',
      lastModified: '2024-01-10T14:30:00Z',
      shareSettings: {
        isPublic: false,
        allowedUsers: [],
        allowedRoles: ['BCM Team']
      }
    }
  ]
}

const generateMockTemplates = (): ReportTemplate[] => {
  return [
    {
      id: 'TPL-001',
      name: 'Executive Summary Template',
      description: 'Standard executive summary format',
      type: 'executive',
      sections: ['Executive Summary', 'Key Metrics', 'Recommendations'],
      parameters: ['date_range', 'department'],
      isBuiltIn: true,
      category: 'strategic',
      lastUsed: '2024-01-15'
    },
    {
      id: 'TPL-002',
      name: 'ISO 22301 Compliance Report',
      description: 'Comprehensive compliance assessment',
      type: 'compliance',
      sections: ['Compliance Status', 'Gap Analysis', 'Action Plan'],
      parameters: ['audit_date', 'scope'],
      isBuiltIn: true,
      category: 'compliance'
    },
    {
      id: 'TPL-003',
      name: 'Incident Analysis Report',
      description: 'Detailed incident investigation and analysis',
      type: 'incident',
      sections: ['Incident Details', 'Root Cause', 'Lessons Learned'],
      parameters: ['incident_id', 'date_range'],
      isBuiltIn: true,
      category: 'operational'
    }
  ]
}

export function ReportingModule() {
  const queryClient = useQueryClient()
  const { publishEvent } = useBCMStore()

  const [activeTab, setActiveTab] = useState<'dashboard' | 'reports' | 'analytics' | 'templates' | 'schedule'>('dashboard')
  const [selectedReport, setSelectedReport] = useState<Report | null>(null)
  const [selectedDashboard, setSelectedDashboard] = useState<Dashboard | null>(null)
  const [showNewReportDialog, setShowNewReportDialog] = useState(false)
  const [showNewDashboardDialog, setShowNewDashboardDialog] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterType, setFilterType] = useState<string>('all')
  const [filterStatus, setFilterStatus] = useState<string>('all')

  // Fetch reports
  const { data: reports = [], isLoading: reportsLoading } = useQuery({
    queryKey: ['bcm-reports'],
    queryFn: async () => {
      const response = await apiClient.get('/api/reports')
      if (response.data) {
        return response.data
      }
      return generateMockReports()
    }
  })

  // Fetch dashboards
  const { data: dashboards = [] } = useQuery({
    queryKey: ['dashboards'],
    queryFn: async () => {
      const response = await apiClient.get('/api/dashboards')
      if (response.data) {
        return response.data
      }
      return generateMockDashboards()
    }
  })

  // Fetch templates
  const { data: templates = [] } = useQuery({
    queryKey: ['report-templates'],
    queryFn: async () => {
      const response = await apiClient.get('/api/reports/templates')
      if (response.data) {
        return response.data
      }
      return generateMockTemplates()
    }
  })

  // Calculate reporting metrics
  const reportingMetrics = {
    totalReports: reports.length,
    scheduledReports: reports.filter((r: Report) => r.frequency !== 'on_demand').length,
    completedThisMonth: reports.filter((r: Report) =>
      r.lastGenerated &&
      new Date(r.lastGenerated).getMonth() === new Date().getMonth()
    ).length,
    avgGenerationTime: 45, // seconds - mock
    totalDashboards: dashboards.length,
    activeDashboards: dashboards.filter((d: Dashboard) => d.isDefault).length,
    reportUsage: 78, // percentage - mock
    storageUsed: reports.reduce((acc: number, r: Report) => acc + (r.size || 0), 0)
  }

  // Filter reports
  const filteredReports = reports.filter((report: Report) => {
    const matchesSearch = report.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         report.category.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesType = filterType === 'all' || report.type === filterType
    const matchesStatus = filterStatus === 'all' || report.status === filterStatus
    return matchesSearch && matchesType && matchesStatus
  })

  // Get status color
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-500'
      case 'generating': return 'bg-blue-500'
      case 'scheduled': return 'bg-yellow-500'
      case 'failed': return 'bg-red-500'
      case 'draft': return 'bg-gray-500'
      default: return 'bg-gray-500'
    }
  }

  // Format file size
  const formatFileSize = (bytes?: number) => {
    if (!bytes) return 'N/A'
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(1024))
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i]
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Reporting & Analytics</h1>
          <p className="text-muted-foreground mt-1">
            Generate insights and reports from BCM data
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={() => queryClient.invalidateQueries({ queryKey: ['bcm-reports'] })}
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </Button>
          <Dialog open={showNewReportDialog} onOpenChange={setShowNewReportDialog}>
            <DialogTrigger asChild>
              <Button>
                <FileText className="w-4 h-4 mr-2" />
                New Report
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>Create New Report</DialogTitle>
                <DialogDescription>
                  Generate a new BCM report from available data
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4 mt-4">
                <div>
                  <Label>Report Name</Label>
                  <Input placeholder="Enter report name" />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label>Report Type</Label>
                    <Select>
                      <SelectTrigger>
                        <SelectValue placeholder="Select type" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="dashboard">Dashboard Summary</SelectItem>
                        <SelectItem value="compliance">Compliance Report</SelectItem>
                        <SelectItem value="incident">Incident Analysis</SelectItem>
                        <SelectItem value="plan">Plan Status Report</SelectItem>
                        <SelectItem value="risk">Risk Assessment</SelectItem>
                        <SelectItem value="kpi">KPI Report</SelectItem>
                        <SelectItem value="executive">Executive Summary</SelectItem>
                        <SelectItem value="regulatory">Regulatory Report</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label>Output Format</Label>
                    <Select>
                      <SelectTrigger>
                        <SelectValue placeholder="Select format" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="pdf">PDF Document</SelectItem>
                        <SelectItem value="excel">Excel Spreadsheet</SelectItem>
                        <SelectItem value="word">Word Document</SelectItem>
                        <SelectItem value="html">HTML Page</SelectItem>
                        <SelectItem value="csv">CSV Data</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <div>
                  <Label>Template</Label>
                  <Select>
                    <SelectTrigger>
                      <SelectValue placeholder="Select template" />
                    </SelectTrigger>
                    <SelectContent>
                      {templates.map((template: ReportTemplate) => (
                        <SelectItem key={template.id} value={template.id}>
                          {template.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label>Date Range</Label>
                  <div className="grid grid-cols-2 gap-2">
                    <Input type="date" placeholder="From" />
                    <Input type="date" placeholder="To" />
                  </div>
                </div>
                <div>
                  <Label>Recipients</Label>
                  <Input placeholder="Enter email addresses (comma-separated)" />
                </div>
                <div className="flex items-center space-x-2">
                  <Checkbox id="schedule" />
                  <Label htmlFor="schedule">Schedule for regular generation</Label>
                </div>
                <div className="flex justify-end gap-2">
                  <Button variant="outline" onClick={() => setShowNewReportDialog(false)}>
                    Cancel
                  </Button>
                  <Button>
                    <BarChart3 className="w-4 h-4 mr-2" />
                    Generate Report
                  </Button>
                </div>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Reporting Metrics Overview */}
      <div className="grid grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <div className="flex justify-between items-center">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Total Reports
              </CardTitle>
              <FileText className="w-4 h-4 text-blue-500" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">{reportingMetrics.totalReports}</div>
            <div className="text-xs text-muted-foreground mt-1">
              {reportingMetrics.scheduledReports} scheduled
            </div>
            <Progress value={reportingMetrics.scheduledReports / reportingMetrics.totalReports * 100} className="mt-2" />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <div className="flex justify-between items-center">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Generated This Month
              </CardTitle>
              <TrendingUp className="w-4 h-4 text-green-500" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{reportingMetrics.completedThisMonth}</div>
            <div className="text-xs text-muted-foreground mt-1">
              Avg time: {reportingMetrics.avgGenerationTime}s
            </div>
            <Progress value={reportingMetrics.completedThisMonth * 10} className="mt-2" />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <div className="flex justify-between items-center">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Active Dashboards
              </CardTitle>
              <BarChart3 className="w-4 h-4 text-purple-500" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-purple-600">{reportingMetrics.activeDashboards}</div>
            <div className="text-xs text-muted-foreground mt-1">
              of {reportingMetrics.totalDashboards} total
            </div>
            <Progress value={reportingMetrics.activeDashboards / reportingMetrics.totalDashboards * 100} className="mt-2" />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <div className="flex justify-between items-center">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Storage Used
              </CardTitle>
              <Activity className="w-4 h-4 text-orange-500" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">
              {formatFileSize(reportingMetrics.storageUsed)}
            </div>
            <div className="text-xs text-muted-foreground mt-1">
              Report usage: {reportingMetrics.reportUsage}%
            </div>
            <Progress value={reportingMetrics.reportUsage} className="mt-2" />
          </CardContent>
        </Card>
      </div>

      {/* Main Content Tabs */}
      <Tabs value={activeTab} onValueChange={(v: any) => setActiveTab(v)}>
        <TabsList className="grid grid-cols-5 w-full">
          <TabsTrigger value="dashboard">Dashboards</TabsTrigger>
          <TabsTrigger value="reports">Reports</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
          <TabsTrigger value="templates">Templates</TabsTrigger>
          <TabsTrigger value="schedule">Schedule</TabsTrigger>
        </TabsList>

        <TabsContent value="dashboard" className="mt-6">
          <div className="grid grid-cols-3 gap-6">
            {/* Available Dashboards */}
            <div className="col-span-2">
              <Card>
                <CardHeader>
                  <CardTitle>Available Dashboards</CardTitle>
                  <CardDescription>Interactive data visualization dashboards</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {dashboards.map((dashboard: Dashboard) => (
                      <div key={dashboard.id} className="border rounded-lg p-4">
                        <div className="flex justify-between items-start mb-2">
                          <div>
                            <h3 className="font-medium text-lg">{dashboard.name}</h3>
                            <p className="text-sm text-muted-foreground">{dashboard.description}</p>
                          </div>
                          <div className="flex gap-2">
                            {dashboard.isDefault && (
                              <Badge className="bg-blue-500">Default</Badge>
                            )}
                            <Badge variant="outline">
                              {dashboard.widgets.length} widgets
                            </Badge>
                          </div>
                        </div>
                        <div className="flex justify-between items-center text-xs text-muted-foreground">
                          <span>Created by {dashboard.createdBy}</span>
                          <span>Modified {new Date(dashboard.lastModified).toLocaleDateString()}</span>
                        </div>
                        <div className="flex gap-2 mt-3">
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
                          <Button size="sm" variant="outline">
                            <Share className="w-4 h-4 mr-1" />
                            Share
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Quick Insights */}
            <Card>
              <CardHeader>
                <CardTitle>Quick Insights</CardTitle>
                <CardDescription>Real-time BCM metrics</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="border rounded p-3">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium">BCM Maturity</span>
                      <TrendingUp className="w-4 h-4 text-green-500" />
                    </div>
                    <div className="text-2xl font-bold text-green-600">78%</div>
                    <Progress value={78} className="mt-2" />
                    <div className="text-xs text-muted-foreground mt-1">
                      +5% from last quarter
                    </div>
                  </div>

                  <div className="border rounded p-3">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium">Plan Effectiveness</span>
                      <Target className="w-4 h-4 text-blue-500" />
                    </div>
                    <div className="text-2xl font-bold text-blue-600">85%</div>
                    <Progress value={85} className="mt-2" />
                    <div className="text-xs text-muted-foreground mt-1">
                      Based on recent tests
                    </div>
                  </div>

                  <div className="border rounded p-3">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium">Compliance Score</span>
                      <Shield className="w-4 h-4 text-purple-500" />
                    </div>
                    <div className="text-2xl font-bold text-purple-600">92%</div>
                    <Progress value={92} className="mt-2" />
                    <div className="text-xs text-muted-foreground mt-1">
                      ISO 22301 assessment
                    </div>
                  </div>

                  <div className="border rounded p-3">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium">Incident Response</span>
                      <Zap className="w-4 h-4 text-yellow-500" />
                    </div>
                    <div className="text-2xl font-bold text-yellow-600">4.2h</div>
                    <div className="text-xs text-muted-foreground mt-1">
                      Average resolution time
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="reports" className="mt-6">
          <Card>
            <CardHeader>
              <div className="flex justify-between items-center">
                <div>
                  <CardTitle>Report Library</CardTitle>
                  <CardDescription>Generated and scheduled reports</CardDescription>
                </div>
                <div className="flex gap-2">
                  <div className="relative">
                    <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                    <Input
                      placeholder="Search reports..."
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
                      <SelectItem value="dashboard">Dashboard</SelectItem>
                      <SelectItem value="compliance">Compliance</SelectItem>
                      <SelectItem value="incident">Incident</SelectItem>
                      <SelectItem value="plan">Plan</SelectItem>
                      <SelectItem value="risk">Risk</SelectItem>
                      <SelectItem value="kpi">KPI</SelectItem>
                      <SelectItem value="executive">Executive</SelectItem>
                      <SelectItem value="regulatory">Regulatory</SelectItem>
                    </SelectContent>
                  </Select>
                  <Select value={filterStatus} onValueChange={setFilterStatus}>
                    <SelectTrigger className="w-32">
                      <SelectValue placeholder="Status" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Status</SelectItem>
                      <SelectItem value="completed">Completed</SelectItem>
                      <SelectItem value="generating">Generating</SelectItem>
                      <SelectItem value="scheduled">Scheduled</SelectItem>
                      <SelectItem value="failed">Failed</SelectItem>
                      <SelectItem value="draft">Draft</SelectItem>
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
                      <th className="text-left p-3 font-medium">Report Name</th>
                      <th className="text-left p-3 font-medium">Type</th>
                      <th className="text-left p-3 font-medium">Status</th>
                      <th className="text-left p-3 font-medium">Format</th>
                      <th className="text-left p-3 font-medium">Last Generated</th>
                      <th className="text-left p-3 font-medium">Size</th>
                      <th className="text-left p-3 font-medium">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredReports.map((report: Report) => (
                      <tr key={report.id} className="border-b hover:bg-accent">
                        <td className="p-3">
                          <div>
                            <div className="font-medium">{report.name}</div>
                            <div className="text-xs text-muted-foreground">
                              {report.id} • {report.category}
                            </div>
                          </div>
                        </td>
                        <td className="p-3 capitalize">{report.type.replace('_', ' ')}</td>
                        <td className="p-3">
                          <Badge className={getStatusColor(report.status)}>
                            {report.status}
                          </Badge>
                        </td>
                        <td className="p-3 uppercase">{report.format}</td>
                        <td className="p-3 text-sm">
                          {report.lastGenerated ? new Date(report.lastGenerated).toLocaleString() : 'Never'}
                        </td>
                        <td className="p-3 text-sm">{formatFileSize(report.size)}</td>
                        <td className="p-3">
                          <div className="flex gap-1">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => setSelectedReport(report)}
                            >
                              <Eye className="w-4 h-4" />
                            </Button>
                            {report.downloadUrl && (
                              <Button variant="ghost" size="sm">
                                <Download className="w-4 h-4" />
                              </Button>
                            )}
                            <Button variant="ghost" size="sm">
                              <Copy className="w-4 h-4" />
                            </Button>
                            <Button variant="ghost" size="sm">
                              <Mail className="w-4 h-4" />
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

        <TabsContent value="analytics" className="mt-6">
          <div className="grid grid-cols-2 gap-6">
            {/* Report Generation Trends */}
            <Card>
              <CardHeader>
                <CardTitle>Report Generation Trends</CardTitle>
                <CardDescription>Monthly report activity</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="grid grid-cols-3 gap-4 text-center">
                    <div className="border rounded p-3">
                      <div className="text-2xl font-bold text-blue-600">45</div>
                      <div className="text-xs text-muted-foreground">This Month</div>
                    </div>
                    <div className="border rounded p-3">
                      <div className="text-2xl font-bold text-green-600">38</div>
                      <div className="text-xs text-muted-foreground">Last Month</div>
                    </div>
                    <div className="border rounded p-3">
                      <div className="text-2xl font-bold text-purple-600">+18%</div>
                      <div className="text-xs text-muted-foreground">Growth</div>
                    </div>
                  </div>
                  <Separator />
                  <div>
                    <h4 className="text-sm font-medium mb-2">Popular Report Types</h4>
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-sm">Dashboard Summary</span>
                        <div className="flex items-center gap-2">
                          <Progress value={75} className="w-20" />
                          <span className="text-xs">75%</span>
                        </div>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm">Compliance Reports</span>
                        <div className="flex items-center gap-2">
                          <Progress value={60} className="w-20" />
                          <span className="text-xs">60%</span>
                        </div>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm">Incident Analysis</span>
                        <div className="flex items-center gap-2">
                          <Progress value={45} className="w-20" />
                          <span className="text-xs">45%</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* User Engagement */}
            <Card>
              <CardHeader>
                <CardTitle>User Engagement</CardTitle>
                <CardDescription>Report usage and interaction metrics</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-green-600">156</div>
                      <div className="text-xs text-muted-foreground">Total Downloads</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-blue-600">23</div>
                      <div className="text-xs text-muted-foreground">Active Users</div>
                    </div>
                  </div>
                  <Separator />
                  <div>
                    <h4 className="text-sm font-medium mb-2">Most Active Users</h4>
                    <div className="space-y-2">
                      <div className="flex justify-between items-center">
                        <span className="text-sm">BCM Manager</span>
                        <Badge variant="outline">12 reports</Badge>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm">Operations Manager</span>
                        <Badge variant="outline">8 reports</Badge>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm">Compliance Officer</span>
                        <Badge variant="outline">6 reports</Badge>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm">CEO</span>
                        <Badge variant="outline">4 reports</Badge>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="templates" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Report Templates</CardTitle>
              <CardDescription>Pre-configured report formats and layouts</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-3 gap-4">
                {templates.map((template: ReportTemplate) => (
                  <div key={template.id} className="border rounded-lg p-4">
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <h3 className="font-medium">{template.name}</h3>
                        <p className="text-sm text-muted-foreground">{template.description}</p>
                      </div>
                      {template.isBuiltIn && (
                        <Badge variant="outline">Built-in</Badge>
                      )}
                    </div>
                    <div className="text-xs text-muted-foreground mb-3">
                      {template.sections.length} sections • {template.parameters.length} parameters
                    </div>
                    <div className="flex gap-2">
                      <Button size="sm">
                        <FileText className="w-4 h-4 mr-1" />
                        Use Template
                      </Button>
                      <Button size="sm" variant="outline">
                        <Eye className="w-4 h-4 mr-1" />
                        Preview
                      </Button>
                      {!template.isBuiltIn && (
                        <Button size="sm" variant="outline">
                          <Edit className="w-4 h-4 mr-1" />
                          Edit
                        </Button>
                      )}
                    </div>
                    {template.lastUsed && (
                      <div className="text-xs text-muted-foreground mt-2">
                        Last used: {new Date(template.lastUsed).toLocaleDateString()}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="schedule" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Scheduled Reports</CardTitle>
              <CardDescription>Automated report generation and distribution</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {reports
                  .filter((r: Report) => r.frequency !== 'on_demand')
                  .map((report: Report) => (
                    <div key={report.id} className="border rounded-lg p-4">
                      <div className="flex justify-between items-start">
                        <div>
                          <h3 className="font-medium">{report.name}</h3>
                          <div className="text-sm text-muted-foreground">
                            {report.type.replace('_', ' ')} • {report.format.toUpperCase()}
                          </div>
                          <div className="text-xs text-muted-foreground mt-1">
                            Recipients: {report.recipients.join(', ')}
                          </div>
                        </div>
                        <div className="text-right">
                          <Badge className="capitalize">{report.frequency}</Badge>
                          {report.nextScheduled && (
                            <div className="text-xs text-muted-foreground mt-1">
                              Next: {new Date(report.nextScheduled).toLocaleDateString()}
                            </div>
                          )}
                        </div>
                      </div>
                      <div className="flex gap-2 mt-3">
                        <Button size="sm" variant="outline">
                          <Settings className="w-4 h-4 mr-1" />
                          Configure
                        </Button>
                        <Button size="sm" variant="outline">
                          <Pause className="w-4 h-4 mr-1" />
                          Pause
                        </Button>
                        <Button size="sm" variant="outline">
                          <Zap className="w-4 h-4 mr-1" />
                          Run Now
                        </Button>
                      </div>
                    </div>
                  ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Selected Report Detail Modal */}
      {selectedReport && (
        <Dialog open={!!selectedReport} onOpenChange={() => setSelectedReport(null)}>
          <DialogContent className="max-w-3xl max-h-[80vh] overflow-y-auto">
            <DialogHeader>
              <div className="flex justify-between items-start">
                <div>
                  <DialogTitle className="text-xl">{selectedReport.name}</DialogTitle>
                  <DialogDescription>
                    {selectedReport.id} • {selectedReport.type.replace('_', ' ')} • {selectedReport.format.toUpperCase()}
                  </DialogDescription>
                </div>
                <Badge className={getStatusColor(selectedReport.status)}>
                  {selectedReport.status}
                </Badge>
              </div>
            </DialogHeader>
            <div className="space-y-6 mt-6">
              {/* Report Details */}
              <div>
                <h3 className="font-medium mb-2">Report Information</h3>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-muted-foreground">Created by:</span>
                    <span className="ml-2">{selectedReport.createdBy}</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Category:</span>
                    <span className="ml-2 capitalize">{selectedReport.category}</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Frequency:</span>
                    <span className="ml-2 capitalize">{selectedReport.frequency.replace('_', ' ')}</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">File size:</span>
                    <span className="ml-2">{formatFileSize(selectedReport.size)}</span>
                  </div>
                  {selectedReport.lastGenerated && (
                    <div>
                      <span className="text-muted-foreground">Last generated:</span>
                      <span className="ml-2">{new Date(selectedReport.lastGenerated).toLocaleString()}</span>
                    </div>
                  )}
                  {selectedReport.nextScheduled && (
                    <div>
                      <span className="text-muted-foreground">Next scheduled:</span>
                      <span className="ml-2">{new Date(selectedReport.nextScheduled).toLocaleString()}</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Recipients */}
              <div>
                <h3 className="font-medium mb-2">Recipients</h3>
                <div className="flex flex-wrap gap-2">
                  {selectedReport.recipients.map((recipient) => (
                    <Badge key={recipient} variant="secondary">{recipient}</Badge>
                  ))}
                </div>
              </div>

              {/* Metrics */}
              {selectedReport.metrics.length > 0 && (
                <div>
                  <h3 className="font-medium mb-2">Key Metrics</h3>
                  <div className="grid grid-cols-2 gap-3">
                    {selectedReport.metrics.map((metric) => (
                      <div key={metric.id} className="border rounded p-2">
                        <div className="font-medium text-sm">{metric.name}</div>
                        <div className="flex items-center gap-2">
                          <span className="text-lg font-bold">{metric.value}</span>
                          <span className="text-xs">{metric.unit}</span>
                          {metric.target && (
                            <span className="text-xs text-muted-foreground">
                              / {metric.target} target
                            </span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Sections */}
              {selectedReport.sections.length > 0 && (
                <div>
                  <h3 className="font-medium mb-2">Report Sections</h3>
                  <div className="space-y-2">
                    {selectedReport.sections
                      .sort((a, b) => a.order - b.order)
                      .map((section) => (
                        <div key={section.id} className="border rounded p-2">
                          <div className="flex items-center gap-2">
                            <Badge variant="outline">{section.order}</Badge>
                            <span className="font-medium text-sm">{section.title}</span>
                            <Badge variant="secondary" className="text-xs">{section.type}</Badge>
                          </div>
                        </div>
                      ))}
                  </div>
                </div>
              )}

              <div className="flex justify-end gap-2 pt-4 border-t">
                {selectedReport.downloadUrl && (
                  <Button variant="outline">
                    <Download className="w-4 h-4 mr-2" />
                    Download
                  </Button>
                )}
                <Button variant="outline">
                  <Copy className="w-4 h-4 mr-2" />
                  Clone
                </Button>
                <Button variant="outline">
                  <Mail className="w-4 h-4 mr-2" />
                  Email
                </Button>
                <Button>
                  <RefreshCw className="w-4 h-4 mr-2" />
                  Regenerate
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      )}
    </div>
  )
}