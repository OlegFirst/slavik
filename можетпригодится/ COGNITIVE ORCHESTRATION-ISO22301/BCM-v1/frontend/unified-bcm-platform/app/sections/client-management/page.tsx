'use client'

import React, { useState } from 'react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import {
  Building2,
  Users,
  Briefcase,
  Globe,
  FolderOpen,
  Calendar,
  DollarSign,
  TrendingUp,
  Clock,
  CheckCircle,
  AlertCircle,
  Plus,
  Settings,
  ChevronRight,
  Shield,
  Activity
} from 'lucide-react'

// Import components
import { ClientPortal } from '@/components/sections/ClientPortal'
import { SpecialistCard } from '@/frontend/bcm-marketplace/src/components/specialist/SpecialistCard'
import { portalAPI, mockPortalData } from '@/lib/api/portal'

// Section Layout Component
function SectionLayout({
  title,
  description,
  children
}: {
  title: string
  description: string
  children: React.ReactNode
}) {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-gradient-to-r from-blue-600 to-cyan-700 text-white">
        <div className="container mx-auto px-4 py-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold flex items-center gap-3">
                <Building2 className="h-8 w-8" />
                {title}
              </h1>
              <p className="text-blue-100 mt-2">{description}</p>
            </div>
            <div className="flex gap-3">
              <Button variant="secondary">
                <Plus className="h-4 w-4 mr-2" />
                New Client
              </Button>
              <Button variant="secondary">
                <FolderOpen className="h-4 w-4 mr-2" />
                New Project
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-6">
        {children}
      </div>
    </div>
  )
}

// Dashboard Stats Component
function DashboardStats() {
  const stats = [
    {
      icon: Building2,
      label: 'Active Clients',
      value: '24',
      change: '+3 this month',
      color: 'text-blue-600 bg-blue-100'
    },
    {
      icon: Briefcase,
      label: 'Active Projects',
      value: '18',
      change: '6 in progress',
      color: 'text-green-600 bg-green-100'
    },
    {
      icon: DollarSign,
      label: 'Revenue (YTD)',
      value: '$485K',
      change: '+22% vs last year',
      color: 'text-purple-600 bg-purple-100'
    },
    {
      icon: Users,
      label: 'Team Members',
      value: '12',
      change: '95% utilized',
      color: 'text-orange-600 bg-orange-100'
    }
  ]

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      {stats.map((stat, index) => (
        <Card key={index}>
          <CardContent className="p-4">
            <div className="flex items-start justify-between">
              <div>
                <div className={`inline-flex p-2 rounded-lg ${stat.color} mb-2`}>
                  <stat.icon className="h-5 w-5" />
                </div>
                <p className="text-xs text-muted-foreground">{stat.label}</p>
                <p className="text-2xl font-bold mt-1">{stat.value}</p>
                <p className="text-xs text-green-600 mt-1">{stat.change}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}

// Client List Component
function ClientList() {
  const clients = [
    {
      id: '1',
      name: 'ACME Corporation',
      industry: 'Technology',
      status: 'active',
      projects: 3,
      lastContact: '2 days ago',
      healthScore: 95,
      revenue: 125000
    },
    {
      id: '2',
      name: 'Global Finance Inc',
      industry: 'Financial Services',
      status: 'active',
      projects: 2,
      lastContact: 'Today',
      healthScore: 88,
      revenue: 89000
    },
    {
      id: '3',
      name: 'Healthcare Plus',
      industry: 'Healthcare',
      status: 'onboarding',
      projects: 1,
      lastContact: 'Yesterday',
      healthScore: 100,
      revenue: 45000
    }
  ]

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800'
      case 'onboarding': return 'bg-blue-100 text-blue-800'
      case 'inactive': return 'bg-gray-100 text-gray-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getHealthColor = (score: number) => {
    if (score >= 90) return 'text-green-600'
    if (score >= 70) return 'text-yellow-600'
    return 'text-red-600'
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Client Portfolio</h3>
        <div className="flex gap-2">
          <Button variant="outline" size="sm">Filter</Button>
          <Button variant="outline" size="sm">Export</Button>
        </div>
      </div>

      {clients.map(client => (
        <Card key={client.id} className="hover:shadow-md transition-shadow">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <Avatar className="h-12 w-12">
                  <AvatarFallback className="bg-gradient-to-br from-blue-500 to-cyan-500 text-white">
                    {client.name.split(' ').map(n => n[0]).join('')}
                  </AvatarFallback>
                </Avatar>
                <div>
                  <div className="flex items-center gap-2">
                    <h4 className="font-medium">{client.name}</h4>
                    <Badge className={getStatusColor(client.status)} variant="secondary">
                      {client.status}
                    </Badge>
                  </div>
                  <div className="flex items-center gap-4 text-sm text-muted-foreground mt-1">
                    <span>{client.industry}</span>
                    <span>•</span>
                    <span>{client.projects} active projects</span>
                    <span>•</span>
                    <span>Last contact: {client.lastContact}</span>
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-6">
                <div className="text-center">
                  <p className="text-xs text-muted-foreground">Health Score</p>
                  <p className={`text-lg font-bold ${getHealthColor(client.healthScore)}`}>
                    {client.healthScore}%
                  </p>
                </div>
                <div className="text-center">
                  <p className="text-xs text-muted-foreground">Revenue</p>
                  <p className="text-lg font-bold">${(client.revenue / 1000).toFixed(0)}K</p>
                </div>
                <Button variant="ghost" size="sm">
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      ))}

      <Button variant="outline" className="w-full">
        View All Clients
      </Button>
    </div>
  )
}

// Project Management Component
function ProjectManagement() {
  const projects = mockPortalData.projects

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800'
      case 'planning': return 'bg-blue-100 text-blue-800'
      case 'on_hold': return 'bg-yellow-100 text-yellow-800'
      case 'completed': return 'bg-gray-100 text-gray-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Active Projects</h3>
        <Button size="sm">
          <Plus className="h-4 w-4 mr-2" />
          New Project
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {projects.map(project => (
          <Card key={project.id}>
            <CardHeader className="pb-3">
              <div className="flex items-start justify-between">
                <div>
                  <CardTitle className="text-base">{project.name}</CardTitle>
                  <Badge className={getStatusColor(project.status)} variant="secondary" className="mt-1">
                    {project.status}
                  </Badge>
                </div>
                <Button variant="ghost" size="sm">
                  <Settings className="h-4 w-4" />
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground mb-4">
                {project.description}
              </p>

              <div className="space-y-3">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Progress</span>
                  <span className="font-medium">{project.progress}%</span>
                </div>
                <Progress value={project.progress} className="h-2" />

                <div className="grid grid-cols-2 gap-3 text-sm">
                  <div>
                    <p className="text-muted-foreground">Start Date</p>
                    <p className="font-medium">{new Date(project.startDate).toLocaleDateString()}</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">End Date</p>
                    <p className="font-medium">
                      {project.endDate ? new Date(project.endDate).toLocaleDateString() : 'Ongoing'}
                    </p>
                  </div>
                </div>

                <div className="flex items-center justify-between pt-3 border-t">
                  <div className="flex items-center gap-2">
                    <Avatar className="h-6 w-6">
                      <AvatarFallback className="text-xs">PM</AvatarFallback>
                    </Avatar>
                    <span className="text-sm">{project.team[0]?.name || 'Unassigned'}</span>
                  </div>
                  {project.budget && (
                    <span className="text-sm font-medium">
                      ${(project.budget / 1000).toFixed(0)}K
                    </span>
                  )}
                </div>

                <div className="flex gap-2">
                  <Button size="sm" variant="outline" className="flex-1">
                    View Details
                  </Button>
                  <Button size="sm" className="flex-1">
                    Open Dashboard
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}

// Specialist Directory Component
function SpecialistDirectory() {
  const specialists = [
    {
      id: '1',
      name: 'Dr. Sarah Martinez',
      title: 'BCM Consultant & ISO Expert',
      specializations: ['ISO 22301', 'Risk Assessment', 'Crisis Management'],
      rating: 4.9,
      reviewCount: 47,
      availability: 'available' as const,
      hourlyRate: 250
    },
    {
      id: '2',
      name: 'Michael Chen',
      title: 'Senior Risk Analyst',
      specializations: ['BIA', 'Financial Services', 'Compliance'],
      rating: 4.8,
      reviewCount: 32,
      availability: 'busy' as const,
      hourlyRate: 200
    },
    {
      id: '3',
      name: 'Jennifer Liu',
      title: 'Crisis Communication Expert',
      specializations: ['Crisis Communication', 'Media Relations', 'Training'],
      rating: 5.0,
      reviewCount: 28,
      availability: 'available' as const,
      hourlyRate: 300
    }
  ]

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Available Specialists</h3>
        <Button variant="outline" size="sm">
          Browse All Specialists
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {specialists.map(specialist => (
          <Card key={specialist.id} className="hover:shadow-md transition-shadow">
            <CardContent className="p-4">
              <div className="flex items-start gap-3">
                <Avatar className="h-12 w-12">
                  <AvatarFallback>
                    {specialist.name.split(' ').map(n => n[0]).join('')}
                  </AvatarFallback>
                </Avatar>
                <div className="flex-1">
                  <h4 className="font-medium">{specialist.name}</h4>
                  <p className="text-sm text-muted-foreground">{specialist.title}</p>

                  <div className="flex items-center gap-2 mt-2">
                    <div className="flex items-center gap-1">
                      <span className="text-yellow-500">★</span>
                      <span className="text-sm font-medium">{specialist.rating}</span>
                    </div>
                    <span className="text-sm text-muted-foreground">
                      ({specialist.reviewCount} reviews)
                    </span>
                  </div>

                  <div className="flex flex-wrap gap-1 mt-2">
                    {specialist.specializations.slice(0, 2).map((spec, i) => (
                      <Badge key={i} variant="secondary" className="text-xs">
                        {spec}
                      </Badge>
                    ))}
                  </div>

                  <div className="flex items-center justify-between mt-3">
                    <div className="flex items-center gap-1">
                      <div className={`w-2 h-2 rounded-full ${
                        specialist.availability === 'available' ? 'bg-green-500' :
                        specialist.availability === 'busy' ? 'bg-yellow-500' :
                        'bg-red-500'
                      }`} />
                      <span className="text-xs text-muted-foreground">
                        {specialist.availability}
                      </span>
                    </div>
                    <span className="text-sm font-medium">
                      ${specialist.hourlyRate}/hr
                    </span>
                  </div>

                  <Button size="sm" className="w-full mt-3">
                    Request Specialist
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}

// Main Client Management Component
export default function ClientManagementSection() {
  const [activeTab, setActiveTab] = useState('overview')

  return (
    <SectionLayout
      title="Client & Project Management"
      description="Manage client relationships, projects, and specialist assignments"
    >
      <DashboardStats />

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="clients">Clients</TabsTrigger>
          <TabsTrigger value="projects">Projects</TabsTrigger>
          <TabsTrigger value="specialists">Specialists</TabsTrigger>
          <TabsTrigger value="portal">Client Portal</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6 mt-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 space-y-6">
              <ClientList />

              {/* Recent Activity */}
              <Card>
                <CardHeader>
                  <CardTitle>Recent Activity</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex items-start gap-3">
                    <CheckCircle className="h-5 w-5 text-green-500 mt-0.5" />
                    <div className="flex-1">
                      <p className="text-sm">Project milestone completed for ACME Corporation</p>
                      <p className="text-xs text-muted-foreground">2 hours ago</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <Users className="h-5 w-5 text-blue-500 mt-0.5" />
                    <div className="flex-1">
                      <p className="text-sm">New specialist assigned to Global Finance project</p>
                      <p className="text-xs text-muted-foreground">4 hours ago</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <AlertCircle className="h-5 w-5 text-yellow-500 mt-0.5" />
                    <div className="flex-1">
                      <p className="text-sm">Risk identified in Healthcare Plus implementation</p>
                      <p className="text-xs text-muted-foreground">Yesterday</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            <div className="space-y-4">
              {/* Upcoming Deadlines */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Upcoming Deadlines</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="p-3 border rounded-lg">
                    <div className="flex items-center justify-between mb-1">
                      <p className="font-medium text-sm">BIA Review - ACME</p>
                      <Badge variant="destructive" className="text-xs">2 days</Badge>
                    </div>
                    <p className="text-xs text-muted-foreground">Risk assessment deliverable</p>
                  </div>
                  <div className="p-3 border rounded-lg">
                    <div className="flex items-center justify-between mb-1">
                      <p className="font-medium text-sm">Training Session</p>
                      <Badge variant="secondary" className="text-xs">5 days</Badge>
                    </div>
                    <p className="text-xs text-muted-foreground">Global Finance team training</p>
                  </div>
                  <div className="p-3 border rounded-lg">
                    <div className="flex items-center justify-between mb-1">
                      <p className="font-medium text-sm">ISO Audit Prep</p>
                      <Badge variant="secondary" className="text-xs">1 week</Badge>
                    </div>
                    <p className="text-xs text-muted-foreground">Documentation review</p>
                  </div>
                </CardContent>
              </Card>

              {/* Team Utilization */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Team Utilization</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div>
                      <div className="flex items-center justify-between text-sm mb-1">
                        <span>Consultants</span>
                        <span>85%</span>
                      </div>
                      <Progress value={85} className="h-2" />
                    </div>
                    <div>
                      <div className="flex items-center justify-between text-sm mb-1">
                        <span>Analysts</span>
                        <span>92%</span>
                      </div>
                      <Progress value={92} className="h-2" />
                    </div>
                    <div>
                      <div className="flex items-center justify-between text-sm mb-1">
                        <span>Project Managers</span>
                        <span>78%</span>
                      </div>
                      <Progress value={78} className="h-2" />
                    </div>
                  </div>
                  <Button variant="outline" size="sm" className="w-full mt-4">
                    View Resource Planning
                  </Button>
                </CardContent>
              </Card>

              {/* Revenue Metrics */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-base flex items-center gap-2">
                    <TrendingUp className="h-4 w-4" />
                    Revenue Metrics
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">MRR</span>
                      <span className="font-medium">$42.5K</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">ARR</span>
                      <span className="font-medium">$510K</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">Pipeline</span>
                      <span className="font-medium">$125K</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">Win Rate</span>
                      <span className="font-medium text-green-600">68%</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </TabsContent>

        <TabsContent value="clients" className="mt-6">
          <ClientList />
        </TabsContent>

        <TabsContent value="projects" className="mt-6">
          <ProjectManagement />
        </TabsContent>

        <TabsContent value="specialists" className="mt-6">
          <SpecialistDirectory />
        </TabsContent>

        <TabsContent value="portal" className="mt-6">
          <ClientPortal />
        </TabsContent>
      </Tabs>
    </SectionLayout>
  )
}