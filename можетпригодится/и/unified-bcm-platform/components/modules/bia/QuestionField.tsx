'use client'

import React from 'react'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Slider } from '@/components/ui/slider'
import { Checkbox } from '@/components/ui/checkbox'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { type BIAQuestion } from '@/services/bia-api'
import { cn } from '@/lib/utils'
import { AlertCircle, DollarSign, Hash, Type, List, Scale3D, ChevronDown } from 'lucide-react'

interface QuestionFieldProps {
  question: BIAQuestion
  value?: string | number | string[]
  onChange: (value: string | number | string[]) => void
  error?: string
  disabled?: boolean
}

export function QuestionField({
  question,
  value,
  onChange,
  error,
  disabled = false
}: QuestionFieldProps) {
  const getFieldIcon = () => {
    switch (question.type) {
      case 'number':
        return question.question.toLowerCase().includes('$') || question.question.toLowerCase().includes('financial')
          ? DollarSign
          : Hash
      case 'text':
        return Type
      case 'select':
      case 'multiselect':
        return List
      case 'slider':
      case 'scale':
        return Scale3D
      default:
        return Type
    }
  }

  const Icon = getFieldIcon()

  const renderField = () => {
    switch (question.type) {
      case 'text':
        if (question.question.toLowerCase().includes('description') ||
            question.question.toLowerCase().includes('notes')) {
          return (
            <Textarea
              id={question.id}
              value={(value as string) || ''}
              onChange={(e) => onChange(e.target.value)}
              disabled={disabled}
              placeholder={`Enter ${question.question.toLowerCase()}...`}
              className={cn(
                "min-h-[100px] resize-none",
                error && "border-red-500 focus:ring-red-500"
              )}
            />
          )
        }
        return (
          <Input
            id={question.id}
            type="text"
            value={(value as string) || ''}
            onChange={(e) => onChange(e.target.value)}
            disabled={disabled}
            placeholder={`Enter ${question.question.toLowerCase()}...`}
            className={cn(error && "border-red-500 focus:ring-red-500")}
          />
        )

      case 'number':
        const isFinancial = question.question.toLowerCase().includes('$') ||
                           question.question.toLowerCase().includes('financial') ||
                           question.question.toLowerCase().includes('cost')
        const isCurrency = question.question.toLowerCase().includes('$')

        return (
          <div className="relative">
            {isCurrency && (
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <DollarSign className="h-4 w-4 text-gray-400" />
              </div>
            )}
            <Input
              id={question.id}
              type="number"
              value={(value as number) || ''}
              onChange={(e) => onChange(Number(e.target.value))}
              disabled={disabled}
              placeholder={isFinancial ? "0.00" : "Enter number..."}
              className={cn(
                isCurrency && "pl-10",
                error && "border-red-500 focus:ring-red-500"
              )}
              min="0"
              step={isFinancial ? "0.01" : "1"}
            />
            {isFinancial && !isCurrency && (
              <div className="text-xs text-gray-500 mt-1">
                Enter amount in dollars (e.g., 50000 for $50,000)
              </div>
            )}
          </div>
        )

      case 'select':
        return (
          <Select
            value={(value as string) || ''}
            onValueChange={(selectedValue) => onChange(selectedValue)}
            disabled={disabled}
          >
            <SelectTrigger className={cn(error && "border-red-500 focus:ring-red-500")}>
              <SelectValue placeholder={`Select ${question.question.toLowerCase()}...`} />
            </SelectTrigger>
            <SelectContent>
              {question.options?.map((option) => (
                <SelectItem key={option} value={option.toLowerCase()}>
                  {option}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        )

      case 'multiselect':
        const selectedValues = (value as string[]) || []

        return (
          <div className="space-y-3">
            <div className="text-sm text-gray-600">
              Select all that apply:
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {question.options?.map((option) => {
                const isChecked = selectedValues.includes(option.toLowerCase())
                return (
                  <div key={option} className="flex items-center space-x-3">
                    <Checkbox
                      id={`${question.id}-${option}`}
                      checked={isChecked}
                      onCheckedChange={(checked) => {
                        if (checked) {
                          onChange([...selectedValues, option.toLowerCase()])
                        } else {
                          onChange(selectedValues.filter(v => v !== option.toLowerCase()))
                        }
                      }}
                      disabled={disabled}
                    />
                    <Label
                      htmlFor={`${question.id}-${option}`}
                      className="text-sm font-normal cursor-pointer"
                    >
                      {option}
                    </Label>
                  </div>
                )
              })}
            </div>
            {selectedValues.length > 0 && (
              <div className="flex flex-wrap gap-2 pt-2">
                {selectedValues.map((selected) => (
                  <Badge
                    key={selected}
                    variant="secondary"
                    className="text-xs"
                  >
                    {question.options?.find(opt => opt.toLowerCase() === selected) || selected}
                  </Badge>
                ))}
              </div>
            )}
          </div>
        )

      case 'slider':
      case 'scale':
        const sliderValue = [(value as number) || 1]
        const maxValue = question.type === 'scale' ? 10 : 10
        const step = 1

        return (
          <div className="space-y-4">
            <div className="px-1">
              <Slider
                value={sliderValue}
                onValueChange={(newValue) => onChange(newValue[0])}
                max={maxValue}
                min={1}
                step={step}
                disabled={disabled}
                className={cn(
                  "w-full",
                  error && "[&>span]:bg-red-500"
                )}
              />
            </div>
            <div className="flex justify-between text-xs text-gray-500">
              <span>1 - Low</span>
              <span className="font-medium text-blue-600 bg-blue-50 px-2 py-1 rounded">
                {sliderValue[0]}
              </span>
              <span>{maxValue} - High</span>
            </div>
            {question.type === 'scale' && (
              <div className="text-xs text-gray-500 space-y-1">
                <div>Scale Guidelines:</div>
                <div>• 1-3: Low impact/importance</div>
                <div>• 4-6: Moderate impact/importance</div>
                <div>• 7-8: High impact/importance</div>
                <div>• 9-10: Critical impact/importance</div>
              </div>
            )}
          </div>
        )

      case 'currency':
        return (
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <DollarSign className="h-4 w-4 text-gray-400" />
            </div>
            <Input
              id={question.id}
              type="number"
              value={(value as number) || ''}
              onChange={(e) => onChange(Number(e.target.value))}
              disabled={disabled}
              placeholder="0.00"
              className={cn(
                "pl-10",
                error && "border-red-500 focus:ring-red-500"
              )}
              min="0"
              step="0.01"
            />
            <div className="text-xs text-gray-500 mt-1">
              Enter amount in USD
            </div>
          </div>
        )

      default:
        return (
          <Input
            id={question.id}
            type="text"
            value={(value as string) || ''}
            onChange={(e) => onChange(e.target.value)}
            disabled={disabled}
            placeholder={`Enter ${question.question.toLowerCase()}...`}
            className={cn(error && "border-red-500 focus:ring-red-500")}
          />
        )
    }
  }

  const getQuestionHint = () => {
    const questionLower = question.question.toLowerCase()

    if (questionLower.includes('rto')) {
      return "Recovery Time Objective: The maximum acceptable length of time to restore a function after disruption"
    }
    if (questionLower.includes('rpo')) {
      return "Recovery Point Objective: The maximum acceptable amount of data loss measured in time"
    }
    if (questionLower.includes('mtpd')) {
      return "Maximum Tolerable Period of Disruption: The time beyond which the organization cannot survive"
    }
    if (questionLower.includes('financial impact')) {
      return "Consider lost revenue, additional costs, penalties, and opportunity costs"
    }
    if (questionLower.includes('criticality')) {
      return "Consider the importance to business operations, customer impact, and regulatory requirements"
    }

    return null
  }

  const hint = getQuestionHint()

  return (
    <div className="space-y-3">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <Label
            htmlFor={question.id}
            className="text-sm font-medium flex items-center gap-2"
          >
            <Icon className="h-4 w-4 text-gray-500" />
            {question.question}
            {question.required && (
              <span className="text-red-500 text-xs">*</span>
            )}
            {question.weight && (
              <Badge variant="outline" className="text-xs">
                Weight: {(question.weight * 100).toFixed(0)}%
              </Badge>
            )}
          </Label>
          {hint && (
            <div className="text-xs text-gray-500 mt-1 italic">
              💡 {hint}
            </div>
          )}
        </div>
      </div>

      {renderField()}

      {error && (
        <Alert className="border-red-200 bg-red-50">
          <AlertCircle className="h-4 w-4 text-red-600" />
          <AlertDescription className="text-red-800 text-sm">
            {error}
          </AlertDescription>
        </Alert>
      )}

      {/* Display current value for complex fields */}
      {(question.type === 'multiselect' && Array.isArray(value) && value.length > 0) && (
        <div className="text-xs text-gray-500">
          {value.length} item{value.length !== 1 ? 's' : ''} selected
        </div>
      )}

      {(question.type === 'number' && typeof value === 'number' && value > 0) && (
        <div className="text-xs text-gray-500">
          {question.question.toLowerCase().includes('$')
            ? `$${value.toLocaleString()}`
            : question.question.toLowerCase().includes('%')
            ? `${value}%`
            : `${value} ${question.question.toLowerCase().includes('hour') ? 'hours' : 'units'}`
          }
        </div>
      )}
    </div>
  )
}