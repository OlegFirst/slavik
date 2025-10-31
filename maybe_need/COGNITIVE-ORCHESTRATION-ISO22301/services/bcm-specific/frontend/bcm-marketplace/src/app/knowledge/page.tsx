'use client'

import React, { useState } from 'react'
import { AppLayout } from '@/components/layout/AppLayout'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { useKnowledgeArticles } from '@/hooks/api'
import {
  Search,
  BookOpen,
  FileText,
  Users,
  Clock,
  Eye,
  Bookmark,
  ThumbsUp,
  Star,
  Filter,
  TrendingUp,
  Award,
  CheckCircle,
  Lightbulb,
  AlertTriangle,
  Settings,
  Shield,
  Building,
  Loader2
} from 'lucide-react'

interface KnowledgeArticle {
  id: string
  title: string
  summary: string
  category: string
  type: 'best_practice' | 'lesson_learned' | 'procedure' | 'case_study' | 'template_guide' | 'troubleshooting' | 'compliance'
  author: {
    name: string
    avatar?: string
    verified: boolean
    title: string
  }
  publishDate: string
  readTime: number
  viewCount: number
  bookmarkCount: number
  usefulness: number
  tags: string[]
  isoClause?: string
  difficulty: 'beginner' | 'intermediate' | 'advanced'
  featured: boolean
}


const categories = [
  'All Categories',
  'Compliance',
  'Crisis Management',
  'Risk Assessment',
  'Business Continuity',
  'Cybersecurity',
  'Training',
  'Templates'
]

const articleTypes = [
  { value: 'all', label: 'All Types', icon: BookOpen },
  { value: 'best_practice', label: 'Best Practices', icon: Star },
  { value: 'lesson_learned', label: 'Lessons Learned', icon: Lightbulb },
  { value: 'procedure', label: 'Procedures', icon: Settings },
  { value: 'case_study', label: 'Case Studies', icon: Building },
  { value: 'template_guide', label: 'Template Guides', icon: FileText },
  { value: 'troubleshooting', label: 'Troubleshooting', icon: AlertTriangle },
  { value: 'compliance', label: 'Compliance', icon: Shield }
]

export default function KnowledgePage() {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('All Categories')
  const [selectedType, setSelectedType] = useState('all')
  const [selectedDifficulty, setSelectedDifficulty] = useState('all')

  // Use the real API hook
  const { data: articlesData, isLoading, error } = useKnowledgeArticles({
    category: selectedCategory === 'All Categories' ? undefined : selectedCategory,
    type: selectedType === 'all' ? undefined : selectedType,
    difficulty: selectedDifficulty === 'all' ? undefined : selectedDifficulty,
    search: searchQuery || undefined
  })

  const articles = articlesData?.data || []

  // Filter articles locally for immediate feedback
  const filteredArticles = articles.filter(article => {
    const matchesSearch = !searchQuery ||
      article.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      article.summary.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (article.tags && article.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase())))

    const matchesCategory = selectedCategory === 'All Categories' || article.category === selectedCategory
    const matchesType = selectedType === 'all' || article.type === selectedType
    const matchesDifficulty = selectedDifficulty === 'all' || article.difficulty === selectedDifficulty

    return matchesSearch && matchesCategory && matchesType && matchesDifficulty
  })

  const getTypeIcon = (type: string) => {
    const typeObj = articleTypes.find(t => t.value === type)
    return typeObj ? typeObj.icon : BookOpen
  }

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'best_practice': return 'bg-green-100 text-green-600'
      case 'lesson_learned': return 'bg-yellow-100 text-yellow-600'
      case 'procedure': return 'bg-blue-100 text-blue-600'
      case 'case_study': return 'bg-purple-100 text-purple-600'
      case 'template_guide': return 'bg-indigo-100 text-indigo-600'
      case 'troubleshooting': return 'bg-red-100 text-red-600'
      case 'compliance': return 'bg-gray-100 text-gray-600'
      default: return 'bg-gray-100 text-gray-600'
    }
  }

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'beginner': return 'bg-green-100 text-green-800'
      case 'intermediate': return 'bg-yellow-100 text-yellow-800'
      case 'advanced': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  // Handle loading state
  if (isLoading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center py-20">
          <div className="text-center">
            <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4" />
            <p className="text-gray-600">Loading knowledge articles...</p>
          </div>
        </div>
      </AppLayout>
    )
  }

  // Handle error state
  if (error) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center py-20">
          <div className="text-center">
            <p className="text-red-600 mb-4">Error loading knowledge articles</p>
            <Button onClick={() => window.location.reload()}>Try Again</Button>
          </div>
        </div>
      </AppLayout>
    )
  }

  return (
    <AppLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <h1 className="text-3xl font-bold">Knowledge Base</h1>
            <p className="text-gray-600">Expert insights, best practices, and comprehensive guides</p>
          </div>
          <Button className="flex items-center gap-2">
            <FileText className="h-4 w-4" />
            Contribute Article
          </Button>
        </div>

        {/* Search and Filters */}
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
            <Input
              placeholder="Search articles, guides, best practices..."
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
              {articleTypes.map(type => (
                <option key={type.value} value={type.value}>{type.label}</option>
              ))}
            </select>

            <select
              value={selectedDifficulty}
              onChange={(e) => setSelectedDifficulty(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md text-sm"
            >
              <option value="all">All Levels</option>
              <option value="beginner">Beginner</option>
              <option value="intermediate">Intermediate</option>
              <option value="advanced">Advanced</option>
            </select>
          </div>
        </div>

        {/* Featured Articles */}
        <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-6">
          <div className="flex items-center gap-2 mb-4">
            <TrendingUp className="h-5 w-5 text-blue-600" />
            <h2 className="text-xl font-semibold">Featured Articles</h2>
          </div>
          <div className="grid md:grid-cols-3 gap-4">
            {articles.filter(a => a.featured).slice(0, 3).map(article => {
              const TypeIcon = getTypeIcon(article.type)
              return (
                <Card key={article.id} className="hover:shadow-md transition-shadow">
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between mb-3">
                      <div className={`p-2 rounded-lg ${getTypeColor(article.type)}`}>
                        <TypeIcon className="h-4 w-4" />
                      </div>
                      <div className="flex items-center gap-1 text-sm">
                        <Star className="h-3 w-3 fill-yellow-400 text-yellow-400" />
                        <span>{article.usefulness}</span>
                      </div>
                    </div>
                    <h3 className="font-semibold text-sm mb-2 line-clamp-2">{article.title}</h3>
                    <div className="flex items-center gap-2 text-xs text-gray-600">
                      <Clock className="h-3 w-3" />
                      <span>{article.readTime} min read</span>
                      <span>•</span>
                      <Eye className="h-3 w-3" />
                      <span>{article.viewCount}</span>
                    </div>
                  </CardContent>
                </Card>
              )
            })}
          </div>
        </div>

        {/* Article Types Quick Filter */}
        <div className="flex flex-wrap gap-2">
          {articleTypes.map(type => {
            const Icon = type.icon
            const isActive = selectedType === type.value
            return (
              <Button
                key={type.value}
                variant={isActive ? 'default' : 'outline'}
                size="sm"
                onClick={() => setSelectedType(type.value)}
                className="flex items-center gap-2"
              >
                <Icon className="h-3 w-3" />
                {type.label}
              </Button>
            )
          })}
        </div>

        {/* Articles Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {filteredArticles.map(article => {
            const TypeIcon = getTypeIcon(article.type)

            return (
              <Card key={article.id} className="hover:shadow-lg transition-shadow">
                <CardContent className="p-6">
                  {/* Article Header */}
                  <div className="flex items-start justify-between mb-4">
                    <div className={`p-3 rounded-lg ${getTypeColor(article.type)}`}>
                      <TypeIcon className="h-6 w-6" />
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge className={getDifficultyColor(article.difficulty)} variant="secondary">
                        {article.difficulty}
                      </Badge>
                      {article.isoClause && (
                        <Badge variant="outline">
                          ISO {article.isoClause}
                        </Badge>
                      )}
                    </div>
                  </div>

                  {/* Title and Summary */}
                  <div className="mb-4">
                    <h3 className="font-semibold text-lg mb-2 line-clamp-2">{article.title}</h3>
                    <p className="text-gray-600 text-sm line-clamp-3">{article.summary}</p>
                  </div>

                  {/* Author */}
                  <div className="flex items-center gap-3 mb-4">
                    <Avatar className="h-8 w-8">
                      <AvatarImage src={article.author.avatar} alt={article.author.name} />
                      <AvatarFallback className="text-xs">
                        {article.author.name.split(' ').map(n => n[0]).join('')}
                      </AvatarFallback>
                    </Avatar>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-1">
                        <span className="text-sm font-medium truncate">{article.author.name}</span>
                        {article.author.verified && (
                          <CheckCircle className="h-3 w-3 text-blue-500" />
                        )}
                      </div>
                      <div className="text-xs text-gray-500 truncate">{article.author.title}</div>
                    </div>
                  </div>

                  {/* Stats */}
                  <div className="flex items-center justify-between mb-4 text-sm text-gray-600">
                    <div className="flex items-center gap-4">
                      <div className="flex items-center gap-1">
                        <Clock className="h-4 w-4" />
                        <span>{article.readTime} min</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <Eye className="h-4 w-4" />
                        <span>{article.viewCount.toLocaleString()}</span>
                      </div>
                    </div>
                    <div className="flex items-center gap-1">
                      <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                      <span>{article.usefulness}</span>
                    </div>
                  </div>

                  {/* Tags */}
                  <div className="mb-4">
                    <div className="flex flex-wrap gap-1">
                      {article.tags.slice(0, 3).map(tag => (
                        <Badge key={tag} variant="secondary" className="text-xs">
                          {tag}
                        </Badge>
                      ))}
                      {article.tags.length > 3 && (
                        <Badge variant="outline" className="text-xs">
                          +{article.tags.length - 3}
                        </Badge>
                      )}
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex gap-2">
                    <Button className="flex-1" size="sm">
                      <BookOpen className="h-3 w-3 mr-1" />
                      Read Article
                    </Button>
                    <Button variant="outline" size="sm">
                      <Bookmark className="h-3 w-3" />
                    </Button>
                    <Button variant="outline" size="sm">
                      <ThumbsUp className="h-3 w-3" />
                    </Button>
                  </div>

                  {/* Published Date */}
                  <div className="mt-3 text-xs text-gray-500">
                    Published {article.publishDate}
                  </div>
                </CardContent>
              </Card>
            )
          })}
        </div>

        {/* Load More */}
        <div className="text-center py-8">
          <Button variant="outline" size="lg">
            Load More Articles
          </Button>
        </div>

        {/* Knowledge Stats */}
        <div className="bg-gray-50 rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-4">Knowledge Base Statistics</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { label: 'Total Articles', value: '1,247', icon: BookOpen },
              { label: 'Expert Contributors', value: '156', icon: Users },
              { label: 'Total Views', value: '2.3M', icon: Eye },
              { label: 'Avg. Rating', value: '4.7/5', icon: Star }
            ].map(stat => (
              <div key={stat.label} className="bg-white rounded-lg p-4 text-center">
                <stat.icon className="h-8 w-8 mx-auto mb-2 text-blue-600" />
                <div className="text-2xl font-bold">{stat.value}</div>
                <div className="text-sm text-gray-600">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </AppLayout>
  )
}