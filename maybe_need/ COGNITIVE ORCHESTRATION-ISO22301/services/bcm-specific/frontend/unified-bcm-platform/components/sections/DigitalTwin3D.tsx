'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Globe, Users, Activity, RefreshCw } from 'lucide-react'

interface DigitalTwin3DProps {
  className?: string
}

export function DigitalTwin3D({ className }: DigitalTwin3DProps) {
  return (
    <div className={`space-y-6 ${className}`}>
      <div className="flex justify-between items-center">
        <div>
          <h3 className="text-xl font-semibold flex items-center gap-2">
            <Globe className="h-6 w-6 text-blue-600" />
            Organization Digital Twin
          </h3>
          <p className="text-sm text-gray-600 mt-1">
            3D visualization of organizational structure and processes
          </p>
        </div>

        <Button variant="outline" size="sm">
          <RefreshCw className="h-4 w-4 mr-2" />
          Sync
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <Card>
            <CardContent className="p-6">
              <div className="h-96 bg-gradient-to-br from-blue-50 to-purple-50 rounded-lg flex items-center justify-center">
                <div className="text-center">
                  <Globe className="h-16 w-16 mx-auto mb-4 text-blue-600" />
                  <h3 className="text-lg font-medium text-gray-700 mb-2">3D Digital Twin</h3>
                  <p className="text-gray-600">Interactive 3D visualization will be implemented here</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Activity className="h-5 w-5" />
                System Overview
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4 text-center">
                <div>
                  <div className="text-2xl font-bold text-green-600">8</div>
                  <div className="text-xs text-gray-600">Healthy</div>
                </div>
                <div>
                  <div className="text-2xl font-bold text-blue-600">12</div>
                  <div className="text-xs text-gray-600">Components</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Integration Status</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm">Backend:</span>
                  <Badge className="bg-green-100 text-green-800">Connected</Badge>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm">Real-time:</span>
                  <Badge className="bg-blue-100 text-blue-800">Active</Badge>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}