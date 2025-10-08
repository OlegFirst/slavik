'use client';

import { useState, useEffect } from 'react';
import { useOrganizations, useOrganizationInsights } from '@/lib/api/queries';
import { InsightCard } from '@/components/insights/insight-card';
import { InsightsChart } from '@/components/charts/insights-chart';
import { Building2, TrendingUp, Activity, FileText, Loader2 } from 'lucide-react';

export default function DashboardPage() {
  const { data: organizations, isLoading: orgsLoading } = useOrganizations();
  const [selectedOrgId, setSelectedOrgId] = useState<string>('');

  const { data: insights, isLoading: insightsLoading } = useOrganizationInsights(selectedOrgId);

  // Auto-select first org (useEffect to avoid infinite loop)
  useEffect(() => {
    if (organizations && organizations.length > 0 && !selectedOrgId) {
      setSelectedOrgId(organizations[0].id);
    }
  }, [organizations, selectedOrgId]);

  const selectedOrg = organizations?.find((o) => o.id === selectedOrgId);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-1">AI-powered insights for your organization</p>
      </div>

      {/* Organization Selector */}
      <div className="bg-white rounded-lg shadow p-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Select Organization
        </label>
        {orgsLoading ? (
          <div className="flex items-center gap-2 text-gray-500">
            <Loader2 className="animate-spin" size={20} />
            <span>Loading organizations...</span>
          </div>
        ) : (
          <select
            value={selectedOrgId}
            onChange={(e) => setSelectedOrgId(e.target.value)}
            className="w-full max-w-md px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            {organizations?.map((org) => (
              <option key={org.id} value={org.id}>
                {org.name} ({org.industry})
              </option>
            ))}
          </select>
        )}
      </div>

      {/* Quick Stats */}
      {selectedOrg && (
        <div className="grid grid-cols-4 gap-4">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <TrendingUp className="text-blue-600" size={24} />
              </div>
              <div>
                <p className="text-sm text-gray-600">Health Score</p>
                <p className="text-2xl font-bold">
                  {selectedOrg.twin_health_score?.toFixed(1) || 'N/A'}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                <Activity className="text-green-600" size={24} />
              </div>
              <div>
                <p className="text-sm text-gray-600">Maturity Level</p>
                <p className="text-2xl font-bold">{selectedOrg.maturity_level}/5</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                <Building2 className="text-purple-600" size={24} />
              </div>
              <div>
                <p className="text-sm text-gray-600">Size</p>
                <p className="text-2xl font-bold capitalize">{selectedOrg.size}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center">
                <FileText className="text-yellow-600" size={24} />
              </div>
              <div>
                <p className="text-sm text-gray-600">Industry</p>
                <p className="text-lg font-bold">{selectedOrg.industry}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* AI Insights */}
      {selectedOrgId && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold text-gray-900">AI Insights</h2>
            {insights && (
              <div className="flex items-center gap-4 text-sm">
                <span className="px-3 py-1 bg-red-100 text-red-800 rounded-full font-medium">
                  Critical: {insights.summary.critical_count}
                </span>
                <span className="px-3 py-1 bg-orange-100 text-orange-800 rounded-full font-medium">
                  High: {insights.summary.high_count}
                </span>
                <span className="px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full font-medium">
                  Medium: {insights.summary.medium_count}
                </span>
                <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full font-medium">
                  Low: {insights.summary.low_count}
                </span>
              </div>
            )}
          </div>

          {/* Charts Visualization */}
          {insights && insights.insights.length > 0 && (
            <InsightsChart summary={insights.summary} />
          )}

          {insightsLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="animate-spin text-blue-600" size={32} />
            </div>
          ) : insights && insights.insights.length > 0 ? (
            <div className="space-y-4">
              {insights.insights.map((insight) => (
                <InsightCard key={insight.id} insight={insight} />
              ))}
            </div>
          ) : (
            <div className="bg-gray-50 rounded-lg p-12 text-center">
              <p className="text-gray-600">No insights available for this organization</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
