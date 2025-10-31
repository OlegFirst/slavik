// Program Orchestrator - оркестратор программного уровня

const BaseOrchestrator = require('./base-orchestrator');

class ProgramOrchestrator extends BaseOrchestrator {
  constructor(config = {}) {
    super('program', config);

    // Специфичные для программного уровня параметры
    this.domains = new Map();         // Зарегистрированные домены
    this.modules = new Map();         // Загруженные модули
    this.adapters = new Map();        // Активные адаптеры
    this.userContexts = new Map();    // Контексты пользователей
  }

  // Определение обязательных сервисов программного уровня
  defineRequiredServices() {
    this.requiredServices.set('domain-registry', {
      critical: true,
      purpose: 'Управление доменами приложений',
      path: '../PROGRAM_COMPONENTS/DOMAIN_REGISTRY',
      fallback: {
        name: 'default-domain',
        domains: new Map([['default', { name: 'Default Domain', capabilities: [] }]]),
        process: async (request) => {
          if (request.action === 'register') {
            this.domains.set(request.domain.name, request.domain);
            return { registered: true };
          } else if (request.action === 'get') {
            return this.domains.get(request.domainName) || this.domains.get('default');
          }
          return { domains: Array.from(this.domains.keys()) };
        }
      },
      options: {
        autoDiscovery: true,
        defaultDomain: 'bcm'
      }
    });

    this.requiredServices.set('module-loader', {
      critical: true,
      purpose: 'Загрузка и управление модулями',
      path: '../PROGRAM_COMPONENTS/MODULE_LIBRARY',
      fallback: {
        name: 'static-modules',
        modules: new Map(),
        process: async (request) => {
          if (request.action === 'load') {
            // Имитация загрузки модуля
            const mockModule = {
              name: request.moduleName,
              capabilities: [],
              process: async (r) => ({ processed: true, module: request.moduleName })
            };
            this.modules.set(request.moduleName, mockModule);
            return { loaded: true, module: mockModule };
          }
          return { modules: Array.from(this.modules.keys()) };
        }
      },
      options: {
        lazyLoading: true,
        preload: ['business-impact-analysis', 'incident-management'],
        modulePath: '../PROGRAM_COMPONENTS/MODULE_LIBRARY'
      }
    });

    this.requiredServices.set('adapter-service', {
      critical: true,
      purpose: 'Интеграция с внешними платформами',
      path: '../PROGRAM_COMPONENTS/INTEGRATION_LAYER/platform-adapters',
      fallback: {
        name: 'mock-adapter',
        process: async (request) => {
          // Mock адаптер для тестирования
          console.log('Using mock adapter for:', request.platform);
          return {
            platform: request.platform || 'mock',
            result: { mocked: true, data: request.data },
            timestamp: Date.now()
          };
        }
      },
      options: {
        adapters: ['odoo', 'standalone', 'external'],
        defaultAdapter: 'odoo',
        connectionTimeout: 30000
      }
    });

    this.requiredServices.set('user-context', {
      critical: false,
      purpose: 'Персонализация для пользователей',
      path: '../PROGRAM_COMPONENTS/USER_CONTEXT',
      fallback: {
        name: 'default-context',
        process: async (request) => {
          // Базовый контекст без персонализации
          return {
            userId: request.userId || 'anonymous',
            preferences: {},
            role: 'user',
            personalization: 'default'
          };
        }
      },
      options: {
        cacheUserContext: true,
        contextTTL: 3600000, // 1 час
        trackPreferences: true
      }
    });

    this.requiredServices.set('business-logic', {
      critical: false,
      purpose: 'Выполнение бизнес-логики',
      fallback: {
        name: 'basic-logic',
        process: async (request) => {
          // Базовая бизнес-логика
          return {
            action: request.action,
            result: 'processed',
            rules: []
          };
        }
      },
      options: {
        rulesEngine: true,
        validation: true
      }
    });
  }

  // Переопределяем обработку для программного уровня
  async handle(request, context = {}) {
    // Добавляем программный контекст
    const programContext = {
      ...context,
      domain: request.domain || this.config.defaultDomain || 'bcm',
      module: request.module,
      userId: context.userId || request.userId,
      programTime: Date.now()
    };

    // Определяем тип обработки
    if (request.type === 'domain') {
      return await this.handleDomainRequest(request, programContext);
    } else if (request.type === 'module') {
      return await this.handleModuleRequest(request, programContext);
    } else if (request.type === 'adapter') {
      return await this.handleAdapterRequest(request, programContext);
    } else if (request.type === 'business') {
      return await this.handleBusinessRequest(request, programContext);
    }

    // Стандартная обработка бизнес-логики
    return await this.processBusinessLogic(request, programContext);
  }

  // Обработка бизнес-логики
  async processBusinessLogic(request, context) {
    // 1. Определяем домен
    const domain = await this.resolveDomain(context.domain);

    if (!domain) {
      throw new Error(`Domain ${context.domain} not found`);
    }

    // 2. Загружаем необходимый модуль
    const module = await this.loadModule(request.module || request.action, domain);

    if (!module) {
      throw new Error(`Module ${request.module} not available for domain ${domain.name}`);
    }

    // 3. Получаем контекст пользователя
    const userContext = await this.getUserContext(context.userId);

    // 4. Выбираем адаптер для выполнения
    const adapter = await this.selectAdapter(module, context);

    // 5. Выполняем через модуль с адаптером
    const result = await this.executeWithModule(module, request, {
      ...context,
      domain,
      userContext,
      adapter
    });

    // 6. Персонализируем результат
    const personalizedResult = await this.personalizeResult(result, userContext);

    // 7. Сохраняем предпочтения пользователя
    await this.updateUserPreferences(context.userId, request, personalizedResult);

    // Эмитим событие обработки
    this.emitEvent('business.logic.processed', {
      domain: domain.name,
      module: module.name,
      userId: context.userId,
      result: personalizedResult
    });

    return personalizedResult;
  }

  // Обработка доменных запросов
  async handleDomainRequest(request, context) {
    const domainRegistry = this.services.get('domain-registry');

    switch (request.action) {
      case 'register':
        // Регистрация нового домена
        const registered = await domainRegistry.process({
          action: 'register',
          domain: request.domainConfig
        });

        if (registered.success) {
          this.domains.set(request.domainConfig.name, request.domainConfig);
          this.emitEvent('domain.registered', request.domainConfig);
        }

        return registered;

      case 'list':
        // Список доменов
        return {
          domains: Array.from(this.domains.values()),
          active: context.domain,
          count: this.domains.size
        };

      case 'switch':
        // Переключение домена
        const newDomain = await this.resolveDomain(request.targetDomain);
        if (newDomain) {
          context.domain = request.targetDomain;
          this.emitEvent('domain.switched', { from: context.domain, to: request.targetDomain });
          return { switched: true, domain: newDomain };
        }
        return { switched: false, error: 'Domain not found' };

      default:
        return { error: 'Unknown domain action' };
    }
  }

  // Обработка модульных запросов
  async handleModuleRequest(request, context) {
    const moduleLoader = this.services.get('module-loader');

    switch (request.action) {
      case 'load':
        // Загрузка модуля
        const loaded = await moduleLoader.process({
          action: 'load',
          moduleName: request.moduleName,
          options: request.options
        });

        if (loaded.module) {
          this.modules.set(request.moduleName, loaded.module);
          this.emitEvent('module.loaded', { module: request.moduleName });
        }

        return loaded;

      case 'unload':
        // Выгрузка модуля
        this.modules.delete(request.moduleName);
        this.emitEvent('module.unloaded', { module: request.moduleName });
        return { unloaded: true };

      case 'list':
        // Список модулей
        return {
          modules: Array.from(this.modules.keys()),
          loaded: this.modules.size,
          available: await this.getAvailableModules()
        };

      case 'execute':
        // Выполнение через модуль
        const module = this.modules.get(request.moduleName);
        if (!module) {
          return { error: 'Module not loaded' };
        }

        return await this.executeWithModule(module, request.data, context);

      default:
        return { error: 'Unknown module action' };
    }
  }

  // Обработка адаптерных запросов
  async handleAdapterRequest(request, context) {
    const adapterService = this.services.get('adapter-service');

    switch (request.action) {
      case 'connect':
        // Подключение к платформе
        const connected = await adapterService.process({
          action: 'connect',
          platform: request.platform,
          config: request.config
        });

        if (connected.success) {
          this.adapters.set(request.platform, connected.adapter);
          this.emitEvent('adapter.connected', { platform: request.platform });
        }

        return connected;

      case 'disconnect':
        // Отключение от платформы
        this.adapters.delete(request.platform);
        this.emitEvent('adapter.disconnected', { platform: request.platform });
        return { disconnected: true };

      case 'execute':
        // Выполнение через адаптер
        const adapter = this.adapters.get(request.platform) ||
                       await this.selectAdapter({ requirements: request.requirements }, context);

        if (!adapter) {
          return { error: 'No suitable adapter found' };
        }

        return await adapter.process(request.data);

      case 'list':
        // Список адаптеров
        return {
          adapters: Array.from(this.adapters.keys()),
          connected: this.adapters.size,
          available: ['odoo', 'standalone', 'external']
        };

      default:
        return { error: 'Unknown adapter action' };
    }
  }

  // Обработка бизнес-запросов
  async handleBusinessRequest(request, context) {
    const businessLogic = this.services.get('business-logic');

    // Валидация бизнес-правил
    if (businessLogic) {
      const validation = await businessLogic.process({
        action: 'validate',
        data: request.data,
        rules: request.rules || []
      });

      if (!validation.valid) {
        return {
          error: 'Business validation failed',
          violations: validation.violations
        };
      }
    }

    // Выполнение бизнес-процесса
    const result = await this.processBusinessLogic(request.data, context);

    // Аудит бизнес-операции
    this.emitEvent('business.operation.completed', {
      operation: request.operation,
      userId: context.userId,
      result: result.success
    });

    return result;
  }

  // Разрешение домена
  async resolveDomain(domainName) {
    // Проверяем кэш
    if (this.domains.has(domainName)) {
      return this.domains.get(domainName);
    }

    // Загружаем из registry
    const domainRegistry = this.services.get('domain-registry');
    if (domainRegistry) {
      const domain = await domainRegistry.process({
        action: 'get',
        domainName: domainName
      });

      if (domain) {
        this.domains.set(domainName, domain);
        return domain;
      }
    }

    return null;
  }

  // Загрузка модуля
  async loadModule(moduleName, domain) {
    // Проверяем загружен ли модуль
    if (this.modules.has(moduleName)) {
      return this.modules.get(moduleName);
    }

    // Загружаем модуль
    const moduleLoader = this.services.get('module-loader');
    if (moduleLoader) {
      const loaded = await moduleLoader.process({
        action: 'load',
        moduleName: moduleName,
        domain: domain.name
      });

      if (loaded.module) {
        this.modules.set(moduleName, loaded.module);
        return loaded.module;
      }
    }

    return null;
  }

  // Получение контекста пользователя
  async getUserContext(userId) {
    // Проверяем кэш
    if (this.userContexts.has(userId)) {
      const cached = this.userContexts.get(userId);
      if (Date.now() - cached.timestamp < 3600000) { // 1 час
        return cached.context;
      }
    }

    // Загружаем контекст
    const userContextService = this.services.get('user-context');
    if (userContextService) {
      const context = await userContextService.process({
        action: 'get',
        userId: userId
      });

      // Кэшируем
      this.userContexts.set(userId, {
        context: context,
        timestamp: Date.now()
      });

      return context;
    }

    return { userId, preferences: {}, role: 'user' };
  }

  // Выбор адаптера
  async selectAdapter(module, context) {
    const adapterService = this.services.get('adapter-service');

    // Определяем требования модуля
    const requirements = module.requirements || {};

    // Если указан конкретный адаптер
    if (context.adapter) {
      return this.adapters.get(context.adapter);
    }

    // Выбираем подходящий адаптер
    if (adapterService) {
      const selected = await adapterService.process({
        action: 'select',
        requirements: requirements,
        context: context
      });

      if (selected.adapter) {
        return selected.adapter;
      }
    }

    // Fallback к default адаптеру
    return this.adapters.get(this.config.defaultAdapter || 'odoo');
  }

  // Выполнение через модуль
  async executeWithModule(module, request, context) {
    try {
      // Подготавливаем данные для модуля
      const moduleRequest = {
        ...request,
        context: context,
        adapter: context.adapter
      };

      // Выполняем модуль
      let result;
      if (module.process) {
        result = await module.process(moduleRequest);
      } else if (module.execute) {
        result = await module.execute(moduleRequest);
      } else if (typeof module === 'function') {
        result = await module(moduleRequest);
      } else {
        throw new Error('Module does not have executable method');
      }

      // Добавляем метаданные
      result._metadata = {
        module: module.name,
        domain: context.domain?.name,
        executedAt: Date.now(),
        userId: context.userId
      };

      return result;

    } catch (error) {
      console.error(`Module execution error in ${module.name}:`, error);

      // Пробуем fallback
      if (module.fallback) {
        return await module.fallback(request, context);
      }

      throw error;
    }
  }

  // Персонализация результата
  async personalizeResult(result, userContext) {
    const userContextService = this.services.get('user-context');

    if (userContextService && userContextService.personalize) {
      return await userContextService.personalize({
        result: result,
        userContext: userContext
      });
    }

    // Базовая персонализация
    if (userContext.preferences?.format) {
      result.format = userContext.preferences.format;
    }

    if (userContext.preferences?.language) {
      result.language = userContext.preferences.language;
    }

    return result;
  }

  // Обновление предпочтений пользователя
  async updateUserPreferences(userId, request, result) {
    const userContextService = this.services.get('user-context');

    if (userContextService && userContextService.updatePreferences) {
      await userContextService.updatePreferences({
        userId: userId,
        action: request.action || request.type,
        feedback: result._feedback,
        timestamp: Date.now()
      });
    }

    // Обновляем кэш
    if (this.userContexts.has(userId)) {
      const cached = this.userContexts.get(userId);
      cached.timestamp = Date.now() - 3600001; // Инвалидируем кэш
    }
  }

  // Получение доступных модулей
  async getAvailableModules() {
    const moduleLoader = this.services.get('module-loader');

    if (moduleLoader && moduleLoader.listAvailable) {
      return await moduleLoader.listAvailable();
    }

    // Возвращаем известные модули
    return [
      'business-impact-analysis',
      'incident-management',
      'risk-assessment',
      'digital-twin',
      'ai-advisor',
      'exercise-testing',
      'compliance-audit',
      'continuity-planning',
      'reporting-analytics'
    ];
  }

  // Проверка нужно ли обрабатывать событие
  shouldHandleEvent(sourceLevel, eventType, data) {
    // Program уровень обрабатывает бизнес-события
    const relevantEvents = [
      'client.request.validated',
      'bridge.translation.completed',
      'module.request',
      'domain.operation',
      'user.action'
    ];

    return relevantEvents.some(pattern => eventType.includes(pattern.split('.')[1]));
  }

  // Получение метрик программного уровня
  getProgramMetrics() {
    const metrics = super.getMetrics();

    metrics.program = {
      domainsRegistered: this.domains.size,
      modulesLoaded: this.modules.size,
      adaptersConnected: this.adapters.size,
      userContextsCached: this.userContexts.size,
      businessOperations: this.stats.businessOperations || 0
    };

    // Метрики по доменам
    metrics.domainMetrics = {};
    this.domains.forEach((domain, name) => {
      metrics.domainMetrics[name] = {
        capabilities: domain.capabilities?.length || 0,
        modules: Array.from(this.modules.values())
          .filter(m => m.domain === name).length
      };
    });

    return metrics;
  }

  // Очистка старых контекстов
  cleanupUserContexts() {
    const now = Date.now();
    const ttl = 3600000; // 1 час

    this.userContexts.forEach((cached, userId) => {
      if (now - cached.timestamp > ttl) {
        this.userContexts.delete(userId);
      }
    });
  }

  // Инициализация
  async initialize() {
    await super.initialize();

    // Предзагрузка модулей если указаны
    if (this.config.preloadModules) {
      for (const moduleName of this.config.preloadModules) {
        await this.loadModule(moduleName, { name: 'default' });
      }
    }

    // Периодическая очистка
    setInterval(() => {
      this.cleanupUserContexts();
    }, 300000); // каждые 5 минут

    return true;
  }
}

module.exports = ProgramOrchestrator;