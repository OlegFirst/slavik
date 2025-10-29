'use client'

import React from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { CheckCircle, AlertTriangle, Clock, FileText, Users, Shield } from 'lucide-react'

export function ComplianceDashboard() {
  const complianceMetrics = {
    overall: 78,
    sections: [
      { name: 'Context', completion: 85, status: 'good' },
      { name: 'Leadership', completion: 92, status: 'excellent' },
      { name: 'Planning', completion: 70, status: 'fair' },
      { name: 'Support', completion: 65, status: 'fair' },
      { name: 'Operation', completion: 80, status: 'good' },
      { name: 'Performance', completion: 88, status: 'good' },
      { name: 'Improvement', completion: 60, status: 'needs-work' }
    ]
  }

  const recentActivities = [
    { type: 'audit', description: 'ISO 22301 internal audit completed', date: '2 days ago' },
    { type: 'policy', description: 'Business Continuity Policy updated', date: '1 week ago' },
    { type: 'training', description: 'Staff BC awareness training conducted', date: '2 weeks ago' }
  ]

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'excellent': return 'bg-green-500'
      case 'good': return 'bg-blue-500'
      case 'fair': return 'bg-yellow-500'
      case 'needs-work': return 'bg-red-500'
      default: return 'bg-gray-500'
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'excellent': return 'default'
      case 'good': return 'secondary'
      case 'fair': return 'outline'
      case 'needs-work': return 'destructive'
      default: return 'outline'
    }
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">ISO 22301 Compliance Dashboard</h1>
          <p className="text-muted-foreground">
            Monitor and track compliance with ISO 22301:2019 Business Continuity Management
          </p>
        </div>
        <Badge variant="outline" className="text-lg px-4 py-2">
          {complianceMetrics.overall}% Complete
        </Badge>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Overall Progress</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{complianceMetrics.overall}%</div>
            <Progress value={complianceMetrics.overall} className="mt-2" />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Issues</CardTitle>
            <AlertTriangle className="h-4 w-4 text-amber-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">7</div>
            <p className="text-xs text-muted-foreground">
              3 critical, 4 minor
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Last Audit</CardTitle>
            <Clock className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">2</div>
            <p className="text-xs text-muted-foreground">
              days ago
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Documents</CardTitle>
            <FileText className="h-4 w-4 text-purple-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">24</div>
            <p className="text-xs text-muted-foreground">
              compliance docs
            </p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Compliance by Section</CardTitle>
            <CardDescription>
              Progress across ISO 22301 main sections
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {complianceMetrics.sections.map((section) => (
              <div key={section.name} className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium">{section.name}</span>
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-muted-foreground">
                      {section.completion}%
                    </span>
                    <Badge variant={getStatusBadge(section.status)} className="text-xs">
                      {section.status.replace('-', ' ')}
                    </Badge>
                  </div>
                </div>
                <Progress value={section.completion} className="h-2" />
              </div>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
            <CardDescription>
              Latest compliance activities and updates
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentActivities.map((activity, index) => (
                <div key={index} className="flex items-start space-x-4">
                  <div className="flex-shrink-0">
                    {activity.type === 'audit' && <Shield className="h-5 w-5 text-blue-600" />}
                    {activity.type === 'policy' && <FileText className="h-5 w-5 text-green-600" />}
                    {activity.type === 'training' && <Users className="h-5 w-5 text-purple-600" />}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900">
                      {activity.description}
                    </p>
                    <p className="text-sm text-muted-foreground">
                      {activity.date}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Implementation Roadmap</CardTitle>
          <CardDescription>
            Planned activities for achieving full compliance
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 border rounded-lg">
              <div>
                <h4 className="font-medium">Complete Business Impact Analysis</h4>
                <p className="text-sm text-muted-foreground">Update BIA documentation and risk assessments</p>
              </div>
              <Badge variant="outline">Next Week</Badge>
            </div>
            <div className="flex items-center justify-between p-4 border rounded-lg">
              <div>
                <h4 className="font-medium">Exercise Testing Program</h4>
                <p className="text-sm text-muted-foreground">Conduct tabletop and full-scale exercises</p>
              </div>
              <Badge variant="outline">Next Month</Badge>
            </div>
            <div className="flex items-center justify-between p-4 border rounded-lg">
              <div>
                <h4 className="font-medium">External Audit Preparation</h4>
                <p className="text-sm text-muted-foreground">Prepare for certification audit</p>
              </div>
              <Badge variant="outline">Q2 2025</Badge>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}