'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { Wrench, FileText, Users, Clock, CheckCircle, Plus, Settings } from 'lucide-react'

interface PlanTemplate {
  id: string
  name: string
  type: 'business-continuity' | 'disaster-recovery' | 'incident-response' | 'crisis-management'
  description: string
  sections: PlanSection[]
  estimatedTime: string
  complexity: 'basic' | 'intermediate' | 'advanced'
  usage: number
}

interface PlanSection {
  id: string
  name: string
  description: string
  required: boolean
  completed: boolean
  fields: PlanField[]
}

interface PlanField {
  id: string
  name: string
  type: 'text' | 'textarea' | 'select' | 'number' | 'date'
  required: boolean
  value?: string
  options?: string[]
}

interface Plan {
  id: string
  name: string
  type: string
  status: 'draft' | 'in-review' | 'approved' | 'active'
  progress: number
  createdAt: string
  updatedAt: string
  assignedTo: string
  reviewDate?: string
}

export function PlanBuilder() {
  const [activeTab, setActiveTab] = useState('builder')
  const [selectedTemplate, setSelectedTemplate] = useState<PlanTemplate | null>(null)

  const [templates] = useState<PlanTemplate[]>([
    {
      id: '1',
      name: 'Business Continuity Plan',
      type: 'business-continuity',
      description: 'Comprehensive business continuity plan template covering all critical business functions',
      estimatedTime: '4-6 hours',
      complexity: 'advanced',
      usage: 47,
      sections: [
        {
          id: '1',
          name: 'Executive Summary',
          description: 'High-level overview of the business continuity strategy',
          required: true,
          completed: false,
          fields: [
            { id: '1', name: 'Plan Purpose', type: 'textarea', required: true },
            { id: '2', name: 'Scope', type: 'textarea', required: true },
            { id: '3', name: 'Key Stakeholders', type: 'textarea', required: true }
          ]
        },
        {
          id: '2',
          name: 'Business Impact Analysis',
          description: 'Assessment of critical business functions and dependencies',
          required: true,
          completed: false,
          fields: [
            { id: '4', name: 'Critical Functions', type: 'textarea', required: true },
            { id: '5', name: 'Recovery Time Objectives', type: 'textarea', required: true },
            { id: '6', name: 'Recovery Point Objectives', type: 'textarea', required: true }
          ]
        }
      ]
    },
    {
      id: '2',
      name: 'Incident Response Plan',
      type: 'incident-response',
      description: 'Template for creating incident response procedures and workflows',
      estimatedTime: '2-3 hours',
      complexity: 'intermediate',
      usage: 23,
      sections: [
        {
          id: '3',
          name: 'Incident Classification',
          description: 'Define incident types and severity levels',
          required: true,
          completed: false,
          fields: [
            { id: '7', name: 'Incident Types', type: 'textarea', required: true },
            { id: '8', name: 'Severity Levels', type: 'select', required: true, options: ['Low', 'Medium', 'High', 'Critical'] }
          ]
        }
      ]
    },
    {
      id: '3',
      name: 'Crisis Management Plan',
      type: 'crisis-management',
      description: 'Crisis management and communication plan template',
      estimatedTime: '3-4 hours',
      complexity: 'advanced',
      usage: 15,
      sections: [
        {
          id: '4',
          name: 'Crisis Team Structure',
          description: 'Define crisis management team roles and responsibilities',
          required: true,
          completed: false,
          fields: [
            { id: '9', name: 'Crisis Manager', type: 'text', required: true },
            { id: '10', name: 'Communication Lead', type: 'text', required: true }
          ]
        }
      ]
    }
  ])

  const [existingPlans] = useState<Plan[]>([
    {
      id: '1',
      name: 'Main Office Business Continuity Plan',
      type: 'business-continuity',
      status: 'active',
      progress: 100,
      createdAt: '2024-08-15T10:00:00Z',
      updatedAt: '2024-09-10T14:30:00Z',
      assignedTo: 'Sarah Johnson',
      reviewDate: '2024-12-15'
    },
    {
      id: '2',
      name: 'IT Disaster Recovery Plan',
      type: 'disaster-recovery',
      status: 'in-review',
      progress: 85,
      createdAt: '2024-09-01T09:15:00Z',
      updatedAt: '2024-09-17T11:45:00Z',
      assignedTo: 'Mike Chen'
    },
    {
      id: '3',
      name: 'Customer Service Crisis Response',
      type: 'crisis-management',
      status: 'draft',
      progress: 45,
      createdAt: '2024-09-10T13:20:00Z',
      updatedAt: '2024-09-16T16:10:00Z',
      assignedTo: 'Emma Wilson'
    }
  ])

  const startBuilding = (template: PlanTemplate) => {
    setSelectedTemplate(template)
    setActiveTab('create')
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800'
      case 'in-review': return 'bg-yellow-100 text-yellow-800'
      case 'approved': return 'bg-blue-100 text-blue-800'
      case 'draft': return 'bg-gray-100 text-gray-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getComplexityColor = (complexity: string) => {
    switch (complexity) {
      case 'basic': return 'bg-green-100 text-green-800'
      case 'intermediate': return 'bg-yellow-100 text-yellow-800'
      case 'advanced': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Enhanced Plan Builder</h2>
          <p className="text-gray-600 mt-1">Create and manage business continuity plans with guided templates</p>
        </div>
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          Create Custom Plan
        </Button>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="builder">Templates</TabsTrigger>
          <TabsTrigger value="create">Create Plan</TabsTrigger>
          <TabsTrigger value="plans">My Plans</TabsTrigger>
          <TabsTrigger value="settings">Settings</TabsTrigger>
        </TabsList>

        <TabsContent value="builder" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {templates.map(template => (
              <Card key={template.id} className="cursor-pointer hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">{template.name}</CardTitle>
                    <Badge className={getComplexityColor(template.complexity)}>
                      {template.complexity}
                    </Badge>
                  </div>
                  <CardDescription>{template.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Sections:</span>
                      <span className="font-medium">{template.sections.length}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Estimated Time:</span>
                      <span className="font-medium">{template.estimatedTime}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Usage:</span>
                      <span className="font-medium">{template.usage} times</span>
                    </div>
                    <Button 
                      className="w-full" 
                      onClick={() => startBuilding(template)}
                    >
                      <Wrench className="h-4 w-4 mr-2" />
                      Use Template
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Plan Building Features</CardTitle>
              <CardDescription>Advanced features available in the enhanced plan builder</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-5 w-5 text-green-600" />
                  <span className="text-sm">Guided Templates</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-5 w-5 text-green-600" />
                  <span className="text-sm">Progress Tracking</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-5 w-5 text-green-600" />
                  <span className="text-sm">Collaboration Tools</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-5 w-5 text-green-600" />
                  <span className="text-sm">Version Control</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-5 w-5 text-green-600" />
                  <span className="text-sm">Approval Workflows</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-5 w-5 text-green-600" />
                  <span className="text-sm">Export Options</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-5 w-5 text-green-600" />
                  <span className="text-sm">Integration with BIA</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-5 w-5 text-green-600" />
                  <span className="text-sm">Automated Reviews</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="create" className="space-y-6">
          {selectedTemplate ? (
            <Card>
              <CardHeader>
                <CardTitle>Creating: {selectedTemplate.name}</CardTitle>
                <CardDescription>{selectedTemplate.description}</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="planName">Plan Name</Label>
                    <Input id="planName" placeholder="Enter plan name..." />
                  </div>
                  <div>
                    <Label htmlFor="assignee">Assigned To</Label>
                    <Select>
                      <SelectTrigger>
                        <SelectValue placeholder="Select assignee..." />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="sarah">Sarah Johnson</SelectItem>
                        <SelectItem value="mike">Mike Chen</SelectItem>
                        <SelectItem value="emma">Emma Wilson</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div>
                  <Label htmlFor="planDescription">Description</Label>
                  <Textarea 
                    id="planDescription" 
                    placeholder="Describe the purpose and scope of this plan..."
                    className="min-h-[100px]"
                  />
                </div>

                <div>
                  <h3 className="font-medium mb-4">Plan Sections ({selectedTemplate.sections.length})</h3>
                  <div className="space-y-4">
                    {selectedTemplate.sections.map(section => (
                      <Card key={section.id}>
                        <CardHeader>
                          <div className="flex items-center justify-between">
                            <CardTitle className="text-base">{section.name}</CardTitle>
                            {section.required && <Badge variant="outline">Required</Badge>}
                          </div>
                          <CardDescription>{section.description}</CardDescription>
                        </CardHeader>
                        <CardContent>
                          <div className="space-y-4">
                            {section.fields.map(field => (
                              <div key={field.id}>
                                <Label htmlFor={field.id}>
                                  {field.name} {field.required && <span className="text-red-500">*</span>}
                                </Label>
                                {field.type === 'textarea' ? (
                                  <Textarea 
                                    id={field.id} 
                                    placeholder={`Enter ${field.name.toLowerCase()}...`}
                                  />
                                ) : field.type === 'select' ? (
                                  <Select>
                                    <SelectTrigger>
                                      <SelectValue placeholder={`Select ${field.name.toLowerCase()}...`} />
                                    </SelectTrigger>
                                    <SelectContent>
                                      {field.options?.map(option => (
                                        <SelectItem key={option} value={option.toLowerCase()}>
                                          {option}
                                        </SelectItem>
                                      ))}
                                    </SelectContent>
                                  </Select>
                                ) : (
                                  <Input 
                                    id={field.id} 
                                    type={field.type}
                                    placeholder={`Enter ${field.name.toLowerCase()}...`}
                                  />
                                )}
                              </div>
                            ))}
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </div>

                <div className="flex gap-2">
                  <Button>Save Draft</Button>
                  <Button variant="outline">Save & Continue</Button>
                  <Button variant="outline">Preview</Button>
                </div>
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-12">
                <FileText className="h-12 w-12 text-gray-400 mb-4" />
                <h3 className="text-lg font-medium mb-2">No Template Selected</h3>
                <p className="text-gray-600 mb-4">Choose a template from the Templates tab to start building your plan</p>
                <Button onClick={() => setActiveTab('builder')}>Browse Templates</Button>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="plans" className="space-y-6">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-medium">My Plans ({existingPlans.length})</h3>
            <div className="flex gap-2">
              <Button variant="outline">Filter</Button>
              <Button variant="outline">Export</Button>
            </div>
          </div>

          <div className="space-y-4">
            {existingPlans.map(plan => (
              <Card key={plan.id}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="text-lg">{plan.name}</CardTitle>
                      <CardDescription>
                        Created: {new Date(plan.createdAt).toLocaleDateString()} • 
                        Updated: {new Date(plan.updatedAt).toLocaleDateString()} • 
                        Assigned to: {plan.assignedTo}
                      </CardDescription>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge className={getStatusColor(plan.status)}>{plan.status}</Badge>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span>Progress</span>
                        <span>{plan.progress}%</span>
                      </div>
                      <Progress value={plan.progress} />
                    </div>
                    
                    {plan.reviewDate && (
                      <div className="text-sm text-gray-600">
                        Next review: {new Date(plan.reviewDate).toLocaleDateString()}
                      </div>
                    )}
                    
                    <div className="flex gap-2">
                      <Button size="sm">View</Button>
                      <Button variant="outline" size="sm">Edit</Button>
                      <Button variant="outline" size="sm">Export</Button>
                      <Button variant="outline" size="sm">Duplicate</Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="settings" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Plan Builder Settings</CardTitle>
              <CardDescription>Configure your plan building preferences</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div>
                  <Label htmlFor="defaultAssignee">Default Assignee</Label>
                  <Select>
                    <SelectTrigger>
                      <SelectValue placeholder="Select default assignee..." />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="self">Assign to myself</SelectItem>
                      <SelectItem value="team-lead">Team Lead</SelectItem>
                      <SelectItem value="bcm-manager">BCM Manager</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label htmlFor="autoSave">Auto-save Interval</Label>
                  <Select>
                    <SelectTrigger>
                      <SelectValue placeholder="Select auto-save interval..." />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="1min">Every minute</SelectItem>
                      <SelectItem value="5min">Every 5 minutes</SelectItem>
                      <SelectItem value="10min">Every 10 minutes</SelectItem>
                      <SelectItem value="disabled">Disabled</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label htmlFor="notifications">Email Notifications</Label>
                  <div className="space-y-2 mt-2">
                    <div className="flex items-center space-x-2">
                      <input type="checkbox" id="plan-updates" />
                      <Label htmlFor="plan-updates">Plan updates and changes</Label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <input type="checkbox" id="review-reminders" />
                      <Label htmlFor="review-reminders">Review reminders</Label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <input type="checkbox" id="approval-requests" />
                      <Label htmlFor="approval-requests">Approval requests</Label>
                    </div>
                  </div>
                </div>
              </div>

              <Button>Save Settings</Button>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}