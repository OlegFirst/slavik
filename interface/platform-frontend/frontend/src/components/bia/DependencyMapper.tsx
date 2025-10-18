'use client';

/**
 * DependencyMapper Component
 * Interactive dependency graph with React Flow
 * AI-powered dependency discovery
 * Real data, no mocks
 */

import { useCallback, useState, useMemo } from 'react';
import ReactFlow, {
  Node,
  Edge,
  Controls,
  Background,
  MiniMap,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  MarkerType,
  BackgroundVariant,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { Sparkles, Plus, Trash2, AlertTriangle, Check, X, Loader2, CheckCircle2, XCircle } from 'lucide-react';
import type { Dependency } from '@/types/bia';
import { useAIDependencyDiscovery } from '@/hooks/bia';

interface DependencyMapperProps {
  dependencies: Dependency[];
  processName: string;
  onDependenciesChange: (dependencies: Dependency[]) => void;
  onAIDiscovery?: () => void;
  aiLoading?: boolean;
  readonly?: boolean;
}

const DEPENDENCY_TYPE_COLORS = {
  process: '#3b82f6',      // blue
  technology: '#8b5cf6',   // purple
  people: '#10b981',       // green
  facility: '#f59e0b',     // amber
  supplier: '#ef4444',     // red
};

const CRITICALITY_COLORS = {
  5: '#ef4444', // Critical - red
  4: '#f97316', // High - orange
  3: '#f59e0b', // Medium - amber
  2: '#3b82f6', // Low - blue
  1: '#6b7280', // Minimal - gray
};

export function DependencyMapper({
  dependencies,
  processName,
  onDependenciesChange,
  onAIDiscovery,
  aiLoading = false,
  readonly = false,
}: DependencyMapperProps) {
  const [selectedDep, setSelectedDep] = useState<Dependency | null>(null);
  const [showAddForm, setShowAddForm] = useState(false);
  const [showAIModal, setShowAIModal] = useState(false);
  const [aiResults, setAIResults] = useState<{
    dependency_map: string;
    risks: any;
    confidence: number;
    metadata: any;
  } | null>(null);

  // AI Dependency Discovery Hook
  const aiDiscovery = useAIDependencyDiscovery({
    onSuccess: (data) => {
      setAIResults(data);
      if (onAIDiscovery) {
        onAIDiscovery();
      }
    },
    onError: (error) => {
      console.error('AI Discovery failed:', error);
    },
  });

  // Convert dependencies to React Flow nodes and edges
  const { initialNodes, initialEdges } = useMemo(() => {
    const nodes: Node[] = [
      // Center node - current process
      {
        id: 'center',
        type: 'default',
        data: { label: processName },
        position: { x: 400, y: 300 },
        style: {
          background: '#f97316',
          color: 'white',
          border: '2px solid #ea580c',
          borderRadius: '8px',
          padding: '16px',
          fontSize: '14px',
          fontWeight: 'bold',
        },
      },
    ];

    const edges: Edge[] = [];

    // Add dependency nodes in a circle around center
    const radius = 250;
    const angleStep = (2 * Math.PI) / Math.max(dependencies.length, 1);

    dependencies.forEach((dep, index) => {
      const angle = index * angleStep;
      const x = 400 + radius * Math.cos(angle);
      const y = 300 + radius * Math.sin(angle);

      const color = DEPENDENCY_TYPE_COLORS[dep.type as keyof typeof DEPENDENCY_TYPE_COLORS] || '#6b7280';
      const criticalityColor = dep.criticality
        ? CRITICALITY_COLORS[dep.criticality as keyof typeof CRITICALITY_COLORS]
        : '#6b7280';

      nodes.push({
        id: `dep-${index}`,
        type: 'default',
        data: {
          label: `${dep.name}\n${dep.type}${dep.criticality ? ` (${dep.criticality}/5)` : ''}`,
        },
        position: { x, y },
        style: {
          background: color,
          color: 'white',
          border: `3px solid ${criticalityColor}`,
          borderRadius: '8px',
          padding: '12px',
          fontSize: '12px',
          minWidth: '120px',
          textAlign: 'center',
        },
      });

      edges.push({
        id: `edge-${index}`,
        source: 'center',
        target: `dep-${index}`,
        animated: dep.required,
        style: {
          stroke: dep.required ? '#ef4444' : '#6b7280',
          strokeWidth: dep.required ? 3 : 2,
        },
        markerEnd: {
          type: MarkerType.ArrowClosed,
          color: dep.required ? '#ef4444' : '#6b7280',
        },
        label: dep.required ? 'Required' : 'Optional',
        labelStyle: {
          fill: dep.required ? '#ef4444' : '#6b7280',
          fontWeight: dep.required ? 'bold' : 'normal',
        },
      });
    });

    return { initialNodes: nodes, initialEdges: edges };
  }, [dependencies, processName]);

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  // Add new dependency
  const handleAddDependency = (newDep: Dependency) => {
    const updated = [...dependencies, newDep];
    onDependenciesChange(updated);
    setShowAddForm(false);
  };

  // Remove dependency
  const handleRemoveDependency = (index: number) => {
    const updated = dependencies.filter((_, i) => i !== index);
    onDependenciesChange(updated);
    setSelectedDep(null);
  };

  // Handle AI Discovery
  const handleAIDiscovery = () => {
    setShowAIModal(true);
    setAIResults(null);
    aiDiscovery.mutate({
      name: processName,
      function: 'Discover dependencies for this process',
    });
  };

  // Parse AI dependency map and convert to Dependency[]
  const parseAIDependencies = (dependencyMap: string): Dependency[] => {
    try {
      // Try to parse as JSON first
      const parsed = JSON.parse(dependencyMap);

      if (Array.isArray(parsed)) {
        return parsed.map((item: any) => ({
          type: item.type || 'technology',
          name: item.name || item.dependency_name || '',
          criticality: item.criticality || item.priority || 3,
          required: item.required || item.is_critical || false,
        }));
      }

      // If it's an object with dependencies array
      if (parsed.dependencies && Array.isArray(parsed.dependencies)) {
        return parsed.dependencies.map((item: any) => ({
          type: item.type || 'technology',
          name: item.name || item.dependency_name || '',
          criticality: item.criticality || item.priority || 3,
          required: item.required || item.is_critical || false,
        }));
      }

      // If it's a structured object, extract dependencies
      const deps: Dependency[] = [];

      ['process', 'technology', 'people', 'facility', 'supplier'].forEach((type) => {
        if (parsed[type] || parsed[`${type}s`]) {
          const items = parsed[type] || parsed[`${type}s`];
          if (Array.isArray(items)) {
            items.forEach((item: any) => {
              deps.push({
                type,
                name: typeof item === 'string' ? item : (item.name || item.dependency_name || ''),
                criticality: typeof item === 'object' ? (item.criticality || item.priority || 3) : 3,
                required: typeof item === 'object' ? (item.required || item.is_critical || false) : false,
              });
            });
          }
        }
      });

      return deps;
    } catch (e) {
      // If JSON parsing fails, try to extract dependencies from text
      console.warn('Failed to parse as JSON, attempting text extraction:', e);

      const deps: Dependency[] = [];
      const lines = dependencyMap.split('\n');

      lines.forEach((line) => {
        // Look for patterns like "- Technology: Database Server (Critical)"
        const match = line.match(/[-*]\s*(\w+):\s*([^(]+)(?:\((.*?)\))?/i);
        if (match) {
          const [, type, name, metadata] = match;
          deps.push({
            type: type.toLowerCase(),
            name: name.trim(),
            criticality: metadata?.toLowerCase().includes('critical') ? 5 : 3,
            required: metadata?.toLowerCase().includes('required') || metadata?.toLowerCase().includes('critical') || false,
          });
        }
      });

      return deps;
    }
  };

  // Add AI-discovered dependencies to existing list
  const handleAddAIDependencies = () => {
    if (!aiResults) return;

    const newDeps = parseAIDependencies(aiResults.dependency_map);

    // Filter out duplicates (by name, case-insensitive)
    const existingNames = new Set(
      dependencies.map((d) => d.name.toLowerCase())
    );

    const uniqueNewDeps = newDeps.filter(
      (dep) => !existingNames.has(dep.name.toLowerCase())
    );

    if (uniqueNewDeps.length > 0) {
      const updated = [...dependencies, ...uniqueNewDeps];
      onDependenciesChange(updated);
    }

    setShowAIModal(false);
    setAIResults(null);
  };

  // Detect circular dependencies
  const hasCircularDependency = useMemo(() => {
    // TODO: Implement proper cycle detection algorithm
    return false;
  }, [dependencies]);

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">
            Dependency Mapping
          </h3>
          <p className="text-sm text-gray-600">
            {dependencies.length} dependencies • {dependencies.filter(d => d.required).length} critical
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handleAIDiscovery}
            disabled={aiDiscovery.isPending || readonly}
            className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {aiDiscovery.isPending ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Discovering...
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                AI Discover
              </>
            )}
          </button>
          {!readonly && (
            <button
              onClick={() => setShowAddForm(true)}
              className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors flex items-center gap-2"
            >
              <Plus className="w-4 h-4" />
              Add Dependency
            </button>
          )}
        </div>
      </div>

      {/* Warnings */}
      {hasCircularDependency && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-2">
          <AlertTriangle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div>
            <strong className="text-red-800">Circular Dependency Detected!</strong>
            <p className="text-red-700 text-sm mt-1">
              Process depends on itself through a chain of dependencies. This must be resolved.
            </p>
          </div>
        </div>
      )}

      {dependencies.filter(d => d.required).length < 2 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 flex items-start gap-2">
          <AlertTriangle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
          <div>
            <strong className="text-yellow-800">Critical processes should have at least 2 required dependencies</strong>
            <p className="text-yellow-700 text-sm mt-1">
              This is a best practice for ISO 22301 compliance.
            </p>
          </div>
        </div>
      )}

      {/* React Flow Graph */}
      <div className="bg-white rounded-xl border-2 border-gray-200 overflow-hidden" style={{ height: '600px' }}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={readonly ? undefined : onNodesChange}
          onEdgesChange={readonly ? undefined : onEdgesChange}
          onConnect={readonly ? undefined : onConnect}
          fitView
          attributionPosition="bottom-left"
        >
          <Background variant={BackgroundVariant.Dots} gap={12} size={1} />
          <Controls />
          <MiniMap
            nodeColor={(node) => {
              if (node.id === 'center') return '#f97316';
              return node.style?.background as string || '#6b7280';
            }}
          />
        </ReactFlow>
      </div>

      {/* Legend */}
      <div className="bg-gray-50 rounded-lg p-4">
        <h4 className="text-sm font-semibold text-gray-900 mb-3">Legend</h4>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          <div>
            <p className="text-xs font-medium text-gray-700 mb-2">Dependency Types</p>
            {Object.entries(DEPENDENCY_TYPE_COLORS).map(([type, color]) => (
              <div key={type} className="flex items-center gap-2 text-xs text-gray-600 mb-1">
                <div className="w-4 h-4 rounded" style={{ backgroundColor: color }} />
                <span className="capitalize">{type}</span>
              </div>
            ))}
          </div>
          <div>
            <p className="text-xs font-medium text-gray-700 mb-2">Criticality Levels</p>
            {Object.entries(CRITICALITY_COLORS).map(([level, color]) => (
              <div key={level} className="flex items-center gap-2 text-xs text-gray-600 mb-1">
                <div className="w-4 h-4 rounded border-2" style={{ borderColor: color }} />
                <span>{level}/5</span>
              </div>
            ))}
          </div>
          <div>
            <p className="text-xs font-medium text-gray-700 mb-2">Connection Types</p>
            <div className="flex items-center gap-2 text-xs text-gray-600 mb-1">
              <div className="w-8 h-0.5 bg-red-600" />
              <span>Required (animated)</span>
            </div>
            <div className="flex items-center gap-2 text-xs text-gray-600 mb-1">
              <div className="w-8 h-0.5 bg-gray-600" />
              <span>Optional</span>
            </div>
          </div>
        </div>
      </div>

      {/* Dependencies List */}
      <div className="bg-white rounded-xl border border-gray-200 p-4">
        <h4 className="text-sm font-semibold text-gray-900 mb-3">Dependencies List</h4>
        {dependencies.length === 0 ? (
          <p className="text-gray-500 text-sm text-center py-8">
            No dependencies added yet. Click "Add Dependency" or use "AI Discover" to get started.
          </p>
        ) : (
          <div className="space-y-2">
            {dependencies.map((dep, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-gray-900">{dep.name}</span>
                    {dep.required && (
                      <span className="px-2 py-0.5 bg-red-100 text-red-800 text-xs rounded-full font-medium">
                        Required
                      </span>
                    )}
                  </div>
                  <div className="flex items-center gap-3 mt-1 text-sm text-gray-600">
                    <span className="capitalize">{dep.type}</span>
                    {dep.criticality && (
                      <span>Criticality: {dep.criticality}/5</span>
                    )}
                  </div>
                </div>
                {!readonly && (
                  <button
                    onClick={() => handleRemoveDependency(index)}
                    className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Add Dependency Form Modal */}
      {showAddForm && (
        <DependencyForm
          onSubmit={handleAddDependency}
          onCancel={() => setShowAddForm(false)}
        />
      )}

      {/* AI Dependency Discovery Modal */}
      {showAIModal && (
        <AIDiscoveryModal
          isLoading={aiDiscovery.isPending}
          error={aiDiscovery.error}
          results={aiResults}
          onClose={() => {
            setShowAIModal(false);
            setAIResults(null);
            aiDiscovery.reset();
          }}
          onAdd={handleAddAIDependencies}
          onRetry={handleAIDiscovery}
          existingDependencies={dependencies}
          parseAIDependencies={parseAIDependencies}
        />
      )}

      {/* TODO: Add dependency editing */}
      {/* TODO: Add import from CSV */}
    </div>
  );
}

/**
 * Dependency Form Component
 */
interface DependencyFormProps {
  onSubmit: (dependency: Dependency) => void;
  onCancel: () => void;
  initialData?: Dependency;
}

function DependencyForm({ onSubmit, onCancel, initialData }: DependencyFormProps) {
  const [formData, setFormData] = useState<Dependency>(
    initialData || {
      type: 'technology',
      name: '',
      required: false,
      criticality: 3,
    }
  );

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (formData.name.trim()) {
      onSubmit(formData);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black bg-opacity-50" onClick={onCancel} />

      <div className="relative bg-white rounded-xl shadow-2xl max-w-md w-full p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Add Dependency
        </h3>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Name */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Dependency Name *
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
              placeholder="e.g., Electronic Health Records System"
              required
            />
          </div>

          {/* Type */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Type *
            </label>
            <select
              value={formData.type}
              onChange={(e) => setFormData({ ...formData, type: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
            >
              <option value="process">Process</option>
              <option value="technology">Technology</option>
              <option value="people">People</option>
              <option value="facility">Facility</option>
              <option value="supplier">Supplier</option>
            </select>
          </div>

          {/* Criticality */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Criticality: {formData.criticality}/5
            </label>
            <input
              type="range"
              min="1"
              max="5"
              value={formData.criticality || 3}
              onChange={(e) => setFormData({ ...formData, criticality: parseInt(e.target.value) })}
              className="w-full"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>Low</span>
              <span>Critical</span>
            </div>
          </div>

          {/* Required */}
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="required"
              checked={formData.required}
              onChange={(e) => setFormData({ ...formData, required: e.target.checked })}
              className="w-4 h-4 text-orange-600 rounded focus:ring-orange-500"
            />
            <label htmlFor="required" className="text-sm font-medium text-gray-700">
              This is a required dependency (critical)
            </label>
          </div>

          {/* Actions */}
          <div className="flex items-center justify-end gap-3 pt-4 border-t border-gray-200">
            <button
              type="button"
              onClick={onCancel}
              className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors flex items-center gap-2"
            >
              <Check className="w-4 h-4" />
              Add Dependency
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

/**
 * AI Discovery Modal Component
 */
interface AIDiscoveryModalProps {
  isLoading: boolean;
  error: Error | null;
  results: {
    dependency_map: string;
    risks: any;
    confidence: number;
    metadata: any;
  } | null;
  onClose: () => void;
  onAdd: () => void;
  onRetry: () => void;
  existingDependencies: Dependency[];
  parseAIDependencies: (dependencyMap: string) => Dependency[];
}

function AIDiscoveryModal({
  isLoading,
  error,
  results,
  onClose,
  onAdd,
  onRetry,
  existingDependencies,
  parseAIDependencies,
}: AIDiscoveryModalProps) {
  // Parse discovered dependencies
  const discoveredDeps = useMemo(() => {
    if (!results) return [];
    return parseAIDependencies(results.dependency_map);
  }, [results, parseAIDependencies]);

  // Filter out duplicates
  const newDependencies = useMemo(() => {
    const existingNames = new Set(
      existingDependencies.map((d) => d.name.toLowerCase())
    );
    return discoveredDeps.filter(
      (dep) => !existingNames.has(dep.name.toLowerCase())
    );
  }, [discoveredDeps, existingDependencies]);

  const duplicates = discoveredDeps.length - newDependencies.length;

  // Get confidence level label and color
  const getConfidenceLevel = (confidence: number) => {
    if (confidence >= 0.8) return { label: 'High', color: 'text-green-700', bg: 'bg-green-50' };
    if (confidence >= 0.6) return { label: 'Medium', color: 'text-yellow-700', bg: 'bg-yellow-50' };
    return { label: 'Low', color: 'text-red-700', bg: 'bg-red-50' };
  };

  const confidenceLevel = results ? getConfidenceLevel(results.confidence) : null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black bg-opacity-50" onClick={onClose} />

      <div className="relative bg-white rounded-xl shadow-2xl max-w-3xl w-full max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-purple-100 rounded-lg">
              <Sparkles className="w-6 h-6 text-purple-600" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">
                AI Dependency Discovery
              </h3>
              <p className="text-sm text-gray-600">
                Powered by BIA Specialist AI
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {/* Loading State */}
          {isLoading && (
            <div className="flex flex-col items-center justify-center py-12">
              <Loader2 className="w-12 h-12 text-purple-600 animate-spin mb-4" />
              <h4 className="text-lg font-semibold text-gray-900 mb-2">
                Analyzing Dependencies...
              </h4>
              <p className="text-sm text-gray-600 text-center max-w-md">
                Our AI is analyzing your process to identify critical dependencies.
                This may take a few moments.
              </p>
            </div>
          )}

          {/* Error State */}
          {error && !isLoading && (
            <div className="flex flex-col items-center justify-center py-12">
              <div className="p-3 bg-red-100 rounded-full mb-4">
                <XCircle className="w-12 h-12 text-red-600" />
              </div>
              <h4 className="text-lg font-semibold text-gray-900 mb-2">
                Discovery Failed
              </h4>
              <p className="text-sm text-gray-600 text-center max-w-md mb-6">
                {error.message || 'An error occurred while discovering dependencies. Please try again.'}
              </p>
              <button
                onClick={onRetry}
                className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors flex items-center gap-2"
              >
                <Sparkles className="w-4 h-4" />
                Try Again
              </button>
            </div>
          )}

          {/* Success State */}
          {results && !isLoading && !error && (
            <div className="space-y-6">
              {/* Confidence Score */}
              <div className={`p-4 rounded-lg border ${confidenceLevel?.bg} border-gray-200`}>
                <div className="flex items-center justify-between mb-2">
                  <h4 className="text-sm font-semibold text-gray-900">
                    AI Confidence Score
                  </h4>
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${confidenceLevel?.color} bg-white`}>
                    {confidenceLevel?.label} ({Math.round(results.confidence * 100)}%)
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-purple-600 h-2 rounded-full transition-all"
                    style={{ width: `${results.confidence * 100}%` }}
                  />
                </div>
              </div>

              {/* Discovered Dependencies */}
              <div>
                <div className="flex items-center justify-between mb-4">
                  <h4 className="text-sm font-semibold text-gray-900">
                    Discovered Dependencies
                  </h4>
                  <span className="text-sm text-gray-600">
                    {newDependencies.length} new
                    {duplicates > 0 && ` • ${duplicates} duplicate${duplicates > 1 ? 's' : ''} filtered`}
                  </span>
                </div>

                {newDependencies.length === 0 ? (
                  <div className="text-center py-8 bg-gray-50 rounded-lg">
                    <p className="text-gray-600">
                      {duplicates > 0
                        ? 'All discovered dependencies are already in your list.'
                        : 'No new dependencies discovered.'}
                    </p>
                  </div>
                ) : (
                  <div className="space-y-2 max-h-80 overflow-y-auto">
                    {newDependencies.map((dep, index) => (
                      <div
                        key={index}
                        className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-200"
                      >
                        <div className="flex-1">
                          <div className="flex items-center gap-2">
                            <span className="font-medium text-gray-900">{dep.name}</span>
                            {dep.required && (
                              <span className="px-2 py-0.5 bg-red-100 text-red-800 text-xs rounded-full font-medium">
                                Required
                              </span>
                            )}
                          </div>
                          <div className="flex items-center gap-3 mt-1 text-sm text-gray-600">
                            <span className="capitalize">{dep.type}</span>
                            {dep.criticality && (
                              <span>Criticality: {dep.criticality}/5</span>
                            )}
                          </div>
                        </div>
                        <CheckCircle2 className="w-5 h-5 text-green-600" />
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Risks (if available) */}
              {results.risks && Object.keys(results.risks).length > 0 && (
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                  <div className="flex items-start gap-2">
                    <AlertTriangle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
                    <div className="flex-1">
                      <h4 className="text-sm font-semibold text-yellow-900 mb-2">
                        Identified Risks
                      </h4>
                      <div className="text-sm text-yellow-800 space-y-1">
                        {Array.isArray(results.risks) ? (
                          results.risks.map((risk: any, idx: number) => (
                            <div key={idx}>
                              {typeof risk === 'string' ? risk : risk.description || risk.name}
                            </div>
                          ))
                        ) : (
                          <pre className="text-xs whitespace-pre-wrap">
                            {JSON.stringify(results.risks, null, 2)}
                          </pre>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Raw Response (collapsible, for debugging) */}
              <details className="bg-gray-50 rounded-lg p-4">
                <summary className="text-sm font-medium text-gray-700 cursor-pointer">
                  View Raw AI Response
                </summary>
                <pre className="mt-3 text-xs text-gray-600 whitespace-pre-wrap overflow-x-auto">
                  {results.dependency_map}
                </pre>
              </details>
            </div>
          )}
        </div>

        {/* Footer */}
        {results && !isLoading && !error && newDependencies.length > 0 && (
          <div className="flex items-center justify-end gap-3 p-6 border-t border-gray-200">
            <button
              onClick={onClose}
              className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={onAdd}
              className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors flex items-center gap-2"
            >
              <Check className="w-4 h-4" />
              Add {newDependencies.length} Dependenc{newDependencies.length === 1 ? 'y' : 'ies'}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
