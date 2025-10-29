'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { RotateCcw, Clock, Users, CheckCircle, AlertCircle, ArrowRight } from 'lucide-react'

interface RecoveryPhase {
  id: string
  name: string
  description: string
  priority: 'critical' | 'high' | 'medium' | 'low'
  status: 'not-started' | 'in-progress' | 'completed' | 'blocked'
  progress: number
  estimatedTime: string
  actualTime?: string
  assignedTeam: string
  dependencies: string[]
  tasks: RecoveryTask[]
}

interface RecoveryTask {
  id: string
  name: string
  status: 'pending' | 'in-progress' | 'completed' | 'failed'
  assignee: string
  estimatedDuration: string
  startedAt?: string
  completedAt?: string
  notes?: string
}

interface RecoveryMetrics {
  rto: number // Recovery Time Objective (hours)
  rpo: number // Recovery Point Objective (hours)  
  actualRecoveryTime?: number
  dataLoss?: number
  systemsAffected: number
  systemsRecovered: number
}

export function RecoveryCoordination() {
  const [activeTab, setActiveTab] = useState('overview')
  
  const [recoveryPhases] = useState<RecoveryPhase[]>([
    {
      id: '1',
      name: 'Immediate Response',
      description: 'Critical systems stabilization and damage assessment',
      priority: 'critical',
      status: 'completed',
      progress: 100,
      estimatedTime: '2 hours',
      actualTime: '1.5 hours',
      assignedTeam: 'Emergency Response Team',
      dependencies: [],
      tasks: [
        { id: '1', name: 'Activate emergency protocols', status: 'completed', assignee: 'John Smith', estimatedDuration: '30 min', completedAt: '2024-09-18T10:30:00Z' },
        { id: '2', name: 'Assess system damage', status: 'completed', assignee: 'Sarah Johnson', estimatedDuration: '60 min', completedAt: '2024-09-18T11:15:00Z' },
        { id: '3', name: 'Establish communication channels', status: 'completed', assignee: 'Mike Davis', estimatedDuration: '30 min', completedAt: '2024-09-18T11:00:00Z' }
      ]
    },
    {
      id: '2', 
      name: 'System Recovery',
      description: 'Restore critical business systems and data',
      priority: 'critical',
      status: 'in-progress',
      progress: 65,
      estimatedTime: '6 hours',
      assignedTeam: 'IT Recovery Team',
      dependencies: ['1'],
      tasks: [
        { id: '4', name: 'Restore primary database', status: 'completed', assignee: 'Alex Chen', estimatedDuration: '2 hours', completedAt: '2024-09-18T13:30:00Z' },
        { id: '5', name: 'Rebuild application servers', status: 'in-progress', assignee: 'Lisa Wong', estimatedDuration: '3 hours', startedAt: '2024-09-18T12:00:00Z' },
        { id: '6', name: 'Verify data integrity', status: 'pending', assignee: 'Tom Brown', estimatedDuration: '1 hour' }
      ]
    },
    {
      id: '3',
      name: 'Service Restoration',
      description: 'Restore business services and user access',
      priority: 'high',
      status: 'not-started',
      progress: 0,
      estimatedTime: '4 hours',
      assignedTeam: 'Business Continuity Team',
      dependencies: ['2'],
      tasks: [
        { id: '7', name: 'Restore user authentication', status: 'pending', assignee: 'Emma Wilson', estimatedDuration: '1 hour' },
        { id: '8', name: 'Test critical workflows', status: 'pending', assignee: 'David Lee', estimatedDuration: '2 hours' },
        { id: '9', name: 'Enable customer access', status: 'pending', assignee: 'Rachel Green', estimatedDuration: '1 hour' }
      ]
    },
    {
      id: '4',
      name: 'Full Operation',
      description: 'Complete restoration and monitoring',
      priority: 'medium',
      status: 'not-started',
      progress: 0,
      estimatedTime: '3 hours',
      assignedTeam: 'Operations Team',
      dependencies: ['3'],
      tasks: [
        { id: '10', name: 'Restore all systems', status: 'pending', assignee: 'Kevin Park', estimatedDuration: '2 hours' },
        { id: '11', name: 'Conduct final testing', status: 'pending', assignee: 'Olivia Taylor', estimatedDuration: '1 hour' }
      ]
    }
  ])

  const [metrics] = useState<RecoveryMetrics>({
    rto: 8, // 8 hours RTO
    rpo: 2, // 2 hours RPO
    actualRecoveryTime: 4.5, // In progress
    dataLoss: 0.5, // 30 minutes of data lost
    systemsAffected: 12,
    systemsRecovered: 8
  })

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-800'
      case 'in-progress': return 'bg-blue-100 text-blue-800'
      case 'blocked': return 'bg-red-100 text-red-800'
      case 'not-started': return 'bg-gray-100 text-gray-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical': return 'bg-red-100 text-red-800'
      case 'high': return 'bg-orange-100 text-orange-800'
      case 'medium': return 'bg-yellow-100 text-yellow-800'
      case 'low': return 'bg-green-100 text-green-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getTaskStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircle className="h-4 w-4 text-green-600" />
      case 'in-progress': return <Clock className="h-4 w-4 text-blue-600" />
      case 'failed': return <AlertCircle className="h-4 w-4 text-red-600" />
      default: return <Clock className="h-4 w-4 text-gray-400" />
    }
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Recovery Coordination</h2>
          <p className="text-gray-600 mt-1">Coordinate and track business recovery operations</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">Generate Report</Button>
          <Button>Update Status</Button>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="phases">Recovery Phases</TabsTrigger>
          <TabsTrigger value="tasks">Tasks</TabsTrigger>
          <TabsTrigger value="metrics">Metrics</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Overall Progress</CardTitle>
                <RotateCcw className="h-4 w-4 text-blue-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">41%</div>
                <Progress value={41} className="mt-2" />
                <p className="text-xs text-gray-600 mt-1">2 of 4 phases completed</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Time Elapsed</CardTitle>
                <Clock className="h-4 w-4 text-orange-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">4.5h</div>
                <p className="text-xs text-gray-600">of 8h RTO</p>
                <div className="text-xs text-green-600 mt-1">Within target</div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Systems Status</CardTitle>
                <CheckCircle className="h-4 w-4 text-green-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">8/12</div>
                <p className="text-xs text-gray-600">Systems recovered</p>
                <div className="text-xs text-blue-600 mt-1">4 in progress</div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Teams Active</CardTitle>
                <Users className="h-4 w-4 text-purple-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">3</div>
                <p className="text-xs text-gray-600">Recovery teams</p>
                <div className="text-xs text-green-600 mt-1">All operational</div>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Recovery Timeline</CardTitle>
              <CardDescription>Current progress across all recovery phases</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {recoveryPhases.map((phase, index) => (
                  <div key={phase.id} className="flex items-center gap-4">
                    <div className="flex-shrink-0 w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
                      {index + 1}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-1">
                        <span className="font-medium">{phase.name}</span>
                        <Badge className={getStatusColor(phase.status)}>{phase.status}</Badge>
                      </div>
                      <Progress value={phase.progress} className="mb-1" />
                      <div className="text-xs text-gray-600 flex justify-between">
                        <span>{phase.description}</span>
                        <span>{phase.progress}%</span>
                      </div>
                    </div>
                    {index < recoveryPhases.length - 1 && (
                      <ArrowRight className="h-4 w-4 text-gray-400" />
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="phases" className="space-y-6">
          <div className="space-y-4">
            {recoveryPhases.map(phase => (
              <Card key={phase.id}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="text-lg">{phase.name}</CardTitle>
                      <CardDescription>{phase.description}</CardDescription>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge className={getPriorityColor(phase.priority)}>{phase.priority}</Badge>
                      <Badge className={getStatusColor(phase.status)}>{phase.status}</Badge>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                    <div className="flex flex-col">
                      <span className="text-sm text-gray-600">Progress</span>
                      <div className="flex items-center gap-2">
                        <Progress value={phase.progress} className="flex-1" />
                        <span className="text-sm font-medium">{phase.progress}%</span>
                      </div>
                    </div>
                    <div className="flex flex-col">
                      <span className="text-sm text-gray-600">Estimated Time</span>
                      <span className="font-medium">{phase.estimatedTime}</span>
                      {phase.actualTime && (
                        <span className="text-xs text-gray-500">Actual: {phase.actualTime}</span>
                      )}
                    </div>
                    <div className="flex flex-col">
                      <span className="text-sm text-gray-600">Assigned Team</span>
                      <span className="font-medium">{phase.assignedTeam}</span>
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <h4 className="font-medium text-sm">Tasks ({phase.tasks.length})</h4>
                    <div className="space-y-2">
                      {phase.tasks.map(task => (
                        <div key={task.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                          <div className="flex items-center gap-3">
                            {getTaskStatusIcon(task.status)}
                            <div>
                              <div className="font-medium text-sm">{task.name}</div>
                              <div className="text-xs text-gray-600">
                                {task.assignee} • {task.estimatedDuration}
                              </div>
                            </div>
                          </div>
                          <Badge variant="outline" className="text-xs">
                            {task.status}
                          </Badge>
                        </div>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="tasks" className="space-y-6">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-medium">All Recovery Tasks</h3>
            <Button>Add Task</Button>
          </div>

          <div className="space-y-4">
            {recoveryPhases.flatMap(phase => 
              phase.tasks.map(task => (
                <Card key={task.id}>
                  <CardContent className="pt-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        {getTaskStatusIcon(task.status)}
                        <div>
                          <div className="font-medium">{task.name}</div>
                          <div className="text-sm text-gray-600">
                            {task.assignee} • Duration: {task.estimatedDuration}
                          </div>
                          {task.startedAt && (
                            <div className="text-xs text-gray-500">
                              Started: {new Date(task.startedAt).toLocaleString()}
                            </div>
                          )}
                          {task.completedAt && (
                            <div className="text-xs text-gray-500">
                              Completed: {new Date(task.completedAt).toLocaleString()}
                            </div>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge variant="outline">{task.status}</Badge>
                        <Button variant="outline" size="sm">Update</Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))
            )}
          </div>
        </TabsContent>

        <TabsContent value="metrics" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">RTO Progress</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{metrics.actualRecoveryTime}h</div>
                <div className="text-sm text-gray-600">of {metrics.rto}h target</div>
                <Progress value={(metrics.actualRecoveryTime! / metrics.rto) * 100} className="mt-2" />
                <div className="text-xs text-green-600 mt-1">56% of RTO used</div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Data Loss</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{metrics.dataLoss}h</div>
                <div className="text-sm text-gray-600">vs {metrics.rpo}h RPO</div>
                <div className="text-xs text-green-600 mt-2">Within RPO target</div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">System Recovery</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{metrics.systemsRecovered}/{metrics.systemsAffected}</div>
                <div className="text-sm text-gray-600">Systems restored</div>
                <Progress value={(metrics.systemsRecovered / metrics.systemsAffected) * 100} className="mt-2" />
                <div className="text-xs text-blue-600 mt-1">
                  {Math.round((metrics.systemsRecovered / metrics.systemsAffected) * 100)}% complete
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Business Impact</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-600">Low</div>
                <div className="text-sm text-gray-600">Current impact level</div>
                <div className="text-xs text-gray-500 mt-2">
                  Estimated revenue impact: $12K/hour
                </div>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Recovery Performance</CardTitle>
              <CardDescription>Key performance indicators for the current recovery operation</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm font-medium">Recovery Time Objective (RTO)</span>
                    <span className="text-sm text-gray-600">{metrics.actualRecoveryTime}h / {metrics.rto}h</span>
                  </div>
                  <Progress value={(metrics.actualRecoveryTime! / metrics.rto) * 100} />
                </div>

                <div>
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm font-medium">Recovery Point Objective (RPO)</span>
                    <span className="text-sm text-gray-600">{metrics.dataLoss}h / {metrics.rpo}h</span>
                  </div>
                  <Progress value={(metrics.dataLoss / metrics.rpo) * 100} />
                </div>

                <div>
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm font-medium">Systems Recovery</span>
                    <span className="text-sm text-gray-600">{metrics.systemsRecovered} / {metrics.systemsAffected}</span>
                  </div>
                  <Progress value={(metrics.systemsRecovered / metrics.systemsAffected) * 100} />
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}