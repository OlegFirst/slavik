/**
 * RiskList Component
 * Main risk browsing interface with filters, search, and view modes
 * Week 5 Round 3 - Risk Assessment Module
 */

'use client';

import { useState, useMemo } from 'react';
import {
  Grid,
  List,
  Search,
  SlidersHorizontal,
  X,
  Plus,
  AlertCircle,
  Loader2,
  TrendingUp,
} from 'lucide-react';
import { Risk, RiskCategory, RiskStatus, RiskSeverity, getCategoryLabel, getStatusLabel } from '@/types/risk';
import { RiskCard } from './RiskCard';
import { cn } from '@/lib/utils';

export interface RiskListProps {
  risks: Risk[];
  onRiskClick?: (risk: Risk) => void;
  onCreateRisk?: () => void;
  defaultViewMode?: 'grid' | 'list';
  enableFilters?: boolean;
  enableSearch?: boolean;
  showCreateButton?: boolean;
  isLoading?: boolean;
  error?: Error | null;
  className?: string;
}

export interface FilterState {
  categories: RiskCategory[];
  statuses: RiskStatus[];
  severities: RiskSeverity[];
  minScore?: number;
  maxScore?: number;
  search: string;
}

export interface SortOption {
  value: string;
  label: string;
}

const SORT_OPTIONS: SortOption[] = [
  { value: 'score_desc', label: 'Highest Score' },
  { value: 'score_asc', label: 'Lowest Score' },
  { value: 'date_desc', label: 'Newest First' },
  { value: 'date_asc', label: 'Oldest First' },
  { value: 'title_asc', label: 'Title A-Z' },
  { value: 'title_desc', label: 'Title Z-A' },
  { value: 'review_date', label: 'Review Date' },
];

export function RiskList({
  risks,
  onRiskClick,
  onCreateRisk,
  defaultViewMode = 'grid',
  enableFilters = true,
  enableSearch = true,
  showCreateButton = true,
  isLoading = false,
  error = null,
  className,
}: RiskListProps) {
  // View mode state
  const [viewMode, setViewMode] = useState<'grid' | 'list'>(defaultViewMode);
  const [showFilters, setShowFilters] = useState(false);

  // Filter state
  const [filters, setFilters] = useState<FilterState>({
    categories: [],
    statuses: [],
    severities: [],
    search: '',
  });

  // Sort state
  const [sortBy, setSortBy] = useState('score_desc');

  // Calculate active filter count
  const activeFilterCount = useMemo(() => {
    let count = 0;
    if (filters.categories.length > 0) count++;
    if (filters.statuses.length > 0) count++;
    if (filters.severities.length > 0) count++;
    if (filters.minScore !== undefined) count++;
    if (filters.maxScore !== undefined) count++;
    if (filters.search) count++;
    return count;
  }, [filters]);

  // Filter and sort risks
  const processedRisks = useMemo(() => {
    let filtered = [...risks];

    // Apply filters
    if (filters.categories.length > 0) {
      filtered = filtered.filter(risk =>
        filters.categories.includes(risk.risk_category)
      );
    }

    if (filters.statuses.length > 0) {
      filtered = filtered.filter(risk =>
        filters.statuses.includes(risk.status)
      );
    }

    if (filters.severities.length > 0) {
      const { getRiskSeverity } = require('@/types/risk');
      filtered = filtered.filter(risk => {
        const severity = getRiskSeverity(risk.inherent_risk_score);
        return filters.severities.includes(severity);
      });
    }

    if (filters.minScore !== undefined) {
      filtered = filtered.filter(risk =>
        risk.inherent_risk_score >= (filters.minScore || 0)
      );
    }

    if (filters.maxScore !== undefined) {
      filtered = filtered.filter(risk =>
        risk.inherent_risk_score <= (filters.maxScore || 25)
      );
    }

    if (filters.search) {
      const searchLower = filters.search.toLowerCase();
      filtered = filtered.filter(risk =>
        risk.risk_title.toLowerCase().includes(searchLower) ||
        risk.description.toLowerCase().includes(searchLower) ||
        risk.risk_code?.toLowerCase().includes(searchLower)
      );
    }

    // Apply sorting
    switch (sortBy) {
      case 'score_desc':
        filtered.sort((a, b) => b.inherent_risk_score - a.inherent_risk_score);
        break;
      case 'score_asc':
        filtered.sort((a, b) => a.inherent_risk_score - b.inherent_risk_score);
        break;
      case 'date_desc':
        filtered.sort((a, b) =>
          new Date(b.created_at || 0).getTime() - new Date(a.created_at || 0).getTime()
        );
        break;
      case 'date_asc':
        filtered.sort((a, b) =>
          new Date(a.created_at || 0).getTime() - new Date(b.created_at || 0).getTime()
        );
        break;
      case 'title_asc':
        filtered.sort((a, b) => a.risk_title.localeCompare(b.risk_title));
        break;
      case 'title_desc':
        filtered.sort((a, b) => b.risk_title.localeCompare(a.risk_title));
        break;
      case 'review_date':
        filtered.sort((a, b) => {
          const dateA = a.last_reviewed_at ? new Date(a.last_reviewed_at).getTime() : 0;
          const dateB = b.last_reviewed_at ? new Date(b.last_reviewed_at).getTime() : 0;
          return dateB - dateA;
        });
        break;
    }

    return filtered;
  }, [risks, filters, sortBy]);

  // Handle filter changes
  const handleFilterChange = (newFilters: Partial<FilterState>) => {
    setFilters(prev => ({ ...prev, ...newFilters }));
  };

  // Clear all filters
  const handleClearFilters = () => {
    setFilters({
      categories: [],
      statuses: [],
      severities: [],
      search: '',
    });
  };

  // Calculate statistics
  const stats = useMemo(() => {
    const { getRiskSeverity } = require('@/types/risk');
    const critical = processedRisks.filter(r => getRiskSeverity(r.inherent_risk_score) === 'critical').length;
    const high = processedRisks.filter(r => getRiskSeverity(r.inherent_risk_score) === 'high').length;
    const medium = processedRisks.filter(r => getRiskSeverity(r.inherent_risk_score) === 'medium').length;
    const low = processedRisks.filter(r => getRiskSeverity(r.inherent_risk_score) === 'low').length;

    return { critical, high, medium, low };
  }, [processedRisks]);

  return (
    <div className={cn('flex flex-col h-full', className)}>
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Risk Assessments</h1>
            <p className="text-sm text-gray-600 mt-1">
              {processedRisks.length} of {risks.length} risks
              {activeFilterCount > 0 && ' (filtered)'}
            </p>
          </div>

          {showCreateButton && onCreateRisk && (
            <button
              onClick={onCreateRisk}
              className="flex items-center gap-2 px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors"
              aria-label="Create new risk"
            >
              <Plus className="w-4 h-4" />
              Create Risk
            </button>
          )}
        </div>

        {/* Search and Controls */}
        <div className="flex items-center gap-4 flex-wrap">
          {/* Search */}
          {enableSearch && (
            <div className="flex-1 min-w-[300px] relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search risks by title, description, code..."
                value={filters.search}
                onChange={(e) => handleFilterChange({ search: e.target.value })}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                aria-label="Search risks"
              />
              {filters.search && (
                <button
                  onClick={() => handleFilterChange({ search: '' })}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  aria-label="Clear search"
                >
                  <X className="w-4 h-4" />
                </button>
              )}
            </div>
          )}

          {/* Sort */}
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
            aria-label="Sort risks"
          >
            {SORT_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>

          {/* Filter Toggle */}
          {enableFilters && (
            <button
              onClick={() => setShowFilters(!showFilters)}
              className={cn(
                'flex items-center gap-2 px-4 py-2 border rounded-lg transition-colors',
                showFilters
                  ? 'bg-orange-50 border-orange-600 text-orange-700'
                  : 'border-gray-300 text-gray-700 hover:bg-gray-50'
              )}
              aria-label={showFilters ? 'Hide filters' : 'Show filters'}
            >
              <SlidersHorizontal className="w-4 h-4" />
              Filters
              {activeFilterCount > 0 && (
                <span className="px-2 py-0.5 bg-orange-600 text-white text-xs rounded-full">
                  {activeFilterCount}
                </span>
              )}
            </button>
          )}

          {/* View Mode Toggle */}
          <div className="flex items-center border border-gray-300 rounded-lg overflow-hidden">
            <button
              onClick={() => setViewMode('grid')}
              className={cn(
                'p-2',
                viewMode === 'grid'
                  ? 'bg-orange-50 text-orange-600'
                  : 'text-gray-600 hover:bg-gray-50'
              )}
              title="Grid view"
              aria-label="Grid view"
            >
              <Grid className="w-4 h-4" />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={cn(
                'p-2 border-l border-gray-300',
                viewMode === 'list'
                  ? 'bg-orange-50 text-orange-600'
                  : 'text-gray-600 hover:bg-gray-50'
              )}
              title="List view"
              aria-label="List view"
            >
              <List className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Active Filters & Stats */}
        {(activeFilterCount > 0 || processedRisks.length > 0) && (
          <div className="mt-4 flex items-center justify-between flex-wrap gap-3">
            {/* Active Filters */}
            {activeFilterCount > 0 && (
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-sm text-gray-600">Active filters:</span>
                {filters.categories.map((category) => (
                  <span
                    key={category}
                    className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm flex items-center gap-2"
                  >
                    {getCategoryLabel(category)}
                    <button
                      onClick={() =>
                        handleFilterChange({
                          categories: filters.categories.filter((c) => c !== category),
                        })
                      }
                      className="hover:text-blue-900"
                      aria-label={`Remove ${category} filter`}
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </span>
                ))}
                {filters.statuses.map((status) => (
                  <span
                    key={status}
                    className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm flex items-center gap-2"
                  >
                    {getStatusLabel(status)}
                    <button
                      onClick={() =>
                        handleFilterChange({
                          statuses: filters.statuses.filter((s) => s !== status),
                        })
                      }
                      className="hover:text-green-900"
                      aria-label={`Remove ${status} filter`}
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </span>
                ))}
                {filters.severities.map((severity) => (
                  <span
                    key={severity}
                    className="px-3 py-1 bg-orange-100 text-orange-700 rounded-full text-sm flex items-center gap-2"
                  >
                    {severity.toUpperCase()}
                    <button
                      onClick={() =>
                        handleFilterChange({
                          severities: filters.severities.filter((s) => s !== severity),
                        })
                      }
                      className="hover:text-orange-900"
                      aria-label={`Remove ${severity} filter`}
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </span>
                ))}
                <button
                  onClick={handleClearFilters}
                  className="px-3 py-1 text-sm text-gray-600 hover:text-gray-900 underline"
                  aria-label="Clear all filters"
                >
                  Clear all
                </button>
              </div>
            )}

            {/* Stats Summary */}
            {processedRisks.length > 0 && (
              <div className="flex items-center gap-4 text-sm">
                <div className="flex items-center gap-1">
                  <span className="w-3 h-3 bg-red-600 rounded-full"></span>
                  <span className="text-gray-600">{stats.critical} Critical</span>
                </div>
                <div className="flex items-center gap-1">
                  <span className="w-3 h-3 bg-orange-600 rounded-full"></span>
                  <span className="text-gray-600">{stats.high} High</span>
                </div>
                <div className="flex items-center gap-1">
                  <span className="w-3 h-3 bg-yellow-600 rounded-full"></span>
                  <span className="text-gray-600">{stats.medium} Medium</span>
                </div>
                <div className="flex items-center gap-1">
                  <span className="w-3 h-3 bg-green-600 rounded-full"></span>
                  <span className="text-gray-600">{stats.low} Low</span>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-y-auto bg-gray-50">
        <div className="p-6">
          {/* Loading State */}
          {isLoading && (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-8 h-8 text-orange-600 animate-spin" />
            </div>
          )}

          {/* Error State */}
          {error && !isLoading && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
              <AlertCircle className="w-12 h-12 text-red-600 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-red-900 mb-2">
                Error Loading Risks
              </h3>
              <p className="text-sm text-red-700">
                {error.message || 'An unknown error occurred'}
              </p>
            </div>
          )}

          {/* Empty State */}
          {!isLoading && !error && processedRisks.length === 0 && (
            <div className="bg-white border-2 border-dashed border-gray-300 rounded-lg p-12 text-center">
              <AlertCircle className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                No Risks Found
              </h3>
              <p className="text-gray-600 mb-6">
                {activeFilterCount > 0
                  ? 'Try adjusting your filters to see more results'
                  : 'Get started by creating your first risk assessment'}
              </p>
              {showCreateButton && onCreateRisk && activeFilterCount === 0 && (
                <button
                  onClick={onCreateRisk}
                  className="px-6 py-3 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors inline-flex items-center gap-2"
                >
                  <Plus className="w-4 h-4" />
                  Create Risk
                </button>
              )}
            </div>
          )}

          {/* Risk Cards */}
          {!isLoading && !error && processedRisks.length > 0 && (
            <div
              className={cn(
                viewMode === 'grid'
                  ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 xl:grid-cols-3 gap-6'
                  : 'space-y-4'
              )}
            >
              {processedRisks.map((risk) => (
                <RiskCard
                  key={risk.id}
                  risk={risk}
                  onClick={() => onRiskClick?.(risk)}
                  layout={viewMode}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
