// Bridge Orchestrator - оркестратор уровня моста

const BaseOrchestrator = require('./base-orchestrator');

class BridgeOrchestrator extends BaseOrchestrator {
  constructor(config = {}) {
    super('bridge', config);

    // Специфичные для bridge уровня параметры
    this.translationRules = new Map();
    this.contextCache = new Map();
    this.learningHistory = [];
    this.fallbackStrategies = new Map();
  }

  // Определение обязательных сервисов bridge уровня
  defineRequiredServices() {
    this.requiredServices.set('ai-bridge-manager', {
      critical: true,
      purpose: 'Интеллектуальная трансляция между системой и программными компонентами',
      path: '../BRIDGE_LAYER/ai-bridge-manager',
      fallback: {
        name: 'simple-translator',
        process: async (request) => {
          // Простая трансляция без AI
          console.log('Using simple translation without AI');
          return {
            translated: request,
            method: 'direct',
            enrichment: {}
          };
        }
      },
      options: {
        learningEnabled: true,
        cacheResults: true,
        maxCacheSize: 1000
      }
    });

    this.requiredServices.set('operational-brain', {
      critical: false,
      purpose: 'Контекстуальный анализ и принятие решений',
      path: '../BRIDGE_LAYER/operational-brain',
      fallback: {
        name: 'basic-analyzer',
        process: async (request) => {
          // Базовый анализ без контекста
          return {
            context: {
              timestamp: Date.now(),
              source: request.source || 'unknown',
              priority: request.priority || 'normal'
            },
            decision: 'proceed',
            confidence: 0.5
          };
        }
      },
      options: {
        contextDepth: 3,
        historySize: 100,
        predictionEnabled: true
      }
    });

    this.requiredServices.set('translation-service', {
      critical: true,
      purpose: 'Трансляция форматов данных между уровнями',
      fallback: {
        name: 'passthrough-translator',
        process: async (request) => {
          // Прямая передача без трансляции
          return { data: request.data, translated: false };
        }
      },
      options: {
        formats: ['system', 'program', 'odoo', 'json', 'xml'],
        validation: true
      }
    });

    this.requiredServices.set('context-enrichment', {
      critical: false,
      purpose: 'Обогащение контекста запросов',
      fallback: {
        name: 'minimal-context',
        process: async (request) => {
          return {
            ...request,
            context: {
              timestamp: Date.now(),
              level: 'bridge'
            }
          };
        }
      },
      options: {
        enrichmentSources: ['user', 'organization', 'historical'],
        cacheEnabled: true
      }
    });

    this.requiredServices.set('cache-service', {
      critical: false,
      purpose: 'Кэширование результатов трансляции',
      fallback: {
        name: 'memory-cache',
        cache: new Map(),
        process: async (request) => {
          const key = JSON.stringify(request);
          if (request.operation === 'get') {
            return this.cache.get(key);
          } else if (request.operation === 'set') {
            this.cache.set(key, request.value);
            return { cached: true };
          }
          return null;
        }
      },
      options: {
        ttl: 300000, // 5 минут
        maxSize: 1000
      }
    });

    this.requiredServices.set('resilience-service', {
      critical: false,
      purpose: 'Обеспечение отказоустойчивости',
      fallback: {
        name: 'basic-resilience',
        process: async (request) => {
          // Базовая стратегия retry
          return {
            strategy: 'retry',
            maxRetries: 3,
            backoff: 'exponential'
          };
        }
      },
      options: {
        circuitBreakerThreshold: 5,
        retryStrategies: ['exponential', 'linear', 'fixed'],
        fallbackTimeout: 30000
      }
    });
  }

  // Переопределяем обработку для bridge уровня
  async handle(request, context = {}) {
    // Добавляем bridge контекст
    const bridgeContext = {
      ...context,
      bridgeTime: Date.now(),
      translationRequired: this.needsTranslation(request),
      enrichmentLevel: this.determineEnrichmentLevel(request)
    };

    // Определяем тип обработки
    if (request.type === 'translate') {
      return await this.handleTranslation(request, bridgeContext);
    } else if (request.type === 'enrich') {
      return await this.handleEnrichment(request, bridgeContext);
    } else if (request.type === 'learn') {
      return await this.handleLearning(request, bridgeContext);
    } else if (request.type === 'fallback') {
      return await this.handleFallback(request, bridgeContext);
    }

    // Автоматическая обработка на основе анализа
    return await this.intelligentHandle(request, bridgeContext);
  }

  // Интеллектуальная обработка с автоопределением
  async intelligentHandle(request, context) {
    const aiBridge = this.services.get('ai-bridge-manager');
    const brain = this.services.get('operational-brain');

    // 1. Анализируем запрос через operational brain
    let analysis = { decision: 'proceed' };
    if (brain) {
      analysis = await brain.process({
        action: 'analyze',
        request: request,
        context: context
      });
    }

    // 2. Определяем нужна ли трансляция
    if (this.needsTranslation(request)) {
      const translationService = this.services.get('translation-service');
      if (translationService) {
        request = await translationService.process({
          action: 'translate',
          data: request,
          fromFormat: context.sourceFormat || 'system',
          toFormat: context.targetFormat || 'program'
        });
      }
    }

    // 3. Обогащаем контекст
    const contextService = this.services.get('context-enrichment');
    if (contextService && analysis.enrichmentRecommended) {
      context = await contextService.process({
        action: 'enrich',
        context: context,
        sources: ['user', 'historical', 'organizational']
      });
    }

    // 4. Проверяем кэш
    const cacheService = this.services.get('cache-service');
    if (cacheService) {
      const cacheKey = this.generateCacheKey(request, context);
      const cached = await cacheService.process({
        operation: 'get',
        key: cacheKey
      });

      if (cached) {
        this.stats.cacheHits = (this.stats.cacheHits || 0) + 1;
        return cached;
      }
    }

    // 5. Применяем AI трансляцию если нужно
    let result;
    if (aiBridge) {
      result = await aiBridge.process({
        action: 'adapt',
        request: request,
        context: context,
        targetLevel: context.targetLevel || 'program'
      });
    } else {
      result = { data: request, adapted: false };
    }

    // 6. Сохраняем в кэш
    if (cacheService && result.cacheable !== false) {
      await cacheService.process({
        operation: 'set',
        key: this.generateCacheKey(request, context),
        value: result,
        ttl: 300000
      });
    }

    // 7. Обучаемся на взаимодействии
    this.learn(request, result, context);

    // Эмитим событие успешной трансляции
    this.emitEvent('translation.completed', {
      request: request,
      result: result,
      context: context
    });

    return result;
  }

  // Обработка трансляции
  async handleTranslation(request, context) {
    const translationService = this.services.get('translation-service');

    if (!translationService) {
      throw new Error('Translation service not available');
    }

    const result = await translationService.process({
      action: 'translate',
      data: request.data,
      from: request.fromFormat || 'system',
      to: request.toFormat || 'program',
      rules: this.getTranslationRules(request.fromFormat, request.toFormat)
    });

    // Сохраняем правила если трансляция успешна
    if (result.success) {
      this.updateTranslationRules(request.fromFormat, request.toFormat, result.rules);
    }

    return result;
  }

  // Обработка обогащения контекста
  async handleEnrichment(request, context) {
    const contextService = this.services.get('context-enrichment');
    const brain = this.services.get('operational-brain');

    // Базовое обогащение
    let enrichedContext = context;
    if (contextService) {
      enrichedContext = await contextService.process({
        action: 'enrich',
        context: context,
        data: request.data,
        sources: request.sources || ['all']
      });
    }

    // Интеллектуальное обогащение через brain
    if (brain) {
      const insights = await brain.process({
        action: 'generateInsights',
        data: request.data,
        context: enrichedContext
      });

      enrichedContext.insights = insights;
      enrichedContext.predictions = await brain.process({
        action: 'predict',
        data: request.data,
        context: enrichedContext
      });
    }

    return {
      originalContext: context,
      enrichedContext: enrichedContext,
      enrichmentLevel: this.calculateEnrichmentLevel(enrichedContext)
    };
  }

  // Обработка обучения
  async handleLearning(request, context) {
    const aiBridge = this.services.get('ai-bridge-manager');

    // Сохраняем в историю
    this.learningHistory.push({
      timestamp: Date.now(),
      request: request,
      context: context,
      result: request.result
    });

    // Ограничиваем размер истории
    if (this.learningHistory.length > 1000) {
      this.learningHistory.shift();
    }

    // Обучаем AI Bridge если доступен
    if (aiBridge && aiBridge.learn) {
      await aiBridge.learn({
        history: this.learningHistory,
        patterns: this.extractPatterns(this.learningHistory)
      });
    }

    // Обновляем правила трансляции на основе обучения
    this.updateRulesFromLearning();

    return {
      learned: true,
      historySize: this.learningHistory.length,
      patternsDetected: this.extractPatterns(this.learningHistory).length
    };
  }

  // Обработка fallback стратегий
  async handleFallback(request, context) {
    const resilienceService = this.services.get('resilience-service');

    // Получаем стратегию fallback
    let strategy = { strategy: 'default' };
    if (resilienceService) {
      strategy = await resilienceService.process({
        action: 'getFallbackStrategy',
        failedComponent: request.failedComponent,
        error: request.error,
        context: context
      });
    }

    // Применяем стратегию
    switch (strategy.strategy) {
      case 'retry':
        return await this.retryWithBackoff(request.originalRequest, strategy);

      case 'circuit-breaker':
        return await this.applyCircuitBreaker(request.failedComponent);

      case 'alternative-route':
        return await this.findAlternativeRoute(request);

      case 'cached-response':
        return await this.getCachedFallback(request);

      default:
        return { fallback: true, strategy: 'default', result: null };
    }
  }

  // Определение необходимости трансляции
  needsTranslation(request) {
    // Проверяем форматы
    if (request.sourceFormat && request.targetFormat) {
      return request.sourceFormat !== request.targetFormat;
    }

    // Проверяем уровни
    if (request.sourceLevel && request.targetLevel) {
      return request.sourceLevel !== request.targetLevel;
    }

    // Эвристика: если есть специфичные поля для разных уровней
    const systemFields = ['orchestrator', 'service', 'workflow'];
    const programFields = ['module', 'domain', 'adapter'];

    const hasSystemFields = systemFields.some(f => request[f]);
    const hasProgramFields = programFields.some(f => request[f]);

    return hasSystemFields && hasProgramFields;
  }

  // Определение уровня обогащения
  determineEnrichmentLevel(request) {
    if (request.enrichment === false) return 'none';
    if (request.enrichment === 'minimal') return 'minimal';
    if (request.critical || request.priority === 'high') return 'full';

    return 'standard';
  }

  // Генерация ключа кэша
  generateCacheKey(request, context) {
    const key = {
      data: request.data || request,
      source: context.sourceLevel,
      target: context.targetLevel,
      user: context.userId
    };
    return JSON.stringify(key);
  }

  // Обучение на взаимодействии
  learn(request, result, context) {
    const pattern = {
      input: this.extractFeatures(request),
      output: this.extractFeatures(result),
      context: this.extractFeatures(context),
      success: result.success !== false,
      timestamp: Date.now()
    };

    this.learningHistory.push(pattern);

    // Периодически анализируем паттерны
    if (this.learningHistory.length % 100 === 0) {
      this.analyzeAndOptimize();
    }
  }

  // Извлечение признаков для обучения
  extractFeatures(obj) {
    return {
      type: obj.type || obj.action,
      size: JSON.stringify(obj).length,
      complexity: this.calculateComplexity(obj),
      hasNested: typeof obj === 'object' && Object.values(obj).some(v => typeof v === 'object')
    };
  }

  // Расчет сложности объекта
  calculateComplexity(obj) {
    let complexity = 0;
    const stack = [obj];

    while (stack.length > 0) {
      const current = stack.pop();
      complexity++;

      if (typeof current === 'object' && current !== null) {
        Object.values(current).forEach(v => {
          if (typeof v === 'object') stack.push(v);
        });
      }
    }

    return complexity;
  }

  // Анализ и оптимизация на основе обучения
  analyzeAndOptimize() {
    const patterns = this.extractPatterns(this.learningHistory);

    // Оптимизируем правила трансляции
    patterns.forEach(pattern => {
      if (pattern.frequency > 10 && pattern.successRate > 0.9) {
        // Добавляем как оптимизированное правило
        this.translationRules.set(pattern.signature, pattern.optimalPath);
      }
    });

    // Обновляем fallback стратегии
    const failures = this.learningHistory.filter(h => !h.success);
    this.updateFallbackStrategies(failures);

    console.log(`Bridge optimization: ${patterns.length} patterns, ${this.translationRules.size} rules`);
  }

  // Извлечение паттернов
  extractPatterns(history) {
    const patterns = new Map();

    history.forEach(item => {
      const signature = `${item.input?.type}-${item.output?.type}`;

      if (!patterns.has(signature)) {
        patterns.set(signature, {
          signature,
          count: 0,
          successes: 0,
          optimalPath: null
        });
      }

      const pattern = patterns.get(signature);
      pattern.count++;
      if (item.success) pattern.successes++;
    });

    return Array.from(patterns.values()).map(p => ({
      ...p,
      frequency: p.count,
      successRate: p.successes / p.count
    }));
  }

  // Обновление fallback стратегий
  updateFallbackStrategies(failures) {
    failures.forEach(failure => {
      const component = failure.input?.component || 'unknown';

      if (!this.fallbackStrategies.has(component)) {
        this.fallbackStrategies.set(component, []);
      }

      // Добавляем новую стратегию на основе анализа
      this.fallbackStrategies.get(component).push({
        condition: failure.context,
        strategy: this.determineBestFallback(failure)
      });
    });
  }

  // Определение лучшей fallback стратегии
  determineBestFallback(failure) {
    if (failure.error?.includes('timeout')) return 'circuit-breaker';
    if (failure.error?.includes('not found')) return 'alternative-route';
    if (failure.retryable) return 'retry';
    return 'cached-response';
  }

  // Retry с backoff
  async retryWithBackoff(request, strategy) {
    let delay = 1000;

    for (let i = 0; i < (strategy.maxRetries || 3); i++) {
      try {
        const result = await this.handle(request);
        return { success: true, result, retries: i + 1 };
      } catch (error) {
        if (strategy.backoff === 'exponential') {
          delay *= 2;
        }
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }

    return { success: false, maxRetriesReached: true };
  }

  // Проверка нужно ли обрабатывать событие
  shouldHandleEvent(sourceLevel, eventType, data) {
    // Bridge обрабатывает события требующие трансляции
    const relevantEvents = [
      'system.request.processed',
      'program.response.ready',
      'translation.required',
      'enrichment.needed',
      'fallback.triggered'
    ];

    return relevantEvents.some(pattern => eventType.includes(pattern.split('.')[1]));
  }

  // Получение метрик bridge
  getBridgeMetrics() {
    const metrics = super.getMetrics();

    metrics.bridge = {
      translationRules: this.translationRules.size,
      learningHistorySize: this.learningHistory.length,
      cacheHits: this.stats.cacheHits || 0,
      fallbackStrategies: this.fallbackStrategies.size,
      averageTranslationTime: this.calculateAverageTranslationTime()
    };

    return metrics;
  }

  // Расчет среднего времени трансляции
  calculateAverageTranslationTime() {
    const recent = this.learningHistory.slice(-100);
    if (recent.length === 0) return 0;

    const times = recent.map(h => h.processingTime || 0);
    return times.reduce((a, b) => a + b, 0) / times.length;
  }
}

module.exports = BridgeOrchestrator;