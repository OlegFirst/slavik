'use client';

import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import type { TreatmentPlanCreate, TreatmentStrategy, TreatmentAction } from '@/types/risk';
import { TreatmentStrategy as TS } from '@/types/risk';
import { Plus, Trash2, Save } from 'lucide-react';
import { cn } from '@/lib/utils';

interface TreatmentPlanFormProps {
  riskId: string;
  initialData?: any;
  onSubmit: (data: TreatmentPlanCreate) => void;
  onCancel?: () => void;
  isLoading?: boolean;
  className?: string;
}

export function TreatmentPlanForm({
  riskId,
  initialData,
  onSubmit,
  onCancel,
  isLoading,
  className,
}: TreatmentPlanFormProps) {
  const [actions, setActions] = useState<TreatmentAction[]>(
    initialData?.actions || []
  );

  const { register, handleSubmit, formState: { errors } } = useForm<TreatmentPlanCreate>({
    defaultValues: initialData || {
      strategy: TS.MITIGATE,
    },
  });

  const addAction = () => {
    setActions([
      ...actions,
      { action: '', responsible: '', deadline: '', status: 'planned' }
    ]);
  };

  const removeAction = (index: number) => {
    setActions(actions.filter((_, i) => i !== index));
  };

  const updateAction = (index: number, field: keyof TreatmentAction, value: string) => {
    const newActions = [...actions];
    newActions[index] = { ...newActions[index], [field]: value };
    setActions(newActions);
  };

  const onFormSubmit = (data: TreatmentPlanCreate) => {
    onSubmit({ ...data, actions });
  };

  return (
    <form onSubmit={handleSubmit(onFormSubmit)} className={cn('space-y-6', className)}>
      {/* Strategy Selection */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Treatment Strategy <span className="text-red-500">*</span>
        </label>
        <select
          {...register('strategy', { required: true })}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
        >
          <option value={TS.AVOID}>Avoid - Eliminate the risk</option>
          <option value={TS.MITIGATE}>Mitigate - Reduce likelihood/impact</option>
          <option value={TS.TRANSFER}>Transfer - Insurance/outsourcing</option>
          <option value={TS.ACCEPT}>Accept - Accept the risk</option>
        </select>
        {errors.strategy && (
          <p className="mt-1 text-sm text-red-600">Strategy is required</p>
        )}
      </div>

      {/* Description */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Description <span className="text-red-500">*</span>
        </label>
        <textarea
          {...register('description', { required: true })}
          rows={4}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
          placeholder="Describe the treatment plan..."
        />
        {errors.description && (
          <p className="mt-1 text-sm text-red-600">Description is required</p>
        )}
      </div>

      {/* Actions */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <label className="block text-sm font-medium text-gray-700">
            Action Items
          </label>
          <button
            type="button"
            onClick={addAction}
            className="px-3 py-1.5 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors inline-flex items-center gap-2 text-sm"
          >
            <Plus className="w-4 h-4" />
            Add Action
          </button>
        </div>

        <div className="space-y-3">
          {actions.length === 0 ? (
            <div className="bg-gray-50 rounded-lg p-8 text-center">
              <p className="text-gray-500 text-sm">
                No action items yet. Click "Add Action" to create one.
              </p>
            </div>
          ) : (
            actions.map((action, index) => (
              <div key={index} className="grid grid-cols-[1fr_auto_auto_auto] gap-3 p-3 bg-gray-50 rounded-lg">
                <input
                  type="text"
                  value={action.action || ''}
                  onChange={(e) => updateAction(index, 'action', e.target.value)}
                  placeholder="Action description"
                  className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-orange-500"
                />
                <input
                  type="text"
                  value={action.responsible || ''}
                  onChange={(e) => updateAction(index, 'responsible', e.target.value)}
                  placeholder="Responsible"
                  className="px-3 py-2 border border-gray-300 rounded-lg text-sm w-32 focus:outline-none focus:ring-2 focus:ring-orange-500"
                />
                <input
                  type="date"
                  value={action.deadline || ''}
                  onChange={(e) => updateAction(index, 'deadline', e.target.value)}
                  className="px-3 py-2 border border-gray-300 rounded-lg text-sm w-40 focus:outline-none focus:ring-2 focus:ring-orange-500"
                />
                <button
                  type="button"
                  onClick={() => removeAction(index)}
                  className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                  title="Remove action"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Cost and Date */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Estimated Cost ($)
          </label>
          <input
            {...register('estimated_cost', { valueAsNumber: true })}
            type="number"
            min="0"
            step="0.01"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
            placeholder="0.00"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Target Date
          </label>
          <input
            {...register('target_date')}
            type="date"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
          />
        </div>
      </div>

      {/* Responsible Party */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Responsible Party
        </label>
        <input
          {...register('responsible_party')}
          type="text"
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
          placeholder="Name of person or team responsible"
        />
      </div>

      {/* Form Actions */}
      <div className="flex items-center justify-end gap-3 pt-4 border-t border-gray-200">
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            disabled={isLoading}
            className="px-6 py-2.5 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
          >
            Cancel
          </button>
        )}
        <button
          type="submit"
          disabled={isLoading}
          className="px-6 py-2.5 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors inline-flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Save className="w-4 h-4" />
          {isLoading ? 'Saving...' : 'Save Plan'}
        </button>
      </div>
    </form>
  );
}
