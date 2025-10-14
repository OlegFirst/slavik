/**
 * Temporary Database Client Stub
 * TODO: Connect to real Supabase when ready
 */

export interface HealthStatus {
  service: string;
  status: 'healthy' | 'warning' | 'error';
  uptime?: string;
  lastCheck?: string;
}

class CentralizedDBClient {
  async checkHealth(): Promise<HealthStatus[]> {
    // Mock data for now
    // TODO: Replace with real Supabase queries
    return [
      {
        service: 'bia-service',
        status: 'healthy',
        uptime: '99.9%',
        lastCheck: new Date().toISOString()
      },
      {
        service: 'risk-service',
        status: 'healthy',
        uptime: '99.8%',
        lastCheck: new Date().toISOString()
      },
      {
        service: 'compliance-service',
        status: 'warning',
        uptime: '98.5%',
        lastCheck: new Date().toISOString()
      }
    ];
  }

  async query(sql: string): Promise<any[]> {
    // Mock query
    console.warn('CentralizedDB.query() is a stub. Query:', sql);
    return [];
  }
}

export const centralizedDB = new CentralizedDBClient();
