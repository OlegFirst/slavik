/**
 * DocumentFilters Component
 * Comprehensive filter panel for document browsing
 * Week 4 Round 3 - Documents Module
 */

'use client';

import { useState, useEffect } from 'react';
import {
  Search,
  X,
  ChevronDown,
  ChevronRight,
  Calendar,
  User,
  Building2,
  Tag,
  Filter,
  RotateCcw,
  Clock,
  FileText,
  Shield,
  CheckSquare,
  Square,
} from 'lucide-react';
import { DocumentType, DocumentStatus, DocumentClassification } from '@/types/documents';

export interface FilterState {
  documentTypes: DocumentType[];
  statuses: DocumentStatus[];
  classifications: DocumentClassification[];
  departments: string[];
  owners: string[];
  dateRange: {
    from?: Date;
    to?: Date;
  };
  search: string;
  tags?: string[];
}

export interface DocumentFiltersProps {
  filters: FilterState;
  onChange: (filters: Partial<FilterState>) => void;
  onClear: () => void;
  departments?: string[];
  owners?: string[];
  tags?: string[];
}

interface FilterPreset {
  id: string;
  label: string;
  icon: React.ReactNode;
  filters: Partial<FilterState>;
}

const FILTER_PRESETS: FilterPreset[] = [
  {
    id: 'my-documents',
    label: 'My documents',
    icon: <User className="w-4 h-4" />,
    filters: {
      // Would filter by current user - requires user context
    },
  },
  {
    id: 'pending-approval',
    label: 'Pending approval',
    icon: <Clock className="w-4 h-4" />,
    filters: {
      statuses: [DocumentStatus.UNDER_REVIEW],
    },
  },
  {
    id: 'recently-published',
    label: 'Recently published',
    icon: <FileText className="w-4 h-4" />,
    filters: {
      statuses: [DocumentStatus.PUBLISHED],
      // Would add date filter for last 30 days
    },
  },
  {
    id: 'restricted',
    label: 'Restricted access',
    icon: <Shield className="w-4 h-4" />,
    filters: {
      classifications: [
        DocumentClassification.CONFIDENTIAL,
        DocumentClassification.RESTRICTED,
        DocumentClassification.HIGHLY_RESTRICTED,
      ],
    },
  },
];

const DOCUMENT_TYPE_GROUPS = {
  'Policies & Procedures': [
    DocumentType.POLICY,
    DocumentType.PROCEDURE,
    DocumentType.SOP,
  ],
  'Risk & Compliance': [
    DocumentType.RISK_ASSESSMENT,
    DocumentType.BIA,
    DocumentType.AUDIT_REPORT,
  ],
  'Plans & Strategies': [
    DocumentType.PLAN,
    DocumentType.EXERCISE_REPORT,
    DocumentType.MANAGEMENT_REVIEW,
  ],
  'Templates & Forms': [
    DocumentType.TEMPLATE,
    DocumentType.FORM,
    DocumentType.CHECKLIST,
  ],
  'Communication & Training': [
    DocumentType.COMMUNICATION,
    DocumentType.TRAINING_MATERIAL,
    DocumentType.CONTACT_LIST,
  ],
  'Documents & Evidence': [
    DocumentType.REPORT,
    DocumentType.EVIDENCE,
    DocumentType.CONTRACT,
    DocumentType.PRESENTATION,
    DocumentType.SPREADSHEET,
    DocumentType.OTHER,
  ],
};

export function DocumentFilters({
  filters,
  onChange,
  onClear,
  departments = [],
  owners = [],
  tags = [],
}: DocumentFiltersProps) {
  const [expandedSections, setExpandedSections] = useState<Set<string>>(
    new Set(['type', 'status', 'classification'])
  );
  const [searchTerm, setSearchTerm] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');

  // Debounce search input
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchTerm);
      onChange({ search: searchTerm });
    }, 300);

    return () => clearTimeout(timer);
  }, [searchTerm]);

  const toggleSection = (section: string) => {
    const newExpanded = new Set(expandedSections);
    if (newExpanded.has(section)) {
      newExpanded.delete(section);
    } else {
      newExpanded.add(section);
    }
    setExpandedSections(newExpanded);
  };

  const handleTypeToggle = (type: DocumentType) => {
    const newTypes = filters.documentTypes.includes(type)
      ? filters.documentTypes.filter((t) => t !== type)
      : [...filters.documentTypes, type];
    onChange({ documentTypes: newTypes });
  };

  const handleStatusToggle = (status: DocumentStatus) => {
    const newStatuses = filters.statuses.includes(status)
      ? filters.statuses.filter((s) => s !== status)
      : [...filters.statuses, status];
    onChange({ statuses: newStatuses });
  };

  const handleClassificationToggle = (classification: DocumentClassification) => {
    const newClassifications = filters.classifications.includes(classification)
      ? filters.classifications.filter((c) => c !== classification)
      : [...filters.classifications, classification];
    onChange({ classifications: newClassifications });
  };

  const applyPreset = (preset: FilterPreset) => {
    onChange(preset.filters);
  };

  const countActiveFilters = () => {
    let count = 0;
    if (filters.documentTypes.length > 0) count++;
    if (filters.statuses.length > 0) count++;
    if (filters.classifications.length > 0) count++;
    if (filters.departments.length > 0) count++;
    if (filters.owners.length > 0) count++;
    if (filters.dateRange.from || filters.dateRange.to) count++;
    if (filters.search) count++;
    if (filters.tags && filters.tags.length > 0) count++;
    return count;
  };

  return (
    <div className="h-full flex flex-col bg-white">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Filter className="w-5 h-5 text-gray-700" />
            <h3 className="font-semibold text-gray-900">Filters</h3>
            {countActiveFilters() > 0 && (
              <span className="px-2 py-0.5 bg-orange-100 text-orange-700 text-xs rounded-full">
                {countActiveFilters()}
              </span>
            )}
          </div>
          <button
            onClick={onClear}
            className="text-sm text-gray-600 hover:text-gray-900 flex items-center gap-1"
          >
            <RotateCcw className="w-4 h-4" />
            Clear all
          </button>
        </div>

        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search documents..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-8 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-orange-500 focus:border-transparent"
          />
          {searchTerm && (
            <button
              onClick={() => setSearchTerm('')}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* Filter Presets */}
      <div className="p-4 border-b border-gray-200">
        <h4 className="text-xs font-semibold text-gray-700 uppercase tracking-wider mb-3">
          Quick Filters
        </h4>
        <div className="space-y-2">
          {FILTER_PRESETS.map((preset) => (
            <button
              key={preset.id}
              onClick={() => applyPreset(preset)}
              className="w-full flex items-center gap-2 px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded-lg transition-colors"
            >
              {preset.icon}
              {preset.label}
            </button>
          ))}
        </div>
      </div>

      {/* Scrollable Filters */}
      <div className="flex-1 overflow-y-auto">
        {/* Document Type Filter */}
        <div className="border-b border-gray-200">
          <button
            onClick={() => toggleSection('type')}
            className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-50 transition-colors"
          >
            <span className="font-medium text-gray-900">Document Type</span>
            <div className="flex items-center gap-2">
              {filters.documentTypes.length > 0 && (
                <span className="px-2 py-0.5 bg-blue-100 text-blue-700 text-xs rounded-full">
                  {filters.documentTypes.length}
                </span>
              )}
              {expandedSections.has('type') ? (
                <ChevronDown className="w-4 h-4 text-gray-500" />
              ) : (
                <ChevronRight className="w-4 h-4 text-gray-500" />
              )}
            </div>
          </button>

          {expandedSections.has('type') && (
            <div className="px-4 pb-4 space-y-4">
              {Object.entries(DOCUMENT_TYPE_GROUPS).map(([groupName, types]) => (
                <div key={groupName}>
                  <div className="text-xs font-semibold text-gray-700 uppercase tracking-wider mb-2">
                    {groupName}
                  </div>
                  <div className="space-y-2">
                    {types.map((type) => (
                      <label
                        key={type}
                        className="flex items-center gap-2 cursor-pointer group"
                      >
                        <button
                          onClick={() => handleTypeToggle(type)}
                          className="text-gray-600 group-hover:text-gray-900"
                        >
                          {filters.documentTypes.includes(type) ? (
                            <CheckSquare className="w-4 h-4 text-orange-600" />
                          ) : (
                            <Square className="w-4 h-4" />
                          )}
                        </button>
                        <span className="text-sm text-gray-700 capitalize">
                          {type.replace(/_/g, ' ')}
                        </span>
                      </label>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Status Filter */}
        <div className="border-b border-gray-200">
          <button
            onClick={() => toggleSection('status')}
            className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-50 transition-colors"
          >
            <span className="font-medium text-gray-900">Status</span>
            <div className="flex items-center gap-2">
              {filters.statuses.length > 0 && (
                <span className="px-2 py-0.5 bg-green-100 text-green-700 text-xs rounded-full">
                  {filters.statuses.length}
                </span>
              )}
              {expandedSections.has('status') ? (
                <ChevronDown className="w-4 h-4 text-gray-500" />
              ) : (
                <ChevronRight className="w-4 h-4 text-gray-500" />
              )}
            </div>
          </button>

          {expandedSections.has('status') && (
            <div className="px-4 pb-4 space-y-2">
              {Object.values(DocumentStatus).map((status) => (
                <label key={status} className="flex items-center gap-2 cursor-pointer group">
                  <button
                    onClick={() => handleStatusToggle(status)}
                    className="text-gray-600 group-hover:text-gray-900"
                  >
                    {filters.statuses.includes(status) ? (
                      <CheckSquare className="w-4 h-4 text-orange-600" />
                    ) : (
                      <Square className="w-4 h-4" />
                    )}
                  </button>
                  <span className="text-sm text-gray-700 capitalize">
                    {status.replace(/_/g, ' ')}
                  </span>
                </label>
              ))}
            </div>
          )}
        </div>

        {/* Classification Filter */}
        <div className="border-b border-gray-200">
          <button
            onClick={() => toggleSection('classification')}
            className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-50 transition-colors"
          >
            <span className="font-medium text-gray-900">Classification</span>
            <div className="flex items-center gap-2">
              {filters.classifications.length > 0 && (
                <span className="px-2 py-0.5 bg-yellow-100 text-yellow-700 text-xs rounded-full">
                  {filters.classifications.length}
                </span>
              )}
              {expandedSections.has('classification') ? (
                <ChevronDown className="w-4 h-4 text-gray-500" />
              ) : (
                <ChevronRight className="w-4 h-4 text-gray-500" />
              )}
            </div>
          </button>

          {expandedSections.has('classification') && (
            <div className="px-4 pb-4 space-y-2">
              {Object.values(DocumentClassification).map((classification) => (
                <label
                  key={classification}
                  className="flex items-center gap-2 cursor-pointer group"
                >
                  <button
                    onClick={() => handleClassificationToggle(classification)}
                    className="text-gray-600 group-hover:text-gray-900"
                  >
                    {filters.classifications.includes(classification) ? (
                      <CheckSquare className="w-4 h-4 text-orange-600" />
                    ) : (
                      <Square className="w-4 h-4" />
                    )}
                  </button>
                  <span className="text-sm text-gray-700 uppercase">
                    {classification.replace(/_/g, ' ')}
                  </span>
                </label>
              ))}
            </div>
          )}
        </div>

        {/* Department Filter */}
        {departments.length > 0 && (
          <div className="border-b border-gray-200">
            <button
              onClick={() => toggleSection('department')}
              className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-50 transition-colors"
            >
              <div className="flex items-center gap-2">
                <Building2 className="w-4 h-4 text-gray-500" />
                <span className="font-medium text-gray-900">Department</span>
              </div>
              {expandedSections.has('department') ? (
                <ChevronDown className="w-4 h-4 text-gray-500" />
              ) : (
                <ChevronRight className="w-4 h-4 text-gray-500" />
              )}
            </button>

            {expandedSections.has('department') && (
              <div className="px-4 pb-4">
                <select
                  value={filters.departments[0] || ''}
                  onChange={(e) =>
                    onChange({
                      departments: e.target.value ? [e.target.value] : [],
                    })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                >
                  <option value="">All departments</option>
                  {departments.map((dept) => (
                    <option key={dept} value={dept}>
                      {dept}
                    </option>
                  ))}
                </select>
              </div>
            )}
          </div>
        )}

        {/* Owner Filter */}
        {owners.length > 0 && (
          <div className="border-b border-gray-200">
            <button
              onClick={() => toggleSection('owner')}
              className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-50 transition-colors"
            >
              <div className="flex items-center gap-2">
                <User className="w-4 h-4 text-gray-500" />
                <span className="font-medium text-gray-900">Owner</span>
              </div>
              {expandedSections.has('owner') ? (
                <ChevronDown className="w-4 h-4 text-gray-500" />
              ) : (
                <ChevronRight className="w-4 h-4 text-gray-500" />
              )}
            </button>

            {expandedSections.has('owner') && (
              <div className="px-4 pb-4">
                <select
                  value={filters.owners[0] || ''}
                  onChange={(e) =>
                    onChange({
                      owners: e.target.value ? [e.target.value] : [],
                    })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                >
                  <option value="">All owners</option>
                  {owners.map((owner) => (
                    <option key={owner} value={owner}>
                      {owner}
                    </option>
                  ))}
                </select>
              </div>
            )}
          </div>
        )}

        {/* Date Range Filter */}
        <div className="border-b border-gray-200">
          <button
            onClick={() => toggleSection('date')}
            className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-50 transition-colors"
          >
            <div className="flex items-center gap-2">
              <Calendar className="w-4 h-4 text-gray-500" />
              <span className="font-medium text-gray-900">Date Range</span>
            </div>
            {expandedSections.has('date') ? (
              <ChevronDown className="w-4 h-4 text-gray-500" />
            ) : (
              <ChevronRight className="w-4 h-4 text-gray-500" />
            )}
          </button>

          {expandedSections.has('date') && (
            <div className="px-4 pb-4 space-y-3">
              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">
                  From
                </label>
                <input
                  type="date"
                  value={
                    filters.dateRange.from
                      ? filters.dateRange.from.toISOString().split('T')[0]
                      : ''
                  }
                  onChange={(e) =>
                    onChange({
                      dateRange: {
                        ...filters.dateRange,
                        from: e.target.value ? new Date(e.target.value) : undefined,
                      },
                    })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">To</label>
                <input
                  type="date"
                  value={
                    filters.dateRange.to
                      ? filters.dateRange.to.toISOString().split('T')[0]
                      : ''
                  }
                  onChange={(e) =>
                    onChange({
                      dateRange: {
                        ...filters.dateRange,
                        to: e.target.value ? new Date(e.target.value) : undefined,
                      },
                    })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                />
              </div>
            </div>
          )}
        </div>

        {/* Tags Filter */}
        {tags.length > 0 && (
          <div className="border-b border-gray-200">
            <button
              onClick={() => toggleSection('tags')}
              className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-50 transition-colors"
            >
              <div className="flex items-center gap-2">
                <Tag className="w-4 h-4 text-gray-500" />
                <span className="font-medium text-gray-900">Tags</span>
              </div>
              {expandedSections.has('tags') ? (
                <ChevronDown className="w-4 h-4 text-gray-500" />
              ) : (
                <ChevronRight className="w-4 h-4 text-gray-500" />
              )}
            </button>

            {expandedSections.has('tags') && (
              <div className="px-4 pb-4">
                <div className="flex flex-wrap gap-2">
                  {tags.map((tag) => (
                    <button
                      key={tag}
                      onClick={() => {
                        const currentTags = filters.tags || [];
                        const newTags = currentTags.includes(tag)
                          ? currentTags.filter((t) => t !== tag)
                          : [...currentTags, tag];
                        onChange({ tags: newTags });
                      }}
                      className={`px-3 py-1 text-xs rounded-full transition-colors ${
                        filters.tags?.includes(tag)
                          ? 'bg-orange-100 text-orange-700 border border-orange-300'
                          : 'bg-gray-100 text-gray-700 border border-gray-300 hover:bg-gray-200'
                      }`}
                    >
                      {tag}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
