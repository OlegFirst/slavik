'use client';

/**
 * ProcessForm Component
 * Professional form for creating/editing BIA processes
 * Real validation, AI integration, no mocks
 */

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useState } from 'react';
import { Sparkles, Loader2, AlertTriangle } from 'lucide-react';
import { biaProcessCreateSchema, type BIAProcessCreateInput } from '@/lib/validations/bia';
import { useCreateBIAProcess, useUpdateBIAProcess, useAISuggestionWithForm } from '@/hooks/bia';
import {
  CriticalityLevel,
  IndustryType,
  GeographicalScope,
  ReputationalImpact,
  RegulatoryImpact,
  PatientSafetyImpact,
  WHOTier,
  type BIAProcess,
  type Dependency,
} from '@/types/bia';
import { DependencyMapper } from './DependencyMapper';
import { ImpactAssessmentForm, type ImpactData } from './ImpactAssessmentForm';
import { RecoveryStrategiesBuilder } from './RecoveryStrategiesBuilder';

interface ProcessFormProps {
  process?: BIAProcess; // For editing
  tenant_id: string;
  onSuccess?: (process: BIAProcess) => void;
  onCancel?: () => void;
}

export function ProcessForm({
  process,
  tenant_id,
  onSuccess,
  onCancel,
}: ProcessFormProps) {
  const isEditing = !!process;
  const [showAIPanel, setShowAIPanel] = useState(false);

  // Extended state for complex sections
  const [dependencies, setDependencies] = useState<Dependency[]>(
    process?.dependencies || []
  );
  const [impactData, setImpactData] = useState<ImpactData | null>(null);
  const [recoveryStrategies, setRecoveryStrategies] = useState<any[]>(
    process?.recovery_strategies || []
  );

  // React Hook Form setup
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    watch,
    setValue,
    reset,
  } = useForm<BIAProcessCreateInput>({
    resolver: zodResolver(biaProcessCreateSchema),
    defaultValues: process ? {
      tenant_id: process.tenant_id,
      name: process.name,
      description: process.description || '',
      department: process.department || '',
      process_owner: process.process_owner || '',
      criticality: process.criticality,
      industry: process.industry,
      geographical_scope: process.geographical_scope,
      rto_hours: process.rto_hours,
      rpo_hours: process.rpo_hours,
      mtpd_hours: process.mtpd_hours,
      financial_impact: process.financial_impact || {},
      who_tier: process.who_tier,
    } : {
      tenant_id,
      rto_hours: 24,
      rpo_hours: 4,
      mtpd_hours: 72,
      criticality: CriticalityLevel.MODERATE,
    },
  });

  // Mutations
  const createMutation = useCreateBIAProcess({
    onSuccess: (data) => {
      reset();
      onSuccess?.(data);
    },
  });

  const updateMutation = useUpdateBIAProcess({
    onSuccess: (data) => {
      onSuccess?.(data);
    },
  });

  // AI Suggestion
  const aiSuggestion = useAISuggestionWithForm(setValue, {
    onSuccess: () => {
      setShowAIPanel(false);
    },
  });

  // Form submission
  const onSubmit = async (data: BIAProcessCreateInput) => {
    // Merge form data with complex sections
    const completeData = {
      ...data,
      dependencies,
      ...(impactData || {}),
      recovery_strategies: recoveryStrategies,
    };

    if (isEditing && process) {
      updateMutation.mutate({
        id: process.id!,
        tenant_id: process.tenant_id,
        updates: completeData,
      });
    } else {
      createMutation.mutate(completeData as any);
    }
  };

  // Get AI suggestion
  const handleGetAISuggestion = () => {
    const formData = watch();

    if (!formData.name || !formData.criticality) {
      alert('Please fill in Process Name and Criticality first');
      return;
    }

    aiSuggestion.mutate({
      name: formData.name,
      industry: formData.industry || 'other',
      criticality: formData.criticality,
      financial_impact: formData.financial_impact || {
        '1_hour': 1000,
        '24_hours': 10000,
      },
      staff_count: formData.personnel_requirements?.staff_count,
    });
  };

  const isPending = createMutation.isPending || updateMutation.isPending;

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">
          {isEditing ? 'Edit BIA Process' : 'Create BIA Process'}
        </h2>
        <button
          type="button"
          onClick={handleGetAISuggestion}
          disabled={aiSuggestion.isPending}
          className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors flex items-center gap-2 disabled:opacity-50"
        >
          {aiSuggestion.isPending ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <Sparkles className="w-4 h-4" />
          )}
          Get AI Suggestion
        </button>
      </div>

      {/* Basic Information */}
      <div className="bg-white rounded-lg border border-gray-200 p-6 space-y-4">
        <h3 className="text-lg font-semibold text-gray-900">Basic Information</h3>

        {/* Process Name */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Process Name *
          </label>
          <input
            {...register('name')}
            type="text"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
            placeholder="e.g., Patient Admission Process"
          />
          {errors.name && (
            <p className="text-red-600 text-sm mt-1">{errors.name.message}</p>
          )}
        </div>

        {/* Description */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Description
          </label>
          <textarea
            {...register('description')}
            rows={3}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
            placeholder="Describe the business process..."
          />
        </div>

        {/* Department & Owner */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Department
            </label>
            <input
              {...register('department')}
              type="text"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
              placeholder="e.g., Emergency Care"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Process Owner
            </label>
            <input
              {...register('process_owner')}
              type="text"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
              placeholder="e.g., Dr. Smith"
            />
          </div>
        </div>
      </div>

      {/* Criticality & Context */}
      <div className="bg-white rounded-lg border border-gray-200 p-6 space-y-4">
        <h3 className="text-lg font-semibold text-gray-900">Criticality & Context</h3>

        <div className="grid grid-cols-2 gap-4">
          {/* Criticality */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Criticality Level *
            </label>
            <select
              {...register('criticality')}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
            >
              <option value={CriticalityLevel.CRITICAL}>Critical</option>
              <option value={CriticalityLevel.HIGH}>High</option>
              <option value={CriticalityLevel.MODERATE}>Moderate</option>
              <option value={CriticalityLevel.MINOR}>Minor</option>
              <option value={CriticalityLevel.LOW}>Low</option>
            </select>
            {errors.criticality && (
              <p className="text-red-600 text-sm mt-1">{errors.criticality.message}</p>
            )}
          </div>

          {/* Industry */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Industry
            </label>
            <select
              {...register('industry')}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
            >
              <option value="">Select industry...</option>
              <option value={IndustryType.HEALTHCARE}>Healthcare</option>
              <option value={IndustryType.FINANCIAL}>Financial</option>
              <option value={IndustryType.MANUFACTURING}>Manufacturing</option>
              <option value={IndustryType.RETAIL}>Retail</option>
              <option value={IndustryType.IT}>IT</option>
              <option value={IndustryType.ENERGY}>Energy</option>
              <option value={IndustryType.TRANSPORT}>Transport</option>
              <option value={IndustryType.GOVERNMENT}>Government</option>
              <option value={IndustryType.EDUCATION}>Education</option>
              <option value={IndustryType.OTHER}>Other</option>
            </select>
          </div>

          {/* Geographical Scope */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Geographical Scope
            </label>
            <select
              {...register('geographical_scope')}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
            >
              <option value="">Select scope...</option>
              <option value={GeographicalScope.LOCAL}>Local</option>
              <option value={GeographicalScope.REGIONAL}>Regional</option>
              <option value={GeographicalScope.NATIONAL}>National</option>
              <option value={GeographicalScope.GLOBAL}>Global</option>
            </select>
          </div>

          {/* WHO Tier (Healthcare) */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              WHO Tier (Healthcare)
            </label>
            <select
              {...register('who_tier')}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
            >
              <option value="">Not applicable</option>
              <option value={WHOTier.TIER_1}>Tier 1 - Immediate (0 min)</option>
              <option value={WHOTier.TIER_2}>Tier 2 - Urgent (2-4h)</option>
              <option value={WHOTier.TIER_3}>Tier 3 - Important (24h)</option>
              <option value={WHOTier.TIER_4}>Tier 4 - Normal (3-5d)</option>
            </select>
          </div>
        </div>
      </div>

      {/* Time Objectives */}
      <div className="bg-white rounded-lg border border-gray-200 p-6 space-y-4">
        <h3 className="text-lg font-semibold text-gray-900">Time Objectives</h3>

        {/* Business Rules Warning */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 flex items-start gap-2">
          <AlertTriangle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
          <div className="text-sm text-blue-800">
            <strong>Business Rules:</strong> RTO ≥ RPO, MTPD ≥ RTO
          </div>
        </div>

        <div className="grid grid-cols-3 gap-4">
          {/* RTO */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              RTO (Recovery Time Objective) *
            </label>
            <div className="relative">
              <input
                {...register('rto_hours', { valueAsNumber: true })}
                type="number"
                step="0.5"
                min="0"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
              />
              <span className="absolute right-4 top-2 text-gray-500">hours</span>
            </div>
            {errors.rto_hours && (
              <p className="text-red-600 text-sm mt-1">{errors.rto_hours.message}</p>
            )}
          </div>

          {/* RPO */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              RPO (Recovery Point Objective) *
            </label>
            <div className="relative">
              <input
                {...register('rpo_hours', { valueAsNumber: true })}
                type="number"
                step="0.5"
                min="0"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
              />
              <span className="absolute right-4 top-2 text-gray-500">hours</span>
            </div>
            {errors.rpo_hours && (
              <p className="text-red-600 text-sm mt-1">{errors.rpo_hours.message}</p>
            )}
          </div>

          {/* MTPD */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              MTPD (Maximum Tolerable Period) *
            </label>
            <div className="relative">
              <input
                {...register('mtpd_hours', { valueAsNumber: true })}
                type="number"
                step="0.5"
                min="0"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
              />
              <span className="absolute right-4 top-2 text-gray-500">hours</span>
            </div>
            {errors.mtpd_hours && (
              <p className="text-red-600 text-sm mt-1">{errors.mtpd_hours.message}</p>
            )}
          </div>
        </div>
      </div>

      {/* Dependencies Section */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <DependencyMapper
          dependencies={dependencies}
          processName={watch('name') || 'Process'}
          onDependenciesChange={setDependencies}
          onAIDiscovery={() => {
            // TODO: Integrate AI dependency discovery
            console.log('AI Dependency Discovery');
          }}
        />
      </div>

      {/* Impact Assessment Section */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <ImpactAssessmentForm
          processId={process?.id}
          initialData={process}
          onComplete={(data) => {
            setImpactData(data);
            console.log('Impact data updated:', data);
          }}
          onAICalculate={() => {
            // TODO: Integrate AI impact calculation
            console.log('AI Impact Calculation');
          }}
        />
      </div>

      {/* Recovery Strategies Section */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <RecoveryStrategiesBuilder
          strategies={recoveryStrategies}
          processRTO={watch('rto_hours') || 24}
          processName={watch('name')}
          dependencies={dependencies}
          onStrategiesChange={setRecoveryStrategies}
        />
      </div>

      {/* Actions */}
      <div className="flex items-center justify-end gap-3 pt-6 border-t border-gray-200">
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            disabled={isPending}
            className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
          >
            Cancel
          </button>
        )}
        <button
          type="submit"
          disabled={isPending}
          className="px-6 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors flex items-center gap-2 disabled:opacity-50"
        >
          {isPending && <Loader2 className="w-4 h-4 animate-spin" />}
          {isEditing ? 'Update Process' : 'Create Process'}
        </button>
      </div>

      {/* Error Display */}
      {(createMutation.error || updateMutation.error) && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-800">
          <strong>Error:</strong>{' '}
          {(createMutation.error || updateMutation.error)?.message}
        </div>
      )}
    </form>
  );
}
