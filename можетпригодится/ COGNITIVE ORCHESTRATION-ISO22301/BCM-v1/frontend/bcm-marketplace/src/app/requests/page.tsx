'use client'

import React, { useState } from 'react'
import { AppLayout } from '@/components/layout/AppLayout'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  Search,
  Filter,
  MapPin,
  Clock,
  DollarSign,
  Building,
  AlertCircle,
  Eye,
  MessageCircle,
  BookmarkPlus,
  Send,
  Calendar,
  Users,
  Star,
  TrendingUp
} from 'lucide-react'

interface ServiceRequest {
  id: string
  title: string
  description: string
  client: {
    name: string
    company: string
    avatar?: string
    rating: number
    reviewCount: number
    verified: boolean
  }
  serviceType: string
  industry: string
  urgency: 'low' | 'medium' | 'high' | 'urgent'
  budget: {
    min: number
    max: number
    type: 'hourly' | 'fixed' | 'retainer'
  }
  duration: string
  location: string
  remote: boolean
  skills: string[]
  requirements: string[]
  deliverables: string[]
  proposalsCount: number
  views: number
  postedDate: string
  deadline: string
  status: 'open' | 'in_progress' | 'completed' | 'cancelled'
  isBookmarked: boolean
}

const mockServiceRequests: ServiceRequest[] = [
  {
    id: '1',
    title: 'Financial Services BCM Gap Analysis & Implementation Plan',
    description: 'We need a comprehensive Business Continuity Management gap analysis for our growing fintech company. Currently have 500+ employees across 5 offices. Looking for an expert to assess our current state, identify gaps against ISO 22301 standards, and develop a detailed implementation roadmap.',
    client: {
      name: 'Sarah Johnson',
      company: 'FinTech Solutions Inc.',
      rating: 4.8,
      reviewCount: 23,
      verified: true
    },
    serviceType: 'BCM Assessment',
    industry: 'Financial Services',
    urgency: 'high',
    budget: { min: 150, max: 200, type: 'hourly' },
    duration: '6-8 weeks',
    location: 'New York, NY',
    remote: true,
    skills: ['ISO 22301', 'Financial Services BCM', 'Gap Analysis', 'Risk Assessment'],
    requirements: [
      'Minimum 5 years BCM consulting experience',
      'ISO 22301 Lead Auditor certification preferred',
      'Financial services industry experience required',
      'Available to start within 2 weeks'
    ],
    deliverables: [
      'Current state assessment report',
      'Gap analysis against ISO 22301',
      'Implementation roadmap with priorities',
      'Resource and budget estimates',
      'Executive presentation'
    ],
    proposalsCount: 12,
    views: 245,
    postedDate: '2024-01-15',
    deadline: '2024-01-25',
    status: 'open',
    isBookmarked: false
  },
  {
    id: '2',
    title: 'Healthcare Crisis Management Training Program',
    description: 'Regional healthcare network needs comprehensive crisis management training for leadership team and key staff. Focus on pandemic response, supply chain disruptions, and maintaining patient care during emergencies.',
    client: {
      name: 'Dr. Michael Chen',
      company: 'Regional Medical Center',
      rating: 4.9,
      reviewCount: 15,
      verified: true
    },
    serviceType: 'Training & Workshop',
    industry: 'Healthcare',
    urgency: 'medium',
    budget: { min: 5000, max: 15000, type: 'fixed' },
    duration: '4 weeks',
    location: 'Chicago, IL',
    remote: false,
    skills: ['Crisis Management', 'Healthcare BCM', 'Training Design', 'Leadership Development'],
    requirements: [
      'Healthcare industry experience required',
      'Crisis management training expertise',
      'Adult learning principles knowledge',
      'Available for onsite delivery'
    ],
    deliverables: [
      'Customized training curriculum',
      'Interactive workshop materials',
      '3-day leadership intensive program',
      'Staff training modules',
      'Crisis response playbooks'
    ],
    proposalsCount: 8,
    views: 189,
    postedDate: '2024-01-12',
    deadline: '2024-01-22',
    status: 'open',
    isBookmarked: true
  },
  {
    id: '3',
    title: 'Manufacturing Supply Chain Resilience Assessment',
    description: 'Global automotive manufacturer seeking expert to assess supply chain resilience and develop business continuity strategies for critical manufacturing operations across multiple facilities.',
    client: {
      name: 'Jennifer Liu',
      company: 'AutoCorp Manufacturing',
      rating: 4.7,
      reviewCount: 31,
      verified: true
    },
    serviceType: 'Risk Assessment',
    industry: 'Manufacturing',
    urgency: 'low',
    budget: { min: 120, max: 180, type: 'hourly' },
    duration: '12-16 weeks',
    location: 'Detroit, MI',
    remote: true,
    skills: ['Supply Chain Risk', 'Manufacturing BCM', 'Business Impact Analysis', 'Vendor Management'],
    requirements: [
      'Manufacturing industry experience',
      'Supply chain risk expertise',
      'Global operations knowledge',
      'BIA methodology expertise'
    ],
    deliverables: [
      'Supply chain risk assessment',
      'Business impact analysis',
      'Resilience recommendations',
      'Vendor risk profiles',
      'Continuity strategy document'
    ],
    proposalsCount: 15,
    views: 334,
    postedDate: '2024-01-10',
    deadline: '2024-01-30',
    status: 'open',
    isBookmarked: false
  }
]

const serviceTypes = [
  'All Types',
  'BCM Assessment',
  'Risk Assessment',
  'Training & Workshop',
  'Crisis Management',
  'Implementation Support',
  'BIA Services',
  'Compliance Audit'
]

const industries = [
  'All Industries',
  'Financial Services',
  'Healthcare',
  'Manufacturing',
  'Technology',
  'Government',
  'Energy & Utilities'
]

export default function ServiceRequestsPage() {
  const [activeTab, setActiveTab] = useState('browse')
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedType, setSelectedType] = useState('All Types')
  const [selectedIndustry, setSelectedIndustry] = useState('All Industries')
  const [selectedUrgency, setSelectedUrgency] = useState('all')
  const [budgetRange, setBudgetRange] = useState([0, 500])

  const getUrgencyColor = (urgency: string) => {
    switch (urgency) {
      case 'urgent': return 'bg-red-100 text-red-800 border-red-200'
      case 'high': return 'bg-orange-100 text-orange-800 border-orange-200'
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      case 'low': return 'bg-green-100 text-green-800 border-green-200'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getBudgetDisplay = (budget: ServiceRequest['budget']) => {
    const { min, max, type } = budget
    const typeLabel = type === 'hourly' ? '/hr' : type === 'fixed' ? 'fixed' : '/month'
    return `$${min}${max !== min ? `-$${max}` : ''} ${typeLabel}`
  }

  const filteredRequests = mockServiceRequests.filter(request => {
    const matchesSearch = request.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         request.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         request.skills.some(skill => skill.toLowerCase().includes(searchQuery.toLowerCase()))
    const matchesType = selectedType === 'All Types' || request.serviceType === selectedType
    const matchesIndustry = selectedIndustry === 'All Industries' || request.industry === selectedIndustry
    const matchesUrgency = selectedUrgency === 'all' || request.urgency === selectedUrgency

    return matchesSearch && matchesType && matchesIndustry && matchesUrgency
  })

  return (
    <AppLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <h1 className="text-3xl font-bold">Service Requests</h1>
            <p className="text-gray-600">Find BCM projects and consulting opportunities</p>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <Search className="h-5 w-5 text-blue-600" />
                <div>
                  <div className="text-2xl font-bold">{mockServiceRequests.length}</div>
                  <div className="text-sm text-gray-600">Open Requests</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <DollarSign className="h-5 w-5 text-green-600" />
                <div>
                  <div className="text-2xl font-bold">$165</div>
                  <div className="text-sm text-gray-600">Avg Hourly Rate</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <Clock className="h-5 w-5 text-purple-600" />
                <div>
                  <div className="text-2xl font-bold">8.5</div>
                  <div className="text-sm text-gray-600">Avg Project Duration (weeks)</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <TrendingUp className="h-5 w-5 text-orange-600" />
                <div>
                  <div className="text-2xl font-bold">92%</div>
                  <div className="text-sm text-gray-600">Success Rate</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList>
            <TabsTrigger value="browse">Browse Requests</TabsTrigger>
            <TabsTrigger value="saved">Saved Requests</TabsTrigger>
            <TabsTrigger value="applied">Applied</TabsTrigger>
          </TabsList>

          <TabsContent value="browse" className="space-y-6">
            {/* Search and Filters */}
            <div className="flex flex-col lg:flex-row gap-4">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                <Input
                  placeholder="Search requests, skills, or companies..."
                  className="pl-10"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>

              <div className="flex gap-2">
                <select
                  value={selectedType}
                  onChange={(e) => setSelectedType(e.target.value)}
                  className="px-3 py-2 border border-gray-300 rounded-md text-sm"
                >
                  {serviceTypes.map(type => (
                    <option key={type} value={type}>{type}</option>
                  ))}
                </select>

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
                  value={selectedUrgency}
                  onChange={(e) => setSelectedUrgency(e.target.value)}
                  className="px-3 py-2 border border-gray-300 rounded-md text-sm"
                >
                  <option value="all">All Urgency</option>
                  <option value="urgent">Urgent</option>
                  <option value="high">High</option>
                  <option value="medium">Medium</option>
                  <option value="low">Low</option>
                </select>
              </div>
            </div>

            {/* Service Requests */}
            <div className="space-y-4">
              {filteredRequests.map(request => (
                <Card key={request.id} className="hover:shadow-lg transition-shadow">
                  <CardContent className="p-6">
                    {/* Header */}
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <h3 className="text-xl font-bold text-gray-900 hover:text-blue-600 cursor-pointer">
                            {request.title}
                          </h3>
                          <Badge className={`text-xs ${getUrgencyColor(request.urgency)}`}>
                            {request.urgency.toUpperCase()}
                          </Badge>
                        </div>

                        <p className="text-gray-600 mb-4 line-clamp-3">
                          {request.description}
                        </p>
                      </div>

                      <div className="flex items-center gap-2 ml-4">
                        <Button variant="outline" size="sm">
                          <BookmarkPlus className={`h-3 w-3 ${request.isBookmarked ? 'text-blue-600' : ''}`} />
                        </Button>
                      </div>
                    </div>

                    {/* Client Info */}
                    <div className="flex items-center gap-4 mb-4 p-3 bg-gray-50 rounded-lg">
                      <Avatar className="h-10 w-10">
                        <AvatarImage src={request.client.avatar} />
                        <AvatarFallback>
                          {request.client.name.split(' ').map(n => n[0]).join('')}
                        </AvatarFallback>
                      </Avatar>
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <h4 className="font-semibold">{request.client.name}</h4>
                          {request.client.verified && (
                            <Badge variant="outline" className="text-blue-600 border-blue-600 text-xs">
                              Verified
                            </Badge>
                          )}
                        </div>
                        <div className="flex items-center gap-4 text-sm text-gray-600">
                          <span className="flex items-center gap-1">
                            <Building className="h-3 w-3" />
                            {request.client.company}
                          </span>
                          <span className="flex items-center gap-1">
                            <Star className="h-3 w-3 fill-yellow-400 text-yellow-400" />
                            {request.client.rating} ({request.client.reviewCount} reviews)
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* Project Details */}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                      <div className="text-center p-3 bg-blue-50 rounded-lg">
                        <DollarSign className="h-4 w-4 mx-auto mb-1 text-blue-600" />
                        <div className="text-xs text-gray-600">Budget</div>
                        <div className="font-semibold text-sm">{getBudgetDisplay(request.budget)}</div>
                      </div>
                      <div className="text-center p-3 bg-green-50 rounded-lg">
                        <Clock className="h-4 w-4 mx-auto mb-1 text-green-600" />
                        <div className="text-xs text-gray-600">Duration</div>
                        <div className="font-semibold text-sm">{request.duration}</div>
                      </div>
                      <div className="text-center p-3 bg-purple-50 rounded-lg">
                        <MapPin className="h-4 w-4 mx-auto mb-1 text-purple-600" />
                        <div className="text-xs text-gray-600">Location</div>
                        <div className="font-semibold text-sm">{request.remote ? 'Remote OK' : request.location}</div>
                      </div>
                      <div className="text-center p-3 bg-orange-50 rounded-lg">
                        <Calendar className="h-4 w-4 mx-auto mb-1 text-orange-600" />
                        <div className="text-xs text-gray-600">Deadline</div>
                        <div className="font-semibold text-sm">{request.deadline}</div>
                      </div>
                    </div>

                    {/* Skills Required */}
                    <div className="mb-4">
                      <h5 className="font-semibold mb-2 text-sm">Skills Required</h5>
                      <div className="flex flex-wrap gap-2">
                        {request.skills.map(skill => (
                          <Badge key={skill} variant="secondary" className="text-xs">
                            {skill}
                          </Badge>
                        ))}
                      </div>
                    </div>

                    {/* Key Requirements Preview */}
                    <div className="mb-4">
                      <h5 className="font-semibold mb-2 text-sm">Key Requirements</h5>
                      <ul className="space-y-1">
                        {request.requirements.slice(0, 2).map((req, index) => (
                          <li key={index} className="flex items-start gap-2 text-sm text-gray-700">
                            <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0" />
                            {req}
                          </li>
                        ))}
                        {request.requirements.length > 2 && (
                          <li className="text-sm text-blue-600 cursor-pointer hover:underline">
                            +{request.requirements.length - 2} more requirements
                          </li>
                        )}
                      </ul>
                    </div>

                    {/* Meta Info and Actions */}
                    <div className="flex items-center justify-between pt-4 border-t">
                      <div className="flex items-center gap-4 text-sm text-gray-500">
                        <div className="flex items-center gap-1">
                          <Send className="h-4 w-4" />
                          <span>{request.proposalsCount} proposals</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <Eye className="h-4 w-4" />
                          <span>{request.views} views</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <Clock className="h-4 w-4" />
                          <span>Posted {request.postedDate}</span>
                        </div>
                      </div>

                      <div className="flex items-center gap-2">
                        <Button variant="outline" size="sm">
                          View Details
                        </Button>
                        <Button size="sm">
                          <Send className="h-3 w-3 mr-1" />
                          Submit Proposal
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* No Results */}
            {filteredRequests.length === 0 && (
              <div className="text-center py-12">
                <Search className="h-12 w-12 mx-auto text-gray-300 mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No requests found</h3>
                <p className="text-gray-600 mb-4">
                  Try adjusting your search criteria or filters
                </p>
                <Button onClick={() => {
                  setSearchQuery('')
                  setSelectedType('All Types')
                  setSelectedIndustry('All Industries')
                  setSelectedUrgency('all')
                }}>
                  Clear Filters
                </Button>
              </div>
            )}
          </TabsContent>

          <TabsContent value="saved" className="space-y-6">
            <div className="text-center py-12">
              <BookmarkPlus className="h-12 w-12 mx-auto text-gray-300 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No saved requests</h3>
              <p className="text-gray-600">Save interesting requests to review later</p>
            </div>
          </TabsContent>

          <TabsContent value="applied" className="space-y-6">
            <div className="text-center py-12">
              <Send className="h-12 w-12 mx-auto text-gray-300 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No applications yet</h3>
              <p className="text-gray-600">Your proposal submissions will appear here</p>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </AppLayout>
  )
}