'use client'

import React, { useState } from 'react'
import { AppLayout } from '@/components/layout/AppLayout'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { useCaseStudies } from '@/hooks/api'
import {
  Search,
  Building,
  Users,
  Calendar,
  DollarSign,
  TrendingUp,
  CheckCircle,
  Eye,
  Heart,
  Share,
  Award,
  Clock,
  MapPin,
  FileText,
  Download,
  Star,
  Filter,
  Briefcase,
  Settings,
  Loader2
} from 'lucide-react'

interface CaseStudy {
  id: string
  title: string
  summary: string
  challenge: string
  solution: string
  results: string
  industry: string
  company: {
    name: string
    size: string
    location: string
  }
  consultant: {
    name: string
    avatar?: string
    verified: boolean
    company: string
  }
  duration: string
  budget: {
    range: string
    currency: string
  }
  tags: string[]
  metrics: {
    label: string
    value: string
    improvement: string
  }[]
  publishDate: string
  viewCount: number
  likeCount: number
  downloadCount: number
  featured: boolean
  compliance: string[]
  attachments: {
    name: string
    type: string
    size: string
  }[]
}


const industries = [
  'All Industries',
  'Healthcare',
  'Financial Services',
  'Manufacturing',
  'Technology',
  'Energy',
  'Government',
  'Education',
  'Retail'
]

const companySizes = [
  'All Sizes',
  '1-50 employees',
  '51-200 employees',
  '201-1000 employees',
  '1000+ employees'
]

export default function CaseStudiesPage() {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedIndustry, setSelectedIndustry] = useState('All Industries')
  const [selectedSize, setSelectedSize] = useState('All Sizes')
  const [sortBy, setSortBy] = useState('featured')

  // Use the real API hook
  const { data: casesData, isLoading, error } = useCaseStudies({
    industry: selectedIndustry === 'All Industries' ? undefined : selectedIndustry,
    company_size: selectedSize === 'All Sizes' ? undefined : selectedSize,
    search: searchQuery || undefined,
    sort: sortBy
  })

  const caseStudies = casesData?.data || []

  // Filter case studies locally for immediate feedback
  const filteredCaseStudies = caseStudies.filter(caseStudy => {
    const matchesSearch = !searchQuery ||
      caseStudy.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      caseStudy.summary.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (caseStudy.tags && caseStudy.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase())))

    const matchesIndustry = selectedIndustry === 'All Industries' || caseStudy.industry === selectedIndustry
    const matchesSize = selectedSize === 'All Sizes' || (caseStudy.company && caseStudy.company.size === selectedSize)

    return matchesSearch && matchesIndustry && matchesSize
  })

  // Handle loading state
  if (isLoading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center py-20">
          <div className="text-center">
            <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4" />
            <p className="text-gray-600">Loading case studies...</p>
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
            <p className="text-red-600 mb-4">Error loading case studies</p>
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
            <h1 className="text-3xl font-bold">Case Studies</h1>
            <p className="text-gray-600">Real-world BCM success stories and implementation examples</p>
          </div>
          <Button className="flex items-center gap-2">
            <FileText className="h-4 w-4" />
            Submit Your Case Study
          </Button>
        </div>

        {/* Search and Filters */}
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
            <Input
              placeholder="Search case studies by industry, challenge, solution..."
              className="pl-10"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>

          <div className="flex gap-2">
            <select
              value={selectedIndustry}
              onChange={(e) => setSelectedIndustry(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md text-sm"
            >
              {industries.map(industry => (
                <option key={industry} value={industry}>{industry}</option>
              ))}
            </select>

            <select
              value={selectedSize}
              onChange={(e) => setSelectedSize(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md text-sm"
            >
              {companySizes.map(size => (
                <option key={size} value={size}>{size}</option>
              ))}
            </select>

            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md text-sm"
            >
              <option value="featured">Featured</option>
              <option value="newest">Newest</option>
              <option value="popular">Most Popular</option>
              <option value="budget_high">Highest Budget</option>
              <option value="budget_low">Lowest Budget</option>
            </select>
          </div>
        </div>

        {/* Featured Case Studies */}
        <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-6">
          <div className="flex items-center gap-2 mb-4">
            <Award className="h-5 w-5 text-blue-600" />
            <h2 className="text-xl font-semibold">Featured Case Studies</h2>
          </div>
          <div className="grid md:grid-cols-2 gap-4">
            {caseStudies.filter(c => c.featured).slice(0, 2).map(caseStudy => (
              <Card key={caseStudy.id} className="hover:shadow-md transition-shadow">
                <CardContent className="p-4">
                  <div className="flex justify-between items-start mb-3">
                    <Badge variant="secondary">{caseStudy.industry}</Badge>
                    <div className="text-right text-sm text-gray-600">
                      <div>{caseStudy.budget.range}</div>
                      <div>{caseStudy.duration}</div>
                    </div>
                  </div>
                  <h3 className="font-semibold text-sm mb-2 line-clamp-2">{caseStudy.title}</h3>
                  <p className="text-xs text-gray-600 mb-3 line-clamp-2">{caseStudy.summary}</p>
                  <div className="flex items-center justify-between text-xs text-gray-500">
                    <div className="flex items-center gap-3">
                      <div className="flex items-center gap-1">
                        <Eye className="h-3 w-3" />
                        <span>{caseStudy.viewCount}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <Heart className="h-3 w-3" />
                        <span>{caseStudy.likeCount}</span>
                      </div>
                    </div>
                    <span>{caseStudy.publishDate}</span>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Case Studies Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {filteredCaseStudies.map(caseStudy => (
            <Card key={caseStudy.id} className="hover:shadow-lg transition-shadow">
              <CardContent className="p-6">
                {/* Header */}
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <Badge variant="outline">{caseStudy.industry}</Badge>
                      <Badge variant="secondary">{caseStudy.company.size}</Badge>
                    </div>
                    <h3 className="font-semibold text-lg line-clamp-2">{caseStudy.title}</h3>
                  </div>
                  {caseStudy.featured && (
                    <Award className="h-5 w-5 text-yellow-500" />
                  )}
                </div>

                {/* Company Info */}
                <div className="mb-4 p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center gap-2 mb-1">
                    <Building className="h-4 w-4 text-gray-600" />
                    <span className="font-medium text-sm">{caseStudy.company.name}</span>
                  </div>
                  <div className="flex items-center gap-4 text-xs text-gray-600">
                    <div className="flex items-center gap-1">
                      <Users className="h-3 w-3" />
                      <span>{caseStudy.company.size}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <MapPin className="h-3 w-3" />
                      <span>{caseStudy.company.location}</span>
                    </div>
                  </div>
                </div>

                {/* Summary */}
                <p className="text-gray-600 text-sm mb-4 line-clamp-3">{caseStudy.summary}</p>

                {/* Key Metrics */}
                <div className="mb-4">
                  <h4 className="font-medium text-sm mb-2">Key Results</h4>
                  <div className="grid grid-cols-2 gap-2">
                    {caseStudy.metrics.slice(0, 4).map(metric => (
                      <div key={metric.label} className="text-center p-2 bg-green-50 rounded">
                        <div className="font-bold text-green-600 text-sm">{metric.value}</div>
                        <div className="text-xs text-gray-600">{metric.label}</div>
                        <div className="text-xs text-green-600">{metric.improvement}</div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Consultant */}
                <div className="flex items-center gap-3 mb-4">
                  <Avatar className="h-8 w-8">
                    <AvatarImage src={caseStudy.consultant.avatar} alt={caseStudy.consultant.name} />
                    <AvatarFallback className="text-xs">
                      {caseStudy.consultant.name.split(' ').map(n => n[0]).join('')}
                    </AvatarFallback>
                  </Avatar>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-1">
                      <span className="text-sm font-medium truncate">{caseStudy.consultant.name}</span>
                      {caseStudy.consultant.verified && (
                        <CheckCircle className="h-3 w-3 text-blue-500" />
                      )}
                    </div>
                    <div className="text-xs text-gray-500 truncate">{caseStudy.consultant.company}</div>
                  </div>
                </div>

                {/* Project Details */}
                <div className="flex items-center justify-between mb-4 text-sm text-gray-600">
                  <div className="flex items-center gap-1">
                    <Calendar className="h-4 w-4" />
                    <span>{caseStudy.duration}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <DollarSign className="h-4 w-4" />
                    <span>{caseStudy.budget.range}</span>
                  </div>
                </div>

                {/* Tags */}
                <div className="mb-4">
                  <div className="flex flex-wrap gap-1">
                    {caseStudy.tags.slice(0, 3).map(tag => (
                      <Badge key={tag} variant="secondary" className="text-xs">
                        {tag}
                      </Badge>
                    ))}
                    {caseStudy.tags.length > 3 && (
                      <Badge variant="outline" className="text-xs">
                        +{caseStudy.tags.length - 3}
                      </Badge>
                    )}
                  </div>
                </div>

                {/* Compliance */}
                <div className="mb-4">
                  <div className="flex items-center gap-1 mb-1">
                    <CheckCircle className="h-3 w-3 text-green-500" />
                    <span className="text-xs text-gray-600">Compliance:</span>
                  </div>
                  <div className="flex flex-wrap gap-1">
                    {caseStudy.compliance.slice(0, 2).map(comp => (
                      <Badge key={comp} variant="outline" className="text-xs">
                        {comp}
                      </Badge>
                    ))}
                    {caseStudy.compliance.length > 2 && (
                      <span className="text-xs text-gray-500">
                        +{caseStudy.compliance.length - 2} more
                      </span>
                    )}
                  </div>
                </div>

                {/* Attachments */}
                {caseStudy.attachments.length > 0 && (
                  <div className="mb-4">
                    <div className="flex items-center gap-1 mb-1">
                      <FileText className="h-3 w-3 text-gray-400" />
                      <span className="text-xs text-gray-600">Attachments:</span>
                    </div>
                    <div className="space-y-1">
                      {caseStudy.attachments.slice(0, 2).map(attachment => (
                        <div key={attachment.name} className="flex items-center gap-2 text-xs text-gray-600">
                          <Download className="h-3 w-3" />
                          <span className="truncate">{attachment.name}</span>
                          <span className="text-gray-400">({attachment.size})</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Stats */}
                <div className="flex items-center justify-between mb-4 text-sm text-gray-600">
                  <div className="flex items-center gap-4">
                    <div className="flex items-center gap-1">
                      <Eye className="h-4 w-4" />
                      <span>{caseStudy.viewCount.toLocaleString()}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Heart className="h-4 w-4" />
                      <span>{caseStudy.likeCount}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Download className="h-4 w-4" />
                      <span>{caseStudy.downloadCount}</span>
                    </div>
                  </div>
                  <span className="text-xs">{caseStudy.publishDate}</span>
                </div>

                {/* Actions */}
                <div className="flex gap-2">
                  <Button className="flex-1" size="sm">
                    <Eye className="h-3 w-3 mr-1" />
                    View Full Case
                  </Button>
                  <Button variant="outline" size="sm">
                    <Heart className="h-3 w-3" />
                  </Button>
                  <Button variant="outline" size="sm">
                    <Share className="h-3 w-3" />
                  </Button>
                  <Button variant="outline" size="sm">
                    <Download className="h-3 w-3" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Load More */}
        <div className="text-center py-8">
          <Button variant="outline" size="lg">
            Load More Case Studies
          </Button>
        </div>

        {/* Industry Overview */}
        <div className="bg-gray-50 rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-4">Case Studies by Industry</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { name: 'Healthcare', count: 89, icon: Building },
              { name: 'Financial', count: 67, icon: TrendingUp },
              { name: 'Manufacturing', count: 134, icon: Settings },
              { name: 'Technology', count: 78, icon: Briefcase }
            ].map(industry => {
              const Icon = industry.icon
              return (
                <div key={industry.name} className="bg-white rounded-lg p-4 text-center hover:shadow-md transition-shadow cursor-pointer">
                  <Icon className="h-8 w-8 mx-auto mb-2 text-blue-600" />
                  <div className="font-medium">{industry.name}</div>
                  <div className="text-sm text-gray-500">{industry.count} cases</div>
                </div>
              )
            })}
          </div>
        </div>
      </div>
    </AppLayout>
  )
}