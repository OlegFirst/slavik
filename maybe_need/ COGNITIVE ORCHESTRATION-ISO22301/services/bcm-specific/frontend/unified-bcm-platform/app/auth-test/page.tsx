'use client'

import React from 'react'
import { AuthStatus } from '@/components/auth/AuthStatus'
import { UserProfile } from '@/components/auth/UserProfile'
import { ProtectedRoute, useAuth } from '@/components/auth/AuthProvider'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  Shield,
  User,
  Server,
  Database,
  TestTube,
  Settings,
  Lock,
  CheckCircle,
  AlertTriangle
} from 'lucide-react'

function AuthTestDashboard() {
  const { user, hasPermission, hasRole } = useAuth()

  const testPermissions = [
    'bcm.read_all',
    'bcm.write_all',
    'bcm.admin',
    'bcm.read_bia',
    'bcm.write_incidents',
    'bcm.super_admin_only'
  ]

  const testRoles = [
    'super_admin',
    'org_admin',
    'manager',
    'analyst',
    'viewer'
  ]

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            🔐 BCM Platform Authentication Test Suite
          </h1>
          <p className="text-gray-600">
            Comprehensive testing environment for unified authentication system
          </p>
        </div>

        {/* Test Tabs */}
        <Tabs defaultValue="status" className="space-y-6">
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="status" className="flex items-center space-x-2">
              <Server className="h-4 w-4" />
              <span>System Status</span>
            </TabsTrigger>
            <TabsTrigger value="auth" className="flex items-center space-x-2">
              <Shield className="h-4 w-4" />
              <span>Authentication</span>
            </TabsTrigger>
            <TabsTrigger value="permissions" className="flex items-center space-x-2">
              <Lock className="h-4 w-4" />
              <span>Permissions</span>
            </TabsTrigger>
            <TabsTrigger value="profile" className="flex items-center space-x-2">
              <User className="h-4 w-4" />
              <span>User Profile</span>
            </TabsTrigger>
            <TabsTrigger value="api" className="flex items-center space-x-2">
              <Database className="h-4 w-4" />
              <span>API Test</span>
            </TabsTrigger>
          </TabsList>

          {/* System Status Tab */}
          <TabsContent value="status">
            <AuthStatus />
          </TabsContent>

          {/* Authentication Tab */}
          <TabsContent value="auth">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Shield className="h-5 w-5" />
                  <span>Authentication Status</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                {user ? (
                  <div className="space-y-4">
                    <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                      <div className="flex items-center space-x-2 text-green-800">
                        <CheckCircle className="h-5 w-5" />
                        <span className="font-medium">Authentication Successful</span>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <h3 className="font-medium mb-3">User Information</h3>
                        <div className="space-y-2 text-sm">
                          <div><strong>Name:</strong> {user.firstName} {user.lastName}</div>
                          <div><strong>Email:</strong> {user.email}</div>
                          <div><strong>Role:</strong> <Badge>{user.role}</Badge></div>
                          <div><strong>Company:</strong> {user.companyName} (#{user.companyId})</div>
                          <div><strong>Departments:</strong> {user.departments.join(', ')}</div>
                        </div>
                      </div>

                      <div>
                        <h3 className="font-medium mb-3">Session Information</h3>
                        <div className="space-y-2 text-sm">
                          <div><strong>Session ID:</strong> {user.sessionId.substring(0, 20)}...</div>
                          <div><strong>Expires:</strong> {user.expiresAt.toLocaleString()}</div>
                          <div><strong>Keycloak ID:</strong> {user.keycloakId}</div>
                          <div><strong>Odoo User ID:</strong> {user.odooUserId}</div>
                          <div><strong>Supabase ID:</strong> {user.supabaseId}</div>
                        </div>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                    <div className="flex items-center space-x-2 text-yellow-800">
                      <AlertTriangle className="h-5 w-5" />
                      <span className="font-medium">Not Authenticated</span>
                    </div>
                    <p className="text-yellow-700 mt-2">Please use the authentication form above to log in.</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Permissions Tab */}
          <TabsContent value="permissions">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Permission Tests */}
              <Card>
                <CardHeader>
                  <CardTitle>Permission Tests</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {testPermissions.map(permission => {
                      const hasThisPermission = hasPermission(permission)
                      return (
                        <div key={permission} className="flex items-center justify-between p-3 border rounded">
                          <span className="text-sm font-mono">{permission}</span>
                          <Badge variant={hasThisPermission ? 'default' : 'outline'}>
                            {hasThisPermission ? 'GRANTED' : 'DENIED'}
                          </Badge>
                        </div>
                      )
                    })}
                  </div>
                </CardContent>
              </Card>

              {/* Role Tests */}
              <Card>
                <CardHeader>
                  <CardTitle>Role Tests</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {testRoles.map(role => {
                      const hasThisRole = hasRole(role)
                      return (
                        <div key={role} className="flex items-center justify-between p-3 border rounded">
                          <span className="text-sm font-mono">{role}</span>
                          <Badge variant={hasThisRole ? 'default' : 'outline'}>
                            {hasThisRole ? 'ACTIVE' : 'INACTIVE'}
                          </Badge>
                        </div>
                      )
                    })}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Protected Content Examples */}
            <Card className="mt-6">
              <CardHeader>
                <CardTitle>Protected Content Examples</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <ProtectedRoute
                  requiredPermission="bcm.read_all"
                  fallback={<div className="p-3 bg-red-50 border border-red-200 rounded text-red-800">❌ Access denied - bcm.read_all permission required</div>}
                >
                  <div className="p-3 bg-green-50 border border-green-200 rounded text-green-800">
                    ✅ Content visible with bcm.read_all permission
                  </div>
                </ProtectedRoute>

                <ProtectedRoute
                  requiredRole="org_admin"
                  fallback={<div className="p-3 bg-red-50 border border-red-200 rounded text-red-800">❌ Access denied - org_admin role required</div>}
                >
                  <div className="p-3 bg-green-50 border border-green-200 rounded text-green-800">
                    ✅ Content visible to org_admin role
                  </div>
                </ProtectedRoute>

                <ProtectedRoute
                  requiredPermission="bcm.super_admin_only"
                  fallback={<div className="p-3 bg-red-50 border border-red-200 rounded text-red-800">❌ Access denied - super admin permission required</div>}
                >
                  <div className="p-3 bg-green-50 border border-green-200 rounded text-green-800">
                    ✅ Super admin content visible
                  </div>
                </ProtectedRoute>
              </CardContent>
            </Card>
          </TabsContent>

          {/* User Profile Tab */}
          <TabsContent value="profile">
            <ProtectedRoute
              fallback={
                <Card>
                  <CardContent className="text-center py-8">
                    <AlertTriangle className="h-12 w-12 text-yellow-500 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">Authentication Required</h3>
                    <p className="text-gray-600">Please log in to view your user profile.</p>
                  </CardContent>
                </Card>
              }
            >
              <UserProfile />
            </ProtectedRoute>
          </TabsContent>

          {/* API Test Tab */}
          <TabsContent value="api">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Database className="h-5 w-5" />
                  <span>API Integration Test</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <h3 className="font-medium text-blue-900 mb-2">API Test Suite</h3>
                    <p className="text-blue-800 text-sm">
                      This section will test API integration with Odoo, Supabase, and other services.
                    </p>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <Button variant="outline" className="flex items-center space-x-2">
                      <TestTube className="h-4 w-4" />
                      <span>Test Odoo API</span>
                    </Button>
                    <Button variant="outline" className="flex items-center space-x-2">
                      <TestTube className="h-4 w-4" />
                      <span>Test Supabase API</span>
                    </Button>
                    <Button variant="outline" className="flex items-center space-x-2">
                      <TestTube className="h-4 w-4" />
                      <span>Test Redis Cache</span>
                    </Button>
                  </div>

                  <div className="text-sm text-gray-600">
                    API testing functionality will be implemented as services come online.
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}

export default function AuthTestPage() {
  return <AuthTestDashboard />
}