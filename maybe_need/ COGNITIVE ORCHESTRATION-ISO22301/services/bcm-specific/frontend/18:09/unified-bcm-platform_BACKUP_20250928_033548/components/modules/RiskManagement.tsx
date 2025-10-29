'use client'

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { riskManagementAPI, riskQueryKeys, type Risk, type RiskMetrics } from '@/services/risk-management-api'
import { toast } from 'sonner'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { Slider } from '@/components/ui/slider'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'
import {
  Shield,
  TrendingUp,
  AlertTriangle,
  BarChart3,
  Plus,
  Filter,
  Download,
  RefreshCw,
  Edit,
  Trash2,
  Eye,
  Target,
  Activity,
  PieChart,
  Loader2,
  ChevronRight,
  Brain
} from 'lucide-react'
import { monteCarloSimulation } from '@/services/monte-carlo-simulation'
import type { SimulationResult, AggregatedSimulationResult } from '@/services/monte-carlo-simulation'
import { AIRiskAdvisor } from '@/components/modules/risk/AIRiskAdvisor'

// Form data interface
interface RiskFormData {
  title: string
  description: string
  category: 'operational' | 'financial' | 'strategic' | 'compliance'
  probability: number
  impact: number
  owner: string
  mitigation: string
}

export function RiskManagementModule() {
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false)
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false)
  const [isFAIRDialogOpen, setIsFAIRDialogOpen] = useState(false)
  const [isTreatmentPlanOpen, setIsTreatmentPlanOpen] = useState(false)
  const [editingRisk, setEditingRisk] = useState<Risk | null>(null)
  const [activeTab, setActiveTab] = useState<'table' | 'heatmap' | 'analytics' | 'appetite' | 'fair' | 'ai-advisor'>('table')
  const [formData, setFormData] = useState<RiskFormData>({
    title: '',
    description: '',
    category: 'operational',
    probability: 5,
    impact: 5,
    owner: '',
    mitigation: ''
  })

  const queryClient = useQueryClient()
  
  // Получение данных рисков через API
  const { data: risks, isLoading, error } = useQuery<Risk[]>({
    queryKey: riskQueryKeys.list({ category: selectedCategory }),
    queryFn: () => riskManagementAPI.getRisks(selectedCategory),
    staleTime: 30000 // 30 seconds
  })

  // Получение метрик через API
  const { data: metrics } = useQuery<RiskMetrics>({
    queryKey: riskQueryKeys.metrics(),
    queryFn: () => riskManagementAPI.getRiskMetrics(),
    staleTime: 60000 // 1 minute
  })

  // Mutations для CRUD операций
  const createRiskMutation = useMutation({
    mutationFn: (data: Omit<Risk, 'id' | 'createdAt' | 'updatedAt'>) =>
      riskManagementAPI.createRisk(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: riskQueryKeys.all })
      setIsCreateDialogOpen(false)
      toast.success('Risk created successfully')
    },
    onError: (err) => {
      console.error('Failed to create risk:', err)
      toast.error('Failed to create risk')
    }
  })

  const updateRiskMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Risk> }) =>
      riskManagementAPI.updateRisk(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: riskQueryKeys.all })
      setIsEditDialogOpen(false)
      toast.success('Risk updated successfully')
    },
    onError: (err) => {
      console.error('Failed to update risk:', err)
      toast.error('Failed to update risk')
    }
  })

  const deleteRiskMutation = useMutation({
    mutationFn: (id: string) => riskManagementAPI.deleteRisk(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: riskQueryKeys.all })
      toast.success('Risk deleted successfully')
    },
    onError: (err) => {
      console.error('Failed to delete risk:', err)
      toast.error('Failed to delete risk')
    }
  })

  if (isLoading) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-64"></div>
          <div className="grid grid-cols-4 gap-4">
            {[1,2,3,4].map(i => (
              <div key={i} className="h-24 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  const filteredRisks = risks?.filter(risk => 
    selectedCategory === 'all' || risk.category === selectedCategory
  ) || []

  return (
    <div className="p-6 space-y-6">
      {/* Заголовок */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Risk Management</h1>
          <p className="text-gray-600">Управление рисками с AI-анализом</p>
        </div>
        <div className="flex gap-3">
          <Button variant="outline" onClick={handleExportRisks}>
            <Download className="h-4 w-4 mr-2" />
            Export Risk Register
          </Button>
          <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
            <DialogTrigger asChild>
              <Button onClick={() => {
                setFormData({
                  title: '',
                  description: '',
                  category: 'operational',
                  probability: 5,
                  impact: 5,
                  owner: '',
                  mitigation: ''
                })
              }}>
                <Plus className="h-4 w-4 mr-2" />
                New Risk
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>Create New Risk</DialogTitle>
              </DialogHeader>
              <RiskForm
                formData={formData}
                setFormData={setFormData}
                onSubmit={() => handleCreateRisk()}
                onCancel={() => setIsCreateDialogOpen(false)}
              />
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Метрики */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <MetricCard 
          title="Total Risks"
          value={metrics?.totalRisks || 0}
          icon={Shield}
          color="blue"
        />
        <MetricCard 
          title="High Risk"
          value={metrics?.highRisks || 0}
          icon={AlertTriangle}
          color="red"
        />
        <MetricCard 
          title="New This Month"
          value={metrics?.newThisMonth || 0}
          icon={TrendingUp}
          color="green"
        />
        <MetricCard 
          title="Avg Risk Score"
          value={metrics?.avgRiskScore || 0}
          icon={BarChart3}
          color="purple"
        />
      </div>

      {/* Tab Navigation */}
      <div className="flex gap-4 items-center justify-between">
        <div className="flex gap-4 items-center">
          <Filter className="h-4 w-4 text-gray-500" />
          <div className="flex gap-2">
            {['all', 'operational', 'financial', 'strategic', 'compliance'].map(category => (
              <Button
                key={category}
                variant={selectedCategory === category ? "default" : "outline"}
                size="sm"
                onClick={() => setSelectedCategory(category)}
              >
                {category.charAt(0).toUpperCase() + category.slice(1)}
              </Button>
            ))}
          </div>
        </div>

        <div className="flex gap-2 flex-wrap">
          <Button
            variant={activeTab === 'table' ? "default" : "outline"}
            size="sm"
            onClick={() => setActiveTab('table')}
          >
            <BarChart3 className="h-4 w-4 mr-2" />
            Table
          </Button>
          <Button
            variant={activeTab === 'heatmap' ? "default" : "outline"}
            size="sm"
            onClick={() => setActiveTab('heatmap')}
          >
            <Target className="h-4 w-4 mr-2" />
            Heat Map
          </Button>
          <Button
            variant={activeTab === 'analytics' ? "default" : "outline"}
            size="sm"
            onClick={() => setActiveTab('analytics')}
          >
            <PieChart className="h-4 w-4 mr-2" />
            Analytics
          </Button>
          <Button
            variant={activeTab === 'appetite' ? "default" : "outline"}
            size="sm"
            onClick={() => setActiveTab('appetite')}
          >
            <Activity className="h-4 w-4 mr-2" />
            Risk Appetite
          </Button>
          <Button
            variant={activeTab === 'fair' ? "default" : "outline"}
            size="sm"
            onClick={() => setActiveTab('fair')}
          >
            <Shield className="h-4 w-4 mr-2" />
            FAIR Analysis
          </Button>
          <Button
            variant={activeTab === 'ai-advisor' ? "default" : "outline"}
            size="sm"
            onClick={() => setActiveTab('ai-advisor')}
          >
            <Brain className="h-4 w-4 mr-2" />
            AI Advisor
          </Button>
        </div>
      </div>

      {/* Content based on active tab */}
      {activeTab === 'table' && (
        <div className="bg-white rounded-lg border shadow-sm">
          <div className="p-6">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-3 px-2 font-medium text-gray-500">Risk</th>
                    <th className="text-left py-3 px-2 font-medium text-gray-500">Category</th>
                    <th className="text-left py-3 px-2 font-medium text-gray-500">Probability</th>
                    <th className="text-left py-3 px-2 font-medium text-gray-500">Impact</th>
                    <th className="text-left py-3 px-2 font-medium text-gray-500">Risk Score</th>
                    <th className="text-left py-3 px-2 font-medium text-gray-500">Status</th>
                    <th className="text-left py-3 px-2 font-medium text-gray-500">Owner</th>
                    <th className="text-left py-3 px-2 font-medium text-gray-500">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredRisks.map(risk => (
                    <tr key={risk.id} className="border-b hover:bg-gray-50">
                      <td className="py-3 px-2">
                        <div className="font-medium text-gray-900">{risk.title}</div>
                      </td>
                      <td className="py-3 px-2">
                        <span className={cn(
                          "inline-flex px-2 py-1 text-xs font-medium rounded-full",
                          risk.category === 'operational' && "bg-blue-100 text-blue-800",
                          risk.category === 'financial' && "bg-green-100 text-green-800",
                          risk.category === 'strategic' && "bg-purple-100 text-purple-800",
                          risk.category === 'compliance' && "bg-yellow-100 text-yellow-800"
                        )}>
                          {risk.category}
                        </span>
                      </td>
                      <td className="py-3 px-2">{risk.probability}/10</td>
                      <td className="py-3 px-2">{risk.impact}/10</td>
                      <td className="py-3 px-2">
                        <span className={cn(
                          "font-medium",
                          risk.riskScore >= 8 && "text-red-600",
                          risk.riskScore >= 5 && risk.riskScore < 8 && "text-yellow-600",
                          risk.riskScore < 5 && "text-green-600"
                        )}>
                          {risk.riskScore.toFixed(1)}
                        </span>
                      </td>
                      <td className="py-3 px-2">
                        <span className={cn(
                          "inline-flex px-2 py-1 text-xs font-medium rounded-full",
                          risk.status === 'open' && "bg-red-100 text-red-800",
                          risk.status === 'mitigated' && "bg-green-100 text-green-800",
                          risk.status === 'accepted' && "bg-yellow-100 text-yellow-800",
                          risk.status === 'transferred' && "bg-blue-100 text-blue-800"
                        )}>
                          {risk.status}
                        </span>
                      </td>
                      <td className="py-3 px-2 text-gray-600">{risk.owner}</td>
                      <td className="py-3 px-2">
                        <div className="flex gap-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleViewRisk(risk)}
                          >
                            <Eye className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleEditRisk(risk)}
                          >
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleDeleteRisk(risk.id)}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'heatmap' && (
        <RiskHeatMap risks={filteredRisks} />
      )}

      {activeTab === 'analytics' && (
        <RiskAnalytics risks={filteredRisks} />
      )}

      {activeTab === 'appetite' && (
        <RiskAppetiteDashboard risks={filteredRisks} />
      )}

      {activeTab === 'fair' && (
        <FAIRAnalysis risks={filteredRisks} />
      )}

      {activeTab === 'ai-advisor' && (
        <AIRiskAdvisor risks={filteredRisks} />
      )}

      {/* Edit Risk Dialog */}
      <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Edit Risk</DialogTitle>
          </DialogHeader>
          <RiskForm
            formData={formData}
            setFormData={setFormData}
            onSubmit={() => handleUpdateRisk()}
            onCancel={() => setIsEditDialogOpen(false)}
            isEditing
          />
        </DialogContent>
      </Dialog>
    </div>
  )

  // Handlers для CRUD операций с API
  async function handleCreateRisk() {
    const newRisk = {
      title: formData.title,
      description: formData.description,
      category: formData.category,
      probability: formData.probability,
      impact: formData.impact,
      riskScore: calculateRiskScore(formData.probability, formData.impact),
      status: 'open' as const,
      owner: formData.owner,
      mitigation: formData.mitigation,
      lastAssessed: new Date().toISOString().split('T')[0]
    }

    await createRiskMutation.mutateAsync(newRisk)
  }

  function handleEditRisk(risk: Risk) {
    setEditingRisk(risk)
    setFormData({
      title: risk.title,
      description: risk.description || '',
      category: risk.category,
      probability: risk.probability,
      impact: risk.impact,
      owner: risk.owner,
      mitigation: risk.mitigation || ''
    })
    setIsEditDialogOpen(true)
  }

  async function handleUpdateRisk() {
    if (!editingRisk) return

    const updatedData: Partial<Risk> = {
      title: formData.title,
      description: formData.description,
      category: formData.category,
      probability: formData.probability,
      impact: formData.impact,
      riskScore: calculateRiskScore(formData.probability, formData.impact),
      owner: formData.owner,
      mitigation: formData.mitigation
    }

    await updateRiskMutation.mutateAsync({
      id: editingRisk.id,
      data: updatedData
    })

    setEditingRisk(null)
  }

  async function handleDeleteRisk(riskId: string) {
    if (confirm('Are you sure you want to delete this risk?')) {
      await deleteRiskMutation.mutateAsync(riskId)
    }
  }

  function handleViewRisk(risk: Risk) {
    // Здесь можно открыть детальную модель просмотра риска
    alert(`Risk Details:\n\nTitle: ${risk.title}\nCategory: ${risk.category}\nRisk Score: ${risk.riskScore}\nOwner: ${risk.owner}`)
  }

  function calculateRiskScore(probability: number, impact: number): number {
    return Number(((probability * impact) / 10).toFixed(1))
  }

  function handleExportRisks() {
    if (!filteredRisks || filteredRisks.length === 0) {
      toast.error('No risks to export')
      return
    }

    try {
      riskManagementAPI.exportRisksToCSV(filteredRisks)
      toast.success(`Exported ${filteredRisks.length} risks to CSV`)
    } catch (error) {
      console.error('Export failed:', error)
      toast.error('Failed to export risks')
    }
  }
}

// Компонент для метрик
function MetricCard({ 
  title, 
  value, 
  icon: Icon, 
  color 
}: {
  title: string
  value: number
  icon: React.ComponentType<{ className?: string }>
  color: 'blue' | 'red' | 'green' | 'purple'
}) {
  return (
    <div className="bg-white rounded-lg border p-6">
      <div className="flex items-center justify-between">
        <div className={cn(
          "w-12 h-12 rounded-lg flex items-center justify-center",
          color === 'blue' && "bg-blue-100 text-blue-600",
          color === 'red' && "bg-red-100 text-red-600", 
          color === 'green' && "bg-green-100 text-green-600",
          color === 'purple' && "bg-purple-100 text-purple-600"
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

// Компонент формы для создания/редактирования рисков
function RiskForm({
  formData,
  setFormData,
  onSubmit,
  onCancel,
  isEditing = false
}: {
  formData: RiskFormData
  setFormData: (data: RiskFormData) => void
  onSubmit: () => void
  onCancel: () => void
  isEditing?: boolean
}) {
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit()
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Title */}
      <div className="space-y-2">
        <Label htmlFor="title">Risk Title *</Label>
        <Input
          id="title"
          value={formData.title}
          onChange={(e) => setFormData({ ...formData, title: e.target.value })}
          placeholder="Enter risk title"
          required
        />
      </div>

      {/* Description */}
      <div className="space-y-2">
        <Label htmlFor="description">Description</Label>
        <Textarea
          id="description"
          value={formData.description}
          onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          placeholder="Describe the risk in detail"
          rows={3}
        />
      </div>

      {/* Category and Owner row */}
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="category">Category *</Label>
          <Select
            value={formData.category}
            onValueChange={(value: 'operational' | 'financial' | 'strategic' | 'compliance') =>
              setFormData({ ...formData, category: value })
            }
          >
            <SelectTrigger>
              <SelectValue placeholder="Select category" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="operational">Operational</SelectItem>
              <SelectItem value="financial">Financial</SelectItem>
              <SelectItem value="strategic">Strategic</SelectItem>
              <SelectItem value="compliance">Compliance</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <Label htmlFor="owner">Risk Owner *</Label>
          <Input
            id="owner"
            value={formData.owner}
            onChange={(e) => setFormData({ ...formData, owner: e.target.value })}
            placeholder="Assign risk owner"
            required
          />
        </div>
      </div>

      {/* Probability and Impact sliders */}
      <div className="grid grid-cols-2 gap-6">
        <div className="space-y-3">
          <Label>Probability (1-10)</Label>
          <div className="px-3">
            <Slider
              value={[formData.probability]}
              onValueChange={(value) => setFormData({ ...formData, probability: value[0] })}
              max={10}
              min={1}
              step={1}
              className="w-full"
            />
            <div className="flex justify-between text-sm text-gray-500 mt-1">
              <span>Low (1)</span>
              <span className="font-medium">{formData.probability}</span>
              <span>High (10)</span>
            </div>
          </div>
        </div>

        <div className="space-y-3">
          <Label>Impact (1-10)</Label>
          <div className="px-3">
            <Slider
              value={[formData.impact]}
              onValueChange={(value) => setFormData({ ...formData, impact: value[0] })}
              max={10}
              min={1}
              step={1}
              className="w-full"
            />
            <div className="flex justify-between text-sm text-gray-500 mt-1">
              <span>Low (1)</span>
              <span className="font-medium">{formData.impact}</span>
              <span>High (10)</span>
            </div>
          </div>
        </div>
      </div>

      {/* Risk Score Display */}
      <div className="bg-gray-50 p-4 rounded-lg">
        <Label className="text-sm font-medium text-gray-700">Calculated Risk Score</Label>
        <div className="text-2xl font-bold text-gray-900 mt-1">
          {((formData.probability * formData.impact) / 10).toFixed(1)}
        </div>
        <div className="text-sm text-gray-500">
          Risk Level: {
            ((formData.probability * formData.impact) / 10) >= 8 ? (
              <span className="text-red-600 font-medium">High</span>
            ) : ((formData.probability * formData.impact) / 10) >= 5 ? (
              <span className="text-yellow-600 font-medium">Medium</span>
            ) : (
              <span className="text-green-600 font-medium">Low</span>
            )
          }
        </div>
      </div>

      {/* Mitigation Strategy */}
      <div className="space-y-2">
        <Label htmlFor="mitigation">Mitigation Strategy</Label>
        <Textarea
          id="mitigation"
          value={formData.mitigation}
          onChange={(e) => setFormData({ ...formData, mitigation: e.target.value })}
          placeholder="Describe mitigation actions and controls"
          rows={3}
        />
      </div>

      {/* Action Buttons */}
      <DialogFooter>
        <Button type="button" variant="outline" onClick={onCancel}>
          Cancel
        </Button>
        <Button type="submit">
          {isEditing ? 'Update Risk' : 'Create Risk'}
        </Button>
      </DialogFooter>
    </form>
  )
}

// Risk Heat Map Component
function RiskHeatMap({ risks }: { risks: Risk[] }) {
  // Create a 10x10 grid for the heat map
  const heatMapData = Array(10).fill(null).map(() => Array(10).fill(null))

  // Populate the grid with risks
  risks.forEach(risk => {
    const x = risk.probability - 1 // Convert to 0-9 index
    const y = risk.impact - 1 // Convert to 0-9 index
    if (!heatMapData[y][x]) {
      heatMapData[y][x] = []
    }
    heatMapData[y][x].push(risk)
  })

  const getRiskColor = (probability: number, impact: number) => {
    const score = (probability * impact) / 10
    if (score >= 8) return 'bg-red-500'
    if (score >= 5) return 'bg-yellow-500'
    return 'bg-green-500'
  }

  return (
    <div className="bg-white rounded-lg border shadow-sm p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold">Risk Heat Map</h3>
        <div className="flex items-center gap-4 text-sm">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-green-500 rounded"></div>
            <span>Low Risk (Score {'<'} 5)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-yellow-500 rounded"></div>
            <span>Medium Risk (5-7.9)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-red-500 rounded"></div>
            <span>High Risk (≥ 8)</span>
          </div>
        </div>
      </div>

      <div className="relative">
        {/* Y-axis label */}
        <div className="absolute left-0 top-1/2 -translate-y-1/2 -rotate-90 text-sm font-medium text-gray-700">
          Impact
        </div>

        {/* Grid container */}
        <div className="ml-8">
          {/* Y-axis numbers */}
          <div className="flex flex-col-reverse absolute -left-6 h-full">
            {Array.from({ length: 10 }, (_, i) => (
              <div key={i} className="flex-1 flex items-center text-xs text-gray-500">
                {i + 1}
              </div>
            ))}
          </div>

          {/* Heat map grid */}
          <div className="grid grid-cols-10 gap-1 mb-4">
            {heatMapData.slice().reverse().map((row, rowIndex) =>
              row.map((cell, colIndex) => {
                const actualRow = 9 - rowIndex
                const probability = colIndex + 1
                const impact = actualRow + 1
                const cellRisks = cell || []

                return (
                  <div
                    key={`${rowIndex}-${colIndex}`}
                    className={cn(
                      "aspect-square border border-gray-200 rounded flex items-center justify-center text-white font-medium text-xs relative group cursor-pointer",
                      cellRisks.length > 0
                        ? getRiskColor(probability, impact)
                        : "bg-gray-100"
                    )}
                    title={cellRisks.length > 0 ? `${cellRisks.length} risk(s)` : 'No risks'}
                  >
                    {cellRisks.length > 0 && cellRisks.length}

                    {/* Tooltip */}
                    {cellRisks.length > 0 && (
                      <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 opacity-0 group-hover:opacity-100 transition-opacity z-10">
                        <div className="bg-gray-900 text-white text-xs rounded p-2 whitespace-nowrap">
                          <div className="font-semibold">Probability: {probability}, Impact: {impact}</div>
                          <div>Risk Score: {((probability * impact) / 10).toFixed(1)}</div>
                          <div className="mt-1">
                            {cellRisks.map((risk: Risk) => (
                              <div key={risk.id} className="truncate max-w-32">
                                {risk.title}
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                )
              })
            )}
          </div>

          {/* X-axis numbers */}
          <div className="grid grid-cols-10 gap-1">
            {Array.from({ length: 10 }, (_, i) => (
              <div key={i} className="text-center text-xs text-gray-500">
                {i + 1}
              </div>
            ))}
          </div>

          {/* X-axis label */}
          <div className="text-center mt-2 text-sm font-medium text-gray-700">
            Probability
          </div>
        </div>
      </div>
    </div>
  )
}

// Risk Analytics Component
function RiskAnalytics({ risks }: { risks: Risk[] }) {
  const categoryData = risks.reduce((acc, risk) => {
    acc[risk.category] = (acc[risk.category] || 0) + 1
    return acc
  }, {} as Record<string, number>)

  const statusData = risks.reduce((acc, risk) => {
    acc[risk.status] = (acc[risk.status] || 0) + 1
    return acc
  }, {} as Record<string, number>)

  const riskLevelData = risks.reduce((acc, risk) => {
    if (risk.riskScore >= 8) acc.high = (acc.high || 0) + 1
    else if (risk.riskScore >= 5) acc.medium = (acc.medium || 0) + 1
    else acc.low = (acc.low || 0) + 1
    return acc
  }, {} as Record<string, number>)

  return (
    <div className="space-y-6">
      {/* Risk Distribution by Category */}
      <div className="bg-white rounded-lg border shadow-sm p-6">
        <h3 className="text-lg font-semibold mb-4">Risk Distribution by Category</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {Object.entries(categoryData).map(([category, count]) => (
            <div key={category} className="text-center">
              <div className="text-2xl font-bold text-gray-900">{count}</div>
              <div className="text-sm text-gray-500 capitalize">{category}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Risk Status Overview */}
      <div className="bg-white rounded-lg border shadow-sm p-6">
        <h3 className="text-lg font-semibold mb-4">Risk Status Overview</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {Object.entries(statusData).map(([status, count]) => (
            <div key={status} className="text-center">
              <div className="text-2xl font-bold text-gray-900">{count}</div>
              <div className="text-sm text-gray-500 capitalize">{status}</div>
              <div className={cn(
                "w-full h-2 rounded mt-2",
                status === 'open' && "bg-red-200",
                status === 'mitigated' && "bg-green-200",
                status === 'accepted' && "bg-yellow-200",
                status === 'transferred' && "bg-blue-200"
              )} />
            </div>
          ))}
        </div>
      </div>

      {/* Risk Level Analysis */}
      <div className="bg-white rounded-lg border shadow-sm p-6">
        <h3 className="text-lg font-semibold mb-4">Risk Level Analysis</h3>
        <div className="grid grid-cols-3 gap-6">
          <div className="text-center">
            <div className="text-3xl font-bold text-red-600">{riskLevelData.high || 0}</div>
            <div className="text-sm text-gray-500">High Risk (≥ 8.0)</div>
            <div className="w-full h-3 bg-red-200 rounded mt-2"></div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-yellow-600">{riskLevelData.medium || 0}</div>
            <div className="text-sm text-gray-500">Medium Risk (5.0-7.9)</div>
            <div className="w-full h-3 bg-yellow-200 rounded mt-2"></div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-green-600">{riskLevelData.low || 0}</div>
            <div className="text-sm text-gray-500">Low Risk (Score {'<'} 5.0)</div>
            <div className="w-full h-3 bg-green-200 rounded mt-2"></div>
          </div>
        </div>
      </div>

      {/* Risk Trends */}
      <div className="bg-white rounded-lg border shadow-sm p-6">
        <h3 className="text-lg font-semibold mb-4">Risk Assessment Recommendations</h3>
        <div className="space-y-4">
          <div className="flex items-start gap-3 p-4 bg-red-50 border border-red-200 rounded-lg">
            <AlertTriangle className="h-5 w-5 text-red-600 mt-0.5" />
            <div>
              <div className="font-medium text-red-900">High Priority Actions</div>
              <div className="text-sm text-red-700 mt-1">
                {riskLevelData.high || 0} high-risk items require immediate attention and mitigation plans.
              </div>
            </div>
          </div>

          <div className="flex items-start gap-3 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <Activity className="h-5 w-5 text-yellow-600 mt-0.5" />
            <div>
              <div className="font-medium text-yellow-900">Medium Priority Review</div>
              <div className="text-sm text-yellow-700 mt-1">
                {riskLevelData.medium || 0} medium-risk items should be reviewed and monitored regularly.
              </div>
            </div>
          </div>

          <div className="flex items-start gap-3 p-4 bg-green-50 border border-green-200 rounded-lg">
            <Shield className="h-5 w-5 text-green-600 mt-0.5" />
            <div>
              <div className="font-medium text-green-900">Acceptable Risk Level</div>
              <div className="text-sm text-green-700 mt-1">
                {riskLevelData.low || 0} low-risk items are within acceptable tolerance levels.
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

// Risk Appetite Dashboard Component
function RiskAppetiteDashboard({ risks }: { risks: Risk[] }) {
  // Определяем риск-аппетит организации (можно загрузить из настроек)
  const riskAppetite = {
    operational: { min: 0, max: 6, tolerance: 7 },
    financial: { min: 0, max: 5, tolerance: 6 },
    strategic: { min: 0, max: 7, tolerance: 8 },
    compliance: { min: 0, max: 3, tolerance: 4 }
  }

  const getCategoryRisks = (category: string) =>
    risks.filter(r => r.category === category)

  const getAppetiteStatus = (category: string, score: number) => {
    const appetite = riskAppetite[category as keyof typeof riskAppetite]
    if (score <= appetite.max) return 'within'
    if (score <= appetite.tolerance) return 'tolerance'
    return 'exceeded'
  }

  return (
    <div className="space-y-6">
      {/* Risk Appetite Overview */}
      <div className="bg-white rounded-lg border shadow-sm p-6">
        <h3 className="text-lg font-semibold mb-4">Risk Appetite Statement</h3>
        <p className="text-gray-600 mb-6">
          Organization's defined risk appetite levels and current risk exposure across different categories
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {Object.entries(riskAppetite).map(([category, limits]) => {
            const categoryRisks = getCategoryRisks(category)
            const avgScore = categoryRisks.length
              ? categoryRisks.reduce((sum, r) => sum + r.riskScore, 0) / categoryRisks.length
              : 0

            return (
              <div key={category} className="border rounded-lg p-4">
                <h4 className="font-medium text-gray-900 capitalize mb-3">{category} Risk</h4>

                {/* Visual representation */}
                <div className="relative mb-3">
                  <div className="h-8 bg-gray-100 rounded-full overflow-hidden">
                    {/* Appetite zone */}
                    <div
                      className="absolute h-full bg-green-200"
                      style={{ width: `${limits.max * 10}%` }}
                    />
                    {/* Tolerance zone */}
                    <div
                      className="absolute h-full bg-yellow-200"
                      style={{ left: `${limits.max * 10}%`, width: `${(limits.tolerance - limits.max) * 10}%` }}
                    />
                    {/* Exceeded zone */}
                    <div
                      className="absolute h-full bg-red-200"
                      style={{ left: `${limits.tolerance * 10}%`, width: `${(10 - limits.tolerance) * 10}%` }}
                    />
                    {/* Current position marker */}
                    <div
                      className="absolute top-0 h-full w-1 bg-blue-600"
                      style={{ left: `${avgScore * 10}%` }}
                    >
                      <div className="absolute -top-6 -left-4 text-xs font-medium text-blue-600">
                        {avgScore.toFixed(1)}
                      </div>
                    </div>
                  </div>
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>0</span>
                    <span>Appetite ({limits.max})</span>
                    <span>Tolerance ({limits.tolerance})</span>
                    <span>10</span>
                  </div>
                </div>

                {/* Status */}
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">
                    {categoryRisks.length} risk(s)
                  </span>
                  <span className={cn(
                    "text-sm font-medium",
                    getAppetiteStatus(category, avgScore) === 'within' && "text-green-600",
                    getAppetiteStatus(category, avgScore) === 'tolerance' && "text-yellow-600",
                    getAppetiteStatus(category, avgScore) === 'exceeded' && "text-red-600"
                  )}>
                    {getAppetiteStatus(category, avgScore) === 'within' && '✓ Within Appetite'}
                    {getAppetiteStatus(category, avgScore) === 'tolerance' && '⚠ In Tolerance'}
                    {getAppetiteStatus(category, avgScore) === 'exceeded' && '✗ Exceeded'}
                  </span>
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Risk Appetite Actions */}
      <div className="bg-white rounded-lg border shadow-sm p-6">
        <h3 className="text-lg font-semibold mb-4">Risk Appetite Actions</h3>
        <div className="space-y-3">
          {Object.entries(riskAppetite).map(([category]) => {
            const categoryRisks = getCategoryRisks(category)
            const avgScore = categoryRisks.length
              ? categoryRisks.reduce((sum, r) => sum + r.riskScore, 0) / categoryRisks.length
              : 0
            const status = getAppetiteStatus(category, avgScore)

            if (status === 'exceeded') {
              return (
                <div key={category} className="p-4 bg-red-50 border border-red-200 rounded-lg">
                  <div className="flex items-start gap-3">
                    <AlertTriangle className="h-5 w-5 text-red-600 mt-0.5" />
                    <div>
                      <div className="font-medium text-red-900 capitalize">{category} Risk Exceeded</div>
                      <div className="text-sm text-red-700 mt-1">
                        Immediate action required. Current average score ({avgScore.toFixed(1)}) exceeds tolerance level.
                        Review and implement additional controls.
                      </div>
                    </div>
                  </div>
                </div>
              )
            }
            return null
          })}
        </div>
      </div>
    </div>
  )
}

// FAIR Analysis Component
function FAIRAnalysis({ risks }: { risks: Risk[] }) {
  const [selectedRisk, setSelectedRisk] = useState<Risk | null>(null)
  const [fairAnalysis, setFairAnalysis] = useState({
    // Frequency factors
    contactFrequency: 5,
    probabilityOfAction: 5,
    threatCapability: 5,
    controlStrength: 5,

    // Magnitude factors
    primaryLoss: 5,
    secondaryLossFreq: 5,
    secondaryLossMag: 5
  })

  // Monte Carlo simulation state
  const [simulationResults, setSimulationResults] = useState<SimulationResult | null>(null)
  const [portfolioResults, setPortfolioResults] = useState<AggregatedSimulationResult | null>(null)
  const [isSimulating, setIsSimulating] = useState(false)

  // Run Monte Carlo simulation for selected risk
  const runSingleRiskSimulation = async () => {
    if (!selectedRisk) {
      toast.error('Please select a risk first')
      return
    }

    setIsSimulating(true)
    try {
      const result = await monteCarloSimulation.runSimulation(
        selectedRisk,
        {
          simulations: 10000,
          confidenceLevel: 0.95,
          timeHorizon: 12
        }
      )
      setSimulationResults(result)
      toast.success('Simulation completed successfully')
    } catch (error) {
      console.error('Simulation failed:', error)
      toast.error('Failed to run simulation')
    } finally {
      setIsSimulating(false)
    }
  }

  // Run portfolio simulation for all risks
  const runPortfolioSimulation = async () => {
    if (!risks || risks.length === 0) {
      toast.error('No risks available for portfolio simulation')
      return
    }

    setIsSimulating(true)
    try {
      const result = await monteCarloSimulation.runPortfolioSimulation(
        risks,
        {
          simulations: 10000,
          confidenceLevel: 0.95,
          timeHorizon: 12
        }
      )
      setPortfolioResults(result)
      toast.success('Portfolio simulation completed successfully')
    } catch (error) {
      console.error('Portfolio simulation failed:', error)
      toast.error('Failed to run portfolio simulation')
    } finally {
      setIsSimulating(false)
    }
  }

  const calculateLEF = () => {
    // Loss Event Frequency = Contact Frequency × Probability of Action × (Threat Capability - Control Strength)
    const vulnScore = Math.max(0, fairAnalysis.threatCapability - fairAnalysis.controlStrength)
    return (fairAnalysis.contactFrequency * fairAnalysis.probabilityOfAction * vulnScore) / 100
  }

  const calculateLossMagnitude = () => {
    // Loss Magnitude = Primary Loss + (Secondary Loss Frequency × Secondary Loss Magnitude)
    return fairAnalysis.primaryLoss + (fairAnalysis.secondaryLossFreq * fairAnalysis.secondaryLossMag) / 10
  }

  const calculateAnnualizedLoss = () => {
    return calculateLEF() * calculateLossMagnitude() * 100000 // Base value in currency
  }

  return (
    <div className="space-y-6">
      {/* FAIR Methodology Overview */}
      <div className="bg-white rounded-lg border shadow-sm p-6">
        <h3 className="text-lg font-semibold mb-4">FAIR (Factor Analysis of Information Risk)</h3>
        <p className="text-gray-600 mb-4">
          Quantitative risk analysis methodology that helps organizations understand, analyze, and quantify information risk in financial terms.
        </p>

        {/* Risk Selection */}
        <div className="mb-6">
          <Label>Select Risk for FAIR Analysis</Label>
          <Select
            value={selectedRisk?.id || ''}
            onValueChange={(value) => setSelectedRisk(risks.find(r => r.id === value) || null)}
          >
            <SelectTrigger className="w-full">
              <SelectValue placeholder="Choose a risk to analyze" />
            </SelectTrigger>
            <SelectContent>
              {risks.map(risk => (
                <SelectItem key={risk.id} value={risk.id}>
                  {risk.title} (Score: {risk.riskScore})
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {selectedRisk && (
          <>
            {/* FAIR Factors Input */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Frequency Factors */}
              <div className="space-y-4">
                <h4 className="font-medium text-gray-900">Frequency Factors</h4>

                <div className="space-y-3">
                  <div>
                    <Label className="text-sm">Contact Frequency (1-10)</Label>
                    <Slider
                      value={[fairAnalysis.contactFrequency]}
                      onValueChange={(value) => setFairAnalysis({...fairAnalysis, contactFrequency: value[0]})}
                      max={10}
                      min={1}
                      step={1}
                      className="mt-2"
                    />
                    <div className="text-xs text-gray-500 mt-1">
                      How often threat agents come into contact: {fairAnalysis.contactFrequency}
                    </div>
                  </div>

                  <div>
                    <Label className="text-sm">Probability of Action (1-10)</Label>
                    <Slider
                      value={[fairAnalysis.probabilityOfAction]}
                      onValueChange={(value) => setFairAnalysis({...fairAnalysis, probabilityOfAction: value[0]})}
                      max={10}
                      min={1}
                      step={1}
                      className="mt-2"
                    />
                    <div className="text-xs text-gray-500 mt-1">
                      Likelihood threat agent will act: {fairAnalysis.probabilityOfAction}
                    </div>
                  </div>

                  <div>
                    <Label className="text-sm">Threat Capability (1-10)</Label>
                    <Slider
                      value={[fairAnalysis.threatCapability]}
                      onValueChange={(value) => setFairAnalysis({...fairAnalysis, threatCapability: value[0]})}
                      max={10}
                      min={1}
                      step={1}
                      className="mt-2"
                    />
                    <div className="text-xs text-gray-500 mt-1">
                      Threat agent's ability to exploit: {fairAnalysis.threatCapability}
                    </div>
                  </div>

                  <div>
                    <Label className="text-sm">Control Strength (1-10)</Label>
                    <Slider
                      value={[fairAnalysis.controlStrength]}
                      onValueChange={(value) => setFairAnalysis({...fairAnalysis, controlStrength: value[0]})}
                      max={10}
                      min={1}
                      step={1}
                      className="mt-2"
                    />
                    <div className="text-xs text-gray-500 mt-1">
                      Effectiveness of controls: {fairAnalysis.controlStrength}
                    </div>
                  </div>
                </div>
              </div>

              {/* Magnitude Factors */}
              <div className="space-y-4">
                <h4 className="font-medium text-gray-900">Magnitude Factors</h4>

                <div className="space-y-3">
                  <div>
                    <Label className="text-sm">Primary Loss Magnitude (1-10)</Label>
                    <Slider
                      value={[fairAnalysis.primaryLoss]}
                      onValueChange={(value) => setFairAnalysis({...fairAnalysis, primaryLoss: value[0]})}
                      max={10}
                      min={1}
                      step={1}
                      className="mt-2"
                    />
                    <div className="text-xs text-gray-500 mt-1">
                      Direct loss from the event: {fairAnalysis.primaryLoss}
                    </div>
                  </div>

                  <div>
                    <Label className="text-sm">Secondary Loss Frequency (1-10)</Label>
                    <Slider
                      value={[fairAnalysis.secondaryLossFreq]}
                      onValueChange={(value) => setFairAnalysis({...fairAnalysis, secondaryLossFreq: value[0]})}
                      max={10}
                      min={1}
                      step={1}
                      className="mt-2"
                    />
                    <div className="text-xs text-gray-500 mt-1">
                      Likelihood of secondary losses: {fairAnalysis.secondaryLossFreq}
                    </div>
                  </div>

                  <div>
                    <Label className="text-sm">Secondary Loss Magnitude (1-10)</Label>
                    <Slider
                      value={[fairAnalysis.secondaryLossMag]}
                      onValueChange={(value) => setFairAnalysis({...fairAnalysis, secondaryLossMag: value[0]})}
                      max={10}
                      min={1}
                      step={1}
                      className="mt-2"
                    />
                    <div className="text-xs text-gray-500 mt-1">
                      Reputation, legal, competitive losses: {fairAnalysis.secondaryLossMag}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* FAIR Results */}
            <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <h4 className="font-medium text-blue-900 mb-3">FAIR Analysis Results</h4>
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <div className="text-sm text-blue-700">Loss Event Frequency</div>
                  <div className="text-2xl font-bold text-blue-900">{calculateLEF().toFixed(2)}</div>
                  <div className="text-xs text-blue-600">events/year</div>
                </div>
                <div>
                  <div className="text-sm text-blue-700">Loss Magnitude Score</div>
                  <div className="text-2xl font-bold text-blue-900">{calculateLossMagnitude().toFixed(1)}</div>
                  <div className="text-xs text-blue-600">severity index</div>
                </div>
                <div>
                  <div className="text-sm text-blue-700">Annualized Loss Expectancy</div>
                  <div className="text-2xl font-bold text-blue-900">
                    ${calculateAnnualizedLoss().toLocaleString()}
                  </div>
                  <div className="text-xs text-blue-600">per year</div>
                </div>
              </div>
            </div>
          </>
        )}
      </div>

      {/* Monte Carlo Simulation */}
      <div className="bg-white rounded-lg border shadow-sm p-6">
        <h3 className="text-lg font-semibold mb-4">Monte Carlo Simulation</h3>
        <p className="text-gray-600 mb-4">
          Run probabilistic simulations to understand the range of possible outcomes
        </p>

        <div className="space-y-4">
          <div className="flex gap-3">
            <Button
              onClick={runSingleRiskSimulation}
              disabled={!selectedRisk || isSimulating}
              className="flex-1"
            >
              {isSimulating ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Running Simulation...
                </>
              ) : (
                <>
                  <Activity className="h-4 w-4 mr-2" />
                  Simulate Selected Risk (10,000 iterations)
                </>
              )}
            </Button>

            <Button
              onClick={runPortfolioSimulation}
              disabled={risks.length === 0 || isSimulating}
              variant="outline"
              className="flex-1"
            >
              {isSimulating ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Running Portfolio...
                </>
              ) : (
                <>
                  <TrendingUp className="h-4 w-4 mr-2" />
                  Simulate Full Portfolio
                </>
              )}
            </Button>
          </div>

          {/* Single Risk Simulation Results */}
          {simulationResults && (
            <div className="mt-6 space-y-4">
              <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-4 rounded-lg">
                <h4 className="font-semibold text-gray-900 mb-3">Simulation Results</h4>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                  <div>
                    <div className="text-xs text-gray-600">Mean Risk Score</div>
                    <div className="text-xl font-bold text-blue-900">
                      {simulationResults.statistics.mean.toFixed(2)}
                    </div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-600">95% Value at Risk</div>
                    <div className="text-xl font-bold text-red-600">
                      {simulationResults.valueAtRisk.toFixed(2)}
                    </div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-600">Probability of High Risk</div>
                    <div className="text-xl font-bold text-orange-600">
                      {(simulationResults.probabilityOfOccurrence * 100).toFixed(1)}%
                    </div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-600">Std Deviation</div>
                    <div className="text-xl font-bold text-gray-700">
                      ±{simulationResults.statistics.standardDeviation.toFixed(2)}
                    </div>
                  </div>
                </div>

                {/* Distribution Chart */}
                <div className="mt-4">
                  <div className="text-sm text-gray-600 mb-2">Risk Score Distribution</div>
                  <div className="h-32 flex items-end gap-1">
                    {simulationResults.distribution.slice(0, 20).map((bin, i) => (
                      <div
                        key={i}
                        className="flex-1 bg-blue-500 hover:bg-blue-600 transition-colors rounded-t"
                        style={{
                          height: `${(bin.probability * 100 * 4)}%`,
                          opacity: 0.7 + (bin.probability * 3)
                        }}
                        title={`Value: ${bin.value}, Frequency: ${bin.frequency}`}
                      />
                    ))}
                  </div>
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>{simulationResults.statistics.min.toFixed(1)}</span>
                    <span>Risk Score</span>
                    <span>{simulationResults.statistics.max.toFixed(1)}</span>
                  </div>
                </div>

                {/* Percentiles */}
                <div className="mt-4 p-3 bg-white/50 rounded">
                  <div className="text-sm font-medium text-gray-700 mb-2">Risk Percentiles</div>
                  <div className="grid grid-cols-3 gap-2 text-xs">
                    <div>P5: <span className="font-semibold">{simulationResults.statistics.percentiles.p5.toFixed(2)}</span></div>
                    <div>P50: <span className="font-semibold">{simulationResults.statistics.percentiles.p50.toFixed(2)}</span></div>
                    <div>P95: <span className="font-semibold">{simulationResults.statistics.percentiles.p95.toFixed(2)}</span></div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Portfolio Simulation Results */}
          {portfolioResults && (
            <div className="mt-6 space-y-4">
              <div className="bg-gradient-to-r from-purple-50 to-pink-50 p-4 rounded-lg">
                <h4 className="font-semibold text-gray-900 mb-3">Portfolio Analysis Results</h4>

                <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-4">
                  <div>
                    <div className="text-xs text-gray-600">Total Portfolio Risk</div>
                    <div className="text-xl font-bold text-purple-900">
                      {portfolioResults.aggregatedLoss.mean.toFixed(2)}
                    </div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-600">95% Confidence Interval</div>
                    <div className="text-xl font-bold text-purple-700">
                      {portfolioResults.confidence.lowerBound.toFixed(1)} - {portfolioResults.confidence.upperBound.toFixed(1)}
                    </div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-600">Correlation Impact</div>
                    <div className="text-xl font-bold text-pink-600">
                      {portfolioResults.correlationImpact > 0 ? '+' : ''}{portfolioResults.correlationImpact.toFixed(1)}%
                    </div>
                  </div>
                </div>

                {/* Top Risk Contributors */}
                <div className="mt-4">
                  <div className="text-sm font-medium text-gray-700 mb-2">Top Risk Contributors</div>
                  <div className="space-y-2">
                    {portfolioResults.topRiskContributors.map((contributor, i) => (
                      <div key={contributor.riskId} className="flex items-center gap-2">
                        <div className="text-xs font-medium text-gray-500 w-4">#{i+1}</div>
                        <div className="flex-1">
                          <div className="flex items-center justify-between">
                            <span className="text-sm font-medium">{contributor.riskTitle}</span>
                            <span className="text-sm font-bold text-purple-600">
                              {contributor.contribution.toFixed(1)}%
                            </span>
                          </div>
                          <div className="h-2 bg-gray-200 rounded-full mt-1">
                            <div
                              className="h-full bg-purple-500 rounded-full"
                              style={{ width: `${contributor.contribution}%` }}
                            />
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Recommendations */}
                {portfolioResults.recommendations.length > 0 && (
                  <div className="mt-4 p-3 bg-white/50 rounded">
                    <div className="text-sm font-medium text-gray-700 mb-2">AI Recommendations</div>
                    <ul className="space-y-1">
                      {portfolioResults.recommendations.map((rec, i) => (
                        <li key={i} className="text-xs text-gray-600 flex items-start">
                          <ChevronRight className="h-3 w-3 mt-0.5 mr-1 text-purple-500 flex-shrink-0" />
                          {rec}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Treatment Plans */}
      <div className="bg-white rounded-lg border shadow-sm p-6">
        <h3 className="text-lg font-semibold mb-4">Treatment Plans</h3>
        <div className="space-y-3">
          <Button variant="outline" className="w-full justify-start">
            <Plus className="h-4 w-4 mr-2" />
            Create Treatment Plan for Selected Risk
          </Button>
          <div className="text-sm text-gray-500">
            Manage risk treatment strategies: Accept, Avoid, Transfer, or Mitigate
          </div>
        </div>
      </div>
    </div>
  )
}

