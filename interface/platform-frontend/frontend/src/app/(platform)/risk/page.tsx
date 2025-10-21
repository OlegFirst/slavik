'use client';

/**
 * Risk Assessment Module - Main List Page
 * Production-ready risk management with filters, stats dashboard, and responsive design
 * Week 5 Round 4 - AI Platform ISO Project
 */

import React, { useState, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import { useRisks } from '@/hooks/risk';
import { RiskList, RiskFilters, type RiskFilterState } from '@/components/risk';
import {
  Plus,
  AlertTriangle,
  TrendingUp,
  Shield,
  BarChart3,
  Filter,
  ChevronRight,
  Loader2,
} from 'lucide-react';
import type { Risk } from '@/types/risk';

export default function RisksPage() {
  const router = useRouter();
  const [filters, setFilters] = useState<RiskFilterState>({});
  const [showFilters, setShowFilters] = useState(false);

  // TODO: Get from auth context
  const organizationId = 'org-123';

  const { data: risks, isLoading, error } = useRisks({
    organization_id: organizationId,
    ...filters,
  });

  // Calculate stats
  const stats = useMemo(() => {
    if (!risks) return null;

    return {
      total: risks.length,
      critical: risks.filter(r => r.inherent_risk_score >= 20).length,
      high: risks.filter(r => r.inherent_risk_score >= 15 && r.inherent_risk_score < 20).length,
      medium: risks.filter(r => r.inherent_risk_score >= 8 && r.inherent_risk_score < 15).length,
      low: risks.filter(r => r.inherent_risk_score < 8).length,
    };
  }, [risks]);

  // Count active filters
  const activeFilterCount = useMemo(() => {
    let count = 0;
    if (filters.category && filters.category.length > 0) count++;
    if (filters.status && filters.status.length > 0) count++;
    if (filters.severity && filters.severity.length > 0) count++;
    if (filters.search) count++;
    return count;
  }, [filters]);

  // Handle filter changes
  const handleFilterChange = (newFilters: Partial<RiskFilterState>) => {
    setFilters((prev) => ({ ...prev, ...newFilters }));
  };

  // Handle filter reset
  const handleResetFilters = () => {
    setFilters({});
  };

  // Handle risk click
  const handleRiskClick = (risk: Risk) => {
    router.push(`/risk/${risk.id}`);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-red-50">
      <div className="max-w-[1800px] mx-auto p-8 space-y-6">
        {/* Breadcrumbs */}
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <button
            onClick={() => router.push('/')}
            className="hover:text-orange-600 transition-colors"
          >
            Home
          </button>
          <ChevronRight className="w-4 h-4" />
          <span className="text-gray-900 font-medium">Risk Assessment</span>
        </div>

        {/* Header */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-orange-100 rounded-xl">
                <AlertTriangle className="w-10 h-10 text-orange-600" />
              </div>
              <div>
                <h1 className="text-4xl font-bold text-gray-900">Risk Assessment</h1>
                <p className="text-gray-600 mt-2">
                  Identify, analyze, and manage organizational risks
                </p>
              </div>
            </div>

            <button
              onClick={() => router.push('/risk/new')}
              className="px-6 py-3 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors inline-flex items-center gap-2 font-medium shadow-lg"
            >
              <Plus className="w-5 h-5" />
              New Risk Assessment
            </button>
          </div>
        </div>

        {/* Stats Cards */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            {/* Total Risks */}
            <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Total Risks</p>
                  <p className="text-3xl font-bold text-gray-900 mt-2">{stats.total}</p>
                  <p className="text-xs text-gray-500 mt-1">All assessments</p>
                </div>
                <div className="p-3 bg-blue-100 rounded-lg">
                  <Shield className="w-8 h-8 text-blue-600" />
                </div>
              </div>
            </div>

            {/* Critical Risks */}
            <div className="bg-gradient-to-br from-red-50 to-red-100 border border-red-200 rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-semibold text-red-700">Critical</p>
                  <p className="text-3xl font-bold text-red-900 mt-2">{stats.critical}</p>
                  <p className="text-xs text-red-600 mt-1">Score 20-25</p>
                </div>
                <div className="p-3 bg-red-200 rounded-lg">
                  <AlertTriangle className="w-8 h-8 text-red-700" />
                </div>
              </div>
            </div>

            {/* High Risks */}
            <div className="bg-gradient-to-br from-orange-50 to-orange-100 border border-orange-200 rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-semibold text-orange-700">High</p>
                  <p className="text-3xl font-bold text-orange-900 mt-2">{stats.high}</p>
                  <p className="text-xs text-orange-600 mt-1">Score 15-19</p>
                </div>
                <div className="p-3 bg-orange-200 rounded-lg">
                  <TrendingUp className="w-8 h-8 text-orange-700" />
                </div>
              </div>
            </div>

            {/* Medium Risks */}
            <div className="bg-gradient-to-br from-yellow-50 to-yellow-100 border border-yellow-200 rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-semibold text-yellow-700">Medium</p>
                  <p className="text-3xl font-bold text-yellow-900 mt-2">{stats.medium}</p>
                  <p className="text-xs text-yellow-600 mt-1">Score 8-14</p>
                </div>
                <div className="p-3 bg-yellow-200 rounded-lg">
                  <BarChart3 className="w-8 h-8 text-yellow-700" />
                </div>
              </div>
            </div>

            {/* Low Risks */}
            <div className="bg-gradient-to-br from-green-50 to-green-100 border border-green-200 rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-semibold text-green-700">Low</p>
                  <p className="text-3xl font-bold text-green-900 mt-2">{stats.low}</p>
                  <p className="text-xs text-green-600 mt-1">Score 1-7</p>
                </div>
                <div className="p-3 bg-green-200 rounded-lg">
                  <Shield className="w-8 h-8 text-green-700" />
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Main Content Area */}
        <div className="bg-white rounded-xl shadow-lg overflow-hidden">
          {/* Controls Bar */}
          <div className="p-4 border-b border-gray-200 bg-gray-50">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <h2 className="text-lg font-semibold text-gray-900">
                  {isLoading ? 'Loading...' : `${risks?.length || 0} Risks`}
                </h2>
                {activeFilterCount > 0 && (
                  <span className="px-3 py-1 bg-orange-100 text-orange-700 text-sm font-medium rounded-full">
                    {activeFilterCount} filter{activeFilterCount !== 1 ? 's' : ''} active
                  </span>
                )}
              </div>

              {/* Filter Toggle */}
              <button
                onClick={() => setShowFilters(!showFilters)}
                className={`flex items-center gap-2 px-4 py-2 border rounded-lg transition-colors ${
                  showFilters
                    ? 'bg-orange-50 border-orange-600 text-orange-700'
                    : 'border-gray-300 text-gray-700 hover:bg-gray-50'
                }`}
              >
                <Filter className="w-4 h-4" />
                Filters
                {activeFilterCount > 0 && (
                  <span className="px-2 py-0.5 bg-orange-600 text-white text-xs rounded-full">
                    {activeFilterCount}
                  </span>
                )}
              </button>
            </div>
          </div>

          {/* Content with Filters */}
          <div className="flex">
            {/* Filters Sidebar */}
            {showFilters && (
              <div className="w-80 border-r border-gray-200 bg-white overflow-y-auto max-h-[800px]">
                <RiskFilters
                  filters={filters}
                  onChange={handleFilterChange}
                  onReset={handleResetFilters}
                />
              </div>
            )}

            {/* Risk List */}
            <div className="flex-1 overflow-y-auto max-h-[800px] bg-gray-50">
              <div className="p-6">
                {/* Loading State */}
                {isLoading && (
                  <div className="flex items-center justify-center py-12">
                    <Loader2 className="w-8 h-8 text-orange-600 animate-spin" />
                  </div>
                )}

                {/* Error State */}
                {error && (
                  <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
                    <AlertTriangle className="w-8 h-8 text-red-600 mx-auto mb-3" />
                    <p className="text-red-800 font-medium">Error loading risks</p>
                    <p className="text-sm text-red-600 mt-2">
                      {error instanceof Error ? error.message : 'Unknown error'}
                    </p>
                  </div>
                )}

                {/* Empty State */}
                {!isLoading && !error && (!risks || risks.length === 0) && (
                  <div className="bg-white border-2 border-dashed border-gray-300 rounded-lg p-12 text-center">
                    <AlertTriangle className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">
                      {activeFilterCount > 0 ? 'No risks found' : 'No risks yet'}
                    </h3>
                    <p className="text-gray-600 mb-6">
                      {activeFilterCount > 0
                        ? 'Try adjusting your filters'
                        : 'Get started by creating your first risk assessment'}
                    </p>
                    <button
                      onClick={() => router.push('/risk/new')}
                      className="px-6 py-3 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors inline-flex items-center gap-2"
                    >
                      <Plus className="w-4 h-4" />
                      Create Risk Assessment
                    </button>
                  </div>
                )}

                {/* Risk List */}
                {!isLoading && !error && risks && risks.length > 0 && (
                  <RiskList
                    risks={risks}
                    onRiskClick={handleRiskClick}
                    isLoading={false}
                    error={null}
                  />
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Keyboard Shortcuts Hint */}
        <div className="fixed bottom-4 right-4 bg-white border border-gray-200 rounded-lg shadow-lg p-3 text-xs text-gray-600 opacity-60 hover:opacity-100 transition-opacity">
          <div className="font-semibold mb-1">Keyboard Shortcuts</div>
          <div className="space-y-0.5">
            <div>
              <kbd className="px-1.5 py-0.5 bg-gray-100 border border-gray-300 rounded">C</kbd>{' '}
              Create
            </div>
            <div>
              <kbd className="px-1.5 py-0.5 bg-gray-100 border border-gray-300 rounded">F</kbd>{' '}
              Filters
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
