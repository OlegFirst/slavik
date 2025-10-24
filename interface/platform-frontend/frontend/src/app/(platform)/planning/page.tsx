'use client';

/**
 * Planning Module - Main List Page
 * Business Continuity Planning with filters, stats dashboard, and responsive design
 * Week 5 Round 4 - AI Platform ISO Project (Agent 13)
 */

import React, { useState, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import { usePlans, usePlanCoverage } from '@/hooks/planning';
import { PlanList } from '@/components/planning';
import { PlanTypeBadge, PlanStatusBadge } from '@/components/planning';
import {
  Plus,
  FileText,
  CheckCircle2,
  FileEdit,
  TrendingUp,
  Filter,
  ChevronRight,
  Loader2,
  Search,
  X,
} from 'lucide-react';
import type { BCPlan, PlanType, PlanStatus } from '@/lib/api/planning-client';

export default function PlanningPage() {
  const router = useRouter();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedPlanType, setSelectedPlanType] = useState<PlanType | undefined>(undefined);
  const [selectedStatus, setSelectedStatus] = useState<PlanStatus | undefined>(undefined);
  const [showFilters, setShowFilters] = useState(false);

  // TODO: Get from auth context
  const organizationId = 'org-123';

  const { data: plansResponse, isLoading, error } = usePlans({
    organization_id: organizationId,
    plan_type: selectedPlanType,
    status: selectedStatus,
  });

  const { data: coverage } = usePlanCoverage({
    organizationId,
  });

  const plans = plansResponse?.plans || [];

  // Filter plans by search term (client-side)
  const filteredPlans = useMemo(() => {
    if (!searchTerm) return plans;
    const term = searchTerm.toLowerCase();
    return plans.filter(
      (plan) =>
        plan.plan_name.toLowerCase().includes(term) ||
        plan.description?.toLowerCase().includes(term) ||
        plan.scope?.toLowerCase().includes(term)
    );
  }, [plans, searchTerm]);

  // Calculate stats
  const stats = useMemo(() => {
    if (!plans) return null;

    return {
      total: plans.length,
      active: plans.filter((p) => p.status === 'active').length,
      draft: plans.filter((p) => p.status === 'draft').length,
      approved: plans.filter((p) => p.status === 'approved').length,
    };
  }, [plans]);

  // Count active filters
  const activeFilterCount = useMemo(() => {
    let count = 0;
    if (selectedPlanType) count++;
    if (selectedStatus) count++;
    if (searchTerm) count++;
    return count;
  }, [selectedPlanType, selectedStatus, searchTerm]);

  // Handle plan click
  const handlePlanClick = (plan: BCPlan) => {
    router.push(`/planning/${plan.id}`);
  };

  // Reset filters
  const handleResetFilters = () => {
    setSearchTerm('');
    setSelectedPlanType(undefined);
    setSelectedStatus(undefined);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      <div className="max-w-[1800px] mx-auto p-8 space-y-6">
        {/* Breadcrumbs */}
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <button
            onClick={() => router.push('/')}
            className="hover:text-blue-600 transition-colors"
          >
            Home
          </button>
          <ChevronRight className="w-4 h-4" />
          <span className="text-gray-900 font-medium">Business Continuity Planning</span>
        </div>

        {/* Header */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-blue-100 rounded-xl">
                <FileText className="w-10 h-10 text-blue-600" />
              </div>
              <div>
                <h1 className="text-4xl font-bold text-gray-900">Business Continuity Planning</h1>
                <p className="text-gray-600 mt-2">
                  Develop and manage recovery strategies and action plans
                </p>
              </div>
            </div>

            <button
              onClick={() => router.push('/planning/new')}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors inline-flex items-center gap-2 font-medium shadow-lg"
            >
              <Plus className="w-5 h-5" />
              Create New Plan
            </button>
          </div>
        </div>

        {/* Stats Cards */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Total Plans */}
            <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Total Plans</p>
                  <p className="text-3xl font-bold text-gray-900 mt-2">{stats.total}</p>
                  <p className="text-xs text-gray-500 mt-1">All BC plans</p>
                </div>
                <div className="p-3 bg-blue-100 rounded-lg">
                  <FileText className="w-8 h-8 text-blue-600" />
                </div>
              </div>
            </div>

            {/* Active Plans */}
            <div className="bg-gradient-to-br from-green-50 to-green-100 border border-green-200 rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-semibold text-green-700">Active</p>
                  <p className="text-3xl font-bold text-green-900 mt-2">{stats.active}</p>
                  <p className="text-xs text-green-600 mt-1">Currently active</p>
                </div>
                <div className="p-3 bg-green-200 rounded-lg">
                  <CheckCircle2 className="w-8 h-8 text-green-700" />
                </div>
              </div>
            </div>

            {/* Draft Plans */}
            <div className="bg-gradient-to-br from-yellow-50 to-yellow-100 border border-yellow-200 rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-semibold text-yellow-700">Draft</p>
                  <p className="text-3xl font-bold text-yellow-900 mt-2">{stats.draft}</p>
                  <p className="text-xs text-yellow-600 mt-1">In development</p>
                </div>
                <div className="p-3 bg-yellow-200 rounded-lg">
                  <FileEdit className="w-8 h-8 text-yellow-700" />
                </div>
              </div>
            </div>

            {/* Coverage Percentage */}
            <div className="bg-gradient-to-br from-purple-50 to-purple-100 border border-purple-200 rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-semibold text-purple-700">Coverage</p>
                  <p className="text-3xl font-bold text-purple-900 mt-2">
                    {coverage?.coverage_percentage || 0}%
                  </p>
                  <p className="text-xs text-purple-600 mt-1">Process coverage</p>
                </div>
                <div className="p-3 bg-purple-200 rounded-lg">
                  <TrendingUp className="w-8 h-8 text-purple-700" />
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Main Content Area */}
        <div className="bg-white rounded-xl shadow-lg overflow-hidden">
          {/* Controls Bar */}
          <div className="p-4 border-b border-gray-200 bg-gray-50">
            <div className="flex items-center justify-between gap-4 flex-wrap">
              <div className="flex items-center gap-4">
                <h2 className="text-lg font-semibold text-gray-900">
                  {isLoading ? 'Loading...' : `${filteredPlans.length} Plans`}
                </h2>
                {activeFilterCount > 0 && (
                  <span className="px-3 py-1 bg-blue-100 text-blue-700 text-sm font-medium rounded-full">
                    {activeFilterCount} filter{activeFilterCount !== 1 ? 's' : ''} active
                  </span>
                )}
              </div>

              {/* Filter Toggle */}
              <button
                onClick={() => setShowFilters(!showFilters)}
                className={`flex items-center gap-2 px-4 py-2 border rounded-lg transition-colors ${
                  showFilters
                    ? 'bg-blue-50 border-blue-600 text-blue-700'
                    : 'border-gray-300 text-gray-700 hover:bg-gray-50'
                }`}
              >
                <Filter className="w-4 h-4" />
                Filters
                {activeFilterCount > 0 && (
                  <span className="px-2 py-0.5 bg-blue-600 text-white text-xs rounded-full">
                    {activeFilterCount}
                  </span>
                )}
              </button>
            </div>

            {/* Search Bar */}
            <div className="mt-4 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search plans by name, code, or description..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-10 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              {searchTerm && (
                <button
                  onClick={() => setSearchTerm('')}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                  <X className="w-5 h-5" />
                </button>
              )}
            </div>

            {/* Filter Controls */}
            {showFilters && (
              <div className="mt-4 p-4 bg-white border border-gray-200 rounded-lg space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Plan Type Filter */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Plan Type
                    </label>
                    <select
                      value={selectedPlanType || ''}
                      onChange={(e) =>
                        setSelectedPlanType(e.target.value as PlanType || undefined)
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="">All Types</option>
                      <option value="bcp">Business Continuity Plan</option>
                      <option value="drp">Disaster Recovery Plan</option>
                      <option value="crisis">Crisis Management</option>
                      <option value="it_recovery">IT Recovery</option>
                      <option value="communication">Communication Plan</option>
                    </select>
                  </div>

                  {/* Status Filter */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Status
                    </label>
                    <select
                      value={selectedStatus || ''}
                      onChange={(e) =>
                        setSelectedStatus(e.target.value as PlanStatus || undefined)
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="">All Statuses</option>
                      <option value="draft">Draft</option>
                      <option value="review">In Review</option>
                      <option value="approved">Approved</option>
                      <option value="active">Active</option>
                      <option value="archived">Archived</option>
                    </select>
                  </div>
                </div>

                {/* Reset Button */}
                {activeFilterCount > 0 && (
                  <button
                    onClick={handleResetFilters}
                    className="text-sm text-blue-600 hover:text-blue-700 font-medium"
                  >
                    Reset all filters
                  </button>
                )}
              </div>
            )}
          </div>

          {/* Content */}
          <div className="p-6 bg-gray-50">
            {/* Loading State */}
            {isLoading && (
              <div className="flex items-center justify-center py-12">
                <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
              </div>
            )}

            {/* Error State */}
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
                <FileText className="w-8 h-8 text-red-600 mx-auto mb-3" />
                <p className="text-red-800 font-medium">Error loading plans</p>
                <p className="text-sm text-red-600 mt-2">
                  {error instanceof Error ? error.message : 'Unknown error'}
                </p>
              </div>
            )}

            {/* Empty State */}
            {!isLoading && !error && filteredPlans.length === 0 && (
              <div className="bg-white border-2 border-dashed border-gray-300 rounded-lg p-12 text-center">
                <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  {activeFilterCount > 0 ? 'No plans found' : 'No plans yet'}
                </h3>
                <p className="text-gray-600 mb-6">
                  {activeFilterCount > 0
                    ? 'Try adjusting your filters or search term'
                    : 'Get started by creating your first business continuity plan'}
                </p>
                <button
                  onClick={() => router.push('/planning/new')}
                  className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors inline-flex items-center gap-2"
                >
                  <Plus className="w-4 h-4" />
                  Create BC Plan
                </button>
              </div>
            )}

            {/* Plan List */}
            {!isLoading && !error && filteredPlans.length > 0 && (
              <PlanList
                plans={filteredPlans as any}
                onPlanClick={handlePlanClick as any}
                loading={false}
              />
            )}
          </div>
        </div>

        {/* ISO 22301 Info Card */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex gap-3">
            <div className="flex-shrink-0">
              <div className="w-5 h-5 bg-blue-500 rounded-full flex items-center justify-center">
                <span className="text-white text-xs font-bold">i</span>
              </div>
            </div>
            <div className="text-sm text-blue-800">
              <p className="font-medium mb-1">ISO 22301:2019 Compliance</p>
              <p className="text-blue-700">
                Business continuity plans must align with Clause 8.3 requirements, including
                recovery strategies, resource requirements, and documented procedures for
                maintaining critical business functions during disruptions.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
