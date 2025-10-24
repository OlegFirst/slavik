'use client';

/**
 * Planning Module - Edit BC Plan Page
 * Form for updating existing business continuity plans
 * Week 5 Round 4 - AI Platform ISO Project (Agent 13)
 */

import React from 'react';
import { useRouter } from 'next/navigation';
import { usePlan, useUpdatePlan } from '@/hooks/planning';
import { PlanForm } from '@/components/planning';
import type { BCPlanUpdate } from '@/lib/api/planning-client';
import { ArrowLeft, FileText, ChevronRight, Loader2, AlertTriangle } from 'lucide-react';

interface PageProps {
  params: {
    id: string;
  };
}

export default function EditPlanPage({ params }: PageProps) {
  const router = useRouter();
  const { data: plan, isLoading } = usePlan({ planId: params.id });
  const updatePlan = useUpdatePlan({
    onSuccess: () => {
      router.push(`/planning/${params.id}`);
    },
  });

  const handleSubmit = (data: any) => {
    updatePlan.mutate({ planId: params.id, data: data as any });
  };

  // Loading State
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 p-8">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
          </div>
        </div>
      </div>
    );
  }

  // Error State
  if (!plan) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 p-8">
        <div className="max-w-4xl mx-auto">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
            <AlertTriangle className="w-8 h-8 text-red-600 mx-auto mb-3" />
            <p className="text-red-800 font-medium">Plan not found</p>
            <button
              onClick={() => router.push('/planning')}
              className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
            >
              Back to Plans
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      <div className="max-w-4xl mx-auto p-8 space-y-6">
        {/* Breadcrumbs */}
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <button
            onClick={() => router.push('/')}
            className="hover:text-blue-600 transition-colors"
          >
            Home
          </button>
          <ChevronRight className="w-4 h-4" />
          <button
            onClick={() => router.push('/planning')}
            className="hover:text-blue-600 transition-colors"
          >
            Business Continuity Planning
          </button>
          <ChevronRight className="w-4 h-4" />
          <button
            onClick={() => router.push(`/planning/${params.id}`)}
            className="hover:text-blue-600 transition-colors truncate max-w-xs"
          >
            {plan.plan_name}
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
            <div className="p-3 bg-blue-100 rounded-xl">
              <FileText className="w-8 h-8 text-blue-600" />
            </div>
            <div className="flex-1 min-w-0">
              <h1 className="text-3xl font-bold text-gray-900">Edit BC Plan</h1>
              <p className="text-gray-600 mt-1 truncate">{plan.plan_name}</p>
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
                Changes to recovery objectives or plan scope may impact associated strategies and
                action plans. Ensure all modifications are properly reviewed and documented before
                activating the updated plan.
              </p>
            </div>
          </div>
        </div>

        {/* Form */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <PlanForm
            initialData={plan as any}
            onSubmit={handleSubmit}
            onCancel={() => router.back()}
            isLoading={updatePlan.isPending}
          />
        </div>

        {/* Audit Trail Info */}
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-gray-900 mb-2">Audit Information</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm text-gray-600">
            {plan.created_at && (
              <div>
                <span className="font-medium">Created:</span>{' '}
                {new Date(plan.created_at).toLocaleString()}
              </div>
            )}
            {plan.updated_at && (
              <div>
                <span className="font-medium">Last Updated:</span>{' '}
                {new Date(plan.updated_at).toLocaleString()}
              </div>
            )}
            {plan.owner_id && (
              <div>
                <span className="font-medium">Owner:</span> {plan.owner_id}
              </div>
            )}
            {plan.approved_by && (
              <div>
                <span className="font-medium">Approved By:</span> {plan.approved_by}
              </div>
            )}
            {plan.approval_date && (
              <div>
                <span className="font-medium">Approved On:</span>{' '}
                {new Date(plan.approval_date).toLocaleString()}
              </div>
            )}
            {plan.review_date && (
              <div>
                <span className="font-medium">Next Review:</span>{' '}
                {new Date(plan.review_date).toLocaleString()}
              </div>
            )}
          </div>
        </div>

        {/* Version Information */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex gap-3">
            <div className="flex-shrink-0">
              <div className="w-5 h-5 bg-blue-500 rounded-full flex items-center justify-center">
                <span className="text-white text-xs font-bold">v</span>
              </div>
            </div>
            <div className="text-sm text-blue-800">
              <p className="font-medium mb-1">Version Control</p>
              <p className="text-blue-700">
                Current version: <span className="font-semibold">{plan.version}</span>. Major
                changes to plan objectives or scope should be reflected in a new version number.
                Version history is maintained for audit and compliance purposes.
              </p>
            </div>
          </div>
        </div>

        {/* ISO Guidelines */}
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-gray-900 mb-3">ISO 22301:2019 Update Guidelines</h3>
          <div className="space-y-2 text-sm text-gray-600">
            <div className="flex items-start gap-2">
              <span className="text-blue-600 font-bold">•</span>
              <span>
                Review and update plans at planned intervals or when significant changes occur
              </span>
            </div>
            <div className="flex items-start gap-2">
              <span className="text-blue-600 font-bold">•</span>
              <span>
                Ensure updated plans remain aligned with business impact analysis and risk
                assessment results
              </span>
            </div>
            <div className="flex items-start gap-2">
              <span className="text-blue-600 font-bold">•</span>
              <span>
                Document the rationale for significant changes to recovery strategies or objectives
              </span>
            </div>
            <div className="flex items-start gap-2">
              <span className="text-blue-600 font-bold">•</span>
              <span>
                Communicate plan updates to all relevant stakeholders and ensure training is
                provided
              </span>
            </div>
            <div className="flex items-start gap-2">
              <span className="text-blue-600 font-bold">•</span>
              <span>Retain previous versions for audit trail and compliance verification</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
