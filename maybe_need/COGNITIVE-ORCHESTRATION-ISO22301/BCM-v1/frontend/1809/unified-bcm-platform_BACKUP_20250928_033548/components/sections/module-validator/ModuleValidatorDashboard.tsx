import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { 
  CheckCircle,
  AlertTriangle,
  XCircle,
  RefreshCw,
  Play,
  Wrench,
  Package,
  AlertCircle
} from 'lucide-react'
import { moduleValidatorClient } from '@/lib/api-client'

interface ModuleValidationResult {
  name: string
  path: string
  errors: string[]
  warnings: string[]
  status: 'error' | 'warning' | 'success'
  version?: string
  category?: string
  installed?: boolean
  dependencies?: string[]
  summary?: string
}

interface ValidationSummary {
  success: boolean
  modules: ModuleValidationResult[]
  total_errors: number
  total_warnings: number
}

export function ModuleValidatorDashboard() {
  const [validationResults, setValidationResults] = useState<ValidationSummary | null>(null)
  const [isValidating, setIsValidating] = useState(false)
  const [lastValidation, setLastValidation] = useState<Date | null>(null)

  useEffect(() => {
    loadValidationResults()
  }, [])

  const loadValidationResults = async () => {
    try {
      const results = await moduleValidatorClient.validateAllModules()
      setValidationResults(results)
      setLastValidation(new Date())
    } catch (error) {
      console.error('Failed to load validation results:', error)
    }
  }

  const runValidation = async () => {
    setIsValidating(true)
    try {
      await loadValidationResults()
    } finally {
      setIsValidating(false)
    }
  }

  const fixModuleIssues = async (moduleName: string) => {
    try {
      await moduleValidatorClient.fixModuleIssues(moduleName)
      // Перезагружаем результаты после исправления
      await loadValidationResults()
    } catch (error) {
      console.error(`Failed to fix issues for ${moduleName}:`, error)
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success': return CheckCircle
      case 'warning': return AlertTriangle
      case 'error': return XCircle
      default: return AlertCircle
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success': return 'default'
      case 'warning': return 'secondary'
      case 'error': return 'destructive'
      default: return 'outline'
    }
  }

  const successModules = validationResults?.modules.filter(m => m.status === 'success').length || 0
  const warningModules = validationResults?.modules.filter(m => m.status === 'warning').length || 0
  const errorModules = validationResults?.modules.filter(m => m.status === 'error').length || 0
  const totalModules = validationResults?.modules.length || 0

  const successRate = totalModules > 0 ? (successModules / totalModules) * 100 : 0

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <CheckCircle className="h-6 w-6 text-green-600" />
            Module Validation Dashboard
          </h2>
          <p className="text-gray-600 mt-1">
            Real-time validation status and health monitoring for all BCM modules
          </p>
        </div>
        <div className="flex items-center gap-2">
          {lastValidation && (
            <span className="text-sm text-gray-500">
              Last validated: {lastValidation.toLocaleTimeString()}
            </span>
          )}
          <Button 
            onClick={runValidation} 
            disabled={isValidating}
            className="flex items-center gap-2"
          >
            {isValidating ? (
              <RefreshCw className="h-4 w-4 animate-spin" />
            ) : (
              <Play className="h-4 w-4" />
            )}
            {isValidating ? 'Validating...' : 'Run Validation'}
          </Button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Modules</CardTitle>
            <Package className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalModules}</div>
            <p className="text-xs text-muted-foreground">
              BCM platform modules
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{successRate.toFixed(1)}%</div>
            <p className="text-xs text-muted-foreground">
              {successModules} of {totalModules} modules
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Errors</CardTitle>
            <XCircle className="h-4 w-4 text-red-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">
              {validationResults?.total_errors || 0}
            </div>
            <p className="text-xs text-muted-foreground">
              In {errorModules} modules
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Warnings</CardTitle>
            <AlertTriangle className="h-4 w-4 text-yellow-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">
              {validationResults?.total_warnings || 0}
            </div>
            <p className="text-xs text-muted-foreground">
              In {warningModules} modules
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Validation Progress */}
      {isValidating && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <RefreshCw className="h-5 w-5 animate-spin text-blue-600" />
              Validation in Progress
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Progress value={75} className="w-full" />
            <p className="text-sm text-gray-600 mt-2">
              Validating module dependencies and configurations...
            </p>
          </CardContent>
        </Card>
      )}

      {/* Module Status Overview */}
      {validationResults && (
        <Card>
          <CardHeader>
            <CardTitle>Module Status Overview</CardTitle>
            <CardDescription>
              Quick overview of all module validation states
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="grid gap-4 md:grid-cols-3">
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm">Healthy Modules</span>
                    <span className="text-sm font-medium">{successModules}</span>
                  </div>
                  <Progress value={(successModules / totalModules) * 100} className="h-2 bg-green-100" />
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm">Modules with Warnings</span>
                    <span className="text-sm font-medium">{warningModules}</span>
                  </div>
                  <Progress value={(warningModules / totalModules) * 100} className="h-2 bg-yellow-100" />
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm">Modules with Errors</span>
                    <span className="text-sm font-medium">{errorModules}</span>
                  </div>
                  <Progress value={(errorModules / totalModules) * 100} className="h-2 bg-red-100" />
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Critical Issues */}
      {validationResults && errorModules > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-red-700">
              <XCircle className="h-5 w-5" />
              Critical Issues Requiring Attention
            </CardTitle>
            <CardDescription>
              Modules with validation errors that need immediate fixing
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {validationResults.modules
                .filter(module => module.status === 'error')
                .map((module) => {
                  const StatusIcon = getStatusIcon(module.status)
                  
                  return (
                    <div key={module.name} className="border border-red-200 rounded-lg p-4 bg-red-50">
                      <div className="flex items-start justify-between">
                        <div className="flex items-start gap-3">
                          <StatusIcon className="h-5 w-5 text-red-600 mt-0.5" />
                          <div>
                            <h4 className="font-medium text-red-900">{module.name}</h4>
                            <p className="text-sm text-red-700 mt-1">
                              {module.errors.length} error{module.errors.length !== 1 ? 's' : ''}, 
                              {' '}{module.warnings.length} warning{module.warnings.length !== 1 ? 's' : ''}
                            </p>
                            <div className="mt-2 space-y-1">
                              {module.errors.slice(0, 2).map((error, idx) => (
                                <p key={idx} className="text-xs text-red-600">• {error}</p>
                              ))}
                              {module.errors.length > 2 && (
                                <p className="text-xs text-red-500">
                                  ... and {module.errors.length - 2} more errors
                                </p>
                              )}
                            </div>
                          </div>
                        </div>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => fixModuleIssues(module.name)}
                          className="flex items-center gap-1 border-red-300 text-red-700 hover:bg-red-100"
                        >
                          <Wrench className="h-3 w-3" />
                          Auto Fix
                        </Button>
                      </div>
                    </div>
                  )
                })}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Recent Validation Results */}
      {validationResults && (
        <Card>
          <CardHeader>
            <CardTitle>All Modules Status</CardTitle>
            <CardDescription>
              Complete validation results for all BCM modules
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {validationResults.modules.map((module) => {
                const StatusIcon = getStatusIcon(module.status)
                
                return (
                  <div key={module.name} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex items-center gap-3">
                      <StatusIcon className={`h-4 w-4 ${
                        module.status === 'success' ? 'text-green-600' :
                        module.status === 'warning' ? 'text-yellow-600' : 'text-red-600'
                      }`} />
                      <div>
                        <h4 className="font-medium">{module.name}</h4>
                        <p className="text-sm text-gray-500">
                          {module.category || 'General'} • v{module.version || '1.0.0'}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <Badge variant={getStatusColor(module.status)}>
                        {module.status.toUpperCase()}
                      </Badge>
                      {module.errors.length > 0 && (
                        <span className="text-xs text-red-600">
                          {module.errors.length} errors
                        </span>
                      )}
                      {module.warnings.length > 0 && (
                        <span className="text-xs text-yellow-600">
                          {module.warnings.length} warnings
                        </span>
                      )}
                      {(module.errors.length > 0 || module.warnings.length > 0) && (
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => fixModuleIssues(module.name)}
                        >
                          <Wrench className="h-3 w-3" />
                        </Button>
                      )}
                    </div>
                  </div>
                )
              })}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
