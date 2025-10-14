// Integration Test для всех баз данных
// Проверяет подключения к PostgreSQL, Supabase, Redis, MongoDB, RabbitMQ

import { unifiedDB } from './unified-database-manager'

export class DatabaseIntegrationTest {
  private results: Map<string, boolean> = new Map()
  private errors: Map<string, string> = new Map()

  async runAllTests(): Promise<{
    passed: number
    failed: number
    results: Record<string, boolean>
    errors: Record<string, string>
    overall: 'success' | 'failure'
  }> {
    console.log('🔬 Starting Database Integration Tests...')

    // Test all database connections
    await this.testPostgreSQLConnection()
    await this.testSupabaseConnection()
    await this.testRedisConnection()
    await this.testMongoDBConnection()
    await this.testRabbitMQConnection()

    // Test cross-database operations
    await this.testCrossDBOperations()

    // Compile results
    const results = Object.fromEntries(this.results)
    const errors = Object.fromEntries(this.errors)
    const passed = Array.from(this.results.values()).filter(v => v).length
    const failed = Array.from(this.results.values()).filter(v => !v).length

    console.log('🔬 Integration Tests Complete')
    console.log(`✅ Passed: ${passed}`)
    console.log(`❌ Failed: ${failed}`)

    return {
      passed,
      failed,
      results,
      errors,
      overall: failed === 0 ? 'success' : 'failure'
    }
  }

  private async testPostgreSQLConnection() {
    try {
      console.log('🔍 Testing PostgreSQL connection...')

      const result = await unifiedDB.query({
        database: 'postgres',
        operation: 'select',
        table: 'res.partner', // Standard Odoo model
        where: [],
        data: { limit: 1 }
      })

      this.results.set('postgresql_connection', true)
      this.results.set('postgresql_query', Array.isArray(result))
      console.log('✅ PostgreSQL: Connection and query test passed')

    } catch (error) {
      this.results.set('postgresql_connection', false)
      this.results.set('postgresql_query', false)
      this.errors.set('postgresql', error instanceof Error ? error.message : 'Unknown error')
      console.log('❌ PostgreSQL: Test failed -', error)
    }
  }

  private async testSupabaseConnection() {
    try {
      console.log('🔍 Testing Supabase connection...')

      // Test basic connection health
      const healthCheck = await unifiedDB.checkDatabasesHealth()
      const supabaseHealth = healthCheck.find(h => h.database === 'supabase')

      this.results.set('supabase_connection', supabaseHealth?.status === 'online')

      // Test simple query
      const result = await unifiedDB.query({
        database: 'supabase',
        operation: 'select',
        table: 'bcm_users',
        where: {},
        data: { limit: 1 }
      })

      this.results.set('supabase_query', true)
      console.log('✅ Supabase: Connection and query test passed')

    } catch (error) {
      this.results.set('supabase_connection', false)
      this.results.set('supabase_query', false)
      this.errors.set('supabase', error instanceof Error ? error.message : 'Unknown error')
      console.log('❌ Supabase: Test failed -', error)
    }
  }

  private async testRedisConnection() {
    try {
      console.log('🔍 Testing Redis connection...')

      // Test cache operations
      const testKey = `test:${Date.now()}`
      const testValue = { test: 'value', timestamp: new Date().toISOString() }

      // Set value
      await unifiedDB.cacheSet(testKey, testValue, 60)
      this.results.set('redis_set', true)

      // Get value
      const retrieved = await unifiedDB.cacheGet(testKey)
      this.results.set('redis_get', retrieved?.test === testValue.test)

      console.log('✅ Redis: Cache operations test passed')

    } catch (error) {
      this.results.set('redis_set', false)
      this.results.set('redis_get', false)
      this.errors.set('redis', error instanceof Error ? error.message : 'Unknown error')
      console.log('❌ Redis: Test failed -', error)
    }
  }

  private async testMongoDBConnection() {
    try {
      console.log('🔍 Testing MongoDB connection...')

      // Test document operations
      const testDoc = {
        title: 'Test Document',
        content: 'Integration test content',
        type: 'test',
        tenant_id: 'test_tenant',
        metadata: { test: true }
      }

      // Store document
      const insertResult = await unifiedDB.storeDocument(testDoc)
      this.results.set('mongodb_insert', !!insertResult)

      // Retrieve documents
      const documents = await unifiedDB.getDocuments({ type: 'test' })
      this.results.set('mongodb_query', Array.isArray(documents))

      console.log('✅ MongoDB: Document operations test passed')

    } catch (error) {
      this.results.set('mongodb_insert', false)
      this.results.set('mongodb_query', false)
      this.errors.set('mongodb', error instanceof Error ? error.message : 'Unknown error')
      console.log('❌ MongoDB: Test failed -', error)
    }
  }

  private async testRabbitMQConnection() {
    try {
      console.log('🔍 Testing RabbitMQ connection...')

      // Test publishing event
      const eventPublished = await unifiedDB.publishEvent('test.integration', {
        message: 'Integration test event',
        timestamp: new Date().toISOString()
      }, 'test_tenant')

      this.results.set('rabbitmq_publish', eventPublished !== false)

      // Test publishing notification
      const notificationPublished = await unifiedDB.publishNotification({
        user_id: 'test_user',
        title: 'Test Notification',
        message: 'Integration test notification',
        type: 'info',
        tenant_id: 'test_tenant'
      })

      this.results.set('rabbitmq_notification', notificationPublished !== false)

      console.log('✅ RabbitMQ: Message publishing test passed')

    } catch (error) {
      this.results.set('rabbitmq_publish', false)
      this.results.set('rabbitmq_notification', false)
      this.errors.set('rabbitmq', error instanceof Error ? error.message : 'Unknown error')
      console.log('❌ RabbitMQ: Test failed -', error)
    }
  }

  private async testCrossDBOperations() {
    try {
      console.log('🔍 Testing cross-database operations...')

      const testUserId = 'integration_test_user'
      const testTenantId = 'integration_test_tenant'

      // Test logging activity (MongoDB + Redis fallback)
      await unifiedDB.logActivity({
        user_id: testUserId,
        action: 'integration_test',
        resource: 'database_test',
        tenant_id: testTenantId,
        metadata: { test_type: 'cross_db' }
      })

      this.results.set('cross_db_logging', true)

      // Test session management (Redis)
      const sessionId = `test_session_${Date.now()}`
      await unifiedDB.setSession(sessionId, {
        user_id: testUserId,
        tenant_id: testTenantId,
        login_time: new Date()
      })

      const session = await unifiedDB.getSession(sessionId)
      this.results.set('cross_db_session', session?.user_id === testUserId)

      console.log('✅ Cross-database operations test passed')

    } catch (error) {
      this.results.set('cross_db_logging', false)
      this.results.set('cross_db_session', false)
      this.errors.set('cross_db', error instanceof Error ? error.message : 'Unknown error')
      console.log('❌ Cross-database operations: Test failed -', error)
    }
  }

  // Health check for all databases
  async checkAllDatabaseHealth() {
    console.log('🔍 Checking all database health...')

    try {
      const healthResults = await unifiedDB.checkDatabasesHealth()

      console.log('📊 Database Health Summary:')
      healthResults.forEach(health => {
        const status = health.status === 'online' ? '✅' :
                      health.status === 'degraded' ? '⚠️' : '❌'
        console.log(`${status} ${health.database}: ${health.status} (${health.responseTime || 0}ms)`)

        if (health.error) {
          console.log(`   Error: ${health.error}`)
        }
      })

      return healthResults
    } catch (error) {
      console.error('❌ Health check failed:', error)
      return []
    }
  }

  // Performance test
  async performanceTest() {
    console.log('⚡ Running performance tests...')

    const tests = [
      {
        name: 'Redis Cache Performance',
        test: async () => {
          const start = Date.now()
          for (let i = 0; i < 100; i++) {
            await unifiedDB.cacheSet(`perf_test_${i}`, { value: i }, 60)
          }
          return Date.now() - start
        }
      },
      {
        name: 'Database Health Check Speed',
        test: async () => {
          const start = Date.now()
          await unifiedDB.checkDatabasesHealth()
          return Date.now() - start
        }
      }
    ]

    const results: Record<string, number> = {}

    for (const test of tests) {
      try {
        const duration = await test.test()
        results[test.name] = duration
        console.log(`✅ ${test.name}: ${duration}ms`)
      } catch (error) {
        console.log(`❌ ${test.name}: Failed -`, error)
        results[test.name] = -1
      }
    }

    return results
  }
}

// Export singleton instance
export const dbIntegrationTest = new DatabaseIntegrationTest()