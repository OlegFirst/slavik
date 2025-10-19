'use client';

/**
 * DocumentTimeline Component
 * Unified timeline showing versions, retention milestones, and audit events
 * Week 4 - Documents Module
 */

import { useState, useMemo } from 'react';
import { format, parseISO } from 'date-fns';
import {
  GitBranch,
  FileText,
  Shield,
  CheckCircle,
  XCircle,
  Clock,
  Eye,
  Download,
  Share2,
  Archive,
  Trash2,
  AlertTriangle,
  FileCheck,
  Calendar,
  Filter,
  FileDown,
} from 'lucide-react';
import { useDocumentVersions } from '@/hooks/documents/useDocumentVersions';
import { useDocumentRetentionStatus } from '@/hooks/documents/useRetentionPolicies';
import { useDocumentAccessLog } from '@/hooks/documents/useDocumentAudit';
import type { Document, DocumentAccess, AccessAction, DocumentStatus } from '@/types/documents';

// ==================== TYPES ====================

interface DocumentTimelineProps {
  documentId: number;
  showExportButton?: boolean;
  defaultDateRange?: number; // days
}

type EventType = 'version' | 'status' | 'retention' | 'audit';

interface TimelineEvent {
  id: string;
  type: EventType;
  timestamp: string;
  title: string;
  description: string;
  icon: React.ComponentType<{ className?: string }>;
  color: string;
  metadata?: Record<string, any>;
  expandable?: boolean;
}

// ==================== HELPER FUNCTIONS ====================

/**
 * Get icon for audit action
 */
function getAuditIcon(action: AccessAction): React.ComponentType<{ className?: string }> {
  const icons: Record<AccessAction, React.ComponentType<{ className?: string }>> = {
    created: FileText,
    updated: FileCheck,
    viewed: Eye,
    downloaded: Download,
    shared: Share2,
    deleted: Trash2,
    restored: Archive,
    approved: CheckCircle,
    rejected: XCircle,
    published: FileCheck,
    archived: Archive,
    version_created: GitBranch,
  };
  return icons[action] || FileText;
}

/**
 * Get color for event type
 */
function getEventColor(type: EventType, subtype?: string): string {
  if (type === 'version') return 'bg-blue-100 text-blue-700 border-blue-300';
  if (type === 'status') {
    if (subtype === 'approved') return 'bg-green-100 text-green-700 border-green-300';
    if (subtype === 'rejected') return 'bg-red-100 text-red-700 border-red-300';
    return 'bg-purple-100 text-purple-700 border-purple-300';
  }
  if (type === 'retention') return 'bg-amber-100 text-amber-700 border-amber-300';
  if (type === 'audit') return 'bg-gray-100 text-gray-700 border-gray-300';
  return 'bg-gray-100 text-gray-700 border-gray-300';
}

/**
 * Convert version to timeline event
 */
function versionToEvent(version: Document, index: number): TimelineEvent {
  return {
    id: `version-${version.document_id}`,
    type: 'version',
    timestamp: version.created_at,
    title: `Version ${version.version} Created`,
    description: version.description || `New version created by ${version.created_by}`,
    icon: GitBranch,
    color: getEventColor('version'),
    metadata: {
      version: version.version,
      status: version.status,
      isLatest: version.is_latest,
      createdBy: version.created_by,
    },
    expandable: true,
  };
}

/**
 * Convert status change to timeline event
 */
function statusChangeToEvent(
  version: Document,
  field: 'approved_at' | 'published_at' | 'archived_at'
): TimelineEvent | null {
  const timestamp = version[field];
  if (!timestamp) return null;

  const configs = {
    approved_at: {
      title: 'Document Approved',
      description: `Version ${version.version} was approved`,
      icon: CheckCircle,
      subtype: 'approved',
    },
    published_at: {
      title: 'Document Published',
      description: `Version ${version.version} was published`,
      icon: FileCheck,
      subtype: 'published',
    },
    archived_at: {
      title: 'Document Archived',
      description: `Version ${version.version} was archived`,
      icon: Archive,
      subtype: 'archived',
    },
  };

  const config = configs[field];

  return {
    id: `status-${version.document_id}-${field}`,
    type: 'status',
    timestamp,
    title: config.title,
    description: config.description,
    icon: config.icon,
    color: getEventColor('status', config.subtype),
    metadata: {
      version: version.version,
      statusChange: field,
    },
  };
}

/**
 * Convert audit log to timeline event
 */
function auditToEvent(log: DocumentAccess): TimelineEvent {
  const actionLabels: Record<AccessAction, string> = {
    created: 'Document Created',
    updated: 'Document Updated',
    viewed: 'Document Viewed',
    downloaded: 'Document Downloaded',
    shared: 'Document Shared',
    deleted: 'Document Deleted',
    restored: 'Document Restored',
    approved: 'Document Approved',
    rejected: 'Document Rejected',
    published: 'Document Published',
    archived: 'Document Archived',
    version_created: 'Version Created',
  };

  return {
    id: `audit-${log.access_id}`,
    type: 'audit',
    timestamp: log.accessed_at,
    title: actionLabels[log.action_type] || log.action_type,
    description: `By ${log.user_id}${log.reason ? `: ${log.reason}` : ''}`,
    icon: getAuditIcon(log.action_type),
    color: getEventColor('audit'),
    metadata: {
      userId: log.user_id,
      action: log.action_type,
      ipAddress: log.ip_address,
      location: log.location,
    },
    expandable: true,
  };
}

// ==================== SUB-COMPONENTS ====================

interface TimelineItemProps {
  event: TimelineEvent;
  isFirst: boolean;
  isLast: boolean;
}

function TimelineItem({ event, isFirst, isLast }: TimelineItemProps) {
  const [expanded, setExpanded] = useState(false);
  const Icon = event.icon;

  return (
    <div className="relative">
      {/* Vertical line */}
      {!isLast && (
        <div className="absolute left-6 top-12 bottom-0 w-0.5 bg-gray-200" />
      )}

      <div className="flex gap-4">
        {/* Icon */}
        <div
          className={`
            flex-shrink-0 h-12 w-12 rounded-full border-2 flex items-center justify-center
            ${event.color}
          `}
        >
          <Icon className="h-6 w-6" />
        </div>

        {/* Content */}
        <div className="flex-1 pb-8">
          <div
            className={`
              bg-white border rounded-lg p-4 shadow-sm
              ${event.expandable ? 'cursor-pointer hover:shadow-md transition-shadow' : ''}
            `}
            onClick={() => event.expandable && setExpanded(!expanded)}
          >
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1">
                <h3 className="font-semibold text-gray-900 mb-1">{event.title}</h3>
                <p className="text-sm text-gray-600">{event.description}</p>
              </div>
              <div className="text-xs text-gray-500 whitespace-nowrap">
                {format(parseISO(event.timestamp), 'MMM d, yyyy HH:mm')}
              </div>
            </div>

            {/* Expanded details */}
            {expanded && event.metadata && (
              <div className="mt-4 pt-4 border-t grid grid-cols-2 gap-3 text-sm">
                {Object.entries(event.metadata).map(([key, value]) => (
                  <div key={key}>
                    <span className="text-gray-500 capitalize">
                      {key.replace(/([A-Z])/g, ' $1').trim()}:
                    </span>
                    <span className="ml-2 font-medium text-gray-900">
                      {typeof value === 'boolean' ? (value ? 'Yes' : 'No') : String(value)}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

interface FilterButtonProps {
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
}

function FilterButton({ active, onClick, children }: FilterButtonProps) {
  return (
    <button
      onClick={onClick}
      className={`
        px-3 py-1.5 rounded-md text-sm font-medium transition-colors
        ${
          active
            ? 'bg-blue-600 text-white'
            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
        }
      `}
    >
      {children}
    </button>
  );
}

// ==================== MAIN COMPONENT ====================

export default function DocumentTimeline({
  documentId,
  showExportButton = true,
  defaultDateRange = 90,
}: DocumentTimelineProps) {
  const [eventTypeFilters, setEventTypeFilters] = useState<Set<EventType>>(
    new Set<EventType>(['version', 'status', 'retention', 'audit'])
  );
  const [dateRange, setDateRange] = useState<number>(defaultDateRange);

  // Fetch data
  const { data: versions, isLoading: versionsLoading } = useDocumentVersions(documentId);
  const { data: retentionStatus, isLoading: retentionLoading } = useDocumentRetentionStatus(documentId);
  const { data: auditData, isLoading: auditLoading } = useDocumentAccessLog(documentId);

  const isLoading = versionsLoading || retentionLoading || auditLoading;

  // Build unified timeline
  const timeline = useMemo(() => {
    const events: TimelineEvent[] = [];

    // Add version events
    if (versions && eventTypeFilters.has('version')) {
      versions.forEach((version, index) => {
        events.push(versionToEvent(version, index));
      });
    }

    // Add status change events
    if (versions && eventTypeFilters.has('status')) {
      versions.forEach((version) => {
        const approvedEvent = statusChangeToEvent(version, 'approved_at');
        const publishedEvent = statusChangeToEvent(version, 'published_at');
        const archivedEvent = statusChangeToEvent(version, 'archived_at');

        if (approvedEvent) events.push(approvedEvent);
        if (publishedEvent) events.push(publishedEvent);
        if (archivedEvent) events.push(archivedEvent);
      });
    }

    // Add retention events
    if (retentionStatus?.policy && eventTypeFilters.has('retention')) {
      const policy = retentionStatus.policy;

      // Policy applied event
      if (policy.created_at) {
        events.push({
          id: `retention-applied-${policy.policy_id}`,
          type: 'retention',
          timestamp: policy.created_at,
          title: 'Retention Policy Applied',
          description: `Policy "${policy.policy_name}" applied to document`,
          icon: Shield,
          color: getEventColor('retention'),
          metadata: {
            policyName: policy.policy_name,
            retentionYears: policy.retention_years,
            triggerType: policy.trigger_type,
          },
        });
      }

      // Retention expiration warning (if approaching)
      if (retentionStatus.days_until_action !== null && retentionStatus.days_until_action < 30) {
        events.push({
          id: `retention-warning-${policy.policy_id}`,
          type: 'retention',
          timestamp: new Date().toISOString(),
          title: 'Retention Expiring Soon',
          description: `${retentionStatus.days_until_action} days until retention action`,
          icon: AlertTriangle,
          color: getEventColor('retention'),
          metadata: {
            daysRemaining: retentionStatus.days_until_action,
          },
        });
      }
    }

    // Add audit events
    if (auditData?.logs && eventTypeFilters.has('audit')) {
      auditData.logs.forEach((log) => {
        events.push(auditToEvent(log));
      });
    }

    // Sort by timestamp (newest first)
    return events.sort((a, b) => {
      const dateA = parseISO(a.timestamp).getTime();
      const dateB = parseISO(b.timestamp).getTime();
      return dateB - dateA;
    });
  }, [versions, retentionStatus, auditData, eventTypeFilters]);

  // Filter by date range
  const filteredTimeline = useMemo(() => {
    if (dateRange === 0) return timeline;

    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - dateRange);

    return timeline.filter((event) => {
      const eventDate = parseISO(event.timestamp);
      return eventDate >= cutoffDate;
    });
  }, [timeline, dateRange]);

  // Toggle event type filter
  const toggleEventType = (type: EventType) => {
    const newFilters = new Set(eventTypeFilters);
    if (newFilters.has(type)) {
      newFilters.delete(type);
    } else {
      newFilters.add(type);
    }
    setEventTypeFilters(newFilters);
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4" />
          <p className="text-gray-600">Loading timeline...</p>
        </div>
      </div>
    );
  }

  // Empty state
  if (filteredTimeline.length === 0) {
    return (
      <div className="text-center py-12">
        <Clock className="h-16 w-16 text-gray-300 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">No Timeline Events</h3>
        <p className="text-gray-600">
          No events found for the selected filters and date range.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 mb-1">Document Timeline</h2>
          <p className="text-gray-600">
            {filteredTimeline.length} event{filteredTimeline.length !== 1 ? 's' : ''}
          </p>
        </div>

        {showExportButton && (
          <button className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50 transition-colors">
            <FileDown className="h-5 w-5" />
            Export PDF
          </button>
        )}
      </div>

      {/* Filters */}
      <div className="bg-white border rounded-lg p-4 space-y-4">
        <div>
          <label className="text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
            <Filter className="h-4 w-4" />
            Event Types
          </label>
          <div className="flex flex-wrap gap-2">
            <FilterButton
              active={eventTypeFilters.has('version')}
              onClick={() => toggleEventType('version')}
            >
              Versions
            </FilterButton>
            <FilterButton
              active={eventTypeFilters.has('status')}
              onClick={() => toggleEventType('status')}
            >
              Status Changes
            </FilterButton>
            <FilterButton
              active={eventTypeFilters.has('retention')}
              onClick={() => toggleEventType('retention')}
            >
              Retention
            </FilterButton>
            <FilterButton
              active={eventTypeFilters.has('audit')}
              onClick={() => toggleEventType('audit')}
            >
              Audit Events
            </FilterButton>
          </div>
        </div>

        <div>
          <label className="text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
            <Calendar className="h-4 w-4" />
            Date Range
          </label>
          <div className="flex gap-2">
            <FilterButton active={dateRange === 7} onClick={() => setDateRange(7)}>
              Last 7 days
            </FilterButton>
            <FilterButton active={dateRange === 30} onClick={() => setDateRange(30)}>
              Last 30 days
            </FilterButton>
            <FilterButton active={dateRange === 90} onClick={() => setDateRange(90)}>
              Last 90 days
            </FilterButton>
            <FilterButton active={dateRange === 0} onClick={() => setDateRange(0)}>
              All Time
            </FilterButton>
          </div>
        </div>
      </div>

      {/* Timeline */}
      <div className="bg-white border rounded-lg p-6">
        <div className="space-y-0">
          {filteredTimeline.map((event, index) => (
            <TimelineItem
              key={event.id}
              event={event}
              isFirst={index === 0}
              isLast={index === filteredTimeline.length - 1}
            />
          ))}
        </div>
      </div>

      {/* Summary */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
          <div>
            <div className="text-2xl font-bold text-blue-900">
              {timeline.filter((e) => e.type === 'version').length}
            </div>
            <div className="text-sm text-blue-700">Versions</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-blue-900">
              {timeline.filter((e) => e.type === 'status').length}
            </div>
            <div className="text-sm text-blue-700">Status Changes</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-blue-900">
              {timeline.filter((e) => e.type === 'retention').length}
            </div>
            <div className="text-sm text-blue-700">Retention Events</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-blue-900">
              {timeline.filter((e) => e.type === 'audit').length}
            </div>
            <div className="text-sm text-blue-700">Audit Events</div>
          </div>
        </div>
      </div>
    </div>
  );
}
