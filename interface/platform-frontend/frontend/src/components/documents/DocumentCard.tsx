/**
 * DocumentCard Component
 * Professional card display for document summary in list/grid views
 * Supports both grid and list layout modes with hover actions
 */

'use client';

import { Document, DocumentClassification } from '@/types/documents';
import { DocumentStatusBadge } from './DocumentStatusBadge';
import { DocumentTypeIcon } from './DocumentTypeIcon';
import { cn } from '@/lib/utils';
import {
  Calendar,
  User,
  Edit,
  Share2,
  Archive,
  FileText,
  Lock,
  Eye,
  CheckCircle,
  XCircle,
} from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

export interface DocumentCardProps {
  document: Document;
  layout?: 'grid' | 'list';
  onClick?: (document: Document) => void;
  onEdit?: (document: Document) => void;
  onShare?: (document: Document) => void;
  onArchive?: (document: Document) => void;
  showActions?: boolean;
  className?: string;
}

const CLASSIFICATION_CONFIG = {
  [DocumentClassification.PUBLIC]: {
    label: 'Public',
    colorClass: 'text-gray-700',
    bgClass: 'bg-gray-100',
    borderClass: 'border-gray-300',
    Icon: Eye,
  },
  [DocumentClassification.INTERNAL]: {
    label: 'Internal',
    colorClass: 'text-blue-700',
    bgClass: 'bg-blue-100',
    borderClass: 'border-blue-300',
    Icon: FileText,
  },
  [DocumentClassification.CONFIDENTIAL]: {
    label: 'Confidential',
    colorClass: 'text-orange-700',
    bgClass: 'bg-orange-100',
    borderClass: 'border-orange-300',
    Icon: Lock,
  },
  [DocumentClassification.RESTRICTED]: {
    label: 'Restricted',
    colorClass: 'text-red-700',
    bgClass: 'bg-red-100',
    borderClass: 'border-red-300',
    Icon: Lock,
  },
  [DocumentClassification.HIGHLY_RESTRICTED]: {
    label: 'Highly Restricted',
    colorClass: 'text-red-900',
    bgClass: 'bg-red-200',
    borderClass: 'border-red-400',
    Icon: Lock,
  },
};

/**
 * DocumentCard displays a document summary card with metadata and quick actions
 *
 * @param document - The Document object to display
 * @param layout - Card layout mode: 'grid' or 'list' (default: 'grid')
 * @param onClick - Handler for clicking the card
 * @param onEdit - Handler for edit action
 * @param onShare - Handler for share action
 * @param onArchive - Handler for archive action
 * @param showActions - Whether to show action buttons on hover (default: true)
 * @param className - Additional CSS classes
 */
export function DocumentCard({
  document,
  layout = 'grid',
  onClick,
  onEdit,
  onShare,
  onArchive,
  showActions = true,
  className,
}: DocumentCardProps) {
  const classificationConfig = CLASSIFICATION_CONFIG[document.classification];
  const ClassificationIcon = classificationConfig.Icon;

  const handleCardClick = () => {
    if (onClick) {
      onClick(document);
    }
  };

  const handleAction = (
    e: React.MouseEvent,
    action?: (document: Document) => void
  ) => {
    e.stopPropagation();
    if (action) {
      action(document);
    }
  };

  const isGridLayout = layout === 'grid';

  return (
    <div
      className={cn(
        'group bg-white rounded-xl border transition-all duration-200',
        'hover:shadow-xl hover:border-orange-300',
        onClick && 'cursor-pointer',
        isGridLayout
          ? 'p-6 shadow-lg'
          : 'p-4 shadow-md flex items-center gap-4',
        className
      )}
      onClick={handleCardClick}
      role="article"
      aria-label={`Document: ${document.title}`}
      tabIndex={onClick ? 0 : undefined}
      onKeyDown={(e) => {
        if (onClick && (e.key === 'Enter' || e.key === ' ')) {
          e.preventDefault();
          onClick(document);
        }
      }}
    >
      {/* Type Icon - Left side for list layout */}
      {!isGridLayout && (
        <div className="flex-shrink-0">
          <DocumentTypeIcon type={document.document_type} size="lg" />
        </div>
      )}

      {/* Main Content */}
      <div className={cn('flex-1', isGridLayout ? 'space-y-4' : 'space-y-2')}>
        {/* Header */}
        <div className="flex items-start justify-between gap-3">
          <div className="flex-1 min-w-0">
            {isGridLayout && (
              <div className="flex items-center gap-2 mb-2">
                <DocumentTypeIcon type={document.document_type} size="md" />
                <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">
                  {document.document_code}
                </span>
              </div>
            )}

            <h3
              className={cn(
                'font-semibold text-gray-900 line-clamp-2',
                isGridLayout ? 'text-lg' : 'text-base'
              )}
            >
              {document.title}
            </h3>

            {document.description && isGridLayout && (
              <p className="text-sm text-gray-600 mt-1 line-clamp-2">
                {document.description}
              </p>
            )}
          </div>

          {/* Quick Actions - Show on hover */}
          {showActions && (
            <div
              className={cn(
                'flex items-center gap-1 transition-opacity duration-200',
                isGridLayout
                  ? 'opacity-0 group-hover:opacity-100'
                  : 'opacity-0 group-hover:opacity-100 md:opacity-100'
              )}
            >
              {onEdit && (
                <button
                  onClick={(e) => handleAction(e, onEdit)}
                  className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                  title="Edit document"
                  aria-label="Edit document"
                >
                  <Edit className="w-4 h-4" />
                </button>
              )}
              {onShare && (
                <button
                  onClick={(e) => handleAction(e, onShare)}
                  className="p-2 text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                  title="Share document"
                  aria-label="Share document"
                >
                  <Share2 className="w-4 h-4" />
                </button>
              )}
              {onArchive && (
                <button
                  onClick={(e) => handleAction(e, onArchive)}
                  className="p-2 text-orange-600 hover:bg-orange-50 rounded-lg transition-colors"
                  title="Archive document"
                  aria-label="Archive document"
                >
                  <Archive className="w-4 h-4" />
                </button>
              )}
            </div>
          )}
        </div>

        {/* Badges Row */}
        <div className="flex items-center gap-2 flex-wrap">
          <DocumentStatusBadge status={document.status} size="sm" />

          {/* Classification Badge */}
          <span
            className={cn(
              'inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium border',
              classificationConfig.bgClass,
              classificationConfig.colorClass,
              classificationConfig.borderClass
            )}
            title={`Classification: ${classificationConfig.label}`}
          >
            <ClassificationIcon className="w-3 h-3" aria-hidden="true" />
            {classificationConfig.label}
          </span>

          {/* Version Badge */}
          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-slate-100 text-slate-700 border border-slate-300">
            v{document.version}
          </span>

          {/* Latest Badge */}
          {document.is_latest && (
            <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-700 border border-green-300">
              Latest
            </span>
          )}
        </div>

        {/* Metadata Row */}
        <div
          className={cn(
            'flex flex-wrap gap-4 text-sm text-gray-600',
            isGridLayout ? 'mt-4' : 'mt-2'
          )}
        >
          {/* Owner */}
          <div className="flex items-center gap-1.5" title={`Owner: ${document.owner_id}`}>
            <User className="w-4 h-4 text-gray-400" aria-hidden="true" />
            <span className="truncate max-w-[150px]">{document.owner_id}</span>
          </div>

          {/* Last Modified */}
          <div className="flex items-center gap-1.5" title={`Last modified: ${new Date(document.updated_at).toLocaleString()}`}>
            <Calendar className="w-4 h-4 text-gray-400" aria-hidden="true" />
            <span>
              {formatDistanceToNow(new Date(document.updated_at), {
                addSuffix: true,
              })}
            </span>
          </div>

          {/* Department */}
          {document.department && isGridLayout && (
            <div className="flex items-center gap-1.5">
              <span className="text-gray-500">•</span>
              <span className="truncate">{document.department}</span>
            </div>
          )}
        </div>

        {/* Approval Status Indicator */}
        {document.requires_approval && isGridLayout && (
          <div className="flex items-center gap-2 pt-3 border-t border-gray-100">
            {document.approved_at ? (
              <div className="flex items-center gap-1.5 text-sm text-green-700">
                <CheckCircle className="w-4 h-4" aria-hidden="true" />
                <span>
                  Approved{' '}
                  {formatDistanceToNow(new Date(document.approved_at), {
                    addSuffix: true,
                  })}
                </span>
              </div>
            ) : (
              <div className="flex items-center gap-1.5 text-sm text-amber-700">
                <XCircle className="w-4 h-4" aria-hidden="true" />
                <span>Pending approval</span>
              </div>
            )}
          </div>
        )}

        {/* Controlled Document Indicator */}
        {document.is_controlled && isGridLayout && (
          <div className="flex items-center gap-1.5 text-xs text-orange-700 bg-orange-50 px-3 py-1.5 rounded-lg border border-orange-200">
            <Lock className="w-3 h-3" aria-hidden="true" />
            <span>Controlled Document</span>
          </div>
        )}
      </div>
    </div>
  );
}

/**
 * Classification badge component (can be used standalone)
 */
export function ClassificationBadge({
  classification,
  size = 'sm',
}: {
  classification: DocumentClassification;
  size?: 'sm' | 'md';
}) {
  const config = CLASSIFICATION_CONFIG[classification];
  const Icon = config.Icon;

  const sizeClasses =
    size === 'sm'
      ? 'text-xs px-2 py-0.5'
      : 'text-sm px-3 py-1';

  return (
    <span
      className={cn(
        'inline-flex items-center gap-1 rounded-full font-medium border',
        config.bgClass,
        config.colorClass,
        config.borderClass,
        sizeClasses
      )}
      title={`Classification: ${config.label}`}
    >
      <Icon className={size === 'sm' ? 'w-3 h-3' : 'w-4 h-4'} aria-hidden="true" />
      {config.label}
    </span>
  );
}
