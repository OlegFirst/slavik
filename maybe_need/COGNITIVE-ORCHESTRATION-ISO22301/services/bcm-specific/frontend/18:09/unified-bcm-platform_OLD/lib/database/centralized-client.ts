/**
 * Centralized Database Client
 * Единая точка доступа ко всем базам данных через Unified Database Gateway
 */

const GATEWAY_URL = process.env.NEXT_PUBLIC_GATEWAY_URL || 'http://localhost:8888'
const API_GATEWAY_URL = process.env.NEXT_PUBLIC_API_GATEWAY_URL || 'http://localhost:8777'

export interface DatabaseQuery {
  database: 'postgres' | 'redis' | 'mongodb' | 'rabbitmq' | 'supabase' | 'odoo'
  operation: 'select' | 'insert' | 'update' | 'delete' | 'cache_get' | 'cache_set' | 'publish' | 'subscribe' | 'odoo_search' | 'odoo_read' | 'odoo_create' | 'odoo_write'
  table?: string
  collection?: string
  key?: string
  data?: any
  where?: any
  tenant_id?: string
  ttl?: number
  // Odoo-specific fields
  model?: string
  domain?: any[]
  ids?: number[]
  fields?: string[]
  context?: any
}

export interface OdooAuthRequest {
  username: string
  password: string
  database?: string
}

export interface OdooAuthResponse {
  user_id: number
  session_id: string
  user_context: any
  company_id: number
  partner_id: number
}

export interface HealthStatus {
  database: string
  status: 'online' | 'offline' | 'degraded'
  response_time?: number
  error?: string
  last_checked: string
}

class CentralizedDatabaseClient {
  private baseUrl: string

  constructor() {
    this.baseUrl = GATEWAY_URL
  }

  /**
   * Execute database query through centralized gateway
   */
  async query(queryParams: DatabaseQuery): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(queryParams)
      })

      if (!response.ok) {
        throw new Error(`Gateway error: ${response.status} ${response.statusText}`)
      }

      return await response.json()
    } catch (error) {
      console.error('Centralized DB query error:', error)
      throw error
    }
  }

  /**
   * Check health of all databases
   */
  async checkHealth(): Promise<HealthStatus[]> {
    try {
      const response = await fetch(`${this.baseUrl}/health/databases`)

      if (!response.ok) {
        throw new Error(`Health check failed: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error('Health check error:', error)
      return []
    }
  }

  /**
   * Get performance metrics
   */
  async getMetrics(): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/metrics`)

      if (!response.ok) {
        throw new Error(`Metrics fetch failed: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error('Metrics error:', error)
      return null
    }
  }

  // Convenience methods for common operations

  /**
   * PostgreSQL operations
   */
  async postgres(operation: string, table: string, data?: any, where?: any) {
    return this.query({
      database: 'postgres',
      operation: operation as any,
      table,
      data,
      where
    })
  }

  /**
   * Redis cache operations
   */
  async cache(operation: 'get' | 'set', key: string, data?: any, ttl?: number) {
    return this.query({
      database: 'redis',
      operation: operation === 'get' ? 'cache_get' : 'cache_set',
      key,
      data,
      ttl
    })
  }

  /**
   * MongoDB document operations
   */
  async mongo(operation: string, collection: string, data?: any, where?: any) {
    return this.query({
      database: 'mongodb',
      operation: operation as any,
      collection,
      data,
      where
    })
  }

  /**
   * RabbitMQ messaging
   */
  async publish(routingKey: string, message: any) {
    return this.query({
      database: 'rabbitmq',
      operation: 'publish',
      key: routingKey,
      data: message
    })
  }

  /**
   * Supabase operations
   */
  async supabase(operation: string, table: string, data?: any, where?: any) {
    return this.query({
      database: 'supabase',
      operation: operation as any,
      table,
      data,
      where
    })
  }

  /**
   * Odoo operations
   */
  async odoo(operation: 'search' | 'read' | 'create' | 'write', model: string, options: {
    domain?: any[]
    ids?: number[]
    fields?: string[]
    data?: any
    context?: any
  } = {}) {
    return this.query({
      database: 'odoo',
      operation: `odoo_${operation}` as any,
      model,
      domain: options.domain,
      ids: options.ids,
      fields: options.fields,
      data: options.data,
      context: options.context
    })
  }

  /**
   * Odoo Authentication
   */
  async authenticateOdoo(credentials: OdooAuthRequest): Promise<OdooAuthResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/auth/odoo`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials)
      })

      if (!response.ok) {
        throw new Error(`Odoo authentication failed: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error('Odoo authentication error:', error)
      throw error
    }
  }

  /**
   * Get Odoo session info
   */
  async getOdooSession(sessionId: string) {
    try {
      const response = await fetch(`${this.baseUrl}/auth/odoo/session/${sessionId}`)

      if (!response.ok) {
        throw new Error(`Session check failed: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error('Session check error:', error)
      throw error
    }
  }

  /**
   * Logout Odoo session
   */
  async logoutOdoo(sessionId: string) {
    try {
      const response = await fetch(`${this.baseUrl}/auth/odoo/session/${sessionId}`, {
        method: 'DELETE'
      })

      if (!response.ok) {
        throw new Error(`Logout failed: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error('Logout error:', error)
      throw error
    }
  }

  /**
   * CRM Bridge methods - работа с BCM проектами через CRM
   */
  async getCrmProjects() {
    try {
      const response = await fetch(`${API_GATEWAY_URL}/api/crm_bridge/projects`)

      if (!response.ok) {
        throw new Error(`CRM projects fetch failed: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error('CRM projects error:', error)
      throw error
    }
  }

  async createBcmWorkspace(projectId: number) {
    try {
      const response = await fetch(`${API_GATEWAY_URL}/api/crm_bridge/projects/${projectId}/workspace`, {
        method: 'POST'
      })

      if (!response.ok) {
        throw new Error(`Workspace creation failed: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error('Workspace creation error:', error)
      throw error
    }
  }

  async getBcmWorkspace(projectId: number) {
    try {
      const response = await fetch(`${API_GATEWAY_URL}/api/crm_bridge/projects/${projectId}/workspace`)

      if (!response.ok) {
        throw new Error(`Workspace fetch failed: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error('Workspace fetch error:', error)
      throw error
    }
  }

  async sendBcmEvent(eventType: string, sourceModule: string, projectId: number, data: any) {
    try {
      const response = await fetch(`${API_GATEWAY_URL}/api/crm_bridge/events/bcm`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          event_type: eventType,
          source_module: sourceModule,
          project_id: projectId,
          data
        })
      })

      if (!response.ok) {
        throw new Error(`Event send failed: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error('Event send error:', error)
      throw error
    }
  }

  async testIntegration() {
    try {
      const response = await fetch(`${API_GATEWAY_URL}/api/crm_bridge/integration/test`)

      if (!response.ok) {
        throw new Error(`Integration test failed: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error('Integration test error:', error)
      throw error
    }
  }

  /**
   * Bulk operations across multiple databases
   */
  async bulkQuery(queries: DatabaseQuery[]): Promise<any[]> {
    const results = await Promise.allSettled(
      queries.map(query => this.query(query))
    )

    return results.map((result, index) => ({
      query: queries[index],
      success: result.status === 'fulfilled',
      data: result.status === 'fulfilled' ? result.value : null,
      error: result.status === 'rejected' ? result.reason.message : null
    }))
  }

  /**
   * Real-time health monitoring
   */
  async startHealthMonitoring(callback: (health: HealthStatus[]) => void, interval = 30000) {
    const monitor = async () => {
      const health = await this.checkHealth()
      callback(health)
    }

    // Initial check
    await monitor()

    // Set up periodic checks
    return setInterval(monitor, interval)
  }
}

// Export singleton instance
export const centralizedDB = new CentralizedDatabaseClient()

// Export class for custom instances
export { CentralizedDatabaseClient }