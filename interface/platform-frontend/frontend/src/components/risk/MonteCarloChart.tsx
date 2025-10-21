/**
 * MonteCarloChart Component
 * Monte Carlo Probabilistic Risk Simulation with Histogram Visualization
 * Displays VaR, CVaR, distribution statistics, and interactive chart
 * Real API integration via useMonteCarlo and useRunMonteCarlo hooks
 * Week 5 - Risk Assessment Module - Round 3
 */

'use client';

import React, { useState } from 'react';
import { useMonteCarlo, useRunMonteCarlo } from '@/hooks/risk';
import type { MonteCarloSimulationCreate, MonteCarloFactor } from '@/types/risk';
import { formatCurrency } from '@/types/risk';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import { Activity, TrendingUp, Percent, Info, Plus, Trash2, BarChart3 } from 'lucide-react';
import { cn } from '@/lib/utils';

interface MonteCarloChartProps {
  riskId: string;
  className?: string;
}

/**
 * MonteCarloChart - Probabilistic Risk Simulation
 *
 * Features:
 * - Run 10,000 iteration simulation
 * - Interactive histogram visualization
 * - Value at Risk (VaR) at 95th percentile
 * - Conditional VaR (CVaR) at 99th percentile
 * - Mean, median, standard deviation
 * - Configurable risk factors with triangular distributions
 * - Real-time calculation with loading states
 */
export function MonteCarloChart({ riskId, className }: MonteCarloChartProps) {
  const [showForm, setShowForm] = useState(false);
  const { data: simulation, isLoading } = useMonteCarlo({ riskId });
  const runSimulation = useRunMonteCarlo(riskId, {
    onSuccess: () => setShowForm(false),
  });

  const [formData, setFormData] = useState<MonteCarloSimulationCreate>({
    iterations: 10000,
    factors: [
      { name: 'Loss Amount', min: 10000, most_likely: 50000, max: 100000 },
      { name: 'Frequency', min: 1, most_likely: 5, max: 12 },
    ],
  });

  const addFactor = () => {
    setFormData({
      ...formData,
      factors: [
        ...formData.factors,
        { name: `Factor ${formData.factors.length + 1}`, min: 0, most_likely: 50, max: 100 },
      ],
    });
  };

  const removeFactor = (index: number) => {
    setFormData({
      ...formData,
      factors: formData.factors.filter((_, i) => i !== index),
    });
  };

  const updateFactor = (index: number, field: keyof MonteCarloFactor, value: string | number) => {
    const updatedFactors = [...formData.factors];
    updatedFactors[index] = { ...updatedFactors[index], [field]: value };
    setFormData({ ...formData, factors: updatedFactors });
  };

  const handleRunSimulation = () => {
    // Validation
    if (formData.iterations < 1000 || formData.iterations > 100000) {
      return;
    }
    if (formData.factors.length === 0) {
      return;
    }
    // Validate each factor
    for (const factor of formData.factors) {
      if (factor.min > factor.most_likely || factor.most_likely > factor.max) {
        return;
      }
    }

    runSimulation.mutate(formData);
  };

  // Prepare histogram data for Recharts
  const histogramData = simulation?.distribution_data?.histogram.map((count, index) => {
    const binValue = simulation.distribution_data!.bin_edges[index];
    const binEnd = simulation.distribution_data!.bin_edges[index + 1];
    const binMid = (binValue + binEnd) / 2;

    return {
      bin: index,
      count,
      value: binMid,
      label: formatCurrency(binMid),
    };
  }) || [];

  // Custom tooltip for histogram
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white px-3 py-2 border border-gray-200 rounded-lg shadow-lg">
          <p className="text-sm font-medium text-gray-900">{payload[0].payload.label}</p>
          <p className="text-xs text-gray-600">
            Frequency: <span className="font-semibold">{payload[0].value}</span>
          </p>
        </div>
      );
    }
    return null;
  };

  if (isLoading) {
    return (
      <div className={cn('bg-white rounded-xl shadow-lg p-6', className)}>
        <div className="animate-pulse space-y-4">
          <div className="h-6 bg-gray-200 rounded w-56" />
          <div className="h-64 bg-gray-200 rounded" />
        </div>
      </div>
    );
  }

  return (
    <div className={cn('bg-white rounded-xl shadow-lg', className)}>
      {/* Header */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-purple-100 rounded-lg">
              <Activity className="w-6 h-6 text-purple-600" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Monte Carlo Simulation</h3>
              <p className="text-sm text-gray-600">Probabilistic Risk Analysis</p>
            </div>
          </div>

          <button
            onClick={() => setShowForm(!showForm)}
            className={cn(
              'px-4 py-2 rounded-lg transition-colors text-sm font-medium',
              showForm
                ? 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                : 'bg-purple-600 text-white hover:bg-purple-700'
            )}
          >
            {showForm ? 'Cancel' : 'Run Simulation'}
          </button>
        </div>
      </div>

      {/* Simulation Form */}
      {showForm && (
        <div className="p-6 bg-gray-50 border-b border-gray-200">
          <div className="flex items-start gap-2 mb-4 p-3 bg-purple-50 border border-purple-200 rounded-lg">
            <Info className="w-4 h-4 text-purple-600 mt-0.5 flex-shrink-0" />
            <div className="text-xs text-purple-900">
              <p className="font-medium mb-1">Monte Carlo Method</p>
              <p>Uses triangular distributions to model uncertainty in risk factors</p>
              <p>Runs 10,000 iterations to calculate probability distributions</p>
            </div>
          </div>

          <h4 className="text-sm font-semibold text-gray-900 mb-4">Simulation Parameters</h4>

          {/* Iterations */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Number of Iterations
            </label>
            <input
              type="number"
              min="1000"
              max="100000"
              step="1000"
              value={formData.iterations}
              onChange={(e) => setFormData({ ...formData, iterations: parseInt(e.target.value) || 10000 })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
            />
            <p className="text-xs text-gray-500 mt-1">Recommended: 10,000 (more = slower but more accurate)</p>
          </div>

          {/* Risk Factors */}
          <div className="mb-4">
            <div className="flex items-center justify-between mb-3">
              <label className="text-sm font-medium text-gray-700">
                Risk Factors (Triangular Distribution)
              </label>
              <button
                onClick={addFactor}
                className="flex items-center gap-1 px-3 py-1.5 text-sm bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
              >
                <Plus className="w-4 h-4" />
                Add Factor
              </button>
            </div>

            <div className="space-y-3">
              {formData.factors.map((factor, index) => (
                <div key={index} className="p-4 bg-white border border-gray-200 rounded-lg">
                  <div className="flex items-center justify-between mb-3">
                    <input
                      type="text"
                      value={factor.name}
                      onChange={(e) => updateFactor(index, 'name', e.target.value)}
                      className="text-sm font-medium text-gray-900 bg-transparent border-b border-gray-300 focus:border-purple-500 outline-none"
                      placeholder="Factor name"
                    />
                    {formData.factors.length > 1 && (
                      <button
                        onClick={() => removeFactor(index)}
                        className="p-1 text-red-600 hover:bg-red-50 rounded transition-colors"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    )}
                  </div>

                  <div className="grid grid-cols-3 gap-3">
                    <div>
                      <label className="block text-xs text-gray-600 mb-1">Minimum</label>
                      <input
                        type="number"
                        min="0"
                        value={factor.min}
                        onChange={(e) => updateFactor(index, 'min', parseFloat(e.target.value) || 0)}
                        className="w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                      />
                    </div>
                    <div>
                      <label className="block text-xs text-gray-600 mb-1">Most Likely</label>
                      <input
                        type="number"
                        min="0"
                        value={factor.most_likely}
                        onChange={(e) => updateFactor(index, 'most_likely', parseFloat(e.target.value) || 0)}
                        className="w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                      />
                    </div>
                    <div>
                      <label className="block text-xs text-gray-600 mb-1">Maximum</label>
                      <input
                        type="number"
                        min="0"
                        value={factor.max}
                        onChange={(e) => updateFactor(index, 'max', parseFloat(e.target.value) || 0)}
                        className="w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <button
            onClick={handleRunSimulation}
            disabled={runSimulation.isPending}
            className="w-full px-4 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-medium"
          >
            {runSimulation.isPending ? (
              <span className="flex items-center justify-center gap-2">
                <Activity className="w-4 h-4 animate-spin" />
                Running Simulation...
              </span>
            ) : (
              'Run Monte Carlo Simulation'
            )}
          </button>
        </div>
      )}

      {/* Results */}
      {simulation && (
        <div className="p-6">
          {/* Key Metrics Grid */}
          <div className="grid grid-cols-4 gap-4 mb-6">
            {/* Mean Loss */}
            <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="text-xs text-blue-700 font-medium mb-1">Mean Loss</p>
              <p className="text-xl font-bold text-blue-900">
                {formatCurrency(simulation.mean_loss)}
              </p>
              <p className="text-xs text-blue-600 mt-1">Average</p>
            </div>

            {/* Median Loss */}
            <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
              <p className="text-xs text-green-700 font-medium mb-1">Median Loss</p>
              <p className="text-xl font-bold text-green-900">
                {formatCurrency(simulation.median_loss)}
              </p>
              <p className="text-xs text-green-600 mt-1">50th %ile</p>
            </div>

            {/* VaR (95%) */}
            <div className="p-4 bg-orange-50 border border-orange-200 rounded-lg">
              <div className="flex items-center gap-1 mb-1">
                <TrendingUp className="w-3 h-3 text-orange-700" />
                <p className="text-xs text-orange-700 font-medium">VaR (95%)</p>
              </div>
              <p className="text-xl font-bold text-orange-900">
                {formatCurrency(simulation.percentile_95)}
              </p>
              <p className="text-xs text-orange-600 mt-1">95th %ile</p>
            </div>

            {/* CVaR (99%) */}
            <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
              <div className="flex items-center gap-1 mb-1">
                <TrendingUp className="w-3 h-3 text-red-700" />
                <p className="text-xs text-red-700 font-medium">CVaR (99%)</p>
              </div>
              <p className="text-xl font-bold text-red-900">
                {formatCurrency(simulation.percentile_99)}
              </p>
              <p className="text-xs text-red-600 mt-1">99th %ile</p>
            </div>
          </div>

          {/* Distribution Statistics */}
          {simulation.distribution_data && (
            <div className="mb-6 p-4 bg-gray-50 border border-gray-200 rounded-lg">
              <p className="text-sm font-semibold text-gray-900 mb-3">Distribution Statistics</p>
              <div className="grid grid-cols-3 gap-4 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Minimum:</span>
                  <span className="font-medium text-gray-900">{formatCurrency(simulation.distribution_data.min)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Maximum:</span>
                  <span className="font-medium text-gray-900">{formatCurrency(simulation.distribution_data.max)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Std Dev:</span>
                  <span className="font-medium text-gray-900">{formatCurrency(simulation.distribution_data.std_dev)}</span>
                </div>
              </div>
            </div>
          )}

          {/* Histogram Chart */}
          {histogramData.length > 0 && (
            <div className="mb-6">
              <div className="flex items-center justify-between mb-3">
                <h4 className="text-sm font-semibold text-gray-900">Loss Distribution</h4>
                <p className="text-xs text-gray-600">{histogramData.length} bins</p>
              </div>
              <div className="h-72 bg-gray-50 border border-gray-200 rounded-lg p-4">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={histogramData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                    <XAxis
                      dataKey="bin"
                      tick={{ fontSize: 11, fill: '#6b7280' }}
                      label={{ value: 'Loss Amount', position: 'insideBottom', offset: -5, fontSize: 12 }}
                    />
                    <YAxis
                      tick={{ fontSize: 11, fill: '#6b7280' }}
                      label={{ value: 'Frequency', angle: -90, position: 'insideLeft', fontSize: 12 }}
                    />
                    <Tooltip content={<CustomTooltip />} />
                    <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                      {histogramData.map((entry, index) => (
                        <Cell
                          key={`cell-${index}`}
                          fill={
                            entry.value >= simulation.percentile_99
                              ? '#dc2626' // red-600
                              : entry.value >= simulation.percentile_95
                              ? '#f97316' // orange-500
                              : '#9333ea' // purple-600
                          }
                        />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
              <div className="flex items-center justify-center gap-6 mt-3 text-xs">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-purple-600 rounded" />
                  <span className="text-gray-700">Normal Range (&lt; 95%)</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-orange-500 rounded" />
                  <span className="text-gray-700">High Risk (95-99%)</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-red-600 rounded" />
                  <span className="text-gray-700">Extreme Risk (&gt; 99%)</span>
                </div>
              </div>
            </div>
          )}

          {/* Simulation Info */}
          <div className="p-4 bg-purple-50 border border-purple-200 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <Percent className="w-4 h-4 text-purple-600" />
              <p className="text-sm font-medium text-purple-900">
                Based on {simulation.iterations.toLocaleString()} iterations
              </p>
            </div>
            <p className="text-xs text-purple-700">
              This simulation uses triangular distributions for {simulation.factors.length} risk factor(s)
            </p>
          </div>

          {/* Timestamp */}
          {simulation.simulated_at && (
            <div className="mt-4 pt-4 border-t border-gray-200">
              <p className="text-xs text-gray-500">
                Simulated: {new Date(simulation.simulated_at).toLocaleString()}
              </p>
            </div>
          )}
        </div>
      )}

      {/* No Results State */}
      {!simulation && !showForm && (
        <div className="p-12 text-center">
          <div className="p-4 bg-gray-100 rounded-full w-20 h-20 mx-auto mb-4 flex items-center justify-center">
            <BarChart3 className="w-10 h-10 text-gray-400" />
          </div>
          <p className="text-gray-900 font-medium mb-1">No Simulation Results</p>
          <p className="text-sm text-gray-600 mb-4">
            Run a Monte Carlo simulation to analyze risk probability distributions
          </p>
          <button
            onClick={() => setShowForm(true)}
            className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors text-sm font-medium"
          >
            Get Started
          </button>
        </div>
      )}
    </div>
  );
}
