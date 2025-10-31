'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { AlertTriangle, Shield, TrendingUp, Activity } from 'lucide-react'

export function RiskVisualization() {
  return (
    <div className="p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold">Risk Visualization</h2>
        <p className="text-gray-600">Visual representation of organizational risks and vulnerabilities</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-red-600" />
              Critical Risks
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm">Data Center Failure</span>
                <Badge className="bg-red-100 text-red-800">Critical</Badge>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm">Cyber Security Breach</span>
                <Badge className="bg-red-100 text-red-800">Critical</Badge>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm">Key Personnel Loss</span>
                <Badge className="bg-orange-100 text-orange-800">High</Badge>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="h-5 w-5 text-green-600" />
              Risk Mitigation
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm">Backup Systems</span>
                <Badge className="bg-green-100 text-green-800">Active</Badge>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm">Security Monitoring</span>
                <Badge className="bg-green-100 text-green-800">Active</Badge>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm">Training Programs</span>
                <Badge className="bg-yellow-100 text-yellow-800">Planned</Badge>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-blue-600" />
              Risk Trends
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm">Overall Risk Level</span>
                <Badge className="bg-orange-100 text-orange-800">Medium</Badge>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm">Trend Direction</span>
                <Badge className="bg-green-100 text-green-800">Improving</Badge>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm">Last Assessment</span>
                <span className="text-sm text-gray-600">2 days ago</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="mt-8 text-center p-8 bg-gray-50 rounded-lg">
        <Activity className="h-16 w-16 mx-auto mb-4 text-gray-400" />
        <h3 className="text-lg font-medium text-gray-700 mb-2">Interactive Risk Map</h3>
        <p className="text-gray-600">Detailed risk visualization and impact analysis will be implemented here</p>
      </div>
    </div>
  )
}