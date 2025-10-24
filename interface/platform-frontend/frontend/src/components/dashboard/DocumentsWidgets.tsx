'use client';

/**
 * DocumentsWidgets Component
 * Dashboard widgets for Documents module showing key metrics and actions
 * Features: Recent documents, pending approvals, status chart, quick actions
 */

import React from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import {
  FileText,
  Clock,
  CheckCircle,
  Upload,
  FilePlus,
  Search,
  AlertCircle,
  TrendingUp,
  Calendar,
  User,
  XCircle,
  FileCheck,
  FileX,
  File,
} from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend, PieLabelRenderProps } from 'recharts';
import { useDocuments } from '@/hooks/documents/useDocuments';
import { useDocumentApprovals, getPendingApprovals } from '@/hooks/documents/useDocumentApprovals';
import { DocumentStatus, DocumentType } from '@/types/documents';
import type { Document, DocumentApproval } from '@/types/documents';

// ==================== TYPES ====================

interface DocumentsWidgetsProps {
  organizationId: string;
}

interface StatusData {
  name: string;
  value: number;
  color: string;
  [key: string]: string | number; // Allow additional properties for Recharts
}

interface RecentDocument {
  id: number;
  title: string;
  type: string;
  status: string;
  modified: string;
}

// ==================== CONSTANTS ====================

const STATUS_COLORS: Record<string, string> = {
  draft: '#94a3b8',        // gray
  under_review: '#f59e0b', // amber
  approved: '#10b981',     // green
  published: '#3b82f6',    // blue
  archived: '#6b7280',     // gray
  superseded: '#8b5cf6',   // purple
  obsolete: '#ef4444',     // red
};

const CHART_COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#6b7280', '#8b5cf6'];

// ==================== COMPONENT ====================

export function DocumentsWidgets({ organizationId }: DocumentsWidgetsProps) {
  const router = useRouter();

  // Fetch recent documents (last 10)
  const { data: documentsData, isLoading: isLoadingDocuments, error: documentsError } = useDocuments(
    {
      tenant_id: organizationId,
      limit: 10,
    },
    {
      staleTime: 60 * 1000, // 1 minute
    }
  );

  // Fetch all documents for status chart
  const { data: allDocumentsData, isLoading: isLoadingAllDocuments } = useDocuments(
    {
      tenant_id: organizationId,
      limit: 1000, // Get enough for accurate stats
    },
    {
      staleTime: 5 * 60 * 1000, // 5 minutes
    }
  );

  // Calculate status distribution
  const getStatusDistribution = (): StatusData[] => {
    if (!allDocumentsData?.documents) return [];

    const statusCounts: Record<string, number> = {};

    allDocumentsData.documents.forEach((doc) => {
      const status = doc.status || 'draft';
      statusCounts[status] = (statusCounts[status] || 0) + 1;
    });

    return Object.entries(statusCounts).map(([status, count]) => ({
      name: formatStatus(status),
      value: count,
      color: STATUS_COLORS[status] || '#6b7280',
    }));
  };

  // Get pending approvals count (mock - in real app would aggregate across all docs)
  const getPendingApprovalsCount = (): number => {
    // In a real implementation, you'd need an endpoint that returns all pending approvals
    // For now, we'll use the documents requiring approval as a proxy
    if (!allDocumentsData?.documents) return 0;

    return allDocumentsData.documents.filter(
      (doc) => doc.requires_approval && doc.status === 'under_review'
    ).length;
  };

  // Format status for display
  const formatStatus = (status: string): string => {
    return status
      .split('_')
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  // Format date for display
  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;

    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  // Get icon for document type
  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'policy':
        return <FileCheck className="h-4 w-4" />;
      case 'procedure':
        return <FileText className="h-4 w-4" />;
      case 'plan':
        return <FileText className="h-4 w-4" />;
      default:
        return <File className="h-4 w-4" />;
    }
  };

  // Get status badge color
  const getStatusBadgeColor = (status: string): string => {
    switch (status) {
      case 'published':
        return 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400';
      case 'approved':
        return 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400';
      case 'under_review':
        return 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400';
      case 'draft':
        return 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-400';
      case 'archived':
        return 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-500';
      case 'obsolete':
        return 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400';
      default:
        return 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-400';
    }
  };

  const statusData = getStatusDistribution();
  const recentDocuments = documentsData?.documents || [];
  const pendingApprovalsCount = getPendingApprovalsCount();
  const totalDocuments = allDocumentsData?.total || 0;

  return (
    <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-2">
      {/* Recent Documents Widget */}
      <div className="rounded-xl border bg-card p-6 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-lg bg-blue-500/10 flex items-center justify-center">
              <FileText className="h-5 w-5 text-blue-600" />
            </div>
            <div>
              <h3 className="font-semibold text-lg">Recent Documents</h3>
              <p className="text-sm text-muted-foreground">Last 10 updated</p>
            </div>
          </div>
          <Link
            href="/documents"
            className="text-sm text-primary hover:underline font-medium"
          >
            View all →
          </Link>
        </div>

        <div className="space-y-2">
          {isLoadingDocuments ? (
            // Loading skeletons
            Array.from({ length: 5 }).map((_, i) => (
              <div
                key={i}
                className="flex items-center gap-3 p-3 rounded-lg border animate-pulse"
              >
                <div className="h-8 w-8 rounded bg-muted" />
                <div className="flex-1 space-y-2">
                  <div className="h-4 bg-muted rounded w-3/4" />
                  <div className="h-3 bg-muted rounded w-1/2" />
                </div>
              </div>
            ))
          ) : documentsError ? (
            <div className="flex items-center gap-2 p-4 rounded-lg bg-red-50 dark:bg-red-900/10 text-red-600">
              <AlertCircle className="h-5 w-5" />
              <span className="text-sm">Failed to load documents</span>
            </div>
          ) : recentDocuments.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <FileText className="h-12 w-12 mx-auto mb-3 opacity-30" />
              <p className="text-sm">No documents yet</p>
              <p className="text-xs mt-1">Upload your first document to get started</p>
            </div>
          ) : (
            recentDocuments.slice(0, 5).map((doc) => (
              <Link
                key={doc.document_id}
                href={`/documents/${doc.document_id}`}
                className="flex items-center gap-3 p-3 rounded-lg border hover:bg-accent transition-colors group"
              >
                <div className="h-8 w-8 rounded bg-muted flex items-center justify-center text-muted-foreground group-hover:text-primary transition-colors">
                  {getTypeIcon(doc.document_type)}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-sm truncate group-hover:text-primary transition-colors">
                    {doc.title}
                  </p>
                  <div className="flex items-center gap-2 mt-1">
                    <span className={`text-xs px-2 py-0.5 rounded-full ${getStatusBadgeColor(doc.status)}`}>
                      {formatStatus(doc.status)}
                    </span>
                    <span className="text-xs text-muted-foreground">
                      {formatDate(doc.updated_at)}
                    </span>
                  </div>
                </div>
              </Link>
            ))
          )}
        </div>

        {!isLoadingDocuments && recentDocuments.length > 5 && (
          <div className="mt-4 pt-4 border-t">
            <Link
              href="/documents"
              className="text-sm text-primary hover:underline font-medium flex items-center gap-1"
            >
              View {recentDocuments.length - 5} more documents →
            </Link>
          </div>
        )}
      </div>

      {/* Pending Approvals Widget */}
      <div className="rounded-xl border bg-card p-6 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-lg bg-amber-500/10 flex items-center justify-center">
              <Clock className="h-5 w-5 text-amber-600" />
            </div>
            <div>
              <h3 className="font-semibold text-lg">Pending Approvals</h3>
              <p className="text-sm text-muted-foreground">Awaiting review</p>
            </div>
          </div>
        </div>

        <div className="space-y-4">
          <div className="flex items-center justify-between p-4 rounded-lg bg-amber-50 dark:bg-amber-900/10 border border-amber-200 dark:border-amber-800">
            <div className="flex items-center gap-3">
              <div className="h-12 w-12 rounded-lg bg-amber-500/20 flex items-center justify-center">
                <Clock className="h-6 w-6 text-amber-600" />
              </div>
              <div>
                <p className="text-3xl font-bold text-amber-600">
                  {isLoadingAllDocuments ? '...' : pendingApprovalsCount}
                </p>
                <p className="text-sm text-muted-foreground">Documents awaiting approval</p>
              </div>
            </div>
          </div>

          {!isLoadingAllDocuments && pendingApprovalsCount > 0 && (
            <div className="space-y-2">
              <p className="text-sm font-medium text-muted-foreground">Recent pending:</p>
              {allDocumentsData?.documents
                .filter((doc) => doc.requires_approval && doc.status === 'under_review')
                .slice(0, 3)
                .map((doc) => (
                  <Link
                    key={doc.document_id}
                    href={`/documents/${doc.document_id}`}
                    className="flex items-center gap-3 p-3 rounded-lg border hover:bg-accent transition-colors group"
                  >
                    <div className="h-8 w-8 rounded bg-amber-100 dark:bg-amber-900/20 flex items-center justify-center">
                      <Clock className="h-4 w-4 text-amber-600" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-sm truncate group-hover:text-primary transition-colors">
                        {doc.title}
                      </p>
                      <p className="text-xs text-muted-foreground truncate">
                        {formatStatus(doc.document_type)}
                      </p>
                    </div>
                  </Link>
                ))}
            </div>
          )}

          {!isLoadingAllDocuments && pendingApprovalsCount === 0 && (
            <div className="text-center py-6 text-muted-foreground">
              <CheckCircle className="h-10 w-10 mx-auto mb-2 opacity-30" />
              <p className="text-sm">All documents reviewed</p>
              <p className="text-xs mt-1">No pending approvals</p>
            </div>
          )}

          <div className="pt-4 border-t">
            <Link
              href="/documents?filter=under_review"
              className="text-sm text-primary hover:underline font-medium flex items-center gap-1"
            >
              View all pending approvals →
            </Link>
          </div>
        </div>
      </div>

      {/* Document Status Chart Widget */}
      <div className="rounded-xl border bg-card p-6 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-lg bg-purple-500/10 flex items-center justify-center">
              <TrendingUp className="h-5 w-5 text-purple-600" />
            </div>
            <div>
              <h3 className="font-semibold text-lg">Document Status</h3>
              <p className="text-sm text-muted-foreground">
                {isLoadingAllDocuments ? 'Loading...' : `${totalDocuments} total documents`}
              </p>
            </div>
          </div>
        </div>

        {isLoadingAllDocuments ? (
          <div className="h-64 flex items-center justify-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary" />
          </div>
        ) : statusData.length === 0 ? (
          <div className="h-64 flex items-center justify-center text-muted-foreground">
            <div className="text-center">
              <FileText className="h-12 w-12 mx-auto mb-3 opacity-30" />
              <p className="text-sm">No documents to display</p>
            </div>
          </div>
        ) : (
          <>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={statusData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={(props: PieLabelRenderProps) => {
                      const percent = Number(props.percent || 0);
                      const name = (props.payload as StatusData)?.name || '';
                      return `${name} ${(percent * 100).toFixed(0)}%`;
                    }}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {statusData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'rgba(255, 255, 255, 0.95)',
                      border: '1px solid #e5e7eb',
                      borderRadius: '8px',
                      boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>

            <div className="mt-4 grid grid-cols-2 gap-2">
              {statusData.map((item, index) => (
                <div
                  key={index}
                  className="flex items-center gap-2 p-2 rounded-lg hover:bg-accent transition-colors"
                >
                  <div
                    className="h-3 w-3 rounded-full flex-shrink-0"
                    style={{ backgroundColor: item.color }}
                  />
                  <div className="flex-1 min-w-0">
                    <p className="text-xs font-medium truncate">{item.name}</p>
                    <p className="text-xs text-muted-foreground">{item.value} docs</p>
                  </div>
                </div>
              ))}
            </div>
          </>
        )}
      </div>

      {/* Quick Actions Widget */}
      <div className="rounded-xl border bg-card p-6 shadow-sm">
        <div className="flex items-center gap-3 mb-4">
          <div className="h-10 w-10 rounded-lg bg-green-500/10 flex items-center justify-center">
            <Zap className="h-5 w-5 text-green-600" />
          </div>
          <div>
            <h3 className="font-semibold text-lg">Quick Actions</h3>
            <p className="text-sm text-muted-foreground">Common tasks</p>
          </div>
        </div>

        <div className="space-y-3">
          <button
            onClick={() => router.push('/documents/new?action=upload')}
            className="w-full flex items-center gap-3 p-4 rounded-lg border border-dashed border-muted-foreground/30 hover:border-primary hover:bg-primary/5 transition-all group"
          >
            <div className="h-10 w-10 rounded-lg bg-blue-500/10 flex items-center justify-center group-hover:bg-blue-500/20 transition-colors">
              <Upload className="h-5 w-5 text-blue-600" />
            </div>
            <div className="text-left">
              <p className="font-medium group-hover:text-primary transition-colors">
                Upload Document
              </p>
              <p className="text-sm text-muted-foreground">
                Upload new file to system
              </p>
            </div>
          </button>

          <button
            onClick={() => router.push('/documents/new')}
            className="w-full flex items-center gap-3 p-4 rounded-lg border border-dashed border-muted-foreground/30 hover:border-primary hover:bg-primary/5 transition-all group"
          >
            <div className="h-10 w-10 rounded-lg bg-green-500/10 flex items-center justify-center group-hover:bg-green-500/20 transition-colors">
              <FilePlus className="h-5 w-5 text-green-600" />
            </div>
            <div className="text-left">
              <p className="font-medium group-hover:text-primary transition-colors">
                Create Document
              </p>
              <p className="text-sm text-muted-foreground">
                Start from scratch or template
              </p>
            </div>
          </button>

          <button
            onClick={() => router.push('/documents?focus=search')}
            className="w-full flex items-center gap-3 p-4 rounded-lg border border-dashed border-muted-foreground/30 hover:border-primary hover:bg-primary/5 transition-all group"
          >
            <div className="h-10 w-10 rounded-lg bg-purple-500/10 flex items-center justify-center group-hover:bg-purple-500/20 transition-colors">
              <Search className="h-5 w-5 text-purple-600" />
            </div>
            <div className="text-left">
              <p className="font-medium group-hover:text-primary transition-colors">
                Search Documents
              </p>
              <p className="text-sm text-muted-foreground">
                Find documents quickly
              </p>
            </div>
          </button>
        </div>

        <div className="mt-4 pt-4 border-t">
          <Link
            href="/documents"
            className="text-sm text-primary hover:underline font-medium flex items-center gap-1"
          >
            Go to Documents module →
          </Link>
        </div>
      </div>
    </div>
  );
}

// Missing import fix
const Zap = ({ className }: { className?: string }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    className={className}
  >
    <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
  </svg>
);
