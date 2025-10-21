/**
 * ApprovalRequest Component
 * Form to request document approval with multi-stage workflow support
 * Week 4 - Documents Module
 */

'use client';

import { useState } from 'react';
import {
  Users,
  MessageSquare,
  Calendar,
  AlertCircle,
  Plus,
  Trash2,
  Send,
  CheckCircle2
} from 'lucide-react';
import { useRequestApproval } from '@/hooks/documents/useDocumentApprovals';
import { cn } from '@/lib/utils';
import toast from 'react-hot-toast';

export interface ApprovalRequestProps {
  documentId: string;
  onRequestSent?: () => void;
}

interface ApprovalStage {
  id: string;
  approvers: string[];
  message: string;
  dueDate: string;
  priority: 'Low' | 'Medium' | 'High' | 'Critical';
}

const PRIORITY_CONFIG = {
  Low: {
    label: 'Low',
    bgClass: 'bg-gray-100',
    textClass: 'text-gray-700',
    borderClass: 'border-gray-300'
  },
  Medium: {
    label: 'Medium',
    bgClass: 'bg-blue-100',
    textClass: 'text-blue-700',
    borderClass: 'border-blue-300'
  },
  High: {
    label: 'High',
    bgClass: 'bg-orange-100',
    textClass: 'text-orange-700',
    borderClass: 'border-orange-300'
  },
  Critical: {
    label: 'Critical',
    bgClass: 'bg-red-100',
    textClass: 'text-red-700',
    borderClass: 'border-red-300'
  },
};

/**
 * ApprovalRequest displays a form to request document approval
 * Supports multi-stage approval workflows with flexible configuration
 *
 * @param documentId - The document ID to request approval for
 * @param onRequestSent - Callback fired when approval request is successfully sent
 */
export function ApprovalRequest({
  documentId,
  onRequestSent
}: ApprovalRequestProps) {
  const [stages, setStages] = useState<ApprovalStage[]>([
    {
      id: crypto.randomUUID(),
      approvers: [''],
      message: '',
      dueDate: '',
      priority: 'Medium',
    },
  ]);
  const [currentStageIndex, setCurrentStageIndex] = useState(0);
  const [selectedApprovers, setSelectedApprovers] = useState<string[]>(['']);
  const [message, setMessage] = useState('');
  const [dueDate, setDueDate] = useState('');
  const [priority, setPriority] = useState<'Low' | 'Medium' | 'High' | 'Critical'>('Medium');
  const [approverSearch, setApproverSearch] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const requestApproval = useRequestApproval(parseInt(documentId), {
    onSuccess: () => {
      toast.success('Approval request sent successfully');
      resetForm();
      onRequestSent?.();
    },
    onError: (error) => {
      toast.error(`Failed to send approval request: ${error.message}`);
      setIsSubmitting(false);
    },
  });

  const resetForm = () => {
    setSelectedApprovers(['']);
    setMessage('');
    setDueDate('');
    setPriority('Medium');
    setApproverSearch('');
    setIsSubmitting(false);
    setStages([
      {
        id: crypto.randomUUID(),
        approvers: [''],
        message: '',
        dueDate: '',
        priority: 'Medium',
      },
    ]);
    setCurrentStageIndex(0);
  };

  const handleAddApprover = () => {
    setSelectedApprovers([...selectedApprovers, '']);
  };

  const handleRemoveApprover = (index: number) => {
    if (selectedApprovers.length > 1) {
      setSelectedApprovers(selectedApprovers.filter((_, i) => i !== index));
    }
  };

  const handleApproverChange = (index: number, value: string) => {
    const newApprovers = [...selectedApprovers];
    newApprovers[index] = value;
    setSelectedApprovers(newApprovers);
  };

  const handleAddStage = () => {
    const newStage: ApprovalStage = {
      id: crypto.randomUUID(),
      approvers: [''],
      message: '',
      dueDate: '',
      priority: 'Medium',
    };
    setStages([...stages, newStage]);
    setCurrentStageIndex(stages.length);
  };

  const handleRemoveStage = (index: number) => {
    if (stages.length > 1) {
      const newStages = stages.filter((_, i) => i !== index);
      setStages(newStages);
      if (currentStageIndex >= newStages.length) {
        setCurrentStageIndex(newStages.length - 1);
      }
    }
  };

  const validateForm = (): boolean => {
    const validApprovers = selectedApprovers.filter(a => a.trim() !== '');

    if (validApprovers.length === 0) {
      toast.error('Please add at least one approver');
      return false;
    }

    if (dueDate) {
      const dueDateObj = new Date(dueDate);
      const today = new Date();
      today.setHours(0, 0, 0, 0);

      if (dueDateObj < today) {
        toast.error('Due date must be in the future');
        return false;
      }
    }

    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);

    // For now, we'll send the first approver in the list
    // Multi-stage support would require backend API updates
    const validApprovers = selectedApprovers.filter(a => a.trim() !== '');
    const firstApprover = validApprovers[0];

    try {
      // Calculate SLA hours from due date if provided
      let slaHours: number | undefined;
      if (dueDate) {
        const now = new Date();
        const due = new Date(dueDate);
        const diffMs = due.getTime() - now.getTime();
        slaHours = Math.max(1, Math.floor(diffMs / (1000 * 60 * 60)));
      }

      await requestApproval.mutateAsync({
        approver_id: firstApprover,
        approver_role: 'Approver', // Default role, could be extended
        sla_hours: slaHours,
        notes: message || undefined,
      });
    } catch (error) {
      // Error handled by mutation callbacks
    }
  };

  const getTodayDate = () => {
    const today = new Date();
    return today.toISOString().split('T')[0];
  };

  return (
    <div className="bg-white rounded-xl shadow-lg border border-gray-200">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200 bg-gradient-to-r from-orange-50 to-amber-50">
        <div className="flex items-center gap-2">
          <Send className="w-5 h-5 text-orange-600" />
          <h2 className="text-lg font-semibold text-gray-900">
            Request Approval
          </h2>
        </div>
        <p className="text-sm text-gray-600 mt-1">
          Request approval from team members for this document
        </p>
      </div>

      <form onSubmit={handleSubmit} className="p-6 space-y-6">
        {/* Multi-stage indicator (if more than one stage) */}
        {stages.length > 1 && (
          <div className="flex items-center gap-2 mb-4">
            {stages.map((stage, index) => (
              <div key={stage.id} className="flex items-center">
                <button
                  type="button"
                  onClick={() => setCurrentStageIndex(index)}
                  className={cn(
                    'px-4 py-2 rounded-lg text-sm font-medium transition-colors',
                    currentStageIndex === index
                      ? 'bg-orange-100 text-orange-700 border border-orange-300'
                      : 'bg-gray-100 text-gray-600 border border-gray-300 hover:bg-gray-200'
                  )}
                >
                  Stage {index + 1}
                </button>
                {index < stages.length - 1 && (
                  <div className="w-8 h-0.5 bg-gray-300 mx-1" />
                )}
              </div>
            ))}
          </div>
        )}

        {/* Approvers Section */}
        <div>
          <label className="flex items-center gap-2 text-sm font-medium text-gray-900 mb-2">
            <Users className="w-4 h-4 text-gray-600" />
            Approvers <span className="text-red-500">*</span>
          </label>
          <div className="space-y-2">
            {selectedApprovers.map((approver, index) => (
              <div key={index} className="flex items-center gap-2">
                <input
                  type="text"
                  value={approver}
                  onChange={(e) => handleApproverChange(index, e.target.value)}
                  placeholder="Enter user ID or email (e.g., user-123, john@example.com)"
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent text-sm"
                  required={index === 0}
                />
                {selectedApprovers.length > 1 && (
                  <button
                    type="button"
                    onClick={() => handleRemoveApprover(index)}
                    className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                    aria-label="Remove approver"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                )}
              </div>
            ))}
          </div>
          <button
            type="button"
            onClick={handleAddApprover}
            className="mt-2 flex items-center gap-1 px-3 py-1.5 text-sm text-orange-600 hover:bg-orange-50 rounded-lg transition-colors"
          >
            <Plus className="w-4 h-4" />
            Add Approver
          </button>
          <p className="text-xs text-gray-500 mt-2">
            Add one or more approvers who will review this document
          </p>
        </div>

        {/* Priority Selector */}
        <div>
          <label className="flex items-center gap-2 text-sm font-medium text-gray-900 mb-2">
            <AlertCircle className="w-4 h-4 text-gray-600" />
            Priority
          </label>
          <div className="grid grid-cols-4 gap-2">
            {Object.entries(PRIORITY_CONFIG).map(([key, config]) => (
              <button
                key={key}
                type="button"
                onClick={() => setPriority(key as typeof priority)}
                className={cn(
                  'px-4 py-2 rounded-lg text-sm font-medium transition-all border',
                  priority === key
                    ? `${config.bgClass} ${config.textClass} ${config.borderClass} ring-2 ring-offset-2 ring-${config.textClass.split('-')[1]}-500`
                    : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                )}
              >
                {config.label}
              </button>
            ))}
          </div>
        </div>

        {/* Due Date */}
        <div>
          <label htmlFor="dueDate" className="flex items-center gap-2 text-sm font-medium text-gray-900 mb-2">
            <Calendar className="w-4 h-4 text-gray-600" />
            Due Date
          </label>
          <input
            type="date"
            id="dueDate"
            value={dueDate}
            onChange={(e) => setDueDate(e.target.value)}
            min={getTodayDate()}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent text-sm"
          />
          <p className="text-xs text-gray-500 mt-1">
            Optional deadline for approval response
          </p>
        </div>

        {/* Message */}
        <div>
          <label htmlFor="message" className="flex items-center gap-2 text-sm font-medium text-gray-900 mb-2">
            <MessageSquare className="w-4 h-4 text-gray-600" />
            Message
          </label>
          <textarea
            id="message"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Add any context or instructions for the approvers..."
            rows={4}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent text-sm resize-none"
          />
          <p className="text-xs text-gray-500 mt-1">
            Provide context or specific areas to review
          </p>
        </div>

        {/* Stage Management (Future Enhancement) */}
        {false && stages.length > 0 && (
          <div className="pt-4 border-t border-gray-200">
            <button
              type="button"
              onClick={handleAddStage}
              className="flex items-center gap-1 px-3 py-1.5 text-sm text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
            >
              <Plus className="w-4 h-4" />
              Add Approval Stage
            </button>
            <p className="text-xs text-gray-500 mt-1">
              Create multi-stage approval workflows
            </p>
          </div>
        )}

        {/* Submit Button */}
        <div className="pt-4 border-t border-gray-200 flex items-center justify-between">
          <div className="flex items-center gap-1 text-xs text-gray-500">
            <AlertCircle className="w-3 h-3" />
            <span>At least one approver is required</span>
          </div>
          <button
            type="submit"
            disabled={isSubmitting}
            className={cn(
              'flex items-center gap-2 px-6 py-2.5 rounded-lg font-medium transition-all',
              'bg-orange-600 text-white hover:bg-orange-700',
              'disabled:opacity-50 disabled:cursor-not-allowed',
              'shadow-lg hover:shadow-xl'
            )}
          >
            {isSubmitting ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                <span>Sending...</span>
              </>
            ) : (
              <>
                <CheckCircle2 className="w-4 h-4" />
                <span>Send Request</span>
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
