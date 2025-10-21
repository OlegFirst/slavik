'use client';

/**
 * Document Retention Policies Management Page
 * Admin page for managing document retention policies
 * Week 4 - Documents Module - Advanced Pages
 */

import { useState, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import { format } from 'date-fns';
import {
  Shield,
  Plus,
  Edit,
  Trash2,
  Search,
  Filter,
  Archive,
  Clock,
  FileText,
  AlertCircle,
  CheckCircle,
  XCircle,
  Calendar,
  MoreVertical,
  Download,
  Upload,
  RefreshCw,
  BarChart3,
  Play,
  Pause,
} from 'lucide-react';
import toast from 'react-hot-toast';

// Hooks
import {
  useRetentionPolicies,
  useCreateRetentionPolicy,
  formatRetentionPeriod,
  getRetentionStatusLabel,
} from '@/hooks/documents';

// Types
import type { RetentionPolicy, DocumentType } from '@/types/documents';

// ==================== TYPES ====================

interface PageProps {}

type StatusFilter = 'all' | 'active' | 'inactive';

interface PolicyFormData {
  policy_name: string;
  description: string;
  document_type: DocumentType | null;
  department: string;
  retention_years: number;
  is_permanent: boolean;
  archive_after_days: number | null;
  destroy_after_days: number | null;
  require_review_before_destruction: boolean;
  is_active: boolean;
}

// ==================== HELPER FUNCTIONS ====================

function getDocumentTypeLabel(type: DocumentType | null): string {
  if (!type) return 'All Types';
  return type
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

function getPolicyStatusColor(isActive: boolean): string {
  return isActive
    ? 'bg-green-100 text-green-700 border-green-300'
    : 'bg-gray-100 text-gray-700 border-gray-300';
}

// ==================== SUB-COMPONENTS ====================

interface PolicyCardProps {
  policy: RetentionPolicy;
  onEdit: () => void;
  onDelete: () => void;
  onToggleActive: () => void;
  isSelected: boolean;
  onToggleSelect: () => void;
}

function PolicyCard({ policy, onEdit, onDelete, onToggleActive, isSelected, onToggleSelect }: PolicyCardProps) {
  const [showMenu, setShowMenu] = useState(false);

  return (
    <div
      className={`bg-white rounded-lg border p-4 transition-all ${
        isSelected ? 'ring-2 ring-orange-500 border-orange-500' : 'border-gray-200'
      }`}
    >
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-start gap-3 flex-1 min-w-0">
          <input
            type="checkbox"
            checked={isSelected}
            onChange={onToggleSelect}
            className="mt-1 h-4 w-4 rounded border-gray-300"
          />
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-2">
              <h3 className="text-lg font-semibold text-gray-900 truncate">{policy.policy_name}</h3>
              <span
                className={`px-2 py-1 text-xs font-medium rounded-full border ${getPolicyStatusColor(
                  policy.is_active
                )}`}
              >
                {policy.is_active ? 'Active' : 'Inactive'}
              </span>
            </div>

            {policy.description && (
              <p className="text-sm text-gray-600 mb-3 line-clamp-2">{policy.description}</p>
            )}

            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-gray-500">Retention Period:</span>
                <span className="ml-2 font-medium text-gray-900">
                  {policy.is_permanent ? 'Permanent' : formatRetentionPeriod(policy.retention_years)}
                </span>
              </div>
              <div>
                <span className="text-gray-500">Document Type:</span>
                <span className="ml-2 font-medium text-gray-900">
                  {getDocumentTypeLabel(policy.document_type)}
                </span>
              </div>
              {policy.department && (
                <div>
                  <span className="text-gray-500">Department:</span>
                  <span className="ml-2 font-medium text-gray-900">{policy.department}</span>
                </div>
              )}
              <div>
                <span className="text-gray-500">Created:</span>
                <span className="ml-2 font-medium text-gray-900">
                  {format(new Date(policy.created_at), 'MMM d, yyyy')}
                </span>
              </div>
            </div>

            {(policy.archive_after_days || policy.destroy_after_days) && (
              <div className="mt-3 pt-3 border-t flex items-center gap-4 text-xs">
                {policy.archive_after_days && (
                  <div className="flex items-center gap-1 text-amber-700">
                    <Archive className="w-3 h-3" />
                    <span>Archive after {policy.archive_after_days} days</span>
                  </div>
                )}
                {policy.destroy_after_days && (
                  <div className="flex items-center gap-1 text-red-700">
                    <Trash2 className="w-3 h-3" />
                    <span>Destroy after {policy.destroy_after_days} days</span>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Actions Menu */}
        <div className="relative">
          <button
            onClick={() => setShowMenu(!showMenu)}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <MoreVertical className="w-5 h-5 text-gray-600" />
          </button>
          {showMenu && (
            <>
              <div className="fixed inset-0 z-10" onClick={() => setShowMenu(false)} />
              <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-xl border border-gray-200 py-2 z-20">
                <button
                  onClick={() => {
                    setShowMenu(false);
                    onEdit();
                  }}
                  className="w-full px-4 py-2 text-left hover:bg-gray-50 transition-colors flex items-center gap-2 text-gray-700"
                >
                  <Edit className="w-4 h-4" />
                  Edit Policy
                </button>
                <button
                  onClick={() => {
                    setShowMenu(false);
                    onToggleActive();
                  }}
                  className="w-full px-4 py-2 text-left hover:bg-gray-50 transition-colors flex items-center gap-2 text-gray-700"
                >
                  {policy.is_active ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                  {policy.is_active ? 'Deactivate' : 'Activate'}
                </button>
                <div className="my-2 border-t border-gray-200" />
                <button
                  onClick={() => {
                    setShowMenu(false);
                    onDelete();
                  }}
                  className="w-full px-4 py-2 text-left hover:bg-red-50 transition-colors flex items-center gap-2 text-red-600"
                >
                  <Trash2 className="w-4 h-4" />
                  Delete Policy
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

interface PolicyFormDialogProps {
  isOpen: boolean;
  onClose: () => void;
  policy?: RetentionPolicy | null;
  onSave: (data: PolicyFormData) => void;
}

function PolicyFormDialog({ isOpen, onClose, policy, onSave }: PolicyFormDialogProps) {
  const [formData, setFormData] = useState<PolicyFormData>({
    policy_name: policy?.policy_name || '',
    description: policy?.description || '',
    document_type: policy?.document_type || null,
    department: policy?.department || '',
    retention_years: policy?.retention_years || 365,
    is_permanent: policy?.is_permanent || false,
    archive_after_days: policy?.archive_after_days || null,
    destroy_after_days: policy?.destroy_after_days || null,
    require_review_before_destruction: policy?.require_review_before_destruction || false,
    is_active: policy?.is_active ?? true,
  });

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave(formData);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4">
          <h2 className="text-2xl font-bold text-gray-900">
            {policy ? 'Edit Retention Policy' : 'Create Retention Policy'}
          </h2>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Policy Name */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Policy Name <span className="text-red-600">*</span>
            </label>
            <input
              type="text"
              required
              value={formData.policy_name}
              onChange={e => setFormData({ ...formData, policy_name: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
              placeholder="e.g., Financial Records Retention"
            />
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
            <textarea
              value={formData.description}
              onChange={e => setFormData({ ...formData, description: e.target.value })}
              rows={3}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
              placeholder="Describe when this policy applies..."
            />
          </div>

          {/* Document Type */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Document Type</label>
            <select
              value={formData.document_type || ''}
              onChange={e =>
                setFormData({ ...formData, document_type: (e.target.value || null) as DocumentType | null })
              }
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
            >
              <option value="">All Types</option>
              <option value="policy">Policy</option>
              <option value="procedure">Procedure</option>
              <option value="plan">Plan</option>
              <option value="risk_assessment">Risk Assessment</option>
              <option value="bia">BIA</option>
              <option value="audit_report">Audit Report</option>
              <option value="contract">Contract</option>
              <option value="sop">SOP</option>
              <option value="report">Report</option>
            </select>
          </div>

          {/* Department */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Department</label>
            <input
              type="text"
              value={formData.department}
              onChange={e => setFormData({ ...formData, department: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
              placeholder="e.g., Finance, IT, HR"
            />
          </div>

          {/* Permanent Flag */}
          <div className="flex items-center">
            <input
              type="checkbox"
              id="is_permanent"
              checked={formData.is_permanent}
              onChange={e => setFormData({ ...formData, is_permanent: e.target.checked })}
              className="h-4 w-4 rounded border-gray-300"
            />
            <label htmlFor="is_permanent" className="ml-2 text-sm text-gray-700">
              Permanent Retention (Never Delete)
            </label>
          </div>

          {/* Retention Period */}
          {!formData.is_permanent && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Retention Period (Days) <span className="text-red-600">*</span>
              </label>
              <input
                type="number"
                required={!formData.is_permanent}
                min="1"
                value={formData.retention_years}
                onChange={e => setFormData({ ...formData, retention_years: parseInt(e.target.value, 10) })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
              />
              <p className="mt-1 text-sm text-gray-500">
                {formatRetentionPeriod(formData.retention_years)}
              </p>
            </div>
          )}

          {/* Archive After Days */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Auto-Archive After (Days)</label>
            <input
              type="number"
              min="0"
              value={formData.archive_after_days || ''}
              onChange={e =>
                setFormData({ ...formData, archive_after_days: e.target.value ? parseInt(e.target.value, 10) : null })
              }
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
              placeholder="Leave empty to disable"
            />
          </div>

          {/* Destroy After Days */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Auto-Delete After (Days)</label>
            <input
              type="number"
              min="0"
              value={formData.destroy_after_days || ''}
              onChange={e =>
                setFormData({
                  ...formData,
                  destroy_after_days: e.target.value ? parseInt(e.target.value, 10) : null,
                })
              }
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
              placeholder="Leave empty to disable"
            />
          </div>

          {/* Review Before Destruction */}
          <div className="flex items-center">
            <input
              type="checkbox"
              id="require_review"
              checked={formData.require_review_before_destruction}
              onChange={e => setFormData({ ...formData, require_review_before_destruction: e.target.checked })}
              className="h-4 w-4 rounded border-gray-300"
            />
            <label htmlFor="require_review" className="ml-2 text-sm text-gray-700">
              Require Review Before Destruction
            </label>
          </div>

          {/* Active Status */}
          <div className="flex items-center">
            <input
              type="checkbox"
              id="is_active"
              checked={formData.is_active}
              onChange={e => setFormData({ ...formData, is_active: e.target.checked })}
              className="h-4 w-4 rounded border-gray-300"
            />
            <label htmlFor="is_active" className="ml-2 text-sm text-gray-700">
              Policy Active
            </label>
          </div>

          {/* Actions */}
          <div className="flex items-center justify-end gap-3 pt-4 border-t">
            <button
              type="button"
              onClick={onClose}
              className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-6 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors"
            >
              {policy ? 'Update Policy' : 'Create Policy'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// ==================== MAIN COMPONENT ====================

export default function RetentionPoliciesPage({}: PageProps) {
  const router = useRouter();

  // TODO: Get actual tenant_id from auth context
  const tenantId = 'tenant-123';
  const isAdmin = true; // TODO: Get from auth context

  // State
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('all');
  const [selectedPolicies, setSelectedPolicies] = useState<Set<number>>(new Set());
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingPolicy, setEditingPolicy] = useState<RetentionPolicy | null>(null);

  // Fetch retention policies
  const { data: policies, isLoading, error, refetch } = useRetentionPolicies(tenantId);

  // Create policy mutation
  const createPolicy = useCreateRetentionPolicy({
    onSuccess: policy => {
      toast.success(`Policy "${policy.policy_name}" created successfully`);
      setIsFormOpen(false);
      setEditingPolicy(null);
    },
    onError: error => {
      toast.error(`Failed to create policy: ${error.message}`);
    },
  });

  // Filter and search policies
  const filteredPolicies = useMemo(() => {
    if (!policies) return [];

    let filtered = [...policies];

    // Status filter
    if (statusFilter === 'active') {
      filtered = filtered.filter(p => p.is_active);
    } else if (statusFilter === 'inactive') {
      filtered = filtered.filter(p => !p.is_active);
    }

    // Search filter
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(
        p =>
          p.policy_name.toLowerCase().includes(query) ||
          p.description?.toLowerCase().includes(query) ||
          p.department?.toLowerCase().includes(query)
      );
    }

    return filtered;
  }, [policies, statusFilter, searchQuery]);

  // Calculate stats
  const stats = useMemo(() => {
    if (!policies) return null;

    const activeCount = policies.filter(p => p.is_active).length;
    const inactiveCount = policies.filter(p => !p.is_active).length;

    return {
      total: policies.length,
      active: activeCount,
      inactive: inactiveCount,
    };
  }, [policies]);

  // Handlers
  const handleCreatePolicy = () => {
    setEditingPolicy(null);
    setIsFormOpen(true);
  };

  const handleEditPolicy = (policy: RetentionPolicy) => {
    setEditingPolicy(policy);
    setIsFormOpen(true);
  };

  const handleDeletePolicy = (policy: RetentionPolicy) => {
    if (confirm(`Delete policy "${policy.policy_name}"? This action cannot be undone.`)) {
      // TODO: Implement delete mutation
      toast.success(`Policy "${policy.policy_name}" deleted`);
    }
  };

  const handleToggleActive = (policy: RetentionPolicy) => {
    // TODO: Implement update mutation
    toast.success(`Policy "${policy.policy_name}" ${policy.is_active ? 'deactivated' : 'activated'}`);
  };

  const handleSavePolicy = (data: PolicyFormData) => {
    if (editingPolicy) {
      // TODO: Implement update mutation
      toast.success(`Policy "${data.policy_name}" updated`);
      setIsFormOpen(false);
      setEditingPolicy(null);
    } else {
      createPolicy.mutate({
        tenant_id: tenantId,
        name: data.policy_name,
        description: data.description,
        document_type: data.document_type ? [data.document_type] : [],
        retention_years: data.retention_years,
        action_after_retention: data.destroy_after_days ? 'DELETE' : data.archive_after_days ? 'ARCHIVE' : 'REVIEW',
        legal_hold_exempt: false,
      });
    }
  };

  const handleToggleSelect = (policyId: number) => {
    const newSelected = new Set(selectedPolicies);
    if (newSelected.has(policyId)) {
      newSelected.delete(policyId);
    } else {
      newSelected.add(policyId);
    }
    setSelectedPolicies(newSelected);
  };

  const handleBulkActivate = () => {
    if (selectedPolicies.size === 0) return;
    toast.success(`Activated ${selectedPolicies.size} policies`);
    setSelectedPolicies(new Set());
  };

  const handleBulkDeactivate = () => {
    if (selectedPolicies.size === 0) return;
    toast.success(`Deactivated ${selectedPolicies.size} policies`);
    setSelectedPolicies(new Set());
  };

  // Permission check
  if (!isAdmin) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-red-50 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="bg-white rounded-xl shadow-lg p-12 text-center">
            <XCircle className="w-16 h-16 text-red-600 mx-auto mb-4" />
            <h1 className="text-2xl font-bold text-gray-900 mb-2">Access Denied</h1>
            <p className="text-gray-600 mb-6">You do not have permission to access retention policies.</p>
            <button
              onClick={() => router.push('/documents')}
              className="px-6 py-3 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors"
            >
              Back to Documents
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Loading state
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-red-50 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="animate-pulse space-y-4">
            <div className="h-8 w-64 bg-gray-200 rounded" />
            <div className="h-32 bg-white rounded-xl" />
            <div className="grid grid-cols-3 gap-4">
              <div className="h-24 bg-white rounded-lg" />
              <div className="h-24 bg-white rounded-lg" />
              <div className="h-24 bg-white rounded-lg" />
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-red-50 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="bg-white rounded-xl shadow-lg p-12 text-center">
            <AlertCircle className="w-16 h-16 text-red-600 mx-auto mb-4" />
            <h1 className="text-2xl font-bold text-gray-900 mb-2">Error Loading Policies</h1>
            <p className="text-gray-600 mb-6">{(error as Error).message}</p>
            <button
              onClick={() => refetch()}
              className="px-6 py-3 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors inline-flex items-center gap-2"
            >
              <RefreshCw className="w-5 h-5" />
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-red-50 p-8">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Breadcrumbs */}
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <button onClick={() => router.push('/')} className="hover:text-orange-600 transition-colors">
            Home
          </button>
          <span>/</span>
          <button onClick={() => router.push('/documents')} className="hover:text-orange-600 transition-colors">
            Documents
          </button>
          <span>/</span>
          <span className="text-gray-900 font-medium">Retention Policies</span>
        </div>

        {/* Header */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex items-start justify-between gap-4">
            <div className="flex items-center gap-3">
              <Shield className="w-8 h-8 text-orange-600" />
              <div>
                <h1 className="text-3xl font-bold text-gray-900">Document Retention Policies</h1>
                <p className="text-gray-600 mt-1">Manage retention rules for document lifecycle</p>
              </div>
            </div>
            <button
              onClick={handleCreatePolicy}
              className="px-6 py-3 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors inline-flex items-center gap-2"
            >
              <Plus className="w-5 h-5" />
              Create Policy
            </button>
          </div>
        </div>

        {/* Stats Dashboard */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white border border-gray-200 rounded-lg p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Total Policies</p>
                  <p className="text-3xl font-bold text-gray-900">{stats.total}</p>
                </div>
                <BarChart3 className="w-10 h-10 text-blue-600" />
              </div>
            </div>
            <div className="bg-white border border-green-200 rounded-lg p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-green-600">Active Policies</p>
                  <p className="text-3xl font-bold text-green-900">{stats.active}</p>
                </div>
                <CheckCircle className="w-10 h-10 text-green-600" />
              </div>
            </div>
            <div className="bg-white border border-gray-200 rounded-lg p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Inactive Policies</p>
                  <p className="text-3xl font-bold text-gray-900">{stats.inactive}</p>
                </div>
                <Pause className="w-10 h-10 text-gray-600" />
              </div>
            </div>
          </div>
        )}

        {/* Filters and Search */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex flex-col md:flex-row gap-4">
            {/* Search */}
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search policies by name, description, or department..."
                  value={searchQuery}
                  onChange={e => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                />
              </div>
            </div>

            {/* Status Filter */}
            <div className="flex items-center gap-2">
              <Filter className="w-5 h-5 text-gray-500" />
              <select
                value={statusFilter}
                onChange={e => setStatusFilter(e.target.value as StatusFilter)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
              >
                <option value="all">All Policies</option>
                <option value="active">Active Only</option>
                <option value="inactive">Inactive Only</option>
              </select>
            </div>

            <button
              onClick={() => refetch()}
              className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors inline-flex items-center gap-2"
            >
              <RefreshCw className="w-5 h-5" />
              Refresh
            </button>
          </div>

          {/* Bulk Actions */}
          {selectedPolicies.size > 0 && (
            <div className="mt-4 pt-4 border-t flex items-center justify-between">
              <p className="text-sm text-gray-600">{selectedPolicies.size} policies selected</p>
              <div className="flex items-center gap-2">
                <button
                  onClick={handleBulkActivate}
                  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors inline-flex items-center gap-2 text-sm"
                >
                  <Play className="w-4 h-4" />
                  Activate
                </button>
                <button
                  onClick={handleBulkDeactivate}
                  className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors inline-flex items-center gap-2 text-sm"
                >
                  <Pause className="w-4 h-4" />
                  Deactivate
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Policies List */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          {filteredPolicies.length === 0 ? (
            <div className="text-center py-12">
              <Shield className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                {searchQuery || statusFilter !== 'all' ? 'No Matching Policies' : 'No Retention Policies'}
              </h3>
              <p className="text-gray-600 mb-6">
                {searchQuery || statusFilter !== 'all'
                  ? 'Try adjusting your filters or search query'
                  : 'Create your first retention policy to get started'}
              </p>
              {!searchQuery && statusFilter === 'all' && (
                <button
                  onClick={handleCreatePolicy}
                  className="px-6 py-3 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors inline-flex items-center gap-2"
                >
                  <Plus className="w-5 h-5" />
                  Create First Policy
                </button>
              )}
            </div>
          ) : (
            <div className="space-y-4">
              {filteredPolicies.map(policy => (
                <PolicyCard
                  key={policy.policy_id}
                  policy={policy}
                  onEdit={() => handleEditPolicy(policy)}
                  onDelete={() => handleDeletePolicy(policy)}
                  onToggleActive={() => handleToggleActive(policy)}
                  isSelected={selectedPolicies.has(policy.policy_id)}
                  onToggleSelect={() => handleToggleSelect(policy.policy_id)}
                />
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Policy Form Dialog */}
      <PolicyFormDialog
        isOpen={isFormOpen}
        onClose={() => {
          setIsFormOpen(false);
          setEditingPolicy(null);
        }}
        policy={editingPolicy}
        onSave={handleSavePolicy}
      />
    </div>
  );
}
