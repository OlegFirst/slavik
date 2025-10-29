'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Building, Map, Brain, AlertTriangle, Settings, Play } from 'lucide-react'

export default function DigitalTwinPage() {
  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Digital Twin of Organization
          </h1>
          <p className="text-lg text-gray-600">
            Comprehensive digital representation of your organization
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Building className="h-6 w-6" />
                3D Organization Model
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-64 bg-gradient-to-br from-blue-50 to-indigo-100 rounded-lg border-2 border-dashed border-blue-200 flex items-center justify-center">
                <div className="text-center">
                  <Building className="h-12 w-12 mx-auto mb-4 text-blue-500" />
                  <h3 className="text-lg font-semibold text-gray-700 mb-2">
                    3D Visualization
                  </h3>
                  <p className="text-gray-600 mb-4">
                    Interactive 3D model
                  </p>
                  <Button>
                    <Play className="h-4 w-4 mr-2" />
                    Launch 3D View
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Brain className="h-6 w-6" />
                AI Analysis
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between p-3 bg-blue-50 rounded">
                  <span className="text-sm font-medium">Risk Analysis</span>
                  <Badge className="bg-blue-100 text-blue-800">Active</Badge>
                </div>
                <div className="flex items-center justify-between p-3 bg-green-50 rounded">
                  <span className="text-sm font-medium">Context Mapping</span>
                  <Badge className="bg-green-100 text-green-800">Complete</Badge>
                </div>
                <div className="flex items-center justify-between p-3 bg-yellow-50 rounded">
                  <span className="text-sm font-medium">Simulation</span>
                  <Badge className="bg-yellow-100 text-yellow-800">Queued</Badge>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}