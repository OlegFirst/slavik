'use client'

import React, { useState } from 'react'
import { AppLayout } from '@/components/layout/AppLayout'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import {
  ArrowLeft,
  Plus,
  Trash2,
  DollarSign,
  Clock,
  MapPin,
  Users,
  CheckCircle,
  AlertCircle,
  FileText,
  Target,
  Lightbulb
} from 'lucide-react'

export default function CreateRequestPage() {
  const [formData, setFormData] = useState({
    // Basic Information
    title: '',
    description: '',
    serviceType: '',
    industry: '',
    companySize: '',
    urgency: 'medium',

    // Project Details
    scopeOfWork: '',
    deliverables: [''],
    duration: '',
    startDate: '',
    endDate: '',

    // Budget
    budgetType: 'hourly',
    budgetMin: '',
    budgetMax: '',

    // Requirements
    requiredSkills: [''],
    requiredCertifications: '',
    minExperience: '',

    // Location
    workLocation: 'remote',
    country: '',
    state: '',
    city: '',

    // Additional
    applicationDeadline: '',
    isPublic: true,
    additionalNotes: ''
  })

  const [currentStep, setCurrentStep] = useState(1)
  const totalSteps = 4

  const addArrayField = (field: 'deliverables' | 'requiredSkills') => {
    setFormData(prev => ({
      ...prev,
      [field]: [...prev[field], '']
    }))
  }

  const updateArrayField = (field: 'deliverables' | 'requiredSkills', index: number, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: prev[field].map((item, i) => i === index ? value : item)
    }))
  }

  const removeArrayField = (field: 'deliverables' | 'requiredSkills', index: number) => {
    setFormData(prev => ({
      ...prev,
      [field]: prev[field].filter((_, i) => i !== index)
    }))
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    // In real app, this would call API
    console.log('Creating service request:', formData)
    // Redirect to dashboard or requests page
  }

  const nextStep = () => {
    if (currentStep < totalSteps) {
      setCurrentStep(currentStep + 1)
    }
  }

  const prevStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1)
    }
  }

  const renderStepContent = () => {
    switch (currentStep) {
      case 1:
        return (
          <div className="space-y-6">
            <div className="text-center mb-8">
              <h2 className="text-2xl font-bold mb-2">Project Overview</h2>
              <p className="text-gray-600">Tell us about your BCM project needs</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium mb-2">Project Title *</label>
                <Input
                  value={formData.title}
                  onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
                  placeholder="e.g., Financial Services BCM Gap Analysis"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Service Type *</label>
                <select
                  value={formData.serviceType}
                  onChange={(e) => setFormData(prev => ({ ...prev, serviceType: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  required
                >
                  <option value="">Select Service Type</option>
                  <option value="consulting">BCM Consulting</option>
                  <option value="assessment">Risk Assessment</option>
                  <option value="bia">Business Impact Analysis</option>
                  <option value="planning">BCM Planning</option>
                  <option value="training">Training & Workshop</option>
                  <option value="audit">Audit & Review</option>
                  <option value="implementation">Implementation Support</option>
                  <option value="crisis_support">Crisis Management Support</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Project Description *</label>
              <Textarea
                value={formData.description}
                onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                placeholder="Describe your project objectives, current situation, and what you're looking to achieve..."
                rows={5}
                required
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <label className="block text-sm font-medium mb-2">Industry</label>
                <select
                  value={formData.industry}
                  onChange={(e) => setFormData(prev => ({ ...prev, industry: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                >
                  <option value="">Select Industry</option>
                  <option value="financial">Financial Services</option>
                  <option value="healthcare">Healthcare</option>
                  <option value="manufacturing">Manufacturing</option>
                  <option value="technology">Technology</option>
                  <option value="government">Government</option>
                  <option value="energy">Energy & Utilities</option>
                  <option value="retail">Retail & E-commerce</option>
                  <option value="education">Education</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Company Size</label>
                <select
                  value={formData.companySize}
                  onChange={(e) => setFormData(prev => ({ ...prev, companySize: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                >
                  <option value="">Select Size</option>
                  <option value="small">1-50 employees</option>
                  <option value="medium">51-200 employees</option>
                  <option value="large">201-1000 employees</option>
                  <option value="enterprise">1000+ employees</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Urgency Level</label>
                <select
                  value={formData.urgency}
                  onChange={(e) => setFormData(prev => ({ ...prev, urgency: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                >
                  <option value="low">Low - Flexible timeline</option>
                  <option value="medium">Medium - 2-4 weeks</option>
                  <option value="high">High - Within 1 week</option>
                  <option value="urgent">Urgent - ASAP</option>
                </select>
              </div>
            </div>
          </div>
        )

      case 2:
        return (
          <div className="space-y-6">
            <div className="text-center mb-8">
              <h2 className="text-2xl font-bold mb-2">Project Scope & Requirements</h2>
              <p className="text-gray-600">Define the scope of work and deliverables</p>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Scope of Work</label>
              <Textarea
                value={formData.scopeOfWork}
                onChange={(e) => setFormData(prev => ({ ...prev, scopeOfWork: e.target.value }))}
                placeholder="Describe the specific work that needs to be done, methodologies to be used, and any constraints..."
                rows={4}
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Expected Deliverables *</label>
              {formData.deliverables.map((deliverable, index) => (
                <div key={index} className="flex gap-2 mb-2">
                  <Input
                    value={deliverable}
                    onChange={(e) => updateArrayField('deliverables', index, e.target.value)}
                    placeholder="e.g., Gap analysis report, Implementation roadmap..."
                  />
                  {formData.deliverables.length > 1 && (
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      onClick={() => removeArrayField('deliverables', index)}
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
                onClick={() => addArrayField('deliverables')}
              >
                <Plus className="h-4 w-4 mr-1" />
                Add Deliverable
              </Button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <label className="block text-sm font-medium mb-2">Project Duration</label>
                <Input
                  value={formData.duration}
                  onChange={(e) => setFormData(prev => ({ ...prev, duration: e.target.value }))}
                  placeholder="e.g., 6-8 weeks, 3 months"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Desired Start Date</label>
                <Input
                  type="date"
                  value={formData.startDate}
                  onChange={(e) => setFormData(prev => ({ ...prev, startDate: e.target.value }))}
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Target End Date</label>
                <Input
                  type="date"
                  value={formData.endDate}
                  onChange={(e) => setFormData(prev => ({ ...prev, endDate: e.target.value }))}
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Required Skills & Expertise</label>
              {formData.requiredSkills.map((skill, index) => (
                <div key={index} className="flex gap-2 mb-2">
                  <Input
                    value={skill}
                    onChange={(e) => updateArrayField('requiredSkills', index, e.target.value)}
                    placeholder="e.g., ISO 22301, Financial Services BCM, Risk Assessment..."
                  />
                  {formData.requiredSkills.length > 1 && (
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      onClick={() => removeArrayField('requiredSkills', index)}
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
                onClick={() => addArrayField('requiredSkills')}
              >
                <Plus className="h-4 w-4 mr-1" />
                Add Skill
              </Button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium mb-2">Required Certifications</label>
                <Textarea
                  value={formData.requiredCertifications}
                  onChange={(e) => setFormData(prev => ({ ...prev, requiredCertifications: e.target.value }))}
                  placeholder="e.g., CBCP, MBCI, ISO 22301 Lead Auditor..."
                  rows={3}
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Minimum Experience (Years)</label>
                <Input
                  type="number"
                  value={formData.minExperience}
                  onChange={(e) => setFormData(prev => ({ ...prev, minExperience: e.target.value }))}
                  placeholder="e.g., 5"
                />
              </div>
            </div>
          </div>
        )

      case 3:
        return (
          <div className="space-y-6">
            <div className="text-center mb-8">
              <h2 className="text-2xl font-bold mb-2">Budget & Location</h2>
              <p className="text-gray-600">Set your budget and work preferences</p>
            </div>

            <div>
              <label className="block text-sm font-medium mb-4">Budget Type</label>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                {[
                  { value: 'hourly', label: 'Hourly Rate', desc: 'Pay by the hour' },
                  { value: 'fixed', label: 'Fixed Project', desc: 'One-time project fee' },
                  { value: 'retainer', label: 'Monthly Retainer', desc: 'Ongoing monthly fee' }
                ].map(option => (
                  <div
                    key={option.value}
                    className={`border rounded-lg p-4 cursor-pointer transition-colors ${
                      formData.budgetType === option.value ? 'border-blue-500 bg-blue-50' : 'border-gray-200'
                    }`}
                    onClick={() => setFormData(prev => ({ ...prev, budgetType: option.value }))}
                  >
                    <div className="font-medium">{option.label}</div>
                    <div className="text-sm text-gray-600">{option.desc}</div>
                  </div>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium mb-2">
                  {formData.budgetType === 'hourly' ? 'Minimum Hourly Rate' :
                   formData.budgetType === 'retainer' ? 'Monthly Budget' : 'Minimum Budget'} ($)
                </label>
                <Input
                  type="number"
                  value={formData.budgetMin}
                  onChange={(e) => setFormData(prev => ({ ...prev, budgetMin: e.target.value }))}
                  placeholder="100"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">
                  {formData.budgetType === 'hourly' ? 'Maximum Hourly Rate' : 'Maximum Budget'} ($)
                </label>
                <Input
                  type="number"
                  value={formData.budgetMax}
                  onChange={(e) => setFormData(prev => ({ ...prev, budgetMax: e.target.value }))}
                  placeholder="200"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium mb-4">Work Location Preference</label>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                {[
                  { value: 'remote', label: 'Remote Only', desc: 'Work from anywhere' },
                  { value: 'onsite', label: 'Onsite Required', desc: 'Must work at our location' },
                  { value: 'hybrid', label: 'Hybrid/Flexible', desc: 'Combination of both' }
                ].map(option => (
                  <div
                    key={option.value}
                    className={`border rounded-lg p-4 cursor-pointer transition-colors ${
                      formData.workLocation === option.value ? 'border-blue-500 bg-blue-50' : 'border-gray-200'
                    }`}
                    onClick={() => setFormData(prev => ({ ...prev, workLocation: option.value }))}
                  >
                    <div className="font-medium">{option.label}</div>
                    <div className="text-sm text-gray-600">{option.desc}</div>
                  </div>
                ))}
              </div>
            </div>

            {formData.workLocation !== 'remote' && (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div>
                  <label className="block text-sm font-medium mb-2">Country</label>
                  <Input
                    value={formData.country}
                    onChange={(e) => setFormData(prev => ({ ...prev, country: e.target.value }))}
                    placeholder="United States"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">State/Province</label>
                  <Input
                    value={formData.state}
                    onChange={(e) => setFormData(prev => ({ ...prev, state: e.target.value }))}
                    placeholder="New York"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">City</label>
                  <Input
                    value={formData.city}
                    onChange={(e) => setFormData(prev => ({ ...prev, city: e.target.value }))}
                    placeholder="New York"
                  />
                </div>
              </div>
            )}
          </div>
        )

      case 4:
        return (
          <div className="space-y-6">
            <div className="text-center mb-8">
              <h2 className="text-2xl font-bold mb-2">Review & Publish</h2>
              <p className="text-gray-600">Final details and publish your request</p>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Application Deadline</label>
              <Input
                type="date"
                value={formData.applicationDeadline}
                onChange={(e) => setFormData(prev => ({ ...prev, applicationDeadline: e.target.value }))}
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Additional Notes (Optional)</label>
              <Textarea
                value={formData.additionalNotes}
                onChange={(e) => setFormData(prev => ({ ...prev, additionalNotes: e.target.value }))}
                placeholder="Any additional information or special requirements..."
                rows={4}
              />
            </div>

            <div>
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={formData.isPublic}
                  onChange={(e) => setFormData(prev => ({ ...prev, isPublic: e.target.checked }))}
                />
                <span className="text-sm font-medium">Make this request public</span>
              </label>
              <p className="text-xs text-gray-500 mt-1">
                Public requests are visible to all verified specialists. Uncheck to make it invite-only.
              </p>
            </div>

            {/* Request Summary */}
            <Card>
              <CardHeader>
                <CardTitle>Request Summary</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <h4 className="font-medium">{formData.title || 'Project Title'}</h4>
                  <p className="text-sm text-gray-600">{formData.serviceType} • {formData.industry}</p>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="text-center p-3 bg-blue-50 rounded-lg">
                    <DollarSign className="h-4 w-4 mx-auto mb-1 text-blue-600" />
                    <div className="text-xs text-gray-600">Budget</div>
                    <div className="font-semibold text-sm">
                      ${formData.budgetMin || '0'}-${formData.budgetMax || '0'}
                    </div>
                  </div>
                  <div className="text-center p-3 bg-green-50 rounded-lg">
                    <Clock className="h-4 w-4 mx-auto mb-1 text-green-600" />
                    <div className="text-xs text-gray-600">Duration</div>
                    <div className="font-semibold text-sm">{formData.duration || 'TBD'}</div>
                  </div>
                  <div className="text-center p-3 bg-purple-50 rounded-lg">
                    <MapPin className="h-4 w-4 mx-auto mb-1 text-purple-600" />
                    <div className="text-xs text-gray-600">Location</div>
                    <div className="font-semibold text-sm capitalize">{formData.workLocation}</div>
                  </div>
                  <div className="text-center p-3 bg-orange-50 rounded-lg">
                    <AlertCircle className="h-4 w-4 mx-auto mb-1 text-orange-600" />
                    <div className="text-xs text-gray-600">Urgency</div>
                    <div className="font-semibold text-sm capitalize">{formData.urgency}</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )

      default:
        return null
    }
  }

  return (
    <AppLayout>
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button variant="outline" size="sm">
              <ArrowLeft className="h-4 w-4 mr-1" />
              Back to Dashboard
            </Button>
            <div>
              <h1 className="text-3xl font-bold">Create Service Request</h1>
              <p className="text-gray-600">Find the perfect BCM specialist for your project</p>
            </div>
          </div>
        </div>

        {/* Progress Indicator */}
        <div className="flex items-center justify-center space-x-4 mb-8">
          {[1, 2, 3, 4].map((step) => (
            <div key={step} className="flex items-center">
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                  step <= currentStep
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-200 text-gray-600'
                }`}
              >
                {step < currentStep ? <CheckCircle className="h-5 w-5" /> : step}
              </div>
              {step < totalSteps && (
                <div
                  className={`w-16 h-1 mx-2 ${
                    step < currentStep ? 'bg-blue-600' : 'bg-gray-200'
                  }`}
                />
              )}
            </div>
          ))}
        </div>

        <Card>
          <CardContent className="p-8">
            <form onSubmit={handleSubmit}>
              {renderStepContent()}

              <div className="flex justify-between pt-8 border-t mt-8">
                <Button
                  type="button"
                  variant="outline"
                  onClick={prevStep}
                  disabled={currentStep === 1}
                >
                  Previous
                </Button>

                {currentStep < totalSteps ? (
                  <Button type="button" onClick={nextStep}>
                    Next Step
                  </Button>
                ) : (
                  <Button type="submit">
                    Publish Request
                  </Button>
                )}
              </div>
            </form>
          </CardContent>
        </Card>

        {/* Help Section */}
        <Card>
          <CardContent className="p-6">
            <div className="flex items-start gap-4">
              <Lightbulb className="h-6 w-6 text-yellow-600 flex-shrink-0 mt-1" />
              <div>
                <h3 className="font-medium mb-2">Tips for a Great Request</h3>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• Be specific about your requirements and deliverables</li>
                  <li>• Provide context about your organization and industry</li>
                  <li>• Set realistic budgets and timelines</li>
                  <li>• Include any compliance or regulatory requirements</li>
                  <li>• Mention preferred communication and working styles</li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  )
}