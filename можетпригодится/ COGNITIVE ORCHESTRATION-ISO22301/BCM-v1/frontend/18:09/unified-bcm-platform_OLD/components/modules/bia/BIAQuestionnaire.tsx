'use client'

import React, { useState, useEffect, useCallback } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { QuestionField } from './QuestionField'
import {
  biaAPI,
  biaQueryKeys,
  type BIAQuestionnaire as BIAQuestionnaireType,
  type BIAResponse,
  type BIAQuestion,
  type BusinessFunction
} from '@/services/bia-api'
import {
  ChevronLeft,
  ChevronRight,
  Save,
  CheckCircle,
  AlertCircle,
  FileText,
  Clock,
  Building,
  DollarSign,
  Settings,
  Users,
  Zap
} from 'lucide-react'
import { cn } from '@/lib/utils'

interface BIAQuestionnaireProps {
  functionId?: string
  onComplete?: (result: any) => void
  onClose?: () => void
  isOpen?: boolean
}

interface StepData {
  id: string
  title: string
  description: string
  icon: React.ComponentType<{ className?: string }>
  questions: BIAQuestion[]
  isComplete?: boolean
}

interface FormData {
  [questionId: string]: string | number | string[]
}

interface ValidationError {
  questionId: string
  message: string
}

export function BIAQuestionnaire({
  functionId,
  onComplete,
  onClose,
  isOpen = false
}: BIAQuestionnaireProps) {
  const [currentStep, setCurrentStep] = useState(0)
  const [formData, setFormData] = useState<FormData>({})
  const [validationErrors, setValidationErrors] = useState<ValidationError[]>([])
  const [isDirty, setIsDirty] = useState(false)
  const [lastSaved, setLastSaved] = useState<Date | null>(null)
  const queryClient = useQueryClient()

  // Fetch questionnaire template
  const { data: questionnaire, isLoading } = useQuery({
    queryKey: biaQueryKeys.questionnaire(functionId),
    queryFn: () => biaAPI.getBIAQuestionnaire(functionId),
    enabled: isOpen
  })

  // Fetch business functions for context
  const { data: businessFunctions } = useQuery({
    queryKey: biaQueryKeys.businessFunctions(),
    queryFn: () => biaAPI.getBusinessFunctions(),
    enabled: isOpen
  })

  // Submit questionnaire mutation
  const submitMutation = useMutation({
    mutationFn: (responses: BIAResponse[]) => {
      if (!questionnaire?.id) throw new Error('No questionnaire ID')
      return biaAPI.submitBIAQuestionnaire(questionnaire.id, responses)
    },
    onSuccess: (result) => {
      queryClient.invalidateQueries({ queryKey: biaQueryKeys.all })
      onComplete?.(result)
    }
  })

  // Define the steps with predefined questions
  const steps: StepData[] = [
    {
      id: 'identification',
      title: 'Function Identification',
      description: 'Define the business function and its basic characteristics',
      icon: Building,
      questions: [
        {
          id: 'function_name',
          category: 'impact',
          question: 'Business Function Name',
          type: 'text',
          required: true
        },
        {
          id: 'department',
          category: 'impact',
          question: 'Department',
          type: 'select',
          options: ['Sales', 'Finance', 'Production', 'IT', 'HR', 'Operations', 'Marketing', 'Support'],
          required: true
        },
        {
          id: 'function_owner',
          category: 'impact',
          question: 'Function Owner',
          type: 'text',
          required: true
        },
        {
          id: 'criticality_level',
          category: 'impact',
          question: 'Initial Criticality Assessment',
          type: 'select',
          options: ['Low', 'Medium', 'High', 'Critical'],
          required: true
        },
        {
          id: 'function_description',
          category: 'impact',
          question: 'Function Description',
          type: 'text',
          required: false
        }
      ]
    },
    {
      id: 'impact',
      title: 'Impact Assessment',
      description: 'Assess the financial, operational, and reputational impacts',
      icon: DollarSign,
      questions: [
        {
          id: 'financial_impact_1h',
          category: 'impact',
          question: 'Financial Impact per Hour ($)',
          type: 'number',
          required: true
        },
        {
          id: 'financial_impact_daily',
          category: 'impact',
          question: 'Financial Impact per Day ($)',
          type: 'number',
          required: true
        },
        {
          id: 'reputation_impact',
          category: 'impact',
          question: 'Reputational Impact Level (1-10)',
          type: 'slider',
          required: true
        },
        {
          id: 'regulatory_impact',
          category: 'impact',
          question: 'Regulatory/Compliance Impact (1-10)',
          type: 'slider',
          required: true
        },
        {
          id: 'operational_impact',
          category: 'impact',
          question: 'Operational Impact (1-10)',
          type: 'slider',
          required: true
        },
        {
          id: 'customer_impact',
          category: 'impact',
          question: 'Customer Impact Description',
          type: 'text',
          required: false
        }
      ]
    },
    {
      id: 'recovery',
      title: 'Recovery Requirements',
      description: 'Define recovery time objectives and priorities',
      icon: Clock,
      questions: [
        {
          id: 'rto_hours',
          category: 'recovery',
          question: 'Recovery Time Objective (RTO) in Hours',
          type: 'number',
          required: true
        },
        {
          id: 'rpo_hours',
          category: 'recovery',
          question: 'Recovery Point Objective (RPO) in Hours',
          type: 'number',
          required: true
        },
        {
          id: 'mtpd_hours',
          category: 'recovery',
          question: 'Maximum Tolerable Period of Disruption (MTPD) in Hours',
          type: 'number',
          required: true
        },
        {
          id: 'recovery_priority',
          category: 'recovery',
          question: 'Recovery Priority Level (1-5)',
          type: 'slider',
          required: true
        },
        {
          id: 'minimum_staff_required',
          category: 'recovery',
          question: 'Minimum Staff Required for Recovery (%)',
          type: 'number',
          required: true
        }
      ]
    },
    {
      id: 'dependencies',
      title: 'Dependencies',
      description: 'Identify critical dependencies and interconnections',
      icon: Settings,
      questions: [
        {
          id: 'it_systems',
          category: 'dependencies',
          question: 'Critical IT Systems',
          type: 'multiselect',
          options: ['ERP System', 'CRM', 'Email System', 'Database', 'Network Infrastructure', 'Security Systems', 'Backup Systems', 'Communication Tools'],
          required: true
        },
        {
          id: 'upstream_dependencies',
          category: 'dependencies',
          question: 'Upstream Dependencies (Functions that this depends on)',
          type: 'multiselect',
          options: ['Supply Chain', 'Finance', 'IT Support', 'Human Resources', 'Legal', 'Facilities', 'Security'],
          required: false
        },
        {
          id: 'downstream_dependencies',
          category: 'dependencies',
          question: 'Downstream Dependencies (Functions that depend on this)',
          type: 'multiselect',
          options: ['Customer Service', 'Billing', 'Shipping', 'Quality Control', 'Reporting', 'Compliance'],
          required: false
        },
        {
          id: 'third_party_services',
          category: 'dependencies',
          question: 'Critical Third-Party Services',
          type: 'multiselect',
          options: ['Payment Processors', 'Cloud Services', 'Vendors', 'Utilities', 'Telecommunications', 'Logistics'],
          required: false
        }
      ]
    },
    {
      id: 'resources',
      title: 'Resource Requirements',
      description: 'Define required resources for normal and recovery operations',
      icon: Users,
      questions: [
        {
          id: 'staff_count',
          category: 'resources',
          question: 'Total Staff Count',
          type: 'number',
          required: true
        },
        {
          id: 'critical_skills',
          category: 'resources',
          question: 'Critical Skills Required',
          type: 'multiselect',
          options: ['Technical Expertise', 'Management', 'Customer Relations', 'Financial Analysis', 'Operations', 'Quality Control', 'Security'],
          required: true
        },
        {
          id: 'workspace_requirements',
          category: 'resources',
          question: 'Workspace Requirements',
          type: 'select',
          options: ['On-site Only', 'Remote Capable', 'Hybrid', 'Mobile'],
          required: true
        },
        {
          id: 'equipment_needs',
          category: 'resources',
          question: 'Critical Equipment/Tools',
          type: 'multiselect',
          options: ['Computers/Laptops', 'Specialized Software', 'Manufacturing Equipment', 'Testing Equipment', 'Vehicles', 'Safety Equipment'],
          required: false
        },
        {
          id: 'facility_requirements',
          category: 'resources',
          question: 'Facility Requirements',
          type: 'multiselect',
          options: ['Dedicated Space', 'Security Access', 'Environmental Controls', 'Backup Power', 'Communications'],
          required: false
        }
      ]
    }
  ]

  // Auto-save functionality
  const autoSave = useCallback(async () => {
    if (isDirty && Object.keys(formData).length > 0) {
      try {
        // Here you would implement actual auto-save to backend
        // For now, we'll just update the local storage
        localStorage.setItem(`bia_draft_${functionId || 'new'}`, JSON.stringify({
          formData,
          currentStep,
          timestamp: new Date().toISOString()
        }))
        setLastSaved(new Date())
        setIsDirty(false)
      } catch (error) {
        console.error('Auto-save failed:', error)
      }
    }
  }, [formData, isDirty, functionId, currentStep])

  // Auto-save every 30 seconds
  useEffect(() => {
    const interval = setInterval(autoSave, 30000)
    return () => clearInterval(interval)
  }, [autoSave])

  // Load draft data on mount
  useEffect(() => {
    if (isOpen) {
      const draftKey = `bia_draft_${functionId || 'new'}`
      const savedDraft = localStorage.getItem(draftKey)
      if (savedDraft) {
        try {
          const { formData: savedData, currentStep: savedStep } = JSON.parse(savedDraft)
          setFormData(savedData)
          setCurrentStep(savedStep)
        } catch (error) {
          console.error('Failed to load draft:', error)
        }
      }
    }
  }, [isOpen, functionId])

  const validateStep = (stepIndex: number): ValidationError[] => {
    const step = steps[stepIndex]
    const errors: ValidationError[] = []

    step.questions.forEach(question => {
      if (question.required) {
        const value = formData[question.id]
        if (value === undefined || value === '' || (Array.isArray(value) && value.length === 0)) {
          errors.push({
            questionId: question.id,
            message: `${question.question} is required`
          })
        }
      }
    })

    return errors
  }

  const handleNext = () => {
    const stepErrors = validateStep(currentStep)
    setValidationErrors(stepErrors)

    if (stepErrors.length === 0) {
      if (currentStep < steps.length - 1) {
        setCurrentStep(currentStep + 1)
      }
    }
  }

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1)
    }
  }

  const handleFieldChange = (questionId: string, value: string | number | string[]) => {
    setFormData(prev => ({
      ...prev,
      [questionId]: value
    }))
    setIsDirty(true)

    // Clear validation error for this field
    setValidationErrors(prev => prev.filter(error => error.questionId !== questionId))
  }

  const handleSubmit = async () => {
    // Validate all steps
    const allErrors: ValidationError[] = []
    steps.forEach((_, index) => {
      allErrors.push(...validateStep(index))
    })

    if (allErrors.length > 0) {
      setValidationErrors(allErrors)
      return
    }

    // Convert form data to responses
    const responses: BIAResponse[] = Object.entries(formData).map(([questionId, answer]) => ({
      questionId,
      answer,
      confidence: 8, // Default confidence level
      notes: ''
    }))

    try {
      await submitMutation.mutateAsync(responses)

      // Clear draft data
      localStorage.removeItem(`bia_draft_${functionId || 'new'}`)
    } catch (error) {
      console.error('Failed to submit questionnaire:', error)
    }
  }

  const progress = ((currentStep + 1) / steps.length) * 100
  const currentStepData = steps[currentStep]
  const isLastStep = currentStep === steps.length - 1
  const canProceed = validateStep(currentStep).length === 0

  if (isLoading) {
    return (
      <Dialog open={isOpen} onOpenChange={onClose}>
        <DialogContent className="max-w-4xl h-[80vh]">
          <div className="flex items-center justify-center h-full">
            <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
          </div>
        </DialogContent>
      </Dialog>
    )
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl h-[90vh] flex flex-col">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-3 text-xl">
            <FileText className="h-6 w-6 text-blue-600" />
            Business Impact Analysis Questionnaire
            {lastSaved && (
              <Badge variant="outline" className="text-xs">
                <Save className="h-3 w-3 mr-1" />
                Saved {lastSaved.toLocaleTimeString()}
              </Badge>
            )}
          </DialogTitle>
          <DialogDescription>
            Complete this comprehensive assessment to analyze the business impact and recovery requirements.
          </DialogDescription>
        </DialogHeader>

        {/* Progress Bar */}
        <div className="space-y-2">
          <div className="flex justify-between text-sm text-gray-500">
            <span>Step {currentStep + 1} of {steps.length}</span>
            <span>{Math.round(progress)}% Complete</span>
          </div>
          <Progress value={progress} className="h-2" />
        </div>

        {/* Step Navigation */}
        <div className="flex justify-between items-center space-x-4 py-4 border-b">
          {steps.map((step, index) => (
            <div
              key={step.id}
              className={cn(
                "flex items-center space-x-2 px-3 py-2 rounded-lg cursor-pointer transition-colors",
                index === currentStep && "bg-blue-50 text-blue-700",
                index < currentStep && "bg-green-50 text-green-700",
                index > currentStep && "text-gray-400"
              )}
              onClick={() => setCurrentStep(index)}
            >
              <step.icon className="h-4 w-4" />
              <span className="text-xs font-medium hidden sm:inline">{step.title}</span>
              {index < currentStep && <CheckCircle className="h-4 w-4" />}
            </div>
          ))}
        </div>

        {/* Current Step Content */}
        <div className="flex-1 overflow-y-auto">
          <Card className="p-6">
            <div className="space-y-6">
              <div className="text-center">
                <currentStepData.icon className="h-12 w-12 text-blue-600 mx-auto mb-3" />
                <h3 className="text-xl font-semibold">{currentStepData.title}</h3>
                <p className="text-gray-600 mt-1">{currentStepData.description}</p>
              </div>

              {/* Validation Errors */}
              {validationErrors.length > 0 && (
                <Alert className="border-red-200 bg-red-50">
                  <AlertCircle className="h-4 w-4 text-red-600" />
                  <AlertDescription className="text-red-800">
                    Please complete all required fields before proceeding.
                  </AlertDescription>
                </Alert>
              )}

              {/* Questions */}
              <div className="space-y-6">
                {currentStepData.questions.map((question) => (
                  <QuestionField
                    key={question.id}
                    question={question}
                    value={formData[question.id]}
                    onChange={(value) => handleFieldChange(question.id, value)}
                    error={validationErrors.find(e => e.questionId === question.id)?.message}
                  />
                ))}
              </div>
            </div>
          </Card>
        </div>

        {/* Footer */}
        <DialogFooter className="flex justify-between items-center pt-4 border-t">
          <div className="flex items-center space-x-2">
            {isDirty && (
              <div className="flex items-center text-sm text-amber-600">
                <Clock className="h-4 w-4 mr-1" />
                Unsaved changes
              </div>
            )}
          </div>

          <div className="flex space-x-3">
            <Button
              variant="outline"
              onClick={handlePrevious}
              disabled={currentStep === 0}
            >
              <ChevronLeft className="h-4 w-4 mr-2" />
              Previous
            </Button>

            <Button
              variant="outline"
              onClick={autoSave}
              disabled={!isDirty}
            >
              <Save className="h-4 w-4 mr-2" />
              Save Draft
            </Button>

            {isLastStep ? (
              <Button
                onClick={handleSubmit}
                disabled={!canProceed || submitMutation.isPending}
                className="bg-green-600 hover:bg-green-700"
              >
                {submitMutation.isPending ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Submitting...
                  </>
                ) : (
                  <>
                    <CheckCircle className="h-4 w-4 mr-2" />
                    Complete Assessment
                  </>
                )}
              </Button>
            ) : (
              <Button
                onClick={handleNext}
                disabled={!canProceed}
              >
                Next
                <ChevronRight className="h-4 w-4 ml-2" />
              </Button>
            )}
          </div>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

// Export trigger component for easy use
export function BIAQuestionnaireDialog({
  children,
  functionId,
  onComplete
}: {
  children: React.ReactNode
  functionId?: string
  onComplete?: (result: any) => void
}) {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <>
      <DialogTrigger asChild onClick={() => setIsOpen(true)}>
        {children}
      </DialogTrigger>
      <BIAQuestionnaire
        functionId={functionId}
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
        onComplete={(result) => {
          onComplete?.(result)
          setIsOpen(false)
        }}
      />
    </>
  )
}