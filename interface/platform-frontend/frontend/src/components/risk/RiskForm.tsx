'use client';

import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { riskCreateSchema } from '@/lib/validations/risk-validation';
import type { RiskCreate, RiskUpdate, Risk } from '@/types/risk';
import { RiskCategory, RiskLikelihood, RiskImpact, RiskStatus } from '@/types/risk';
import { calculateRiskScore } from '@/types/risk';
import {
  AlertTriangle,
  Save,
  X,
  Plus,
  Trash2,
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface RiskFormProps {
  initialData?: Risk;
  onSubmit: (data: RiskCreate | RiskUpdate) => void;
  onCancel?: () => void;
  isLoading?: boolean;
  className?: string;
}

/**
 * RiskForm - Create or edit risk assessments
 *
 * Features:
 * - Full risk metadata
 * - Real-time risk score calculation
 * - Vulnerabilities array management
 * - Zod validation
 * - Auto-save draft support
 */
export function RiskForm({
  initialData,
  onSubmit,
  onCancel,
  isLoading = false,
  className,
}: RiskFormProps) {
  const [vulnerabilities, setVulnerabilities] = useState<string[]>(
    initialData?.vulnerabilities || []
  );
  const [newVulnerability, setNewVulnerability] = useState('');

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<RiskCreate>({
    resolver: zodResolver(riskCreateSchema),
    defaultValues: initialData ? {
      risk_title: initialData.risk_title,
      risk_code: initialData.risk_code,
      risk_category: initialData.risk_category,
      description: initialData.description,
      threat_source: initialData.threat_source,
      vulnerabilities: initialData.vulnerabilities,
      likelihood: initialData.likelihood,
      impact: initialData.impact,
      treatment_strategy: initialData.treatment_strategy,
      risk_owner_id: initialData.risk_owner_id,
      status: initialData.status,
      related_processes: initialData.related_processes,
      related_assets: initialData.related_assets,
    } : {
      organization_id: 'org-123', // TODO: Get from auth
      vulnerabilities: [],
      likelihood: 3,
      impact: 3,
      status: RiskStatus.IDENTIFIED,
    },
  });

  // Watch likelihood and impact for real-time score calculation
  const likelihood = watch('likelihood');
  const impact = watch('impact');
  const inherentScore = calculateRiskScore(likelihood, impact);

  const handleAddVulnerability = () => {
    if (newVulnerability.trim()) {
      setVulnerabilities([...vulnerabilities, newVulnerability.trim()]);
      setNewVulnerability('');
    }
  };

  const handleRemoveVulnerability = (index: number) => {
    setVulnerabilities(vulnerabilities.filter((_, i) => i !== index));
  };

  const onFormSubmit = (data: RiskCreate) => {
    onSubmit({
      ...data,
      vulnerabilities,
    });
  };

  return (
    <form onSubmit={handleSubmit(onFormSubmit)} className={cn('space-y-6', className)}>
      {/* Basic Information */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Basic Information</h3>

        <div className="space-y-4">
          {/* Risk Title */}
          <div>
            <label htmlFor="risk_title" className="block text-sm font-medium text-gray-700 mb-1">
              Risk Title <span className="text-red-500">*</span>
            </label>
            <input
              {...register('risk_title')}
              type="text"
              id="risk_title"
              className={cn(
                'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500',
                errors.risk_title ? 'border-red-500' : 'border-gray-300'
              )}
              placeholder="e.g., Data Center Power Failure"
            />
            {errors.risk_title && (
              <p className="text-sm text-red-600 mt-1">{errors.risk_title.message}</p>
            )}
          </div>

          {/* Risk Code */}
          <div>
            <label htmlFor="risk_code" className="block text-sm font-medium text-gray-700 mb-1">
              Risk Code (Optional)
            </label>
            <input
              {...register('risk_code')}
              type="text"
              id="risk_code"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
              placeholder="e.g., RISK-2024-001"
            />
          </div>

          {/* Category */}
          <div>
            <label htmlFor="risk_category" className="block text-sm font-medium text-gray-700 mb-1">
              Category <span className="text-red-500">*</span>
            </label>
            <select
              {...register('risk_category')}
              id="risk_category"
              className={cn(
                'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500',
                errors.risk_category ? 'border-red-500' : 'border-gray-300'
              )}
            >
              <option value="">Select category...</option>
              <option value={RiskCategory.OPERATIONAL}>Operational</option>
              <option value={RiskCategory.FINANCIAL}>Financial</option>
              <option value={RiskCategory.STRATEGIC}>Strategic</option>
              <option value={RiskCategory.COMPLIANCE}>Compliance</option>
              <option value={RiskCategory.REPUTATIONAL}>Reputational</option>
              <option value={RiskCategory.CYBERSECURITY}>Cybersecurity</option>
              <option value={RiskCategory.NATURAL_DISASTER}>Natural Disaster</option>
            </select>
            {errors.risk_category && (
              <p className="text-sm text-red-600 mt-1">{errors.risk_category.message}</p>
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
              rows={4}
              className={cn(
                'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500',
                errors.description ? 'border-red-500' : 'border-gray-300'
              )}
              placeholder="Describe the risk in detail..."
            />
            {errors.description && (
              <p className="text-sm text-red-600 mt-1">{errors.description.message}</p>
            )}
          </div>

          {/* Threat Source */}
          <div>
            <label htmlFor="threat_source" className="block text-sm font-medium text-gray-700 mb-1">
              Threat Source (Optional)
            </label>
            <input
              {...register('threat_source')}
              type="text"
              id="threat_source"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
              placeholder="e.g., Natural disaster, Cyberattack, Equipment failure"
            />
          </div>
        </div>
      </div>

      {/* Risk Analysis */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Risk Analysis</h3>

        <div className="grid grid-cols-2 gap-4 mb-6">
          {/* Likelihood */}
          <div>
            <label htmlFor="likelihood" className="block text-sm font-medium text-gray-700 mb-1">
              Likelihood (1-5) <span className="text-red-500">*</span>
            </label>
            <select
              {...register('likelihood', { valueAsNumber: true })}
              id="likelihood"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
            >
              <option value={RiskLikelihood.RARE}>1 - Rare (&lt; 5%)</option>
              <option value={RiskLikelihood.UNLIKELY}>2 - Unlikely (5-20%)</option>
              <option value={RiskLikelihood.POSSIBLE}>3 - Possible (20-50%)</option>
              <option value={RiskLikelihood.LIKELY}>4 - Likely (50-80%)</option>
              <option value={RiskLikelihood.ALMOST_CERTAIN}>5 - Almost Certain (&gt; 80%)</option>
            </select>
          </div>

          {/* Impact */}
          <div>
            <label htmlFor="impact" className="block text-sm font-medium text-gray-700 mb-1">
              Impact (1-5) <span className="text-red-500">*</span>
            </label>
            <select
              {...register('impact', { valueAsNumber: true })}
              id="impact"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
            >
              <option value={RiskImpact.INSIGNIFICANT}>1 - Insignificant</option>
              <option value={RiskImpact.MINOR}>2 - Minor</option>
              <option value={RiskImpact.MODERATE}>3 - Moderate</option>
              <option value={RiskImpact.MAJOR}>4 - Major</option>
              <option value={RiskImpact.CATASTROPHIC}>5 - Catastrophic</option>
            </select>
          </div>
        </div>

        {/* Real-time Score Display */}
        <div className="bg-gradient-to-br from-orange-50 to-red-50 rounded-lg p-4 border border-orange-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Inherent Risk Score</p>
              <p className="text-3xl font-bold text-gray-900">{inherentScore}</p>
              <p className="text-sm text-gray-600">Likelihood ({likelihood}) × Impact ({impact})</p>
            </div>
            <AlertTriangle className="w-12 h-12 text-orange-600" />
          </div>
        </div>
      </div>

      {/* Vulnerabilities */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Vulnerabilities <span className="text-red-500">*</span>
        </h3>

        <div className="flex gap-2 mb-4">
          <input
            type="text"
            value={newVulnerability}
            onChange={(e) => setNewVulnerability(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddVulnerability())}
            placeholder="Add a vulnerability..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
          />
          <button
            type="button"
            onClick={handleAddVulnerability}
            className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors inline-flex items-center gap-2"
          >
            <Plus className="w-4 h-4" />
            Add
          </button>
        </div>

        <div className="space-y-2">
          {vulnerabilities.map((vuln, index) => (
            <div key={index} className="flex items-center gap-2 p-3 bg-gray-50 rounded-lg">
              <p className="flex-1 text-sm text-gray-700">{vuln}</p>
              <button
                type="button"
                onClick={() => handleRemoveVulnerability(index)}
                className="p-1 text-red-600 hover:bg-red-50 rounded transition-colors"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          ))}
        </div>

        {vulnerabilities.length === 0 && (
          <p className="text-sm text-gray-500 text-center py-4">
            No vulnerabilities added yet. At least one is required.
          </p>
        )}
      </div>

      {/* Status */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Status & Ownership</h3>

        <div className="space-y-4">
          {/* Status */}
          <div>
            <label htmlFor="status" className="block text-sm font-medium text-gray-700 mb-1">
              Status <span className="text-red-500">*</span>
            </label>
            <select
              {...register('status')}
              id="status"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
            >
              <option value={RiskStatus.IDENTIFIED}>Identified</option>
              <option value={RiskStatus.ANALYZING}>Analyzing</option>
              <option value={RiskStatus.TREATED}>Treated</option>
              <option value={RiskStatus.MONITORING}>Monitoring</option>
              <option value={RiskStatus.CLOSED}>Closed</option>
            </select>
          </div>

          {/* Risk Owner */}
          <div>
            <label htmlFor="risk_owner_id" className="block text-sm font-medium text-gray-700 mb-1">
              Risk Owner (Optional)
            </label>
            <input
              {...register('risk_owner_id')}
              type="text"
              id="risk_owner_id"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
              placeholder="User ID (UUID format)"
            />
            {errors.risk_owner_id && (
              <p className="text-sm text-red-600 mt-1">{errors.risk_owner_id.message}</p>
            )}
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
          className="px-6 py-2.5 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors inline-flex items-center gap-2 disabled:opacity-50"
        >
          <Save className="w-4 h-4" />
          {isLoading ? 'Saving...' : initialData ? 'Update Risk' : 'Create Risk'}
        </button>
      </div>
    </form>
  );
}
