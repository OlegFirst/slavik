'use client';

/**
 * Risk Assessment Module - Risk Detail Page
 * Comprehensive risk view with tabs for overview, FAIR analysis, Monte Carlo, and treatment plans
 * Week 5 Round 4 - AI Platform ISO Project
 */

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useRisk } from '@/hooks/risk';
import {
  RiskCategoryBadge,
  RiskSeverityBadge,
  RiskStatusBadge,
  FAIRAnalysisCard,
  MonteCarloChart,
  TreatmentPlanList,
} from '@/components/risk';
import { getRiskSeverity } from '@/types/risk';
import {
  ArrowLeft,
  Edit,
  Trash2,
  Calendar,
  User,
  AlertTriangle,
  FileText,
  BarChart3,
  Target,
  ChevronRight,
  Loader2,
} from 'lucide-react';
import { format } from 'date-fns';

interface PageProps {
  params: {
    id: string;
  };
}

type TabType = 'overview' | 'fair' | 'montecarlo' | 'treatment';

export default function RiskDetailPage({ params }: PageProps) {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<TabType>('overview');

  const { data: risk, isLoading, error } = useRisk({ id: params.id });

  // Loading State
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-red-50 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 text-orange-600 animate-spin" />
          </div>
        </div>
      </div>
    );
  }

  // Error State
  if (error || !risk) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-red-50 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
            <AlertTriangle className="w-8 h-8 text-red-600 mx-auto mb-3" />
            <p className="text-red-800 font-medium">Error loading risk</p>
            <p className="text-sm text-red-600 mt-2">
              {error instanceof Error ? error.message : 'Risk not found'}
            </p>
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

  const tabs = [
    {
      id: 'overview' as TabType,
      label: 'Overview',
      icon: <FileText className="w-4 h-4" />,
    },
    {
      id: 'fair' as TabType,
      label: 'FAIR Analysis',
      icon: <BarChart3 className="w-4 h-4" />,
    },
    {
      id: 'montecarlo' as TabType,
      label: 'Monte Carlo',
      icon: <Target className="w-4 h-4" />,
    },
    {
      id: 'treatment' as TabType,
      label: 'Treatment Plans',
      icon: <Target className="w-4 h-4" />,
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-red-50">
      <div className="max-w-7xl mx-auto p-8 space-y-6">
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
          <span className="text-gray-900 font-medium truncate max-w-xs">
            {risk.risk_title}
          </span>
        </div>

        {/* Header */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-4 flex-1 min-w-0">
              <button
                onClick={() => router.push('/risk')}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors flex-shrink-0"
                aria-label="Back to risks"
              >
                <ArrowLeft className="w-5 h-5 text-gray-600" />
              </button>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-3 mb-2 flex-wrap">
                  <h1 className="text-3xl font-bold text-gray-900 truncate">
                    {risk.risk_title}
                  </h1>
                  <RiskSeverityBadge severity={getRiskSeverity(risk.inherent_risk_score)} />
                </div>
                <div className="flex items-center gap-4 flex-wrap">
                  {risk.risk_code && (
                    <p className="text-sm text-gray-500 font-mono">{risk.risk_code}</p>
                  )}
                  <RiskCategoryBadge category={risk.risk_category} />
                  <RiskStatusBadge status={risk.status} />
                </div>
              </div>
            </div>

            <div className="flex items-center gap-2 flex-shrink-0">
              <button
                onClick={() => router.push(`/risk/${params.id}/edit`)}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors inline-flex items-center gap-2"
              >
                <Edit className="w-4 h-4" />
                Edit
              </button>
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
                      ? 'border-orange-600 text-orange-600'
                      : 'border-transparent text-gray-600 hover:text-gray-900'
                  }`}
                >
                  {tab.icon}
                  {tab.label}
                </button>
              ))}
            </nav>
          </div>

          <div className="p-6">
            {/* Overview Tab */}
            {activeTab === 'overview' && (
              <div className="space-y-6">
                {/* Risk Details Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Left Column */}
                  <div className="space-y-6">
                    {/* Description */}
                    <div>
                      <h3 className="text-sm font-semibold text-gray-900 mb-2">
                        Description
                      </h3>
                      <p className="text-gray-700 leading-relaxed">{risk.description}</p>
                    </div>

                    {/* Threat Source */}
                    {risk.threat_source && (
                      <div>
                        <h3 className="text-sm font-semibold text-gray-900 mb-2">
                          Threat Source
                        </h3>
                        <p className="text-gray-700">{risk.threat_source}</p>
                      </div>
                    )}

                    {/* Vulnerabilities */}
                    {risk.vulnerabilities.length > 0 && (
                      <div>
                        <h3 className="text-sm font-semibold text-gray-900 mb-2">
                          Vulnerabilities
                        </h3>
                        <ul className="space-y-2">
                          {risk.vulnerabilities.map((vuln, i) => (
                            <li key={i} className="flex items-start gap-2">
                              <AlertTriangle className="w-4 h-4 text-orange-600 mt-0.5 flex-shrink-0" />
                              <span className="text-gray-700">{vuln}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>

                  {/* Right Column */}
                  <div className="space-y-6">
                    {/* Risk Scores */}
                    <div>
                      <h3 className="text-sm font-semibold text-gray-900 mb-3">
                        Risk Scores
                      </h3>
                      <div className="space-y-3">
                        {/* Inherent Risk */}
                        <div className="bg-gradient-to-r from-red-50 to-orange-50 rounded-lg p-4 border border-red-200">
                          <p className="text-sm text-red-700 font-medium mb-1">
                            Inherent Risk Score
                          </p>
                          <p className="text-4xl font-bold text-red-900">
                            {risk.inherent_risk_score}
                          </p>
                          <p className="text-sm text-red-600 mt-2">
                            Likelihood: {risk.likelihood} × Impact: {risk.impact}
                          </p>
                        </div>

                        {/* Residual Risk */}
                        {risk.residual_risk_score && (
                          <div className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg p-4 border border-green-200">
                            <p className="text-sm text-green-700 font-medium mb-1">
                              Residual Risk Score
                            </p>
                            <p className="text-4xl font-bold text-green-900">
                              {risk.residual_risk_score}
                            </p>
                            <p className="text-sm text-green-600 mt-2">After treatment</p>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Metadata */}
                    <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                      <h3 className="text-sm font-semibold text-gray-900 mb-3">
                        Metadata
                      </h3>
                      <div className="space-y-2 text-sm">
                        {risk.risk_owner_id && (
                          <div className="flex items-center gap-2 text-gray-600">
                            <User className="w-4 h-4" />
                            <span>Owner: {risk.risk_owner_id}</span>
                          </div>
                        )}
                        {risk.created_at && (
                          <div className="flex items-center gap-2 text-gray-600">
                            <Calendar className="w-4 h-4" />
                            <span>
                              Created: {format(new Date(risk.created_at), 'PPP')}
                            </span>
                          </div>
                        )}
                        {risk.last_reviewed_at && (
                          <div className="flex items-center gap-2 text-gray-600">
                            <Calendar className="w-4 h-4" />
                            <span>
                              Last Reviewed:{' '}
                              {format(new Date(risk.last_reviewed_at), 'PPP')}
                            </span>
                          </div>
                        )}
                        {risk.next_review_date && (
                          <div className="flex items-center gap-2 text-gray-600">
                            <Calendar className="w-4 h-4" />
                            <span>
                              Next Review:{' '}
                              {format(new Date(risk.next_review_date), 'PPP')}
                            </span>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* FAIR Analysis Tab */}
            {activeTab === 'fair' && (
              <div>
                <FAIRAnalysisCard riskId={params.id} />
              </div>
            )}

            {/* Monte Carlo Tab */}
            {activeTab === 'montecarlo' && (
              <div>
                <MonteCarloChart riskId={params.id} />
              </div>
            )}

            {/* Treatment Plans Tab */}
            {activeTab === 'treatment' && (
              <div>
                <TreatmentPlanList riskId={params.id} />
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
