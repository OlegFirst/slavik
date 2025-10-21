'use client';

/**
 * ImpactAssessmentForm Component
 * Comprehensive impact assessment per ISO 22301
 * Financial, operational, reputational, regulatory, patient safety
 * AI-powered impact calculation
 */

import { useState, useEffect } from 'react';
import { DollarSign, AlertTriangle, Scale, Heart, TrendingUp, Sparkles, X, CheckCircle, XCircle, Loader2 } from 'lucide-react';
import {
  ReputationalImpact,
  RegulatoryImpact,
  PatientSafetyImpact,
  type BIAProcess,
} from '@/types/bia';
import { useAIImpactCalculation } from '@/hooks/bia';

interface ImpactAssessmentFormProps {
  processId?: number;
  initialData?: Partial<BIAProcess>;
  onComplete: (impactData: ImpactData) => void;
  onAICalculate?: () => void;
  aiLoading?: boolean;
}

export interface ImpactData {
  financial_impact: Record<string, number>;
  operational_impact: Record<string, string>;
  reputational_impact: ReputationalImpact;
  regulatory_impact: RegulatoryImpact;
  patient_safety_impact?: PatientSafetyImpact;
}

const TIMEFRAMES = [
  { key: '1_hour', label: '1 Hour', hours: 1 },
  { key: '4_hours', label: '4 Hours', hours: 4 },
  { key: '8_hours', label: '8 Hours', hours: 8 },
  { key: '24_hours', label: '24 Hours', hours: 24 },
  { key: '1_week', label: '1 Week', hours: 168 },
  { key: '1_month', label: '1 Month', hours: 720 },
];

export function ImpactAssessmentForm({
  processId,
  initialData,
  onComplete,
  onAICalculate,
  aiLoading = false,
}: ImpactAssessmentFormProps) {
  // AI Modal State
  const [showAIModal, setShowAIModal] = useState(false);
  const [aiResult, setAIResult] = useState<any>(null);

  // Financial Impact
  const [financialImpact, setFinancialImpact] = useState<Record<string, number>>(
    initialData?.financial_impact || {
      '1_hour': 0,
      '4_hours': 0,
      '8_hours': 0,
      '24_hours': 0,
      '1_week': 0,
      '1_month': 0,
    }
  );

  // Operational Impact
  const [operationalImpact, setOperationalImpact] = useState<Record<string, string>>(
    initialData?.operational_impact || {}
  );

  // Reputational Impact
  const [reputationalImpact, setReputationalImpact] = useState<ReputationalImpact>(
    initialData?.reputational_impact || ReputationalImpact.NONE
  );

  // Regulatory Impact
  const [regulatoryImpact, setRegulatoryImpact] = useState<RegulatoryImpact>(
    initialData?.regulatory_impact || RegulatoryImpact.NO_VIOLATIONS
  );

  // Patient Safety Impact (Healthcare)
  const [patientSafetyImpact, setPatientSafetyImpact] = useState<PatientSafetyImpact>(
    initialData?.patient_safety_impact || PatientSafetyImpact.NO_IMPACT
  );

  // Validation
  const [errors, setErrors] = useState<string[]>([]);

  // AI Impact Calculation Hook
  const aiImpactMutation = useAIImpactCalculation({
    onSuccess: (data) => {
      setAIResult(data);
    },
    onError: (error) => {
      console.error('AI Impact Calculation failed:', error);
    },
  });

  // Handle AI Calculate button click
  const handleAICalculate = () => {
    setShowAIModal(true);
    setAIResult(null);

    // Trigger AI calculation with process data
    aiImpactMutation.mutate({
      name: initialData?.name || 'Unknown Process',
      daily_revenue: initialData?.annual_revenue_impact ? initialData.annual_revenue_impact / 365 : undefined,
      customers: initialData?.peak_concurrent_users,
      tenant_id: initialData?.tenant_id,
    });
  };

  // Parse AI response and populate form fields
  const handleApplyAIResults = () => {
    if (!aiResult) return;

    try {
      // Parse the impact curve data
      const impactData = aiResult.critical_timeframes || {};

      // Map AI timeframes to our form timeframes
      const newFinancialImpact: Record<string, number> = {
        '1_hour': impactData['1h'] || impactData['1_hour'] || 0,
        '4_hours': impactData['4h'] || impactData['4_hours'] || 0,
        '8_hours': impactData['8h'] || impactData['8_hours'] || 0,
        '24_hours': impactData['24h'] || impactData['24_hours'] || impactData['1d'] || 0,
        '1_week': impactData['1w'] || impactData['1_week'] || impactData['7d'] || 0,
        '1_month': impactData['1m'] || impactData['1_month'] || impactData['30d'] || 0,
      };

      setFinancialImpact(newFinancialImpact);

      // Parse operational impact from metadata if available
      if (aiResult.metadata?.operational_impact) {
        setOperationalImpact(aiResult.metadata.operational_impact);
      }

      // Parse reputational impact
      if (aiResult.metadata?.reputational_impact) {
        setReputationalImpact(aiResult.metadata.reputational_impact as ReputationalImpact);
      }

      // Parse regulatory impact
      if (aiResult.metadata?.regulatory_impact) {
        setRegulatoryImpact(aiResult.metadata.regulatory_impact as RegulatoryImpact);
      }

      // Parse patient safety impact
      if (aiResult.metadata?.patient_safety_impact) {
        setPatientSafetyImpact(aiResult.metadata.patient_safety_impact as PatientSafetyImpact);
      }

      setShowAIModal(false);

      // Clear any existing errors
      setErrors([]);
    } catch (error) {
      console.error('Error parsing AI results:', error);
      setErrors(['Failed to parse AI results. Please try again or enter values manually.']);
    }
  };

  // Handle ESC key to close modal
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && showAIModal) {
        setShowAIModal(false);
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [showAIModal]);

  const validateFinancialImpact = (): boolean => {
    const newErrors: string[] = [];

    // Check increasing values
    let prevValue = 0;
    for (const timeframe of TIMEFRAMES) {
      const value = financialImpact[timeframe.key] || 0;
      if (value < prevValue) {
        newErrors.push(`Financial impact must increase over time (${timeframe.label} is less than previous)`);
      }
      prevValue = value;
    }

    setErrors(newErrors);
    return newErrors.length === 0;
  };

  const handleSubmit = () => {
    if (!validateFinancialImpact()) {
      return;
    }

    const impactData: ImpactData = {
      financial_impact: financialImpact,
      operational_impact: operationalImpact,
      reputational_impact: reputationalImpact,
      regulatory_impact: regulatoryImpact,
      patient_safety_impact: patientSafetyImpact,
    };

    onComplete(impactData);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Impact Assessment</h3>
          <p className="text-sm text-gray-600">
            Assess the impact of process disruption across multiple dimensions
          </p>
        </div>
        <button
          onClick={handleAICalculate}
          disabled={aiImpactMutation.isPending}
          className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {aiImpactMutation.isPending ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Calculating...
            </>
          ) : (
            <>
              <Sparkles className="w-4 h-4" />
              AI Calculate
            </>
          )}
        </button>
      </div>

      {/* Errors */}
      {errors.length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-start gap-2">
            <AlertTriangle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            <div>
              <strong className="text-red-800">Validation Errors:</strong>
              <ul className="list-disc list-inside text-red-700 text-sm mt-1">
                {errors.map((error, i) => (
                  <li key={i}>{error}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Financial Impact */}
      <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
        <div className="flex items-center gap-2 mb-4">
          <DollarSign className="w-6 h-6 text-green-600" />
          <h4 className="text-lg font-semibold text-gray-900">Financial Impact</h4>
        </div>
        <p className="text-sm text-gray-600 mb-4">
          Estimated financial loss over time (must increase progressively)
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {TIMEFRAMES.map((timeframe) => (
            <div key={timeframe.key}>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {timeframe.label}
              </label>
              <div className="relative">
                <span className="absolute left-3 top-2.5 text-gray-500">$</span>
                <input
                  type="number"
                  min="0"
                  step="100"
                  value={financialImpact[timeframe.key] || ''}
                  onChange={(e) =>
                    setFinancialImpact({
                      ...financialImpact,
                      [timeframe.key]: parseFloat(e.target.value) || 0,
                    })
                  }
                  onBlur={validateFinancialImpact}
                  className="w-full pl-8 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                  placeholder="0"
                />
              </div>
            </div>
          ))}
        </div>

        {/* Financial Impact Chart Preview */}
        <div className="mt-4 p-4 bg-gray-50 rounded-lg">
          <div className="flex items-center gap-2 mb-2">
            <TrendingUp className="w-4 h-4 text-blue-600" />
            <span className="text-sm font-medium text-gray-700">Impact Progression</span>
          </div>
          <div className="flex items-end gap-2 h-24">
            {TIMEFRAMES.map((timeframe) => {
              const value = financialImpact[timeframe.key] || 0;
              const maxValue = Math.max(...Object.values(financialImpact), 1);
              const height = (value / maxValue) * 100;

              return (
                <div key={timeframe.key} className="flex-1 flex flex-col items-center gap-1">
                  <div className="w-full bg-blue-200 rounded-t" style={{ height: `${height}%` }}>
                    <div className="w-full h-full bg-blue-500 rounded-t" />
                  </div>
                  <span className="text-xs text-gray-600 text-center">{timeframe.label}</span>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Operational Impact */}
      <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
        <h4 className="text-lg font-semibold text-gray-900 mb-4">Operational Impact</h4>
        <div className="space-y-3">
          {['Service Delivery', 'Customer Satisfaction', 'Staff Productivity', 'Quality'].map((aspect) => (
            <div key={aspect}>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {aspect}
              </label>
              <textarea
                value={operationalImpact[aspect] || ''}
                onChange={(e) =>
                  setOperationalImpact({
                    ...operationalImpact,
                    [aspect]: e.target.value,
                  })
                }
                rows={2}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                placeholder={`Describe impact on ${aspect.toLowerCase()}...`}
              />
            </div>
          ))}
        </div>
      </div>

      {/* Reputational Impact */}
      <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
        <div className="flex items-center gap-2 mb-4">
          <AlertTriangle className="w-6 h-6 text-yellow-600" />
          <h4 className="text-lg font-semibold text-gray-900">Reputational Impact</h4>
        </div>
        <select
          value={reputationalImpact}
          onChange={(e) => setReputationalImpact(e.target.value as ReputationalImpact)}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
        >
          <option value={ReputationalImpact.NONE}>None - No reputational damage</option>
          <option value={ReputationalImpact.MINOR}>Minor - Minimal media attention</option>
          <option value={ReputationalImpact.MODERATE}>Moderate - Local media coverage</option>
          <option value={ReputationalImpact.MAJOR}>Major - National media coverage</option>
          <option value={ReputationalImpact.CATASTROPHIC}>Catastrophic - International impact</option>
        </select>
      </div>

      {/* Regulatory Impact */}
      <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
        <div className="flex items-center gap-2 mb-4">
          <Scale className="w-6 h-6 text-blue-600" />
          <h4 className="text-lg font-semibold text-gray-900">Regulatory Impact</h4>
        </div>
        <select
          value={regulatoryImpact}
          onChange={(e) => setRegulatoryImpact(e.target.value as RegulatoryImpact)}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
        >
          <option value={RegulatoryImpact.NO_VIOLATIONS}>No Violations</option>
          <option value={RegulatoryImpact.MINOR_VIOLATIONS}>Minor Violations - Warnings possible</option>
          <option value={RegulatoryImpact.MAJOR_VIOLATIONS}>Major Violations - Fines likely</option>
          <option value={RegulatoryImpact.LICENSE_AT_RISK}>License at Risk - Suspension possible</option>
          <option value={RegulatoryImpact.CRIMINAL_LIABILITY}>Criminal Liability - Legal action certain</option>
        </select>
      </div>

      {/* Patient Safety Impact (Healthcare) */}
      <div className="bg-white rounded-xl border-2 border-red-200 p-6">
        <div className="flex items-center gap-2 mb-4">
          <Heart className="w-6 h-6 text-red-600" />
          <h4 className="text-lg font-semibold text-gray-900">Patient Safety Impact (Healthcare)</h4>
        </div>
        <p className="text-sm text-gray-600 mb-3">
          Leave as "No Impact" if not applicable to healthcare
        </p>
        <select
          value={patientSafetyImpact}
          onChange={(e) => setPatientSafetyImpact(e.target.value as PatientSafetyImpact)}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
        >
          <option value={PatientSafetyImpact.NO_IMPACT}>No Impact - Not applicable</option>
          <option value={PatientSafetyImpact.DELAYED_CARE}>Delayed Care - Minor delays</option>
          <option value={PatientSafetyImpact.COMPROMISED_QUALITY}>Compromised Quality - Reduced care quality</option>
          <option value={PatientSafetyImpact.PATIENT_HARM_PROBABLE}>Patient Harm Probable - Serious risk</option>
          <option value={PatientSafetyImpact.LIFE_THREATENING}>Life Threatening - Critical risk</option>
        </select>

        {patientSafetyImpact !== PatientSafetyImpact.NO_IMPACT && (
          <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-800 text-sm font-medium">
              ️ Patient safety impact detected. This process requires:
            </p>
            <ul className="list-disc list-inside text-red-700 text-sm mt-2">
              <li>Immediate escalation to clinical leadership</li>
              <li>Enhanced monitoring and validation</li>
              <li>Documented mitigation strategies</li>
              <li>Regular safety audits</li>
            </ul>
          </div>
        )}
      </div>

      {/* Submit */}
      <div className="flex items-center justify-end gap-3 pt-6 border-t border-gray-200">
        <button
          onClick={handleSubmit}
          className="px-6 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors"
        >
          Save Impact Assessment
        </button>
      </div>

      {/* AI Impact Calculation Modal */}
      {showAIModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          {/* Backdrop */}
          <div
            className="absolute inset-0 bg-black bg-opacity-50 transition-opacity"
            onClick={() => !aiImpactMutation.isPending && setShowAIModal(false)}
          />

          {/* Modal */}
          <div className="relative bg-white rounded-xl shadow-2xl max-w-3xl w-full max-h-[90vh] overflow-hidden flex flex-col animate-in fade-in slide-in-from-bottom-4 duration-300">
            {/* Header */}
            <div className="flex items-center justify-between p-6 border-b border-gray-200 bg-gradient-to-r from-purple-50 to-pink-50">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-purple-600 rounded-lg">
                  <Sparkles className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">AI Impact Analysis</h2>
                  <p className="text-sm text-gray-600">Powered by BIA Specialist AI</p>
                </div>
              </div>
              {!aiImpactMutation.isPending && (
                <button
                  onClick={() => setShowAIModal(false)}
                  className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  <X className="w-6 h-6" />
                </button>
              )}
            </div>

            {/* Content */}
            <div className="flex-1 overflow-y-auto p-6">
              {/* Loading State */}
              {aiImpactMutation.isPending && (
                <div className="flex flex-col items-center justify-center py-12">
                  <Loader2 className="w-16 h-16 text-purple-600 animate-spin mb-4" />
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">Analyzing Impact...</h3>
                  <p className="text-gray-600 text-center max-w-md">
                    Our AI is analyzing your process and calculating potential impact across multiple timeframes.
                    This may take a few moments.
                  </p>
                </div>
              )}

              {/* Error State */}
              {aiImpactMutation.isError && (
                <div className="flex flex-col items-center justify-center py-12">
                  <div className="p-4 bg-red-100 rounded-full mb-4">
                    <XCircle className="w-12 h-12 text-red-600" />
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">Analysis Failed</h3>
                  <p className="text-gray-600 text-center max-w-md mb-6">
                    {aiImpactMutation.error?.message || 'Unable to calculate impact. Please try again or enter values manually.'}
                  </p>
                  <div className="flex gap-3">
                    <button
                      onClick={handleAICalculate}
                      className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
                    >
                      Retry
                    </button>
                    <button
                      onClick={() => setShowAIModal(false)}
                      className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
                    >
                      Close
                    </button>
                  </div>
                </div>
              )}

              {/* Success State */}
              {aiImpactMutation.isSuccess && aiResult && (
                <div className="space-y-6">
                  {/* Confidence Score */}
                  <div className="bg-gradient-to-r from-green-50 to-emerald-50 border-2 border-green-200 rounded-xl p-6">
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center gap-2">
                        <CheckCircle className="w-6 h-6 text-green-600" />
                        <h3 className="text-lg font-semibold text-gray-900">Analysis Complete</h3>
                      </div>
                      <div className="text-right">
                        <div className="text-3xl font-bold text-green-600">
                          {Math.round((aiResult.confidence || 0) * 100)}%
                        </div>
                        <div className="text-sm text-gray-600">Confidence</div>
                      </div>
                    </div>
                    <p className="text-gray-700">
                      AI has analyzed your process and calculated impact projections with high confidence.
                    </p>
                  </div>

                  {/* Impact Curve Visualization */}
                  {aiResult.impact_curve && (
                    <div className="bg-gray-50 rounded-xl p-6">
                      <h4 className="text-md font-semibold text-gray-900 mb-3 flex items-center gap-2">
                        <TrendingUp className="w-5 h-5 text-blue-600" />
                        Impact Curve Analysis
                      </h4>
                      <div className="bg-white rounded-lg p-4 border border-gray-200">
                        <pre className="text-sm text-gray-700 whitespace-pre-wrap font-mono">
                          {aiResult.impact_curve}
                        </pre>
                      </div>
                    </div>
                  )}

                  {/* Critical Timeframes */}
                  {aiResult.critical_timeframes && (
                    <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
                      <h4 className="text-md font-semibold text-gray-900 mb-4 flex items-center gap-2">
                        <DollarSign className="w-5 h-5 text-green-600" />
                        Financial Impact Over Time
                      </h4>
                      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                        {Object.entries(aiResult.critical_timeframes).map(([timeframe, value]) => (
                          <div key={timeframe} className="bg-gray-50 rounded-lg p-4">
                            <div className="text-sm text-gray-600 mb-1">{timeframe}</div>
                            <div className="text-2xl font-bold text-gray-900">
                              ${typeof value === 'number' ? value.toLocaleString() : String(value)}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Additional Metadata */}
                  {aiResult.metadata && (
                    <div className="bg-blue-50 rounded-xl p-6 border border-blue-200">
                      <h4 className="text-md font-semibold text-gray-900 mb-3">Additional Insights</h4>
                      <div className="space-y-2 text-sm">
                        {aiResult.metadata.reputational_impact && (
                          <div className="flex items-start gap-2">
                            <AlertTriangle className="w-4 h-4 text-yellow-600 mt-0.5 flex-shrink-0" />
                            <div>
                              <span className="font-medium">Reputational Impact:</span>{' '}
                              <span className="text-gray-700">{aiResult.metadata.reputational_impact}</span>
                            </div>
                          </div>
                        )}
                        {aiResult.metadata.regulatory_impact && (
                          <div className="flex items-start gap-2">
                            <Scale className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" />
                            <div>
                              <span className="font-medium">Regulatory Impact:</span>{' '}
                              <span className="text-gray-700">{aiResult.metadata.regulatory_impact}</span>
                            </div>
                          </div>
                        )}
                        {aiResult.metadata.patient_safety_impact && (
                          <div className="flex items-start gap-2">
                            <Heart className="w-4 h-4 text-red-600 mt-0.5 flex-shrink-0" />
                            <div>
                              <span className="font-medium">Patient Safety:</span>{' '}
                              <span className="text-gray-700">{aiResult.metadata.patient_safety_impact}</span>
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Actions */}
                  <div className="flex items-center justify-end gap-3 pt-4 border-t border-gray-200">
                    <button
                      onClick={() => setShowAIModal(false)}
                      className="px-6 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={handleApplyAIResults}
                      className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors flex items-center gap-2"
                    >
                      <CheckCircle className="w-5 h-5" />
                      Apply to Form
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* TODO: Add impact over time chart (recharts) */}
      {/* TODO: Add industry benchmarking */}
    </div>
  );
}
