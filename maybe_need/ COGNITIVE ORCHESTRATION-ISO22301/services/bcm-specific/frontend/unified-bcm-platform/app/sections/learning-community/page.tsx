'use client'

import React, { useState } from 'react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  BookOpen,
  Users,
  Trophy,
  GraduationCap,
  MessageSquare,
  Library,
  Target,
  Sparkles,
  ChevronRight
} from 'lucide-react'

// Temporary placeholder components
function Training() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Training Module</CardTitle>
      </CardHeader>
      <CardContent>
        <p>Training content will be integrated here.</p>
      </CardContent>
    </Card>
  )
}

function CommunityForum() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Community Forum</CardTitle>
      </CardHeader>
      <CardContent>
        <p>Community forum will be integrated here.</p>
      </CardContent>
    </Card>
  )
}

function KnowledgeHub() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Knowledge Hub</CardTitle>
      </CardHeader>
      <CardContent>
        <p>Knowledge hub will be integrated here.</p>
      </CardContent>
    </Card>
  )
}

function GamificationDashboard() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Achievements Dashboard</CardTitle>
      </CardHeader>
      <CardContent>
        <p>Gamification dashboard will be integrated here.</p>
      </CardContent>
    </Card>
  )
}

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
      <div className="bg-gradient-to-r from-purple-600 to-indigo-700 text-white">
        <div className="container mx-auto px-4 py-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold flex items-center gap-3">
                <GraduationCap className="h-8 w-8" />
                {title}
              </h1>
              <p className="text-purple-100 mt-2">{description}</p>
            </div>
            <div className="flex gap-3">
              <Button variant="secondary">
                <Sparkles className="h-4 w-4 mr-2" />
                Achievements
              </Button>
              <Button variant="secondary">
                <Target className="h-4 w-4 mr-2" />
                My Progress
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

// Quick Stats Component
function QuickStats() {
  const stats = [
    {
      icon: BookOpen,
      label: 'Courses Completed',
      value: '12',
      change: '+3 this month',
      color: 'text-blue-600 bg-blue-100'
    },
    {
      icon: Trophy,
      label: 'Total Points',
      value: '2,450',
      change: '+350 this week',
      color: 'text-yellow-600 bg-yellow-100'
    },
    {
      icon: Users,
      label: 'Community Rank',
      value: '#5',
      change: '↑ 2 positions',
      color: 'text-green-600 bg-green-100'
    },
    {
      icon: Target,
      label: 'Learning Streak',
      value: '15 days',
      change: 'Keep it up!',
      color: 'text-purple-600 bg-purple-100'
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

// Learning Paths Component
function LearningPaths() {
  const paths = [
    {
      id: '1',
      name: 'BCM Fundamentals',
      description: 'Master the basics of Business Continuity Management',
      modules: 8,
      completedModules: 5,
      difficulty: 'beginner',
      estimatedTime: '12 hours'
    },
    {
      id: '2',
      name: 'ISO 22301 Certification',
      description: 'Prepare for ISO 22301 certification exam',
      modules: 12,
      completedModules: 3,
      difficulty: 'advanced',
      estimatedTime: '24 hours'
    },
    {
      id: '3',
      name: 'Crisis Communication',
      description: 'Learn effective crisis communication strategies',
      modules: 6,
      completedModules: 6,
      difficulty: 'intermediate',
      estimatedTime: '8 hours'
    }
  ]

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'beginner': return 'bg-green-100 text-green-800'
      case 'intermediate': return 'bg-yellow-100 text-yellow-800'
      case 'advanced': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Your Learning Paths</h3>
        <Button variant="outline" size="sm">
          Browse All Paths
        </Button>
      </div>

      {paths.map(path => (
        <Card key={path.id} className="hover:shadow-md transition-shadow">
          <CardContent className="p-4">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <h4 className="font-medium">{path.name}</h4>
                  <Badge className={getDifficultyColor(path.difficulty)} variant="secondary">
                    {path.difficulty}
                  </Badge>
                </div>
                <p className="text-sm text-muted-foreground mb-3">{path.description}</p>
                <div className="flex items-center gap-4 text-sm">
                  <span className="flex items-center gap-1">
                    <BookOpen className="h-3 w-3" />
                    {path.completedModules}/{path.modules} modules
                  </span>
                  <span className="flex items-center gap-1">
                    <Trophy className="h-3 w-3" />
                    {Math.round((path.completedModules / path.modules) * 100)}% complete
                  </span>
                  <span className="text-muted-foreground">{path.estimatedTime}</span>
                </div>
                <div className="mt-3">
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-gradient-to-r from-purple-500 to-indigo-500 h-2 rounded-full"
                      style={{ width: `${(path.completedModules / path.modules) * 100}%` }}
                    />
                  </div>
                </div>
              </div>
              <Button size="sm" variant={path.completedModules === path.modules ? 'outline' : 'default'}>
                {path.completedModules === path.modules ? 'Review' : 'Continue'}
                <ChevronRight className="h-4 w-4 ml-1" />
              </Button>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}

// Main Learning Community Component
export default function LearningCommunitySection() {
  const [activeTab, setActiveTab] = useState('overview')

  return (
    <SectionLayout
      title="Learning & Community Hub"
      description="Enhance your BCM knowledge, earn achievements, and connect with professionals"
    >
      <QuickStats />

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="training">Training</TabsTrigger>
          <TabsTrigger value="community">Community</TabsTrigger>
          <TabsTrigger value="knowledge">Knowledge Hub</TabsTrigger>
          <TabsTrigger value="gamification">Achievements</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6 mt-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <LearningPaths />
            </div>

            <div className="space-y-4">
              {/* Recent Activity */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Recent Activity</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex items-start gap-2">
                    <div className="w-2 h-2 rounded-full bg-green-500 mt-1.5" />
                    <div className="flex-1">
                      <p className="text-sm">Completed "Risk Assessment Basics"</p>
                      <p className="text-xs text-muted-foreground">2 hours ago</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-2">
                    <div className="w-2 h-2 rounded-full bg-blue-500 mt-1.5" />
                    <div className="flex-1">
                      <p className="text-sm">Earned "Quick Learner" badge</p>
                      <p className="text-xs text-muted-foreground">Yesterday</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-2">
                    <div className="w-2 h-2 rounded-full bg-purple-500 mt-1.5" />
                    <div className="flex-1">
                      <p className="text-sm">Joined "ISO 22301 Study Group"</p>
                      <p className="text-xs text-muted-foreground">3 days ago</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Upcoming Events */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Upcoming Events</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="space-y-3">
                    <div className="p-3 border rounded-lg">
                      <p className="font-medium text-sm">BCM Webinar Series</p>
                      <p className="text-xs text-muted-foreground">Tomorrow, 2:00 PM</p>
                      <Badge variant="outline" className="mt-2 text-xs">Live Event</Badge>
                    </div>
                    <div className="p-3 border rounded-lg">
                      <p className="font-medium text-sm">Crisis Simulation Exercise</p>
                      <p className="text-xs text-muted-foreground">Feb 5, 10:00 AM</p>
                      <Badge variant="outline" className="mt-2 text-xs">Workshop</Badge>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Community Highlights */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Community Highlights</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Active Discussions</span>
                      <Badge>23</Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm">New Members This Week</span>
                      <Badge>+47</Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Knowledge Articles</span>
                      <Badge>156</Badge>
                    </div>
                  </div>
                  <Button variant="outline" size="sm" className="w-full mt-3">
                    <MessageSquare className="h-4 w-4 mr-2" />
                    Join Discussion
                  </Button>
                </CardContent>
              </Card>
            </div>
          </div>
        </TabsContent>

        <TabsContent value="training" className="mt-6">
          <Training />
        </TabsContent>

        <TabsContent value="community" className="mt-6">
          <CommunityForum />
        </TabsContent>

        <TabsContent value="knowledge" className="mt-6">
          <KnowledgeHub />
        </TabsContent>

        <TabsContent value="gamification" className="mt-6">
          <GamificationDashboard />
        </TabsContent>
      </Tabs>
    </SectionLayout>
  )
}