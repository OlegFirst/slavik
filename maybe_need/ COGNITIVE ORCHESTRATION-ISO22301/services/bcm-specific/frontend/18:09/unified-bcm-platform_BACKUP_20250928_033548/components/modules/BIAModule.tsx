'use client'

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import {
  TrendingUp,
  Clock,
  DollarSign,
  Building,
  Users,
  Plus,
  Download,
  Play,
  BarChart3,
  AlertCircle,
  Network,
  GitBranch,
  FileText,
  Brain
} from 'lucide-react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  biaAPI,
  biaQueryKeys,
  type BIAResult,
  type BIAMetrics
} from '@/services/bia-api'

// Import new BIA components
import { BIAQuestionnaireDialog } from '@/components/modules/bia/BIAQuestionnaire'
import { DependencyMap } from '@/components/modules/bia/DependencyMap'
import { CriticalPathAnalysis } from '@/components/modules/bia/CriticalPathAnalysis'
import { BIAReportGenerator } from '@/components/modules/bia/BIAReportGenerator'
import { ImpactTimeline } from '@/components/modules/bia/ImpactTimeline'
import { MLOptimizationDashboard } from '@/components/modules/bia/MLOptimizationDashboard'
import { ExternalServicesIntegration } from '@/components/modules/bia/ExternalServicesIntegration'
import { CollaborativeSession } from '@/components/modules/bia/CollaborativeSession'

export function BIAModule() {
  const [selectedDepartment, setSelectedDepartment] = useState<string>('all')
  const [selectedCriticality, setSelectedCriticality] = useState<string>('all')
  const queryClient = useQueryClient()

  // Fetch BIA results with filtering
  const { data: biaResults, isLoading, error } = useQuery({
    queryKey: biaQueryKeys.result({
      department: selectedDepartment,
      criticalityLevel: selectedCriticality
    }),
    queryFn: () => biaAPI.getBIAResults({
      department: selectedDepartment !== 'all' ? selectedDepartment : undefined,
      criticalityLevel: selectedCriticality !== 'all' ? selectedCriticality : undefined
    })
  })

  // Fetch BIA metrics
  const { data: metrics, isLoading: metricsLoading } = useQuery({
    queryKey: biaQueryKeys.metrics(),
    queryFn: () => biaAPI.getBIAMetrics()
  })

  // Run BIA Analysis mutation
  const runAnalysisMutation = useMutation({
    mutationFn: (functionIds?: string[]) => biaAPI.runBIAAnalysis(functionIds),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: biaQueryKeys.all })
    }
  })

  // Export to CSV mutation
  const exportMutation = useMutation({
    mutationFn: () => {
      if (biaResults) {
        biaAPI.exportBIAToCSV(biaResults)
      }
      return Promise.resolve()
    }
  })

  if (isLoading || metricsLoading) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-96"></div>
          <div className="grid grid-cols-4 gap-4">
            {[1,2,3,4].map(i => (
              <div key={i} className="h-24 bg-gray-200 rounded"></div>
            ))}
          </div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <h3 className="text-red-800 font-medium">Error loading BIA data</h3>
          <p className="text-red-600 text-sm mt-1">
            Unable to load BIA results. Please try again later.
          </p>
        </div>
      </div>
    )
  }

  const filteredResults = biaResults || []
  const departments = ['all', ...Array.from(new Set(biaResults?.map(r => r.department) || []))]
  const criticalityLevels = ['all', 'critical', 'high', 'medium', 'low']

  return (
    <div className="p-6 space-y-6">
      {/* Заголовок */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Business Impact Analysis</h1>
          <p className="text-gray-600">AI-powered BIA Engine v2.0 с ML-оптимизацией</p>
        </div>
        <div className="flex gap-3">
          <Button
            variant="outline"
            onClick={() => exportMutation.mutate()}
            disabled={exportMutation.isPending || !biaResults?.length}
          >
            <Download className="h-4 w-4 mr-2" />
            {exportMutation.isPending ? 'Exporting...' : 'Export Report'}
          </Button>
          <Button
            variant="outline"
            onClick={() => runAnalysisMutation.mutate(undefined)}
            disabled={runAnalysisMutation.isPending}
          >
            <Play className="h-4 w-4 mr-2" />
            {runAnalysisMutation.isPending ? 'Running...' : 'Run Analysis'}
          </Button>
          <BIAQuestionnaireDialog
            onComplete={(result) => {
              queryClient.invalidateQueries({ queryKey: biaQueryKeys.all })
            }}
          >
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              New BIA
            </Button>
          </BIAQuestionnaireDialog>
        </div>
      </div>

      {/* Метрики */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <BIAMetricCard 
          title="Total Functions"
          value={metrics?.totalFunctions || 0}
          icon={Building}
          color="blue"
        />
        <BIAMetricCard 
          title="Critical Functions"
          value={metrics?.criticalFunctions || 0}
          icon={AlertCircle}
          color="red"
        />
        <BIAMetricCard 
          title="Avg RTO"
          value={`${metrics?.avgRTO || 0}h`}
          icon={Clock}
          color="yellow"
        />
        <BIAMetricCard 
          title="Financial Risk"
          value={`$${((metrics?.totalFinancialRisk || 0) / 1000000).toFixed(1)}M`}
          icon={DollarSign}
          color="green"
        />
      </div>

      {/* Фильтры по департаментам и критичности */}
      <div className="space-y-4">
        <div className="flex gap-4 items-center flex-wrap">
          <Building className="h-4 w-4 text-gray-500" />
          <span className="text-sm font-medium text-gray-700">Department:</span>
          <div className="flex gap-2 flex-wrap">
            {departments.map(dept => (
              <Button
                key={dept}
                variant={selectedDepartment === dept ? "default" : "outline"}
                size="sm"
                onClick={() => setSelectedDepartment(dept)}
              >
                {dept === 'all' ? 'All Departments' : dept}
              </Button>
            ))}
          </div>
        </div>

        <div className="flex gap-4 items-center flex-wrap">
          <AlertCircle className="h-4 w-4 text-gray-500" />
          <span className="text-sm font-medium text-gray-700">Criticality:</span>
          <div className="flex gap-2 flex-wrap">
            {criticalityLevels.map(level => (
              <Button
                key={level}
                variant={selectedCriticality === level ? "default" : "outline"}
                size="sm"
                onClick={() => setSelectedCriticality(level)}
                className={cn(
                  level === 'critical' && selectedCriticality === level && "bg-red-600 hover:bg-red-700",
                  level === 'high' && selectedCriticality === level && "bg-orange-600 hover:bg-orange-700",
                  level === 'medium' && selectedCriticality === level && "bg-yellow-600 hover:bg-yellow-700",
                  level === 'low' && selectedCriticality === level && "bg-green-600 hover:bg-green-700"
                )}
              >
                {level === 'all' ? 'All Levels' : level.charAt(0).toUpperCase() + level.slice(1)}
              </Button>
            ))}
          </div>
        </div>
      </div>

      {/* BIA Results Table */}
      <div className="bg-white rounded-lg border shadow-sm">
        <div className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">BIA Results</h3>
            <div className="text-sm text-gray-500">
              {filteredResults.length} function{filteredResults.length !== 1 ? 's' : ''} shown
            </div>
          </div>

          {filteredResults.length === 0 ? (
            <div className="text-center py-8">
              <AlertCircle className="h-12 w-12 text-gray-300 mx-auto mb-4" />
              <h4 className="text-lg font-medium text-gray-900 mb-2">No BIA results found</h4>
              <p className="text-gray-500">
                {selectedDepartment !== 'all' || selectedCriticality !== 'all'
                  ? 'Try adjusting your filters or create a new BIA assessment.'
                  : 'Get started by creating your first BIA assessment.'
                }
              </p>
              <Button className="mt-4">
                <Plus className="h-4 w-4 mr-2" />
                Create New Assessment
              </Button>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-3 px-2 font-medium text-gray-500">Business Function</th>
                    <th className="text-left py-3 px-2 font-medium text-gray-500">Department</th>
                    <th className="text-left py-3 px-2 font-medium text-gray-500">RTO</th>
                    <th className="text-left py-3 px-2 font-medium text-gray-500">RPO</th>
                    <th className="text-left py-3 px-2 font-medium text-gray-500">MTPD</th>
                    <th className="text-left py-3 px-2 font-medium text-gray-500">Impact/Hour</th>
                    <th className="text-left py-3 px-2 font-medium text-gray-500">Criticality</th>
                    <th className="text-left py-3 px-2 font-medium text-gray-500">Dependencies</th>
                    <th className="text-left py-3 px-2 font-medium text-gray-500">Last Assessed</th>
                    <th className="text-left py-3 px-2 font-medium text-gray-500">Assessed By</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredResults.map(result => (
                    <tr key={result.id} className="border-b hover:bg-gray-50 cursor-pointer">
                      <td className="py-3 px-2">
                        <div className="font-medium text-gray-900">{result.businessFunction}</div>
                        {result.assessmentVersion && (
                          <div className="text-xs text-gray-500">v{result.assessmentVersion}</div>
                        )}
                      </td>
                      <td className="py-3 px-2 text-gray-600">{result.department}</td>
                      <td className="py-3 px-2">
                        <span className="font-mono text-sm">{result.rto}h</span>
                      </td>
                      <td className="py-3 px-2">
                        <span className="font-mono text-sm">{result.rpo}h</span>
                      </td>
                      <td className="py-3 px-2">
                        <span className="font-mono text-sm">{result.mtpd}h</span>
                      </td>
                      <td className="py-3 px-2">
                        <span className="font-mono text-sm">${result.financialImpactPerHour.toLocaleString()}</span>
                      </td>
                      <td className="py-3 px-2">
                        <span className={cn(
                          "inline-flex px-2 py-1 text-xs font-medium rounded-full",
                          result.criticalityLevel === 'critical' && "bg-red-100 text-red-800",
                          result.criticalityLevel === 'high' && "bg-orange-100 text-orange-800",
                          result.criticalityLevel === 'medium' && "bg-yellow-100 text-yellow-800",
                          result.criticalityLevel === 'low' && "bg-green-100 text-green-800"
                        )}>
                          {result.criticalityLevel}
                        </span>
                      </td>
                      <td className="py-3 px-2">
                        <div className="text-xs text-gray-500">
                          {result.dependencies.length} dependencies
                        </div>
                        {result.dependencies.length > 0 && (
                          <div className="text-xs text-gray-400 truncate max-w-[120px]" title={result.dependencies.join(', ')}>
                            {result.dependencies.join(', ')}
                          </div>
                        )}
                      </td>
                      <td className="py-3 px-2 text-sm text-gray-600">
                        {new Date(result.lastAssessed).toLocaleDateString()}
                      </td>
                      <td className="py-3 px-2 text-sm text-gray-600">
                        {result.assessedBy || 'Unknown'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {/* Advanced BIA Analysis Tabs */}
      <Tabs defaultValue="insights" className="w-full">
        <TabsList className="grid w-full grid-cols-8">
          <TabsTrigger value="insights">
            <BarChart3 className="h-4 w-4 mr-2" />
            Insights
          </TabsTrigger>
          <TabsTrigger value="dependencies">
            <Network className="h-4 w-4 mr-2" />
            Dependencies
          </TabsTrigger>
          <TabsTrigger value="critical-path">
            <GitBranch className="h-4 w-4 mr-2" />
            Critical Path
          </TabsTrigger>
          <TabsTrigger value="timeline">
            <Clock className="h-4 w-4 mr-2" />
            Impact Timeline
          </TabsTrigger>
          <TabsTrigger value="ml-optimization">
            <Brain className="h-4 w-4 mr-2" />
            ML Optimization
          </TabsTrigger>
          <TabsTrigger value="collaboration">
            <Users className="h-4 w-4 mr-2" />
            Collaboration
          </TabsTrigger>
          <TabsTrigger value="reports">
            <FileText className="h-4 w-4 mr-2" />
            Reports
          </TabsTrigger>
          <TabsTrigger value="analysis">
            <TrendingUp className="h-4 w-4 mr-2" />
            Analysis
          </TabsTrigger>
        </TabsList>

        <TabsContent value="insights" className="mt-6">
          {/* ML Insights Panel - existing content */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg border p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <BarChart3 className="h-5 w-5 text-blue-600" />
            AI Recommendations
            {runAnalysisMutation.isPending && (
              <div className="h-4 w-4 animate-spin rounded-full border-2 border-blue-600 border-t-transparent"></div>
            )}
          </h3>

          {runAnalysisMutation.data?.results ? (
            <div className="space-y-3">
              <div className="p-3 bg-blue-50 rounded-lg">
                <div className="font-medium text-blue-900">Analysis Complete</div>
                <div className="text-sm text-blue-700">
                  {runAnalysisMutation.data.results.functionsAnalyzed} functions analyzed,
                  {runAnalysisMutation.data.results.criticalPathsIdentified} critical paths identified
                </div>
              </div>

              {runAnalysisMutation.data.results.recommendations?.map((rec: string, idx: number) => (
                <div key={idx} className="p-3 bg-yellow-50 rounded-lg">
                  <div className="font-medium text-yellow-900">Recommendation {idx + 1}</div>
                  <div className="text-sm text-yellow-700">{rec}</div>
                </div>
              ))}

              <div className="p-3 bg-green-50 rounded-lg">
                <div className="font-medium text-green-900">Optimization Opportunities</div>
                <div className="text-sm text-green-700">
                  {runAnalysisMutation.data.results.optimizationOpportunities} potential improvements identified
                </div>
              </div>
            </div>
          ) : (
            <div className="space-y-3">
              <div className="p-3 bg-blue-50 rounded-lg">
                <div className="font-medium text-blue-900">RTO Optimization</div>
                <div className="text-sm text-blue-700">
                  {filteredResults.filter(r => r.rto > 24).length} functions can reduce RTO with infrastructure upgrade
                </div>
              </div>
              <div className="p-3 bg-yellow-50 rounded-lg">
                <div className="font-medium text-yellow-900">Cost Reduction</div>
                <div className="text-sm text-yellow-700">
                  Shared backup systems can save ${Math.round(
                    filteredResults.reduce((sum, r) => sum + r.financialImpactPerHour, 0) * 0.1 / 1000
                  )}K annually
                </div>
              </div>
              <div className="p-3 bg-green-50 rounded-lg">
                <div className="font-medium text-green-900">Dependencies</div>
                <div className="text-sm text-green-700">
                  Automated dependency mapping completed for {filteredResults.length}/{metrics?.totalFunctions || filteredResults.length} functions
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="bg-white rounded-lg border p-6">
          <h3 className="text-lg font-semibold mb-4">Financial Impact Summary</h3>
          <div className="space-y-4">
            {filteredResults.length > 0 ? (
              <>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">1-hour outage</span>
                  <span className="font-semibold">
                    ${Math.round(filteredResults.reduce((sum, r) => sum + r.financialImpactPerHour, 0)).toLocaleString()}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">4-hour outage</span>
                  <span className="font-semibold">
                    ${Math.round(filteredResults.reduce((sum, r) => sum + r.financialImpactPerHour * 4, 0)).toLocaleString()}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">24-hour outage</span>
                  <span className="font-semibold text-red-600">
                    ${Math.round(filteredResults.reduce((sum, r) => sum + r.financialImpactPerHour * 24, 0)).toLocaleString()}
                  </span>
                </div>
                <div className="border-t pt-4">
                  <div className="flex justify-between items-center text-lg font-bold">
                    <span>Max Potential Loss (MTPD)</span>
                    <span className="text-red-600">
                      ${Math.round(
                        filteredResults.reduce((sum, r) =>
                          sum + (r.financialImpactPerHour * r.mtpd), 0
                        ) / 1000000 * 100
                      ) / 100}M
                    </span>
                  </div>
                </div>

                <div className="mt-4 pt-4 border-t">
                  <div className="text-sm text-gray-600 space-y-1">
                    <div>Critical functions: {filteredResults.filter(r => r.criticalityLevel === 'critical').length}</div>
                    <div>Average RTO: {Math.round(filteredResults.reduce((sum, r) => sum + r.rto, 0) / filteredResults.length * 10) / 10}h</div>
                    <div>Total dependencies: {filteredResults.reduce((sum, r) => sum + r.dependencies.length, 0)}</div>
                  </div>
                </div>
              </>
            ) : (
              <div className="text-center py-4 text-gray-500">
                No data available for financial impact calculation
              </div>
            )}
          </div>
        </div>
      </div>
        </TabsContent>

        <TabsContent value="dependencies" className="mt-6">
          <DependencyMap />
        </TabsContent>

        <TabsContent value="critical-path" className="mt-6">
          <CriticalPathAnalysis />
        </TabsContent>

        <TabsContent value="timeline" className="mt-6">
          <ImpactTimeline />
        </TabsContent>

        <TabsContent value="ml-optimization" className="mt-6">
          <MLOptimizationDashboard />
        </TabsContent>

        <TabsContent value="collaboration" className="mt-6">
          <CollaborativeSession biaResults={biaResults || []} />
        </TabsContent>

        <TabsContent value="reports" className="mt-6">
          <BIAReportGenerator />
        </TabsContent>

        <TabsContent value="analysis" className="mt-6">
          <ExternalServicesIntegration biaResults={biaResults || []} />
        </TabsContent>
      </Tabs>
    </div>
  )
}

// Компонент метрики BIA
function BIAMetricCard({ 
  title, 
  value, 
  icon: Icon, 
  color 
}: {
  title: string
  value: string | number
  icon: React.ComponentType<{ className?: string }>
  color: 'blue' | 'red' | 'yellow' | 'green'
}) {
  return (
    <div className="bg-white rounded-lg border p-6">
      <div className="flex items-center justify-between">
        <div className={cn(
          "w-12 h-12 rounded-lg flex items-center justify-center",
          color === 'blue' && "bg-blue-100 text-blue-600",
          color === 'red' && "bg-red-100 text-red-600", 
          color === 'yellow' && "bg-yellow-100 text-yellow-600",
          color === 'green' && "bg-green-100 text-green-600"
        )}>
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

