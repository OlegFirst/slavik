'use client'

import React, { useState } from 'react'
import { AppLayout } from '@/components/layout/AppLayout'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import {
  User,
  Mail,
  Phone,
  MapPin,
  Building,
  Award,
  Star,
  Calendar,
  DollarSign,
  FileText,
  Camera,
  Plus,
  X,
  Save,
  Edit,
  Eye
} from 'lucide-react'

export default function SpecialistProfilePage() {
  const [isEditing, setIsEditing] = useState(false)
  const [profileData, setProfileData] = useState({
    firstName: 'John',
    lastName: 'Smith',
    email: 'john.smith@example.com',
    phone: '+1 (555) 123-4567',
    title: 'Senior BCM Consultant',
    company: 'BCM Solutions Inc.',
    location: 'New York, USA',
    bio: 'Experienced Business Continuity Management consultant with over 10 years of expertise in risk assessment, crisis management, and regulatory compliance. Specialized in healthcare and financial services sectors.',
    hourlyRate: 150,
    availability: 'Available',
    specializations: ['ISO 22301', 'Crisis Management', 'Risk Assessment', 'Business Impact Analysis'],
    certifications: ['CBCP', 'MBCI', 'ISO 22301 Lead Auditor'],
    languages: ['English', 'Spanish'],
    website: 'https://johnsmith-bcm.com',
    linkedin: 'https://linkedin.com/in/johnsmith-bcm'
  })

  const handleSave = () => {
    setIsEditing(false)
    // In real app, this would save to API
    console.log('Profile updated:', profileData)
  }

  const addSpecialization = () => {
    const newSpec = prompt('Enter new specialization:')
    if (newSpec && !profileData.specializations.includes(newSpec)) {
      setProfileData(prev => ({
        ...prev,
        specializations: [...prev.specializations, newSpec]
      }))
    }
  }

  const removeSpecialization = (spec: string) => {
    setProfileData(prev => ({
      ...prev,
      specializations: prev.specializations.filter(s => s !== spec)
    }))
  }

  const addCertification = () => {
    const newCert = prompt('Enter new certification:')
    if (newCert && !profileData.certifications.includes(newCert)) {
      setProfileData(prev => ({
        ...prev,
        certifications: [...prev.certifications, newCert]
      }))
    }
  }

  const removeCertification = (cert: string) => {
    setProfileData(prev => ({
      ...prev,
      certifications: prev.certifications.filter(c => c !== cert)
    }))
  }

  return (
    <AppLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold">My Profile</h1>
            <p className="text-gray-600">Manage your professional profile and settings</p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" asChild>
              <a href="/portfolio" target="_blank">
                <Eye className="h-4 w-4 mr-2" />
                View Public Profile
              </a>
            </Button>
            {isEditing ? (
              <div className="flex gap-2">
                <Button variant="outline" onClick={() => setIsEditing(false)}>
                  Cancel
                </Button>
                <Button onClick={handleSave}>
                  <Save className="h-4 w-4 mr-2" />
                  Save Changes
                </Button>
              </div>
            ) : (
              <Button onClick={() => setIsEditing(true)}>
                <Edit className="h-4 w-4 mr-2" />
                Edit Profile
              </Button>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Profile Overview */}
          <div className="lg:col-span-1 space-y-6">
            <Card>
              <CardContent className="p-6 text-center">
                <div className="relative mb-4">
                  <Avatar className="h-24 w-24 mx-auto">
                    <AvatarImage src="/api/placeholder/150/150" alt="Profile" />
                    <AvatarFallback className="text-2xl">
                      {profileData.firstName[0]}{profileData.lastName[0]}
                    </AvatarFallback>
                  </Avatar>
                  {isEditing && (
                    <Button
                      size="sm"
                      className="absolute -bottom-2 left-1/2 transform -translate-x-1/2"
                      variant="outline"
                    >
                      <Camera className="h-3 w-3" />
                    </Button>
                  )}
                </div>
                <h3 className="text-xl font-semibold">
                  {profileData.firstName} {profileData.lastName}
                </h3>
                <p className="text-gray-600">{profileData.title}</p>
                <div className="flex items-center justify-center gap-1 mt-2">
                  <Building className="h-4 w-4 text-gray-400" />
                  <span className="text-sm text-gray-600">{profileData.company}</span>
                </div>
                <div className="flex items-center justify-center gap-1 mt-1">
                  <MapPin className="h-4 w-4 text-gray-400" />
                  <span className="text-sm text-gray-600">{profileData.location}</span>
                </div>

                <div className="flex items-center justify-center mt-4">
                  <div className="flex items-center gap-1">
                    <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                    <span className="font-medium">4.9</span>
                    <span className="text-sm text-gray-500">(47 reviews)</span>
                  </div>
                </div>

                <Badge variant="secondary" className="mt-3">
                  {profileData.availability}
                </Badge>
              </CardContent>
            </Card>

            {/* Quick Stats */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Performance</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Projects Completed</span>
                  <span className="font-medium">89</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Success Rate</span>
                  <span className="font-medium">98%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Response Time</span>
                  <span className="font-medium">&lt; 2 hours</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Total Earned</span>
                  <span className="font-medium">$127,500</span>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Profile Details */}
          <div className="lg:col-span-2 space-y-6">
            {/* Basic Information */}
            <Card>
              <CardHeader>
                <CardTitle>Basic Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">First Name</label>
                    {isEditing ? (
                      <Input
                        value={profileData.firstName}
                        onChange={(e) => setProfileData(prev => ({ ...prev, firstName: e.target.value }))}
                      />
                    ) : (
                      <p className="py-2">{profileData.firstName}</p>
                    )}
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Last Name</label>
                    {isEditing ? (
                      <Input
                        value={profileData.lastName}
                        onChange={(e) => setProfileData(prev => ({ ...prev, lastName: e.target.value }))}
                      />
                    ) : (
                      <p className="py-2">{profileData.lastName}</p>
                    )}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Professional Title</label>
                  {isEditing ? (
                    <Input
                      value={profileData.title}
                      onChange={(e) => setProfileData(prev => ({ ...prev, title: e.target.value }))}
                    />
                  ) : (
                    <p className="py-2">{profileData.title}</p>
                  )}
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">Company</label>
                    {isEditing ? (
                      <Input
                        value={profileData.company}
                        onChange={(e) => setProfileData(prev => ({ ...prev, company: e.target.value }))}
                      />
                    ) : (
                      <p className="py-2">{profileData.company}</p>
                    )}
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Location</label>
                    {isEditing ? (
                      <Input
                        value={profileData.location}
                        onChange={(e) => setProfileData(prev => ({ ...prev, location: e.target.value }))}
                      />
                    ) : (
                      <p className="py-2">{profileData.location}</p>
                    )}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Professional Bio</label>
                  {isEditing ? (
                    <Textarea
                      value={profileData.bio}
                      onChange={(e) => setProfileData(prev => ({ ...prev, bio: e.target.value }))}
                      rows={4}
                    />
                  ) : (
                    <p className="py-2 text-gray-700">{profileData.bio}</p>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Contact Information */}
            <Card>
              <CardHeader>
                <CardTitle>Contact Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">Email</label>
                    {isEditing ? (
                      <Input
                        type="email"
                        value={profileData.email}
                        onChange={(e) => setProfileData(prev => ({ ...prev, email: e.target.value }))}
                      />
                    ) : (
                      <p className="py-2">{profileData.email}</p>
                    )}
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Phone</label>
                    {isEditing ? (
                      <Input
                        value={profileData.phone}
                        onChange={(e) => setProfileData(prev => ({ ...prev, phone: e.target.value }))}
                      />
                    ) : (
                      <p className="py-2">{profileData.phone}</p>
                    )}
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">Website</label>
                    {isEditing ? (
                      <Input
                        value={profileData.website}
                        onChange={(e) => setProfileData(prev => ({ ...prev, website: e.target.value }))}
                      />
                    ) : (
                      <p className="py-2">
                        <a href={profileData.website} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                          {profileData.website}
                        </a>
                      </p>
                    )}
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">LinkedIn</label>
                    {isEditing ? (
                      <Input
                        value={profileData.linkedin}
                        onChange={(e) => setProfileData(prev => ({ ...prev, linkedin: e.target.value }))}
                      />
                    ) : (
                      <p className="py-2">
                        <a href={profileData.linkedin} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                          {profileData.linkedin}
                        </a>
                      </p>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Expertise & Rates */}
            <Card>
              <CardHeader>
                <CardTitle>Expertise & Rates</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div>
                  <label className="block text-sm font-medium mb-2">Hourly Rate (USD)</label>
                  {isEditing ? (
                    <div className="relative">
                      <DollarSign className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                      <Input
                        type="number"
                        value={profileData.hourlyRate}
                        onChange={(e) => setProfileData(prev => ({ ...prev, hourlyRate: parseInt(e.target.value) || 0 }))}
                        className="pl-10"
                      />
                    </div>
                  ) : (
                    <p className="py-2">${profileData.hourlyRate}/hour</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Specializations</label>
                  <div className="flex flex-wrap gap-2">
                    {profileData.specializations.map(spec => (
                      <Badge key={spec} variant="secondary" className="flex items-center gap-1">
                        {spec}
                        {isEditing && (
                          <button
                            onClick={() => removeSpecialization(spec)}
                            className="ml-1 hover:bg-gray-300 rounded-full p-0.5"
                          >
                            <X className="h-3 w-3" />
                          </button>
                        )}
                      </Badge>
                    ))}
                    {isEditing && (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={addSpecialization}
                        className="h-7"
                      >
                        <Plus className="h-3 w-3 mr-1" />
                        Add
                      </Button>
                    )}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Certifications</label>
                  <div className="flex flex-wrap gap-2">
                    {profileData.certifications.map(cert => (
                      <Badge key={cert} variant="outline" className="flex items-center gap-1">
                        <Award className="h-3 w-3" />
                        {cert}
                        {isEditing && (
                          <button
                            onClick={() => removeCertification(cert)}
                            className="ml-1 hover:bg-gray-300 rounded-full p-0.5"
                          >
                            <X className="h-3 w-3" />
                          </button>
                        )}
                      </Badge>
                    ))}
                    {isEditing && (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={addCertification}
                        className="h-7"
                      >
                        <Plus className="h-3 w-3 mr-1" />
                        Add
                      </Button>
                    )}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Languages</label>
                  <div className="flex flex-wrap gap-2">
                    {profileData.languages.map(lang => (
                      <Badge key={lang} variant="outline">
                        {lang}
                      </Badge>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </AppLayout>
  )
}