'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Building, Users, MapPin, Network } from 'lucide-react'

export function OrganizationMap() {
  return (
    <div className="p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold">Organization Mapping</h2>
        <p className="text-gray-600">Organizational structure and relationships visualization</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Building className="h-5 w-5 text-blue-600" />
              Executive Level
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm">CEO Office</span>
                <Badge className="bg-red-100 text-red-800">Critical</Badge>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm">Board Relations</span>
                <Badge className="bg-orange-100 text-orange-800">High</Badge>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users className="h-5 w-5 text-green-600" />
              Operations
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm">IT Operations</span>
                <Badge className="bg-red-100 text-red-800">Critical</Badge>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm">Business Operations</span>
                <Badge className="bg-yellow-100 text-yellow-800">Medium</Badge>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MapPin className="h-5 w-5 text-orange-600" />
              Locations
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm">Primary Data Center</span>
                <Badge className="bg-red-100 text-red-800">Critical</Badge>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm">Main Office</span>
                <Badge className="bg-orange-100 text-orange-800">High</Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="mt-8 text-center p-8 bg-gray-50 rounded-lg">
        <Network className="h-16 w-16 mx-auto mb-4 text-gray-400" />
        <h3 className="text-lg font-medium text-gray-700 mb-2">Interactive Organization Map</h3>
        <p className="text-gray-600">Detailed organizational mapping will be implemented here</p>
      </div>
    </div>
  )
}