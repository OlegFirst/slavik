'use client';

/**
 * Planning Module - BC Plan Detail Page
 * Comprehensive view of business continuity plan with tabs for overview, strategies, and actions
 * Week 5 Round 4 - AI Platform ISO Project (Agent 13)
 */

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { usePlan, useStrategies, useActions } from '@/hooks/planning';
import {
  PlanTypeBadge,
  PlanStatusBadge,
  StrategyCard,
  ActionCard,
} from '@/components/planning';
import {
  ArrowLeft,
  Edit,
  CheckCircle,
  Play,
  Archive,
  Calendar,
  User,
  FileText,
  Target,
  ListChecks,
  Clock,
  DollarSign,
  Shield,
  ChevronRight,
  Loader2,
  AlertTriangle,
} from 'lucide-react';
import { format } from 'date-fns';

interface PageProps {
  params: {
    id: string;
  };
}

type TabType = 'overview' | 'strategies' | 'actions' | 'history';

export default function PlanDetailPage({ params }: PageProps) {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<TabType>('overview');

  const { data: plan, isLoading, error } = usePlan({ planId: params.id });
  const { data: strategiesData } = useStrategies({ planId: params.id });
  const { data: actionsData } = useActions({ planId: params.id });

  const strategies = Array.isArray(strategiesData) ? strategiesData : [];
  const actions = Array.isArray(actionsData) ? actionsData : [];

  // Loading State
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
          </div>
        </div>
      </div>
    );
  }

  // Error State
  if (error || !plan) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
            <AlertTriangle className="w-8 h-8 text-red-600 mx-auto mb-3" />
            <p className="text-red-800 font-medium">Error loading plan</p>
            <p className="text-sm text-red-600 mt-2">
              {error instanceof Error ? error.message : 'Plan not found'}
            </p>
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

  const tabs = [
    {
      id: 'overview' as TabType,
      label: 'Overview',
      icon: <FileText className="w-4 h-4" />,
      count: undefined,
    },
    {
      id: 'strategies' as TabType,
      label: 'Strategies',
      icon: <Target className="w-4 h-4" />,
      count: strategies.length,
    },
    {
      id: 'actions' as TabType,
      label: 'Actions',
      icon: <ListChecks className="w-4 h-4" />,
      count: actions.length,
    },
    {
      id: 'history' as TabType,
      label: 'History',
      icon: <Clock className="w-4 h-4" />,
      count: undefined,
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      <div className="max-w-7xl mx-auto p-8 space-y-6">
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
          <span className="text-gray-900 font-medium truncate max-w-xs">
            {plan.plan_name}
          </span>
        </div>

        {/* Header */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-4 flex-1 min-w-0">
              <button
                onClick={() => router.push('/planning')}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors flex-shrink-0"
                aria-label="Back to plans"
              >
                <ArrowLeft className="w-5 h-5 text-gray-600" />
              </button>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-3 mb-2 flex-wrap">
                  <h1 className="text-3xl font-bold text-gray-900 truncate">
                    {plan.plan_name}
                  </h1>
                  <PlanStatusBadge status={plan.status} />
                </div>
                <div className="flex items-center gap-4 flex-wrap">
                  {plan.id && (
                    <p className="text-sm text-gray-500 font-mono">{plan.id.substring(0, 8)}</p>
                  )}
                  <PlanTypeBadge type={plan.plan_type as any} />
                  <span className="text-sm text-gray-500">Version {plan.version}</span>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-2 flex-shrink-0">
              <button
                onClick={() => router.push(`/planning/${params.id}/edit`)}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors inline-flex items-center gap-2"
              >
                <Edit className="w-4 h-4" />
                Edit
              </button>
              {plan.status === 'draft' && (
                <button
                  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors inline-flex items-center gap-2"
                  title="Approve Plan"
                >
                  <CheckCircle className="w-4 h-4" />
                  Approve
                </button>
              )}
              {plan.status === 'approved' && (
                <button
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors inline-flex items-center gap-2"
                  title="Activate Plan"
                >
                  <Play className="w-4 h-4" />
                  Activate
                </button>
              )}
              {plan.status === 'active' && (
                <button
                  className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors inline-flex items-center gap-2"
                  title="Archive Plan"
                >
                  <Archive className="w-4 h-4" />
                  Archive
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-xl shadow-lg">
          <div className="border-b border-gray-200">
            <nav className="flex gap-8 px-6 overflow-x-auto">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`py-4 border-b-2 font-medium transition-colors inline-flex items-center gap-2 whitespace-nowrap ${
                    activeTab === tab.id
                      ? 'border-blue-600 text-blue-600'
                      : 'border-transparent text-gray-600 hover:text-gray-900'
                  }`}
                >
                  {tab.icon}
                  {tab.label}
                  {tab.count !== undefined && (
                    <span className="px-2 py-0.5 bg-gray-100 text-gray-700 text-xs rounded-full font-semibold">
                      {tab.count}
                    </span>
                  )}
                </button>
              ))}
            </nav>
          </div>

          <div className="p-6">
            {/* Overview Tab */}
            {activeTab === 'overview' && (
              <div className="space-y-6">
                {/* Recovery Objectives */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200 rounded-lg p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <Clock className="w-5 h-5 text-blue-600" />
                      <h3 className="font-semibold text-blue-900">Version</h3>
                    </div>
                    <p className="text-2xl font-bold text-blue-900">
                      {plan.version}
                    </p>
                    <p className="text-xs text-blue-700 mt-1">Current Version</p>
                  </div>

                  <div className="bg-gradient-to-br from-indigo-50 to-indigo-100 border border-indigo-200 rounded-lg p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <Target className="w-5 h-5 text-indigo-600" />
                      <h3 className="font-semibold text-indigo-900">Status</h3>
                    </div>
                    <p className="text-2xl font-bold text-indigo-900 capitalize">
                      {plan.status}
                    </p>
                    <p className="text-xs text-indigo-700 mt-1">Plan Status</p>
                  </div>

                  <div className="bg-gradient-to-br from-purple-50 to-purple-100 border border-purple-200 rounded-lg p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <AlertTriangle className="w-5 h-5 text-purple-600" />
                      <h3 className="font-semibold text-purple-900">Active</h3>
                    </div>
                    <p className="text-2xl font-bold text-purple-900">
                      {plan.is_active ? 'Yes' : 'No'}
                    </p>
                    <p className="text-xs text-purple-700 mt-1">Activation Status</p>
                  </div>
                </div>

                {/* Plan Details Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Left Column */}
                  <div className="space-y-6">
                    {/* Scope */}
                    <div>
                      <h3 className="text-sm font-semibold text-gray-900 mb-2">Scope</h3>
                      <p className="text-gray-700 leading-relaxed">{plan.scope}</p>
                    </div>

                    {/* Description */}
                    <div>
                      <h3 className="text-sm font-semibold text-gray-900 mb-2">
                        Description
                      </h3>
                      <p className="text-gray-700 leading-relaxed">{plan.description}</p>
                    </div>

                    {/* Objectives */}
                    {plan.objectives.length > 0 && (
                      <div>
                        <h3 className="text-sm font-semibold text-gray-900 mb-2">
                          Objectives
                        </h3>
                        <ul className="list-disc list-inside space-y-1">
                          {plan.objectives.map((obj, i) => (
                            <li key={i} className="text-gray-700">{obj}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Related Processes */}
                    {plan.related_processes.length > 0 && (
                      <div>
                        <h3 className="text-sm font-semibold text-gray-900 mb-2">
                          Related Processes
                        </h3>
                        <div className="flex flex-wrap gap-2">
                          {plan.related_processes.map((process, i) => (
                            <span
                              key={i}
                              className="px-3 py-1 bg-blue-100 text-blue-700 text-sm rounded-full"
                            >
                              {process}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Related Risks */}
                    {plan.related_risks.length > 0 && (
                      <div>
                        <h3 className="text-sm font-semibold text-gray-900 mb-2">
                          Related Risks
                        </h3>
                        <div className="flex flex-wrap gap-2">
                          {plan.related_risks.map((risk, i) => (
                            <span
                              key={i}
                              className="px-3 py-1 bg-red-100 text-red-700 text-sm rounded-full"
                            >
                              {risk}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Right Column */}
                  <div className="space-y-6">
                    {/* Related Assets */}
                    {plan.related_assets.length > 0 && (
                      <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                        <h3 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
                          <Shield className="w-4 h-4" />
                          Related Assets
                        </h3>
                        <div className="flex flex-wrap gap-2">
                          {plan.related_assets.map((asset, i) => (
                            <span
                              key={i}
                              className="px-3 py-1 bg-green-100 text-green-700 text-sm rounded-full"
                            >
                              {asset}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Metadata */}
                    <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                      <h3 className="text-sm font-semibold text-gray-900 mb-3">Metadata</h3>
                      <div className="space-y-2 text-sm">
                        {plan.owner_id && (
                          <div className="flex items-center gap-2 text-gray-600">
                            <User className="w-4 h-4" />
                            <span>Owner: {plan.owner_id}</span>
                          </div>
                        )}
                        {plan.created_at && (
                          <div className="flex items-center gap-2 text-gray-600">
                            <Calendar className="w-4 h-4" />
                            <span>Created: {format(new Date(plan.created_at), 'PPP')}</span>
                          </div>
                        )}
                        {plan.approved_by && (
                          <div className="flex items-center gap-2 text-gray-600">
                            <CheckCircle className="w-4 h-4" />
                            <span>Approved by: {plan.approved_by}</span>
                          </div>
                        )}
                        {plan.approval_date && (
                          <div className="flex items-center gap-2 text-gray-600">
                            <Calendar className="w-4 h-4" />
                            <span>Approved: {format(new Date(plan.approval_date), 'PPP')}</span>
                          </div>
                        )}
                        {plan.review_date && (
                          <div className="flex items-center gap-2 text-gray-600">
                            <Calendar className="w-4 h-4" />
                            <span>
                              Next Review: {format(new Date(plan.review_date), 'PPP')}
                            </span>
                          </div>
                        )}
                        {plan.effective_date && (
                          <div className="flex items-center gap-2 text-gray-600">
                            <Calendar className="w-4 h-4" />
                            <span>
                              Effective: {format(new Date(plan.effective_date), 'PPP')}
                            </span>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Strategies Tab */}
            {activeTab === 'strategies' && (
              <div className="space-y-4">
                {strategies.length === 0 ? (
                  <div className="text-center py-12">
                    <Target className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                    <p className="text-gray-600">No recovery strategies defined yet</p>
                    <button className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                      Add Strategy
                    </button>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {strategies.map((strategy) => (
                      <StrategyCard key={strategy.id} strategy={strategy as any} />
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Actions Tab */}
            {activeTab === 'actions' && (
              <div className="space-y-4">
                {actions.length === 0 ? (
                  <div className="text-center py-12">
                    <ListChecks className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                    <p className="text-gray-600">No action items created yet</p>
                    <button className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                      Add Action
                    </button>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {actions.map((action) => (
                      <ActionCard key={action.id} action={action as any} />
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* History Tab */}
            {activeTab === 'history' && (
              <div className="text-center py-12">
                <Clock className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                <p className="text-gray-600">Plan history coming soon</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
