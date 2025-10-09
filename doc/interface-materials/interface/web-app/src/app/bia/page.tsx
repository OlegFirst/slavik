'use client'

import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'
import { MainLayout } from '@/components/layout/main-layout'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { FileText, Plus, Clock, CheckCircle2, AlertCircle } from 'lucide-react'
import type { BIAAssessment } from '@/types'

export default function BIAPage() {
  const { data: assessments, isLoading } = useQuery({
    queryKey: ['bia', 'assessments'],
    queryFn: () => apiClient.getBIAs(),
    // Mock data for development
    placeholderData: [
      {
        id: '1',
        organization_id: 'org1',
        name: 'IT Infrastructure Assessment',
        description: 'Critical IT systems and infrastructure',
        status: 'completed',
        criticality_score: 9.2,
        rto: 4,
        rpo: 1,
        mtpd: 24,
        created_by: 'admin',
        created_at: '2025-09-15T10:00:00Z',
        updated_at: '2025-10-01T15:30:00Z',
      },
      {
        id: '2',
        organization_id: 'org1',
        name: 'Payment Processing System',
        description: 'Customer payment and transaction processing',
        status: 'in_progress',
        criticality_score: 9.8,
        rto: 2,
        rpo: 0.5,
        mtpd: 8,
        created_by: 'admin',
        created_at: '2025-10-05T08:00:00Z',
        updated_at: '2025-10-08T12:00:00Z',
      },
      {
        id: '3',
        organization_id: 'org1',
        name: 'Customer Support Operations',
        description: 'Support ticketing and communication systems',
        status: 'draft',
        criticality_score: 7.5,
        rto: 8,
        rpo: 4,
        mtpd: 48,
        created_by: 'admin',
        created_at: '2025-10-08T14:00:00Z',
        updated_at: '2025-10-08T14:00:00Z',
      },
    ] as BIAAssessment[],
  })

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Business Impact Analysis</h1>
            <p className="text-muted-foreground">
              Assess and prioritize critical business functions
            </p>
          </div>
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            New BIA Assessment
          </Button>
        </div>

        {/* Stats */}
        <div className="grid gap-4 md:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Assessments</CardTitle>
              <FileText className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{assessments?.length || 0}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Completed</CardTitle>
              <CheckCircle2 className="h-4 w-4 text-green-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {assessments?.filter((a) => a.status === 'completed').length || 0}
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">In Progress</CardTitle>
              <Clock className="h-4 w-4 text-blue-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {assessments?.filter((a) => a.status === 'in_progress').length || 0}
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Avg Criticality</CardTitle>
              <AlertCircle className="h-4 w-4 text-orange-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {assessments?.length
                  ? (
                      assessments.reduce((sum, a) => sum + a.criticality_score, 0) /
                      assessments.length
                    ).toFixed(1)
                  : '0'}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Tabs */}
        <Tabs defaultValue="all">
          <TabsList>
            <TabsTrigger value="all">All Assessments</TabsTrigger>
            <TabsTrigger value="in_progress">In Progress</TabsTrigger>
            <TabsTrigger value="completed">Completed</TabsTrigger>
            <TabsTrigger value="draft">Drafts</TabsTrigger>
          </TabsList>

          <TabsContent value="all" className="space-y-4 mt-6">
            {isLoading ? (
              <Card>
                <CardContent className="p-6">
                  <p className="text-center text-muted-foreground">Loading assessments...</p>
                </CardContent>
              </Card>
            ) : (
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {assessments?.map((assessment) => (
                  <BIACard key={assessment.id} assessment={assessment} />
                ))}
              </div>
            )}
          </TabsContent>

          <TabsContent value="in_progress" className="space-y-4 mt-6">
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {assessments
                ?.filter((a) => a.status === 'in_progress')
                .map((assessment) => (
                  <BIACard key={assessment.id} assessment={assessment} />
                ))}
            </div>
          </TabsContent>

          <TabsContent value="completed" className="space-y-4 mt-6">
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {assessments
                ?.filter((a) => a.status === 'completed')
                .map((assessment) => (
                  <BIACard key={assessment.id} assessment={assessment} />
                ))}
            </div>
          </TabsContent>

          <TabsContent value="draft" className="space-y-4 mt-6">
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {assessments
                ?.filter((a) => a.status === 'draft')
                .map((assessment) => (
                  <BIACard key={assessment.id} assessment={assessment} />
                ))}
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </MainLayout>
  )
}

function BIACard({ assessment }: { assessment: BIAAssessment }) {
  const statusColors = {
    draft: 'secondary',
    in_progress: 'info',
    completed: 'success',
    approved: 'success',
    archived: 'outline',
  } as const

  const criticalityColor =
    assessment.criticality_score >= 9
      ? 'text-red-500'
      : assessment.criticality_score >= 7
      ? 'text-orange-500'
      : 'text-yellow-500'

  return (
    <Card className="hover:shadow-lg transition-shadow cursor-pointer">
      <CardHeader>
        <div className="flex items-start justify-between">
          <CardTitle className="text-lg">{assessment.name}</CardTitle>
          <Badge variant={statusColors[assessment.status]}>
            {assessment.status.replace('_', ' ')}
          </Badge>
        </div>
        <CardDescription className="line-clamp-2">
          {assessment.description}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Criticality Score</span>
            <span className={`font-bold ${criticalityColor}`}>
              {assessment.criticality_score}/10
            </span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">RTO</span>
            <span className="font-medium">{assessment.rto}h</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">RPO</span>
            <span className="font-medium">{assessment.rpo}h</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">MTPD</span>
            <span className="font-medium">{assessment.mtpd}h</span>
          </div>
        </div>
        <div className="mt-4 pt-4 border-t">
          <p className="text-xs text-muted-foreground">
            Updated {new Date(assessment.updated_at).toLocaleDateString()}
          </p>
        </div>
      </CardContent>
    </Card>
  )
}
