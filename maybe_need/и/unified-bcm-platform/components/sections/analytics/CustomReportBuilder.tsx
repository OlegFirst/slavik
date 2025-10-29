import React, { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  FileText,
  Download,
  Play,
  Settings,
  Calendar,
  Filter,
  BarChart3,
  PieChart,
  TrendingUp,
  Clock,
  Plus
} from 'lucide-react'

interface ReportTemplate {
  id: string
  name: string
  description: string
  category: 'executive' | 'operational' | 'compliance' | 'audit'
  frequency: 'daily' | 'weekly' | 'monthly' | 'quarterly' | 'on-demand'
  lastGenerated?: string
  status: 'active' | 'draft' | 'archived'
  format: 'pdf' | 'excel' | 'dashboard'
  recipients: string[]
}

interface CustomReport {
  id: string
  name: string
  createdBy: string
  createdDate: string
  status: 'generating' | 'completed' | 'failed'
  size: string
  format: 'pdf' | 'excel' | 'csv'
}

export function CustomReportBuilder() {
  const [activeTab, setActiveTab] = useState('templates')

  const reportTemplates: ReportTemplate[] = [
    {
      id: 'executive-summary',
      name: 'Executive BCM Summary',
      description: 'High-level BCM performance and strategic overview for C-level executives',
      category: 'executive',
      frequency: 'monthly',
      lastGenerated: '2024-01-15',
      status: 'active',
      format: 'pdf',
      recipients: ['ceo@company.com', 'coo@company.com']
    },
    {
      id: 'incident-analysis',
      name: 'Incident Response Analysis',
      description: 'Detailed analysis of incident response performance and lessons learned',
      category: 'operational',
      frequency: 'weekly',
      lastGenerated: '2024-01-20',
      status: 'active',
      format: 'dashboard',
      recipients: ['incident-team@company.com']
    },
    {
      id: 'risk-assessment-report',
      name: 'Risk Assessment Report',
      description: 'Comprehensive risk analysis with mitigation recommendations',
      category: 'operational',
      frequency: 'monthly',
      lastGenerated: '2024-01-10',
      status: 'active',
      format: 'pdf',
      recipients: ['risk-team@company.com', 'management@company.com']
    },
    {
      id: 'compliance-status',
      name: 'BCM Compliance Status Report',
      description: 'Regulatory compliance status and audit readiness assessment',
      category: 'compliance',
      frequency: 'quarterly',
      lastGenerated: '2024-01-01',
      status: 'active',
      format: 'excel',
      recipients: ['compliance@company.com', 'audit@company.com']
    },
    {
      id: 'training-metrics',
      name: 'Training & Awareness Metrics',
      description: 'BCM training completion rates and competency assessments',
      category: 'operational',
      frequency: 'monthly',
      lastGenerated: '2024-01-18',
      status: 'active',
      format: 'dashboard',
      recipients: ['hr@company.com', 'training@company.com']
    },
    {
      id: 'audit-readiness',
      name: 'Audit Readiness Assessment',
      description: 'Comprehensive audit preparation and compliance verification',
      category: 'audit',
      frequency: 'on-demand',
      status: 'draft',
      format: 'pdf',
      recipients: ['audit@company.com']
    }
  ]

  const recentReports: CustomReport[] = [
    {
      id: '1',
      name: 'Executive BCM Summary - January 2024',
      createdBy: 'System',
      createdDate: '2024-01-20T09:00:00Z',
      status: 'completed',
      size: '2.3 MB',
      format: 'pdf'
    },
    {
      id: '2',
      name: 'Weekly Incident Analysis - W3 2024',
      createdBy: 'John Smith',
      createdDate: '2024-01-19T15:30:00Z',
      status: 'completed',
      size: '1.8 MB',
      format: 'excel'
    },
    {
      id: '3',
      name: 'Custom Risk Analysis - Supply Chain',
      createdBy: 'Sarah Johnson',
      createdDate: '2024-01-19T11:15:00Z',
      status: 'generating',
      size: '-',
      format: 'pdf'
    },
    {
      id: '4',
      name: 'Q4 2023 Compliance Report',
      createdBy: 'System',
      createdDate: '2024-01-18T08:00:00Z',
      status: 'completed',
      size: '5.1 MB',
      format: 'excel'
    }
  ]

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'executive': return 'default'
      case 'operational': return 'secondary'
      case 'compliance': return 'outline'
      case 'audit': return 'destructive'
      default: return 'outline'
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'default'
      case 'draft': return 'secondary'
      case 'archived': return 'outline'
      case 'completed': return 'default'
      case 'generating': return 'secondary'
      case 'failed': return 'destructive'
      default: return 'outline'
    }
  }

  const getFormatIcon = (format: string) => {
    switch (format) {
      case 'pdf': return FileText
      case 'excel': return BarChart3
      case 'csv': return FileText
      case 'dashboard': return PieChart
      default: return FileText
    }
  }

  const generateReport = (templateId: string) => {
    console.log(`Generating report from template: ${templateId}`)
    // In real implementation, this would trigger report generation
  }

  const downloadReport = (reportId: string) => {
    console.log(`Downloading report: ${reportId}`)
    // In real implementation, this would download the report
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <FileText className="h-6 w-6 text-green-600" />
            Custom Report Builder
          </h2>
          <p className="text-gray-600 mt-1">
            Create, schedule, and manage custom BCM reports and analytics
          </p>
        </div>
        <Button className="flex items-center gap-2">
          <Plus className="h-4 w-4" />
          Create Custom Report
        </Button>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="templates">Report Templates</TabsTrigger>
          <TabsTrigger value="recent">Recent Reports</TabsTrigger>
          <TabsTrigger value="builder">Report Builder</TabsTrigger>
          <TabsTrigger value="scheduled">Scheduled Reports</TabsTrigger>
        </TabsList>

        <TabsContent value="templates">
          <div className="grid gap-4">
            {reportTemplates.map((template) => {
              const FormatIcon = getFormatIcon(template.format)
              
              return (
                <Card key={template.id}>
                  <CardHeader className="pb-3">
                    <div className="flex items-start justify-between">
                      <div className="space-y-2">
                        <div className="flex items-center gap-2">
                          <CardTitle className="text-lg">{template.name}</CardTitle>
                          <Badge variant={getCategoryColor(template.category)}>
                            {template.category}
                          </Badge>
                          <Badge variant={getStatusColor(template.status)}>
                            {template.status}
                          </Badge>
                        </div>
                        <CardDescription>{template.description}</CardDescription>
                        <div className="flex items-center gap-4 text-sm text-gray-500">
                          <div className="flex items-center gap-1">
                            <Calendar className="h-3 w-3" />
                            {template.frequency}
                          </div>
                          <div className="flex items-center gap-1">
                            <FormatIcon className="h-3 w-3" />
                            {template.format.toUpperCase()}
                          </div>
                          {template.lastGenerated && (
                            <div className="flex items-center gap-1">
                              <Clock className="h-3 w-3" />
                              Last: {new Date(template.lastGenerated).toLocaleDateString()}
                            </div>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => generateReport(template.id)}
                          className="flex items-center gap-1"
                        >
                          <Play className="h-3 w-3" />
                          Generate
                        </Button>
                        <Button size="sm" variant="ghost">
                          <Settings className="h-3 w-3" />
                        </Button>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      <div className="text-sm font-medium">Recipients:</div>
                      <div className="flex flex-wrap gap-1">
                        {template.recipients.map((recipient, index) => (
                          <Badge key={index} variant="outline" className="text-xs">
                            {recipient}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )
            })}
          </div>
        </TabsContent>

        <TabsContent value="recent">
          <div className="space-y-4">
            {recentReports.map((report) => {
              const FormatIcon = getFormatIcon(report.format)
              
              return (
                <Card key={report.id}>
                  <CardContent className="pt-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-start gap-3">
                        <FormatIcon className="h-8 w-8 text-blue-600 mt-1" />
                        <div className="space-y-1">
                          <h3 className="font-medium">{report.name}</h3>
                          <div className="flex items-center gap-4 text-sm text-gray-500">
                            <span>Created by {report.createdBy}</span>
                            <span>{new Date(report.createdDate).toLocaleDateString()}</span>
                            <span>{report.size}</span>
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge variant={getStatusColor(report.status)}>
                          {report.status}
                        </Badge>
                        {report.status === 'completed' && (
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => downloadReport(report.id)}
                            className="flex items-center gap-1"
                          >
                            <Download className="h-3 w-3" />
                            Download
                          </Button>
                        )}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )
            })}
          </div>
        </TabsContent>

        <TabsContent value="builder">
          <Card>
            <CardHeader>
              <CardTitle>Custom Report Builder</CardTitle>
              <CardDescription>
                Build custom reports with drag-and-drop components and flexible filtering
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-6 md:grid-cols-2">
                <div>
                  <h4 className="font-medium mb-3">Available Components</h4>
                  <div className="space-y-2">
                    <div className="p-3 border rounded-lg bg-blue-50 hover:bg-blue-100 cursor-pointer">
                      <div className="flex items-center gap-2">
                        <BarChart3 className="h-4 w-4 text-blue-600" />
                        <span className="font-medium">KPI Metrics</span>
                      </div>
                      <p className="text-xs text-gray-600 mt-1">
                        Key performance indicators and metrics
                      </p>
                    </div>
                    <div className="p-3 border rounded-lg bg-green-50 hover:bg-green-100 cursor-pointer">
                      <div className="flex items-center gap-2">
                        <TrendingUp className="h-4 w-4 text-green-600" />
                        <span className="font-medium">Trend Analysis</span>
                      </div>
                      <p className="text-xs text-gray-600 mt-1">
                        Historical trends and forecasting
                      </p>
                    </div>
                    <div className="p-3 border rounded-lg bg-purple-50 hover:bg-purple-100 cursor-pointer">
                      <div className="flex items-center gap-2">
                        <PieChart className="h-4 w-4 text-purple-600" />
                        <span className="font-medium">Risk Matrix</span>
                      </div>
                      <p className="text-xs text-gray-600 mt-1">
                        Risk assessments and heat maps
                      </p>
                    </div>
                    <div className="p-3 border rounded-lg bg-orange-50 hover:bg-orange-100 cursor-pointer">
                      <div className="flex items-center gap-2">
                        <Clock className="h-4 w-4 text-orange-600" />
                        <span className="font-medium">Incident Timeline</span>
                      </div>
                      <p className="text-xs text-gray-600 mt-1">
                        Incident response timelines
                      </p>
                    </div>
                  </div>
                </div>
                <div>
                  <h4 className="font-medium mb-3">Report Canvas</h4>
                  <div className="border-2 border-dashed border-gray-300 rounded-lg h-64 flex items-center justify-center">
                    <div className="text-center text-gray-500">
                      <FileText className="h-8 w-8 mx-auto mb-2" />
                      <p>Drag components here to build your report</p>
                      <Button variant="outline" size="sm" className="mt-2">
                        Start Building
                      </Button>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="scheduled">
          <div className="grid gap-4">
            {reportTemplates.filter(t => t.status === 'active').map((template) => (
              <Card key={template.id}>
                <CardContent className="pt-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <Calendar className="h-6 w-6 text-blue-600" />
                      <div>
                        <h3 className="font-medium">{template.name}</h3>
                        <div className="text-sm text-gray-500">
                          Scheduled {template.frequency} • Next: {
                            new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toLocaleDateString()
                          }
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge variant="default">Active</Badge>
                      <Button size="sm" variant="outline">
                        <Settings className="h-3 w-3 mr-1" />
                        Modify
                      </Button>
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
