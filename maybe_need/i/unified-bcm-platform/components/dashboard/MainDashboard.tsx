'use client'

import { useQuery } from '@tanstack/react-query'
import { bcmAPI, type DashboardData } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { 
  Activity,
  Brain,
  Shield,
  TrendingUp,
  AlertTriangle,
  Users,
  Settings,
  BarChart3,
  RefreshCw,
  ExternalLink
} from 'lucide-react'

export function MainDashboard() {
  const {
    data: dashboardData,
    isLoading,
    error,
    refetch
  } = useQuery<DashboardData>({
    queryKey: ['dashboard'],
    queryFn: () => bcmAPI.getDashboardData(),
    refetchInterval: 30000, // Refresh every 30 seconds
    initialData: {
      kpis: {
        totalRisks: 147,
        activeBCPs: 23,
        criticalIncidents: 3,
        complianceScore: 94,
      },
      recentActivity: [
        {
          id: '1',
          type: 'risk' as const,
          title: 'High-risk vulnerability identified',
          description: 'Critical security vulnerability detected in customer database',
          timestamp: '2025-09-19T10:15:30.000Z',
          severity: 'high' as const,
        },
        {
          id: '2',
          type: 'bcp' as const,
          title: 'Business Continuity Plan updated',
          description: 'IT infrastructure recovery plan updated with new procedures',
          timestamp: '2025-09-19T08:15:30.000Z',
          severity: 'medium' as const,
        },
        {
          id: '3',
          type: 'incident' as const,
          title: 'Network outage resolved',
          description: 'Data center connectivity restored within RTO',
          timestamp: '2025-09-19T06:15:30.000Z',
          severity: 'critical' as const,
        },
      ],
      aiOrgans: [
        { id: 'organ-1', name: 'Governance Brain', status: 'active' as const, health: 94, responseTime: 120, tokensUsed: 8420 },
        { id: 'organ-2', name: 'Risk Advisor', status: 'active' as const, health: 87, responseTime: 85, tokensUsed: 6250 },
        { id: 'organ-3', name: 'Incident Commander', status: 'active' as const, health: 92, responseTime: 95, tokensUsed: 7880 },
        { id: 'organ-4', name: 'Training Mentor', status: 'idle' as const, health: 76, responseTime: 140, tokensUsed: 4320 },
        { id: 'organ-5', name: 'Audit Inspector', status: 'active' as const, health: 89, responseTime: 110, tokensUsed: 5670 },
        { id: 'organ-6', name: 'Recovery Planner', status: 'active' as const, health: 91, responseTime: 75, tokensUsed: 7200 },
        { id: 'organ-7', name: 'Communication Hub', status: 'active' as const, health: 85, responseTime: 130, tokensUsed: 6840 },
        { id: 'organ-8', name: 'Resource Manager', status: 'error' as const, health: 65, responseTime: 220, tokensUsed: 3100 },
        { id: 'organ-9', name: 'Performance Monitor', status: 'active' as const, health: 93, responseTime: 90, tokensUsed: 8100 },
        { id: 'organ-10', name: 'Knowledge Keeper', status: 'active' as const, health: 88, responseTime: 105, tokensUsed: 5940 }
      ].map((organ) => ({
        ...organ,
        lastActivity: '2025-09-19T10:15:30.000Z',
        capabilities: ['analysis', 'recommendations', 'automation'],
      })),
      systemHealth: {
        cpu: 65,
        memory: 45,
        disk: 35,
        network: 95,
        timestamp: '2025-09-19T12:15:30.000Z',
        services: {
          odoo: true,
          postgres: true,
          redis: false,
          ai_orchestrator: true,
          bia_engine: false,
        },
      }
    }
  })

  if (isLoading && !dashboardData) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-4 text-blue-600" />
          <p className="text-slate-600">Loading BCM Platform...</p>
        </div>
      </div>
    )
  }

  const { kpis, recentActivity, aiOrgans, systemHealth } = dashboardData!

  const healthyOrgans = aiOrgans.filter(organ => organ.status === 'active').length
  const totalServices = Object.values(systemHealth.services).length
  const healthyServices = Object.values(systemHealth.services).filter(Boolean).length

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Header */}
      <div className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-10">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-slate-900">BCM Platform</h1>
              <p className="text-slate-600">Business Continuity Management Dashboard</p>
            </div>
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2 text-sm">
                <div className={cn(
                  "w-2 h-2 rounded-full",
                  healthyServices === totalServices ? "bg-green-500" : 
                  healthyServices > totalServices * 0.7 ? "bg-yellow-500" : "bg-red-500"
                )} />
                <span className="text-slate-600">
                  {healthyServices}/{totalServices} Services Online
                </span>
              </div>
              <Button variant="outline" size="sm" onClick={() => refetch()}>
                <RefreshCw className="h-4 w-4 mr-2" />
                Refresh
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="p-6 space-y-6">
        {/* KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <KPICard
            title="Total Risks"
            value={kpis.totalRisks}
            icon={AlertTriangle}
            change="+12 this month"
            changeType="increase"
            color="red"
          />
          <KPICard
            title="Active BCPs"
            value={kpis.activeBCPs}
            icon={Shield}
            change="+2 this week"
            changeType="increase"
            color="blue"
          />
          <KPICard
            title="Critical Incidents"
            value={kpis.criticalIncidents}
            icon={AlertTriangle}
            change="-1 vs last week"
            changeType="decrease"
            color="yellow"
          />
          <KPICard
            title="Compliance Score"
            value={`${kpis.complianceScore}%`}
            icon={TrendingUp}
            change="ISO 22301"
            changeType="neutral"
            color="green"
          />
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* AI Organisms Status */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-xl shadow-sm border p-6">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-2">
                  <Brain className="h-5 w-5 text-blue-600" />
                  <h2 className="text-lg font-semibold">AI Organisms</h2>
                  <span className="text-sm text-slate-500">
                    {healthyOrgans}/{aiOrgans.length} Active
                  </span>
                </div>
                <Button variant="outline" size="sm">
                  <Settings className="h-4 w-4 mr-2" />
                  Manage
                </Button>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {aiOrgans.slice(0, 6).map((organ) => (
                  <div key={organ.id} className="p-4 border rounded-lg hover:shadow-md transition-shadow">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="font-medium text-sm">{organ.name}</h3>
                      <div className={cn(
                        "w-2 h-2 rounded-full",
                        organ.status === 'active' ? "bg-green-500" :
                        organ.status === 'idle' ? "bg-yellow-500" : "bg-red-500"
                      )} />
                    </div>
                    <div className="text-xs text-slate-500 mb-2">
                      Health: {organ.health}% • {organ.responseTime}ms
                    </div>
                    <div className="w-full bg-slate-100 rounded-full h-1">
                      <div 
                        className={cn(
                          "h-1 rounded-full transition-all",
                          organ.health > 80 ? "bg-green-500" :
                          organ.health > 60 ? "bg-yellow-500" : "bg-red-500"
                        )}
                        style={{ width: `${organ.health}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
              
              {aiOrgans.length > 6 && (
                <div className="mt-4 text-center">
                  <Button variant="ghost" size="sm">
                    View All {aiOrgans.length} Organisms
                  </Button>
                </div>
              )}
            </div>
          </div>

          {/* Recent Activity */}
          <div className="bg-white rounded-xl shadow-sm border p-6">
            <div className="flex items-center gap-2 mb-6">
              <Activity className="h-5 w-5 text-blue-600" />
              <h2 className="text-lg font-semibold">Recent Activity</h2>
            </div>
            
            <div className="space-y-4">
              {recentActivity.map((activity) => (
                <div key={activity.id} className="flex gap-3">
                  <div className={cn(
                    "w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0",
                    activity.severity === 'critical' ? "bg-red-100 text-red-600" :
                    activity.severity === 'high' ? "bg-orange-100 text-orange-600" :
                    activity.severity === 'medium' ? "bg-yellow-100 text-yellow-600" :
                    "bg-blue-100 text-blue-600"
                  )}>
                    {activity.type === 'risk' && <AlertTriangle className="h-4 w-4" />}
                    {activity.type === 'bcp' && <Shield className="h-4 w-4" />}
                    {activity.type === 'incident' && <Activity className="h-4 w-4" />}
                    {activity.type === 'training' && <Users className="h-4 w-4" />}
                    {activity.type === 'audit' && <BarChart3 className="h-4 w-4" />}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-slate-900 truncate">
                      {activity.title}
                    </p>
                    <p className="text-xs text-slate-500 line-clamp-2">
                      {activity.description}
                    </p>
                    <p className="text-xs text-slate-400 mt-1">
                      {activity.timestamp.split('T')[1].split('.')[0]}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white rounded-xl shadow-sm border p-6">
          <h2 className="text-lg font-semibold mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Button className="h-auto p-4 justify-start" variant="outline">
              <div className="text-left">
                <div className="font-medium">Create Risk Assessment</div>
                <div className="text-sm text-slate-500">Start new risk analysis</div>
              </div>
            </Button>
            <Button className="h-auto p-4 justify-start" variant="outline">
              <div className="text-left">
                <div className="font-medium">Report Incident</div>
                <div className="text-sm text-slate-500">Log new business disruption</div>
              </div>
            </Button>
            <Button className="h-auto p-4 justify-start" variant="outline">
              <div className="text-left">
                <div className="font-medium">Schedule Exercise</div>
                <div className="text-sm text-slate-500">Plan continuity training</div>
              </div>
            </Button>
          </div>
        </div>

        {/* External Links */}
        <div className="bg-white rounded-xl shadow-sm border p-6">
          <h2 className="text-lg font-semibold mb-4">System Access</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Button variant="outline" size="sm" className="justify-between">
              Odoo BCM Core
              <ExternalLink className="h-4 w-4" />
            </Button>
            <Button variant="outline" size="sm" className="justify-between">
              AI Orchestrator
              <ExternalLink className="h-4 w-4" />
            </Button>
            <Button variant="outline" size="sm" className="justify-between">
              Grafana Monitoring
              <ExternalLink className="h-4 w-4" />
            </Button>
            <Button variant="outline" size="sm" className="justify-between">
              Admin Panel
              <ExternalLink className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}

interface KPICardProps {
  title: string
  value: string | number
  icon: React.ComponentType<{ className?: string }>
  change: string
  changeType: 'increase' | 'decrease' | 'neutral'
  color: 'red' | 'blue' | 'yellow' | 'green'
}

function KPICard({ title, value, icon: Icon, change, changeType, color }: KPICardProps) {
  return (
    <div className="bg-white rounded-xl shadow-sm border p-6">
      <div className="flex items-center justify-between mb-4">
        <div className={cn(
          "w-10 h-10 rounded-lg flex items-center justify-center",
          color === 'red' ? "bg-red-100 text-red-600" :
          color === 'blue' ? "bg-blue-100 text-blue-600" :
          color === 'yellow' ? "bg-yellow-100 text-yellow-600" :
          "bg-green-100 text-green-600"
        )}>
          <Icon className="h-5 w-5" />
        </div>
      </div>
      <div className="space-y-1">
        <p className="text-2xl font-bold text-slate-900">{value}</p>
        <p className="text-sm font-medium text-slate-600">{title}</p>
        <p className={cn(
          "text-xs",
          changeType === 'increase' ? "text-green-600" :
          changeType === 'decrease' ? "text-red-600" :
          "text-slate-500"
        )}>
          {change}
        </p>
      </div>
    </div>
  )
}
