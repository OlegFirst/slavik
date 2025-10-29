'use client'

import React, { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import {
  MessageSquare,
  Search,
  Plus,
  Eye,
  ThumbsUp,
  MessageCircle,
  Clock,
  Pin,
  Star,
  Filter,
  TrendingUp
} from 'lucide-react'

interface ForumPost {
  id: string
  title: string
  content: string
  author: {
    name: string
    avatar?: string
    badge: string
  }
  category: string
  tags: string[]
  createdAt: string
  views: number
  likes: number
  replies: number
  isPinned?: boolean
  isAnswered?: boolean
}

const mockPosts: ForumPost[] = [
  {
    id: '1',
    title: 'ISO 22301:2019 Implementation Best Practices',
    content: 'Looking for advice on implementing ISO 22301:2019 in a healthcare environment. What are the key challenges and success factors?',
    author: {
      name: 'Sarah Johnson',
      badge: 'Expert'
    },
    category: 'ISO Standards',
    tags: ['iso22301', 'healthcare', 'implementation'],
    createdAt: '2 hours ago',
    views: 234,
    likes: 18,
    replies: 12,
    isPinned: true,
    isAnswered: true
  },
  {
    id: '2',
    title: 'Crisis Communication During Cyber Incidents',
    content: 'What are effective strategies for maintaining stakeholder communication during cybersecurity incidents?',
    author: {
      name: 'Michael Chen',
      badge: 'Mentor'
    },
    category: 'Crisis Management',
    tags: ['crisis', 'communication', 'cybersecurity'],
    createdAt: '4 hours ago',
    views: 189,
    likes: 15,
    replies: 8,
    isAnswered: false
  },
  {
    id: '3',
    title: 'Business Impact Analysis Templates',
    content: 'Does anyone have good BIA templates for financial services? Looking for something comprehensive but not overwhelming.',
    author: {
      name: 'Emily Rodriguez',
      badge: 'Contributor'
    },
    category: 'Templates & Tools',
    tags: ['bia', 'templates', 'financial'],
    createdAt: '6 hours ago',
    views: 156,
    likes: 22,
    replies: 15
  },
  {
    id: '4',
    title: 'Remote Work BCM Challenges',
    content: 'With hybrid work models becoming permanent, how do we adapt our BCM strategies? Especially for critical functions.',
    author: {
      name: 'David Kim',
      badge: 'Member'
    },
    category: 'Strategy',
    tags: ['remote-work', 'strategy', 'adaptation'],
    createdAt: '8 hours ago',
    views: 298,
    likes: 31,
    replies: 19
  }
]

const categories = [
  'All Categories',
  'ISO Standards',
  'Crisis Management',
  'Risk Assessment',
  'Business Impact Analysis',
  'Templates & Tools',
  'Strategy',
  'Training & Certification',
  'Technology Solutions'
]

export function CommunityForum() {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('All Categories')
  const [sortBy, setSortBy] = useState('recent')

  const filteredPosts = mockPosts.filter(post => {
    const matchesSearch = post.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         post.content.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesCategory = selectedCategory === 'All Categories' || post.category === selectedCategory
    return matchesSearch && matchesCategory
  })

  const sortedPosts = [...filteredPosts].sort((a, b) => {
    switch (sortBy) {
      case 'popular':
        return (b.likes + b.replies) - (a.likes + a.replies)
      case 'views':
        return b.views - a.views
      case 'recent':
      default:
        return new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
    }
  })

  return (
    <div className="space-y-6">
      {/* Forum Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold">Community Forum</h2>
          <p className="text-gray-600">Share knowledge, ask questions, and connect with BCM professionals</p>
        </div>
        <Button className="flex items-center gap-2">
          <Plus className="h-4 w-4" />
          New Discussion
        </Button>
      </div>

      {/* Search and Filters */}
      <div className="flex flex-col md:flex-row gap-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
          <Input
            placeholder="Search discussions..."
            className="pl-10"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>

        <div className="flex gap-2">
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md text-sm"
          >
            {categories.map(category => (
              <option key={category} value={category}>{category}</option>
            ))}
          </select>

          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md text-sm"
          >
            <option value="recent">Recent</option>
            <option value="popular">Popular</option>
            <option value="views">Most Viewed</option>
          </select>
        </div>
      </div>

      {/* Forum Categories Quick Access */}
      <div className="flex flex-wrap gap-2">
        {categories.slice(1, 6).map(category => (
          <Button
            key={category}
            variant={selectedCategory === category ? "default" : "outline"}
            size="sm"
            onClick={() => setSelectedCategory(category)}
          >
            {category}
          </Button>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Main Forum Posts */}
        <div className="lg:col-span-3 space-y-4">
          {sortedPosts.map(post => (
            <Card key={post.id} className="hover:shadow-md transition-shadow">
              <CardContent className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      {post.isPinned && (
                        <Pin className="h-4 w-4 text-blue-600" />
                      )}
                      <h3 className="text-lg font-semibold hover:text-blue-600 cursor-pointer">
                        {post.title}
                      </h3>
                      {post.isAnswered && (
                        <Badge variant="secondary" className="text-green-600">
                          <Star className="h-3 w-3 mr-1" />
                          Answered
                        </Badge>
                      )}
                    </div>

                    <p className="text-gray-600 text-sm mb-3 line-clamp-2">
                      {post.content}
                    </p>

                    <div className="flex items-center gap-4 text-sm text-gray-500">
                      <div className="flex items-center gap-1">
                        <Avatar className="h-6 w-6">
                          <AvatarImage src={post.author.avatar} />
                          <AvatarFallback>
                            {post.author.name.split(' ').map(n => n[0]).join('')}
                          </AvatarFallback>
                        </Avatar>
                        <span>{post.author.name}</span>
                        <Badge variant="outline" className="text-xs ml-1">
                          {post.author.badge}
                        </Badge>
                      </div>

                      <div className="flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        <span>{post.createdAt}</span>
                      </div>

                      <Badge variant="secondary">{post.category}</Badge>
                    </div>

                    <div className="flex items-center gap-2 mt-3">
                      {post.tags.map(tag => (
                        <Badge key={tag} variant="outline" className="text-xs">
                          #{tag}
                        </Badge>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="flex items-center justify-between pt-4 border-t">
                  <div className="flex items-center gap-4 text-sm text-gray-500">
                    <div className="flex items-center gap-1">
                      <Eye className="h-4 w-4" />
                      <span>{post.views}</span>
                    </div>

                    <div className="flex items-center gap-1">
                      <ThumbsUp className="h-4 w-4" />
                      <span>{post.likes}</span>
                    </div>

                    <div className="flex items-center gap-1">
                      <MessageCircle className="h-4 w-4" />
                      <span>{post.replies}</span>
                    </div>
                  </div>

                  <Button variant="ghost" size="sm">
                    View Discussion
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Active Topics */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5" />
                Trending Topics
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {[
                'ISO 22301 Updates',
                'Cyber Resilience',
                'Supply Chain Risk',
                'Remote Work BCM',
                'AI in BCM'
              ].map((topic, index) => (
                <div key={topic} className="flex items-center justify-between">
                  <span className="text-sm">{topic}</span>
                  <Badge variant="outline" className="text-xs">
                    {Math.floor(Math.random() * 50) + 10}
                  </Badge>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Community Guidelines */}
          <Card>
            <CardHeader>
              <CardTitle>Community Guidelines</CardTitle>
            </CardHeader>
            <CardContent className="text-sm text-gray-600 space-y-2">
              <p>• Be respectful and professional</p>
              <p>• Search before posting</p>
              <p>• Use clear, descriptive titles</p>
              <p>• Tag posts appropriately</p>
              <p>• Share knowledge generously</p>
            </CardContent>
          </Card>

          {/* Quick Stats */}
          <Card>
            <CardHeader>
              <CardTitle>Community Stats</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Total Posts</span>
                <span className="font-medium">2,156</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Active Members</span>
                <span className="font-medium">847</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">This Week</span>
                <span className="font-medium">+127 posts</span>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}