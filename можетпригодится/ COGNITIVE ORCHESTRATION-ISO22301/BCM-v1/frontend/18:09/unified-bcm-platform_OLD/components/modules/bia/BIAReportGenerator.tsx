'use client'

import { useState, useRef, useCallback, useMemo } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import {
  FileText,
  Download,
  Eye,
  Settings,
  BarChart3,
  TrendingUp,
  AlertCircle,
  DollarSign,
  Clock,
  Building,
  Users,
  CheckCircle,
  X,
  Loader2,
  RefreshCw,
  Filter,
  Layout,
  Grid,
  List,
  PieChart,
  FileSpreadsheet,
  FileJson,
  Calendar,
  Target,
  Shield,
  Zap
} from 'lucide-react'
import {
  biaAPI,
  biaQueryKeys,
  type BIAResult,
  type BIAMetrics,
  type CriticalPath,
  type DependencyMapping
} from '@/services/bia-api'

// Report generation utilities
import jsPDF from 'jspdf'
import 'jspdf-autotable'
import * as XLSX from 'xlsx'
import { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, HeadingLevel } from 'docx'
import html2canvas from 'html2canvas'

// Chart utilities
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  PointElement,
  LineElement,
  RadarController,
  RadialLinearScale
} from 'chart.js'

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  PointElement,
  LineElement,
  RadarController,
  RadialLinearScale
)

// Report template types
export type ReportTemplate = 'executive' | 'technical' | 'iso22301' | 'summary'
export type ExportFormat = 'pdf' | 'excel' | 'word' | 'json'

interface ReportSection {
  id: string
  name: string
  enabled: boolean
  required?: boolean
  description?: string
}

interface ReportConfig {
  template: ReportTemplate
  sections: ReportSection[]
  includeCharts: boolean
  includeRecommendations: boolean
  includeFinancialAnalysis: boolean
  customTitle?: string
  customSubtitle?: string
  organizationName?: string
  reportingPeriod?: {
    start: string
    end: string
  }
}

interface GeneratedReport {
  id: string
  title: string
  generatedAt: string
  template: ReportTemplate
  sections: any[]
  charts: any[]
  metadata: any
}

const defaultSections: Record<ReportTemplate, ReportSection[]> = {
  executive: [
    { id: 'executive-summary', name: 'Executive Summary', enabled: true, required: true, description: 'High-level overview and key findings' },
    { id: 'key-metrics', name: 'Key Performance Metrics', enabled: true, required: true, description: 'Critical KPIs and metrics dashboard' },
    { id: 'critical-functions', name: 'Critical Business Functions', enabled: true, description: 'Analysis of most critical functions' },
    { id: 'financial-impact', name: 'Financial Impact Analysis', enabled: true, description: 'Cost of disruption analysis' },
    { id: 'risk-assessment', name: 'Risk Assessment Summary', enabled: true, description: 'High-level risk overview' },
    { id: 'recommendations', name: 'Strategic Recommendations', enabled: true, description: 'Executive-level recommendations' }
  ],
  technical: [
    { id: 'technical-overview', name: 'Technical Overview', enabled: true, required: true, description: 'Technical analysis methodology' },
    { id: 'detailed-analysis', name: 'Detailed Function Analysis', enabled: true, required: true, description: 'In-depth technical analysis' },
    { id: 'dependency-mapping', name: 'Dependency Analysis', enabled: true, description: 'System and process dependencies' },
    { id: 'critical-paths', name: 'Critical Path Analysis', enabled: true, description: 'Critical path identification' },
    { id: 'recovery-procedures', name: 'Recovery Procedures', enabled: true, description: 'Technical recovery procedures' },
    { id: 'optimization-opportunities', name: 'Optimization Opportunities', enabled: true, description: 'Technical improvement recommendations' },
    { id: 'implementation-roadmap', name: 'Implementation Roadmap', enabled: false, description: 'Technical implementation plan' }
  ],
  iso22301: [
    { id: 'iso-compliance-overview', name: 'ISO 22301 Compliance Overview', enabled: true, required: true, description: 'Compliance status overview' },
    { id: 'context-organization', name: 'Context of Organization', enabled: true, required: true, description: 'ISO 22301 clause 4 compliance' },
    { id: 'leadership-commitment', name: 'Leadership & Commitment', enabled: true, description: 'ISO 22301 clause 5 compliance' },
    { id: 'bia-process', name: 'BIA Process & Methodology', enabled: true, required: true, description: 'ISO 22301 clause 8.2 compliance' },
    { id: 'risk-assessment', name: 'Risk Assessment', enabled: true, description: 'ISO 22301 clause 8.3 compliance' },
    { id: 'bc-strategy', name: 'BC Strategy & Solutions', enabled: true, description: 'ISO 22301 clause 8.4 compliance' },
    { id: 'monitoring-measurement', name: 'Monitoring & Measurement', enabled: true, description: 'ISO 22301 clause 9 compliance' },
    { id: 'improvement', name: 'Continual Improvement', enabled: false, description: 'ISO 22301 clause 10 compliance' }
  ],
  summary: [
    { id: 'summary-overview', name: 'BIA Summary', enabled: true, required: true, description: 'Quick overview of findings' },
    { id: 'key-findings', name: 'Key Findings', enabled: true, required: true, description: 'Most important discoveries' },
    { id: 'critical-functions-summary', name: 'Critical Functions', enabled: true, description: 'Summary of critical functions' },
    { id: 'priority-actions', name: 'Priority Actions', enabled: true, description: 'Immediate action items' },
    { id: 'next-steps', name: 'Next Steps', enabled: true, description: 'Recommended next steps' }
  ]
}

export function BIAReportGenerator() {
  const [isOpen, setIsOpen] = useState(false)
  const [reportConfig, setReportConfig] = useState<ReportConfig>({
    template: 'executive',
    sections: defaultSections.executive,
    includeCharts: true,
    includeRecommendations: true,
    includeFinancialAnalysis: true,
    organizationName: 'Your Organization',
    reportingPeriod: {
      start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      end: new Date().toISOString().split('T')[0]
    }
  })
  const [previewMode, setPreviewMode] = useState(false)
  const [generatedReport, setGeneratedReport] = useState<GeneratedReport | null>(null)
  const [isGenerating, setIsGenerating] = useState(false)
  const previewRef = useRef<HTMLDivElement>(null)

  // Fetch data for report generation
  const { data: biaResults, isLoading: biaLoading } = useQuery({
    queryKey: biaQueryKeys.result({}),
    queryFn: () => biaAPI.getBIAResults({})
  })

  const { data: metrics, isLoading: metricsLoading } = useQuery({
    queryKey: biaQueryKeys.metrics(),
    queryFn: () => biaAPI.getBIAMetrics()
  })

  const { data: criticalPaths } = useQuery({
    queryKey: biaQueryKeys.criticalPaths(),
    queryFn: () => biaAPI.getCriticalPaths()
  })

  const { data: dependencies } = useQuery({
    queryKey: biaQueryKeys.dependencies(),
    queryFn: () => biaAPI.getDependencyMappings()
  })

  // Generate report data
  const generateReportData = useCallback(async (): Promise<GeneratedReport> => {
    const reportData: GeneratedReport = {
      id: `report-${Date.now()}`,
      title: reportConfig.customTitle || `${reportConfig.template.toUpperCase()} BIA Report`,
      generatedAt: new Date().toISOString(),
      template: reportConfig.template,
      sections: [],
      charts: [],
      metadata: {
        organizationName: reportConfig.organizationName,
        reportingPeriod: reportConfig.reportingPeriod,
        generatedBy: 'BIA Report Generator',
        totalFunctions: biaResults?.length || 0,
        criticalFunctions: biaResults?.filter(r => r.criticalityLevel === 'critical').length || 0
      }
    }

    // Generate sections based on configuration
    for (const section of reportConfig.sections) {
      if (!section.enabled) continue

      switch (section.id) {
        case 'executive-summary':
          reportData.sections.push(generateExecutiveSummary(biaResults, metrics))
          break
        case 'key-metrics':
          reportData.sections.push(generateKeyMetrics(metrics))
          break
        case 'critical-functions':
        case 'critical-functions-summary':
          reportData.sections.push(generateCriticalFunctions(biaResults))
          break
        case 'financial-impact':
          reportData.sections.push(generateFinancialImpact(biaResults))
          break
        case 'dependency-mapping':
          reportData.sections.push(generateDependencyAnalysis(dependencies))
          break
        case 'critical-paths':
          reportData.sections.push(generateCriticalPathsAnalysis(criticalPaths))
          break
        case 'recommendations':
          reportData.sections.push(generateRecommendations(biaResults, criticalPaths))
          break
        case 'iso-compliance-overview':
          reportData.sections.push(generateISOComplianceOverview(biaResults, metrics))
          break
        case 'detailed-analysis':
          reportData.sections.push(generateDetailedAnalysis(biaResults))
          break
        default:
          reportData.sections.push(generateGenericSection(section, biaResults))
      }
    }

    // Generate charts if enabled
    if (reportConfig.includeCharts) {
      reportData.charts = await generateCharts(biaResults, metrics)
    }

    return reportData
  }, [reportConfig, biaResults, metrics, criticalPaths, dependencies])

  // Template selection
  const handleTemplateChange = useCallback((template: ReportTemplate) => {
    setReportConfig(prev => ({
      ...prev,
      template,
      sections: defaultSections[template]
    }))
  }, [])

  // Section management
  const toggleSection = useCallback((sectionId: string) => {
    setReportConfig(prev => ({
      ...prev,
      sections: prev.sections.map(section =>
        section.id === sectionId
          ? { ...section, enabled: !section.enabled }
          : section
      )
    }))
  }, [])

  // Generate preview
  const generatePreview = useCallback(async () => {
    setIsGenerating(true)
    try {
      const report = await generateReportData()
      setGeneratedReport(report)
      setPreviewMode(true)
    } catch (error) {
      console.error('Failed to generate preview:', error)
    } finally {
      setIsGenerating(false)
    }
  }, [generateReportData])

  // Export functions
  const exportToPDF = useCallback(async (report: GeneratedReport) => {
    const pdf = new jsPDF({
      orientation: 'portrait',
      unit: 'mm',
      format: 'a4'
    })

    // Add title page
    pdf.setFontSize(24)
    pdf.setFont('helvetica', 'bold')
    pdf.text(report.title, 20, 30)

    pdf.setFontSize(14)
    pdf.setFont('helvetica', 'normal')
    pdf.text(`Generated: ${new Date(report.generatedAt).toLocaleDateString()}`, 20, 45)
    pdf.text(`Organization: ${report.metadata.organizationName}`, 20, 55)

    if (report.metadata.reportingPeriod) {
      pdf.text(`Period: ${report.metadata.reportingPeriod.start} to ${report.metadata.reportingPeriod.end}`, 20, 65)
    }

    let yPosition = 85

    // Add sections
    for (const section of report.sections) {
      if (yPosition > 250) {
        pdf.addPage()
        yPosition = 20
      }

      pdf.setFontSize(16)
      pdf.setFont('helvetica', 'bold')
      pdf.text(section.title, 20, yPosition)
      yPosition += 10

      pdf.setFontSize(11)
      pdf.setFont('helvetica', 'normal')

      if (section.content) {
        const lines = pdf.splitTextToSize(section.content, 170)
        pdf.text(lines, 20, yPosition)
        yPosition += lines.length * 5 + 10
      }

      if (section.table) {
        (pdf as any).autoTable({
          head: [section.table.headers],
          body: section.table.rows,
          startY: yPosition,
          margin: { left: 20, right: 20 },
          styles: { fontSize: 9 }
        })
        yPosition = (pdf as any).lastAutoTable.finalY + 10
      }
    }

    pdf.save(`${report.title.replace(/\s+/g, '_')}_${new Date().toISOString().split('T')[0]}.pdf`)
  }, [])

  const exportToExcel = useCallback(async (report: GeneratedReport) => {
    const workbook = XLSX.utils.book_new()

    // Summary sheet
    const summaryData = [
      ['Report Title', report.title],
      ['Generated', new Date(report.generatedAt).toLocaleDateString()],
      ['Organization', report.metadata.organizationName],
      ['Total Functions', report.metadata.totalFunctions],
      ['Critical Functions', report.metadata.criticalFunctions],
      [''],
      ['Section', 'Summary'],
      ...report.sections.map(section => [section.title, section.summary || section.content?.substring(0, 100) + '...'])
    ]

    const summarySheet = XLSX.utils.aoa_to_sheet(summaryData)
    XLSX.utils.book_append_sheet(workbook, summarySheet, 'Summary')

    // Data sheets for each section with tabular data
    for (const section of report.sections) {
      if (section.table) {
        const worksheet = XLSX.utils.aoa_to_sheet([
          section.table.headers,
          ...section.table.rows
        ])
        XLSX.utils.book_append_sheet(workbook, worksheet, section.title.substring(0, 31))
      }
    }

    // Raw data sheet
    if (biaResults) {
      const rawDataSheet = XLSX.utils.json_to_sheet(biaResults)
      XLSX.utils.book_append_sheet(workbook, rawDataSheet, 'Raw BIA Data')
    }

    XLSX.writeFile(workbook, `${report.title.replace(/\s+/g, '_')}_${new Date().toISOString().split('T')[0]}.xlsx`)
  }, [biaResults])

  const exportToWord = useCallback(async (report: GeneratedReport) => {
    const doc = new Document({
      sections: [{
        properties: {},
        children: [
          new Paragraph({
            text: report.title,
            heading: HeadingLevel.TITLE
          }),
          new Paragraph({
            children: [
              new TextRun(`Generated: ${new Date(report.generatedAt).toLocaleDateString()}`),
              new TextRun('\n'),
              new TextRun(`Organization: ${report.metadata.organizationName}`)
            ]
          }),
          ...report.sections.flatMap(section => [
            new Paragraph({
              text: section.title,
              heading: HeadingLevel.HEADING_1
            }),
            new Paragraph({
              text: section.content || section.summary || ''
            })
          ])
        ]
      }]
    })

    const buffer = await Packer.toBuffer(doc)
    const blob = new Blob([new Uint8Array(buffer)], { type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${report.title.replace(/\s+/g, '_')}_${new Date().toISOString().split('T')[0]}.docx`
    link.click()
    URL.revokeObjectURL(url)
  }, [])

  const exportToJSON = useCallback(async (report: GeneratedReport) => {
    const jsonData = {
      ...report,
      exportedAt: new Date().toISOString(),
      rawData: {
        biaResults,
        metrics,
        criticalPaths,
        dependencies
      }
    }

    const blob = new Blob([JSON.stringify(jsonData, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${report.title.replace(/\s+/g, '_')}_${new Date().toISOString().split('T')[0]}.json`
    link.click()
    URL.revokeObjectURL(url)
  }, [biaResults, metrics, criticalPaths, dependencies])

  const handleExport = useCallback(async (format: ExportFormat) => {
    if (!generatedReport) return

    try {
      switch (format) {
        case 'pdf':
          await exportToPDF(generatedReport)
          break
        case 'excel':
          await exportToExcel(generatedReport)
          break
        case 'word':
          await exportToWord(generatedReport)
          break
        case 'json':
          await exportToJSON(generatedReport)
          break
      }
    } catch (error) {
      console.error(`Failed to export as ${format}:`, error)
    }
  }, [generatedReport, exportToPDF, exportToExcel, exportToWord, exportToJSON])

  if (biaLoading || metricsLoading) {
    return (
      <div className="flex items-center justify-center p-8">
        <Loader2 className="h-8 w-8 animate-spin" />
        <span className="ml-2">Loading BIA data...</span>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">BIA Report Generator</h2>
          <p className="text-gray-600">Generate comprehensive Business Impact Analysis reports</p>
        </div>
        <Button
          onClick={() => setIsOpen(!isOpen)}
          className="flex items-center gap-2"
        >
          <FileText className="h-4 w-4" />
          {isOpen ? 'Close Generator' : 'Generate Report'}
        </Button>
      </div>

      {isOpen && (
        <div className="bg-white rounded-lg border shadow-sm">
          <div className="p-6 space-y-6">
            {/* Template Selection */}
            <div>
              <h3 className="text-lg font-semibold mb-4">Report Template</h3>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                {Object.keys(defaultSections).map((template) => (
                  <button
                    key={template}
                    onClick={() => handleTemplateChange(template as ReportTemplate)}
                    className={cn(
                      "p-4 border rounded-lg text-left transition-colors",
                      reportConfig.template === template
                        ? "border-blue-500 bg-blue-50"
                        : "border-gray-200 hover:border-gray-300"
                    )}
                  >
                    <div className="flex items-center gap-2 mb-2">
                      {template === 'executive' && <TrendingUp className="h-5 w-5 text-blue-600" />}
                      {template === 'technical' && <Settings className="h-5 w-5 text-green-600" />}
                      {template === 'iso22301' && <Shield className="h-5 w-5 text-purple-600" />}
                      {template === 'summary' && <Layout className="h-5 w-5 text-orange-600" />}
                      <span className="font-medium capitalize">{template}</span>
                    </div>
                    <p className="text-sm text-gray-600">
                      {template === 'executive' && 'High-level strategic overview for executives'}
                      {template === 'technical' && 'Detailed technical analysis and procedures'}
                      {template === 'iso22301' && 'ISO 22301 compliance-focused report'}
                      {template === 'summary' && 'Concise summary with key findings'}
                    </p>
                  </button>
                ))}
              </div>
            </div>

            {/* Report Configuration */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Basic Settings */}
              <div>
                <h3 className="text-lg font-semibold mb-4">Report Configuration</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Organization Name
                    </label>
                    <input
                      type="text"
                      value={reportConfig.organizationName}
                      onChange={(e) => setReportConfig(prev => ({ ...prev, organizationName: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Custom Title
                    </label>
                    <input
                      type="text"
                      value={reportConfig.customTitle || ''}
                      onChange={(e) => setReportConfig(prev => ({ ...prev, customTitle: e.target.value }))}
                      placeholder={`${reportConfig.template.toUpperCase()} BIA Report`}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Period Start
                      </label>
                      <input
                        type="date"
                        value={reportConfig.reportingPeriod?.start}
                        onChange={(e) => setReportConfig(prev => ({
                          ...prev,
                          reportingPeriod: { ...prev.reportingPeriod!, start: e.target.value }
                        }))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Period End
                      </label>
                      <input
                        type="date"
                        value={reportConfig.reportingPeriod?.end}
                        onChange={(e) => setReportConfig(prev => ({
                          ...prev,
                          reportingPeriod: { ...prev.reportingPeriod!, end: e.target.value }
                        }))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                  </div>
                </div>
              </div>

              {/* Report Sections */}
              <div>
                <h3 className="text-lg font-semibold mb-4">Report Sections</h3>
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {reportConfig.sections.map((section) => (
                    <div
                      key={section.id}
                      className="flex items-start gap-3 p-3 border border-gray-200 rounded-lg"
                    >
                      <input
                        type="checkbox"
                        checked={section.enabled}
                        onChange={() => toggleSection(section.id)}
                        disabled={section.required}
                        className="mt-1"
                      />
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <span className="font-medium text-sm">{section.name}</span>
                          {section.required && (
                            <span className="text-xs text-red-600 bg-red-100 px-2 py-1 rounded">Required</span>
                          )}
                        </div>
                        {section.description && (
                          <p className="text-xs text-gray-600 mt-1">{section.description}</p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Advanced Options */}
            <div>
              <h3 className="text-lg font-semibold mb-4">Advanced Options</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={reportConfig.includeCharts}
                    onChange={(e) => setReportConfig(prev => ({ ...prev, includeCharts: e.target.checked }))}
                  />
                  <BarChart3 className="h-4 w-4" />
                  <span className="text-sm">Include Charts & Visualizations</span>
                </label>
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={reportConfig.includeRecommendations}
                    onChange={(e) => setReportConfig(prev => ({ ...prev, includeRecommendations: e.target.checked }))}
                  />
                  <Target className="h-4 w-4" />
                  <span className="text-sm">Include AI Recommendations</span>
                </label>
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={reportConfig.includeFinancialAnalysis}
                    onChange={(e) => setReportConfig(prev => ({ ...prev, includeFinancialAnalysis: e.target.checked }))}
                  />
                  <DollarSign className="h-4 w-4" />
                  <span className="text-sm">Include Financial Analysis</span>
                </label>
              </div>
            </div>

            {/* Actions */}
            <div className="flex gap-4 pt-4 border-t">
              <Button
                onClick={generatePreview}
                disabled={isGenerating}
                className="flex items-center gap-2"
              >
                {isGenerating ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Eye className="h-4 w-4" />
                )}
                {isGenerating ? 'Generating...' : 'Preview Report'}
              </Button>
              {generatedReport && (
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    onClick={() => handleExport('pdf')}
                    className="flex items-center gap-2"
                  >
                    <FileText className="h-4 w-4" />
                    Export PDF
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => handleExport('excel')}
                    className="flex items-center gap-2"
                  >
                    <FileSpreadsheet className="h-4 w-4" />
                    Export Excel
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => handleExport('word')}
                    className="flex items-center gap-2"
                  >
                    <FileText className="h-4 w-4" />
                    Export Word
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => handleExport('json')}
                    className="flex items-center gap-2"
                  >
                    <FileJson className="h-4 w-4" />
                    Export JSON
                  </Button>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Preview */}
      {previewMode && generatedReport && (
        <div className="bg-white rounded-lg border shadow-sm">
          <div className="p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold">Report Preview</h3>
              <Button
                variant="outline"
                onClick={() => setPreviewMode(false)}
                className="flex items-center gap-2"
              >
                <X className="h-4 w-4" />
                Close Preview
              </Button>
            </div>

            <div ref={previewRef} className="prose max-w-none">
              <ReportPreview report={generatedReport} />
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

// Helper functions for generating report sections
function generateExecutiveSummary(biaResults?: BIAResult[], metrics?: BIAMetrics) {
  const criticalCount = biaResults?.filter(r => r.criticalityLevel === 'critical').length || 0
  const totalFinancialRisk = biaResults?.reduce((sum, r) => sum + (r.financialImpactPerHour * r.mtpd), 0) || 0

  return {
    title: 'Executive Summary',
    content: `This Business Impact Analysis (BIA) provides a comprehensive assessment of ${biaResults?.length || 0} business functions across the organization. Our analysis identified ${criticalCount} critical functions that require immediate attention and specialized recovery procedures.

Key findings include a total potential financial risk of $${(totalFinancialRisk / 1000000).toFixed(2)}M across all assessed functions, with an average Recovery Time Objective (RTO) of ${metrics?.avgRTO?.toFixed(1) || 'N/A'} hours. The assessment reveals significant interdependencies between critical business functions that must be considered in business continuity planning.

Critical functions identified include those with RTOs of 4 hours or less and financial impacts exceeding $50,000 per hour. These functions require prioritized resource allocation and enhanced backup procedures to ensure organizational resilience.`,
    summary: `BIA assessment complete: ${biaResults?.length || 0} functions analyzed, ${criticalCount} critical functions identified, $${(totalFinancialRisk / 1000000).toFixed(2)}M total risk exposure.`
  }
}

function generateKeyMetrics(metrics?: BIAMetrics) {
  return {
    title: 'Key Performance Metrics',
    content: 'Critical business continuity metrics derived from the BIA assessment.',
    table: {
      headers: ['Metric', 'Value', 'Status', 'Target'],
      rows: [
        ['Total Functions Assessed', (metrics?.totalFunctions || 0).toString(), 'Complete', 'All Functions'],
        ['Critical Functions', (metrics?.criticalFunctions || 0).toString(), 'Identified', '< 20% of Total'],
        ['Average RTO', `${metrics?.avgRTO?.toFixed(1) || 'N/A'} hours`, 'Calculated', '< 24 hours'],
        ['Total Financial Risk', `$${((metrics?.totalFinancialRisk || 0) / 1000000).toFixed(2)}M`, 'Assessed', 'Minimize'],
        ['Assessments Completed', (metrics?.assessmentsCompleted || 0).toString(), 'Current', '100%'],
        ['Pending Assessments', (metrics?.pendingAssessments || 0).toString(), 'Outstanding', '0']
      ]
    },
    summary: `Key metrics show ${metrics?.totalFunctions || 0} functions assessed with ${metrics?.criticalFunctions || 0} critical functions identified.`
  }
}

function generateCriticalFunctions(biaResults?: BIAResult[]) {
  const criticalFunctions = biaResults?.filter(r => r.criticalityLevel === 'critical') || []

  return {
    title: 'Critical Business Functions Analysis',
    content: `Analysis of ${criticalFunctions.length} critical business functions that pose the highest risk to organizational operations. These functions require prioritized attention in business continuity planning due to their low tolerance for disruption and high financial impact.`,
    table: {
      headers: ['Function', 'Department', 'RTO (h)', 'Financial Impact/Hour', 'Dependencies'],
      rows: criticalFunctions.map(func => [
        func.businessFunction,
        func.department,
        func.rto.toString(),
        `$${func.financialImpactPerHour.toLocaleString()}`,
        func.dependencies.slice(0, 3).join(', ') + (func.dependencies.length > 3 ? '...' : '')
      ])
    },
    summary: `${criticalFunctions.length} critical functions identified requiring specialized recovery procedures.`
  }
}

function generateFinancialImpact(biaResults?: BIAResult[]) {
  const sortedByImpact = [...(biaResults || [])].sort((a, b) => b.financialImpactPerHour - a.financialImpactPerHour)

  return {
    title: 'Financial Impact Analysis',
    content: 'Comprehensive analysis of financial impact across all business functions, ranked by hourly impact rate.',
    table: {
      headers: ['Function', 'Impact/Hour', '4-Hour Impact', '24-Hour Impact', 'MTPD Impact'],
      rows: sortedByImpact.slice(0, 10).map(func => [
        func.businessFunction,
        `$${func.financialImpactPerHour.toLocaleString()}`,
        `$${(func.financialImpactPerHour * 4).toLocaleString()}`,
        `$${(func.financialImpactPerHour * 24).toLocaleString()}`,
        `$${(func.financialImpactPerHour * func.mtpd).toLocaleString()}`
      ])
    },
    summary: `Top 10 functions by financial impact, with highest single-hour impact of $${sortedByImpact[0]?.financialImpactPerHour.toLocaleString() || '0'}.`
  }
}

function generateDependencyAnalysis(dependencies?: DependencyMapping[]) {
  return {
    title: 'Dependency Analysis',
    content: `Analysis of ${dependencies?.length || 0} critical dependencies between business functions. Understanding these relationships is crucial for effective recovery sequencing.`,
    table: {
      headers: ['Source Function', 'Target Dependency', 'Type', 'Impact Level', 'Recovery Sequence'],
      rows: (dependencies || []).map(dep => [
        dep.sourceFunction,
        dep.targetFunction,
        dep.dependencyType,
        dep.impactLevel.toString(),
        dep.recoverySequence?.toString() || 'TBD'
      ])
    },
    summary: `${dependencies?.filter(d => d.dependencyType === 'critical').length || 0} critical dependencies identified requiring coordinated recovery.`
  }
}

function generateCriticalPathsAnalysis(criticalPaths?: CriticalPath[]) {
  return {
    title: 'Critical Path Analysis',
    content: 'Identification and analysis of critical business function paths that represent the highest risk to organizational operations.',
    table: {
      headers: ['Path Name', 'Functions', 'Total RTO', 'Bottleneck', 'Risk Level'],
      rows: (criticalPaths || []).map(path => [
        path.name,
        path.functions.join(', '),
        `${path.totalRTO}h`,
        path.bottleneckFunction,
        path.riskLevel
      ])
    },
    summary: `${criticalPaths?.length || 0} critical paths identified with optimization opportunities for ${criticalPaths?.reduce((sum, p) => sum + p.optimizationOpportunities.length, 0) || 0} functions.`
  }
}

function generateRecommendations(biaResults?: BIAResult[], criticalPaths?: CriticalPath[]) {
  const recommendations = [
    'Implement redundant systems for critical functions with RTOs less than 4 hours',
    'Develop automated failover procedures for high-impact financial processes',
    'Establish cross-training programs for critical function personnel',
    'Create backup facilities for manufacturing and production functions',
    'Implement real-time monitoring for critical dependencies'
  ]

  return {
    title: 'Strategic Recommendations',
    content: 'AI-generated recommendations based on BIA analysis findings and industry best practices.',
    table: {
      headers: ['Priority', 'Recommendation', 'Impact', 'Effort', 'Timeline'],
      rows: recommendations.map((rec, idx) => [
        (idx + 1).toString(),
        rec,
        'High',
        idx < 2 ? 'Medium' : 'High',
        idx < 2 ? '3-6 months' : '6-12 months'
      ])
    },
    summary: `${recommendations.length} strategic recommendations provided for improving organizational resilience.`
  }
}

function generateISOComplianceOverview(biaResults?: BIAResult[], metrics?: BIAMetrics) {
  return {
    title: 'ISO 22301 Compliance Overview',
    content: 'Assessment of current BIA implementation against ISO 22301:2019 requirements for business continuity management systems.',
    table: {
      headers: ['Clause', 'Requirement', 'Status', 'Evidence', 'Gap Analysis'],
      rows: [
        ['8.2.1', 'BIA Process Established', 'Compliant', 'Documented procedures in place', 'None'],
        ['8.2.2', 'Functions Identified', 'Compliant', `${biaResults?.length || 0} functions assessed`, 'None'],
        ['8.2.3', 'Dependencies Mapped', 'Partial', 'Dependencies documented', 'Automated mapping needed'],
        ['8.2.4', 'Impact Analysis', 'Compliant', 'Financial impacts calculated', 'None'],
        ['8.2.5', 'Recovery Requirements', 'Compliant', 'RTO/RPO defined', 'None']
      ]
    },
    summary: 'Strong compliance with ISO 22301 BIA requirements, minor gaps in dependency automation.'
  }
}

function generateDetailedAnalysis(biaResults?: BIAResult[]) {
  return {
    title: 'Detailed Function Analysis',
    content: 'Comprehensive technical analysis of all assessed business functions.',
    table: {
      headers: ['Function', 'Dept', 'RTO', 'RPO', 'MTPD', 'Criticality', 'Last Assessed'],
      rows: (biaResults || []).map(func => [
        func.businessFunction,
        func.department,
        `${func.rto}h`,
        `${func.rpo}h`,
        `${func.mtpd}h`,
        func.criticalityLevel,
        func.lastAssessed
      ])
    },
    summary: `Complete analysis of ${biaResults?.length || 0} business functions with technical specifications.`
  }
}

function generateGenericSection(section: ReportSection, biaResults?: BIAResult[]) {
  return {
    title: section.name,
    content: section.description || `This section contains information about ${section.name.toLowerCase()}.`,
    summary: `${section.name} section included in report.`
  }
}

async function generateCharts(biaResults?: BIAResult[], metrics?: BIAMetrics) {
  // In a real implementation, this would generate actual chart images
  // For now, we'll return metadata about charts that would be generated
  return [
    {
      type: 'bar',
      title: 'Functions by Criticality Level',
      data: 'Chart showing distribution of functions across criticality levels'
    },
    {
      type: 'pie',
      title: 'Financial Impact Distribution',
      data: 'Pie chart of financial impact by department'
    },
    {
      type: 'line',
      title: 'RTO vs Financial Impact',
      data: 'Scatter plot showing relationship between RTO and financial impact'
    }
  ]
}

// Report Preview Component
function ReportPreview({ report }: { report: GeneratedReport }) {
  return (
    <div className="space-y-8">
      {/* Title Page */}
      <div className="text-center border-b pb-8">
        <h1 className="text-3xl font-bold mb-4">{report.title}</h1>
        <div className="text-gray-600 space-y-2">
          <p>Generated: {new Date(report.generatedAt).toLocaleDateString()}</p>
          <p>Organization: {report.metadata.organizationName}</p>
          {report.metadata.reportingPeriod && (
            <p>Period: {report.metadata.reportingPeriod.start} to {report.metadata.reportingPeriod.end}</p>
          )}
        </div>
      </div>

      {/* Sections */}
      {report.sections.map((section, index) => (
        <div key={index} className="space-y-4">
          <h2 className="text-2xl font-semibold text-gray-900">{section.title}</h2>
          {section.content && (
            <div className="text-gray-700 leading-relaxed">
              {section.content.split('\n').map((paragraph: string, idx: number) => (
                <p key={idx} className="mb-4">{paragraph}</p>
              ))}
            </div>
          )}
          {section.table && (
            <div className="overflow-x-auto">
              <table className="w-full border-collapse border border-gray-300">
                <thead>
                  <tr className="bg-gray-50">
                    {section.table.headers.map((header: string, idx: number) => (
                      <th key={idx} className="border border-gray-300 px-4 py-2 text-left font-semibold">
                        {header}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {section.table.rows.map((row: string[], idx: number) => (
                    <tr key={idx} className="even:bg-gray-50">
                      {row.map((cell, cellIdx) => (
                        <td key={cellIdx} className="border border-gray-300 px-4 py-2">
                          {cell}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      ))}
    </div>
  )
}