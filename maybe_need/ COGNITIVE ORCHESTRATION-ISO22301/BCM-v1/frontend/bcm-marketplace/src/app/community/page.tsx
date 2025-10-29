'use client'

import React, { useState } from 'react'
import { AppLayout } from '@/components/layout/AppLayout'
import { CommunityForum } from '@/components/community/CommunityForum'
import { KnowledgeHub } from '@/components/community/KnowledgeHub'
import { LiveChat } from '@/components/community/LiveChat'
import { ExpertDirectory } from '@/components/community/ExpertDirectory'
import { CaseStudies } from '@/components/community/CaseStudies'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  Users,
  MessageSquare,
  BookOpen,
  MessageCircle,
  Star,
  TrendingUp,
  Calendar,
  Award,
  Eye,
  ThumbsUp,
  Clock
} from 'lucide-react'

export default function CommunityPage() {
  const [activeTab, setActiveTab] = useState('forum')

  return (
    <AppLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="space-y-2">
          <h1 className="text-3xl font-bold">BCM Community Hub</h1>
          <p className="text-gray-600">
            Connect with BCM professionals, share knowledge, and grow together
          </p>
        </div>

        {/* Community Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <Users className="h-5 w-5 text-blue-600" />
                <div>
                  <div className="text-2xl font-bold">12,847</div>
                  <div className="text-sm text-gray-600">Community Members</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <MessageSquare className="h-5 w-5 text-green-600" />
                <div>
                  <div className="text-2xl font-bold">2,156</div>
                  <div className="text-sm text-gray-600">Forum Posts</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <BookOpen className="h-5 w-5 text-purple-600" />
                <div>
                  <div className="text-2xl font-bold">487</div>
                  <div className="text-sm text-gray-600">Knowledge Articles</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <Star className="h-5 w-5 text-yellow-600" />
                <div>
                  <div className="text-2xl font-bold">94%</div>
                  <div className="text-sm text-gray-600">Satisfaction Rate</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Main Content Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-6">
            <TabsTrigger value="forum" className="flex items-center gap-2">
              <MessageSquare className="h-4 w-4" />
              Forum
            </TabsTrigger>
            <TabsTrigger value="knowledge" className="flex items-center gap-2">
              <BookOpen className="h-4 w-4" />
              Knowledge Hub
            </TabsTrigger>
            <TabsTrigger value="cases" className="flex items-center gap-2">
              <Award className="h-4 w-4" />
              Case Studies
            </TabsTrigger>
            <TabsTrigger value="chat" className="flex items-center gap-2">
              <MessageCircle className="h-4 w-4" />
              Live Chat
            </TabsTrigger>
            <TabsTrigger value="experts" className="flex items-center gap-2">
              <Users className="h-4 w-4" />
              Expert Directory
            </TabsTrigger>
            <TabsTrigger value="events" className="flex items-center gap-2">
              <Calendar className="h-4 w-4" />
              Events
            </TabsTrigger>
          </TabsList>

          <TabsContent value="forum" className="space-y-6">
            <CommunityForum />
          </TabsContent>

          <TabsContent value="knowledge" className="space-y-6">
            <KnowledgeHub />
          </TabsContent>

          <TabsContent value="cases" className="space-y-6">
            <CaseStudies />
          </TabsContent>

          <TabsContent value="chat" className="space-y-6">
            <LiveChat />
          </TabsContent>

          <TabsContent value="experts" className="space-y-6">
            <ExpertDirectory />
          </TabsContent>

          <TabsContent value="events" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Upcoming Events */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Calendar className="h-5 w-5" />
                    <span>Upcoming Events</span>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {[
                    {
                      title: 'BCM Best Practices Webinar',
                      date: 'Nov 25, 2024',
                      time: '2:00 PM EST',
                      attendees: 156,
                      type: 'Webinar'
                    },
                    {
                      title: 'Crisis Management Workshop',
                      date: 'Dec 3, 2024',
                      time: '10:00 AM EST',
                      attendees: 89,
                      type: 'Workshop'
                    },
                    {
                      title: 'ISO 22301 Implementation',
                      date: 'Dec 12, 2024',
                      time: '1:00 PM EST',
                      attendees: 234,
                      type: 'Training'
                    }
                  ].map((event, index) => (
                    <div key={index} className="flex items-start justify-between p-4 border rounded-lg">
                      <div className="flex-1">
                        <h3 className="font-medium text-gray-900">{event.title}</h3>
                        <div className="flex items-center space-x-4 text-sm text-gray-500 mt-2">
                          <div className="flex items-center space-x-1">
                            <Calendar className="h-3 w-3" />
                            <span>{event.date}</span>
                          </div>
                          <div className="flex items-center space-x-1">
                            <Clock className="h-3 w-3" />
                            <span>{event.time}</span>
                          </div>
                          <div className="flex items-center space-x-1">
                            <Users className="h-3 w-3" />
                            <span>{event.attendees} attending</span>
                          </div>
                        </div>
                      </div>
                      <div className="flex flex-col items-end space-y-2">
                        <Badge variant="secondary">{event.type}</Badge>
                        <Button size="sm">Join</Button>
                      </div>
                    </div>
                  ))}
                </CardContent>
              </Card>

              {/* Community Leaders */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Award className="h-5 w-5" />
                    <span>Community Leaders</span>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {[
                    {
                      name: 'Sarah Johnson',
                      title: 'Senior BCM Consultant',
                      contributions: 127,
                      badge: 'Expert'
                    },
                    {
                      name: 'Michael Chen',
                      title: 'Risk Management Director',
                      contributions: 95,
                      badge: 'Mentor'
                    },
                    {
                      name: 'Emily Rodriguez',
                      title: 'BCM Implementation Specialist',
                      contributions: 78,
                      badge: 'Contributor'
                    }
                  ].map((leader, index) => (
                    <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                          <span className="font-medium text-blue-600">
                            {leader.name.split(' ').map(n => n[0]).join('')}
                          </span>
                        </div>
                        <div>
                          <h4 className="font-medium">{leader.name}</h4>
                          <p className="text-sm text-gray-600">{leader.title}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <Badge variant="outline">{leader.badge}</Badge>
                        <p className="text-xs text-gray-500 mt-1">{leader.contributions} contributions</p>
                      </div>
                    </div>
                  ))}
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </AppLayout>
  )
}