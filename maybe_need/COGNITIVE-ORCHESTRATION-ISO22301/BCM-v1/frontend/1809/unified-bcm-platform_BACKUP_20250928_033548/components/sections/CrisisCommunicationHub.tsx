'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Radio, Users, MessageSquare, AlertTriangle, Phone, Mail, Megaphone } from 'lucide-react'

interface CommunicationChannel {
  id: string
  name: string
  type: 'internal' | 'external' | 'emergency'
  status: 'active' | 'inactive' | 'maintenance'
  lastUsed: string
  coverage: string
}

interface CrisisMessage {
  id: string
  type: 'alert' | 'update' | 'all-clear'
  priority: 'high' | 'medium' | 'low'
  title: string
  content: string
  channels: string[]
  recipients: string[]
  sentAt?: string
  status: 'draft' | 'scheduled' | 'sent'
}

export function CrisisCommunicationHub() {
  const [channels] = useState<CommunicationChannel[]>([
    {
      id: '1',
      name: 'Emergency Alert System',
      type: 'emergency',
      status: 'active',
      lastUsed: '2024-09-15T10:30:00Z',
      coverage: '100% workforce'
    },
    {
      id: '2', 
      name: 'Internal SMS Broadcast',
      type: 'internal',
      status: 'active',
      lastUsed: '2024-09-17T14:20:00Z',
      coverage: '98% workforce'
    },
    {
      id: '3',
      name: 'Public Relations Channel',
      type: 'external',
      status: 'active',
      lastUsed: '2024-09-10T09:15:00Z',
      coverage: 'Media & stakeholders'
    },
    {
      id: '4',
      name: 'Customer Portal Alerts',
      type: 'external',
      status: 'maintenance',
      lastUsed: '2024-09-16T16:45:00Z',
      coverage: 'All customers'
    }
  ])

  const [messages] = useState<CrisisMessage[]>([
    {
      id: '1',
      type: 'alert',
      priority: 'high',
      title: 'System Maintenance Scheduled',
      content: 'Critical system maintenance will begin at 2:00 AM UTC. All services will be temporarily unavailable.',
      channels: ['1', '2'],
      recipients: ['all-staff', 'it-team'],
      sentAt: '2024-09-18T01:45:00Z',
      status: 'sent'
    },
    {
      id: '2',
      type: 'update',
      priority: 'medium',
      title: 'Business Continuity Exercise Results',
      content: 'Thank you for participating in today\'s BC exercise. Results and feedback will be shared by EOD.',
      channels: ['2'],
      recipients: ['all-staff'],
      sentAt: '2024-09-17T17:30:00Z',
      status: 'sent'
    },
    {
      id: '3',
      type: 'alert',
      priority: 'high',
      title: 'Emergency Response Drill',
      content: 'Mandatory emergency response drill scheduled for tomorrow 10 AM. All departments must participate.',
      channels: ['1', '2', '4'],
      recipients: ['all-staff', 'department-heads'],
      status: 'draft'
    }
  ])

  const [activeTab, setActiveTab] = useState('dashboard')

  const getChannelIcon = (type: string) => {
    switch (type) {
      case 'emergency': return <AlertTriangle className="h-4 w-4" />
      case 'internal': return <Users className="h-4 w-4" />
      case 'external': return <Megaphone className="h-4 w-4" />
      default: return <Radio className="h-4 w-4" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800'
      case 'inactive': return 'bg-gray-100 text-gray-800'
      case 'maintenance': return 'bg-yellow-100 text-yellow-800'
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

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Crisis Communication Hub</h2>
          <p className="text-gray-600 mt-1">Manage crisis communications and emergency alerts</p>
        </div>
        <Button className="bg-red-600 hover:bg-red-700">
          <AlertTriangle className="h-4 w-4 mr-2" />
          Emergency Broadcast
        </Button>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="dashboard">Dashboard</TabsTrigger>
          <TabsTrigger value="channels">Channels</TabsTrigger>
          <TabsTrigger value="messages">Messages</TabsTrigger>
          <TabsTrigger value="templates">Templates</TabsTrigger>
        </TabsList>

        <TabsContent value="dashboard" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Active Channels</CardTitle>
                <Radio className="h-4 w-4 text-green-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">3</div>
                <p className="text-xs text-gray-600">1 under maintenance</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Messages Today</CardTitle>
                <MessageSquare className="h-4 w-4 text-blue-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">12</div>
                <p className="text-xs text-gray-600">+3 from yesterday</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Coverage</CardTitle>
                <Users className="h-4 w-4 text-purple-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">98%</div>
                <p className="text-xs text-gray-600">Workforce reached</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Response Rate</CardTitle>
                <Phone className="h-4 w-4 text-orange-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">85%</div>
                <p className="text-xs text-gray-600">Average acknowledgment</p>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Recent Crisis Communications</CardTitle>
              <CardDescription>Latest messages and their delivery status</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {messages.filter(m => m.status === 'sent').slice(0, 3).map(message => (
                  <div key={message.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <Badge className={getPriorityColor(message.priority)}>{message.priority}</Badge>
                        <span className="font-medium">{message.title}</span>
                      </div>
                      <p className="text-sm text-gray-600">{message.content}</p>
                      <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
                        <span>Sent: {new Date(message.sentAt!).toLocaleString()}</span>
                        <span>Channels: {message.channels.length}</span>
                        <span>Recipients: {message.recipients.length}</span>
                      </div>
                    </div>
                    <Button variant="outline" size="sm">View Details</Button>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="channels" className="space-y-6">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-medium">Communication Channels</h3>
            <Button>Add Channel</Button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {channels.map(channel => (
              <Card key={channel.id}>
                <CardHeader className="flex flex-row items-center justify-between space-y-0">
                  <div className="flex items-center gap-2">
                    {getChannelIcon(channel.type)}
                    <CardTitle className="text-base">{channel.name}</CardTitle>
                  </div>
                  <Badge className={getStatusColor(channel.status)}>{channel.status}</Badge>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Type:</span>
                      <span className="capitalize">{channel.type}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Coverage:</span>
                      <span>{channel.coverage}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Last Used:</span>
                      <span>{new Date(channel.lastUsed).toLocaleDateString()}</span>
                    </div>
                  </div>
                  <div className="flex gap-2 mt-4">
                    <Button variant="outline" size="sm" className="flex-1">Test</Button>
                    <Button variant="outline" size="sm" className="flex-1">Configure</Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="messages" className="space-y-6">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-medium">Crisis Messages</h3>
            <Button>
              <MessageSquare className="h-4 w-4 mr-2" />
              New Message
            </Button>
          </div>

          <div className="space-y-4">
            {messages.map(message => (
              <Card key={message.id}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Badge className={getPriorityColor(message.priority)}>{message.priority}</Badge>
                      <Badge variant="outline">{message.type}</Badge>
                      <span className="font-medium">{message.title}</span>
                    </div>
                    <Badge className={message.status === 'sent' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}>
                      {message.status}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-sm mb-4">{message.content}</p>
                  <div className="flex items-center gap-6 text-xs text-gray-500 mb-4">
                    <span>Channels: {message.channels.length}</span>
                    <span>Recipients: {message.recipients.join(', ')}</span>
                    {message.sentAt && <span>Sent: {new Date(message.sentAt).toLocaleString()}</span>}
                  </div>
                  <div className="flex gap-2">
                    {message.status === 'draft' && (
                      <>
                        <Button size="sm">Send Now</Button>
                        <Button variant="outline" size="sm">Schedule</Button>
                      </>
                    )}
                    <Button variant="outline" size="sm">Edit</Button>
                    <Button variant="outline" size="sm">Duplicate</Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="templates" className="space-y-6">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-medium">Message Templates</h3>
            <Button>Create Template</Button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[
              { name: 'System Outage Alert', type: 'alert', usage: 23 },
              { name: 'Emergency Evacuation', type: 'emergency', usage: 5 },
              { name: 'Scheduled Maintenance', type: 'update', usage: 47 },
              { name: 'All Clear Notification', type: 'all-clear', usage: 18 },
              { name: 'Exercise Announcement', type: 'update', usage: 12 },
              { name: 'Weather Advisory', type: 'alert', usage: 31 }
            ].map((template, index) => (
              <Card key={index}>
                <CardHeader>
                  <CardTitle className="text-base">{template.name}</CardTitle>
                  <CardDescription>
                    <Badge variant="outline" className="text-xs">{template.type}</Badge>
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="flex justify-between items-center mb-4">
                    <span className="text-sm text-gray-600">Used {template.usage} times</span>
                  </div>
                  <div className="flex gap-2">
                    <Button variant="outline" size="sm" className="flex-1">Use</Button>
                    <Button variant="outline" size="sm" className="flex-1">Edit</Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}