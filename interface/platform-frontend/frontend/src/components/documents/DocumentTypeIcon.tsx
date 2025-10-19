/**
 * DocumentTypeIcon Component
 * Icon display for document types with color coding and tooltips
 * Supports all 21 DocumentType enum values
 */

'use client';

import { DocumentType } from '@/types/documents';
import { cn } from '@/lib/utils';
import {
  FileText,
  FileCode,
  FileSpreadsheet,
  FileInput,
  ListChecks,
  BarChart,
  FileType,
  BookOpen,
  Shield,
  FileCheck,
  Book,
  FileSignature,
  Database,
  ScrollText,
  Archive,
  Award,
  Mail,
  Presentation,
  Users,
  File,
  AlertTriangle,
  Briefcase,
  ClipboardList,
  PhoneCall,
  MessageSquare,
  GraduationCap,
  FileStack,
} from 'lucide-react';
import { LucideIcon } from 'lucide-react';

export interface DocumentTypeIconProps {
  type: DocumentType;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
  showTooltip?: boolean;
  className?: string;
}

interface TypeConfig {
  label: string;
  description: string;
  Icon: LucideIcon;
  colorClass: string;
  bgClass: string;
}

const TYPE_CONFIG: Record<DocumentType, TypeConfig> = {
  [DocumentType.POLICY]: {
    label: 'Policy',
    description: 'Organizational policy document',
    Icon: FileText,
    colorClass: 'text-blue-600',
    bgClass: 'bg-blue-100',
  },
  [DocumentType.PROCEDURE]: {
    label: 'Procedure',
    description: 'Step-by-step procedure',
    Icon: FileCode,
    colorClass: 'text-purple-600',
    bgClass: 'bg-purple-100',
  },
  [DocumentType.PLAN]: {
    label: 'Plan',
    description: 'Strategic or operational plan',
    Icon: FileSpreadsheet,
    colorClass: 'text-green-600',
    bgClass: 'bg-green-100',
  },
  [DocumentType.FORM]: {
    label: 'Form',
    description: 'Data collection form',
    Icon: FileInput,
    colorClass: 'text-indigo-600',
    bgClass: 'bg-indigo-100',
  },
  [DocumentType.CHECKLIST]: {
    label: 'Checklist',
    description: 'Verification checklist',
    Icon: ListChecks,
    colorClass: 'text-teal-600',
    bgClass: 'bg-teal-100',
  },
  [DocumentType.REPORT]: {
    label: 'Report',
    description: 'Analysis or status report',
    Icon: BarChart,
    colorClass: 'text-orange-600',
    bgClass: 'bg-orange-100',
  },
  [DocumentType.TEMPLATE]: {
    label: 'Template',
    description: 'Reusable document template',
    Icon: FileType,
    colorClass: 'text-pink-600',
    bgClass: 'bg-pink-100',
  },
  [DocumentType.RISK_ASSESSMENT]: {
    label: 'Risk Assessment',
    description: 'Risk analysis document',
    Icon: AlertTriangle,
    colorClass: 'text-red-600',
    bgClass: 'bg-red-100',
  },
  [DocumentType.BIA]: {
    label: 'BIA',
    description: 'Business Impact Analysis',
    Icon: Briefcase,
    colorClass: 'text-amber-600',
    bgClass: 'bg-amber-100',
  },
  [DocumentType.EXERCISE_REPORT]: {
    label: 'Exercise Report',
    description: 'Exercise or drill report',
    Icon: ClipboardList,
    colorClass: 'text-cyan-600',
    bgClass: 'bg-cyan-100',
  },
  [DocumentType.AUDIT_REPORT]: {
    label: 'Audit Report',
    description: 'Audit findings and recommendations',
    Icon: FileCheck,
    colorClass: 'text-violet-600',
    bgClass: 'bg-violet-100',
  },
  [DocumentType.MANAGEMENT_REVIEW]: {
    label: 'Management Review',
    description: 'Management review meeting record',
    Icon: Users,
    colorClass: 'text-slate-600',
    bgClass: 'bg-slate-100',
  },
  [DocumentType.CONTACT_LIST]: {
    label: 'Contact List',
    description: 'Emergency or team contact list',
    Icon: PhoneCall,
    colorClass: 'text-emerald-600',
    bgClass: 'bg-emerald-100',
  },
  [DocumentType.COMMUNICATION]: {
    label: 'Communication',
    description: 'Communication plan or notice',
    Icon: MessageSquare,
    colorClass: 'text-sky-600',
    bgClass: 'bg-sky-100',
  },
  [DocumentType.TRAINING_MATERIAL]: {
    label: 'Training Material',
    description: 'Training guide or presentation',
    Icon: GraduationCap,
    colorClass: 'text-fuchsia-600',
    bgClass: 'bg-fuchsia-100',
  },
  [DocumentType.EVIDENCE]: {
    label: 'Evidence',
    description: 'Compliance evidence record',
    Icon: Archive,
    colorClass: 'text-lime-600',
    bgClass: 'bg-lime-100',
  },
  [DocumentType.CONTRACT]: {
    label: 'Contract',
    description: 'Legal contract or agreement',
    Icon: FileSignature,
    colorClass: 'text-rose-600',
    bgClass: 'bg-rose-100',
  },
  [DocumentType.SOP]: {
    label: 'SOP',
    description: 'Standard Operating Procedure',
    Icon: BookOpen,
    colorClass: 'text-blue-700',
    bgClass: 'bg-blue-100',
  },
  [DocumentType.PRESENTATION]: {
    label: 'Presentation',
    description: 'Slide deck or presentation',
    Icon: Presentation,
    colorClass: 'text-orange-500',
    bgClass: 'bg-orange-100',
  },
  [DocumentType.SPREADSHEET]: {
    label: 'Spreadsheet',
    description: 'Data spreadsheet or workbook',
    Icon: FileSpreadsheet,
    colorClass: 'text-green-700',
    bgClass: 'bg-green-100',
  },
  [DocumentType.OTHER]: {
    label: 'Other',
    description: 'Other document type',
    Icon: File,
    colorClass: 'text-gray-600',
    bgClass: 'bg-gray-100',
  },
};

const SIZE_CONFIG = {
  sm: {
    iconSize: 'w-4 h-4',
    textClass: 'text-xs',
    paddingClass: 'px-2 py-1',
    gapClass: 'gap-1',
  },
  md: {
    iconSize: 'w-5 h-5',
    textClass: 'text-sm',
    paddingClass: 'px-3 py-1.5',
    gapClass: 'gap-1.5',
  },
  lg: {
    iconSize: 'w-6 h-6',
    textClass: 'text-base',
    paddingClass: 'px-4 py-2',
    gapClass: 'gap-2',
  },
};

/**
 * DocumentTypeIcon displays an icon representing the document type
 *
 * @param type - The DocumentType enum value
 * @param size - Icon size variant (default: 'md')
 * @param showLabel - Whether to display the type label (default: false)
 * @param showTooltip - Whether to show tooltip on hover (default: true)
 * @param className - Additional CSS classes
 */
export function DocumentTypeIcon({
  type,
  size = 'md',
  showLabel = false,
  showTooltip = true,
  className,
}: DocumentTypeIconProps) {
  const config = TYPE_CONFIG[type];
  const sizeConfig = SIZE_CONFIG[size];
  const Icon = config.Icon;

  if (showLabel) {
    return (
      <div
        className={cn(
          'inline-flex items-center rounded-lg font-medium transition-colors duration-200',
          config.bgClass,
          config.colorClass,
          sizeConfig.paddingClass,
          sizeConfig.gapClass,
          className
        )}
        title={showTooltip ? config.description : undefined}
        role="img"
        aria-label={config.label}
      >
        <Icon className={sizeConfig.iconSize} aria-hidden="true" />
        <span className={sizeConfig.textClass}>{config.label}</span>
      </div>
    );
  }

  return (
    <div
      className={cn(
        'inline-flex items-center justify-center transition-colors duration-200',
        config.colorClass,
        className
      )}
      title={showTooltip ? config.description : undefined}
      role="img"
      aria-label={config.label}
    >
      <Icon className={sizeConfig.iconSize} aria-hidden="true" />
    </div>
  );
}

/**
 * Get document type configuration (useful for external components)
 */
export function getTypeConfig(type: DocumentType): TypeConfig {
  return TYPE_CONFIG[type];
}

/**
 * Get document type category for grouping
 */
export function getTypeCategory(type: DocumentType): string {
  const categories: Record<string, DocumentType[]> = {
    'Governance': [DocumentType.POLICY, DocumentType.PROCEDURE, DocumentType.SOP],
    'Planning': [DocumentType.PLAN, DocumentType.BIA, DocumentType.RISK_ASSESSMENT],
    'Reports': [DocumentType.REPORT, DocumentType.AUDIT_REPORT, DocumentType.EXERCISE_REPORT, DocumentType.MANAGEMENT_REVIEW],
    'Templates': [DocumentType.TEMPLATE, DocumentType.FORM, DocumentType.CHECKLIST],
    'Communication': [DocumentType.COMMUNICATION, DocumentType.CONTACT_LIST, DocumentType.PRESENTATION],
    'Training': [DocumentType.TRAINING_MATERIAL],
    'Evidence': [DocumentType.EVIDENCE, DocumentType.CONTRACT],
    'Data': [DocumentType.SPREADSHEET],
    'Other': [DocumentType.OTHER],
  };

  for (const [category, types] of Object.entries(categories)) {
    if (types.includes(type)) {
      return category;
    }
  }

  return 'Other';
}
