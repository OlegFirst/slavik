'use client';

/**
 * Risk Assessment Module - Edit Risk Page
 * Form for updating existing risk assessments
 * Week 5 Round 4 - AI Platform ISO Project
 */

import React from 'react';
import { useRouter } from 'next/navigation';
import { useRisk, useUpdateRisk } from '@/hooks/risk';
import { RiskForm } from '@/components/risk';
import type { RiskUpdate } from '@/types/risk';
import { ArrowLeft, AlertTriangle, ChevronRight, Loader2 } from 'lucide-react';

interface PageProps {
  params: {
    id: string;
  };
}

export default function EditRiskPage({ params }: PageProps) {
  const router = useRouter();
  const { data: risk, isLoading } = useRisk({ id: params.id });
  const updateRisk = useUpdateRisk({
    onSuccess: () => {
      router.push(`/risk/${params.id}`);
    },
  });

  const handleSubmit = (data: RiskUpdate) => {
    updateRisk.mutate({ id: params.id, data });
  };

  // Loading State
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-red-50 p-8">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 text-orange-600 animate-spin" />
          </div>
        </div>
      </div>
    );
  }

  // Error State
  if (!risk) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-red-50 p-8">
        <div className="max-w-4xl mx-auto">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
            <AlertTriangle className="w-8 h-8 text-red-600 mx-auto mb-3" />
            <p className="text-red-800 font-medium">Risk not found</p>
            <button
              onClick={() => router.push('/risk')}
              className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
            >
              Back to Risks
            </button>
          </div>
        </div>
      </div>
    );
  }

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
          <button
            onClick={() => router.push(`/risk/${params.id}`)}
            className="hover:text-orange-600 transition-colors truncate max-w-xs"
          >
            {risk.risk_title}
          </button>
          <ChevronRight className="w-4 h-4" />
          <span className="text-gray-900 font-medium">Edit</span>
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
            <div className="flex-1 min-w-0">
              <h1 className="text-3xl font-bold text-gray-900">Edit Risk Assessment</h1>
              <p className="text-gray-600 mt-1 truncate">{risk.risk_title}</p>
            </div>
          </div>
        </div>

        {/* Warning Card */}
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex gap-3">
            <div className="flex-shrink-0">
              <AlertTriangle className="w-5 h-5 text-yellow-600" />
            </div>
            <div className="text-sm text-yellow-800">
              <p className="font-medium mb-1">Important</p>
              <p className="text-yellow-700">
                Changes to risk scores may impact treatment plans and historical trend data.
                Ensure all modifications are properly documented.
              </p>
            </div>
          </div>
        </div>

        {/* Form */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <RiskForm
            initialData={risk}
            onSubmit={handleSubmit}
            onCancel={() => router.back()}
            isLoading={updateRisk.isPending}
          />
        </div>

        {/* Audit Trail Info */}
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-gray-900 mb-2">Audit Information</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm text-gray-600">
            {risk.created_at && (
              <div>
                <span className="font-medium">Created:</span>{' '}
                {new Date(risk.created_at).toLocaleString()}
              </div>
            )}
            {risk.updated_at && (
              <div>
                <span className="font-medium">Last Updated:</span>{' '}
                {new Date(risk.updated_at).toLocaleString()}
              </div>
            )}
            {risk.risk_owner_id && (
              <div>
                <span className="font-medium">Owner:</span> {risk.risk_owner_id}
              </div>
            )}
            {risk.last_reviewed_at && (
              <div>
                <span className="font-medium">Last Reviewed:</span>{' '}
                {new Date(risk.last_reviewed_at).toLocaleString()}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
