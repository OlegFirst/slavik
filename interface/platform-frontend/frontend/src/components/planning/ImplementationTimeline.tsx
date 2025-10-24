/**
 * Planning Module - Implementation Timeline Component
 * Gantt-style timeline visualization for planning events and milestones
 *
 * Created: 2025-10-21
 * Agent: 10/6 (Planning Module Round 3)
 */

'use client';

import { useState, useMemo } from 'react';
import { useImplementationTimeline } from '@/hooks/planning';
import {
  Calendar,
  CheckCircle,
  Clock,
  Shield,
  Target,
  AlertCircle,
  Filter,
  Download,
  Printer,
  ChevronDown,
  ChevronUp,
  TrendingUp,
  BarChart3,
} from 'lucide-react';
import { format, parseISO, isWithinInterval, startOfDay, endOfDay } from 'date-fns';
import type { TimelineEvent } from '@/lib/api/planning-client';

// ==================== TYPES ====================

interface ImplementationTimelineProps {
  organizationId: string;
  startDate?: string;
  endDate?: string;
  className?: string;
}

type EventType = TimelineEvent['event_type'];

interface EventTypeConfig {
  icon: React.ComponentType<{ className?: string }>;
  color: string;
  bgColor: string;
  borderColor: string;
  label: string;
}

// ==================== CONSTANTS ====================

const EVENT_TYPE_CONFIGS: Record<EventType, EventTypeConfig> = {
  plan_created: {
    icon: Calendar,
    color: 'text-blue-600',
    bgColor: 'bg-blue-50',
    borderColor: 'border-blue-200',
    label: 'Plan Created',
  },
  plan_approved: {
    icon: CheckCircle,
    color: 'text-green-600',
    bgColor: 'bg-green-50',
    borderColor: 'border-green-200',
    label: 'Plan Approved',
  },
  plan_activated: {
    icon: Shield,
    color: 'text-indigo-600',
    bgColor: 'bg-indigo-50',
    borderColor: 'border-indigo-200',
    label: 'Plan Activated',
  },
  strategy_tested: {
    icon: Target,
    color: 'text-purple-600',
    bgColor: 'bg-purple-50',
    borderColor: 'border-purple-200',
    label: 'Strategy Tested',
  },
  action_completed: {
    icon: CheckCircle,
    color: 'text-emerald-600',
    bgColor: 'bg-emerald-50',
    borderColor: 'border-emerald-200',
    label: 'Action Completed',
  },
};

// ==================== COMPONENT ====================

export function ImplementationTimeline({
  organizationId,
  startDate,
  endDate,
  className = '',
}: ImplementationTimelineProps) {
  // ==================== STATE ====================

  const [selectedEventTypes, setSelectedEventTypes] = useState<Set<EventType>>(
    new Set(Object.keys(EVENT_TYPE_CONFIGS) as EventType[])
  );
  const [showFilters, setShowFilters] = useState(false);
  const [expandedEvents, setExpandedEvents] = useState<Set<number>>(new Set());

  // ==================== DATA FETCHING ====================

  const { data: events, isLoading, error } = useImplementationTimeline({
    organizationId,
    startDate,
    endDate,
  });

  // ==================== COMPUTED VALUES ====================

  const filteredEvents = useMemo(() => {
    if (!events) return [];
    return events.filter((event) => selectedEventTypes.has(event.event_type));
  }, [events, selectedEventTypes]);

  const eventStats = useMemo(() => {
    if (!events) return null;

    return {
      plan_created: events.filter((e) => e.event_type === 'plan_created').length,
      plan_approved: events.filter((e) => e.event_type === 'plan_approved').length,
      plan_activated: events.filter((e) => e.event_type === 'plan_activated').length,
      strategy_tested: events.filter((e) => e.event_type === 'strategy_tested').length,
      action_completed: events.filter((e) => e.event_type === 'action_completed').length,
      total: events.length,
    };
  }, [events]);

  const groupedEvents = useMemo(() => {
    if (!filteredEvents) return new Map<string, TimelineEvent[]>();

    const groups = new Map<string, TimelineEvent[]>();

    filteredEvents.forEach((event) => {
      const dateKey = format(parseISO(event.event_date), 'yyyy-MM-dd');
      if (!groups.has(dateKey)) {
        groups.set(dateKey, []);
      }
      groups.get(dateKey)!.push(event);
    });

    // Sort groups by date descending
    return new Map(
      Array.from(groups.entries()).sort(([a], [b]) => b.localeCompare(a))
    );
  }, [filteredEvents]);

  // ==================== EVENT HANDLERS ====================

  const toggleEventType = (eventType: EventType) => {
    setSelectedEventTypes((prev) => {
      const next = new Set(prev);
      if (next.has(eventType)) {
        next.delete(eventType);
      } else {
        next.add(eventType);
      }
      return next;
    });
  };

  const toggleAllEventTypes = () => {
    if (selectedEventTypes.size === Object.keys(EVENT_TYPE_CONFIGS).length) {
      setSelectedEventTypes(new Set());
    } else {
      setSelectedEventTypes(new Set(Object.keys(EVENT_TYPE_CONFIGS) as EventType[]));
    }
  };

  const toggleEventExpanded = (index: number) => {
    setExpandedEvents((prev) => {
      const next = new Set(prev);
      if (next.has(index)) {
        next.delete(index);
      } else {
        next.add(index);
      }
      return next;
    });
  };

  const handleExportCSV = () => {
    if (!filteredEvents || filteredEvents.length === 0) return;

    const headers = ['Event Date', 'Event Type', 'Plan Name', 'Description'];
    const rows = filteredEvents.map((event) => [
      format(parseISO(event.event_date), 'yyyy-MM-dd HH:mm:ss'),
      event.event_type.replace('_', ' '),
      event.plan_name || 'N/A',
      event.description,
    ]);

    const csv = [
      headers.join(','),
      ...rows.map((row) =>
        row.map((cell) => `"${String(cell).replace(/"/g, '""')}"`).join(',')
      ),
    ].join('\n');

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `timeline-${format(new Date(), 'yyyy-MM-dd')}.csv`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const handlePrint = () => {
    window.print();
  };

  // ==================== RENDER HELPERS ====================

  const renderEventIcon = (eventType: EventType) => {
    const config = EVENT_TYPE_CONFIGS[eventType];
    const Icon = config.icon;
    return <Icon className={`w-5 h-5 ${config.color}`} />;
  };

  const renderEventBadge = (eventType: EventType) => {
    const config = EVENT_TYPE_CONFIGS[eventType];
    return (
      <span
        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${config.bgColor} ${config.color} border ${config.borderColor}`}
      >
        {config.label}
      </span>
    );
  };

  // ==================== LOADING STATE ====================

  if (isLoading) {
    return (
      <div className={`space-y-4 ${className}`}>
        <div className="flex items-center justify-between mb-6">
          <div className="h-8 w-48 bg-gray-200 rounded animate-pulse" />
          <div className="flex gap-2">
            <div className="h-9 w-24 bg-gray-200 rounded animate-pulse" />
            <div className="h-9 w-24 bg-gray-200 rounded animate-pulse" />
          </div>
        </div>

        {[...Array(5)].map((_, i) => (
          <div key={i} className="flex gap-4 animate-pulse">
            <div className="w-12 h-12 bg-gray-200 rounded-full flex-shrink-0" />
            <div className="flex-1 space-y-2">
              <div className="h-4 bg-gray-200 rounded w-1/4" />
              <div className="h-3 bg-gray-100 rounded w-1/2" />
              <div className="h-3 bg-gray-100 rounded w-3/4" />
            </div>
          </div>
        ))}

        <div className="bg-gray-100 rounded-lg p-6 mt-6 animate-pulse">
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="space-y-2">
                <div className="h-8 bg-gray-200 rounded" />
                <div className="h-4 bg-gray-200 rounded" />
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  // ==================== ERROR STATE ====================

  if (error) {
    return (
      <div className={`bg-red-50 border border-red-200 rounded-lg p-6 ${className}`}>
        <div className="flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="text-sm font-semibold text-red-900 mb-1">
              Failed to load timeline
            </h3>
            <p className="text-sm text-red-600">
              {error instanceof Error ? error.message : 'An unexpected error occurred'}
            </p>
          </div>
        </div>
      </div>
    );
  }

  // ==================== EMPTY STATE ====================

  if (!events || events.length === 0) {
    return (
      <div className={`text-center py-12 ${className}`}>
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gray-100 mb-4">
          <Clock className="w-8 h-8 text-gray-400" />
        </div>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">No timeline events</h3>
        <p className="text-gray-500 max-w-sm mx-auto">
          {startDate && endDate
            ? 'No events found in this date range. Try adjusting the filters.'
            : 'No events have been recorded yet. Events will appear here as plans are created and actions are completed.'}
        </p>
      </div>
    );
  }

  // ==================== MAIN RENDER ====================

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header with controls */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="inline-flex items-center justify-center w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-purple-500">
            <BarChart3 className="w-5 h-5 text-white" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-gray-900">Implementation Timeline</h2>
            <p className="text-sm text-gray-500">
              {eventStats?.total || 0} events tracked
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <Filter className="w-4 h-4" />
            Filters
            {showFilters ? (
              <ChevronUp className="w-4 h-4" />
            ) : (
              <ChevronDown className="w-4 h-4" />
            )}
          </button>

          <button
            onClick={handleExportCSV}
            className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            title="Export to CSV"
          >
            <Download className="w-4 h-4" />
            Export
          </button>

          <button
            onClick={handlePrint}
            className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors print:hidden"
            title="Print timeline"
          >
            <Printer className="w-4 h-4" />
            Print
          </button>
        </div>
      </div>

      {/* Filters panel */}
      {showFilters && (
        <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-semibold text-gray-900">Event Type Filters</h3>
            <button
              onClick={toggleAllEventTypes}
              className="text-sm font-medium text-blue-600 hover:text-blue-700"
            >
              {selectedEventTypes.size === Object.keys(EVENT_TYPE_CONFIGS).length
                ? 'Deselect All'
                : 'Select All'}
            </button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
            {(Object.entries(EVENT_TYPE_CONFIGS) as [EventType, EventTypeConfig][]).map(
              ([eventType, config]) => (
                <label
                  key={eventType}
                  className="flex items-center gap-2 cursor-pointer group"
                >
                  <input
                    type="checkbox"
                    checked={selectedEventTypes.has(eventType)}
                    onChange={() => toggleEventType(eventType)}
                    className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                  <span className="flex items-center gap-2 text-sm text-gray-700 group-hover:text-gray-900">
                    <span className={`${config.color}`}>{renderEventIcon(eventType)}</span>
                    {config.label}
                  </span>
                </label>
              )
            )}
          </div>

          <div className="mt-3 pt-3 border-t border-gray-200">
            <p className="text-xs text-gray-500">
              Showing {filteredEvents.length} of {events.length} events
            </p>
          </div>
        </div>
      )}

      {/* Timeline */}
      {filteredEvents.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-lg border border-gray-200">
          <Filter className="w-12 h-12 text-gray-400 mx-auto mb-3" />
          <p className="text-gray-500">
            No events match the selected filters. Try selecting more event types.
          </p>
        </div>
      ) : (
        <div className="relative">
          {/* Vertical gradient line */}
          <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-gradient-to-b from-blue-200 via-purple-200 to-pink-200 print:from-gray-300 print:via-gray-300 print:to-gray-300" />

          {/* Events grouped by date */}
          <div className="space-y-8">
            {Array.from(groupedEvents.entries()).map(([dateKey, dayEvents], dateIndex) => (
              <div key={dateKey} className="space-y-4">
                {/* Date header */}
                <div className="flex items-center gap-4 ml-16">
                  <div className="flex-shrink-0">
                    <div className="text-sm font-semibold text-gray-900">
                      {format(parseISO(dateKey), 'EEEE, MMMM d, yyyy')}
                    </div>
                    <div className="text-xs text-gray-500">
                      {dayEvents.length} {dayEvents.length === 1 ? 'event' : 'events'}
                    </div>
                  </div>
                  <div className="flex-1 h-px bg-gradient-to-r from-gray-200 to-transparent" />
                </div>

                {/* Events for this date */}
                {dayEvents.map((event, eventIndex) => {
                  const globalIndex = dateIndex * 1000 + eventIndex;
                  const config = EVENT_TYPE_CONFIGS[event.event_type];
                  const Icon = config.icon;
                  const isExpanded = expandedEvents.has(globalIndex);

                  return (
                    <div key={globalIndex} className="relative flex gap-4">
                      {/* Icon circle */}
                      <div
                        className={`relative z-10 flex-shrink-0 w-12 h-12 rounded-full ${config.bgColor} border-4 border-white shadow-lg flex items-center justify-center print:shadow-sm`}
                      >
                        <Icon className={`w-5 h-5 ${config.color}`} />
                      </div>

                      {/* Event content */}
                      <div className="flex-1 pb-4">
                        <div
                          className={`bg-white rounded-lg shadow-md border ${config.borderColor} overflow-hidden transition-shadow hover:shadow-lg print:shadow-sm`}
                        >
                          {/* Event header */}
                          <div className="p-4">
                            <div className="flex items-start justify-between gap-4 mb-2">
                              <div className="flex-1 min-w-0">
                                <h4 className="text-sm font-semibold text-gray-900 truncate">
                                  {event.plan_name || 'Unknown Plan'}
                                </h4>
                                <p className="text-xs text-gray-500 mt-0.5">
                                  {format(parseISO(event.event_date), 'h:mm a')}
                                </p>
                              </div>
                              {renderEventBadge(event.event_type)}
                            </div>

                            {/* Event description */}
                            <p
                              className={`text-sm text-gray-600 ${
                                isExpanded ? '' : 'line-clamp-2'
                              }`}
                            >
                              {event.description}
                            </p>

                            {/* Expand/collapse button */}
                            {event.description.length > 100 && (
                              <button
                                onClick={() => toggleEventExpanded(globalIndex)}
                                className="mt-2 text-xs font-medium text-blue-600 hover:text-blue-700 print:hidden"
                              >
                                {isExpanded ? 'Show less' : 'Show more'}
                              </button>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Timeline statistics */}
      {eventStats && (
        <div className="bg-gradient-to-br from-gray-50 to-gray-100 rounded-lg p-6 border border-gray-200 print:bg-white">
          <div className="flex items-center gap-2 mb-4">
            <TrendingUp className="w-5 h-5 text-gray-600" />
            <h3 className="text-sm font-semibold text-gray-900">Timeline Statistics</h3>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
            {(Object.entries(EVENT_TYPE_CONFIGS) as [EventType, EventTypeConfig][]).map(
              ([eventType, config]) => (
                <div
                  key={eventType}
                  className="bg-white rounded-lg p-4 border border-gray-200 text-center print:border-gray-300"
                >
                  <div className="flex items-center justify-center mb-2">
                    <div className={`${config.color}`}>{renderEventIcon(eventType)}</div>
                  </div>
                  <p className={`text-2xl font-bold ${config.color} mb-1`}>
                    {eventStats[eventType]}
                  </p>
                  <p className="text-xs text-gray-600">{config.label}</p>
                </div>
              )
            )}
          </div>

          <div className="mt-4 pt-4 border-t border-gray-200 text-center">
            <p className="text-sm text-gray-600">
              Total Events: <span className="font-semibold text-gray-900">{eventStats.total}</span>
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
