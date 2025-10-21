/**
 * FAIRAnalysisCard Component
 * Factor Analysis of Information Risk (FAIR) - Quantitative Risk Analysis
 * Displays ALE, risk rating, confidence intervals, and analysis parameters
 * Real API integration via useFAIRAnalysis and usePerformFAIR hooks
 * Week 5 - Risk Assessment Module - Round 3
 */

'use client';

import React, { useState } from 'react';
import { useFAIRAnalysis, usePerformFAIR } from '@/hooks/risk';
import type { FAIRAnalysisCreate } from '@/types/risk';
import { formatCurrency } from '@/types/risk';
import {
  DollarSign,
  TrendingUp,
  AlertCircle,
  Calculator,
  BarChart3,
  Info,
  Activity,
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface FAIRAnalysisCardProps {
  riskId: string;
  className?: string;
}

/**
 * FAIRAnalysisCard - Factor Analysis of Information Risk
 *
 * Features:
 * - Display Annual Loss Expectancy (ALE)
 * - Risk rating visualization (low/medium/high/critical)
 * - 95% confidence intervals
 * - Interactive analysis form with validation
 * - Real-time calculation
 * - Loading and error states
 *
 * FAIR Methodology:
 * - Loss Event Frequency = Threat Event Frequency × Vulnerability
 * - ALE = Loss Event Frequency × Loss Magnitude (triangular distribution)
 * - Risk Rating based on ALE thresholds
 */
export function FAIRAnalysisCard({ riskId, className }: FAIRAnalysisCardProps) {
  const [showForm, setShowForm] = useState(false);
  const { data: fairAnalysis, isLoading } = useFAIRAnalysis({ riskId });
  const performFAIR = usePerformFAIR(riskId, {
    onSuccess: () => setShowForm(false),
  });

  const [formData, setFormData] = useState<FAIRAnalysisCreate>({
    threat_event_frequency: 12,
    vulnerability_score: 0.5,
    primary_loss_min: 10000,
    primary_loss_max: 100000,
    primary_loss_most_likely: 50000,
    secondary_loss_min: 0,
    secondary_loss_max: 0,
  });

  const handleRunAnalysis = () => {
    // Validation
    if (formData.threat_event_frequency <= 0) {
      return;
    }
    if (formData.vulnerability_score < 0 || formData.vulnerability_score > 1) {
      return;
    }
    if (formData.primary_loss_min > formData.primary_loss_most_likely ||
        formData.primary_loss_most_likely > formData.primary_loss_max) {
      return;
    }

    performFAIR.mutate(formData);
  };

  if (isLoading) {
    return (
      <div className={cn('bg-white rounded-xl shadow-lg p-6', className)}>
        <div className="animate-pulse space-y-4">
          <div className="h-6 bg-gray-200 rounded w-48" />
          <div className="h-24 bg-gray-200 rounded" />
          <div className="h-16 bg-gray-200 rounded" />
        </div>
      </div>
    );
  }

  const getRatingColor = (rating: string) => {
    switch (rating) {
      case 'critical': return 'bg-red-100 text-red-800 border-red-300';
      case 'high': return 'bg-orange-100 text-orange-800 border-orange-300';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'low': return 'bg-green-100 text-green-800 border-green-300';
      default: return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  return (
    <div className={cn('bg-white rounded-xl shadow-lg', className)}>
      {/* Header */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-orange-100 rounded-lg">
              <Calculator className="w-6 h-6 text-orange-600" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">FAIR Analysis</h3>
              <p className="text-sm text-gray-600">Factor Analysis of Information Risk</p>
            </div>
          </div>

          <button
            onClick={() => setShowForm(!showForm)}
            className={cn(
              'px-4 py-2 rounded-lg transition-colors text-sm font-medium',
              showForm
                ? 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                : 'bg-orange-600 text-white hover:bg-orange-700'
            )}
          >
            {showForm ? 'Cancel' : 'Run Analysis'}
          </button>
        </div>
      </div>

      {/* Analysis Form */}
      {showForm && (
        <div className="p-6 bg-gray-50 border-b border-gray-200">
          <div className="flex items-start gap-2 mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
            <Info className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" />
            <div className="text-xs text-blue-900">
              <p className="font-medium mb-1">FAIR Methodology</p>
              <p>Loss Event Frequency = TEF × Vulnerability</p>
              <p>ALE = LEF × Loss Magnitude (triangular distribution)</p>
            </div>
          </div>

          <h4 className="text-sm font-semibold text-gray-900 mb-4">Analysis Parameters</h4>

          <div className="grid grid-cols-2 gap-4">
            {/* Threat Event Frequency */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Threat Event Frequency (per year)
              </label>
              <input
                type="number"
                min="0"
                step="1"
                value={formData.threat_event_frequency}
                onChange={(e) => setFormData({ ...formData, threat_event_frequency: parseFloat(e.target.value) || 0 })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                placeholder="12"
              />
              <p className="text-xs text-gray-500 mt-1">Expected threat occurrences per year</p>
            </div>

            {/* Vulnerability Score */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Vulnerability Score (0-1)
              </label>
              <input
                type="number"
                step="0.1"
                min="0"
                max="1"
                value={formData.vulnerability_score}
                onChange={(e) => setFormData({ ...formData, vulnerability_score: parseFloat(e.target.value) || 0 })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                placeholder="0.5"
              />
              <p className="text-xs text-gray-500 mt-1">Probability threat succeeds (0 = impossible, 1 = certain)</p>
            </div>

            {/* Primary Loss - Minimum */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Primary Loss - Minimum ($)
              </label>
              <input
                type="number"
                min="0"
                step="1000"
                value={formData.primary_loss_min}
                onChange={(e) => setFormData({ ...formData, primary_loss_min: parseFloat(e.target.value) || 0 })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                placeholder="10000"
              />
              <p className="text-xs text-gray-500 mt-1">Best-case loss scenario</p>
            </div>

            {/* Primary Loss - Most Likely */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Primary Loss - Most Likely ($)
              </label>
              <input
                type="number"
                min="0"
                step="1000"
                value={formData.primary_loss_most_likely}
                onChange={(e) => setFormData({ ...formData, primary_loss_most_likely: parseFloat(e.target.value) || 0 })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                placeholder="50000"
              />
              <p className="text-xs text-gray-500 mt-1">Expected loss scenario</p>
            </div>

            {/* Primary Loss - Maximum */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Primary Loss - Maximum ($)
              </label>
              <input
                type="number"
                min="0"
                step="1000"
                value={formData.primary_loss_max}
                onChange={(e) => setFormData({ ...formData, primary_loss_max: parseFloat(e.target.value) || 0 })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                placeholder="100000"
              />
              <p className="text-xs text-gray-500 mt-1">Worst-case loss scenario</p>
            </div>

            {/* Secondary Loss - Optional */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Secondary Loss Range ($ - optional)
              </label>
              <div className="flex gap-2">
                <input
                  type="number"
                  min="0"
                  step="1000"
                  value={formData.secondary_loss_min || 0}
                  onChange={(e) => setFormData({ ...formData, secondary_loss_min: parseFloat(e.target.value) || 0 })}
                  className="w-1/2 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                  placeholder="Min"
                />
                <input
                  type="number"
                  min="0"
                  step="1000"
                  value={formData.secondary_loss_max || 0}
                  onChange={(e) => setFormData({ ...formData, secondary_loss_max: parseFloat(e.target.value) || 0 })}
                  className="w-1/2 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                  placeholder="Max"
                />
              </div>
              <p className="text-xs text-gray-500 mt-1">Indirect costs (reputational, legal, etc.)</p>
            </div>
          </div>

          <button
            onClick={handleRunAnalysis}
            disabled={performFAIR.isPending}
            className="mt-6 w-full px-4 py-3 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-medium"
          >
            {performFAIR.isPending ? (
              <span className="flex items-center justify-center gap-2">
                <Activity className="w-4 h-4 animate-spin" />
                Analyzing...
              </span>
            ) : (
              'Run FAIR Analysis'
            )}
          </button>
        </div>
      )}

      {/* Results */}
      {fairAnalysis && (
        <div className="p-6">
          {/* Annual Loss Expectancy */}
          <div className="mb-6 p-6 bg-gradient-to-r from-orange-50 to-red-50 border border-orange-200 rounded-xl">
            <div className="flex items-center justify-between mb-2">
              <p className="text-sm font-medium text-gray-700">Annual Loss Expectancy (ALE)</p>
              <DollarSign className="w-5 h-5 text-orange-600" />
            </div>
            <p className="text-4xl font-bold text-gray-900 mb-1">
              {formatCurrency(fairAnalysis.annual_loss_expectancy)}
            </p>
            <p className="text-xs text-gray-600">
              Expected annual financial impact from this risk
            </p>
          </div>

          {/* Grid: Risk Rating & Loss Event Frequency */}
          <div className="grid grid-cols-2 gap-4 mb-6">
            {/* Risk Rating */}
            <div>
              <p className="text-sm font-medium text-gray-700 mb-2">Risk Rating</p>
              <span className={cn(
                'inline-flex px-4 py-2 rounded-lg border text-base font-semibold uppercase',
                getRatingColor(fairAnalysis.risk_rating)
              )}>
                {fairAnalysis.risk_rating}
              </span>
            </div>

            {/* Loss Event Frequency */}
            <div className="p-4 bg-purple-50 border border-purple-200 rounded-lg">
              <p className="text-xs text-purple-700 mb-1">Loss Event Frequency</p>
              <p className="text-2xl font-bold text-purple-900">
                {fairAnalysis.loss_event_frequency.toFixed(2)}
              </p>
              <p className="text-xs text-purple-600 mt-1">events/year</p>
            </div>
          </div>

          {/* Confidence Interval */}
          <div className="p-5 bg-blue-50 border border-blue-200 rounded-lg mb-6">
            <div className="flex items-center gap-2 mb-3">
              <TrendingUp className="w-5 h-5 text-blue-600" />
              <p className="text-sm font-semibold text-blue-900">95% Confidence Interval</p>
            </div>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-blue-700 mb-1">Low (P5)</p>
                <p className="text-lg font-bold text-blue-900">
                  {formatCurrency(fairAnalysis.confidence_interval_low)}
                </p>
              </div>
              <div className="flex-1 mx-6 h-2 bg-blue-200 rounded-full relative">
                <div className="absolute inset-0 bg-gradient-to-r from-blue-400 to-blue-600 rounded-full" />
              </div>
              <div className="text-right">
                <p className="text-xs text-blue-700 mb-1">High (P95)</p>
                <p className="text-lg font-bold text-blue-900">
                  {formatCurrency(fairAnalysis.confidence_interval_high)}
                </p>
              </div>
            </div>
            <p className="text-xs text-blue-700 mt-3">
              95% of loss events will fall within this range
            </p>
          </div>

          {/* Input Parameters Summary */}
          <div className="p-4 bg-gray-50 border border-gray-200 rounded-lg">
            <p className="text-xs font-semibold text-gray-700 mb-3">Analysis Parameters</p>
            <div className="grid grid-cols-2 gap-3 text-xs">
              <div className="flex justify-between">
                <span className="text-gray-600">Threat Events/Year:</span>
                <span className="font-medium text-gray-900">{fairAnalysis.threat_event_frequency}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Vulnerability:</span>
                <span className="font-medium text-gray-900">{(fairAnalysis.vulnerability_score * 100).toFixed(0)}%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Primary Loss Range:</span>
                <span className="font-medium text-gray-900">
                  {formatCurrency(fairAnalysis.primary_loss_min)} - {formatCurrency(fairAnalysis.primary_loss_max)}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Most Likely Loss:</span>
                <span className="font-medium text-gray-900">{formatCurrency(fairAnalysis.primary_loss_most_likely)}</span>
              </div>
            </div>
          </div>

          {/* Analysis Metadata */}
          {fairAnalysis.analyzed_at && (
            <div className="mt-4 pt-4 border-t border-gray-200">
              <p className="text-xs text-gray-500">
                Analyzed: {new Date(fairAnalysis.analyzed_at).toLocaleString()}
                {fairAnalysis.analyzed_by && ` by ${fairAnalysis.analyzed_by}`}
              </p>
            </div>
          )}
        </div>
      )}

      {/* No Results State */}
      {!fairAnalysis && !showForm && (
        <div className="p-12 text-center">
          <div className="p-4 bg-gray-100 rounded-full w-20 h-20 mx-auto mb-4 flex items-center justify-center">
            <BarChart3 className="w-10 h-10 text-gray-400" />
          </div>
          <p className="text-gray-900 font-medium mb-1">No FAIR Analysis Available</p>
          <p className="text-sm text-gray-600 mb-4">
            Run a quantitative risk analysis to calculate Annual Loss Expectancy
          </p>
          <button
            onClick={() => setShowForm(true)}
            className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors text-sm font-medium"
          >
            Get Started
          </button>
        </div>
      )}
    </div>
  );
}
