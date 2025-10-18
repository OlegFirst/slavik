'use client';

/**
 * ProcessModal Component
 * Modal dialog for creating/editing BIA processes
 * Professional UI with backdrop and animations
 */

import { useEffect } from 'react';
import { X } from 'lucide-react';
import { ProcessForm } from './ProcessForm';
import type { BIAProcess } from '@/types/bia';

interface ProcessModalProps {
  isOpen: boolean;
  onClose: () => void;
  process?: BIAProcess; // For editing
  tenant_id: string;
  onSuccess?: (process: BIAProcess) => void;
}

export function ProcessModal({
  isOpen,
  onClose,
  process,
  tenant_id,
  onSuccess,
}: ProcessModalProps) {
  // Handle ESC key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isOpen, onClose]);

  // Prevent body scroll when modal is open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }

    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black bg-opacity-50 transition-opacity"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col animate-in fade-in slide-in-from-bottom-4 duration-300">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-2xl font-bold text-gray-900">
            {process ? 'Edit BIA Process' : 'Create New BIA Process'}
          </h2>
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Content - Scrollable */}
        <div className="flex-1 overflow-y-auto p-6">
          <ProcessForm
            process={process}
            tenant_id={tenant_id}
            onSuccess={(data) => {
              onSuccess?.(data);
              onClose();
            }}
            onCancel={onClose}
          />
        </div>
      </div>
    </div>
  );
}
