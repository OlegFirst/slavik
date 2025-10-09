'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Alert, AlertDescription } from '@/components/ui/alert'
import {
  Search,
  Download,
  Star,
  Users,
  Clock,
  Shield,
  AlertTriangle,
  CheckCircle,
  FileText,
  Settings,
  Zap,
  Eye,
  Plus
} from 'lucide-react'
import { useProcessTemplates, useCreateFromTemplate } from '@/lib/hooks/useWorkflow'

interface ProcessTemplate {
  id: string
  name: string
  description: string
  category: 'emergency' | 'incident' | 'bcm' | 'audit' | 'compliance' | 'training'
  complexity: 'simple' | 'medium' | 'complex'
  rating: number
  downloads: number
  author: string
  version: string
  lastUpdated: string
  tags: string[]
  estimatedTime: string
  features: string[]
  previewImage?: string
  compliance: string[]
}

// Mock templates data
const mockTemplates: ProcessTemplate[] = [
  {
    id: 'template-001',
    name: 'Emergency Response Protocol',
    description: 'Comprehensive emergency response workflow for business continuity scenarios including natural disasters, cyber attacks, and operational failures.',
    category: 'emergency',
    complexity: 'complex',
    rating: 4.8,
    downloads: 1247,
    author: 'BCM Solutions',
    version: '2.1',
    lastUpdated: '2025-01-15',
    tags: ['ISO 22301', 'Emergency', 'Crisis Management', 'Communication'],
    estimatedTime: '2-4 hours setup',
    features: [
      'Automated stakeholder notifications',
      'Crisis communication workflows',
      'Resource allocation tracking',
      'Media response protocols',
      'Recovery procedures'
    ],
    compliance: ['ISO 22301:2019', 'NIST Framework', 'SOX']
  },
  {
    id: 'template-002',
    name: 'Incident Management Standard',
    description: 'ITIL-based incident management process for rapid response and resolution of IT service disruptions.',
    category: 'incident',
    complexity: 'medium',
    rating: 4.6,
    downloads: 892,
    author: 'ITIL Experts',
    version: '1.5',
    lastUpdated: '2025-01-10',
    tags: ['ITIL', 'Incident', 'IT Service', 'Resolution'],
    estimatedTime: '1-2 hours setup',
    features: [
      'Automatic ticket creation',
      'Escalation workflows',
      'SLA monitoring',
      'Root cause analysis',
      'Knowledge base integration'
    ],
    compliance: ['ITIL v4', 'ISO 20000']
  },
  {
    id: 'template-003',
    name: 'Business Continuity Plan',
    description: 'Complete business continuity planning template with risk assessment, impact analysis, and recovery strategies.',
    category: 'bcm',
    complexity: 'complex',
    rating: 4.9,
    downloads: 2156,
    author: 'Continuity Pro',
    version: '3.0',
    lastUpdated: '2025-01-12',
    tags: ['BCP', 'Risk Assessment', 'Recovery', 'Business Impact'],
    estimatedTime: '4-8 hours setup',
    features: [
      'Business impact analysis',
      'Risk assessment workflows',
      'Recovery time objectives',
      'Supplier management',
      'Testing and exercises'
    ],
    compliance: ['ISO 22301:2019', 'BS 25999', 'NFPA 1600']
  },
  {
    id: 'template-004',
    name: 'Compliance Audit Process',
    description: 'Systematic compliance audit workflow for regulatory requirements and internal policy adherence.',
    category: 'audit',
    complexity: 'medium',
    rating: 4.4,
    downloads: 567,
    author: 'Audit Associates',
    version: '1.8',
    lastUpdated: '2025-01-08',
    tags: ['Audit', 'Compliance', 'Documentation', 'Reporting'],
    estimatedTime: '2-3 hours setup',
    features: [
      'Audit planning workflows',
      'Evidence collection',
      'Finding documentation',
      'Corrective action tracking',
      'Report generation'
    ],
    compliance: ['SOX', 'GDPR', 'ISO 27001', 'COSO']
  },
  {
    id: 'template-005',
    name: 'Training & Awareness Program',
    description: 'Comprehensive training workflow for business continuity awareness and skill development.',
    category: 'training',
    complexity: 'simple',
    rating: 4.3,
    downloads: 423,
    author: 'Learning Solutions',
    version: '1.2',
    lastUpdated: '2025-01-05',
    tags: ['Training', 'Awareness', 'Skills', 'Certification'],
    estimatedTime: '1 hour setup',
    features: [
      'Training schedule management',
      'Progress tracking',
      'Certification workflows',
      'Feedback collection',
      'Knowledge assessments'
    ],
    compliance: ['ISO 22301', 'Training Standards']
  }
]

const categoryColors = {
  emergency: 'bg-red-100 text-red-700 border-red-200',
  incident: 'bg-orange-100 text-orange-700 border-orange-200',
  bcm: 'bg-blue-100 text-blue-700 border-blue-200',
  audit: 'bg-purple-100 text-purple-700 border-purple-200',
  compliance: 'bg-green-100 text-green-700 border-green-200',
  training: 'bg-yellow-100 text-yellow-700 border-yellow-200'
}

const complexityIcons = {
  simple: <CheckCircle className="h-4 w-4 text-green-500" />,
  medium: <Settings className="h-4 w-4 text-yellow-500" />,
  complex: <Zap className="h-4 w-4 text-red-500" />
}

export function TemplateMarketplace() {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [selectedComplexity, setSelectedComplexity] = useState<string>('all')
  const [selectedTemplate, setSelectedTemplate] = useState<ProcessTemplate | null>(null)
  const [previewOpen, setPreviewOpen] = useState(false)

  const createFromTemplate = useCreateFromTemplate()

  // Filter templates based on search and filters
  const filteredTemplates = mockTemplates.filter(template => {
    const matchesSearch = template.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         template.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         template.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))

    const matchesCategory = selectedCategory === 'all' || template.category === selectedCategory
    const matchesComplexity = selectedComplexity === 'all' || template.complexity === selectedComplexity

    return matchesSearch && matchesCategory && matchesComplexity
  })

  const handleUseTemplate = async (template: ProcessTemplate) => {
    try {
      await createFromTemplate.mutateAsync({
        templateId: template.id,
        customization: {
          name: `${template.name} - ${new Date().toLocaleDateString()}`,
          department: 'Default Department',
          owner: 'Current User'
        }
      })
      setPreviewOpen(false)
    } catch (error) {
      console.error('Failed to create from template:', error)
    }
  }

  const renderStars = (rating: number) => {
    return (
      <div className="flex items-center">
        {[1, 2, 3, 4, 5].map((star) => (
          <Star
            key={star}
            className={`h-4 w-4 ${
              star <= rating ? 'text-yellow-400 fill-current' : 'text-gray-300'
            }`}
          />
        ))}
        <span className="ml-1 text-sm text-gray-600">({rating})</span>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold">Template Marketplace</h3>
          <p className="text-sm text-gray-600">
            Ready-to-use workflow templates for common business continuity scenarios
          </p>
        </div>
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          Create Template
        </Button>
      </div>

      {/* Search and Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <Input
            placeholder="Search templates..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>

        <Select value={selectedCategory} onValueChange={setSelectedCategory}>
          <SelectTrigger className="w-48">
            <SelectValue placeholder="Category" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Categories</SelectItem>
            <SelectItem value="emergency">Emergency Response</SelectItem>
            <SelectItem value="incident">Incident Management</SelectItem>
            <SelectItem value="bcm">Business Continuity</SelectItem>
            <SelectItem value="audit">Audit & Compliance</SelectItem>
            <SelectItem value="training">Training</SelectItem>
          </SelectContent>
        </Select>

        <Select value={selectedComplexity} onValueChange={setSelectedComplexity}>
          <SelectTrigger className="w-40">
            <SelectValue placeholder="Complexity" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Levels</SelectItem>
            <SelectItem value="simple">Simple</SelectItem>
            <SelectItem value="medium">Medium</SelectItem>
            <SelectItem value="complex">Complex</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Templates Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredTemplates.map((template) => (
          <Card key={template.id} className="hover:shadow-lg transition-shadow cursor-pointer">
            <CardHeader className="pb-3">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <CardTitle className="text-lg mb-2">{template.name}</CardTitle>
                  <CardDescription className="text-sm line-clamp-2">
                    {template.description}
                  </CardDescription>
                </div>
                <Badge className={categoryColors[template.category]}>
                  {template.category.toUpperCase()}
                </Badge>
              </div>
            </CardHeader>

            <CardContent className="space-y-4">
              {/* Rating and Stats */}
              <div className="flex items-center justify-between">
                {renderStars(template.rating)}
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <Download className="h-4 w-4" />
                  {template.downloads.toLocaleString()}
                </div>
              </div>

              {/* Complexity and Time */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  {complexityIcons[template.complexity]}
                  <span className="text-sm capitalize">{template.complexity}</span>
                </div>
                <div className="flex items-center gap-1 text-sm text-gray-600">
                  <Clock className="h-4 w-4" />
                  {template.estimatedTime}
                </div>
              </div>

              {/* Tags */}
              <div className="flex flex-wrap gap-1">
                {template.tags.slice(0, 3).map((tag) => (
                  <Badge key={tag} variant="outline" className="text-xs">
                    {tag}
                  </Badge>
                ))}
                {template.tags.length > 3 && (
                  <Badge variant="outline" className="text-xs">
                    +{template.tags.length - 3}
                  </Badge>
                )}
              </div>

              {/* Author and Version */}
              <div className="flex items-center justify-between text-sm text-gray-600">
                <span>by {template.author}</span>
                <span>v{template.version}</span>
              </div>

              {/* Actions */}
              <div className="flex gap-2 pt-2">
                <Dialog open={previewOpen && selectedTemplate?.id === template.id} onOpenChange={setPreviewOpen}>
                  <DialogTrigger asChild>
                    <Button
                      variant="outline"
                      size="sm"
                      className="flex-1"
                      onClick={() => setSelectedTemplate(template)}
                    >
                      <Eye className="h-4 w-4 mr-1" />
                      Preview
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
                    <DialogHeader>
                      <DialogTitle className="flex items-center gap-2">
                        {template.name}
                        <Badge className={categoryColors[template.category]}>
                          {template.category.toUpperCase()}
                        </Badge>
                      </DialogTitle>
                      <DialogDescription>
                        {template.description}
                      </DialogDescription>
                    </DialogHeader>

                    <div className="space-y-6 mt-4">
                      {/* Template Details */}
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div className="text-center">
                          <div className="text-2xl font-bold">{template.rating}</div>
                          <div className="text-sm text-gray-600">Rating</div>
                        </div>
                        <div className="text-center">
                          <div className="text-2xl font-bold">{template.downloads.toLocaleString()}</div>
                          <div className="text-sm text-gray-600">Downloads</div>
                        </div>
                        <div className="text-center">
                          <div className="text-2xl font-bold capitalize">{template.complexity}</div>
                          <div className="text-sm text-gray-600">Complexity</div>
                        </div>
                        <div className="text-center">
                          <div className="text-2xl font-bold">v{template.version}</div>
                          <div className="text-sm text-gray-600">Version</div>
                        </div>
                      </div>

                      {/* Features */}
                      <div>
                        <h4 className="font-semibold mb-3">Key Features</h4>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                          {template.features.map((feature, index) => (
                            <div key={index} className="flex items-center gap-2">
                              <CheckCircle className="h-4 w-4 text-green-500" />
                              <span className="text-sm">{feature}</span>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* Compliance */}
                      <div>
                        <h4 className="font-semibold mb-3">Compliance Standards</h4>
                        <div className="flex flex-wrap gap-2">
                          {template.compliance.map((standard) => (
                            <Badge key={standard} variant="secondary" className="flex items-center gap-1">
                              <Shield className="h-3 w-3" />
                              {standard}
                            </Badge>
                          ))}
                        </div>
                      </div>

                      {/* All Tags */}
                      <div>
                        <h4 className="font-semibold mb-3">Tags</h4>
                        <div className="flex flex-wrap gap-2">
                          {template.tags.map((tag) => (
                            <Badge key={tag} variant="outline">
                              {tag}
                            </Badge>
                          ))}
                        </div>
                      </div>

                      {/* Action Buttons */}
                      <div className="flex gap-3 pt-4 border-t">
                        <Button
                          onClick={() => handleUseTemplate(template)}
                          disabled={createFromTemplate.isPending}
                          className="flex-1"
                        >
                          <Plus className="h-4 w-4 mr-2" />
                          {createFromTemplate.isPending ? 'Creating...' : 'Use This Template'}
                        </Button>
                        <Button variant="outline">
                          <Download className="h-4 w-4 mr-2" />
                          Download
                        </Button>
                      </div>
                    </div>
                  </DialogContent>
                </Dialog>

                <Button
                  size="sm"
                  onClick={() => handleUseTemplate(template)}
                  disabled={createFromTemplate.isPending}
                  className="flex-1"
                >
                  <Plus className="h-4 w-4 mr-1" />
                  Use
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* No Results */}
      {filteredTemplates.length === 0 && (
        <div className="text-center py-12">
          <FileText className="h-12 w-12 mx-auto text-gray-400 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No templates found</h3>
          <p className="text-gray-600 mb-4">
            Try adjusting your search criteria or filters
          </p>
          <Button variant="outline" onClick={() => {
            setSearchQuery('')
            setSelectedCategory('all')
            setSelectedComplexity('all')
          }}>
            Clear Filters
          </Button>
        </div>
      )}

      {/* Success Alert */}
      {createFromTemplate.isSuccess && (
        <Alert>
          <CheckCircle className="h-4 w-4" />
          <AlertDescription>
            Template has been successfully applied to create a new process!
          </AlertDescription>
        </Alert>
      )}
    </div>
  )
}