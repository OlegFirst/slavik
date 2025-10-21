'use client';

import React from 'react';
import { RiskCategory, RiskStatus, RiskSeverity } from '@/types/risk';
import { Filter, X } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface RiskFilterState {
  category?: RiskCategory;
  status?: RiskStatus;
  severity?: RiskSeverity;
  minScore?: number;
  maxScore?: number;
  owner?: string;
  search?: string;
}

interface RiskFiltersProps {
  filters: RiskFilterState;
  onChange: (filters: RiskFilterState) => void;
  onReset: () => void;
  className?: string;
}

/**
 * RiskFilters - Advanced filter panel for risk list
 *
 * Features:
 * - Category, status, severity filters
 * - Risk score range filtering
 * - Owner filtering
 * - Search functionality
 * - Clear all filters
 */
export function RiskFilters({ filters, onChange, onReset, className }: RiskFiltersProps) {
  const hasActiveFilters = Object.values(filters).some(v => v !== undefined && v !== '');

  const handleCategoryChange = (category: string) => {
    onChange({
      ...filters,
      category: category === '' ? undefined : (category as RiskCategory),
    });
  };

  const handleStatusChange = (status: string) => {
    onChange({
      ...filters,
      status: status === '' ? undefined : (status as RiskStatus),
    });
  };

  const handleSeverityChange = (severity: string) => {
    onChange({
      ...filters,
      severity: severity === '' ? undefined : (severity as RiskSeverity),
    });
  };

  const handleMinScoreChange = (value: string) => {
    const num = value === '' ? undefined : parseInt(value, 10);
    onChange({
      ...filters,
      minScore: num,
    });
  };

  const handleMaxScoreChange = (value: string) => {
    const num = value === '' ? undefined : parseInt(value, 10);
    onChange({
      ...filters,
      maxScore: num,
    });
  };

  const handleOwnerChange = (value: string) => {
    onChange({
      ...filters,
      owner: value === '' ? undefined : value,
    });
  };

  const handleSearchChange = (value: string) => {
    onChange({
      ...filters,
      search: value === '' ? undefined : value,
    });
  };

  return (
    <div className={cn('bg-white rounded-lg border border-gray-200 p-6', className)}>
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Filter className="w-5 h-5 text-gray-600" />
          <h3 className="text-lg font-semibold text-gray-900">Filters</h3>
        </div>

        {hasActiveFilters && (
          <button
            onClick={onReset}
            className="text-sm text-orange-600 hover:text-orange-700 inline-flex items-center gap-1 transition-colors"
          >
            <X className="w-4 h-4" />
            Clear All
          </button>
        )}
      </div>

      <div className="space-y-4">
        {/* Search */}
        <div>
          <label htmlFor="search" className="block text-sm font-medium text-gray-700 mb-2">
            Search
          </label>
          <input
            id="search"
            type="text"
            value={filters.search || ''}
            onChange={(e) => handleSearchChange(e.target.value)}
            placeholder="Search risks by title or code..."
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
          />
        </div>

        {/* Category Filter */}
        <div>
          <label htmlFor="category" className="block text-sm font-medium text-gray-700 mb-2">
            Category
          </label>
          <select
            id="category"
            value={filters.category || ''}
            onChange={(e) => handleCategoryChange(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
          >
            <option value="">All Categories</option>
            <option value={RiskCategory.OPERATIONAL}>Operational</option>
            <option value={RiskCategory.FINANCIAL}>Financial</option>
            <option value={RiskCategory.STRATEGIC}>Strategic</option>
            <option value={RiskCategory.COMPLIANCE}>Compliance</option>
            <option value={RiskCategory.REPUTATIONAL}>Reputational</option>
            <option value={RiskCategory.CYBERSECURITY}>Cybersecurity</option>
            <option value={RiskCategory.NATURAL_DISASTER}>Natural Disaster</option>
          </select>
        </div>

        {/* Status Filter */}
        <div>
          <label htmlFor="status" className="block text-sm font-medium text-gray-700 mb-2">
            Status
          </label>
          <select
            id="status"
            value={filters.status || ''}
            onChange={(e) => handleStatusChange(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
          >
            <option value="">All Statuses</option>
            <option value={RiskStatus.IDENTIFIED}>Identified</option>
            <option value={RiskStatus.ANALYZING}>Analyzing</option>
            <option value={RiskStatus.TREATED}>Treated</option>
            <option value={RiskStatus.MONITORING}>Monitoring</option>
            <option value={RiskStatus.CLOSED}>Closed</option>
          </select>
        </div>

        {/* Severity Filter */}
        <div>
          <label htmlFor="severity" className="block text-sm font-medium text-gray-700 mb-2">
            Severity
          </label>
          <select
            id="severity"
            value={filters.severity || ''}
            onChange={(e) => handleSeverityChange(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
          >
            <option value="">All Severity Levels</option>
            <option value="low">Low (1-7)</option>
            <option value="medium">Medium (8-14)</option>
            <option value="high">High (15-19)</option>
            <option value="critical">Critical (20-25)</option>
          </select>
        </div>

        {/* Score Range */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Risk Score Range
          </label>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label htmlFor="minScore" className="block text-xs text-gray-600 mb-1">
                Min Score
              </label>
              <input
                id="minScore"
                type="number"
                min="1"
                max="25"
                value={filters.minScore || ''}
                onChange={(e) => handleMinScoreChange(e.target.value)}
                placeholder="1"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
              />
            </div>
            <div>
              <label htmlFor="maxScore" className="block text-xs text-gray-600 mb-1">
                Max Score
              </label>
              <input
                id="maxScore"
                type="number"
                min="1"
                max="25"
                value={filters.maxScore || ''}
                onChange={(e) => handleMaxScoreChange(e.target.value)}
                placeholder="25"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
              />
            </div>
          </div>
          <p className="text-xs text-gray-500 mt-1">
            Risk score is calculated as Likelihood × Impact (1-25)
          </p>
        </div>

        {/* Owner Filter */}
        <div>
          <label htmlFor="owner" className="block text-sm font-medium text-gray-700 mb-2">
            Risk Owner
          </label>
          <input
            id="owner"
            type="text"
            value={filters.owner || ''}
            onChange={(e) => handleOwnerChange(e.target.value)}
            placeholder="Filter by owner ID..."
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
          />
        </div>
      </div>

      {/* Active Filters Summary */}
      {hasActiveFilters && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <p className="text-sm text-gray-600 mb-2">Active Filters:</p>
          <div className="flex flex-wrap gap-2">
            {filters.category && (
              <span className="inline-flex items-center gap-1 px-2 py-1 bg-orange-100 text-orange-700 rounded text-xs">
                Category: {filters.category}
                <button
                  onClick={() => handleCategoryChange('')}
                  className="hover:text-orange-900"
                >
                  <X className="w-3 h-3" />
                </button>
              </span>
            )}
            {filters.status && (
              <span className="inline-flex items-center gap-1 px-2 py-1 bg-orange-100 text-orange-700 rounded text-xs">
                Status: {filters.status}
                <button
                  onClick={() => handleStatusChange('')}
                  className="hover:text-orange-900"
                >
                  <X className="w-3 h-3" />
                </button>
              </span>
            )}
            {filters.severity && (
              <span className="inline-flex items-center gap-1 px-2 py-1 bg-orange-100 text-orange-700 rounded text-xs">
                Severity: {filters.severity}
                <button
                  onClick={() => handleSeverityChange('')}
                  className="hover:text-orange-900"
                >
                  <X className="w-3 h-3" />
                </button>
              </span>
            )}
            {filters.minScore !== undefined && (
              <span className="inline-flex items-center gap-1 px-2 py-1 bg-orange-100 text-orange-700 rounded text-xs">
                Min Score: {filters.minScore}
                <button
                  onClick={() => handleMinScoreChange('')}
                  className="hover:text-orange-900"
                >
                  <X className="w-3 h-3" />
                </button>
              </span>
            )}
            {filters.maxScore !== undefined && (
              <span className="inline-flex items-center gap-1 px-2 py-1 bg-orange-100 text-orange-700 rounded text-xs">
                Max Score: {filters.maxScore}
                <button
                  onClick={() => handleMaxScoreChange('')}
                  className="hover:text-orange-900"
                >
                  <X className="w-3 h-3" />
                </button>
              </span>
            )}
            {filters.owner && (
              <span className="inline-flex items-center gap-1 px-2 py-1 bg-orange-100 text-orange-700 rounded text-xs">
                Owner: {filters.owner}
                <button
                  onClick={() => handleOwnerChange('')}
                  className="hover:text-orange-900"
                >
                  <X className="w-3 h-3" />
                </button>
              </span>
            )}
            {filters.search && (
              <span className="inline-flex items-center gap-1 px-2 py-1 bg-orange-100 text-orange-700 rounded text-xs">
                Search: "{filters.search}"
                <button
                  onClick={() => handleSearchChange('')}
                  className="hover:text-orange-900"
                >
                  <X className="w-3 h-3" />
                </button>
              </span>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
