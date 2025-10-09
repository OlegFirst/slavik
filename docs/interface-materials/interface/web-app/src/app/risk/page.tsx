'use client'

import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'
import { MainLayout } from '@/components/layout/main-layout'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { AlertTriangle, Plus, TrendingUp, Shield } from 'lucide-react'
import type { Risk } from '@/types'

export default function RiskPage() {
  const { data: risks, isLoading } = useQuery({
    queryKey: ['risks'],
    queryFn: () => apiClient.getRisks(),
    // Mock data for development
    placeholderData: [
      {
        id: '1',
        organization_id: 'org1',
        name: 'Cybersecurity Data Breach',
        description: 'Potential unauthorized access to customer data',
        category: 'technology',
        likelihood: 4,
        impact: 5,
        risk_score: 20,
        status: 'assessed',
        owner: 'IT Security Team',
        mitigation_strategy: 'Enhanced monitoring, MFA implementation',
        created_at: '2025-09-01T10:00:00Z',
        updated_at: '2025-10-01T15:30:00Z',
      },
      {
        id: '2',
        organization_id: 'org1',
        name: 'Supply Chain Disruption',
        description: 'Critical supplier failure affecting operations',
        category: 'operational',
        likelihood: 3,
        impact: 4,
        risk_score: 12,
        status: 'treated',
        owner: 'Operations Manager',
        mitigation_strategy: 'Diversify suppliers, maintain buffer stock',
        created_at: '2025-09-15T08:00:00Z',
        updated_at: '2025-10-05T12:00:00Z',
      },
      {
        id: '3',
        organization_id: 'org1',
        name: 'Regulatory Non-Compliance',
        description: 'Failure to meet ISO 22301 requirements',
        category: 'compliance',
        likelihood: 2,
        impact: 4,
        risk_score: 8,
        status: 'monitored',
        owner: 'Compliance Officer',
        mitigation_strategy: 'Regular audits, training programs',
        created_at: '2025-09-20T14:00:00Z',
        updated_at: '2025-10-08T10:00:00Z',
      },
      {
        id: '4',
        organization_id: 'org1',
        name: 'Key Personnel Loss',
        description: 'Critical staff departure affecting operations',
        category: 'strategic',
        likelihood: 3,
        impact: 3,
        risk_score: 9,
        status: 'identified',
        owner: 'HR Director',
        created_at: '2025-10-01T09:00:00Z',
        updated_at: '2025-10-08T09:00:00Z',
      },
    ] as Risk[],
  })

  const riskMatrix = risks?.reduce(
    (acc, risk) => {
      if (risk.risk_score >= 15) acc.critical.push(risk)
      else if (risk.risk_score >= 10) acc.high.push(risk)
      else if (risk.risk_score >= 5) acc.medium.push(risk)
      else acc.low.push(risk)
      return acc
    },
    { critical: [], high: [], medium: [], low: [] } as {
      critical: Risk[]
      high: Risk[]
      medium: Risk[]
      low: Risk[]
    }
  )

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Risk Management</h1>
            <p className="text-muted-foreground">
              Identify, assess, and mitigate organizational risks
            </p>
          </div>
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            Report New Risk
          </Button>
        </div>

        {/* Stats */}
        <div className="grid gap-4 md:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Risks</CardTitle>
              <AlertTriangle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{risks?.length || 0}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Critical</CardTitle>
              <AlertTriangle className="h-4 w-4 text-red-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-500">
                {riskMatrix?.critical.length || 0}
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">High Priority</CardTitle>
              <AlertTriangle className="h-4 w-4 text-orange-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-orange-500">
                {riskMatrix?.high.length || 0}
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Mitigated</CardTitle>
              <Shield className="h-4 w-4 text-green-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {risks?.filter((r) => r.status === 'treated').length || 0}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Risk Heat Map */}
        <Card>
          <CardHeader>
            <CardTitle>Risk Heat Map</CardTitle>
            <CardDescription>Visual representation of risk likelihood vs impact</CardDescription>
          </CardHeader>
          <CardContent>
            <RiskHeatMap risks={risks || []} />
          </CardContent>
        </Card>

        {/* Risk List Tabs */}
        <Tabs defaultValue="all">
          <TabsList>
            <TabsTrigger value="all">All Risks</TabsTrigger>
            <TabsTrigger value="critical">Critical</TabsTrigger>
            <TabsTrigger value="high">High</TabsTrigger>
            <TabsTrigger value="treated">Treated</TabsTrigger>
          </TabsList>

          <TabsContent value="all" className="space-y-4 mt-6">
            <div className="space-y-4">
              {risks?.map((risk) => (
                <RiskCard key={risk.id} risk={risk} />
              ))}
            </div>
          </TabsContent>

          <TabsContent value="critical" className="space-y-4 mt-6">
            <div className="space-y-4">
              {riskMatrix?.critical.map((risk) => (
                <RiskCard key={risk.id} risk={risk} />
              ))}
            </div>
          </TabsContent>

          <TabsContent value="high" className="space-y-4 mt-6">
            <div className="space-y-4">
              {riskMatrix?.high.map((risk) => (
                <RiskCard key={risk.id} risk={risk} />
              ))}
            </div>
          </TabsContent>

          <TabsContent value="treated" className="space-y-4 mt-6">
            <div className="space-y-4">
              {risks?.filter((r) => r.status === 'treated').map((risk) => (
                <RiskCard key={risk.id} risk={risk} />
              ))}
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </MainLayout>
  )
}

function RiskCard({ risk }: { risk: Risk }) {
  const severityColor =
    risk.risk_score >= 15
      ? 'destructive'
      : risk.risk_score >= 10
      ? 'warning'
      : risk.risk_score >= 5
      ? 'info'
      : 'secondary'

  const statusColors = {
    identified: 'secondary',
    assessed: 'info',
    treated: 'success',
    monitored: 'warning',
    closed: 'outline',
  } as const

  return (
    <Card>
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-2">
              <CardTitle className="text-lg">{risk.name}</CardTitle>
              <Badge variant={severityColor}>Score: {risk.risk_score}/25</Badge>
              <Badge variant={statusColors[risk.status]}>{risk.status}</Badge>
            </div>
            <CardDescription className="mt-2">{risk.description}</CardDescription>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid gap-4 md:grid-cols-2">
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Category</span>
              <span className="font-medium capitalize">{risk.category}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Likelihood</span>
              <span className="font-medium">{risk.likelihood}/5</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Impact</span>
              <span className="font-medium">{risk.impact}/5</span>
            </div>
          </div>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Owner</span>
              <span className="font-medium">{risk.owner}</span>
            </div>
            {risk.mitigation_strategy && (
              <div className="text-sm">
                <span className="text-muted-foreground">Mitigation: </span>
                <span className="text-muted-foreground">{risk.mitigation_strategy}</span>
              </div>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

function RiskHeatMap({ risks }: { risks: Risk[] }) {
  // Create a 5x5 matrix
  const matrix = Array.from({ length: 5 }, (_, i) =>
    Array.from({ length: 5 }, (_, j) => ({
      likelihood: 5 - i,
      impact: j + 1,
      risks: risks.filter(
        (r) => r.likelihood === 5 - i && r.impact === j + 1
      ),
    }))
  )

  const getCellColor = (likelihood: number, impact: number) => {
    const score = likelihood * impact
    if (score >= 15) return 'bg-red-500'
    if (score >= 10) return 'bg-orange-500'
    if (score >= 5) return 'bg-yellow-500'
    return 'bg-green-500'
  }

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-6 gap-2">
        {/* Empty corner */}
        <div className="text-center text-sm font-medium"></div>
        {/* Impact headers */}
        {[1, 2, 3, 4, 5].map((i) => (
          <div key={i} className="text-center text-sm font-medium">
            {i}
          </div>
        ))}

        {/* Matrix rows */}
        {matrix.map((row, rowIdx) => (
          <>
            {/* Likelihood label */}
            <div className="text-center text-sm font-medium flex items-center justify-center">
              {5 - rowIdx}
            </div>
            {/* Risk cells */}
            {row.map((cell, colIdx) => (
              <div
                key={`${rowIdx}-${colIdx}`}
                className={`${getCellColor(
                  cell.likelihood,
                  cell.impact
                )} h-16 rounded flex items-center justify-center text-white font-bold cursor-pointer hover:opacity-80 transition-opacity`}
                title={`${cell.risks.length} risk(s)`}
              >
                {cell.risks.length > 0 && cell.risks.length}
              </div>
            ))}
          </>
        ))}
      </div>
      <div className="flex items-center justify-between text-sm text-muted-foreground">
        <div className="flex items-center gap-2">
          <TrendingUp className="h-4 w-4" />
          <span>Likelihood</span>
        </div>
        <div className="flex items-center gap-2">
          <span>Impact</span>
          <AlertTriangle className="h-4 w-4" />
        </div>
      </div>
    </div>
  )
}
