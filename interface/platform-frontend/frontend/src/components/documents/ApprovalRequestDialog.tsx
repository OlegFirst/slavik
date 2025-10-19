/**
 * ApprovalRequestDialog Component
 * Modal dialog to request approval from user/role
 * Week 4 - Documents Module - Agent 10
 */

'use client';

import { useState, useEffect } from 'react';
import { X, UserPlus, Clock, MessageSquare, Send, CheckCircle } from 'lucide-react';
import { useRequestApproval, useDocumentApprovals, getApprovalProgress } from '@/hooks/documents';
import toast from 'react-hot-toast';

export interface ApprovalRequestDialogProps {
  documentId: number;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  triggerButton?: React.ReactNode;
}

interface FormData {
  approverId: string;
  approverRole: string;
  slaHours: number | null;
  notes: string;
}

const SLA_PRESETS = [
  { label: '24 hours', value: 24 },
  { label: '48 hours', value: 48 },
  { label: '1 week', value: 168 },
  { label: '2 weeks', value: 336 },
];

export function ApprovalRequestDialog({
  documentId,
  open,
  onOpenChange,
  triggerButton,
}: ApprovalRequestDialogProps) {
  const [formData, setFormData] = useState<FormData>({
    approverId: '',
    approverRole: '',
    slaHours: 48,
    notes: '',
  });
  const [showPreview, setShowPreview] = useState(false);

  // Fetch existing approvals to show approval chain
  const { data: existingApprovals } = useDocumentApprovals(documentId, {
    enabled: open,
  });

  const approvalProgress = existingApprovals
    ? getApprovalProgress(existingApprovals)
    : null;

  // Request approval mutation
  const requestApproval = useRequestApproval(documentId, {
    onSuccess: () => {
      toast.success('Approval request sent successfully');
      onOpenChange(false);
      resetForm();
    },
    onError: (error) => {
      toast.error(`Failed to request approval: ${error.message}`);
    },
  });

  const resetForm = () => {
    setFormData({
      approverId: '',
      approverRole: '',
      slaHours: 48,
      notes: '',
    });
    setShowPreview(false);
  };

  useEffect(() => {
    if (!open) {
      resetForm();
    }
  }, [open]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.approverId.trim()) {
      toast.error('Please enter an approver ID');
      return;
    }

    if (!formData.approverRole.trim()) {
      toast.error('Please enter an approver role');
      return;
    }

    requestApproval.mutate({
      approver_id: formData.approverId,
      approver_role: formData.approverRole,
      sla_hours: formData.slaHours || undefined,
      notes: formData.notes || undefined,
    });
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      onOpenChange(false);
    }
  };

  if (!open && !triggerButton) return null;

  return (
    <>
      {/* Trigger Button */}
      {triggerButton && (
        <div onClick={() => onOpenChange(true)}>{triggerButton}</div>
      )}

      {/* Dialog Overlay */}
      {open && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
          onClick={() => onOpenChange(false)}
          onKeyDown={handleKeyDown}
          role="dialog"
          aria-modal="true"
          aria-labelledby="approval-dialog-title"
        >
          {/* Dialog Content */}
          <div
            className="relative w-full max-w-2xl max-h-[90vh] overflow-y-auto bg-white rounded-lg shadow-xl"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className="sticky top-0 z-10 bg-white border-b px-6 py-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <UserPlus className="h-5 w-5 text-blue-600" />
                  <h2 id="approval-dialog-title" className="text-lg font-semibold text-gray-900">
                    Request Approval
                  </h2>
                </div>
                <button
                  onClick={() => onOpenChange(false)}
                  className="rounded-md p-1 hover:bg-gray-100 transition-colors"
                  aria-label="Close dialog"
                >
                  <X className="h-5 w-5 text-gray-500" />
                </button>
              </div>

              {/* Approval Chain Info */}
              {approvalProgress && approvalProgress.total > 0 && (
                <div className="mt-3 p-3 bg-blue-50 rounded-md border border-blue-200">
                  <p className="text-sm font-medium text-blue-900">Current Approval Chain</p>
                  <div className="mt-1 flex items-center gap-4 text-sm text-blue-700">
                    <span>{approvalProgress.approved} approved</span>
                    <span>{approvalProgress.pending} pending</span>
                    <span>{approvalProgress.rejected} rejected</span>
                  </div>
                  <div className="mt-2 h-2 bg-blue-100 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-blue-600 transition-all"
                      style={{ width: `${approvalProgress.completionRate}%` }}
                    />
                  </div>
                </div>
              )}
            </div>

            {/* Form */}
            <form onSubmit={handleSubmit} className="p-6 space-y-5">
              {!showPreview ? (
                <>
                  {/* Approver ID */}
                  <div>
                    <label htmlFor="approverId" className="block text-sm font-medium text-gray-700 mb-1">
                      Approver ID <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      id="approverId"
                      value={formData.approverId}
                      onChange={(e) => setFormData({ ...formData, approverId: e.target.value })}
                      placeholder="user-123, manager-456, etc."
                      className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                      required
                    />
                    <p className="mt-1 text-xs text-gray-500">Enter the user ID of the approver</p>
                  </div>

                  {/* Approver Role */}
                  <div>
                    <label htmlFor="approverRole" className="block text-sm font-medium text-gray-700 mb-1">
                      Approver Role <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      id="approverRole"
                      value={formData.approverRole}
                      onChange={(e) => setFormData({ ...formData, approverRole: e.target.value })}
                      placeholder="Quality Manager, Technical Lead, etc."
                      className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                      required
                    />
                    <p className="mt-1 text-xs text-gray-500">Role or title of the approver</p>
                  </div>

                  {/* SLA Hours */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      SLA Deadline (Optional)
                    </label>
                    <div className="grid grid-cols-4 gap-2 mb-3">
                      {SLA_PRESETS.map((preset) => (
                        <button
                          key={preset.value}
                          type="button"
                          onClick={() => setFormData({ ...formData, slaHours: preset.value })}
                          className={`
                            px-3 py-2 text-sm rounded-md border transition-colors
                            ${
                              formData.slaHours === preset.value
                                ? 'bg-blue-600 text-white border-blue-600'
                                : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                            }
                          `}
                        >
                          {preset.label}
                        </button>
                      ))}
                    </div>
                    <div className="flex items-center gap-2">
                      <Clock className="h-4 w-4 text-gray-500" />
                      <input
                        type="number"
                        id="slaHours"
                        value={formData.slaHours || ''}
                        onChange={(e) => setFormData({ ...formData, slaHours: e.target.value ? parseInt(e.target.value) : null })}
                        placeholder="Custom hours"
                        min="1"
                        className="flex-1 rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                      <span className="text-sm text-gray-600">hours</span>
                    </div>
                  </div>

                  {/* Request Notes */}
                  <div>
                    <label htmlFor="notes" className="block text-sm font-medium text-gray-700 mb-1">
                      Request Message (Optional)
                    </label>
                    <div className="relative">
                      <MessageSquare className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                      <textarea
                        id="notes"
                        value={formData.notes}
                        onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                        placeholder="Add any additional context or instructions for the approver..."
                        rows={4}
                        className="w-full pl-10 rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                  </div>
                </>
              ) : (
                /* Preview */
                <div className="space-y-4">
                  <div className="p-4 bg-gray-50 rounded-lg border">
                    <h3 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
                      <CheckCircle className="h-4 w-4 text-blue-600" />
                      Review Approval Request
                    </h3>
                    <dl className="space-y-2 text-sm">
                      <div>
                        <dt className="font-medium text-gray-700">Approver ID:</dt>
                        <dd className="text-gray-900">{formData.approverId}</dd>
                      </div>
                      <div>
                        <dt className="font-medium text-gray-700">Approver Role:</dt>
                        <dd className="text-gray-900">{formData.approverRole}</dd>
                      </div>
                      {formData.slaHours && (
                        <div>
                          <dt className="font-medium text-gray-700">SLA Deadline:</dt>
                          <dd className="text-gray-900">{formData.slaHours} hours</dd>
                        </div>
                      )}
                      {formData.notes && (
                        <div>
                          <dt className="font-medium text-gray-700">Message:</dt>
                          <dd className="text-gray-900">{formData.notes}</dd>
                        </div>
                      )}
                    </dl>
                  </div>
                </div>
              )}

              {/* Footer Actions */}
              <div className="flex items-center justify-between pt-4 border-t">
                <button
                  type="button"
                  onClick={() => onOpenChange(false)}
                  className="px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-md transition-colors"
                >
                  Cancel
                </button>
                <div className="flex gap-2">
                  {showPreview ? (
                    <>
                      <button
                        type="button"
                        onClick={() => setShowPreview(false)}
                        className="px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-md transition-colors"
                      >
                        Back to Edit
                      </button>
                      <button
                        type="submit"
                        disabled={requestApproval.isPending}
                        className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        <Send className="h-4 w-4" />
                        {requestApproval.isPending ? 'Sending...' : 'Send Request'}
                      </button>
                    </>
                  ) : (
                    <button
                      type="button"
                      onClick={() => setShowPreview(true)}
                      className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md transition-colors"
                    >
                      Preview Request
                    </button>
                  )}
                </div>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
}
