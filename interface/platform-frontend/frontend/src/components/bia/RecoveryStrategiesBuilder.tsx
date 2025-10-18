'use client';

/**
 * RecoveryStrategiesBuilder Component
 * Build and manage recovery strategies for BIA processes
 * AI-powered strategy suggestions
 * Cost estimation and priority ordering
 */

import { useState } from 'react';
import { Plus, Trash2, GripVertical, CheckCircle2, AlertTriangle, Sparkles, DollarSign, X, TrendingUp } from 'lucide-react';
import { useAIRecoveryStrategies } from '@/hooks/bia';

interface RecoveryStrategy {
  id?: string;
  name: string;
  description: string;
  type: 'manual_workaround' | 'alternate_location' | 'alternate_supplier' | 'backup_system' | 'staff_reallocation' | 'other';
  rto_capability_hours: number; // Can this strategy meet the RTO?
  resources_required: string[];
  estimated_cost?: number;
  priority: number; // 1-5
  implementation_steps?: string[];
  validation_requirements?: string[];
}

interface RecoveryStrategiesBuilderProps {
  strategies: RecoveryStrategy[];
  processRTO: number; // Target RTO for validation
  processName?: string; // For AI context
  dependencies?: any[]; // For AI context
  onStrategiesChange: (strategies: RecoveryStrategy[]) => void;
  onAISuggest?: () => void;
  aiLoading?: boolean;
  readonly?: boolean;
}

const STRATEGY_TYPES = [
  { value: 'manual_workaround', label: 'Manual Workaround', icon: '✍️' },
  { value: 'alternate_location', label: 'Alternate Location', icon: '📍' },
  { value: 'alternate_supplier', label: 'Alternate Supplier', icon: '🏢' },
  { value: 'backup_system', label: 'Backup System', icon: '💾' },
  { value: 'staff_reallocation', label: 'Staff Reallocation', icon: '👥' },
  { value: 'other', label: 'Other', icon: '⚙️' },
];

export function RecoveryStrategiesBuilder({
  strategies,
  processRTO,
  processName,
  dependencies,
  onStrategiesChange,
  onAISuggest,
  aiLoading = false,
  readonly = false,
}: RecoveryStrategiesBuilderProps) {
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingStrategy, setEditingStrategy] = useState<RecoveryStrategy | null>(null);
  const [showAISuggestions, setShowAISuggestions] = useState(false);
  const [aiSuggestions, setAISuggestions] = useState<any[]>([]);
  const [aiConfidence, setAIConfidence] = useState<number>(0);

  // AI Recovery Strategies Hook
  const aiRecoveryStrategies = useAIRecoveryStrategies({
    onSuccess: (data) => {
      setAISuggestions(data.strategies || []);
      setAIConfidence(data.confidence || 0);
      setShowAISuggestions(true);
    },
    onError: (error) => {
      console.error('AI Strategy Suggestion Error:', error);
      alert(`Failed to get AI suggestions: ${error.message}`);
    },
  });

  // Add new strategy
  const handleAddStrategy = (strategy: RecoveryStrategy) => {
    const newStrategy = {
      ...strategy,
      id: `strategy-${Date.now()}`,
    };
    onStrategiesChange([...strategies, newStrategy]);
    setShowAddForm(false);
  };

  // Update existing strategy
  const handleUpdateStrategy = (updatedStrategy: RecoveryStrategy) => {
    onStrategiesChange(
      strategies.map((s) => (s.id === updatedStrategy.id ? updatedStrategy : s))
    );
    setEditingStrategy(null);
  };

  // Remove strategy
  const handleRemoveStrategy = (id: string) => {
    onStrategiesChange(strategies.filter((s) => s.id !== id));
  };

  // Move strategy up/down (priority ordering)
  const handleMoveStrategy = (index: number, direction: 'up' | 'down') => {
    const newStrategies = [...strategies];
    const targetIndex = direction === 'up' ? index - 1 : index + 1;

    if (targetIndex >= 0 && targetIndex < newStrategies.length) {
      [newStrategies[index], newStrategies[targetIndex]] = [
        newStrategies[targetIndex],
        newStrategies[index],
      ];
      onStrategiesChange(newStrategies);
    }
  };

  // Handle AI Suggest
  const handleAISuggest = () => {
    if (!processName || processName.trim() === '') {
      alert('Please enter a process name first');
      return;
    }

    // Call the custom handler if provided (for backward compatibility)
    if (onAISuggest) {
      onAISuggest();
      return;
    }

    // Otherwise, use the built-in AI hook
    aiRecoveryStrategies.mutate({
      name: processName,
      rto_hours: processRTO,
      dependencies: dependencies || [],
    });
  };

  // Add AI-suggested strategy to the list
  const handleAddAISuggestion = (suggestion: any) => {
    const newStrategy: RecoveryStrategy = {
      id: `strategy-${Date.now()}`,
      name: suggestion.name || suggestion.strategy_name || 'AI Suggested Strategy',
      description: suggestion.description || suggestion.details || '',
      type: suggestion.type || 'other',
      rto_capability_hours: suggestion.rto_capability_hours || suggestion.rto_hours || processRTO,
      resources_required: suggestion.resources_required || suggestion.resources || [],
      estimated_cost: suggestion.estimated_cost || suggestion.cost,
      priority: suggestion.priority || 3,
      implementation_steps: suggestion.implementation_steps || suggestion.steps,
      validation_requirements: suggestion.validation_requirements || suggestion.validation,
    };

    // Check for duplicates
    const isDuplicate = strategies.some(
      (s) => s.name.toLowerCase() === newStrategy.name.toLowerCase()
    );

    if (isDuplicate) {
      if (!confirm(`A strategy named "${newStrategy.name}" already exists. Add anyway?`)) {
        return;
      }
    }

    onStrategiesChange([...strategies, newStrategy]);
  };

  // Add all AI suggestions
  const handleAddAllAISuggestions = () => {
    aiSuggestions.forEach((suggestion) => {
      handleAddAISuggestion(suggestion);
    });
    setShowAISuggestions(false);
  };

  // Check if strategies can meet RTO
  const canMeetRTO = strategies.some((s) => s.rto_capability_hours <= processRTO);
  const totalEstimatedCost = strategies.reduce((sum, s) => sum + (s.estimated_cost || 0), 0);

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Recovery Strategies</h3>
          <p className="text-sm text-gray-600">
            {strategies.length} strategies • Target RTO: {processRTO}h
            {totalEstimatedCost > 0 && ` • Est. Cost: $${totalEstimatedCost.toLocaleString()}`}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handleAISuggest}
            disabled={aiRecoveryStrategies.isPending || aiLoading || readonly}
            className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors flex items-center gap-2 disabled:opacity-50"
          >
            {(aiRecoveryStrategies.isPending || aiLoading) ? (
              <>
                <Sparkles className="w-4 h-4 animate-spin" />
                Suggesting...
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                AI Suggest
              </>
            )}
          </button>
          {!readonly && (
            <button
              onClick={() => setShowAddForm(true)}
              className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors flex items-center gap-2"
            >
              <Plus className="w-4 h-4" />
              Add Strategy
            </button>
          )}
        </div>
      </div>

      {/* Validation Alert */}
      {!canMeetRTO && strategies.length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-2">
          <AlertTriangle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div>
            <strong className="text-red-800">RTO Validation Failed!</strong>
            <p className="text-red-700 text-sm mt-1">
              None of your recovery strategies can meet the target RTO of {processRTO} hours.
              Add or modify strategies to meet this requirement.
            </p>
          </div>
        </div>
      )}

      {canMeetRTO && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 flex items-start gap-2">
          <CheckCircle2 className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
          <div>
            <strong className="text-green-800">RTO Requirements Met</strong>
            <p className="text-green-700 text-sm mt-1">
              At least one strategy can achieve the target RTO of {processRTO} hours.
            </p>
          </div>
        </div>
      )}

      {/* Strategies List */}
      {strategies.length === 0 ? (
        <div className="bg-gray-50 rounded-xl border-2 border-dashed border-gray-300 p-12 text-center">
          <p className="text-gray-600">
            No recovery strategies defined yet.
          </p>
          <p className="text-gray-500 text-sm mt-2">
            Click "Add Strategy" or use "AI Suggest" to get started.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {strategies.map((strategy, index) => {
            const strategyType = STRATEGY_TYPES.find((t) => t.value === strategy.type);
            const meetsRTO = strategy.rto_capability_hours <= processRTO;

            return (
              <div
                key={strategy.id}
                className={`bg-white rounded-xl border-2 p-4 transition-all ${
                  meetsRTO ? 'border-green-200' : 'border-gray-200'
                }`}
              >
                <div className="flex items-start gap-3">
                  {/* Drag Handle */}
                  {!readonly && (
                    <div className="flex flex-col gap-1 mt-1">
                      <button
                        onClick={() => handleMoveStrategy(index, 'up')}
                        disabled={index === 0}
                        className="p-1 text-gray-400 hover:text-gray-600 disabled:opacity-30"
                      >
                        <GripVertical className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleMoveStrategy(index, 'down')}
                        disabled={index === strategies.length - 1}
                        className="p-1 text-gray-400 hover:text-gray-600 disabled:opacity-30"
                      >
                        <GripVertical className="w-4 h-4" />
                      </button>
                    </div>
                  )}

                  {/* Content */}
                  <div className="flex-1">
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <span className="text-2xl">{strategyType?.icon}</span>
                        <div>
                          <h4 className="font-semibold text-gray-900">{strategy.name}</h4>
                          <p className="text-sm text-gray-600">{strategyType?.label}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        {meetsRTO && (
                          <div className="flex items-center" title="Meets RTO">
                            <CheckCircle2 className="w-5 h-5 text-green-600" />
                          </div>
                        )}
                        <span className="px-3 py-1 bg-blue-100 text-blue-800 text-xs rounded-full font-medium">
                          Priority {strategy.priority}/5
                        </span>
                      </div>
                    </div>

                    <p className="text-gray-700 text-sm mb-3">{strategy.description}</p>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                      <div>
                        <span className="text-gray-600">RTO Capability:</span>
                        <span className={`ml-2 font-semibold ${meetsRTO ? 'text-green-600' : 'text-red-600'}`}>
                          {strategy.rto_capability_hours}h
                        </span>
                      </div>
                      {strategy.estimated_cost && (
                        <div className="flex items-center gap-1">
                          <DollarSign className="w-4 h-4 text-gray-600" />
                          <span className="text-gray-600">Cost:</span>
                          <span className="ml-1 font-semibold text-gray-900">
                            ${strategy.estimated_cost.toLocaleString()}
                          </span>
                        </div>
                      )}
                      <div>
                        <span className="text-gray-600">Resources:</span>
                        <span className="ml-2 font-semibold text-gray-900">
                          {strategy.resources_required?.length || 0}
                        </span>
                      </div>
                    </div>

                    {strategy.resources_required && strategy.resources_required.length > 0 && (
                      <div className="mt-3">
                        <span className="text-xs font-medium text-gray-600">Required Resources:</span>
                        <div className="flex flex-wrap gap-2 mt-1">
                          {strategy.resources_required.map((resource, i) => (
                            <span
                              key={i}
                              className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded"
                            >
                              {resource}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Actions */}
                  {!readonly && (
                    <div className="flex flex-col gap-2">
                      <button
                        onClick={() => setEditingStrategy(strategy)}
                        className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                        title="Edit"
                      >
                        ✏️
                      </button>
                      <button
                        onClick={() => strategy.id && handleRemoveStrategy(strategy.id)}
                        className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                        title="Delete"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Add/Edit Strategy Form Modal */}
      {(showAddForm || editingStrategy) && (
        <StrategyForm
          initialData={editingStrategy || undefined}
          processRTO={processRTO}
          onSubmit={editingStrategy ? handleUpdateStrategy : handleAddStrategy}
          onCancel={() => {
            setShowAddForm(false);
            setEditingStrategy(null);
          }}
        />
      )}

      {/* AI Suggestions Modal */}
      {showAISuggestions && (
        <AISuggestionsModal
          suggestions={aiSuggestions}
          confidence={aiConfidence}
          processRTO={processRTO}
          onAddSuggestion={handleAddAISuggestion}
          onAddAll={handleAddAllAISuggestions}
          onClose={() => setShowAISuggestions(false)}
        />
      )}
    </div>
  );
}

/**
 * Strategy Form Component
 */
interface StrategyFormProps {
  initialData?: RecoveryStrategy;
  processRTO: number;
  onSubmit: (strategy: RecoveryStrategy) => void;
  onCancel: () => void;
}

function StrategyForm({ initialData, processRTO, onSubmit, onCancel }: StrategyFormProps) {
  const [formData, setFormData] = useState<RecoveryStrategy>(
    initialData || {
      name: '',
      description: '',
      type: 'manual_workaround',
      rto_capability_hours: processRTO,
      resources_required: [],
      priority: 3,
    }
  );

  const [resourceInput, setResourceInput] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (formData.name.trim() && formData.description.trim()) {
      onSubmit(formData);
    }
  };

  const handleAddResource = () => {
    if (resourceInput.trim()) {
      setFormData({
        ...formData,
        resources_required: [...formData.resources_required, resourceInput.trim()],
      });
      setResourceInput('');
    }
  };

  const handleRemoveResource = (index: number) => {
    setFormData({
      ...formData,
      resources_required: formData.resources_required.filter((_, i) => i !== index),
    });
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black bg-opacity-50" onClick={onCancel} />

      <div className="relative bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-white border-b border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900">
            {initialData ? 'Edit Recovery Strategy' : 'Add Recovery Strategy'}
          </h3>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {/* Name */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Strategy Name *
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
              placeholder="e.g., Manual Paper-Based Admission Process"
              required
            />
          </div>

          {/* Type */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Strategy Type *
            </label>
            <select
              value={formData.type}
              onChange={(e) => setFormData({ ...formData, type: e.target.value as any })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
            >
              {STRATEGY_TYPES.map((type) => (
                <option key={type.value} value={type.value}>
                  {type.icon} {type.label}
                </option>
              ))}
            </select>
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Description *
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              rows={3}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
              placeholder="Describe how this strategy works..."
              required
            />
          </div>

          {/* RTO Capability & Priority */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                RTO Capability (hours) *
              </label>
              <input
                type="number"
                min="0"
                step="0.5"
                value={formData.rto_capability_hours}
                onChange={(e) =>
                  setFormData({ ...formData, rto_capability_hours: parseFloat(e.target.value) })
                }
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                required
              />
              {formData.rto_capability_hours > processRTO && (
                <p className="text-red-600 text-xs mt-1">
                  ⚠️ Exceeds target RTO of {processRTO}h
                </p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Priority (1-5)
              </label>
              <input
                type="range"
                min="1"
                max="5"
                value={formData.priority}
                onChange={(e) => setFormData({ ...formData, priority: parseInt(e.target.value) })}
                className="w-full"
              />
              <div className="flex justify-between text-xs text-gray-500">
                <span>Low</span>
                <span className="font-semibold">{formData.priority}</span>
                <span>High</span>
              </div>
            </div>
          </div>

          {/* Estimated Cost */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Estimated Cost (optional)
            </label>
            <div className="relative">
              <span className="absolute left-3 top-2.5 text-gray-500">$</span>
              <input
                type="number"
                min="0"
                value={formData.estimated_cost || ''}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    estimated_cost: e.target.value ? parseFloat(e.target.value) : undefined,
                  })
                }
                className="w-full pl-8 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                placeholder="0"
              />
            </div>
          </div>

          {/* Resources Required */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Resources Required
            </label>
            <div className="flex gap-2 mb-2">
              <input
                type="text"
                value={resourceInput}
                onChange={(e) => setResourceInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddResource())}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                placeholder="e.g., Paper forms, Backup staff"
              />
              <button
                type="button"
                onClick={handleAddResource}
                className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
              >
                <Plus className="w-4 h-4" />
              </button>
            </div>
            {formData.resources_required.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {formData.resources_required.map((resource, i) => (
                  <span
                    key={i}
                    className="px-3 py-1 bg-gray-100 text-gray-700 text-sm rounded-full flex items-center gap-2"
                  >
                    {resource}
                    <button
                      type="button"
                      onClick={() => handleRemoveResource(i)}
                      className="text-red-600 hover:text-red-800"
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>
            )}
          </div>

          {/* Actions */}
          <div className="flex items-center justify-end gap-3 pt-4 border-t border-gray-200">
            <button
              type="button"
              onClick={onCancel}
              className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 flex items-center gap-2"
            >
              <CheckCircle2 className="w-4 h-4" />
              {initialData ? 'Update Strategy' : 'Add Strategy'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

/**
 * AI Suggestions Modal Component
 */
interface AISuggestionsModalProps {
  suggestions: any[];
  confidence: number;
  processRTO: number;
  onAddSuggestion: (suggestion: any) => void;
  onAddAll: () => void;
  onClose: () => void;
}

function AISuggestionsModal({
  suggestions,
  confidence,
  processRTO,
  onAddSuggestion,
  onAddAll,
  onClose,
}: AISuggestionsModalProps) {
  const getConfidenceColor = (conf: number) => {
    if (conf >= 0.8) return 'text-green-600 bg-green-100';
    if (conf >= 0.6) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const getConfidenceLabel = (conf: number) => {
    if (conf >= 0.8) return 'High Confidence';
    if (conf >= 0.6) return 'Medium Confidence';
    return 'Low Confidence';
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black bg-opacity-50" onClick={onClose} />

      <div className="relative bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b border-gray-200 p-6 z-10">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-xl font-semibold text-gray-900 flex items-center gap-2">
                <Sparkles className="w-6 h-6 text-purple-600" />
                AI Strategy Suggestions
              </h3>
              <p className="text-sm text-gray-600 mt-1">
                {suggestions.length} strategies suggested for {processRTO}h RTO
              </p>
            </div>
            <button
              onClick={onClose}
              className="p-2 text-gray-500 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Confidence Badge */}
          <div className="mt-4 flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-gray-600" />
            <span className="text-sm font-medium text-gray-700">AI Confidence:</span>
            <span className={`px-3 py-1 rounded-full text-sm font-semibold ${getConfidenceColor(confidence)}`}>
              {getConfidenceLabel(confidence)} ({(confidence * 100).toFixed(0)}%)
            </span>
          </div>
        </div>

        {/* Suggestions List */}
        <div className="p-6 space-y-4">
          {suggestions.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-600">No suggestions available.</p>
              <p className="text-gray-500 text-sm mt-2">
                The AI could not generate suitable strategies for this process.
              </p>
            </div>
          ) : (
            suggestions.map((suggestion, index) => {
              const strategyType = STRATEGY_TYPES.find(
                (t) => t.value === (suggestion.type || 'other')
              );
              const meetsRTO = (suggestion.rto_capability_hours || suggestion.rto_hours || processRTO) <= processRTO;

              return (
                <div
                  key={index}
                  className={`bg-white rounded-lg border-2 p-4 transition-all ${
                    meetsRTO ? 'border-green-200 bg-green-50/50' : 'border-gray-200'
                  }`}
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-start gap-3">
                      <span className="text-2xl">{strategyType?.icon}</span>
                      <div>
                        <h4 className="font-semibold text-gray-900">
                          {suggestion.name || suggestion.strategy_name || 'Unnamed Strategy'}
                        </h4>
                        <p className="text-sm text-gray-600">{strategyType?.label || 'Other'}</p>
                      </div>
                    </div>
                    {meetsRTO && (
                      <div className="flex items-center gap-1 text-green-600 text-sm font-medium">
                        <CheckCircle2 className="w-4 h-4" />
                        Meets RTO
                      </div>
                    )}
                  </div>

                  <p className="text-gray-700 text-sm mb-3">
                    {suggestion.description || suggestion.details || 'No description provided.'}
                  </p>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm mb-3">
                    <div>
                      <span className="text-gray-600">RTO Capability:</span>
                      <span className={`ml-2 font-semibold ${meetsRTO ? 'text-green-600' : 'text-red-600'}`}>
                        {suggestion.rto_capability_hours || suggestion.rto_hours || processRTO}h
                      </span>
                    </div>
                    {(suggestion.estimated_cost || suggestion.cost) && (
                      <div className="flex items-center gap-1">
                        <DollarSign className="w-4 h-4 text-gray-600" />
                        <span className="text-gray-600">Cost:</span>
                        <span className="ml-1 font-semibold text-gray-900">
                          ${(suggestion.estimated_cost || suggestion.cost).toLocaleString()}
                        </span>
                      </div>
                    )}
                    <div>
                      <span className="text-gray-600">Priority:</span>
                      <span className="ml-2 font-semibold text-blue-600">
                        {suggestion.priority || 3}/5
                      </span>
                    </div>
                    <div>
                      <span className="text-gray-600">Resources:</span>
                      <span className="ml-2 font-semibold text-gray-900">
                        {(suggestion.resources_required || suggestion.resources || []).length}
                      </span>
                    </div>
                  </div>

                  {(suggestion.resources_required || suggestion.resources)?.length > 0 && (
                    <div className="mb-3">
                      <span className="text-xs font-medium text-gray-600">Required Resources:</span>
                      <div className="flex flex-wrap gap-2 mt-1">
                        {(suggestion.resources_required || suggestion.resources).map((resource: string, i: number) => (
                          <span
                            key={i}
                            className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded"
                          >
                            {resource}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  <div className="flex items-center justify-end pt-3 border-t border-gray-200">
                    <button
                      onClick={() => {
                        onAddSuggestion(suggestion);
                        // Optional: Show success feedback
                      }}
                      className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors flex items-center gap-2"
                    >
                      <Plus className="w-4 h-4" />
                      Add This Strategy
                    </button>
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Footer Actions */}
        {suggestions.length > 0 && (
          <div className="sticky bottom-0 bg-gray-50 border-t border-gray-200 p-6 flex items-center justify-between">
            <p className="text-sm text-gray-600">
              Review and add suggested strategies to your recovery plan
            </p>
            <div className="flex items-center gap-3">
              <button
                onClick={onClose}
                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-white transition-colors"
              >
                Close
              </button>
              <button
                onClick={onAddAll}
                className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors flex items-center gap-2"
              >
                <CheckCircle2 className="w-4 h-4" />
                Add All Strategies
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
