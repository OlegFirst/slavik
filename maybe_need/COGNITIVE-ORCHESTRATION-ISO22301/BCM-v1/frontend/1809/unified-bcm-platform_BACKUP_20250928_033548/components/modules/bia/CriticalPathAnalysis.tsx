'use client'

import React, { useState, useEffect, useMemo, useCallback } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  ComposedChart,
  Bar,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  BarChart,
  Cell,
  PieChart,
  Pie,
  Treemap
} from 'recharts'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Separator } from '@/components/ui/separator'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Slider } from '@/components/ui/slider'
import { Switch } from '@/components/ui/switch'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import {
  AlertTriangle,
  Clock,
  TrendingUp,
  Download,
  Settings,
  Eye,
  Play,
  Pause,
  RotateCcw,
  Zap,
  Target,
  DollarSign,
  Users,
  Building,
  Activity,
  ArrowRight,
  Calendar,
  FileSpreadsheet,
  ChevronRight,
  ChevronDown,
  Maximize2,
  RefreshCw,
  BarChart3,
  Network,
  Info,
  CheckCircle2,
  XCircle,
  AlertCircle
} from 'lucide-react'
import { biaAPI, CriticalPath, OptimizationOpportunity, BIAResult } from '@/services/bia-api'

// Enhanced Types for Critical Path Analysis
interface CriticalPathTask {
  id: string
  name: string
  functionId: string
  startTime: number
  duration: number
  endTime: number
  dependencies: string[]
  criticalityLevel: 'low' | 'medium' | 'high' | 'critical'
  resourceRequirements: ResourceRequirement[]
  parallelTracks: string[]
  status: 'pending' | 'in_progress' | 'completed' | 'blocked'
  riskFactors: RiskFactor[]
  optimizationPotential: number
}

interface ResourceRequirement {
  type: 'human' | 'technology' | 'facility' | 'financial'
  name: string
  quantity: number
  availability: number
  cost: number
  criticality: 'low' | 'medium' | 'high' | 'critical'
}

interface RiskFactor {
  id: string
  type: 'dependency' | 'resource' | 'timing' | 'external'
  description: string
  probability: number
  impact: number
  mitigation: string
}

interface ScenarioModel {
  id: string
  name: string
  description: string
  modifications: {
    taskId: string
    newDuration: number
    newResources?: ResourceRequirement[]
  }[]
  projectedImpact: {
    totalRTO: number
    costSavings: number
    riskReduction: number
    resourceOptimization: number
  }
}

interface GanttData {
  taskId: string
  taskName: string
  start: number
  end: number
  duration: number
  progress: number
  criticality: string
  track: number
  dependencies: string[]
  resources: string
}

export default function CriticalPathAnalysis() {
  // State Management
  const [selectedPath, setSelectedPath] = useState<string>('')
  const [viewMode, setViewMode] = useState<'timeline' | 'gantt' | 'resources' | 'optimization'>('timeline')
  const [timeScale, setTimeScale] = useState<'hours' | 'days' | 'weeks'>('hours')
  const [selectedScenario, setSelectedScenario] = useState<string>('')
  const [simulationRunning, setSimulationRunning] = useState(false)
  const [draggedTask, setDraggedTask] = useState<string | null>(null)
  const [showOptimizationDialog, setShowOptimizationDialog] = useState(false)
  const [selectedOptimization, setSelectedOptimization] = useState<OptimizationOpportunity | null>(null)
  const [customScenario, setCustomScenario] = useState<ScenarioModel | null>(null)
  const [expandedSections, setExpandedSections] = useState<string[]>(['overview'])

  // Data Fetching
  const { data: criticalPaths, isLoading: pathsLoading, refetch: refetchPaths } = useQuery({
    queryKey: ['criticalPaths'],
    queryFn: () => biaAPI.getCriticalPaths(),
  })

  const { data: biaResults, isLoading: resultsLoading } = useQuery({
    queryKey: ['biaResults'],
    queryFn: () => biaAPI.getBIAResults(),
  })

  // Transform data for visualization
  const transformedData = useMemo(() => {
    if (!criticalPaths || !biaResults) return []

    const selectedPathData = criticalPaths.find(path => path.id === selectedPath) || criticalPaths[0]
    if (!selectedPathData) return []

    const tasks: CriticalPathTask[] = selectedPathData.functions.map((functionName, index) => {
      const biaFunction = biaResults.find(r => r.businessFunction === functionName)

      return {
        id: `task-${index}`,
        name: functionName,
        functionId: biaFunction?.id || `func-${index}`,
        startTime: index * 2, // 2-hour intervals for demo
        duration: biaFunction?.rto || 4,
        endTime: (index * 2) + (biaFunction?.rto || 4),
        dependencies: index > 0 ? [`task-${index - 1}`] : [],
        criticalityLevel: biaFunction?.criticalityLevel || 'medium',
        resourceRequirements: [
          {
            type: 'human',
            name: 'Recovery Team',
            quantity: Math.ceil((biaFunction?.rto || 4) / 2),
            availability: 0.8,
            cost: 1000,
            criticality: biaFunction?.criticalityLevel || 'medium'
          },
          {
            type: 'technology',
            name: 'IT Resources',
            quantity: 1,
            availability: 0.9,
            cost: 5000,
            criticality: biaFunction?.criticalityLevel || 'medium'
          }
        ],
        parallelTracks: [],
        status: 'pending',
        riskFactors: [
          {
            id: `risk-${index}`,
            type: 'dependency',
            description: 'Dependent on previous function recovery',
            probability: 0.3,
            impact: 0.7,
            mitigation: 'Implement parallel recovery processes'
          }
        ],
        optimizationPotential: Math.random() * 50 + 10 // 10-60% optimization potential
      }
    })

    return tasks
  }, [criticalPaths, biaResults, selectedPath])

  // Gantt Chart Data
  const ganttData: GanttData[] = useMemo(() => {
    return transformedData.map((task, index) => ({
      taskId: task.id,
      taskName: task.name,
      start: task.startTime,
      end: task.endTime,
      duration: task.duration,
      progress: 0,
      criticality: task.criticalityLevel,
      track: index,
      dependencies: task.dependencies,
      resources: task.resourceRequirements.map(r => r.name).join(', ')
    }))
  }, [transformedData])

  // Calculate Critical Path Metrics
  const pathMetrics = useMemo(() => {
    if (!transformedData.length) return null

    const totalDuration = Math.max(...transformedData.map(t => t.endTime))
    const criticalTasks = transformedData.filter(t => t.criticalityLevel === 'critical')
    const bottleneck = transformedData.reduce((prev, current) =>
      prev.duration > current.duration ? prev : current
    )

    const totalCost = transformedData.reduce((sum, task) =>
      sum + task.resourceRequirements.reduce((taskSum, resource) =>
        taskSum + (resource.cost * resource.quantity), 0
      ), 0
    )

    const optimizationPotential = transformedData.reduce((sum, task) =>
      sum + task.optimizationPotential, 0
    ) / transformedData.length

    return {
      totalDuration,
      criticalTasks: criticalTasks.length,
      bottleneck: bottleneck.name,
      totalCost,
      optimizationPotential,
      parallelOpportunities: transformedData.filter(t => t.dependencies.length === 0).length - 1,
      riskScore: transformedData.reduce((sum, task) =>
        sum + task.riskFactors.reduce((riskSum, risk) =>
          riskSum + (risk.probability * risk.impact), 0
        ), 0
      ) / transformedData.length
    }
  }, [transformedData])

  // Color schemes for visualization
  const criticalityColors = {
    low: '#10B981',
    medium: '#F59E0B',
    high: '#EF4444',
    critical: '#DC2626'
  }

  const trackColors = [
    '#3B82F6', '#8B5CF6', '#10B981', '#F59E0B', '#EF4444', '#6366F1', '#EC4899', '#14B8A6'
  ]

  // Event Handlers
  const handleTaskDragStart = useCallback((taskId: string) => {
    setDraggedTask(taskId)
  }, [])

  const handleTaskDrop = useCallback((targetIndex: number) => {
    if (!draggedTask) return

    // Implement task reordering logic
    console.log(`Moving task ${draggedTask} to position ${targetIndex}`)
    setDraggedTask(null)
  }, [draggedTask])

  const handleOptimizationApply = useCallback((optimization: OptimizationOpportunity) => {
    console.log('Applying optimization:', optimization)
    // Implement optimization application logic
    setShowOptimizationDialog(false)
  }, [])

  const handleScenarioRun = useCallback(() => {
    setSimulationRunning(true)

    // Simulate scenario execution
    setTimeout(() => {
      setSimulationRunning(false)
    }, 3000)
  }, [])

  const exportToCsv = useCallback(() => {
    if (!criticalPaths) return

    const csvContent = [
      ['Path ID', 'Path Name', 'Task Name', 'Start Time', 'Duration', 'End Time', 'Criticality', 'Resources', 'Cost'],
      ...transformedData.map(task => [
        selectedPath,
        criticalPaths.find(p => p.id === selectedPath)?.name || '',
        task.name,
        task.startTime.toString(),
        task.duration.toString(),
        task.endTime.toString(),
        task.criticalityLevel,
        task.resourceRequirements.map(r => r.name).join('; '),
        task.resourceRequirements.reduce((sum, r) => sum + (r.cost * r.quantity), 0).toString()
      ])
    ].map(row => row.join(',')).join('\n')

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)
    link.setAttribute('href', url)
    link.setAttribute('download', `critical_path_analysis_${new Date().toISOString().split('T')[0]}.csv`)
    link.style.visibility = 'hidden'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }, [criticalPaths, transformedData, selectedPath])

  const toggleSection = useCallback((section: string) => {
    setExpandedSections(prev =>
      prev.includes(section)
        ? prev.filter(s => s !== section)
        : [...prev, section]
    )
  }, [])

  if (pathsLoading || resultsLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-4" />
          <p>Loading critical path analysis...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Critical Path Analysis</h2>
          <p className="text-muted-foreground mt-2">
            Analyze recovery sequences and optimize business continuity planning
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button onClick={() => refetchPaths()} variant="outline" size="sm">
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
          <Button onClick={exportToCsv} variant="outline" size="sm">
            <Download className="h-4 w-4 mr-2" />
            Export CSV
          </Button>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="sm">
                <Settings className="h-4 w-4 mr-2" />
                Options
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent>
              <DropdownMenuLabel>View Options</DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={() => setViewMode('timeline')}>
                <BarChart3 className="h-4 w-4 mr-2" />
                Timeline View
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => setViewMode('gantt')}>
                <Calendar className="h-4 w-4 mr-2" />
                Gantt Chart
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => setViewMode('resources')}>
                <Users className="h-4 w-4 mr-2" />
                Resource View
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => setViewMode('optimization')}>
                <Target className="h-4 w-4 mr-2" />
                Optimization
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>

      {/* Critical Path Selection */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Network className="h-5 w-5" />
            Select Critical Path
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <Label htmlFor="path-select">Critical Path</Label>
              <Select value={selectedPath} onValueChange={setSelectedPath}>
                <SelectTrigger>
                  <SelectValue placeholder="Select a critical path" />
                </SelectTrigger>
                <SelectContent>
                  {criticalPaths?.map((path) => (
                    <SelectItem key={path.id} value={path.id}>
                      {path.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="time-scale">Time Scale</Label>
              <Select value={timeScale} onValueChange={(value: any) => setTimeScale(value)}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="hours">Hours</SelectItem>
                  <SelectItem value="days">Days</SelectItem>
                  <SelectItem value="weeks">Weeks</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="view-mode">View Mode</Label>
              <Select value={viewMode} onValueChange={(value: any) => setViewMode(value)}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="timeline">Timeline</SelectItem>
                  <SelectItem value="gantt">Gantt Chart</SelectItem>
                  <SelectItem value="resources">Resources</SelectItem>
                  <SelectItem value="optimization">Optimization</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Path Metrics Overview */}
      {pathMetrics && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center gap-2">
                <Clock className="h-5 w-5 text-blue-500" />
                <div>
                  <p className="text-sm text-muted-foreground">Total Recovery Time</p>
                  <p className="text-2xl font-bold">{pathMetrics.totalDuration}h</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center gap-2">
                <AlertTriangle className="h-5 w-5 text-red-500" />
                <div>
                  <p className="text-sm text-muted-foreground">Critical Tasks</p>
                  <p className="text-2xl font-bold">{pathMetrics.criticalTasks}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center gap-2">
                <DollarSign className="h-5 w-5 text-green-500" />
                <div>
                  <p className="text-sm text-muted-foreground">Recovery Cost</p>
                  <p className="text-2xl font-bold">${(pathMetrics.totalCost / 1000).toFixed(0)}K</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5 text-purple-500" />
                <div>
                  <p className="text-sm text-muted-foreground">Optimization Potential</p>
                  <p className="text-2xl font-bold">{pathMetrics.optimizationPotential.toFixed(0)}%</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Main Visualization */}
      <Tabs value={viewMode} onValueChange={(value: any) => setViewMode(value)}>
        <TabsList>
          <TabsTrigger value="timeline">Timeline</TabsTrigger>
          <TabsTrigger value="gantt">Gantt Chart</TabsTrigger>
          <TabsTrigger value="resources">Resources</TabsTrigger>
          <TabsTrigger value="optimization">Optimization</TabsTrigger>
        </TabsList>

        <TabsContent value="timeline" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Recovery Timeline</CardTitle>
              <CardDescription>
                Visual timeline showing the recovery sequence and parallel tracks
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={400}>
                <ComposedChart data={ganttData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    dataKey="start"
                    type="number"
                    domain={[0, 'dataMax']}
                    label={{ value: `Time (${timeScale})`, position: 'insideBottom', offset: -5 }}
                  />
                  <YAxis
                    dataKey="track"
                    type="number"
                    domain={[0, transformedData.length]}
                    tickFormatter={(value) => `Track ${value + 1}`}
                  />
                  <Tooltip
                    formatter={(value, name, props) => [
                      `${value}${timeScale === 'hours' ? 'h' : timeScale === 'days' ? 'd' : 'w'}`,
                      name
                    ]}
                    labelFormatter={(label) => `Time: ${label}${timeScale === 'hours' ? 'h' : timeScale === 'days' ? 'd' : 'w'}`}
                  />
                  <Legend />
                  <Bar
                    dataKey="duration"
                    fill="#3B82F6"
                    name="Duration"
                  >
                    {ganttData.map((entry, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={criticalityColors[entry.criticality as keyof typeof criticalityColors]}
                      />
                    ))}
                  </Bar>
                  <Line
                    type="monotone"
                    dataKey="progress"
                    stroke="#10B981"
                    strokeWidth={2}
                    name="Progress"
                  />
                </ComposedChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Task Details */}
          <Card>
            <CardHeader>
              <CardTitle>Task Breakdown</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {transformedData.map((task, index) => (
                  <div
                    key={task.id}
                    className="border rounded-lg p-4 hover:bg-muted/50 transition-colors"
                    draggable
                    onDragStart={() => handleTaskDragStart(task.id)}
                    onDrop={() => handleTaskDrop(index)}
                    onDragOver={(e) => e.preventDefault()}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <Badge
                          variant={task.criticalityLevel === 'critical' ? 'destructive' : 'secondary'}
                        >
                          {task.criticalityLevel}
                        </Badge>
                        <h4 className="font-semibold">{task.name}</h4>
                      </div>
                      <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <Clock className="h-4 w-4" />
                        {task.duration}h
                        <ArrowRight className="h-4 w-4" />
                        <span>T+{task.endTime}h</span>
                      </div>
                    </div>

                    <div className="mt-3 grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                      <div>
                        <p className="font-medium mb-1">Resources Required</p>
                        {task.resourceRequirements.map((resource, idx) => (
                          <p key={idx} className="text-muted-foreground">
                            {resource.name}: {resource.quantity}x (${resource.cost})
                          </p>
                        ))}
                      </div>

                      <div>
                        <p className="font-medium mb-1">Dependencies</p>
                        {task.dependencies.length > 0 ? (
                          task.dependencies.map((dep, idx) => (
                            <p key={idx} className="text-muted-foreground">{dep}</p>
                          ))
                        ) : (
                          <p className="text-muted-foreground">None</p>
                        )}
                      </div>

                      <div>
                        <p className="font-medium mb-1">Optimization Potential</p>
                        <div className="flex items-center gap-2">
                          <Progress value={task.optimizationPotential} className="flex-1" />
                          <span className="text-xs">{task.optimizationPotential.toFixed(0)}%</span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="gantt" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Gantt Chart View</CardTitle>
              <CardDescription>
                Detailed project timeline with dependencies and resource allocation
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={500}>
                <BarChart
                  data={ganttData}
                  layout="horizontal"
                  margin={{ top: 20, right: 30, left: 120, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    type="number"
                    domain={[0, 'dataMax']}
                    label={{ value: `Time (${timeScale})`, position: 'insideBottom', offset: -5 }}
                  />
                  <YAxis
                    type="category"
                    dataKey="taskName"
                    width={100}
                  />
                  <Tooltip
                    formatter={(value: any, name: string) => [
                      `${value}${timeScale === 'hours' ? 'h' : timeScale === 'days' ? 'd' : 'w'}`,
                      name
                    ]}
                  />
                  <Legend />
                  <Bar dataKey="start" stackId="a" fill="#E5E7EB" name="Start Time" />
                  <Bar dataKey="duration" stackId="a" name="Duration">
                    {ganttData.map((entry, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={criticalityColors[entry.criticality as keyof typeof criticalityColors]}
                      />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="resources" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Resource Allocation Chart */}
            <Card>
              <CardHeader>
                <CardTitle>Resource Allocation</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={transformedData.flatMap(task =>
                        task.resourceRequirements.map(resource => ({
                          name: resource.name,
                          value: resource.cost * resource.quantity,
                          type: resource.type
                        }))
                      )}
                      cx="50%"
                      cy="50%"
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    >
                      {transformedData.flatMap(task => task.resourceRequirements).map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={trackColors[index % trackColors.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value: any) => [`$${value.toLocaleString()}`, 'Cost']} />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Resource Utilization */}
            <Card>
              <CardHeader>
                <CardTitle>Resource Utilization</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {Array.from(new Set(transformedData.flatMap(task =>
                    task.resourceRequirements.map(r => r.type)
                  ))).map((resourceType) => {
                    const resources = transformedData.flatMap(task =>
                      task.resourceRequirements.filter(r => r.type === resourceType)
                    )
                    const totalQuantity = resources.reduce((sum, r) => sum + r.quantity, 0)
                    const avgAvailability = resources.reduce((sum, r) => sum + r.availability, 0) / resources.length

                    return (
                      <div key={resourceType}>
                        <div className="flex justify-between items-center mb-2">
                          <span className="capitalize font-medium">{resourceType} Resources</span>
                          <span className="text-sm text-muted-foreground">
                            {(avgAvailability * 100).toFixed(0)}% available
                          </span>
                        </div>
                        <Progress value={avgAvailability * 100} />
                        <p className="text-xs text-muted-foreground mt-1">
                          Total required: {totalQuantity} units
                        </p>
                      </div>
                    )
                  })}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Detailed Resource Breakdown */}
          <Card>
            <CardHeader>
              <CardTitle>Resource Requirements by Task</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={400}>
                <BarChart data={transformedData.map(task => ({
                  taskName: task.name,
                  humanCost: task.resourceRequirements.filter(r => r.type === 'human').reduce((sum, r) => sum + (r.cost * r.quantity), 0),
                  technologyCost: task.resourceRequirements.filter(r => r.type === 'technology').reduce((sum, r) => sum + (r.cost * r.quantity), 0),
                  facilityCost: task.resourceRequirements.filter(r => r.type === 'facility').reduce((sum, r) => sum + (r.cost * r.quantity), 0),
                  financialCost: task.resourceRequirements.filter(r => r.type === 'financial').reduce((sum, r) => sum + (r.cost * r.quantity), 0)
                }))}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="taskName" angle={-45} textAnchor="end" height={100} />
                  <YAxis />
                  <Tooltip formatter={(value: any) => [`$${value.toLocaleString()}`, 'Cost']} />
                  <Legend />
                  <Bar dataKey="humanCost" stackId="a" fill="#3B82F6" name="Human Resources" />
                  <Bar dataKey="technologyCost" stackId="a" fill="#8B5CF6" name="Technology" />
                  <Bar dataKey="facilityCost" stackId="a" fill="#10B981" name="Facilities" />
                  <Bar dataKey="financialCost" stackId="a" fill="#F59E0B" name="Financial" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="optimization" className="space-y-4">
          {/* Optimization Opportunities */}
          <Card>
            <CardHeader>
              <CardTitle>Optimization Opportunities</CardTitle>
              <CardDescription>
                Identify and apply optimizations to improve recovery times and reduce costs
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {criticalPaths?.find(p => p.id === selectedPath)?.optimizationOpportunities.map((opportunity, index) => (
                  <div key={index} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <h4 className="font-semibold">Function Optimization</h4>
                        <p className="text-sm text-muted-foreground">
                          Function ID: {opportunity.functionId}
                        </p>
                      </div>
                      <Badge variant={opportunity.effort === 'low' ? 'secondary' : opportunity.effort === 'medium' ? 'default' : 'destructive'}>
                        {opportunity.effort} effort
                      </Badge>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-4">
                      <div>
                        <p className="text-sm font-medium">Current RTO</p>
                        <p className="text-2xl font-bold text-red-500">{opportunity.currentRTO}h</p>
                      </div>
                      <div>
                        <p className="text-sm font-medium">Optimized RTO</p>
                        <p className="text-2xl font-bold text-green-500">{opportunity.optimizedRTO}h</p>
                      </div>
                      <div>
                        <p className="text-sm font-medium">Investment</p>
                        <p className="text-2xl font-bold">${(opportunity.investment / 1000).toFixed(0)}K</p>
                      </div>
                      <div>
                        <p className="text-sm font-medium">Cost Benefit</p>
                        <p className="text-2xl font-bold text-green-500">${(opportunity.costBenefit / 1000).toFixed(0)}K</p>
                      </div>
                    </div>

                    <div className="flex justify-between items-center mt-4">
                      <div className="flex items-center gap-2">
                        <span className="text-sm">Time Savings:</span>
                        <Badge variant="outline">
                          {opportunity.currentRTO - opportunity.optimizedRTO}h
                        </Badge>
                        <span className="text-sm">ROI:</span>
                        <Badge variant="outline">
                          {((opportunity.costBenefit / opportunity.investment) * 100).toFixed(0)}%
                        </Badge>
                      </div>
                      <Button
                        size="sm"
                        onClick={() => {
                          setSelectedOptimization(opportunity)
                          setShowOptimizationDialog(true)
                        }}
                      >
                        Apply Optimization
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* What-If Scenario Modeling */}
          <Card>
            <CardHeader>
              <CardTitle>What-If Scenario Modeling</CardTitle>
              <CardDescription>
                Create and test different recovery scenarios
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center gap-2">
                  <Button
                    variant="outline"
                    onClick={handleScenarioRun}
                    disabled={simulationRunning}
                  >
                    {simulationRunning ? (
                      <>
                        <Pause className="h-4 w-4 mr-2" />
                        Running...
                      </>
                    ) : (
                      <>
                        <Play className="h-4 w-4 mr-2" />
                        Run Scenario
                      </>
                    )}
                  </Button>
                  <Button variant="outline" size="sm">
                    <RotateCcw className="h-4 w-4 mr-2" />
                    Reset
                  </Button>
                </div>

                {simulationRunning && (
                  <Alert>
                    <Activity className="h-4 w-4" />
                    <AlertTitle>Simulation Running</AlertTitle>
                    <AlertDescription>
                      Analyzing scenario impact on recovery timeline and costs...
                    </AlertDescription>
                  </Alert>
                )}

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <Label>Scenario Name</Label>
                    <Input placeholder="Enter scenario name" />
                  </div>
                  <div>
                    <Label>Resource Multiplier</Label>
                    <Slider
                      defaultValue={[1]}
                      max={3}
                      min={0.5}
                      step={0.1}
                      className="mt-2"
                    />
                  </div>
                  <div>
                    <Label>Parallel Processing</Label>
                    <div className="flex items-center space-x-2 mt-2">
                      <Switch id="parallel-mode" />
                      <Label htmlFor="parallel-mode">Enable</Label>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Optimization Dialog */}
      <Dialog open={showOptimizationDialog} onOpenChange={setShowOptimizationDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Apply Optimization</DialogTitle>
            <DialogDescription>
              Review and confirm the optimization changes
            </DialogDescription>
          </DialogHeader>

          {selectedOptimization && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Current RTO</Label>
                  <Input value={`${selectedOptimization.currentRTO} hours`} disabled />
                </div>
                <div>
                  <Label>Optimized RTO</Label>
                  <Input value={`${selectedOptimization.optimizedRTO} hours`} disabled />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Investment Required</Label>
                  <Input value={`$${selectedOptimization.investment.toLocaleString()}`} disabled />
                </div>
                <div>
                  <Label>Expected Benefit</Label>
                  <Input value={`$${selectedOptimization.costBenefit.toLocaleString()}`} disabled />
                </div>
              </div>

              <Alert>
                <Info className="h-4 w-4" />
                <AlertTitle>Impact Summary</AlertTitle>
                <AlertDescription>
                  This optimization will reduce recovery time by {selectedOptimization.currentRTO - selectedOptimization.optimizedRTO} hours
                  with an ROI of {((selectedOptimization.costBenefit / selectedOptimization.investment) * 100).toFixed(0)}%.
                </AlertDescription>
              </Alert>
            </div>
          )}

          <DialogFooter>
            <Button variant="outline" onClick={() => setShowOptimizationDialog(false)}>
              Cancel
            </Button>
            <Button onClick={() => selectedOptimization && handleOptimizationApply(selectedOptimization)}>
              Apply Optimization
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Bottom Insights Panel */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Zap className="h-5 w-5" />
            AI-Powered Insights & Recommendations
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <Alert>
              <CheckCircle2 className="h-4 w-4" />
              <AlertTitle>Optimization Opportunity</AlertTitle>
              <AlertDescription>
                Consider implementing parallel recovery for functions 2-4 to reduce total RTO by 30%.
              </AlertDescription>
            </Alert>

            <Alert>
              <AlertCircle className="h-4 w-4" />
              <AlertTitle>Bottleneck Detected</AlertTitle>
              <AlertDescription>
                {pathMetrics?.bottleneck} is the critical bottleneck. Consider additional resources.
              </AlertDescription>
            </Alert>

            <Alert>
              <XCircle className="h-4 w-4" />
              <AlertTitle>Resource Constraint</AlertTitle>
              <AlertDescription>
                Human resources are over-allocated during peak recovery periods.
              </AlertDescription>
            </Alert>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

// Export the component
export { CriticalPathAnalysis }