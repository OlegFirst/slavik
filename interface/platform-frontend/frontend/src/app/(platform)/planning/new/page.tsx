'use client';

/**
 * Planning Module - Create New BC Plan Page
 * Form for creating new business continuity plans with validation
 * Week 5 Round 4 - AI Platform ISO Project (Agent 13)
 */

import React from 'react';
import { useRouter } from 'next/navigation';
import { useCreatePlan } from '@/hooks/planning';
import { PlanForm } from '@/components/planning';
import type { BCPlanCreate, PlanType } from '@/lib/api/planning-client';
import { ArrowLeft, FileText, ChevronRight, Shield, Target, Users } from 'lucide-react';

export default function NewPlanPage() {
  const router = useRouter();
  const createPlan = useCreatePlan({
    onSuccess: (plan) => {
      router.push(`/planning/${plan.id}`);
    },
  });

  // TODO: Get from auth context
  const organizationId = 'org-123';
  const userId = 'user-123';

  const handleSubmit = (data: BCPlanCreate) => {
    // Ensure required fields are set
    const planData: BCPlanCreate = {
      ...data,
      organization_id: organizationId,
      owner_id: userId,
    };
    createPlan.mutate(planData);
  };

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
          <span className="text-gray-900 font-medium">New Plan</span>
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
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Create BC Plan</h1>
              <p className="text-gray-600 mt-1">
                Develop a comprehensive business continuity plan
              </p>
            </div>
          </div>
        </div>

        {/* Info Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Plan Structure */}
          <div className="bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200 rounded-lg p-4">
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2 bg-blue-200 rounded-lg">
                <Shield className="w-5 h-5 text-blue-700" />
              </div>
              <h3 className="font-semibold text-blue-900">Plan Structure</h3>
            </div>
            <p className="text-sm text-blue-700">
              Define scope, objectives, and recovery strategies aligned with ISO 22301:2019
            </p>
          </div>

          {/* Recovery Objectives */}
          <div className="bg-gradient-to-br from-indigo-50 to-indigo-100 border border-indigo-200 rounded-lg p-4">
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2 bg-indigo-200 rounded-lg">
                <Target className="w-5 h-5 text-indigo-700" />
              </div>
              <h3 className="font-semibold text-indigo-900">RTO/RPO/MTPD</h3>
            </div>
            <p className="text-sm text-indigo-700">
              Set recovery time and point objectives to guide continuity efforts
            </p>
          </div>

          {/* Resource Planning */}
          <div className="bg-gradient-to-br from-purple-50 to-purple-100 border border-purple-200 rounded-lg p-4">
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2 bg-purple-200 rounded-lg">
                <Users className="w-5 h-5 text-purple-700" />
              </div>
              <h3 className="font-semibold text-purple-900">Resources</h3>
            </div>
            <p className="text-sm text-purple-700">
              Identify personnel, equipment, and facilities needed for recovery
            </p>
          </div>
        </div>

        {/* ISO 22301 Guidelines */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex gap-3">
            <div className="flex-shrink-0">
              <div className="w-5 h-5 bg-blue-500 rounded-full flex items-center justify-center">
                <span className="text-white text-xs font-bold">i</span>
              </div>
            </div>
            <div className="text-sm text-blue-800">
              <p className="font-medium mb-1">ISO 22301:2019 Clause 8.3 Requirements</p>
              <ul className="list-disc list-inside space-y-1 text-blue-700">
                <li>Define clear business continuity objectives and priorities</li>
                <li>Identify recovery strategies for critical business functions</li>
                <li>Document resource requirements (personnel, equipment, facilities)</li>
                <li>Establish recovery time objectives (RTO) and recovery point objectives (RPO)</li>
                <li>Consider dependencies and interdependencies between processes</li>
                <li>Align plans with risk assessment and business impact analysis results</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Form */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <PlanForm
            onSubmit={handleSubmit as any}
            onCancel={() => router.back()}
            isLoading={createPlan.isPending}
          />
        </div>

        {/* Help Text */}
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-gray-900 mb-2">Need Help?</h3>
          <p className="text-sm text-gray-600">
            Business continuity plans should be comprehensive yet actionable. Start with a clear
            scope definition, then outline recovery strategies that address identified risks and
            business impacts. You can add detailed recovery strategies and action plans after
            creating the initial plan structure.
          </p>
        </div>

        {/* Plan Type Guide */}
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-gray-900 mb-3">Plan Type Guide</h3>
          <div className="space-y-3 text-sm">
            <div className="flex gap-3">
              <div className="flex-shrink-0 w-24 font-medium text-gray-700">Strategic</div>
              <div className="text-gray-600">
                High-level plans for overall business continuity direction and governance
              </div>
            </div>
            <div className="flex gap-3">
              <div className="flex-shrink-0 w-24 font-medium text-gray-700">Tactical</div>
              <div className="text-gray-600">
                Department or function-level plans for coordinating recovery activities
              </div>
            </div>
            <div className="flex gap-3">
              <div className="flex-shrink-0 w-24 font-medium text-gray-700">Operational</div>
              <div className="text-gray-600">
                Detailed procedures for executing specific recovery tasks and processes
              </div>
            </div>
          </div>
        </div>

        {/* Recovery Objectives Guide */}
        <div className="bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-blue-900 mb-3">Understanding Recovery Objectives</h3>
          <div className="space-y-3 text-sm">
            <div className="flex gap-3">
              <div className="flex-shrink-0 w-16 font-semibold text-blue-800">RTO</div>
              <div className="text-blue-700">
                <span className="font-medium">Recovery Time Objective:</span> Maximum acceptable
                time to restore a business process after a disruption
              </div>
            </div>
            <div className="flex gap-3">
              <div className="flex-shrink-0 w-16 font-semibold text-blue-800">RPO</div>
              <div className="text-blue-700">
                <span className="font-medium">Recovery Point Objective:</span> Maximum acceptable
                amount of data loss measured in time
              </div>
            </div>
            <div className="flex gap-3">
              <div className="flex-shrink-0 w-16 font-semibold text-blue-800">MTPD</div>
              <div className="text-blue-700">
                <span className="font-medium">Maximum Tolerable Period of Disruption:</span> Time
                before the business impact becomes unacceptable
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
