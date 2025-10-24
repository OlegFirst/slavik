'use client';

import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { bcPlanCreateSchema, bcPlanUpdateSchema, resourceSchema } from '@/lib/validations/planning-validation';
import type { BCPlan, BCPlanCreate, Resource } from '@/types/planning';
import { PlanType, StrategyType, PlanStatus } from '@/types/planning';
import {
  FileText,
  Save,
  X,
  Plus,
  Trash2,
  Target,
  DollarSign,
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface PlanFormProps {
  initialData?: BCPlan;
  onSubmit: (data: BCPlanCreate) => void;
  onCancel?: () => void;
  isLoading?: boolean;
  className?: string;
}

/**
 * PlanForm - Create or edit business continuity plans
 *
 * Features:
 * - Full BC plan metadata
 * - Recovery objectives (RTO, RPO, MTPD)
 * - Resource management
 * - Zod validation
 * - Edit/Create modes
 */
export function PlanForm({
  initialData,
  onSubmit,
  onCancel,
  isLoading = false,
  className,
}: PlanFormProps) {
  const [resources, setResources] = useState<Resource[]>(
    initialData?.required_resources || []
  );
  const [newResource, setNewResource] = useState<Partial<Resource>>({
    resource_type: 'personnel',
    resource_name: '',
    availability: 'available',
  });

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<BCPlanCreate>({
    resolver: zodResolver(initialData ? bcPlanUpdateSchema : bcPlanCreateSchema),
    defaultValues: initialData ? {
      organization_id: initialData.organization_id,
      plan_name: initialData.plan_name,
      plan_code: initialData.plan_code,
      plan_type: initialData.plan_type,
      plan_version: initialData.plan_version,
      scope_description: initialData.scope_description,
      applicable_processes: initialData.applicable_processes,
      applicable_assets: initialData.applicable_assets,
      covered_risks: initialData.covered_risks,
      rto_target: initialData.rto_target,
      rpo_target: initialData.rpo_target,
      mtpd_target: initialData.mtpd_target,
      strategy_type: initialData.strategy_type,
      strategy_description: initialData.strategy_description,
      required_resources: initialData.required_resources,
      estimated_cost: initialData.estimated_cost,
      status: initialData.status,
      approved_by: initialData.approved_by,
      approved_at: initialData.approved_at,
      last_reviewed_at: initialData.last_reviewed_at,
      next_review_date: initialData.next_review_date,
      created_by: initialData.created_by,
    } : {
      organization_id: 'org-123', // TODO: Get from auth
      plan_type: PlanType.OPERATIONAL,
      plan_version: '1.0',
      status: PlanStatus.DRAFT,
      applicable_processes: [],
      applicable_assets: [],
      covered_risks: [],
      required_resources: [],
      estimated_cost: 0,
      created_by: 'current-user', // TODO: Get from auth
    },
  });

  // Watch RTO, RPO, MTPD for validation feedback
  const rto = watch('rto_target');
  const rpo = watch('rpo_target');
  const mtpd = watch('mtpd_target');

  const handleAddResource = () => {
    if (newResource.resource_name && newResource.resource_type && newResource.availability) {
      const validResource: Resource = {
        resource_type: newResource.resource_type as Resource['resource_type'],
        resource_name: newResource.resource_name,
        quantity: newResource.quantity,
        cost_estimate: newResource.cost_estimate,
        availability: newResource.availability as Resource['availability'],
      };
      setResources([...resources, validResource]);
      setNewResource({
        resource_type: 'personnel',
        resource_name: '',
        availability: 'available',
      });
    }
  };

  const handleRemoveResource = (index: number) => {
    setResources(resources.filter((_, i) => i !== index));
  };

  const onFormSubmit = (data: BCPlanCreate) => {
    onSubmit({
      ...data,
      required_resources: resources,
    });
  };

  return (
    <form onSubmit={handleSubmit(onFormSubmit)} className={cn('space-y-6', className)}>
      {/* Basic Information */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <FileText className="w-5 h-5 text-blue-600" />
          Plan Information
        </h3>

        <div className="space-y-4">
          {/* Plan Name */}
          <div>
            <label htmlFor="plan_name" className="block text-sm font-medium text-gray-700 mb-1">
              Plan Name <span className="text-red-500">*</span>
            </label>
            <input
              {...register('plan_name')}
              type="text"
              id="plan_name"
              className={cn(
                'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                errors.plan_name ? 'border-red-500' : 'border-gray-300'
              )}
              placeholder="e.g., IT Disaster Recovery Plan"
            />
            {errors.plan_name && (
              <p className="text-sm text-red-600 mt-1">{errors.plan_name.message}</p>
            )}
          </div>

          {/* Plan Code */}
          <div>
            <label htmlFor="plan_code" className="block text-sm font-medium text-gray-700 mb-1">
              Plan Code <span className="text-red-500">*</span>
            </label>
            <input
              {...register('plan_code')}
              type="text"
              id="plan_code"
              className={cn(
                'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                errors.plan_code ? 'border-red-500' : 'border-gray-300'
              )}
              placeholder="e.g., IT-DR-001"
            />
            {errors.plan_code && (
              <p className="text-sm text-red-600 mt-1">{errors.plan_code.message}</p>
            )}
          </div>

          {/* Plan Type */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label htmlFor="plan_type" className="block text-sm font-medium text-gray-700 mb-1">
                Plan Type <span className="text-red-500">*</span>
              </label>
              <select
                {...register('plan_type')}
                id="plan_type"
                className={cn(
                  'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                  errors.plan_type ? 'border-red-500' : 'border-gray-300'
                )}
              >
                <option value={PlanType.STRATEGIC}>Strategic</option>
                <option value={PlanType.TACTICAL}>Tactical</option>
                <option value={PlanType.OPERATIONAL}>Operational</option>
              </select>
              {errors.plan_type && (
                <p className="text-sm text-red-600 mt-1">{errors.plan_type.message}</p>
              )}
            </div>

            <div>
              <label htmlFor="plan_version" className="block text-sm font-medium text-gray-700 mb-1">
                Version
              </label>
              <input
                {...register('plan_version')}
                type="text"
                id="plan_version"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="1.0"
              />
            </div>
          </div>

          {/* Scope Description */}
          <div>
            <label htmlFor="scope_description" className="block text-sm font-medium text-gray-700 mb-1">
              Scope Description <span className="text-red-500">*</span>
            </label>
            <textarea
              {...register('scope_description')}
              id="scope_description"
              rows={3}
              className={cn(
                'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                errors.scope_description ? 'border-red-500' : 'border-gray-300'
              )}
              placeholder="Describe the scope of this plan..."
            />
            {errors.scope_description && (
              <p className="text-sm text-red-600 mt-1">{errors.scope_description.message}</p>
            )}
          </div>

          {/* Status */}
          <div>
            <label htmlFor="status" className="block text-sm font-medium text-gray-700 mb-1">
              Status <span className="text-red-500">*</span>
            </label>
            <select
              {...register('status')}
              id="status"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value={PlanStatus.DRAFT}>Draft</option>
              <option value={PlanStatus.REVIEW}>In Review</option>
              <option value={PlanStatus.APPROVED}>Approved</option>
              <option value={PlanStatus.ACTIVE}>Active</option>
              <option value={PlanStatus.ARCHIVED}>Archived</option>
            </select>
          </div>
        </div>
      </div>

      {/* Recovery Objectives */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <Target className="w-5 h-5 text-green-600" />
          Recovery Objectives
        </h3>

        <div className="grid grid-cols-3 gap-4">
          {/* RTO */}
          <div>
            <label htmlFor="rto_target" className="block text-sm font-medium text-gray-700 mb-1">
              RTO (minutes) <span className="text-red-500">*</span>
            </label>
            <input
              {...register('rto_target', { valueAsNumber: true })}
              type="number"
              id="rto_target"
              className={cn(
                'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                errors.rto_target ? 'border-red-500' : 'border-gray-300'
              )}
              placeholder="240"
            />
            {errors.rto_target && (
              <p className="text-sm text-red-600 mt-1">{errors.rto_target.message}</p>
            )}
            <p className="text-xs text-gray-500 mt-1">Recovery Time Objective</p>
          </div>

          {/* RPO */}
          <div>
            <label htmlFor="rpo_target" className="block text-sm font-medium text-gray-700 mb-1">
              RPO (minutes) <span className="text-red-500">*</span>
            </label>
            <input
              {...register('rpo_target', { valueAsNumber: true })}
              type="number"
              id="rpo_target"
              className={cn(
                'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                errors.rpo_target ? 'border-red-500' : 'border-gray-300'
              )}
              placeholder="60"
            />
            {errors.rpo_target && (
              <p className="text-sm text-red-600 mt-1">{errors.rpo_target.message}</p>
            )}
            <p className="text-xs text-gray-500 mt-1">Recovery Point Objective</p>
          </div>

          {/* MTPD */}
          <div>
            <label htmlFor="mtpd_target" className="block text-sm font-medium text-gray-700 mb-1">
              MTPD (minutes) <span className="text-red-500">*</span>
            </label>
            <input
              {...register('mtpd_target', { valueAsNumber: true })}
              type="number"
              id="mtpd_target"
              className={cn(
                'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                errors.mtpd_target ? 'border-red-500' : 'border-gray-300'
              )}
              placeholder="480"
            />
            {errors.mtpd_target && (
              <p className="text-sm text-red-600 mt-1">{errors.mtpd_target.message}</p>
            )}
            <p className="text-xs text-gray-500 mt-1">Max Tolerable Period of Disruption</p>
          </div>
        </div>

        {/* Validation Info */}
        {(rto && mtpd && rpo) && (
          <div className="mt-4 bg-gradient-to-br from-blue-50 to-green-50 rounded-lg p-4 border border-blue-200">
            <p className="text-sm text-gray-700">
              <strong>Validation:</strong> RTO ({rto} min) must be ≤ MTPD ({mtpd} min) and RPO ({rpo} min) should be ≤ RTO
            </p>
          </div>
        )}
      </div>

      {/* Strategy */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Strategy</h3>

        <div className="space-y-4">
          {/* Strategy Type */}
          <div>
            <label htmlFor="strategy_type" className="block text-sm font-medium text-gray-700 mb-1">
              Strategy Type <span className="text-red-500">*</span>
            </label>
            <select
              {...register('strategy_type')}
              id="strategy_type"
              className={cn(
                'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
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

          {/* Strategy Description */}
          <div>
            <label htmlFor="strategy_description" className="block text-sm font-medium text-gray-700 mb-1">
              Strategy Description <span className="text-red-500">*</span>
            </label>
            <textarea
              {...register('strategy_description')}
              id="strategy_description"
              rows={4}
              className={cn(
                'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                errors.strategy_description ? 'border-red-500' : 'border-gray-300'
              )}
              placeholder="Describe the strategy for business continuity..."
            />
            {errors.strategy_description && (
              <p className="text-sm text-red-600 mt-1">{errors.strategy_description.message}</p>
            )}
          </div>

          {/* Estimated Cost */}
          <div>
            <label htmlFor="estimated_cost" className="block text-sm font-medium text-gray-700 mb-1 flex items-center gap-1">
              <DollarSign className="w-4 h-4" />
              Estimated Cost
            </label>
            <input
              {...register('estimated_cost', { valueAsNumber: true })}
              type="number"
              id="estimated_cost"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="50000"
            />
          </div>
        </div>
      </div>

      {/* Resources */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Required Resources</h3>

        <div className="grid grid-cols-4 gap-3 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
            <select
              value={newResource.resource_type}
              onChange={(e) => setNewResource({ ...newResource, resource_type: e.target.value as Resource['resource_type'] })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="personnel">Personnel</option>
              <option value="equipment">Equipment</option>
              <option value="facility">Facility</option>
              <option value="technology">Technology</option>
              <option value="financial">Financial</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
            <input
              type="text"
              value={newResource.resource_name}
              onChange={(e) => setNewResource({ ...newResource, resource_name: e.target.value })}
              placeholder="Resource name..."
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Availability</label>
            <select
              value={newResource.availability}
              onChange={(e) => setNewResource({ ...newResource, availability: e.target.value as Resource['availability'] })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="available">Available</option>
              <option value="limited">Limited</option>
              <option value="unavailable">Unavailable</option>
            </select>
          </div>

          <div className="flex items-end">
            <button
              type="button"
              onClick={handleAddResource}
              className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors inline-flex items-center justify-center gap-2"
            >
              <Plus className="w-4 h-4" />
              Add
            </button>
          </div>
        </div>

        <div className="space-y-2">
          {resources.map((resource, index) => (
            <div key={index} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
              <div className="flex-1 grid grid-cols-3 gap-3">
                <p className="text-sm">
                  <strong className="text-gray-700">{resource.resource_type}:</strong> {resource.resource_name}
                </p>
                <p className="text-sm text-gray-600">
                  Availability: <span className="capitalize">{resource.availability}</span>
                </p>
                <p className="text-sm text-gray-600">
                  {resource.cost_estimate && `Cost: $${resource.cost_estimate}`}
                  {resource.quantity && ` | Qty: ${resource.quantity}`}
                </p>
              </div>
              <button
                type="button"
                onClick={() => handleRemoveResource(index)}
                className="p-1 text-red-600 hover:bg-red-50 rounded transition-colors"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          ))}
        </div>

        {resources.length === 0 && (
          <p className="text-sm text-gray-500 text-center py-4">
            No resources added yet. Add resources required for this plan.
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
          className="px-6 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors inline-flex items-center gap-2 disabled:opacity-50"
        >
          <Save className="w-4 h-4" />
          {isLoading ? 'Saving...' : initialData ? 'Update Plan' : 'Create Plan'}
        </button>
      </div>
    </form>
  );
}
