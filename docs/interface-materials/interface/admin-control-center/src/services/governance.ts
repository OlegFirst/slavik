/**
 * Infrastructure Governance Service API Client
 *
 * REAL API integration for Phase 1.1 Governance Layer
 * Connects to Infrastructure Coordinator and Decision Center (port 9091)
 */

import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_GOVERNANCE_API_URL || 'http://localhost:9091';

// Create axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    console.log(`[Governance API] ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('[Governance API] Request error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => {
    console.log(`[Governance API] Response:`, response.status);
    return response;
  },
  (error) => {
    console.error('[Governance API] Error:', error.response?.status, error.message);
    return Promise.reject(error);
  }
);

// ============================================================================
// Types
// ============================================================================

export interface GovernanceHealth {
  status: string;
  decision_center_active: boolean;
  policy_engine_loaded: boolean;
  escalation_manager_active: boolean;
  total_policies: number;
  governance_maturity_score: number;
}

export interface Decision {
  id: string;
  timestamp: string;
  service_name: string;
  action_type: string;
  decision: 'APPROVE' | 'REJECT' | 'ESCALATE' | 'PENDING';
  reasoning: string;
  policy_matched: string;
  requires_approval: boolean;
  escalation_level?: number;
  approved_by?: string;
}

export interface Escalation {
  id: string;
  timestamp: string;
  service_name: string;
  action_type: string;
  level: number;
  trigger: string;
  status: 'ACTIVE' | 'RESOLVED' | 'APPROVED';
  decision_id: string;
  notified_channels: string[];
  resolved_at?: string;
  resolved_by?: string;
}

export interface PolicySummary {
  total_policies: number;
  critical_services: number;
  recovery_policies: number;
  optimization_policies: number;
  escalation_rules: number;
  last_reload: string;
}

export interface AuditEntry {
  timestamp: string;
  action: string;
  service: string;
  decision: string;
  reasoning: string;
  user?: string;
  metadata: Record<string, any>;
}

export interface GovernanceStats {
  total_decisions: number;
  decisions_approved: number;
  decisions_rejected: number;
  decisions_escalated: number;
  active_escalations: number;
  resolved_escalations: number;
  policy_compliance_rate: number;
  avg_decision_time_ms: number;
  governance_maturity_score: number;
}

export interface DecisionRequest {
  service_name: string;
  action_type: 'recovery' | 'optimization' | 'configuration';
  current_attempt?: number;
  recommendation?: Record<string, any>;
}

export interface ApprovalRequest {
  decision_id: string;
  approved_by: string;
  notes?: string;
}

export interface EscalationResolveRequest {
  escalation_id: string;
  resolved_by: string;
  resolution_notes: string;
}

// ============================================================================
// API Methods
// ============================================================================

export const governanceService = {
  /**
   * Get governance health status
   * GET /governance/health
   */
  async getHealth(): Promise<GovernanceHealth> {
    const response = await apiClient.get('/governance/health');
    return response.data;
  },

  /**
   * Get governance statistics
   * GET /governance/stats
   */
  async getStats(): Promise<GovernanceStats> {
    const response = await apiClient.get('/governance/stats');
    return response.data;
  },

  /**
   * Get recent decisions (with pagination)
   * GET /governance/decisions
   */
  async getDecisions(limit: number = 50, offset: number = 0): Promise<Decision[]> {
    const response = await apiClient.get('/governance/decisions', {
      params: { limit, offset }
    });
    return response.data;
  },

  /**
   * Get specific decision by ID
   * GET /governance/decisions/:id
   */
  async getDecision(id: string): Promise<Decision> {
    const response = await apiClient.get(`/governance/decisions/${id}`);
    return response.data;
  },

  /**
   * Get active escalations
   * GET /governance/escalations
   */
  async getEscalations(status: 'ACTIVE' | 'RESOLVED' | 'ALL' = 'ACTIVE'): Promise<Escalation[]> {
    const response = await apiClient.get('/governance/escalations', {
      params: { status }
    });
    return response.data;
  },

  /**
   * Get policy summary
   * GET /governance/policies
   */
  async getPolicySummary(): Promise<PolicySummary> {
    const response = await apiClient.get('/governance/policies');
    return response.data;
  },

  /**
   * Get audit trail
   * GET /governance/audit
   */
  async getAuditTrail(limit: number = 100, service?: string): Promise<AuditEntry[]> {
    const response = await apiClient.get('/governance/audit', {
      params: { limit, service }
    });
    return response.data;
  },

  /**
   * Request a decision from Decision Center
   * POST /governance/decide
   */
  async requestDecision(request: DecisionRequest): Promise<Decision> {
    const response = await apiClient.post('/governance/decide', request);
    return response.data;
  },

  /**
   * Approve a pending decision
   * POST /governance/approve
   */
  async approveDecision(request: ApprovalRequest): Promise<Decision> {
    const response = await apiClient.post('/governance/approve', request);
    return response.data;
  },

  /**
   * Reject a pending decision
   * POST /governance/reject
   */
  async rejectDecision(request: ApprovalRequest): Promise<Decision> {
    const response = await apiClient.post('/governance/reject', request);
    return response.data;
  },

  /**
   * Resolve an escalation
   * POST /governance/escalations/:id/resolve
   */
  async resolveEscalation(request: EscalationResolveRequest): Promise<Escalation> {
    const response = await apiClient.post(
      `/governance/escalations/${request.escalation_id}/resolve`,
      request
    );
    return response.data;
  },

  /**
   * Reload policies from YAML (hot-reload)
   * POST /governance/policies/reload
   */
  async reloadPolicies(): Promise<PolicySummary> {
    const response = await apiClient.post('/governance/policies/reload');
    return response.data;
  },

  /**
   * Get Prometheus metrics
   * GET /metrics
   */
  async getMetrics(): Promise<string> {
    const response = await apiClient.get('/metrics');
    return response.data;
  },

  /**
   * Parse Prometheus metrics
   */
  parseMetrics(metricsText: string): Record<string, number> {
    const metrics: Record<string, number> = {};
    const lines = metricsText.split('\n');

    for (const line of lines) {
      if (line.startsWith('#') || !line.trim()) continue;

      const parts = line.split(' ');
      if (parts.length >= 2) {
        const key = parts[0];
        const value = parseFloat(parts[1]);

        if (!isNaN(value)) {
          metrics[key] = value;
        }
      }
    }

    return metrics;
  },

  /**
   * Subscribe to real-time events via EventBus
   * (For WebSocket integration if available)
   */
  subscribeToEvents(callback: (event: any) => void): () => void {
    // This would use WebSocket or EventSource for real-time updates
    // For now, return cleanup function
    console.log('[Governance] Event subscription feature pending');
    return () => {};
  },
};

export default governanceService;
