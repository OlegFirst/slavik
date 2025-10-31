'use client'

import React, { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import {
  Users,
  Search,
  MapPin,
  Star,
  MessageCircle,
  Calendar,
  Award,
  Building,
  Clock,
  Filter,
  UserCheck,
  Mail
} from 'lucide-react'

interface Expert {
  id: string
  name: string
  title: string
  company: string
  avatar?: string
  location: string
  specializations: string[]
  certifications: string[]
  rating: number
  reviewCount: number
  responseTime: string
  status: 'online' | 'away' | 'offline'
  lastActive: string
  isVerified: boolean
  yearsExperience: number
  projectsCompleted: number
  bio: string
}

const mockExperts: Expert[] = [
  {
    id: '1',
    name: 'Dr. Sarah Martinez',
    title: 'Senior BCM Consultant',
    company: 'Resilience Consulting Group',
    location: 'New York, USA',
    specializations: ['ISO 22301', 'Crisis Management', 'Risk Assessment'],
    certifications: ['CBCP', 'MBCI', 'ISO 22301 Lead Auditor'],
    rating: 4.9,
    reviewCount: 127,
    responseTime: '< 2 hours',
    status: 'online',
    lastActive: 'Active now',
    isVerified: true,
    yearsExperience: 12,
    projectsCompleted: 89,
    bio: 'Specialized in healthcare and financial services BCM implementations with focus on regulatory compliance.'
  },
  {
    id: '2',
    name: 'Michael Thompson',
    title: 'Risk Management Director',
    company: 'Global Risk Solutions',
    location: 'London, UK',
    specializations: ['Supply Chain Risk', 'Cyber Resilience', 'Business Impact Analysis'],
    certifications: ['CBCP', 'CISA', 'PMP'],
    rating: 4.8,
    reviewCount: 95,
    responseTime: '< 4 hours',
    status: 'online',
    lastActive: '15 min ago',
    isVerified: true,
    yearsExperience: 15,
    projectsCompleted: 134,
    bio: 'Expert in technology risk management and digital transformation resilience strategies.'
  },
  {
    id: '3',
    name: 'Jennifer Liu',
    title: 'Crisis Communication Specialist',
    company: 'CrisisComm Experts',
    location: 'Toronto, Canada',
    specializations: ['Crisis Communication', 'Stakeholder Management', 'Media Relations'],
    certifications: ['APR', 'CBCP', 'Crisis Communications Certificate'],
    rating: 4.7,
    reviewCount: 78,
    responseTime: '< 6 hours',
    status: 'away',
    lastActive: '2 hours ago',
    isVerified: true,
    yearsExperience: 9,
    projectsCompleted: 67,
    bio: 'Specialized in crisis communication strategies for multinational corporations and public sector organizations.'
  },
  {
    id: '4',
    name: 'Robert Chen',
    title: 'BCM Program Manager',
    company: 'Enterprise Solutions Inc.',
    location: 'Singapore',
    specializations: ['BCM Program Management', 'Training & Awareness', 'Compliance Auditing'],
    certifications: ['MBCI', 'CBCP', 'Six Sigma Black Belt'],
    rating: 4.6,
    reviewCount: 52,
    responseTime: '< 8 hours',
    status: 'offline',
    lastActive: '1 day ago',
    isVerified: true,
    yearsExperience: 11,
    projectsCompleted: 73,
    bio: 'Focus on establishing comprehensive BCM programs for manufacturing and logistics companies.'
  }
]

const specializations = [
  'All Specializations',
  'ISO 22301',
  'Crisis Management',
  'Risk Assessment',
  'Supply Chain Risk',
  'Cyber Resilience',
  'Business Impact Analysis',
  'Crisis Communication',
  'BCM Program Management',
  'Training & Awareness'
]

const locations = [
  'All Locations',
  'North America',
  'Europe',
  'Asia Pacific',
  'Latin America',
  'Middle East & Africa'
]

export function ExpertDirectory() {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedSpecialization, setSelectedSpecialization] = useState('All Specializations')
  const [selectedLocation, setSelectedLocation] = useState('All Locations')
  const [statusFilter, setStatusFilter] = useState('all')

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online': return 'bg-green-500'
      case 'away': return 'bg-yellow-500'
      case 'offline': return 'bg-gray-400'
      default: return 'bg-gray-400'
    }
  }

  const filteredExperts = mockExperts.filter(expert => {
    const matchesSearch = expert.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         expert.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         expert.specializations.some(spec => spec.toLowerCase().includes(searchQuery.toLowerCase()))

    const matchesSpecialization = selectedSpecialization === 'All Specializations' ||
                                 expert.specializations.includes(selectedSpecialization)

    const matchesLocation = selectedLocation === 'All Locations' ||
                           expert.location.includes(selectedLocation.replace(' & ', ' '))

    const matchesStatus = statusFilter === 'all' || expert.status === statusFilter

    return matchesSearch && matchesSpecialization && matchesLocation && matchesStatus
  })

  return (
    <div className="space-y-6">
      {/* Expert Directory Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold">Expert Directory</h2>
          <p className="text-gray-600">Connect with verified BCM professionals and thought leaders</p>
        </div>
        <Button className="flex items-center gap-2">
          <UserCheck className="h-4 w-4" />
          Become a Verified Expert
        </Button>
      </div>

      {/* Search and Filters */}
      <div className="flex flex-col md:flex-row gap-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
          <Input
            placeholder="Search experts by name, title, or specialization..."
            className="pl-10"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>

        <div className="flex gap-2">
          <select
            value={selectedSpecialization}
            onChange={(e) => setSelectedSpecialization(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md text-sm"
          >
            {specializations.map(spec => (
              <option key={spec} value={spec}>{spec}</option>
            ))}
          </select>

          <select
            value={selectedLocation}
            onChange={(e) => setSelectedLocation(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md text-sm"
          >
            {locations.map(location => (
              <option key={location} value={location}>{location}</option>
            ))}
          </select>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md text-sm"
          >
            <option value="all">All Status</option>
            <option value="online">Online</option>
            <option value="away">Away</option>
            <option value="offline">Offline</option>
          </select>
        </div>
      </div>

      {/* Expert Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        {filteredExperts.map(expert => (
          <Card key={expert.id} className="hover:shadow-lg transition-shadow">
            <CardContent className="p-6">
              {/* Expert Header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className="relative">
                    <Avatar className="h-12 w-12">
                      <AvatarImage src={expert.avatar} alt={expert.name} />
                      <AvatarFallback>
                        {expert.name.split(' ').map(n => n[0]).join('')}
                      </AvatarFallback>
                    </Avatar>
                    <div
                      className={`absolute -bottom-1 -right-1 w-4 h-4 rounded-full border-2 border-white ${getStatusColor(expert.status)}`}
                      title={expert.status}
                    />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <h3 className="font-semibold text-gray-900 truncate">{expert.name}</h3>
                      {expert.isVerified && (
                        <UserCheck className="h-4 w-4 text-blue-500" />
                      )}
                    </div>
                    <p className="text-sm text-gray-600 truncate">{expert.title}</p>
                    <div className="flex items-center gap-1 mt-1">
                      <Building className="h-3 w-3 text-gray-400" />
                      <p className="text-xs text-gray-500 truncate">{expert.company}</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Rating and Stats */}
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <div className="flex items-center gap-1">
                    <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                    <span className="font-medium">{expert.rating}</span>
                    <span className="text-sm text-gray-500">({expert.reviewCount})</span>
                  </div>
                </div>
                <div className="flex items-center gap-1 text-xs text-gray-500">
                  <Clock className="h-3 w-3" />
                  <span>Responds in {expert.responseTime}</span>
                </div>
              </div>

              {/* Location */}
              <div className="flex items-center gap-1 mb-3">
                <MapPin className="h-4 w-4 text-gray-400" />
                <span className="text-sm text-gray-600">{expert.location}</span>
              </div>

              {/* Bio */}
              <p className="text-sm text-gray-600 mb-4 line-clamp-2">
                {expert.bio}
              </p>

              {/* Specializations */}
              <div className="mb-4">
                <div className="flex flex-wrap gap-1">
                  {expert.specializations.slice(0, 3).map(spec => (
                    <Badge key={spec} variant="secondary" className="text-xs">
                      {spec}
                    </Badge>
                  ))}
                  {expert.specializations.length > 3 && (
                    <Badge variant="outline" className="text-xs">
                      +{expert.specializations.length - 3} more
                    </Badge>
                  )}
                </div>
              </div>

              {/* Certifications */}
              <div className="mb-4">
                <div className="flex items-center gap-1 mb-1">
                  <Award className="h-3 w-3 text-gray-400" />
                  <span className="text-xs text-gray-600">Certifications:</span>
                </div>
                <div className="flex flex-wrap gap-1">
                  {expert.certifications.slice(0, 2).map(cert => (
                    <Badge key={cert} variant="outline" className="text-xs">
                      {cert}
                    </Badge>
                  ))}
                  {expert.certifications.length > 2 && (
                    <span className="text-xs text-gray-500">
                      +{expert.certifications.length - 2} more
                    </span>
                  )}
                </div>
              </div>

              {/* Stats */}
              <div className="flex justify-between text-xs text-gray-500 mb-4">
                <span>{expert.yearsExperience} years experience</span>
                <span>{expert.projectsCompleted} projects completed</span>
              </div>

              {/* Status */}
              <div className="flex items-center gap-1 text-xs text-gray-500 mb-4">
                <div className={`w-2 h-2 rounded-full ${getStatusColor(expert.status)}`} />
                <span className="capitalize">{expert.status}</span>
                <span>•</span>
                <span>{expert.lastActive}</span>
              </div>

              {/* Actions */}
              <div className="flex gap-2">
                <Button className="flex-1" size="sm">
                  <MessageCircle className="h-3 w-3 mr-1" />
                  Message
                </Button>
                <Button variant="outline" size="sm">
                  <Mail className="h-3 w-3 mr-1" />
                  Email
                </Button>
                <Button variant="outline" size="sm">
                  <Calendar className="h-3 w-3" />
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* No Results */}
      {filteredExperts.length === 0 && (
        <div className="text-center py-12">
          <Users className="h-12 w-12 mx-auto text-gray-300 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No experts found</h3>
          <p className="text-gray-600 mb-4">
            Try adjusting your search criteria or filters
          </p>
          <Button onClick={() => {
            setSearchQuery('')
            setSelectedSpecialization('All Specializations')
            setSelectedLocation('All Locations')
            setStatusFilter('all')
          }}>
            Clear Filters
          </Button>
        </div>
      )}

      {/* Directory Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-8">
        <Card>
          <CardContent className="p-4 text-center">
            <Users className="h-8 w-8 mx-auto mb-2 text-blue-600" />
            <div className="text-2xl font-bold">{mockExperts.length}</div>
            <div className="text-sm text-gray-600">Verified Experts</div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4 text-center">
            <Award className="h-8 w-8 mx-auto mb-2 text-green-600" />
            <div className="text-2xl font-bold">
              {mockExperts.reduce((sum, expert) => sum + expert.certifications.length, 0)}
            </div>
            <div className="text-sm text-gray-600">Total Certifications</div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4 text-center">
            <Star className="h-8 w-8 mx-auto mb-2 text-yellow-600" />
            <div className="text-2xl font-bold">4.8</div>
            <div className="text-sm text-gray-600">Average Rating</div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4 text-center">
            <Clock className="h-8 w-8 mx-auto mb-2 text-purple-600" />
            <div className="text-2xl font-bold">&lt; 4h</div>
            <div className="text-sm text-gray-600">Avg Response Time</div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}