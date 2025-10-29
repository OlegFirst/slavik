// CLIENT INFRASTRUCTURE - Клиентская инфраструктура и безопасность
// Этот слой обслуживает реальных клиентов/пользователей

class ClientInfrastructure {
  constructor() {
    this.components = {
      security: null,
      auth: null,
      databases: null,
      monitoring: null,
      apiGateway: null,
      coordinators: null
    };

    this.status = 'initializing';
    this.healthChecks = new Map();
  }

  async initialize() {
    console.log('🚀 Initializing Client Infrastructure...');

    // 1. Security Gateway
    this.components.security = await this.initializeSecurity();

    // 2. Authentication & Authorization
    this.components.auth = await this.initializeAuth();

    // 3. Client Databases
    this.components.databases = await this.initializeDatabases();

    // 4. Monitoring & Metrics
    this.components.monitoring = await this.initializeMonitoring();

    // 5. API Gateway
    this.components.apiGateway = await this.initializeAPIGateway();

    // 6. Coordinators
    this.components.coordinators = await this.initializeCoordinators();

    this.status = 'ready';
    console.log('✅ Client Infrastructure Ready!');

    return this;
  }

  // SECURITY LAYER
  async initializeSecurity() {
    const SecurityGateway = require('./security/security-gateway');
    const security = new SecurityGateway({
      waf: {
        enabled: true,
        rules: 'OWASP_CRS_3.0',
        customRules: './security/waf-rules.json'
      },
      ddosProtection: {
        enabled: true,
        maxRequestsPerMinute: 1000,
        blacklistDuration: 3600
      },
      rateLimiting: {
        enabled: true,
        defaultLimit: 100,
        premiumLimit: 1000
      },
      encryption: {
        algorithm: 'AES-256-GCM',
        keyRotation: true,
        rotationInterval: 86400
      }
    });

    await security.initialize();
    this.healthChecks.set('security', security.healthCheck.bind(security));

    return security;
  }

  // AUTH LAYER
  async initializeAuth() {
    const AuthManager = require('./auth/auth-manager');
    const auth = new AuthManager({
      providers: {
        keycloak: {
          enabled: true,
          url: process.env.KEYCLOAK_URL || 'http://localhost:8080',
          realm: 'bcm-platform',
          clientId: 'bcm-client',
          clientSecret: process.env.KEYCLOAK_SECRET
        },
        jwt: {
          secret: process.env.JWT_SECRET || 'change-me-in-production',
          expiresIn: '24h',
          refreshExpiresIn: '7d'
        },
        oauth2: {
          enabled: true,
          providers: ['google', 'github', 'microsoft']
        },
        mfa: {
          enabled: true,
          methods: ['totp', 'sms', 'email']
        }
      },
      authorization: {
        rbac: {
          enabled: true,
          rolesSource: 'database'
        },
        abac: {
          enabled: true,
          policyEngine: 'opa',
          policiesPath: './auth/policies/'
        },
        cache: {
          provider: 'redis',
          ttl: 300
        }
      }
    });

    await auth.initialize();
    this.healthChecks.set('auth', auth.healthCheck.bind(auth));

    return auth;
  }

  // DATABASE LAYER
  async initializeDatabases() {
    const DatabaseManager = require('./databases/database-manager');
    const databases = new DatabaseManager({
      postgres: {
        enabled: true,
        host: process.env.PG_HOST || 'localhost',
        port: 5432,
        database: 'bcm_clients',
        user: process.env.PG_USER || 'postgres',
        password: process.env.PG_PASSWORD,
        pool: {
          min: 2,
          max: 10
        }
      },
      mongodb: {
        enabled: true,
        url: process.env.MONGO_URL || 'mongodb://localhost:27017',
        database: 'bcm_documents',
        options: {
          useUnifiedTopology: true
        }
      },
      redis: {
        enabled: true,
        host: process.env.REDIS_HOST || 'localhost',
        port: 6379,
        password: process.env.REDIS_PASSWORD,
        databases: {
          cache: 0,
          sessions: 1,
          pubsub: 2
        }
      },
      influxdb: {
        enabled: true,
        url: process.env.INFLUX_URL || 'http://localhost:8086',
        token: process.env.INFLUX_TOKEN,
        org: 'bcm-platform',
        bucket: 'metrics'
      }
    });

    await databases.initialize();
    this.healthChecks.set('databases', databases.healthCheck.bind(databases));

    return databases;
  }

  // MONITORING LAYER
  async initializeMonitoring() {
    const MonitoringStack = require('./monitoring/monitoring-stack');
    const monitoring = new MonitoringStack({
      prometheus: {
        enabled: true,
        port: 9090,
        scrapeInterval: '15s',
        retention: '30d',
        exporters: [
          'node_exporter',
          'postgres_exporter',
          'redis_exporter',
          'custom_bcm_exporter'
        ]
      },
      grafana: {
        enabled: true,
        port: 3000,
        dashboards: [
          'system-overview',
          'bcm-metrics',
          'client-analytics',
          'security-monitoring'
        ]
      },
      elasticsearch: {
        enabled: true,
        url: process.env.ELASTIC_URL || 'http://localhost:9200',
        indices: {
          logs: 'bcm-logs',
          events: 'bcm-events',
          audit: 'bcm-audit'
        }
      },
      jaeger: {
        enabled: true,
        agentHost: 'localhost',
        agentPort: 6831,
        samplingRate: 0.1
      }
    });

    await monitoring.initialize();
    this.healthChecks.set('monitoring', monitoring.healthCheck.bind(monitoring));

    // Экспорт метрик для Prometheus
    monitoring.registerMetrics({
      bcm_requests_total: 'Counter for total BCM requests',
      bcm_request_duration: 'Histogram for request duration',
      bcm_active_users: 'Gauge for active users',
      bcm_errors_total: 'Counter for errors'
    });

    return monitoring;
  }

  // API GATEWAY
  async initializeAPIGateway() {
    const APIGateway = require('./api-gateway/gateway');
    const gateway = new APIGateway({
      provider: 'kong', // или 'traefik', 'nginx'
      port: 8000,
      adminPort: 8001,

      routes: {
        '/api/system/*': {
          target: 'http://system-components:3000',
          rateLimit: 1000,
          auth: 'jwt'
        },
        '/api/bcm/*': {
          target: 'http://program-components:3001',
          rateLimit: 500,
          auth: 'jwt',
          transform: true
        },
        '/api/bridge/*': {
          target: 'http://bridge-layer:3002',
          rateLimit: 100,
          auth: 'jwt',
          cache: true
        }
      },

      plugins: {
        cors: {
          enabled: true,
          origins: ['*'],
          credentials: true
        },
        compression: {
          enabled: true,
          level: 6
        },
        caching: {
          enabled: true,
          ttl: 300
        },
        logging: {
          enabled: true,
          level: 'info'
        }
      }
    });

    await gateway.initialize();
    this.healthChecks.set('apiGateway', gateway.healthCheck.bind(gateway));

    return gateway;
  }

  // COORDINATORS
  async initializeCoordinators() {
    const CoordinatorServices = require('./coordinators/coordinator-services');
    const coordinators = new CoordinatorServices({

      // Координатор зависимостей
      dependencyCoordinator: {
        enabled: true,
        scanInterval: 60000,
        strategies: {
          fallback: 'auto',
          versionConflict: 'latest',
          unavailable: 'cache'
        }
      },

      // Координатор устойчивости
      resilienceCoordinator: {
        enabled: true,
        circuitBreaker: {
          threshold: 5,
          timeout: 30000,
          resetTimeout: 60000
        },
        retry: {
          maxAttempts: 3,
          backoff: 'exponential',
          maxDelay: 10000
        },
        bulkhead: {
          maxConcurrent: 10,
          maxQueue: 100
        }
      },

      // Координатор метрик
      metricsCoordinator: {
        enabled: true,
        prometheus: {
          endpoint: '/metrics',
          namespace: 'bcm_client'
        },
        businessMetrics: [
          'user_actions',
          'api_calls',
          'error_rates',
          'response_times'
        ]
      }
    });

    await coordinators.initialize();
    this.healthChecks.set('coordinators', coordinators.healthCheck.bind(coordinators));

    return coordinators;
  }

  // Централизованная проверка здоровья
  async performHealthCheck() {
    const results = {};

    for (const [component, checkFn] of this.healthChecks) {
      try {
        results[component] = await checkFn();
      } catch (error) {
        results[component] = {
          status: 'unhealthy',
          error: error.message
        };
      }
    }

    return {
      timestamp: new Date(),
      status: this.status,
      components: results,
      overall: Object.values(results).every(r => r.status === 'healthy') ? 'healthy' : 'degraded'
    };
  }

  // Обработка клиентских запросов
  async handleClientRequest(request) {
    // 1. Security check
    const securityCheck = await this.components.security.validate(request);
    if (!securityCheck.passed) {
      return { error: 'Security validation failed', details: securityCheck.reason };
    }

    // 2. Authentication
    const authResult = await this.components.auth.authenticate(request);
    if (!authResult.authenticated) {
      return { error: 'Authentication failed', code: 401 };
    }

    // 3. Authorization
    const authzResult = await this.components.auth.authorize(authResult.user, request.resource);
    if (!authzResult.authorized) {
      return { error: 'Access denied', code: 403 };
    }

    // 4. Rate limiting
    const rateLimitCheck = await this.components.security.checkRateLimit(authResult.user.id);
    if (!rateLimitCheck.allowed) {
      return { error: 'Rate limit exceeded', retryAfter: rateLimitCheck.retryAfter };
    }

    // 5. Route through API Gateway
    const response = await this.components.apiGateway.route(request, {
      user: authResult.user,
      permissions: authzResult.permissions
    });

    // 6. Log metrics
    await this.components.monitoring.logRequest({
      user: authResult.user.id,
      resource: request.resource,
      duration: response.duration,
      status: response.status
    });

    return response;
  }

  // Graceful shutdown
  async shutdown() {
    console.log('🛑 Shutting down Client Infrastructure...');

    for (const [name, component] of Object.entries(this.components)) {
      if (component && component.shutdown) {
        console.log(`  Shutting down ${name}...`);
        await component.shutdown();
      }
    }

    this.status = 'shutdown';
    console.log('✅ Client Infrastructure shutdown complete');
  }
}

module.exports = ClientInfrastructure;