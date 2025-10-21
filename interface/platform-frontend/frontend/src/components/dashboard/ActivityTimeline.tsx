/**
 * ActivityTimeline Component
 * Displays recent platform activities across all modules
 * Dashboard Module - Agent 5
 * AI Platform ISO 22301 BCM
 */

'use client';

import { useState, useMemo } from 'react';
import { formatDistanceToNow, format } from 'date-fns';
import {
  FileText,
  CheckCircle,
  XCircle,
  Edit,
  Trash2,
  Share2,
  AlertTriangle,
  TrendingUp,
  Activity as ActivityIcon,
  Building2,
  Shield,
  ClipboardList,
  Calendar,
  Eye,
  Send,
  Archive,
  GitBranch,
  User,
  Filter,
  Clock,
  X,
} from 'lucide-react';
import { cn } from '@/lib/utils';

/**
 * Activity Module Types
 */
export type ActivityModule = 'documents' | 'bia' | 'risk' | 'planning' | 'all';

/**
 * Activity Action Types
 */
export type ActivityAction =
  | 'created'
  | 'updated'
  | 'deleted'
  | 'approved'
  | 'rejected'
  | 'published'
  | 'archived'
  | 'shared'
  | 'viewed'
  | 'completed'
  | 'started'
  | 'assessed'
  | 'mitigated';

/**
 * Activity Interface
 */
export interface Activity {
  id: string;
  user: {
    name: string;
    avatar?: string;
    initials?: string;
  };
  action: ActivityAction;
  target: string;
  targetType?: string;
  module: ActivityModule;
  timestamp: Date;
  description?: string;
  metadata?: Record<string, any>;
}

/**
 * Module Configuration
 */
const MODULE_CONFIG: Record<
  Exclude<ActivityModule, 'all'>,
  { label: string; color: string; bgColor: string; icon: any }
> = {
  documents: {
    label: 'Documents',
    color: 'text-blue-700',
    bgColor: 'bg-blue-100',
    icon: FileText,
  },
  bia: {
    label: 'BIA',
    color: 'text-purple-700',
    bgColor: 'bg-purple-100',
    icon: TrendingUp,
  },
  risk: {
    label: 'Risk',
    color: 'text-red-700',
    bgColor: 'bg-red-100',
    icon: Shield,
  },
  planning: {
    label: 'Planning',
    color: 'text-green-700',
    bgColor: 'bg-green-100',
    icon: Calendar,
  },
};

/**
 * Action Configuration
 */
const ACTION_CONFIG: Record<ActivityAction, { icon: any; color: string; label: string }> = {
  created: {
    icon: FileText,
    color: 'text-blue-600',
    label: 'created',
  },
  updated: {
    icon: Edit,
    color: 'text-amber-600',
    label: 'updated',
  },
  deleted: {
    icon: Trash2,
    color: 'text-red-600',
    label: 'deleted',
  },
  approved: {
    icon: CheckCircle,
    color: 'text-green-600',
    label: 'approved',
  },
  rejected: {
    icon: XCircle,
    color: 'text-red-600',
    label: 'rejected',
  },
  published: {
    icon: Send,
    color: 'text-indigo-600',
    label: 'published',
  },
  archived: {
    icon: Archive,
    color: 'text-gray-600',
    label: 'archived',
  },
  shared: {
    icon: Share2,
    color: 'text-purple-600',
    label: 'shared',
  },
  viewed: {
    icon: Eye,
    color: 'text-gray-600',
    label: 'viewed',
  },
  completed: {
    icon: CheckCircle,
    color: 'text-green-600',
    label: 'completed',
  },
  started: {
    icon: ActivityIcon,
    color: 'text-blue-600',
    label: 'started',
  },
  assessed: {
    icon: ClipboardList,
    color: 'text-orange-600',
    label: 'assessed',
  },
  mitigated: {
    icon: Shield,
    color: 'text-teal-600',
    label: 'mitigated',
  },
};

/**
 * Generate Mock Activities
 * In production, this would come from an API endpoint
 */
function generateMockActivities(): Activity[] {
  const now = new Date();

  const users = [
    { name: 'John Smith', initials: 'JS' },
    { name: 'Sarah Johnson', initials: 'SJ' },
    { name: 'Mike Chen', initials: 'MC' },
    { name: 'Alice Williams', initials: 'AW' },
    { name: 'David Brown', initials: 'DB' },
    { name: 'Emma Davis', initials: 'ED' },
    { name: 'Robert Taylor', initials: 'RT' },
    { name: 'Lisa Anderson', initials: 'LA' },
  ];

  const activities: Activity[] = [
    {
      id: '1',
      user: users[0],
      action: 'created',
      target: 'Risk Assessment: Data Breach Risk',
      targetType: 'Risk Assessment',
      module: 'risk',
      timestamp: new Date(now.getTime() - 15 * 60 * 1000), // 15 minutes ago
      description: 'Created new risk assessment for data breach scenarios',
    },
    {
      id: '2',
      user: users[1],
      action: 'approved',
      target: 'Document: BC Policy v2.0',
      targetType: 'Policy',
      module: 'documents',
      timestamp: new Date(now.getTime() - 45 * 60 * 1000), // 45 minutes ago
      description: 'Approved business continuity policy document',
    },
    {
      id: '3',
      user: users[2],
      action: 'updated',
      target: 'BIA Process: Customer Support',
      targetType: 'BIA Process',
      module: 'bia',
      timestamp: new Date(now.getTime() - 2 * 60 * 60 * 1000), // 2 hours ago
      description: 'Updated recovery time objectives and dependencies',
    },
    {
      id: '4',
      user: users[3],
      action: 'completed',
      target: 'Exercise: Fire Drill 2025',
      targetType: 'Exercise',
      module: 'planning',
      timestamp: new Date(now.getTime() - 3 * 60 * 60 * 1000), // 3 hours ago
      description: 'Completed fire evacuation drill with all departments',
    },
    {
      id: '5',
      user: users[4],
      action: 'assessed',
      target: 'Risk: Cloud Infrastructure Failure',
      targetType: 'Risk',
      module: 'risk',
      timestamp: new Date(now.getTime() - 4 * 60 * 60 * 1000), // 4 hours ago
      description: 'Completed FAIR analysis and risk quantification',
    },
    {
      id: '6',
      user: users[5],
      action: 'published',
      target: 'Document: Incident Response Plan',
      targetType: 'Plan',
      module: 'documents',
      timestamp: new Date(now.getTime() - 5 * 60 * 60 * 1000), // 5 hours ago
      description: 'Published updated incident response procedures',
    },
    {
      id: '7',
      user: users[6],
      action: 'created',
      target: 'BIA: Financial Operations',
      targetType: 'BIA',
      module: 'bia',
      timestamp: new Date(now.getTime() - 6 * 60 * 60 * 1000), // 6 hours ago
      description: 'Started business impact analysis for finance department',
    },
    {
      id: '8',
      user: users[7],
      action: 'shared',
      target: 'Document: Security Audit Report Q4',
      targetType: 'Report',
      module: 'documents',
      timestamp: new Date(now.getTime() - 7 * 60 * 60 * 1000), // 7 hours ago
      description: 'Shared audit report with executive team',
      metadata: { recipients: 5 },
    },
    {
      id: '9',
      user: users[0],
      action: 'mitigated',
      target: 'Risk: Third-Party Vendor Disruption',
      targetType: 'Risk',
      module: 'risk',
      timestamp: new Date(now.getTime() - 8 * 60 * 60 * 1000), // 8 hours ago
      description: 'Implemented mitigation controls and backup vendors',
    },
    {
      id: '10',
      user: users[1],
      action: 'updated',
      target: 'Plan: Business Continuity Testing Schedule',
      targetType: 'Plan',
      module: 'planning',
      timestamp: new Date(now.getTime() - 10 * 60 * 60 * 1000), // 10 hours ago
      description: 'Updated quarterly testing schedule for 2025',
    },
    {
      id: '11',
      user: users[2],
      action: 'created',
      target: 'Risk: Supply Chain Disruption',
      targetType: 'Risk',
      module: 'risk',
      timestamp: new Date(now.getTime() - 12 * 60 * 60 * 1000), // 12 hours ago
      description: 'Identified new supply chain risk scenario',
    },
    {
      id: '12',
      user: users[3],
      action: 'approved',
      target: 'BIA: IT Infrastructure',
      targetType: 'BIA',
      module: 'bia',
      timestamp: new Date(now.getTime() - 14 * 60 * 60 * 1000), // 14 hours ago
      description: 'Approved critical process assessment',
    },
    {
      id: '13',
      user: users[4],
      action: 'started',
      target: 'Exercise: Cybersecurity Incident Simulation',
      targetType: 'Exercise',
      module: 'planning',
      timestamp: new Date(now.getTime() - 16 * 60 * 60 * 1000), // 16 hours ago
      description: 'Initiated tabletop exercise for security team',
    },
    {
      id: '14',
      user: users[5],
      action: 'updated',
      target: 'Document: Contact Directory',
      targetType: 'Contact List',
      module: 'documents',
      timestamp: new Date(now.getTime() - 18 * 60 * 60 * 1000), // 18 hours ago
      description: 'Updated emergency contact information',
    },
    {
      id: '15',
      user: users[6],
      action: 'completed',
      target: 'BIA: Sales Operations',
      targetType: 'BIA',
      module: 'bia',
      timestamp: new Date(now.getTime() - 20 * 60 * 60 * 1000), // 20 hours ago
      description: 'Finalized impact analysis and recovery strategies',
    },
    {
      id: '16',
      user: users[7],
      action: 'assessed',
      target: 'Risk: Natural Disaster Impact',
      targetType: 'Risk',
      module: 'risk',
      timestamp: new Date(now.getTime() - 22 * 60 * 60 * 1000), // 22 hours ago
      description: 'Conducted vulnerability assessment for facility',
    },
    {
      id: '17',
      user: users[0],
      action: 'created',
      target: 'Document: Training Presentation - BCM Awareness',
      targetType: 'Presentation',
      module: 'documents',
      timestamp: new Date(now.getTime() - 24 * 60 * 60 * 1000), // 1 day ago
      description: 'Created employee awareness training materials',
    },
    {
      id: '18',
      user: users[1],
      action: 'published',
      target: 'Plan: Crisis Communication Plan',
      targetType: 'Plan',
      module: 'planning',
      timestamp: new Date(now.getTime() - 26 * 60 * 60 * 1000), // 26 hours ago
      description: 'Published updated crisis communication procedures',
    },
    {
      id: '19',
      user: users[2],
      action: 'updated',
      target: 'Risk: Ransomware Attack',
      targetType: 'Risk',
      module: 'risk',
      timestamp: new Date(now.getTime() - 28 * 60 * 60 * 1000), // 28 hours ago
      description: 'Updated risk score based on recent threat intelligence',
    },
    {
      id: '20',
      user: users[3],
      action: 'archived',
      target: 'Document: BC Policy v1.0 (Superseded)',
      targetType: 'Policy',
      module: 'documents',
      timestamp: new Date(now.getTime() - 30 * 60 * 60 * 1000), // 30 hours ago
      description: 'Archived previous policy version',
    },
  ];

  return activities.sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime());
}

/**
 * User Avatar Component
 */
function UserAvatar({ user }: { user: Activity['user'] }) {
  const initials = user.initials || user.name
    .split(' ')
    .map(n => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);

  return (
    <div className="relative flex-shrink-0">
      {user.avatar ? (
        <img
          src={user.avatar}
          alt={user.name}
          className="w-10 h-10 rounded-full border-2 border-white shadow-sm"
        />
      ) : (
        <div className="w-10 h-10 rounded-full border-2 border-white shadow-sm bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
          <span className="text-white text-sm font-semibold">{initials}</span>
        </div>
      )}
      <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-green-500 border-2 border-white rounded-full" />
    </div>
  );
}

/**
 * ActivityTimeline Component Props
 */
export interface ActivityTimelineProps {
  maxHeight?: string;
  showFilters?: boolean;
  maxActivities?: number;
}

/**
 * ActivityTimeline Component
 */
export function ActivityTimeline({
  maxHeight = '600px',
  showFilters = true,
  maxActivities = 20,
}: ActivityTimelineProps) {
  const [selectedModule, setSelectedModule] = useState<ActivityModule>('all');
  const [activities] = useState<Activity[]>(generateMockActivities());

  // Filter activities
  const filteredActivities = useMemo(() => {
    let filtered = activities;

    if (selectedModule !== 'all') {
      filtered = filtered.filter(activity => activity.module === selectedModule);
    }

    return filtered.slice(0, maxActivities);
  }, [activities, selectedModule, maxActivities]);

  // Filter buttons
  const filterButtons: { value: ActivityModule; label: string; icon?: any }[] = [
    { value: 'all', label: 'All', icon: ActivityIcon },
    { value: 'documents', label: 'Documents', icon: FileText },
    { value: 'bia', label: 'BIA', icon: TrendingUp },
    { value: 'risk', label: 'Risk', icon: Shield },
    { value: 'planning', label: 'Planning', icon: Calendar },
  ];

  return (
    <div className="flex flex-col h-full">
      {/* Header with Filters */}
      {showFilters && (
        <div className="mb-4 pb-4 border-b space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Clock className="h-5 w-5 text-gray-500" />
              <h3 className="text-lg font-semibold text-gray-900">Recent Activity</h3>
            </div>
            <span className="text-sm text-gray-500">
              {filteredActivities.length} {filteredActivities.length === 1 ? 'activity' : 'activities'}
            </span>
          </div>

          {/* Filter Buttons */}
          <div className="flex items-center gap-2 flex-wrap">
            <Filter className="h-4 w-4 text-gray-500" />
            <span className="text-sm font-medium text-gray-700">Filter:</span>
            <div className="flex gap-2 flex-wrap">
              {filterButtons.map((filter) => {
                const Icon = filter.icon;
                const isActive = selectedModule === filter.value;

                return (
                  <button
                    key={filter.value}
                    onClick={() => setSelectedModule(filter.value)}
                    className={cn(
                      'inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-full border transition-all',
                      isActive
                        ? 'bg-blue-600 text-white border-blue-600 shadow-sm'
                        : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50 hover:border-gray-400'
                    )}
                  >
                    {Icon && <Icon className="h-3.5 w-3.5" />}
                    {filter.label}
                    {isActive && selectedModule !== 'all' && (
                      <X className="h-3 w-3 ml-0.5" />
                    )}
                  </button>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* Timeline Container */}
      <div
        className="flex-1 overflow-y-auto pr-2 space-y-4"
        style={{ maxHeight }}
      >
        {filteredActivities.length === 0 ? (
          // Empty State
          <div className="flex flex-col items-center justify-center py-12 text-center">
            <ActivityIcon className="h-12 w-12 text-gray-300 mb-3" />
            <p className="text-gray-500 font-medium">No activities found</p>
            <p className="text-sm text-gray-400 mt-1">
              {selectedModule !== 'all'
                ? `No ${selectedModule} activities yet`
                : 'Activities will appear here as actions are taken'}
            </p>
          </div>
        ) : (
          // Timeline
          <div className="relative">
            {/* Vertical Timeline Line */}
            <div className="absolute left-5 top-2 bottom-2 w-px bg-gradient-to-b from-gray-300 via-gray-200 to-transparent" />

            {/* Activities */}
            <div className="space-y-4">
              {filteredActivities.map((activity, index) => {
                const actionConfig = ACTION_CONFIG[activity.action];
                const ActionIcon = actionConfig.icon;
                const moduleConfig = activity.module !== 'all' ? MODULE_CONFIG[activity.module] : null;
                const ModuleIcon = moduleConfig?.icon;

                return (
                  <div key={activity.id} className="relative flex gap-4 group">
                    {/* Avatar */}
                    <UserAvatar user={activity.user} />

                    {/* Content Card */}
                    <div className="flex-1 pb-2">
                      <div className="bg-white rounded-lg border border-gray-200 p-4 shadow-sm hover:shadow-md transition-shadow">
                        {/* Header */}
                        <div className="flex items-start justify-between gap-3 mb-2">
                          <div className="flex-1 min-w-0">
                            {/* User and Action */}
                            <div className="flex items-center gap-2 flex-wrap mb-1">
                              <span className="font-semibold text-gray-900 truncate">
                                {activity.user.name}
                              </span>
                              <span className={cn('font-medium', actionConfig.color)}>
                                {activity.action}
                              </span>
                              <ActionIcon className={cn('h-4 w-4 flex-shrink-0', actionConfig.color)} />
                            </div>

                            {/* Target */}
                            <p className="text-sm text-gray-700 font-medium mb-1">
                              {activity.target}
                            </p>

                            {/* Description */}
                            {activity.description && (
                              <p className="text-sm text-gray-600 line-clamp-2">
                                {activity.description}
                              </p>
                            )}
                          </div>

                          {/* Module Badge */}
                          {moduleConfig && (
                            <div
                              className={cn(
                                'flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium flex-shrink-0',
                                moduleConfig.bgColor,
                                moduleConfig.color
                              )}
                            >
                              {ModuleIcon && <ModuleIcon className="h-3 w-3" />}
                              {moduleConfig.label}
                            </div>
                          )}
                        </div>

                        {/* Footer */}
                        <div className="flex items-center gap-3 text-xs text-gray-500 pt-2 border-t">
                          <time
                            dateTime={activity.timestamp.toISOString()}
                            title={format(activity.timestamp, 'PPpp')}
                            className="flex items-center gap-1"
                          >
                            <Clock className="h-3 w-3" />
                            {formatDistanceToNow(activity.timestamp, { addSuffix: true })}
                          </time>

                          {/* Metadata */}
                          {activity.metadata && Object.keys(activity.metadata).length > 0 && (
                            <>
                              <span>•</span>
                              {Object.entries(activity.metadata).map(([key, value]) => (
                                <span key={key} className="capitalize">
                                  {key}: {String(value)}
                                </span>
                              ))}
                            </>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>

      {/* Footer Summary */}
      {filteredActivities.length > 0 && (
        <div className="mt-4 pt-4 border-t">
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-600">
              Showing {filteredActivities.length} of {activities.length} total activities
            </span>
            <button
              onClick={() => setSelectedModule('all')}
              className="text-blue-600 hover:text-blue-700 font-medium hover:underline"
            >
              View all
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

/**
 * Hook for using activities (future API integration)
 */
export function useMockActivities() {
  return useMemo(() => generateMockActivities(), []);
}

/**
 * Export utility functions
 */
export { MODULE_CONFIG, ACTION_CONFIG };
