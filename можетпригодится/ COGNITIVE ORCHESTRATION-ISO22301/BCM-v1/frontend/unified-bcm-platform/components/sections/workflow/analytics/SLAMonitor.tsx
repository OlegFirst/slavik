'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Progress } from '@/components/ui/progress'
import {
  AlertTriangle,
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle,
  RefreshCw,
  Bell,
  TrendingDown,
  TrendingUp
} from 'lucide-react'
import { useSLAStatus, useSLABreaches, useSLAComplianceReport } from '@/lib/hooks/useWorkflow'
import type { SLAStatus } from '@/lib/services/workflow-api'

interface SLAMonitorProps {
  processIds?: string[]
  department?: string
  showBreaches?: boolean
  autoRefresh?: boolean
}

export function SLAMonitor({
  processIds,
  department,
  showBreaches = true,
  autoRefresh = true
}: SLAMonitorProps) {
  const [selectedPeriod, setSelectedPeriod] = useState<'7d' | '30d' | '90d'>('30d')

  const {
    data: slaStatus,
    isLoading: statusLoading,
    error: statusError,
    refetch: refetchStatus
  } = useSLAStatus(processIds)

  const {
    data: slaBreaches,
    isLoading: breachesLoading,
    error: breachesError,
    refetch: refetchBreaches
  } = useSLABreaches({
    department,
    dateRange: {
      from: new Date(Date.now() - (selectedPeriod === '7d' ? 7 : selectedPeriod === '30d' ? 30 : 90) * 24 * 60 * 60 * 1000).toISOString(),
      to: new Date().toISOString()
    }
  })

  const {
    data: complianceReport,
    isLoading: complianceLoading
  } = useSLAComplianceReport({
    processIds,
    department,
    period: selectedPeriod
  })

  // Auto refresh every minute if enabled
  useEffect(() => {
    if (!autoRefresh) return

    const interval = setInterval(() => {
      refetchStatus()
      refetchBreaches()
    }, 60000) // 1 minute

    return () => clearInterval(interval)
  }, [autoRefresh, refetchStatus, refetchBreaches])

  const getSLAStatusIcon = (status: SLAStatus['currentStatus']) => {
    switch (status) {
      case 'compliant':
        return <CheckCircle className="h-5 w-5 text-green-500" />
      case 'warning':
        return <AlertCircle className="h-5 w-5 text-yellow-500" />
      case 'breach':
        return <XCircle className="h-5 w-5 text-red-500" />
      default:
        return <Clock className="h-5 w-5 text-gray-500" />
    }
  }

  const getSLAStatusBadge = (status: SLAStatus['currentStatus']) => {
    switch (status) {
      case 'compliant':
        return { variant: 'default' as const, text: 'Compliant' }
      case 'warning':
        return { variant: 'outline' as const, text: 'Warning' }
      case 'breach':
        return { variant: 'destructive' as const, text: 'Breach' }
      default:
        return { variant: 'secondary' as const, text: 'Unknown' }
    }
  }

  const getRiskLevelColor = (riskLevel: SLAStatus['riskLevel']) => {
    switch (riskLevel) {
      case 'low': return 'text-green-600'
      case 'medium': return 'text-yellow-600'
      case 'high': return 'text-orange-600'
      case 'critical': return 'text-red-600'
      default: return 'text-gray-600'
    }
  }

  const formatTimeRemaining = (minutes: number) => {
    if (minutes < 0) return 'Overdue'
    if (minutes < 60) return `${minutes}m`
    const hours = Math.floor(minutes / 60)
    const remainingMinutes = minutes % 60
    if (hours < 24) return remainingMinutes > 0 ? `${hours}h ${remainingMinutes}m` : `${hours}h`
    const days = Math.floor(hours / 24)
    const remainingHours = hours % 24
    return remainingHours > 0 ? `${days}d ${remainingHours}h` : `${days}d`
  }

  const getProgressValue = (timeRemaining: number, totalTime: number = 100) => {
    if (timeRemaining < 0) return 0
    return Math.min(100, (timeRemaining / totalTime) * 100)
  }

  const criticalBreaches = slaBreaches?.filter(breach => breach.severity === 'breach') || []
  const warnings = slaBreaches?.filter(breach => breach.severity === 'warning') || []

  const isLoading = statusLoading || breachesLoading || complianceLoading
  const hasError = statusError || breachesError

  if (hasError) {
    return (
      <Alert variant="destructive">
        <AlertTriangle className="h-4 w-4" />
        <AlertDescription>
          Failed to load SLA monitoring data. Please try again.
          <Button variant="outline" size="sm" onClick={() => { refetchStatus(); refetchBreaches() }} className="ml-2">
            Retry
          </Button>
        </AlertDescription>
      </Alert>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header with summary stats */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold flex items-center gap-2">
            <Clock className="h-5 w-5" />
            SLA Monitor
          </h3>
          <p className="text-sm text-gray-600">
            Real-time monitoring of Service Level Agreement compliance
          </p>
        </div>
        <div className="flex items-center gap-2">
          {autoRefresh && (
            <Badge variant="outline" className="flex items-center gap-1">
              <RefreshCw className="h-3 w-3" />
              Auto-refresh
            </Badge>
          )}
          <Button variant="outline" size="sm" onClick={() => { refetchStatus(); refetchBreaches() }}>
            <RefreshCw className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Compliance Overview */}
      {complianceReport && (
        <div className="grid grid-cols-3 gap-4">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Overall Compliance</p>
                  <p className="text-2xl font-bold">{complianceReport.overallCompliance}%</p>
                </div>
                {complianceReport.overallCompliance >= 95 ? (
                  <TrendingUp className="h-8 w-8 text-green-500" />
                ) : (
                  <TrendingDown className="h-8 w-8 text-red-500" />
                )}
              </div>
              <Progress value={complianceReport.overallCompliance} className="mt-2" />
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Active Breaches</p>
                  <p className="text-2xl font-bold text-red-600">{criticalBreaches.length}</p>
                </div>
                <XCircle className="h-8 w-8 text-red-500" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Warnings</p>
                  <p className="text-2xl font-bold text-yellow-600">{warnings.length}</p>
                </div>
                <AlertTriangle className="h-8 w-8 text-yellow-500" />
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Active SLA Status */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Clock className="h-5 w-5" />
            Active SLA Status
          </CardTitle>
          <CardDescription>
            Current status of all monitored processes
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-4">
              {[1, 2, 3].map(i => (
                <div key={i} className="flex items-center space-x-4">
                  <div className="h-12 w-12 bg-gray-200 rounded animate-pulse" />
                  <div className="flex-1 space-y-2">
                    <div className="h-4 bg-gray-200 rounded animate-pulse" />
                    <div className="h-3 bg-gray-200 rounded animate-pulse w-3/4" />
                  </div>
                </div>
              ))}
            </div>
          ) : slaStatus?.length ? (
            <div className="space-y-4">
              {slaStatus.map((status) => (
                <div key={status.processId} className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex items-center space-x-4">
                    {getSLAStatusIcon(status.currentStatus)}
                    <div>
                      <p className="font-medium">Process {status.processId}</p>
                      <p className="text-sm text-gray-600">
                        Risk Level: <span className={getRiskLevelColor(status.riskLevel)}>{status.riskLevel.toUpperCase()}</span>
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center space-x-4">
                    <div className="text-right">
                      <p className="text-sm font-medium">
                        {formatTimeRemaining(status.timeRemaining)}
                      </p>
                      <p className="text-xs text-gray-500">
                        {status.timeRemaining < 0 ? 'Overdue' : 'Remaining'}
                      </p>
                    </div>

                    <div className="w-24">
                      <Progress
                        value={getProgressValue(status.timeRemaining)}
                        className={`h-2 ${status.currentStatus === 'breach' ? '[&>*]:bg-red-500' : status.currentStatus === 'warning' ? '[&>*]:bg-yellow-500' : '[&>*]:bg-green-500'}`}
                      />
                    </div>

                    <Badge {...getSLAStatusBadge(status.currentStatus)} />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <Clock className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>No SLA monitoring data available</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Recent Breaches */}
      {showBreaches && criticalBreaches.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-red-600">
              <Bell className="h-5 w-5" />
              Critical SLA Breaches
            </CardTitle>
            <CardDescription>
              Recent breaches requiring immediate attention
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {criticalBreaches.slice(0, 5).map((breach, index) => (
                <Alert key={index} variant="destructive">
                  <XCircle className="h-4 w-4" />
                  <AlertDescription>
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium">Process {breach.processId}</p>
                        <p className="text-sm">{breach.description}</p>
                      </div>
                      <div className="text-right">
                        <p className="text-xs">{new Date(breach.timestamp).toLocaleString()}</p>
                        <Badge variant="destructive" size="sm">
                          {breach.severity.toUpperCase()}
                        </Badge>
                      </div>
                    </div>
                  </AlertDescription>
                </Alert>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Warnings */}
      {showBreaches && warnings.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-yellow-600">
              <AlertTriangle className="h-5 w-5" />
              SLA Warnings
            </CardTitle>
            <CardDescription>
              Processes approaching SLA breach thresholds
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {warnings.slice(0, 3).map((warning, index) => (
                <Alert key={index}>
                  <AlertTriangle className="h-4 w-4" />
                  <AlertDescription>
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium">Process {warning.processId}</p>
                        <p className="text-sm">{warning.description}</p>
                      </div>
                      <div className="text-right">
                        <p className="text-xs">{new Date(warning.timestamp).toLocaleString()}</p>
                        <Badge variant="outline" size="sm">
                          {warning.severity.toUpperCase()}
                        </Badge>
                      </div>
                    </div>
                  </AlertDescription>
                </Alert>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}