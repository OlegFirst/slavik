'use client'

import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'
import { MainLayout } from '@/components/layout/main-layout'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Separator } from '@/components/ui/separator'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  FileText,
  Shield,
  TrendingUp,
  Users,
  Zap,
} from 'lucide-react'

export default function DashboardPage() {
  // Fetch dashboard data
  const { data: summary, isLoading } = useQuery({
    queryKey: ['dashboard', 'summary'],
    queryFn: () => apiClient.getDashboardSummary(),
    // Fallback mock data for development
    placeholderData: {
      total_assessments: 12,
      active_risks: 8,
      compliance_score: 87,
      active_incidents: 2,
      critical_processes: 15,
      overdue_tasks: 3,
    },
  })

  if (isLoading) {
    return (
      <MainLayout>
        <div className="flex items-center justify-center h-full">
          <div className="text-center">
            <Activity className="h-12 w-12 animate-spin mx-auto text-primary" />
            <p className="mt-4 text-muted-foreground">Loading dashboard...</p>
          </div>
        </div>
      </MainLayout>
    )
  }

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground">
            Welcome to your Business Continuity Management platform
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <StatCard
            title="BIA Assessments"
            value={summary?.total_assessments || 0}
            description="Active assessments"
            icon={FileText}
            trend="+2 this month"
          />
          <StatCard
            title="Active Risks"
            value={summary?.active_risks || 0}
            description="Requires attention"
            icon={AlertTriangle}
            trend="3 high priority"
            variant="warning"
          />
          <StatCard
            title="ISO 22301 Compliance"
            value={`${summary?.compliance_score || 0}%`}
            description="Overall compliance"
            icon={Shield}
            trend="+5% from last audit"
            variant="success"
          />
          <StatCard
            title="Critical Processes"
            value={summary?.critical_processes || 0}
            description="Monitored processes"
            icon={Activity}
            trend="All systems operational"
          />
        </div>

        {/* Main Content Grid */}
        <div className="grid gap-6 lg:grid-cols-2">
          {/* Journey Timeline */}
          <Card>
            <CardHeader>
              <CardTitle>BCM Journey</CardTitle>
              <CardDescription>Your progress toward full compliance</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <JourneyStep
                title="Organization Setup"
                status="completed"
                description="Profile and configuration complete"
              />
              <JourneyStep
                title="Business Impact Analysis"
                status="in-progress"
                description="12 assessments, 3 in progress"
                progress={75}
              />
              <JourneyStep
                title="Risk Assessment"
                status="in-progress"
                description="8 risks identified and assessed"
                progress={60}
              />
              <JourneyStep
                title="Recovery Planning"
                status="pending"
                description="Not started"
              />
              <JourneyStep
                title="Testing & Exercises"
                status="pending"
                description="Not started"
              />
            </CardContent>
          </Card>

          {/* AI Recommendations */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Zap className="h-5 w-5 text-yellow-500" />
                AI Recommendations
              </CardTitle>
              <CardDescription>Intelligent insights from your data</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <RecommendationItem
                priority="high"
                title="Critical Process Missing RTO"
                description="Payment Processing system lacks defined Recovery Time Objective"
                action="Define RTO"
              />
              <RecommendationItem
                priority="medium"
                title="Risk Treatment Overdue"
                description="3 high-priority risks have passed treatment deadline"
                action="Review Risks"
              />
              <RecommendationItem
                priority="low"
                title="Documentation Update"
                description="Business Continuity Policy requires annual review"
                action="Review Policy"
              />
            </CardContent>
          </Card>
        </div>

        {/* Recent Activities & Risk Overview */}
        <div className="grid gap-6 lg:grid-cols-2">
          {/* Recent Activities */}
          <Card>
            <CardHeader>
              <CardTitle>Recent Activities</CardTitle>
              <CardDescription>Latest updates across the platform</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <ActivityItem
                type="bia"
                title="BIA Assessment Completed"
                description="IT Infrastructure - Criticality: High"
                time="2 hours ago"
                user="John Smith"
              />
              <ActivityItem
                type="risk"
                title="Risk Assessed"
                description="Cybersecurity Threat - Score: 15/25"
                time="5 hours ago"
                user="Sarah Johnson"
              />
              <ActivityItem
                type="document"
                title="Document Approved"
                description="Incident Response Plan v2.1"
                time="1 day ago"
                user="Admin"
              />
              <ActivityItem
                type="compliance"
                title="Gap Analysis Updated"
                description="ISO 22301:2019 - 5 new items"
                time="2 days ago"
                user="Mike Davis"
              />
            </CardContent>
          </Card>

          {/* Risk Heat Map Preview */}
          <Card>
            <CardHeader>
              <CardTitle>Risk Overview</CardTitle>
              <CardDescription>Distribution by severity</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <RiskBar label="Critical" count={2} total={20} color="bg-red-500" />
                <RiskBar label="High" count={6} total={20} color="bg-orange-500" />
                <RiskBar label="Medium" count={8} total={20} color="bg-yellow-500" />
                <RiskBar label="Low" count={4} total={20} color="bg-green-500" />
              </div>
              <div className="mt-4 pt-4 border-t">
                <p className="text-sm text-muted-foreground">
                  Total: <span className="font-semibold">{summary?.active_risks || 0} active risks</span>
                </p>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
            <CardDescription>Common tasks and workflows</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-3">
              <QuickActionButton
                icon={FileText}
                title="New BIA Assessment"
                description="Start business impact analysis"
              />
              <QuickActionButton
                icon={AlertTriangle}
                title="Report Risk"
                description="Identify and assess new risk"
              />
              <QuickActionButton
                icon={Activity}
                title="Run Simulation"
                description="Digital Twin disruption test"
              />
            </div>
          </CardContent>
        </Card>
      </div>
    </MainLayout>
  )
}

// Component Helpers
function StatCard({
  title,
  value,
  description,
  icon: Icon,
  trend,
  variant = 'default',
}: any) {
  const colors = {
    default: 'bg-blue-500',
    warning: 'bg-yellow-500',
    success: 'bg-green-500',
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        <Icon className={`h-4 w-4 ${colors[variant]} text-white rounded p-0.5`} />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        <p className="text-xs text-muted-foreground">{description}</p>
        {trend && (
          <p className="text-xs text-muted-foreground mt-2 flex items-center gap-1">
            <TrendingUp className="h-3 w-3" />
            {trend}
          </p>
        )}
      </CardContent>
    </Card>
  )
}

function JourneyStep({ title, status, description, progress }: any) {
  const statusColors = {
    completed: 'bg-green-500',
    'in-progress': 'bg-blue-500',
    pending: 'bg-gray-300',
  }

  return (
    <div className="flex gap-4">
      <div className="flex flex-col items-center">
        <div
          className={`h-8 w-8 rounded-full ${statusColors[status]} flex items-center justify-center`}
        >
          {status === 'completed' && <CheckCircle2 className="h-5 w-5 text-white" />}
          {status === 'in-progress' && <Activity className="h-5 w-5 text-white animate-pulse" />}
        </div>
        {status !== 'pending' && <div className="w-0.5 h-full bg-gray-200 mt-2" />}
      </div>
      <div className="flex-1 pb-4">
        <h4 className="font-semibold">{title}</h4>
        <p className="text-sm text-muted-foreground">{description}</p>
        {progress && (
          <Progress value={progress} className="mt-2 h-2" />
        )}
      </div>
    </div>
  )
}

function RecommendationItem({ priority, title, description, action }: any) {
  const priorityColors = {
    high: 'destructive',
    medium: 'warning',
    low: 'secondary',
  }

  return (
    <div className="flex items-start gap-3 p-3 border rounded-lg">
      <Zap className="h-5 w-5 text-yellow-500 mt-0.5" />
      <div className="flex-1">
        <div className="flex items-center gap-2">
          <h4 className="font-semibold text-sm">{title}</h4>
          <Badge variant={priorityColors[priority]} className="text-xs">
            {priority}
          </Badge>
        </div>
        <p className="text-sm text-muted-foreground mt-1">{description}</p>
        <button className="text-sm text-primary hover:underline mt-2">
          {action} →
        </button>
      </div>
    </div>
  )
}

function ActivityItem({ type, title, description, time, user }: any) {
  const icons = {
    bia: FileText,
    risk: AlertTriangle,
    document: FileText,
    compliance: Shield,
  }
  const Icon = icons[type]

  return (
    <div className="flex gap-3">
      <div className="h-8 w-8 rounded-full bg-muted flex items-center justify-center">
        <Icon className="h-4 w-4" />
      </div>
      <div className="flex-1">
        <h4 className="text-sm font-semibold">{title}</h4>
        <p className="text-sm text-muted-foreground">{description}</p>
        <p className="text-xs text-muted-foreground mt-1">
          {time} • {user}
        </p>
      </div>
    </div>
  )
}

function RiskBar({ label, count, total, color }: any) {
  const percentage = (count / total) * 100

  return (
    <div>
      <div className="flex justify-between text-sm mb-1">
        <span className="font-medium">{label}</span>
        <span className="text-muted-foreground">{count}</span>
      </div>
      <div className="h-2 bg-muted rounded-full overflow-hidden">
        <div
          className={`h-full ${color}`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  )
}

function QuickActionButton({ icon: Icon, title, description }: any) {
  return (
    <button className="flex items-start gap-3 p-4 border rounded-lg hover:border-primary hover:shadow-md transition-all text-left">
      <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center">
        <Icon className="h-5 w-5 text-primary" />
      </div>
      <div>
        <h4 className="font-semibold text-sm">{title}</h4>
        <p className="text-xs text-muted-foreground mt-1">{description}</p>
      </div>
    </button>
  )
}
