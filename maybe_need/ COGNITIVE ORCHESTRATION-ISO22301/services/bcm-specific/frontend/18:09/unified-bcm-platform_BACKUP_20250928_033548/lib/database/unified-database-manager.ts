// Unified Database Manager для BCM Platform
// Централизованное управление PostgreSQL + Supabase + Redis + MongoDB
// Интеграция с Docker Compose архитектурой

import { centralizedSupabase, centralizedBCM } from '@/lib/supabase/centralized-client'

// Database configuration from docker-compose.yml
export const DB_CONFIG = {
  postgres: {
    host: process.env.NEXT_PUBLIC_POSTGRES_HOST || 'localhost',
    port: parseInt(process.env.NEXT_PUBLIC_POSTGRES_PORT || '5432'),
    database: process.env.NEXT_PUBLIC_POSTGRES_DB || 'bcm_platform',
    username: process.env.NEXT_PUBLIC_POSTGRES_USER || 'odoo',
    password: process.env.NEXT_PUBLIC_POSTGRES_PASSWORD || 'postgres123'
  },
  redis: {
    url: process.env.NEXT_PUBLIC_REDIS_URL || 'redis://localhost:6379',
    host: process.env.NEXT_PUBLIC_REDIS_HOST || 'localhost',
    port: parseInt(process.env.NEXT_PUBLIC_REDIS_PORT || '6379'),
    databases: {
      cache: 0,        // Основной кэш
      sessions: 1,     // Пользовательские сессии
      notifications: 2, // Уведомления
      documents: 3,    // Кэш документов
      compliance: 4,   // Комплаенс данные
      simulation: 5,   // Симуляции
      exercise: 6      // Учения
    }
  },
  mongodb: {
    url: process.env.NEXT_PUBLIC_MONGODB_URL || '',
    database: process.env.NEXT_PUBLIC_MONGODB_DATABASE || 'bcm_documents',
    collections: {
      documents: 'documents',
      logs: 'audit_logs',
      files: 'uploaded_files',
      templates: 'document_templates',
      versions: 'document_versions'
    }
  },
  rabbitmq: {
    url: process.env.NEXT_PUBLIC_RABBITMQ_URL || 'amqp://bcm:bcm123@localhost:5672/',
    exchanges: {
      events: 'bcm.events',
      notifications: 'bcm.notifications',
      ai_tasks: 'bcm.ai_tasks'
    }
  }
}

// Database connection types
export type DatabaseType = 'postgres' | 'supabase' | 'redis' | 'mongodb'

// Unified query interface
export interface UnifiedQuery {
  operation: 'select' | 'insert' | 'update' | 'delete' | 'cache_get' | 'cache_set'
  database: DatabaseType
  table?: string
  collection?: string
  key?: string
  data?: any
  where?: any
  tenant_id?: string
}

// Connection health status
export interface DatabaseHealth {
  database: DatabaseType
  status: 'online' | 'offline' | 'degraded'
  responseTime?: number
  error?: string
  lastChecked: Date
}

// Unified Database Manager
export class UnifiedDatabaseManager {
  private redisClient: any = null
  private mongoClient: any = null
  private healthCache: Map<DatabaseType, DatabaseHealth> = new Map()

  constructor() {
    this.initializeConnections()
  }

  // Initialize all database connections
  private async initializeConnections() {
    try {
      // Redis connection (optional for development)
      if (typeof window === 'undefined' && process.env.NODE_ENV === 'production') {
        try {
          // Server-side Redis initialization only in production
          const Redis = await import('redis')
          this.redisClient = Redis.createClient({
            url: DB_CONFIG.redis.url
          })

          this.redisClient.on('error', (err: any) => {
            console.warn('Redis connection error (non-fatal):', err.message)
            this.redisClient = null // Disable Redis on connection error
          })

          await this.redisClient.connect()
          console.log('✅ Redis connected')
        } catch (error) {
          console.warn('⚠️ Redis unavailable, using in-memory fallback')
          this.redisClient = null
        }
      } else {
        console.log('⚠️ Redis disabled in development mode')
      }

      // MongoDB connection (if configured)
      if (DB_CONFIG.mongodb.url && typeof window === 'undefined') {
        const { MongoClient } = await import('mongodb')
        this.mongoClient = new MongoClient(DB_CONFIG.mongodb.url)
        await this.mongoClient.connect()
        console.log('✅ MongoDB connected')
      }

    } catch (error) {
      console.error('Database initialization error:', error)
    }
  }

  // PostgreSQL operations (via Odoo API)
  async postgresQuery(query: {
    model: string
    method: string
    args?: any[]
    kwargs?: any
    tenant_id?: string
  }) {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_ODOO_URL}/web/dataset/call_kw`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.getOdooSessionToken()}`
        },
        body: JSON.stringify({
          jsonrpc: '2.0',
          method: 'call',
          params: {
            model: query.model,
            method: query.method,
            args: query.args || [],
            kwargs: {
              ...query.kwargs,
              context: {
                ...query.kwargs?.context,
                company_id: query.tenant_id ? parseInt(query.tenant_id) : undefined
              }
            }
          }
        })
      })

      const result = await response.json()
      return result.result
    } catch (error) {
      console.error('PostgreSQL query error:', error)
      throw error
    }
  }

  // Supabase operations (централизованные)
  async supabaseQuery(query: {
    table: string
    operation: 'select' | 'insert' | 'update' | 'delete'
    data?: any
    where?: any
    tenant_id?: string
  }) {
    try {
      // Set tenant context if provided
      if (query.tenant_id) {
        await centralizedBCM.setTenantContext(query.tenant_id)
      }

      let supabaseQuery = centralizedSupabase.from(query.table)

      switch (query.operation) {
        case 'select':
          if (query.where) {
            Object.entries(query.where).forEach(([key, value]) => {
              supabaseQuery = supabaseQuery.eq(key, value)
            })
          }
          return await supabaseQuery.select()

        case 'insert':
          return await supabaseQuery.insert(query.data)

        case 'update':
          if (query.where) {
            Object.entries(query.where).forEach(([key, value]) => {
              supabaseQuery = supabaseQuery.eq(key, value)
            })
          }
          return await supabaseQuery.update(query.data)

        case 'delete':
          if (query.where) {
            Object.entries(query.where).forEach(([key, value]) => {
              supabaseQuery = supabaseQuery.eq(key, value)
            })
          }
          return await supabaseQuery.delete()

        default:
          throw new Error(`Unsupported Supabase operation: ${query.operation}`)
      }
    } catch (error) {
      console.error('Supabase query error:', error)
      throw error
    }
  }

  // Redis operations with fallback
  async redisOperation(operation: {
    type: 'get' | 'set' | 'del' | 'exists' | 'expire'
    key: string
    value?: any
    database?: number
    ttl?: number
  }) {
    try {
      if (!this.redisClient) {
        console.log('Redis not available, using fallback behavior')
        // Return appropriate fallback responses
        switch (operation.type) {
          case 'get': return null
          case 'set': return 'OK'
          case 'del': return 0
          case 'exists': return 0
          case 'expire': return 0
          default: return null
        }
      }

      // Select database if specified
      if (operation.database !== undefined) {
        await this.redisClient.select(operation.database)
      }

      switch (operation.type) {
        case 'get':
          const value = await this.redisClient.get(operation.key)
          try {
            return JSON.parse(value)
          } catch {
            return value
          }

        case 'set':
          if (operation.ttl) {
            return await this.redisClient.setEx(
              operation.key,
              operation.ttl,
              JSON.stringify(operation.value)
            )
          } else {
            return await this.redisClient.set(
              operation.key,
              JSON.stringify(operation.value)
            )
          }

        case 'del':
          return await this.redisClient.del(operation.key)

        case 'exists':
          return await this.redisClient.exists(operation.key)

        case 'expire':
          return await this.redisClient.expire(operation.key, operation.ttl || 3600)

        default:
          throw new Error(`Unsupported Redis operation: ${operation.type}`)
      }
    } catch (error) {
      console.error('Redis operation error:', error)
      throw error
    }
  }

  // MongoDB operations
  async mongoOperation(operation: {
    collection: string
    type: 'find' | 'findOne' | 'insertOne' | 'insertMany' | 'updateOne' | 'updateMany' | 'deleteOne' | 'deleteMany'
    filter?: any
    data?: any
    options?: any
  }) {
    try {
      if (!this.mongoClient) {
        throw new Error('MongoDB client not initialized')
      }

      const db = this.mongoClient.db(DB_CONFIG.mongodb.database)
      const collection = db.collection(operation.collection)

      switch (operation.type) {
        case 'find':
          return await collection.find(operation.filter || {}, operation.options).toArray()

        case 'findOne':
          return await collection.findOne(operation.filter || {}, operation.options)

        case 'insertOne':
          return await collection.insertOne(operation.data)

        case 'insertMany':
          return await collection.insertMany(operation.data)

        case 'updateOne':
          return await collection.updateOne(operation.filter, { $set: operation.data }, operation.options)

        case 'updateMany':
          return await collection.updateMany(operation.filter, { $set: operation.data }, operation.options)

        case 'deleteOne':
          return await collection.deleteOne(operation.filter)

        case 'deleteMany':
          return await collection.deleteMany(operation.filter)

        default:
          throw new Error(`Unsupported MongoDB operation: ${operation.type}`)
      }
    } catch (error) {
      console.error('MongoDB operation error:', error)
      throw error
    }
  }

  // Universal query method
  async query(query: UnifiedQuery) {
    switch (query.database) {
      case 'postgres':
        if (!query.table) throw new Error('Table required for PostgreSQL query')
        return await this.postgresQuery({
          model: query.table,
          method: this.mapOperationToOdooMethod(query.operation),
          args: query.data ? [query.data] : [],
          kwargs: { domain: query.where || [] },
          tenant_id: query.tenant_id
        })

      case 'supabase':
        if (!query.table) throw new Error('Table required for Supabase query')
        return await this.supabaseQuery({
          table: query.table,
          operation: query.operation as any,
          data: query.data,
          where: query.where,
          tenant_id: query.tenant_id
        })

      case 'redis':
        if (!query.key) throw new Error('Key required for Redis operation')
        return await this.redisOperation({
          type: query.operation === 'cache_get' ? 'get' : 'set',
          key: query.key,
          value: query.data
        })

      case 'mongodb':
        if (!query.collection) throw new Error('Collection required for MongoDB query')
        return await this.mongoOperation({
          collection: query.collection,
          type: this.mapOperationToMongoMethod(query.operation),
          filter: query.where,
          data: query.data
        })

      default:
        throw new Error(`Unsupported database: ${query.database}`)
    }
  }

  // Health checks for all databases
  async checkDatabasesHealth(): Promise<DatabaseHealth[]> {
    const results: DatabaseHealth[] = []

    // Check PostgreSQL (via Odoo)
    results.push(await this.checkPostgresHealth())

    // Check Supabase
    results.push(await this.checkSupabaseHealth())

    // Check Redis
    results.push(await this.checkRedisHealth())

    // Check MongoDB (if configured)
    if (DB_CONFIG.mongodb.url) {
      results.push(await this.checkMongoHealth())
    }

    return results
  }

  private async checkPostgresHealth(): Promise<DatabaseHealth> {
    const startTime = Date.now()
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_ODOO_URL}/web/health`, {
        method: 'GET',
        timeout: 5000
      })

      if (response.ok) {
        return {
          database: 'postgres',
          status: 'online',
          responseTime: Date.now() - startTime,
          lastChecked: new Date()
        }
      } else {
        throw new Error(`HTTP ${response.status}`)
      }
    } catch (error) {
      return {
        database: 'postgres',
        status: 'offline',
        error: error instanceof Error ? error.message : 'Unknown error',
        lastChecked: new Date()
      }
    }
  }

  private async checkSupabaseHealth(): Promise<DatabaseHealth> {
    const startTime = Date.now()
    try {
      const isHealthy = await centralizedBCM.checkConnection()

      return {
        database: 'supabase',
        status: isHealthy ? 'online' : 'offline',
        responseTime: Date.now() - startTime,
        lastChecked: new Date()
      }
    } catch (error) {
      return {
        database: 'supabase',
        status: 'offline',
        error: error instanceof Error ? error.message : 'Unknown error',
        lastChecked: new Date()
      }
    }
  }

  private async checkRedisHealth(): Promise<DatabaseHealth> {
    const startTime = Date.now()
    try {
      if (this.redisClient) {
        await this.redisClient.ping()
        return {
          database: 'redis',
          status: 'online',
          responseTime: Date.now() - startTime,
          lastChecked: new Date()
        }
      } else {
        // Redis is disabled in development mode
        return {
          database: 'redis',
          status: 'offline',
          error: 'Redis disabled in development mode',
          lastChecked: new Date()
        }
      }
    } catch (error) {
      return {
        database: 'redis',
        status: 'offline',
        error: error instanceof Error ? error.message : 'Unknown error',
        lastChecked: new Date()
      }
    }
  }

  private async checkMongoHealth(): Promise<DatabaseHealth> {
    const startTime = Date.now()
    try {
      if (this.mongoClient) {
        await this.mongoClient.db().admin().ping()
        return {
          database: 'mongodb',
          status: 'online',
          responseTime: Date.now() - startTime,
          lastChecked: new Date()
        }
      } else {
        throw new Error('MongoDB client not initialized')
      }
    } catch (error) {
      return {
        database: 'mongodb',
        status: 'offline',
        error: error instanceof Error ? error.message : 'Unknown error',
        lastChecked: new Date()
      }
    }
  }

  // Helper methods
  private mapOperationToOdooMethod(operation: string): string {
    switch (operation) {
      case 'select': return 'search_read'
      case 'insert': return 'create'
      case 'update': return 'write'
      case 'delete': return 'unlink'
      default: return 'search_read'
    }
  }

  private mapOperationToMongoMethod(operation: string): any {
    switch (operation) {
      case 'select': return 'find'
      case 'insert': return 'insertOne'
      case 'update': return 'updateOne'
      case 'delete': return 'deleteOne'
      default: return 'find'
    }
  }

  private getOdooSessionToken(): string {
    // Get from unified auth
    return localStorage.getItem('odoo_session_token') || ''
  }

  // Cache management
  async cacheSet(key: string, value: any, ttl: number = 3600) {
    return await this.redisOperation({
      type: 'set',
      key,
      value,
      database: DB_CONFIG.redis.databases.cache,
      ttl
    })
  }

  async cacheGet(key: string) {
    return await this.redisOperation({
      type: 'get',
      key,
      database: DB_CONFIG.redis.databases.cache
    })
  }

  // Session management
  async setSession(sessionId: string, sessionData: any, ttl: number = 86400) {
    return await this.redisOperation({
      type: 'set',
      key: `session:${sessionId}`,
      value: sessionData,
      database: DB_CONFIG.redis.databases.sessions,
      ttl
    })
  }

  async getSession(sessionId: string) {
    return await this.redisOperation({
      type: 'get',
      key: `session:${sessionId}`,
      database: DB_CONFIG.redis.databases.sessions
    })
  }

  // Document management (MongoDB)
  async storeDocument(document: {
    title: string
    content: string
    type: string
    tenant_id: string
    metadata?: any
  }) {
    if (!DB_CONFIG.mongodb.url) {
      throw new Error('MongoDB not configured')
    }

    return await this.mongoOperation({
      collection: DB_CONFIG.mongodb.collections.documents,
      type: 'insertOne',
      data: {
        ...document,
        created_at: new Date(),
        updated_at: new Date()
      }
    })
  }

  async getDocuments(filter: any = {}) {
    if (!DB_CONFIG.mongodb.url) {
      throw new Error('MongoDB not configured')
    }

    return await this.mongoOperation({
      collection: DB_CONFIG.mongodb.collections.documents,
      type: 'find',
      filter
    })
  }

  // Audit log (MongoDB)
  async logActivity(activity: {
    user_id: string
    action: string
    resource: string
    tenant_id: string
    metadata?: any
  }) {
    if (!DB_CONFIG.mongodb.url) {
      // Fallback to Redis if MongoDB not available
      return await this.redisOperation({
        type: 'set',
        key: `audit:${Date.now()}:${activity.user_id}`,
        value: {
          ...activity,
          timestamp: new Date()
        },
        database: DB_CONFIG.redis.databases.cache,
        ttl: 86400 * 30 // 30 days
      })
    }

    return await this.mongoOperation({
      collection: DB_CONFIG.mongodb.collections.logs,
      type: 'insertOne',
      data: {
        ...activity,
        timestamp: new Date()
      }
    })
  }
}

// Export singleton instance
export const unifiedDB = new UnifiedDatabaseManager()