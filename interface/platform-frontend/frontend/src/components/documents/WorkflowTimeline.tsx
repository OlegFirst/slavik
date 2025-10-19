/**
 * WorkflowTimeline Component
 * Visual timeline of document workflow history
 * Week 4 - Documents Module - Agent 10
 */

'use client';

import { useState } from 'react';
import { formatDistanceToNow, format } from 'date-fns';
import {
  FileText,
  Send,
  CheckCircle,
  XCircle,
  Eye,
  Share2,
  Archive,
  RotateCcw,
  Edit,
  GitBranch,
  Clock,
  Filter,
  ChevronDown,
  ChevronUp,
  User,
} from 'lucide-react';
import { useWorkflowStatus } from '@/hooks/documents';
import { DocumentStatus, AccessAction } from '@/types/documents';

export interface WorkflowTimelineProps {
  documentId: number;
  showFilters?: boolean;
}

/**
 * Workflow event types derived from document status changes and actions
 */
interface WorkflowEvent {
  id: string;
  timestamp: string;
  actor: string;
  action: string;
  actionType: AccessAction | 'status_change' | 'approval_request';
  details?: string;
  metadata?: Record<string, any>;
}

/**
 * Get icon and color for event type
 */
function getEventConfig(actionType: string) {
  const configs: Record<string, { icon: any; color: string; bgColor: string; label: string }> = {
    created: {
      icon: FileText,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100',
      label: 'Created',
    },
    updated: {
      icon: Edit,
      color: 'text-amber-600',
      bgColor: 'bg-amber-100',
      label: 'Updated',
    },
    viewed: {
      icon: Eye,
      color: 'text-gray-600',
      bgColor: 'bg-gray-100',
      label: 'Viewed',
    },
    shared: {
      icon: Share2,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100',
      label: 'Shared',
    },
    approved: {
      icon: CheckCircle,
      color: 'text-green-600',
      bgColor: 'bg-green-100',
      label: 'Approved',
    },
    rejected: {
      icon: XCircle,
      color: 'text-red-600',
      bgColor: 'bg-red-100',
      label: 'Rejected',
    },
    published: {
      icon: Send,
      color: 'text-indigo-600',
      bgColor: 'bg-indigo-100',
      label: 'Published',
    },
    archived: {
      icon: Archive,
      color: 'text-gray-600',
      bgColor: 'bg-gray-100',
      label: 'Archived',
    },
    restored: {
      icon: RotateCcw,
      color: 'text-teal-600',
      bgColor: 'bg-teal-100',
      label: 'Restored',
    },
    version_created: {
      icon: GitBranch,
      color: 'text-cyan-600',
      bgColor: 'bg-cyan-100',
      label: 'Version Created',
    },
    status_change: {
      icon: Clock,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100',
      label: 'Status Changed',
    },
    approval_request: {
      icon: Send,
      color: 'text-orange-600',
      bgColor: 'bg-orange-100',
      label: 'Approval Requested',
    },
  };

  return configs[actionType] || configs.updated;
}

/**
 * Mock workflow events generator
 * In production, this would come from an API endpoint
 */
function generateMockEvents(documentId: number): WorkflowEvent[] {
  const now = new Date();
  return [
    {
      id: '1',
      timestamp: new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000).toISOString(),
      actor: 'John Smith',
      action: 'Created document',
      actionType: AccessAction.CREATED,
      details: 'Initial draft created',
    },
    {
      id: '2',
      timestamp: new Date(now.getTime() - 6 * 24 * 60 * 60 * 1000).toISOString(),
      actor: 'John Smith',
      action: 'Updated content',
      actionType: AccessAction.UPDATED,
      details: 'Added sections 1-3',
    },
    {
      id: '3',
      timestamp: new Date(now.getTime() - 5 * 24 * 60 * 60 * 1000).toISOString(),
      actor: 'John Smith',
      action: 'Requested approval',
      actionType: 'approval_request',
      details: 'Sent to Quality Manager for review',
    },
    {
      id: '4',
      timestamp: new Date(now.getTime() - 4 * 24 * 60 * 60 * 1000).toISOString(),
      actor: 'Sarah Johnson',
      action: 'Approved document',
      actionType: AccessAction.APPROVED,
      details: 'Approved by Quality Manager',
      metadata: { stage: 1, notes: 'Looks good, ready for publication' },
    },
    {
      id: '5',
      timestamp: new Date(now.getTime() - 3 * 24 * 60 * 60 * 1000).toISOString(),
      actor: 'John Smith',
      action: 'Published document',
      actionType: AccessAction.PUBLISHED,
      details: 'Document published to organization',
    },
    {
      id: '6',
      timestamp: new Date(now.getTime() - 2 * 24 * 60 * 60 * 1000).toISOString(),
      actor: 'Michael Chen',
      action: 'Viewed document',
      actionType: AccessAction.VIEWED,
      details: 'First view by team member',
    },
    {
      id: '7',
      timestamp: new Date(now.getTime() - 1 * 24 * 60 * 60 * 1000).toISOString(),
      actor: 'John Smith',
      action: 'Shared with team',
      actionType: AccessAction.SHARED,
      details: 'Shared with Engineering team',
      metadata: { permission: 'view', recipients: 5 },
    },
  ];
}

export function WorkflowTimeline({ documentId, showFilters = true }: WorkflowTimelineProps) {
  const [expandedEvents, setExpandedEvents] = useState<Set<string>>(new Set());
  const [selectedFilter, setSelectedFilter] = useState<string | null>(null);

  // Fetch workflow status
  const { data: workflowStatus, isLoading } = useWorkflowStatus(documentId);

  // Mock events (in production, fetch from API)
  const allEvents = generateMockEvents(documentId);

  // Filter events
  const filteredEvents = selectedFilter
    ? allEvents.filter((event) => event.actionType === selectedFilter)
    : allEvents;

  // Filter options
  const filterOptions = [
    { value: null, label: 'All Events' },
    { value: AccessAction.CREATED, label: 'Created' },
    { value: AccessAction.UPDATED, label: 'Updates' },
    { value: AccessAction.APPROVED, label: 'Approvals' },
    { value: AccessAction.PUBLISHED, label: 'Published' },
    { value: AccessAction.SHARED, label: 'Shares' },
    { value: AccessAction.VIEWED, label: 'Views' },
  ];

  const toggleEventExpanded = (eventId: string) => {
    setExpandedEvents((prev) => {
      const next = new Set(prev);
      if (next.has(eventId)) {
        next.delete(eventId);
      } else {
        next.add(eventId);
      }
      return next;
    });
  };

  if (isLoading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="flex gap-4 animate-pulse">
            <div className="w-10 h-10 bg-gray-200 rounded-full" />
            <div className="flex-1 space-y-2">
              <div className="h-4 bg-gray-200 rounded w-1/3" />
              <div className="h-3 bg-gray-200 rounded w-1/2" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (filteredEvents.length === 0) {
    return (
      <div className="text-center py-12">
        <Clock className="h-12 w-12 text-gray-300 mx-auto mb-3" />
        <p className="text-gray-500 font-medium">No workflow history available</p>
        <p className="text-sm text-gray-400 mt-1">Events will appear here as actions are taken</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Filters */}
      {showFilters && (
        <div className="flex items-center gap-2 pb-4 border-b">
          <Filter className="h-4 w-4 text-gray-500" />
          <span className="text-sm font-medium text-gray-700">Filter:</span>
          <div className="flex flex-wrap gap-2">
            {filterOptions.map((option) => (
              <button
                key={option.value || 'all'}
                onClick={() => setSelectedFilter(option.value)}
                className={`
                  px-3 py-1 text-xs font-medium rounded-full border transition-colors
                  ${
                    selectedFilter === option.value
                      ? 'bg-blue-600 text-white border-blue-600'
                      : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                  }
                `}
              >
                {option.label}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Timeline */}
      <div className="relative">
        {/* Connecting Line */}
        <div className="absolute left-5 top-0 bottom-0 w-0.5 bg-gray-200" />

        {/* Events */}
        <div className="space-y-6">
          {filteredEvents.map((event, index) => {
            const config = getEventConfig(event.actionType);
            const Icon = config.icon;
            const isExpanded = expandedEvents.has(event.id);
            const hasDetails = event.details || event.metadata;

            return (
              <div key={event.id} className="relative flex gap-4">
                {/* Icon */}
                <div
                  className={`
                    relative z-10 flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center
                    ${config.bgColor} border-2 border-white shadow-sm
                  `}
                >
                  <Icon className={`h-5 w-5 ${config.color}`} />
                </div>

                {/* Content */}
                <div className="flex-1 pb-6">
                  <div className="bg-white rounded-lg border p-4 hover:shadow-md transition-shadow">
                    {/* Header */}
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <span className={`text-sm font-semibold ${config.color}`}>
                            {config.label}
                          </span>
                          <span className="text-sm text-gray-600">{event.action}</span>
                        </div>
                        <div className="flex items-center gap-3 text-xs text-gray-500">
                          <div className="flex items-center gap-1">
                            <User className="h-3 w-3" />
                            <span>{event.actor}</span>
                          </div>
                          <span>•</span>
                          <time
                            dateTime={event.timestamp}
                            title={format(new Date(event.timestamp), 'PPpp')}
                          >
                            {formatDistanceToNow(new Date(event.timestamp), { addSuffix: true })}
                          </time>
                        </div>
                      </div>

                      {/* Expand Button */}
                      {hasDetails && (
                        <button
                          onClick={() => toggleEventExpanded(event.id)}
                          className="rounded-md p-1 hover:bg-gray-100 transition-colors"
                          aria-expanded={isExpanded}
                          aria-label={isExpanded ? 'Collapse details' : 'Expand details'}
                        >
                          {isExpanded ? (
                            <ChevronUp className="h-4 w-4 text-gray-500" />
                          ) : (
                            <ChevronDown className="h-4 w-4 text-gray-500" />
                          )}
                        </button>
                      )}
                    </div>

                    {/* Expanded Details */}
                    {isExpanded && hasDetails && (
                      <div className="mt-3 pt-3 border-t space-y-2">
                        {event.details && (
                          <p className="text-sm text-gray-700">{event.details}</p>
                        )}
                        {event.metadata && (
                          <div className="bg-gray-50 rounded p-3">
                            <p className="text-xs font-medium text-gray-700 mb-1">Additional Details</p>
                            <dl className="space-y-1 text-xs text-gray-600">
                              {Object.entries(event.metadata).map(([key, value]) => (
                                <div key={key} className="flex gap-2">
                                  <dt className="font-medium capitalize">{key.replace(/_/g, ' ')}:</dt>
                                  <dd>{typeof value === 'object' ? JSON.stringify(value) : String(value)}</dd>
                                </div>
                              ))}
                            </dl>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Current Status */}
      {workflowStatus && (
        <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
          <div className="flex items-center gap-2 mb-2">
            <Clock className="h-4 w-4 text-blue-600" />
            <span className="text-sm font-semibold text-blue-900">Current Status</span>
          </div>
          <p className="text-sm text-blue-700">
            Document is currently <span className="font-medium">{workflowStatus.current_state}</span>
          </p>
          {workflowStatus.available_actions.length > 0 && (
            <p className="text-xs text-blue-600 mt-1">
              Available actions: {workflowStatus.available_actions.join(', ')}
            </p>
          )}
        </div>
      )}
    </div>
  );
}
