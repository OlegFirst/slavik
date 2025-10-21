'use client';

/**
 * Risk Assessment Module - Create New Risk Page
 * Form for creating new risk assessments with validation
 * Week 5 Round 4 - AI Platform ISO Project
 */

import React from 'react';
import { useRouter } from 'next/navigation';
import { useCreateRisk } from '@/hooks/risk';
import { RiskForm } from '@/components/risk';
import type { RiskCreate } from '@/types/risk';
import { ArrowLeft, AlertTriangle, ChevronRight } from 'lucide-react';

export default function NewRiskPage() {
  const router = useRouter();
  const createRisk = useCreateRisk({
    onSuccess: (risk) => {
      router.push(`/risk/${risk.id}`);
    },
  });

  // TODO: Get from auth context
  const organizationId = 'org-123';

  const handleSubmit = (data: RiskCreate | import('@/types/risk').RiskUpdate) => {
    // Convert to RiskCreate and ensure organization_id is set
    const riskData: RiskCreate = {
      organization_id: organizationId,
      risk_title: ('risk_title' in data ? data.risk_title : '') || '',
      risk_category: ('risk_category' in data ? data.risk_category : 'operational' as any) || 'operational' as any,
      description: ('description' in data ? data.description : '') || '',
      vulnerabilities: data.vulnerabilities || [],
      likelihood: data.likelihood || 3,
      impact: data.impact || 3,
      ...data,
    };
    createRisk.mutate(riskData);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-red-50">
      <div className="max-w-4xl mx-auto p-8 space-y-6">
        {/* Breadcrumbs */}
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <button
            onClick={() => router.push('/')}
            className="hover:text-orange-600 transition-colors"
          >
            Home
          </button>
          <ChevronRight className="w-4 h-4" />
          <button
            onClick={() => router.push('/risk')}
            className="hover:text-orange-600 transition-colors"
          >
            Risk Assessment
          </button>
          <ChevronRight className="w-4 h-4" />
          <span className="text-gray-900 font-medium">New Risk</span>
        </div>

        {/* Header */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex items-center gap-4">
            <button
              onClick={() => router.back()}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              aria-label="Go back"
            >
              <ArrowLeft className="w-5 h-5 text-gray-600" />
            </button>
            <div className="p-3 bg-orange-100 rounded-xl">
              <AlertTriangle className="w-8 h-8 text-orange-600" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Create Risk Assessment</h1>
              <p className="text-gray-600 mt-1">
                Identify and analyze a new organizational risk
              </p>
            </div>
          </div>
        </div>

        {/* Info Card */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex gap-3">
            <div className="flex-shrink-0">
              <div className="w-5 h-5 bg-blue-500 rounded-full flex items-center justify-center">
                <span className="text-white text-xs font-bold">i</span>
              </div>
            </div>
            <div className="text-sm text-blue-800">
              <p className="font-medium mb-1">Risk Assessment Guidelines</p>
              <ul className="list-disc list-inside space-y-1 text-blue-700">
                <li>Use the 1-5 scale for likelihood and impact assessment</li>
                <li>Inherent risk score is automatically calculated (Likelihood × Impact)</li>
                <li>Provide clear, actionable descriptions of vulnerabilities</li>
                <li>Treatment plans can be added after initial risk creation</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Form */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <RiskForm
            onSubmit={handleSubmit}
            onCancel={() => router.back()}
            isLoading={createRisk.isPending}
          />
        </div>

        {/* Help Text */}
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-gray-900 mb-2">Need Help?</h3>
          <p className="text-sm text-gray-600">
            Risk assessments follow ISO 22301:2019 Clause 8.2.3 guidelines. For more
            information on risk categories and scoring methodologies, refer to the{' '}
            <button className="text-orange-600 hover:text-orange-700 font-medium">
              Risk Management Guide
            </button>
            .
          </p>
        </div>
      </div>
    </div>
  );
}
