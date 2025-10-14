'use client'

import { useState } from 'react'
import { useForm, FormProvider } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Loader2, Plus, Trash2, AlertTriangle, CheckCircle } from 'lucide-react'
import {
  businessProcessSchema,
  type BusinessProcessInput
} from '@/lib/validations/workflow-schemas'
import { useCreateProcess, useCreateProcessWithWorkflow } from '@/lib/hooks/useWorkflow'

interface CreateProcessFormProps {
  onSuccess?: (process: any) => void
  onCancel?: () => void
  enableWorkflowCreation?: boolean
}

export function CreateProcessForm({
  onSuccess,
  onCancel,
  enableWorkflowCreation = false
}: CreateProcessFormProps) {
  const [stakeholders, setStakeholders] = useState<string[]>([''])
  const [currentStakeholder, setCurrentStakeholder] = useState('')

  const createProcess = useCreateProcess()
  const createProcessWithWorkflow = useCreateProcessWithWorkflow()

  const form = useForm<BusinessProcessInput>({
    resolver: zodResolver(businessProcessSchema),
    defaultValues: {
      name: '',
      description: '',
      category: 'bcp',
      status: 'draft',
      owner: '',
      department: '',
      stakeholders: [],
      complexity: 'medium',
      criticality: 'medium',
      rto: '4 hours',
      rpo: '1 hour',
      version: '1.0'
    },
    mode: 'onChange' // Real-time validation
  })

  const { handleSubmit, register, setValue, watch, formState: { errors, isValid, isSubmitting } } = form

  const addStakeholder = () => {
    if (currentStakeholder.trim() && !stakeholders.includes(currentStakeholder.trim())) {
      const newStakeholders = [...stakeholders.filter(s => s), currentStakeholder.trim()]
      setStakeholders(newStakeholders)
      setValue('stakeholders', newStakeholders)
      setCurrentStakeholder('')
    }
  }

  const removeStakeholder = (index: number) => {
    const newStakeholders = stakeholders.filter((_, i) => i !== index)
    setStakeholders(newStakeholders)
    setValue('stakeholders', newStakeholders)
  }

  const onSubmit = async (data: BusinessProcessInput) => {
    try {
      if (enableWorkflowCreation) {
        await createProcessWithWorkflow.mutateAsync({
          process: data,
          // Could add BPMN and automation data here
        })
      } else {
        await createProcess.mutateAsync(data)
      }

      onSuccess?.(data)
    } catch (error) {
      // Error handling is done in the hooks
      console.error('Form submission error:', error)
    }
  }

  const isLoading = createProcess.isPending || createProcessWithWorkflow.isPending

  return (
    <FormProvider {...form}>
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              {enableWorkflowCreation ? '🔄 Create Complete Workflow' : '📋 Create Business Process'}
            </CardTitle>
            <CardDescription>
              {enableWorkflowCreation
                ? 'Create a business process with optional BPMN diagram and automation rules'
                : 'Define a new business continuity process for your organization'
              }
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Basic Information */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="name">
                  Process Name <span className="text-red-500">*</span>
                </Label>
                <Input
                  id="name"
                  {...register('name')}
                  placeholder="e.g., Emergency Response Protocol"
                  className={errors.name ? 'border-red-500' : ''}
                />
                {errors.name && (
                  <p className="text-sm text-red-500 mt-1">{errors.name.message}</p>
                )}
              </div>

              <div>
                <Label htmlFor="category">
                  Category <span className="text-red-500">*</span>
                </Label>
                <Select onValueChange={(value) => setValue('category', value as any)}>
                  <SelectTrigger className={errors.category ? 'border-red-500' : ''}>
                    <SelectValue placeholder="Select category" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="bcp">Business Continuity Planning</SelectItem>
                    <SelectItem value="incident">Incident Management</SelectItem>
                    <SelectItem value="training">Training & Education</SelectItem>
                    <SelectItem value="audit">Audit & Compliance</SelectItem>
                    <SelectItem value="governance">Governance</SelectItem>
                  </SelectContent>
                </Select>
                {errors.category && (
                  <p className="text-sm text-red-500 mt-1">{errors.category.message}</p>
                )}
              </div>
            </div>

            <div>
              <Label htmlFor="description">
                Description <span className="text-red-500">*</span>
              </Label>
              <Textarea
                id="description"
                {...register('description')}
                placeholder="Describe the purpose and scope of this process"
                rows={3}
                className={errors.description ? 'border-red-500' : ''}
              />
              {errors.description && (
                <p className="text-sm text-red-500 mt-1">{errors.description.message}</p>
              )}
            </div>

            {/* Ownership */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="owner">
                  Process Owner <span className="text-red-500">*</span>
                </Label>
                <Input
                  id="owner"
                  {...register('owner')}
                  placeholder="John Smith"
                  className={errors.owner ? 'border-red-500' : ''}
                />
                {errors.owner && (
                  <p className="text-sm text-red-500 mt-1">{errors.owner.message}</p>
                )}
              </div>

              <div>
                <Label htmlFor="department">
                  Department <span className="text-red-500">*</span>
                </Label>
                <Input
                  id="department"
                  {...register('department')}
                  placeholder="Risk Management"
                  className={errors.department ? 'border-red-500' : ''}
                />
                {errors.department && (
                  <p className="text-sm text-red-500 mt-1">{errors.department.message}</p>
                )}
              </div>
            </div>

            {/* Stakeholders */}
            <div>
              <Label>
                Stakeholders <span className="text-red-500">*</span>
              </Label>
              <div className="flex gap-2 mt-1">
                <Input
                  value={currentStakeholder}
                  onChange={(e) => setCurrentStakeholder(e.target.value)}
                  placeholder="Add stakeholder"
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault()
                      addStakeholder()
                    }
                  }}
                />
                <Button type="button" onClick={addStakeholder} size="sm">
                  <Plus className="h-4 w-4" />
                </Button>
              </div>

              {stakeholders.filter(s => s).length > 0 && (
                <div className="flex flex-wrap gap-2 mt-2">
                  {stakeholders.filter(s => s).map((stakeholder, index) => (
                    <Badge key={index} variant="secondary" className="flex items-center gap-1">
                      {stakeholder}
                      <button
                        type="button"
                        onClick={() => removeStakeholder(index)}
                        className="ml-1 hover:bg-red-100 rounded-full p-1"
                      >
                        <Trash2 className="h-3 w-3" />
                      </button>
                    </Badge>
                  ))}
                </div>
              )}

              {errors.stakeholders && (
                <p className="text-sm text-red-500 mt-1">{errors.stakeholders.message}</p>
              )}
            </div>

            {/* Process Characteristics */}
            <div className="grid grid-cols-3 gap-4">
              <div>
                <Label htmlFor="complexity">Complexity</Label>
                <Select onValueChange={(value) => setValue('complexity', value as any)}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select complexity" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="low">Low</SelectItem>
                    <SelectItem value="medium">Medium</SelectItem>
                    <SelectItem value="high">High</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label htmlFor="criticality">
                  Criticality <span className="text-red-500">*</span>
                </Label>
                <Select onValueChange={(value) => setValue('criticality', value as any)}>
                  <SelectTrigger className={errors.criticality ? 'border-red-500' : ''}>
                    <SelectValue placeholder="Select criticality" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="low">Low</SelectItem>
                    <SelectItem value="medium">Medium</SelectItem>
                    <SelectItem value="high">High</SelectItem>
                    <SelectItem value="critical">Critical</SelectItem>
                  </SelectContent>
                </Select>
                {errors.criticality && (
                  <p className="text-sm text-red-500 mt-1">{errors.criticality.message}</p>
                )}
              </div>

              <div>
                <Label htmlFor="status">Status</Label>
                <Select onValueChange={(value) => setValue('status', value as any)}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select status" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="draft">Draft</SelectItem>
                    <SelectItem value="under_review">Under Review</SelectItem>
                    <SelectItem value="active">Active</SelectItem>
                    <SelectItem value="archived">Archived</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            {/* RTO/RPO */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="rto">
                  RTO (Recovery Time Objective) <span className="text-red-500">*</span>
                </Label>
                <Input
                  id="rto"
                  {...register('rto')}
                  placeholder="e.g., 4 hours"
                  className={errors.rto ? 'border-red-500' : ''}
                />
                {errors.rto && (
                  <p className="text-sm text-red-500 mt-1">{errors.rto.message}</p>
                )}
                <p className="text-xs text-gray-500 mt-1">
                  Format: "X minutes/hours/days" (e.g., "2 hours", "30 minutes")
                </p>
              </div>

              <div>
                <Label htmlFor="rpo">
                  RPO (Recovery Point Objective) <span className="text-red-500">*</span>
                </Label>
                <Input
                  id="rpo"
                  {...register('rpo')}
                  placeholder="e.g., 1 hour"
                  className={errors.rpo ? 'border-red-500' : ''}
                />
                {errors.rpo && (
                  <p className="text-sm text-red-500 mt-1">{errors.rpo.message}</p>
                )}
                <p className="text-xs text-gray-500 mt-1">
                  Must be less than or equal to RTO
                </p>
              </div>
            </div>

            {/* Form Validation Status */}
            {Object.keys(errors).length > 0 && (
              <Alert variant="destructive">
                <AlertTriangle className="h-4 w-4" />
                <AlertDescription>
                  Please fix the validation errors above before submitting.
                </AlertDescription>
              </Alert>
            )}

            {isValid && Object.keys(errors).length === 0 && watch('name') && (
              <Alert>
                <CheckCircle className="h-4 w-4" />
                <AlertDescription>
                  Form is valid and ready to submit.
                </AlertDescription>
              </Alert>
            )}
          </CardContent>
        </Card>

        {/* Submit Buttons */}
        <div className="flex justify-end space-x-2">
          {onCancel && (
            <Button type="button" variant="outline" onClick={onCancel} disabled={isLoading}>
              Cancel
            </Button>
          )}
          <Button type="submit" disabled={!isValid || isLoading}>
            {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            {enableWorkflowCreation ? 'Create Complete Workflow' : 'Create Process'}
          </Button>
        </div>
      </form>
    </FormProvider>
  )
}