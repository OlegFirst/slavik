'use client'

import React, { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { cn } from '@/lib/utils'
import {
  FileUp,
  Send,
  Settings,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Zap,
  FileText,
  Bell,
  Cpu,
  Upload,
  Download,
  Play,
  Users,
  Target,
  MessageSquare,
  Activity,
  Workflow
} from 'lucide-react'
import {
  biaAPI,
  biaQueryKeys,
  type BIAResult
} from '@/services/bia-api'

interface ExternalServicesIntegrationProps {
  biaResults: BIAResult[]
}

export function ExternalServicesIntegration({ biaResults }: ExternalServicesIntegrationProps) {
  const [selectedProcesses, setSelectedProcesses] = useState<string[]>([])
  const [documentFile, setDocumentFile] = useState<File | null>(null)
  const [notificationRecipients, setNotificationRecipients] = useState('')
  const [notificationMessage, setNotificationMessage] = useState('')
  const queryClient = useQueryClient()

  // Check external services health
  const { data: servicesHealth, isLoading: healthLoading } = useQuery({
    queryKey: ['external-services', 'health'],
    queryFn: () => biaAPI.checkExternalServicesHealth(),
    refetchInterval: 30000 // Check every 30 seconds
  })

  // Get AI recommendations
  const { data: aiRecommendations, isLoading: recommendationsLoading } = useQuery({
    queryKey: ['bia', 'ai-recommendations', biaResults.map(r => r.id).join(',')],
    queryFn: () => biaAPI.getBIARecommendations(biaResults),
    enabled: biaResults.length > 0
  })

  // Generate test scenario mutation
  const generateScenarioMutation = useMutation({
    mutationFn: (processIds: string[]) => biaAPI.generateBIATestScenario(processIds),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['scenarios'] })
    }
  })

  // Process document mutation
  const processDocumentMutation = useMutation({
    mutationFn: (file: File) => biaAPI.processBIADocument(file),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: biaQueryKeys.all })
      setDocumentFile(null)
    }
  })

  // Send notification mutation
  const sendNotificationMutation = useMutation({
    mutationFn: ({ message, recipients }: { message: string, recipients: string[] }) =>
      biaAPI.sendBIANotification('BIA Analysis Update', message, recipients),
    onSuccess: () => {
      setNotificationMessage('')
      setNotificationRecipients('')
    }
  })

  const handleProcessSelection = (processId: string) => {
    setSelectedProcesses(prev =>
      prev.includes(processId)
        ? prev.filter(id => id !== processId)
        : [...prev, processId]
    )
  }

  const getServiceStatusColor = (isHealthy: boolean) => {
    return isHealthy ? 'text-green-600 bg-green-100' : 'text-red-600 bg-red-100'
  }

  const getServiceStatusIcon = (isHealthy: boolean) => {
    return isHealthy ? CheckCircle : XCircle
  }

  return (
    <div className="space-y-6">
      {/* External Services Health Status */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5 text-blue-600" />
            External Services Status
          </CardTitle>
        </CardHeader>
        <CardContent>
          {healthLoading ? (
            <div className="animate-pulse space-y-2">
              {[1,2,3,4,5].map(i => (
                <div key={i} className="h-4 bg-gray-200 rounded w-full"></div>
              ))}
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {Object.entries(servicesHealth || {}).map(([service, isHealthy]) => {
                const StatusIcon = getServiceStatusIcon(isHealthy)
                return (
                  <div key={service} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex items-center gap-2">
                      <StatusIcon className={cn("h-4 w-4", getServiceStatusColor(isHealthy))} />
                      <span className="text-sm font-medium">
                        {service.replace(/_/g, ' ')}
                      </span>
                    </div>
                    <Badge variant={isHealthy ? 'default' : 'destructive'}>
                      {isHealthy ? 'Online' : 'Offline'}
                    </Badge>
                  </div>
                )
              })}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Integration Tabs */}
      <Tabs defaultValue="scenarios" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="scenarios">
            <Target className="h-4 w-4 mr-2" />
            Scenarios
          </TabsTrigger>
          <TabsTrigger value="documents">
            <FileText className="h-4 w-4 mr-2" />
            Documents
          </TabsTrigger>
          <TabsTrigger value="notifications">
            <Bell className="h-4 w-4 mr-2" />
            Notifications
          </TabsTrigger>
          <TabsTrigger value="ai-insights">
            <Cpu className="h-4 w-4 mr-2" />
            AI Insights
          </TabsTrigger>
        </TabsList>

        {/* Scenario Generation Tab */}
        <TabsContent value="scenarios" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Workflow className="h-5 w-5 text-purple-600" />
                Generate BIA Test Scenarios
              </CardTitle>
              <p className="text-sm text-gray-600">
                Create realistic disruption scenarios to test your BIA processes and recovery procedures
              </p>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Process Selection */}
              <div>
                <Label className="text-sm font-medium mb-2 block">
                  Select Processes to Include in Scenario
                </Label>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2 max-h-40 overflow-y-auto border rounded-lg p-3">
                  {biaResults.map(process => (
                    <div key={process.id} className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        id={`process-${process.id}`}
                        checked={selectedProcesses.includes(process.id)}
                        onChange={() => handleProcessSelection(process.id)}
                        className="rounded border-gray-300"
                      />
                      <label
                        htmlFor={`process-${process.id}`}
                        className="text-sm cursor-pointer flex-1"
                      >
                        {process.businessFunction}
                        <Badge variant="outline" className="ml-2 text-xs">
                          {process.criticalityLevel}
                        </Badge>
                      </label>
                    </div>
                  ))}
                </div>
              </div>

              {selectedProcesses.length > 0 && (
                <Alert>
                  <AlertTriangle className="h-4 w-4" />
                  <AlertDescription>
                    {selectedProcesses.length} process(es) selected.
                    The scenario will be tailored to test these specific business functions.
                  </AlertDescription>
                </Alert>
              )}

              <Button
                onClick={() => generateScenarioMutation.mutate(selectedProcesses)}
                disabled={selectedProcesses.length === 0 || generateScenarioMutation.isPending}
                className="w-full"
              >
                {generateScenarioMutation.isPending ? (
                  <>
                    <Activity className="h-4 w-4 mr-2 animate-spin" />
                    Generating Scenario...
                  </>
                ) : (
                  <>
                    <Play className="h-4 w-4 mr-2" />
                    Generate Test Scenario
                  </>
                )}
              </Button>

              {generateScenarioMutation.data && (
                <Card className="bg-green-50 border-green-200">
                  <CardContent className="p-4">
                    <h4 className="font-medium text-green-900 mb-2">
                      Scenario Generated: {generateScenarioMutation.data.title}
                    </h4>
                    <p className="text-sm text-green-700 mb-3">
                      {generateScenarioMutation.data.description}
                    </p>
                    <div className="flex gap-2">
                      <Badge variant="outline">
                        {generateScenarioMutation.data.category}
                      </Badge>
                      <Badge variant="outline">
                        {generateScenarioMutation.data.estimated_duration} minutes
                      </Badge>
                      <Badge variant="outline">
                        {generateScenarioMutation.data.participant_roles.length} roles
                      </Badge>
                    </div>
                  </CardContent>
                </Card>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Document Processing Tab */}
        <TabsContent value="documents" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileUp className="h-5 w-5 text-blue-600" />
                Process BIA Documents
              </CardTitle>
              <p className="text-sm text-gray-600">
                Upload and automatically process BIA documents to extract data and create assessments
              </p>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="document-upload" className="text-sm font-medium mb-2 block">
                  Upload BIA Document (PDF, DOCX, XLSX)
                </Label>
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                  <input
                    id="document-upload"
                    type="file"
                    accept=".pdf,.docx,.xlsx"
                    onChange={(e) => setDocumentFile(e.target.files?.[0] || null)}
                    className="hidden"
                  />
                  <label htmlFor="document-upload" className="cursor-pointer">
                    <Upload className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                    <p className="text-sm text-gray-600">
                      Click to select a BIA document or drag and drop
                    </p>
                  </label>
                </div>

                {documentFile && (
                  <div className="mt-2 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <FileText className="h-4 w-4 text-blue-600" />
                        <span className="text-sm font-medium">{documentFile.name}</span>
                        <Badge variant="outline">
                          {Math.round(documentFile.size / 1024)} KB
                        </Badge>
                      </div>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setDocumentFile(null)}
                      >
                        Remove
                      </Button>
                    </div>
                  </div>
                )}
              </div>

              <Button
                onClick={() => documentFile && processDocumentMutation.mutate(documentFile)}
                disabled={!documentFile || processDocumentMutation.isPending}
                className="w-full"
              >
                {processDocumentMutation.isPending ? (
                  <>
                    <Activity className="h-4 w-4 mr-2 animate-spin" />
                    Processing Document...
                  </>
                ) : (
                  <>
                    <Zap className="h-4 w-4 mr-2" />
                    Process & Extract BIA Data
                  </>
                )}
              </Button>

              {processDocumentMutation.data && (
                <Card className="bg-green-50 border-green-200">
                  <CardContent className="p-4">
                    <h4 className="font-medium text-green-900 mb-2">
                      Document Processed Successfully
                    </h4>
                    <p className="text-sm text-green-700">
                      Extracted BIA data and created new assessment for: {processDocumentMutation.data.businessFunction}
                    </p>
                  </CardContent>
                </Card>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Notifications Tab */}
        <TabsContent value="notifications" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Bell className="h-5 w-5 text-orange-600" />
                Send BIA Notifications
              </CardTitle>
              <p className="text-sm text-gray-600">
                Send updates and alerts about BIA processes to stakeholders
              </p>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="recipients" className="text-sm font-medium mb-2 block">
                  Recipients (email addresses, comma-separated)
                </Label>
                <Input
                  id="recipients"
                  type="email"
                  placeholder="john@company.com, jane@company.com"
                  value={notificationRecipients}
                  onChange={(e) => setNotificationRecipients(e.target.value)}
                />
              </div>

              <div>
                <Label htmlFor="message" className="text-sm font-medium mb-2 block">
                  Notification Message
                </Label>
                <Textarea
                  id="message"
                  placeholder="Enter your BIA update message..."
                  value={notificationMessage}
                  onChange={(e) => setNotificationMessage(e.target.value)}
                  className="min-h-[100px]"
                />
              </div>

              <Button
                onClick={() => sendNotificationMutation.mutate({
                  message: notificationMessage,
                  recipients: notificationRecipients.split(',').map(r => r.trim()).filter(Boolean)
                })}
                disabled={!notificationMessage || !notificationRecipients || sendNotificationMutation.isPending}
                className="w-full"
              >
                {sendNotificationMutation.isPending ? (
                  <>
                    <Activity className="h-4 w-4 mr-2 animate-spin" />
                    Sending...
                  </>
                ) : (
                  <>
                    <Send className="h-4 w-4 mr-2" />
                    Send Notification
                  </>
                )}
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* AI Insights Tab */}
        <TabsContent value="ai-insights" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Cpu className="h-5 w-5 text-purple-600" />
                AI-Powered BIA Insights
              </CardTitle>
              <p className="text-sm text-gray-600">
                Get intelligent recommendations and insights based on your BIA data
              </p>
            </CardHeader>
            <CardContent>
              {recommendationsLoading ? (
                <div className="animate-pulse space-y-4">
                  <div className="h-4 bg-gray-200 rounded w-full"></div>
                  <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                  <div className="h-4 bg-gray-200 rounded w-1/2"></div>
                </div>
              ) : aiRecommendations ? (
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h4 className="font-medium">AI Analysis Results</h4>
                    <Badge variant="outline">
                      {Math.round(aiRecommendations.confidence * 100)}% confidence
                    </Badge>
                  </div>

                  <div className="p-4 bg-purple-50 border border-purple-200 rounded-lg">
                    <p className="text-sm text-purple-800 mb-3">
                      <strong>Analysis:</strong> {aiRecommendations.reasoning}
                    </p>
                  </div>

                  <div>
                    <h5 className="font-medium mb-2">Recommendations</h5>
                    <ul className="space-y-2">
                      {aiRecommendations.recommendations.map((rec: string, index: number) => (
                        <li key={index} className="flex items-start gap-2">
                          <CheckCircle className="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
                          <span className="text-sm">{rec}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              ) : (
                <div className="text-center py-8">
                  <MessageSquare className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                  <p className="text-gray-500">No BIA data available for AI analysis</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}