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
  Building,
  Calendar,
  Award,
  TrendingUp,
  Filter,
  ArrowRight,
  ExternalLink,
  Users
} from 'lucide-react'

interface CaseStudy {
  id: string
  title: string
  summary: string
  description: string
  specialist: {
    name: string
    avatar?: string
    title: string
    rating: number
    verified: boolean
  }
  client: {
    industry: string
    size: string
    location: string
  }
  project: {
    type: string
    duration: string
    teamSize: number
    completionDate: string
    budget: string
  }
  keyAchievements: string[]
  technologiesUsed: string[]
  challenges: string[]
  results: {
    rtoImprovement?: string
    rpoImprovement?: string
    costSavings?: string
    complianceLevel?: string
  }
  tags: string[]
  industry: string
  difficulty: 'Basic' | 'Intermediate' | 'Advanced' | 'Expert'
  views: number
  downloads: number
  rating: number
  isFeatured?: boolean
  attachments: {
    name: string
    type: string
    size: string
    downloadUrl: string
  }[]
}

const mockCaseStudies: CaseStudy[] = [
  {
    id: '1',
    title: 'Global Financial Institution BCM Transformation',
    summary: 'Complete BCM program overhaul for a major international bank with 50,000+ employees across 40 countries.',
    description: 'Led a comprehensive Business Continuity Management transformation project for one of the world\'s largest financial institutions. The project involved redesigning the entire BCM framework, implementing new technologies, and ensuring compliance with global regulatory requirements.',
    specialist: {
      name: 'Dr. Sarah Martinez',
      title: 'Senior BCM Consultant & Former CBCI President',
      rating: 4.9,
      verified: true
    },
    client: {
      industry: 'Financial Services',
      size: '50,000+ employees',
      location: 'Global (40 countries)'
    },
    project: {
      type: 'BCM Program Implementation',
      duration: '18 months',
      teamSize: 25,
      completionDate: '2024-03-15',
      budget: '$2.5M - $5M'
    },
    keyAchievements: [
      'Reduced RTO from 24 hours to 2 hours for critical systems',
      'Achieved 99.99% uptime during 3 major crisis events',
      'Passed all regulatory audits with zero critical findings',
      'Trained 15,000+ staff members across all regions',
      'Implemented automated failover for 200+ critical processes'
    ],
    technologiesUsed: [
      'MetricStream BCM',
      'ServiceNow ITBM',
      'Fusion Risk Management',
      'Microsoft Azure Site Recovery',
      'Zerto Disaster Recovery'
    ],
    challenges: [
      'Complex multi-jurisdictional regulatory requirements',
      'Legacy system integration across 40 countries',
      'Cultural change management in traditional organization',
      'Coordinating 25-person global project team'
    ],
    results: {
      rtoImprovement: '92% reduction (24h → 2h)',
      rpoImprovement: '85% reduction (4h → 30min)',
      costSavings: '$12M annually in operational efficiency',
      complianceLevel: '100% regulatory compliance maintained'
    },
    tags: ['iso22301', 'financial-services', 'global-implementation', 'regulatory-compliance'],
    industry: 'Financial Services',
    difficulty: 'Expert',
    views: 4520,
    downloads: 890,
    rating: 4.8,
    isFeatured: true,
    attachments: [
      { name: 'Executive Summary.pdf', type: 'PDF', size: '2.1 MB', downloadUrl: '#' },
      { name: 'Implementation Timeline.xlsx', type: 'Excel', size: '850 KB', downloadUrl: '#' },
      { name: 'ROI Analysis.pdf', type: 'PDF', size: '1.5 MB', downloadUrl: '#' }
    ]
  },
  {
    id: '2',
    title: 'Healthcare System Pandemic Response Implementation',
    summary: 'Rapid BCM implementation for a 15-hospital healthcare network during COVID-19 pandemic.',
    description: 'Emergency BCM program deployment for a major healthcare network facing unprecedented challenges during the COVID-19 pandemic. Focus on maintaining critical patient care while ensuring staff safety.',
    specialist: {
      name: 'Michael Thompson',
      title: 'Healthcare BCM Specialist',
      rating: 4.7,
      verified: true
    },
    client: {
      industry: 'Healthcare',
      size: '15 hospitals, 25,000 staff',
      location: 'Regional (5 states)'
    },
    project: {
      type: 'Crisis Management & BCM',
      duration: '8 months',
      teamSize: 12,
      completionDate: '2021-11-30',
      budget: '$500K - $1M'
    },
    keyAchievements: [
      'Maintained 100% emergency services availability',
      'Reduced patient transfer times by 40%',
      'Implemented surge capacity protocols for 300% patient increase',
      'Zero critical service interruptions during peak pandemic'
    ],
    technologiesUsed: [
      'Epic EHR Integration',
      'Telehealth Platforms',
      'Crisis Communication Systems',
      'Resource Management Dashboards'
    ],
    challenges: [
      'Rapidly changing pandemic conditions',
      'Staff shortage and burnout management',
      'Supply chain disruptions',
      'Balancing patient care with safety protocols'
    ],
    results: {
      rtoImprovement: '60% faster response time',
      costSavings: '$8M in avoided service disruptions',
      complianceLevel: 'Full regulatory compliance maintained'
    },
    tags: ['healthcare', 'pandemic-response', 'crisis-management', 'surge-capacity'],
    industry: 'Healthcare',
    difficulty: 'Advanced',
    views: 2890,
    downloads: 445,
    rating: 4.9,
    attachments: [
      { name: 'Pandemic Response Plan.pdf', type: 'PDF', size: '3.2 MB', downloadUrl: '#' },
      { name: 'Surge Capacity Protocols.pdf', type: 'PDF', size: '1.8 MB', downloadUrl: '#' }
    ]
  },
  {
    id: '3',
    title: 'Manufacturing Supply Chain Resilience Program',
    summary: 'End-to-end supply chain BCM for automotive manufacturer with global operations.',
    description: 'Comprehensive supply chain resilience program for a major automotive manufacturer, focusing on supplier risk management and alternative sourcing strategies.',
    specialist: {
      name: 'Jennifer Liu',
      title: 'Supply Chain BCM Expert',
      rating: 4.8,
      verified: true
    },
    client: {
      industry: 'Automotive Manufacturing',
      size: '75,000 employees',
      location: 'Global (25 countries)'
    },
    project: {
      type: 'Supply Chain BCM',
      duration: '14 months',
      teamSize: 18,
      completionDate: '2023-08-20',
      budget: '$1M - $2.5M'
    },
    keyAchievements: [
      'Mapped 5,000+ suppliers across 3 tiers',
      'Reduced single-source dependencies by 70%',
      'Established alternative sourcing for 95% of critical components',
      'Achieved 48-hour supplier disruption notification system'
    ],
    technologiesUsed: [
      'SAP Ariba Risk Management',
      'Resilinc Supply Chain Monitoring',
      'RapidRatings Financial Health',
      'Supplier Risk Intelligence Platforms'
    ],
    challenges: [
      'Complex multi-tier supplier network',
      'Geopolitical risks and trade tensions',
      'Semiconductor shortage impacts',
      'Balancing cost with resilience'
    ],
    results: {
      rtoImprovement: '75% faster supplier alternative activation',
      costSavings: '$25M avoided losses during chip shortage',
      complianceLevel: 'Enhanced supplier compliance by 85%'
    },
    tags: ['supply-chain', 'manufacturing', 'automotive', 'supplier-risk'],
    industry: 'Manufacturing',
    difficulty: 'Advanced',
    views: 1950,
    downloads: 320,
    rating: 4.6,
    attachments: [
      { name: 'Supply Chain Resilience Framework.pdf', type: 'PDF', size: '4.1 MB', downloadUrl: '#' },
      { name: 'Supplier Risk Assessment Template.xlsx', type: 'Excel', size: '1.2 MB', downloadUrl: '#' }
    ]
  }
]

const industries = [
  'All Industries',
  'Financial Services',
  'Healthcare',
  'Manufacturing',
  'Technology',
  'Government',
  'Energy & Utilities',
  'Retail',
  'Education'
]

const projectTypes = [
  'All Types',
  'BCM Program Implementation',
  'Risk Assessment',
  'Crisis Management',
  'Supply Chain BCM',
  'Compliance & Audit',
  'Training Programs'
]

export function CaseStudies() {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedIndustry, setSelectedIndustry] = useState('All Industries')
  const [selectedType, setSelectedType] = useState('All Types')
  const [selectedDifficulty, setSelectedDifficulty] = useState('all')

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'Basic': return 'bg-green-100 text-green-800'
      case 'Intermediate': return 'bg-blue-100 text-blue-800'
      case 'Advanced': return 'bg-orange-100 text-orange-800'
      case 'Expert': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const filteredCaseStudies = mockCaseStudies.filter(caseStudy => {
    const matchesSearch = caseStudy.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         caseStudy.summary.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         caseStudy.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
    const matchesIndustry = selectedIndustry === 'All Industries' || caseStudy.industry === selectedIndustry
    const matchesType = selectedType === 'All Types' || caseStudy.project.type === selectedType
    const matchesDifficulty = selectedDifficulty === 'all' || caseStudy.difficulty === selectedDifficulty

    return matchesSearch && matchesIndustry && matchesType && matchesDifficulty
  })

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold">BCM Case Studies</h2>
          <p className="text-gray-600">Real-world BCM implementations and success stories from verified experts</p>
        </div>
        <Button className="flex items-center gap-2">
          <FileText className="h-4 w-4" />
          Submit Case Study
        </Button>
      </div>

      {/* Search and Filters */}
      <div className="flex flex-col md:flex-row gap-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
          <Input
            placeholder="Search case studies, industries, or technologies..."
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
            value={selectedType}
            onChange={(e) => setSelectedType(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md text-sm"
          >
            {projectTypes.map(type => (
              <option key={type} value={type}>{type}</option>
            ))}
          </select>

          <select
            value={selectedDifficulty}
            onChange={(e) => setSelectedDifficulty(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md text-sm"
          >
            <option value="all">All Levels</option>
            <option value="Basic">Basic</option>
            <option value="Intermediate">Intermediate</option>
            <option value="Advanced">Advanced</option>
            <option value="Expert">Expert</option>
          </select>
        </div>
      </div>

      {/* Case Studies Grid */}
      <div className="space-y-6">
        {filteredCaseStudies.map(caseStudy => (
          <Card key={caseStudy.id} className="hover:shadow-lg transition-shadow">
            <CardContent className="p-8">
              {/* Header */}
              <div className="flex items-start justify-between mb-6">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    {caseStudy.isFeatured && (
                      <Badge className="bg-yellow-100 text-yellow-800">
                        <Star className="h-3 w-3 mr-1" />
                        Featured
                      </Badge>
                    )}
                    <Badge className={`text-xs ${getDifficultyColor(caseStudy.difficulty)}`}>
                      {caseStudy.difficulty}
                    </Badge>
                    <Badge variant="outline">{caseStudy.industry}</Badge>
                  </div>
                  <h3 className="text-xl font-bold text-gray-900 mb-2 hover:text-blue-600 cursor-pointer">
                    {caseStudy.title}
                  </h3>
                  <p className="text-gray-600 mb-4">
                    {caseStudy.summary}
                  </p>
                </div>
              </div>

              {/* Specialist Info */}
              <div className="flex items-center gap-4 mb-6 p-4 bg-gray-50 rounded-lg">
                <Avatar className="h-12 w-12">
                  <AvatarImage src={caseStudy.specialist.avatar} />
                  <AvatarFallback>
                    {caseStudy.specialist.name.split(' ').map(n => n[0]).join('')}
                  </AvatarFallback>
                </Avatar>
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <h4 className="font-semibold">{caseStudy.specialist.name}</h4>
                    {caseStudy.specialist.verified && (
                      <Badge variant="outline" className="text-blue-600 border-blue-600">
                        <Award className="h-3 w-3 mr-1" />
                        Verified
                      </Badge>
                    )}
                  </div>
                  <p className="text-sm text-gray-600">{caseStudy.specialist.title}</p>
                  <div className="flex items-center gap-1 mt-1">
                    <Star className="h-3 w-3 fill-yellow-400 text-yellow-400" />
                    <span className="text-sm font-medium">{caseStudy.specialist.rating}</span>
                  </div>
                </div>
              </div>

              {/* Project Overview */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                <div className="text-center p-3 bg-blue-50 rounded-lg">
                  <div className="text-sm text-gray-600">Duration</div>
                  <div className="font-semibold">{caseStudy.project.duration}</div>
                </div>
                <div className="text-center p-3 bg-green-50 rounded-lg">
                  <div className="text-sm text-gray-600">Team Size</div>
                  <div className="font-semibold">{caseStudy.project.teamSize} people</div>
                </div>
                <div className="text-center p-3 bg-purple-50 rounded-lg">
                  <div className="text-sm text-gray-600">Client Size</div>
                  <div className="font-semibold text-xs">{caseStudy.client.size}</div>
                </div>
                <div className="text-center p-3 bg-orange-50 rounded-lg">
                  <div className="text-sm text-gray-600">Budget Range</div>
                  <div className="font-semibold text-xs">{caseStudy.project.budget}</div>
                </div>
              </div>

              {/* Key Results */}
              {Object.keys(caseStudy.results).length > 0 && (
                <div className="mb-6">
                  <h5 className="font-semibold mb-3 flex items-center gap-2">
                    <TrendingUp className="h-4 w-4 text-green-600" />
                    Key Results
                  </h5>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {Object.entries(caseStudy.results).filter(([_, value]) => value).map(([key, value]) => (
                      <div key={key} className="flex justify-between items-center p-3 bg-green-50 rounded-lg">
                        <span className="text-sm text-gray-600 capitalize">
                          {key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}
                        </span>
                        <span className="font-semibold text-green-800">{value}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Key Achievements */}
              <div className="mb-6">
                <h5 className="font-semibold mb-3">Key Achievements</h5>
                <ul className="space-y-2">
                  {caseStudy.keyAchievements.slice(0, 3).map((achievement, index) => (
                    <li key={index} className="flex items-start gap-2">
                      <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0" />
                      <span className="text-sm text-gray-700">{achievement}</span>
                    </li>
                  ))}
                  {caseStudy.keyAchievements.length > 3 && (
                    <li className="text-sm text-blue-600 cursor-pointer hover:underline">
                      +{caseStudy.keyAchievements.length - 3} more achievements...
                    </li>
                  )}
                </ul>
              </div>

              {/* Technologies */}
              <div className="mb-6">
                <h5 className="font-semibold mb-3">Technologies & Frameworks</h5>
                <div className="flex flex-wrap gap-2">
                  {caseStudy.technologiesUsed.map(tech => (
                    <Badge key={tech} variant="secondary" className="text-xs">
                      {tech}
                    </Badge>
                  ))}
                </div>
              </div>

              {/* Tags */}
              <div className="mb-6">
                <div className="flex flex-wrap gap-2">
                  {caseStudy.tags.map(tag => (
                    <Badge key={tag} variant="outline" className="text-xs">
                      #{tag}
                    </Badge>
                  ))}
                </div>
              </div>

              {/* Stats and Actions */}
              <div className="flex items-center justify-between pt-4 border-t">
                <div className="flex items-center gap-4 text-sm text-gray-500">
                  <div className="flex items-center gap-1">
                    <Eye className="h-4 w-4" />
                    <span>{caseStudy.views.toLocaleString()}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Download className="h-4 w-4" />
                    <span>{caseStudy.downloads.toLocaleString()}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                    <span>{caseStudy.rating}</span>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  {caseStudy.attachments.length > 0 && (
                    <Button variant="outline" size="sm">
                      <Download className="h-3 w-3 mr-1" />
                      Download ({caseStudy.attachments.length})
                    </Button>
                  )}
                  <Button size="sm">
                    View Full Case Study
                    <ArrowRight className="h-3 w-3 ml-1" />
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* No Results */}
      {filteredCaseStudies.length === 0 && (
        <div className="text-center py-12">
          <FileText className="h-12 w-12 mx-auto text-gray-300 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No case studies found</h3>
          <p className="text-gray-600 mb-4">
            Try adjusting your search criteria or filters
          </p>
          <Button onClick={() => {
            setSearchQuery('')
            setSelectedIndustry('All Industries')
            setSelectedType('All Types')
            setSelectedDifficulty('all')
          }}>
            Clear Filters
          </Button>
        </div>
      )}

      {/* Case Study Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-8">
        <Card>
          <CardContent className="p-4 text-center">
            <FileText className="h-8 w-8 mx-auto mb-2 text-blue-600" />
            <div className="text-2xl font-bold">{mockCaseStudies.length}</div>
            <div className="text-sm text-gray-600">Case Studies</div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4 text-center">
            <Users className="h-8 w-8 mx-auto mb-2 text-green-600" />
            <div className="text-2xl font-bold">
              {new Set(mockCaseStudies.map(cs => cs.specialist.name)).size}
            </div>
            <div className="text-sm text-gray-600">Contributing Experts</div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4 text-center">
            <Building className="h-8 w-8 mx-auto mb-2 text-purple-600" />
            <div className="text-2xl font-bold">
              {new Set(mockCaseStudies.map(cs => cs.industry)).size}
            </div>
            <div className="text-sm text-gray-600">Industries Covered</div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4 text-center">
            <Download className="h-8 w-8 mx-auto mb-2 text-orange-600" />
            <div className="text-2xl font-bold">
              {mockCaseStudies.reduce((sum, cs) => sum + cs.downloads, 0).toLocaleString()}
            </div>
            <div className="text-sm text-gray-600">Total Downloads</div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}