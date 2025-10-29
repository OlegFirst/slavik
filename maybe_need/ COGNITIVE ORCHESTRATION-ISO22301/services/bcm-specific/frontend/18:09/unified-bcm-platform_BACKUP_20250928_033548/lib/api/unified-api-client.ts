// Unified API Client for Enterprise BCM Platform
// Handles: Odoo (Business) + Supabase (AI/Real-time) + Redis (Cache) integration

import { unifiedAuth, UnifiedUser } from '@/lib/auth/unified-auth'

// API Response types
export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  error?: string
  message?: string
  meta?: {
    total?: number
    page?: number
    limit?: number
  }
}

// Multi-tenant query options
export interface QueryOptions {
  filters?: Record<string, any>
  pagination?: {
    page: number
    limit: number
  }
  sorting?: {
    field: string
    direction: 'asc' | 'desc'
  }[]
  include?: string[]
  companyId?: number // Override company filter
}

// Unified API Client Class
export class UnifiedApiClient {
  private baseUrl: string
  private user: UnifiedUser | null = null

  constructor() {
    this.baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8069'
    this.user = unifiedAuth.getCurrentUser()

    // Listen for auth changes
    unifiedAuth.onAuthStateChange((user) => {
      this.user = user
    })
  }

  // 1. Odoo Business Data Operations
  async odoo<T = any>(
    model: string,
    method: string = 'search_read',
    args: any[] = [],
    options: QueryOptions = {}
  ): Promise<ApiResponse<T>> {
    try {
      if (!this.user) {
        throw new Error('Authentication required')
      }

      // Build Odoo domain with multi-tenancy
      const domain = this.buildOdooDomain(options)

      // Prepare Odoo RPC call
      const payload = {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          service: 'object',
          method: 'execute_kw',
          args: [
            this.user.odooUserId,
            model,
            method,
            args,
            {
              domain,
              limit: options.pagination?.limit || 100,
              offset: ((options.pagination?.page || 1) - 1) * (options.pagination?.limit || 100),
              order: this.buildOdooOrder(options.sorting),
              fields: options.include,
              ...options.filters
            }
          ]
        },
        id: Math.random()
      }

      const response = await fetch(`${this.baseUrl}/jsonrpc`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.user.accessToken}`
        },
        body: JSON.stringify(payload)
      })

      if (!response.ok) {
        throw new Error(`Odoo API error: ${response.statusText}`)
      }

      const result = await response.json()

      if (result.error) {
        throw new Error(result.error.message)
      }

      return {
        success: true,
        data: result.result
      }

    } catch (error) {
      console.error('Odoo API error:', error)
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      }
    }
  }

  // 2. Supabase AI/Real-time Operations
  async supabase<T = any>(
    table: string,
    operation: 'select' | 'insert' | 'update' | 'delete' | 'rpc',
    data?: any,
    options: QueryOptions = {}
  ): Promise<ApiResponse<T>> {
    try {
      if (!this.user) {
        throw new Error('Authentication required')
      }

      // Use Supabase client with user context
      const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
      const response = await fetch(`${supabaseUrl}/rest/v1/${table}`, {
        method: operation === 'select' ? 'GET' :
                operation === 'insert' ? 'POST' :
                operation === 'update' ? 'PATCH' : 'DELETE',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.user.accessToken}`,
          'apikey': process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
          'user-id': this.user.supabaseId
        },
        body: data ? JSON.stringify(data) : undefined
      })

      const result = await response.json()

      return {
        success: response.ok,
        data: result
      }

    } catch (error) {
      console.error('Supabase API error:', error)
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      }
    }
  }

  // 3. Redis Cache Operations
  async cache<T = any>(
    key: string,
    operation: 'get' | 'set' | 'del' | 'exists',
    value?: T,
    ttl?: number
  ): Promise<ApiResponse<T>> {
    try {
      if (!this.user) {
        throw new Error('Authentication required')
      }

      // Add user/company prefix to key for isolation
      const prefixedKey = `${this.user.companyId}:${this.user.odooUserId}:${key}`

      const response = await fetch(`${this.baseUrl}/api/cache`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.user.accessToken}`
        },
        body: JSON.stringify({
          operation,
          key: prefixedKey,
          value,
          ttl
        })
      })

      const result = await response.json()

      return {
        success: response.ok,
        data: result.data
      }

    } catch (error) {
      console.error('Cache error:', error)
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      }
    }
  }

  // 4. Multi-tenant Business Operations
  async getBcmData<T = any>(
    module: string,
    operation: string,
    params: Record<string, any> = {},
    options: QueryOptions = {}
  ): Promise<ApiResponse<T>> {

    // Route to appropriate BCM module
    const moduleRoutes = {
      'bia': () => this.odoo('bcm.business_impact_analysis', 'search_read', [], options),
      'risk': () => this.odoo('bcm.risk_assessment', 'search_read', [], options),
      'plans': () => this.odoo('bcm.continuity_plan', 'search_read', [], options),
      'incidents': () => this.odoo('bcm.incident', 'search_read', [], options),
      'training': () => this.odoo('bcm.training_program', 'search_read', [], options),
      'governance': () => this.odoo('bcm.governance_framework', 'search_read', [], options),
      'audit': () => this.odoo('bcm.audit', 'search_read', [], options),
      'context': () => this.odoo('bcm.organizational_context', 'search_read', [], options),
      'exercise': () => this.odoo('bcm.exercise', 'search_read', [], options),
      'templates': () => this.odoo('bcm.document_template', 'search_read', [], options),
      'clients': () => this.odoo('res.partner', 'search_read', [['is_company', '=', true]], options),
      'kpi': () => this.odoo('bcm.kpi', 'search_read', [], options),
      'reporting': () => this.odoo('bcm.report', 'search_read', [], options),
      'configuration': () => this.odoo('bcm.configuration', 'search_read', [], options),

      // AI/Real-time operations via Supabase
      'ai_analysis': () => this.supabase('ai_analysis', 'select', null, options),
      'chat_history': () => this.supabase('chat_history', 'select', null, options),
      'real_time_metrics': () => this.supabase('real_time_metrics', 'select', null, options),
      'ai_recommendations': () => this.supabase('ai_recommendations', 'select', null, options)
    }

    const moduleHandler = moduleRoutes[module as keyof typeof moduleRoutes]

    if (!moduleHandler) {
      return {
        success: false,
        error: `Unknown BCM module: ${module}`
      }
    }

    return moduleHandler()
  }

  // 5. Real-time Subscriptions
  async subscribeToUpdates(
    channel: string,
    callback: (data: any) => void,
    filters?: Record<string, any>
  ) {
    if (!this.user) {
      throw new Error('Authentication required')
    }

    // Company-isolated channel name
    const companyChannel = `company_${this.user.companyId}_${channel}`

    return unifiedAuth.subscribeToRealtimeChannel(companyChannel, (payload) => {
      // Apply user-level filtering
      if (filters) {
        const matchesFilter = Object.entries(filters).every(([key, value]) =>
          payload.new?.[key] === value || payload.old?.[key] === value
        )

        if (!matchesFilter) return
      }

      callback(payload)
    })
  }

  // 6. Cross-service Analytics
  async getUnifiedAnalytics(
    metrics: string[],
    dateRange: { from: Date; to: Date },
    options: QueryOptions = {}
  ): Promise<ApiResponse<any>> {
    try {
      if (!this.user) {
        throw new Error('Authentication required')
      }

      // Parallel requests to different services
      const [odooMetrics, supabaseMetrics, cachedResults] = await Promise.all([
        // Odoo business metrics
        this.odoo('bcm.analytics', 'get_metrics', [
          metrics.filter(m => m.startsWith('bcm_')),
          dateRange.from.toISOString(),
          dateRange.to.toISOString()
        ], options),

        // Supabase AI metrics
        this.supabase('analytics', 'rpc', {
          function_name: 'get_ai_metrics',
          args: {
            metrics: metrics.filter(m => m.startsWith('ai_')),
            date_from: dateRange.from.toISOString(),
            date_to: dateRange.to.toISOString(),
            user_id: this.user.supabaseId
          }
        }),

        // Check cache for previous results
        this.cache(`analytics_${metrics.join('_')}_${dateRange.from.getTime()}_${dateRange.to.getTime()}`, 'get')
      ])

      // Combine results
      const combinedData = {
        odoo: odooMetrics.data,
        supabase: supabaseMetrics.data,
        cached: cachedResults.data,
        timestamp: new Date().toISOString()
      }

      // Cache combined results for 15 minutes
      await this.cache(
        `analytics_${metrics.join('_')}_${dateRange.from.getTime()}_${dateRange.to.getTime()}`,
        'set',
        combinedData,
        15 * 60 // 15 minutes
      )

      return {
        success: true,
        data: combinedData
      }

    } catch (error) {
      console.error('Analytics error:', error)
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      }
    }
  }

  // 7. Helper methods
  private buildOdooDomain(options: QueryOptions): any[] {
    const domain = []

    // Always add company filter for multi-tenancy
    if (this.user?.companyId) {
      domain.push(['company_id', '=', options.companyId || this.user.companyId])
    }

    // Add custom filters
    if (options.filters) {
      Object.entries(options.filters).forEach(([field, value]) => {
        if (Array.isArray(value)) {
          domain.push([field, 'in', value])
        } else {
          domain.push([field, '=', value])
        }
      })
    }

    return domain
  }

  private buildOdooOrder(sorting?: QueryOptions['sorting']): string {
    if (!sorting || sorting.length === 0) {
      return 'id desc'
    }

    return sorting
      .map(sort => `${sort.field} ${sort.direction}`)
      .join(', ')
  }

  // 8. Batch operations
  async batch(operations: Array<{
    service: 'odoo' | 'supabase' | 'cache'
    operation: string
    params: any[]
  }>): Promise<ApiResponse<any[]>> {
    try {
      const results = await Promise.allSettled(
        operations.map(op => {
          switch (op.service) {
            case 'odoo':
              return this.odoo(op.params[0], op.params[1], op.params[2], op.params[3])
            case 'supabase':
              return this.supabase(op.params[0], op.params[1], op.params[2], op.params[3])
            case 'cache':
              return this.cache(op.params[0], op.params[1], op.params[2], op.params[3])
            default:
              throw new Error(`Unknown service: ${op.service}`)
          }
        })
      )

      return {
        success: true,
        data: results.map(result =>
          result.status === 'fulfilled' ? result.value : { error: result.reason }
        )
      }

    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Batch operation failed'
      }
    }
  }
}

// Singleton instance
export const unifiedApi = new UnifiedApiClient()

// Export for global access
declare global {
  interface Window {
    unifiedApi: UnifiedApiClient
  }
}

if (typeof window !== 'undefined') {
  window.unifiedApi = unifiedApi
}

// Convenience methods for common operations
export const bcmApi = {
  // Business Impact Analysis
  bia: {
    getAll: (options?: QueryOptions) => unifiedApi.getBcmData('bia', 'search_read', {}, options),
    getById: (id: number) => unifiedApi.odoo('bcm.business_impact_analysis', 'read', [[id]]),
    create: (data: any) => unifiedApi.odoo('bcm.business_impact_analysis', 'create', [data]),
    update: (id: number, data: any) => unifiedApi.odoo('bcm.business_impact_analysis', 'write', [[id], data])
  },

  // Risk Assessment
  risk: {
    getAll: (options?: QueryOptions) => unifiedApi.getBcmData('risk', 'search_read', {}, options),
    getById: (id: number) => unifiedApi.odoo('bcm.risk_assessment', 'read', [[id]]),
    create: (data: any) => unifiedApi.odoo('bcm.risk_assessment', 'create', [data]),
    update: (id: number, data: any) => unifiedApi.odoo('bcm.risk_assessment', 'write', [[id], data])
  },

  // AI Analysis
  ai: {
    analyze: (data: any) => unifiedApi.supabase('ai_analysis', 'insert', data),
    getRecommendations: () => unifiedApi.supabase('ai_recommendations', 'select'),
    getChatHistory: () => unifiedApi.supabase('chat_history', 'select')
  },

  // Real-time metrics
  realtime: {
    subscribe: (callback: (data: any) => void) =>
      unifiedApi.subscribeToUpdates('metrics', callback),
    getMetrics: () => unifiedApi.supabase('real_time_metrics', 'select')
  },

  // Analytics
  analytics: {
    get: (metrics: string[], dateRange: { from: Date; to: Date }) =>
      unifiedApi.getUnifiedAnalytics(metrics, dateRange)
  }
}