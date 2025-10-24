'use client';

import { useBIAAlignment } from '@/hooks/planning/analytics';
import { CheckCircle, AlertTriangle, XCircle, Target, ArrowUpDown, Filter, Download } from 'lucide-react';
import type { BIAAlignment } from '@/lib/api/planning-client';
import { useState, useMemo } from 'react';

interface CoverageMatrixProps {
  organizationId: string;
}

type SortField = 'process_name' | 'coverage' | 'rto_target' | 'rto_current' | 'gap' | 'plans';
type SortDirection = 'asc' | 'desc';
type FilterType = 'all' | 'covered' | 'uncovered' | 'gaps';

export function CoverageMatrix({ organizationId }: CoverageMatrixProps) {
  const { data: alignmentData, isLoading, error } = useBIAAlignment({ organizationId });

  // State for sorting and filtering
  const [sortField, setSortField] = useState<SortField>('process_name');
  const [sortDirection, setSortDirection] = useState<SortDirection>('asc');
  const [filterType, setFilterType] = useState<FilterType>('all');
  const [searchQuery, setSearchQuery] = useState('');

  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="h-8 bg-gray-200 rounded animate-pulse" />
        <div className="h-64 bg-gray-100 rounded animate-pulse" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-sm text-red-600">Failed to load coverage data</p>
      </div>
    );
  }

  // Convert to array if needed (hook returns BIAAlignment but we need array)
  const alignment: BIAAlignment[] = Array.isArray(alignmentData)
    ? alignmentData
    : alignmentData
    ? [alignmentData as BIAAlignment]
    : [];

  if (alignment.length === 0) {
    return (
      <div className="text-center py-12">
        <Target className="w-12 h-12 text-gray-400 mx-auto mb-3" />
        <p className="text-gray-500">No BIA processes found</p>
      </div>
    );
  }

  // Calculate coverage stats
  const totalProcesses = alignment.length;
  const coveredProcesses = alignment.filter((a: BIAAlignment) => a.has_plan).length;
  const coveragePercentage = Math.round((coveredProcesses / totalProcesses) * 100);

  // Calculate RTO gaps
  const processesWithGaps = alignment.filter((a: BIAAlignment) => a.gap && a.gap > 0);
  const criticalGaps = processesWithGaps.filter((a: BIAAlignment) => a.gap && a.gap > 60); // > 1 hour gap

  // Apply filtering and sorting
  const filteredAndSortedAlignment = useMemo(() => {
    let filtered = alignment;

    // Apply filter
    if (filterType === 'covered') {
      filtered = filtered.filter((a: BIAAlignment) => a.has_plan);
    } else if (filterType === 'uncovered') {
      filtered = filtered.filter((a: BIAAlignment) => !a.has_plan);
    } else if (filterType === 'gaps') {
      filtered = filtered.filter((a: BIAAlignment) => a.gap && a.gap > 0);
    }

    // Apply search
    if (searchQuery) {
      filtered = filtered.filter((a: BIAAlignment) =>
        a.process_name.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    // Apply sorting
    const sorted = [...filtered].sort((a: BIAAlignment, b: BIAAlignment) => {
      let comparison = 0;

      switch (sortField) {
        case 'process_name':
          comparison = a.process_name.localeCompare(b.process_name);
          break;
        case 'coverage':
          comparison = (a.has_plan ? 1 : 0) - (b.has_plan ? 1 : 0);
          break;
        case 'rto_target':
          comparison = (a.rto_target || 0) - (b.rto_target || 0);
          break;
        case 'rto_current':
          comparison = (a.rto_current || 0) - (b.rto_current || 0);
          break;
        case 'gap':
          comparison = (a.gap || 0) - (b.gap || 0);
          break;
        case 'plans':
          comparison = a.plan_ids.length - b.plan_ids.length;
          break;
      }

      return sortDirection === 'asc' ? comparison : -comparison;
    });

    return sorted;
  }, [alignment, filterType, searchQuery, sortField, sortDirection]);

  // Handle sort
  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  // Handle export
  const handleExport = () => {
    const csv = [
      ['Process Name', 'Coverage', 'RTO Target (min)', 'RTO Current (min)', 'Gap (min)', 'Plans'].join(','),
      ...filteredAndSortedAlignment.map((item: BIAAlignment) =>
        [
          `"${item.process_name}"`,
          item.has_plan ? 'Covered' : 'Not Covered',
          item.rto_target || '',
          item.rto_current || '',
          item.gap || '',
          item.plan_ids.length,
        ].join(',')
      ),
    ].join('\n');

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `bia-coverage-matrix-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6">
      {/* Coverage Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Coverage</p>
              <p className="text-2xl font-bold text-gray-900">{coveragePercentage}%</p>
            </div>
            <div className={`w-12 h-12 rounded-full flex items-center justify-center ${
              coveragePercentage >= 90 ? 'bg-green-100' :
              coveragePercentage >= 70 ? 'bg-yellow-100' :
              'bg-red-100'
            }`}>
              {coveragePercentage >= 90 ? (
                <CheckCircle className="w-6 h-6 text-green-600" />
              ) : coveragePercentage >= 70 ? (
                <AlertTriangle className="w-6 h-6 text-yellow-600" />
              ) : (
                <XCircle className="w-6 h-6 text-red-600" />
              )}
            </div>
          </div>
          <div className="mt-2 h-2 bg-gray-200 rounded-full overflow-hidden">
            <div
              className={`h-full ${
                coveragePercentage >= 90 ? 'bg-green-500' :
                coveragePercentage >= 70 ? 'bg-yellow-500' :
                'bg-red-500'
              }`}
              style={{ width: `${coveragePercentage}%` }}
            />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <p className="text-sm text-gray-600">Covered Processes</p>
          <p className="text-2xl font-bold text-green-600">{coveredProcesses}</p>
          <p className="text-xs text-gray-500 mt-1">of {totalProcesses} total</p>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <p className="text-sm text-gray-600">RTO Gaps</p>
          <p className="text-2xl font-bold text-yellow-600">{processesWithGaps.length}</p>
          <p className="text-xs text-gray-500 mt-1">{criticalGaps.length} critical</p>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <p className="text-sm text-gray-600">Uncovered</p>
          <p className="text-2xl font-bold text-red-600">{totalProcesses - coveredProcesses}</p>
          <p className="text-xs text-gray-500 mt-1">need plans</p>
        </div>
      </div>

      {/* Controls */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
          <div className="flex flex-col sm:flex-row gap-3 flex-1">
            {/* Search */}
            <div className="relative flex-1 max-w-md">
              <input
                type="text"
                placeholder="Search processes..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            {/* Filter */}
            <div className="flex items-center gap-2">
              <Filter className="w-4 h-4 text-gray-500" />
              <select
                value={filterType}
                onChange={(e) => setFilterType(e.target.value as FilterType)}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="all">All Processes</option>
                <option value="covered">Covered Only</option>
                <option value="uncovered">Uncovered Only</option>
                <option value="gaps">With RTO Gaps</option>
              </select>
            </div>
          </div>

          {/* Export Button */}
          <button
            onClick={handleExport}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Download className="w-4 h-4" />
            Export CSV
          </button>
        </div>

        {/* Results Count */}
        <div className="mt-3 text-sm text-gray-600">
          Showing {filteredAndSortedAlignment.length} of {totalProcesses} processes
        </div>
      </div>

      {/* Matrix Table */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Process Coverage Matrix</h3>
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                  onClick={() => handleSort('process_name')}
                >
                  <div className="flex items-center gap-2">
                    Process
                    {sortField === 'process_name' && (
                      <ArrowUpDown className="w-3 h-3" />
                    )}
                  </div>
                </th>
                <th
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                  onClick={() => handleSort('coverage')}
                >
                  <div className="flex items-center gap-2">
                    Coverage
                    {sortField === 'coverage' && (
                      <ArrowUpDown className="w-3 h-3" />
                    )}
                  </div>
                </th>
                <th
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                  onClick={() => handleSort('rto_target')}
                >
                  <div className="flex items-center gap-2">
                    RTO Target
                    {sortField === 'rto_target' && (
                      <ArrowUpDown className="w-3 h-3" />
                    )}
                  </div>
                </th>
                <th
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                  onClick={() => handleSort('rto_current')}
                >
                  <div className="flex items-center gap-2">
                    RTO Current
                    {sortField === 'rto_current' && (
                      <ArrowUpDown className="w-3 h-3" />
                    )}
                  </div>
                </th>
                <th
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                  onClick={() => handleSort('gap')}
                >
                  <div className="flex items-center gap-2">
                    Gap
                    {sortField === 'gap' && (
                      <ArrowUpDown className="w-3 h-3" />
                    )}
                  </div>
                </th>
                <th
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                  onClick={() => handleSort('plans')}
                >
                  <div className="flex items-center gap-2">
                    Plans
                    {sortField === 'plans' && (
                      <ArrowUpDown className="w-3 h-3" />
                    )}
                  </div>
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredAndSortedAlignment.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-12 text-center">
                    <div className="flex flex-col items-center gap-2">
                      <Target className="w-12 h-12 text-gray-400" />
                      <p className="text-gray-500">No processes match your filters</p>
                    </div>
                  </td>
                </tr>
              ) : (
                filteredAndSortedAlignment.map((item: BIAAlignment, index: number) => (
                <tr key={index} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {item.process_name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {item.has_plan ? (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                        <CheckCircle className="w-3 h-3 mr-1" />
                        Covered
                      </span>
                    ) : (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                        <XCircle className="w-3 h-3 mr-1" />
                        Not Covered
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {item.rto_target ? `${item.rto_target} min` : '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {item.rto_current ? `${item.rto_current} min` : '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {item.gap !== undefined && item.gap !== null ? (
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        item.gap === 0 ? 'bg-green-100 text-green-800' :
                        item.gap > 60 ? 'bg-red-100 text-red-800' :
                        'bg-yellow-100 text-yellow-800'
                      }`}>
                        {item.gap > 0 ? `+${item.gap} min` : 'On Target'}
                      </span>
                    ) : (
                      <span className="text-gray-400">-</span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {item.plan_ids.length > 0 ? (
                      <span className="text-blue-600 font-medium">{item.plan_ids.length}</span>
                    ) : (
                      <span className="text-gray-400">0</span>
                    )}
                  </td>
                </tr>
              ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
