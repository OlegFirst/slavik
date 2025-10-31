/**
 * React hooks for Workflow Management
 */

import { useQuery, useMutation, useQueryClient, keepPreviousData } from '@tanstack/react-query'
import { toast } from 'sonner'
import {
  workflowDashboardApi,
  processManagementApi,
  bpmnDesignerApi,
  automationApi,
  integrationApi,
  workflowTemplatesApi,
  workflowAnalyticsApi,
  slaManagementApi,
  type WorkflowMetrics,
  type BusinessProcess,
  type BPMNDiagram,
  type AutomationRule,
  type ActiveWorkflow,
  type ProcessPerformanceMetrics,
  type BottleneckAnalysis,
  type TrendData,
  type SLADefinition,
  type SLAStatus
} from '@/lib/services/workflow-api'

// Query keys
export const workflowQueryKeys = {
  all: ['workflow'] as const,
  metrics: () => [...workflowQueryKeys.all, 'metrics'] as const,
  activeWorkflows: () => [...workflowQueryKeys.all, 'active'] as const,
  processes: (filters?: any) => [...workflowQueryKeys.all, 'processes', filters] as const,
  bpmnDiagrams: () => [...workflowQueryKeys.all, 'bpmn'] as const,
  automationRules: () => [...workflowQueryKeys.all, 'automation'] as const,
  serviceStatus: () => [...workflowQueryKeys.all, 'status'] as const,
  templates: () => [...workflowQueryKeys.all, 'templates'] as const,
  // 🆕 NEW: Analytics & SLA query keys
  analytics: (filters?: any) => [...workflowQueryKeys.all, 'analytics', filters] as const,
  performance: (filters?: any) => [...workflowQueryKeys.all, 'performance', filters] as const,
  bottlenecks: (processId?: string) => [...workflowQueryKeys.all, 'bottlenecks', processId] as const,
  trends: (processId: string, period: string) => [...workflowQueryKeys.all, 'trends', processId, period] as const,
  sla: () => [...workflowQueryKeys.all, 'sla'] as const,
  slaStatus: (processIds?: string[]) => [...workflowQueryKeys.all, 'sla', 'status', processIds] as const,
  slaBreaches: (filters?: any) => [...workflowQueryKeys.all, 'sla', 'breaches', filters] as const
}

/**
 * Workflow Dashboard Hooks
 */
export function useWorkflowMetrics() {
  return useQuery({
    queryKey: workflowQueryKeys.metrics(),
    queryFn: () => workflowDashboardApi.getMetrics(),
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchInterval: 30 * 1000 // Refresh every 30 seconds
  })
}

export function useActiveWorkflows() {
  return useQuery({
    queryKey: workflowQueryKeys.activeWorkflows(),
    queryFn: () => workflowDashboardApi.getActiveWorkflows(),
    staleTime: 1 * 60 * 1000, // 1 minute
    refetchInterval: 10 * 1000 // Refresh every 10 seconds
  })
}

export function useWorkflow(id: string) {
  return useQuery({
    queryKey: [...workflowQueryKeys.activeWorkflows(), id],
    queryFn: () => workflowDashboardApi.getWorkflow(id),
    enabled: !!id
  })
}

/**
 * Process Management Hooks with proper error handling
 */
export function useProcesses(filters?: {
  category?: string
  status?: string
  search?: string
  page?: number
  limit?: number
}) {
  return useQuery({
    queryKey: workflowQueryKeys.processes(filters),
    queryFn: async () => {
      const result = await processManagementApi.getProcesses(filters)
      if (!result.success) {
        throw new Error(result.message)
      }
      return result.data
    },
    staleTime: 2 * 60 * 1000, // 2 minutes
    placeholderData: keepPreviousData, // Keep previous data while loading new
    retry: (failureCount, error) => {
      // Don't retry on validation errors
      if (error.message.includes('validation') || error.message.includes('permission')) {
        return false
      }
      return failureCount < 3
    },
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
    meta: {
      errorMessage: 'Failed to load business processes'
    }
  })
}

export function useCreateProcess() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (processInput: BusinessProcessInput) => {
      const result = await processManagementApi.createProcess(processInput)
      if (!result.success) {
        throw new Error(result.message)
      }
      return result.data
    },
    onSuccess: (data) => {
      // Invalidate and refetch queries
      queryClient.invalidateQueries({ queryKey: workflowQueryKeys.processes() })
      queryClient.invalidateQueries({ queryKey: workflowQueryKeys.metrics() })

      // Optimistically add the new process to the cache
      queryClient.setQueryData(
        workflowQueryKeys.processes(),
        (oldData: any) => {
          if (!oldData) return oldData
          return {
            ...oldData,
            data: [data, ...oldData.data],
            pagination: {
              ...oldData.pagination,
              total: oldData.pagination.total + 1
            }
          }
        }
      )

      toast.success('Business process created successfully')
    },
    onError: (error: Error) => {
      console.error('Failed to create process:', error)
      toast.error(error.message || 'Failed to create business process')
    }
  })
}

// 🔥 NEW: Hook for transaction-safe process creation
export function useCreateProcessWithWorkflow() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({
      process,
      bpmn,
      automation
    }: {
      process: BusinessProcessInput
      bpmn?: BPMNDiagramInput
      automation?: AutomationRuleInput[]
    }) => {
      const result = await processManagementApi.createProcessWithWorkflow(
        process,
        bpmn,
        automation
      )
      if (!result.success) {
        throw new Error(result.message)
      }
      return result.data
    },
    onSuccess: (data) => {
      // Invalidate multiple query types since we created multiple resources
      queryClient.invalidateQueries({ queryKey: workflowQueryKeys.processes() })
      queryClient.invalidateQueries({ queryKey: workflowQueryKeys.bmpnDiagrams() })
      queryClient.invalidateQueries({ queryKey: workflowQueryKeys.automationRules() })
      queryClient.invalidateQueries({ queryKey: workflowQueryKeys.metrics() })

      toast.success(
        `Complete workflow created: Process "${data.process.name}"` +
        (data.bpmnDiagram ? ' with BPMN diagram' : '') +
        (data.automationRules ? ` and ${data.automationRules.length} automation rules` : '')
      )
    },
    onError: (error: Error) => {
      console.error('Failed to create complete workflow:', error)
      toast.error(error.message || 'Failed to create complete workflow')
    }
  })
}

export function useUpdateProcess() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, process }: { id: string; process: Partial<BusinessProcess> }) =>
      processManagementApi.updateProcess(id, process),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: workflowQueryKeys.processes() })
    }
  })
}

export function useDeleteProcess() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: string) => processManagementApi.deleteProcess(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: workflowQueryKeys.processes() })
      queryClient.invalidateQueries({ queryKey: workflowQueryKeys.metrics() })
    }
  })
}

export function useArchiveProcess() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: string) => processManagementApi.archiveProcess(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: workflowQueryKeys.processes() })
    }
  })
}

/**
 * BPMN Designer Hooks
 */
export function useBPMNDiagrams() {
  return useQuery({
    queryKey: workflowQueryKeys.bmpnDiagrams(),
    queryFn: () => bpmnDesignerApi.getDiagrams(),
    staleTime: 5 * 60 * 1000 // 5 minutes
  })
}

export function useBPMNDiagram(id: string) {
  return useQuery({
    queryKey: [...workflowQueryKeys.bmpnDiagrams(), id],
    queryFn: () => bpmnDesignerApi.getDiagram(id),
    enabled: !!id
  })
}

export function useCreateBPMNDiagram() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (diagram: Omit<BPMNDiagram, 'id' | 'lastModified'>) =>
      bpmnDesignerApi.createDiagram(diagram),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: workflowQueryKeys.bmpnDiagrams() })
    }
  })
}

export function useUpdateBPMNDiagram() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, diagram }: { id: string; diagram: Partial<BPMNDiagram> }) =>
      bpmnDesignerApi.updateDiagram(id, diagram),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: [...workflowQueryKeys.bmpnDiagrams(), id] })
      queryClient.invalidateQueries({ queryKey: workflowQueryKeys.bmpnDiagrams() })
    }
  })
}

export function useDeleteBPMNDiagram() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: string) => bpmnDesignerApi.deleteDiagram(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: workflowQueryKeys.bmpnDiagrams() })
    }
  })
}

export function useExportBPMNDiagram() {
  return useMutation({
    mutationFn: ({ id, format }: { id: string; format: 'xml' | 'svg' | 'png' }) =>
      bpmnDesignerApi.exportDiagram(id, format)
  })
}

export function useImportBPMNDiagram() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (file: File) => bpmnDesignerApi.importDiagram(file),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: workflowQueryKeys.bmpnDiagrams() })
    }
  })
}

export function useValidateBPMNDiagram() {
  return useMutation({
    mutationFn: (id: string) => bpmnDesignerApi.validateDiagram(id)
  })
}

export function useSimulateBPMNWorkflow() {
  return useMutation({
    mutationFn: (id: string) => bpmnDesignerApi.simulateWorkflow(id)
  })
}

/**
 * Automation Center Hooks
 */
export function useAutomationRules() {
  return useQuery({
    queryKey: workflowQueryKeys.automationRules(),
    queryFn: () => automationApi.getRules(),
    staleTime: 2 * 60 * 1000 // 2 minutes
  })
}

export function useCreateAutomationRule() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (rule: Omit<AutomationRule, 'id' | 'executionCount' | 'lastExecuted'>) =>
      automationApi.createRule(rule),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: workflowQueryKeys.automationRules() })
      queryClient.invalidateQueries({ queryKey: workflowQueryKeys.metrics() })
    }
  })
}

export function useUpdateAutomationRule() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, rule }: { id: string; rule: Partial<AutomationRule> }) =>
      automationApi.updateRule(id, rule),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: workflowQueryKeys.automationRules() })
    }
  })
}

export function useDeleteAutomationRule() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: string) => automationApi.deleteRule(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: workflowQueryKeys.automationRules() })
      queryClient.invalidateQueries({ queryKey: workflowQueryKeys.metrics() })
    }
  })
}

export function useToggleAutomationRule() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: string) => automationApi.toggleRule(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: workflowQueryKeys.automationRules() })
    }
  })
}

export function useExecuteAutomationRule() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: string) => automationApi.executeRule(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: workflowQueryKeys.automationRules() })
    }
  })
}

export function useAutomationRuleHistory(id: string) {
  return useQuery({
    queryKey: [...workflowQueryKeys.automationRules(), id, 'history'],
    queryFn: () => automationApi.getRuleHistory(id),
    enabled: !!id
  })
}

export function useAutomationAnalytics() {
  return useQuery({
    queryKey: [...workflowQueryKeys.automationRules(), 'analytics'],
    queryFn: () => automationApi.getAnalytics(),
    staleTime: 5 * 60 * 1000 // 5 minutes
  })
}

/**
 * Integration Status Hooks
 */
export function useServiceStatus() {
  return useQuery({
    queryKey: workflowQueryKeys.serviceStatus(),
    queryFn: () => integrationApi.getServiceStatus(),
    staleTime: 30 * 1000, // 30 seconds
    refetchInterval: 60 * 1000 // Refresh every minute
  })
}

export function useTestBPMNService() {
  return useMutation({
    mutationFn: () => integrationApi.testBPMNService()
  })
}

/**
 * Templates Hooks
 */
export function useProcessTemplates() {
  return useQuery({
    queryKey: [...workflowQueryKeys.templates(), 'processes'],
    queryFn: () => workflowTemplatesApi.getProcessTemplates(),
    staleTime: 10 * 60 * 1000 // 10 minutes
  })
}

export function useAutomationTemplates() {
  return useQuery({
    queryKey: [...workflowQueryKeys.templates(), 'automation'],
    queryFn: () => workflowTemplatesApi.getAutomationTemplates(),
    staleTime: 10 * 60 * 1000 // 10 minutes
  })
}

export function useCreateFromTemplate() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ templateId, customization }: { templateId: string; customization: any }) =>
      workflowTemplatesApi.createFromTemplate(templateId, customization),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: workflowQueryKeys.processes() })
      queryClient.invalidateQueries({ queryKey: workflowQueryKeys.metrics() })
    }
  })
}

/**
 * 🆕 NEW: Workflow Analytics Hooks
 */
export function useWorkflowAnalytics(filters?: {
  department?: string
  category?: string
  dateRange?: { from: string; to: string }
}) {
  return useQuery({
    queryKey: workflowQueryKeys.analytics(filters),
    queryFn: async () => {
      const result = await workflowAnalyticsApi.getWorkflowAnalytics(filters)
      if (!result.success) {
        throw new Error(result.message)
      }
      return result.data
    },
    staleTime: 2 * 60 * 1000, // 2 minutes
    refetchInterval: 30 * 1000 // Refresh every 30 seconds
  })
}

export function useProcessPerformance(filters?: {
  processIds?: string[]
  department?: string
  category?: string
  dateRange?: { from: string; to: string }
}) {
  return useQuery({
    queryKey: workflowQueryKeys.performance(filters),
    queryFn: async () => {
      const result = await workflowAnalyticsApi.getProcessPerformance(filters)
      if (!result.success) {
        throw new Error(result.message)
      }
      return result.data
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    placeholderData: keepPreviousData
  })
}

export function useBottleneckAnalysis(processId?: string) {
  return useQuery({
    queryKey: workflowQueryKeys.bottlenecks(processId),
    queryFn: async () => {
      const result = await workflowAnalyticsApi.getBottleneckAnalysis(processId)
      if (!result.success) {
        throw new Error(result.message)
      }
      return result.data
    },
    staleTime: 10 * 60 * 1000, // 10 minutes
    enabled: !!processId
  })
}

export function useTrendAnalysis(processId: string, period: '7d' | '30d' | '90d' | '1y') {
  return useQuery({
    queryKey: workflowQueryKeys.trends(processId, period),
    queryFn: async () => {
      const result = await workflowAnalyticsApi.getTrendAnalysis(processId, period)
      if (!result.success) {
        throw new Error(result.message)
      }
      return result.data
    },
    staleTime: 15 * 60 * 1000, // 15 minutes
    enabled: !!processId
  })
}

export function useGenerateAnalyticsReport() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (config: {
      processIds: string[]
      metrics: string[]
      format: 'json' | 'csv' | 'pdf'
      dateRange: { from: string; to: string }
    }) => {
      const result = await workflowAnalyticsApi.generateReport(config)
      if (!result.success) {
        throw new Error(result.message)
      }
      return result.data
    },
    onSuccess: () => {
      toast.success('Analytics report generated successfully')
    },
    onError: (error: Error) => {
      toast.error(`Failed to generate report: ${error.message}`)
    }
  })
}

/**
 * 🆕 NEW: SLA Management Hooks
 */
export function useSLADefinitions(processId?: string) {
  return useQuery({
    queryKey: [...workflowQueryKeys.sla(), 'definitions', processId],
    queryFn: async () => {
      const result = await slaManagementApi.getSLADefinitions(processId)
      if (!result.success) {
        throw new Error(result.message)
      }
      return result.data
    },
    staleTime: 10 * 60 * 1000 // 10 minutes
  })
}

export function useSLAStatus(processIds?: string[]) {
  return useQuery({
    queryKey: workflowQueryKeys.slaStatus(processIds),
    queryFn: async () => {
      const result = await slaManagementApi.getSLAStatus(processIds)
      if (!result.success) {
        throw new Error(result.message)
      }
      return result.data
    },
    staleTime: 30 * 1000, // 30 seconds
    refetchInterval: 60 * 1000 // Refresh every minute
  })
}

export function useSLABreaches(filters?: {
  severity?: 'warning' | 'breach'
  department?: string
  dateRange?: { from: string; to: string }
}) {
  return useQuery({
    queryKey: workflowQueryKeys.slaBreaches(filters),
    queryFn: async () => {
      const result = await slaManagementApi.getSLABreaches(filters)
      if (!result.success) {
        throw new Error(result.message)
      }
      return result.data
    },
    staleTime: 2 * 60 * 1000, // 2 minutes
    refetchInterval: 30 * 1000 // Refresh every 30 seconds
  })
}

export function useSLAComplianceReport(filters?: {
  processIds?: string[]
  department?: string
  period?: '7d' | '30d' | '90d'
}) {
  return useQuery({
    queryKey: [...workflowQueryKeys.sla(), 'compliance', filters],
    queryFn: async () => {
      const result = await slaManagementApi.getSLAComplianceReport(filters)
      if (!result.success) {
        throw new Error(result.message)
      }
      return result.data
    },
    staleTime: 5 * 60 * 1000 // 5 minutes
  })
}

export function useCreateSLADefinition() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (sla: Omit<SLADefinition, 'id'>) => {
      const result = await slaManagementApi.createSLADefinition(sla)
      if (!result.success) {
        throw new Error(result.message)
      }
      return result.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: workflowQueryKeys.sla() })
      toast.success('SLA definition created successfully')
    },
    onError: (error: Error) => {
      toast.error(`Failed to create SLA definition: ${error.message}`)
    }
  })
}

export function useUpdateSLADefinition() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({ id, sla }: { id: string; sla: Partial<SLADefinition> }) => {
      const result = await slaManagementApi.updateSLADefinition(id, sla)
      if (!result.success) {
        throw new Error(result.message)
      }
      return result.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: workflowQueryKeys.sla() })
      toast.success('SLA definition updated successfully')
    },
    onError: (error: Error) => {
      toast.error(`Failed to update SLA definition: ${error.message}`)
    }
  })
}

/**
 * Combined hook for workflow section with analytics
 */
export function useWorkflowSection() {
  const metrics = useWorkflowMetrics()
  const activeWorkflows = useActiveWorkflows()
  const processes = useProcesses()
  const automationRules = useAutomationRules()
  const serviceStatus = useServiceStatus()
  const analytics = useWorkflowAnalytics()
  const slaStatus = useSLAStatus()

  return {
    metrics: metrics.data,
    activeWorkflows: activeWorkflows.data,
    processes: processes.data,
    automationRules: automationRules.data,
    serviceStatus: serviceStatus.data,
    analytics: analytics.data,
    slaStatus: slaStatus.data,
    isLoading: metrics.isLoading || activeWorkflows.isLoading || processes.isLoading || analytics.isLoading,
    error: metrics.error || activeWorkflows.error || processes.error || analytics.error,
    refetch: () => {
      metrics.refetch()
      activeWorkflows.refetch()
      processes.refetch()
      automationRules.refetch()
      analytics.refetch()
      slaStatus.refetch()
    }
  }
}