'use client'

import React, { useState, useEffect, useCallback } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Textarea } from '@/components/ui/textarea'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { cn } from '@/lib/utils'
import {
  Users,
  MessageSquare,
  Share2,
  Eye,
  Edit3,
  Clock,
  Bell,
  CheckCircle,
  AlertCircle,
  Send,
  UserPlus,
  Settings,
  Activity,
  Calendar,
  FileText,
  Video,
  Mic,
  Monitor
} from 'lucide-react'
import {
  biaAPI,
  biaQueryKeys,
  type BIAResult,
  type CollaborationSession,
  type SessionParticipant,
  type SessionComment,
  type SessionChange
} from '@/services/bia-api'

interface CollaborativeSessionProps {
  biaResults: BIAResult[]
  sessionId?: string
  readonly?: boolean
}

export function CollaborativeSession({ biaResults, sessionId, readonly = false }: CollaborativeSessionProps) {
  const [activeTab, setActiveTab] = useState('participants')
  const [newComment, setNewComment] = useState('')
  const [inviteEmail, setInviteEmail] = useState('')
  const [isSharing, setIsSharing] = useState(false)
  const queryClient = useQueryClient()

  // Get active collaboration session
  const { data: session, isLoading: sessionLoading } = useQuery({
    queryKey: ['collaboration', 'session', sessionId],
    queryFn: () => biaAPI.getCollaborationSession(sessionId || 'default'),
    refetchInterval: 2000, // Real-time updates every 2 seconds
    enabled: !!sessionId || true
  })

  // Get session participants
  const { data: participants, isLoading: participantsLoading } = useQuery({
    queryKey: ['collaboration', 'participants', sessionId],
    queryFn: () => biaAPI.getSessionParticipants(sessionId || 'default'),
    refetchInterval: 5000
  })

  // Get session comments and activity
  const { data: comments, isLoading: commentsLoading } = useQuery({
    queryKey: ['collaboration', 'comments', sessionId],
    queryFn: () => biaAPI.getSessionComments(sessionId || 'default'),
    refetchInterval: 3000
  })

  // Get real-time changes
  const { data: recentChanges } = useQuery({
    queryKey: ['collaboration', 'changes', sessionId],
    queryFn: () => biaAPI.getSessionChanges(sessionId || 'default'),
    refetchInterval: 2000
  })

  // Add comment mutation
  const addCommentMutation = useMutation({
    mutationFn: (comment: string) => biaAPI.addSessionComment(sessionId || 'default', comment),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['collaboration', 'comments'] })
      setNewComment('')
    }
  })

  // Invite participant mutation
  const inviteParticipantMutation = useMutation({
    mutationFn: (email: string) => biaAPI.inviteParticipant(sessionId || 'default', email),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['collaboration', 'participants'] })
      setInviteEmail('')
    }
  })

  // Start screen sharing mutation
  const startSharingMutation = useMutation({
    mutationFn: () => biaAPI.startScreenSharing(sessionId || 'default'),
    onSuccess: () => setIsSharing(true)
  })

  // Handle new comment submission
  const handleAddComment = useCallback(async () => {
    if (!newComment.trim()) return
    await addCommentMutation.mutateAsync(newComment)
  }, [newComment, addCommentMutation])

  // Handle participant invitation
  const handleInviteParticipant = useCallback(async () => {
    if (!inviteEmail.trim()) return
    await inviteParticipantMutation.mutateAsync(inviteEmail)
  }, [inviteEmail, inviteParticipantMutation])

  // Get participant status color
  const getParticipantStatusColor = (status: string) => {
    switch (status) {
      case 'online': return 'bg-green-500'
      case 'away': return 'bg-yellow-500'
      case 'busy': return 'bg-red-500'
      default: return 'bg-gray-400'
    }
  }

  // Format time ago
  const formatTimeAgo = (timestamp: string) => {
    const now = new Date()
    const time = new Date(timestamp)
    const diffMs = now.getTime() - time.getTime()
    const diffMins = Math.floor(diffMs / (1000 * 60))

    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins}m ago`
    if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`
    return `${Math.floor(diffMins / 1440)}d ago`
  }

  if (sessionLoading) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="animate-pulse space-y-4">
            <div className="h-4 bg-gray-200 rounded w-1/4"></div>
            <div className="h-4 bg-gray-200 rounded w-1/2"></div>
            <div className="h-4 bg-gray-200 rounded w-1/3"></div>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      {/* Session Header */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Users className="h-5 w-5 text-blue-600" />
              <div>
                <CardTitle>Collaborative BIA Session</CardTitle>
                <p className="text-sm text-gray-600 mt-1">
                  {session?.name || 'BIA Analysis Collaboration'}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant="outline" className="flex items-center gap-1">
                <Activity className="h-3 w-3" />
                {participants?.filter(p => p.status === 'online').length || 0} online
              </Badge>
              {!readonly && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => startSharingMutation.mutate()}
                  disabled={isSharing}
                >
                  <Monitor className="h-4 w-4 mr-2" />
                  {isSharing ? 'Sharing...' : 'Share Screen'}
                </Button>
              )}
            </div>
          </div>
        </CardHeader>
      </Card>

      {/* Collaboration Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="participants" className="flex items-center gap-2">
            <Users className="h-4 w-4" />
            Participants
          </TabsTrigger>
          <TabsTrigger value="comments" className="flex items-center gap-2">
            <MessageSquare className="h-4 w-4" />
            Comments
          </TabsTrigger>
          <TabsTrigger value="changes" className="flex items-center gap-2">
            <Activity className="h-4 w-4" />
            Changes
          </TabsTrigger>
          <TabsTrigger value="settings" className="flex items-center gap-2">
            <Settings className="h-4 w-4" />
            Settings
          </TabsTrigger>
        </TabsList>

        {/* Participants Tab */}
        <TabsContent value="participants" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                Session Participants
                {!readonly && (
                  <div className="flex items-center gap-2">
                    <Input
                      placeholder="Email to invite"
                      value={inviteEmail}
                      onChange={(e) => setInviteEmail(e.target.value)}
                      className="w-48"
                    />
                    <Button
                      size="sm"
                      onClick={handleInviteParticipant}
                      disabled={inviteParticipantMutation.isPending}
                    >
                      <UserPlus className="h-4 w-4 mr-2" />
                      Invite
                    </Button>
                  </div>
                )}
              </CardTitle>
            </CardHeader>
            <CardContent>
              {participantsLoading ? (
                <div className="animate-pulse space-y-3">
                  {[1,2,3].map(i => (
                    <div key={i} className="flex items-center gap-3">
                      <div className="h-10 w-10 bg-gray-200 rounded-full"></div>
                      <div className="h-4 bg-gray-200 rounded w-32"></div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="space-y-3">
                  {participants?.map((participant: SessionParticipant) => (
                    <div key={participant.id} className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex items-center gap-3">
                        <div className="relative">
                          <Avatar className="h-10 w-10">
                            <AvatarImage src={participant.avatar} />
                            <AvatarFallback>
                              {participant.name.split(' ').map(n => n[0]).join('')}
                            </AvatarFallback>
                          </Avatar>
                          <div className={cn(
                            "absolute -bottom-1 -right-1 h-3 w-3 rounded-full border-2 border-white",
                            getParticipantStatusColor(participant.status)
                          )}></div>
                        </div>
                        <div>
                          <p className="font-medium">{participant.name}</p>
                          <p className="text-sm text-gray-600">{participant.role}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge variant="outline">
                          {participant.status}
                        </Badge>
                        {participant.permissions.includes('edit') && (
                          <Badge variant="secondary">
                            <Edit3 className="h-3 w-3 mr-1" />
                            Editor
                          </Badge>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Comments Tab */}
        <TabsContent value="comments" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Session Comments</CardTitle>
            </CardHeader>
            <CardContent>
              {!readonly && (
                <div className="mb-6 space-y-3">
                  <Label htmlFor="new-comment">Add Comment</Label>
                  <Textarea
                    id="new-comment"
                    placeholder="Share your thoughts about this BIA analysis..."
                    value={newComment}
                    onChange={(e) => setNewComment(e.target.value)}
                    className="min-h-[80px]"
                  />
                  <Button
                    onClick={handleAddComment}
                    disabled={!newComment.trim() || addCommentMutation.isPending}
                    className="w-full"
                  >
                    <Send className="h-4 w-4 mr-2" />
                    {addCommentMutation.isPending ? 'Posting...' : 'Post Comment'}
                  </Button>
                </div>
              )}

              <div className="space-y-4">
                {commentsLoading ? (
                  <div className="animate-pulse space-y-4">
                    {[1,2,3].map(i => (
                      <div key={i} className="flex gap-3">
                        <div className="h-8 w-8 bg-gray-200 rounded-full"></div>
                        <div className="flex-1 space-y-2">
                          <div className="h-4 bg-gray-200 rounded w-1/4"></div>
                          <div className="h-4 bg-gray-200 rounded w-full"></div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : comments?.length ? (
                  comments.map((comment: SessionComment) => (
                    <div key={comment.id} className="flex gap-3 p-4 border rounded-lg">
                      <Avatar className="h-8 w-8">
                        <AvatarImage src={comment.author.avatar} />
                        <AvatarFallback>
                          {comment.author.name.split(' ').map(n => n[0]).join('')}
                        </AvatarFallback>
                      </Avatar>
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <span className="font-medium">{comment.author.name}</span>
                          <span className="text-sm text-gray-500">
                            {formatTimeAgo(comment.timestamp)}
                          </span>
                        </div>
                        <p className="text-sm">{comment.content}</p>
                        {comment.mentions && comment.mentions.length > 0 && (
                          <div className="mt-2 flex gap-1">
                            {comment.mentions.map(mention => (
                              <Badge key={mention} variant="outline" className="text-xs">
                                @{mention}
                              </Badge>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    <MessageSquare className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                    <p>No comments yet. Start the conversation!</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Changes Tab */}
        <TabsContent value="changes" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Recent Changes</CardTitle>
              <p className="text-sm text-gray-600">
                Real-time updates from all session participants
              </p>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {recentChanges?.map((change: SessionChange) => (
                  <div key={change.id} className="flex items-start gap-3 p-3 border-l-4 border-blue-200 bg-blue-50 rounded-r-lg">
                    <div className="flex-shrink-0">
                      {change.type === 'edit' && <Edit3 className="h-4 w-4 text-blue-600" />}
                      {change.type === 'comment' && <MessageSquare className="h-4 w-4 text-green-600" />}
                      {change.type === 'join' && <UserPlus className="h-4 w-4 text-purple-600" />}
                    </div>
                    <div className="flex-1">
                      <p className="text-sm">
                        <span className="font-medium">{change.author.name}</span>
                        {' '}{change.description}
                      </p>
                      <p className="text-xs text-gray-500 mt-1">
                        {formatTimeAgo(change.timestamp)}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Settings Tab */}
        <TabsContent value="settings" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Session Settings</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Session Duration</Label>
                  <div className="flex items-center gap-2">
                    <Clock className="h-4 w-4 text-gray-500" />
                    <span className="text-sm">
                      {session?.duration ? `${Math.floor(session.duration / 60)}h ${session.duration % 60}m` : 'Unlimited'}
                    </span>
                  </div>
                </div>
                <div className="space-y-2">
                  <Label>Auto-save</Label>
                  <div className="flex items-center gap-2">
                    <CheckCircle className="h-4 w-4 text-green-600" />
                    <span className="text-sm">Every 30 seconds</span>
                  </div>
                </div>
              </div>

              <Alert>
                <Bell className="h-4 w-4" />
                <AlertDescription>
                  All changes are automatically saved and synchronized across all participants.
                  You can export the final BIA analysis when the session is complete.
                </AlertDescription>
              </Alert>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}