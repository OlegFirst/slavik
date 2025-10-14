/**
 * Orchestrator API Client
 * =======================
 *
 * Client for AI Orchestrator REST API (http://localhost:8050)
 */

const BASE_URL = 'http://localhost:8050';

export interface OrchestratorStats {
  total_decisions: number;
  by_action: Record<string, number>;
  by_priority: Record<string, number>;
  avg_latency_ms: number;
  auto_resolution_rate: number;
  escalation_rate: number;
  safety_approval_rate: number;
  service_registry: {
    total_services: number;
    healthy_services: number;
    services: Array<{
      name: string;
      url: string;
      status: 'healthy' | 'unhealthy';
      last_check: string;
    }>;
  };
  delegation_stats?: {
    total_delegations: number;
    by_specialist: Record<string, number>;
  };
  crisis_stats?: {
    total_crises: number;
    active_crisis_ids: string[];
    by_level: Record<string, number>;
  };
  pdca_stats?: {
    total_cycles: number;
    avg_quality_score: number;
  };
}

export interface Decision {
  id: string;
  action: string;
  priority: string;
  rationale: string;
  confidence: number;
  safety_approved: boolean;
  timestamp: string;
  execution_result?: any;
}

export interface Crisis {
  id: string;
  level: 'MINOR' | 'MAJOR' | 'CRITICAL' | 'CATASTROPHIC';
  affected_services: string[];
  detected_at: string;
  status: 'active' | 'activated' | 'resolved';
  bc_plan_activated?: boolean;
}

export interface HealthStatus {
  status: 'healthy' | 'degraded' | 'unhealthy';
  components: {
    event_bus: boolean;
    service_registry: boolean;
    decision_center: boolean;
    crisis_coordinator: boolean;
    pdca_engine: boolean;
  };
  timestamp: string;
}

class OrchestratorAPI {
  private baseUrl: string;

  constructor(baseUrl: string = BASE_URL) {
    this.baseUrl = baseUrl;
  }

  /**
   * Get orchestrator health status
   */
  async getHealth(): Promise<HealthStatus> {
    const response = await fetch(`${this.baseUrl}/health`);
    if (!response.ok) {
      throw new Error(`Health check failed: ${response.statusText}`);
    }
    return response.json();
  }

  /**
   * Get orchestrator statistics
   */
  async getStats(): Promise<OrchestratorStats> {
    const response = await fetch(`${this.baseUrl}/stats`);
    if (!response.ok) {
      throw new Error(`Failed to fetch stats: ${response.statusText}`);
    }
    return response.json();
  }

  /**
   * Make a decision
   */
  async decide(situation: any, tenantId: string = 'default'): Promise<Decision> {
    const response = await fetch(`${this.baseUrl}/api/v1/decide`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ situation, tenant_id: tenantId }),
    });
    if (!response.ok) {
      throw new Error(`Decision failed: ${response.statusText}`);
    }
    return response.json();
  }

  /**
   * Detect crisis
   */
  async detectCrisis(situation: any, tenantId: string = 'default'): Promise<Crisis | null> {
    const response = await fetch(`${this.baseUrl}/api/v1/crisis/detect`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ situation, tenant_id: tenantId }),
    });
    if (!response.ok) {
      throw new Error(`Crisis detection failed: ${response.statusText}`);
    }
    const data = await response.json();
    return data.crisis || null;
  }

  /**
   * Get crisis status
   */
  async getCrisisStatus(crisisId: string): Promise<Crisis> {
    const response = await fetch(`${this.baseUrl}/api/v1/crisis/${crisisId}/status`);
    if (!response.ok) {
      throw new Error(`Failed to get crisis status: ${response.statusText}`);
    }
    return response.json();
  }

  /**
   * Activate crisis response
   */
  async activateCrisisResponse(crisisId: string, planType: string = 'default'): Promise<any> {
    const response = await fetch(`${this.baseUrl}/api/v1/crisis/${crisisId}/activate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ plan_type: planType }),
    });
    if (!response.ok) {
      throw new Error(`Failed to activate crisis response: ${response.statusText}`);
    }
    return response.json();
  }

  /**
   * Resolve crisis
   */
  async resolveCrisis(crisisId: string): Promise<any> {
    const response = await fetch(`${this.baseUrl}/api/v1/crisis/${crisisId}/resolve`, {
      method: 'POST',
    });
    if (!response.ok) {
      throw new Error(`Failed to resolve crisis: ${response.statusText}`);
    }
    return response.json();
  }

  /**
   * Trigger evolution cycle
   */
  async triggerEvolution(): Promise<any> {
    const response = await fetch(`${this.baseUrl}/admin/evolve`, {
      method: 'POST',
    });
    if (!response.ok) {
      throw new Error(`Evolution failed: ${response.statusText}`);
    }
    return response.json();
  }

  /**
   * Clear strategy cache
   */
  async clearCache(): Promise<any> {
    const response = await fetch(`${this.baseUrl}/admin/cache/clear`, {
      method: 'POST',
    });
    if (!response.ok) {
      throw new Error(`Cache clear failed: ${response.statusText}`);
    }
    return response.json();
  }

  /**
   * Get Prometheus metrics
   */
  async getMetrics(): Promise<string> {
    const response = await fetch(`${this.baseUrl}/metrics`);
    if (!response.ok) {
      throw new Error(`Failed to fetch metrics: ${response.statusText}`);
    }
    return response.text();
  }
}

export const orchestratorAPI = new OrchestratorAPI();
