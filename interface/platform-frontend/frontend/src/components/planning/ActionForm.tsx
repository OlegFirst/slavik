'use client';

import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { actionPlanCreateSchema, actionPlanUpdateSchema } from '@/lib/validations/planning-validation';
import type { ActionPlan, ActionPlanCreate } from '@/types/planning';
import { ActionType, Priority, ActionStatus } from '@/types/planning';
import {
  CheckSquare,
  Save,
  X,
  Calendar,
  AlertCircle,
  TrendingUp,
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface ActionFormProps {
  initialData?: ActionPlan;
  planId: string;
  onSubmit: (data: ActionPlanCreate) => void;
  onCancel?: () => void;
  isLoading?: boolean;
  className?: string;
}

/**
 * ActionForm - Create or edit action plans
 *
 * Features:
 * - Action item metadata (title, type, priority)
 * - Responsibility assignment (primary + backup)
 * - Timeline management (start, target, completion dates)
 * - Progress tracking with slider
 * - Zod validation
 * - Edit/Create modes
 */
export function ActionForm({
  initialData,
  planId,
  onSubmit,
  onCancel,
  isLoading = false,
  className,
}: ActionFormProps) {
  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<ActionPlanCreate>({
    resolver: zodResolver(initialData ? actionPlanUpdateSchema : actionPlanCreateSchema),
    defaultValues: initialData ? {
      plan_id: initialData.plan_id,
      action_title: initialData.action_title,
      action_type: initialData.action_type,
      priority: initialData.priority,
      description: initialData.description,
      responsible_party: initialData.responsible_party,
      backup_responsible: initialData.backup_responsible,
      start_date: initialData.start_date,
      target_date: initialData.target_date,
      completion_date: initialData.completion_date,
      status: initialData.status,
      progress_percentage: initialData.progress_percentage,
      depends_on: initialData.depends_on,
      blocks: initialData.blocks,
    } : {
      plan_id: planId,
      action_type: ActionType.PREVENTIVE,
      priority: Priority.MEDIUM,
      status: ActionStatus.NOT_STARTED,
      progress_percentage: 0,
      depends_on: [],
      blocks: [],
    },
  });

  // Watch status and progress for UI feedback
  const status = watch('status');
  const progress = watch('progress_percentage');
  const priority = watch('priority');

  const onFormSubmit = (data: ActionPlanCreate) => {
    onSubmit(data);
  };

  // Get priority color
  const getPriorityBg = (p: Priority) => {
    switch (p) {
      case Priority.CRITICAL:
        return 'bg-red-100 border-red-300';
      case Priority.HIGH:
        return 'bg-orange-100 border-orange-300';
      case Priority.MEDIUM:
        return 'bg-yellow-100 border-yellow-300';
      case Priority.LOW:
        return 'bg-gray-100 border-gray-300';
      default:
        return 'bg-gray-100 border-gray-300';
    }
  };

  return (
    <form onSubmit={handleSubmit(onFormSubmit)} className={cn('space-y-6', className)}>
      {/* Basic Information */}
      <div className={cn('rounded-lg border-2 p-6', getPriorityBg(priority))}>
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <CheckSquare className="w-5 h-5 text-purple-600" />
          Action Information
        </h3>

        <div className="space-y-4">
          {/* Action Title */}
          <div>
            <label htmlFor="action_title" className="block text-sm font-medium text-gray-700 mb-1">
              Action Title <span className="text-red-500">*</span>
            </label>
            <input
              {...register('action_title')}
              type="text"
              id="action_title"
              className={cn(
                'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 bg-white',
                errors.action_title ? 'border-red-500' : 'border-gray-300'
              )}
              placeholder="e.g., Implement backup power system"
            />
            {errors.action_title && (
              <p className="text-sm text-red-600 mt-1">{errors.action_title.message}</p>
            )}
          </div>

          {/* Action Type and Priority */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label htmlFor="action_type" className="block text-sm font-medium text-gray-700 mb-1">
                Action Type <span className="text-red-500">*</span>
              </label>
              <select
                {...register('action_type')}
                id="action_type"
                className={cn(
                  'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 bg-white',
                  errors.action_type ? 'border-red-500' : 'border-gray-300'
                )}
              >
                <option value={ActionType.PREVENTIVE}>Preventive</option>
                <option value={ActionType.DETECTIVE}>Detective</option>
                <option value={ActionType.CORRECTIVE}>Corrective</option>
                <option value={ActionType.RECOVERY}>Recovery</option>
              </select>
              {errors.action_type && (
                <p className="text-sm text-red-600 mt-1">{errors.action_type.message}</p>
              )}
            </div>

            <div>
              <label htmlFor="priority" className="block text-sm font-medium text-gray-700 mb-1 flex items-center gap-1">
                <AlertCircle className="w-4 h-4" />
                Priority <span className="text-red-500">*</span>
              </label>
              <select
                {...register('priority')}
                id="priority"
                className={cn(
                  'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 bg-white',
                  errors.priority ? 'border-red-500' : 'border-gray-300'
                )}
              >
                <option value={Priority.CRITICAL}>Critical</option>
                <option value={Priority.HIGH}>High</option>
                <option value={Priority.MEDIUM}>Medium</option>
                <option value={Priority.LOW}>Low</option>
              </select>
              {errors.priority && (
                <p className="text-sm text-red-600 mt-1">{errors.priority.message}</p>
              )}
            </div>
          </div>

          {/* Description */}
          <div>
            <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
              Description <span className="text-red-500">*</span>
            </label>
            <textarea
              {...register('description')}
              id="description"
              rows={4}
              className={cn(
                'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 bg-white',
                errors.description ? 'border-red-500' : 'border-gray-300'
              )}
              placeholder="Describe the action in detail..."
            />
            {errors.description && (
              <p className="text-sm text-red-600 mt-1">{errors.description.message}</p>
            )}
          </div>
        </div>
      </div>

      {/* Responsibility */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Responsibility</h3>

        <div className="space-y-4">
          {/* Responsible Party */}
          <div>
            <label htmlFor="responsible_party" className="block text-sm font-medium text-gray-700 mb-1">
              Responsible Party <span className="text-red-500">*</span>
            </label>
            <input
              {...register('responsible_party')}
              type="text"
              id="responsible_party"
              className={cn(
                'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500',
                errors.responsible_party ? 'border-red-500' : 'border-gray-300'
              )}
              placeholder="e.g., John Doe, IT Manager"
            />
            {errors.responsible_party && (
              <p className="text-sm text-red-600 mt-1">{errors.responsible_party.message}</p>
            )}
          </div>

          {/* Backup Responsible */}
          <div>
            <label htmlFor="backup_responsible" className="block text-sm font-medium text-gray-700 mb-1">
              Backup Responsible (Optional)
            </label>
            <input
              {...register('backup_responsible')}
              type="text"
              id="backup_responsible"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
              placeholder="e.g., Jane Smith, Deputy IT Manager"
            />
            {errors.backup_responsible && (
              <p className="text-sm text-red-600 mt-1">{errors.backup_responsible.message}</p>
            )}
          </div>
        </div>
      </div>

      {/* Timeline */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <Calendar className="w-5 h-5 text-blue-600" />
          Timeline
        </h3>

        <div className="grid grid-cols-3 gap-4">
          {/* Start Date */}
          <div>
            <label htmlFor="start_date" className="block text-sm font-medium text-gray-700 mb-1">
              Start Date
            </label>
            <input
              {...register('start_date')}
              type="date"
              id="start_date"
              className={cn(
                'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500',
                errors.start_date ? 'border-red-500' : 'border-gray-300'
              )}
            />
            {errors.start_date && (
              <p className="text-sm text-red-600 mt-1">{errors.start_date.message}</p>
            )}
          </div>

          {/* Target Date */}
          <div>
            <label htmlFor="target_date" className="block text-sm font-medium text-gray-700 mb-1">
              Target Date
            </label>
            <input
              {...register('target_date')}
              type="date"
              id="target_date"
              className={cn(
                'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500',
                errors.target_date ? 'border-red-500' : 'border-gray-300'
              )}
            />
            {errors.target_date && (
              <p className="text-sm text-red-600 mt-1">{errors.target_date.message}</p>
            )}
          </div>

          {/* Completion Date */}
          <div>
            <label htmlFor="completion_date" className="block text-sm font-medium text-gray-700 mb-1">
              Completion Date
            </label>
            <input
              {...register('completion_date')}
              type="date"
              id="completion_date"
              className={cn(
                'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500',
                errors.completion_date ? 'border-red-500' : 'border-gray-300'
              )}
            />
            {errors.completion_date && (
              <p className="text-sm text-red-600 mt-1">{errors.completion_date.message}</p>
            )}
          </div>
        </div>
      </div>

      {/* Progress */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-green-600" />
          Progress & Status
        </h3>

        <div className="space-y-4">
          {/* Status */}
          <div>
            <label htmlFor="status" className="block text-sm font-medium text-gray-700 mb-1">
              Status <span className="text-red-500">*</span>
            </label>
            <select
              {...register('status')}
              id="status"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              <option value={ActionStatus.NOT_STARTED}>Not Started</option>
              <option value={ActionStatus.IN_PROGRESS}>In Progress</option>
              <option value={ActionStatus.COMPLETED}>Completed</option>
              <option value={ActionStatus.DELAYED}>Delayed</option>
              <option value={ActionStatus.CANCELLED}>Cancelled</option>
            </select>
          </div>

          {/* Progress Percentage */}
          <div>
            <label htmlFor="progress_percentage" className="block text-sm font-medium text-gray-700 mb-1">
              Progress: {progress}%
            </label>
            <div className="flex items-center gap-3">
              <input
                {...register('progress_percentage', { valueAsNumber: true })}
                type="range"
                id="progress_percentage"
                min="0"
                max="100"
                step="5"
                className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-purple-600"
              />
              <input
                {...register('progress_percentage', { valueAsNumber: true })}
                type="number"
                min="0"
                max="100"
                className="w-20 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
              />
            </div>
            {errors.progress_percentage && (
              <p className="text-sm text-red-600 mt-1">{errors.progress_percentage.message}</p>
            )}

            {/* Progress Bar Visualization */}
            <div className="mt-3 bg-gray-200 rounded-full h-4 overflow-hidden">
              <div
                className={cn(
                  'h-full transition-all duration-300',
                  progress < 25 && 'bg-red-500',
                  progress >= 25 && progress < 50 && 'bg-orange-500',
                  progress >= 50 && progress < 75 && 'bg-yellow-500',
                  progress >= 75 && progress < 100 && 'bg-green-500',
                  progress === 100 && 'bg-green-600'
                )}
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>

          {/* Status Info */}
          <div className={cn(
            'p-3 rounded-lg border',
            status === ActionStatus.NOT_STARTED && 'bg-gray-50 border-gray-200',
            status === ActionStatus.IN_PROGRESS && 'bg-blue-50 border-blue-200',
            status === ActionStatus.COMPLETED && 'bg-green-50 border-green-200',
            status === ActionStatus.DELAYED && 'bg-red-50 border-red-200',
            status === ActionStatus.CANCELLED && 'bg-gray-50 border-gray-300'
          )}>
            <p className="text-sm text-gray-700">
              <strong>Current Status:</strong> {status.replace('_', ' ').toUpperCase()} - {progress}% complete
            </p>
          </div>
        </div>
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
          className="px-6 py-2.5 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors inline-flex items-center gap-2 disabled:opacity-50"
        >
          <Save className="w-4 h-4" />
          {isLoading ? 'Saving...' : initialData ? 'Update Action' : 'Create Action'}
        </button>
      </div>
    </form>
  );
}
