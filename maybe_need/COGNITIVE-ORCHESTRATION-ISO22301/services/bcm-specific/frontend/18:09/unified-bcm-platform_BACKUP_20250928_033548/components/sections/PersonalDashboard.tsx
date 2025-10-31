'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { BarChart, CheckCircle, Clock, AlertTriangle, Users, FileText, Calendar, TrendingUp } from 'lucide-react'

interface PersonalTask {
  id: string
  title: string
  type: 'plan' | 'review' | 'exercise' | 'assessment'
  priority: 'high' | 'medium' | 'low'
  dueDate: string
  status: 'pending' | 'in-progress' | 'completed' | 'overdue'
  progress: number
}

interface PersonalMetric {
  id: string
  name: string
  value: number
  target: number
  unit: string
  trend: 'up' | 'down' | 'stable'
  period: string
}

export function PersonalDashboard() {
  const [activeTab, setActiveTab] = useState('overview')

  const [personalTasks] = useState<PersonalTask[]>([
    {
      id: '1',
      title: 'Review IT Disaster Recovery Plan',
      type: 'review',
      priority: 'high',
      dueDate: '2024-09-20T09:00:00Z',
      status: 'pending',
      progress: 0
    },
    {
      id: '2',
      title: 'Complete BIA for Finance Department',
      type: 'assessment',
      priority: 'high',
      dueDate: '2024-09-25T17:00:00Z',
      status: 'in-progress',
      progress: 65
    },
    {
      id: '3',
      title: 'Quarterly BCM Exercise Planning',
      type: 'exercise',
      priority: 'medium',
      dueDate: '2024-09-30T12:00:00Z',
      status: 'pending',
      progress: 0
    },
    {
      id: '4',
      title: 'Update Crisis Communication Plan',
      type: 'plan',
      priority: 'medium',
      dueDate: '2024-10-05T16:00:00Z',
      status: 'in-progress',
      progress: 30
    }
  ])

  const [personalMetrics] = useState<PersonalMetric[]>([
    {
      id: '1',
      name: 'Plans Reviewed',
      value: 8,
      target: 12,
      unit: 'plans',
      trend: 'up',
      period: 'this month'
    },
    {
      id: '2',
      name: 'Tasks Completed',
      value: 24,
      target: 30,
      unit: 'tasks',
      trend: 'up',
      period: 'this month'
    },
    {
      id: '3',
      name: 'Risk Assessments',
      value: 5,
      target: 8,
      unit: 'assessments',
      trend: 'stable',
      period: 'this quarter'
    },
    {
      id: '4',
      name: 'Exercise Participation',
      value: 3,
      target: 4,
      unit: 'exercises',
      trend: 'up',
      period: 'this quarter'
    }
  ])

  const getTaskStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-800'
      case 'in-progress': return 'bg-blue-100 text-blue-800'
      case 'pending': return 'bg-gray-100 text-gray-800'
      case 'overdue': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'bg-red-100 text-red-800'
      case 'medium': return 'bg-yellow-100 text-yellow-800'
      case 'low': return 'bg-green-100 text-green-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up': return <TrendingUp className="h-4 w-4 text-green-600" />
      case 'down': return <TrendingUp className="h-4 w-4 text-red-600 transform rotate-180" />
      case 'stable': return <div className="h-4 w-4 bg-gray-400 rounded-full"></div>
      default: return null
    }
  }

  const getTaskIcon = (type: string) => {
    switch (type) {
      case 'plan': return <FileText className="h-4 w-4" />
      case 'review': return <CheckCircle className="h-4 w-4" />
      case 'exercise': return <Users className="h-4 w-4" />
      case 'assessment': return <BarChart className="h-4 w-4" />
      default: return <Clock className="h-4 w-4" />
    }
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Personal Dashboard</h2>
          <p className="text-gray-600 mt-1">Your personalized BCM overview and activity summary</p>
        </div>
        <div className="text-sm text-gray-500">
          Last updated: {new Date().toLocaleString()}
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="tasks">My Tasks</TabsTrigger>
          <TabsTrigger value="metrics">Performance</TabsTrigger>
          <TabsTrigger value="calendar">Calendar</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          {/* Quick Stats */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Active Tasks</CardTitle>
                <Clock className="h-4 w-4 text-blue-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {personalTasks.filter(t => t.status === 'in-progress' || t.status === 'pending').length}
                </div>
                <p className="text-xs text-gray-600">2 high priority</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Completed</CardTitle>
                <CheckCircle className="h-4 w-4 text-green-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">24</div>
                <p className="text-xs text-gray-600">This month</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Overdue</CardTitle>
                <AlertTriangle className="h-4 w-4 text-red-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">0</div>
                <p className="text-xs text-gray-600">Great work!</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Progress</CardTitle>
                <BarChart className="h-4 w-4 text-purple-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">80%</div>
                <p className="text-xs text-gray-600">Monthly target</p>
              </CardContent>
            </Card>
          </div>

          {/* Recent Activity */}
          <Card>
            <CardHeader>
              <CardTitle>Recent Activity</CardTitle>
              <CardDescription>Your latest BCM activities and updates</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {[
                  { action: 'Completed', item: 'Main Office BCP Review', time: '2 hours ago', type: 'success' },
                  { action: 'Updated', item: 'IT Disaster Recovery Plan', time: '1 day ago', type: 'info' },
                  { action: 'Created', item: 'Q4 Exercise Schedule', time: '2 days ago', type: 'info' },
                  { action: 'Reviewed', item: 'Finance Department BIA', time: '3 days ago', type: 'success' }
                ].map((activity, index) => (
                  <div key={index} className="flex items-center gap-4 p-3 bg-gray-50 rounded-lg">
                    <div className={`w-2 h-2 rounded-full ${
                      activity.type === 'success' ? 'bg-green-500' : 'bg-blue-500'
                    }`} />
                    <div className="flex-1">
                      <div className="text-sm">
                        <span className="font-medium">{activity.action}</span> {activity.item}
                      </div>
                      <div className="text-xs text-gray-500">{activity.time}</div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Upcoming Deadlines */}
          <Card>
            <CardHeader>
              <CardTitle>Upcoming Deadlines</CardTitle>
              <CardDescription>Tasks and reviews due in the next 7 days</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {personalTasks
                  .filter(task => new Date(task.dueDate) <= new Date(Date.now() + 7 * 24 * 60 * 60 * 1000))
                  .map(task => (
                    <div key={task.id} className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex items-center gap-3">
                        {getTaskIcon(task.type)}
                        <div>
                          <div className="font-medium text-sm">{task.title}</div>
                          <div className="text-xs text-gray-500">
                            Due: {new Date(task.dueDate).toLocaleDateString()}
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge className={getPriorityColor(task.priority)}>{task.priority}</Badge>
                        <Badge className={getTaskStatusColor(task.status)}>{task.status}</Badge>
                      </div>
                    </div>
                  ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="tasks" className="space-y-6">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-medium">My Tasks ({personalTasks.length})</h3>
            <div className="flex gap-2">
              <Button variant="outline">Filter</Button>
              <Button variant="outline">Sort</Button>
            </div>
          </div>

          <div className="space-y-4">
            {personalTasks.map(task => (
              <Card key={task.id}>
                <CardContent className="pt-4">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-3">
                      {getTaskIcon(task.type)}
                      <div>
                        <div className="font-medium">{task.title}</div>
                        <div className="text-sm text-gray-600">
                          Due: {new Date(task.dueDate).toLocaleDateString()} at {new Date(task.dueDate).toLocaleTimeString()}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge className={getPriorityColor(task.priority)}>{task.priority}</Badge>
                      <Badge className={getTaskStatusColor(task.status)}>{task.status}</Badge>
                    </div>
                  </div>
                  
                  {task.progress > 0 && (
                    <div className="mb-3">
                      <div className="flex justify-between text-sm mb-1">
                        <span>Progress</span>
                        <span>{task.progress}%</span>
                      </div>
                      <Progress value={task.progress} />
                    </div>
                  )}
                  
                  <div className="flex gap-2">
                    <Button size="sm">View Details</Button>
                    <Button variant="outline" size="sm">Update Progress</Button>
                    {task.status === 'pending' && (
                      <Button variant="outline" size="sm">Start Task</Button>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="metrics" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {personalMetrics.map(metric => (
              <Card key={metric.id}>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium">{metric.name}</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between mb-2">
                    <div className="text-2xl font-bold">{metric.value}</div>
                    {getTrendIcon(metric.trend)}
                  </div>
                  <div className="text-sm text-gray-600 mb-2">
                    Target: {metric.target} {metric.unit}
                  </div>
                  <Progress value={(metric.value / metric.target) * 100} className="mb-1" />
                  <div className="text-xs text-gray-500">{metric.period}</div>
                </CardContent>
              </Card>
            ))}
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Performance Summary</CardTitle>
              <CardDescription>Your BCM performance metrics and trends</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <h4 className="font-medium mb-2">This Month</h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span>Plans reviewed:</span>
                        <span className="font-medium">8 / 12</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Tasks completed:</span>
                        <span className="font-medium">24 / 30</span>
                      </div>
                      <div className="flex justify-between">
                        <span>On-time completion:</span>
                        <span className="font-medium text-green-600">100%</span>
                      </div>
                    </div>
                  </div>
                  <div>
                    <h4 className="font-medium mb-2">This Quarter</h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span>Risk assessments:</span>
                        <span className="font-medium">5 / 8</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Exercise participation:</span>
                        <span className="font-medium">3 / 4</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Quality score:</span>
                        <span className="font-medium text-green-600">4.8 / 5.0</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="calendar" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Upcoming Events</CardTitle>
              <CardDescription>Your BCM calendar and scheduled activities</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {[
                  { date: '2024-09-20', title: 'IT DR Plan Review', type: 'review', time: '09:00 AM' },
                  { date: '2024-09-22', title: 'BCM Committee Meeting', type: 'meeting', time: '02:00 PM' },
                  { date: '2024-09-25', title: 'Finance BIA Due', type: 'deadline', time: '05:00 PM' },
                  { date: '2024-09-27', title: 'Crisis Exercise', type: 'exercise', time: '10:00 AM' },
                  { date: '2024-09-30', title: 'Monthly BCM Report', type: 'report', time: '12:00 PM' }
                ].map((event, index) => (
                  <div key={index} className="flex items-center gap-4 p-3 border rounded-lg">
                    <div className="text-center">
                      <div className="text-sm font-medium">{new Date(event.date).getDate()}</div>
                      <div className="text-xs text-gray-600">
                        {new Date(event.date).toLocaleDateString('en-US', { month: 'short' })}
                      </div>
                    </div>
                    <div className="flex-1">
                      <div className="font-medium text-sm">{event.title}</div>
                      <div className="text-xs text-gray-600">{event.time}</div>
                    </div>
                    <Badge variant="outline" className="capitalize">{event.type}</Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}