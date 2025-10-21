// BCM Clients Management Service Architecture
// Интеграция: Admin Panel ↔ Odoo ↔ Client Database

import { API_ENDPOINTS } from './bcm';

export interface Client {
  id: string;
  name: string;
  type: 'enterprise' | 'government' | 'nonprofit' | 'startup';
  industry: string;
  size: 'small' | 'medium' | 'large' | 'enterprise';
  status: 'active' | 'inactive' | 'prospect' | 'churned';
  contact_person: string;
  email: string;
  phone: string;
  address: string;
  bcm_maturity_level: 1 | 2 | 3 | 4 | 5;
  compliance_frameworks: string[];
  modules_subscribed: string[];
  risk_profile: 'low' | 'medium' | 'high' | 'critical';
  last_assessment_date: string;
  next_review_date: string;
  created_date: string;
  last_activity: string;
  contract_status: 'active' | 'expired' | 'pending_renewal';
  annual_revenue: number;
  employee_count: number;
  odoo_partner_id?: number;
}

export interface ClientMetrics {
  total_clients: number;
  active_clients: number;
  new_clients_this_month: number;
  clients_by_type: Record<Client['type'], number>;
  clients_by_industry: Record<string, number>;
  average_maturity_level: number;
  high_risk_clients: number;
}

export const clientService = {

  // ======================================
  // LAYER 1: Admin Panel Client Management
  // ======================================

  // Get all clients for admin management
  async getAdminClients(): Promise<Client[]> {
    try {
      console.log(' Fetching clients for admin management...');

      // Get clients from Odoo partners with BCM subscription
      const odooClients = await this.getOdooClients();

      return odooClients;
    } catch (error) {
      console.error(' Failed to fetch admin clients:', error);
      return this.getFallbackClients();
    }
  },

  // Get client metrics for dashboard
  async getClientMetrics(): Promise<ClientMetrics> {
    try {
      const clients = await this.getAdminClients();

      return {
        total_clients: clients.length,
        active_clients: clients.filter(c => c.status === 'active').length,
        new_clients_this_month: clients.filter(c => {
          const createdDate = new Date(c.created_date);
          const oneMonthAgo = new Date();
          oneMonthAgo.setMonth(oneMonthAgo.getMonth() - 1);
          return createdDate >= oneMonthAgo;
        }).length,
        clients_by_type: this.groupByField(clients, 'type'),
        clients_by_industry: this.groupByField(clients, 'industry'),
        average_maturity_level: clients.reduce((sum, c) => sum + c.bcm_maturity_level, 0) / clients.length,
        high_risk_clients: clients.filter(c => c.risk_profile === 'high' || c.risk_profile === 'critical').length
      };
    } catch (error) {
      console.error(' Failed to fetch client metrics:', error);
      return this.getFallbackMetrics();
    }
  },

  // Create new client
  async createClient(clientData: Omit<Client, 'id' | 'created_date' | 'last_activity'>): Promise<boolean> {
    try {
      console.log(' Creating new client...');

      const response = await fetch(`${API_ENDPOINTS.ODOO_BCM}/web/dataset/call_kw/res.partner/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          params: {
            vals: {
              name: clientData.name,
              email: clientData.email,
              phone: clientData.phone,
              street: clientData.address,
              is_bcm_client: true,
              bcm_client_type: clientData.type,
              bcm_industry: clientData.industry,
              bcm_company_size: clientData.size,
              bcm_status: clientData.status,
              bcm_maturity_level: clientData.bcm_maturity_level,
              bcm_risk_profile: clientData.risk_profile,
              bcm_compliance_frameworks: clientData.compliance_frameworks.join(','),
              bcm_modules_subscribed: clientData.modules_subscribed.join(','),
              bcm_contact_person: clientData.contact_person,
              bcm_contract_status: clientData.contract_status,
              bcm_annual_revenue: clientData.annual_revenue,
              bcm_employee_count: clientData.employee_count
            }
          }
        })
      });

      return response.ok;
    } catch (error) {
      console.error(' Failed to create client:', error);
      return false;
    }
  },

  // Update client information
  async updateClient(clientId: string, updates: Partial<Client>): Promise<boolean> {
    try {
      console.log(` Updating client ${clientId}...`);

      const response = await fetch(`${API_ENDPOINTS.ODOO_BCM}/web/dataset/call_kw/res.partner/write`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          params: {
            ids: [parseInt(clientId)],
            vals: this.mapClientToOdooVals(updates)
          }
        })
      });

      return response.ok;
    } catch (error) {
      console.error(' Failed to update client:', error);
      return false;
    }
  },

  // ======================================
  // LAYER 2: Odoo Integration
  // ======================================

  // Get clients from Odoo partners
  async getOdooClients(): Promise<Client[]> {
    try {
      const response = await fetch(`${API_ENDPOINTS.ODOO_BCM}/web/dataset/call_kw/res.partner/search_read`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          params: {
            domain: [['is_bcm_client', '=', true]],
            fields: [
              'name', 'email', 'phone', 'street', 'bcm_client_type', 'bcm_industry',
              'bcm_company_size', 'bcm_status', 'bcm_maturity_level', 'bcm_risk_profile',
              'bcm_compliance_frameworks', 'bcm_modules_subscribed', 'bcm_contact_person',
              'bcm_contract_status', 'bcm_annual_revenue', 'bcm_employee_count',
              'create_date', 'write_date', 'bcm_last_assessment_date', 'bcm_next_review_date'
            ]
          }
        })
      });

      if (response.ok) {
        const result = await response.json();
        return (result.result || []).map(this.mapOdooToClient);
      }
      return [];
    } catch (error) {
      console.warn('Odoo clients unavailable:', error);
      return [];
    }
  },

  // ======================================
  // UTILITY FUNCTIONS
  // ======================================

  // Map Odoo record to Client interface
  mapOdooToClient(odooRecord: any): Client {
    return {
      id: odooRecord.id.toString(),
      name: odooRecord.name || '',
      type: odooRecord.bcm_client_type || 'enterprise',
      industry: odooRecord.bcm_industry || 'Technology',
      size: odooRecord.bcm_company_size || 'medium',
      status: odooRecord.bcm_status || 'active',
      contact_person: odooRecord.bcm_contact_person || '',
      email: odooRecord.email || '',
      phone: odooRecord.phone || '',
      address: odooRecord.street || '',
      bcm_maturity_level: odooRecord.bcm_maturity_level || 1,
      compliance_frameworks: odooRecord.bcm_compliance_frameworks ?
        odooRecord.bcm_compliance_frameworks.split(',') : ['ISO 22301'],
      modules_subscribed: odooRecord.bcm_modules_subscribed ?
        odooRecord.bcm_modules_subscribed.split(',') : [],
      risk_profile: odooRecord.bcm_risk_profile || 'medium',
      last_assessment_date: odooRecord.bcm_last_assessment_date || '',
      next_review_date: odooRecord.bcm_next_review_date || '',
      created_date: odooRecord.create_date,
      last_activity: odooRecord.write_date,
      contract_status: odooRecord.bcm_contract_status || 'active',
      annual_revenue: odooRecord.bcm_annual_revenue || 0,
      employee_count: odooRecord.bcm_employee_count || 0,
      odoo_partner_id: odooRecord.id
    };
  },

  // Map Client updates to Odoo vals
  mapClientToOdooVals(client: Partial<Client>): any {
    const vals: any = {};

    if (client.name) vals.name = client.name;
    if (client.email) vals.email = client.email;
    if (client.phone) vals.phone = client.phone;
    if (client.address) vals.street = client.address;
    if (client.type) vals.bcm_client_type = client.type;
    if (client.industry) vals.bcm_industry = client.industry;
    if (client.size) vals.bcm_company_size = client.size;
    if (client.status) vals.bcm_status = client.status;
    if (client.bcm_maturity_level) vals.bcm_maturity_level = client.bcm_maturity_level;
    if (client.risk_profile) vals.bcm_risk_profile = client.risk_profile;
    if (client.compliance_frameworks) vals.bcm_compliance_frameworks = client.compliance_frameworks.join(',');
    if (client.modules_subscribed) vals.bcm_modules_subscribed = client.modules_subscribed.join(',');
    if (client.contact_person) vals.bcm_contact_person = client.contact_person;
    if (client.contract_status) vals.bcm_contract_status = client.contract_status;
    if (client.annual_revenue) vals.bcm_annual_revenue = client.annual_revenue;
    if (client.employee_count) vals.bcm_employee_count = client.employee_count;

    return vals;
  },

  // Group clients by field
  groupByField(clients: Client[], field: keyof Client): Record<string, number> {
    return clients.reduce((acc, client) => {
      const key = String(client[field]);
      acc[key] = (acc[key] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);
  },

  // Fallback clients when Odoo unavailable
  getFallbackClients(): Client[] {
    return [
      {
        id: '1',
        name: 'TechCorp Solutions',
        type: 'enterprise',
        industry: 'Technology',
        size: 'large',
        status: 'active',
        contact_person: 'John Smith',
        email: 'john.smith@techcorp.com',
        phone: '+1-555-0123',
        address: '123 Tech Street, Silicon Valley, CA',
        bcm_maturity_level: 4,
        compliance_frameworks: ['ISO 22301', 'SOC 2'],
        modules_subscribed: ['BCM Core', 'BCM Risk Management', 'BCM BIA'],
        risk_profile: 'medium',
        last_assessment_date: '2024-08-15',
        next_review_date: '2024-12-15',
        created_date: '2023-01-15T00:00:00Z',
        last_activity: '2024-09-10T00:00:00Z',
        contract_status: 'active',
        annual_revenue: 50000000,
        employee_count: 500
      },
      {
        id: '2',
        name: 'Government Agency XYZ',
        type: 'government',
        industry: 'Government',
        size: 'enterprise',
        status: 'active',
        contact_person: 'Jane Doe',
        email: 'jane.doe@gov.agency',
        phone: '+1-555-0456',
        address: '456 Government Ave, Washington, DC',
        bcm_maturity_level: 5,
        compliance_frameworks: ['ISO 22301', 'NIST', 'FedRAMP'],
        modules_subscribed: ['BCM Core', 'BCM Governance', 'BCM AI Control'],
        risk_profile: 'high',
        last_assessment_date: '2024-09-01',
        next_review_date: '2025-01-01',
        created_date: '2022-06-01T00:00:00Z',
        last_activity: '2024-09-15T00:00:00Z',
        contract_status: 'active',
        annual_revenue: 0,
        employee_count: 1200
      }
    ];
  },

  // Fallback metrics when Odoo unavailable
  getFallbackMetrics(): ClientMetrics {
    return {
      total_clients: 25,
      active_clients: 22,
      new_clients_this_month: 3,
      clients_by_type: {
        enterprise: 15,
        government: 5,
        nonprofit: 3,
        startup: 2
      },
      clients_by_industry: {
        'Technology': 10,
        'Finance': 5,
        'Healthcare': 4,
        'Government': 5,
        'Other': 1
      },
      average_maturity_level: 3.2,
      high_risk_clients: 8
    };
  }
};

// Export for admin panel integration
export default clientService;