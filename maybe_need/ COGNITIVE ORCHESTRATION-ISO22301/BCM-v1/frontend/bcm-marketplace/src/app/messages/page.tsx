'use client'

import React, { useState } from 'react'
import { AppLayout } from '@/components/layout/AppLayout'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import {
  Search,
  Send,
  Paperclip,
  Phone,
  Video,
  MoreVertical,
  Star,
  Circle,
  Archive,
  Trash2,
  Flag,
  Users,
  MessageCircle,
  Clock,
  CheckCheck,
  Check,
  Plus
} from 'lucide-react'

interface Message {
  id: string
  content: string
  senderId: string
  timestamp: string
  isRead: boolean
  attachments?: {
    name: string
    url: string
    type: string
  }[]
}

interface Conversation {
  id: string
  participant: {
    id: string
    name: string
    avatar?: string
    title: string
    company: string
    isOnline: boolean
    lastSeen: string
    verified: boolean
    rating: number
  }
  lastMessage: Message
  unreadCount: number
  isPinned: boolean
  isArchived: boolean
  projectTitle?: string
  projectId?: string
  messages: Message[]
}

const mockConversations: Conversation[] = [
  {
    id: '1',
    participant: {
      id: 'client_1',
      name: 'Sarah Johnson',
      title: 'Risk Manager',
      company: 'FinTech Solutions Inc.',
      isOnline: true,
      lastSeen: 'Active now',
      verified: true,
      rating: 4.8
    },
    lastMessage: {
      id: 'msg_1',
      content: 'Thanks for the detailed proposal. When would you be available for a call to discuss the timeline?',
      senderId: 'client_1',
      timestamp: '2024-01-16T10:30:00Z',
      isRead: false
    },
    unreadCount: 2,
    isPinned: true,
    isArchived: false,
    projectTitle: 'Financial Services BCM Gap Analysis',
    projectId: 'proj_1',
    messages: [
      {
        id: 'msg_0',
        content: 'Hi! I reviewed your BCM consulting profile and I\'m impressed with your experience in financial services. We have a gap analysis project that might be perfect for your expertise.',
        senderId: 'client_1',
        timestamp: '2024-01-16T09:00:00Z',
        isRead: true
      },
      {
        id: 'msg_1',
        content: 'Thanks for the detailed proposal. When would you be available for a call to discuss the timeline?',
        senderId: 'client_1',
        timestamp: '2024-01-16T10:30:00Z',
        isRead: false
      }
    ]
  },
  {
    id: '2',
    participant: {
      id: 'client_2',
      name: 'Dr. Michael Chen',
      title: 'COO',
      company: 'Regional Medical Center',
      isOnline: false,
      lastSeen: '2 hours ago',
      verified: true,
      rating: 4.9
    },
    lastMessage: {
      id: 'msg_2',
      content: 'Perfect! The training materials look comprehensive. Let\'s schedule the delivery for next month.',
      senderId: 'client_2',
      timestamp: '2024-01-16T08:15:00Z',
      isRead: true
    },
    unreadCount: 0,
    isPinned: false,
    isArchived: false,
    projectTitle: 'Healthcare Crisis Management Training',
    projectId: 'proj_2',
    messages: [
      {
        id: 'msg_2',
        content: 'Perfect! The training materials look comprehensive. Let\'s schedule the delivery for next month.',
        senderId: 'client_2',
        timestamp: '2024-01-16T08:15:00Z',
        isRead: true
      }
    ]
  },
  {
    id: '3',
    participant: {
      id: 'specialist_1',
      name: 'Jennifer Liu',
      title: 'Senior BCM Consultant',
      company: 'BCM Experts LLC',
      isOnline: true,
      lastSeen: 'Active now',
      verified: true,
      rating: 4.7
    },
    lastMessage: {
      id: 'msg_3',
      content: 'I have experience with similar manufacturing assessments. Would love to collaborate on this project.',
      senderId: 'specialist_1',
      timestamp: '2024-01-15T16:45:00Z',
      isRead: true
    },
    unreadCount: 0,
    isPinned: false,
    isArchived: false,
    projectTitle: 'Supply Chain Resilience Assessment',
    projectId: 'proj_3',
    messages: [
      {
        id: 'msg_3',
        content: 'I have experience with similar manufacturing assessments. Would love to collaborate on this project.',
        senderId: 'specialist_1',
        timestamp: '2024-01-15T16:45:00Z',
        isRead: true
      }
    ]
  }
]

export default function MessagesPage() {
  const [selectedConversation, setSelectedConversation] = useState(mockConversations[0])
  const [newMessage, setNewMessage] = useState('')
  const [searchQuery, setSearchQuery] = useState('')

  const currentUserId = 'current_user' // In real app, this would come from auth context

  const sendMessage = () => {
    if (newMessage.trim() && selectedConversation) {
      const message: Message = {
        id: `msg_${Date.now()}`,
        content: newMessage,
        senderId: currentUserId,
        timestamp: new Date().toISOString(),
        isRead: true
      }

      // In real app, this would call API
      console.log('Sending message:', message)
      setNewMessage('')
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp)
    const now = new Date()
    const diffInHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60)

    if (diffInHours < 1) {
      const minutes = Math.floor(diffInHours * 60)
      return minutes < 1 ? 'Just now' : `${minutes}m ago`
    } else if (diffInHours < 24) {
      return `${Math.floor(diffInHours)}h ago`
    } else {
      return date.toLocaleDateString()
    }
  }

  const filteredConversations = mockConversations.filter(conv =>
    conv.participant.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    conv.participant.company.toLowerCase().includes(searchQuery.toLowerCase()) ||
    (conv.projectTitle && conv.projectTitle.toLowerCase().includes(searchQuery.toLowerCase()))
  )

  return (
    <AppLayout>
      <div className="h-[calc(100vh-8rem)] flex">
        {/* Conversations Sidebar */}
        <div className="w-1/3 border-r border-gray-200 flex flex-col">
          {/* Sidebar Header */}
          <div className="p-4 border-b border-gray-200">
            <div className="flex items-center justify-between mb-4">
              <h1 className="text-2xl font-bold">Messages</h1>
              <Button size="sm">
                <Plus className="h-4 w-4" />
              </Button>
            </div>

            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
              <Input
                placeholder="Search conversations..."
                className="pl-10"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
          </div>

          {/* Conversations List */}
          <div className="flex-1 overflow-y-auto">
            {filteredConversations.map(conversation => (
              <div
                key={conversation.id}
                onClick={() => setSelectedConversation(conversation)}
                className={`p-4 border-b border-gray-100 cursor-pointer hover:bg-gray-50 transition-colors ${
                  selectedConversation?.id === conversation.id ? 'bg-blue-50 border-r-2 border-r-blue-500' : ''
                }`}
              >
                <div className="flex items-start space-x-3">
                  <div className="relative">
                    <Avatar className="h-10 w-10">
                      <AvatarImage src={conversation.participant.avatar} />
                      <AvatarFallback>
                        {conversation.participant.name.split(' ').map(n => n[0]).join('')}
                      </AvatarFallback>
                    </Avatar>
                    {conversation.participant.isOnline && (
                      <div className="absolute -bottom-1 -right-1 w-3 h-3 bg-green-500 rounded-full border-2 border-white"></div>
                    )}
                  </div>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <h3 className="font-semibold text-gray-900 truncate">
                          {conversation.participant.name}
                        </h3>
                        {conversation.participant.verified && (
                          <Badge variant="outline" className="text-blue-600 border-blue-600 text-xs px-1 py-0">
                            ✓
                          </Badge>
                        )}
                      </div>
                      <div className="flex items-center gap-1">
                        {conversation.unreadCount > 0 && (
                          <Badge className="bg-blue-500 text-white text-xs min-w-5 h-5 flex items-center justify-center rounded-full">
                            {conversation.unreadCount}
                          </Badge>
                        )}
                        <span className="text-xs text-gray-500">
                          {formatTimestamp(conversation.lastMessage.timestamp)}
                        </span>
                      </div>
                    </div>

                    <div className="flex items-center gap-1 text-sm text-gray-600 mb-1">
                      <span>{conversation.participant.company}</span>
                      <Star className="h-3 w-3 fill-yellow-400 text-yellow-400" />
                      <span>{conversation.participant.rating}</span>
                    </div>

                    {conversation.projectTitle && (
                      <div className="text-xs text-blue-600 mb-1 truncate">
                        Project: {conversation.projectTitle}
                      </div>
                    )}

                    <p className="text-sm text-gray-600 truncate">
                      {conversation.lastMessage.senderId === currentUserId ? 'You: ' : ''}
                      {conversation.lastMessage.content}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Chat Area */}
        {selectedConversation ? (
          <div className="flex-1 flex flex-col">
            {/* Chat Header */}
            <div className="p-4 border-b border-gray-200 bg-white">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="relative">
                    <Avatar className="h-10 w-10">
                      <AvatarImage src={selectedConversation.participant.avatar} />
                      <AvatarFallback>
                        {selectedConversation.participant.name.split(' ').map(n => n[0]).join('')}
                      </AvatarFallback>
                    </Avatar>
                    {selectedConversation.participant.isOnline && (
                      <div className="absolute -bottom-1 -right-1 w-3 h-3 bg-green-500 rounded-full border-2 border-white"></div>
                    )}
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <h2 className="font-semibold">{selectedConversation.participant.name}</h2>
                      {selectedConversation.participant.verified && (
                        <Badge variant="outline" className="text-blue-600 border-blue-600 text-xs">
                          Verified
                        </Badge>
                      )}
                    </div>
                    <div className="flex items-center gap-2 text-sm text-gray-600">
                      <span>{selectedConversation.participant.title}</span>
                      <span>•</span>
                      <span>{selectedConversation.participant.company}</span>
                      <span>•</span>
                      <div className="flex items-center gap-1">
                        <Circle className={`h-2 w-2 ${selectedConversation.participant.isOnline ? 'text-green-500 fill-green-500' : 'text-gray-400 fill-gray-400'}`} />
                        <span>{selectedConversation.participant.lastSeen}</span>
                      </div>
                    </div>
                    {selectedConversation.projectTitle && (
                      <div className="text-xs text-blue-600 mt-1">
                        Project: {selectedConversation.projectTitle}
                      </div>
                    )}
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <Button variant="outline" size="sm">
                    <Phone className="h-4 w-4" />
                  </Button>
                  <Button variant="outline" size="sm">
                    <Video className="h-4 w-4" />
                  </Button>
                  <Button variant="outline" size="sm">
                    <MoreVertical className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {selectedConversation.messages.map(message => (
                <div
                  key={message.id}
                  className={`flex gap-3 ${message.senderId === currentUserId ? 'flex-row-reverse' : ''}`}
                >
                  {message.senderId !== currentUserId && (
                    <Avatar className="h-8 w-8 flex-shrink-0">
                      <AvatarImage src={selectedConversation.participant.avatar} />
                      <AvatarFallback>
                        {selectedConversation.participant.name.split(' ').map(n => n[0]).join('')}
                      </AvatarFallback>
                    </Avatar>
                  )}

                  <div className={`flex-1 max-w-xs lg:max-w-md ${message.senderId === currentUserId ? 'text-right' : ''}`}>
                    <div
                      className={`inline-block p-3 rounded-lg ${
                        message.senderId === currentUserId
                          ? 'bg-blue-500 text-white'
                          : 'bg-gray-100 text-gray-900'
                      }`}
                    >
                      <p className="text-sm">{message.content}</p>
                      {message.attachments && message.attachments.length > 0 && (
                        <div className="mt-2 space-y-1">
                          {message.attachments.map((attachment, index) => (
                            <div key={index} className="flex items-center gap-2 p-2 bg-white bg-opacity-20 rounded">
                              <Paperclip className="h-3 w-3" />
                              <span className="text-xs">{attachment.name}</span>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                    <div className={`flex items-center gap-1 mt-1 text-xs text-gray-500 ${
                      message.senderId === currentUserId ? 'justify-end' : ''
                    }`}>
                      <span>{formatTimestamp(message.timestamp)}</span>
                      {message.senderId === currentUserId && (
                        <div className="flex items-center">
                          {message.isRead ? (
                            <CheckCheck className="h-3 w-3 text-blue-500" />
                          ) : (
                            <Check className="h-3 w-3" />
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Message Input */}
            <div className="p-4 border-t border-gray-200 bg-white">
              <div className="flex items-end gap-2">
                <Button variant="outline" size="sm" className="mb-1">
                  <Paperclip className="h-4 w-4" />
                </Button>
                <div className="flex-1">
                  <Textarea
                    placeholder={`Message ${selectedConversation.participant.name}...`}
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    className="min-h-[40px] max-h-32 resize-none"
                    rows={1}
                  />
                </div>
                <Button onClick={sendMessage} disabled={!newMessage.trim()}>
                  <Send className="h-4 w-4" />
                </Button>
              </div>
              <div className="flex items-center justify-between mt-2 text-xs text-gray-500">
                <span>Press Enter to send, Shift+Enter for new line</span>
                <span>{selectedConversation.participant.isOnline ? 'Online' : `Last seen ${selectedConversation.participant.lastSeen}`}</span>
              </div>
            </div>
          </div>
        ) : (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center">
              <MessageCircle className="h-12 w-12 mx-auto text-gray-300 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">Select a conversation</h3>
              <p className="text-gray-600">Choose a conversation from the sidebar to start messaging</p>
            </div>
          </div>
        )}
      </div>
    </AppLayout>
  )
}