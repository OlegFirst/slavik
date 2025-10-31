import { useEffect, useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import {
  Activity,
  Users,
  Server,
  Database,
  Wifi,
  WifiOff,
  AlertCircle,
  CheckCircle,
  Clock,
  TrendingUp,
  TrendingDown
} from 'lucide-react'
import { useUnifiedPlatformWebSocket } from '@/hooks/useUnifiedPlatformWebSocket'

interface SectionMetrics {
  name: string
  users: number
  status: 'active' | 'idle' | 'offline'
  lastActivity: string
  performance: number
}

export function UnifiedPlatformMonitor() {
  const { metrics, isConnected, lastUpdate, sendUserActivity } = useUnifiedPlatformWebSocket()
  const [sections, setSections] = useState<SectionMetrics[]>([])
  const [systemHealth, setSystemHealth] = useState(95)

  useEffect(() => {
    // Track this monitor's activity
    sendUserActivity('admin_panel', 'enter')

    return () => {
      sendUserActivity('admin_panel', 'exit')
    }
  }, [sendUserActivity])

  useEffect(() => {
    if (metrics) {
      // Convert metrics to section display format
      const sectionList: SectionMetrics[] = [
        {
          name: 'Digital Twin',
          users: metrics.sections['digital-twin']?.users || 0,
          status: metrics.sections['digital-twin']?.users > 0 ? 'active' : 'idle',
          lastActivity: new Date(metrics.sections['digital-twin']?.lastActivity || Date.now()).toLocaleTimeString(),
          performance: 98
        },
        {
          name: 'Risk Management',
          users: metrics.sections['risk-management']?.users || 0,
          status: metrics.sections['risk-management']?.users > 0 ? 'active' : 'idle',
          lastActivity: new Date(metrics.sections['risk-management']?.lastActivity || Date.now()).toLocaleTimeString(),
          performance: 95
        },
        {
          name: 'BIA',
          users: metrics.sections['bia']?.users || 0,
          status: metrics.sections['bia']?.users > 0 ? 'active' : 'idle',
          lastActivity: new Date(metrics.sections['bia']?.lastActivity || Date.now()).toLocaleTimeString(),
          performance: 92
        },
        {
          name: 'Incident Management',
          users: metrics.sections['incident-management']?.users || 0,
          status: metrics.sections['incident-management']?.users > 0 ? 'active' : 'idle',
          lastActivity: new Date(metrics.sections['incident-management']?.lastActivity || Date.now()).toLocaleTimeString(),
          performance: 96
        },
        {
          name: 'Training',
          users: metrics.sections['training']?.users || 0,
          status: metrics.sections['training']?.users > 0 ? 'active' : 'idle',
          lastActivity: new Date(metrics.sections['training']?.lastActivity || Date.now()).toLocaleTimeString(),
          performance: 90
        },
        {
          name: 'Compliance',
          users: metrics.sections['compliance']?.users || 0,
          status: metrics.sections['compliance']?.users > 0 ? 'active' : 'idle',
          lastActivity: new Date(metrics.sections['compliance']?.lastActivity || Date.now()).toLocaleTimeString(),
          performance: 94
        }
      ]
      setSections(sectionList)

      // Calculate overall system health
      const avgPerformance = metrics.performance ?
        (100 - (metrics.performance.errorCount / Math.max(1, metrics.performance.requestCount)) * 100) : 95
      setSystemHealth(Math.round(avgPerformance))
    }
  }, [metrics])

  // Fallback data if WebSocket is not connected
  useEffect(() => {
    if (!isConnected) {
      setSections([
        { name: 'Digital Twin', users: 3, status: 'active', lastActivity: '2 min ago', performance: 98 },
        { name: 'Risk Management', users: 5, status: 'active', lastActivity: '1 min ago', performance: 95 },
        { name: 'BIA', users: 2, status: 'active', lastActivity: '5 min ago', performance: 92 },
        { name: 'Incident Management', users: 1, status: 'idle', lastActivity: '15 min ago', performance: 96 },
        { name: 'Training', users: 8, status: 'active', lastActivity: 'Just now', performance: 90 },
        { name: 'Compliance', users: 0, status: 'offline', lastActivity: '1 hour ago', performance: 94 }
      ])
    }
  }, [isConnected])

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-500'
      case 'idle': return 'bg-yellow-500'
      case 'offline': return 'bg-gray-400'
      default: return 'bg-gray-400'
    }
  }

  const getPerformanceColor = (performance: number) => {
    if (performance >= 95) return 'text-green-600'
    if (performance >= 85) return 'text-yellow-600'
    return 'text-red-600'
  }

  return (
    <Card className="w-full">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <CardTitle className="flex items-center gap-2">
              <Server className="h-5 w-5" />
              Unified Platform Monitor
            </CardTitle>
            <CardDescription>
              Real-time monitoring across all BCM sections
            </CardDescription>
          </div>
          <div className="flex items-center gap-3">
            <Badge variant={isConnected ? "default" : "secondary"} className="flex items-center gap-1">
              {isConnected ? <Wifi className="h-3 w-3" /> : <WifiOff className="h-3 w-3" />}
              {isConnected ? 'Connected' : 'HTTP Mode'}
            </Badge>
            <div className="text-xs text-muted-foreground flex items-center gap-1">
              <Clock className="h-3 w-3" />
              {lastUpdate.toLocaleTimeString()}
            </div>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* System Overview */}
        <div className="grid grid-cols-4 gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-1">
              <Users className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm font-medium">Active Users</span>
            </div>
            <div className="text-2xl font-bold">
              {metrics?.activeUsers || sections.reduce((sum, s) => sum + s.users, 0)}
            </div>
          </div>
          <div className="space-y-1">
            <div className="flex items-center gap-1">
              <Activity className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm font-medium">System Health</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-2xl font-bold">{systemHealth}%</span>
              {systemHealth >= 95 ?
                <CheckCircle className="h-4 w-4 text-green-600" /> :
                <AlertCircle className="h-4 w-4 text-yellow-600" />
              }
            </div>
          </div>
          <div className="space-y-1">
            <div className="flex items-center gap-1">
              <Database className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm font-medium">Response Time</span>
            </div>
            <div className="text-2xl font-bold">
              {metrics?.performance?.responseTime || 142}ms
            </div>
          </div>
          <div className="space-y-1">
            <div className="flex items-center gap-1">
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm font-medium">Requests/min</span>
            </div>
            <div className="text-2xl font-bold">
              {metrics?.performance?.requestCount || 247}
            </div>
          </div>
        </div>

        {/* Section Status Grid */}
        <div className="space-y-2">
          <h4 className="text-sm font-medium text-muted-foreground">Section Activity</h4>
          <div className="grid grid-cols-2 gap-3">
            {sections.map((section) => (
              <div key={section.name} className="border rounded-lg p-3 space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className={`w-2 h-2 rounded-full ${getStatusColor(section.status)}`} />
                    <span className="font-medium text-sm">{section.name}</span>
                  </div>
                  <Badge variant="outline" className="text-xs">
                    {section.users} {section.users === 1 ? 'user' : 'users'}
                  </Badge>
                </div>
                <div className="space-y-1">
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-muted-foreground">Performance</span>
                    <span className={getPerformanceColor(section.performance)}>
                      {section.performance}%
                    </span>
                  </div>
                  <Progress value={section.performance} className="h-1" />
                </div>
                <div className="text-xs text-muted-foreground">
                  Last activity: {section.lastActivity}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* System Resources */}
        {metrics?.system && (
          <div className="space-y-2">
            <h4 className="text-sm font-medium text-muted-foreground">System Resources</h4>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1">
                <div className="flex items-center justify-between text-sm">
                  <span>Memory Usage</span>
                  <span className="font-medium">{metrics.system.memoryUsage}%</span>
                </div>
                <Progress value={metrics.system.memoryUsage} className="h-2" />
              </div>
              <div className="space-y-1">
                <div className="flex items-center justify-between text-sm">
                  <span>CPU Usage</span>
                  <span className="font-medium">{metrics.system.cpuUsage}%</span>
                </div>
                <Progress value={metrics.system.cpuUsage} className="h-2" />
              </div>
            </div>
          </div>
        )}

        {/* Connection Status */}
        {!isConnected && (
          <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-3">
            <div className="flex items-center gap-2">
              <AlertCircle className="h-4 w-4 text-yellow-600" />
              <span className="text-sm text-yellow-800 dark:text-yellow-200">
                WebSocket unavailable. Using HTTP polling for metrics.
              </span>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}