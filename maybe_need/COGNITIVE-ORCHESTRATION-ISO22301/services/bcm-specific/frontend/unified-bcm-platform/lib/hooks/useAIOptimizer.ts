'use client'

import { useMutation, useQuery } from '@tanstack/react-query'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// Types
interface ProcessOptimizationRequest {
  processId: string
  historicalData?: Record<string, any>
  optimizationGoals?: string[]
}

interface OptimizationPrediction {
  processId: string
  predictions: {
    execution_time: number
    bottleneck_probability: number
    resource_optimization: {
      current_allocation: { resources: number; estimated_time: number; estimated_cost: number }
      recommended_allocation: { resources: number; estimated_time: number; estimated_cost: number }
      expected_improvement: { time_saved_minutes: number; cost_saved: number; efficiency_gain: number }
    }
  }
  recommendations: Array<{
    type: string
    priority: string
    title: string
    description: string
    impact: string
    effort: string
  }>
  confidenceScore: number
  estimatedImprovement: {
    time_reduction: number
    efficiency_gain: number
  }
}

interface BottleneckAnalysis {
  processId: string
  bottlenecks: Array<{
    type: string
    severity: string
    description: string
    impact_score: number
  }>
  severity: string
  recommendations: string[]
  estimatedImpact: {
    time_delay: number
    cost_impact: number
  }
}

interface ResourceOptimization {
  processId: string
  currentAllocation: { resources: number }
  recommendedAllocation: { resources: number }
  expectedImprovement: {
    time_saved: number
    efficiency_gain: number
  }
  costImpact: number
}

interface AnomalyDetection {
  processId: string
  anomalies: Array<{
    type: string
    description: string
    severity: string
  }>
  riskLevel: string
  recommendations: string[]
}

interface AIModelStatus {
  models: Array<{
    model_type: string
    version: string
    accuracy: number
    trained_at: string
    training_data_size: number
  }>
  total_models: number
  last_updated: string | null
}

// API Functions
const aiOptimizerApi = {
  optimizePerformance: async (data: ProcessOptimizationRequest): Promise<OptimizationPrediction> => {
    const response = await fetch(`${API_BASE}/api/v1/ai/optimize/performance`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    })

    if (!response.ok) {
      throw new Error('Failed to optimize performance')
    }

    return response.json()
  },

  analyzeBottlenecks: async (processId: string): Promise<BottleneckAnalysis> => {
    const response = await fetch(`${API_BASE}/api/v1/ai/analyze/bottlenecks/${processId}`)

    if (!response.ok) {
      throw new Error('Failed to analyze bottlenecks')
    }

    return response.json()
  },

  optimizeResources: async (processId: string): Promise<ResourceOptimization> => {
    const response = await fetch(`${API_BASE}/api/v1/ai/optimize/resources/${processId}`)

    if (!response.ok) {
      throw new Error('Failed to optimize resources')
    }

    return response.json()
  },

  detectAnomalies: async (processId: string): Promise<AnomalyDetection> => {
    const response = await fetch(`${API_BASE}/api/v1/ai/detect/anomalies/${processId}`)

    if (!response.ok) {
      throw new Error('Failed to detect anomalies')
    }

    return response.json()
  },

  retrainModels: async (): Promise<{ message: string; status: string }> => {
    const response = await fetch(`${API_BASE}/api/v1/ai/models/retrain`, {
      method: 'POST',
    })

    if (!response.ok) {
      throw new Error('Failed to retrain models')
    }

    return response.json()
  },

  getModelStatus: async (): Promise<AIModelStatus> => {
    const response = await fetch(`${API_BASE}/api/v1/ai/models/status`)

    if (!response.ok) {
      throw new Error('Failed to get model status')
    }

    return response.json()
  },
}

// React Query Hooks

// Performance Optimization
export const useOptimizePerformance = () => {
  return useMutation({
    mutationFn: aiOptimizerApi.optimizePerformance,
    onError: (error) => {
      console.error('Performance optimization failed:', error)
    },
  })
}

// Bottleneck Analysis
export const useBottleneckAnalysis = (processId: string, enabled = true) => {
  return useQuery({
    queryKey: ['bottleneck-analysis', processId],
    queryFn: () => aiOptimizerApi.analyzeBottlenecks(processId),
    enabled: enabled && !!processId,
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 2,
  })
}

// Resource Optimization
export const useResourceOptimization = (processId: string, enabled = true) => {
  return useQuery({
    queryKey: ['resource-optimization', processId],
    queryFn: () => aiOptimizerApi.optimizeResources(processId),
    enabled: enabled && !!processId,
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 2,
  })
}

// Anomaly Detection
export const useAnomalyDetection = (processId: string, enabled = true) => {
  return useQuery({
    queryKey: ['anomaly-detection', processId],
    queryFn: () => aiOptimizerApi.detectAnomalies(processId),
    enabled: enabled && !!processId,
    staleTime: 2 * 60 * 1000, // 2 minutes (more frequent for anomalies)
    retry: 2,
  })
}

// Model Management
export const useRetrainModels = () => {
  return useMutation({
    mutationFn: aiOptimizerApi.retrainModels,
    onSuccess: () => {
      console.log('Models retrain initiated successfully')
    },
    onError: (error) => {
      console.error('Model retrain failed:', error)
    },
  })
}

export const useAIModelStatus = (enabled = true) => {
  return useQuery({
    queryKey: ['ai-model-status'],
    queryFn: aiOptimizerApi.getModelStatus,
    enabled,
    staleTime: 10 * 60 * 1000, // 10 minutes
    refetchInterval: 5 * 60 * 1000, // Refetch every 5 minutes
    retry: 2,
  })
}

// Combined AI Analysis Hook
export const useAIWorkflowAnalysis = (processId: string, enabled = true) => {
  const bottleneckAnalysis = useBottleneckAnalysis(processId, enabled)
  const resourceOptimization = useResourceOptimization(processId, enabled)
  const anomalyDetection = useAnomalyDetection(processId, enabled)
  const modelStatus = useAIModelStatus(enabled)

  return {
    bottleneckAnalysis,
    resourceOptimization,
    anomalyDetection,
    modelStatus,
    isLoading: bottleneckAnalysis.isLoading || resourceOptimization.isLoading || anomalyDetection.isLoading,
    isError: bottleneckAnalysis.isError || resourceOptimization.isError || anomalyDetection.isError,
    error: bottleneckAnalysis.error || resourceOptimization.error || anomalyDetection.error,
  }
}

// Utility function to calculate overall process health score
export const calculateProcessHealthScore = (
  bottleneckAnalysis?: BottleneckAnalysis,
  anomalyDetection?: AnomalyDetection,
  resourceOptimization?: ResourceOptimization
): number => {
  if (!bottleneckAnalysis || !anomalyDetection) return 0

  let score = 100

  // Deduct points for bottlenecks
  if (bottleneckAnalysis.severity === 'high') score -= 30
  else if (bottleneckAnalysis.severity === 'medium') score -= 15
  else if (bottleneckAnalysis.severity === 'low') score -= 5

  // Deduct points for anomalies
  if (anomalyDetection.riskLevel === 'high') score -= 25
  else if (anomalyDetection.riskLevel === 'medium') score -= 10

  // Deduct points for each detected anomaly
  score -= anomalyDetection.anomalies.length * 5

  // Add points for resource optimization potential
  if (resourceOptimization?.expectedImprovement.efficiency_gain > 20) score += 10
  else if (resourceOptimization?.expectedImprovement.efficiency_gain > 10) score += 5

  return Math.max(0, Math.min(100, score))
}

export type {
  ProcessOptimizationRequest,
  OptimizationPrediction,
  BottleneckAnalysis,
  ResourceOptimization,
  AnomalyDetection,
  AIModelStatus,
}