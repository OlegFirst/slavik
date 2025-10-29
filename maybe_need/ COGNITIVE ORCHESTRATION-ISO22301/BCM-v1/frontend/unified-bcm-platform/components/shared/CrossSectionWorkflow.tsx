import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { 
  ArrowRight,
  Workflow,
  Play,
  Pause,
  Settings,
  AlertCircle,
  CheckCircle,
  Clock,
  Zap
} from 'lucide-react'
import {
  getCrossSectionWorkflows,
  executeCrossSectionWorkflow,
  getSectionContext,
  type CrossSectionWorkflow,
  type SectionContext
} from '@/lib/section-integration'

interface CrossSectionWorkflowProps {
  currentSection: string
  className?: string
}

interface WorkflowExecution {
  workflowId: string
  status: 'running' | 'completed' | 'failed'
  progress: number
  startTime: Date
  completedActions: number
  totalActions: number
}

export function CrossSectionWorkflow({ currentSection, className }: CrossSectionWorkflowProps) {
  const [workflows, setWorkflows] = useState<CrossSectionWorkflow[]>([])
  const [executions, setExecutions] = useState<WorkflowExecution[]>([])
  const [context, setContext] = useState<SectionContext | null>(null)

  useEffect(() => {
    // Load workflows for current section
    const sectionWorkflows = getCrossSectionWorkflows(currentSection)
    setWorkflows(sectionWorkflows)

    // Load section context
    const currentContext = getSectionContext()
    setContext(currentContext)
  }, [currentSection])

  const executeWorkflow = async (workflow: CrossSectionWorkflow) => {
    const execution: WorkflowExecution = {
      workflowId: workflow.id,
      status: 'running',
      progress: 0,
      startTime: new Date(),
      completedActions: 0,
      totalActions: workflow.actions.length
    }

    setExecutions(prev => [...prev, execution])

    try {
      // Simulate workflow execution with progress updates
      for (let i = 0; i < workflow.actions.length; i++) {
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        setExecutions(prev => prev.map(exec => 
          exec.workflowId === workflow.id
            ? {
                ...exec,
                progress: ((i + 1) / workflow.actions.length) * 100,
                completedActions: i + 1
              }
            : exec
        ))
      }

      // Execute the actual workflow
      if (context) {
        await executeCrossSectionWorkflow(workflow.id, {}, context)
      }

      setExecutions(prev => prev.map(exec => 
        exec.workflowId === workflow.id
          ? { ...exec, status: 'completed', progress: 100 }
          : exec
      ))
    } catch (error) {
      setExecutions(prev => prev.map(exec => 
        exec.workflowId === workflow.id
          ? { ...exec, status: 'failed' }
          : exec
      ))
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running': return Clock
      case 'completed': return CheckCircle
      case 'failed': return AlertCircle
      default: return Clock
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return 'secondary'
      case 'completed': return 'default'
      case 'failed': return 'destructive'
      default: return 'outline'
    }
  }

  if (workflows.length === 0) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Workflow className="h-5 w-5 text-gray-400" />
            Cross-Section Workflows
          </CardTitle>
          <CardDescription>
            No automated workflows configured for this section
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center text-gray-500 py-8">
            <Workflow className="h-12 w-12 mx-auto mb-2 text-gray-300" />
            <p>Configure workflows to automate actions across sections</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className={`space-y-4 ${className}`}>
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold flex items-center gap-2">
            <Workflow className="h-5 w-5 text-blue-600" />
            Cross-Section Workflows
          </h3>
          <p className="text-sm text-gray-600">
            Automated workflows that coordinate actions across sections
          </p>
        </div>
        <Button variant="outline" size="sm">
          <Settings className="h-4 w-4 mr-1" />
          Configure
        </Button>
      </div>

      <div className="grid gap-4">
        {workflows.map((workflow) => {
          const execution = executions.find(exec => exec.workflowId === workflow.id)
          const StatusIcon = execution ? getStatusIcon(execution.status) : Play

          return (
            <Card key={workflow.id}>
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <div className="space-y-1">
                    <CardTitle className="text-base">{workflow.name}</CardTitle>
                    <div className="flex items-center gap-2">
                      <Badge variant={workflow.status === 'active' ? 'default' : 'secondary'}>
                        {workflow.status.toUpperCase()}
                      </Badge>
                      {execution && (
                        <Badge variant={getStatusColor(execution.status)}>
                          {execution.status.toUpperCase()}
                        </Badge>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {execution && (
                      <div className="text-right text-xs text-gray-500">
                        {execution.completedActions}/{execution.totalActions} actions
                      </div>
                    )}
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => executeWorkflow(workflow)}
                      disabled={!!execution && execution.status === 'running'}
                      className="flex items-center gap-1"
                    >
                      <StatusIcon className="h-3 w-3" />
                      {execution?.status === 'running' ? 'Running' : 'Execute'}
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {/* Trigger */}
                  <div>
                    <div className="text-sm font-medium text-gray-700 mb-2">Trigger:</div>
                    <div className="flex items-center gap-2 text-sm">
                      <Badge variant="outline">{workflow.trigger.sectionId}</Badge>
                      <ArrowRight className="h-3 w-3 text-gray-400" />
                      <code className="text-xs bg-gray-100 px-2 py-1 rounded">
                        {workflow.trigger.eventType}
                      </code>
                    </div>
                  </div>

                  {/* Actions Flow */}
                  <div>
                    <div className="text-sm font-medium text-gray-700 mb-2">Actions:</div>
                    <div className="flex items-center gap-1 overflow-x-auto pb-2">
                      {workflow.actions.map((action, index) => (
                        <React.Fragment key={index}>
                          <div className="flex flex-col items-center min-w-[100px]">
                            <div className={`
                              w-6 h-6 rounded-full flex items-center justify-center text-xs mb-1
                              ${execution && execution.completedActions > index
                                ? 'bg-green-100 text-green-600'
                                : execution && execution.completedActions === index && execution.status === 'running'
                                ? 'bg-blue-100 text-blue-600'
                                : 'bg-gray-100 text-gray-400'
                              }
                            `}>
                              {index + 1}
                            </div>
                            <Badge variant="outline" className="text-xs">
                              {action.sectionId}
                            </Badge>
                            <div className="text-xs text-center mt-1 text-gray-500">
                              {action.actionType.replace(/-/g, ' ')}
                            </div>
                          </div>
                          {index < workflow.actions.length - 1 && (
                            <ArrowRight className="h-3 w-3 text-gray-400 flex-shrink-0" />
                          )}
                        </React.Fragment>
                      ))}
                    </div>
                  </div>

                  {/* Progress Bar */}
                  {execution && execution.status === 'running' && (
                    <div>
                      <div className="flex justify-between text-xs text-gray-600 mb-1">
                        <span>Progress</span>
                        <span>{Math.round(execution.progress)}%</span>
                      </div>
                      <Progress value={execution.progress} className="h-2" />
                    </div>
                  )}

                  {/* Execution Status */}
                  {execution && execution.status !== 'running' && (
                    <div className={`
                      p-3 rounded-lg flex items-center gap-2
                      ${execution.status === 'completed' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'}
                    `}>
                      <StatusIcon className="h-4 w-4" />
                      <span className="text-sm">
                        Workflow {execution.status === 'completed' ? 'completed successfully' : 'failed'}
                      </span>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>

      {/* Context Information */}
      {context && (
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Current Context</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-gray-500">Current Section:</span>
                <div className="font-medium">{context.currentSection}</div>
              </div>
              {context.previousSection && (
                <div>
                  <span className="text-gray-500">Previous Section:</span>
                  <div className="font-medium">{context.previousSection}</div>
                </div>
              )}
            </div>
            {Object.keys(context.sharedState).length > 0 && (
              <div className="mt-3">
                <span className="text-gray-500 text-sm">Shared State:</span>
                <div className="mt-1 flex flex-wrap gap-1">
                  {Object.keys(context.sharedState).map(key => (
                    <Badge key={key} variant="outline" className="text-xs">
                      {key}
                    </Badge>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  )
}
