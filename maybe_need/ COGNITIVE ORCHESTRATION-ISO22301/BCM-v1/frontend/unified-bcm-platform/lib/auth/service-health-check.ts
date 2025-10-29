// Service Health Check for BCM Platform
// Проверяет доступность всех сервисов и настраивает fallback режимы

export interface ServiceStatus {
  name: string
  url: string
  status: 'online' | 'offline' | 'unknown'
  responseTime?: number
  error?: string
  lastChecked: Date
}

export interface PlatformHealth {
  overall: 'healthy' | 'degraded' | 'offline'
  services: ServiceStatus[]
  recommendations: string[]
}

// Проверка здоровья всех сервисов
export async function checkPlatformHealth(): Promise<PlatformHealth> {
  const services = [
    {
      name: 'Keycloak SSO',
      url: process.env.NEXT_PUBLIC_KEYCLOAK_URL || 'http://localhost:8080',
      path: '/auth/realms/master'
    },
    {
      name: 'Odoo Backend',
      url: process.env.NEXT_PUBLIC_ODOO_URL || 'http://localhost:8069',
      path: '/web/database/selector'
    },
    {
      name: 'Supabase',
      url: process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://demo.supabase.co',
      path: '/rest/v1/'
    },
    {
      name: 'Redis Cache',
      url: process.env.NEXT_PUBLIC_REDIS_URL || 'redis://localhost:6379',
      path: '' // Redis проверяется отдельно
    },
    {
      name: 'AI Orchestrator',
      url: process.env.NEXT_PUBLIC_AI_URL || 'http://localhost:8000',
      path: '/health'
    },
    {
      name: 'BIA Engine',
      url: process.env.NEXT_PUBLIC_BIA_URL || 'http://localhost:8082',
      path: '/health'
    }
  ]

  const results: ServiceStatus[] = []
  const recommendations: string[] = []

  for (const service of services) {
    const startTime = Date.now()

    try {
      if (service.name === 'Redis Cache') {
        // Redis нужна специальная проверка
        results.push({
          name: service.name,
          url: service.url,
          status: 'unknown', // Пока не можем проверить из браузера
          responseTime: 0,
          lastChecked: new Date()
        })
        continue
      }

      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 5000) // 5 секунд timeout

      const response = await fetch(`${service.url}${service.path}`, {
        method: 'GET',
        signal: controller.signal,
        mode: 'no-cors' // Для CORS issues
      })

      clearTimeout(timeoutId)
      const responseTime = Date.now() - startTime

      results.push({
        name: service.name,
        url: service.url,
        status: 'online',
        responseTime,
        lastChecked: new Date()
      })

    } catch (error) {
      const responseTime = Date.now() - startTime

      results.push({
        name: service.name,
        url: service.url,
        status: 'offline',
        responseTime,
        error: error instanceof Error ? error.message : 'Unknown error',
        lastChecked: new Date()
      })

      // Добавляем рекомендации
      if (service.name === 'Keycloak SSO') {
        recommendations.push('Keycloak недоступен - будет использован demo режим аутентификации')
      } else if (service.name === 'Odoo Backend') {
        recommendations.push('Odoo недоступен - некоторые бизнес-функции будут ограничены')
      } else if (service.name === 'AI Orchestrator') {
        recommendations.push('AI сервисы недоступны - AI функции будут отключены')
      }
    }
  }

  // Определяем общий статус
  const onlineServices = results.filter(s => s.status === 'online').length
  const totalServices = results.length

  let overall: 'healthy' | 'degraded' | 'offline'

  if (onlineServices === totalServices) {
    overall = 'healthy'
  } else if (onlineServices >= totalServices / 2) {
    overall = 'degraded'
    recommendations.push(`${totalServices - onlineServices} из ${totalServices} сервисов недоступны`)
  } else {
    overall = 'offline'
    recommendations.push('Большинство сервисов недоступно - переключаемся в offline режим')
  }

  return {
    overall,
    services: results,
    recommendations
  }
}

// Fallback конфигурация для различных сценариев
export function getFallbackConfig(health: PlatformHealth) {
  const config = {
    authMode: 'demo' as 'keycloak' | 'demo' | 'offline',
    dataMode: 'mock' as 'odoo' | 'supabase' | 'mock' | 'offline',
    aiMode: 'disabled' as 'enabled' | 'limited' | 'disabled',
    realtimeMode: 'disabled' as 'enabled' | 'disabled',
    features: {
      sso: false,
      multiTenant: false,
      ai: false,
      realtime: false,
      analytics: false
    }
  }

  // Проверяем доступность Keycloak
  const keycloak = health.services.find(s => s.name === 'Keycloak SSO')
  if (keycloak?.status === 'online') {
    config.authMode = 'keycloak'
    config.features.sso = true
    config.features.multiTenant = true
  }

  // Проверяем доступность Odoo
  const odoo = health.services.find(s => s.name === 'Odoo Backend')
  if (odoo?.status === 'online') {
    config.dataMode = 'odoo'
    config.features.analytics = true
  }

  // Проверяем AI сервисы
  const ai = health.services.find(s => s.name === 'AI Orchestrator')
  if (ai?.status === 'online') {
    config.aiMode = 'enabled'
    config.features.ai = true
  }

  // Проверяем Supabase
  const supabase = health.services.find(s => s.name === 'Supabase')
  if (supabase?.status === 'online') {
    config.features.realtime = true
    config.realtimeMode = 'enabled'
    if (config.dataMode === 'mock') {
      config.dataMode = 'supabase'
    }
  }

  return config
}

// Demo данные для fallback режима
export const demoUser = {
  id: 'demo-user-123',
  email: 'demo@bcm-platform.com',
  firstName: 'Demo',
  lastName: 'User',
  fullName: 'Demo User',
  companyId: 1,
  companyName: 'Demo BCM Company',
  role: 'org_admin' as const,
  departments: ['IT', 'Risk Management'],
  sessionId: 'demo-session-' + Date.now(),
  accessToken: 'demo-access-token',
  refreshToken: 'demo-refresh-token',
  expiresAt: new Date(Date.now() + 24 * 60 * 60 * 1000), // 24 часа
  permissions: [
    'bcm.read_all',
    'bcm.write_all',
    'bcm.admin',
    'bcm.read_bia',
    'bcm.write_bia',
    'bcm.read_risk_assessment',
    'bcm.write_risk_assessment',
    'bcm.read_incidents',
    'bcm.write_incidents',
    'bcm.read_plans',
    'bcm.write_plans'
  ],
  modules: [
    'bia',
    'risk_management',
    'incidents',
    'plans',
    'governance',
    'training',
    'exercise',
    'templates',
    'ai_analysis',
    'reporting'
  ],
  source: 'demo',
  avatarUrl: '/avatars/demo-user.png',
  theme: 'light',
  language: 'en',
  timezone: 'UTC'
}

// Инициализация платформы с проверкой здоровья
export async function initializePlatform() {
  console.log('🚀 Initializing BCM Platform...')

  // Проверяем здоровье сервисов
  const health = await checkPlatformHealth()
  console.log('📊 Platform Health Check:', health)

  // Получаем fallback конфигурацию
  const config = getFallbackConfig(health)
  console.log('⚙️ Platform Configuration:', config)

  // Выводим статус в консоль
  if (health.overall === 'healthy') {
    console.log('✅ All services online - Full functionality available')
  } else if (health.overall === 'degraded') {
    console.log('⚠️ Some services offline - Limited functionality')
    health.recommendations.forEach(rec => console.log(`   - ${rec}`))
  } else {
    console.log('🔴 Most services offline - Demo mode active')
    health.recommendations.forEach(rec => console.log(`   - ${rec}`))
  }

  // Сохраняем конфигурацию для использования в приложении
  if (typeof window !== 'undefined') {
    window.bcmPlatformHealth = health
    window.bcmPlatformConfig = config
  }

  return { health, config }
}

// Global declarations
declare global {
  interface Window {
    bcmPlatformHealth?: PlatformHealth
    bcmPlatformConfig?: ReturnType<typeof getFallbackConfig>
  }
}

// Utility functions
export function isServiceOnline(serviceName: string): boolean {
  const health = typeof window !== 'undefined' ? window.bcmPlatformHealth : null
  const service = health?.services.find(s => s.name === serviceName)
  return service?.status === 'online'
}

export function getPlatformConfig() {
  return typeof window !== 'undefined' ? window.bcmPlatformConfig : null
}

export function getServiceUrl(serviceName: string): string | null {
  const health = typeof window !== 'undefined' ? window.bcmPlatformHealth : null
  const service = health?.services.find(s => s.name === serviceName)
  return service?.url || null
}