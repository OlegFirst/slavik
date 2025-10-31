'use client'

import React, { useState } from 'react'
import { AppLayout } from '@/components/layout/AppLayout'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { useSolutions } from '@/hooks/api'
import {
  Search,
  Filter,
  Download,
  Star,
  Users,
  FileText,
  Shield,
  Building,
  Clock,
  DollarSign,
  Eye,
  Heart,
  CheckCircle,
  Zap,
  BookOpen,
  Settings,
  TrendingUp,
  Loader2
} from 'lucide-react'

interface Solution {
  id: string
  title: string
  description: string
  category: string
  type: 'template' | 'tool' | 'framework' | 'checklist' | 'policy'
  author: {
    name: string
    avatar?: string
    verified: boolean
    company: string
  }
  price: number
  currency: string
  rating: number
  reviewCount: number
  downloadCount: number
  tags: string[]
  preview: string
  format: string[]
  lastUpdated: string
  compliance: string[]
  industries: string[]
  featured: boolean
}


const categories = [
  'All Categories',
  'Business Continuity Planning',
  'Crisis Management',
  'Risk Assessment',
  'Incident Management',
  'Compliance',
  'Emergency Response',
  'Training Materials'
]

const solutionTypes = [
  'All Types',
  'template',
  'tool',
  'framework',
  'checklist',
  'policy'
]

export default function SolutionsPage() {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('All Categories')
  const [selectedType, setSelectedType] = useState('All Types')
  const [sortBy, setSortBy] = useState('featured')
  const [showFilters, setShowFilters] = useState(false)

  // Use the real API hook
  const { data: solutionsData, isLoading, error } = useSolutions({
    category: selectedCategory === 'All Categories' ? undefined : selectedCategory,
    type: selectedType === 'All Types' ? undefined : selectedType,
    search: searchQuery || undefined,
    sort: sortBy
  })

  const solutions = solutionsData?.data || []

  // Filter solutions locally for immediate feedback
  const filteredSolutions = solutions.filter(solution => {
    const matchesSearch = !searchQuery ||
      solution.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      solution.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (solution.tags && solution.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase())))

    const matchesCategory = selectedCategory === 'All Categories' || solution.category === selectedCategory
    const matchesType = selectedType === 'All Types' || solution.type === selectedType

    return matchesSearch && matchesCategory && matchesType
  })

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'template': return FileText
      case 'tool': return Settings
      case 'framework': return Building
      case 'checklist': return CheckCircle
      case 'policy': return Shield
      default: return FileText
    }
  }

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'template': return 'bg-blue-100 text-blue-600'
      case 'tool': return 'bg-green-100 text-green-600'
      case 'framework': return 'bg-purple-100 text-purple-600'
      case 'checklist': return 'bg-orange-100 text-orange-600'
      case 'policy': return 'bg-red-100 text-red-600'
      default: return 'bg-gray-100 text-gray-600'
    }
  }

  // Handle loading state
  if (isLoading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center py-20">
          <div className="text-center">
            <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4" />
            <p className="text-gray-600">Loading solutions...</p>
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
            <p className="text-red-600 mb-4">Error loading solutions</p>
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
            <h1 className="text-3xl font-bold">Solutions Marketplace</h1>
            <p className="text-gray-600">Ready-to-use BCM templates, tools, and frameworks</p>
          </div>
          <Button className="flex items-center gap-2">
            <Zap className="h-4 w-4" />
            Sell Your Solutions
          </Button>
        </div>

        {/* Search and Filters */}
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
            <Input
              placeholder="Search solutions, templates, tools..."
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
              {solutionTypes.map(type => (
                <option key={type} value={type}>
                  {type === 'All Types' ? type : type.charAt(0).toUpperCase() + type.slice(1)}
                </option>
              ))}
            </select>

            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md text-sm"
            >
              <option value="featured">Featured</option>
              <option value="popular">Most Popular</option>
              <option value="newest">Newest</option>
              <option value="price_low">Price: Low to High</option>
              <option value="price_high">Price: High to Low</option>
              <option value="rating">Highest Rated</option>
            </select>
          </div>
        </div>

        {/* Featured Section */}
        <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-6">
          <div className="flex items-center gap-2 mb-4">
            <TrendingUp className="h-5 w-5 text-blue-600" />
            <h2 className="text-xl font-semibold">Featured Solutions</h2>
          </div>
          <div className="grid md:grid-cols-3 gap-4">
            {solutions.filter(s => s.featured).slice(0, 3).map(solution => {
              const TypeIcon = getTypeIcon(solution.type)
              return (
                <Card key={solution.id} className="hover:shadow-md transition-shadow">
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between mb-3">
                      <div className={`p-2 rounded-lg ${getTypeColor(solution.type)}`}>
                        <TypeIcon className="h-4 w-4" />
                      </div>
                      <div className="text-right">
                        <div className="text-lg font-bold">${solution.price}</div>
                        <div className="text-xs text-gray-500">{solution.currency}</div>
                      </div>
                    </div>
                    <h3 className="font-semibold text-sm mb-2 line-clamp-2">{solution.title}</h3>
                    <div className="flex items-center gap-2 text-xs text-gray-600">
                      <Star className="h-3 w-3 fill-yellow-400 text-yellow-400" />
                      <span>{solution.rating}</span>
                      <span>•</span>
                      <Download className="h-3 w-3" />
                      <span>{solution.downloadCount}</span>
                    </div>
                  </CardContent>
                </Card>
              )
            })}
          </div>
        </div>

        {/* Solutions Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
          {filteredSolutions.map(solution => {
            const TypeIcon = getTypeIcon(solution.type)

            return (
              <Card key={solution.id} className="hover:shadow-lg transition-shadow">
                <CardContent className="p-6">
                  {/* Solution Header */}
                  <div className="flex items-start justify-between mb-4">
                    <div className={`p-3 rounded-lg ${getTypeColor(solution.type)}`}>
                      <TypeIcon className="h-6 w-6" />
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-bold">${solution.price}</div>
                      <div className="text-sm text-gray-500">{solution.currency}</div>
                    </div>
                  </div>

                  {/* Title and Description */}
                  <div className="mb-4">
                    <h3 className="font-semibold text-lg mb-2 line-clamp-2">{solution.title}</h3>
                    <p className="text-gray-600 text-sm line-clamp-3">{solution.description}</p>
                  </div>

                  {/* Author */}
                  <div className="flex items-center gap-3 mb-4">
                    <Avatar className="h-8 w-8">
                      <AvatarImage src={solution.author.avatar} alt={solution.author.name} />
                      <AvatarFallback className="text-xs">
                        {solution.author.name.split(' ').map(n => n[0]).join('')}
                      </AvatarFallback>
                    </Avatar>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-1">
                        <span className="text-sm font-medium truncate">{solution.author.name}</span>
                        {solution.author.verified && (
                          <CheckCircle className="h-3 w-3 text-blue-500" />
                        )}
                      </div>
                      <div className="text-xs text-gray-500 truncate">{solution.author.company}</div>
                    </div>
                  </div>

                  {/* Stats */}
                  <div className="flex items-center justify-between mb-4 text-sm text-gray-600">
                    <div className="flex items-center gap-1">
                      <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                      <span>{solution.rating}</span>
                      <span>({solution.reviewCount})</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Download className="h-4 w-4" />
                      <span>{solution.downloadCount.toLocaleString()}</span>
                    </div>
                  </div>

                  {/* Tags */}
                  <div className="mb-4">
                    <div className="flex flex-wrap gap-1">
                      {solution.tags.slice(0, 3).map(tag => (
                        <Badge key={tag} variant="secondary" className="text-xs">
                          {tag}
                        </Badge>
                      ))}
                      {solution.tags.length > 3 && (
                        <Badge variant="outline" className="text-xs">
                          +{solution.tags.length - 3}
                        </Badge>
                      )}
                    </div>
                  </div>

                  {/* Format and Compliance */}
                  <div className="mb-4 space-y-2">
                    <div className="flex items-center gap-2 text-xs text-gray-600">
                      <FileText className="h-3 w-3" />
                      <span>Formats: {solution.format.join(', ')}</span>
                    </div>
                    <div className="flex items-center gap-2 text-xs text-gray-600">
                      <Shield className="h-3 w-3" />
                      <span>Compliance: {solution.compliance.slice(0, 2).join(', ')}</span>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex gap-2">
                    <Button className="flex-1" size="sm">
                      <Download className="h-3 w-3 mr-1" />
                      Buy Now
                    </Button>
                    <Button variant="outline" size="sm">
                      <Eye className="h-3 w-3" />
                    </Button>
                    <Button variant="outline" size="sm">
                      <Heart className="h-3 w-3" />
                    </Button>
                  </div>

                  {/* Last Updated */}
                  <div className="mt-3 flex items-center gap-1 text-xs text-gray-500">
                    <Clock className="h-3 w-3" />
                    <span>Updated {solution.lastUpdated}</span>
                  </div>
                </CardContent>
              </Card>
            )
          })}
        </div>

        {/* Load More */}
        <div className="text-center py-8">
          <Button variant="outline" size="lg">
            Load More Solutions
          </Button>
        </div>

        {/* Categories Overview */}
        <div className="bg-gray-50 rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-4">Browse by Category</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { name: 'Templates', icon: FileText, count: 234 },
              { name: 'Tools', icon: Settings, count: 156 },
              { name: 'Frameworks', icon: Building, count: 89 },
              { name: 'Checklists', icon: CheckCircle, count: 167 }
            ].map(category => (
              <div key={category.name} className="bg-white rounded-lg p-4 text-center hover:shadow-md transition-shadow cursor-pointer">
                <category.icon className="h-8 w-8 mx-auto mb-2 text-blue-600" />
                <div className="font-medium">{category.name}</div>
                <div className="text-sm text-gray-500">{category.count} items</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </AppLayout>
  )
}