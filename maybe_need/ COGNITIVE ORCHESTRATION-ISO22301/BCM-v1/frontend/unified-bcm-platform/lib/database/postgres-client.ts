// PostgreSQL Client для BCM Platform
// Интеграция с Odoo через унифицированный API
// Использует конфигурацию из docker-compose.yml

interface OdooSessionInfo {
  session_id: string
  user_id: number
  company_id: number
  username: string
  db: string
  server_version: string
  user_context: Record<string, any>
}

interface OdooRPCRequest {
  jsonrpc: string
  method: string
  params: {
    service?: string
    method?: string
    args?: any[]
    model?: string
    kwargs?: any
  }
  id?: number
}

interface OdooRPCResponse {
  jsonrpc: string
  id?: number
  result?: any
  error?: {
    code: number
    message: string
    data: any
  }
}

// PostgreSQL/Odoo integration client
export class PostgreSQLClient {
  private baseUrl: string
  private sessionInfo: OdooSessionInfo | null = null
  private sessionId: string | null = null

  constructor() {
    this.baseUrl = process.env.NEXT_PUBLIC_ODOO_URL || 'http://localhost:8069'
  }

  // Authenticate with Odoo/PostgreSQL backend
  async authenticate(credentials: {
    database: string
    username: string
    password: string
  }): Promise<OdooSessionInfo> {
    try {
      const response = await fetch(`${this.baseUrl}/web/session/authenticate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          jsonrpc: '2.0',
          method: 'call',
          params: {
            db: credentials.database,
            login: credentials.username,
            password: credentials.password
          }
        })
      })

      const result: OdooRPCResponse = await response.json()

      if (result.error) {
        throw new Error(`Odoo authentication failed: ${result.error.message}`)
      }

      if (!result.result || !result.result.uid) {
        throw new Error('Authentication failed: Invalid credentials')
      }

      this.sessionInfo = {
        session_id: result.result.session_id,
        user_id: result.result.uid,
        company_id: result.result.company_id,
        username: result.result.username,
        db: result.result.db,
        server_version: result.result.server_version,
        user_context: result.result.user_context || {}
      }

      // Store session for subsequent requests
      this.sessionId = result.result.session_id

      console.log('✅ PostgreSQL/Odoo authenticated:', {
        user: this.sessionInfo.username,
        company: this.sessionInfo.company_id,
        database: this.sessionInfo.db
      })

      return this.sessionInfo
    } catch (error) {
      console.error('PostgreSQL authentication error:', error)
      throw error
    }
  }

  // Execute RPC call to Odoo/PostgreSQL
  async rpcCall(request: {
    model: string
    method: string
    args?: any[]
    kwargs?: any
    context?: any
  }): Promise<any> {
    if (!this.sessionInfo) {
      throw new Error('Not authenticated. Call authenticate() first.')
    }

    try {
      const rpcRequest: OdooRPCRequest = {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: request.model,
          method: request.method,
          args: request.args || [],
          kwargs: {
            ...request.kwargs,
            context: {
              ...this.sessionInfo.user_context,
              ...request.context,
              // Ensure multi-tenancy
              allowed_company_ids: [this.sessionInfo.company_id]
            }
          }
        },
        id: Math.floor(Math.random() * 1000000)
      }

      const response = await fetch(`${this.baseUrl}/web/dataset/call_kw`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Cookie': `session_id=${this.sessionId}`
        },
        body: JSON.stringify(rpcRequest)
      })

      const result: OdooRPCResponse = await response.json()

      if (result.error) {
        throw new Error(`RPC call failed: ${result.error.message}`)
      }

      return result.result
    } catch (error) {
      console.error('PostgreSQL RPC call error:', error)
      throw error
    }
  }

  // BCM-specific operations

  // Get BCM users (from res.users with BCM context)
  async getBCMUsers(filters: any[] = []): Promise<any[]> {
    return await this.rpcCall({
      model: 'res.users',
      method: 'search_read',
      kwargs: {
        domain: [
          ['active', '=', true],
          ['company_id', '=', this.sessionInfo!.company_id],
          ...filters
        ],
        fields: [
          'id', 'name', 'login', 'email', 'active',
          'company_id', 'company_ids', 'groups_id',
          'last_login', 'create_date', 'write_date'
        ]
      }
    })
  }

  // Get BCM incidents
  async getBCMIncidents(filters: any[] = []): Promise<any[]> {
    return await this.rpcCall({
      model: 'bcm.incident',
      method: 'search_read',
      kwargs: {
        domain: [
          ['company_id', '=', this.sessionInfo!.company_id],
          ...filters
        ],
        fields: [
          'id', 'name', 'description', 'state', 'priority',
          'incident_type', 'impact_level', 'detected_date',
          'resolved_date', 'assigned_to', 'company_id'
        ]
      }
    })
  }

  // Get BCM risk assessments
  async getBCMRiskAssessments(filters: any[] = []): Promise<any[]> {
    return await this.rpcCall({
      model: 'bcm.risk.assessment',
      method: 'search_read',
      kwargs: {
        domain: [
          ['company_id', '=', this.sessionInfo!.company_id],
          ...filters
        ],
        fields: [
          'id', 'name', 'description', 'risk_category',
          'probability', 'impact', 'risk_level', 'status',
          'assessment_date', 'next_review_date', 'company_id'
        ]
      }
    })
  }

  // Get BCM business impact analysis
  async getBCMBIA(filters: any[] = []): Promise<any[]> {
    return await this.rpcCall({
      model: 'bcm.bia.analysis',
      method: 'search_read',
      kwargs: {
        domain: [
          ['company_id', '=', this.sessionInfo!.company_id],
          ...filters
        ],
        fields: [
          'id', 'name', 'business_process', 'criticality_level',
          'rto', 'rpo', 'mbco', 'impact_financial',
          'impact_operational', 'impact_regulatory', 'company_id'
        ]
      }
    })
  }

  // Get BCM exercises
  async getBCMExercises(filters: any[] = []): Promise<any[]> {
    return await this.rpcCall({
      model: 'bcm.exercise',
      method: 'search_read',
      kwargs: {
        domain: [
          ['company_id', '=', this.sessionInfo!.company_id],
          ...filters
        ],
        fields: [
          'id', 'name', 'description', 'exercise_type',
          'planned_date', 'actual_date', 'status',
          'participants', 'objectives', 'results', 'company_id'
        ]
      }
    })
  }

  // Get BCM compliance items
  async getBCMCompliance(filters: any[] = []): Promise<any[]> {
    return await this.rpcCall({
      model: 'bcm.compliance.item',
      method: 'search_read',
      kwargs: {
        domain: [
          ['company_id', '=', this.sessionInfo!.company_id],
          ...filters
        ],
        fields: [
          'id', 'name', 'requirement', 'standard',
          'status', 'evidence', 'assessment_date',
          'next_review_date', 'responsible_person', 'company_id'
        ]
      }
    })
  }

  // Create record in PostgreSQL via Odoo
  async createRecord(model: string, data: any): Promise<number> {
    const recordData = {
      ...data,
      company_id: this.sessionInfo!.company_id // Ensure multi-tenancy
    }

    return await this.rpcCall({
      model,
      method: 'create',
      args: [recordData]
    })
  }

  // Update record in PostgreSQL via Odoo
  async updateRecord(model: string, recordId: number, data: any): Promise<boolean> {
    return await this.rpcCall({
      model,
      method: 'write',
      args: [[recordId], data]
    })
  }

  // Delete record from PostgreSQL via Odoo
  async deleteRecord(model: string, recordId: number): Promise<boolean> {
    return await this.rpcCall({
      model,
      method: 'unlink',
      args: [[recordId]]
    })
  }

  // Search records with complex filters
  async searchRecords(model: string, domain: any[] = [], options: {
    fields?: string[]
    limit?: number
    offset?: number
    order?: string
  } = {}): Promise<any[]> {
    // Add company filter for multi-tenancy
    const companyDomain = [
      ['company_id', '=', this.sessionInfo!.company_id],
      ...domain
    ]

    return await this.rpcCall({
      model,
      method: 'search_read',
      kwargs: {
        domain: companyDomain,
        fields: options.fields,
        limit: options.limit,
        offset: options.offset,
        order: options.order
      }
    })
  }

  // Execute custom SQL via Odoo (for advanced operations)
  async executeSQLQuery(query: string, params: any[] = []): Promise<any[]> {
    return await this.rpcCall({
      model: 'ir.database.query',
      method: 'execute_query',
      args: [query, params],
      context: {
        // Security context for SQL execution
        safe_sql: true,
        tenant_id: this.sessionInfo!.company_id
      }
    })
  }

  // Get database statistics
  async getDatabaseStats(): Promise<any> {
    return await this.rpcCall({
      model: 'ir.database.stats',
      method: 'get_stats',
      args: [],
      context: {
        company_id: this.sessionInfo!.company_id
      }
    })
  }

  // Check database health
  async checkHealth(): Promise<{
    status: 'healthy' | 'degraded' | 'offline'
    response_time: number
    connection_count: number
    database_size: string
  }> {
    const startTime = Date.now()

    try {
      const healthData = await this.rpcCall({
        model: 'ir.database.health',
        method: 'check_health',
        args: []
      })

      return {
        status: 'healthy',
        response_time: Date.now() - startTime,
        connection_count: healthData.connection_count || 0,
        database_size: healthData.database_size || 'Unknown'
      }
    } catch (error) {
      return {
        status: 'offline',
        response_time: Date.now() - startTime,
        connection_count: 0,
        database_size: 'Unknown'
      }
    }
  }

  // Get current session info
  getSessionInfo(): OdooSessionInfo | null {
    return this.sessionInfo
  }

  // Logout and clear session
  async logout(): Promise<void> {
    if (this.sessionId) {
      try {
        await fetch(`${this.baseUrl}/web/session/destroy`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Cookie': `session_id=${this.sessionId}`
          }
        })
      } catch (error) {
        console.warn('Logout request failed:', error)
      }
    }

    this.sessionInfo = null
    this.sessionId = null
  }

  // Utility: Check if authenticated
  isAuthenticated(): boolean {
    return this.sessionInfo !== null && this.sessionId !== null
  }

  // Utility: Get current company ID
  getCurrentCompanyId(): number | null {
    return this.sessionInfo?.company_id || null
  }

  // Utility: Get current user ID
  getCurrentUserId(): number | null {
    return this.sessionInfo?.user_id || null
  }
}

// Export singleton instance
export const postgresClient = new PostgreSQLClient()

// Export types
export type { OdooSessionInfo, OdooRPCRequest, OdooRPCResponse }