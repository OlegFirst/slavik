// Базовый класс для всех оркестраторов системы

const EventEmitter = require('events');

class BaseOrchestrator extends EventEmitter {
  constructor(level, config = {}) {
    super();

    this.level = level; // 'system', 'bridge', 'program', 'client', 'sandbox'
    this.config = config;
    this.services = new Map();
    this.requiredServices = new Map();
    this.status = 'initializing';
    this.startTime = Date.now();

    // Статистика
    this.stats = {
      requestsHandled: 0,
      requestsFailed: 0,
      servicesLoaded: 0,
      servicesFailed: 0,
      eventsEmitted: 0,
      eventsReceived: 0
    };

    // Здоровье сервисов
    this.healthChecks = new Map();

    // Подписки на другие оркестраторы
    this.subscriptions = new Map();
  }

  // Определение обязательных сервисов для уровня
  defineRequiredServices() {
    // Переопределяется в наследниках
    throw new Error('defineRequiredServices() must be implemented');
  }

  // Инициализация оркестратора
  async initialize() {
    console.log(`🚀 Initializing ${this.level} Orchestrator...`);

    try {
      // Определяем обязательные сервисы
      this.defineRequiredServices();

      // Загружаем сервисы
      await this.loadServices();

      // Настраиваем health checks
      this.setupHealthChecks();

      // Начинаем мониторинг
      this.startMonitoring();

      this.status = 'ready';
      console.log(`✅ ${this.level} Orchestrator ready!`);

      // Эмитим событие готовности
      this.emit(`${this.level}.orchestrator.ready`, {
        level: this.level,
        services: Array.from(this.services.keys()),
        timestamp: Date.now()
      });

      return true;
    } catch (error) {
      this.status = 'failed';
      console.error(`❌ ${this.level} Orchestrator initialization failed:`, error);
      throw error;
    }
  }

  // Загрузка сервисов
  async loadServices() {
    for (const [name, config] of this.requiredServices) {
      try {
        console.log(`  Loading ${name}...`);

        // Пробуем загрузить основную реализацию
        const service = await this.loadService(name, config);

        if (service) {
          this.services.set(name, service);
          this.stats.servicesLoaded++;
          console.log(`    ✅ ${name} loaded`);
        } else {
          throw new Error(`Failed to load ${name}`);
        }

      } catch (error) {
        console.warn(`    ⚠️ ${name} failed, trying fallback...`);

        // Пробуем fallback
        const fallback = await this.loadFallback(name, config);

        if (fallback) {
          this.services.set(name, fallback);
          this.stats.servicesLoaded++;
          console.log(`    ✅ ${name} loaded (fallback)`);
        } else if (config.critical) {
          // Критичный сервис без fallback - фатальная ошибка
          throw new Error(`Critical service ${name} failed and has no fallback`);
        } else {
          // Некритичный сервис - продолжаем без него
          this.stats.servicesFailed++;
          console.warn(`    ❌ ${name} skipped (non-critical)`);
        }
      }
    }
  }

  // Загрузка конкретного сервиса
  async loadService(name, config) {
    // Определяем путь к сервису
    const servicePath = config.path || `./${this.level}-services/${name}`;

    try {
      // Динамическая загрузка модуля
      const ServiceClass = require(servicePath);

      // Создаем экземпляр
      const service = new ServiceClass(config.options || {});

      // Инициализируем если есть метод
      if (service.initialize) {
        await service.initialize();
      }

      return service;

    } catch (error) {
      // Если основная реализация недоступна
      if (config.implementations && config.implementations.length > 0) {
        // Пробуем альтернативные реализации
        for (const impl of config.implementations) {
          try {
            const altPath = `./${this.level}-services/${name}/${impl}`;
            const AltServiceClass = require(altPath);
            const service = new AltServiceClass(config.options || {});

            if (service.initialize) {
              await service.initialize();
            }

            return service;
          } catch (implError) {
            continue; // Пробуем следующую реализацию
          }
        }
      }

      return null;
    }
  }

  // Загрузка fallback сервиса
  async loadFallback(name, config) {
    if (!config.fallback) {
      return null;
    }

    try {
      // Fallback может быть простым объектом или классом
      if (typeof config.fallback === 'string') {
        const FallbackClass = require(`./${this.level}-services/${name}/fallback`);
        return new FallbackClass();
      } else if (typeof config.fallback === 'object') {
        // Простой fallback объект
        return config.fallback;
      } else if (typeof config.fallback === 'function') {
        // Fallback функция
        return { process: config.fallback };
      }
    } catch (error) {
      console.error(`Failed to load fallback for ${name}:`, error);
    }

    // Последний резерв - mock объект
    return {
      name: `${name}-mock`,
      process: async (request) => {
        console.warn(`Mock ${name} processing request`);
        return { mock: true, service: name };
      },
      healthCheck: async () => ({ status: 'mock' })
    };
  }

  // Обработка запроса
  async handle(request, context = {}) {
    this.stats.requestsHandled++;

    const enrichedContext = {
      ...context,
      level: this.level,
      orchestrator: this.constructor.name,
      timestamp: Date.now(),
      requestId: this.generateRequestId()
    };

    try {
      // Проходим по цепочке сервисов
      for (const [name, service] of this.services) {
        if (this.shouldProcessService(name, request, enrichedContext)) {
          console.log(`  ${this.level}: Processing with ${name}`);

          // Обрабатываем через сервис
          const result = await this.processWithService(
            service,
            request,
            enrichedContext
          );

          // Добавляем результат в контекст
          enrichedContext[name] = result;

          // Проверяем, нужно ли прервать цепочку
          if (result && result.stopChain) {
            break;
          }
        }
      }

      // Эмитим событие успешной обработки
      this.emitEvent('request.processed', {
        request,
        context: enrichedContext,
        level: this.level
      });

      return {
        success: true,
        level: this.level,
        context: enrichedContext
      };

    } catch (error) {
      this.stats.requestsFailed++;

      // Эмитим событие ошибки
      this.emitEvent('request.failed', {
        request,
        error: error.message,
        level: this.level
      });

      return {
        success: false,
        level: this.level,
        error: error.message,
        context: enrichedContext
      };
    }
  }

  // Определяем нужно ли обрабатывать через сервис
  shouldProcessService(serviceName, request, context) {
    const service = this.services.get(serviceName);

    // Если у сервиса есть метод canHandle
    if (service && service.canHandle) {
      return service.canHandle(request, context);
    }

    // По умолчанию обрабатываем все
    return true;
  }

  // Обработка через конкретный сервис
  async processWithService(service, request, context) {
    try {
      if (service.process) {
        return await service.process(request, context);
      } else if (typeof service === 'function') {
        return await service(request, context);
      } else {
        return { processed: true };
      }
    } catch (error) {
      console.error(`Service processing error:`, error);

      // Если сервис критичный - пробрасываем ошибку
      const serviceConfig = this.getServiceConfig(service);
      if (serviceConfig && serviceConfig.critical) {
        throw error;
      }

      // Иначе продолжаем с ошибкой в контексте
      return { error: error.message };
    }
  }

  // Подписка на другой оркестратор
  subscribe(otherOrchestrator, eventPatterns = ['*']) {
    if (!otherOrchestrator || !otherOrchestrator.on) {
      throw new Error('Invalid orchestrator for subscription');
    }

    const subscription = {
      orchestrator: otherOrchestrator,
      patterns: eventPatterns,
      handlers: []
    };

    // Подписываемся на события
    for (const pattern of eventPatterns) {
      const handler = (data) => {
        this.stats.eventsReceived++;
        this.handleExternalEvent(otherOrchestrator.level, pattern, data);
      };

      otherOrchestrator.on(pattern, handler);
      subscription.handlers.push({ pattern, handler });
    }

    this.subscriptions.set(otherOrchestrator.level, subscription);

    console.log(`📡 ${this.level} subscribed to ${otherOrchestrator.level} events`);
  }

  // Обработка внешнего события
  async handleExternalEvent(sourceLevel, eventType, data) {
    console.log(`📨 ${this.level} received ${eventType} from ${sourceLevel}`);

    // Определяем нужно ли обрабатывать
    if (this.shouldHandleEvent(sourceLevel, eventType, data)) {
      // Обрабатываем как обычный запрос
      await this.handle(data, {
        source: sourceLevel,
        eventType: eventType,
        external: true
      });
    }
  }

  // Определяем нужно ли обрабатывать событие
  shouldHandleEvent(sourceLevel, eventType, data) {
    // Переопределяется в наследниках
    return true;
  }

  // Эмиссия события
  emitEvent(eventType, data) {
    this.stats.eventsEmitted++;
    const fullEventType = `${this.level}.${eventType}`;

    console.log(`📢 ${this.level} emitting ${fullEventType}`);

    this.emit(fullEventType, data);
    this.emit('*', { type: fullEventType, data }); // Для wildcard подписок
  }

  // Настройка health checks
  setupHealthChecks() {
    for (const [name, service] of this.services) {
      if (service.healthCheck) {
        this.healthChecks.set(name, service.healthCheck.bind(service));
      }
    }
  }

  // Мониторинг
  startMonitoring() {
    // Периодическая проверка здоровья
    setInterval(async () => {
      for (const [name, checkFn] of this.healthChecks) {
        try {
          const health = await checkFn();

          if (health.status !== 'healthy') {
            console.warn(`⚠️ ${this.level}/${name} is ${health.status}`);

            // Пробуем восстановить
            await this.recoverService(name);
          }
        } catch (error) {
          console.error(`Health check failed for ${name}:`, error);
        }
      }
    }, this.config.healthCheckInterval || 30000);

    // Сбор метрик
    setInterval(() => {
      this.emitEvent('metrics', this.getMetrics());
    }, this.config.metricsInterval || 60000);
  }

  // Восстановление сервиса
  async recoverService(serviceName) {
    const config = this.requiredServices.get(serviceName);

    if (!config) return;

    console.log(`🔧 Attempting to recover ${serviceName}...`);

    try {
      // Пробуем перезагрузить
      const service = await this.loadService(serviceName, config);

      if (service) {
        this.services.set(serviceName, service);
        console.log(`✅ ${serviceName} recovered`);
      }
    } catch (error) {
      console.error(`Failed to recover ${serviceName}:`, error);
    }
  }

  // Получение метрик
  getMetrics() {
    return {
      level: this.level,
      status: this.status,
      stats: { ...this.stats },
      services: {
        loaded: this.services.size,
        healthy: Array.from(this.healthChecks.keys()).length
      },
      subscriptions: this.subscriptions.size,
      timestamp: Date.now()
    };
  }

  // Получение статуса здоровья
  async getHealthStatus() {
    const memory = process.memoryUsage();

    return {
      level: this.level,
      status: this.status,
      stats: { ...this.stats },
      services: {
        loaded: this.services.size,
        healthy: Array.from(this.healthChecks.keys()).length,
        list: Array.from(this.services.keys())
      },
      subscriptions: this.subscriptions.size,
      memory: {
        heapUsed: memory.heapUsed,
        heapTotal: memory.heapTotal,
        external: memory.external
      },
      uptime: Date.now() - this.startTime,
      timestamp: Date.now()
    };
  }

  // Генерация ID запроса
  generateRequestId() {
    return `${this.level}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  // Получение конфигурации сервиса
  getServiceConfig(service) {
    for (const [name, config] of this.requiredServices) {
      if (this.services.get(name) === service) {
        return config;
      }
    }
    return null;
  }

  // Graceful shutdown
  async shutdown() {
    console.log(`🛑 Shutting down ${this.level} Orchestrator...`);

    this.status = 'shutting_down';

    // Отписываемся от событий
    for (const [level, subscription] of this.subscriptions) {
      for (const { pattern, handler } of subscription.handlers) {
        subscription.orchestrator.off(pattern, handler);
      }
    }

    // Останавливаем сервисы
    for (const [name, service] of this.services) {
      if (service.shutdown) {
        console.log(`  Stopping ${name}...`);
        await service.shutdown();
      }
    }

    this.status = 'shutdown';
    console.log(`✅ ${this.level} Orchestrator shutdown complete`);
  }
}

module.exports = BaseOrchestrator;