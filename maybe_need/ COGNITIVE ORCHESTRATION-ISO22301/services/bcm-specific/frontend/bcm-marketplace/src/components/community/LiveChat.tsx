'use client'

import React, { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  MessageCircle,
  Send,
  Users,
  Settings,
  Mic,
  Video,
  Paperclip,
  Smile,
  Phone,
  MoreVertical,
  UserPlus,
  Search,
  Hash,
  Lock,
  Globe,
  Clock
} from 'lucide-react'

interface ChatMessage {
  id: string
  user: {
    name: string
    avatar?: string
    status: 'online' | 'away' | 'offline'
    role: string
  }
  message: string
  timestamp: string
  type: 'text' | 'file' | 'image' | 'system'
  isOwnMessage?: boolean
}

interface ChatRoom {
  id: string
  name: string
  description: string
  type: 'public' | 'private' | 'direct'
  memberCount: number
  lastActivity: string
  isActive?: boolean
}

const mockMessages: ChatMessage[] = [
  {
    id: '1',
    user: {
      name: 'Sarah Johnson',
      status: 'online',
      role: 'BCM Expert'
    },
    message: 'Has anyone dealt with supply chain disruption planning in the automotive industry?',
    timestamp: '10:32 AM',
    type: 'text'
  },
  {
    id: '2',
    user: {
      name: 'Michael Chen',
      status: 'online',
      role: 'Risk Manager'
    },
    message: 'Yes! We implemented a comprehensive supplier risk assessment framework last year. Happy to share some insights.',
    timestamp: '10:35 AM',
    type: 'text'
  },
  {
    id: '3',
    user: {
      name: 'You',
      status: 'online',
      role: 'Member'
    },
    message: 'That would be incredibly helpful! What were the key challenges you faced?',
    timestamp: '10:37 AM',
    type: 'text',
    isOwnMessage: true
  },
  {
    id: '4',
    user: {
      name: 'Emily Rodriguez',
      status: 'online',
      role: 'Consultant'
    },
    message: 'I\'d love to hear about this too. We\'re starting a similar project next month.',
    timestamp: '10:39 AM',
    type: 'text'
  }
]

const chatRooms: ChatRoom[] = [
  {
    id: '1',
    name: 'General BCM Discussion',
    description: 'Open discussion about all things BCM',
    type: 'public',
    memberCount: 1247,
    lastActivity: '2 min ago',
    isActive: true
  },
  {
    id: '2',
    name: 'ISO 22301 Implementation',
    description: 'Share experiences and ask questions about ISO 22301',
    type: 'public',
    memberCount: 523,
    lastActivity: '5 min ago'
  },
  {
    id: '3',
    name: 'Crisis Management',
    description: 'Real-time crisis management discussions',
    type: 'public',
    memberCount: 389,
    lastActivity: '12 min ago'
  },
  {
    id: '4',
    name: 'Consultants Corner',
    description: 'Private group for BCM consultants',
    type: 'private',
    memberCount: 156,
    lastActivity: '1 hour ago'
  }
]

const onlineUsers = [
  { name: 'Sarah Johnson', role: 'BCM Expert', status: 'online' },
  { name: 'Michael Chen', role: 'Risk Manager', status: 'online' },
  { name: 'Emily Rodriguez', role: 'Consultant', status: 'online' },
  { name: 'David Kim', role: 'Analyst', status: 'away' },
  { name: 'Lisa Zhang', role: 'Director', status: 'online' }
]

export function LiveChat() {
  const [selectedRoom, setSelectedRoom] = useState(chatRooms[0])
  const [message, setMessage] = useState('')
  const [activeTab, setActiveTab] = useState('chat')

  const sendMessage = () => {
    if (message.trim()) {
      // In real implementation, this would send message to server
      console.log('Sending message:', message)
      setMessage('')
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <div className="space-y-6">
      {/* Live Chat Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold">Live Community Chat</h2>
          <p className="text-gray-600">Real-time discussions with BCM professionals worldwide</p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="outline" className="flex items-center gap-1">
            <div className="w-2 h-2 bg-green-500 rounded-full"></div>
            {onlineUsers.filter(u => u.status === 'online').length} online
          </Badge>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 h-[600px]">
        {/* Chat Rooms Sidebar */}
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span className="flex items-center gap-2">
                <Hash className="h-4 w-4" />
                Rooms
              </span>
              <Button size="sm" variant="outline">
                <UserPlus className="h-3 w-3" />
              </Button>
            </CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <div className="space-y-1">
              {chatRooms.map(room => (
                <div
                  key={room.id}
                  onClick={() => setSelectedRoom(room)}
                  className={`flex items-center gap-3 p-3 cursor-pointer hover:bg-gray-50 transition-colors ${
                    selectedRoom.id === room.id ? 'bg-blue-50 border-r-2 border-blue-500' : ''
                  }`}
                >
                  <div className="flex-shrink-0">
                    {room.type === 'private' ? (
                      <Lock className="h-4 w-4 text-gray-500" />
                    ) : (
                      <Globe className="h-4 w-4 text-gray-500" />
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <h4 className="text-sm font-medium truncate">{room.name}</h4>
                      {room.isActive && (
                        <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                      )}
                    </div>
                    <p className="text-xs text-gray-500 truncate">{room.memberCount} members</p>
                    <p className="text-xs text-gray-400">{room.lastActivity}</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Main Chat Area */}
        <Card className="lg:col-span-2 flex flex-col">
          <CardHeader className="flex-shrink-0">
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="flex items-center gap-2">
                  <Hash className="h-5 w-5" />
                  {selectedRoom.name}
                </CardTitle>
                <p className="text-sm text-gray-600">{selectedRoom.description}</p>
              </div>
              <div className="flex items-center gap-2">
                <Button size="sm" variant="outline">
                  <Phone className="h-3 w-3" />
                </Button>
                <Button size="sm" variant="outline">
                  <Video className="h-3 w-3" />
                </Button>
                <Button size="sm" variant="outline">
                  <MoreVertical className="h-3 w-3" />
                </Button>
              </div>
            </div>
          </CardHeader>

          {/* Chat Messages */}
          <CardContent className="flex-1 overflow-y-auto space-y-4 max-h-96">
            {mockMessages.map(msg => (
              <div
                key={msg.id}
                className={`flex gap-3 ${msg.isOwnMessage ? 'flex-row-reverse' : ''}`}
              >
                <Avatar className="h-8 w-8 flex-shrink-0">
                  <AvatarImage src={msg.user.avatar} />
                  <AvatarFallback>
                    {msg.user.name.split(' ').map(n => n[0]).join('')}
                  </AvatarFallback>
                </Avatar>
                <div className={`flex-1 ${msg.isOwnMessage ? 'text-right' : ''}`}>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-sm font-medium">{msg.user.name}</span>
                    <Badge variant="outline" className="text-xs">
                      {msg.user.role}
                    </Badge>
                    <span className="text-xs text-gray-500">{msg.timestamp}</span>
                  </div>
                  <div
                    className={`inline-block p-3 rounded-lg max-w-xs lg:max-w-md ${
                      msg.isOwnMessage
                        ? 'bg-blue-500 text-white'
                        : 'bg-gray-100 text-gray-900'
                    }`}
                  >
                    <p className="text-sm">{msg.message}</p>
                  </div>
                </div>
              </div>
            ))}
          </CardContent>

          {/* Message Input */}
          <div className="flex-shrink-0 border-t p-4">
            <div className="flex items-center gap-2">
              <Button size="sm" variant="outline" className="p-2">
                <Paperclip className="h-4 w-4" />
              </Button>
              <div className="flex-1 relative">
                <Input
                  placeholder={`Message ${selectedRoom.name}`}
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  className="pr-20"
                />
                <div className="absolute right-2 top-1/2 transform -translate-y-1/2 flex items-center gap-1">
                  <Button size="sm" variant="ghost" className="p-1">
                    <Smile className="h-4 w-4" />
                  </Button>
                  <Button size="sm" variant="ghost" className="p-1">
                    <Mic className="h-4 w-4" />
                  </Button>
                </div>
              </div>
              <Button onClick={sendMessage} className="px-3">
                <Send className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </Card>

        {/* Online Users Sidebar */}
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users className="h-4 w-4" />
              Online ({onlineUsers.filter(u => u.status === 'online').length})
            </CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <div className="space-y-1">
              {onlineUsers.map((user, index) => (
                <div key={index} className="flex items-center gap-3 p-3 hover:bg-gray-50 cursor-pointer">
                  <div className="relative">
                    <Avatar className="h-8 w-8">
                      <AvatarFallback>
                        {user.name.split(' ').map(n => n[0]).join('')}
                      </AvatarFallback>
                    </Avatar>
                    <div
                      className={`absolute -bottom-1 -right-1 w-3 h-3 rounded-full border-2 border-white ${
                        user.status === 'online' ? 'bg-green-500' :
                        user.status === 'away' ? 'bg-yellow-500' :
                        'bg-gray-400'
                      }`}
                    />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">{user.name}</p>
                    <p className="text-xs text-gray-500 truncate">{user.role}</p>
                  </div>
                </div>
              ))}
            </div>

            <div className="p-3 border-t">
              <h4 className="text-sm font-medium mb-2">Quick Actions</h4>
              <div className="space-y-2">
                <Button size="sm" variant="outline" className="w-full justify-start">
                  <UserPlus className="h-3 w-3 mr-2" />
                  Invite Members
                </Button>
                <Button size="sm" variant="outline" className="w-full justify-start">
                  <Settings className="h-3 w-3 mr-2" />
                  Room Settings
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Chat Features */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="p-4 text-center">
            <MessageCircle className="h-8 w-8 mx-auto mb-2 text-blue-600" />
            <h3 className="font-medium">Real-time Messaging</h3>
            <p className="text-sm text-gray-600">Instant communication with BCM professionals</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4 text-center">
            <Video className="h-8 w-8 mx-auto mb-2 text-green-600" />
            <h3 className="font-medium">Video Calls</h3>
            <p className="text-sm text-gray-600">Start video conferences directly from chat</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4 text-center">
            <Users className="h-8 w-8 mx-auto mb-2 text-purple-600" />
            <h3 className="font-medium">Expert Network</h3>
            <p className="text-sm text-gray-600">Connect with verified BCM experts instantly</p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}