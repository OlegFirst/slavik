'use client'

import React, { useState, useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { cn } from '@/lib/utils'
import {
  Clock,
  AlertTriangle,
  DollarSign,
  TrendingUp,
  TrendingDown,
  Play,
  Pause,
  RotateCcw,
  Settings,
  Download,
  Zap,
  Calendar,
  Activity
} from 'lucide-react'
import {
  biaAPI,
  biaQueryKeys,
  type BIAResult
} from '@/services/bia-api'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell
} from 'recharts'

// Types for Impact Timeline
interface TimelineEvent {
  timeHours: number
  eventType: 'outage_start' | 'recovery_milestone' | 'full_recovery' | 'critical_point'
  description: string
  financialImpact: number
  cumulativeImpact: number
  affectedProcesses: string[]
  severity: 'low' | 'medium' | 'high' | 'critical'
}

interface ImpactPhase {
  name: string
  startHour: number
  endHour: number
  description: string
  impact: number
  color: string
}

interface RecoveryScenario {
  id: string
  name: string
  description: string
  timeline: TimelineEvent[]
  totalCost: number
  recoveryTime: number
  confidence: number
}

const COLORS = {
  critical: '#ef4444',
  high: '#f97316',
  medium: '#eab308',
  low: '#22c55e',
  recovery: '#3b82f6'
}

export function ImpactTimeline() {
  const [selectedScenario, setSelectedScenario] = useState<string>('base')
  const [timeRange, setTimeRange] = useState<'24h' | '72h' | '7d' | '30d'>('72h')
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)

  // Fetch BIA results
  const { data: biaResults, isLoading } = useQuery({
    queryKey: biaQueryKeys.results(),
    queryFn: () => biaAPI.getBIAResults({})
  })

  // Generate impact timeline data
  const timelineData = useMemo(() => {
    if (!biaResults) return []

    const maxHours = timeRange === '24h' ? 24 : timeRange === '72h' ? 72 : timeRange === '7d' ? 168 : 720
    const data: Array<{
      time: number
      timeLabel: string
      cumulativeImpact: number
      hourlyImpact: number
      activeProcesses: number
      criticalProcesses: number
      recoveryRate: number
    }> = []

    for (let hour = 0; hour <= maxHours; hour += timeRange === '30d' ? 24 : 1) {
      let cumulativeImpact = 0
      let activeProcesses = 0
      let criticalProcesses = 0

      biaResults.forEach(process => {
        if (hour >= process.rto) {
          // Process is down
          activeProcesses++
          if (process.criticalityLevel === 'critical') criticalProcesses++

          // Calculate impact based on time and severity
          const timeFactor = Math.min(hour / process.mtpd, 1)
          const impact = process.financialImpactPerHour * timeFactor *
            (process.criticalityLevel === 'critical' ? 2 :
             process.criticalityLevel === 'high' ? 1.5 :
             process.criticalityLevel === 'medium' ? 1 : 0.5)

          cumulativeImpact += impact
        }
      })

      data.push({
        time: hour,
        timeLabel: timeRange === '30d' ? `Day ${Math.floor(hour/24)}` : `${hour}h`,
        cumulativeImpact: Math.round(cumulativeImpact),
        hourlyImpact: hour > 0 ? Math.round(cumulativeImpact - (data[data.length - 1]?.cumulativeImpact || 0)) : 0,
        activeProcesses,
        criticalProcesses,
        recoveryRate: Math.max(0, 100 - (hour / maxHours) * 100)
      })
    }

    return data
  }, [biaResults, timeRange])

  // Generate recovery scenarios
  const recoveryScenarios: RecoveryScenario[] = useMemo(() => [
    {
      id: 'optimistic',
      name: 'Optimistic Recovery',
      description: 'Best-case scenario with all systems restored quickly',
      timeline: [],
      totalCost: timelineData.reduce((sum, point) => sum + point.hourlyImpact * 0.7, 0),
      recoveryTime: 12,
      confidence: 0.3
    },
    {
      id: 'base',
      name: 'Base Case Recovery',
      description: 'Expected recovery time based on current capabilities',
      timeline: [],
      totalCost: timelineData.reduce((sum, point) => sum + point.hourlyImpact, 0),
      recoveryTime: 24,
      confidence: 0.7
    },
    {
      id: 'pessimistic',
      name: 'Pessimistic Recovery',
      description: 'Worst-case scenario with extended recovery times',
      timeline: [],
      totalCost: timelineData.reduce((sum, point) => sum + point.hourlyImpact * 1.5, 0),
      recoveryTime: 72,
      confidence: 0.1
    }
  ], [timelineData])

  // Generate impact phases
  const impactPhases: ImpactPhase[] = useMemo(() => {
    const maxHours = timeRange === '24h' ? 24 : timeRange === '72h' ? 72 : timeRange === '7d' ? 168 : 720

    return [
      {
        name: 'Immediate Impact',
        startHour: 0,
        endHour: Math.min(4, maxHours),
        description: 'Initial disruption and immediate response',
        impact: 25,
        color: COLORS.high
      },
      {
        name: 'Escalation Phase',
        startHour: 4,
        endHour: Math.min(12, maxHours),
        description: 'Impact spreads, customer complaints increase',
        impact: 60,
        color: COLORS.critical
      },
      {
        name: 'Crisis Phase',
        startHour: 12,
        endHour: Math.min(24, maxHours),
        description: 'Full business impact, regulatory attention',
        impact: 100,
        color: '#7c2d12'
      },
      {
        name: 'Recovery Phase',
        startHour: 24,
        endHour: maxHours,
        description: 'Systems restored, business operations resuming',
        impact: 40,
        color: COLORS.recovery
      }
    ]
  }, [timeRange])

  const exportTimeline = () => {
    const csvContent = timelineData.map(row =>
      `${row.timeLabel},${row.cumulativeImpact},${row.hourlyImpact},${row.activeProcesses}`
    ).join('\n')

    const blob = new Blob([`Time,Cumulative Impact,Hourly Impact,Active Processes\n${csvContent}`], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `impact-timeline-${timeRange}-${new Date().toISOString().split('T')[0]}.csv`
    link.click()
    URL.revokeObjectURL(url)
  }

  if (isLoading) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-64"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Impact Timeline Analysis</h2>
          <p className="text-gray-600">
            Temporal analysis of business impact across different disruption scenarios
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="outline" onClick={exportTimeline}>
            <Download className="h-4 w-4 mr-2" />
            Export Timeline
          </Button>
          <Button variant="outline" onClick={() => setIsPlaying(!isPlaying)}>
            {isPlaying ? <Pause className="h-4 w-4 mr-2" /> : <Play className="h-4 w-4 mr-2" />}
            {isPlaying ? 'Pause' : 'Play'} Simulation
          </Button>
        </div>
      </div>

      {/* Controls */}
      <Card>
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <Clock className="h-4 w-4 text-gray-500" />
                <span className="text-sm font-medium">Time Range:</span>
                <div className="flex gap-1">
                  {(['24h', '72h', '7d', '30d'] as const).map(range => (
                    <Button
                      key={range}
                      variant={timeRange === range ? "default" : "outline"}
                      size="sm"
                      onClick={() => setTimeRange(range)}
                    >
                      {range}
                    </Button>
                  ))}
                </div>
              </div>

              <div className="flex items-center gap-2">
                <Activity className="h-4 w-4 text-gray-500" />
                <span className="text-sm font-medium">Scenario:</span>
                <select
                  value={selectedScenario}
                  onChange={(e) => setSelectedScenario(e.target.value)}
                  className="text-sm border rounded px-2 py-1"
                >
                  {recoveryScenarios.map(scenario => (
                    <option key={scenario.id} value={scenario.id}>
                      {scenario.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="flex items-center gap-4 text-sm">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                <span>Critical Impact</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                <span>Recovery Phase</span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Timeline Visualization */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Timeline Chart */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-blue-600" />
              Financial Impact Over Time
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={timelineData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="timeLabel" />
                  <YAxis tickFormatter={(value) => `$${(value / 1000).toFixed(0)}K`} />
                  <Tooltip
                    formatter={(value: number, name: string) => [
                      name === 'cumulativeImpact' ? `$${value.toLocaleString()}` : value,
                      name === 'cumulativeImpact' ? 'Cumulative Impact' :
                      name === 'hourlyImpact' ? 'Hourly Impact' : name
                    ]}
                  />
                  <Legend />
                  <Area
                    type="monotone"
                    dataKey="cumulativeImpact"
                    stackId="1"
                    stroke={COLORS.critical}
                    fill={COLORS.critical}
                    fillOpacity={0.3}
                  />
                  <Line
                    type="monotone"
                    dataKey="hourlyImpact"
                    stroke={COLORS.high}
                    strokeWidth={2}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Impact Phases */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Calendar className="h-5 w-5 text-purple-600" />
              Impact Phases
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {impactPhases.map((phase, index) => (
              <div key={index} className="p-3 rounded-lg border">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium text-sm">{phase.name}</span>
                  <Badge variant="outline" style={{ color: phase.color }}>
                    {phase.startHour}h - {phase.endHour}h
                  </Badge>
                </div>
                <p className="text-xs text-gray-600 mb-2">{phase.description}</p>
                <div className="flex items-center gap-2">
                  <div
                    className="h-2 rounded-full flex-1"
                    style={{ backgroundColor: phase.color, opacity: 0.3 }}
                  >
                    <div
                      className="h-full rounded-full"
                      style={{
                        backgroundColor: phase.color,
                        width: `${phase.impact}%`
                      }}
                    />
                  </div>
                  <span className="text-xs font-medium">{phase.impact}%</span>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>

      {/* Recovery Scenarios Comparison */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Zap className="h-5 w-5 text-green-600" />
            Recovery Scenarios Comparison
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {recoveryScenarios.map(scenario => (
              <div
                key={scenario.id}
                className={cn(
                  "p-4 rounded-lg border cursor-pointer transition-all",
                  selectedScenario === scenario.id
                    ? "border-blue-500 bg-blue-50"
                    : "border-gray-200 hover:border-gray-300"
                )}
                onClick={() => setSelectedScenario(scenario.id)}
              >
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium">{scenario.name}</h4>
                  <Badge variant={scenario.confidence > 0.5 ? "default" : "secondary"}>
                    {Math.round(scenario.confidence * 100)}% confidence
                  </Badge>
                </div>
                <p className="text-sm text-gray-600 mb-3">{scenario.description}</p>

                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Total Cost:</span>
                    <span className="font-medium">${scenario.totalCost.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>Recovery Time:</span>
                    <span className="font-medium">{scenario.recoveryTime}h</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full transition-all"
                      style={{ width: `${scenario.confidence * 100}%` }}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Key Metrics Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-red-100 rounded-lg">
                <DollarSign className="h-5 w-5 text-red-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Peak Hourly Impact</p>
                <p className="text-lg font-bold">
                  ${Math.max(...timelineData.map(d => d.hourlyImpact)).toLocaleString()}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-orange-100 rounded-lg">
                <Clock className="h-5 w-5 text-orange-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Critical Period</p>
                <p className="text-lg font-bold">
                  {impactPhases.find(p => p.impact === 100)?.startHour || 0}-
                  {impactPhases.find(p => p.impact === 100)?.endHour || 24}h
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Activity className="h-5 w-5 text-blue-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Affected Processes</p>
                <p className="text-lg font-bold">
                  {Math.max(...timelineData.map(d => d.activeProcesses))}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-green-100 rounded-lg">
                <TrendingUp className="h-5 w-5 text-green-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Recovery Rate</p>
                <p className="text-lg font-bold">
                  {Math.round(timelineData[timelineData.length - 1]?.recoveryRate || 0)}%
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}