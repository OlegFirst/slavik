'use client'

import React, { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  BookOpen,
  Search,
  Download,
  Eye,
  Star,
  Clock,
  User,
  FileText,
  Video,
  Link as LinkIcon,
  Filter,
  BookmarkPlus,
  Share2
} from 'lucide-react'

interface KnowledgeArticle {
  id: string
  title: string
  summary: string
  content: string
  type: 'article' | 'template' | 'video' | 'guide'
  author: {
    name: string
    avatar?: string
    title: string
  }
  category: string
  tags: string[]
  difficulty: 'Beginner' | 'Intermediate' | 'Advanced'
  readTime: number
  views: number
  rating: number
  downloads?: number
  createdAt: string
  updatedAt: string
}

const mockArticles: KnowledgeArticle[] = [
  {
    id: '1',
    title: 'Complete Guide to ISO 22301:2019 Implementation',
    summary: 'A comprehensive step-by-step guide to implementing ISO 22301:2019 standard in your organization.',
    content: 'Full implementation guide...',
    type: 'guide',
    author: {
      name: 'Dr. Sarah Martinez',
      title: 'BCM Consultant & ISO Expert'
    },
    category: 'ISO Standards',
    tags: ['iso22301', 'implementation', 'compliance'],
    difficulty: 'Intermediate',
    readTime: 25,
    views: 3247,
    rating: 4.8,
    createdAt: '2024-01-15',
    updatedAt: '2024-01-20'
  },
  {
    id: '2',
    title: 'Business Impact Analysis Template Package',
    summary: 'Ready-to-use BIA templates for different industries including healthcare, finance, and manufacturing.',
    content: 'Template package...',
    type: 'template',
    author: {
      name: 'Michael Thompson',
      title: 'Senior Risk Analyst'
    },
    category: 'Templates',
    tags: ['bia', 'templates', 'risk-assessment'],
    difficulty: 'Beginner',
    readTime: 10,
    views: 1892,
    rating: 4.6,
    downloads: 847,
    createdAt: '2024-01-10',
    updatedAt: '2024-01-18'
  },
  {
    id: '3',
    title: 'Crisis Communication Strategies (Video Series)',
    summary: 'Learn effective crisis communication techniques through real-world case studies and expert interviews.',
    content: 'Video content...',
    type: 'video',
    author: {
      name: 'Jennifer Liu',
      title: 'Crisis Communication Expert'
    },
    category: 'Crisis Management',
    tags: ['crisis', 'communication', 'stakeholders'],
    difficulty: 'Intermediate',
    readTime: 45,
    views: 2156,
    rating: 4.9,
    createdAt: '2024-01-08',
    updatedAt: '2024-01-16'
  },
  {
    id: '4',
    title: 'BCM Metrics and KPIs Framework',
    summary: 'Establish meaningful metrics to measure the effectiveness of your business continuity program.',
    content: 'Metrics framework...',
    type: 'article',
    author: {
      name: 'Robert Chen',
      title: 'BCM Program Manager'
    },
    category: 'Strategy',
    tags: ['metrics', 'kpis', 'measurement'],
    difficulty: 'Advanced',
    readTime: 18,
    views: 1634,
    rating: 4.7,
    createdAt: '2024-01-05',
    updatedAt: '2024-01-14'
  }
]

const categories = [
  'All Categories',
  'ISO Standards',
  'Crisis Management',
  'Risk Assessment',
  'Templates',
  'Strategy',
  'Compliance',
  'Technology',
  'Case Studies'
]

export function KnowledgeHub() {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('All Categories')
  const [selectedType, setSelectedType] = useState('all')
  const [selectedDifficulty, setSelectedDifficulty] = useState('all')

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'article': return <FileText className="h-4 w-4" />
      case 'template': return <Download className="h-4 w-4" />
      case 'video': return <Video className="h-4 w-4" />
      case 'guide': return <BookOpen className="h-4 w-4" />
      default: return <FileText className="h-4 w-4" />
    }
  }

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'Beginner': return 'bg-green-100 text-green-800'
      case 'Intermediate': return 'bg-yellow-100 text-yellow-800'
      case 'Advanced': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const filteredArticles = mockArticles.filter(article => {
    const matchesSearch = article.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         article.summary.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesCategory = selectedCategory === 'All Categories' || article.category === selectedCategory
    const matchesType = selectedType === 'all' || article.type === selectedType
    const matchesDifficulty = selectedDifficulty === 'all' || article.difficulty === selectedDifficulty

    return matchesSearch && matchesCategory && matchesType && matchesDifficulty
  })

  return (
    <div className="space-y-6">
      {/* Knowledge Hub Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold">Knowledge Hub</h2>
          <p className="text-gray-600">Access curated BCM knowledge, templates, and resources</p>
        </div>
        <Button className="flex items-center gap-2">
          <BookmarkPlus className="h-4 w-4" />
          Contribute Knowledge
        </Button>
      </div>

      {/* Search and Filters */}
      <div className="flex flex-col md:flex-row gap-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
          <Input
            placeholder="Search knowledge base..."
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
            value={selectedType}
            onChange={(e) => setSelectedType(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md text-sm"
          >
            <option value="all">All Types</option>
            <option value="article">Articles</option>
            <option value="template">Templates</option>
            <option value="video">Videos</option>
            <option value="guide">Guides</option>
          </select>

          <select
            value={selectedDifficulty}
            onChange={(e) => setSelectedDifficulty(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md text-sm"
          >
            <option value="all">All Levels</option>
            <option value="Beginner">Beginner</option>
            <option value="Intermediate">Intermediate</option>
            <option value="Advanced">Advanced</option>
          </select>
        </div>
      </div>

      {/* Content Tabs */}
      <Tabs defaultValue="browse" className="w-full">
        <TabsList>
          <TabsTrigger value="browse">Browse All</TabsTrigger>
          <TabsTrigger value="popular">Most Popular</TabsTrigger>
          <TabsTrigger value="recent">Recently Added</TabsTrigger>
          <TabsTrigger value="bookmarked">My Bookmarks</TabsTrigger>
        </TabsList>

        <TabsContent value="browse" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Main Content */}
            <div className="lg:col-span-2 space-y-4">
              {filteredArticles.map(article => (
                <Card key={article.id} className="hover:shadow-md transition-shadow">
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          {getTypeIcon(article.type)}
                          <h3 className="text-lg font-semibold hover:text-blue-600 cursor-pointer">
                            {article.title}
                          </h3>
                          <Badge className={`text-xs ${getDifficultyColor(article.difficulty)}`}>
                            {article.difficulty}
                          </Badge>
                        </div>

                        <p className="text-gray-600 text-sm mb-3 line-clamp-2">
                          {article.summary}
                        </p>

                        <div className="flex items-center gap-4 text-sm text-gray-500 mb-3">
                          <div className="flex items-center gap-1">
                            <Avatar className="h-6 w-6">
                              <AvatarImage src={article.author.avatar} />
                              <AvatarFallback>
                                {article.author.name.split(' ').map(n => n[0]).join('')}
                              </AvatarFallback>
                            </Avatar>
                            <span>{article.author.name}</span>
                          </div>

                          <div className="flex items-center gap-1">
                            <Clock className="h-3 w-3" />
                            <span>{article.readTime} min read</span>
                          </div>

                          <div className="flex items-center gap-1">
                            <Eye className="h-3 w-3" />
                            <span>{article.views.toLocaleString()} views</span>
                          </div>

                          <div className="flex items-center gap-1">
                            <Star className="h-3 w-3 fill-yellow-400 text-yellow-400" />
                            <span>{article.rating}</span>
                          </div>
                        </div>

                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <Badge variant="secondary">{article.category}</Badge>
                            {article.tags.slice(0, 2).map(tag => (
                              <Badge key={tag} variant="outline" className="text-xs">
                                #{tag}
                              </Badge>
                            ))}
                          </div>

                          <div className="flex items-center gap-2">
                            {article.type === 'template' && (
                              <Button size="sm" variant="outline">
                                <Download className="h-3 w-3 mr-1" />
                                Download
                              </Button>
                            )}
                            <Button size="sm" variant="ghost">
                              <Share2 className="h-3 w-3 mr-1" />
                              Share
                            </Button>
                            <Button size="sm">
                              Read More
                            </Button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* Sidebar */}
            <div className="space-y-6">
              {/* Popular Downloads */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Download className="h-5 w-5" />
                    Popular Downloads
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {[
                    { name: 'BIA Template Pack', downloads: 2847 },
                    { name: 'Crisis Plan Template', downloads: 1923 },
                    { name: 'Risk Register Template', downloads: 1654 },
                    { name: 'BCM Policy Template', downloads: 1432 }
                  ].map((item, index) => (
                    <div key={index} className="flex items-center justify-between">
                      <span className="text-sm truncate">{item.name}</span>
                      <div className="flex items-center gap-1 text-xs text-gray-500">
                        <Download className="h-3 w-3" />
                        {item.downloads}
                      </div>
                    </div>
                  ))}
                </CardContent>
              </Card>

              {/* Featured Contributors */}
              <Card>
                <CardHeader>
                  <CardTitle>Featured Contributors</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {[
                    { name: 'Dr. Sarah Martinez', articles: 23, rating: 4.8 },
                    { name: 'Michael Thompson', articles: 18, rating: 4.7 },
                    { name: 'Jennifer Liu', articles: 15, rating: 4.9 }
                  ].map((contributor, index) => (
                    <div key={index} className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Avatar className="h-8 w-8">
                          <AvatarFallback>
                            {contributor.name.split(' ').map(n => n[0]).join('')}
                          </AvatarFallback>
                        </Avatar>
                        <div>
                          <p className="text-sm font-medium">{contributor.name}</p>
                          <p className="text-xs text-gray-500">{contributor.articles} articles</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-1">
                        <Star className="h-3 w-3 fill-yellow-400 text-yellow-400" />
                        <span className="text-xs">{contributor.rating}</span>
                      </div>
                    </div>
                  ))}
                </CardContent>
              </Card>

              {/* Knowledge Categories */}
              <Card>
                <CardHeader>
                  <CardTitle>Browse by Category</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  {categories.slice(1).map(category => (
                    <Button
                      key={category}
                      variant="ghost"
                      size="sm"
                      className="w-full justify-start"
                      onClick={() => setSelectedCategory(category)}
                    >
                      {category}
                    </Button>
                  ))}
                </CardContent>
              </Card>
            </div>
          </div>
        </TabsContent>

        <TabsContent value="popular">
          <div className="text-center py-8">
            <BookOpen className="h-12 w-12 mx-auto text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Most Popular Content</h3>
            <p className="text-gray-600">Content sorted by views and ratings will appear here.</p>
          </div>
        </TabsContent>

        <TabsContent value="recent">
          <div className="text-center py-8">
            <Clock className="h-12 w-12 mx-auto text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Recently Added</h3>
            <p className="text-gray-600">Latest knowledge base additions will appear here.</p>
          </div>
        </TabsContent>

        <TabsContent value="bookmarked">
          <div className="text-center py-8">
            <BookmarkPlus className="h-12 w-12 mx-auto text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Your Bookmarks</h3>
            <p className="text-gray-600">Your saved articles and resources will appear here.</p>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}