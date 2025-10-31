import { bcmAPI } from './api';

// Real BCM Data Service - Integration with Odoo BCM Platform
// Connects to actual BCM modules and retrieves live compliance data

export interface BCMModule {
  id: number;
  name: string;
  module_name: string;
  version: string;
  status: 'installed' | 'to_upgrade' | 'to_install' | 'uninstalled';
  dependencies: string[];
  summary: string;
  category: string;
  compliance_score?: number;
  last_audit?: string;
}

export interface ComplianceStatus {
  id: number;
  organization_name: string;
  iso22301_status: 'compliant' | 'partially_compliant' | 'non_compliant';
  compliance_percentage: number;
  last_assessment_date: string;
  next_review_date: string;
  critical_findings: number;
  open_actions: number;
  risk_level: 'low' | 'medium' | 'high' | 'critical';
}

export interface RiskAssessment {
  id: number;
  risk_name: string;
  category: string;
  likelihood: number;
  impact: number;
  risk_score: number;
  mitigation_status: 'open' | 'in_progress' | 'closed';
  owner: string;
  due_date: string;
  last_review: string;
}

export interface BIAResult {
  id: number;
  business_process: string;
  criticality: 'critical' | 'important' | 'supporting';
  rto: number; // Recovery Time Objective (hours)
  rpo: number; // Recovery Point Objective (hours)
  mtpd: number; // Maximum Tolerable Period of Disruption
  impact_financial: number;
  impact_operational: string;
  dependencies: string[];
  last_updated: string;
}

export interface IncidentRecord {
  id: number;
  incident_type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  status: 'open' | 'investigating' | 'resolved' | 'closed';
  reported_date: string;
  resolved_date?: string;
  impact_description: string;
  response_time_minutes: number;
  recovery_time_minutes?: number;
  lessons_learned?: string;
}

export interface AuditFinding {
  id: number;
  audit_id: number;
  clause_reference: string;
  finding_type: 'non_conformity' | 'opportunity' | 'observation';
  description: string;
  evidence: string;
  corrective_action: string;
  responsible_person: string;
  target_date: string;
  status: 'open' | 'in_progress' | 'closed' | 'verified';
  priority: 'low' | 'medium' | 'high';
}

export interface KPIMetric {
  id: number;
  metric_name: string;
  category: string;
  current_value: number;
  target_value: number;
  unit: string;
  trend: 'improving' | 'stable' | 'declining';
  last_updated: string;
  frequency: 'daily' | 'weekly' | 'monthly' | 'quarterly';
  threshold_warning: number;
  threshold_critical: number;
}

export interface DigitalTwinMetrics {
  organization_id: number;
  resilience_score: number;
  business_continuity_index: number;
  risk_exposure: number;
  recovery_readiness: number;
  compliance_maturity: number;
  simulation_results: {
    scenario_name: string;
    predicted_impact: number;
    recovery_time_estimate: number;
    confidence_level: number;
  }[];
  last_simulation: string;
}

// BCM Real Data Service
export const bcmRealDataService = {
  // Module Management
  async getInstalledModules(): Promise<BCMModule[]> {
    try {
      const response = await bcmAPI.get('/api/bcm/modules/installed');
      return response.data || [];
    } catch (error) {
      console.error('Error fetching BCM modules:', error);
      return [];
    }
  },

  async getModuleStatus(moduleName: string): Promise<BCMModule | null> {
    try {
      const response = await bcmAPI.get(`/api/bcm/modules/${moduleName}/status`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching module ${moduleName} status:`, error);
      return null;
    }
  },

  // Compliance Management
  async getComplianceOverview(): Promise<ComplianceStatus[]> {
    try {
      const response = await bcmAPI.get('/api/bcm/compliance/overview');
      return response.data || [];
    } catch (error) {
      console.error('Error fetching compliance overview:', error);
      return [];
    }
  },

  async getComplianceByOrganization(orgId: number): Promise<ComplianceStatus | null> {
    try {
      const response = await bcmAPI.get(`/api/bcm/compliance/organization/${orgId}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching compliance for org ${orgId}:`, error);
      return null;
    }
  },

  // Risk Management
  async getRiskAssessments(): Promise<RiskAssessment[]> {
    try {
      const response = await bcmAPI.get('/api/bcm/risk/assessments');
      return response.data || [];
    } catch (error) {
      console.error('Error fetching risk assessments:', error);
      return [];
    }
  },

  async getHighPriorityRisks(): Promise<RiskAssessment[]> {
    try {
      const response = await bcmAPI.get('/api/bcm/risk/high-priority');
      return response.data || [];
    } catch (error) {
      console.error('Error fetching high priority risks:', error);
      return [];
    }
  },

  // Business Impact Analysis
  async getBIAResults(): Promise<BIAResult[]> {
    try {
      const response = await bcmAPI.get('/api/bcm/bia/results');
      return response.data || [];
    } catch (error) {
      console.error('Error fetching BIA results:', error);
      return [];
    }
  },

  async getCriticalProcesses(): Promise<BIAResult[]> {
    try {
      const response = await bcmAPI.get('/api/bcm/bia/critical-processes');
      return response.data || [];
    } catch (error) {
      console.error('Error fetching critical processes:', error);
      return [];
    }
  },

  // Incident Management
  async getIncidents(): Promise<IncidentRecord[]> {
    try {
      const response = await bcmAPI.get('/api/bcm/incidents');
      return response.data || [];
    } catch (error) {
      console.error('Error fetching incidents:', error);
      return [];
    }
  },

  async getActiveIncidents(): Promise<IncidentRecord[]> {
    try {
      const response = await bcmAPI.get('/api/bcm/incidents/active');
      return response.data || [];
    } catch (error) {
      console.error('Error fetching active incidents:', error);
      return [];
    }
  },

  // Audit Management
  async getAuditFindings(): Promise<AuditFinding[]> {
    try {
      const response = await bcmAPI.get('/api/bcm/audit/findings');
      return response.data || [];
    } catch (error) {
      console.error('Error fetching audit findings:', error);
      return [];
    }
  },

  async getOpenFindings(): Promise<AuditFinding[]> {
    try {
      const response = await bcmAPI.get('/api/bcm/audit/findings/open');
      return response.data || [];
    } catch (error) {
      console.error('Error fetching open findings:', error);
      return [];
    }
  },

  // KPI Management
  async getKPIMetrics(): Promise<KPIMetric[]> {
    try {
      const response = await bcmAPI.get('/api/bcm/kpi/metrics');
      return response.data || [];
    } catch (error) {
      console.error('Error fetching KPI metrics:', error);
      return [];
    }
  },

  async getKPIDashboard(): Promise<{
    total_metrics: number;
    on_target: number;
    warning: number;
    critical: number;
    trending_up: number;
    trending_down: number;
  }> {
    try {
      const response = await bcmAPI.get('/api/bcm/kpi/dashboard');
      return response.data || {
        total_metrics: 0,
        on_target: 0,
        warning: 0,
        critical: 0,
        trending_up: 0,
        trending_down: 0
      };
    } catch (error) {
      console.error('Error fetching KPI dashboard:', error);
      return {
        total_metrics: 0,
        on_target: 0,
        warning: 0,
        critical: 0,
        trending_up: 0,
        trending_down: 0
      };
    }
  },

  // Digital Twin Analytics
  async getDigitalTwinMetrics(orgId?: number): Promise<DigitalTwinMetrics | null> {
    try {
      const url = orgId ?
        `/api/bcm/digital-twin/metrics/${orgId}` :
        '/api/bcm/digital-twin/metrics';
      const response = await bcmAPI.get(url);
      return response.data;
    } catch (error) {
      console.error('Error fetching digital twin metrics:', error);
      return null;
    }
  },

  async runScenarioSimulation(scenarioId: number): Promise<{
    simulation_id: string;
    status: 'running' | 'completed' | 'failed';
    estimated_completion: string;
  }> {
    try {
      const response = await bcmAPI.post(`/api/bcm/digital-twin/simulate/${scenarioId}`);
      return response.data;
    } catch (error) {
      console.error('Error running scenario simulation:', error);
      throw error;
    }
  },

  // Platform Health & Monitoring
  async getPlatformHealth(): Promise<{
    overall_status: 'healthy' | 'warning' | 'critical';
    modules_status: { [key: string]: 'active' | 'inactive' | 'error' };
    database_status: 'connected' | 'disconnected' | 'slow';
    cache_hit_rate: number;
    api_response_time: number;
    active_users: number;
    system_load: number;
  }> {
    try {
      const response = await bcmAPI.get('/api/bcm/platform/health');
      return response.data;
    } catch (error) {
      console.error('Error fetching platform health:', error);
      return {
        overall_status: 'critical',
        modules_status: {},
        database_status: 'disconnected',
        cache_hit_rate: 0,
        api_response_time: 0,
        active_users: 0,
        system_load: 0
      };
    }
  },

  // AI Organs Integration
  async getAIOrganStatus(): Promise<{
    total_organs: number;
    active_organs: number;
    processing_requests: number;
    avg_response_time: number;
    token_usage_today: number;
    organs: Array<{
      name: string;
      status: 'active' | 'busy' | 'offline';
      load_percentage: number;
      last_activity: string;
    }>;
  }> {
    try {
      const response = await bcmAPI.get('/api/bcm/ai-organs/status');
      return response.data;
    } catch (error) {
      console.error('Error fetching AI organ status:', error);
      return {
        total_organs: 0,
        active_organs: 0,
        processing_requests: 0,
        avg_response_time: 0,
        token_usage_today: 0,
        organs: []
      };
    }
  },

  // Real-time Updates
  async subscribeToUpdates(callback: (update: any) => void): Promise<() => void> {
    // WebSocket connection for real-time updates
    try {
      const ws = new WebSocket('ws://localhost:8888/ws/bcm-updates');

      ws.onmessage = (event) => {
        try {
          const update = JSON.parse(event.data);
          callback(update);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

      // Return cleanup function
      return () => {
        ws.close();
      };
    } catch (error) {
      console.error('Error establishing WebSocket connection:', error);
      return () => {}; // Empty cleanup function
    }
  },

  // Cache Management
  async clearCache(cacheType?: 'compliance' | 'risk' | 'bia' | 'audit' | 'kpi' | 'all'): Promise<boolean> {
    try {
      const response = await bcmAPI.delete('/api/bcm/cache/clear', {
        params: { type: cacheType || 'all' }
      });
      return response.data.success || false;
    } catch (error) {
      console.error('Error clearing cache:', error);
      return false;
    }
  },

  async getCacheStats(): Promise<{
    hit_rate: number;
    total_requests: number;
    cache_size_mb: number;
    contexts: { [key: string]: { keys: number; size_mb: number } };
  }> {
    try {
      const response = await bcmAPI.get('/api/bcm/cache/stats');
      return response.data;
    } catch (error) {
      console.error('Error fetching cache stats:', error);
      return {
        hit_rate: 0,
        total_requests: 0,
        cache_size_mb: 0,
        contexts: {}
      };
    }
  }
};

// Cached versions of frequently accessed data
export const bcmCachedService = {
  // Cache for 5 minutes
  async getComplianceOverviewCached(): Promise<ComplianceStatus[]> {
    const cacheKey = 'compliance_overview';
    const cached = localStorage.getItem(cacheKey);
    const cacheTime = localStorage.getItem(`${cacheKey}_time`);

    if (cached && cacheTime) {
      const age = Date.now() - parseInt(cacheTime);
      if (age < 300000) { // 5 minutes
        return JSON.parse(cached);
      }
    }

    const data = await bcmRealDataService.getComplianceOverview();
    localStorage.setItem(cacheKey, JSON.stringify(data));
    localStorage.setItem(`${cacheKey}_time`, Date.now().toString());
    return data;
  },

  // Cache for 10 minutes
  async getKPIDashboardCached() {
    const cacheKey = 'kpi_dashboard';
    const cached = localStorage.getItem(cacheKey);
    const cacheTime = localStorage.getItem(`${cacheKey}_time`);

    if (cached && cacheTime) {
      const age = Date.now() - parseInt(cacheTime);
      if (age < 600000) { // 10 minutes
        return JSON.parse(cached);
      }
    }

    const data = await bcmRealDataService.getKPIDashboard();
    localStorage.setItem(cacheKey, JSON.stringify(data));
    localStorage.setItem(`${cacheKey}_time`, Date.now().toString());
    return data;
  }
};

export default bcmRealDataService;