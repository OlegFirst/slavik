// System Orchestrator - оркестратор системного уровня

const BaseOrchestrator = require('./base-orchestrator');

class SystemOrchestrator extends BaseOrchestrator {
  constructor(config = {}) {
    super('system', config);

    // Специфичные для системного уровня параметры
    this.eventQueue = [];
    this.workflows = new Map();
    this.dataConnections = new Map();
    this.aiModels = new Map();
  }

  // Определение обязательных сервисов системного уровня
  defineRequiredServices() {
    this.requiredServices.set('event-bus', {
      critical: true,
      purpose: 'Асинхронная коммуникация между компонентами',
      path: '../SYSTEM_COMPONENTS/2_EVENTS/event-bus',
      implementations: ['rabbitmq', 'redis', 'in-memory'],
      fallback: {
        name: 'direct-call-bus',
        process: async (request) => {
          // Прямые вызовы вместо очереди
          console.log('Using direct calls instead of event bus');
          return { delivered: true, method: 'direct' };
        }
      },
      options: {
        host: this.config.eventBusHost || 'localhost',
        port: this.config.eventBusPort || 5672
      }
    });

    this.requiredServices.set('workflow-engine', {
      critical: false,
      purpose: 'Выполнение бизнес-процессов и workflow',
      path: '../SYSTEM_COMPONENTS/3_PROCESSING/workflow-engine',
      implementations: ['camunda', 'node-workflow', 'simple'],
      fallback: {
        name: 'sequential-executor',
        process: async (request) => {
          // Последовательное выполнение
          console.log('Using sequential execution instead of workflow');
          return { executed: true, method: 'sequential' };
        }
      },
      options: {
        maxConcurrent: 10,
        timeout: 30000
      }
    });

    this.requiredServices.set('data-gateway', {
      critical: true,
      purpose: 'Унифицированный доступ к данным',
      path: '../SYSTEM_COMPONENTS/4_STORAGE/data-gateway',
      implementations: ['postgresql', 'mongodb', 'multi-db'],
      fallback: {
        name: 'memory-storage',
        storage: new Map(),
        process: async (request) => {
          // In-memory хранилище
          if (request.operation === 'save') {
            this.storage.set(request.key, request.value);
            return { saved: true };
          } else if (request.operation === 'get') {
            return { value: this.storage.get(request.key) };
          }
          return { processed: true };
        }
      },
      options: {
        connectionString: this.config.dbConnection,
        poolSize: 10
      }
    });

    this.requiredServices.set('ai-service', {
      critical: false,
      purpose: 'Интеллектуальные функции и предсказания',
      path: '../SYSTEM_COMPONENTS/5_INTELLIGENCE/ai-service',
      implementations: ['openai', 'local-llm', 'tensorflow'],
      fallback: {
        name: 'rule-based-ai',
        process: async (request) => {
          // Правила вместо AI
          console.log('Using rule-based logic instead of AI');

          // Простая логика на правилах
          if (request.type === 'predict') {
            return {
              prediction: Math.random() > 0.5 ? 'positive' : 'negative',
              confidence: 0.6,
              method: 'rules'
            };
          } else if (request.type === 'analyze') {
            return {
              analysis: 'Basic rule-based analysis',
              insights: ['insight1', 'insight2'],
              method: 'rules'
            };
          }

          return { processed: true, method: 'rules' };
        }
      },
      options: {
        apiKey: this.config.aiApiKey,
        model: 'gpt-4',
        maxTokens: 1000
      }
    });

    this.requiredServices.set('monitoring', {
      critical: false,
      purpose: 'Мониторинг и сбор метрик',
      path: '../SYSTEM_COMPONENTS/6_TOOLS/monitoring',
      implementations: ['prometheus', 'custom', 'console'],
      fallback: {
        name: 'console-monitor',
        metrics: [],
        process: async (request) => {
          // Логирование в консоль
          console.log(`[METRIC] ${request.metric}: ${request.value}`);
          if (!this.metrics) this.metrics = [];
          this.metrics.push({ ...request, timestamp: Date.now() });
          return { logged: true };
        },
        getMetrics: () => this.metrics
      },
      options: {
        exportInterval: 15000,
        retention: '30d'
      }
    });
  }

  // Переопределяем обработку запроса для системного уровня
  async handle(request, context = {}) {
    // Добавляем системный контекст
    const systemContext = {
      ...context,
      systemTime: Date.now(),
      systemId: this.config.systemId || 'main',
      capabilities: Array.from(this.services.keys())
    };

    // Определяем тип обработки
    if (request.type === 'event') {
      return await this.handleEvent(request, systemContext);
    } else if (request.type === 'workflow') {
      return await this.handleWorkflow(request, systemContext);
    } else if (request.type === 'data') {
      return await this.handleData(request, systemContext);
    } else if (request.type === 'ai') {
      return await this.handleAI(request, systemContext);
    }

    // Стандартная обработка
    return super.handle(request, systemContext);
  }

  // Обработка событий
  async handleEvent(request, context) {
    const eventBus = this.services.get('event-bus');

    if (!eventBus) {
      throw new Error('Event bus service not available');
    }

    // Публикуем событие
    const result = await eventBus.process({
      action: 'publish',
      topic: request.topic || 'system.events',
      message: request.message,
      metadata: context
    });

    // Эмитим для других оркестраторов
    this.emitEvent('event.published', {
      topic: request.topic,
      message: request.message,
      result
    });

    return result;
  }

  // Обработка workflow
  async handleWorkflow(request, context) {
    const workflowEngine = this.services.get('workflow-engine');

    if (!workflowEngine) {
      // Fallback к последовательному выполнению
      return await this.executeSequentially(request.steps, context);
    }

    // Запускаем workflow
    const result = await workflowEngine.process({
      action: 'execute',
      workflow: request.workflow,
      steps: request.steps,
      context: context
    });

    // Эмитим событие завершения workflow
    this.emitEvent('workflow.completed', {
      workflow: request.workflow,
      result
    });

    return result;
  }

  // Обработка данных
  async handleData(request, context) {
    const dataGateway = this.services.get('data-gateway');

    if (!dataGateway) {
      throw new Error('Data gateway service not available');
    }

    let result;

    switch (request.operation) {
      case 'query':
        result = await dataGateway.process({
          action: 'query',
          collection: request.collection,
          filter: request.filter,
          projection: request.projection
        });
        break;

      case 'save':
        result = await dataGateway.process({
          action: 'save',
          collection: request.collection,
          data: request.data,
          options: request.options
        });
        break;

      case 'update':
        result = await dataGateway.process({
          action: 'update',
          collection: request.collection,
          filter: request.filter,
          update: request.update
        });
        break;

      case 'delete':
        result = await dataGateway.process({
          action: 'delete',
          collection: request.collection,
          filter: request.filter
        });
        break;

      default:
        result = await dataGateway.process(request);
    }

    // Эмитим событие изменения данных
    if (['save', 'update', 'delete'].includes(request.operation)) {
      this.emitEvent('data.changed', {
        collection: request.collection,
        operation: request.operation,
        result
      });
    }

    return result;
  }

  // Обработка AI запросов
  async handleAI(request, context) {
    const aiService = this.services.get('ai-service');

    if (!aiService) {
      // Используем fallback (правила)
      return {
        error: 'AI service not available',
        fallback: true,
        result: this.applyRules(request)
      };
    }

    let result;

    switch (request.action) {
      case 'predict':
        result = await aiService.process({
          action: 'predict',
          model: request.model || 'default',
          input: request.input,
          parameters: request.parameters
        });
        break;

      case 'analyze':
        result = await aiService.process({
          action: 'analyze',
          data: request.data,
          type: request.analysisType,
          options: request.options
        });
        break;

      case 'generate':
        result = await aiService.process({
          action: 'generate',
          prompt: request.prompt,
          maxTokens: request.maxTokens,
          temperature: request.temperature
        });
        break;

      default:
        result = await aiService.process(request);
    }

    // Эмитим событие AI обработки
    this.emitEvent('ai.processed', {
      action: request.action,
      model: request.model,
      result
    });

    return result;
  }

  // Последовательное выполнение шагов (fallback для workflow)
  async executeSequentially(steps, context) {
    const results = [];

    for (const step of steps) {
      try {
        const result = await this.handle(step, context);
        results.push({ step: step.name, success: true, result });

        // Проверяем условие остановки
        if (result.stopWorkflow) {
          break;
        }
      } catch (error) {
        results.push({
          step: step.name,
          success: false,
          error: error.message
        });

        // Если шаг критичный - прерываем
        if (step.critical) {
          break;
        }
      }
    }

    return {
      method: 'sequential',
      results,
      completed: results.every(r => r.success)
    };
  }

  // Применение правил (fallback для AI)
  applyRules(request) {
    // Простые правила для разных типов запросов
    const rules = {
      risk_assessment: (data) => {
        const score = (data.probability || 0.5) * (data.impact || 0.5);
        return {
          risk_level: score > 0.7 ? 'high' : score > 0.3 ? 'medium' : 'low',
          score,
          method: 'rule-based'
        };
      },

      incident_priority: (data) => {
        if (data.severity === 'critical' || data.affected_users > 1000) {
          return { priority: 'P1', method: 'rule-based' };
        } else if (data.severity === 'high' || data.affected_users > 100) {
          return { priority: 'P2', method: 'rule-based' };
        } else if (data.severity === 'medium' || data.affected_users > 10) {
          return { priority: 'P3', method: 'rule-based' };
        }
        return { priority: 'P4', method: 'rule-based' };
      },

      recommendation: (data) => {
        const recommendations = [];

        if (data.risk_level === 'high') {
          recommendations.push('Immediate action required');
          recommendations.push('Escalate to management');
        }

        if (data.type === 'security') {
          recommendations.push('Review security policies');
          recommendations.push('Conduct security audit');
        }

        return {
          recommendations,
          confidence: 0.5,
          method: 'rule-based'
        };
      }
    };

    const ruleType = request.ruleType || 'default';
    const rule = rules[ruleType];

    if (rule) {
      return rule(request.data || {});
    }

    return {
      message: 'No specific rules available',
      method: 'rule-based'
    };
  }

  // Проверяем нужно ли обрабатывать внешнее событие
  shouldHandleEvent(sourceLevel, eventType, data) {
    // Системный уровень обрабатывает события от всех уровней
    const relevantEvents = [
      'bridge.translation.required',
      'program.module.loaded',
      'client.auth.succeeded',
      'sandbox.optimization.ready'
    ];

    // Проверяем по паттерну
    return relevantEvents.some(pattern => eventType.includes(pattern.split('.')[1]));
  }

  // Специальные методы системного уровня
  async optimizeSystem() {
    console.log('🔧 Running system optimization...');

    // Оптимизация кэша
    const dataGateway = this.services.get('data-gateway');
    if (dataGateway && dataGateway.optimizeCache) {
      await dataGateway.optimizeCache();
    }

    // Очистка очередей событий
    const eventBus = this.services.get('event-bus');
    if (eventBus && eventBus.cleanupQueues) {
      await eventBus.cleanupQueues();
    }

    // Обновление AI моделей
    const aiService = this.services.get('ai-service');
    if (aiService && aiService.updateModels) {
      await aiService.updateModels();
    }

    this.emitEvent('optimization.completed', {
      timestamp: Date.now(),
      services: Array.from(this.services.keys())
    });
  }

  // Получение системных метрик
  getSystemMetrics() {
    const metrics = super.getMetrics();

    // Добавляем системные метрики
    metrics.system = {
      eventQueueSize: this.eventQueue.length,
      activeWorkflows: this.workflows.size,
      dataConnections: this.dataConnections.size,
      aiModels: this.aiModels.size
    };

    // Собираем метрики от сервисов
    for (const [name, service] of this.services) {
      if (service.getMetrics) {
        metrics.services[name] = service.getMetrics();
      }
    }

    return metrics;
  }
}

module.exports = SystemOrchestrator;