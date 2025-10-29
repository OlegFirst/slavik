'use client'

import { useMutation, useQuery } from '@tanstack/react-query'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// Types
interface ProcessExecutionLog {
  process_id: string
  execution_id: string
  start_time: string
  end_time?: string
  status: 'running' | 'completed' | 'failed' | 'cancelled'
  executed_by?: string
  metadata?: Record<string, any>
}

interface ProcessEventLog {
  execution_id: string
  event_type: 'start' | 'end' | 'checkpoint' | 'error' | 'decision'
  step_name: string
  timestamp: string
  duration_minutes?: number
  actor?: string
  data?: Record<string, any>
}

interface ProcessPerformanceAnalysis {
  process_id: string
  analysis_period: {
    from: string
    to: string
  }
  performance_metrics: {
    total_executions: number
    average_duration: number
    median_duration: number
    min_duration: number
    max_duration: number
    duration_std: number
    success_rate: number
    failure_rate: number
    cancellation_rate: number
    status_distribution: Record<string, number>
  }
  trends: Array<{
    date: string
    executions: number
    avg_duration: number
    success_rate: number
  }>
  insights: string[]
}

interface ProcessPattern {
  pattern: string[]
  frequency: number
  confidence: number
  support?: number
}

interface PatternDiscovery {
  process_id: string
  total_traces_analyzed: number
  patterns: {
    sequence_patterns: ProcessPattern[]
    parallel_patterns: ProcessPattern[]
    loop_patterns: ProcessPattern[]
    skip_patterns: Array<{
      step: string
      skip_frequency: number
      skip_rate: number
      execution_frequency: number
    }>
    timing_patterns: Array<{
      step: string
      avg_duration: number
      median_duration: number
      min_duration: number
      max_duration: number
      std_duration: number
      sample_size: number
    }>
  }
  insights: string[]
}

interface ProcessDeviation {
  execution_id: string
  deviation_type: 'timing' | 'sequence' | 'resource' | 'quality'
  severity: 'low' | 'medium' | 'high' | 'critical'
  description?: string
  step?: string
  actual_value?: any
  expected_value?: any
  deviation_score?: number
}

interface DeviationDetection {
  process_id: string
  total_traces_analyzed: number
  total_deviations: number
  deviation_rate: number
  deviations: {
    timing_deviations: ProcessDeviation[]
    sequence_deviations: ProcessDeviation[]
    resource_deviations: ProcessDeviation[]
    quality_deviations: ProcessDeviation[]
  }
  severity_breakdown: {
    low: number
    medium: number
    high: number
    critical: number
  }
  insights: string[]
}

interface ProcessMiningRequest {
  process_id: string
  date_from?: string
  date_to?: string
  include_patterns: boolean
  include_deviations: boolean
  include_performance: boolean
}

interface ComprehensiveAnalysis {
  process_id: string
  analysis_date: string
  analysis_scope: {
    days_back: number
    date_from?: string
    date_to?: string
  }
  performance_analysis?: ProcessPerformanceAnalysis
  pattern_discovery?: PatternDiscovery
  deviation_detection?: DeviationDetection
  overall_insights: string[]
  analysis_summary: {
    total_insights: number
    performance_included: boolean
    patterns_included: boolean
    deviations_included: boolean
  }
}

interface ProcessSummary {
  process_id: string
  statistics: {
    total_executions: number
    completed_executions: number
    failed_executions: number
    success_rate: number
    recent_executions_7d: number
    discovered_patterns: number
    detected_deviations: number
  }
  last_updated: string
}

// API Functions
const processMiningApi = {
  logExecution: async (execution: ProcessExecutionLog): Promise<{ message: string; id: string }> => {
    const response = await fetch(`${API_BASE}/api/v1/process-mining/log-execution`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(execution),
    })

    if (!response.ok) {
      throw new Error('Failed to log process execution')
    }

    return response.json()
  },

  logEvent: async (event: ProcessEventLog): Promise<{ message: string; id: string }> => {
    const response = await fetch(`${API_BASE}/api/v1/process-mining/log-event`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(event),
    })

    if (!response.ok) {
      throw new Error('Failed to log process event')
    }

    return response.json()
  },

  analyzePerformance: async (processId: string, daysBack: number = 30): Promise<ProcessPerformanceAnalysis> => {
    const response = await fetch(`${API_BASE}/api/v1/process-mining/analyze-performance/${processId}?days_back=${daysBack}`, {
      method: 'POST',
    })

    if (!response.ok) {
      throw new Error('Failed to analyze process performance')
    }

    return response.json()
  },

  discoverPatterns: async (processId: string, daysBack: number = 30): Promise<PatternDiscovery> => {
    const response = await fetch(`${API_BASE}/api/v1/process-mining/discover-patterns/${processId}?days_back=${daysBack}`, {
      method: 'POST',
    })

    if (!response.ok) {
      throw new Error('Failed to discover process patterns')
    }

    return response.json()
  },

  detectDeviations: async (processId: string, daysBack: number = 30): Promise<DeviationDetection> => {
    const response = await fetch(`${API_BASE}/api/v1/process-mining/detect-deviations/${processId}?days_back=${daysBack}`, {
      method: 'POST',
    })

    if (!response.ok) {
      throw new Error('Failed to detect process deviations')
    }

    return response.json()
  },

  comprehensiveAnalysis: async (request: ProcessMiningRequest): Promise<ComprehensiveAnalysis> => {
    const response = await fetch(`${API_BASE}/api/v1/process-mining/comprehensive-analysis`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    })

    if (!response.ok) {
      throw new Error('Failed to perform comprehensive analysis')
    }

    return response.json()
  },

  getProcessSummary: async (processId: string): Promise<ProcessSummary> => {
    const response = await fetch(`${API_BASE}/api/v1/process-mining/processes/${processId}/summary`)

    if (!response.ok) {
      throw new Error('Failed to get process summary')
    }

    return response.json()
  },
}

// React Query Hooks

// Execution Logging
export const useLogExecution = () => {
  return useMutation({
    mutationFn: processMiningApi.logExecution,
    onSuccess: () => {
      console.log('Process execution logged successfully')
    },
    onError: (error) => {
      console.error('Failed to log execution:', error)
    },
  })
}

export const useLogEvent = () => {
  return useMutation({
    mutationFn: processMiningApi.logEvent,
    onSuccess: () => {
      console.log('Process event logged successfully')
    },
    onError: (error) => {
      console.error('Failed to log event:', error)
    },
  })
}

// Performance Analysis
export const usePerformanceAnalysis = (processId: string, daysBack: number = 30, enabled = true) => {
  return useQuery({
    queryKey: ['process-mining-performance', processId, daysBack],
    queryFn: () => processMiningApi.analyzePerformance(processId, daysBack),
    enabled: enabled && !!processId,
    staleTime: 10 * 60 * 1000, // 10 minutes
    retry: 2,
  })
}

// Pattern Discovery
export const usePatternDiscovery = (processId: string, daysBack: number = 30, enabled = true) => {
  return useQuery({
    queryKey: ['process-mining-patterns', processId, daysBack],
    queryFn: () => processMiningApi.discoverPatterns(processId, daysBack),
    enabled: enabled && !!processId,
    staleTime: 15 * 60 * 1000, // 15 minutes
    retry: 2,
  })
}

// Deviation Detection
export const useDeviationDetection = (processId: string, daysBack: number = 30, enabled = true) => {
  return useQuery({
    queryKey: ['process-mining-deviations', processId, daysBack],
    queryFn: () => processMiningApi.detectDeviations(processId, daysBack),
    enabled: enabled && !!processId,
    staleTime: 5 * 60 * 1000, // 5 minutes (more frequent for deviations)
    retry: 2,
  })
}

// Comprehensive Analysis
export const useComprehensiveAnalysis = () => {
  return useMutation({
    mutationFn: processMiningApi.comprehensiveAnalysis,
    onError: (error) => {
      console.error('Comprehensive analysis failed:', error)
    },
  })
}

// Process Summary
export const useProcessSummary = (processId: string, enabled = true) => {
  return useQuery({
    queryKey: ['process-mining-summary', processId],
    queryFn: () => processMiningApi.getProcessSummary(processId),
    enabled: enabled && !!processId,
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 2,
  })
}

// Combined Process Mining Hook
export const useProcessMiningAnalysis = (processId: string, daysBack: number = 30, enabled = true) => {
  const performanceAnalysis = usePerformanceAnalysis(processId, daysBack, enabled)
  const patternDiscovery = usePatternDiscovery(processId, daysBack, enabled)
  const deviationDetection = useDeviationDetection(processId, daysBack, enabled)
  const processSummary = useProcessSummary(processId, enabled)

  return {
    performanceAnalysis,
    patternDiscovery,
    deviationDetection,
    processSummary,
    isLoading: performanceAnalysis.isLoading || patternDiscovery.isLoading || deviationDetection.isLoading,
    isError: performanceAnalysis.isError || patternDiscovery.isError || deviationDetection.isError,
    error: performanceAnalysis.error || patternDiscovery.error || deviationDetection.error,
  }
}

// Utility functions
export const calculateProcessHealthScore = (
  performance?: ProcessPerformanceAnalysis,
  deviations?: DeviationDetection,
  patterns?: PatternDiscovery
): number => {
  if (!performance || !deviations) return 0

  let score = 100

  // Performance factors
  if (performance.performance_metrics.success_rate < 80) score -= 25
  else if (performance.performance_metrics.success_rate < 90) score -= 15
  else if (performance.performance_metrics.success_rate < 95) score -= 5

  // Deviation factors
  const deviationRate = deviations.deviation_rate
  if (deviationRate > 30) score -= 20
  else if (deviationRate > 20) score -= 15
  else if (deviationRate > 10) score -= 10

  // Severity of deviations
  const { critical, high, medium } = deviations.severity_breakdown
  score -= critical * 10 + high * 5 + medium * 2

  // Pattern efficiency (optional bonus)
  if (patterns) {
    const loopPatterns = patterns.patterns.loop_patterns.length
    if (loopPatterns > 3) score -= 5 // Too many loops indicate inefficiency

    const skipPatterns = patterns.patterns.skip_patterns.filter(p => p.skip_rate > 0.3).length
    if (skipPatterns > 0) score += 5 // Optional steps indicate good flexibility
  }

  return Math.max(0, Math.min(100, score))
}

export const formatDeviationSeverity = (severity: string): { color: string; label: string } => {
  switch (severity) {
    case 'critical':
      return { color: 'red', label: 'Critical' }
    case 'high':
      return { color: 'orange', label: 'High' }
    case 'medium':
      return { color: 'yellow', label: 'Medium' }
    case 'low':
      return { color: 'blue', label: 'Low' }
    default:
      return { color: 'gray', label: 'Unknown' }
  }
}

export const formatPatternConfidence = (confidence: number): string => {
  if (confidence >= 0.9) return 'Very High'
  if (confidence >= 0.7) return 'High'
  if (confidence >= 0.5) return 'Medium'
  if (confidence >= 0.3) return 'Low'
  return 'Very Low'
}

export type {
  ProcessExecutionLog,
  ProcessEventLog,
  ProcessPerformanceAnalysis,
  PatternDiscovery,
  DeviationDetection,
  ProcessMiningRequest,
  ComprehensiveAnalysis,
  ProcessSummary,
  ProcessPattern,
  ProcessDeviation,
}