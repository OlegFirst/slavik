/**
 * BIA Service API Client
 * Real integration with backend (port 8012)
 * No mocks, no fake data
 */

import { SERVICES } from '@/config/services';
import type {
  BIAProcess,
  BIAProcessCreate,
  AIRTOSuggestion,
  BIASummaryReport,
  BulkOperationReport,
  CriticalityLevel,
  ProcessStatus
} from '@/types/bia';

const BIA_BASE_URL = SERVICES.BIA.url;

class BIAAPIError extends Error {
  constructor(
    message: string,
    public status: number,
    public response?: any
  ) {
    super(message);
    this.name = 'BIAAPIError';
  }
}

async function request<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${BIA_BASE_URL}${endpoint}`;

  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new BIAAPIError(
      error.detail || 'Request failed',
      response.status,
      error
    );
  }

  return response.json();
}

export const biaAPI = {
  // ==================== PROCESSES ====================

  /**
   * List BIA processes with optional filters
   */
  async listProcesses(params: {
    tenant_id: string;
    criticality?: CriticalityLevel;
    status?: ProcessStatus;
  }): Promise<BIAProcess[]> {
    const searchParams = new URLSearchParams();
    searchParams.append('tenant_id', params.tenant_id);
    if (params.criticality) searchParams.append('criticality', params.criticality);
    if (params.status) searchParams.append('status', params.status);

    return request<BIAProcess[]>(
      `/api/bia/processes?${searchParams.toString()}`
    );
  },

  /**
   * Get single BIA process by ID
   */
  async getProcess(id: number, tenant_id: string): Promise<BIAProcess> {
    return request<BIAProcess>(
      `/api/bia/processes/${id}?tenant_id=${tenant_id}`
    );
  },

  /**
   * Create new BIA process
   */
  async createProcess(data: BIAProcessCreate): Promise<BIAProcess> {
    return request<BIAProcess>(
      '/api/bia/processes',
      {
        method: 'POST',
        body: JSON.stringify(data),
      }
    );
  },

  /**
   * Update existing BIA process
   */
  async updateProcess(
    id: number,
    tenant_id: string,
    updates: Partial<BIAProcess>
  ): Promise<BIAProcess> {
    return request<BIAProcess>(
      `/api/bia/processes/${id}?tenant_id=${tenant_id}`,
      {
        method: 'PUT',
        body: JSON.stringify(updates),
      }
    );
  },

  /**
   * Delete BIA process
   */
  async deleteProcess(id: number, tenant_id: string): Promise<{ status: string; process_id: number }> {
    return request(
      `/api/bia/processes/${id}?tenant_id=${tenant_id}`,
      {
        method: 'DELETE',
      }
    );
  },

  /**
   * Mark process as completed
   */
  async completeProcess(id: number, tenant_id: string): Promise<{ status: string; process: BIAProcess }> {
    return request(
      `/api/bia/processes/${id}/complete?tenant_id=${tenant_id}`,
      {
        method: 'POST',
      }
    );
  },

  // ==================== AI FEATURES ====================

  /**
   * Get AI-powered RTO suggestion
   */
  async getAISuggestion(params: {
    name: string;
    industry: string;
    criticality: CriticalityLevel;
    financial_impact: Record<string, number>;
    staff_count?: number;
  }): Promise<AIRTOSuggestion> {
    return request<AIRTOSuggestion>(
      '/api/bia/ai/suggest-rto',
      {
        method: 'POST',
        body: JSON.stringify(params),
      }
    );
  },

  /**
   * AI: Analyze process criticality
   * Uses BIA Specialist AI to analyze process and recommend RTO/RPO
   */
  async analyzeProcessCriticality(params: {
    name: string;
    description?: string;
    department?: string;
    revenue_impact?: number;
    regulatory?: boolean;
    customer_impact?: string;
    tenant_id?: string;
  }): Promise<{
    criticality_analysis: string;
    recommendations: any;
    confidence: number;
    metadata: any;
  }> {
    return request(
      '/api/bia/ai/analyze-criticality',
      {
        method: 'POST',
        body: JSON.stringify(params),
      }
    );
  },

  /**
   * AI: Map process dependencies
   * Uses BIA Specialist AI to identify upstream/downstream dependencies
   */
  async mapDependencies(params: {
    name: string;
    function?: string;
    tenant_id?: string;
  }): Promise<{
    dependency_map: string;
    risks: any;
    confidence: number;
    metadata: any;
  }> {
    return request(
      '/api/bia/ai/map-dependencies',
      {
        method: 'POST',
        body: JSON.stringify(params),
      }
    );
  },

  /**
   * AI: Calculate impact over time
   * Uses BIA Specialist AI to calculate time-based impact curve
   */
  async calculateImpactOverTime(params: {
    name: string;
    daily_revenue?: number;
    customers?: number;
    tenant_id?: string;
  }): Promise<{
    impact_curve: string;
    critical_timeframes: any;
    confidence: number;
    metadata: any;
  }> {
    return request(
      '/api/bia/ai/calculate-impact',
      {
        method: 'POST',
        body: JSON.stringify(params),
      }
    );
  },

  /**
   * AI: Conduct comprehensive BIA
   * Uses BIA Specialist AI to conduct full BIA for organization
   */
  async conductBIA(params: {
    name: string;
    industry: string;
    size?: number;
    processes?: any[];
    tenant_id?: string;
  }): Promise<{
    bia_report: string;
    critical_processes: any;
    confidence: number;
    metadata: any;
  }> {
    return request(
      '/api/bia/ai/conduct-bia',
      {
        method: 'POST',
        body: JSON.stringify(params),
      }
    );
  },

  /**
   * AI: Suggest recovery strategies
   * Uses BIA Specialist AI to suggest recovery strategies based on RTO and dependencies
   */
  async suggestRecoveryStrategies(params: {
    name: string;
    rto_hours: number;
    dependencies?: any[];
    tenant_id?: string;
  }): Promise<{
    strategies: any[];
    confidence: number;
    metadata: any;
  }> {
    return request(
      '/api/bia/ai/suggest-strategies',
      {
        method: 'POST',
        body: JSON.stringify(params),
      }
    );
  },

  // ==================== REPORTS ====================

  /**
   * Get BIA summary report for tenant
   */
  async getSummaryReport(tenant_id: string): Promise<BIASummaryReport> {
    return request<BIASummaryReport>(
      `/api/bia/reports/summary?tenant_id=${tenant_id}`
    );
  },

  // ==================== BULK OPERATIONS ====================

  /**
   * Bulk create BIA processes
   */
  async bulkCreateProcesses(
    processes: BIAProcessCreate[],
    max_concurrency: number = 10
  ): Promise<BulkOperationReport> {
    return request<BulkOperationReport>(
      '/api/bia/processes/bulk',
      {
        method: 'POST',
        body: JSON.stringify({
          processes,
          max_concurrency
        }),
      }
    );
  },

  /**
   * Bulk update BIA processes
   */
  async bulkUpdateProcesses(
    updates: Array<{ process_id: number; [key: string]: any }>,
    tenant_id: string,
    max_concurrency: number = 10
  ): Promise<BulkOperationReport> {
    return request<BulkOperationReport>(
      `/api/bia/processes/bulk/update?tenant_id=${tenant_id}`,
      {
        method: 'PUT',
        body: JSON.stringify({
          updates,
          max_concurrency
        }),
      }
    );
  },

  /**
   * Bulk delete BIA processes
   */
  async bulkDeleteProcesses(
    process_ids: number[],
    tenant_id: string,
    max_concurrency: number = 10
  ): Promise<BulkOperationReport> {
    return request<BulkOperationReport>(
      `/api/bia/processes/bulk/delete?tenant_id=${tenant_id}`,
      {
        method: 'DELETE',
        body: JSON.stringify({
          process_ids,
          max_concurrency
        }),
      }
    );
  },

  /**
   * Bulk validate processes before creation
   */
  async bulkValidateProcesses(
    processes: BIAProcessCreate[],
    max_concurrency: number = 20
  ): Promise<BulkOperationReport> {
    return request<BulkOperationReport>(
      '/api/bia/processes/bulk/validate',
      {
        method: 'POST',
        body: JSON.stringify({
          processes,
          max_concurrency
        }),
      }
    );
  },

  // ==================== HEALTH CHECK ====================

  /**
   * Check BIA service health
   */
  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    return request('/health');
  },
};

export { BIAAPIError };
export type { BIAProcess, BIAProcessCreate, AIRTOSuggestion, BIASummaryReport };
