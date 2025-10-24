'use client';

import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { recoveryStrategyCreateSchema, recoveryStrategyUpdateSchema } from '@/lib/validations/planning-validation';
import type { RecoveryStrategy, RecoveryStrategyCreate, RecoveryStep, Personnel } from '@/types/planning';
import { StrategyType } from '@/types/planning';
import {
  GitBranch,
  Save,
  X,
  Plus,
  Trash2,
  Clock,
  Users,
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface StrategyFormProps {
  initialData?: RecoveryStrategy;
  planId: string;
  onSubmit: (data: RecoveryStrategyCreate) => void;
  onCancel?: () => void;
  isLoading?: boolean;
  className?: string;
}

/**
 * StrategyForm - Create or edit recovery strategies
 *
 * Features:
 * - Recovery strategy metadata
 * - Recovery steps management (dynamic array)
 * - Personnel assignment
 * - Zod validation
 * - Edit/Create modes
 */
export function StrategyForm({
  initialData,
  planId,
  onSubmit,
  onCancel,
  isLoading = false,
  className,
}: StrategyFormProps) {
  const [recoverySteps, setRecoverySteps] = useState<RecoveryStep[]>(
    initialData?.recovery_steps || []
  );
  const [personnel, setPersonnel] = useState<Personnel[]>(
    initialData?.required_personnel || []
  );
  const [newStep, setNewStep] = useState<Partial<RecoveryStep>>({
    step_number: recoverySteps.length + 1,
    step_title: '',
    description: '',
    estimated_duration: 30,
    responsible_role: '',
    dependencies: [],
  });
  const [newPersonnel, setNewPersonnel] = useState<Partial<Personnel>>({
    role: '',
    name: '',
    availability: 'primary',
  });

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RecoveryStrategyCreate>({
    resolver: zodResolver(initialData ? recoveryStrategyUpdateSchema : recoveryStrategyCreateSchema),
    defaultValues: initialData ? {
      plan_id: initialData.plan_id,
      strategy_name: initialData.strategy_name,
      strategy_type: initialData.strategy_type,
      description: initialData.description,
      activation_trigger: initialData.activation_trigger,
      activation_time: initialData.activation_time,
      recovery_steps: initialData.recovery_steps,
      required_personnel: initialData.required_personnel,
      required_equipment: initialData.required_equipment,
      required_facilities: initialData.required_facilities,
      last_tested_at: initialData.last_tested_at,
      test_results: initialData.test_results,
      effectiveness_rating: initialData.effectiveness_rating,
    } : {
      plan_id: planId,
      strategy_type: StrategyType.RECOVERY,
      activation_time: 60,
      recovery_steps: [],
      required_personnel: [],
      required_equipment: [],
      required_facilities: [],
    },
  });

  const handleAddStep = () => {
    if (newStep.step_title && newStep.description && newStep.responsible_role) {
      const validStep: RecoveryStep = {
        step_number: newStep.step_number || recoverySteps.length + 1,
        step_title: newStep.step_title,
        description: newStep.description,
        estimated_duration: newStep.estimated_duration || 30,
        responsible_role: newStep.responsible_role,
        dependencies: newStep.dependencies || [],
      };
      setRecoverySteps([...recoverySteps, validStep]);
      setNewStep({
        step_number: recoverySteps.length + 2,
        step_title: '',
        description: '',
        estimated_duration: 30,
        responsible_role: '',
        dependencies: [],
      });
    }
  };

  const handleRemoveStep = (index: number) => {
    setRecoverySteps(recoverySteps.filter((_, i) => i !== index));
  };

  const handleAddPersonnel = () => {
    if (newPersonnel.role) {
      const validPersonnel: Personnel = {
        role: newPersonnel.role,
        name: newPersonnel.name,
        contact_info: newPersonnel.contact_info,
        availability: newPersonnel.availability as Personnel['availability'],
      };
      setPersonnel([...personnel, validPersonnel]);
      setNewPersonnel({
        role: '',
        name: '',
        availability: 'primary',
      });
    }
  };

  const handleRemovePersonnel = (index: number) => {
    setPersonnel(personnel.filter((_, i) => i !== index));
  };

  const onFormSubmit = (data: RecoveryStrategyCreate) => {
    onSubmit({
      ...data,
      recovery_steps: recoverySteps,
      required_personnel: personnel,
    });
  };

  return (
    <form onSubmit={handleSubmit(onFormSubmit)} className={cn('space-y-6', className)}>
      {/* Basic Information */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <GitBranch className="w-5 h-5 text-teal-600" />
          Strategy Information
        </h3>

        <div className="space-y-4">
          {/* Strategy Name */}
          <div>
            <label htmlFor="strategy_name" className="block text-sm font-medium text-gray-700 mb-1">
              Strategy Name <span className="text-red-500">*</span>
            </label>
            <input
              {...register('strategy_name')}
              type="text"
              id="strategy_name"
              className={cn(
                'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500',
                errors.strategy_name ? 'border-red-500' : 'border-gray-300'
              )}
              placeholder="e.g., Failover to Backup Data Center"
            />
            {errors.strategy_name && (
              <p className="text-sm text-red-600 mt-1">{errors.strategy_name.message}</p>
            )}
          </div>

          {/* Strategy Type */}
          <div>
            <label htmlFor="strategy_type" className="block text-sm font-medium text-gray-700 mb-1">
              Strategy Type <span className="text-red-500">*</span>
            </label>
            <select
              {...register('strategy_type')}
              id="strategy_type"
              className={cn(
                'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500',
                errors.strategy_type ? 'border-red-500' : 'border-gray-300'
              )}
            >
              <option value={StrategyType.PREVENTION}>Prevention</option>
              <option value={StrategyType.MITIGATION}>Mitigation</option>
              <option value={StrategyType.RECOVERY}>Recovery</option>
              <option value={StrategyType.TRANSFER}>Transfer</option>
            </select>
            {errors.strategy_type && (
              <p className="text-sm text-red-600 mt-1">{errors.strategy_type.message}</p>
            )}
          </div>

          {/* Description */}
          <div>
            <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
              Description <span className="text-red-500">*</span>
            </label>
            <textarea
              {...register('description')}
              id="description"
              rows={3}
              className={cn(
                'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500',
                errors.description ? 'border-red-500' : 'border-gray-300'
              )}
              placeholder="Describe the recovery strategy..."
            />
            {errors.description && (
              <p className="text-sm text-red-600 mt-1">{errors.description.message}</p>
            )}
          </div>
        </div>
      </div>

      {/* Activation */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <Clock className="w-5 h-5 text-orange-600" />
          Activation
        </h3>

        <div className="space-y-4">
          {/* Activation Trigger */}
          <div>
            <label htmlFor="activation_trigger" className="block text-sm font-medium text-gray-700 mb-1">
              Activation Trigger <span className="text-red-500">*</span>
            </label>
            <input
              {...register('activation_trigger')}
              type="text"
              id="activation_trigger"
              className={cn(
                'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500',
                errors.activation_trigger ? 'border-red-500' : 'border-gray-300'
              )}
              placeholder="e.g., Primary system failure detected"
            />
            {errors.activation_trigger && (
              <p className="text-sm text-red-600 mt-1">{errors.activation_trigger.message}</p>
            )}
          </div>

          {/* Activation Time */}
          <div>
            <label htmlFor="activation_time" className="block text-sm font-medium text-gray-700 mb-1">
              Activation Time (minutes) <span className="text-red-500">*</span>
            </label>
            <input
              {...register('activation_time', { valueAsNumber: true })}
              type="number"
              id="activation_time"
              className={cn(
                'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500',
                errors.activation_time ? 'border-red-500' : 'border-gray-300'
              )}
              placeholder="60"
            />
            {errors.activation_time && (
              <p className="text-sm text-red-600 mt-1">{errors.activation_time.message}</p>
            )}
            <p className="text-xs text-gray-500 mt-1">Time required to activate this strategy</p>
          </div>
        </div>
      </div>

      {/* Recovery Steps */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Recovery Steps</h3>

        <div className="grid grid-cols-12 gap-3 mb-4">
          <div className="col-span-1">
            <label className="block text-sm font-medium text-gray-700 mb-1">#</label>
            <input
              type="number"
              value={newStep.step_number}
              onChange={(e) => setNewStep({ ...newStep, step_number: parseInt(e.target.value) })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
            />
          </div>

          <div className="col-span-3">
            <label className="block text-sm font-medium text-gray-700 mb-1">Title</label>
            <input
              type="text"
              value={newStep.step_title}
              onChange={(e) => setNewStep({ ...newStep, step_title: e.target.value })}
              placeholder="Step title..."
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
            />
          </div>

          <div className="col-span-3">
            <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <input
              type="text"
              value={newStep.description}
              onChange={(e) => setNewStep({ ...newStep, description: e.target.value })}
              placeholder="Description..."
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
            />
          </div>

          <div className="col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">Duration (min)</label>
            <input
              type="number"
              value={newStep.estimated_duration}
              onChange={(e) => setNewStep({ ...newStep, estimated_duration: parseInt(e.target.value) })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
            />
          </div>

          <div className="col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">Role</label>
            <input
              type="text"
              value={newStep.responsible_role}
              onChange={(e) => setNewStep({ ...newStep, responsible_role: e.target.value })}
              placeholder="Role..."
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
            />
          </div>

          <div className="col-span-1 flex items-end">
            <button
              type="button"
              onClick={handleAddStep}
              className="w-full px-3 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition-colors inline-flex items-center justify-center"
            >
              <Plus className="w-4 h-4" />
            </button>
          </div>
        </div>

        <div className="space-y-2">
          {recoverySteps.map((step, index) => (
            <div key={index} className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <span className="inline-flex items-center justify-center w-6 h-6 bg-teal-600 text-white rounded-full text-xs font-semibold">
                    {step.step_number}
                  </span>
                  <strong className="text-sm text-gray-900">{step.step_title}</strong>
                  <span className="text-xs text-gray-500">({step.estimated_duration} min)</span>
                </div>
                <p className="text-sm text-gray-600 ml-8">{step.description}</p>
                <p className="text-xs text-gray-500 ml-8 mt-1">Role: {step.responsible_role}</p>
              </div>
              <button
                type="button"
                onClick={() => handleRemoveStep(index)}
                className="p-1 text-red-600 hover:bg-red-50 rounded transition-colors"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          ))}
        </div>

        {recoverySteps.length === 0 && (
          <p className="text-sm text-gray-500 text-center py-4">
            No recovery steps added yet. Add steps to define the recovery process.
          </p>
        )}
      </div>

      {/* Personnel */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <Users className="w-5 h-5 text-purple-600" />
          Required Personnel
        </h3>

        <div className="grid grid-cols-12 gap-3 mb-4">
          <div className="col-span-3">
            <label className="block text-sm font-medium text-gray-700 mb-1">Role</label>
            <input
              type="text"
              value={newPersonnel.role}
              onChange={(e) => setNewPersonnel({ ...newPersonnel, role: e.target.value })}
              placeholder="e.g., IT Manager"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
            />
          </div>

          <div className="col-span-3">
            <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
            <input
              type="text"
              value={newPersonnel.name}
              onChange={(e) => setNewPersonnel({ ...newPersonnel, name: e.target.value })}
              placeholder="Person name (optional)"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
            />
          </div>

          <div className="col-span-3">
            <label className="block text-sm font-medium text-gray-700 mb-1">Contact</label>
            <input
              type="text"
              value={newPersonnel.contact_info}
              onChange={(e) => setNewPersonnel({ ...newPersonnel, contact_info: e.target.value })}
              placeholder="Phone/Email (optional)"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
            />
          </div>

          <div className="col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">Availability</label>
            <select
              value={newPersonnel.availability}
              onChange={(e) => setNewPersonnel({ ...newPersonnel, availability: e.target.value as Personnel['availability'] })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
            >
              <option value="primary">Primary</option>
              <option value="backup">Backup</option>
              <option value="on-call">On-Call</option>
            </select>
          </div>

          <div className="col-span-1 flex items-end">
            <button
              type="button"
              onClick={handleAddPersonnel}
              className="w-full px-3 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors inline-flex items-center justify-center"
            >
              <Plus className="w-4 h-4" />
            </button>
          </div>
        </div>

        <div className="space-y-2">
          {personnel.map((person, index) => (
            <div key={index} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
              <div className="flex-1 grid grid-cols-3 gap-3">
                <p className="text-sm">
                  <strong className="text-gray-700">{person.role}</strong>
                  {person.name && <span className="text-gray-600"> - {person.name}</span>}
                </p>
                <p className="text-sm text-gray-600">{person.contact_info || 'No contact info'}</p>
                <p className="text-sm">
                  <span className={cn(
                    'px-2 py-0.5 rounded-full text-xs font-medium',
                    person.availability === 'primary' && 'bg-green-100 text-green-700',
                    person.availability === 'backup' && 'bg-yellow-100 text-yellow-700',
                    person.availability === 'on-call' && 'bg-blue-100 text-blue-700'
                  )}>
                    {person.availability}
                  </span>
                </p>
              </div>
              <button
                type="button"
                onClick={() => handleRemovePersonnel(index)}
                className="p-1 text-red-600 hover:bg-red-50 rounded transition-colors"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          ))}
        </div>

        {personnel.length === 0 && (
          <p className="text-sm text-gray-500 text-center py-4">
            No personnel assigned yet. Add personnel required for this strategy.
          </p>
        )}
      </div>

      {/* Form Actions */}
      <div className="flex items-center justify-end gap-3">
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            disabled={isLoading}
            className="px-6 py-2.5 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors inline-flex items-center gap-2 disabled:opacity-50"
          >
            <X className="w-4 h-4" />
            Cancel
          </button>
        )}
        <button
          type="submit"
          disabled={isLoading}
          className="px-6 py-2.5 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition-colors inline-flex items-center gap-2 disabled:opacity-50"
        >
          <Save className="w-4 h-4" />
          {isLoading ? 'Saving...' : initialData ? 'Update Strategy' : 'Create Strategy'}
        </button>
      </div>
    </form>
  );
}
