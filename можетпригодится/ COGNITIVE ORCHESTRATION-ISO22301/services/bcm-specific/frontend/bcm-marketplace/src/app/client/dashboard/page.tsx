'use client'

import React, { useState } from 'react'
import { AppLayout } from '@/components/layout/AppLayout'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  Plus,
  Search,
  Filter,
  Clock,
  Users,
  DollarSign,
  FileText,
  MessageSquare,
  Eye,
  Edit,
  CheckCircle,
  AlertCircle,
  TrendingUp,
  Calendar,
  Star,
  Send,
  BookOpen,
  Building
} from 'lucide-react'

interface ServiceRequest {
  id: string
  title: string
  description: string
  serviceType: string
  industry: string
  urgency: 'low' | 'medium' | 'high' | 'urgent'
  budget: {
    min: number
    max: number
    type: 'hourly' | 'fixed' | 'retainer'
  }
  duration: string
  location: string
  remote: boolean
  status: 'draft' | 'posted' | 'in_review' | 'assigned' | 'in_progress' | 'completed' | 'cancelled'
  proposalsCount: number
  views: number
  postedDate: string
  deadline: string
  selectedSpecialist?: {
    name: string
    avatar?: string
    rating: number
  }
}

interface ActiveProject {
  id: string
  title: string
  specialist: {
    name: string
    avatar?: string
    rating: number
  }
  progress: number
  budget: string
  startDate: string
  dueDate: string
  status: 'planning' | 'in_progress' | 'review' | 'completed'
  lastUpdate: string
  nextMilestone: string
}

const mockRequests: ServiceRequest[] = [
  {
    id: '1',
    title: 'Financial Services BCM Gap Analysis & Implementation Plan',
    description: 'Comprehensive BCM gap analysis for growing fintech company. Need expert to assess current state and develop implementation roadmap.',
    serviceType: 'BCM Assessment',
    industry: 'Financial Services',
    urgency: 'high',
    budget: { min: 150, max: 200, type: 'hourly' },
    duration: '6-8 weeks',
    location: 'New York, NY',
    remote: true,
    status: 'assigned',
    proposalsCount: 12,
    views: 245,
    postedDate: '2024-01-15',
    deadline: '2024-01-25',
    selectedSpecialist: {
      name: 'Dr. Sarah Martinez',
      rating: 4.9
    }
  },
  {
    id: '2',
    title: 'Healthcare Crisis Management Training Program',
    description: 'Regional healthcare network needs crisis management training for leadership team.',
    serviceType: 'Training & Workshop',
    industry: 'Healthcare',
    urgency: 'medium',
    budget: { min: 5000, max: 15000, type: 'fixed' },
    duration: '4 weeks',
    location: 'Chicago, IL',
    remote: false,
    status: 'in_progress',
    proposalsCount: 8,
    views: 189,
    postedDate: '2024-01-12',
    deadline: '2024-01-22'
  },
  {
    id: '3',
    title: 'Manufacturing Supply Chain Resilience Assessment',
    description: 'Global automotive manufacturer seeking supply chain resilience expert.',
    serviceType: 'Risk Assessment',
    industry: 'Manufacturing',
    urgency: 'low',
    budget: { min: 120, max: 180, type: 'hourly' },
    duration: '12-16 weeks',
    location: 'Detroit, MI',
    remote: true,
    status: 'posted',
    proposalsCount: 15,
    views: 334,
    postedDate: '2024-01-10',
    deadline: '2024-01-30'
  }
]

const mockProjects: ActiveProject[] = [
  {
    id: '1',
    title: 'Financial Services BCM Gap Analysis',
    specialist: {
      name: 'Dr. Sarah Martinez',
      rating: 4.9
    },
    progress: 75,
    budget: '$32,500',
    startDate: '2024-01-26',
    dueDate: '2024-03-15',
    status: 'in_progress',
    lastUpdate: '2024-02-14',
    nextMilestone: 'Implementation Plan Delivery'
  },
  {
    id: '2',
    title: 'Healthcare Crisis Training',
    specialist: {
      name: 'Michael Thompson',
      rating: 4.7
    },
    progress: 45,
    budget: '$12,000',
    startDate: '2024-01-23',
    dueDate: '2024-02-23',
    status: 'in_progress',
    lastUpdate: '2024-02-12',
    nextMilestone: 'Training Material Review'
  }
]

export default function ClientDashboard() {
  const [activeTab, setActiveTab] = useState('overview')

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'draft': return 'bg-gray-100 text-gray-800'
      case 'posted': return 'bg-blue-100 text-blue-800'
      case 'in_review': return 'bg-yellow-100 text-yellow-800'
      case 'assigned': return 'bg-purple-100 text-purple-800'
      case 'in_progress': return 'bg-orange-100 text-orange-800'
      case 'completed': return 'bg-green-100 text-green-800'
      case 'cancelled': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getUrgencyColor = (urgency: string) => {
    switch (urgency) {
      case 'urgent': return 'bg-red-100 text-red-800'
      case 'high': return 'bg-orange-100 text-orange-800'
      case 'medium': return 'bg-yellow-100 text-yellow-800'
      case 'low': return 'bg-green-100 text-green-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getBudgetDisplay = (budget: ServiceRequest['budget']) => {
    const { min, max, type } = budget
    const typeLabel = type === 'hourly' ? '/hr' : type === 'fixed' ? 'fixed' : '/month'
    return `$${min}${max !== min ? `-$${max}` : ''} ${typeLabel}`
  }

  return (
    <AppLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <h1 className="text-3xl font-bold">Client Dashboard</h1>
            <p className="text-gray-600">Manage your BCM service requests and projects</p>
          </div>
          <Button className="flex items-center gap-2">
            <Plus className="h-4 w-4" />
            Post New Request
          </Button>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <FileText className="h-5 w-5 text-blue-600" />
                <div>
                  <div className="text-2xl font-bold">{mockRequests.length}</div>
                  <div className="text-sm text-gray-600">Service Requests</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <Users className="h-5 w-5 text-green-600" />
                <div>
                  <div className="text-2xl font-bold">{mockProjects.length}</div>
                  <div className="text-sm text-gray-600">Active Projects</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <DollarSign className="h-5 w-5 text-purple-600" />
                <div>
                  <div className="text-2xl font-bold">$44,500</div>
                  <div className="text-sm text-gray-600">Total Investment</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <TrendingUp className="h-5 w-5 text-orange-600" />
                <div>
                  <div className="text-2xl font-bold">4.8</div>
                  <div className="text-sm text-gray-600">Avg Specialist Rating</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="requests">My Requests</TabsTrigger>
            <TabsTrigger value="projects">Active Projects</TabsTrigger>
            <TabsTrigger value="completed">Completed</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            {/* Recent Activity */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Recent Activity</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-start gap-4">
                    <div className="w-2 h-2 bg-green-500 rounded-full mt-3"></div>
                    <div className="flex-1">
                      <p className="text-sm font-medium">Dr. Sarah Martinez submitted milestone deliverable</p>
                      <p className="text-xs text-gray-500">Financial Services BCM Gap Analysis • 2 hours ago</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-4">
                    <div className="w-2 h-2 bg-blue-500 rounded-full mt-3"></div>
                    <div className="flex-1">
                      <p className="text-sm font-medium">New proposal received from Jennifer Liu</p>
                      <p className="text-xs text-gray-500">Manufacturing Supply Chain Assessment • 5 hours ago</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-4">
                    <div className="w-2 h-2 bg-orange-500 rounded-full mt-3"></div>
                    <div className="flex-1">
                      <p className="text-sm font-medium">Training schedule confirmed with Michael Thompson</p>
                      <p className="text-xs text-gray-500">Healthcare Crisis Training • 1 day ago</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Recommended Specialists</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {[
                    { name: 'Jennifer Liu', rating: 4.8, expertise: 'Supply Chain BCM', projects: 67 },
                    { name: 'Robert Chen', rating: 4.6, expertise: 'BCM Program Management', projects: 73 },
                    { name: 'Emily Rodriguez', rating: 4.9, expertise: 'Crisis Communication', projects: 45 }
                  ].map((specialist, index) => (
                    <div key={index} className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <Avatar className="h-10 w-10">
                          <AvatarFallback>
                            {specialist.name.split(' ').map(n => n[0]).join('')}
                          </AvatarFallback>
                        </Avatar>
                        <div>
                          <p className="font-medium text-sm">{specialist.name}</p>
                          <p className="text-xs text-gray-600">{specialist.expertise}</p>
                          <div className="flex items-center gap-2 mt-1">
                            <Star className="h-3 w-3 fill-yellow-400 text-yellow-400" />
                            <span className="text-xs">{specialist.rating}</span>
                            <span className="text-xs text-gray-500">• {specialist.projects} projects</span>
                          </div>
                        </div>
                      </div>
                      <Button size="sm" variant="outline">View</Button>
                    </div>
                  ))}
                </CardContent>
              </Card>
            </div>

            {/* Current Projects Summary */}
            <Card>
              <CardHeader>
                <CardTitle>Current Projects Overview</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {mockProjects.map(project => (
                    <div key={project.id} className="border rounded-lg p-4">
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex-1">
                          <h4 className="font-medium">{project.title}</h4>
                          <div className="flex items-center gap-2 text-sm text-gray-600 mt-1">
                            <Avatar className="h-6 w-6">
                              <AvatarFallback className="text-xs">
                                {project.specialist.name.split(' ').map(n => n[0]).join('')}
                              </AvatarFallback>
                            </Avatar>
                            <span>{project.specialist.name}</span>
                            <Star className="h-3 w-3 fill-yellow-400 text-yellow-400" />
                            <span>{project.specialist.rating}</span>
                          </div>
                        </div>
                        <Badge className={getStatusColor(project.status)}>
                          {project.status.replace('_', ' ')}
                        </Badge>
                      </div>

                      <div className="space-y-3">
                        <div>
                          <div className="flex justify-between text-sm mb-1">
                            <span>Progress</span>
                            <span>{project.progress}%</span>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-2">
                            <div
                              className="bg-blue-600 h-2 rounded-full"
                              style={{ width: `${project.progress}%` }}
                            />
                          </div>
                        </div>

                        <div className="grid grid-cols-2 gap-4 text-sm">
                          <div>
                            <span className="text-gray-600">Budget:</span>
                            <div className="font-medium">{project.budget}</div>
                          </div>
                          <div>
                            <span className="text-gray-600">Due:</span>
                            <div className="font-medium">{project.dueDate}</div>
                          </div>
                        </div>

                        <div className="text-sm">
                          <span className="text-gray-600">Next Milestone:</span>
                          <div className="font-medium">{project.nextMilestone}</div>
                        </div>

                        <div className="flex gap-2 pt-2">
                          <Button size="sm" variant="outline" className="flex-1">
                            <MessageSquare className="h-3 w-3 mr-1" />
                            Message
                          </Button>
                          <Button size="sm" className="flex-1">
                            View Details
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="requests" className="space-y-4">
            {mockRequests.map(request => (
              <Card key={request.id} className="hover:shadow-md transition-shadow">
                <CardContent className="p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-lg font-semibold">{request.title}</h3>
                        <Badge className={getStatusColor(request.status)}>
                          {request.status.replace('_', ' ')}
                        </Badge>
                        <Badge className={getUrgencyColor(request.urgency)}>
                          {request.urgency}
                        </Badge>
                      </div>
                      <p className="text-gray-600 text-sm mb-3 line-clamp-2">{request.description}</p>

                      {request.selectedSpecialist && (
                        <div className="flex items-center gap-2 mb-3 p-2 bg-green-50 rounded-lg">
                          <CheckCircle className="h-4 w-4 text-green-600" />
                          <span className="text-sm">Assigned to {request.selectedSpecialist.name}</span>
                          <Star className="h-3 w-3 fill-yellow-400 text-yellow-400" />
                          <span className="text-sm">{request.selectedSpecialist.rating}</span>
                        </div>
                      )}
                    </div>

                    <div className="flex items-center gap-2">
                      <Button variant="outline" size="sm">
                        <Edit className="h-3 w-3 mr-1" />
                        Edit
                      </Button>
                      <Button size="sm">
                        <Eye className="h-3 w-3 mr-1" />
                        View
                      </Button>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                    <div className="text-center p-3 bg-blue-50 rounded-lg">
                      <DollarSign className="h-4 w-4 mx-auto mb-1 text-blue-600" />
                      <div className="text-xs text-gray-600">Budget</div>
                      <div className="font-semibold text-sm">{getBudgetDisplay(request.budget)}</div>
                    </div>
                    <div className="text-center p-3 bg-green-50 rounded-lg">
                      <Clock className="h-4 w-4 mx-auto mb-1 text-green-600" />
                      <div className="text-xs text-gray-600">Duration</div>
                      <div className="font-semibold text-sm">{request.duration}</div>
                    </div>
                    <div className="text-center p-3 bg-purple-50 rounded-lg">
                      <Send className="h-4 w-4 mx-auto mb-1 text-purple-600" />
                      <div className="text-xs text-gray-600">Proposals</div>
                      <div className="font-semibold text-sm">{request.proposalsCount}</div>
                    </div>
                    <div className="text-center p-3 bg-orange-50 rounded-lg">
                      <Eye className="h-4 w-4 mx-auto mb-1 text-orange-600" />
                      <div className="text-xs text-gray-600">Views</div>
                      <div className="font-semibold text-sm">{request.views}</div>
                    </div>
                  </div>

                  <div className="flex items-center justify-between text-sm text-gray-500 pt-4 border-t">
                    <div className="flex items-center gap-4">
                      <span>Posted {request.postedDate}</span>
                      <span>•</span>
                      <span>Deadline {request.deadline}</span>
                    </div>
                    {request.status === 'posted' && request.proposalsCount > 0 && (
                      <Button size="sm">
                        Review Proposals ({request.proposalsCount})
                      </Button>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </TabsContent>

          <TabsContent value="projects" className="space-y-4">
            {mockProjects.map(project => (
              <Card key={project.id} className="hover:shadow-md transition-shadow">
                <CardContent className="p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold mb-2">{project.title}</h3>
                      <div className="flex items-center gap-4 mb-3">
                        <div className="flex items-center gap-2">
                          <Avatar className="h-8 w-8">
                            <AvatarFallback>
                              {project.specialist.name.split(' ').map(n => n[0]).join('')}
                            </AvatarFallback>
                          </Avatar>
                          <div>
                            <p className="font-medium text-sm">{project.specialist.name}</p>
                            <div className="flex items-center gap-1">
                              <Star className="h-3 w-3 fill-yellow-400 text-yellow-400" />
                              <span className="text-xs">{project.specialist.rating}</span>
                            </div>
                          </div>
                        </div>
                        <Badge className={getStatusColor(project.status)}>
                          {project.status.replace('_', ' ')}
                        </Badge>
                      </div>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Progress</span>
                        <span className="font-medium">{project.progress}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-blue-600 h-2 rounded-full"
                          style={{ width: `${project.progress}%` }}
                        />
                      </div>
                    </div>

                    <div className="text-center p-3 bg-green-50 rounded-lg">
                      <DollarSign className="h-4 w-4 mx-auto mb-1 text-green-600" />
                      <div className="text-xs text-gray-600">Budget</div>
                      <div className="font-semibold text-sm">{project.budget}</div>
                    </div>

                    <div className="text-center p-3 bg-orange-50 rounded-lg">
                      <Calendar className="h-4 w-4 mx-auto mb-1 text-orange-600" />
                      <div className="text-xs text-gray-600">Due Date</div>
                      <div className="font-semibold text-sm">{project.dueDate}</div>
                    </div>
                  </div>

                  <div className="mb-4">
                    <div className="text-sm text-gray-600 mb-1">Next Milestone:</div>
                    <div className="font-medium">{project.nextMilestone}</div>
                  </div>

                  <div className="flex items-center justify-between pt-4 border-t">
                    <div className="text-xs text-gray-500">
                      Last updated: {project.lastUpdate}
                    </div>
                    <div className="flex gap-2">
                      <Button variant="outline" size="sm">
                        <MessageSquare className="h-3 w-3 mr-1" />
                        Message
                      </Button>
                      <Button size="sm">
                        View Details
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </TabsContent>

          <TabsContent value="completed" className="space-y-6">
            <div className="text-center py-12">
              <CheckCircle className="h-12 w-12 mx-auto text-gray-300 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No completed projects yet</h3>
              <p className="text-gray-600">Your completed projects and their reviews will appear here</p>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </AppLayout>
  )
}