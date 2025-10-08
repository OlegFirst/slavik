'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useQueueTheoryBIA } from '@/lib/api/queries';
import { QueueTheoryRequest, QueueTheoryResponse } from '@/lib/api/types';
import { Loader2, Calculator, TrendingDown, Clock, DollarSign } from 'lucide-react';
import { BIACharts } from '@/components/charts/bia-charts';

export default function BIAPage() {
  const [result, setResult] = useState<QueueTheoryResponse | null>(null);
  const { mutate, isPending } = useQueueTheoryBIA();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<QueueTheoryRequest>({
    defaultValues: {
      simulation_hours: 168,
      num_servers: 1,
    },
  });

  const onSubmit = (data: QueueTheoryRequest) => {
    mutate(data, {
      onSuccess: (response) => {
        setResult(response);
      },
    });
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Queue Theory BIA</h1>
        <p className="text-gray-600 mt-1">Mathematical Business Impact Analysis using M/M/c queues and Erlang C formula</p>
      </div>

      {/* Input Form */}
      <form onSubmit={handleSubmit(onSubmit)} className="bg-white rounded-lg shadow">
        <div className="p-6 space-y-6">
          {/* Business Process Info */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900">Business Process Information</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Process Name *
                </label>
                <input
                  {...register('name', { required: 'Process name is required' })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., Order Processing System"
                />
                {errors.name && <p className="text-red-600 text-sm mt-1">{errors.name.message}</p>}
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Description
                </label>
                <input
                  {...register('description')}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Brief description"
                />
              </div>
            </div>
          </div>

          {/* Queue Parameters */}
          <div className="space-y-4 border-t pt-6">
            <h3 className="text-lg font-semibold text-gray-900">Queue Parameters</h3>
            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Arrival Rate (λ) *
                </label>
                <input
                  type="number"
                  step="0.1"
                  {...register('arrival_rate', { required: true, valueAsNumber: true, min: 0.1 })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="10.0"
                />
                <p className="text-xs text-gray-500 mt-1">Requests arriving per hour</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Service Rate (μ) *
                </label>
                <input
                  type="number"
                  step="0.1"
                  {...register('service_rate', { required: true, valueAsNumber: true, min: 0.1 })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="12.0"
                />
                <p className="text-xs text-gray-500 mt-1">Processed per hour (per server)</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Servers (c) *
                </label>
                <input
                  type="number"
                  {...register('num_servers', { required: true, valueAsNumber: true, min: 1 })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="2"
                />
                <p className="text-xs text-gray-500 mt-1">Number of parallel servers</p>
              </div>
            </div>
          </div>

          {/* Financial Impact */}
          <div className="space-y-4 border-t pt-6">
            <h3 className="text-lg font-semibold text-gray-900">Financial Impact</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Revenue per Hour *
                </label>
                <div className="relative">
                  <span className="absolute left-3 top-2 text-gray-500">$</span>
                  <input
                    type="number"
                    step="100"
                    {...register('revenue_per_hour', { required: true, valueAsNumber: true, min: 0 })}
                    className="w-full pl-8 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="50000"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Downtime Cost per Hour *
                </label>
                <div className="relative">
                  <span className="absolute left-3 top-2 text-gray-500">$</span>
                  <input
                    type="number"
                    step="100"
                    {...register('cost_per_hour_downtime', { required: true, valueAsNumber: true, min: 0 })}
                    className="w-full pl-8 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="75000"
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Tolerances */}
          <div className="space-y-4 border-t pt-6">
            <h3 className="text-lg font-semibold text-gray-900">Tolerances</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Max Acceptable Wait (hours) *
                </label>
                <input
                  type="number"
                  step="0.1"
                  {...register('max_acceptable_wait', { required: true, valueAsNumber: true, min: 0.1 })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="0.5"
                />
                <p className="text-xs text-gray-500 mt-1">How long can customers wait?</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Max Data Loss (hours) *
                </label>
                <input
                  type="number"
                  step="0.5"
                  {...register('max_data_loss_hours', { required: true, valueAsNumber: true, min: 0 })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="2.0"
                />
                <p className="text-xs text-gray-500 mt-1">RPO tolerance</p>
              </div>
            </div>
          </div>

          {/* Simulation Settings */}
          <div className="space-y-4 border-t pt-6">
            <h3 className="text-lg font-semibold text-gray-900">Simulation Settings</h3>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Simulation Duration (hours)
              </label>
              <input
                type="number"
                {...register('simulation_hours', { valueAsNumber: true, min: 1 })}
                className="w-full max-w-xs px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="168"
              />
              <p className="text-xs text-gray-500 mt-1">Default: 168 hours (1 week)</p>
            </div>
          </div>
        </div>

        <div className="px-6 py-4 bg-gray-50 border-t rounded-b-lg">
          <button
            type="submit"
            disabled={isPending}
            className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed font-medium transition-colors flex items-center justify-center gap-2"
          >
            {isPending ? (
              <>
                <Loader2 className="animate-spin" size={20} />
                <span>Running Analysis...</span>
              </>
            ) : (
              <>
                <Calculator size={20} />
                <span>Run Queue Theory Analysis</span>
              </>
            )}
          </button>
        </div>
      </form>

      {/* Results */}
      {result && (
        <div className="space-y-4">
          <h2 className="text-2xl font-bold text-gray-900">Analysis Results</h2>

          {/* Queue Metrics */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">Queue Metrics</h3>
            <div className="grid grid-cols-4 gap-4">
              <div className="p-4 bg-blue-50 rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <Clock className="text-blue-600" size={20} />
                  <p className="text-sm text-gray-600">Avg Wait Time</p>
                </div>
                <p className="text-2xl font-bold text-gray-900">
                  {(result.queue_metrics.average_wait_time * 60).toFixed(1)} min
                </p>
              </div>
              <div className="p-4 bg-purple-50 rounded-lg">
                <p className="text-sm text-gray-600 mb-2">Queue Length</p>
                <p className="text-2xl font-bold text-gray-900">
                  {result.queue_metrics.average_queue_length.toFixed(1)}
                </p>
              </div>
              <div className="p-4 bg-orange-50 rounded-lg">
                <p className="text-sm text-gray-600 mb-2">Utilization</p>
                <p className="text-2xl font-bold text-gray-900">
                  {(result.queue_metrics.server_utilization * 100).toFixed(1)}%
                </p>
              </div>
              <div className="p-4 bg-green-50 rounded-lg">
                <p className="text-sm text-gray-600 mb-2">Prob. Wait</p>
                <p className="text-2xl font-bold text-gray-900">
                  {(result.queue_metrics.probability_wait * 100).toFixed(1)}%
                </p>
              </div>
            </div>
          </div>

          {/* Business Impact */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">Business Impact</h3>
            <div className="grid grid-cols-3 gap-4">
              <div className="p-4 bg-red-50 rounded-lg border-l-4 border-red-500">
                <div className="flex items-center gap-2 mb-2">
                  <DollarSign className="text-red-600" size={20} />
                  <p className="text-sm text-gray-600">Loss/Hour</p>
                </div>
                <p className="text-2xl font-bold text-red-900">
                  ${result.business_impact.potential_revenue_loss_per_hour.toLocaleString()}
                </p>
              </div>
              <div className="p-4 bg-red-50 rounded-lg border-l-4 border-red-600">
                <div className="flex items-center gap-2 mb-2">
                  <TrendingDown className="text-red-700" size={20} />
                  <p className="text-sm text-gray-600">Annual Risk</p>
                </div>
                <p className="text-2xl font-bold text-red-900">
                  ${(result.business_impact.estimated_annual_risk / 1000000).toFixed(1)}M
                </p>
              </div>
              <div className="p-4 bg-yellow-50 rounded-lg border-l-4 border-yellow-500">
                <p className="text-sm text-gray-600 mb-2">MTD</p>
                <p className="text-2xl font-bold text-gray-900">
                  {result.business_impact.mtd} hours
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  ({(result.business_impact.mtd / 24).toFixed(1)} days)
                </p>
              </div>
            </div>
            <div className="mt-4 p-4 bg-red-100 rounded-lg">
              <p className="text-sm font-semibold uppercase tracking-wide text-red-900">
                Impact Category: {result.business_impact.impact_category}
              </p>
            </div>
          </div>

          {/* RTO/RPO Recommendations */}
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg shadow p-6 border-2 border-blue-200">
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Calculator className="text-blue-600" size={24} />
              RTO/RPO Recommendations
            </h3>
            <div className="grid grid-cols-2 gap-6 mb-4">
              <div className="bg-white p-4 rounded-lg">
                <p className="text-sm text-gray-600 mb-1">Recommended RTO</p>
                <p className="text-3xl font-bold text-blue-600">
                  {(result.rto_rpo_recommendations.recommended_rto_hours * 60).toFixed(0)} min
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  ({result.rto_rpo_recommendations.recommended_rto_hours.toFixed(2)} hours)
                </p>
              </div>
              <div className="bg-white p-4 rounded-lg">
                <p className="text-sm text-gray-600 mb-1">Recommended RPO</p>
                <p className="text-3xl font-bold text-indigo-600">
                  {(result.rto_rpo_recommendations.recommended_rpo_hours * 60).toFixed(0)} min
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  ({result.rto_rpo_recommendations.recommended_rpo_hours.toFixed(2)} hours)
                </p>
              </div>
            </div>
            <div className="bg-white p-4 rounded-lg">
              <p className="text-sm font-medium text-gray-700 mb-2">Rationale:</p>
              <p className="text-sm text-gray-600 leading-relaxed">
                {result.rto_rpo_recommendations.rationale}
              </p>
            </div>
          </div>

          {/* Recovery Strategies */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">Recovery Strategies</h3>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Strategy</th>
                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Cost/Year</th>
                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">RTO</th>
                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Risk Reduction</th>
                  </tr>
                </thead>
                <tbody>
                  {result.recovery_strategies.map((strategy, i) => (
                    <tr key={i} className="border-b hover:bg-gray-50">
                      <td className="py-3 px-4 font-medium">{strategy.name}</td>
                      <td className="py-3 px-4">${strategy.estimated_cost_annual.toLocaleString()}</td>
                      <td className="py-3 px-4">
                        {(strategy.expected_rto_hours * 60).toFixed(0)} min
                      </td>
                      <td className="py-3 px-4">
                        <span className="px-2 py-1 bg-green-100 text-green-800 rounded text-sm font-medium">
                          {strategy.risk_reduction_percentage.toFixed(0)}%
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Charts & Visualizations */}
          <BIACharts
            queueMetrics={result.queue_metrics}
            recoveryStrategies={result.recovery_strategies}
          />

          {/* Simulation Stats */}
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-center justify-between text-sm text-gray-600">
              <span>Customers Served: <strong>{result.simulation_details.total_customers_served.toLocaleString()}</strong></span>
              <span>Simulation Time: <strong>{result.simulation_details.total_simulation_time} hours</strong></span>
              <span>Confidence: <strong>{(result.simulation_details.confidence_level * 100).toFixed(0)}%</strong></span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
