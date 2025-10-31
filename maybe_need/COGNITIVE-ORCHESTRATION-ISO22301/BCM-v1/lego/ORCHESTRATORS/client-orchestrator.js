// Client Orchestrator - оркестратор клиентского уровня

const BaseOrchestrator = require('./base-orchestrator');

class ClientOrchestrator extends BaseOrchestrator {
  constructor(config = {}) {
    super('client', config);

    // Специфичные для клиентского уровня параметры
    this.sessions = new Map();        // Активные сессии пользователей
    this.rateLimits = new Map();      // Rate limiting для пользователей
    this.securityEvents = [];         // События безопасности
    this.apiRoutes = new Map();       // Маршруты API
    this.websockets = new Map();      // WebSocket соединения
    this.metrics = {
      totalRequests: 0,
      successfulRequests: 0,
      failedRequests: 0,
      blockedRequests: 0,
      activeUsers: 0
    };
  }

  // Определение обязательных сервисов клиентского уровня
  defineRequiredServices() {
    this.requiredServices.set('auth-service', {
      critical: true,
      purpose: 'Аутентификация и авторизация пользователей',
      path: '../CLIENT_INFRASTRUCTURE/auth',
      fallback: {
        name: 'basic-auth',
        users: new Map([['admin', { password: 'admin', role: 'admin' }]]),
        sessions: new Map(),
        process: async (request) => {
          if (request.action === 'authenticate') {
            const user = this.users.get(request.username);
            if (user && user.password === request.password) {
              const token = `token-${Date.now()}-${Math.random()}`;
              this.sessions.set(token, { user: request.username, expires: Date.now() + 3600000 });
              return { authenticated: true, token };
            }
            return { authenticated: false };
          } else if (request.action === 'validate') {
            const session = this.sessions.get(request.token);
            return { valid: session && session.expires > Date.now() };
          }
          return { error: 'Unknown auth action' };
        }
      },
      options: {
        providers: ['local', 'jwt', 'oauth2'],
        sessionTTL: 3600000,
        mfaEnabled: false
      }
    });

    this.requiredServices.set('security-gateway', {
      critical: true,
      purpose: 'Защита от атак и угроз',
      path: '../CLIENT_INFRASTRUCTURE/security/security-gateway',
      fallback: {
        name: 'basic-security',
        process: async (request) => {
          // Базовая проверка безопасности
          const suspicious = this.checkSuspiciousPatterns(request);
          return {
            passed: !suspicious,
            reason: suspicious ? 'Suspicious pattern detected' : null
          };
        },
        checkSuspiciousPatterns: (request) => {
          const patterns = ['<script', 'DROP TABLE', '../..', 'eval('];
          const requestStr = JSON.stringify(request);
          return patterns.some(p => requestStr.includes(p));
        }
      },
      options: {
        wafEnabled: true,
        ddosProtection: true,
        rateLimiting: true,
        encryptionEnabled: true
      }
    });

    this.requiredServices.set('database-service', {
      critical: true,
      purpose: 'Управление клиентскими данными',
      fallback: {
        name: 'memory-db',
        storage: new Map(),
        process: async (request) => {
          switch (request.action) {
            case 'save':
              this.storage.set(request.key, request.value);
              return { saved: true };
            case 'get':
              return { value: this.storage.get(request.key) };
            case 'delete':
              this.storage.delete(request.key);
              return { deleted: true };
            case 'query':
              const results = [];
              this.storage.forEach((value, key) => {
                if (this.matchesQuery(value, request.query)) {
                  results.push({ key, value });
                }
              });
              return { results };
            default:
              return { error: 'Unknown database action' };
          }
        },
        matchesQuery: (value, query) => {
          // Простое сопоставление
          return Object.keys(query).every(k => value[k] === query[k]);
        }
      },
      options: {
        databases: ['postgres', 'mongodb', 'redis'],
        connectionPool: true,
        caching: true
      }
    });

    this.requiredServices.set('monitoring-service', {
      critical: false,
      purpose: 'Мониторинг и метрики',
      fallback: {
        name: 'console-monitor',
        metrics: [],
        process: async (request) => {
          if (request.action === 'log') {
            console.log(`[METRIC] ${request.name}: ${request.value}`);
            this.metrics.push({ ...request, timestamp: Date.now() });
            return { logged: true };
          } else if (request.action === 'get') {
            return { metrics: this.metrics };
          }
          return { metrics: [] };
        }
      },
      options: {
        providers: ['prometheus', 'grafana', 'elasticsearch'],
        exportInterval: 15000,
        retention: '30d'
      }
    });

    this.requiredServices.set('api-gateway', {
      critical: false,
      purpose: 'API маршрутизация и управление',
      fallback: {
        name: 'simple-router',
        routes: new Map(),
        process: async (request) => {
          if (request.action === 'route') {
            const handler = this.routes.get(request.path) || this.routes.get('*');
            if (handler) {
              return await handler(request);
            }
            return { error: 'Route not found', status: 404 };
          } else if (request.action === 'register') {
            this.routes.set(request.path, request.handler);
            return { registered: true };
          }
          return { error: 'Unknown routing action' };
        }
      },
      options: {
        cors: true,
        compression: true,
        caching: true,
        rateLimit: 1000
      }
    });
  }

  // Переопределяем обработку для клиентского уровня
  async handle(request, context = {}) {
    // Увеличиваем счетчик запросов
    this.metrics.totalRequests++;

    // Добавляем клиентский контекст
    const clientContext = {
      ...context,
      clientTime: Date.now(),
      ip: request.ip || context.ip || 'unknown',
      userAgent: request.headers?.['user-agent'] || 'unknown',
      sessionId: context.sessionId || this.generateSessionId()
    };

    try {
      // 1. Проверка безопасности
      const securityResult = await this.checkSecurity(request, clientContext);
      if (!securityResult.passed) {
        this.metrics.blockedRequests++;
        this.logSecurityEvent('blocked', request, securityResult.reason);
        return {
          error: 'Security check failed',
          reason: securityResult.reason,
          status: 403
        };
      }

      // 2. Аутентификация
      const authResult = await this.authenticate(request, clientContext);
      if (request.requiresAuth !== false && !authResult.authenticated) {
        this.metrics.failedRequests++;
        return {
          error: 'Authentication required',
          status: 401
        };
      }

      // 3. Авторизация
      if (authResult.authenticated) {
        const authzResult = await this.authorize(authResult.user, request, clientContext);
        if (!authzResult.authorized) {
          this.metrics.failedRequests++;
          this.logSecurityEvent('unauthorized', request, authResult.user);
          return {
            error: 'Access denied',
            status: 403
          };
        }
        clientContext.user = authResult.user;
        clientContext.permissions = authzResult.permissions;
      }

      // 4. Rate limiting
      const rateLimitResult = await this.checkRateLimit(clientContext);
      if (!rateLimitResult.allowed) {
        this.metrics.blockedRequests++;
        return {
          error: 'Rate limit exceeded',
          retryAfter: rateLimitResult.retryAfter,
          status: 429
        };
      }

      // 5. Обработка запроса по типу
      let result;
      switch (request.type) {
        case 'http':
          result = await this.handleHTTPRequest(request, clientContext);
          break;
        case 'websocket':
          result = await this.handleWebSocketRequest(request, clientContext);
          break;
        case 'graphql':
          result = await this.handleGraphQLRequest(request, clientContext);
          break;
        case 'grpc':
          result = await this.handleGRPCRequest(request, clientContext);
          break;
        default:
          result = await this.routeRequest(request, clientContext);
      }

      // 6. Логирование и метрики
      await this.logRequest(request, result, clientContext);
      this.metrics.successfulRequests++;

      // 7. Обновление сессии
      if (clientContext.sessionId) {
        this.updateSession(clientContext.sessionId, clientContext);
      }

      // Эмитим событие успешной обработки
      this.emitEvent('client.request.processed', {
        request: { ...request, sensitive: undefined }, // Убираем чувствительные данные
        result: result.success,
        userId: clientContext.user?.id,
        sessionId: clientContext.sessionId
      });

      return result;

    } catch (error) {
      this.metrics.failedRequests++;
      console.error('Client request error:', error);

      // Логируем ошибку
      await this.logError(error, request, clientContext);

      // Эмитим событие ошибки
      this.emitEvent('client.request.failed', {
        error: error.message,
        request: { type: request.type, path: request.path },
        sessionId: clientContext.sessionId
      });

      return {
        error: 'Internal server error',
        status: 500,
        requestId: clientContext.requestId
      };
    }
  }

  // Проверка безопасности
  async checkSecurity(request, context) {
    const securityGateway = this.services.get('security-gateway');

    if (!securityGateway) {
      return { passed: true }; // Если нет security gateway, пропускаем
    }

    if (securityGateway.process) {
      return await securityGateway.process({
        action: 'validate',
        request: request,
        ip: context.ip,
        headers: request.headers || {}
      });
    } else {
      return await securityGateway.validate(request, context);
    }
  }

  // Аутентификация
  async authenticate(request, context) {
    const authService = this.services.get('auth-service');

    // Проверяем различные методы аутентификации
    if (request.headers?.authorization) {
      // Bearer token
      const token = request.headers.authorization.replace('Bearer ', '');
      return await authService.process({
        action: 'validate',
        token: token
      });
    } else if (request.cookies?.sessionId) {
      // Session cookie
      return await authService.process({
        action: 'validateSession',
        sessionId: request.cookies.sessionId
      });
    } else if (request.apiKey) {
      // API key
      return await authService.process({
        action: 'validateApiKey',
        apiKey: request.apiKey
      });
    } else if (request.username && request.password) {
      // Basic auth
      return await authService.process({
        action: 'authenticate',
        username: request.username,
        password: request.password
      });
    }

    return { authenticated: false };
  }

  // Авторизация
  async authorize(user, request, context) {
    const authService = this.services.get('auth-service');

    if (!authService) {
      return { authorized: true, permissions: [] }; // Если нет auth service, разрешаем
    }

    return await authService.process({
      action: 'authorize',
      user: user,
      resource: request.resource || request.path,
      action: request.action || request.method || 'read',
      context: context
    });
  }

  // Проверка rate limit
  async checkRateLimit(context) {
    const key = context.user?.id || context.ip || 'anonymous';
    const now = Date.now();
    const window = 60000; // 1 минута
    const limit = context.user?.rateLimit || 100; // 100 запросов в минуту

    if (!this.rateLimits.has(key)) {
      this.rateLimits.set(key, {
        count: 1,
        resetTime: now + window
      });
      return { allowed: true };
    }

    const rateLimit = this.rateLimits.get(key);

    if (now > rateLimit.resetTime) {
      rateLimit.count = 1;
      rateLimit.resetTime = now + window;
      return { allowed: true };
    }

    rateLimit.count++;

    if (rateLimit.count > limit) {
      return {
        allowed: false,
        retryAfter: Math.ceil((rateLimit.resetTime - now) / 1000)
      };
    }

    return { allowed: true };
  }

  // Обработка HTTP запросов
  async handleHTTPRequest(request, context) {
    const apiGateway = this.services.get('api-gateway');

    if (apiGateway) {
      return await apiGateway.process({
        action: 'route',
        method: request.method,
        path: request.path,
        headers: request.headers,
        body: request.body,
        query: request.query,
        context: context
      });
    }

    // Fallback маршрутизация
    return await this.routeRequest(request, context);
  }

  // Обработка WebSocket запросов
  async handleWebSocketRequest(request, context) {
    if (request.action === 'connect') {
      // Новое WebSocket соединение
      const wsId = `ws-${Date.now()}-${Math.random()}`;
      this.websockets.set(wsId, {
        id: wsId,
        user: context.user,
        connected: Date.now(),
        context: context
      });

      this.emitEvent('websocket.connected', { wsId, userId: context.user?.id });

      return {
        connected: true,
        wsId: wsId,
        protocols: ['json', 'binary']
      };

    } else if (request.action === 'message') {
      // Сообщение через WebSocket
      const ws = this.websockets.get(request.wsId);
      if (!ws) {
        return { error: 'WebSocket not found' };
      }

      // Обрабатываем сообщение
      const result = await this.processWebSocketMessage(request.message, ws);

      // Broadcast если нужно
      if (result.broadcast) {
        await this.broadcastToWebSockets(result.data, result.filter);
      }

      return result;

    } else if (request.action === 'disconnect') {
      // Отключение WebSocket
      this.websockets.delete(request.wsId);
      this.emitEvent('websocket.disconnected', { wsId: request.wsId });
      return { disconnected: true };
    }

    return { error: 'Unknown WebSocket action' };
  }

  // Обработка GraphQL запросов
  async handleGraphQLRequest(request, context) {
    // Проверяем тип операции
    const operation = this.parseGraphQLOperation(request.query);

    if (operation.type === 'query') {
      // Выполняем query
      return await this.executeGraphQLQuery(operation, request.variables, context);
    } else if (operation.type === 'mutation') {
      // Проверяем права на mutation
      const authz = await this.authorize(context.user, { action: 'mutate' }, context);
      if (!authz.authorized) {
        return { error: 'Mutation not authorized' };
      }
      return await this.executeGraphQLMutation(operation, request.variables, context);
    } else if (operation.type === 'subscription') {
      // Подписка
      return await this.handleGraphQLSubscription(operation, request.variables, context);
    }

    return { error: 'Invalid GraphQL operation' };
  }

  // Обработка gRPC запросов
  async handleGRPCRequest(request, context) {
    // gRPC специфичная обработка
    return {
      message: 'gRPC handler',
      service: request.service,
      method: request.method,
      // Реальная реализация требует protobuf
      placeholder: true
    };
  }

  // Маршрутизация запросов
  async routeRequest(request, context) {
    // Определяем куда направить запрос
    const route = this.findRoute(request.path || request.action);

    if (route) {
      return await route.handler(request, context);
    }

    // Если маршрут не найден, пробуем отправить в Program уровень
    this.emitEvent('client.request.validated', {
      request: request,
      context: context
    });

    return {
      routed: true,
      destination: 'program',
      requestId: context.requestId
    };
  }

  // Логирование запроса
  async logRequest(request, result, context) {
    const monitoringService = this.services.get('monitoring-service');

    if (monitoringService) {
      await monitoringService.process({
        action: 'log',
        type: 'request',
        name: 'client_request',
        value: 1,
        labels: {
          method: request.method || request.type,
          path: request.path,
          status: result.status || (result.error ? 'error' : 'success'),
          userId: context.user?.id,
          duration: Date.now() - context.clientTime
        }
      });
    }
  }

  // Логирование ошибки
  async logError(error, request, context) {
    const monitoringService = this.services.get('monitoring-service');

    if (monitoringService) {
      await monitoringService.process({
        action: 'log',
        type: 'error',
        name: 'client_error',
        value: 1,
        error: {
          message: error.message,
          stack: error.stack,
          request: { type: request.type, path: request.path },
          context: { userId: context.user?.id, sessionId: context.sessionId }
        }
      });
    }

    // Сохраняем в security events если критично
    if (error.security) {
      this.logSecurityEvent('error', request, error.message);
    }
  }

  // Логирование событий безопасности
  logSecurityEvent(type, request, details) {
    const event = {
      type: type,
      timestamp: Date.now(),
      request: {
        ip: request.ip,
        path: request.path,
        method: request.method
      },
      details: details
    };

    this.securityEvents.push(event);

    // Ограничиваем размер лога
    if (this.securityEvents.length > 10000) {
      this.securityEvents.shift();
    }

    // Эмитим для мониторинга
    this.emitEvent('security.event', event);
  }

  // Обновление сессии
  updateSession(sessionId, context) {
    if (!this.sessions.has(sessionId)) {
      this.sessions.set(sessionId, {
        id: sessionId,
        created: Date.now(),
        requests: 0
      });
    }

    const session = this.sessions.get(sessionId);
    session.lastActivity = Date.now();
    session.requests++;
    session.user = context.user;

    // Обновляем метрику активных пользователей
    this.metrics.activeUsers = this.sessions.size;
  }

  // Генерация session ID
  generateSessionId() {
    return `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  // Поиск маршрута
  findRoute(path) {
    // Exact match
    if (this.apiRoutes.has(path)) {
      return this.apiRoutes.get(path);
    }

    // Pattern match
    for (const [pattern, route] of this.apiRoutes) {
      if (pattern.includes('*') && this.matchPattern(path, pattern)) {
        return route;
      }
    }

    return null;
  }

  // Сопоставление с паттерном
  matchPattern(path, pattern) {
    const regex = new RegExp('^' + pattern.replace(/\*/g, '.*') + '$');
    return regex.test(path);
  }

  // Парсинг GraphQL операции
  parseGraphQLOperation(query) {
    // Упрощенный парсер
    if (query.includes('query')) return { type: 'query', query };
    if (query.includes('mutation')) return { type: 'mutation', query };
    if (query.includes('subscription')) return { type: 'subscription', query };
    return { type: 'unknown', query };
  }

  // Обработка WebSocket сообщения
  async processWebSocketMessage(message, ws) {
    // Обработка в зависимости от типа сообщения
    if (message.type === 'ping') {
      return { type: 'pong', timestamp: Date.now() };
    }

    // Передаем дальше для обработки
    const result = await this.handle(message, ws.context);

    return {
      ...result,
      wsId: ws.id
    };
  }

  // Broadcast to WebSockets
  async broadcastToWebSockets(data, filter) {
    for (const [wsId, ws] of this.websockets) {
      if (!filter || filter(ws)) {
        // Отправляем сообщение (в реальности через WebSocket connection)
        this.emitEvent('websocket.send', { wsId, data });
      }
    }
  }

  // Проверка нужно ли обрабатывать событие
  shouldHandleEvent(sourceLevel, eventType, data) {
    // Client уровень обрабатывает входящие запросы
    const relevantEvents = [
      'incoming.request',
      'auth.required',
      'security.alert',
      'rate.limit.exceeded'
    ];

    return relevantEvents.some(pattern => eventType.includes(pattern.split('.')[0]));
  }

  // Получение метрик клиентского уровня
  getClientMetrics() {
    const metrics = super.getMetrics();

    metrics.client = {
      ...this.metrics,
      activeSessions: this.sessions.size,
      activeWebSockets: this.websockets.size,
      securityEvents: this.securityEvents.length,
      routes: this.apiRoutes.size
    };

    // Метрики по сессиям
    metrics.sessionMetrics = {
      average: this.calculateAverageSessionMetrics(),
      peak: this.calculatePeakLoad()
    };

    return metrics;
  }

  // Расчет средних метрик сессий
  calculateAverageSessionMetrics() {
    if (this.sessions.size === 0) return { requests: 0, duration: 0 };

    let totalRequests = 0;
    let totalDuration = 0;
    const now = Date.now();

    this.sessions.forEach(session => {
      totalRequests += session.requests || 0;
      totalDuration += (now - session.created);
    });

    return {
      requests: totalRequests / this.sessions.size,
      duration: totalDuration / this.sessions.size
    };
  }

  // Расчет пиковой нагрузки
  calculatePeakLoad() {
    // Анализируем последние 100 запросов
    const recentRequests = this.securityEvents
      .filter(e => e.type === 'request')
      .slice(-100);

    if (recentRequests.length === 0) return 0;

    // Группируем по секундам
    const requestsPerSecond = {};
    recentRequests.forEach(r => {
      const second = Math.floor(r.timestamp / 1000);
      requestsPerSecond[second] = (requestsPerSecond[second] || 0) + 1;
    });

    return Math.max(...Object.values(requestsPerSecond));
  }

  // Очистка старых данных
  cleanup() {
    const now = Date.now();
    const sessionTTL = 3600000; // 1 час

    // Очищаем старые сессии
    this.sessions.forEach((session, id) => {
      if (now - session.lastActivity > sessionTTL) {
        this.sessions.delete(id);
      }
    });

    // Очищаем старые rate limits
    this.rateLimits.forEach((limit, key) => {
      if (now > limit.resetTime + 60000) {
        this.rateLimits.delete(key);
      }
    });

    // Обновляем метрики
    this.metrics.activeUsers = this.sessions.size;
  }

  // Инициализация
  async initialize() {
    await super.initialize();

    // Регистрируем базовые маршруты
    this.apiRoutes.set('/health', {
      handler: async () => ({ status: 'healthy', timestamp: Date.now() })
    });

    this.apiRoutes.set('/metrics', {
      handler: async () => this.getClientMetrics()
    });

    // Периодическая очистка
    setInterval(() => {
      this.cleanup();
    }, 60000); // каждую минуту

    return true;
  }
}

module.exports = ClientOrchestrator;