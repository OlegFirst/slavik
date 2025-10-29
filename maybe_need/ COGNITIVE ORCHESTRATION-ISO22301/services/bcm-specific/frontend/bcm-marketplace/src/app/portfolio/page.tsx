'use client'

import React, { useState } from 'react'
import { AppLayout } from '@/components/layout/AppLayout'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import {
  FileText,
  Upload,
  Plus,
  Eye,
  Edit,
  Trash2,
  Star,
  Download,
  Calendar,
  Building,
  Users,
  Award,
  ExternalLink
} from 'lucide-react'

interface PortfolioItem {
  id: string
  title: string
  description: string
  industry: string
  projectType: string
  duration: string
  teamSize: number
  completionDate: string
  role: string
  keyAchievements: string[]
  technologiesUsed: string[]
  attachments: {
    name: string
    type: string
    size: string
    url: string
  }[]
  isPublic: boolean
  isFeatured: boolean
  views: number
  downloads: number
}

const mockPortfolioItems: PortfolioItem[] = [
  {
    id: '1',
    title: 'Financial Services BCM Implementation',
    description: 'Led comprehensive BCM program implementation for a major international bank with 50,000+ employees across 40 countries.',
    industry: 'Financial Services',
    projectType: 'BCM Program Implementation',
    duration: '18 months',
    teamSize: 25,
    completionDate: '2024-03-15',
    role: 'Lead BCM Consultant',
    keyAchievements: [
      'Reduced RTO from 24 hours to 2 hours for critical systems',
      'Achieved 99.99% uptime during 3 major crisis events',
      'Passed all regulatory audits with zero critical findings',
      'Trained 15,000+ staff members across all regions'
    ],
    technologiesUsed: [
      'MetricStream BCM',
      'ServiceNow ITBM',
      'Microsoft Azure Site Recovery',
      'Zerto Disaster Recovery'
    ],
    attachments: [
      { name: 'Executive Summary.pdf', type: 'PDF', size: '2.1 MB', url: '#' },
      { name: 'Implementation Timeline.xlsx', type: 'Excel', size: '850 KB', url: '#' }
    ],
    isPublic: true,
    isFeatured: true,
    views: 1250,
    downloads: 340
  },
  {
    id: '2',
    title: 'Healthcare Crisis Management Program',
    description: 'Emergency BCM implementation for 15-hospital network during COVID-19 pandemic.',
    industry: 'Healthcare',
    projectType: 'Crisis Management',
    duration: '8 months',
    teamSize: 12,
    completionDate: '2021-11-30',
    role: 'Crisis Management Lead',
    keyAchievements: [
      'Maintained 100% emergency services availability',
      'Reduced patient transfer times by 40%',
      'Implemented surge capacity for 300% patient increase'
    ],
    technologiesUsed: [
      'Epic EHR Integration',
      'Telehealth Platforms',
      'Crisis Communication Systems'
    ],
    attachments: [
      { name: 'Pandemic Response Plan.pdf', type: 'PDF', size: '3.2 MB', url: '#' }
    ],
    isPublic: true,
    isFeatured: false,
    views: 890,
    downloads: 120
  }
]

export default function PortfolioPage() {
  const [showAddForm, setShowAddForm] = useState(false)
  const [portfolioItems, setPortfolioItems] = useState(mockPortfolioItems)
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    industry: '',
    projectType: '',
    duration: '',
    teamSize: '',
    completionDate: '',
    role: '',
    keyAchievements: [''],
    technologiesUsed: [''],
    isPublic: true
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    // In real app, this would call API
    console.log('Submitting portfolio item:', formData)
    setShowAddForm(false)
    // Reset form
    setFormData({
      title: '',
      description: '',
      industry: '',
      projectType: '',
      duration: '',
      teamSize: '',
      completionDate: '',
      role: '',
      keyAchievements: [''],
      technologiesUsed: [''],
      isPublic: true
    })
  }

  const addArrayField = (field: 'keyAchievements' | 'technologiesUsed') => {
    setFormData(prev => ({
      ...prev,
      [field]: [...prev[field], '']
    }))
  }

  const updateArrayField = (field: 'keyAchievements' | 'technologiesUsed', index: number, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: prev[field].map((item, i) => i === index ? value : item)
    }))
  }

  const removeArrayField = (field: 'keyAchievements' | 'technologiesUsed', index: number) => {
    setFormData(prev => ({
      ...prev,
      [field]: prev[field].filter((_, i) => i !== index)
    }))
  }

  if (showAddForm) {
    return (
      <AppLayout>
        <div className="max-w-4xl mx-auto space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold">Add Portfolio Item</h1>
              <p className="text-gray-600">Showcase your BCM expertise and projects</p>
            </div>
            <Button variant="outline" onClick={() => setShowAddForm(false)}>
              Cancel
            </Button>
          </div>

          <Card>
            <CardContent className="p-6">
              <form onSubmit={handleSubmit} className="space-y-6">
                {/* Basic Information */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">Project Title *</label>
                    <Input
                      value={formData.title}
                      onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
                      placeholder="e.g., Financial Services BCM Implementation"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">Your Role *</label>
                    <Input
                      value={formData.role}
                      onChange={(e) => setFormData(prev => ({ ...prev, role: e.target.value }))}
                      placeholder="e.g., Lead BCM Consultant"
                      required
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Project Description *</label>
                  <Textarea
                    value={formData.description}
                    onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                    placeholder="Describe the project scope, objectives, and your contributions..."
                    rows={4}
                    required
                  />
                </div>

                {/* Project Details */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">Industry</label>
                    <select
                      value={formData.industry}
                      onChange={(e) => setFormData(prev => ({ ...prev, industry: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md"
                    >
                      <option value="">Select Industry</option>
                      <option value="Financial Services">Financial Services</option>
                      <option value="Healthcare">Healthcare</option>
                      <option value="Manufacturing">Manufacturing</option>
                      <option value="Technology">Technology</option>
                      <option value="Government">Government</option>
                      <option value="Energy">Energy & Utilities</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">Project Type</label>
                    <select
                      value={formData.projectType}
                      onChange={(e) => setFormData(prev => ({ ...prev, projectType: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md"
                    >
                      <option value="">Select Type</option>
                      <option value="BCM Program Implementation">BCM Program Implementation</option>
                      <option value="Risk Assessment">Risk Assessment</option>
                      <option value="Business Impact Analysis">Business Impact Analysis</option>
                      <option value="Crisis Management">Crisis Management</option>
                      <option value="Training Program">Training Program</option>
                      <option value="BCM Audit">BCM Audit</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">Duration</label>
                    <Input
                      value={formData.duration}
                      onChange={(e) => setFormData(prev => ({ ...prev, duration: e.target.value }))}
                      placeholder="e.g., 12 months"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">Team Size</label>
                    <Input
                      type="number"
                      value={formData.teamSize}
                      onChange={(e) => setFormData(prev => ({ ...prev, teamSize: e.target.value }))}
                      placeholder="e.g., 15"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Completion Date</label>
                  <Input
                    type="date"
                    value={formData.completionDate}
                    onChange={(e) => setFormData(prev => ({ ...prev, completionDate: e.target.value }))}
                  />
                </div>

                {/* Key Achievements */}
                <div>
                  <label className="block text-sm font-medium mb-2">Key Achievements</label>
                  {formData.keyAchievements.map((achievement, index) => (
                    <div key={index} className="flex gap-2 mb-2">
                      <Input
                        value={achievement}
                        onChange={(e) => updateArrayField('keyAchievements', index, e.target.value)}
                        placeholder="Describe a key achievement or result..."
                      />
                      {formData.keyAchievements.length > 1 && (
                        <Button
                          type="button"
                          variant="outline"
                          size="sm"
                          onClick={() => removeArrayField('keyAchievements', index)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      )}
                    </div>
                  ))}
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={() => addArrayField('keyAchievements')}
                  >
                    <Plus className="h-4 w-4 mr-1" />
                    Add Achievement
                  </Button>
                </div>

                {/* Technologies Used */}
                <div>
                  <label className="block text-sm font-medium mb-2">Technologies & Frameworks Used</label>
                  {formData.technologiesUsed.map((tech, index) => (
                    <div key={index} className="flex gap-2 mb-2">
                      <Input
                        value={tech}
                        onChange={(e) => updateArrayField('technologiesUsed', index, e.target.value)}
                        placeholder="e.g., MetricStream BCM, ServiceNow..."
                      />
                      {formData.technologiesUsed.length > 1 && (
                        <Button
                          type="button"
                          variant="outline"
                          size="sm"
                          onClick={() => removeArrayField('technologiesUsed', index)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      )}
                    </div>
                  ))}
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={() => addArrayField('technologiesUsed')}
                  >
                    <Plus className="h-4 w-4 mr-1" />
                    Add Technology
                  </Button>
                </div>

                {/* File Attachments */}
                <div>
                  <label className="block text-sm font-medium mb-2">Attachments (Optional)</label>
                  <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                    <Upload className="h-8 w-8 mx-auto text-gray-400 mb-2" />
                    <p className="text-sm text-gray-600">
                      Drop files here or click to upload
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      Supported: PDF, Word, Excel, PowerPoint (max 10MB each)
                    </p>
                  </div>
                </div>

                {/* Visibility Settings */}
                <div>
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={formData.isPublic}
                      onChange={(e) => setFormData(prev => ({ ...prev, isPublic: e.target.checked }))}
                    />
                    <span className="text-sm font-medium">Make this portfolio item public</span>
                  </label>
                  <p className="text-xs text-gray-500 mt-1">
                    Public items can be viewed by potential clients and included in community case studies
                  </p>
                </div>

                <div className="flex justify-end gap-4">
                  <Button type="button" variant="outline" onClick={() => setShowAddForm(false)}>
                    Cancel
                  </Button>
                  <Button type="submit">
                    Save Portfolio Item
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
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
            <h1 className="text-3xl font-bold">My Portfolio</h1>
            <p className="text-gray-600">
              Showcase your BCM projects and expertise to potential clients
            </p>
          </div>
          <Button onClick={() => setShowAddForm(true)} className="flex items-center gap-2">
            <Plus className="h-4 w-4" />
            Add Portfolio Item
          </Button>
        </div>

        {/* Portfolio Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <FileText className="h-5 w-5 text-blue-600" />
                <div>
                  <div className="text-2xl font-bold">{portfolioItems.length}</div>
                  <div className="text-sm text-gray-600">Portfolio Items</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <Eye className="h-5 w-5 text-green-600" />
                <div>
                  <div className="text-2xl font-bold">
                    {portfolioItems.reduce((sum, item) => sum + item.views, 0).toLocaleString()}
                  </div>
                  <div className="text-sm text-gray-600">Total Views</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <Download className="h-5 w-5 text-purple-600" />
                <div>
                  <div className="text-2xl font-bold">
                    {portfolioItems.reduce((sum, item) => sum + item.downloads, 0)}
                  </div>
                  <div className="text-sm text-gray-600">Total Downloads</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <Award className="h-5 w-5 text-yellow-600" />
                <div>
                  <div className="text-2xl font-bold">
                    {portfolioItems.filter(item => item.isFeatured).length}
                  </div>
                  <div className="text-sm text-gray-600">Featured Items</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Portfolio Items */}
        <div className="space-y-4">
          {portfolioItems.map(item => (
            <Card key={item.id} className="hover:shadow-lg transition-shadow">
              <CardContent className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-xl font-bold text-gray-900">{item.title}</h3>
                      {item.isFeatured && (
                        <Badge className="bg-yellow-100 text-yellow-800">
                          <Star className="h-3 w-3 mr-1" />
                          Featured
                        </Badge>
                      )}
                      <Badge variant={item.isPublic ? "default" : "secondary"}>
                        {item.isPublic ? "Public" : "Private"}
                      </Badge>
                    </div>
                    <p className="text-gray-600 mb-4">{item.description}</p>
                  </div>

                  <div className="flex items-center gap-2">
                    <Button variant="outline" size="sm">
                      <Edit className="h-3 w-3 mr-1" />
                      Edit
                    </Button>
                    <Button variant="outline" size="sm">
                      <Eye className="h-3 w-3 mr-1" />
                      Preview
                    </Button>
                  </div>
                </div>

                {/* Project Details */}
                <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
                  <div className="text-center p-3 bg-blue-50 rounded-lg">
                    <Building className="h-4 w-4 mx-auto mb-1 text-blue-600" />
                    <div className="text-xs text-gray-600">Industry</div>
                    <div className="font-semibold text-sm">{item.industry}</div>
                  </div>
                  <div className="text-center p-3 bg-green-50 rounded-lg">
                    <FileText className="h-4 w-4 mx-auto mb-1 text-green-600" />
                    <div className="text-xs text-gray-600">Type</div>
                    <div className="font-semibold text-sm">{item.projectType}</div>
                  </div>
                  <div className="text-center p-3 bg-purple-50 rounded-lg">
                    <Calendar className="h-4 w-4 mx-auto mb-1 text-purple-600" />
                    <div className="text-xs text-gray-600">Duration</div>
                    <div className="font-semibold text-sm">{item.duration}</div>
                  </div>
                  <div className="text-center p-3 bg-orange-50 rounded-lg">
                    <Users className="h-4 w-4 mx-auto mb-1 text-orange-600" />
                    <div className="text-xs text-gray-600">Team</div>
                    <div className="font-semibold text-sm">{item.teamSize} people</div>
                  </div>
                  <div className="text-center p-3 bg-pink-50 rounded-lg">
                    <Award className="h-4 w-4 mx-auto mb-1 text-pink-600" />
                    <div className="text-xs text-gray-600">Role</div>
                    <div className="font-semibold text-sm">{item.role}</div>
                  </div>
                </div>

                {/* Key Achievements Preview */}
                <div className="mb-4">
                  <h5 className="font-semibold mb-2">Key Achievements</h5>
                  <ul className="space-y-1">
                    {item.keyAchievements.slice(0, 2).map((achievement, index) => (
                      <li key={index} className="flex items-start gap-2">
                        <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0" />
                        <span className="text-sm text-gray-700">{achievement}</span>
                      </li>
                    ))}
                    {item.keyAchievements.length > 2 && (
                      <li className="text-sm text-blue-600">
                        +{item.keyAchievements.length - 2} more achievements
                      </li>
                    )}
                  </ul>
                </div>

                {/* Technologies */}
                <div className="mb-4">
                  <h5 className="font-semibold mb-2">Technologies Used</h5>
                  <div className="flex flex-wrap gap-2">
                    {item.technologiesUsed.map(tech => (
                      <Badge key={tech} variant="secondary" className="text-xs">
                        {tech}
                      </Badge>
                    ))}
                  </div>
                </div>

                {/* Attachments */}
                {item.attachments.length > 0 && (
                  <div className="mb-4">
                    <h5 className="font-semibold mb-2">Attachments ({item.attachments.length})</h5>
                    <div className="flex flex-wrap gap-2">
                      {item.attachments.map(attachment => (
                        <div key={attachment.name} className="flex items-center gap-2 p-2 bg-gray-50 rounded-lg text-sm">
                          <FileText className="h-4 w-4 text-gray-500" />
                          <span>{attachment.name}</span>
                          <span className="text-gray-500">({attachment.size})</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Stats */}
                <div className="flex items-center justify-between pt-4 border-t">
                  <div className="flex items-center gap-4 text-sm text-gray-500">
                    <div className="flex items-center gap-1">
                      <Eye className="h-4 w-4" />
                      <span>{item.views.toLocaleString()} views</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Download className="h-4 w-4" />
                      <span>{item.downloads} downloads</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Calendar className="h-4 w-4" />
                      <span>Completed {item.completionDate}</span>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    {item.isPublic && (
                      <Button variant="outline" size="sm">
                        <ExternalLink className="h-3 w-3 mr-1" />
                        Public Link
                      </Button>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {portfolioItems.length === 0 && (
          <div className="text-center py-12">
            <FileText className="h-12 w-12 mx-auto text-gray-300 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No portfolio items yet</h3>
            <p className="text-gray-600 mb-4">
              Start showcasing your BCM expertise by adding your first portfolio item
            </p>
            <Button onClick={() => setShowAddForm(true)}>
              <Plus className="h-4 w-4 mr-1" />
              Add Portfolio Item
            </Button>
          </div>
        )}
      </div>
    </AppLayout>
  )
}