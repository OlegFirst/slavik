'use client'

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useState, useEffect, useMemo } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import useBCMStore from '@/lib/bcm-store'
import { toast } from 'sonner'
import {
  Brain,
  Crown,
  BarChart3,
  Zap,
  GraduationCap,
  CheckCircle,
  Calendar,
  MessageCircle,
  Settings,
  TrendingUp,
  FileText,
  Play,
  Pause,
  RotateCw,
  AlertCircle,
  Activity,
  Clock,
  Shield,
  Power,
  ExternalLink,
  ChevronRight,
  Wifi,
  WifiOff
} from 'lucide-react'

// Enhanced TypeScript interfaces
interface AIOrgan {
  id: string
  name: string
  category: string
  status: 'active' | 'idle' | 'error' | 'maintenance' | 'initializing'
  health: number
  lastActivity: string
  responseTime: number
  tokensUsed: number
  capabilities: string[]
  linkedModule?: string
  integrationData?: AIOrganIntegration
}

interface AIOrganIntegration {
  moduleLink: string
  stats?: {
    activeItems: number
    completedToday: number
    pendingActions: number
  }
  lastSync?: string
  recommendations?: string[]
}

interface AIMetrics {
  activeOrgans: number
  totalHealth: number
  tokensToday: number
  avgResponseTime: number
  systemLoad: number
}

interface AIDecision {
  id: string
  organId: string
  timestamp: string
  decision: string
  confidence: number
  context: string
  relatedModule?: string
  actionUrl?: string
}

// Enhanced AI Organs configuration with module links
const AI_ORGANS_CONFIG = [
  {
    id: 'governance-brain',
    name: 'Governance Brain',
    category: 'strategic',
    linkedModule: '/modules/governance',
    description: 'Strategic decision-making and policy guidance'
  },
  {
    id: 'risk-advisor',
    name: 'Risk Advisor',
    category: 'analysis',
    linkedModule: '/modules/risk-management',
    description: 'Risk assessment and predictive analysis'
  },
  {
    id: 'incident-commander',
    name: 'Incident Commander',
    category: 'response',
    linkedModule: '/modules/incidents',
    description: 'Emergency response coordination'
  },
  {
    id: 'bia-analyst',
    name: 'BIA Analyst',
    category: 'analysis',
    linkedModule: '/modules/bia',
    description: 'Business Impact Analysis and criticality assessment'
  },
  {
    id: 'training-mentor',
    name: 'Training Mentor',
    category: 'learning',
    linkedModule: '/modules/training',
    description: 'Learning optimization and competency development'
  },
  {
    id: 'audit-inspector',
    name: 'Audit Inspector',
    category: 'compliance',
    linkedModule: '/modules/audit',
    description: 'Compliance monitoring and audit automation'
  },
  {
    id: 'recovery-planner',
    name: 'Recovery Planner',
    category: 'planning',
    linkedModule: '/modules/plans',
    description: 'Business recovery strategy development'
  },
  {
    id: 'communication-hub',
    name: 'Communication Hub',
    category: 'coordination',
    linkedModule: '/modules/community',
    description: 'Stakeholder communication management'
  },
  {
    id: 'performance-monitor',
    name: 'Performance Monitor',
    category: 'analytics',
    linkedModule: '/modules/kpi',
    description: 'KPI tracking and performance analysis'
  },
  {
    id: 'knowledge-keeper',
    name: 'Knowledge Keeper',
    category: 'documentation',
    linkedModule: '/modules/templates',
    description: 'Knowledge management and documentation'
  }
]

export function AIControlCenterModule() {
  const router = useRouter()
  const queryClient = useQueryClient()
  const [selectedOrgan, setSelectedOrgan] = useState<string | null>(null)
  const [isConfigOpen, setIsConfigOpen] = useState(false)
  const [showIntegrationPreview, setShowIntegrationPreview] = useState<string | null>(null)

  // Zustand store integration
  const {
    aiOrgansHealth,
    aiOrgansStatus,
    aiIntegration,
    wsConnected,
    activeRisks,
    activeIncidents,
    recentBIAAnalyses,
    updateAIOrganHealth,
    updateAIOrganStatus,
    publishEvent,
    addNotification
  } = useBCMStore()

  // Initialize WebSocket connection
  useEffect(() => {
    const cleanup = initWebSocketConnection()
    return cleanup
  }, [])

  // Fetch AI organs data with Zustand integration
  const { data: organs, isLoading, refetch } = useQuery<AIOrgan[]>({
    queryKey: ['ai-organs'],
    queryFn: async () => {
      // Integrate with Zustand store data
      const mockOrgans = getMockOrgansData()

      // Merge with store state
      return mockOrgans.map(organ => ({
        ...organ,
        health: aiOrgansHealth[organ.id] || organ.health,
        status: aiOrgansStatus[organ.id] || organ.status,
        integrationData: getOrganIntegrationData(organ.id)
      }))
    },
    refetchInterval: 10000
  })

  // Get integration data for specific organ
  const getOrganIntegrationData = (organId: string): AIOrganIntegration | undefined => {
    switch(organId) {
      case 'risk-advisor':
        return {
          moduleLink: '/modules/risk-management',
          stats: {
            activeItems: activeRisks.length,
            completedToday: 5,
            pendingActions: 3
          },
          lastSync: '2 минуты назад',
          recommendations: aiIntegration.riskAdvisor.recommendations
        }
      case 'bia-analyst':
        return {
          moduleLink: '/modules/bia',
          stats: {
            activeItems: recentBIAAnalyses.length,
            completedToday: aiIntegration.biaAnalyst.completedAnalyses,
            pendingActions: 2
          },
          lastSync: '5 минут назад',
          recommendations: ['Обновить RTO для критических функций']
        }
      case 'incident-commander':
        return {
          moduleLink: '/modules/incidents',
          stats: {
            activeItems: activeIncidents.length,
            completedToday: 3,
            pendingActions: activeIncidents.filter(i => i.status === 'active').length
          },
          lastSync: '1 минута назад'
        }
      default:
        return undefined
    }
  }

  // Fetch AI metrics with store integration
  const { data: metrics } = useQuery<AIMetrics>({
    queryKey: ['ai-metrics'],
    queryFn: async () => {
      const activeCount = Object.values(aiOrgansStatus).filter(s => s === 'active').length
      const avgHealth = Object.values(aiOrgansHealth).reduce((a, b) => a + b, 0) / 10

      return {
        activeOrgans: activeCount,
        totalHealth: Math.round(avgHealth),
        tokensToday: 458293,
        avgResponseTime: 342,
        systemLoad: 68
      }
    },
    refetchInterval: 10000
  })

  // Fetch recent AI decisions
  const { data: decisions } = useQuery<AIDecision[]>({
    queryKey: ['ai-decisions'],
    queryFn: async () => getMockDecisions(),
    refetchInterval: 5000
  })

  // Control organ mutation with Zustand integration
  const organControlMutation = useMutation({
    mutationFn: async ({ organId, action }: { organId: string, action: 'start' | 'stop' | 'restart' }) => {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 500))

      // Update Zustand store
      const newStatus = action === 'start' ? 'active' : action === 'stop' ? 'idle' : 'maintenance'
      updateAIOrganStatus(organId, newStatus)

      // Publish event
      publishEvent({
        type: 'ai_decision',
        source: 'ai-control-center',
        data: { organId, action, status: newStatus }
      })

      return { success: true }
    },
    onSuccess: (data, variables) => {
      toast.success(`${variables.action === 'start' ? 'Запущен' : variables.action === 'stop' ? 'Остановлен' : 'Перезапущен'} орган ${variables.organId}`)
      refetch()
    },
    onError: () => {
      toast.error('Ошибка при управлении AI органом')
    }
  })

  // Handle organ control actions
  const handleOrganAction = async (organId: string, action: 'start' | 'stop' | 'restart') => {
    organControlMutation.mutate({ organId, action })
  }

  // Navigate to linked module
  const handleModuleNavigation = (moduleLink?: string) => {
    if (moduleLink) {
      router.push(moduleLink)
    }
  }

  // Emergency stop all organs
  const handleEmergencyStop = async () => {
    if (confirm('Вы уверены? Это остановит все AI органы!')) {
      organs?.forEach(organ => {
        if (organ.status === 'active') {
          handleOrganAction(organ.id, 'stop')
        }
      })

      addNotification({
        type: 'warning',
        title: 'Emergency Stop активирован',
        message: 'Все AI органы остановлены',
        source: 'ai-control-center'
      })
    }
  }

  if (isLoading) {
    return <LoadingState />
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header with WebSocket status */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
              <Brain className="h-8 w-8 text-purple-600" />
              AI Control Center
            </h1>
            <p className="text-gray-600 mt-1">Digital BCM Organism Management</p>
          </div>
          <div className={cn(
            "flex items-center gap-2 px-3 py-1 rounded-full text-sm",
            wsConnected ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"
          )}>
            {wsConnected ? <Wifi className="h-3 w-3" /> : <WifiOff className="h-3 w-3" />}
            {wsConnected ? 'Connected' : 'Disconnected'}
          </div>
        </div>
        <div className="flex gap-3">
          <Button
            variant="outline"
            onClick={() => refetch()}
            className="flex items-center gap-2"
          >
            <RotateCw className="h-4 w-4" />
            Refresh All
          </Button>
          <Button
            variant="destructive"
            onClick={handleEmergencyStop}
            className="flex items-center gap-2"
          >
            <Power className="h-4 w-4" />
            Emergency Stop
          </Button>
          <Button
            variant="default"
            className="bg-purple-600 hover:bg-purple-700"
            onClick={() => setIsConfigOpen(!isConfigOpen)}
          >
            <Settings className="h-4 w-4 mr-2" />
            Settings
          </Button>
        </div>
      </div>

      {/* Enhanced Metrics Cards with cross-module data */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
        <MetricCard
          title="Active Organs"
          value={`${metrics?.activeOrgans || 0}/10`}
          icon={Activity}
          color="purple"
          trend={metrics?.activeOrgans === 10 ? 'up' : 'neutral'}
        />
        <MetricCard
          title="System Health"
          value={`${metrics?.totalHealth || 0}%`}
          icon={Activity}
          color={metrics?.totalHealth! > 80 ? 'green' : metrics?.totalHealth! > 50 ? 'yellow' : 'red'}
        />
        <MetricCard
          title="Active Risks"
          value={activeRisks.length}
          icon={Shield}
          color="red"
          onClick={() => router.push('/modules/risk-management')}
        />
        <MetricCard
          title="Active Incidents"
          value={activeIncidents.filter(i => i.status === 'active').length}
          icon={Zap}
          color="yellow"
          onClick={() => router.push('/modules/incidents')}
        />
        <MetricCard
          title="Tokens Today"
          value={metrics?.tokensToday?.toLocaleString() || '0'}
          icon={TrendingUp}
          color="blue"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Area - Enhanced Organ Cards Grid */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-gray-900">AI Organs</h2>
            <div className="text-sm text-gray-500">
              Click on organs to navigate to their modules
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {organs?.map(organ => (
              <EnhancedOrganCard
                key={organ.id}
                organ={organ}
                onAction={handleOrganAction}
                onSelect={() => setSelectedOrgan(organ.id)}
                onNavigate={() => handleModuleNavigation(organ.linkedModule)}
                isSelected={selectedOrgan === organ.id}
                showPreview={() => setShowIntegrationPreview(organ.id)}
              />
            ))}
          </div>
        </div>

        {/* Enhanced Side Panel with cross-module activity */}
        <div className="space-y-4">
          <h2 className="text-xl font-semibold text-gray-900">Cross-Module Activity</h2>

          {/* Integration Preview */}
          {showIntegrationPreview && (
            <div className="bg-purple-50 border border-purple-200 rounded-lg p-4 mb-4">
              <h3 className="font-medium text-purple-900 mb-2">Integration Preview</h3>
              {organs?.find(o => o.id === showIntegrationPreview)?.integrationData && (
                <div className="space-y-2 text-sm text-purple-800">
                  <p>Active Items: {organs.find(o => o.id === showIntegrationPreview)?.integrationData?.stats?.activeItems || 0}</p>
                  <p>Completed Today: {organs.find(o => o.id === showIntegrationPreview)?.integrationData?.stats?.completedToday || 0}</p>
                  <p>Last Sync: {organs.find(o => o.id === showIntegrationPreview)?.integrationData?.lastSync}</p>
                  <Button
                    size="sm"
                    variant="outline"
                    className="mt-2 w-full"
                    onClick={() => router.push(organs.find(o => o.id === showIntegrationPreview)?.linkedModule || '/')}
                  >
                    <ExternalLink className="h-3 w-3 mr-1" />
                    Go to Module
                  </Button>
                </div>
              )}
              <Button
                size="sm"
                variant="ghost"
                onClick={() => setShowIntegrationPreview(null)}
                className="mt-2 w-full"
              >
                Close
              </Button>
            </div>
          )}

          {/* Enhanced Decision Log with module links */}
          <div className="bg-white rounded-lg border shadow-sm max-h-[600px] overflow-y-auto">
            <div className="p-4 space-y-3">
              <h3 className="font-medium text-gray-900 mb-3">Recent AI Decisions</h3>
              {decisions?.map(decision => (
                <EnhancedDecisionLogItem
                  key={decision.id}
                  decision={decision}
                  onNavigate={() => decision.actionUrl && router.push(decision.actionUrl)}
                />
              ))}
              {(!decisions || decisions.length === 0) && (
                <p className="text-gray-500 text-center py-8">No recent decisions</p>
              )}
            </div>
          </div>

          {/* System Alerts with module context */}
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <h3 className="font-medium text-yellow-900 mb-2 flex items-center gap-2">
              <AlertCircle className="h-4 w-4" />
              System Notifications
            </h3>
            <div className="space-y-2 text-sm text-yellow-800">
              <div
                className="cursor-pointer hover:underline"
                onClick={() => router.push('/modules/risk-management')}
              >
                • Risk Advisor: {activeRisks.length} active risks require attention →
              </div>
              <div
                className="cursor-pointer hover:underline"
                onClick={() => router.push('/modules/bia')}
              >
                • BIA Analyst: {aiIntegration.biaAnalyst.criticalFunctions} critical functions identified →
              </div>
              <div
                className="cursor-pointer hover:underline"
                onClick={() => router.push('/modules/audit')}
              >
                • Audit Inspector: Scheduled maintenance in 2 hours →
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Enhanced Configuration Panel with integration settings */}
      {isConfigOpen && (
        <div className="bg-white rounded-lg border shadow-sm p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">AI Configuration & Integration</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                API Endpoint
              </label>
              <input
                type="text"
                className="w-full px-3 py-2 border rounded-lg"
                defaultValue="http://localhost:8000"
                placeholder="API endpoint URL"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                WebSocket URL
              </label>
              <input
                type="text"
                className="w-full px-3 py-2 border rounded-lg"
                defaultValue="ws://localhost:8000/ws"
                placeholder="WebSocket URL"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Daily Token Limit
              </label>
              <input
                type="number"
                className="w-full px-3 py-2 border rounded-lg"
                defaultValue="1000000"
                placeholder="Token limit"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Max Response Time (ms)
              </label>
              <input
                type="number"
                className="w-full px-3 py-2 border rounded-lg"
                defaultValue="5000"
                placeholder="Max response time"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Integration Mode
              </label>
              <select className="w-full px-3 py-2 border rounded-lg">
                <option value="realtime">Real-time (WebSocket)</option>
                <option value="polling">Polling (10s)</option>
                <option value="manual">Manual refresh only</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Cross-Module Sync
              </label>
              <select className="w-full px-3 py-2 border rounded-lg">
                <option value="enabled">Enabled</option>
                <option value="disabled">Disabled</option>
              </select>
            </div>
          </div>
          <div className="mt-6 flex justify-end gap-3">
            <Button variant="outline" onClick={() => setIsConfigOpen(false)}>
              Cancel
            </Button>
            <Button
              className="bg-purple-600 hover:bg-purple-700"
              onClick={() => {
                toast.success('Configuration saved')
                setIsConfigOpen(false)
              }}
            >
              Save Settings
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}

// Enhanced Helper Components
function MetricCard({
  title,
  value,
  icon: Icon,
  color,
  trend,
  onClick
}: {
  title: string
  value: string | number
  icon: any
  color: string
  trend?: 'up' | 'down' | 'neutral'
  onClick?: () => void
}) {
  const colorClasses = {
    purple: 'bg-purple-100 text-purple-600',
    green: 'bg-green-100 text-green-600',
    yellow: 'bg-yellow-100 text-yellow-600',
    red: 'bg-red-100 text-red-600',
    blue: 'bg-blue-100 text-blue-600',
    indigo: 'bg-indigo-100 text-indigo-600',
  }[color]

  return (
    <div
      className={cn(
        "bg-white rounded-lg border shadow-sm p-6 transition-all",
        onClick && "cursor-pointer hover:shadow-md hover:scale-105"
      )}
      onClick={onClick}
    >
      <div className="flex items-center justify-between">
        <div className={cn("w-12 h-12 rounded-lg flex items-center justify-center", colorClasses)}>
          <Icon className="h-6 w-6" />
        </div>
        {trend && (
          <TrendingUp className={cn(
            "h-4 w-4",
            trend === 'up' ? 'text-green-500' : trend === 'down' ? 'text-red-500' : 'text-gray-400'
          )} />
        )}
      </div>
      <div className="mt-4">
        <div className="text-2xl font-bold text-gray-900">{value}</div>
        <div className="text-sm text-gray-500">{title}</div>
      </div>
    </div>
  )
}

function EnhancedOrganCard({
  organ,
  onAction,
  onSelect,
  onNavigate,
  isSelected,
  showPreview
}: {
  organ: AIOrgan
  onAction: (id: string, action: 'start' | 'stop' | 'restart') => void
  onSelect: () => void
  onNavigate: () => void
  isSelected: boolean
  showPreview: () => void
}) {
  const categoryIcons = {
    strategic: Crown,
    analysis: BarChart3,
    response: Zap,
    learning: GraduationCap,
    compliance: CheckCircle,
    planning: Calendar,
    coordination: MessageCircle,
    optimization: Settings,
    analytics: TrendingUp,
    documentation: FileText
  }

  const statusColors = {
    active: 'bg-green-100 text-green-800 border-green-200',
    idle: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    error: 'bg-red-100 text-red-800 border-red-200',
    maintenance: 'bg-gray-100 text-gray-800 border-gray-200',
    initializing: 'bg-blue-100 text-blue-800 border-blue-200'
  }

  const Icon = categoryIcons[organ.category as keyof typeof categoryIcons] || Brain

  return (
    <div
      className={cn(
        "bg-white rounded-lg border shadow-sm p-4 transition-all hover:shadow-md",
        isSelected && "ring-2 ring-purple-500"
      )}
    >
      <div
        className="cursor-pointer"
        onClick={onSelect}
      >
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-purple-100 flex items-center justify-center">
              <Icon className="h-5 w-5 text-purple-600" />
            </div>
            <div>
              <h3 className="font-medium text-gray-900">{organ.name}</h3>
              <span className={cn(
                "text-xs px-2 py-1 rounded-full inline-block mt-1",
                statusColors[organ.status]
              )}>
                {organ.status === 'active' ? 'Active' :
                 organ.status === 'idle' ? 'Idle' :
                 organ.status === 'error' ? 'Error' :
                 organ.status === 'initializing' ? 'Initializing' : 'Maintenance'}
              </span>
            </div>
          </div>
          {organ.linkedModule && (
            <Button
              size="sm"
              variant="ghost"
              onClick={(e) => {
                e.stopPropagation()
                onNavigate()
              }}
            >
              <ExternalLink className="h-3 w-3" />
            </Button>
          )}
        </div>

        {/* Health Bar */}
        <div className="mb-3">
          <div className="flex justify-between text-xs text-gray-500 mb-1">
            <span>Health</span>
            <span>{organ.health}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
            <div
              className={cn(
                "h-full transition-all duration-500",
                organ.health > 80 ? 'bg-green-500' :
                organ.health > 50 ? 'bg-yellow-500' : 'bg-red-500'
              )}
              style={{ width: `${organ.health}%` }}
            />
          </div>
        </div>

        {/* Integration Stats */}
        {organ.integrationData && (
          <div className="mb-3 p-2 bg-gray-50 rounded text-xs">
            <div className="grid grid-cols-3 gap-2 text-center">
              <div>
                <div className="font-medium text-gray-900">{organ.integrationData.stats?.activeItems || 0}</div>
                <div className="text-gray-500">Active</div>
              </div>
              <div>
                <div className="font-medium text-gray-900">{organ.integrationData.stats?.completedToday || 0}</div>
                <div className="text-gray-500">Today</div>
              </div>
              <div>
                <div className="font-medium text-gray-900">{organ.integrationData.stats?.pendingActions || 0}</div>
                <div className="text-gray-500">Pending</div>
              </div>
            </div>
          </div>
        )}

        {/* Metrics */}
        <div className="grid grid-cols-2 gap-2 text-xs text-gray-600 mb-3">
          <div>
            <span className="text-gray-400">Response:</span>
            <span className="ml-1 font-medium">{organ.responseTime}ms</span>
          </div>
          <div>
            <span className="text-gray-400">Tokens:</span>
            <span className="ml-1 font-medium">{organ.tokensUsed.toLocaleString()}</span>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-2">
        {organ.status === 'active' ? (
          <Button
            size="sm"
            variant="outline"
            className="flex-1"
            onClick={(e) => {
              e.stopPropagation()
              onAction(organ.id, 'stop')
            }}
          >
            <Pause className="h-3 w-3 mr-1" />
            Stop
          </Button>
        ) : (
          <Button
            size="sm"
            variant="outline"
            className="flex-1"
            onClick={(e) => {
              e.stopPropagation()
              onAction(organ.id, 'start')
            }}
          >
            <Play className="h-3 w-3 mr-1" />
            Start
          </Button>
        )}
        <Button
          size="sm"
          variant="outline"
          className="flex-1"
          onClick={(e) => {
            e.stopPropagation()
            onAction(organ.id, 'restart')
          }}
        >
          <RotateCw className="h-3 w-3 mr-1" />
          Restart
        </Button>
        {organ.integrationData && (
          <Button
            size="sm"
            variant="ghost"
            onClick={(e) => {
              e.stopPropagation()
              showPreview()
            }}
          >
            <ChevronRight className="h-3 w-3" />
          </Button>
        )}
      </div>

      {/* Last Activity */}
      <div className="mt-3 pt-3 border-t text-xs text-gray-500">
        Last activity: {organ.lastActivity}
      </div>
    </div>
  )
}

function EnhancedDecisionLogItem({
  decision,
  onNavigate
}: {
  decision: AIDecision
  onNavigate?: () => void
}) {
  const organNames: { [key: string]: string } = {
    'governance-brain': 'Governance Brain',
    'risk-advisor': 'Risk Advisor',
    'incident-commander': 'Incident Commander',
    'bia-analyst': 'BIA Analyst',
    'training-mentor': 'Training Mentor',
    'audit-inspector': 'Audit Inspector',
    'recovery-planner': 'Recovery Planner',
    'communication-hub': 'Communication Hub',
    'resource-manager': 'Resource Manager',
    'performance-monitor': 'Performance Monitor',
    'knowledge-keeper': 'Knowledge Keeper'
  }

  return (
    <div
      className={cn(
        "border-l-4 border-purple-200 pl-4 py-2 transition-all",
        decision.actionUrl && "cursor-pointer hover:bg-gray-50"
      )}
      onClick={onNavigate}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="text-sm font-medium text-gray-900 flex items-center gap-2">
            {organNames[decision.organId] || decision.organId}
            {decision.actionUrl && (
              <ExternalLink className="h-3 w-3 text-gray-400" />
            )}
          </div>
          <div className="text-sm text-gray-600 mt-1">{decision.decision}</div>
          <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
            <span>Confidence: {(decision.confidence * 100).toFixed(0)}%</span>
            <span>{new Date(decision.timestamp).toLocaleTimeString()}</span>
            {decision.relatedModule && (
              <span className="text-purple-600">→ {decision.relatedModule}</span>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

function LoadingState() {
  return (
    <div className="flex items-center justify-center h-96">
      <div className="text-center">
        <Brain className="h-12 w-12 text-purple-600 animate-pulse mx-auto mb-4" />
        <p className="text-gray-600">Loading AI Control Center...</p>
      </div>
    </div>
  )
}

// WebSocket initialization
function initWebSocketConnection() {
  // This would be imported from bcm-store in production
  console.log('Initializing WebSocket connection...')
  // Return cleanup function
  return () => {
    console.log('Cleaning up WebSocket connection')
  }
}

// Enhanced Mock Data Functions with cross-module integration
function getMockOrgansData(): AIOrgan[] {
  const config = AI_ORGANS_CONFIG

  return config.map((organ, index) => ({
    id: organ.id,
    name: organ.name,
    category: organ.category,
    status: index < 7 ? 'active' : index === 7 ? 'idle' : index === 8 ? 'error' : 'maintenance',
    health: index < 7 ? 85 + Math.floor(Math.random() * 15) : index === 8 ? 45 : 75,
    lastActivity: index < 7 ? '2 min ago' : index === 7 ? '15 min ago' : index === 8 ? 'Connection error' : 'Scheduled',
    responseTime: 200 + Math.floor(Math.random() * 300),
    tokensUsed: Math.floor(Math.random() * 50000) + 10000,
    capabilities: [
      'Analysis',
      'Decision Making',
      'Pattern Recognition',
      'Prediction'
    ],
    linkedModule: organ.linkedModule
  }))
}

function getMockDecisions(): AIDecision[] {
  const decisions = [
    {
      id: '1',
      organId: 'risk-advisor',
      timestamp: new Date(Date.now() - 1000 * 60 * 2).toISOString(),
      decision: 'Supply chain risk detected. Activating alternative suppliers recommended.',
      confidence: 0.92,
      context: 'Supply Chain Analysis',
      relatedModule: 'Risk Management',
      actionUrl: '/modules/risk-management'
    },
    {
      id: '2',
      organId: 'incident-commander',
      timestamp: new Date(Date.now() - 1000 * 60 * 5).toISOString(),
      decision: 'Incident #1247 classified as low priority. Quick response team assigned.',
      confidence: 0.88,
      context: 'Incident Response',
      relatedModule: 'Incidents',
      actionUrl: '/modules/incidents'
    },
    {
      id: '3',
      organId: 'bia-analyst',
      timestamp: new Date(Date.now() - 1000 * 60 * 7).toISOString(),
      decision: 'BIA completed for customer service. RTO set to 4 hours.',
      confidence: 0.94,
      context: 'Business Impact Analysis',
      relatedModule: 'BIA',
      actionUrl: '/modules/bia'
    },
    {
      id: '4',
      organId: 'governance-brain',
      timestamp: new Date(Date.now() - 1000 * 60 * 8).toISOString(),
      decision: 'Q2 BCM strategy approved. Cascading goals initiated.',
      confidence: 0.95,
      context: 'Strategic Planning',
      relatedModule: 'Governance',
      actionUrl: '/modules/governance'
    },
    {
      id: '5',
      organId: 'training-mentor',
      timestamp: new Date(Date.now() - 1000 * 60 * 12).toISOString(),
      decision: 'Personalized training plans created for 15 new employees.',
      confidence: 0.90,
      context: 'Learning Management',
      relatedModule: 'Training',
      actionUrl: '/modules/training'
    },
    {
      id: '6',
      organId: 'audit-inspector',
      timestamp: new Date(Date.now() - 1000 * 60 * 15).toISOString(),
      decision: 'Recovery process audit completed. 3 non-conformities identified.',
      confidence: 0.94,
      context: 'Compliance Audit',
      relatedModule: 'Audit',
      actionUrl: '/modules/audit'
    },
    {
      id: '7',
      organId: 'performance-monitor',
      timestamp: new Date(Date.now() - 1000 * 60 * 20).toISOString(),
      decision: 'Recovery time KPI improved by 15%. Positive trend confirmed.',
      confidence: 0.87,
      context: 'Performance Analysis',
      relatedModule: 'KPI',
      actionUrl: '/modules/kpi'
    },
    {
      id: '8',
      organId: 'communication-hub',
      timestamp: new Date(Date.now() - 1000 * 60 * 25).toISOString(),
      decision: 'Stakeholder notifications sent automatically for drill completion.',
      confidence: 0.99,
      context: 'Stakeholder Communication'
    },
    {
      id: '9',
      organId: 'resource-manager',
      timestamp: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
      decision: 'Resource reallocation optimized. 12% cost savings achieved.',
      confidence: 0.85,
      context: 'Resource Optimization'
    },
    {
      id: '10',
      organId: 'recovery-planner',
      timestamp: new Date(Date.now() - 1000 * 60 * 35).toISOString(),
      decision: 'Recovery plan updated for critical business processes.',
      confidence: 0.91,
      context: 'Recovery Planning',
      relatedModule: 'Plans',
      actionUrl: '/modules/plans'
    },
    {
      id: '11',
      organId: 'knowledge-keeper',
      timestamp: new Date(Date.now() - 1000 * 60 * 40).toISOString(),
      decision: '127 new documents indexed. Knowledge base updated.',
      confidence: 0.96,
      context: 'Knowledge Management',
      relatedModule: 'Templates',
      actionUrl: '/modules/templates'
    }
  ]

  return decisions
}