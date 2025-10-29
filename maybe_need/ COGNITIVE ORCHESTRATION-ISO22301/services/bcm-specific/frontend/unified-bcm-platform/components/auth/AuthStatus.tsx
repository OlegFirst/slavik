'use client'

import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import {
  CheckCircle,
  XCircle,
  AlertTriangle,
  Loader2,
  Server,
  Database,
  Zap,
  Shield,
  Wifi,
  WifiOff,
  RefreshCw,
  Settings
} from 'lucide-react'
import { useAuth } from './AuthProvider'
import { checkPlatformHealth, type PlatformHealth, getPlatformConfig } from '@/lib/auth/service-health-check'
import { centralizedBCM, centralizedSupabase } from '@/lib/supabase/centralized-client'

export function AuthStatus() {
  const { user, isAuthenticated, login, logout, isLoading } = useAuth()
  const [health, setHealth] = useState<PlatformHealth | null>(null)
  const [config, setConfig] = useState<any>(null)
  const [healthLoading, setHealthLoading] = useState(false)
  const [testCredentials, setTestCredentials] = useState({
    email: 'admin@bcm-platform.com',
    password: 'demo123'
  })
  const [supabaseTestResult, setSupabaseTestResult] = useState<any>(null)
  const [supabaseLoading, setSupabaseLoading] = useState(false)

  // Check platform health on mount
  useEffect(() => {
    checkHealth()
  }, [])

  // Get current config
  useEffect(() => {
    const currentConfig = getPlatformConfig()
    setConfig(currentConfig)
  }, [health])

  const checkHealth = async () => {
    setHealthLoading(true)
    try {
      const platformHealth = await checkPlatformHealth()
      setHealth(platformHealth)
    } catch (error) {
      console.error('Health check failed:', error)
    } finally {
      setHealthLoading(false)
    }
  }

  const handleTestLogin = async () => {
    try {
      await login(testCredentials.email, testCredentials.password)
    } catch (error) {
      console.error('Test login failed:', error)
    }
  }

  const handleSupabaseTest = async () => {
    setSupabaseLoading(true)
    try {
      // Test centralized Supabase connection
      const isConnected = await centralizedBCM.checkConnection()

      if (!isConnected) {
        setSupabaseTestResult({
          success: false,
          error: 'Failed to connect to centralized Supabase'
        })
        return
      }

      // Test user creation/retrieval with centralized schema
      const testResult = await centralizedSupabase.auth.signInWithPassword({
        email: 'demo@bcm-platform.com',
        password: 'demo123'
      })

      if (testResult.error) {
        // Try to sign up if user doesn't exist
        const signUpResult = await centralizedSupabase.auth.signUp({
          email: 'demo@bcm-platform.com',
          password: 'demo123',
          options: {
            data: {
              full_name: 'Demo User',
              company_id: 1
            }
          }
        })

        if (signUpResult.error) {
          throw signUpResult.error
        }

        setSupabaseTestResult({
          success: true,
          message: '✅ Centralized Supabase working! Demo user created.',
          userData: {
            id: signUpResult.data.user?.id,
            email: signUpResult.data.user?.email,
            created_via: 'centralized_signup'
          }
        })
      } else {
        // Get user from centralized bcm_users table
        const user = await centralizedBCM.getUser(testResult.data.user.id)

        setSupabaseTestResult({
          success: true,
          message: '✅ Centralized Supabase fully operational! User authenticated.',
          userData: {
            id: user?.id,
            email: user?.email,
            full_name: user?.full_name,
            company_id: user?.company_id,
            company_name: user?.bcm_companies?.name,
            schema: 'centralized_bcm'
          }
        })
      }
    } catch (error) {
      setSupabaseTestResult({
        success: false,
        error: error instanceof Error ? error.message : 'Centralized test failed'
      })
    } finally {
      setSupabaseLoading(false)
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'online': return <CheckCircle className="h-4 w-4 text-green-500" />
      case 'offline': return <XCircle className="h-4 w-4 text-red-500" />
      default: return <AlertTriangle className="h-4 w-4 text-yellow-500" />
    }
  }

  const getOverallStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'bg-green-100 text-green-800 border-green-200'
      case 'degraded': return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      case 'offline': return 'bg-red-100 text-red-800 border-red-200'
      default: return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  return (
    <div className="space-y-6 max-w-4xl mx-auto p-6">
      {/* Platform Health Status */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center space-x-2">
              <Server className="h-5 w-5" />
              <span>Platform Health Status</span>
            </CardTitle>
            <Button
              variant="outline"
              size="sm"
              onClick={checkHealth}
              disabled={healthLoading}
            >
              {healthLoading ? (
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
              ) : (
                <RefreshCw className="h-4 w-4 mr-2" />
              )}
              Refresh
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {health ? (
            <div className="space-y-4">
              {/* Overall Status */}
              <div className={`p-3 rounded-lg border ${getOverallStatusColor(health.overall)}`}>
                <div className="flex items-center space-x-2">
                  {health.overall === 'healthy' ? (
                    <Wifi className="h-5 w-5" />
                  ) : (
                    <WifiOff className="h-5 w-5" />
                  )}
                  <span className="font-medium">
                    Platform Status: {health.overall.toUpperCase()}
                  </span>
                </div>
              </div>

              {/* Services Status */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {health.services.map((service, index) => (
                  <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex items-center space-x-3">
                      {getStatusIcon(service.status)}
                      <div>
                        <div className="font-medium text-sm">{service.name}</div>
                        <div className="text-xs text-gray-600">{service.url}</div>
                      </div>
                    </div>
                    <div className="text-right">
                      <Badge variant={service.status === 'online' ? 'default' : 'secondary'}>
                        {service.status}
                      </Badge>
                      {service.responseTime && (
                        <div className="text-xs text-gray-600 mt-1">
                          {service.responseTime}ms
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>

              {/* Recommendations */}
              {health.recommendations.length > 0 && (
                <Alert>
                  <AlertTriangle className="h-4 w-4" />
                  <AlertDescription>
                    <div className="space-y-1">
                      {health.recommendations.map((rec, index) => (
                        <div key={index} className="text-sm">• {rec}</div>
                      ))}
                    </div>
                  </AlertDescription>
                </Alert>
              )}
            </div>
          ) : (
            <div className="flex items-center justify-center p-8">
              <Loader2 className="h-6 w-6 animate-spin mr-2" />
              Checking platform health...
            </div>
          )}
        </CardContent>
      </Card>

      {/* Authentication Configuration */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Shield className="h-5 w-5" />
            <span>Authentication Configuration</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {config ? (
            <div className="space-y-4">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center">
                  <div className="text-sm font-medium">Auth Mode</div>
                  <Badge className="mt-1">
                    {config.authMode}
                  </Badge>
                </div>
                <div className="text-center">
                  <div className="text-sm font-medium">Data Mode</div>
                  <Badge className="mt-1">
                    {config.dataMode}
                  </Badge>
                </div>
                <div className="text-center">
                  <div className="text-sm font-medium">AI Mode</div>
                  <Badge className="mt-1">
                    {config.aiMode}
                  </Badge>
                </div>
                <div className="text-center">
                  <div className="text-sm font-medium">Real-time</div>
                  <Badge className="mt-1">
                    {config.realtimeMode}
                  </Badge>
                </div>
              </div>

              <div className="space-y-2">
                <div className="text-sm font-medium">Available Features:</div>
                <div className="flex flex-wrap gap-2">
                  {Object.entries(config.features).map(([feature, enabled]) => (
                    <Badge
                      key={feature}
                      variant={enabled ? 'default' : 'outline'}
                      className="text-xs"
                    >
                      {feature}: {enabled ? 'ON' : 'OFF'}
                    </Badge>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="text-gray-600">Configuration loading...</div>
          )}
        </CardContent>
      </Card>

      {/* Authentication Test */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Zap className="h-5 w-5" />
            <span>Authentication Test</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {!isAuthenticated ? (
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium">Email</label>
                  <input
                    type="email"
                    className="w-full mt-1 px-3 py-2 border rounded-md"
                    value={testCredentials.email}
                    onChange={(e) => setTestCredentials(prev => ({ ...prev, email: e.target.value }))}
                  />
                </div>
                <div>
                  <label className="text-sm font-medium">Password</label>
                  <input
                    type="password"
                    className="w-full mt-1 px-3 py-2 border rounded-md"
                    value={testCredentials.password}
                    onChange={(e) => setTestCredentials(prev => ({ ...prev, password: e.target.value }))}
                  />
                </div>
              </div>
              <Button
                onClick={handleTestLogin}
                disabled={isLoading}
                className="w-full"
              >
                {isLoading ? (
                  <Loader2 className="h-4 w-4 animate-spin mr-2" />
                ) : (
                  <Shield className="h-4 w-4 mr-2" />
                )}
                Test Authentication
              </Button>
              <Alert>
                <AlertTriangle className="h-4 w-4" />
                <AlertDescription>
                  Demo Mode: Any email/password combination will work for testing.
                </AlertDescription>
              </Alert>
            </div>
          ) : (
            <div className="space-y-4">
              <Alert className="border-green-200 bg-green-50">
                <CheckCircle className="h-4 w-4 text-green-600" />
                <AlertDescription className="text-green-800">
                  ✅ Authentication successful! Welcome, {user?.firstName} {user?.lastName}
                </AlertDescription>
              </Alert>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <div>
                  <div className="font-medium">User Info:</div>
                  <div>Email: {user?.email}</div>
                  <div>Role: {user?.role}</div>
                  <div>Company: {user?.companyName}</div>
                </div>
                <div>
                  <div className="font-medium">Session:</div>
                  <div>ID: {user?.sessionId?.substring(0, 20)}...</div>
                  <div>Expires: {user?.expiresAt?.toLocaleTimeString()}</div>
                </div>
              </div>

              <div className="space-y-2">
                <div className="font-medium text-sm">Permissions ({user?.permissions.length}):</div>
                <div className="flex flex-wrap gap-1">
                  {user?.permissions.slice(0, 10).map((permission, index) => (
                    <Badge key={index} variant="outline" className="text-xs">
                      {permission}
                    </Badge>
                  ))}
                  {user && user.permissions.length > 10 && (
                    <Badge variant="outline" className="text-xs">
                      +{user.permissions.length - 10} more
                    </Badge>
                  )}
                </div>
              </div>

              <Button
                onClick={logout}
                variant="outline"
                className="w-full"
              >
                <Shield className="h-4 w-4 mr-2" />
                Sign Out
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Supabase Integration Test */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Database className="h-5 w-5" />
            <span>Supabase Integration Test</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <p className="text-blue-800 text-sm">
                ✅ Using centralized Supabase schema with bcm_users, ai_organism_memory tables
              </p>
              <p className="text-blue-600 text-xs mt-1">
                URL: mvzlkpzakzlmmxyjjtvr.supabase.co | Schema: /Users/MD/ISO-22301/supabase
              </p>
            </div>

            <Button
              onClick={handleSupabaseTest}
              disabled={supabaseLoading}
              className="w-full"
            >
              {supabaseLoading ? (
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
              ) : (
                <Database className="h-4 w-4 mr-2" />
              )}
              Test Supabase Connection & BCM Tables
            </Button>

            {supabaseTestResult && (
              <div className={`p-4 rounded-lg border ${
                supabaseTestResult.success
                  ? 'bg-green-50 border-green-200'
                  : 'bg-red-50 border-red-200'
              }`}>
                <div className={`font-medium ${
                  supabaseTestResult.success ? 'text-green-800' : 'text-red-800'
                }`}>
                  {supabaseTestResult.success ? '✅ Success!' : '❌ Failed'}
                </div>
                <p className={`text-sm mt-1 ${
                  supabaseTestResult.success ? 'text-green-700' : 'text-red-700'
                }`}>
                  {supabaseTestResult.message || supabaseTestResult.error}
                </p>

                {supabaseTestResult.sql && (
                  <div className="mt-3">
                    <details className="text-xs">
                      <summary className="cursor-pointer font-medium">
                        📋 SQL Script for Supabase Dashboard
                      </summary>
                      <pre className="mt-2 p-2 bg-gray-100 rounded text-xs overflow-x-auto">
                        {supabaseTestResult.sql}
                      </pre>
                    </details>
                  </div>
                )}

                {supabaseTestResult.userData && (
                  <div className="mt-3">
                    <div className="font-medium text-xs">Demo User Created:</div>
                    <pre className="text-xs p-2 bg-gray-100 rounded mt-1">
                      {JSON.stringify(supabaseTestResult.userData, null, 2)}
                    </pre>
                  </div>
                )}
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}